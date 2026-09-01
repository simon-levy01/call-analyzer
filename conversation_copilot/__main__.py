import argparse
import json
import sqlite3
import sys
import textwrap
from datetime import datetime, timezone
from pathlib import Path

from pydantic import ValidationError

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
        OpenAIInterpreter,
        RetrievedMemoryContext,
        StableInterpretationCard,
        TERRA_MODEL,
        UsageLedger,
        VisualAggregator,
        VocalObservation,
        build_snapshot,
        conservative_request_cost,
        format_interpretation_body,
        prepare_interpretation_request,
    )
    from .models import ConversationTurn, SpeakerRole
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

    root = tk.Tk()
    root.title("Conversation Copilot")
    root.geometry("1280x680")
    root.minsize(1000, 560)
    main_pane = tk.PanedWindow(root, orient=tk.HORIZONTAL, sashrelief=tk.RAISED)
    main_pane.pack(fill="both", expand=True)
    left_column = tk.Frame(main_pane)
    transcript_column = tk.LabelFrame(main_pane, text="Final transcript")
    main_pane.add(left_column, minsize=760, stretch="always")
    main_pane.add(transcript_column, minsize=320, stretch="always")
    tk.Label(left_column, text=summary, justify="left", padx=12, pady=8).pack(anchor="w")
    tk.Label(left_column, text="Visible call windows").pack(anchor="w", padx=12)
    window_list = tk.Listbox(left_column, height=7)
    window_list.pack(fill="x", padx=12, pady=4)
    memory_store = None
    memory_startup_error = ""
    semantic_backfill_lock = threading.Lock()
    try:
        memory_store = MemoryStore()
    except MemoryStoreUnavailable as exc:
        memory_startup_error = str(exc)
    contact_frame = tk.LabelFrame(left_column, text="Selected Contact — confirm before memory is used")
    contact_frame.pack(fill="x", padx=12, pady=4)
    contact_query = tk.Entry(contact_frame)
    contact_query.grid(row=0, column=0, sticky="ew", padx=6, pady=5)
    contact_box = ttk.Combobox(contact_frame, state="readonly", width=35)
    contact_box.grid(row=0, column=1, sticky="ew", padx=6, pady=5)
    contact_search_button = tk.Button(contact_frame, text="Search")
    contact_search_button.grid(row=0, column=2, padx=3)
    contact_select_button = tk.Button(contact_frame, text="Select")
    contact_select_button.grid(row=0, column=3, padx=3)
    contact_create_button = tk.Button(contact_frame, text="Create Contact")
    contact_create_button.grid(row=0, column=4, padx=3)
    contact_clear_button = tk.Button(contact_frame, text="Clear")
    contact_clear_button.grid(row=0, column=5, padx=3)
    memory_manage_button = tk.Button(contact_frame, text="Manage memory")
    memory_manage_button.grid(row=0, column=6, padx=3)
    import_button = tk.Button(contact_frame, text="Import chat")
    import_button.grid(row=0, column=7, padx=3)
    unassigned_button = tk.Button(contact_frame, text="Unassigned")
    unassigned_button.grid(row=0, column=8, padx=3)
    contact_frame.columnconfigure(0, weight=1)
    contact_frame.columnconfigure(1, weight=1)
    confirmed_contact_label = tk.Label(contact_frame, text="Confirmed contact: none", anchor="w")
    confirmed_contact_label.grid(row=1, column=0, columnspan=9, sticky="ew", padx=6)
    memory_status_label = tk.Label(
        contact_frame,
        text=(memory_startup_error or "No contact confirmed — retrieval and extraction are off"),
        anchor="w",
    )
    memory_status_label.grid(row=2, column=0, columnspan=9, sticky="ew", padx=6, pady=(0, 5))
    tk.Label(
        contact_frame,
        text="Assigned calls retain attributed text locally; after Stop, bounded text may be sent to OpenAI for proposals (store=false).",
        fg="#7a3f00",
        anchor="w",
    ).grid(row=3, column=0, columnspan=9, sticky="ew", padx=6, pady=(0, 5))
    audio_controls = tk.LabelFrame(left_column, text="Two-sided local transcription")
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
    controls = tk.Frame(left_column)
    controls.pack(fill="x", padx=12)
    refresh_button = tk.Button(controls, text="Refresh")
    start_button = tk.Button(controls, text="Start")
    stop_button = tk.Button(controls, text="Stop", state="disabled")
    switch_button = tk.Button(controls, text="Switch face", state="disabled")
    for button in (refresh_button, start_button, stop_button, switch_button):
        button.pack(side="left", padx=(0, 6))
    selected_label = tk.Label(left_column, text="Selected: none", anchor="w")
    selected_label.pack(fill="x", padx=12, pady=(10, 0))
    status_label = tk.Label(left_column, text="Select a call window", anchor="w")
    status_label.pack(fill="x", padx=12)
    metrics_label = tk.Label(left_column, text="Signals: 0/s · faces: 0 · landmarks: 0 · blendshapes: 0")
    metrics_label.pack(anchor="w", padx=12)
    audio_status_label = tk.Label(left_column, text="Audio devices loading", anchor="w")
    audio_status_label.pack(fill="x", padx=12)
    interpretation_frame = tk.LabelFrame(left_column, text="Conversation interpretation")
    interpretation_frame.pack(fill="x", padx=12, pady=6)
    interpretation_status_label = tk.Label(
        interpretation_frame,
        text="Waiting for a call",
        anchor="w",
        font=("TkDefaultFont", 10, "bold"),
    )
    interpretation_status_label.pack(fill="x", padx=8, pady=(6, 2))
    interpretation_body_label = tk.Label(
        interpretation_frame,
        text="Hypotheses only — never a claim about true emotion or intention.",
        anchor="w",
        justify="left",
        wraplength=710,
    )
    interpretation_body_label.pack(fill="x", padx=8)
    interpretation_meta_label = tk.Label(
        interpretation_frame,
        text="This call's estimated interpretation spend: $0.0000",
        anchor="w",
    )
    interpretation_meta_label.pack(fill="x", padx=8, pady=(2, 4))
    terra_controls = tk.Frame(interpretation_frame)
    terra_controls.pack(fill="x", padx=8, pady=(0, 6))
    tk.Label(terra_controls, text="Terra reasoning").pack(side="left")
    terra_reasoning = ttk.Combobox(
        terra_controls, state="disabled", values=("none", "low"), width=8
    )
    terra_reasoning.current(0)
    terra_reasoning.pack(side="left", padx=6)
    terra_button = tk.Button(
        terra_controls, text="Check with Terra", state="disabled"
    )
    terra_button.pack(side="left")
    thumbnail_label = tk.Label(transcript_column, text="No selected face", width=160, height=120)
    transcript_title = tk.Label(transcript_column, text="Finalized attributed text", anchor="w")
    transcript_title.pack(fill="x", padx=8, pady=(6, 0))
    transcript = tk.Text(transcript_column, state="disabled", wrap="word")
    transcript.pack(fill="both", expand=True, padx=8, pady=(2, 8))

    windows = []
    session: LiveVideoSession | None = None
    audio_catalog: AudioDeviceCatalog | None = None
    audio_session: AudioCallSession | None = None
    turns: list[ConversationTurn] = []
    vocal_observations: list[VocalObservation] = []
    visual_aggregator = VisualAggregator()
    usage_ledger: UsageLedger | None = None
    stable_interpretation = StableInterpretationCard()
    interpretation_coordinator: InterpretationCoordinator | None = None
    interpretation_generation = 0
    next_interpretation_snapshot_id = 0
    latest_interpretation_snapshot = None
    interpretation_updated_at = ""
    manual_terra_running = False
    manual_terra_results: queue.SimpleQueue[tuple] = queue.SimpleQueue()
    memory_snapshot_results: queue.SimpleQueue[tuple] = queue.SimpleQueue()
    memory_analysis_results: queue.SimpleQueue[tuple] = queue.SimpleQueue()
    latest_memory_possibilities: list[RetrievedMemoryContext] = []
    contact_choices = []
    selected_contact_id: str | None = None
    selected_contact_label: str | None = None
    call_speaker_fallback = "Contact"
    current_record_id: str | None = None
    stopping = False
    stop_started = 0.0
    shutdown_handoff: queue.SimpleQueue[str] = queue.SimpleQueue()
    thumbnail_photo = None

    def render_interpretation(*, replaced: bool = False, note: str = "") -> None:
        nonlocal interpretation_updated_at
        if replaced:
            interpretation_updated_at = datetime.now().astimezone().strftime("%H:%M:%S")
        update = stable_interpretation.update
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
            update, stable_interpretation.message, latest_memory_possibilities
        ))
        spend = usage_ledger.total_dollars if usage_ledger else 0.0
        warning = " · Warning threshold reached" if usage_ledger and usage_ledger.warning_reached else ""
        updated = f" · Updated {interpretation_updated_at}" if interpretation_updated_at else ""
        extra = f" · {note}" if note else ""
        interpretation_meta_label.configure(
            text=f"This call's estimated interpretation spend: ${spend:.4f}{updated}{warning}{extra}"
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
        if memory_store is None or not semantic_backfill_lock.acquire(blocking=False):
            return
        worker_path = memory_store.path

        def backfill() -> None:
            try:
                with MemoryStore(worker_path, verify=False) as worker_store:
                    worker_store.backfill_semantic_embeddings()
            except Exception:
                pass
            finally:
                semantic_backfill_lock.release()

        threading.Thread(target=backfill, name="contact-memory-embedding", daemon=True).start()

    schedule_semantic_backfill()

    def invalidate_memory_context() -> None:
        nonlocal interpretation_generation, latest_interpretation_snapshot
        nonlocal next_interpretation_snapshot_id, latest_memory_possibilities
        interpretation_generation += 1
        next_interpretation_snapshot_id = 0
        latest_interpretation_snapshot = None
        latest_memory_possibilities = []
        stable_interpretation.reset()
        if interpretation_coordinator:
            interpretation_coordinator.reset(interpretation_generation)
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

    def manage_memory() -> None:
        if memory_store is None or selected_contact_id is None:
            messagebox.showinfo("Contact memory", "Confirm one contact first.")
            return
        contact_id = selected_contact_id
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
                items.insert(
                    tk.END,
                    f"Proposal · {row['state']} · {type_labels[row['memory_type']]} · "
                    f"{row['confidence']} confidence · {row['sensitivity']}{duplicate} · {row['content']}",
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
                    items.insert(
                        tk.END,
                        f"Proposal · {row['state']} · {type_labels[row['memory_type']]} · "
                        f"{row['confidence']} confidence · {row['sensitivity']} · {row['content']}",
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
                "Merge contacts", f"Keep {memory_store.get_contact(contact_id).label} and merge {merged.label}?\n\n{details}\n\nSimilar memories stay separate and are marked for review.",
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
                        _chunks, estimate = extraction_maximum_cost(record_turns)
                    except ValueError as exc:
                        messagebox.showerror("Retry analysis", str(exc), parent=dialog)
                        return
                    if estimate > 0.25:
                        messagebox.showwarning("Retry analysis", f"Estimated maximum ${estimate:.4f} exceeds the $0.25 run limit.", parent=dialog)
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
            ("Cloud permission", toggle_cloud_permission), ("Connect", connect_selected),
            ("Edit contact", edit_contact), ("Aliases", manage_aliases),
            ("Retry analysis", lambda: choose_record("retry")),
            ("Delete source", lambda: choose_record("delete")), ("Reassign source", lambda: choose_record("reassign")),
            ("Export JSON", export_contact), ("Merge contact", merge_contact), ("Delete contact", delete_contact),
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
            estimated_chunks, estimate = extraction_maximum_cost(preview.turns)
        except ValueError:
            memory_status_label.configure(text="Imported conversation saved; a turn exceeds the extraction limit, so analysis did not run")
            return
        if estimate > 0.25:
            memory_status_label.configure(text=f"Imported conversation saved; ${estimate:.4f} estimate exceeds the $0.25 run limit")
            return
        if not messagebox.askyesno(
            "Analyze import", f"Saved attributed text only. Send {estimated_chunks} bounded text chunk(s) to OpenAI with store=false?\nMaximum estimated cost: ${estimate:.4f}",
        ):
            memory_status_label.configure(text="Imported conversation saved; analysis waits for explicit retry")
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

    contact_search_button.configure(command=refresh_contact_choices)
    contact_select_button.configure(command=select_contact)
    contact_create_button.configure(command=create_contact)
    contact_clear_button.configure(command=lambda: set_selected_contact(None))
    memory_manage_button.configure(command=manage_memory)
    import_button.configure(command=import_chat)
    unassigned_button.configure(command=show_unassigned)
    refresh_contact_choices()

    def begin_interpretation_session() -> None:
        nonlocal usage_ledger, interpretation_coordinator
        nonlocal interpretation_generation, next_interpretation_snapshot_id
        nonlocal latest_interpretation_snapshot, interpretation_updated_at
        nonlocal manual_terra_running, latest_memory_possibilities
        interpretation_generation += 1
        next_interpretation_snapshot_id = 0
        latest_interpretation_snapshot = None
        latest_memory_possibilities = []
        interpretation_updated_at = ""
        manual_terra_running = False
        stable_interpretation.reset()
        usage_ledger = None
        try:
            usage_ledger = UsageLedger()
            luna = OpenAIInterpreter(
                model=LUNA_MODEL,
                reasoning="low",
                ledger=usage_ledger,
                is_current=lambda item: item.generation == interpretation_generation,
            )
            interpretation_coordinator = InterpretationCoordinator(
                luna, generation=interpretation_generation
            )
        except InterpretationAuthenticationUnavailable:
            interpretation_coordinator = None
            stable_interpretation.show_unavailable(
                "OpenAI key not configured — local capture and transcription continue",
                time.perf_counter(),
            )
        except ValueError:
            interpretation_coordinator = None
            stable_interpretation.show_unavailable(
                "Interpretation budget configuration is invalid — local processing continues",
                time.perf_counter(),
            )
        except (ImportError, OSError):
            interpretation_coordinator = None
            stable_interpretation.show_unavailable(
                "Cloud interpretation unavailable — local processing continues",
                time.perf_counter(),
            )
        render_interpretation(replaced=True)

    def offer_interpretation_snapshot() -> None:
        nonlocal next_interpretation_snapshot_id, latest_interpretation_snapshot
        if stopping or len(turns) < 2:
            return
        next_interpretation_snapshot_id += 1
        snapshot_id = next_interpretation_snapshot_id
        generation = interpretation_generation
        captured_turns = [item.model_copy(deep=True) for item in turns]
        captured_vocal = list(vocal_observations)
        captured_visual = visual_aggregator.buckets()
        captured_contact_id = selected_contact_id

        def build_with_memory() -> None:
            try:
                contexts = []
                possible_contexts = []
                ambiguous = False
                semantic_available = False
                if memory_store is not None and captured_contact_id is not None:
                    query, date_query = memory_retrieval_inputs(captured_turns)
                    with MemoryStore(memory_store.path, verify=False) as worker_store:
                        result = worker_store.retrieve(
                            captured_contact_id,
                            query,
                            for_cloud=True,
                            date_query=date_query,
                            semantic_query=memory_semantic_input(captured_turns),
                            contact_cue_query=memory_semantic_input(
                                captured_turns,
                                speaker_role=SpeakerRole.SELECTED_CONTACT,
                            ),
                        )
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
                        contexts = possible_contexts
                snapshot = build_snapshot(
                    captured_turns,
                    snapshot_id=snapshot_id,
                    generation=generation,
                    vocal_observations=captured_vocal,
                    visual_buckets=captured_visual,
                    contact_id=captured_contact_id,
                    retrieved_memories=contexts,
                )
                prepared = prepare_interpretation_request(snapshot)
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
                    (generation, snapshot_id, fallback, False, [], False, type(exc).__name__)
                )

        if memory_store is not None and selected_contact_id is not None:
            threading.Thread(target=build_with_memory, name="contact-memory-retrieval", daemon=True).start()
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
            stable_interpretation.show_unavailable(
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
        nonlocal latest_interpretation_snapshot, latest_memory_possibilities
        while True:
            try:
                generation, snapshot_id, snapshot, ambiguous, possibilities, semantic_available, error_type = memory_snapshot_results.get_nowait()
            except queue.Empty:
                break
            if generation != interpretation_generation or stopping:
                continue
            if latest_interpretation_snapshot is not None and snapshot_id < latest_interpretation_snapshot.snapshot_id:
                continue
            if snapshot is None:
                if error_type == "ValueError":
                    stable_interpretation.show_unavailable(
                        "Recent conversation exceeds the safe interpretation input limit",
                        time.perf_counter(),
                    )
                    render_interpretation(replaced=True)
                else:
                    memory_status_label.configure(
                        text="Local memory retrieval unavailable — interpretation continues without memory"
                    )
                continue
            if error_type:
                memory_status_label.configure(text="Local memory retrieval unavailable — interpretation continues without memory")
            elif ambiguous:
                memory_status_label.configure(text="Several memories may fit — memory withheld; clarify the reference")
            elif snapshot.memories:
                suffix = "" if semantic_available else " · indirect recall reduced"
                memory_status_label.configure(text=f"Using {len(snapshot.memories)} approved memory excerpt(s) for the confirmed contact{suffix}")
            else:
                memory_status_label.configure(
                    text=(
                        "No eligible approved memory matched this snapshot"
                        if semantic_available
                        else "No lexical match — indirect recall reduced; run --install-memory-model"
                    )
                )
            latest_interpretation_snapshot = snapshot
            latest_memory_possibilities = possibilities
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
            render_interpretation(note="Two finalized turns are required for Terra")
            return
        if manual_terra_running:
            return
        try:
            prepared = prepare_interpretation_request(item)
        except ValueError:
            stable_interpretation.show_unavailable(
                "Recent conversation exceeds the safe Terra input limit",
                time.perf_counter(),
            )
            render_interpretation(replaced=True)
            return
        maximum = conservative_request_cost(
            TERRA_MODEL, prepared.estimated_input_tokens
        )
        if ledger.total_dollars + maximum > ledger.limits.hard_dollars:
            render_interpretation(note="Session budget reached — Terra unavailable")
            return
        if not messagebox.askyesno(
            "Check with Terra",
            f"Run one Terra {terra_reasoning.get()} request on the newest snapshot?\n\n"
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
                    model=TERRA_MODEL,
                    reasoning=reasoning,
                    ledger=ledger,
                    is_current=lambda snapshot: snapshot.generation == interpretation_generation,
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
        poll_memory_results()
        nonlocal manual_terra_running
        if interpretation_coordinator:
            for event in interpretation_coordinator.poll(now):
                if event.kind == CoordinatorEventKind.ACCEPTED:
                    assert event.update is not None
                    if stable_interpretation.offer(event.update, now) == "replaced":
                        render_interpretation(replaced=True)
                elif event.kind == CoordinatorEventKind.ERROR:
                    stable_interpretation.show_unavailable(
                        interpretation_error_message(event.error_type), now
                    )
                    render_interpretation(replaced=True)
                else:
                    render_interpretation()
        if stable_interpretation.tick(now):
            render_interpretation(replaced=True)
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
                render_interpretation(note="Terra result expired after newer context")
            elif error_type:
                stable_interpretation.show_unavailable(
                    interpretation_error_message(error_type), now
                )
                render_interpretation(replaced=True, note="Terra check failed")
            elif stable_interpretation.offer(result, now, manual=True) == "unchanged":
                render_interpretation(note="Terra found no meaningful change")
            else:
                render_interpretation(replaced=True, note="Checked with Terra")

    terra_button.configure(command=check_with_terra)

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

        worker_path = memory_store.path
        ledger = usage_ledger
        try:
            _chunks, estimate = extraction_maximum_cost(memory_store.record_turns(record_id))
        except KeyError:
            memory_status_label.configure(text="Conversation record unavailable; memory analysis did not run")
            return
        except ValueError:
            memory_status_label.configure(text="Conversation saved; a turn exceeds the extraction limit, so analysis did not run")
            return
        if ledger is None or ledger.total_dollars + estimate > ledger.limits.hard_dollars:
            memory_status_label.configure(
                text="Conversation saved; shared call budget cannot cover extraction, so analysis waits for manual retry"
            )
            current_record_id = None
            return

        def run_extraction() -> None:
            try:
                with MemoryStore(worker_path, verify=False) as worker_store:
                    extractor = OpenAIMemoryExtractor(ledger=ledger)
                    batch_id = analyze_record(worker_store, record_id, extractor)
            except Exception as exc:
                memory_analysis_results.put((record_id, None, type(exc).__name__))
            else:
                memory_analysis_results.put((record_id, batch_id, None))

        threading.Thread(target=run_extraction, name="post-call-memory-extraction", daemon=True).start()
        memory_status_label.configure(text="Conversation saved; extracting a bounded proposal batch")
        current_record_id = None

    def stop() -> None:
        nonlocal stopping, stop_started, interpretation_generation
        nonlocal latest_interpretation_snapshot, latest_memory_possibilities
        if stopping:
            return
        stopping = True
        interpretation_generation += 1
        latest_interpretation_snapshot = None
        latest_memory_possibilities = []
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
        if session:
            if session.snapshot().status == "Face lost":
                session.continue_tracking()
            else:
                session.switch_face()

    def poll_once() -> None:
        nonlocal audio_catalog, audio_runtime_error, session, audio_session, thumbnail_photo, stopping, current_record_id
        current = session
        if current:
            snapshot = current.snapshot()
            visual_aggregator.add(snapshot.current_signal, datetime.now(timezone.utc))
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
        elif audio_session and audio_session.snapshot().running:
            visual_aggregator.add(None, datetime.now(timezone.utc))
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
