"""Contact-scoped Qt panels using the existing revision-safe memory operations."""
from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from functools import wraps

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QWidget, QVBoxLayout, QPlainTextEdit, QLineEdit, QListWidget, QCheckBox, QFileDialog, QSplitter
from .desktop import Panel, label, button, row, card, clear, scroll, combo, confirm, edit_text
from .memory import MemoryStore
from .interpretation import UsageLedger
from .ask_memory import AskSession, cloud_answer, validate_sources


def store_errors(method):
    """Keep database contention inside the panel, not an unhandled Qt callback."""
    @wraps(method)
    def guarded(self, *args, **kwargs):
        try:
            return method(self, *args, **kwargs)
        except (sqlite3.Error, ValueError, KeyError) as exc:
            self.status.setText(f"Saved content unavailable: {exc}. Close and reopen to retry.")
    return guarded


def text_panel(parent, title, text, valid=None):
    panel = Panel(parent, title)
    box = QPlainTextEdit(text)
    box.setReadOnly(True)
    panel.body.addWidget(box, 1)
    if valid:
        def check():
            try:
                if not valid():
                    box.setPlainText("Source changed or was deleted. Reopen current content.")
                    timer.stop()
            except (sqlite3.Error, KeyError, ValueError):
                box.setPlainText("Source is unavailable. Reopen current content.")
        timer = QTimer(panel)
        timer.timeout.connect(check)
        timer.start(500)
    panel.show()
    return panel


