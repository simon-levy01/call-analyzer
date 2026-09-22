"""Isolated Tk integration for the F10 shell; no device or real model work."""
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, ttk

from conversation_copilot import ask_memory, audio, memory, windows
from conversation_copilot.__main__ import show_window
from conversation_copilot.f06_evaluation import seed_case
from conversation_copilot.models import ConversationTurn, SpeakerRole
from conversation_copilot.ui_theme import RoundedButton
from conversation_copilot.windows import CallWindow


def test_f10_home_memories_review_and_settings(tmp_path, monkeypatch):
    path = tmp_path / "ui.sqlite3"
    monkeypatch.setenv("APPDATA", str(tmp_path))
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
        continue_tracking = switch_face
        def snapshot(self):
            from types import SimpleNamespace
            return SimpleNamespace(status="Tracking", signal_rate=4.0, face_count=1,
                                   landmark_count=478, blendshape_count=52,
                                   thumbnail_rgb=None, current_signal=None)

    monkeypatch.setattr(memory, "MemoryStore", IsolatedStore)
    monkeypatch.setattr(IsolatedStore, "backfill_semantic_embeddings", lambda self, **kwargs: 0)
    monkeypatch.setattr(audio, "local_model_available", lambda: False)
    monkeypatch.setattr(windows, "list_call_windows", lambda: [CallWindow(1, "Fictional call", "fixture.exe", "Fixture")])
    import conversation_copilot.video as video
    monkeypatch.setattr(video, "LiveVideoSession", FakeVideo)
    monkeypatch.setattr(messagebox, "askyesno", lambda *a, **k: True)
    monkeypatch.setattr(messagebox, "askyesnocancel", lambda *a, **k: False)
    monkeypatch.setattr(messagebox, "showinfo", lambda *a, **k: None)
    monkeypatch.setattr(messagebox, "showerror", lambda *a, **k: None)
    monkeypatch.setattr(simpledialog, "askstring", lambda *a, **k: "Dentist appointment is at 3 PM.")
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
        matches = [w for w in descendants(widget)
                   if isinstance(w, (tk.Button, ttk.Button)) and w.cget("text") == text]
        assert matches, (text, [w.cget("text") for w in descendants(widget)
                                if isinstance(w, (tk.Button, ttk.Button))])
        return matches[0]

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
            unthemed = tk.Toplevel(root)
            RoundedButton(unthemed, text="Unthemed popup button").pack()
            unthemed.update_idletasks()
            unthemed.destroy()
            widgets = descendants(root)
            assert not any(isinstance(widget, tk.Canvas) for widget in widgets)
            assert root._cc_app_icon.width() == root._cc_app_icon.height() == 64
            assert root._cc_corner_logo.width() == root._cc_corner_logo.height() == 48
            assert sum(bool(widget.cget("image")) for widget in widgets if isinstance(widget, tk.Label)) == 1
            assert all(str(widget.cget("background")).casefold() not in {"white", "#ffffff"}
                       for widget in widgets if isinstance(widget, (tk.Listbox, tk.Text)))
            assert button(root, "Start call")
            assert button(root, "Settings")
            assert not any(widget.cget("text") in {"Select", "Clear"}
                           for widget in widgets if isinstance(widget, (tk.Button, ttk.Button)))
            assert not any(widget.cget("text") == "Language"
                           for widget in widgets if isinstance(widget, tk.Label))
            assert any("storage disabled" in str(widget.cget("text"))
                       for widget in widgets if isinstance(widget, tk.Label))
            theme_toggle = next(widget for widget in widgets if isinstance(widget, (tk.Button, ttk.Button))
                                and widget.cget("text") in {"Dark theme", "Light theme"})
            original_page = root.cget("background")
            theme_toggle.invoke()
            assert root.cget("background") != original_page
            theme_toggle.invoke()
            contact_box = next(widget for widget in widgets if isinstance(widget, ttk.Combobox)
                               and any(str(value).startswith("Yaheli") for value in widget.cget("values")))
            contact_box.current(next(i for i, value in enumerate(contact_box.cget("values"))
                                     if str(value).startswith("Yaheli")))
            contact_box.event_generate("<<ComboboxSelected>>")

            assert len([widget for widget in widgets if isinstance(widget, (tk.Button, ttk.Button))
                        and widget.cget("text") == "Memories"]) >= 2
            button(root, "Memories").invoke()
            ask = next(widget for widget in root.winfo_children()
                       if isinstance(widget, real_top) and widget.title() == "Memories")
            assert button(ask, "Ask")
            assert not any(isinstance(widget, tk.Button) and widget.cget("text") in {"Ask locally", "Use cloud help"}
                           for widget in descendants(ask))
            question = next(widget for widget in descendants(ask)
                            if isinstance(widget, tk.Entry) and not isinstance(widget, ttk.Combobox))
            question.insert(0, "What time is the dentist appointment?")
            button(ask, "Ask").invoke()
            root.after(350, lambda: check(lambda: ask_done(ask)))

        def ask_done(ask):
            assert "3 PM" in next(widget for widget in descendants(ask)
                                  if isinstance(widget, tk.Text)).get("1.0", "end")
            frames = {widget.cget("text") for widget in descendants(ask) if isinstance(widget, tk.LabelFrame)}
            assert {"✦  Answer", "Memories behind this answer", "Other saved memories"} <= frames
            assert button(ask, "Edit")
            assert button(ask, "Delete")
            for text in ("Edit aliases", "Merge contact", "Export data", "Delete contact"):
                assert button(ask, text)
            assert not any(isinstance(widget, tk.Button) and widget.cget("text") in {"Open exact source", "Choose this event"}
                           for widget in descendants(ask))
            button(ask, "Edit").invoke()
            assert any("Dentist appointment is at 3 PM." in str(widget.cget("text"))
                       for widget in descendants(ask) if isinstance(widget, tk.Label))
            button(ask, "Delete").invoke()
            assert not any("Dentist appointment is at 3 PM." in str(widget.cget("text"))
                           for widget in descendants(ask) if isinstance(widget, tk.Label))
            button(ask, "← Back to Home").invoke()
            button(root, "Settings").invoke()
            settings = next(widget for widget in root.winfo_children()
                            if isinstance(widget, real_top) and widget.title() == "Settings")
            assert button(settings, "Save override")
            key_entries = [widget for widget in descendants(settings) if isinstance(widget, tk.Entry)]
            assert key_entries and all(widget.cget("show") == "•" for widget in key_entries)
            assert not any(isinstance(widget, (tk.Checkbutton, tk.Radiobutton))
                           for widget in descendants(settings))
            settings_text = " ".join(str(widget.cget("text")) for widget in descendants(settings)
                                     if isinstance(widget, (tk.Label, tk.LabelFrame, tk.Button)))
            assert "Text size" not in settings_text
            assert "Edit aliases" not in settings_text
            button(settings, "← Back to Home").invoke()
            button(root, "◷  History").invoke()
            chooser = next(widget for widget in root.winfo_children()
                           if isinstance(widget, real_top) and widget.title() == "Review one conversation")
            options = next(widget for widget in descendants(chooser) if isinstance(widget, tk.Listbox))
            options.selection_set(next(i for i, text in enumerate(options.get(0, tk.END))
                                       if "UI narrative fixture" in text))
            button(chooser, "Review selected record").invoke()
            review = next(widget for widget in root.winfo_children()
                          if isinstance(widget, real_top) and widget.title() == "Review conversation")
            assert button(review, "Approve selected")
            assert button(review, "Reject all")
            assert button(review, "Approve all memories + summary")
            assert button(review, "Summary versions")
            checkboxes = [widget for widget in descendants(review) if isinstance(widget, tk.Checkbutton)]
            assert checkboxes
            button(review, "Select all").invoke()
            assert all(bool(review.getvar(widget.cget("variable"))) for widget in checkboxes)
            button(review, "Clear").invoke()
            assert not any(bool(review.getvar(widget.cget("variable"))) for widget in checkboxes)
            assert not any(isinstance(widget, tk.Button) and "cloud" in str(widget.cget("text")).casefold()
                           for widget in descendants(review))
            assert "They discussed the book" in next(widget for widget in descendants(review)
                                                      if isinstance(widget, tk.Text)).get("1.0", tk.END)
            review.destroy()
            window_list = next(widget for widget in descendants(root) if isinstance(widget, tk.Listbox)
                               and "Fictional call" in str(widget.get(0, tk.END)))
            window_list.selection_set(0)
            button(root, "Start call").invoke()
            root.update_idletasks()
            live = next(widget for widget in root.winfo_children()[0].winfo_children()
                        if any(isinstance(child, (tk.Button, ttk.Button)) and child.cget("text") == "■  END CALL"
                               for child in descendants(widget)))
            assert live.winfo_manager() == "pack"
            for text in ("■  END CALL", "Refresh all", "Transcript", "Memories", "Face ok · Switch"):
                assert button(root, text)
            group_titles = {widget.cget("text") for widget in descendants(root) if isinstance(widget, tk.LabelFrame)}
            assert {"Possible tone", "Social cue", "Potential responses", "Related memory", "Follow-up"} <= group_titles
            assert all(str(widget.cget("image")) == str(root._cc_corner_logo)
                       for widget in descendants(root)
                       if isinstance(widget, tk.Label) and widget.cget("image"))
            button(root, "Face ok · Switch").invoke()
            assert FakeVideo.instances[-1].switched == 1
            button(root, "Transcript").invoke()
            transcript = next(widget for widget in root.winfo_children()
                              if isinstance(widget, real_top) and widget.title() == "Live transcript")
            assert "No finalized transcript" in next(widget for widget in descendants(transcript)
                                                      if isinstance(widget, tk.Text)).get("1.0", tk.END)
            transcript.destroy()
            button(root, "■  END CALL").invoke()
            root.after(450, lambda: check(finished))

        def finished():
            assert button(root, "Start call")
            live = next(widget for widget in root.winfo_children()[0].winfo_children()
                        if any(isinstance(child, (tk.Button, ttk.Button)) and child.cget("text") == "■  END CALL"
                               for child in descendants(widget)))
            assert not live.winfo_manager()
            completed.append(True)
            root.destroy()

        root.after(50, lambda: check(start))
        root.after(5000, root.destroy)
        return root

    monkeypatch.setattr(tk, "Tk", create_root)
    show_window("F10 isolated UI fixture")
    assert failures == []
    assert completed == [True]
