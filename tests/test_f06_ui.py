"""Isolated Tk integration for the F10 shell; no device or real model work."""
import gc
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, ttk

from conversation_copilot import ask_memory, audio, memory, windows
from conversation_copilot.__main__ import show_window
from conversation_copilot.f06_evaluation import seed_case
from conversation_copilot.models import ConversationTurn, SpeakerRole
from conversation_copilot.windows import CallWindow


def test_f10_home_ask_review_and_settings(tmp_path, monkeypatch):
    path = tmp_path / "ui.sqlite3"
    original_store = memory.MemoryStore
    with original_store(path) as store:
        session, _memory_id = seed_case(store, "appointment")
        contact_id = session.contact_id
        record = store.create_record(
            source_kind="call", source_label="UI narrative fixture", timezone_name="UTC",
            contact_id=contact_id, status="stopped", turns=[ConversationTurn(
                speaker_name="Yaheli", speaker_role=SpeakerRole.SELECTED_CONTACT,
                source="fixture", content="We discussed the book and will meet Friday.", display_order=1,
            )],
        )
        batch = store.create_batch(record, model="fake", reasoning="none")
        store.store_proposals(batch, [memory.MemoryProposalInput(
            content="Meet Friday", memory_type="event_date", confidence="high", evidence_turns=[1],
        )])
        store.create_summary_draft(record, memory.SummaryOutput(statements=[memory.SummaryStatementInput(
            section="discussed", content="They discussed the book and planned to meet Friday.",
            kind="fact", confidence="high", evidence_turns=[1],
        )]), expected_generation=1)

    class IsolatedStore(original_store):
        def __init__(self, selected_path=None, **kwargs):
            super().__init__(selected_path or path, **kwargs)

    monkeypatch.setattr(memory, "MemoryStore", IsolatedStore)
    monkeypatch.setattr(IsolatedStore, "backfill_semantic_embeddings", lambda self, **kwargs: 0)
    monkeypatch.setattr(audio, "local_model_available", lambda: False)
    monkeypatch.setattr(windows, "list_call_windows", lambda: [])
    monkeypatch.setattr(messagebox, "askyesno", lambda *a, **k: True)
    monkeypatch.setattr(messagebox, "showinfo", lambda *a, **k: None)
    monkeypatch.setattr(messagebox, "showerror", lambda *a, **k: None)
    monkeypatch.setattr(
        ask_memory, "cloud_answer",
        lambda store, text, sources, **kwargs: ask_memory.AskSession(contact_id).answer(
            store, "What time is the dentist appointment?"
        ),
    )

    failures = []
    completed = []
    real_tk, real_top = tk.Tk, tk.Toplevel

    def descendants(widget):
        result = []
        for child in widget.winfo_children():
            result.append(child)
            result.extend(descendants(child))
        return result

    def button(widget, text):
        return next(w for w in descendants(widget)
                    if isinstance(w, (tk.Button, ttk.Button)) and w.cget("text") == text)

    def top(*args, **kwargs):
        widget = real_top(*args, **kwargs)
        widget.withdraw()
        return widget

    monkeypatch.setattr(tk, "Toplevel", top)

    def create_root():
        root = real_tk()
        root.withdraw()
        root.report_callback_exception = lambda *args: failures.append(args[1])

        def check(callback):
            try:
                callback()
            except Exception as exc:
                failures.append(exc)
                if root.winfo_exists():
                    root.destroy()

        def start():
            widgets = descendants(root)
            assert not any(isinstance(widget, tk.Canvas) for widget in widgets)
            assert button(root, "Start call")
            assert button(root, "Settings")
            contact_box = next(widget for widget in widgets if isinstance(widget, ttk.Combobox)
                               and any(str(value).startswith("Yaheli") for value in widget.cget("values")))
            contact_box.current(next(i for i, value in enumerate(contact_box.cget("values"))
                                     if str(value).startswith("Yaheli")))
            button(root, "Select").invoke()

            button(root, "Ask Memory").invoke()
            ask = next(widget for widget in root.winfo_children()
                       if isinstance(widget, real_top) and widget.title() == "Ask Memory")
            assert button(ask, "Submit")
            assert not any(isinstance(widget, tk.Button) and widget.cget("text") in {"Ask locally", "Use cloud help"}
                           for widget in descendants(ask))
            scope = next(widget for widget in descendants(ask) if isinstance(widget, ttk.Combobox))
            scope.current(next(i for i, value in enumerate(scope.cget("values"))
                               if str(value).startswith("Yaheli")))
            scope.event_generate("<<ComboboxSelected>>")
            question = next(widget for widget in descendants(ask)
                            if isinstance(widget, tk.Entry) and not isinstance(widget, ttk.Combobox))
            question.insert(0, "What time is the dentist appointment?")
            button(ask, "Submit").invoke()
            root.after(350, lambda: check(lambda: ask_done(ask)))

        def ask_done(ask):
            assert "3 PM" in next(widget for widget in descendants(ask)
                                  if isinstance(widget, tk.Text)).get("1.0", "end")
            ask.destroy()
            button(root, "Settings").invoke()
            settings = next(widget for widget in root.winfo_children()
                            if isinstance(widget, real_top) and widget.title() == "Settings")
            assert button(settings, "Save settings")
            assert button(settings, "Edit aliases")
            settings.destroy()
            button(root, "Conversation history").invoke()
            chooser = next(widget for widget in root.winfo_children()
                           if isinstance(widget, real_top) and widget.title() == "Review one conversation")
            options = next(widget for widget in descendants(chooser) if isinstance(widget, tk.Listbox))
            options.selection_set(next(i for i, text in enumerate(options.get(0, tk.END))
                                       if "UI narrative fixture" in text))
            button(chooser, "Review selected record").invoke()
            review = next(widget for widget in root.winfo_children()
                          if isinstance(widget, real_top) and widget.title() == "Summary and memories")
            assert button(review, "Approve selected")
            assert button(review, "Reject all")
            assert button(review, "Approve all memories + summary")
            assert button(review, "Summary versions")
            assert not any(isinstance(widget, tk.Button) and "cloud" in str(widget.cget("text")).casefold()
                           for widget in descendants(review))
            assert "They discussed the book" in next(widget for widget in descendants(review)
                                                      if isinstance(widget, tk.Text)).get("1.0", tk.END)
            completed.append(True)
            root.destroy()

        root.after(50, lambda: check(start))
        root.after(5000, root.destroy)
        return root

    monkeypatch.setattr(tk, "Tk", create_root)
    try:
        show_window("F10 isolated UI fixture")
    finally:
        gc.collect()
    assert failures == []
    assert completed == [True]