class Memories(Panel):
    def __init__(self, app, contact_id):
        super().__init__(app, "Memories", (920, 680))
        self.app, self.store, self.contact_id = app, app.memory_store, contact_id
        self.contact = self.store.get_contact(contact_id)
        self.state = AskSession(contact_id)
        self.result = None
        self.related = set()
        self.running = False
        self.alive = True
        self.finished.connect(self.cleanup)
        self.body.addWidget(label(f"Ask about {self.contact.label}, or tidy up your saved memories."))
        controls = row()
        for title, callback, role in (("Edit aliases", self.aliases, "tone"), ("Merge contact", self.merge, "social"),
                                      ("Export data", self.export, "replies"), ("Delete contact", self.delete_contact, "danger")):
            action = button(title, callback, role)
            action.setEnabled(not (app.audio_session or app.starting) or title not in {"Merge contact", "Delete contact"})
            controls.addWidget(action)
        self.body.addLayout(controls)
        self.question = QLineEdit()
        self.question.setPlaceholderText("What would you like to remember?")
        self.question.setMaxLength(500)
        self.question.setAccessibleName("Memory question")
        self.question.returnPressed.connect(self.ask)
        self.ask_button = button("Ask", self.ask, "primary")
        self.body.addLayout(row(self.question, self.ask_button))
        self.status = label()
        self.body.addWidget(self.status)
        answer_card, answer_layout = card("Answer", "tone")
        self.answer = label("Ask a question to see an answer and the memories associated with it.")
        self.answer.setTextInteractionFlags(Qt.TextSelectableByMouse)
        answer_layout.addWidget(self.answer)
        self.body.addWidget(answer_card)
        contents = QWidget()
        self.items = QVBoxLayout(contents)
        self.items.setContentsMargins(0, 0, 0, 0)
        self.body.addWidget(scroll(contents), 1)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.validate_answer)
        self.timer.start(750)
        self.reload()

    def cleanup(self, *_):
        self.alive = False
        self.state.close()

    def reset_answer(self):
        self.state.new_question()
        self.result = None
        self.related.clear()
        self.answer.setText("Saved information changed. Ask again for a current answer.")

    def validate_answer(self):
        if self.result:
            try:
                valid = validate_sources(self.store, self.result.sources)
            except sqlite3.Error:
                self.answer.setText("Memory store busy; answer temporarily hidden until its sources can be checked.")
                return
            if not valid:
                self.reset_answer()
                self.reload()
            else:
                self.answer.setText(self.result.answer)

    def ask(self):
        question = self.question.text().strip()
        if self.running or not question:
            return
        self.running = True
        self.ask_button.setEnabled(False)
        self.status.setText("Finding an answer…")
        generation = self.state.generation
        sources = self.result.sources if self.result else ()
        contact_id, event_id = self.state.contact_id, self.state.event_id
        live = self.app.audio_session is not None and not self.app.stopping
        ledger = self.app.usage_ledger if live else self.app.outside_ask_ledger
        model = self.app.selected_live_model()
        path = self.store.path
        def work():
            with MemoryStore(path, verify=False) as store:
                return cloud_answer(store, question, sources, ledger=ledger, live=live,
                    contact_id=contact_id, event_id=event_id, reference=datetime.now().astimezone(),
                    date_mode=None, is_current=lambda: self.alive and self.state.generation == generation,
                    model=model, reasoning="low")
        def done(result, error):
            if not self.alive:
                return
            self.running = False
            self.ask_button.setEnabled(True)
            if generation != self.state.generation:
                return
            if error:
                self.status.setText(f"Answer unavailable ({type(error).__name__}). Saved memories remain available.")
                return
            try:
                if not validate_sources(self.store, result.sources):
                    self.reset_answer()
                    return
                self.result = result
                self.related = {source.id for source in result.sources if source.revision_id}
                for source in result.sources:
                    if source.revision_id is None:
                        self.related.update(r[0] for r in self.store._connection.execute(
                            "SELECT memory_id FROM summary_dependencies WHERE statement_id=? AND memory_id IS NOT NULL", (source.id,)))
                self.answer.setText(result.answer)
                self.status.setText(f"{len(self.related)} associated saved memories")
                self.reload()
            except (sqlite3.Error, ValueError, KeyError) as exc:
                self.status.setText(f"Answer validation unavailable: {exc}")
        self.app.run_job(work, done)

    @store_errors
    def reload(self):
        clear(self.items)
        rows = [dict(r) for r in self.store.list_current_memories(self.contact_id)]
        for associated, title in ((True, "Memories behind this answer"), (False, "Other saved memories")):
            group, layout = card(title)
            selected = [r for r in rows if (r["memory_id"] in self.related) == associated]
            if not selected:
                layout.addWidget(label("No associated memories yet." if associated else "No saved memories here yet."))
            for memory in selected:
                item, content = card(role="replies" if associated else "social")
                content.addWidget(label(memory["content"]))
                content.addLayout(row(label("Saved " + ((memory["approved_at"] or "")[:10] or "date unavailable")), 1,
                    button("Edit", lambda m=memory: self.edit_memory(m)),
                    button("Delete", lambda m=memory: self.delete_memory(m), "danger")))
                layout.addWidget(item)
            self.items.addWidget(group)
        self.items.addStretch()

    def edit_memory(self, memory):
        text = edit_text(self, "Edit memory", memory["content"])
        if text is None:
            return
        try:
            choices = {}
            for statement in self.store.memory_summary_preview(memory["memory_id"]):
                answer = confirm(self, "Linked summary", "Update this linked sentence with your correction?\n\n" + statement["content"], three=True)
                if answer is None:
                    return
                choices[statement["id"]] = "update" if answer else "keep"
            self.store.correct_memory(memory["memory_id"], text.strip(), expected_revision_id=memory["revision_id"], summary_choices=choices)
            self.app.invalidate_memory_context()
            self.app.schedule_semantic_backfill()
            self.reset_answer()
            self.reload()
        except (ValueError, KeyError, sqlite3.Error) as exc:
            self.app.report(exc, self)

    def delete_memory(self, memory):
        if not confirm(self, "Delete memory", "Permanently delete this memory and all its revisions?\n\n" + memory["content"]):
            return
        try:
            self.store.delete_memory(memory["memory_id"])
            self.app.invalidate_memory_context()
            self.reset_answer()
            self.reload()
        except (ValueError, KeyError, sqlite3.Error) as exc:
            self.app.report(exc, self)

    def aliases(self):
        panel = Panel(self, "Edit aliases", (540, 430))
        listing = QListWidget()
        panel.body.addWidget(listing, 1)
        def reload():
            listing.clear()
            for alias in self.store.list_aliases(self.contact_id):
                listing.addItem(alias["spelling"])
                listing.item(listing.count() - 1).setData(Qt.UserRole, alias["id"])
        def add():
            text = edit_text(panel, "Add alias", multiline=False)
            if text:
                try:
                    self.store.add_alias(self.contact_id, text)
                    reload()
                except (ValueError, sqlite3.Error) as exc:
                    self.app.report(exc, panel)
        def remove():
            if listing.currentItem():
                try:
                    self.store.remove_alias(listing.currentItem().data(Qt.UserRole))
                    reload()
                except (ValueError, sqlite3.Error) as exc:
                    self.app.report(exc, panel)
        panel.body.addLayout(row(button("Add", add), button("Remove", remove, "danger")))
        reload()
        panel.show()

    def merge(self):
        panel = Panel(self, "Merge contact", (580, 340))
        pending = [dict(r) for r in self.store.list_current_memories(self.contact_id) if r["needs_review"]]
        if pending:
            panel.resize(680, 560)
            panel.body.addWidget(label("Confirm that these previously merged memories belong to this contact before using them in answers."))
            body = QWidget()
            layout = QVBoxLayout(body)
            choices = []
            for memory in pending:
                check = QCheckBox("Reviewed for this contact")
                layout.addWidget(label(memory["content"]))
                layout.addWidget(check)
                choices.append((memory, check))
            panel.body.addWidget(scroll(body), 1)
            def reviewed():
                expected = {m["memory_id"]: m["revision_id"] for m, check in choices if check.isChecked()}
                if not expected:
                    return
                try:
                    self.store.confirm_reviewed_memories(expected)
                    self.app.invalidate_memory_context()
                    self.reset_answer()
                    self.reload()
                    panel.close()
                except (ValueError, KeyError, sqlite3.Error) as exc:
                    self.app.report(exc, panel)
            panel.body.addWidget(button("Confirm selected memories", reviewed, "primary"))
        selector = combo()
        for contact in self.store.list_contacts():
            if contact.id != self.contact_id:
                selector.addItem(contact.label, contact.id)
        selector.setCurrentIndex(-1)
        panel.body.addWidget(label("Choose the other contact to merge into " + self.contact.label))
        panel.body.addWidget(selector)
        def apply():
            other = selector.currentData()
            if not other:
                return
            try:
                preview = self.store.merge_preview(self.contact_id, other)
                if not confirm(panel, "Confirm merge", "Derived content will require review.\n\n" + "\n".join(f"{k}: {v}" for k, v in preview.items())):
                    return
                self.store.merge_contacts(self.contact_id, other)
                self.app.refresh_contacts()
                self.app.invalidate_memory_context()
                self.reset_answer()
                self.reload()
                panel.close()
                self.merge()
            except (ValueError, KeyError, sqlite3.Error) as exc:
                self.app.report(exc, panel)
        panel.body.addWidget(button("Merge selected contact", apply, "primary"))
        panel.show()

    def export(self):
        if not confirm(self, "Export data", "Exported files remain outside the app and are not removed by later in-app deletion. Continue?"):
            return
        target, _ = QFileDialog.getSaveFileName(self, "Export contact", "", "JSON (*.json)", options=QFileDialog.DontUseNativeDialog)
        if target:
            try:
                payload = self.store.export_json(contact_id=self.contact_id, all_data=False)
                self.store.validate_export(payload)
                Path(target).write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
                self.status.setText("Exported. This file is outside later app deletion control.")
            except (ValueError, OSError, sqlite3.Error) as exc:
                self.app.report(exc, self)

    def delete_contact(self):
        try:
            preview = self.store.contact_deletion_preview(self.contact_id)
            if not confirm(self, "Delete contact", f"Permanently delete {self.contact.label} and local content?\n\n" + "\n".join(f"{k}: {v}" for k, v in preview.items())):
                return
            self.store.delete_contact(self.contact_id)
            self.app.selected_contact_id = self.app.selected_contact_label = None
            self.app.refresh_contacts()
            self.app.invalidate_memory_context()
            self.close()
        except (ValueError, KeyError, sqlite3.Error) as exc:
            self.app.report(exc, self)


