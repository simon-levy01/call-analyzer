"""Isolated Tk integration; fictional store and no device/model/cloud startup."""
import tkinter as tk
import sqlite3
import threading
from tkinter import filedialog, messagebox, simpledialog, ttk

from conversation_copilot import audio, memory, windows, ask_memory
from conversation_copilot.__main__ import show_window
from conversation_copilot.f06_evaluation import seed_case


def test_ask_ui_uses_independent_scope_and_current_source(tmp_path, monkeypatch):
    in_call = [False]
    path = tmp_path / "ui.sqlite3"
    original_store = memory.MemoryStore
    with original_store(path) as store:
        session, memory_id = seed_case(store, "appointment")
        contact_id = session.contact_id
    class IsolatedStore(original_store):
        def __init__(self, selected_path=None, **kwargs):
            super().__init__(selected_path or path, **kwargs)
    monkeypatch.setattr(memory, "MemoryStore", IsolatedStore)
    backfills = []
    monkeypatch.setattr(IsolatedStore, "backfill_semantic_embeddings", lambda self, **kwargs: backfills.append(True))
    monkeypatch.setattr(audio, "local_model_available", lambda: False)
    monkeypatch.setattr(windows, "list_call_windows", lambda: [])
    def unavailable():
        raise audio.AudioUnavailable("no devices in UI fixture")
    monkeypatch.setattr(audio, "AudioDeviceCatalog", unavailable)
    monkeypatch.setattr(messagebox, "askyesno", lambda *a, **k: True)
    monkeypatch.setattr(messagebox, "showinfo", lambda *a, **k: None)
    busy = [2]
    validate = ask_memory.validate_sources
    def busy_then_validate(*args, **kwargs):
        if threading.current_thread() is threading.main_thread() and busy[0]:
            busy[0] -= 1
            raise sqlite3.OperationalError("database is locked")
        return validate(*args, **kwargs)
    monkeypatch.setattr(ask_memory, "validate_sources", busy_then_validate)
    commands = {}
    real_button = tk.Button.__init__
    def capture_button(self, *args, **kwargs):
        if kwargs.get("command"):
            commands[kwargs.get("text")] = kwargs["command"]
        real_button(self, *args, **kwargs)
    monkeypatch.setattr(tk.Button, "__init__", capture_button)
    cloud_calls = []
    release_cloud = threading.Event()
    def fake_cloud(store, text, sources, **kwargs):
        cloud_calls.append(kwargs)
        release_cloud.wait(2)
        return ask_memory.AskSession(contact_id).answer(store, "What time is the dentist appointment?")
    monkeypatch.setattr(ask_memory, "cloud_answer", fake_cloud)
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
        return next(w for w in descendants(widget) if isinstance(w, tk.Button) and w.cget("text") == text)
    def top(*args, **kwargs):
        widget = real_top(*args, **kwargs)
        widget.withdraw()
        return widget
    monkeypatch.setattr(tk, "Toplevel", top)
    def create_root():
        root = real_tk()
        root.withdraw()
        root.report_callback_exception = lambda *args: (failures.append(args[1]), root.destroy())
        def check(callback):
            try:
                callback()
            except Exception as exc:
                failures.append(exc)
                root.destroy()
        def start():
            root.update_idletasks()
            canvas = next(w for w in descendants(root) if isinstance(w, tk.Canvas))
            assert canvas.bbox("all")[3] > canvas.winfo_height()
            canvas.yview_moveto(1)
            assert canvas.yview()[0] > 0
            canvas.yview_moveto(0)
            button(root, "Ask Memory").invoke()
            dialog = next(w for w in root.winfo_children() if isinstance(w, real_top))
            scope = next(w for w in descendants(dialog) if isinstance(w, ttk.Combobox))
            scope.current(next(i for i, value in enumerate(scope.cget("values")) if str(value).startswith("Yaheli")))
            scope.event_generate("<<ComboboxSelected>>")
            question = next(w for w in descendants(dialog) if isinstance(w, tk.Entry) and not isinstance(w, ttk.Combobox))
            question.insert(0, "What time is the dentist appointment?")
            button(dialog, "Ask locally").invoke()
            def answered():
                content = next(w for w in descendants(dialog) if isinstance(w, tk.Text)).get("1.0", "end")
                assert "3 PM" in content
                if not in_call[0]:
                    question.delete(0, tk.END)
                    question.insert(0, "Where is it?")
                    # Cloud questions no longer require an identical local search first.
                callback = commands["Ask locally"]
                cells = dict(zip(callback.__code__.co_freevars, callback.__closure__))
                if in_call[0]:
                    from conversation_copilot.interpretation import UsageLedger
                    cells["audio_session"].cell_contents = object()
                    cells["usage_ledger"].cell_contents = UsageLedger()
                button(dialog, "Use cloud help").invoke()
                # Stop while the request is in flight; attribution was captured at click time.
                cells["audio_session"].cell_contents = None
                release_cloud.set()
                root.after(250, lambda: check(cloud_finished))
            def cloud_finished():
                callback = commands["Ask locally"]
                cells = dict(zip(callback.__code__.co_freevars, callback.__closure__))
                assert cloud_calls[-1]["live"] is in_call[0]
                assert cloud_calls[-1]["contact_id"] == contact_id
                assert cloud_calls[-1]["ledger"] is cells["usage_ledger" if in_call[0] else "outside_ask_ledger"].cell_contents
                if not in_call[0]:
                    in_call[0] = True
                    release_cloud.clear()
                    answered()
                    return
                scope.current(1)
                scope.event_generate("<<ComboboxSelected>>")
                button(dialog, "Ask locally").invoke()
                def advance():
                    button(dialog, "Next discovery page").invoke()
                    root.after(400, lambda: check(new_question))
                def new_question():
                    assert cells["page"].cell_contents[0] == 12
                    question.delete(0, tk.END)
                    question.insert(0, "Where is the dentist appointment?")
                    button(dialog, "Ask locally").invoke()
                    root.after(400, lambda: check(discovery_answered))
                def discovery_answered():
                    assert cells["page"].cell_contents[0] == 0
                    assert memory_id in {source.id for source in cells["shown"].cell_contents[0].sources}
                    delete_source()
                root.after(400, lambda: check(advance))
            def delete_source():
                with original_store(path, verify=False) as store:
                    store.delete_memory(memory_id)
                def invalidated():
                    content = next(w for w in descendants(dialog) if isinstance(w, tk.Text)).get("1.0", "end")
                    assert "3 PM" not in content
                    before = len(backfills)
                    dialog.tk.call(dialog.protocol("WM_DELETE_WINDOW"))
                    def resumed():
                        assert len(backfills) > before
                        main_scope = next(w for w in descendants(root) if isinstance(w, ttk.Combobox)
                                          and any(str(value).startswith("Yaheli") for value in w.cget("values")))
                        main_scope.current(next(i for i, value in enumerate(main_scope.cget("values")) if str(value).startswith("Yaheli")))
                        button(root, "Select").invoke()
                        from conversation_copilot.models import ConversationTurn, SpeakerRole
                        with original_store(path, verify=False) as store:
                            record = store.create_record(source_kind="call", source_label="UI narrative fixture", timezone_name="UTC", contact_id=contact_id, status="stopped", turns=[ConversationTurn(speaker_name="Yaheli", speaker_role=SpeakerRole.SELECTED_CONTACT, source="fixture", content="We discussed the book and will meet Friday.", display_order=1)])
                            batch = store.create_batch(record, model="fake", reasoning="none")
                            store.store_proposals(batch, [memory.MemoryProposalInput(content="Meet Friday", memory_type="event_date", confidence="high", evidence_turns=[1])])
                            store.create_summary_draft(record, memory.SummaryOutput(statements=[memory.SummaryStatementInput(section="discussed", content="They discussed the book and planned to meet Friday.", kind="fact", confidence="high", evidence_turns=[1])]), expected_generation=1)
                            with store.transaction() as db:
                                db.execute("INSERT INTO review_jobs(record_id,generation,state,created_at) VALUES (?,1,'running','ui-test')", (record,))
                        def open_review():
                            button(root, "Review conversation").invoke()
                            chooser = next(w for w in root.winfo_children() if isinstance(w, real_top) and w.title() == "Review one conversation")
                            options = next(w for w in descendants(chooser) if isinstance(w, tk.Listbox))
                            options.selection_set(next(i for i, text in enumerate(options.get(0, tk.END)) if "UI narrative fixture" in text))
                            button(chooser, "Review selected record").invoke()
                        open_review()
                        open_review()
                        reviews = [w for w in root.winfo_children() if isinstance(w, real_top) and w.title().startswith("Post-call review")]
                        assert len(reviews) == 1
                        review = reviews[0]
                        assert not any(isinstance(w, ttk.Progressbar) for w in descendants(review))
                        assert any(isinstance(w, tk.Label) and 'Generating summary and memories' in w.cget('text') for w in descendants(review))
                        assert "They discussed the book" in next(w for w in descendants(review) if isinstance(w, tk.Text)).get("1.0", tk.END)
                        assert any("pending · Meet Friday" in str(w.get(0, tk.END)) for w in descendants(review) if isinstance(w, tk.Listbox))
                        with original_store(path, verify=False) as store:
                            with store.transaction() as db:
                                db.execute("UPDATE review_jobs SET state='complete' WHERE record_id=?", (record,))
                        def finished_review():
                            assert not any(isinstance(w, tk.Label) and 'Generating summary and memories' in w.cget('text') for w in descendants(review))
                            completed.append(True)
                            root.destroy()
                        root.after(1700, lambda: check(finished_review))
                    root.after(150, lambda: check(resumed))
                root.after(1200, lambda: check(invalidated))
            root.after(1200, lambda: check(answered))
        root.after(50, lambda: check(start))
        root.after(10000, root.destroy)
        return root
    monkeypatch.setattr(tk, "Tk", create_root)
    show_window("F06 isolated UI fixture")
    assert failures == []
    assert completed
