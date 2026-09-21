import argparse
import json
import os
import sqlite3
import sys
import textwrap
from datetime import datetime, timedelta, timezone
from pathlib import Path

from pydantic import ValidationError

from . import test_log

from .parser import parse_whatsapp_transcript
from .memory import (
    format_memory_date,
    memory_retrieval_inputs,
    memory_semantic_input,
    parse_memory_date,
)

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


def _relabel_contact_turns(turns, speaker_name: str) -> None:
    from .models import SpeakerRole

    for turn in turns:
        if turn.speaker_role == SpeakerRole.SELECTED_CONTACT:
            turn.speaker_name = speaker_name


def _vocal_observation_from_audio(draft, display_order: int):
    if draft.vocal is None:
        return None
    from .interpretation import VocalObservation

    vocal = draft.vocal
    return VocalObservation(
        turn_display_order=display_order,
        available=vocal.available,
        duration_seconds=vocal.duration_seconds,
        relative_energy=vocal.relative_energy,
        voiced_ratio=vocal.voiced_ratio,
        words_per_voiced_second=vocal.words_per_voiced_second,
        gap_seconds=vocal.gap_seconds,
        overlaps_user=vocal.overlaps_user,
        unavailable_reason=vocal.unavailable_reason,
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
    from tkinter import filedialog, messagebox, simpledialog, ttk

    from .audio import (
        AudioCallSession,
        AudioDeviceCatalog,
        AudioUnavailable,
        DEFAULT_MICROPHONE_THRESHOLD,
        device_labels,
        local_model_available,
        prepare_transcription_runtime,
        production_transcription_language,
        transcription_language_labels,
    )
    from .interpretation import (
        CoordinatorEventKind,
        InterpretationAuthenticationUnavailable,
        InterpretationBudgetExceeded,
        InterpretationCoordinator,
        LUNA_MODEL,
        TERRA_MODEL,
        OpenAIInterpreter,
        RetrievedMemoryContext,
        StableInterpretationCard,
        UsageLedger,
        VisualAggregator,
        VocalObservation,
        build_snapshot,
        conservative_request_cost,
        format_interpretation_body,
        local_openai_api_key,
        save_local_openai_api_key,
        prepare_interpretation_request,
    )
    from .models import ConversationTurn, SpeakerRole
    from .guidance import CATEGORIES, GuidanceDisplay, interpret_guidance
    from .ask_memory import AskSession, memory_source, validate_sources, cloud_answer, ASK_INPUT_LIMIT, ASK_OUTPUT_LIMIT
    from .post_call import process_review, review_estimate
    from .memory import (
        AmbiguousContact,
        MEMORY_TYPES,
        MemoryStore,
        MemoryStoreUnavailable,
        OpenAIMemoryExtractor,
        analyze_record,
        extraction_maximum_cost,
    )
    audio_runtime_error = ""
    try:
        if not local_model_available():
            raise AudioUnavailable("Local transcription model is not installed")
        prepare_transcription_runtime()
    except Exception as exc:
        audio_runtime_error = str(exc) or f"Local transcription unavailable ({type(exc).__name__})"
    from .video import LiveVideoSession
    from .windows import list_call_windows, whatsapp_call_active

    test_log.start()
    root = tk.Tk()
    root.title("Conversation Copilot")
    settings_path = Path(os.environ.get("APPDATA", str(Path.home()))) / "ConversationCopilot" / "settings.json"
    try:
        ui_settings = json.loads(settings_path.read_text(encoding="utf-8"))
    except (OSError, ValueError, TypeError):
        ui_settings = {}
    root.geometry("1120x730")
    root.minsize(900, 640)
    root.configure(bg="#f4f1eb")
    style = ttk.Style(root)
    style.configure("Primary.TButton", font=("Segoe UI", 10, "bold"), padding=(12, 8))
    style.configure("Quiet.TButton", padding=(9, 6))
    screen_host = tk.Frame(root, bg="#f4f1eb")
    screen_host.pack(fill="both", expand=True)
    home_screen = tk.Frame(screen_host, bg="#f4f1eb")
    live_screen = tk.Frame(screen_host, bg="#f4f1eb")
    home_screen.pack(fill="both", expand=True)

    home_header = tk.Frame(home_screen, bg="#f4f1eb")
    home_header.pack(fill="x", padx=22, pady=(18, 10))
    tk.Label(home_header, text="Conversation Copilot", font=("Segoe UI", 22, "bold"), bg="#f4f1eb").pack(side="left")
    settings_button = ttk.Button(home_header, text="Settings", style="Quiet.TButton")
    settings_button.pack(side="right")
    home_body = tk.Frame(home_screen, bg="#f4f1eb")
    home_body.pack(fill="both", expand=True, padx=18, pady=(0, 18))
    home_body.columnconfigure(0, weight=3, uniform="home")
    home_body.columnconfigure(1, weight=2, uniform="home")
    home_body.rowconfigure(0, weight=1)
    left_column = tk.Frame(home_body, bg="#f4f1eb")
    left_column.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
    home_right = tk.Frame(home_body, bg="#f4f1eb")
    home_right.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
    memory_store = None
    memory_startup_error = ""
    semantic_backfill_lock = threading.Lock()
    semantic_backfill_requested = False
    try:
        memory_store = MemoryStore()
    except MemoryStoreUnavailable as exc:
        memory_startup_error = str(exc)
    contact_frame = tk.LabelFrame(left_column, text="Contact", font=("Segoe UI", 10, "bold"), bg="#ffffff", padx=8, pady=6)
    contact_frame.pack(fill="x", pady=(0, 10))
    contact_query = tk.Entry(contact_frame)
    contact_query.grid(row=0, column=0, sticky="ew", padx=4, pady=4)
    contact_box = ttk.Combobox(contact_frame, state="readonly", width=35)
    contact_box.grid(row=0, column=1, columnspan=2, sticky="ew", padx=4, pady=4)
    contact_search_button = tk.Button(contact_frame, text="Search")
    contact_search_button.grid(row=0, column=3, padx=3)
    contact_select_button = tk.Button(contact_frame, text="Select")
    contact_select_button.grid(row=0, column=4, padx=3)
    contact_create_button = tk.Button(contact_frame, text="Create Contact")
    contact_create_button.grid(row=1, column=0, padx=3, pady=4, sticky="ew")
    contact_clear_button = tk.Button(contact_frame, text="Clear")
    contact_clear_button.grid(row=1, column=1, padx=3, pady=4, sticky="ew")
    memory_manage_button = tk.Button(contact_frame, text="Manage memory")
    memory_manage_button.grid(row=1, column=2, padx=3, pady=4, sticky="ew")
    import_button = tk.Button(contact_frame, text="Import chat")
    import_button.grid(row=1, column=3, padx=3, pady=4, sticky="ew")
    unassigned_button = tk.Button(contact_frame, text="Unassigned")
    contact_frame.columnconfigure(0, weight=1)
    contact_frame.columnconfigure(1, weight=1)
    confirmed_contact_label = tk.Label(contact_frame, text="Confirmed contact: none", anchor="w")
    confirmed_contact_label.grid(row=2, column=0, columnspan=5, sticky="ew", padx=6)
    memory_status_label = tk.Label(
        contact_frame,
        text=(memory_startup_error or "No contact confirmed — retrieval and extraction are off"),
        anchor="w",
    )
    memory_status_label.grid(row=3, column=0, columnspan=5, sticky="ew", padx=6, pady=(0, 5))
    tk.Label(
        contact_frame,
        text="Assigned calls retain attributed text locally; after Stop, bounded text may be sent to OpenAI for proposals (store=false).",
        fg="#7a3f00",
        anchor="w",
    ).grid(row=4, column=0, columnspan=5, sticky="ew", padx=6, pady=(0, 5))
    audio_controls = tk.LabelFrame(left_column, text="Audio", font=("Segoe UI", 10, "bold"), bg="#ffffff", padx=8, pady=6)
    audio_controls.pack(fill="x", pady=(0, 10))
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
        values=transcription_language_labels(),
        width=16,
    )
    language_box.current(0)
    language_box.grid(row=3, column=1, sticky="w", padx=6, pady=4)
    tk.Label(audio_controls, text="Mic threshold (lower = more sensitive)").grid(row=4, column=0, sticky="w", padx=6, pady=4)
    sensitivity = tk.Scale(audio_controls, from_=50, to=2_000, resolution=50, orient="horizontal")
    sensitivity.set(DEFAULT_MICROPHONE_THRESHOLD)
    sensitivity.grid(row=4, column=1, sticky="ew", padx=6, pady=4)
    audio_controls.columnconfigure(1, weight=1)
    controls = tk.LabelFrame(home_right, text="Call window", font=("Segoe UI", 10, "bold"), bg="#ffffff", padx=8, pady=8)
    controls.pack(fill="x", pady=(0, 10))
    window_list = tk.Listbox(controls, height=6, exportselection=False)
    window_list.pack(fill="x", pady=(0, 6))
    refresh_button = tk.Button(controls, text="Refresh")
    refresh_button.pack(side="left")
    selected_label = tk.Label(controls, text="Selected: none", anchor="w", bg="#ffffff")
    selected_label.pack(side="left", fill="x", expand=True, padx=8)

    model_frame = tk.LabelFrame(home_right, text="Live and Ask model", font=("Segoe UI", 10, "bold"), bg="#ffffff", padx=8, pady=8)
    model_frame.pack(fill="x", pady=(0, 10))
    live_model_choice = tk.StringVar(value="Luna low")
    model_box = ttk.Combobox(model_frame, state="readonly", textvariable=live_model_choice, values=("Luna low", "Terra low"))
    model_box.pack(fill="x")
    tk.Label(model_frame, text="Review and memory generation always use Terra low. Usage is cumulative and shown during calls.", bg="#ffffff", fg="#555555", justify="left", wraplength=360).pack(fill="x", pady=(6, 0))

    home_actions = tk.LabelFrame(home_right, text="Prepare", font=("Segoe UI", 10, "bold"), bg="#ffffff", padx=8, pady=8)
    home_actions.pack(fill="x", pady=(0, 10))
    ask_button = tk.Button(home_actions, text="Ask Memory")
    ask_button.pack(fill="x", pady=2)
    review_button = tk.Button(home_actions, text="Conversation history")
    review_button.pack(fill="x", pady=2)
    start_button = ttk.Button(home_right, text="Start call", style="Primary.TButton")
    start_button.pack(fill="x", pady=(2, 8))
    status_label = tk.Label(home_right, text="Select a call window", anchor="w", justify="left", bg="#f4f1eb", wraplength=400)
    status_label.pack(fill="x")
    audio_status_label = tk.Label(home_right, text="Audio devices loading", anchor="w", justify="left", bg="#f4f1eb", wraplength=400)
    audio_status_label.pack(fill="x", pady=(3, 0))

    live_header = tk.Frame(live_screen, bg="#f4f1eb")
    live_header.pack(fill="x", padx=12, pady=(10, 5))
    live_contact_label = tk.Label(live_header, text="Live call", font=("Segoe UI", 15, "bold"), bg="#f4f1eb")
    live_contact_label.pack(side="left")
    stop_button = ttk.Button(live_header, text="End call", style="Primary.TButton", state="disabled")
    stop_button.pack(side="right")
    live_meta_label = tk.Label(live_screen, text="Luna low · $0.0000 this call", anchor="w", bg="#f4f1eb", fg="#555555")
    live_meta_label.pack(fill="x", padx=12)
    live_status = tk.Frame(live_screen, bg="#ffffff", bd=1, relief="solid")
    live_status.pack(fill="x", padx=12, pady=6)
    live_audio_label = tk.Label(live_status, text="Audio starting", bg="#ffffff", anchor="w")
    live_audio_label.pack(side="left", padx=8, pady=6)
    live_face_label = tk.Label(live_status, text="Face selected", bg="#ffffff", anchor="w")
    live_face_label.pack(side="left", padx=8, pady=6)
    switch_button = tk.Button(live_status, text="Switch face", state="disabled")
    switch_button.pack(side="right", padx=6, pady=4)
    suggest_button = tk.Button(live_status, text="Refresh all", state="disabled")
    suggest_button.pack(side="right", padx=2, pady=4)

    hidden_state = tk.Frame(live_screen)
    metrics_label = tk.Label(hidden_state, text="")
    interpretation_frame = tk.Frame(hidden_state)
    interpretation_status_label = tk.Label(
        interpretation_frame,
        text="Waiting for a call",
        anchor="w",
        font=("TkDefaultFont", 10, "bold"),
    )
    interpretation_status_label.pack()
    interpretation_body_label = tk.Label(
        interpretation_frame,
        text="Hypotheses only — never a claim about true emotion or intention.",
        anchor="w",
        justify="left",
        wraplength=710,
    )
    interpretation_body_label.pack()
    interpretation_meta_label = tk.Label(
        interpretation_frame,
        text="This call's estimated interpretation spend: $0.0000",
        anchor="w",
    )
    interpretation_meta_label.pack()
    terra_controls = tk.Frame(hidden_state)
    tk.Label(terra_controls, text="Reasoning").pack(side="left")
    terra_reasoning = ttk.Combobox(
        terra_controls, state="disabled", values=("low",), width=8
    )
    terra_reasoning.current(0)
    terra_reasoning.pack(side="left", padx=6)
    terra_button = tk.Button(
        terra_controls, text="Check now", state="disabled"
    )
    terra_button.pack(side="left")
    guidance_frame = tk.Frame(live_screen, bg="#f4f1eb")
    guidance_frame.pack(fill="both", expand=True, padx=12, pady=(0, 6))
    guidance_status = tk.Label(guidance_frame, text="Select a contact to enable guidance", anchor="w", bg="#f4f1eb", wraplength=460)
    guidance_status.pack(fill="x")
    guidance_rows = {}
    guidance_display = GuidanceDisplay()
    for category, label in (("tones", "Possible tone"), ("social_cues", "Social cue"), ("replies", "Potential responses"), ("remember", "Related memory"), ("follow_up", "Follow-up")):
        group = tk.LabelFrame(guidance_frame, text=label, font=("Segoe UI", 9, "bold"), bg="#ffffff", padx=5, pady=3)
        group.pack(fill="x", pady=2)
        guidance_rows[category] = group
    live_footer = tk.Frame(live_screen, bg="#f4f1eb")
    live_footer.pack(fill="x", padx=12, pady=(0, 10))
    transcript_button = tk.Button(live_footer, text="Transcript")
    transcript_button.pack(side="left")
    live_ask_button = tk.Button(live_footer, text="Ask Memory")
    live_ask_button.pack(side="left", padx=5)
    thumbnail_label = tk.Label(hidden_state, text="No selected face")
    transcript_title = tk.Label(hidden_state, text="Finalized attributed text")
    transcript = tk.Text(hidden_state, state="disabled", wrap="word")

    windows = []
    session: LiveVideoSession | None = None
    audio_catalog: AudioDeviceCatalog | None = None
    audio_session: AudioCallSession | None = None
    turns: list[ConversationTurn] = []
    vocal_observations: list[VocalObservation] = []
    visual_aggregator = VisualAggregator()
    capture_clock_origin = datetime.now(timezone.utc) - timedelta(seconds=time.perf_counter())
    usage_ledger: UsageLedger | None = None
    stable_interpretation = StableInterpretationCard()
    interpretation_coordinator: InterpretationCoordinator | None = None
    interpretation_generation = 0
    guidance_topic_start = 0
    next_interpretation_snapshot_id = 0
    latest_interpretation_snapshot = None
    interpretation_updated_at = ""
    manual_terra_running = False
    manual_terra_results: queue.SimpleQueue[tuple] = queue.SimpleQueue()
    memory_snapshot_results: queue.SimpleQueue[tuple] = queue.SimpleQueue()
    memory_analysis_results: queue.SimpleQueue[tuple] = queue.SimpleQueue()
    contact_choices = []
    selected_contact_id: str | None = None
    selected_contact_label: str | None = None
    call_speaker_fallback = "Contact"
    current_record_id: str | None = None
    stopping = False
    stop_started = 0.0
    shutdown_handoff: queue.SimpleQueue[str] = queue.SimpleQueue()
    thumbnail_photo = None
    local_active = False
    local_pending = {"ask": None, "live": None}
    local_done = queue.SimpleQueue()
    ask_dialog = None
    outside_ask_ledger = UsageLedger.product()
    review_running = set()
    review_errors = {}
    review_dialogs = {}
    review_results = queue.SimpleQueue()

    def apply_readability() -> None:
        import tkinter.font as tkfont
        size = {"Default": 9, "Large": 11, "Extra large": 13}.get(ui_settings.get("text_size"), 9)
        for name in ("TkDefaultFont", "TkTextFont", "TkMenuFont"):
            tkfont.nametofont(name).configure(size=size)
        high = bool(ui_settings.get("high_contrast"))
        def recolor(widget):
            options = widget.configure()
            try:
                if "background" in options and not isinstance(widget, (tk.Entry, tk.Text, tk.Listbox)):
                    if high:
                        if not hasattr(widget, "_normal_background"):
                            widget._normal_background = widget.cget("background")
                        widget.configure(background="#000000")
                    elif hasattr(widget, "_normal_background"):
                        widget.configure(background=widget._normal_background)
                if "foreground" in options and not isinstance(widget, (tk.Entry, tk.Text, tk.Listbox)):
                    if high:
                        if not hasattr(widget, "_normal_foreground"):
                            widget._normal_foreground = widget.cget("foreground")
                        widget.configure(foreground="#ffffff")
                    elif hasattr(widget, "_normal_foreground"):
                        widget.configure(foreground=widget._normal_foreground)
            except tk.TclError:
                pass
            for child in widget.winfo_children():
                recolor(child)
        recolor(root)

    def selected_live_model():
        return TERRA_MODEL if live_model_choice.get().startswith("Terra") else LUNA_MODEL

    def submit_local(kind, work):
        local_pending[kind] = work

    def poll_local():
        nonlocal local_active
        try:
            local_done.get_nowait()
            local_active = False
        except queue.Empty:
            pass
        if local_active:
            return
        for kind in ("ask", "live"):
            work = local_pending[kind]
            if work is not None:
                local_pending[kind] = None
                local_active = True
                def run(work=work):
                    try:
                        work()
                    finally:
                        local_done.put(True)
                threading.Thread(target=run, name="bounded-local-retrieval", daemon=True).start()
                break

    def source_current(sources, **kwargs):
        try:
            return validate_sources(memory_store, sources, **kwargs)
        except sqlite3.Error:
            return None

    def show_evidence(parent, text, valid):
        preview = tk.Toplevel(parent)
        preview.title("Exact local source")
        box = tk.Text(preview, wrap="word", height=18, width=80)
        box.pack(fill="both", expand=True)
        box.insert("1.0", text)
        box.configure(state="disabled")
        def validate_preview():
            if not preview.winfo_exists():
                return
            try:
                current = valid()
            except sqlite3.Error:
                current = None
            except (ValueError, KeyError):
                current = False
            content = text if current else ("Memory store busy — retrying source validation." if current is None
                      else "Source changed or was deleted. Reopen current evidence.")
            if box.get("1.0", "end-1c") != content:
                box.configure(state="normal")
                box.delete("1.0", tk.END)
                box.insert("1.0", content)
                box.configure(state="disabled")
            if current is False:
                return
            preview.after(250, validate_preview)
        validate_preview()
        return preview

    def render_guidance():
        update = guidance_display.filter_update(stable_interpretation.update) if stable_interpretation.update else None
        displayed = {
            category: ((list(getattr(update, category)) if update else [])
                       if category in {"tones", "social_cues"} else guidance_display.visible(category))
            for category in guidance_rows
        }
        test_log.emit("display_guidance", contact_id=selected_contact_id, items=displayed)
        guidance_status.configure(text=(
            "Suggestions are possibilities, not facts."
            if selected_contact_id else "Confirm a contact to enable memory-aware guidance."
        ))

        def exact_sources(candidate):
            evidence_generation = interpretation_generation
            evidence = candidate.evidence if hasattr(candidate, "evidence") else candidate
            matching = [turn for turn in turns if turn.display_order in evidence.turn_ids]
            sources = []
            lines = [f"{turn.timestamp}: {turn.speaker_name}: {turn.content}" for turn in matching]
            if memory_store and selected_contact_id:
                revisions = {*evidence.memory_ids, *getattr(evidence, "preference_ids", [])}
                for revision_id in revisions:
                    row = memory_store._connection.execute(
                        "SELECT memory_id FROM memory_revisions WHERE id=?", (revision_id,)
                    ).fetchone()
                    source = memory_source(memory_store, row[0], selected_contact_id, display_limit=None) if row else None
                    if source and source.revision_id == revision_id:
                        sources.append(source)
                        lines.append(f"{source.kind} · {source.source_date}: {source.content}")
            return "\n\n".join(lines) or "Exact source is no longer available.", lambda: (
                evidence_generation == interpretation_generation and not stopping
                and all(turn in turns for turn in matching)
                and validate_sources(memory_store, tuple(sources), display_limit=None)
            )

        def pop_out(category, candidate, content, why=""):
            popup = tk.Toplevel(root)
            popup.title(guidance_rows[category].cget("text"))
            popup.geometry("430x230")
            tk.Label(popup, text=content, font=("Segoe UI", 12, "bold"), wraplength=390,
                     justify="left", anchor="w").pack(fill="x", padx=14, pady=(14, 5))
            if why:
                tk.Label(popup, text=why, wraplength=390, justify="left", anchor="w",
                         fg="#555555").pack(fill="x", padx=14)
            tk.Label(popup, text=f"Captured {datetime.now().astimezone().strftime('%H:%M:%S')} · {selected_contact_label or 'No contact'}",
                     fg="#666666").pack(anchor="w", padx=14, pady=8)
            actions = tk.Frame(popup)
            actions.pack(fill="x", padx=14, pady=8)
            def open_sources():
                try:
                    text, valid = exact_sources(candidate)
                    show_evidence(popup, text, valid)
                except (sqlite3.Error, ValueError, KeyError):
                    messagebox.showinfo("Sources", "Exact source is unavailable; reopen the current suggestion.", parent=popup)
            tk.Button(actions, text="Sources", command=open_sources).pack(side="left")
            tk.Button(actions, text="Close", command=popup.destroy).pack(side="right")

        for category, group in guidance_rows.items():
            for child in group.winfo_children():
                child.destroy()
            items = displayed[category]
            if not items:
                tk.Label(group, text="Nothing useful to show yet.", bg="#ffffff", fg="#777777",
                         anchor="w").pack(fill="x")
                continue
            for index, wrapped in enumerate(items):
                candidate = wrapped if category in {"tones", "social_cues"} else wrapped.candidate
                content = candidate.hypothesis if hasattr(candidate, "hypothesis") else candidate.text
                if category == "remember" and not content.casefold().startswith("possibly related"):
                    content = "Possibly related: " + content
                why = ""
                if category in {"tones", "social_cues"}:
                    modalities = ", ".join(str(value.value).replace("_", " ") for value in candidate.evidence.modalities)
                    why = f"Why: cautious reading of recent {modalities or 'conversation'} cues."
                row = tk.Frame(group, bg="#ffffff")
                row.pack(fill="x", pady=1)
                text = content + (f"\n{why}" if why else "")
                tk.Label(row, text=text, justify="left", wraplength=330, anchor="w", bg="#ffffff").pack(side="left", fill="x", expand=True)
                def dismiss(category=category, index=index):
                    guidance_display.dismiss(category, index, update=update)
                    render_guidance()
                tk.Button(row, text="Dismiss", command=dismiss).pack(side="right", padx=(3, 0))
                tk.Button(row, text="Pop out", command=lambda c=category, x=candidate, t=content, w=why: pop_out(c, x, t, w)).pack(side="right")

    def open_ask():
        nonlocal ask_dialog
        if memory_store is None:
            return
        if ask_dialog is not None and ask_dialog.winfo_exists():
            ask_dialog.lift()
            return
        try:
            contacts = memory_store.list_contacts(limit=10000)
        except (ValueError, KeyError, sqlite3.Error) as exc:
            memory_status_label.configure(text=f"Ask unavailable or memory store busy: {exc}")
            return
        dialog = ask_dialog = tk.Toplevel(root)
        dialog.title("Ask Memory")
        dialog.geometry("720x560")
        state = AskSession(selected_contact_id)
        results = queue.SimpleQueue()
        shown = [None]
        last_source_check = [0.0]
        running = [False]
        page = [0]
        scope = ttk.Combobox(dialog, state="readonly", values=["Choose contact", *[c.label for c in contacts]])
        scope.pack(fill="x", padx=8, pady=8)
        scope.current(next((i + 1 for i, c in enumerate(contacts) if c.id == selected_contact_id), 0))
        question = tk.Entry(dialog)
        question.pack(fill="x", padx=8)
        reference = tk.Label(dialog, text=f"Query reference: {datetime.now().astimezone().isoformat()} · date queries: DD/MM/YYYY or ISO")
        reference.pack(anchor="w", padx=8)
        date_filter = ttk.Combobox(dialog, state="readonly", values=("Clarify date meaning", "Event date", "Recorded date"))
        date_filter.current(0)
        date_filter.pack(anchor="w", padx=8)
        controls = tk.Frame(dialog)
        controls.pack(fill="x", padx=8, pady=6)
        status = tk.Label(dialog, text="Search approved memories and manually approved summaries.", anchor="w", wraplength=720, justify="left")
        status.pack(fill="x", padx=8)
        answer = tk.Text(dialog, height=10, wrap="word", state="disabled")
        answer.pack(fill="both", expand=True, padx=8, pady=6)
        source_list = tk.Listbox(dialog, height=6, exportselection=False)
        source_list.pack(fill="x", padx=8)
        source_actions = tk.Frame(dialog)
        source_actions.pack(fill="x", padx=8, pady=8)

        def clear():
            state.new_question()
            page[0] = 0
            shown[0] = None
            source_list.delete(0, tk.END)
            answer.configure(state="normal")
            answer.delete("1.0", tk.END)
            answer.configure(state="disabled")
            question.delete(0, tk.END)

        def change_scope(_event=None):
            index = scope.current()
            clear()
            state.set_scope(contacts[index - 1].id if index >= 1 else None)

        scope.bind("<<ComboboxSelected>>", change_scope)

        def ask(use_cloud=True, *, page_forward=False):
            if running[0]:
                return
            text = question.get().strip()
            if not 1 <= len(text) <= 500:
                status.configure(text="Enter a question of 1–500 characters.")
                return
            if not page_forward:
                page[0] = 0
            generation = state.generation
            from copy import deepcopy
            worker_state = deepcopy(state)
            query_offset = page[0]
            query_reference = datetime.now().astimezone()
            date_mode = (None, "event", "recorded")[date_filter.current()]
            reference.configure(text=f"Query reference: {query_reference.isoformat()} · date queries: DD/MM/YYYY or ISO")
            selected_sources = shown[0].sources if shown[0] else ()
            live = audio_session is not None and not stopping
            ledger = usage_ledger if live else outside_ask_ledger
            if use_cloud:
                if not state.contact_id:
                    status.configure(text="Choose one contact to search.")
                    return
            running[0] = True
            status.configure(text="Pending — capture and transcription continue.")
            worker_path = memory_store.path
            def work():
                try:
                    with MemoryStore(worker_path, verify=False) as worker_store:
                        if generation != state.generation:
                            return
                        result = cloud_answer(worker_store, text, selected_sources, ledger=ledger, live=live,
                            contact_id=worker_state.contact_id, event_id=worker_state.event_id,
                            reference=query_reference, date_mode=date_mode,
                            is_current=lambda: generation == state.generation, model=selected_live_model(), reasoning="low") if use_cloud else worker_state.answer(worker_store, text, offset=query_offset, reference=query_reference, date_mode=date_mode)
                    results.put((generation, result, None, worker_state))
                except Exception as exc:
                    results.put((generation, None, type(exc).__name__, None))
                finally:
                    results.put((generation, None, "finished", None))
            if use_cloud:
                threading.Thread(target=work, name="explicit-cloud-ask", daemon=True).start()
            else:
                submit_local("ask", work)

        tk.Button(controls, text="Submit", command=ask).pack(side="left")
        tk.Button(controls, text="New question", command=clear).pack(side="left")
        question.bind("<Return>", lambda _event: ask())

        def chosen_source():
            selected = source_list.curselection()
            return shown[0].sources[selected[0]] if selected and shown[0] else None

        def choose_event():
            source = chosen_source()
            if source is None:
                return
            state.choose_event(source.id)
            status.configure(text="Event selected. Ask a short follow-up; evidence will be checked again.")

        def preview_source():
            source = chosen_source()
            if source is None:
                return
            current = source_current((source,))
            if current is not True:
                status.configure(text="Memory store busy; retry opening the source." if current is None else "Source changed or was deleted. Ask again.")
                return
            lines = [f"{source.kind} · {source.contact_label}\nSource date: {source.source_date}\n"
                     f"Event date: {source.event_date or 'see original wording; unresolved if absent'}\n"
                     f"Confidence: {source.confidence}\n\n{source.content}"]
            if source.record_id:
                try:
                    lines += [f"Turn {turn.display_order} · {turn.timestamp} · {turn.speaker_name}: {turn.content}"
                              for turn in memory_store.record_turns(source.record_id) if turn.display_order in source.turns]
                except sqlite3.Error:
                    status.configure(text="Memory store busy; retry opening the source.")
                    return
            show_evidence(dialog, "\n\n".join(lines), lambda: validate_sources(memory_store, (source,)))

        tk.Button(source_actions, text="Choose this event", command=choose_event).pack(side="left")
        tk.Button(source_actions, text="Open exact source", command=preview_source).pack(side="left", padx=6)

        def poll_ask():
            if not dialog.winfo_exists():
                return
            while True:
                try:
                    generation, result, error, completed_state = results.get_nowait()
                except queue.Empty:
                    break
                if error == "finished":
                    running[0] = False
                    continue
                if generation != state.generation:
                    continue
                if error:
                    status.configure(text=f"Unavailable ({error}); valid local results remain available.")
                else:
                    current = source_current(result.sources)
                    if current is None:
                        running[0] = True
                        results.put((generation, result, error, completed_state))
                        status.configure(text="Memory store busy — retrying result validation.")
                        break
                    running[0] = False
                    if not current:
                        status.configure(text="Evidence changed; ask again using current approved sources.")
                        continue
                    state.questions, state.exchanges = completed_state.questions, completed_state.exchanges
                    state.event_id = completed_state.event_id
                    shown[0] = result
                    status.configure(text=f"{result.status}{' · ' + result.confidence + ' confidence' if result.confidence else ''} · {result.coverage} · {result.backend}")
                    answer.configure(state="normal")
                    answer.delete("1.0", tk.END)
                    answer.insert("1.0", result.answer)
                    answer.configure(state="disabled")
                    source_list.delete(0, tk.END)
                    for source in result.sources:
                        source_list.insert(tk.END, f"{source.contact_label} · {source.kind} · {source.source_date[:10]} · {source.content}")
            if shown[0] and time.perf_counter() - last_source_check[0] >= 1:
                last_source_check[0] = time.perf_counter()
                current = source_current(shown[0].sources)
                if current is None:
                    status.configure(text="Memory store busy — retrying source validation.")
                elif current is False:
                    clear()
                    status.configure(text="Evidence changed; ask again using current approved sources.")
                elif str(status.cget("text")).startswith("Memory store busy"):
                    status.configure(text=f"{shown[0].status} · {shown[0].coverage} · {shown[0].backend}")
            dialog.after(150, poll_ask)

        def close_ask():
            nonlocal ask_dialog
            state.close()
            shown[0] = None
            ask_dialog = None
            dialog.destroy()
            schedule_semantic_backfill()

        dialog.protocol("WM_DELETE_WINDOW", close_ask)
        dialog.after(150, poll_ask)
        question.focus_set()

    ask_button.configure(command=open_ask)
    live_ask_button.configure(command=open_ask)

    def open_transcript() -> None:
        dialog = tk.Toplevel(root)
        dialog.title("Live transcript")
        dialog.geometry("520x540")
        box = tk.Text(dialog, wrap="word", state="normal")
        box.pack(fill="both", expand=True, padx=10, pady=10)
        box.insert("1.0", "".join(f"{turn.speaker_name}: {turn.content}\n" for turn in turns)
                   or "No finalized transcript text yet.")
        box.configure(state="disabled")
        tk.Button(dialog, text="Close", command=dialog.destroy).pack(pady=(0, 10))

    transcript_button.configure(command=open_transcript)

    def open_review(record_id=None):
        if memory_store is None:
            return
        if record_id is None:
            if selected_contact_id is None:
                messagebox.showinfo("Review conversation", "Select a contact first.", parent=root)
                return
            try:
                records = memory_store.list_records(selected_contact_id)
            except (ValueError, KeyError, sqlite3.Error) as exc:
                memory_status_label.configure(text=f"Review unavailable or memory store busy: {exc}")
                return
            chooser = tk.Toplevel(root)
            chooser.title("Review one conversation")
            choices = tk.Listbox(chooser, width=85)
            choices.pack(fill="both", expand=True)
            for record in records:
                choices.insert(tk.END, f"{record['source_label']} · {record['started_at'] or record['created_at']} · {record['status']}")
            def choose():
                if choices.curselection():
                    chosen = records[choices.curselection()[0]]["id"]
                    chooser.destroy()
                    open_review(chosen)
            tk.Button(chooser, text="Review selected record", command=choose).pack()
            return
        existing = review_dialogs.get(record_id)
        if existing is not None and existing.winfo_exists():
            existing.lift()
            existing.focus_set()
            return
        dialog = tk.Toplevel(root)
        review_dialogs[record_id] = dialog
        dialog.bind("<Destroy>", lambda event: review_dialogs.pop(record_id, None) if event.widget is dialog else None)
        dialog.title("Summary and memories")
        dialog.geometry("1120x720")
        review_header = tk.Frame(dialog)
        review_header.pack(fill="x", padx=12, pady=(10, 3))
        tk.Label(review_header, text="Summary and memories", font=("Segoe UI", 18, "bold")).pack(side="left")
        tk.Button(review_header, text="Back to Home", command=dialog.destroy).pack(side="right")
        label = tk.Label(dialog, text="Draft · not searchable until approved", anchor="w")
        label.pack(fill="x", padx=12, pady=(0, 8))
        panes = tk.PanedWindow(dialog, orient=tk.HORIZONTAL)
        panes.pack(fill="both", expand=True)
        summary_panel = tk.Frame(panes)
        memory_panel = tk.LabelFrame(panes, text="Memories from this conversation")
        panes.add(summary_panel, stretch="always", minsize=480)
        panes.add(memory_panel, stretch="always", minsize=360)
        narrative = tk.Text(summary_panel, wrap="word", height=12, state="disabled")
        narrative.pack(fill="both", expand=True, padx=8)
        tk.Label(summary_panel, text="Click a sentence to select it for editing or source review.").pack(anchor="w", padx=8)
        listing = tk.Listbox(summary_panel, width=65, height=3, exportselection=False)
        listing.pack(fill="both", expand=True, padx=8)
        memories = tk.Listbox(memory_panel, exportselection=False, selectmode="extended", width=50)
        memories.pack(fill="both", expand=True, padx=8, pady=8)
        memory_scroll = ttk.Scrollbar(memory_panel, orient="horizontal", command=memories.xview)
        memory_scroll.pack(fill="x", padx=8)
        memories.configure(xscrollcommand=memory_scroll.set)
        memory_rows = []
        rows = []
        version_id = [None]
        def edit_review_memory():
            if not memories.curselection():
                return
            item = memory_rows[memories.curselection()[0]]
            if item["state"] not in {"approved", "pending"}:
                return
            content = simpledialog.askstring("Edit linked memory", "Corrected fact (up to 280 characters):", initialvalue=item["content"], parent=dialog)
            if content is None:
                return
            try:
                linked = memory_store._connection.execute("SELECT DISTINCT s.* FROM summary_statements s JOIN summary_dependencies d ON d.statement_id=s.id WHERE (d.memory_id=? OR d.proposal_id=?) AND s.excluded=0", (item["id"], item["id"])).fetchall()
                choices = {}
                for sentence in linked:
                    choice = messagebox.askyesnocancel("Update linked summary sentence", f"Replace this sentence with the corrected fact?\n{sentence['content']}\n\nNew: {content}\nYes: sync this sentence. No: retain its prior wording. Cancel: discard edit.", parent=dialog)
                    if choice is None:
                        return
                    choices[sentence["id"]] = "update" if choice else "keep"
                if item["state"] == "approved":
                    memory_store.correct_memory(item["id"], content, expected_revision_id=item["revision"], summary_choices=choices, normalized_date_start=None)
                else:
                    memory_store.edit_pending_review_memory(item["id"], content, expected_content=item["content"], summary_ids=[sid for sid, choice in choices.items() if choice == "update"])
                invalidate_memory_context()
                reload()
            except (ValueError, KeyError, sqlite3.Error) as exc:
                label.configure(text=f"Edit unavailable: {exc}")
        def approve_review_memories(approve=True):
            chosen = [memory_rows[i] for i in memories.curselection() if memory_rows[i]["state"] == "pending"]
            if not chosen or not messagebox.askyesno("Review selected memories", f"{'Approve' if approve else 'Reject'} these memories?\n\n" + "\n".join(item["content"] for item in chosen), parent=dialog):
                return
            try:
                memory_store.review_record_proposals(
                    record_id, [item["id"] for item in chosen], approve=approve,
                    expected_pending={item["id"]: item["content"] for item in chosen},
                )
                invalidate_memory_context()
                reload()
            except (ValueError, KeyError, sqlite3.Error) as exc:
                label.configure(text=f"Memory review unavailable: {exc}")
        def review_all_memories(approve=True):
            pending = [dict(row) for row in memory_store.record_pending_proposals(record_id)]
            if not pending or not messagebox.askyesno("Review all memories", f"{'Approve' if approve else 'Reject'} all {len(pending)} pending memories from this conversation?", parent=dialog):
                return
            try:
                memory_store.review_record_proposals(
                    record_id, None, approve=approve,
                    expected_pending={item["id"]: item["content"] for item in pending},
                )
                invalidate_memory_context()
                reload()
            except (ValueError, KeyError, sqlite3.Error) as exc:
                label.configure(text=f"Memory review unavailable: {exc}")
        memory_actions = tk.Frame(memory_panel)
        memory_actions.pack(fill="x")
        for text, command in (
            ("Select all", lambda: memories.selection_set(0, tk.END)),
            ("Clear", lambda: memories.selection_clear(0, tk.END)),
            ("Edit", edit_review_memory),
            ("Approve selected", approve_review_memories),
            ("Reject selected", lambda: approve_review_memories(False)),
            ("Approve all", review_all_memories),
            ("Reject all", lambda: review_all_memories(False)),
        ):
            tk.Button(memory_actions, text=text, command=command).pack(side="left", padx=2, pady=4)
        def reload():
            try:
                selection = listing.curselection()
                selected_id = rows[selection[0]]["id"] if selection else None
                rows.clear()
                listing.delete(0, tk.END)
                version = memory_store._connection.execute(
                    "SELECT * FROM summary_versions WHERE record_id=? ORDER BY created_at DESC,rowid DESC LIMIT 1", (record_id,)
                ).fetchone()
                version_id[0] = version["id"] if version else None
                if version:
                    label.configure(text=f"Summary {version['state']} · {'partial coverage' if version['partial'] else 'bounded coverage'} · Approval includes its linked pending memories.")
                    if len(memory_store.summary_turns(record_id, for_cloud=True)) < len(memory_store.record_turns(record_id)):
                        label.configure(text=label.cget("text") + " Source turns withheld; full-source extraction is skipped unless already reviewed.")
                    rows.extend(memory_store.summary_statements(version["id"]))
                    for row in rows:
                        listing.insert(tk.END, f"{'EXCLUDED · ' if row['excluded'] else ''}{row['section']} · {row['kind']} · {row['content']}")
                    for index, row in enumerate(rows):
                        if row["id"] == selected_id:
                            listing.selection_set(index)
                narrative_position = narrative.yview()[0]
                narrative.configure(state="normal")
                narrative.delete("1.0", tk.END)
                paragraph = None
                for index, row in enumerate(rows):
                    if row["excluded"]:
                        continue
                    group = row["section"] in {"questions", "follow_ups"}
                    if paragraph is not None:
                        narrative.insert(tk.END, "\n\n" if group != paragraph else " ")
                    tag = f"sentence_{index}"
                    narrative.insert(tk.END, row["content"], tag)
                    def select_sentence(_event, index=index):
                        listing.selection_clear(0, tk.END)
                        listing.selection_set(index)
                    narrative.tag_bind(tag, "<Button-1>", select_sentence)
                    paragraph = group
                narrative.configure(state="disabled")
                narrative.yview_moveto(narrative_position)
                owner = memory_store._connection.execute("SELECT contact_id FROM conversation_records WHERE id=?", (record_id,)).fetchone()
                selected_memories = {memory_rows[i]["id"] for i in memories.curselection() if i < len(memory_rows)}
                memory_rows.clear()
                memories.delete(0, tk.END)
                if owner and owner[0]:
                    for item in memory_store.list_current_memories(owner[0]):
                        if memory_store._connection.execute("SELECT 1 FROM memory_sources WHERE revision_id=? AND record_id=?", (item["revision_id"], record_id)).fetchone():
                            memory_rows.append({"id": item["memory_id"], "revision": item["revision_id"], "content": item["content"], "state": "approved"})
                    for item in memory_store.list_proposals(owner[0]):
                        if item["state"] != "approved" and memory_store._connection.execute("SELECT 1 FROM proposal_batches WHERE id=? AND record_id=?", (item["batch_id"], record_id)).fetchone():
                            memory_rows.append({"id": item["id"], "content": item["content"], "state": item["state"]})
                for index, item in enumerate(memory_rows):
                    memories.insert(tk.END, f"{'☐ ' if item['state'] == 'pending' else ''}{item['state']} · {item['content']}")
                    if item["id"] in selected_memories:
                        memories.selection_set(index)
                if not version:
                    label.configure(text="No summary yet. Generate one bounded review after seeing its estimate.")
                job = memory_store._connection.execute("SELECT state FROM review_jobs WHERE record_id=?", (record_id,)).fetchone()
                busy = record_id in review_running or bool(job and job[0] == "running")
                if busy:
                    label.configure(text="Generating summary and memories… Please wait until all chunks are complete.")
                else:
                    if job and job[0] == "pending":
                        reason = review_errors.get(record_id, "Review paused or interrupted")
                        label.configure(text=f"{reason}. Partial results saved; Process remaining resumes from the last completed chunk.")
                for button in controls.winfo_children():
                    button.configure(state="disabled" if busy else "normal")
                for button in memory_actions.winfo_children():
                    button.configure(state="disabled" if busy else "normal")
            except (ValueError, KeyError, sqlite3.Error) as exc:
                label.configure(text=f"Source unavailable or memory store busy: {exc}")

        controls = tk.Frame(summary_panel)
        controls.pack(fill="x", padx=8, pady=8)
        def generate():
            try:
                review_estimate(memory_store, record_id)
            except Exception as exc:
                label.configure(text=f"Review unavailable: {exc}")
                return
            start_review_job(record_id, UsageLedger.product())
        def approve():
            approving = version_id[0]
            expected = {s["id"]: (s["content"], s["excluded"]) for s in rows}
            try:
                linked = memory_store._connection.execute("SELECT DISTINCT p.id,p.content FROM memory_proposals p JOIN summary_dependencies d ON d.proposal_id=p.id JOIN summary_statements s ON s.id=d.statement_id WHERE s.summary_id=? AND s.excluded=0 AND p.state='pending'", (approving,)).fetchall()
            except sqlite3.Error as exc:
                label.configure(text=f"Approval unavailable: {exc}")
                return
            if approving and messagebox.askyesno("Approve summary and linked memories", "Approve this summary and these linked pending memories?\nRejected/excluded items remain excluded.\n\n" + "\n".join(item["content"] for item in linked), parent=dialog):
                try:
                    memory_store.approve_summary(approving, expected_pending={item["id"]: item["content"] for item in linked}, expected_statements=expected)
                except Exception as exc:
                    label.configure(text=f"Approval unavailable: {exc}")
                    return
                invalidate_memory_context()
                reload()
        def approve_everything():
            approving = version_id[0]
            if not approving:
                label.configure(text="Generate a summary before approving everything.")
                return
            expected = {s["id"]: (s["content"], s["excluded"]) for s in rows}
            pending = [dict(row) for row in memory_store.record_pending_proposals(record_id)]
            if not messagebox.askyesno("Approve all", f"Approve the summary and all {len(pending)} pending memories from this conversation?", parent=dialog):
                return
            try:
                memory_store.approve_all_memories_and_summary(
                    approving,
                    expected_pending={item["id"]: item["content"] for item in pending},
                    expected_statements=expected,
                )
                invalidate_memory_context()
                reload()
            except Exception as exc:
                label.configure(text=f"Approval unavailable: {exc}")
        def edit(remove=False, restore=False):
            if not listing.curselection():
                return
            row = rows[listing.curselection()[0]]
            content = row["content"] if remove or restore else simpledialog.askstring("Edit statement", "Save changes explicitly approves your corrected wording on an approved summary:", initialvalue=row["content"], parent=dialog)
            if content is None:
                return
            if restore and not messagebox.askyesno("Restore summary statement", "Explicitly restore this summary statement? This does not approve its rejected memory proposal.", parent=dialog):
                return
            try:
                if remove or restore:
                    memory_store.edit_summary_statement(row["id"], content, excluded=remove)
                else:
                    links = {}
                    dependencies = memory_store._connection.execute("SELECT * FROM summary_dependencies WHERE statement_id=?", (row["id"],)).fetchall()
                    for item in memory_rows:
                        if item["state"] not in {"pending", "approved"} or not any(item["id"] in (d["memory_id"], d["proposal_id"]) for d in dependencies):
                            continue
                        choice = messagebox.askyesnocancel("Update linked memory", f"Summary sentence:\n{content}\n\nAlso replace this {item['state']} memory with the corrected fact?\n{item['content']}\n\nPending memories remain pending until approval.", parent=dialog)
                        if choice is None:
                            return
                        if choice:
                            links[item["id"]] = item.get("revision", item["content"])
                    memory_store.edit_review_sentence(row["id"], content, expected_content=row["content"], links=links)
            except Exception as exc:
                label.configure(text=f"Change unavailable: {exc}")
                return
            invalidate_memory_context()
            reload()
        def delete():
            try:
                if messagebox.askyesno("Delete summary", "Delete every summary version for this conversation? Its transcript and independently approved memories remain.", parent=dialog):
                    memory_store.delete_summary(record_id)
                    invalidate_memory_context()
                    reload()
            except (ValueError, KeyError, sqlite3.Error) as exc:
                label.configure(text=f"Deletion unavailable: {exc}")

        def evidence():
            try:
                if not listing.curselection():
                    return
                row = dict(rows[listing.curselection()[0]])
                owner = memory_store._connection.execute("SELECT * FROM conversation_records WHERE id=?", (record_id,)).fetchone()
                if owner is None:
                    label.configure(text="Conversation no longer exists; reopen current evidence.")
                    return
                record = dict(owner)
                sequences = {item[0] for item in memory_store._connection.execute("SELECT sequence FROM summary_evidence WHERE statement_id=?", (row["id"],))}
                text = f"Summary {row['kind']} · {row['origin']} · {row['confidence']} confidence\n{row['content']}\n\n"
                text += "\n\n".join(f"Turn {turn.display_order} · {turn.timestamp} · {turn.speaker_name}: {turn.content}"
                                      for turn in memory_store.record_turns(record_id) if turn.display_order in sequences)
                def valid():
                    current = memory_store._connection.execute("SELECT * FROM summary_statements WHERE id=?", (row["id"],)).fetchone()
                    owner = memory_store._connection.execute("SELECT * FROM conversation_records WHERE id=?", (record_id,)).fetchone()
                    return current is not None and dict(current) == row and owner is not None and dict(owner) == record
                show_evidence(dialog, text, valid)
            except (ValueError, KeyError, sqlite3.Error) as exc:
                label.configure(text=f"Source unavailable or memory store busy: {exc}")

        def permission(allowed):
            if not listing.curselection():
                return
            row = rows[listing.curselection()[0]]
            if not messagebox.askyesno("Summary cloud permission", f"{'Allow this sensitive statement in cloud Ask when all linked memories also permit it' if allowed else 'Mark this statement sensitive and block cloud use'}?\n{row['content']}", parent=dialog):
                return
            try:
                if not allowed:
                    memory_store.mark_summary_sensitive(row["id"])
                else:
                    memory_store.set_summary_cloud_permission(row["id"], True)
                invalidate_memory_context()
                reload()
            except (ValueError, KeyError, sqlite3.Error) as exc:
                label.configure(text=str(exc))
        def review_legacy_sources():
            try:
                record = memory_store._connection.execute("SELECT * FROM conversation_records WHERE id=?", (record_id,)).fetchone()
                if record is None:
                    raise ValueError("conversation no longer exists")
                source_turns = memory_store.record_turns(record_id)
                snapshot = dict(record)
                def current():
                    row = memory_store._connection.execute("SELECT * FROM conversation_records WHERE id=?", (record_id,)).fetchone()
                    return row is not None and dict(row) == snapshot and memory_store.record_turns(record_id) == source_turns
                review = show_evidence(dialog, "Legacy deletion history: historical summaries are withheld until exact turns are reviewed.\n"
                    "Select only turns containing no previously deleted facts. Known deletion exclusions and sensitive permissions remain enforced.\n\n" +
                    "\n\n".join(f"Turn {t.display_order} · {t.timestamp} · {t.speaker_name}: {t.content}" for t in source_turns), current)
                tk.Label(review, text="Reviewed safe turn numbers, separated by commas (no selection by default):").pack()
                selected = tk.Entry(review)
                selected.pack(fill="x")
                def allow():
                    try:
                        if not current():
                            raise ValueError("source changed; reopen its review")
                        sequences = {int(value.strip()) for value in selected.get().split(",")}
                        if not messagebox.askyesno("Confirm exact source review", "I reviewed these exact turns and confirm they contain no previously deleted facts. Allow them for historical summaries?", parent=review):
                            return
                        memory_store.review_legacy_summary_turns(record_id, sequences, expected_generation=record["generation"])
                    except (ValueError, sqlite3.Error) as exc:
                        messagebox.showerror("Source review", str(exc), parent=review)
                        return
                    review.destroy()
                    reload()
                tk.Button(review, text="Allow only these reviewed turns", command=allow).pack(fill="x")
            except (ValueError, sqlite3.Error) as exc:
                label.configure(text=f"Source review unavailable: {exc}")
        def proposals():
            try:
                row = memory_store._connection.execute("SELECT contact_id FROM conversation_records WHERE id=?", (record_id,)).fetchone()
                if row and row[0]:
                    manage_memory(row[0])
                else:
                    label.configure(text="Conversation or assigned contact is unavailable.")
            except (ValueError, KeyError, sqlite3.Error) as exc:
                label.configure(text=f"Memory proposals unavailable or memory store busy: {exc}")
        def transcript_source():
            try:
                record_turns = memory_store.record_turns(record_id)
                show_evidence(dialog, "\n".join(
                    f"{turn.timestamp} · {turn.speaker_name}: {turn.content}" for turn in record_turns
                ) or "No transcript text was retained.", lambda: memory_store.record_turns(record_id) == record_turns)
            except (ValueError, KeyError, sqlite3.Error) as exc:
                label.configure(text=f"Transcript unavailable: {exc}")
        def summary_versions():
            versions = memory_store._connection.execute(
                "SELECT id,state,created_at,partial FROM summary_versions WHERE record_id=? ORDER BY created_at DESC,rowid DESC",
                (record_id,),
            ).fetchall()
            popup = tk.Toplevel(dialog)
            popup.title("Summary versions")
            listing_versions = tk.Listbox(popup, width=80, height=12)
            listing_versions.pack(fill="both", expand=True, padx=10, pady=10)
            for version in versions:
                listing_versions.insert(tk.END, f"{version['created_at']} · {version['state']} · {'partial' if version['partial'] else 'bounded'} · {version['id']}")
            tk.Button(popup, text="Close", command=popup.destroy).pack(pady=(0, 10))
        for text, command in (("Generate summary / process remaining", generate), ("Approve summary", approve),
                              ("Approve all memories + summary", approve_everything), ("Open exact source", evidence),
                              ("Edit / Save changes", edit), ("Remove statement", lambda: edit(remove=True)),
                              ("Restore excluded statement", lambda: edit(restore=True)), ("Delete summary", delete),
                              ("Review legacy source exclusions", review_legacy_sources),
                              ("Summary versions", summary_versions), ("Transcript and source", transcript_source),
                              ("Contact and data", proposals), ("Review later", dialog.destroy)):
            tk.Button(controls, text=text, command=command).pack(anchor="w", fill="x")
        def refresh_review():
            if dialog.winfo_exists():
                try:
                    reload()
                except (sqlite3.Error, ValueError):
                    label.configure(text="Source unavailable or memory store busy; review will refresh shortly.")
                finally:
                    dialog.after(1500, refresh_review)
        refresh_review()

    def start_review_job(record_id, ledger):
        if review_running:
            memory_status_label.configure(text="Another bounded review is running; this record remains available for a later explicit run.")
            return False
        review_running.add(record_id)
        review_errors.pop(record_id, None)
        worker_path = memory_store.path
        def run():
            try:
                with MemoryStore(worker_path, verify=False) as worker:
                    result = process_review(worker, record_id, ledger=ledger,
                        can_run=lambda: audio_session is None or stopping)
                review_results.put((record_id, result, None))
            except Exception as exc:
                review_results.put((record_id, None, str(exc)))
        threading.Thread(target=run, name="bounded-post-call-review", daemon=True).start()
        return True

    review_button.configure(command=open_review)

    def render_interpretation(*, replaced: bool = False, note: str = "") -> None:
        nonlocal interpretation_updated_at
        if replaced:
            interpretation_updated_at = datetime.now().astimezone().strftime("%H:%M:%S")
        update = stable_interpretation.update
        if replaced:
            test_log.emit("display_interpretation", update=update, note=note, message=stable_interpretation.message)
        if update is None:
            interpretation_status_label.configure(
                text=(
                    "Waiting for interpretation"
                    if stable_interpretation.message.startswith("Waiting")
                    else "Interpretation unavailable"
                )
            )
        else:
            interpretation_status_label.configure(
                text=update.status.value.replace("_", " ").title()
            )
        interpretation_body_label.configure(text=format_interpretation_body(
            update, stable_interpretation.message, stable_interpretation.memory_possibilities
        ))
        spend = usage_ledger.total_dollars if usage_ledger else 0.0
        warning = " · Warning threshold reached" if usage_ledger and usage_ledger.warning_reached else ""
        updated = f" · Updated {interpretation_updated_at}" if interpretation_updated_at else ""
        extra = f" · {note}" if note else ""
        interpretation_meta_label.configure(
            text=f"This call's estimated interpretation spend: ${spend:.4f}{updated}{warning}{extra}"
        )
        live_meta_label.configure(text=f"{live_model_choice.get()} · ${spend:.4f} this call")
        if replaced:
            render_guidance()

    def set_interpretation_unavailable(message: str, now: float) -> None:
        stable_interpretation.show_unavailable(message, now)
        memory_status_label.configure(
            text="No recent approved memory context is displayed"
        )

    def render_transcript_turns(visible_turns, *, replace: bool) -> None:
        transcript.configure(state="normal")
        if replace:
            transcript.delete("1.0", tk.END)
        transcript.insert(
            tk.END,
            "".join(f"{turn.speaker_name}: {turn.content}\n" for turn in visible_turns),
        )
        transcript.configure(state="disabled")
        transcript.see(tk.END)

    def refresh_contact_choices() -> None:
        nonlocal contact_choices
        if memory_store is None:
            contact_choices = []
        else:
            contact_choices = memory_store.list_contacts(contact_query.get())
        contact_box.configure(values=[item.label for item in contact_choices])
        selected_index = next(
            (index for index, item in enumerate(contact_choices) if item.id == selected_contact_id), -1
        )
        if selected_contact_id is None and contact_choices:
            contact_box.current(0)
        elif selected_index >= 0:
            contact_box.current(selected_index)
        else:
            contact_box.set("")

    def schedule_semantic_backfill() -> None:
        nonlocal semantic_backfill_requested
        semantic_backfill_requested = True
        if memory_store is None or audio_session is not None or ask_dialog is not None or not semantic_backfill_lock.acquire(blocking=False):
            return
        semantic_backfill_requested = False
        worker_path = memory_store.path

        def backfill() -> None:
            try:
                with MemoryStore(worker_path, verify=False) as worker_store:
                    worker_store.backfill_semantic_embeddings(can_run=lambda: audio_session is None and ask_dialog is None)
            except Exception:
                pass
            finally:
                semantic_backfill_lock.release()

        threading.Thread(target=backfill, name="contact-memory-embedding", daemon=True).start()

    schedule_semantic_backfill()

    def invalidate_memory_context() -> None:
        nonlocal interpretation_generation, latest_interpretation_snapshot
        nonlocal next_interpretation_snapshot_id
        interpretation_generation += 1
        next_interpretation_snapshot_id = 0
        latest_interpretation_snapshot = None
        test_log.emit("context_reset", generation=interpretation_generation, contact_id=selected_contact_id)
        visual_aggregator.reset()
        stable_interpretation.reset()
        guidance_display.reset()
        render_guidance()
        if interpretation_coordinator:
            interpretation_coordinator.reset(interpretation_generation, preserve_cadence=True)
        render_interpretation(replaced=True)

    def set_selected_contact(contact_id: str | None) -> bool:
        nonlocal selected_contact_id, selected_contact_label, current_record_id
        if memory_store is None:
            return False
        try:
            contact = memory_store.get_contact(contact_id) if contact_id else None
            if current_record_id:
                memory_store.assign_record(current_record_id, contact_id)
        except (KeyError, ValueError, sqlite3.OperationalError) as exc:
            messagebox.showerror("Select contact", str(exc))
            return False
        changed = selected_contact_id != contact_id
        previous_speaker_name = selected_contact_label or call_speaker_fallback
        if changed:
            invalidate_memory_context()
        selected_contact_id = contact_id
        test_log.emit("contact_selected", contact_id=contact_id, record_id=current_record_id, generation=interpretation_generation)
        selected_contact_label = contact.label if contact is not None else None
        speaker_name = selected_contact_label or call_speaker_fallback
        if audio_session is not None:
            audio_session.contact_name = speaker_name
        if (changed or speaker_name != previous_speaker_name) and turns:
            _relabel_contact_turns(turns, speaker_name)
            render_transcript_turns(turns, replace=True)
        if contact is not None:
            confirmed_contact_label.configure(text=f"Confirmed contact: {contact.label}")
            memory_status_label.configure(text="Contact memory is eligible")
            if turns:
                offer_interpretation_snapshot()
        else:
            confirmed_contact_label.configure(text="Confirmed contact: none")
            memory_status_label.configure(text="No contact confirmed — retrieval and extraction are off")
        return True

    def select_contact() -> None:
        index = contact_box.current()
        if index < 0 or index >= len(contact_choices):
            messagebox.showinfo("Selected Contact", "Search for and choose a contact first.")
            return
        set_selected_contact(contact_choices[index].id)

    def create_contact() -> None:
        if memory_store is None:
            messagebox.showerror("Contact memory", memory_startup_error)
            return
        name = simpledialog.askstring("Create Contact", "Display name:", parent=root)
        if not name:
            return
        disambiguator = simpledialog.askstring(
            "Create Contact", "Optional disambiguator (last name, work, friend):", parent=root
        )
        try:
            contact = memory_store.create_contact(
                name, disambiguator or None, timezone_name=str(datetime.now().astimezone().tzinfo)
            )
        except (ValueError, sqlite3.OperationalError) as exc:
            messagebox.showerror("Create contact", str(exc))
            return
        refresh_contact_choices()
        set_selected_contact(contact.id)

    def manage_memory(contact_id=None) -> None:
        contact_id = contact_id or selected_contact_id
        if memory_store is None or contact_id is None:
            messagebox.showinfo("Contact memory", "Confirm one contact first.")
            return
        dialog = tk.Toplevel(root)
        dialog.title(f"Memory — {memory_store.get_contact(contact_id).label}")
        dialog.geometry("760x430")
        search_controls = tk.Frame(dialog)
        search_controls.pack(fill="x", padx=8, pady=(8, 0))
        memory_query = tk.Entry(search_controls)
        memory_query.pack(side="left", fill="x", expand=True)
        all_contacts = tk.BooleanVar(value=False)
        tk.Checkbutton(search_controls, text="Explicit all-contact search", variable=all_contacts).pack(side="left", padx=6)
        filter_controls = tk.Frame(dialog)
        filter_controls.pack(fill="x", padx=8, pady=(4, 0))
        lifecycle_filter = ttk.Combobox(filter_controls, state="readonly", width=12, values=("approved", "pending", "rejected"))
        lifecycle_filter.set("approved")
        lifecycle_filter.pack(side="left")
        type_labels = {value: value.replace("_", " ").title() for value in MEMORY_TYPES}
        type_labels["event_date"] = "Event / date"
        label_types = {label: value for value, label in type_labels.items()}
        type_filter = ttk.Combobox(
            filter_controls, state="readonly", width=22, values=("Any type", *type_labels.values())
        )
        type_filter.set("Any type")
        type_filter.pack(side="left", padx=4)
        sensitivity_filter = ttk.Combobox(filter_controls, state="readonly", width=12, values=("any sensitivity", "normal", "sensitive"))
        sensitivity_filter.set("any sensitivity")
        sensitivity_filter.pack(side="left")
        date_from = tk.Entry(filter_controls, width=12)
        date_from.insert(0, "from DD/MM/YYYY")
        date_from.pack(side="left", padx=4)
        date_to = tk.Entry(filter_controls, width=12)
        date_to.insert(0, "to DD/MM/YYYY")
        date_to.pack(side="left")
        items = tk.Listbox(dialog, selectmode="extended", exportselection=False)
        items.pack(fill="both", expand=True, padx=8, pady=8)
        tk.Label(
            dialog,
            text="Use Ctrl or Shift to select multiple pending proposals for approval or rejection.",
            anchor="w",
            fg="#555555",
        ).pack(fill="x", padx=8, pady=(0, 5))
        rows = []

        def reload_items() -> None:
            nonlocal rows
            rows = list(memory_store.list_current_memories(contact_id))
            proposals = list(memory_store.list_proposals(contact_id))
            items.delete(0, tk.END)
            for row in rows:
                permission = " · cloud permitted" if row["cloud_allowed"] else ""
                review = " · needs review" if row["needs_review"] else ""
                items.insert(tk.END, f"Memory · {type_labels[row['memory_type']]} · {row['confidence']}{permission}{review} · {row['content']}")
            for row in proposals:
                duplicates = memory_store.proposal_duplicate_descriptions(row["id"])
                duplicate = f" · Possible duplicate of: {duplicates[0]}" if duplicates else ""
                generic = " · LIKELY GENERIC — easy to reject" if row["likely_generic"] else ""
                items.insert(
                    tk.END,
                    f"Proposal · {row['state']} · {type_labels[row['memory_type']]} · "
                    f"{row['confidence']} confidence · {row['sensitivity']}{generic}{duplicate} · {row['content']}",
                )
            rows += proposals

        def search_items() -> None:
            nonlocal rows
            query = memory_query.get().strip()
            memory_type = None if type_filter.get() == "Any type" else label_types[type_filter.get()]
            sensitivity = None if sensitivity_filter.get() == "any sensitivity" else sensitivity_filter.get()
            start = date_from.get().strip()
            end = date_to.get().strip()
            start = None if start == "from DD/MM/YYYY" else start
            end = None if end == "to DD/MM/YYYY" else end
            try:
                start = parse_memory_date(start).date().isoformat() if start else None
                end = parse_memory_date(end).date().isoformat() if end else None
            except ValueError:
                messagebox.showerror("Search", "Dates must use DD/MM/YYYY.", parent=dialog)
                return
            lifecycle = lifecycle_filter.get()
            if lifecycle != "approved":
                if all_contacts.get():
                    messagebox.showinfo("Search", "Proposal search stays within the confirmed contact.", parent=dialog)
                    return
                rows = [
                    row for row in memory_store.list_proposals(contact_id)
                    if row["state"] == lifecycle
                    and (not query or query.casefold() in row["content"].casefold())
                    and (memory_type is None or row["memory_type"] == memory_type)
                    and (sensitivity is None or row["sensitivity"] == sensitivity)
                    and (not start or (row["normalized_date_end"] or row["normalized_date_start"] or row["created_at"])[:10] >= start)
                    and (not end or (row["normalized_date_start"] or row["created_at"])[:10] <= end)
                ]
                items.delete(0, tk.END)
                for row in rows:
                    generic = " · LIKELY GENERIC — easy to reject" if row["likely_generic"] else ""
                    items.insert(
                        tk.END,
                        f"Proposal · {row['state']} · {type_labels[row['memory_type']]} · "
                        f"{row['confidence']} confidence · {row['sensitivity']}{generic} · {row['content']}",
                    )
                return
            try:
                rows = list(memory_store.search(
                    query, contact_id=contact_id, all_contacts=all_contacts.get(), memory_type=memory_type,
                    sensitivity=sensitivity, date_from=start, date_to=end,
                ))
            except (ValueError, sqlite3.OperationalError) as exc:
                messagebox.showerror("Search", str(exc), parent=dialog)
                return
            items.delete(0, tk.END)
            for row in rows:
                contact_suffix = (
                    f" · contact {memory_store.get_contact(row['contact_id']).label}"
                    if all_contacts.get() else ""
                )
                items.insert(tk.END, f"Match{contact_suffix} · {type_labels[row['memory_type']]} · {row['content']}")

        tk.Button(search_controls, text="Search", command=search_items).pack(side="left")

        def selected_row():
            selection = items.curselection()
            return rows[selection[0]] if selection else None

        def selected_rows():
            return [rows[index] for index in items.curselection()]

        def selected_contact_row(row) -> bool:
            if row is None or "contact_id" not in row.keys() or row["contact_id"] == contact_id:
                return True
            owner = memory_store.get_contact(row["contact_id"]).label
            messagebox.showwarning(
                "Switch contact first",
                f"This memory belongs to {owner}. Select that contact before changing or deleting it.",
                parent=dialog,
            )
            return False

        buttons = tk.Frame(dialog)
        buttons.pack(fill="x", padx=8, pady=(0, 8))

        def memory_editor(
            title: str,
            *,
            content: str = "",
            memory_type: str = "other",
            confidence: str = "high",
            sensitivity: str = "normal",
            normalized_date_start: str = "",
        ):
            result = None
            editor = tk.Toplevel(dialog)
            editor.title(title)
            editor.geometry("620x430")
            editor.transient(dialog)
            editor.grab_set()
            editor.columnconfigure(1, weight=1)
            editor.rowconfigure(1, weight=1)
            tk.Label(editor, text="Memory text", anchor="w").grid(
                row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=(10, 4)
            )
            content_box = tk.Text(editor, height=10, width=58, wrap="word")
            content_box.insert("1.0", content)
            content_box.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=10)
            tk.Label(editor, text="Memory type").grid(row=2, column=0, sticky="w", padx=10, pady=(10, 4))
            type_box = ttk.Combobox(editor, state="readonly", values=tuple(type_labels.values()))
            type_box.set(type_labels[memory_type])
            type_box.grid(row=2, column=1, sticky="ew", padx=(0, 10), pady=(10, 4))
            tk.Label(
                editor,
                text="If you choose Other, describe the custom category in the memory text.",
                anchor="w",
                fg="#555555",
            ).grid(row=3, column=1, sticky="ew", padx=(0, 10))
            tk.Label(editor, text="Confidence").grid(row=4, column=0, sticky="w", padx=10, pady=6)
            confidence_box = ttk.Combobox(editor, state="readonly", values=("low", "medium", "high"))
            confidence_box.set(confidence)
            confidence_box.grid(row=4, column=1, sticky="ew", padx=(0, 10), pady=6)
            tk.Label(editor, text="Event date (DD/MM/YYYY, optional)").grid(row=5, column=0, sticky="w", padx=10, pady=6)
            date_box = tk.Entry(editor)
            date_box.insert(0, format_memory_date(normalized_date_start))
            date_box.grid(row=5, column=1, sticky="ew", padx=(0, 10), pady=6)
            tk.Label(editor, text="Sensitivity").grid(row=6, column=0, sticky="w", padx=10, pady=6)
            sensitivity_box = ttk.Combobox(editor, state="readonly", values=("normal", "sensitive"))
            sensitivity_box.set(sensitivity)
            sensitivity_box.grid(row=6, column=1, sticky="ew", padx=(0, 10), pady=6)
            actions = tk.Frame(editor)
            actions.grid(row=7, column=0, columnspan=2, sticky="e", padx=10, pady=10)

            def save() -> None:
                nonlocal result
                value = content_box.get("1.0", "end-1c").strip()
                if not value:
                    messagebox.showinfo(title, "Memory text is required.", parent=editor)
                    return
                date_value = date_box.get().strip()
                try:
                    normalized_date = parse_memory_date(date_value)
                except ValueError:
                    messagebox.showinfo(title, "Use DD/MM/YYYY for the event date.", parent=editor)
                    return
                result = (
                    value,
                    label_types[type_box.get()],
                    confidence_box.get(),
                    sensitivity_box.get(),
                    normalized_date,
                )
                editor.destroy()

            tk.Button(actions, text="Cancel", command=editor.destroy).pack(side="right")
            tk.Button(actions, text="Save", command=save).pack(side="right", padx=(0, 6))
            content_box.focus_set()
            editor.wait_window()
            return result

        def add_memory() -> None:
            values = memory_editor("Add approved memory")
            if values is None:
                return
            content, memory_type, confidence, sensitivity, normalized_date = values
            try:
                memory_store.create_memory(
                    contact_id, content, memory_type=memory_type,
                    confidence=confidence, sensitivity=sensitivity,
                    original_date_text=normalized_date.date().isoformat() if normalized_date else None,
                    normalized_date_start=normalized_date,
                )
            except (ValueError, sqlite3.OperationalError) as exc:
                messagebox.showerror("Add memory", str(exc), parent=dialog)
                return
            invalidate_memory_context()
            schedule_semantic_backfill()
            reload_items()

        def correct_selected() -> None:
            row = selected_row()
            if row is None or "memory_id" not in row.keys() or not selected_contact_row(row):
                return
            current_date = row["normalized_date_start"] or ""
            values = memory_editor(
                "Correct memory",
                content=row["content"],
                memory_type=row["memory_type"],
                confidence=row["confidence"],
                sensitivity=row["sensitivity"],
                normalized_date_start=current_date,
            )
            if values is None:
                return
            content, memory_type, confidence, sensitivity, normalized_date = values
            try:
                correction = {
                    "memory_type": memory_type,
                    "confidence": confidence,
                    "sensitivity": sensitivity,
                }
                choices = {}
                for statement in memory_store.memory_summary_preview(row["memory_id"]):
                    choice = messagebox.askyesnocancel(
                        "Update linked summary sentence",
                        f"Old memory: {row['content']}\nNew memory: {content}\n\n"
                        f"Summary: {statement['content']}\n\n"
                        "Yes: Update the sentence to match this corrected fact.\n"
                        "No: Keep the previous wording as dated history.\nCancel: leave the memory unchanged.", parent=dialog,
                    )
                    if choice is None:
                        return
                    choices[statement["id"]] = "update" if choice else "keep"
                correction["summary_choices"] = choices
                correction["expected_revision_id"] = row["revision_id"]
                new_date = normalized_date.date().isoformat() if normalized_date else ""
                if new_date != current_date:
                    correction["normalized_date_start"] = normalized_date
                memory_store.correct_memory(
                    row["memory_id"], content, **correction,
                )
            except (ValueError, sqlite3.OperationalError) as exc:
                messagebox.showerror("Correct memory", str(exc), parent=dialog)
                return
            invalidate_memory_context()
            schedule_semantic_backfill()
            reload_items()

        def delete_selected() -> None:
            chosen = selected_rows()
            if not chosen:
                messagebox.showinfo("Delete memory", "Choose one or more approved memories.", parent=dialog)
                return
            if any("memory_id" not in row.keys() or not selected_contact_row(row) for row in chosen):
                messagebox.showinfo("Delete memory", "Select only approved memories for this contact.", parent=dialog)
                return
            count = len(chosen)
            if messagebox.askyesno(
                "Delete memories",
                f"Permanently erase {count} selected memor{'y' if count == 1 else 'ies'}, including every revision and search entry?",
                parent=dialog,
            ):
                try:
                    memory_store.delete_memories([row["memory_id"] for row in chosen])
                except (KeyError, ValueError, sqlite3.OperationalError) as exc:
                    messagebox.showerror("Delete memories", str(exc), parent=dialog)
                    return
                invalidate_memory_context()
                reload_items()

        def review_selected(approve: bool) -> None:
            chosen = selected_rows()
            if not chosen:
                messagebox.showinfo("Review proposals", "Choose one or more pending proposals.", parent=dialog)
                return
            if any("batch_id" not in row.keys() or row["state"] != "pending" for row in chosen):
                messagebox.showinfo("Review proposals", "Select only pending proposals.", parent=dialog)
                return
            try:
                memory_store.review_proposals([row["id"] for row in chosen], approve=approve)
            except (KeyError, ValueError, sqlite3.OperationalError) as exc:
                messagebox.showerror("Review proposals", str(exc), parent=dialog)
                reload_items()
                return
            invalidate_memory_context()
            if approve:
                schedule_semantic_backfill()
            reload_items()

        def toggle_cloud_permission() -> None:
            row = selected_row()
            if row is None or "memory_id" not in row.keys() or not selected_contact_row(row) or row["sensitivity"] != "sensitive":
                messagebox.showinfo("Cloud permission", "Choose a sensitive memory first.", parent=dialog)
                return
            try:
                memory_store.set_cloud_permission(row["memory_id"], not bool(row["cloud_allowed"]))
            except (KeyError, ValueError, sqlite3.OperationalError) as exc:
                messagebox.showerror("Cloud permission", str(exc), parent=dialog)
                return
            invalidate_memory_context()
            schedule_semantic_backfill()
            reload_items()

        def reopen_selected() -> None:
            row = selected_row()
            if row is not None and "batch_id" in row.keys() and row["state"] == "rejected":
                try:
                    memory_store.reopen_proposal(row["id"])
                except (ValueError, sqlite3.OperationalError) as exc:
                    messagebox.showerror("Reopen proposal", str(exc), parent=dialog)
                    return
                reload_items()

        def confirm_reviewed() -> None:
            try:
                chosen = selected_rows()
                if not chosen or any("memory_id" not in row.keys() or not selected_contact_row(row) for row in chosen):
                    return
                text = f"Contact: {memory_store.get_contact(contact_id).label}\n"
                for row in chosen:
                    sources = memory_store._connection.execute("SELECT * FROM memory_sources WHERE revision_id=?", (row["revision_id"],)).fetchall()
                    text += f"\nCurrent revision: {row['revision_id']}\n{row['content']}\n"
                    for source in sources:
                        text += f"\nSource: {source['record_id'] or 'Original source deleted'} · {source['approximate_date'] or 'date unknown'}\n"
                        if source["record_id"]:
                            sequences = set(json.loads(source["turn_sequences"]))
                            text += "\n".join(f"Turn {turn.display_order} · {turn.timestamp} · {turn.speaker_name}: {turn.content}"
                                               for turn in memory_store.record_turns(source["record_id"]) if turn.display_order in sequences)
                review = show_evidence(dialog, text, lambda: all(memory_store.current_revision(row["memory_id"])["id"] == row["revision_id"] for row in chosen))
                def confirm():
                    try:
                        # Validate the complete selection before applying its review decisions.
                        if any(memory_store.current_revision(row["memory_id"])["id"] != row["revision_id"] for row in chosen):
                            raise ValueError("A revision changed; reopen this review")
                        memory_store.confirm_reviewed_memories({row["memory_id"]: row["revision_id"] for row in chosen})
                    except (ValueError, KeyError, sqlite3.Error) as exc:
                        messagebox.showerror("Review memory", str(exc), parent=dialog)
                        return
                    invalidate_memory_context()
                    reload_items()
                    review.destroy()
                tk.Button(review, text="Confirm I reviewed these contacts, revisions and sources", command=confirm).pack(fill="x")

            except (ValueError, KeyError, sqlite3.Error) as exc:
                messagebox.showerror("Review memory", f"Source unavailable or memory store busy: {exc}", parent=dialog)

        def delete_rejected_selected() -> None:
            row = selected_row()
            if row is None or "batch_id" not in row.keys() or row["state"] != "rejected":
                messagebox.showinfo("Delete rejected proposal", "Choose a rejected proposal first.", parent=dialog)
                return
            if messagebox.askyesno("Delete rejected proposal", "Permanently delete this rejected proposal?", parent=dialog):
                try:
                    memory_store.delete_rejected_proposal(row["id"])
                except (ValueError, sqlite3.OperationalError) as exc:
                    messagebox.showerror("Delete rejected proposal", str(exc), parent=dialog)
                    return
                reload_items()

        def connect_selected() -> None:
            selections = items.curselection()
            if len(selections) != 2:
                messagebox.showinfo("Connect memories", "Select exactly two approved memories.", parent=dialog)
                return
            chosen = [rows[index] for index in selections]
            if any("memory_id" not in row.keys() or not selected_contact_row(row) for row in chosen):
                return
            try:
                memory_store.connect_memories(chosen[0]["memory_id"], chosen[1]["memory_id"])
            except (KeyError, ValueError, sqlite3.OperationalError) as exc:
                messagebox.showerror("Connect memories", str(exc), parent=dialog)
                return
            messagebox.showinfo("Connect memories", "The memories are now related for one-hop retrieval.", parent=dialog)

        def edit_contact() -> None:
            try:
                contact = memory_store.get_contact(contact_id)
            except (KeyError, sqlite3.OperationalError) as exc:
                messagebox.showerror("Edit contact", str(exc), parent=dialog)
                return
            name = simpledialog.askstring("Edit contact", "Display name:", initialvalue=contact.display_name, parent=dialog)
            if not name:
                return
            disambiguator = simpledialog.askstring(
                "Edit contact", "Optional disambiguator:", initialvalue=contact.disambiguator or "", parent=dialog
            )
            timezone_name = simpledialog.askstring(
                "Edit contact", "Optional time-zone context:", initialvalue=contact.timezone_name or "", parent=dialog
            )
            try:
                updated = memory_store.edit_contact(
                    contact_id, display_name=name, disambiguator=disambiguator or None,
                    timezone_name=timezone_name or None,
                )
            except (KeyError, ValueError, sqlite3.OperationalError) as exc:
                messagebox.showerror("Edit contact", str(exc), parent=dialog)
                return
            dialog.title(f"Memory — {updated.label}")
            refresh_contact_choices()

        def manage_aliases() -> None:
            alias_dialog = tk.Toplevel(dialog)
            alias_dialog.title("Contact aliases")
            alias_list = tk.Listbox(alias_dialog, width=60)
            alias_list.pack(fill="both", expand=True, padx=8, pady=8)
            alias_rows = []

            def reload_aliases() -> None:
                nonlocal alias_rows
                alias_rows = memory_store.list_aliases(contact_id)
                alias_list.delete(0, tk.END)
                for alias in alias_rows:
                    alias_list.insert(tk.END, f"{alias['spelling']} · {alias['origin']}")

            def add_alias() -> None:
                spelling = simpledialog.askstring("Add alias", "Alias or nickname:", parent=alias_dialog)
                if spelling:
                    try:
                        memory_store.add_alias(contact_id, spelling)
                    except (KeyError, ValueError, sqlite3.OperationalError) as exc:
                        messagebox.showerror("Add alias", str(exc), parent=alias_dialog)
                        return
                    refresh_contact_choices()
                    reload_aliases()

            def remove_alias() -> None:
                selection = alias_list.curselection()
                if not selection:
                    return
                try:
                    memory_store.remove_alias(alias_rows[selection[0]]["id"])
                except (ValueError, sqlite3.OperationalError) as exc:
                    messagebox.showinfo("Remove alias", str(exc), parent=alias_dialog)
                    return
                refresh_contact_choices()
                reload_aliases()

            tk.Button(alias_dialog, text="Add", command=add_alias).pack(side="left", padx=8, pady=(0, 8))
            tk.Button(alias_dialog, text="Remove", command=remove_alias).pack(side="left", pady=(0, 8))
            reload_aliases()

        def merge_contact() -> None:
            query = simpledialog.askstring(
                "Merge contacts", "Contact to merge into the currently selected survivor:", parent=dialog
            )
            if not query:
                return
            candidates = [item for item in memory_store.list_contacts(query) if item.id != contact_id]
            if len(candidates) != 1:
                messagebox.showinfo("Merge contacts", "Search must identify exactly one other contact.", parent=dialog)
                return
            merged = candidates[0]
            preview = memory_store.merge_preview(contact_id, merged.id)
            details = "\n".join(f"{name.replace('_', ' ')}: {count}" for name, count in preview.items())
            if messagebox.askyesno(
                "Merge contacts", f"Keep {memory_store.get_contact(contact_id).label} and merge {merged.label}?\n\n{details}\n\nMerged memories stay separate and are withheld from retrieval until reviewed. Multi-select them and use Confirm reviewed memory to review their sources together.",
                parent=dialog,
            ):
                try:
                    memory_store.merge_contacts(contact_id, merged.id)
                except (KeyError, ValueError, sqlite3.OperationalError) as exc:
                    messagebox.showerror("Merge contacts", str(exc), parent=dialog)
                    return
                refresh_contact_choices()
                if selected_contact_id == merged.id:
                    set_selected_contact(contact_id)
                else:
                    invalidate_memory_context()
                reload_items()

        def delete_contact() -> None:
            nonlocal current_record_id
            preview = memory_store.contact_deletion_preview(contact_id)
            details = "\n".join(f"{name}: {count}" for name, count in preview.items())
            if messagebox.askyesno(
                "Delete contact", f"Permanently delete this contact and all local content?\n\n{details}", parent=dialog
            ):
                try:
                    memory_store.delete_contact(contact_id)
                except Exception as exc:
                    messagebox.showerror("Delete contact", f"Contact was not deleted ({type(exc).__name__}).", parent=dialog)
                    return
                if selected_contact_id == contact_id:
                    current_record_id = None
                    set_selected_contact(None)
                dialog.destroy()
                refresh_contact_choices()

        def export_contact() -> None:
            export_all = messagebox.askyesnocancel(
                "Export JSON", "Export every contact?\n\nYes exports all contacts. No exports only the selected contact.", parent=dialog
            )
            if export_all is None:
                return
            target = filedialog.asksaveasfilename(
                parent=dialog, defaultextension=".json", filetypes=[("JSON", "*.json")]
            )
            if not target:
                return
            try:
                payload = memory_store.export_json(
                    all_data=export_all, contact_id=None if export_all else contact_id
                )
                memory_store.validate_export(payload)
                Path(target).write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
            except (KeyError, ValueError, OSError, sqlite3.OperationalError) as exc:
                messagebox.showerror("Export failed", str(exc), parent=dialog)
                return
            messagebox.showwarning("Export complete", "The exported file is outside later app deletion control.", parent=dialog)

        def choose_record(action: str) -> None:
            records = list(memory_store.list_records(contact_id))
            if not records:
                messagebox.showinfo("Conversation records", "This contact has no retained conversation records.", parent=dialog)
                return
            chooser = tk.Toplevel(dialog)
            chooser.title("Choose Conversation Record")
            record_list = tk.Listbox(chooser, width=90)
            record_list.pack(fill="both", expand=True, padx=8, pady=8)
            for record in records:
                record_list.insert(tk.END, f"{record['source_kind']} · {record['source_label']} · {record['analysis_state']} · {record['started_at'] or 'time unavailable'}")

            def continue_action() -> None:
                selection = record_list.curselection()
                if not selection:
                    return
                record = records[selection[0]]
                chooser.destroy()
                if action == "retry":
                    record = next(
                        (item for item in memory_store.list_records(contact_id) if item["id"] == record["id"]),
                        None,
                    )
                    if record is None:
                        messagebox.showinfo("Retry analysis", "This conversation is no longer available for this contact.", parent=dialog)
                        return
                    if record["analysis_state"] == "complete":
                        messagebox.showinfo("Retry analysis", "This conversation already has a proposal batch for review.", parent=dialog)
                        return
                    if record["analysis_state"] == "running":
                        messagebox.showinfo("Retry analysis", "Analysis is already running for this conversation.", parent=dialog)
                        return
                    record_turns = memory_store.record_turns(record["id"])
                    try:
                        _chunks, _estimate = extraction_maximum_cost(record_turns)
                    except ValueError as exc:
                        messagebox.showerror("Retry analysis", str(exc), parent=dialog)
                        return
                    worker_path = memory_store.path
                    retry_batch = memory_store.retryable_batch(record["id"])

                    def retry_analysis() -> None:
                        try:
                            with MemoryStore(worker_path, verify=False) as worker_store:
                                batch_id = analyze_record(
                                    worker_store, record["id"], OpenAIMemoryExtractor(), batch_id=retry_batch
                                )
                        except Exception as exc:
                            memory_analysis_results.put((record["id"], None, type(exc).__name__))
                        else:
                            memory_analysis_results.put((record["id"], batch_id, None))

                    threading.Thread(target=retry_analysis, name="retry-memory-extraction", daemon=True).start()
                    memory_status_label.configure(text="Retrying bounded memory analysis")
                    return
                target = None
                if action == "reassign":
                    query = simpledialog.askstring("Reassign conversation", "Correct contact name or disambiguator:", parent=dialog)
                    if not query:
                        return
                    candidates = [item for item in memory_store.list_contacts(query) if item.id != contact_id]
                    if len(candidates) != 1:
                        messagebox.showinfo("Reassign conversation", "Search must identify exactly one other contact.", parent=dialog)
                        return
                    target = candidates[0]
                preview = memory_store.reassignment_preview(record["id"])
                review = tk.Toplevel(dialog)
                review.title("Derived memory preview")
                tk.Label(
                    review,
                    text="Derived memories are selected for deletion by default. Deselect an item to keep it explicitly.",
                    anchor="w",
                ).pack(fill="x", padx=8, pady=8)
                derived = tk.Listbox(review, selectmode="multiple", width=100)
                derived.pack(fill="both", expand=True, padx=8)
                for item in preview:
                    derived.insert(tk.END, item["content"] or "[content unavailable]")
                if preview:
                    derived.selection_set(0, tk.END)

                def apply_record_change() -> None:
                    selected_for_delete = set(derived.curselection())
                    keep = [
                        str(item["memory_id"]) for index, item in enumerate(preview)
                        if index not in selected_for_delete
                    ]
                    try:
                        if action == "delete":
                            memory_store.delete_source(record["id"], keep_memory_ids=keep)
                        else:
                            assert target is not None
                            memory_store.reassign_record(record["id"], target.id, keep_memory_ids=keep)
                    except (KeyError, ValueError, sqlite3.OperationalError) as exc:
                        messagebox.showerror("Conversation record", str(exc), parent=review)
                        return
                    review.destroy()
                    invalidate_memory_context()
                    reload_items()

                label = "Delete source" if action == "delete" else f"Reassign to {target.label}"
                tk.Button(review, text=label, command=apply_record_change).pack(pady=8)

            tk.Button(chooser, text="Continue", command=continue_action).pack(pady=(0, 8))

        actions = (
            ("Add", add_memory), ("Correct", correct_selected), ("Delete selected", delete_selected),
            ("Approve selected", lambda: review_selected(True)), ("Reject selected", lambda: review_selected(False)),
            ("Reopen", reopen_selected), ("Delete rejected", delete_rejected_selected),
            ("Connect", connect_selected),
            ("Edit contact", edit_contact), ("Aliases", manage_aliases),
            ("Retry analysis", lambda: choose_record("retry")),
            ("Delete source", lambda: choose_record("delete")), ("Reassign source", lambda: choose_record("reassign")),
            ("Export JSON", export_contact), ("Merge contact", merge_contact), ("Delete contact", delete_contact),
            ("Confirm reviewed memory", confirm_reviewed),
        )
        for index, (label, command) in enumerate(actions):
            tk.Button(buttons, text=label, command=command).grid(
                row=index // 6, column=index % 6, sticky="ew", padx=(0, 5), pady=(0, 4)
            )
        for column in range(6):
            buttons.columnconfigure(column, weight=1)
        reload_items()

    def import_chat() -> None:
        if memory_store is None or selected_contact_id is None:
            messagebox.showinfo("Import chat", "Confirm the contact before importing attributed text.")
            return
        source = filedialog.askopenfilename(filetypes=[("Text", "*.txt"), ("All files", "*.*")])
        if not source:
            return
        try:
            text = Path(source).read_text(encoding="utf-8-sig")
            parsed = parse_whatsapp_transcript(text, source="whatsapp_import")
            preview = memory_store.import_preview(
                parsed, timezone_name=str(datetime.now().astimezone().tzinfo)
            )
        except Exception as exc:
            messagebox.showerror("Import chat", f"Import preview failed ({type(exc).__name__}).")
            return
        user_name = simpledialog.askstring(
            "Confirm participants",
            f"Participants: {', '.join(preview.participants)}\nAssumed time zone: {preview.timezone_name}\n\nWhich participant is you?",
            parent=root,
        )
        if not user_name:
            return
        try:
            record_id = memory_store.confirm_import(
                preview, user_name=user_name, contact_id=selected_contact_id, source_label=Path(source).name
            )
        except Exception as exc:
            messagebox.showerror("Import chat", f"Participant mapping failed ({type(exc).__name__}).")
            return
        try:
            extraction_maximum_cost(preview.turns)
        except ValueError:
            memory_status_label.configure(text="Imported conversation saved; a turn exceeds the extraction limit, so analysis did not run")
            return
        worker_path = memory_store.path

        def run_import_analysis() -> None:
            try:
                with MemoryStore(worker_path, verify=False) as worker_store:
                    batch_id = analyze_record(worker_store, record_id, OpenAIMemoryExtractor())
            except Exception as exc:
                memory_analysis_results.put((record_id, None, type(exc).__name__))
            else:
                memory_analysis_results.put((record_id, batch_id, None))

        threading.Thread(target=run_import_analysis, name="import-memory-extraction", daemon=True).start()

    def show_unassigned() -> None:
        if memory_store is None:
            return
        records = list(memory_store.list_unassigned())
        if not records:
            messagebox.showinfo("Unassigned Conversations", "There are no unassigned conversations.")
            return
        dialog = tk.Toplevel(root)
        dialog.title("Unassigned Conversations")
        listing = tk.Listbox(dialog, width=90)
        listing.pack(fill="both", expand=True, padx=8, pady=8)
        for row in records:
            listing.insert(tk.END, f"{row['source_kind']} · {row['source_label']} · {row['started_at'] or 'time unavailable'}")

        def assign_selected() -> None:
            selection = listing.curselection()
            if not selection or selected_contact_id is None:
                messagebox.showinfo("Assign conversation", "Select a row and confirm a contact in the main window.", parent=dialog)
                return
            try:
                memory_store.assign_record(records[selection[0]]["id"], selected_contact_id)
            except (KeyError, ValueError) as exc:
                messagebox.showerror("Assign conversation", str(exc), parent=dialog)
                return
            dialog.destroy()
            memory_status_label.configure(text="Conversation assigned; use import/call analysis to create proposals")

        tk.Button(dialog, text="Assign to confirmed contact", command=assign_selected).pack(pady=(0, 8))

    def open_settings() -> None:
        dialog = tk.Toplevel(root)
        dialog.title("Settings")
        dialog.geometry("820x680")
        dialog.minsize(720, 620)
        header = tk.Frame(dialog)
        header.pack(fill="x", padx=18, pady=(14, 8))
        tk.Label(header, text="Settings", font=("Segoe UI", 20, "bold")).pack(side="left")
        tk.Button(header, text="Back to Home", command=dialog.destroy).pack(side="right")
        body = tk.Frame(dialog)
        body.pack(fill="both", expand=True, padx=18, pady=(0, 14))
        body.columnconfigure(0, weight=1)
        body.columnconfigure(1, weight=1)

        api = tk.LabelFrame(body, text="API key", padx=10, pady=8)
        api.grid(row=0, column=0, columnspan=2, sticky="ew", pady=5)
        configured = bool(local_openai_api_key())
        tk.Label(api, text="System key in use" if configured else "No API key configured",
                 font=("Segoe UI", 10, "bold"), anchor="w").pack(fill="x")
        tk.Label(api, text="The saved key is never shown. Enter a replacement only when you want to change it.",
                 anchor="w", justify="left").pack(fill="x")
        key_row = tk.Frame(api)
        key_row.pack(fill="x", pady=(7, 0))
        key_entry = tk.Entry(key_row, show="•")
        key_entry.pack(side="left", fill="x", expand=True)
        key_status = tk.Label(api, text="", anchor="w")
        key_status.pack(fill="x")
        def save_key():
            try:
                save_local_openai_api_key(key_entry.get())
            except (OSError, ValueError) as exc:
                key_status.configure(text=str(exc), fg="#9b1c1c")
                return
            key_entry.delete(0, tk.END)
            key_status.configure(text="Replacement saved privately.", fg="#1f6b3c")
        tk.Button(key_row, text="Save override", command=save_key).pack(side="left", padx=(6, 0))

        readability = tk.LabelFrame(body, text="Readability", padx=10, pady=8)
        readability.grid(row=1, column=0, sticky="nsew", padx=(0, 5), pady=5)
        text_size = tk.StringVar(value=ui_settings.get("text_size", "Default"))
        for name in ("Default", "Large", "Extra large"):
            tk.Radiobutton(readability, text=name, value=name, variable=text_size).pack(anchor="w")
        high_contrast = tk.BooleanVar(value=bool(ui_settings.get("high_contrast")))
        reduce_motion = tk.BooleanVar(value=bool(ui_settings.get("reduce_motion")))
        tk.Checkbutton(readability, text="High contrast", variable=high_contrast).pack(anchor="w")
        tk.Checkbutton(readability, text="Reduce motion", variable=reduce_motion).pack(anchor="w")
        preview = tk.Label(readability, text="Preview: clear, calm guidance", font=("Segoe UI", 11, "bold"))
        preview.pack(fill="x", pady=(8, 0))

        privacy = tk.LabelFrame(body, text="Privacy and cloud", padx=10, pady=8)
        privacy.grid(row=1, column=1, sticky="nsew", padx=(5, 0), pady=5)
        tk.Label(privacy, text="Eligible call context is sent only for Live, Ask, and Review requests. OpenAI requests use store=false.",
                 justify="left", wraplength=330, anchor="w").pack(fill="x")
        tk.Label(privacy, text="Transcription, face tracking, contact data, and exact source review stay local.",
                 justify="left", wraplength=330, anchor="w", fg="#555555").pack(fill="x", pady=(8, 0))

        contact = tk.LabelFrame(body, text="Selected contact", padx=10, pady=8)
        contact.grid(row=2, column=0, columnspan=2, sticky="ew", pady=5)
        tk.Label(contact, text=selected_contact_label or "No contact selected", font=("Segoe UI", 11, "bold")).pack(anchor="w")
        contact_actions = tk.Frame(contact)
        contact_actions.pack(fill="x", pady=(6, 0))
        for text in ("Edit aliases", "Merge", "Export", "Delete"):
            tk.Button(contact_actions, text=text, command=manage_memory).pack(side="left", padx=(0, 5))

        help_box = tk.LabelFrame(body, text="Help", padx=10, pady=8)
        help_box.grid(row=3, column=0, columnspan=2, sticky="ew", pady=5)
        for title, detail in (
            ("What the cues mean", "Cues are cautious possibilities based on recent context, never facts about a person."),
            ("Where my data goes", "Contact data and raw sources stay local; bounded eligible context is used only for requested cloud features."),
            ("Keyboard and accessibility", "Use Tab and Shift+Tab to move, Enter or Space to activate, and Escape to close supporting windows."),
        ):
            tk.Button(help_box, text=title, anchor="w", command=lambda t=title, d=detail: messagebox.showinfo(t, d, parent=dialog)).pack(fill="x", pady=2)

        def save_settings():
            ui_settings.update({"text_size": text_size.get(), "high_contrast": high_contrast.get(),
                                "reduce_motion": reduce_motion.get()})
            apply_readability()
            settings_path.parent.mkdir(parents=True, exist_ok=True)
            settings_path.write_text(json.dumps(ui_settings, sort_keys=True), encoding="utf-8")
            messagebox.showinfo("Settings", "Settings saved.", parent=dialog)

        ttk.Button(body, text="Save settings", style="Primary.TButton", command=save_settings).grid(
            row=4, column=0, columnspan=2, sticky="ew", pady=(8, 0)
        )
        dialog.bind("<Escape>", lambda _event: dialog.destroy())

    contact_search_button.configure(command=refresh_contact_choices)
    contact_select_button.configure(command=select_contact)
    contact_create_button.configure(command=create_contact)
    contact_clear_button.configure(command=lambda: set_selected_contact(None))
    memory_manage_button.configure(command=manage_memory)
    import_button.configure(command=import_chat)
    unassigned_button.configure(command=show_unassigned)
    settings_button.configure(command=open_settings)
    refresh_contact_choices()

    def begin_interpretation_session() -> None:
        nonlocal guidance_topic_start
        guidance_topic_start = 0
        test_log.emit("call_start", contact_id=selected_contact_id)
        nonlocal usage_ledger, interpretation_coordinator
        nonlocal interpretation_generation, next_interpretation_snapshot_id
        nonlocal latest_interpretation_snapshot, interpretation_updated_at
        nonlocal manual_terra_running
        interpretation_generation += 1
        next_interpretation_snapshot_id = 0
        latest_interpretation_snapshot = None
        interpretation_updated_at = ""
        manual_terra_running = False
        stable_interpretation.reset()
        guidance_display.reset()
        render_guidance()
        usage_ledger = None
        try:
            usage_ledger = UsageLedger.product()
            live_model = selected_live_model()
            interpreter = OpenAIInterpreter(
                model=live_model,
                reasoning="low",
                ledger=usage_ledger,
                live=True,
                is_current=lambda item: item.generation == interpretation_generation,
            )
            ledger = usage_ledger
            def current_guidance(item, store):
                if item.generation != interpretation_generation or stopping or item.contact_id != selected_contact_id:
                    return False
                if max(turn.display_order for turn in item.turns) < guidance_topic_start:
                    return False
                if item.memories:
                    for memory in item.memories:
                        source = memory_source(store, memory.memory_id, item.contact_id, for_cloud=True, display_limit=None)
                        if source is None or source.revision_id != memory.revision_id:
                            return False
                return True
            def combined(item):
                if item.contact_id:
                    with MemoryStore(memory_store.path, verify=False) as store:
                        result = interpret_guidance(item, ledger=ledger, client=interpreter._client, model=live_model, reasoning="low",
                            is_current=lambda snapshot: current_guidance(snapshot, store))
                        return result
                return interpreter(item)
            interpretation_coordinator = InterpretationCoordinator(combined, generation=interpretation_generation,
                first_request_at=time.perf_counter() + 12, adaptive_cadence=True)
        except InterpretationAuthenticationUnavailable:
            interpretation_coordinator = None
            set_interpretation_unavailable(
                "OpenAI key not configured — local capture and transcription continue",
                time.perf_counter(),
            )
        except ValueError:
            interpretation_coordinator = None
            set_interpretation_unavailable(
                "Interpretation budget configuration is invalid — local processing continues",
                time.perf_counter(),
            )
        except (ImportError, OSError):
            interpretation_coordinator = None
            set_interpretation_unavailable(
                "Cloud interpretation unavailable — local processing continues",
                time.perf_counter(),
            )
        render_interpretation(replaced=True)

    def offer_interpretation_snapshot() -> None:
        nonlocal next_interpretation_snapshot_id, latest_interpretation_snapshot
        nonlocal guidance_topic_start
        if stopping or not turns:
            return
        previous_guidance = repr(guidance_display.items)
        guidance_display.on_speech(turns[-1])
        if previous_guidance != repr(guidance_display.items):
            render_guidance()
        from .memory import _TOPIC_BOUNDARY
        new_topic = bool(_TOPIC_BOUNDARY.search(turns[-1].content))
        from .guidance import guidance_context_reset
        if guidance_context_reset(turns[-1].content):
            guidance_topic_start = turns[-1].display_order
            guidance_display.invalidate(new_topic=new_topic, turn_ids=set(), memory_ids=set())
            render_guidance()
        next_interpretation_snapshot_id += 1
        snapshot_id = next_interpretation_snapshot_id
        generation = interpretation_generation
        captured_turns = [item.model_copy(deep=True) for item in turns]
        captured_vocal = list(vocal_observations)
        captured_at = datetime.now(timezone.utc)
        captured_visual = visual_aggregator.buckets(captured_at)
        captured_contact_id = selected_contact_id

        def build_with_memory() -> None:
            try:
                contexts = []
                possible_contexts = []
                ambiguous = False
                semantic_available = False
                preference_notice = ""
                if memory_store is not None and captured_contact_id is not None:
                    query, date_query = memory_retrieval_inputs(captured_turns)
                    with MemoryStore(memory_store.path, verify=False) as worker_store:
                        result = worker_store.retrieve(
                            captured_contact_id,
                            query,
                            for_cloud=False,
                            date_query=date_query,
                            semantic_query=memory_semantic_input(captured_turns),
                            contact_cue_query=memory_semantic_input(
                                captured_turns,
                                speaker_role=SpeakerRole.SELECTED_CONTACT,
                            ),
                        )
                    test_log.emit("retrieval_result", generation=generation, snapshot_id=snapshot_id, contact_id=captured_contact_id, query=query, date_query=date_query, semantic_query=memory_semantic_input(captured_turns), result=result)
                    ambiguous = result.ambiguous
                    semantic_available = result.semantic_available
                    possible_contexts = [
                        RetrievedMemoryContext(
                            memory_id=item.memory_id,
                            revision_id=item.revision_id,
                            excerpt=textwrap.shorten(item.content, width=180, placeholder="…"),
                            memory_type=item.memory_type,
                            confidence=item.confidence,
                            sensitivity_safe=item.cloud_eligible,
                            rank=item.rank,
                            relevance=item.reason,
                        )
                        for item in result.matches[:4]
                    ]
                    if not ambiguous:
                        contexts = [item for item in possible_contexts if item.sensitivity_safe]
                    with MemoryStore(memory_store.path, verify=False) as worker_store:
                        available_memories = worker_store.list_current_memories(captured_contact_id)
                        test_log.emit("retrieval_corpus", generation=generation, snapshot_id=snapshot_id, contact_id=captured_contact_id, memories=[dict(row) for row in available_memories])
                        preferences = [row for row in available_memories
                            if row["memory_type"] in {"communication_style", "relationship_preference"}
                            and not row["needs_review"] and (row["sensitivity"] == "normal" or row["cloud_allowed"])]
                    if len(preferences) > 1:
                        preference_notice = "Multiple approved preferences: review for conflicts; at most two are supplied."
                    ranks = {item.memory_id: item.rank for item in possible_contexts}
                    preferences.sort(key=lambda row: ranks.get(row["memory_id"], 999))
                    styles = [RetrievedMemoryContext(memory_id=row["memory_id"], revision_id=row["revision_id"],
                        excerpt=textwrap.shorten(row["content"], width=180, placeholder="…"), memory_type=row["memory_type"], confidence=row["confidence"],
                        sensitivity_safe=True, rank=i + 1, relevance="approved contact communication preference")
                        for i, row in enumerate(preferences[:2])]
                    style_ids = {item.revision_id for item in styles}
                    contexts = [item for item in contexts if item.revision_id not in style_ids][:4 - len(styles)] + styles
                snapshot = build_snapshot(
                    captured_turns,
                    snapshot_id=snapshot_id,
                    generation=generation,
                    vocal_observations=captured_vocal,
                    visual_buckets=captured_visual,
                    contact_id=captured_contact_id,
                    retrieved_memories=contexts,
                    created_at=captured_at,
                )
                prepared = prepare_interpretation_request(snapshot, preserve_transcript=True)
                if prepared.memory_count != len(snapshot.memories):
                    snapshot = snapshot.model_copy(
                        update={"memories": snapshot.memories[:prepared.memory_count]}
                    )
                memory_snapshot_results.put(
                    (
                        generation,
                        snapshot_id,
                        snapshot,
                        ambiguous,
                        possible_contexts,
                        semantic_available,
                        None,
                        preference_notice,
                    )
                )
            except Exception as exc:
                try:
                    fallback = build_snapshot(
                        captured_turns, snapshot_id=snapshot_id, generation=generation,
                        vocal_observations=captured_vocal, visual_buckets=captured_visual,
                    )
                except Exception:
                    fallback = None
                memory_snapshot_results.put(
                    (generation, snapshot_id, fallback, False, [], False, type(exc).__name__, "")
                )

        if memory_store is not None and selected_contact_id is not None:
            submit_local("live", build_with_memory)
            return
        try:
            latest_interpretation_snapshot = build_snapshot(
                captured_turns,
                snapshot_id=snapshot_id,
                generation=generation,
                vocal_observations=captured_vocal,
                visual_buckets=captured_visual,
            )
        except ValueError:
            set_interpretation_unavailable(
                "Recent conversation exceeds the safe interpretation input limit",
                time.perf_counter(),
            )
            render_interpretation(replaced=True)
            return
        if interpretation_coordinator:
            interpretation_coordinator.offer(
                latest_interpretation_snapshot, time.perf_counter()
            )
            if not manual_terra_running:
                terra_reasoning.configure(state="readonly")
                terra_button.configure(state="normal")

    def poll_memory_results() -> None:
        nonlocal latest_interpretation_snapshot, next_interpretation_snapshot_id
        while True:
            try:
                generation, snapshot_id, snapshot, ambiguous, possibilities, semantic_available, error_type, preference_notice = memory_snapshot_results.get_nowait()
            except queue.Empty:
                break
            if generation != interpretation_generation or stopping:
                continue
            if (latest_interpretation_snapshot is not None and snapshot_id < latest_interpretation_snapshot.snapshot_id
                and (snapshot is None or max(t.display_order for t in snapshot.turns) <= max(t.display_order for t in latest_interpretation_snapshot.turns))):
                continue
            if snapshot is not None and latest_interpretation_snapshot is not None and snapshot_id < latest_interpretation_snapshot.snapshot_id:
                next_interpretation_snapshot_id += 1
                snapshot = snapshot.model_copy(update={"snapshot_id": next_interpretation_snapshot_id})
            if snapshot is None:
                stable_interpretation.clear_memory_possibilities()
                if error_type == "ValueError":
                    set_interpretation_unavailable(
                        "Recent conversation exceeds the safe interpretation input limit",
                        time.perf_counter(),
                    )
                    render_interpretation(replaced=True)
                else:
                    memory_status_label.configure(
                        text="Local memory retrieval unavailable — interpretation continues without memory"
                    )
                    render_interpretation()
                continue
            if error_type:
                stable_interpretation.clear_memory_possibilities()
                memory_status_label.configure(text="Local memory retrieval unavailable — interpretation continues without memory")
            else:
                stable_interpretation.offer_memory_possibilities(
                    [item for item in possibilities if not item.sensitivity_safe and not ambiguous
                     and "lexical" in item.relevance], time.perf_counter()
                )
                if not ambiguous:
                    guidance_display.offer_local_remember([item for item in possibilities if not item.sensitivity_safe
                        and "lexical" in item.relevance], max(turn.display_order for turn in snapshot.turns), time.perf_counter())
                    render_guidance()
                if ambiguous:
                    memory_status_label.configure(text="Several memories may fit — ambiguous facts withheld; approved style preferences may still apply")
                elif snapshot.memories:
                    suffix = "" if semantic_available else " · indirect recall reduced"
                    shown = len(stable_interpretation.memory_possibilities)
                    memory_status_label.configure(text=f"Checking {len(snapshot.memories)} candidate memories for relevance · {shown} displayed{suffix}")
                elif stable_interpretation.memory_possibilities:
                    memory_status_label.configure(
                        text=f"Showing {len(stable_interpretation.memory_possibilities)} approved memory context item(s) · recent match retained briefly"
                    )
                else:
                    memory_status_label.configure(
                        text=(
                            "No eligible approved memory matched this snapshot"
                            if semantic_available
                            else "No lexical match — indirect recall reduced; run --install-memory-model"
                        )
                    )
            if preference_notice:
                memory_status_label.configure(text=memory_status_label.cget("text") + " · " + preference_notice)
            latest_interpretation_snapshot = snapshot
            render_interpretation()
            if interpretation_coordinator:
                interpretation_coordinator.offer(snapshot, time.perf_counter())
                if not manual_terra_running:
                    terra_reasoning.configure(state="readonly")
                    terra_button.configure(state="normal")
        while True:
            try:
                record_id, batch_id, error_type = memory_analysis_results.get_nowait()
            except queue.Empty:
                break
            if error_type:
                memory_status_label.configure(text=f"Conversation saved; memory analysis can be retried ({error_type})")
            else:
                memory_status_label.configure(text="Memory proposals are ready for review in Manage memory")

    def interpretation_error_message(error_type: str | None) -> str:
        if error_type == InterpretationBudgetExceeded.__name__:
            return "Interpretation session budget reached — local processing continues"
        if error_type == InterpretationAuthenticationUnavailable.__name__:
            return "OpenAI authentication unavailable — local processing continues"
        return "Cloud interpretation unavailable — local processing continues"

    def check_with_terra() -> None:
        nonlocal manual_terra_running
        item = latest_interpretation_snapshot
        ledger = usage_ledger
        if stopping or item is None or ledger is None:
            render_interpretation(note="Transcribed speech is required for Luna")
            return
        if manual_terra_running:
            return
        try:
            prepared = prepare_interpretation_request(item)
        except ValueError:
            set_interpretation_unavailable(
                "Recent conversation exceeds the safe Luna input limit",
                time.perf_counter(),
            )
            render_interpretation(replaced=True)
            return
        maximum = conservative_request_cost(LUNA_MODEL, prepared.estimated_input_tokens)
        if not messagebox.askyesno(
            "Check with Luna",
            f"Run one Luna {terra_reasoning.get()} request on the newest snapshot?\n\n"
            f"Conservative maximum: ${maximum:.4f}\n"
            f"This call's estimated interpretation spend: ${ledger.total_dollars:.4f}",
        ):
            return
        manual_terra_running = True
        terra_reasoning.configure(state="disabled")
        terra_button.configure(state="disabled")
        generation = interpretation_generation
        reasoning = terra_reasoning.get()

        def run() -> None:
            try:
                result = OpenAIInterpreter(
                    model=LUNA_MODEL,
                    reasoning=reasoning,
                    ledger=ledger,
                    is_current=lambda snapshot: snapshot.generation == interpretation_generation,
                    live=True,
                )(item)
            except Exception as exc:
                manual_terra_results.put(
                    (generation, item.snapshot_id, None, type(exc).__name__)
                )
            else:
                manual_terra_results.put(
                    (generation, item.snapshot_id, result, None)
                )

        threading.Thread(
            target=run, name="manual-terra-interpretation", daemon=True
        ).start()

    def poll_interpretation(now: float) -> None:
        if semantic_backfill_requested:
            schedule_semantic_backfill()
        poll_local()
        poll_memory_results()
        while True:
            try:
                record, result, error = review_results.get_nowait()
            except queue.Empty:
                break
            review_running.discard(record)
            if error:
                review_errors[record] = error
            memory_status_label.configure(text=f"Review pending: {error}" if error else "Summary draft and memory proposals ready for separate review.")
        nonlocal manual_terra_running
        suggest_button.configure(state="normal" if selected_contact_id and latest_interpretation_snapshot and
            interpretation_coordinator and not interpretation_coordinator.snapshot().in_flight and not stopping else "disabled")
        if interpretation_coordinator:
            for event in interpretation_coordinator.poll(now):
                test_log.emit("coordinator_event", generation=interpretation_generation, result=event)
                if event.kind == CoordinatorEventKind.ACCEPTED:
                    assert event.update is not None
                    if hasattr(event.update, "replies"):
                        from .guidance import selected_memory_context, reconcile_replies
                        guidance_update = reconcile_replies(event.update, turns)
                        if latest_interpretation_snapshot:
                            stable_interpretation.offer_memory_possibilities(
                                selected_memory_context(latest_interpretation_snapshot.memories, guidance_update), now)
                            memory_status_label.configure(text=f"Showing {len(stable_interpretation.memory_possibilities)} relevant memory context item(s)")
                        source_age = ((datetime.now(timezone.utc) - guidance_update.context_at).total_seconds()
                                      if guidance_update.context_at is not None else 0)
                        guidance_display.offer(guidance_update, now, source_age=source_age)
                        render_guidance()
                    if stable_interpretation.offer(event.update, now) == "replaced":
                        render_interpretation(replaced=True)
                elif event.kind == CoordinatorEventKind.ERROR:
                    set_interpretation_unavailable(
                        interpretation_error_message(event.error_type), now
                    )
                    render_interpretation(replaced=True)
                else:
                    render_interpretation()
        memory_expired = stable_interpretation.expire_memory_possibilities(now)
        previous_guidance = repr((guidance_display.items, guidance_display.local_remember))
        guidance_display.tick(now)
        if previous_guidance != repr((guidance_display.items, guidance_display.local_remember)):
            render_guidance()
        if memory_expired:
            if stable_interpretation.memory_possibilities:
                memory_status_label.configure(
                    text=f"Showing {len(stable_interpretation.memory_possibilities)} approved memory context item(s) · recent match retained briefly"
                )
            else:
                memory_status_label.configure(
                    text="No recent approved memory context is displayed"
                )
        if interpretation_coordinator and audio_session and not stopping:
            state = interpretation_coordinator.snapshot()
            if state.in_flight:
                activity = "Analyzing the conversation…"
            elif state.pending_snapshot_id is not None:
                activity = "Listening — next analysis is scheduled"
            elif not guidance_display.all_items("replies"):
                activity = "Listening — guidance is active"
            else:
                activity = "Listening — guidance is active"
            test_log.emit("guidance_waiting_state", state=state, activity=activity, last_speaker=turns[-1].speaker_role if turns else None)
            guidance_status.configure(text=activity)
        else:
            guidance_status.configure(text="Select a contact to enable guidance" if not selected_contact_id else "Start a call to receive live guidance")
        if stable_interpretation.tick(now):
            render_interpretation(replaced=True)
        elif memory_expired:
            render_interpretation()
        while True:
            try:
                generation, snapshot_id, result, error_type = (
                    manual_terra_results.get_nowait()
                )
            except queue.Empty:
                break
            manual_terra_running = False
            current = latest_interpretation_snapshot
            if current is not None and not stopping:
                terra_reasoning.configure(state="readonly")
                terra_button.configure(state="normal")
            if (
                generation != interpretation_generation
                or current is None
                or snapshot_id != current.snapshot_id
            ):
                render_interpretation(note="Luna result expired after newer context")
            elif error_type:
                set_interpretation_unavailable(
                    interpretation_error_message(error_type), now
                )
                render_interpretation(replaced=True, note="Luna check failed")
            elif stable_interpretation.offer(result, now, manual=True) == "unchanged":
                render_interpretation(note="Luna found no meaningful change")
            else:
                render_interpretation(replaced=True, note="Checked with Luna")

    terra_button.configure(command=check_with_terra)

    def suggest_now():
        nonlocal next_interpretation_snapshot_id, latest_interpretation_snapshot
        if latest_interpretation_snapshot and interpretation_coordinator and not stopping:
            guidance_display.dismissed.clear()
            next_interpretation_snapshot_id += 1
            checkpoint = datetime.now(timezone.utc)
            latest_interpretation_snapshot = latest_interpretation_snapshot.model_copy(update={
                "snapshot_id": next_interpretation_snapshot_id, "manual": True,
                "created_at": checkpoint, "visual_buckets": list(visual_aggregator.buckets(checkpoint))})
            interpretation_coordinator.offer(latest_interpretation_snapshot, time.perf_counter(), manual=True)
            suggest_button.configure(state="disabled")

    suggest_button.configure(command=suggest_now)

    def show_home() -> None:
        live_screen.pack_forget()
        home_screen.pack(fill="both", expand=True)
        screen_host.pack_propagate(False)
        screen_host.configure(width=1120, height=730)
        root.pack_propagate(False)
        root.minsize(900, 640)
        root.geometry("1120x730")
        model_box.configure(state="readonly")

    def show_live() -> None:
        home_screen.pack_forget()
        live_screen.pack(fill="both", expand=True)
        root.minsize(470, 650)
        height = min(860, max(650, root.winfo_screenheight() - 90))
        width = 510
        screen_host.pack_propagate(False)
        screen_host.configure(width=width, height=height)
        root.pack_propagate(False)
        x = max(0, root.winfo_screenwidth() - width - 24)
        root.geometry(f"{width}x{height}+{x}+28")
        live_contact_label.configure(text=selected_contact_label or call_speaker_fallback)
        live_meta_label.configure(text=f"{live_model_choice.get()} · $0.0000 this call")
        model_box.configure(state="disabled")

    def set_running(running: bool) -> None:
        window_list.configure(state="disabled" if running else "normal")
        refresh_button.configure(state="disabled" if running else "normal")
        start_button.configure(state="disabled" if running else "normal")
        stop_button.configure(state="normal" if running else "disabled")
        import_button.configure(state="disabled" if running else "normal")
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
        terra_state = (
            "readonly"
            if running and latest_interpretation_snapshot and not manual_terra_running
            else "disabled"
        )
        terra_reasoning.configure(state=terra_state)
        terra_button.configure(
            state="normal" if terra_state == "readonly" else "disabled"
        )
        if running:
            show_live()
        elif not stopping:
            show_home()

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

    def finish_memory_record() -> None:
        nonlocal current_record_id, selected_contact_id
        if memory_store is None or current_record_id is None:
            current_record_id = None
            return
        record_id = current_record_id
        try:
            memory_store.stop_record(record_id)
            if selected_contact_id is None and messagebox.askyesno(
                "Unassigned Conversation",
                "Assign this conversation now so it can produce contact memory?\n\n"
                "Choose No to keep it under Unassigned Conversations without retrieval or extraction.",
            ):
                name = simpledialog.askstring("Assign conversation", "Contact name or alias:", parent=root)
                if name:
                    candidates = []
                    try:
                        contact = memory_store.resolve_contact(name)
                    except AmbiguousContact as exc:
                        labels = "\n".join(item.label for item in exc.candidates)
                        messagebox.showinfo("Ambiguous contact", f"Choose the contact explicitly in the contact control:\n{labels}")
                        contact = None
                        candidates = list(exc.candidates)
                    if contact is None and not candidates:
                        candidates = memory_store.list_contacts(name)
                        if candidates:
                            labels = "\n".join(item.label for item in candidates)
                            messagebox.showinfo(
                                "Choose contact",
                                f"This name has possible matches. Choose one explicitly in the contact control:\n{labels}",
                            )
                        else:
                            contact = memory_store.create_contact(
                                name, timezone_name=str(datetime.now().astimezone().tzinfo)
                            )
                    if contact is not None:
                        if set_selected_contact(contact.id):
                            refresh_contact_choices()
            if selected_contact_id is None:
                memory_status_label.configure(text="Conversation kept under Unassigned Conversations; no memory analysis ran")
                current_record_id = None
                return
            current_record_id = None
        except Exception as exc:
            memory_status_label.configure(text=f"Conversation finalization failed ({type(exc).__name__})")
            current_record_id = None
            return

        ledger = usage_ledger
        try:
            _chunks, _estimate = review_estimate(memory_store, record_id)
        except KeyError:
            memory_status_label.configure(text="Conversation record unavailable; memory analysis did not run")
            return
        except ValueError:
            memory_status_label.configure(text="Conversation saved; a turn exceeds the extraction limit, so analysis did not run")
            return
        open_review(record_id)
        if ledger is None:
            memory_status_label.configure(
                text="Conversation saved; review remains pending until generation is available"
            )
            current_record_id = None
            return

        if start_review_job(record_id, ledger):
            memory_status_label.configure(text="Conversation saved; preparing bounded summary and existing memory proposals")
        current_record_id = None

    def stop() -> None:
        nonlocal stopping, stop_started, interpretation_generation
        nonlocal latest_interpretation_snapshot
        if stopping:
            return
        stopping = True
        test_log.emit("call_stop", generation=interpretation_generation, records=usage_ledger.records if usage_ledger else (), committed_dollars=usage_ledger.committed_dollars if usage_ledger else 0)
        if usage_ledger:
            usage_ledger.stopped = True
        guidance_display.reset()
        render_guidance()
        local_pending["live"] = None
        interpretation_generation += 1
        latest_interpretation_snapshot = None
        stable_interpretation.clear_memory_possibilities()
        if interpretation_coordinator:
            interpretation_coordinator.reset(interpretation_generation)
        stop_started = time.perf_counter()
        stop_button.configure(state="disabled")
        switch_button.configure(state="disabled")
        terra_reasoning.configure(state="disabled")
        terra_button.configure(state="disabled")
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
        nonlocal audio_catalog, session, audio_session, current_record_id
        nonlocal call_speaker_fallback
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
        test_log.emit("call_window_selected", display_name=window.display_name, microphone=microphone_box.get(), playback=playback_box.get(), language=language_box.get())
        call_speaker_fallback = window.display_name
        turns.clear()
        vocal_observations.clear()
        visual_aggregator.reset()
        begin_interpretation_session()
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
        if memory_store is not None:
            try:
                current_record_id = memory_store.create_record(
                    source_kind="call",
                    source_label=window.kind,
                    timezone_name=str(datetime.now().astimezone().tzinfo),
                    contact_id=selected_contact_id,
                    status="active",
                )
            except Exception as exc:
                current_record_id = None
                memory_status_label.configure(text=f"Call continues without durable text memory ({type(exc).__name__})")
        audio_ready = (
            not audio_runtime_error
            and audio_catalog is not None
            and microphone_box.current() >= 0
            and playback_box.current() >= 0
        )
        if audio_ready:
            try:
                assert audio_catalog is not None
                language = production_transcription_language(language_box.get())
                audio_session = AudioCallSession(
                    audio_catalog,
                    audio_catalog.microphones[microphone_box.current()],
                    audio_catalog.playbacks[playback_box.current()],
                    language,
                    contact_name=selected_contact_label or call_speaker_fallback,
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
            test_log.emit("transcript", record_id=current_record_id, generation=interpretation_generation, turn=turn, vocal=draft.vocal)
            if memory_store is not None and current_record_id is not None:
                try:
                    memory_store.append_turn(current_record_id, turn)
                except Exception as exc:
                    memory_status_label.configure(text=f"Conversation text persistence failed ({type(exc).__name__})")
            vocal = _vocal_observation_from_audio(draft, turn.display_order)
            if vocal is not None:
                vocal_observations.append(vocal)
            offer_interpretation_snapshot()
            render_transcript_turns((turn,), replace=False)

    def switch() -> None:
        test_log.emit("face_switch_requested")
        if session:
            visual_aggregator.reset()
            if session.snapshot().status == "Face lost":
                session.continue_tracking()
            else:
                invalidate_memory_context()
                session.switch_face()

    def poll_once() -> None:
        nonlocal audio_catalog, audio_runtime_error, session, audio_session, thumbnail_photo, stopping, current_record_id
        if test_log.startup_error:
            root.title("Conversation Copilot — LOG FAILED: " + test_log.startup_error)
        elif test_log.active:
            root.title("Conversation Copilot — " + ("LOG FAILED: " + test_log.active.error if test_log.active.error else "Private test logging ON"))
        current = session
        if current:
            snapshot = current.snapshot()
            observed_at = capture_clock_origin + timedelta(seconds=time.perf_counter())
            signal = snapshot.current_signal
            captured_at = (capture_clock_origin + timedelta(seconds=signal.timestamp_ms / 1000)) if signal else None
            visual_aggregator.add(signal, observed_at, captured_at=captured_at)
            if test_log.active:
                test_log.emit("visual", generation=interpretation_generation, contact_id=selected_contact_id, observed_at=observed_at, captured_at=captured_at, status=snapshot.status, face_count=snapshot.face_count, signal_timestamp_ms=signal.timestamp_ms if signal else None, face_box=signal.face_box if signal else None, blendshapes=dict(signal.blendshapes) if signal else None, expressions=visual_aggregator.expressions(), buckets=visual_aggregator.buckets(observed_at)[-1:])
            status_label.configure(text="Face tracking paused — select Continue tracking" if snapshot.status == "Face lost" else snapshot.status)
            live_face_label.configure(text="Face lost" if snapshot.status == "Face lost" else "Face selected")
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
            thumbnail_photo = None
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
        elif audio_session and audio_session.snapshot().running:
            visual_aggregator.add(None, datetime.now(timezone.utc))
        current_audio = audio_session
        if current_audio:
            snapshot = current_audio.snapshot()
            test_log.emit("audio_status", running=snapshot.running, microphone_status=snapshot.microphone_status, playback_status=snapshot.playback_status, fault=snapshot.fault)
            audio_status_label.configure(
                text=(
                    snapshot.fault
                    or f"Mic: {snapshot.microphone_status} · Playback: {snapshot.playback_status}"
                )
            )
            live_audio_label.configure(text=snapshot.fault or f"Mic {snapshot.microphone_status} · Call {snapshot.playback_status}")
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
        poll_interpretation(time.perf_counter())
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
                finish_memory_record()
                schedule_semantic_backfill()
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
                finish_memory_record()
                schedule_semantic_backfill()
                set_running(False)
                populate_audio_choices(initial=False)
            else:
                shutdown_handoff.put(error)

    def poll() -> None:
        try:
            poll_once()
        except Exception as exc:
            test_log.emit("ui_poll_error", error_type=type(exc).__name__)
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
            if memory_store is not None:
                if current_record_id is not None:
                    try:
                        memory_store.stop_record(current_record_id)
                    except Exception:
                        pass
                memory_store.close()
            root.destroy()

    refresh_button.configure(command=refresh)
    start_button.configure(command=start)
    stop_button.configure(command=stop)
    switch_button.configure(command=switch)
    root.protocol("WM_DELETE_WINDOW", close)
    apply_readability()
    refresh(initial_audio=True)
    poll()
    root.mainloop()
    test_log.emit("app_closed")


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
        "--install-memory-model",
        action="store_true",
        help="install the approved local indirect-memory retrieval model",
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
    actions.add_argument(
        "--evaluate-f04",
        action="store_true",
        help="run the capped paid F04 model comparison",
    )
    actions.add_argument(
        "--evaluate-f05-local",
        action="store_true",
        help="run the F05 fixed retrieval and 100k-revision local gates",
    )
    actions.add_argument(
        "--evaluate-f05-real",
        action="store_true",
        help="run the capped fictional-data F05 extraction profile comparison",
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
    elif args.install_memory_model:
        try:
            from .memory import MemoryStore
            from .semantic import install_model

            with MemoryStore() as store:
                details = install_model(store.semantic_cache_dir)
                details["embedded_memories"] = store.backfill_semantic_embeddings()
            print(json.dumps(details, sort_keys=True))
        except Exception as exc:
            print(f"Memory model installation failed ({type(exc).__name__}): {exc}", file=sys.stderr)
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
    elif args.evaluate_f04:
        try:
            from .f04_evaluation import run_real_evaluation

            print(run_real_evaluation())
        except Exception as exc:
            print(
                f"F04 evaluation stopped safely ({type(exc).__name__})",
                file=sys.stderr,
            )
            return 1
    elif args.evaluate_f05_local:
        try:
            from .f05_evaluation import run_local_evaluation

            print(run_local_evaluation())
        except Exception as exc:
            print(f"F05 local evaluation failed ({type(exc).__name__}): {exc}", file=sys.stderr)
            return 1
    elif args.evaluate_f05_real:
        try:
            from .f05_evaluation import run_real_extraction_evaluation

            print(run_real_extraction_evaluation())
        except Exception as exc:
            print(f"F05 real evaluation stopped safely ({type(exc).__name__})", file=sys.stderr)
            return 1
    else:
        show_window(summary)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