class History(Panel):
    def __init__(self, app, contact_id):
        super().__init__(app, "Conversation history", (800, 560))
        self.app, self.store, self.contact_id = app, app.memory_store, contact_id
        self.records = []
        self.status = label()
        self.body.addWidget(self.status)
        self.listing = QListWidget()
        self.body.addWidget(self.listing, 1)
        self.body.addLayout(row(button("Review", self.review, "primary"), button("Reassign", self.reassign),
                                button("Delete source", self.delete, "danger"), button("Unassigned", self.unassigned)))
        self.listing.itemDoubleClicked.connect(lambda *_: self.review())
        self.reload()

    @store_errors
    def reload(self):
        self.records = [dict(r) for r in self.store.list_records(self.contact_id)]
        self.listing.clear()
        for record in self.records:
            self.listing.addItem(f"{record['started_at'] or record['created_at']} · {record['source_label']} · {record['status']} · {record['analysis_state']}")

    def selected(self):
        index = self.listing.currentRow()
        return self.records[index] if 0 <= index < len(self.records) else None

    def review(self):
        record = self.selected()
        if record:
            self.app.open_review(record["id"])

    @store_errors
    def mutate(self, target=None):
        record = self.selected()
        if not record or record["id"] == self.app.current_record_id:
            return
        panel = Panel(self, "Review derived memories", (680, 490))
        panel.body.addWidget(label("Checked memories will be deleted. Uncheck a memory to explicitly keep it."))
        selections = []
        for item in self.store.reassignment_preview(record["id"]):
            check = QCheckBox(item["content"] or "Unavailable memory")
            check.setChecked(True)
            panel.body.addWidget(check)
            selections.append((item["memory_id"], check))
        def apply():
            if not confirm(panel, "Confirm source change", "Apply this irreversible source change and the selected memory deletions?"):
                return
            keep = [identifier for identifier, check in selections if not check.isChecked()]
            try:
                if target:
                    self.store.reassign_record(record["id"], target, keep_memory_ids=keep)
                else:
                    self.store.delete_source(record["id"], keep_memory_ids=keep)
                self.app.invalidate_memory_context()
                self.reload()
                panel.close()
            except (ValueError, KeyError, sqlite3.Error) as exc:
                self.app.report(exc, panel)
        panel.body.addWidget(button("Apply reassignment" if target else "Delete source", apply, "danger"))
        panel.show()

    def delete(self):
        self.mutate()

    def reassign(self):
        panel = Panel(self, "Reassign conversation", (540, 320))
        selector = combo()
        for contact in self.store.list_contacts():
            if contact.id != self.contact_id:
                selector.addItem(contact.label, contact.id)
        selector.setCurrentIndex(-1)
        panel.body.addWidget(selector)
        def choose():
            if selector.currentData():
                target = selector.currentData()
                panel.close()
                self.mutate(target)
        panel.body.addWidget(button("Continue", choose, "primary"))
        panel.show()

    def unassigned(self):
        panel = Panel(self, "Unassigned conversations", (720, 440))
        records = list(self.store.list_unassigned())
        listing = QListWidget()
        for record in records:
            listing.addItem(f"{record['source_label']} · {record['started_at'] or record['created_at']}")
        panel.body.addWidget(listing)
        def assign():
            if listing.currentRow() >= 0:
                try:
                    self.store.assign_record(records[listing.currentRow()]["id"], self.contact_id)
                    self.reload()
                    panel.close()
                except (ValueError, KeyError, sqlite3.Error) as exc:
                    self.app.report(exc, panel)
        panel.body.addWidget(button("Assign to selected contact", assign, "primary"))
        panel.show()