def test_f10_live_is_compact_and_returns_home(tmp_path, monkeypatch):
    path = tmp_path / "live.sqlite3"
    original_store = memory.MemoryStore
    class IsolatedStore(original_store):
        def __init__(self, selected_path=None, **kwargs):
            super().__init__(selected_path or path, **kwargs)

    class FakeVideo:
        instances = []
        def __init__(self, _window):
            from types import SimpleNamespace
            self.worker_alive = True
            self.capture = SimpleNamespace(worker_alive=True)
            self.switched = 0
            FakeVideo.instances.append(self)
        def start(self):
            pass
        def stop(self):
            self.worker_alive = False
            self.capture.worker_alive = False
        def switch_face(self):
            self.switched += 1
        def continue_tracking(self):
            self.switched += 1
        def snapshot(self):
            from types import SimpleNamespace
            return SimpleNamespace(
                status="Tracking", signal_rate=4.0, face_count=1, landmark_count=478,
                blendshape_count=52, thumbnail_rgb=None, current_signal=None,
            )

    monkeypatch.setattr(memory, "MemoryStore", IsolatedStore)
    monkeypatch.setattr(IsolatedStore, "backfill_semantic_embeddings", lambda self, **kwargs: 0)
    monkeypatch.setattr(audio, "local_model_available", lambda: False)
    monkeypatch.setattr(windows, "list_call_windows", lambda: [CallWindow(1, "Fictional call", "fixture.exe", "Fixture")])
    import conversation_copilot.video as video
    monkeypatch.setattr(video, "LiveVideoSession", FakeVideo)
    monkeypatch.setattr(messagebox, "askyesno", lambda *a, **k: False)
    monkeypatch.setattr(messagebox, "showinfo", lambda *a, **k: None)

    failures, completed = [], []
    real_tk, real_top = tk.Tk, tk.Toplevel
    def descendants(widget):
        result = []
        for child in widget.winfo_children():
            result.append(child)
            result.extend(descendants(child))
        return result
    def button(widget, text):
        return next(w for w in descendants(widget)
                    if isinstance(w, (tk.Button, ttk.Button)) and w.cget("text") == text)
    def top(*args, **kwargs):
        widget = real_top(*args, **kwargs)
        widget.withdraw()
        return widget
    monkeypatch.setattr(tk, "Toplevel", top)

    def create_root():
        root = real_tk()
        root.withdraw()
        root.report_callback_exception = lambda *args: failures.append(args[1])
        def check(callback):
            try:
                callback()
            except Exception as exc:
                failures.append(exc)
                if root.winfo_exists():
                    root.destroy()
        def start():
            window_list = next(w for w in descendants(root) if isinstance(w, tk.Listbox)
                               and "Fictional call" in str(w.get(0, tk.END)))
            window_list.selection_set(0)
            button(root, "Start call").invoke()
            root.update_idletasks()
            live = next(w for w in root.winfo_children()[0].winfo_children()
                        if any(isinstance(child, ttk.Button) and child.cget("text") == "End call"
                               for child in descendants(w)))
            assert live.winfo_manager() == "pack"
            for text in ("End call", "Refresh all", "Transcript", "Ask Memory", "Switch face"):
                assert button(root, text)
            group_titles = {w.cget("text") for w in descendants(root) if isinstance(w, tk.LabelFrame)}
            assert {"Possible tone", "Social cue", "Potential responses", "Related memory", "Follow-up"} <= group_titles
            assert not any(isinstance(w, tk.Label) and w.cget("image") for w in descendants(root))
            button(root, "Switch face").invoke()
            assert FakeVideo.instances[-1].switched == 1
            button(root, "Transcript").invoke()
            transcript = next(w for w in root.winfo_children()
                              if isinstance(w, real_top) and w.title() == "Live transcript")
            assert "No finalized transcript" in next(w for w in descendants(transcript)
                                                      if isinstance(w, tk.Text)).get("1.0", tk.END)
            transcript.destroy()
            button(root, "End call").invoke()
            root.after(450, lambda: check(finished))
        def finished():
            assert button(root, "Start call")
            live = next(w for w in root.winfo_children()[0].winfo_children()
                        if any(isinstance(child, ttk.Button) and child.cget("text") == "End call"
                               for child in descendants(w)))
            assert not live.winfo_manager()
            completed.append(True)
            root.destroy()
        root.after(50, lambda: check(start))
        root.after(4000, root.destroy)
        return root

    monkeypatch.setattr(tk, "Tk", create_root)
    try:
        show_window("F10 live UI fixture")
    finally:
        gc.collect()
    assert failures == []
    assert completed == [True]
