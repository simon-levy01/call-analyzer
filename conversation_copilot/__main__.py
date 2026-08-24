import argparse
import sys
from pathlib import Path

from pydantic import ValidationError

from .parser import parse_whatsapp_transcript

FIXTURE_PATH = Path(__file__).with_name("demo") / "lecturer_demo_chat.txt"


def foundation_summary() -> str:
    text = FIXTURE_PATH.read_text(encoding="utf-8-sig")
    turns = parse_whatsapp_transcript(text, source="demo")
    speaker_count = len({turn.speaker_name for turn in turns})
    if len(turns) != 500 or speaker_count != 2:
        raise ValueError(
            f"expected 500 Conversation Turns from 2 speakers, got {len(turns)} from {speaker_count}"
        )
    return f"Foundation ready\n{len(turns)} Conversation Turns\n{speaker_count} speakers"


def _conversation_turn_from_audio(draft, display_order: int):
    from .models import ConversationTurn

    return ConversationTurn(
        speaker_name=draft.speaker_name,
        speaker_role=draft.speaker_role,
        source=draft.source,
        content=draft.content,
        timestamp=draft.timestamp,
        display_order=display_order,
        is_media=False,
    )


def _needs_audio_selection(
    catalog, microphone_index: int, playback_index: int
) -> bool:
    return bool(
        catalog
        and catalog.microphones
        and catalog.playbacks
        and (microphone_index < 0 or playback_index < 0)
    )


def _keep_audio_after_video_end(audio_session) -> bool:
    return bool(audio_session and audio_session.snapshot().running)