def import_chat(app):
    from .parser import parse_whatsapp_transcript
    panel = Panel(app, "Import text", (820, 660))
    text = QPlainTextEdit()
    text.setPlaceholderText("Paste exported WhatsApp text, or open a text file.")
    panel.body.addWidget(text, 1)
    status = label("Preview the text and map the participants before saving.")
    selector = combo()
    panel.body.addWidget(status)
    panel.body.addLayout(row(label("Which participant is you?"), selector))
    preview = [None]
    source_name = ["Pasted WhatsApp text"]
    contact_id = app.selected_contact_id
    def load():
        source, _ = QFileDialog.getOpenFileName(panel, "Open text", "", "Text (*.txt)", options=QFileDialog.DontUseNativeDialog)
        if source:
            try:
                text.setPlainText(Path(source).read_text(encoding="utf-8-sig"))
                source_name[0] = Path(source).name
            except (OSError, UnicodeError) as exc:
                app.report(exc, panel)
    def inspect():
        try:
            preview[0] = app.memory_store.import_preview(parse_whatsapp_transcript(text.toPlainText(), source="whatsapp_import"),
                timezone_name=str(datetime.now().astimezone().tzinfo))
            selector.clear()
            selector.addItems(preview[0].participants)
            selector.setCurrentIndex(-1)
            status.setText(f"{len(preview[0].turns)} turns · month/day dates · assumed timezone {preview[0].timezone_name}. Select yourself to confirm attribution.")
            text.setReadOnly(True)
        except (ValueError, KeyError) as exc:
            status.setText(str(exc))
    def save():
        if preview[0] is None or selector.currentIndex() < 0:
            status.setText("Preview the text and choose your participant first.")
            return
        try:
            record = app.memory_store.confirm_import(preview[0], user_name=selector.currentText(), contact_id=contact_id, source_label=source_name[0])
            panel.close()
            app.open_review(record)
            app.start_review_job(record, UsageLedger.product())
        except (ValueError, KeyError, sqlite3.Error) as exc:
            app.report(exc, panel)
    panel.body.addLayout(row(button("Open file", load), button("Preview", inspect), button("Import and generate", save, "primary")))
    panel.show()


