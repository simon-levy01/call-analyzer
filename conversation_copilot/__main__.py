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


def show_window(summary: str) -> None:
    import tkinter as tk
    from tkinter import messagebox

    from .video import LiveVideoSession
    from .windows import list_call_windows

    root = tk.Tk()
    root.title("Conversation Copilot")
    root.minsize(620, 520)
    tk.Label(root, text=summary, justify="left", padx=12, pady=8).pack(anchor="w")
    tk.Label(root, text="Visible call windows").pack(anchor="w", padx=12)
    window_list = tk.Listbox(root, height=7)
    window_list.pack(fill="x", padx=12, pady=4)
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
    thumbnail_label = tk.Label(root, text="No selected face", width=160, height=120)
    thumbnail_label.pack(pady=12)

    windows = []
    session: LiveVideoSession | None = None
    thumbnail_photo = None

    def set_running(running: bool) -> None:
        window_list.configure(state="disabled" if running else "normal")
        refresh_button.configure(state="disabled" if running else "normal")
        start_button.configure(state="disabled" if running else "normal")
        stop_button.configure(state="normal" if running else "disabled")
        switch_button.configure(
            text="Switch face", state="normal" if running else "disabled"
        )

    def refresh() -> None:
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

    def stop() -> None:
        nonlocal session, thumbnail_photo
        current, session = session, None
        if current:
            try:
                current.stop()
            except (RuntimeError, TimeoutError) as exc:
                status_label.configure(text=f"Stop failed ({type(exc).__name__})")
            else:
                status_label.configure(text=current.snapshot().status)
        thumbnail_photo = None
        thumbnail_label.configure(image="", text="No selected face")
        set_running(False)

    def start() -> None:
        nonlocal session
        selection = window_list.curselection()
        if not selection:
            messagebox.showinfo("Conversation Copilot", "Choose a call window first.")
            return
        window = windows[selection[0]]
        selected_label.configure(text=f"Selected: {window.display_name}")
        status_label.configure(text="Starting")
        root.update_idletasks()
        try:
            session = LiveVideoSession(window)
            session.start()
        except BaseException as exc:
            session = None
            status_label.configure(text=f"Capture could not start ({type(exc).__name__})")
            return
        set_running(True)

    def switch() -> None:
        if session:
            if session.snapshot().status == "Face lost":
                session.continue_tracking()
            else:
                session.switch_face()

    def poll() -> None:
        nonlocal session, thumbnail_photo
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
                height, width = snapshot.thumbnail_rgb.shape[:2]
                ppm = f"P6 {width} {height} 255\n".encode() + snapshot.thumbnail_rgb.tobytes()
                thumbnail_photo = tk.PhotoImage(data=ppm, format="PPM")
                thumbnail_label.configure(image=thumbnail_photo, text="")
            else:
                thumbnail_photo = None
                thumbnail_label.configure(image="", text="No selected face")
            if not current.worker_alive and not current.capture.worker_alive:
                stop()
        root.after(100, poll)

    def close() -> None:
        if session:
            stop()
        root.destroy()

    refresh_button.configure(command=refresh)
    start_button.configure(command=start)
    stop_button.configure(command=stop)
    switch_button.configure(command=switch)
    root.protocol("WM_DELETE_WINDOW", close)
    refresh()
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
        except BaseException as exc:
            print(f"Video check failed ({type(exc).__name__}): {exc}", file=sys.stderr)
            return 1
    elif args.check_video_capture:
        try:
            from .mock_call import run_video_capture_check

            print(run_video_capture_check())
        except BaseException as exc:
            print(
                f"Video capture check failed ({type(exc).__name__}): {exc}",
                file=sys.stderr,
            )
            return 1
    elif args.benchmark_video:
        try:
            from .benchmark import run_benchmark

            print(run_benchmark(args.seconds))
        except BaseException as exc:
            print(f"Video benchmark failed ({type(exc).__name__}): {exc}", file=sys.stderr)
            return 1
    else:
        show_window(summary)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
