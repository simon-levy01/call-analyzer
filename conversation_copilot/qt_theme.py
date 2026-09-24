"""Shared Qt palette: every control and secondary window uses the same theme."""
from PySide6.QtGui import QColor, QPalette
from PySide6.QtCore import Qt
from pathlib import Path


def apply_theme(app, dark):
    app.styleHints().setColorScheme(Qt.ColorScheme.Dark if dark else Qt.ColorScheme.Light)
    page, surface, ink, muted, line = ("#0E1119", "#191E2E", "#E9EDF8", "#A9B5D6", "#3C4970") if dark else ("#FFF7EC", "#FFFFFF", "#16214A", "#4C5E8C", "#CBD5E8")
    roles = dict(zip(("tone", "social", "replies", "memory", "follow_up"),
                     ("#3A2E12", "#2A2447", "#1C2A4E", "#123326", "#3A1E1A") if dark else
                     ("#FFF0CC", "#F0E9FF", "#E7F0FF", "#E9F9F1", "#FFE9E7")))
    palette = QPalette()
    for role, color in ((QPalette.Window, page), (QPalette.Base, surface), (QPalette.AlternateBase, page),
                        (QPalette.WindowText, ink), (QPalette.Text, ink), (QPalette.Button, surface),
                        (QPalette.ButtonText, ink), (QPalette.Highlight, "#344C83" if dark else "#DCE8FF"),
                        (QPalette.HighlightedText, ink), (QPalette.ToolTipBase, surface), (QPalette.ToolTipText, ink)):
        palette.setColor(role, QColor(color))
    app.setPalette(palette)
    style = f"""
        QWidget {{ color: {ink}; font-family: 'Segoe UI'; font-size: 13px; }}
        QWidget, QDialog, QMessageBox {{ background: {page}; }}
        QLabel {{ background: transparent; }}
        QWidget[plain=true] {{ background: transparent; }}
        QLabel[heading=true] {{ font-size: 20px; font-weight: 700; }}
        QFrame[card=true] {{ background: {surface}; border: 1px solid {line}; border-radius: 18px; }}
        QPushButton {{ background: {surface}; border: 1px solid {line}; border-radius: 12px; padding: 7px 13px; font-weight: 600; }}
        QPushButton:hover {{ border: 2px solid #7395ED; padding: 6px 12px; }}
        QPushButton:pressed {{ background: #344C83; color: white; }}
        QPushButton:disabled {{ color: {muted}; background: {page}; border-color: {line}; }}
        QPushButton[role=primary] {{ background: #2B5BE0; color: white; border-color: #7395ED; }}
        QPushButton[role=start]:enabled {{ background: #15803D; color: white; border-color: #4ADE80; }}
        QPushButton[role=start]:enabled:hover {{ background: #166534; }}
        QPushButton[role=start]:enabled:pressed {{ background: #14532D; }}
        QPushButton[role=danger] {{ background: #B42E27; color: white; border-color: #F68479; }}
        QPushButton[large=true] {{ font-size: 20px; border-radius: 18px; }}
        QLineEdit, QPlainTextEdit, QListWidget, QComboBox {{ background: {surface}; border: 1px solid {line}; border-radius: 10px; padding: 8px; selection-background-color: #344C83; selection-color: white; }}
        QComboBox {{ padding-right: 30px; }}
        QComboBox::drop-down {{ border: none; width: 26px; }}
        QComboBox::down-arrow {{ image: url('{(Path(__file__).with_name('assets') / 'chevron.svg').as_posix()}'); width: 12px; height: 12px; }}
        QComboBox QAbstractItemView {{ background: {surface}; color: {ink}; border: 1px solid {line}; selection-background-color: #344C83; outline: 0; padding: 4px; }}
        QAbstractItemView::item {{ padding: 9px; border-radius: 6px; }}
        QAbstractItemView::item:selected {{ background: #344C83; color: white; }}
        QScrollArea {{ border: none; background: transparent; }}
        QScrollBar:vertical {{ width: 10px; background: transparent; }}
        QScrollBar::handle:vertical {{ background: {line}; min-height: 24px; border-radius: 5px; }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
        QCheckBox {{ spacing: 8px; padding: 6px; background: transparent; }}
        QCheckBox::indicator {{ width: 20px; height: 20px; border: 1px solid {line}; border-radius: 5px; background: {surface}; }}
        QCheckBox::indicator:checked {{ background: #2B5BE0; image: url('{(Path(__file__).with_name('assets') / 'check.svg').as_posix()}'); }}
        QSlider::groove:horizontal {{ height: 6px; background: {line}; border-radius: 3px; }}
        QSlider::handle:horizontal {{ width: 18px; margin: -6px 0; background: #4B7BF0; border-radius: 9px; }}
        QPushButton:focus, QLineEdit:focus, QComboBox:focus, QPlainTextEdit:focus, QCheckBox:focus {{ border: 2px solid #7395ED; }}
    """
    for role, color in roles.items():
        style += f'QFrame[role="{role}"], QPushButton[role="{role}"] {{ background: {color}; }}'
    style += f'QPushButton:disabled {{ background: {page}; color: {muted}; border-color: {line}; }}'
    app.setStyleSheet(style)