class Review(Panel):
    def __init__(self, app, record_id):
        super().__init__(app, "Summary and memories", (1080, 740))
        self.app, self.store, self.record_id = app, app.memory_store, record_id
        self.version = None
        self.statements = []
        self.memories = []
        self.checks = {}
        self.status = label()
        self.body.addWidget(self.status)
        self.provenance = label()
        self.body.addWidget(self.provenance)
        panes = QSplitter(Qt.Horizontal)
        self.body.addWidget(panes, 1)
        summary, summary_layout = card("Summary")
        self.narrative = QPlainTextEdit()
        self.narrative.setReadOnly(True)
        self.narrative.setAccessibleName("Saved summary")
        summary_layout.addWidget(self.narrative, 1)
        self.sentences = QListWidget()
        self.sentences.setAccessibleName("Summary sentences")
        self.sentences.setMaximumHeight(96)
        summary_layout.addWidget(label("Select a sentence below to edit it or inspect its source."))
        summary_layout.addWidget(self.sentences, 1)
        summary_layout.addLayout(row(button("Edit sentence", self.edit_sentence), button("Sources", self.sources)))
        summary_layout.addLayout(row(button("Exclude", lambda: self.exclude(True)), button("Restore", lambda: self.exclude(False))))
        summary_layout.addWidget(button("Approve summary", self.approve_summary, "memory"))
        panes.addWidget(summary)
        memories, memory_layout = card("Memories from this conversation")
        body = QWidget()
        self.memory_layout = QVBoxLayout(body)
        memory_layout.addWidget(scroll(body), 1)
        memory_layout.addLayout(row(button("Select all pending", self.select_all), button("Clear selection", self.clear_selection)))
        memory_layout.addLayout(row(button("Approve selected", lambda: self.review_memories(True), "memory"),
                                    button("Reject selected", lambda: self.review_memories(False), "follow_up")))
        memory_layout.addLayout(row(button("Approve all", lambda: self.review_memories(True, all_items=True), "memory"),
                                    button("Reject all pending", lambda: self.review_memories(False, all_items=True), "follow_up")))
        panes.addWidget(memories)
        self.body.addLayout(row(button("Approve all memories and summary", lambda: self.approve_summary(combined=True), "primary"),
                                button("Review later", self.close)))
        self.more = combo(("More actions…", "Generate / continue", "Summary versions", "Transcript", "Delete summary", "Review legacy source exclusions"))
        self.more.activated.connect(self.more_action)
        self.body.addWidget(self.more)
        self.progress_timer = QTimer(self)
        self.progress_timer.timeout.connect(self.show_progress)
        self.progress_timer.start(500)
        self.reload()

    def show_progress(self):
        if self.record_id in self.app.review_running:
            estimate = self.app.review_estimates.get(self.record_id)
            self.status.setText("Generating with Terra low… Your transcript is saved." +
                (f" Estimated generation maximum ${estimate:.4f}." if estimate is not None else ""))

    @store_errors
    def reload(self):
        db = self.store._connection
        version = db.execute("SELECT * FROM summary_versions WHERE record_id=? ORDER BY created_at DESC,rowid DESC LIMIT 1", (self.record_id,)).fetchone()
        self.version = dict(version) if version else None
        self.statements = [dict(s) for s in self.store.summary_statements(version["id"])] if version else []
        self.narrative.setPlainText("\n\n".join(s["content"] for s in self.statements if not s["excluded"]))
        self.sentences.clear()
        for statement in self.statements:
            self.sentences.addItem(("Excluded · " if statement["excluded"] else "") + statement["content"])
        record = db.execute("SELECT * FROM conversation_records WHERE id=?", (self.record_id,)).fetchone()
        if record:
            contact = self.store.get_contact(record["contact_id"]) if record["contact_id"] else None
            model = self.version["model"] if self.version else "Terra low when generated"
            usage = db.execute("SELECT usage_json FROM review_jobs WHERE record_id=?", (self.record_id,)).fetchone()
            dollars = sum(item.get("dollars", 0) for item in json.loads(usage[0])) if usage else 0
            self.provenance.setText(f"{contact.label if contact else 'Unassigned'} · {record['started_at'] or record['created_at']} · {model} · recorded generation usage ${dollars:.4f}")
        self.memories = []
        if record and record["contact_id"]:
            for memory in self.store.list_current_memories(record["contact_id"]):
                if db.execute("SELECT 1 FROM memory_sources WHERE revision_id=? AND record_id=?", (memory["revision_id"], self.record_id)).fetchone():
                    self.memories.append(dict(id=memory["memory_id"], revision=memory["revision_id"], content=memory["content"], state="approved"))
            for proposal in self.store.list_proposals(record["contact_id"]):
                if proposal["state"] != "approved" and db.execute("SELECT 1 FROM proposal_batches WHERE id=? AND record_id=?", (proposal["batch_id"], self.record_id)).fetchone():
                    self.memories.append(dict(id=proposal["id"], content=proposal["content"], state=proposal["state"]))
        selected = {identifier for identifier, check in self.checks.items() if check.isChecked()}
        self.checks = {}
        clear(self.memory_layout)
        for memory in self.memories:
            item, layout = card(role="replies")
            check = QCheckBox(memory["state"].title())
            check.setAccessibleName(memory["state"] + " memory: " + memory["content"])
            check.setEnabled(memory["state"] == "pending")
            check.setChecked(memory["id"] in selected)
            self.checks[memory["id"]] = check
            layout.addWidget(check)
            layout.addWidget(label(memory["content"]))
            controls = row()
            if memory["state"] in {"pending", "approved"}:
                controls.addWidget(button("Edit", lambda m=memory: self.edit_memory(m)))
            if memory["state"] == "pending":
                controls.addWidget(button("Approve", lambda m=memory: self.review_memories(True, one=m), "memory"))
                controls.addWidget(button("Reject", lambda m=memory: self.review_memories(False, one=m), "follow_up"))
            elif memory["state"] == "approved":
                controls.addWidget(button("Delete", lambda m=memory: self.delete_memory(m), "danger"))
            elif memory["state"] == "rejected":
                controls.addWidget(button("Reopen", lambda m=memory: self.reopen(m)))
                controls.addWidget(button("Permanently delete", lambda m=memory: self.delete_memory(m), "danger"))
            layout.addLayout(controls)
            self.memory_layout.addWidget(item)
        self.memory_layout.addStretch()
        state = self.version["state"] if self.version else "No summary yet"
        if self.record_id in self.app.review_running:
            state = "Generating with Terra low… Your transcript is saved."
        elif self.record_id in self.app.review_errors:
            state = "Generation incomplete: " + self.app.review_errors[self.record_id]
        elif self.version and self.version["partial"]:
            state += " · partial coverage; use Continue to process remaining content"
        self.status.setText(state)

    def select_all(self):
        for check in self.checks.values():
            if check.isEnabled():
                check.setChecked(True)

    def clear_selection(self):
        for check in self.checks.values():
            check.setChecked(False)

    def changed(self):
        self.app.invalidate_memory_context()
        self.app.schedule_semantic_backfill()
        self.reload()

    def review_memories(self, approve, *, all_items=False, one=None):
        selected = [one] if one else [m for m in self.memories if m["state"] == "pending" and (all_items or self.checks[m["id"]].isChecked())]
        if not selected or not confirm(self, "Review memories", ("Approve" if approve else "Reject") + " these memories?\n\n" + "\n".join(m["content"] for m in selected)):
            return
        try:
            self.store.review_record_proposals(self.record_id, None if all_items else [m["id"] for m in selected],
                approve=approve, expected_pending={m["id"]: m["content"] for m in selected})
            self.changed()
        except (ValueError, KeyError, sqlite3.Error) as exc:
            self.app.report(exc, self)

    def approve_summary(self, *, combined=False):
        if not self.version:
            return
        pending = [dict(r) for r in self.store.record_pending_proposals(self.record_id)]
        if not combined:
            linked = {r[0] for r in self.store._connection.execute(
                "SELECT DISTINCT d.proposal_id FROM summary_dependencies d JOIN summary_statements s ON s.id=d.statement_id WHERE s.summary_id=? AND s.excluded=0", (self.version["id"],))}
            pending = [p for p in pending if p["id"] in linked]
        text = "Approve this summary and all pending memories?" if combined else "Approve this summary and its linked pending memories?"
        if not confirm(self, "Approve summary", text):
            return
        try:
            operation = self.store.approve_all_memories_and_summary if combined else self.store.approve_summary
            operation(self.version["id"], expected_pending={r["id"]: r["content"] for r in pending},
                      expected_statements={s["id"]: (s["content"], s["excluded"]) for s in self.statements})
            self.changed()
        except (ValueError, KeyError, sqlite3.Error) as exc:
            self.app.report(exc, self)

    def selected_sentence(self):
        index = self.sentences.currentRow()
        return self.statements[index] if 0 <= index < len(self.statements) else None

    def edit_sentence(self):
        sentence = self.selected_sentence()
        if not sentence:
            return
        content = edit_text(self, "Edit summary sentence", sentence["content"])
        if content is None:
            return
        try:
            dependencies = self.store._connection.execute("SELECT * FROM summary_dependencies WHERE statement_id=?", (sentence["id"],)).fetchall()
            links = {}
            for memory in self.memories:
                if memory["state"] not in {"pending", "approved"} or not any(memory["id"] in (d["memory_id"], d["proposal_id"]) for d in dependencies):
                    continue
                choice = confirm(self, "Linked memory", "Also update this linked memory? Pending memories remain pending.\n\n" + memory["content"], three=True)
                if choice is None:
                    return
                if choice:
                    links[memory["id"]] = memory.get("revision", memory["content"])
            self.store.edit_review_sentence(sentence["id"], content, expected_content=sentence["content"], links=links)
            self.changed()
        except (ValueError, KeyError, sqlite3.Error) as exc:
            self.app.report(exc, self)

    def exclude(self, excluded):
        sentence = self.selected_sentence()
        if sentence and confirm(self, "Change summary", "Exclude this sentence?" if excluded else "Explicitly restore this sentence? This does not approve a rejected memory."):
            try:
                self.store.edit_summary_statement(sentence["id"], sentence["content"], excluded=excluded)
                self.changed()
            except (ValueError, KeyError, sqlite3.Error) as exc:
                self.app.report(exc, self)

    def edit_memory(self, memory):
        content = edit_text(self, "Edit memory", memory["content"])
        if content is None:
            return
        try:
            linked = self.store._connection.execute("SELECT DISTINCT s.* FROM summary_statements s JOIN summary_dependencies d ON d.statement_id=s.id WHERE (d.memory_id=? OR d.proposal_id=?) AND s.excluded=0", (memory["id"], memory["id"])).fetchall()
            choices = {}
            for statement in linked:
                choice = confirm(self, "Linked summary", "Also update this summary sentence?\n\n" + statement["content"], three=True)
                if choice is None:
                    return
                choices[statement["id"]] = "update" if choice else "keep"
            if memory["state"] == "approved":
                self.store.correct_memory(memory["id"], content, expected_revision_id=memory["revision"], summary_choices=choices)
            else:
                self.store.edit_pending_review_memory(memory["id"], content, expected_content=memory["content"], summary_ids=[key for key, value in choices.items() if value == "update"])
            self.changed()
        except (ValueError, KeyError, sqlite3.Error) as exc:
            self.app.report(exc, self)

    def delete_memory(self, memory):
        if confirm(self, "Delete memory", "Permanently delete this memory?\n\n" + memory["content"]):
            try:
                if memory["state"] == "approved":
                    self.store.delete_memory(memory["id"])
                else:
                    self.store.delete_rejected_proposal(memory["id"])
                self.changed()
            except (ValueError, KeyError, sqlite3.Error) as exc:
                self.app.report(exc, self)

    def reopen(self, memory):
        try:
            self.store.reopen_proposal(memory["id"])
            self.changed()
        except (ValueError, KeyError, sqlite3.Error) as exc:
            self.app.report(exc, self)

    def sources(self):
        sentence = self.selected_sentence()
        if not sentence:
            return
        sequences = {r[0] for r in self.store._connection.execute("SELECT sequence FROM summary_evidence WHERE statement_id=?", (sentence["id"],))}
        text = "\n\n".join(f"{turn.timestamp} · {turn.speaker_name}: {turn.content}" for turn in self.store.record_turns(self.record_id) if turn.display_order in sequences)
        def valid():
            current = self.store._connection.execute("SELECT * FROM summary_statements WHERE id=?", (sentence["id"],)).fetchone()
            return current is not None and dict(current) == sentence
        text_panel(self, "Exact source", text or "Source unavailable", valid)

    def more_action(self, index):
        self.more.setCurrentIndex(0)
        try:
            if index == 1:
                if confirm(self, "Generate / continue", "Generate with Terra low? Existing versions are retained. This uses your API account."):
                    self.app.start_review_job(self.record_id, UsageLedger.product())
                    self.reload()
            elif index == 2:
                versions = self.store._connection.execute("SELECT * FROM summary_versions WHERE record_id=? ORDER BY created_at DESC,rowid DESC", (self.record_id,)).fetchall()
                content = []
                for version in versions:
                    content.append(f"{version['created_at']} · {version['state']}\n" + "\n".join(s["content"] for s in self.store.summary_statements(version["id"])))
                text_panel(self, "Summary versions", "\n\n".join(content))
            elif index == 3:
                turns = self.store.record_turns(self.record_id)
                text_panel(self, "Transcript", "\n\n".join(f"{t.timestamp} · {t.speaker_name}: {t.content}" for t in turns),
                           lambda: self.store.record_turns(self.record_id) == turns)
            elif index == 4 and confirm(self, "Delete summary", "Delete all summary versions? Transcript and independently approved memories remain."):
                self.store.delete_summary(self.record_id)
                self.changed()
            elif index == 5:
                self.legacy_sources()
        except (ValueError, KeyError, sqlite3.Error) as exc:
            self.app.report(exc, self)

    def legacy_sources(self):
        record = self.store._connection.execute("SELECT * FROM conversation_records WHERE id=?", (self.record_id,)).fetchone()
        if not record:
            return
        turns = self.store.record_turns(self.record_id)
        panel = text_panel(self, "Review legacy sources", "Select only turns containing no previously deleted facts.\n\n" + "\n\n".join(f"Turn {t.display_order} · {t.content}" for t in turns))
        field = QLineEdit()
        field.setPlaceholderText("Reviewed safe turn numbers, separated by commas")
        panel.body.addWidget(field)
        def allow():
            try:
                sequences = {int(value.strip()) for value in field.text().split(",")}
                if not confirm(panel, "Confirm source review", "I reviewed these exact turns and confirm they contain no previously deleted facts."):
                    return
                self.store.review_legacy_summary_turns(self.record_id, sequences, expected_generation=record["generation"])
                panel.close()
                self.reload()
            except (ValueError, sqlite3.Error) as exc:
                self.app.report(exc, panel)
        panel.body.addWidget(button("Allow reviewed turns", allow, "primary"))