def show_window(summary: str) -> None:
    import queue
    import threading
    import time
    import tkinter as tk
    from tkinter import messagebox, ttk

    from .audio import (
        AudioCallSession,
        AudioDeviceCatalog,
        AudioUnavailable,
        device_labels,
        local_model_available,
        prepare_transcription_runtime,
    )
    from .models import ConversationTurn
    audio_runtime_error = ""
    try:
        if not local_model_available():
            raise AudioUnavailable("Local transcription model is not installed")
        prepare_transcription_runtime()
    except Exception as exc:
        audio_runtime_error = str(exc) or f"Local transcription unavailable ({type(exc).__name__})"
    from .video import LiveVideoSession
    from .windows import list_call_windows, whatsapp_call_active

    root = tk.Tk()
    root.title("Conversation Copilot")
    root.minsize(760, 760)
    tk.Label(root, text=summary, justify="left", padx=12, pady=8).pack(anchor="w")
    tk.Label(root, text="Visible call windows").pack(anchor="w", padx=12)
    window_list = tk.Listbox(root, height=7)
    window_list.pack(fill="x", padx=12, pady=4)
    audio_controls = tk.LabelFrame(root, text="Two-sided local transcription")
    audio_controls.pack(fill="x", padx=12, pady=6)
    tk.Label(audio_controls, text="Microphone").grid(row=0, column=0, sticky="w", padx=6, pady=4)
    microphone_box = ttk.Combobox(audio_controls, state="readonly", width=54)
    microphone_box.grid(row=0, column=1, sticky="ew", padx=6, pady=4)
    tk.Label(audio_controls, text="Call audio").grid(row=1, column=0, sticky="w", padx=6, pady=4)
    playback_box = ttk.Combobox(audio_controls, state="readonly", width=54)
    playback_box.grid(row=1, column=1, sticky="ew", padx=6, pady=4)
    tk.Label(
        audio_controls,
        text="Captures every sound on this device — close Chrome and other audio apps",
        fg="#9a4b00",
    ).grid(row=2, column=1, sticky="w", padx=6, pady=(0, 4))
    tk.Label(audio_controls, text="Language").grid(row=3, column=0, sticky="w", padx=6, pady=4)
    language_box = ttk.Combobox(
        audio_controls,
        state="readonly",
        values=("English", "Hebrew", "Auto"),
        width=16,
    )
    language_box.current(0)
    language_box.grid(row=3, column=1, sticky="w", padx=6, pady=4)
    tk.Label(audio_controls, text="Mic sensitivity").grid(row=4, column=0, sticky="w", padx=6, pady=4)
    sensitivity = tk.Scale(audio_controls, from_=50, to=2_000, resolution=50, orient="horizontal")
    sensitivity.set(250)
    sensitivity.grid(row=4, column=1, sticky="ew", padx=6, pady=4)
    audio_controls.columnconfigure(1, weight=1)
    controls = tk.Frame(root)
    controls.pack(fill="x", padx=12)
    refresh_button = tk.Button(controls, text="Refresh")
    start_button = tk.Button(controls, text="Start")
    stop_button = tk.Button(controls, text="Stop", state="disabled")
    switch_button = tk.Button(controls, text="Switch face", state="disabled")
    for button in (refresh_button, start_button, stop_button, switch_button):
        button.pack(side="left", padx=(0, 6))
    selected_label = tk.Label(root, text="Selected: none", anchor="w")
    selected_label.pack(fill="x", padx=12, pady=(10, 0))
    status_label = tk.Label(root, text="Select a call window", anchor="w")
    status_label.pack(fill="x", padx=12)
    metrics_label = tk.Label(root, text="Signals: 0/s · faces: 0 · landmarks: 0 · blendshapes: 0")
    metrics_label.pack(anchor="w", padx=12)
    audio_status_label = tk.Label(root, text="Audio devices loading", anchor="w")
    audio_status_label.pack(fill="x", padx=12)
    thumbnail_label = tk.Label(root, text="No selected face", width=160, height=120)
    transcript_title = tk.Label(root, text="Final transcript", anchor="w")
    transcript_title.pack(fill="x", padx=12)
    transcript = tk.Text(root, height=9, state="disabled", wrap="word")
    transcript.pack(fill="both", expand=True, padx=12, pady=(2, 10))

    windows = []
    session: LiveVideoSession | None = None
    audio_catalog: AudioDeviceCatalog | None = None
    audio_session: AudioCallSession | None = None
    turns: list[ConversationTurn] = []
    stopping = False
    stop_started = 0.0
    shutdown_handoff: queue.SimpleQueue[str] = queue.SimpleQueue()
    thumbnail_photo = None

    def set_running(running: bool) -> None:
        window_list.configure(state="disabled" if running else "normal")
        refresh_button.configure(state="disabled" if running else "normal")
        start_button.configure(state="disabled" if running else "normal")
        stop_button.configure(state="normal" if running else "disabled")
        for selector in (microphone_box, playback_box, language_box):
            selector.configure(
                state="disabled" if running or audio_runtime_error else "readonly"
            )
        sensitivity.configure(
            state="disabled" if running or audio_runtime_error else "normal"
        )
        switch_button.configure(
            text="Switch face", state="normal" if running else "disabled"
        )

    def populate_audio_choices(*, initial: bool) -> None:
        if audio_catalog is None:
            microphone_box.configure(values=())
            microphone_box.set("")
            playback_box.configure(values=())
            playback_box.set("")
            return
        microphone_box.configure(values=device_labels(audio_catalog.microphones))
        playback_box.configure(
            values=device_labels([item.render for item in audio_catalog.playbacks])
        )
        microphone_box.set("")
        playback_box.set("")
        if initial and audio_catalog.default_microphone_index is not None:
            for index, record in enumerate(audio_catalog.microphones):
                if record.index == audio_catalog.default_microphone_index:
                    microphone_box.current(index)
                    break
        if initial and audio_catalog.default_render_index is not None:
            for index, item in enumerate(audio_catalog.playbacks):
                if item.render.index == audio_catalog.default_render_index:
                    playback_box.current(index)
                    break
        audio_status_label.configure(
            text=(
                "Select microphone and playback; close Chrome and other audio apps"
                if audio_catalog.microphones and audio_catalog.playbacks
                else "No usable WASAPI microphone/playback pair found"
            )
        )

    def refresh_audio(*, initial: bool) -> None:
        nonlocal audio_catalog
        if audio_runtime_error:
            for selector in (microphone_box, playback_box, language_box):
                selector.configure(state="disabled")
            sensitivity.configure(state="disabled")
            audio_status_label.configure(text=audio_runtime_error)
            populate_audio_choices(initial=False)
            return
        if audio_session and audio_session.snapshot().running:
            return
        try:
            if audio_catalog:
                audio_catalog.close()
            audio_catalog = AudioDeviceCatalog()
        except Exception as exc:
            audio_catalog = None
            audio_status_label.configure(text=f"Audio enumeration failed ({type(exc).__name__})")
        populate_audio_choices(initial=initial)

    def refresh(*, initial_audio: bool = False) -> None:
        nonlocal windows
        try:
            windows = list_call_windows()
        except OSError as exc:
            status_label.configure(text=f"Window scan failed ({type(exc).__name__})")
            windows = []
        window_list.delete(0, tk.END)
        for window in windows:
            window_list.insert(tk.END, window.display_name)
        status_label.configure(
            text="Select a call window" if windows else "No eligible call windows found"
        )
        refresh_audio(initial=initial_audio)

    def stop() -> None:
        nonlocal stopping, stop_started
        if stopping:
            return
        stopping = True
        stop_started = time.perf_counter()
        stop_button.configure(state="disabled")
        switch_button.configure(state="disabled")
        status_label.configure(text="Stopping")
        if audio_session:
            audio_session.request_stop()

        def finish_video(current: LiveVideoSession | None) -> None:
            error = ""
            if current:
                try:
                    current.stop()
                except (RuntimeError, TimeoutError) as exc:
                    error = f"Stop failed ({type(exc).__name__})"
            shutdown_handoff.put(error)

        threading.Thread(
            target=finish_video,
            args=(session,),
            name="ui-session-stop",
            daemon=True,
        ).start()

    def start() -> None:
        nonlocal audio_catalog, session, audio_session
        selection = window_list.curselection()
        if not selection:
            messagebox.showinfo("Conversation Copilot", "Choose a call window first.")
            return
        if not audio_runtime_error and _needs_audio_selection(
            audio_catalog, microphone_box.current(), playback_box.current()
        ):
            messagebox.showinfo(
                "Conversation Copilot", "Choose a microphone and playback device first."
            )
            return
        window = windows[selection[0]]
        turns.clear()
        transcript.configure(state="normal")
        transcript.delete("1.0", tk.END)
        transcript.configure(state="disabled")
        selected_label.configure(text=f"Selected: {window.display_name}")
        status_label.configure(text="Starting")
        root.update_idletasks()
        try:
            session = LiveVideoSession(window)
            session.start()
        except Exception as exc:
            if session:
                try:
                    session.stop()
                except Exception:
                    pass
            session = None
            status_label.configure(text=f"Assisted call could not start ({type(exc).__name__})")
            return
        audio_ready = (
            not audio_runtime_error
            and audio_catalog is not None
            and microphone_box.current() >= 0
            and playback_box.current() >= 0
        )
        if audio_ready:
            try:
                assert audio_catalog is not None
                language = {"English": "en", "Hebrew": "he", "Auto": None}[language_box.get()]
                audio_session = AudioCallSession(
                    audio_catalog,
                    audio_catalog.microphones[microphone_box.current()],
                    audio_catalog.playbacks[playback_box.current()],
                    language,
                    contact_name=window.display_name,
                    microphone_threshold=float(sensitivity.get()),
                    source_guard=(
                        (lambda: not whatsapp_call_active())
                        if window.kind == "Google Meet"
                        else None
                    ),
                    retain_catalog_on_clean_stop=True,
                )
                audio_session.start()
            except Exception as exc:
                if audio_session:
                    try:
                        audio_session.stop()
                    except TimeoutError:
                        pass
                audio_session = None
                if audio_catalog:
                    try:
                        audio_catalog.close()
                    except Exception:
                        pass
                audio_catalog = None
                audio_status_label.configure(text=str(exc) or type(exc).__name__)
                populate_audio_choices(initial=False)
        else:
            if audio_runtime_error:
                audio_status_label.configure(text=audio_runtime_error)
            elif audio_catalog is not None:
                audio_status_label.configure(
                    text="Audio inactive — no usable microphone"
                )
        set_running(True)

    def drain_audio_results(current_audio: AudioCallSession) -> None:
        while True:
            try:
                draft = current_audio.results.get_nowait()
            except queue.Empty:
                break
            turn = _conversation_turn_from_audio(draft, len(turns) + 1)
            turns.append(turn)
            transcript.configure(state="normal")
            transcript.insert(tk.END, f"{turn.speaker_name}: {turn.content}\n")
            transcript.configure(state="disabled")
            transcript.see(tk.END)

    def switch() -> None:
        if session:
            if session.snapshot().status == "Face lost":
                session.continue_tracking()
            else:
                session.switch_face()

    def poll_once() -> None:
        nonlocal audio_catalog, audio_runtime_error, session, audio_session, thumbnail_photo, stopping
        current = session
        if current:
            snapshot = current.snapshot()
            status_label.configure(text=snapshot.status)
            switch_button.configure(
                text=(
                    "Continue tracking"
                    if snapshot.status == "Face lost"
                    else "Switch face"
                )
            )
            metrics_label.configure(
                text=(
                    f"Signals: {snapshot.signal_rate:.0f}/s · faces: {snapshot.face_count} · "
                    f"landmarks: {snapshot.landmark_count} · "
                    f"blendshapes: {snapshot.blendshape_count}"
                )
            )
            if snapshot.thumbnail_rgb is not None:
                if not thumbnail_label.winfo_manager():
                    thumbnail_label.pack(pady=6, before=transcript_title)
                height, width = snapshot.thumbnail_rgb.shape[:2]
                ppm = f"P6 {width} {height} 255\n".encode() + snapshot.thumbnail_rgb.tobytes()
                thumbnail_photo = tk.PhotoImage(data=ppm, format="PPM")
                thumbnail_label.configure(image=thumbnail_photo, text="")
            else:
                thumbnail_photo = None
                thumbnail_label.configure(image="", text="No selected face")
                thumbnail_label.pack_forget()
            if not current.worker_alive and not current.capture.worker_alive:
                if _keep_audio_after_video_end(audio_session):
                    session = None
                    switch_button.configure(state="disabled")
                    status_label.configure(
                        text=f"{snapshot.status} · transcription continuing"
                    )
                    metrics_label.configure(
                        text="Signals: 0/s · faces: 0 · landmarks: 0 · blendshapes: 0"
                    )
                else:
                    stop()
        current_audio = audio_session
        if current_audio:
            snapshot = current_audio.snapshot()
            audio_status_label.configure(
                text=(
                    snapshot.fault
                    or f"Mic: {snapshot.microphone_status} · Playback: {snapshot.playback_status}"
                )
            )
            drain_audio_results(current_audio)
            if snapshot.fault and not snapshot.running and not stopping:
                audio_session = None
                if snapshot.fault == "Audio shutdown timed out":
                    audio_catalog = None
                    audio_runtime_error = "Audio shutdown timed out — restart the app"
                    populate_audio_choices(initial=False)
                    audio_status_label.configure(text=audio_runtime_error)
                else:
                    refresh_audio(initial=False)
                    audio_status_label.configure(text=snapshot.fault)
                if session is None:
                    stop()
        if stopping and not shutdown_handoff.empty():
            error = shutdown_handoff.get()
            audio_snapshot = audio_session.snapshot() if audio_session else None
            audio_done = not audio_snapshot or not audio_snapshot.running
            audio_timed_out = bool(
                audio_snapshot and audio_snapshot.fault == "Audio shutdown timed out"
            )
            if audio_timed_out:
                error = "Stop failed (TimeoutError)"
            if audio_done:
                if audio_session:
                    drain_audio_results(audio_session)
                session = None
                audio_session = None
                stopping = False
                thumbnail_photo = None
                thumbnail_label.configure(image="", text="No selected face")
                thumbnail_label.pack_forget()
                if audio_timed_out:
                    audio_catalog = None
                    audio_runtime_error = "Audio shutdown timed out — restart the app"
                    status_label.configure(text=error)
                    audio_status_label.configure(text=audio_runtime_error)
                    populate_audio_choices(initial=False)
                else:
                    status_label.configure(text=error or "Stopped")
                set_running(False)
                if not audio_timed_out and (
                    audio_catalog is None or audio_catalog.closed
                ):
                    audio_catalog = None
                    populate_audio_choices(initial=False)
            elif time.perf_counter() - stop_started > 6:
                if audio_session:
                    drain_audio_results(audio_session)
                session = None
                audio_session = None
                audio_catalog = None
                stopping = False
                audio_runtime_error = "Audio shutdown timed out — restart the app"
                status_label.configure(text="Stop failed (TimeoutError)")
                audio_status_label.configure(text=audio_runtime_error)
                set_running(False)
                populate_audio_choices(initial=False)
            else:
                shutdown_handoff.put(error)

    def poll() -> None:
        try:
            poll_once()
        except Exception as exc:
            status_label.configure(text=f"Update failed ({type(exc).__name__})")
        finally:
            root.after(100, poll)

    def close() -> None:
        if stopping:
            root.destroy()
            return
        if audio_session:
            try:
                audio_session.stop()
            except TimeoutError:
                pass
        if session:
            try:
                session.stop()
            except (RuntimeError, TimeoutError):
                pass
        try:
            if audio_catalog:
                audio_catalog.close()
        except Exception:
            pass
        finally:
            root.destroy()

    refresh_button.configure(command=refresh)
    start_button.configure(command=start)
    stop_button.configure(command=stop)
    switch_button.configure(command=switch)
    root.protocol("WM_DELETE_WINDOW", close)
    refresh(initial_audio=True)
    poll()
    root.mainloop()


