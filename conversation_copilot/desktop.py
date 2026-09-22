"""Qt desktop interface. Capture, retrieval and approval remain in the existing backend."""
from __future__ import annotations

import queue
import sqlite3
import sys
import textwrap
import threading
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

from PySide6.QtCore import Qt, QTimer, QSettings
from PySide6.QtGui import QIcon, QImage, QPixmap
from PySide6.QtWidgets import (
    QApplication, QWidget, QDialog, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QComboBox, QLineEdit, QPlainTextEdit, QListWidget,
    QScrollArea, QFrame, QSlider, QStackedWidget, QMessageBox, QListView,
)

from . import test_log
from .models import conversation_turn_from_audio as _conversation_turn_from_audio
from .models import vocal_observation_from_audio as _vocal_observation_from_audio
from .memory import MemoryStore, memory_retrieval_inputs, memory_semantic_input
from .models import SpeakerRole
from .interpretation import (
    CoordinatorEventKind, InterpretationAuthenticationUnavailable,
    InterpretationBudgetExceeded, InterpretationCoordinator, LUNA_MODEL, TERRA_MODEL,
    OpenAIInterpreter, RetrievedMemoryContext, StableInterpretationCard, UsageLedger,
    VisualAggregator, build_snapshot, prepare_interpretation_request,
    local_openai_api_key, save_local_openai_api_key,
)
from .guidance import GuidanceDisplay, interpret_guidance
from .ask_memory import memory_source, validate_sources


def label(text="", *, heading=False):
    widget = QLabel(text)
    widget.setWordWrap(True)
    widget.setTextFormat(Qt.PlainText)
    if heading:
        widget.setProperty("heading", True)
    return widget


def button(text, callback, role=""):
    widget = QPushButton(text)
    widget.setProperty("role", role)
    widget.setCursor(Qt.PointingHandCursor)
    widget.clicked.connect(lambda _checked=False: callback())
    widget.setMinimumHeight(38)
    return widget


def row(*widgets):
    layout = QHBoxLayout()
    layout.setSpacing(8)
    for widget in widgets:
        if isinstance(widget, QWidget):
            layout.addWidget(widget)
        elif isinstance(widget, int):
            layout.addStretch(widget)
        else:
            layout.addLayout(widget)
    return layout


def clear(layout):
    while layout.count():
        item = layout.takeAt(0)
        if item.widget():
            item.widget().hide()
            item.widget().deleteLater()
        elif item.layout():
            clear(item.layout())


def card(title="", role=""):
    widget = QFrame()
    widget.setProperty("card", True)
    widget.setProperty("role", role)
    layout = QVBoxLayout(widget)
    layout.setContentsMargins(16, 14, 16, 14)
    layout.setSpacing(10)
    if title:
        layout.addWidget(label(title, heading=True))
    return widget, layout


def scroll(widget):
    area = QScrollArea()
    area.setWidgetResizable(True)
    area.setFrameShape(QFrame.NoFrame)
    area.setWidget(widget)
    return area


def combo(items=()):
    widget = QComboBox()
    widget.addItems(list(items))
    widget.setMinimumHeight(40)
    widget.setSizeAdjustPolicy(QComboBox.AdjustToMinimumContentsLengthWithIcon)
    widget.setMinimumContentsLength(12)
    # A Qt view, not the platform's unstyleable native popup.
    widget.setView(QListView())
    return widget


def confirm(parent, title, text, *, three=False):
    box = QMessageBox(parent)
    box.setWindowTitle(title)
    box.setText(text)
    box.setTextFormat(Qt.PlainText)
    box.setIcon(QMessageBox.Question)
    box.setStandardButtons(QMessageBox.Yes | QMessageBox.No | (QMessageBox.Cancel if three else QMessageBox.NoButton))
    box.setDefaultButton(QMessageBox.Cancel if three else QMessageBox.No)
    result = box.exec()
    return None if result == QMessageBox.Cancel else result == QMessageBox.Yes


class Panel(QDialog):
    def __init__(self, parent, title, size=(760, 570), *, modal=True):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setWindowModality(Qt.ApplicationModal if modal else Qt.NonModal)
        if not modal:
            self.setWindowFlag(Qt.WindowStaysOnTopHint)
        self.resize(*size)
        self.setMinimumSize(360, 260)
        self.body = QVBoxLayout(self)
        self.body.setContentsMargins(20, 18, 20, 18)
        self.body.setSpacing(12)
        heading = label(title, heading=True)
        heading.setWordWrap(False)
        self.body.addLayout(row(heading, 1, button("Close", self.close)))


def edit_text(parent, title, initial="", *, multiline=True, prompt=""):
    dialog = Panel(parent, title, (640, 420) if multiline else (500, 260))
    dialog.setAttribute(Qt.WA_DeleteOnClose, False)
    if prompt:
        dialog.body.addWidget(label(prompt))
    field = QPlainTextEdit(initial) if multiline else QLineEdit(initial)
    field.setAccessibleName(title)
    dialog.body.addWidget(field, 1)
    dialog.body.addLayout(row(1, button("Cancel", dialog.reject), button("Save", dialog.accept, "primary")))
    field.setFocus()
    accepted = dialog.exec() == QDialog.Accepted
    value = field.toPlainText() if multiline else field.text()
    dialog.deleteLater()
    return value if accepted else None


