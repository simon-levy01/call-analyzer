"""First-run setup for the downloadable Windows app."""
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QProgressBar

from . import audio, semantic
from .interpretation import local_openai_api_key, save_local_openai_api_key


def needs_setup(database_path):
    return (not local_openai_api_key() or not audio.local_model_available()
            or not semantic.model_ready(semantic.default_cache_dir(database_path)))


class SetupDialog(QDialog):
    progress = Signal(str)

    def __init__(self, owner):
        super().__init__(owner)
        self.owner = owner
        self.busy = False
        self.setWindowTitle('Set up Conversation Copilot')
        self.setWindowModality(Qt.ApplicationModal)
        self.resize(600, 430)
        layout = QVBoxLayout(self)
        intro = QLabel('Welcome. This app saves your contacts, memories and call history locally '
                       'in your Windows account. First, prepare the local models and add your OpenAI API key.')
        intro.setWordWrap(True)
        layout.addWidget(intro)
        requirements = QLabel('Calls require a compatible NVIDIA GPU and driver. Model setup needs internet '
                             'and several GB of free space. AI features use your API account and cost money.')
        requirements.setWordWrap(True)
        layout.addWidget(requirements)
        self.key = QLineEdit()
        self.key.setEchoMode(QLineEdit.Password)
        self.key.setPlaceholderText('OpenAI API key' if not local_openai_api_key() else 'Optional replacement API key')
        self.key.setAccessibleName('OpenAI API key')
        layout.addWidget(self.key)
        self.status = QLabel('Ready to prepare the models. Downloads can take several minutes.')
        self.status.setWordWrap(True)
        layout.addWidget(self.status)
        self.progress.connect(self.status.setText)
        self.bar = QProgressBar()
        self.bar.setRange(0, 0)
        self.bar.hide()
        layout.addWidget(self.bar)
        self.prepare = QPushButton('Prepare models and save key')
        self.prepare.clicked.connect(self.start)
        layout.addWidget(self.prepare)
        self.later = QPushButton('Set up later')
        self.later.clicked.connect(self.reject)
        layout.addWidget(self.later)

    def start(self):
        if self.busy:
            return
        try:
            if self.key.text().strip():
                save_local_openai_api_key(self.key.text())
                self.key.clear()
            if not local_openai_api_key():
                raise ValueError('Enter your OpenAI API key to continue.')
        except (ValueError, OSError) as exc:
            self.status.setText(str(exc))
            return
        self.owner.key_configured = True
        self.owner.update_readiness()
        self.busy = True
        self.prepare.setEnabled(False)
        self.later.setEnabled(False)
        self.key.setEnabled(False)
        self.bar.show()
        self.status.setText('Checking the NVIDIA GPU and local models…')
        cache_dir = semantic.default_cache_dir(self.owner.memory_store.path)

        def work():
            audio.prepare_transcription_runtime()
            if not audio.local_model_available():
                self.progress.emit('Downloading the transcription model…')
                audio.install_local_model()
            self.progress.emit('Checking the transcription model…')
            model = audio._load_local_model()
            del model
            if not semantic.model_ready(cache_dir):
                self.progress.emit('Downloading the memory model…')
                semantic.install_model(cache_dir)
            if not audio.local_model_available() or not semantic.model_ready(cache_dir):
                raise RuntimeError('Model setup did not finish. Please try again.')

        def finished(result, error):
            self.busy = False
            self.bar.hide()
            self.later.setEnabled(True)
            self.key.setEnabled(True)
            self.prepare.setEnabled(True)
            if error:
                self.status.setText(f'Setup could not finish: {error}\nCheck your internet connection and NVIDIA driver, then try again.')
                self.prepare.setText('Retry setup')
            else:
                self.key.setEnabled(False)
                self.status.setText('Setup complete. Your API key and models are saved on this computer.')
                self.prepare.setText('Continue to the app')
                self.prepare.clicked.disconnect(self.start)
                self.prepare.clicked.connect(self.accept)
                if not self.owner.closing:
                    self.owner.refresh_devices()
                    self.owner.schedule_semantic_backfill()
        self.owner.run_job(work, finished)

    def reject(self):
        if not self.busy:
            super().reject()

    def closeEvent(self, event):
        if self.busy:
            event.ignore()
        else:
            super().closeEvent(event)