def main(argv: list[str] | None = None) -> int:
    arg_parser = argparse.ArgumentParser(prog="python -m conversation_copilot")
    actions = arg_parser.add_mutually_exclusive_group()
    actions.add_argument("--check", action="store_true", help="validate the F01 fixture")
    actions.add_argument("--check-video", action="store_true", help="validate local face processing")
    actions.add_argument(
        "--check-video-capture",
        action="store_true",
        help="validate WGC using a local mock call",
    )
    actions.add_argument(
        "--benchmark-video",
        action="store_true",
        help="benchmark local face processing",
    )
    actions.add_argument(
        "--install-transcription-model",
        action="store_true",
        help="install the approved local transcription model",
    )
    actions.add_argument(
        "--check-audio",
        action="store_true",
        help="replay the approved local audio corpus offline",
    )
    actions.add_argument(
        "--benchmark-audio",
        action="store_true",
        help="benchmark two-source transcription with the F02 loop",
    )
    arg_parser.add_argument("--seconds", type=float, default=600)
    args = arg_parser.parse_args(argv)

    try:
        summary = foundation_summary()
    except ValidationError:
        print(
            "Foundation check failed: fixture produced an invalid Conversation Turn",
            file=sys.stderr,
        )
        return 1
    except (OSError, ValueError) as exc:
        print(f"Foundation check failed: {exc}", file=sys.stderr)
        return 1

    if args.check:
        print(summary)
    elif args.check_video:
        try:
            from .video import run_video_check

            print(run_video_check())
        except Exception as exc:
            print(f"Video check failed ({type(exc).__name__}): {exc}", file=sys.stderr)
            return 1
    elif args.check_video_capture:
        try:
            from .mock_call import run_video_capture_check

            print(run_video_capture_check())
        except Exception as exc:
            print(
                f"Video capture check failed ({type(exc).__name__}): {exc}",
                file=sys.stderr,
            )
            return 1
    elif args.benchmark_video:
        try:
            from .benchmark import run_benchmark

            print(run_benchmark(args.seconds))
        except Exception as exc:
            print(f"Video benchmark failed ({type(exc).__name__}): {exc}", file=sys.stderr)
            return 1
    elif args.install_transcription_model:
        try:
            from .audio import install_local_model

            install_local_model()
            print("Local transcription model installed")
        except Exception as exc:
            print(f"Model installation failed ({type(exc).__name__}): {exc}", file=sys.stderr)
            return 1
    elif args.check_audio:
        try:
            from .audio import run_audio_replay

            print(run_audio_replay())
        except Exception as exc:
            print(f"Audio replay failed ({type(exc).__name__}): {exc}", file=sys.stderr)
            return 1
    elif args.benchmark_audio:
        try:
            from .audio import run_audio_benchmark

            print(run_audio_benchmark(args.seconds))
        except Exception as exc:
            print(f"Audio benchmark failed ({type(exc).__name__}): {exc}", file=sys.stderr)
            return 1
    else:
        show_window(summary)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