class Desktop(QWidget):
    def __init__(self, store=None, *, discover=True):
        super().__init__()
        self.setWindowTitle("Conversation Copilot")
        self.resize(1100, 740)
        self.setMinimumSize(480, 420)
        self.memory_store = store or MemoryStore()
        self.settings = QSettings("ConversationCopilot", "Desktop")
        self.key_configured = bool(local_openai_api_key())
        self.last_key_check = time.monotonic()
        self.dark = self.settings.value("theme", "dark") == "dark"
        self.windows = []
        self.audio_catalog = None
        self.audio_runtime_error = "Checking local runtime…"
        self.session = self.audio_session = None
        self.preview_session = None
        self.preview_loading = False
        self.capture_failed = False
        self.call_started = 0.0
        self.starting = self.stopping = self.closing = False
        self.closed = False
        self.turns = []
        self.vocal_observations = []
        self.visual_aggregator = VisualAggregator()
        self.capture_clock_origin = datetime.now(timezone.utc) - timedelta(seconds=time.perf_counter())
        self.usage_ledger = None
        self.outside_ask_ledger = UsageLedger.product()
        self.stable_interpretation = StableInterpretationCard()
        self.guidance_display = GuidanceDisplay()
        self.interpretation_coordinator = None
        self.interpretation_generation = self.guidance_topic_start = self.next_interpretation_snapshot_id = 0
        self.latest_interpretation_snapshot = None
        self.interpretation_updated_at = ""
        self.memory_snapshot_results = queue.SimpleQueue()
        self.local_done = queue.SimpleQueue()
        self.local_pending = {"ask": None, "live": None}
        self.local_active = False
        self.review_running = set()
        self.review_errors = {}
        self.review_estimates = {}
        self.cloud_error = ""
        self.persistence_error = ""
        self.semantic_backfill_requested = False
        self.backfill_running = False
        self.selected_contact_id = self.selected_contact_label = self.current_record_id = None
        self.call_speaker_fallback = "Contact"
        self.jobs = queue.SimpleQueue()
        self.pending_jobs = 0
        self.discovery_running = False
        self.popups = []
        self.review_dialogs = {}
        self.last_guidance = None
        self.last_source_check = 0
        self.root_layout = QVBoxLayout(self)
        self.root_layout.setContentsMargins(0, 0, 0, 0)
        self.pages = QStackedWidget()
        self.root_layout.addWidget(self.pages)
        self.build_home()
        self.build_live()
        self.set_logo()
        self.apply_theme()
        self.refresh_contacts()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.poll)
        self.timer.start(100)
        if discover:
            QTimer.singleShot(0, self.refresh_devices)
            QTimer.singleShot(1500, self.schedule_semantic_backfill)

    def set_logo(self):
        image = QImage(str(Path(__file__).with_name("assets") / "conversation-copilot-icon.png"))
        # The supplied original has generous transparent margins.
        if not image.isNull():
            image = image.copy(280, 290, 690, 700)
            pixmap = QPixmap.fromImage(image)
            self.setWindowIcon(QIcon(pixmap))
            self.logo.setPixmap(pixmap.scaled(48, 48, Qt.KeepAspectRatio, Qt.SmoothTransformation))

    def build_home(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(18, 14, 18, 14)
        layout.setSpacing(10)
        self.logo = QLabel()
        self.theme_button = button("Light theme", self.toggle_theme)
        layout.addLayout(row(self.logo, label("Conversation Copilot", heading=True), 1,
                             self.theme_button, button("Settings", self.open_settings)))
        layout.addWidget(label("Say hi, and I'll listen along."))
        contact_card, content = card("Who are you talking to?")
        self.contact_box = combo()
        self.contact_box.setAccessibleName("Selected contact")
        self.contact_box.setPlaceholderText("Choose a contact")
        self.contact_box.currentIndexChanged.connect(self.select_contact)
        content.addWidget(self.contact_box)
        actions = row()
        for text, callback, role in (
            ("Create", self.create_contact, "tone"), ("Edit", self.open_memories, "social"),
            ("Memories", self.open_memories, "memory"), ("History", self.open_history, "replies"),
            ("Import text", self.import_chat, "follow_up"),
        ):
            actions.addWidget(button(text, callback, role), 1)
        content.addLayout(actions)
        self.memory_status_label = label("Choose a contact to get ready.")
        self.memory_status_label.hide()
        layout.addWidget(contact_card)
        setup = QHBoxLayout()
        sound, sound_layout = card("Sound check")
        self.microphone_box = combo()
        self.playback_box = combo()
        for caption, selector in (("Microphone", self.microphone_box), ("Call audio", self.playback_box)):
            selector.setAccessibleName(caption)
            sound_layout.addLayout(row(label(caption), selector))
            selector.currentIndexChanged.connect(self.update_readiness)
        sound_layout.addWidget(label("Captures all sound on this output device. Close unrelated audio apps."))
        self.sensitivity = QSlider(Qt.Horizontal)
        self.sensitivity.setRange(50, 2000)
        self.sensitivity.setSingleStep(50)
        from .audio import DEFAULT_MICROPHONE_THRESHOLD
        self.sensitivity.setValue(int(DEFAULT_MICROPHONE_THRESHOLD))
        sound_layout.addWidget(label("Microphone threshold · lower is more sensitive"))
        sound_layout.addWidget(self.sensitivity)
        self.audio_status_label = label("Checking devices…")
        sound_layout.addWidget(self.audio_status_label)
        watch, watch_layout = card("Your call window")
        self.window_box = combo()
        self.window_box.setAccessibleName("Call window")
        self.window_box.setPlaceholderText("Choose an active call window")
        self.window_box.currentIndexChanged.connect(self.window_changed)
        self.refresh_button = button("Refresh devices and windows", self.refresh_devices, "replies")
        self.refresh_button.setText("Refresh")
        self.refresh_button.setAccessibleName("Refresh devices and windows")
        watch_layout.addLayout(row(self.window_box, self.refresh_button))
        self.face_preview = label("Choose a window, then preview the selected face.")
        self.face_preview.setMinimumHeight(90)
        self.face_preview.setAlignment(Qt.AlignCenter)
        self.preview_button = button("Preview face", self.preview_face, "social")
        self.home_switch_button = button("Switch face", self.switch_preview, "social")
        preview_actions = QVBoxLayout()
        preview_actions.addWidget(self.preview_button)
        preview_actions.addWidget(self.home_switch_button)
        watch_layout.addLayout(row(self.face_preview, preview_actions))
        self.model_box = combo(("Luna low", "Terra low"))
        self.model_box.setAccessibleName("Live and Ask model")
        self.model_box.setFixedWidth(150)
        watch_layout.addLayout(row(label("Live and Ask"), self.model_box, 1))
        watch_layout.addWidget(label("Terra has 10× Luna's token rates. Review generation uses Terra low."))
        setup.addWidget(sound, 1)
        setup.addWidget(watch, 1)
        layout.addLayout(setup, 1)
        ready, ready_layout = card()
        self.ready_text = label()
        self.start_button = button("Start call  →", self.start_call, "primary")
        self.start_button.setMinimumSize(220, 64)
        self.start_button.setProperty("large", True)
        ready_line = row(self.ready_text, self.start_button)
        ready_line.setStretch(0, 1)
        ready_layout.addLayout(ready_line)
        self.status_label = label()
        self.recovery_button = button("Open unsaved transcript", self.open_transcript, "danger")
        self.recovery_button.hide()
        self.home = QWidget()
        home_layout = QVBoxLayout(self.home)
        home_layout.setContentsMargins(0, 0, 0, 0)
        home_layout.addWidget(scroll(page), 1)
        ready_layout.addWidget(self.status_label)
        ready_layout.addWidget(self.recovery_button)
        home_layout.addWidget(ready)
        self.pages.addWidget(self.home)

    def build_live(self):
        self.live = QWidget()
        layout = QVBoxLayout(self.live)
        layout.setContentsMargins(14, 14, 14, 14)
        self.live_contact_label = label("Live call", heading=True)
        self.stop_button = button("■  END CALL", self.stop, "danger")
        self.stop_button.setMinimumHeight(48)
        layout.addLayout(row(self.live_contact_label, 1, self.stop_button))
        self.live_meta_label = label()
        layout.addWidget(self.live_meta_label)
        self.live_audio_label, self.live_face_label = label(), label()
        layout.addLayout(row(self.live_audio_label, self.live_face_label))
        self.guidance_status = label("Listening…")
        self.suggest_button = button("Refresh all", self.suggest_now, "primary")
        layout.addLayout(row(self.guidance_status, 1, self.suggest_button))
        self.call_notice = label("Suggestions are possibilities, not facts about feelings or intent.")
        layout.addWidget(self.call_notice)
        body = QWidget()
        self.guidance_grid = QGridLayout(body)
        self.guidance_grid.setContentsMargins(0, 0, 0, 0)
        self.guidance_rows = {}
        for index, (category, title, role) in enumerate((
            ("tones", "Possible tones", "tone"), ("social_cues", "Social cues", "social"),
            ("replies", "Potential responses", "replies"), ("remember", "Related memories", "memory"),
            ("follow_up", "Follow-up questions", "follow_up"),
        )):
            group, content = card(title, role)
            content.setAlignment(Qt.AlignTop)
            self.guidance_rows[category] = content
            self.guidance_grid.addWidget(group, index // 2, index % 2, 1, 2 if index == 4 else 1)
        layout.addWidget(scroll(body), 1)
        layout.addWidget(self.memory_status_label)
        self.memory_status_label.show()
        self.switch_button = button("Switch face", self.switch, "social")
        layout.addLayout(row(button("Transcript", self.open_transcript),
                             button("Memories", self.open_memories, "memory"), self.switch_button))
        self.pages.addWidget(self.live)

    def apply_theme(self):
        from .qt_theme import apply_theme
        apply_theme(QApplication.instance(), self.dark)
        self.theme_button.setText("Light theme" if self.dark else "Dark theme")
        if sys.platform == "win32":
            import ctypes
            dark = ctypes.c_int(int(self.dark))
            ctypes.windll.dwmapi.DwmSetWindowAttribute(int(self.winId()), 20, ctypes.byref(dark), 4)

    def toggle_theme(self):
        self.dark = not self.dark
        self.settings.setValue("theme", "dark" if self.dark else "light")
        self.apply_theme()

    def run_job(self, work, completed):
        self.pending_jobs += 1
        def run():
            try:
                result, error = work(), None
            except Exception as exc:
                result, error = None, exc
            self.jobs.put((completed, result, error))
        threading.Thread(target=run, daemon=True, name="desktop-work").start()

    def report(self, error, parent=None):
        QMessageBox.warning(parent or self, "Action unavailable", str(error))

    def refresh_contacts(self):
        self.contact_box.blockSignals(True)
        self.contact_box.clear()
        for contact in self.memory_store.list_contacts():
            self.contact_box.addItem(contact.label, contact.id)
        self.contact_box.setCurrentIndex(self.contact_box.findData(self.selected_contact_id))
        self.contact_box.blockSignals(False)

    def select_contact(self, index):
        if self.audio_session or self.starting:
            return
        self.selected_contact_id = self.contact_box.itemData(index)
        self.selected_contact_label = self.contact_box.itemText(index) if index >= 0 else None
        self.invalidate_memory_context()
        self.memory_status_label.setText(self.selected_contact_label or "Choose a contact.")
        self.update_readiness()

    def create_contact(self):
        if self.starting or self.audio_session or self.stopping:
            return
        panel = Panel(self, "Create contact", (540, 340))
        name, detail = QLineEdit(), QLineEdit()
        name.setPlaceholderText("Display name")
        name.setAccessibleName("Display name")
        detail.setPlaceholderText("Optional last name, work, friend…")
        detail.setAccessibleName("Contact disambiguator")
        panel.body.addWidget(name)
        panel.body.addWidget(detail)
        def save():
            try:
                contact = self.memory_store.create_contact(name.text().strip(), detail.text().strip() or None,
                    timezone_name=str(datetime.now().astimezone().tzinfo))
                self.selected_contact_id, self.selected_contact_label = contact.id, contact.label
                self.refresh_contacts()
                self.update_readiness()
                panel.close()
            except (ValueError, sqlite3.Error) as exc:
                self.report(exc, panel)
        panel.body.addWidget(button("Create", save, "primary"))
        panel.show()

    def selected_live_model(self):
        return TERRA_MODEL if self.model_box.currentText().startswith("Terra") else LUNA_MODEL

    def readiness(self):
        missing = []
        if not self.selected_contact_id:
            missing.append("contact")
        if self.window_box.currentIndex() < 0:
            missing.append("call window")
        if self.audio_catalog is None or self.microphone_box.currentIndex() < 0 or self.playback_box.currentIndex() < 0:
            missing.append("microphone and call audio")
        if self.audio_runtime_error:
            missing.append("local audio runtime")
        if self.capture_failed:
            missing.append("restart after capture shutdown failure")
        if not self.key_configured:
            missing.append("API key in Settings")
        return missing

    def update_readiness(self, *_):
        missing = self.readiness()
        active = self.starting or self.stopping or self.audio_session is not None
        self.start_button.setEnabled(not missing and not active and not self.discovery_running and not self.preview_loading)
        self.ready_text.setText("Call in progress" if active else "Checking devices…" if self.discovery_running else "Preparing face preview…" if self.preview_loading else
            ("Choose or fix: " + ", ".join(missing) if missing else "✓  Everything is ready for your call"))

    def refresh_devices(self):
        if self.discovery_running or self.audio_session or self.starting or self.stopping:
            return
        self.discovery_running = True
        self.refresh_button.setEnabled(False)
        old_catalog, self.audio_catalog = self.audio_catalog, None
        self.microphone_box.clear()
        self.playback_box.clear()
        self.window_box.clear()
        self.audio_status_label.setText("Looking for devices…")
        def discover():
            if old_catalog:
                old_catalog.close()
            if sys.platform != "win32":
                return [], None, "Call capture on this platform is not yet implemented. Saved memories and history are available."
            from .audio import AudioDeviceCatalog, local_model_available, prepare_transcription_runtime
            from .windows import list_call_windows
            windows = list_call_windows()
            catalog = AudioDeviceCatalog()
            try:
                if not local_model_available():
                    raise RuntimeError("Install the local transcription model before starting a call.")
                prepare_transcription_runtime()
                error = ""
            except Exception as exc:
                error = str(exc)
            return windows, catalog, error
        def done(result, error):
            self.discovery_running = False
            self.refresh_button.setEnabled(True)
            if error:
                self.audio_runtime_error = str(error)
            else:
                self.windows, self.audio_catalog, self.audio_runtime_error = result
                from .audio import device_labels
                self.window_box.addItems([item.display_name for item in self.windows])
                self.window_box.setCurrentIndex(-1)
                if self.audio_catalog:
                    self.microphone_box.addItems(device_labels(self.audio_catalog.microphones))
                    self.playback_box.addItems(device_labels([item.render for item in self.audio_catalog.playbacks]))
                    self.microphone_box.setCurrentIndex(-1)
                    self.playback_box.setCurrentIndex(-1)
            self.audio_status_label.setText(self.audio_runtime_error or "Choose both devices explicitly.")
            self.update_readiness()
        self.run_job(discover, done)

    def window_changed(self, *_):
        if self.preview_session:
            current, self.preview_session = self.preview_session, None
            self.run_job(current.stop, lambda *_: None)
        self.face_preview.setText("Preview the selected face before the call.")
        self.update_readiness()

    def preview_face(self):
        if self.preview_session or self.preview_loading or self.window_box.currentIndex() < 0 or self.starting:
            return
        window = self.windows[self.window_box.currentIndex()]
        self.preview_button.setEnabled(False)
        self.preview_loading = True
        def work():
            from .video import LiveVideoSession
            session = LiveVideoSession(window)
            try:
                session.start()
            except Exception:
                session.stop()
                raise
            return session
        def done(result, error):
            self.preview_loading = False
            self.preview_button.setEnabled(True)
            if error:
                self.face_preview.setText(f"Preview unavailable: {error}")
            elif self.window_box.currentIndex() < 0 or self.windows[self.window_box.currentIndex()] != window or self.starting or self.audio_session or self.closing:
                self.run_job(result.stop, lambda *_: None)
            else:
                self.preview_session = result
        self.run_job(work, done)

    def switch_preview(self):
        current = self.preview_session
        if current:
            if current.snapshot().status == "Face lost":
                current.continue_tracking()
            else:
                current.switch_face()

    def start_call(self):
        if self.readiness() or self.starting or self.audio_session or self.stopping or self.preview_loading or self.discovery_running:
            return
        if self.persistence_error and not confirm(self, "Unsaved transcript", "Some previous transcript text could not be saved. Starting another call clears the temporary transcript. Have you copied it and want to continue?"):
            return
        self.starting = True
        self.home.setEnabled(False)
        self.update_readiness()
        window = self.windows[self.window_box.currentIndex()]
        catalog = self.audio_catalog
        microphone = catalog.microphones[self.microphone_box.currentIndex()]
        playback = catalog.playbacks[self.playback_box.currentIndex()]
        threshold = self.sensitivity.value()
        preview, self.preview_session = self.preview_session, None
        cleanup_failed = []
        self.status_label.setText("Starting local capture…")
        self.contact_box.setEnabled(False)
        self.model_box.setEnabled(False)
        def work():
            from .audio import AudioCallSession, production_transcription_language
            from .video import LiveVideoSession
            from .windows import whatsapp_call_active
            video, audio = preview, None
            try:
                if video is None:
                    video = LiveVideoSession(window)
                    video.start()
                audio = AudioCallSession(catalog, microphone, playback, production_transcription_language("English"),
                    contact_name=self.selected_contact_label, microphone_threshold=threshold,
                    source_guard=(lambda: not whatsapp_call_active()) if window.kind == "Google Meet" else None,
                    retain_catalog_on_clean_stop=True)
                audio.start()
                return video, audio
            except Exception:
                for partial in (audio, video):
                    if partial:
                        try:
                            partial.stop()
                        except Exception:
                            cleanup_failed.append(True)
                raise
        def done(result, error):
            self.starting = False
            self.home.setEnabled(True)
            if error:
                self.capture_failed = self.capture_failed or bool(cleanup_failed)
                self.status_label.setText(f"Call could not start: {error}")
                self.face_preview.setText("Preview stopped. Select Preview face to try again.")
                self.contact_box.setEnabled(True)
                self.model_box.setEnabled(True)
                self.refresh_devices()
                return
            self.session, self.audio_session = result
            self.call_started = time.monotonic()
            self.turns.clear()
            self.persistence_error = self.cloud_error = ""
            self.vocal_observations.clear()
            self.visual_aggregator.reset()
            self.call_speaker_fallback = window.display_name
            try:
                self.current_record_id = self.memory_store.create_record(source_kind="call", source_label=window.kind,
                    timezone_name=str(datetime.now().astimezone().tzinfo), contact_id=self.selected_contact_id, status="active")
            except Exception as exc:
                self.persistence_error = f"Cannot safely retain transcript ({type(exc).__name__}). Copy the temporary transcript."
                self.stop()
                return
            self.begin_interpretation_session()
            self.live_contact_label.setText(self.selected_contact_label)
            self.pages.setCurrentWidget(self.live)
            self.resize(660, 780)
            self.stop_button.setEnabled(True)
            self.switch_button.setEnabled(True)
            if self.closing:
                self.stop()
        self.run_job(work, done)

    def stop(self):
        if self.stopping or self.starting or (self.audio_session is None and self.session is None):
            return
        self.stopping = True
        if self.usage_ledger:
            self.usage_ledger.stopped = True
        self.interpretation_generation += 1
        self.local_pending["live"] = None
        self.latest_interpretation_snapshot = None
        if self.interpretation_coordinator:
            self.interpretation_coordinator.reset(self.interpretation_generation)
        self.stop_button.setEnabled(False)
        self.guidance_status.setText("Ending call and saving final text…")
        audio, video = self.audio_session, self.session
        if audio:
            audio.request_stop()
        def work():
            errors = []
            for session in (video, audio):
                if session:
                    try:
                        session.stop()
                    except Exception as exc:
                        errors.append(str(exc))
            return errors
        def done(errors, error):
            if audio:
                self.drain_audio_results(audio)
            self.audio_session = self.session = None
            self.stopping = False
            self.contact_box.setEnabled(True)
            self.model_box.setEnabled(True)
            record, self.current_record_id = self.current_record_id, None
            finalized = True
            if record:
                try:
                    self.memory_store.stop_record(record)
                except (sqlite3.Error, ValueError, KeyError) as exc:
                    finalized = False
                    self.persistence_error = f"Call could not be finalized ({type(exc).__name__}). Keep the app open and copy the temporary transcript."
            self.pages.setCurrentWidget(self.home)
            self.resize(1100, 740)
            self.status_label.setText(self.persistence_error or "; ".join(errors or []) or "Call saved.")
            if errors or error:
                self.capture_failed = True
                self.audio_runtime_error = "Capture shutdown failed; restart before another call."
            if record and finalized and not self.closing and not self.persistence_error:
                self.open_review(record)
                self.start_review_job(record, self.usage_ledger or UsageLedger.product())
            if self.closing:
                self.close()
        self.run_job(work, done)

    def render_interpretation(self, *, replaced=False, note=""):
        spend = self.usage_ledger.total_dollars if self.usage_ledger else 0
        self.live_meta_label.setText(f"{self.model_box.currentText()} · estimated ${spend:.4f}")
        if replaced:
            self.render_guidance()
        if note:
            self.guidance_status.setText(note)

    def set_interpretation_unavailable(self, message, now):
        self.stable_interpretation.show_unavailable(message, now)
        self.cloud_error = message
        self.call_notice.setText(self.persistence_error or self.cloud_error)

    def schedule_semantic_backfill(self):
        self.semantic_backfill_requested = True
        if self.backfill_running or self.audio_session or self.starting or self.closing:
            return
        self.semantic_backfill_requested = False
        self.backfill_running = True
        path = self.memory_store.path
        def work():
            with MemoryStore(path, verify=False) as store:
                return store.backfill_semantic_embeddings(can_run=lambda: not self.audio_session and not self.starting and not self.closing)
        def done(_result, _error):
            self.backfill_running = False
        self.run_job(work, done)

    def render_guidance(self):
        update = self.guidance_display.filter_update(self.stable_interpretation.update) if self.stable_interpretation.update else None
        displayed = {category: (list(getattr(update, category)) if update else []) if category in {"tones", "social_cues"}
                     else self.guidance_display.visible(category) for category in self.guidance_rows}
        signature = repr(displayed)
        if signature == self.last_guidance:
            return
        self.last_guidance = signature
        for category, layout in self.guidance_rows.items():
            while layout.count() > 1:
                item = layout.takeAt(1)
                if item.widget():
                    item.widget().hide()
                    item.widget().deleteLater()
            if not displayed[category]:
                layout.addWidget(label("Nothing useful to show yet."))
            for index, wrapped in enumerate(displayed[category]):
                candidate = wrapped if category in {"tones", "social_cues"} else wrapped.candidate
                content = candidate.hypothesis if hasattr(candidate, "hypothesis") else candidate.text
                item = QWidget()
                item.setProperty("plain", True)
                item_layout = QHBoxLayout(item)
                item_layout.setContentsMargins(0, 3, 0, 3)
                item_layout.addWidget(label(content), 1)
                def dismiss(c=category, i=index, u=update):
                    self.guidance_display.dismiss(c, i, update=u)
                    self.render_guidance()
                for caption, accessible, callback in (("↗", "Pop out", lambda c=category, x=candidate, t=content: self.pop_out(c, x, t)), ("×", "Dismiss", dismiss)):
                    action = button(caption, callback)
                    action.setAccessibleName(accessible)
                    action.setToolTip(accessible)
                    action.setMinimumHeight(28)
                    action.setFixedWidth(34)
                    item_layout.addWidget(action)
                layout.addWidget(item)

    def pop_out(self, category, candidate, content):
        panel = Panel(self, category.replace("_", " ").title(), (440, 260), modal=False)
        wording = label(content, heading=True)
        panel.body.addWidget(wording, 1)
        panel.body.addWidget(label(f"Captured suggestion · {self.selected_contact_label} · {datetime.now().astimezone():%H:%M:%S}"))
        evidence = getattr(candidate, "evidence", candidate)
        revisions = set(getattr(evidence, "memory_ids", ())) | set(getattr(evidence, "preference_ids", ()))
        captured_contact = self.selected_contact_id
        record_id = self.current_record_id
        source_record = self.memory_store._connection.execute("SELECT generation FROM conversation_records WHERE id=?", (record_id,)).fetchone() if record_id else None
        def current_sources():
            self.memory_store.get_contact(captured_contact)
            current = {r["revision_id"] for r in self.memory_store.list_current_memories(captured_contact)}
            if not revisions.issubset(current):
                return False
            if record_id:
                record = self.memory_store._connection.execute("SELECT contact_id,generation FROM conversation_records WHERE id=?", (record_id,)).fetchone()
                if not record or record[0] != captured_contact or (source_record and record[1] != source_record[0]):
                    return False
            return True
        captured_turns = [turn.model_copy(deep=True) for turn in self.turns if turn.display_order in getattr(evidence, "turn_ids", ())]
        def show_sources():
            from .desktop_data import text_panel
            try:
                if not current_sources():
                    raise ValueError("Source changed or was deleted.")
                lines = [f"{turn.timestamp} · {turn.speaker_name}: {turn.content}" for turn in captured_turns]
                for memory in self.memory_store.list_current_memories(captured_contact):
                    if memory["revision_id"] in revisions:
                        lines.append(memory["content"])
                text_panel(panel, "Exact source", "\n\n".join(lines) or "No retained source available.", current_sources)
            except (ValueError, KeyError, sqlite3.Error) as exc:
                self.report(exc, panel)
        panel.body.addWidget(button("Sources", show_sources))
        def validate():
            try:
                if not current_sources():
                    raise ValueError("source changed")
            except (ValueError, KeyError):
                wording.setText("This suggestion's source changed or was deleted.")
                timer.stop()
            except sqlite3.Error:
                wording.setText("Source validation unavailable. Reopen the suggestion.")
            else:
                wording.setText(content)
        timer = QTimer(panel)
        timer.timeout.connect(validate)
        timer.start(500)
        panel.show()

    def open_transcript(self):
        panel = Panel(self, "Live transcript", (640, 540))
        box = QPlainTextEdit()
        box.setReadOnly(True)
        panel.body.addWidget(box, 1)
        panel.body.addWidget(button("Return to latest", lambda: box.verticalScrollBar().setValue(box.verticalScrollBar().maximum())))
        shown = [0]
        def refresh():
            if shown[0] > len(self.turns):
                box.clear()
                shown[0] = 0
            if shown[0] == len(self.turns):
                return
            bar = box.verticalScrollBar()
            follow = bar.value() >= bar.maximum() - 2
            position = bar.value()
            box.appendPlainText("\n".join(f"{t.timestamp:%H:%M:%S} · {t.speaker_name}: {t.content}" for t in self.turns[shown[0]:]))
            shown[0] = len(self.turns)
            bar.setValue(bar.maximum() if follow else position)
        timer = QTimer(panel)
        timer.timeout.connect(refresh)
        timer.start(200)
        refresh()
        panel.show()

    def open_settings(self):
        panel = Panel(self, "Settings", (600, 350))
        panel.body.addWidget(label("API key", heading=True))
        panel.body.addWidget(label("•••••••••••• · Existing key in use" if local_openai_api_key() else "No API key configured"))
        panel.body.addWidget(label("Leave this empty to keep your existing key. A replacement is saved privately on this computer."))
        field = QLineEdit()
        field.setEchoMode(QLineEdit.Password)
        field.setPlaceholderText("Replacement API key")
        field.setAccessibleName("Replacement API key")
        panel.body.addWidget(field)
        status = label()
        panel.body.addWidget(status)
        def save():
            if not field.text().strip():
                status.setText("Keeping the existing key.")
                return
            try:
                save_local_openai_api_key(field.text())
                self.key_configured = True
                field.clear()
                status.setText("Replacement saved privately.")
                self.update_readiness()
            except (ValueError, OSError) as exc:
                status.setText(str(exc))
        panel.body.addWidget(button("Save key", save, "primary"))
        panel.show()

    def open_memories(self):
        if self.selected_contact_id:
            from .desktop_data import Memories
            Memories(self, self.selected_contact_id).show()

    def open_history(self):
        from .desktop_data import History
        if self.selected_contact_id:
            History(self, self.selected_contact_id).show()

    def import_chat(self):
        from .desktop_data import import_chat
        if self.selected_contact_id and not self.audio_session and not self.starting:
            import_chat(self)

    def open_review(self, record_id):
        from .desktop_data import Review
        existing = self.review_dialogs.get(record_id)
        if existing:
            existing.raise_()
            return
        panel = Review(self, record_id)
        self.review_dialogs[record_id] = panel
        panel.destroyed.connect(lambda: self.review_dialogs.pop(record_id, None))
        panel.show()

    def start_review_job(self, record_id, ledger):
        if self.review_running or self.audio_session:
            panel = self.review_dialogs.get(record_id)
            if panel:
                panel.status.setText("Another call or review is running. This record is saved; use Continue afterward.")
            return False
        self.review_running.add(record_id)
        self.review_errors.pop(record_id, None)
        panel = self.review_dialogs.get(record_id)
        if panel:
            panel.reload()
        path = self.memory_store.path
        def work():
            from .post_call import process_review, review_estimate
            with MemoryStore(path, verify=False) as store:
                self.review_estimates[record_id] = review_estimate(store, record_id)[1]
                return process_review(store, record_id, ledger=ledger, can_run=lambda: not self.audio_session and not self.starting)
        def done(result, error):
            self.review_running.discard(record_id)
            if error:
                self.review_errors[record_id] = str(error)
            panel = self.review_dialogs.get(record_id)
            if panel:
                panel.reload()
            if not error:
                self.schedule_semantic_backfill()
        self.run_job(work, done)
        return True

    def poll(self):
        try:
            if time.monotonic() - self.last_key_check >= 5:
                self.last_key_check = time.monotonic()
                self.key_configured = bool(local_openai_api_key())
            while not self.jobs.empty():
                completed, result, error = self.jobs.get_nowait()
                self.pending_jobs -= 1
                completed(result, error)
            preview = self.preview_session
            if preview:
                snapshot = preview.snapshot()
                pixels = snapshot.thumbnail_rgb
                if pixels is not None:
                    height, width, _ = pixels.shape
                    image = QImage(pixels.data, width, height, pixels.strides[0], QImage.Format_RGB888).copy()
                    self.face_preview.setPixmap(QPixmap.fromImage(image).scaled(144, 108, Qt.KeepAspectRatio, Qt.SmoothTransformation))
                else:
                    self.face_preview.setText(snapshot.status)
            if self.session:
                snapshot = self.session.snapshot()
                now = self.capture_clock_origin + timedelta(seconds=time.perf_counter())
                signal = snapshot.current_signal
                captured = self.capture_clock_origin + timedelta(seconds=signal.timestamp_ms / 1000) if signal else None
                self.visual_aggregator.add(signal, now, captured_at=captured)
                self.live_face_label.setText(snapshot.status)
                self.switch_button.setText("Continue tracking" if snapshot.status == "Face lost" else "Switch face")
                if not self.session.worker_alive and not self.session.capture.worker_alive and not self.stopping:
                    self.session = None
                    self.switch_button.setEnabled(False)
                    self.live_face_label.setText("Face unavailable · audio continues")
            if self.audio_session:
                state = self.audio_session.snapshot()
                minutes, seconds = divmod(int(time.monotonic() - self.call_started), 60)
                spend = self.usage_ledger.total_dollars if self.usage_ledger else 0
                self.live_meta_label.setText(f"{minutes:02d}:{seconds:02d} · {self.model_box.currentText()} · estimated ${spend:.4f}")
                self.live_audio_label.setText(state.fault or f"Mic {state.microphone_status} · Call {state.playback_status}")
                self.drain_audio_results(self.audio_session)
                if not state.running and not self.stopping:
                    self.stop()
            if self.audio_session or self.stopping:
                self.poll_interpretation(time.perf_counter())
            else:
                self.poll_local()
                if self.semantic_backfill_requested:
                    self.schedule_semantic_backfill()
            self.update_readiness()
            self.recovery_button.setVisible(bool(self.persistence_error))
            self.call_notice.setText(self.persistence_error or self.cloud_error or "Suggestions are possibilities, not facts about feelings or intent.")
            if self.closing and not self.pending_jobs and not self.audio_session and not self.starting:
                self.close()
        except Exception as exc:
            test_log.emit("ui_poll_error", error_type=type(exc).__name__)
            self.status_label.setText(f"Update unavailable: {type(exc).__name__}: {exc}")

    def closeEvent(self, event):
        if self.audio_session or self.starting or self.stopping:
            if not self.closing and not confirm(self, "End call and exit?", "Stop capture and save finalized transcript before closing?"):
                event.ignore()
                return
            self.closing = True
            self.stop()
            event.ignore()
            return
        if self.preview_session:
            preview, self.preview_session = self.preview_session, None
            self.closing = True
            self.run_job(preview.stop, lambda *_: None)
        if self.pending_jobs:
            self.closing = True
            self.status_label.setText("Finishing background work before closing…")
            event.ignore()
            return
        self.closed = True
        if self.persistence_error and not confirm(self, "Unsaved transcript", "Some transcript text could not be saved. Close anyway? Choose No to copy it from Open unsaved transcript first."):
            self.closed = False
            self.closing = False
            event.ignore()
            return
        self.timer.stop()
        for timer in self.findChildren(QTimer):
            timer.stop()
        for panel in self.findChildren(QDialog):
            panel.close()
        if self.audio_catalog:
            self.audio_catalog.close()
        self.memory_store.close()
        event.accept()

    def submit_local(self, kind, work):
        self.local_pending[kind] = work

    def poll_local(self):
        try:
            self.local_done.get_nowait()
            self.local_active = False
        except queue.Empty:
            pass
        if self.local_active:
            return
        for kind in ('ask', 'live'):
            work = self.local_pending[kind]
            if work is not None:
                self.local_pending[kind] = None
                self.local_active = True

                def run(work=work):
                    try:
                        work()
                    finally:
                        self.local_done.put(True)
                threading.Thread(target=run, name='bounded-local-retrieval', daemon=True).start()
                break

    def invalidate_memory_context(self) -> None:
        self.interpretation_generation += 1
        self.next_interpretation_snapshot_id = 0
        self.latest_interpretation_snapshot = None
        test_log.emit('context_reset', generation=self.interpretation_generation, contact_id=self.selected_contact_id)
        self.visual_aggregator.reset()
        self.stable_interpretation.reset()
        self.guidance_display.reset()
        self.render_guidance()
        if self.interpretation_coordinator:
            self.interpretation_coordinator.reset(self.interpretation_generation, preserve_cadence=True)
        self.render_interpretation(replaced=True)

    def begin_interpretation_session(self) -> None:
        self.guidance_topic_start = 0
        test_log.emit('call_start', contact_id=self.selected_contact_id)
        self.interpretation_generation += 1
        self.next_interpretation_snapshot_id = 0
        self.latest_interpretation_snapshot = None
        self.interpretation_updated_at = ''
        self.stable_interpretation.reset()
        self.guidance_display.reset()
        self.render_guidance()
        self.usage_ledger = None
        try:
            self.usage_ledger = UsageLedger.product()
            live_model = self.selected_live_model()
            interpreter = OpenAIInterpreter(model=live_model, reasoning='low', ledger=self.usage_ledger, live=True, is_current=lambda item: item.generation == self.interpretation_generation)
            ledger = self.usage_ledger

            def current_guidance(item, store):
                if item.generation != self.interpretation_generation or self.stopping or item.contact_id != self.selected_contact_id:
                    return False
                if max((turn.display_order for turn in item.turns)) < self.guidance_topic_start:
                    return False
                if item.memories:
                    for memory in item.memories:
                        source = memory_source(store, memory.memory_id, item.contact_id, for_cloud=True, display_limit=None)
                        if source is None or source.revision_id != memory.revision_id:
                            return False
                return True

            def combined(item):
                if item.contact_id:
                    with MemoryStore(self.memory_store.path, verify=False) as store:
                        result = interpret_guidance(item, ledger=ledger, client=interpreter._client, model=live_model, reasoning='low', is_current=lambda snapshot: current_guidance(snapshot, store))
                        return result
                return interpreter(item)
            self.interpretation_coordinator = InterpretationCoordinator(combined, generation=self.interpretation_generation, first_request_at=time.perf_counter() + 12, adaptive_cadence=True)
        except InterpretationAuthenticationUnavailable:
            self.interpretation_coordinator = None
            self.set_interpretation_unavailable('OpenAI key not configured — local capture and transcription continue', time.perf_counter())
        except ValueError:
            self.interpretation_coordinator = None
            self.set_interpretation_unavailable('Interpretation budget configuration is invalid — local processing continues', time.perf_counter())
        except (ImportError, OSError):
            self.interpretation_coordinator = None
            self.set_interpretation_unavailable('Cloud interpretation unavailable — local processing continues', time.perf_counter())
        self.render_interpretation(replaced=True)

    def offer_interpretation_snapshot(self) -> None:
        if self.stopping or not self.turns:
            return
        previous_guidance = repr(self.guidance_display.items)
        self.guidance_display.on_speech(self.turns[-1])
        if previous_guidance != repr(self.guidance_display.items):
            self.render_guidance()
        from .memory import _TOPIC_BOUNDARY
        new_topic = bool(_TOPIC_BOUNDARY.search(self.turns[-1].content))
        from .guidance import guidance_context_reset
        if guidance_context_reset(self.turns[-1].content):
            self.guidance_topic_start = self.turns[-1].display_order
            self.guidance_display.invalidate(new_topic=new_topic, turn_ids=set(), memory_ids=set())
            self.render_guidance()
        self.next_interpretation_snapshot_id += 1
        snapshot_id = self.next_interpretation_snapshot_id
        generation = self.interpretation_generation
        captured_turns = [item.model_copy(deep=True) for item in self.turns]
        captured_vocal = list(self.vocal_observations)
        captured_at = datetime.now(timezone.utc)
        captured_visual = self.visual_aggregator.buckets(captured_at)
        captured_contact_id = self.selected_contact_id

        def build_with_memory() -> None:
            try:
                contexts = []
                possible_contexts = []
                ambiguous = False
                semantic_available = False
                preference_notice = ''
                if self.memory_store is not None and captured_contact_id is not None:
                    query, date_query = memory_retrieval_inputs(captured_turns)
                    with MemoryStore(self.memory_store.path, verify=False) as worker_store:
                        result = worker_store.retrieve(captured_contact_id, query, for_cloud=False, date_query=date_query, semantic_query=memory_semantic_input(captured_turns), contact_cue_query=memory_semantic_input(captured_turns, speaker_role=SpeakerRole.SELECTED_CONTACT))
                    test_log.emit('retrieval_result', generation=generation, snapshot_id=snapshot_id, contact_id=captured_contact_id, query=query, date_query=date_query, semantic_query=memory_semantic_input(captured_turns), result=result)
                    ambiguous = result.ambiguous
                    semantic_available = result.semantic_available
                    possible_contexts = [RetrievedMemoryContext(memory_id=item.memory_id, revision_id=item.revision_id, excerpt=textwrap.shorten(item.content, width=180, placeholder='…'), memory_type=item.memory_type, confidence=item.confidence, sensitivity_safe=item.cloud_eligible, rank=item.rank, relevance=item.reason) for item in result.matches[:4]]
                    if not ambiguous:
                        contexts = [item for item in possible_contexts if item.sensitivity_safe]
                    with MemoryStore(self.memory_store.path, verify=False) as worker_store:
                        available_memories = worker_store.list_current_memories(captured_contact_id)
                        test_log.emit('retrieval_corpus', generation=generation, snapshot_id=snapshot_id, contact_id=captured_contact_id, memories=[dict(row) for row in available_memories])
                        preferences = [row for row in available_memories if row['memory_type'] in {'communication_style', 'relationship_preference'} and (not row['needs_review']) and (row['sensitivity'] == 'normal' or row['cloud_allowed'])]
                    if len(preferences) > 1:
                        preference_notice = 'Multiple approved preferences: review for conflicts; at most two are supplied.'
                    ranks = {item.memory_id: item.rank for item in possible_contexts}
                    preferences.sort(key=lambda row: ranks.get(row['memory_id'], 999))
                    styles = [RetrievedMemoryContext(memory_id=row['memory_id'], revision_id=row['revision_id'], excerpt=textwrap.shorten(row['content'], width=180, placeholder='…'), memory_type=row['memory_type'], confidence=row['confidence'], sensitivity_safe=True, rank=i + 1, relevance='approved contact communication preference') for i, row in enumerate(preferences[:2])]
                    style_ids = {item.revision_id for item in styles}
                    contexts = [item for item in contexts if item.revision_id not in style_ids][:4 - len(styles)] + styles
                snapshot = build_snapshot(captured_turns, snapshot_id=snapshot_id, generation=generation, vocal_observations=captured_vocal, visual_buckets=captured_visual, contact_id=captured_contact_id, retrieved_memories=contexts, created_at=captured_at)
                prepared = prepare_interpretation_request(snapshot, preserve_transcript=True)
                if prepared.memory_count != len(snapshot.memories):
                    snapshot = snapshot.model_copy(update={'memories': snapshot.memories[:prepared.memory_count]})
                self.memory_snapshot_results.put((generation, snapshot_id, snapshot, ambiguous, possible_contexts, semantic_available, None, preference_notice))
            except Exception as exc:
                try:
                    fallback = build_snapshot(captured_turns, snapshot_id=snapshot_id, generation=generation, vocal_observations=captured_vocal, visual_buckets=captured_visual)
                except Exception:
                    fallback = None
                self.memory_snapshot_results.put((generation, snapshot_id, fallback, False, [], False, type(exc).__name__, ''))
        if self.memory_store is not None and self.selected_contact_id is not None:
            self.submit_local('live', build_with_memory)
            return
        try:
            self.latest_interpretation_snapshot = build_snapshot(captured_turns, snapshot_id=snapshot_id, generation=generation, vocal_observations=captured_vocal, visual_buckets=captured_visual)
        except ValueError:
            self.set_interpretation_unavailable('Recent conversation exceeds the safe interpretation input limit', time.perf_counter())
            self.render_interpretation(replaced=True)
            return
        if self.interpretation_coordinator:
            self.interpretation_coordinator.offer(self.latest_interpretation_snapshot, time.perf_counter())

    def poll_memory_results(self) -> None:
        while True:
            try:
                generation, snapshot_id, snapshot, ambiguous, possibilities, semantic_available, error_type, preference_notice = self.memory_snapshot_results.get_nowait()
            except queue.Empty:
                break
            if generation != self.interpretation_generation or self.stopping:
                continue
            if self.latest_interpretation_snapshot is not None and snapshot_id < self.latest_interpretation_snapshot.snapshot_id and (snapshot is None or max((t.display_order for t in snapshot.turns)) <= max((t.display_order for t in self.latest_interpretation_snapshot.turns))):
                continue
            if snapshot is not None and self.latest_interpretation_snapshot is not None and (snapshot_id < self.latest_interpretation_snapshot.snapshot_id):
                self.next_interpretation_snapshot_id += 1
                snapshot = snapshot.model_copy(update={'snapshot_id': self.next_interpretation_snapshot_id})
            if snapshot is None:
                self.stable_interpretation.clear_memory_possibilities()
                if error_type == 'ValueError':
                    self.set_interpretation_unavailable('Recent conversation exceeds the safe interpretation input limit', time.perf_counter())
                    self.render_interpretation(replaced=True)
                else:
                    self.memory_status_label.setText('Local memory retrieval unavailable — interpretation continues without memory')
                    self.render_interpretation()
                continue
            if error_type:
                self.stable_interpretation.clear_memory_possibilities()
                self.memory_status_label.setText('Local memory retrieval unavailable — interpretation continues without memory')
            else:
                self.stable_interpretation.offer_memory_possibilities([item for item in possibilities if not item.sensitivity_safe and (not ambiguous) and ('lexical' in item.relevance)], time.perf_counter())
                if not ambiguous:
                    self.guidance_display.offer_local_remember([item for item in possibilities if not item.sensitivity_safe and 'lexical' in item.relevance], max((turn.display_order for turn in snapshot.turns)), time.perf_counter())
                    self.render_guidance()
                if ambiguous:
                    self.memory_status_label.setText('Several memories may fit — ambiguous facts withheld; approved style preferences may still apply')
                elif snapshot.memories:
                    suffix = '' if semantic_available else ' · indirect recall reduced'
                    shown = len(self.stable_interpretation.memory_possibilities)
                    self.memory_status_label.setText(f'Checking {len(snapshot.memories)} candidate memories for relevance · {shown} displayed{suffix}')
                elif self.stable_interpretation.memory_possibilities:
                    self.memory_status_label.setText(f'Showing {len(self.stable_interpretation.memory_possibilities)} approved memory context item(s) · recent match retained briefly')
                else:
                    self.memory_status_label.setText('No eligible approved memory matched this snapshot' if semantic_available else 'No lexical match — indirect recall reduced; run --install-memory-model')
            if preference_notice:
                self.memory_status_label.setText(self.memory_status_label.text() + ' · ' + preference_notice)
            self.latest_interpretation_snapshot = snapshot
            self.render_interpretation()
            if self.interpretation_coordinator:
                self.interpretation_coordinator.offer(snapshot, time.perf_counter())

    def interpretation_error_message(self, error_type: str | None) -> str:
        if error_type == InterpretationBudgetExceeded.__name__:
            return 'Interpretation session budget reached — local processing continues'
        if error_type == InterpretationAuthenticationUnavailable.__name__:
            return 'OpenAI authentication unavailable — local processing continues'
        return 'Cloud interpretation unavailable — local processing continues'

    def poll_interpretation(self, now: float) -> None:
        if self.semantic_backfill_requested:
            self.schedule_semantic_backfill()
        self.poll_local()
        self.poll_memory_results()
        self.suggest_button.setEnabled(bool(self.selected_contact_id and self.latest_interpretation_snapshot and self.interpretation_coordinator and not self.interpretation_coordinator.snapshot().in_flight and not self.stopping))
        if self.interpretation_coordinator:
            for event in self.interpretation_coordinator.poll(now):
                test_log.emit('coordinator_event', generation=self.interpretation_generation, result=event)
                if event.kind == CoordinatorEventKind.ACCEPTED:
                    self.cloud_error = ""
                    assert event.update is not None
                    if hasattr(event.update, 'replies'):
                        from .guidance import selected_memory_context, reconcile_replies
                        guidance_update = reconcile_replies(event.update, self.turns)
                        if self.latest_interpretation_snapshot:
                            self.stable_interpretation.offer_memory_possibilities(selected_memory_context(self.latest_interpretation_snapshot.memories, guidance_update), now)
                            self.memory_status_label.setText(f'Showing {len(self.stable_interpretation.memory_possibilities)} relevant memory context item(s)')
                        source_age = (datetime.now(timezone.utc) - guidance_update.context_at).total_seconds() if guidance_update.context_at is not None else 0
                        self.guidance_display.offer(guidance_update, now, source_age=source_age)
                        self.render_guidance()
                    if self.stable_interpretation.offer(event.update, now) == 'replaced':
                        self.render_interpretation(replaced=True)
                elif event.kind == CoordinatorEventKind.ERROR:
                    self.set_interpretation_unavailable(self.interpretation_error_message(event.error_type), now)
                    self.render_interpretation(replaced=True)
                else:
                    self.render_interpretation()
        memory_expired = self.stable_interpretation.expire_memory_possibilities(now)
        previous_guidance = repr((self.guidance_display.items, self.guidance_display.local_remember))
        self.guidance_display.tick(now)
        if previous_guidance != repr((self.guidance_display.items, self.guidance_display.local_remember)):
            self.render_guidance()
        if memory_expired:
            if self.stable_interpretation.memory_possibilities:
                self.memory_status_label.setText(f'Showing {len(self.stable_interpretation.memory_possibilities)} approved memory context item(s) · recent match retained briefly')
            else:
                self.memory_status_label.setText('No recent approved memory context is displayed')
        if self.interpretation_coordinator and self.audio_session and (not self.stopping):
            state = self.interpretation_coordinator.snapshot()
            if state.in_flight:
                activity = 'Analyzing the conversation…'
            elif state.pending_snapshot_id is not None:
                activity = 'Listening — next analysis is scheduled'
            elif not self.guidance_display.all_items('replies'):
                activity = 'Listening — guidance is active'
            else:
                activity = 'Listening — guidance is active'
            test_log.emit('guidance_waiting_state', state=state, activity=activity, last_speaker=self.turns[-1].speaker_role if self.turns else None)
            self.guidance_status.setText(activity)
        else:
            self.guidance_status.setText('Select a contact to enable guidance' if not self.selected_contact_id else 'Start a call to receive live guidance')
        if self.stable_interpretation.tick(now):
            self.render_interpretation(replaced=True)
        elif memory_expired:
            self.render_interpretation()

    def suggest_now(self):
        if self.latest_interpretation_snapshot and self.interpretation_coordinator and (not self.stopping):
            self.guidance_display.dismissed.clear()
            self.next_interpretation_snapshot_id += 1
            checkpoint = datetime.now(timezone.utc)
            self.latest_interpretation_snapshot = self.latest_interpretation_snapshot.model_copy(update={'snapshot_id': self.next_interpretation_snapshot_id, 'manual': True, 'created_at': checkpoint, 'visual_buckets': list(self.visual_aggregator.buckets(checkpoint))})
            self.interpretation_coordinator.offer(self.latest_interpretation_snapshot, time.perf_counter(), manual=True)
            self.suggest_button.setEnabled(False)

    def drain_audio_results(self, current_audio) -> None:
        while True:
            try:
                draft = current_audio.results.get_nowait()
            except queue.Empty:
                break
            turn = _conversation_turn_from_audio(draft, len(self.turns) + 1)
            self.turns.append(turn)
            test_log.emit('transcript', record_id=self.current_record_id, generation=self.interpretation_generation, turn=turn, vocal=draft.vocal)
            if self.memory_store is not None and self.current_record_id is not None:
                try:
                    self.memory_store.append_turn(self.current_record_id, turn)
                except Exception as exc:
                    self.persistence_error = f'Transcript could not be fully saved ({type(exc).__name__}). Keep the app open and copy the transcript.'
                    self.call_notice.setText(self.persistence_error)
            vocal = _vocal_observation_from_audio(draft, turn.display_order)
            if vocal is not None:
                self.vocal_observations.append(vocal)
            self.offer_interpretation_snapshot()

    def switch(self) -> None:
        test_log.emit('face_switch_requested')
        if self.session:
            self.visual_aggregator.reset()
            if self.session.snapshot().status == 'Face lost':
                self.session.continue_tracking()
            else:
                self.invalidate_memory_context()
                self.session.switch_face()


def run():
    if sys.platform == "win32":
        import ctypes
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("ConversationCopilot")
    app = QApplication.instance() or QApplication(sys.argv[:1])
    app.setStyle("Fusion")
    test_log.start()
    try:
        window = Desktop()
    except (sqlite3.Error, OSError, RuntimeError) as exc:
        QMessageBox.critical(None, "Conversation Copilot could not open", f"Local data could not be opened safely. No data was reset.\n\n{exc}")
        return
    window.show()
    app.exec()
    test_log.emit("app_closed")
