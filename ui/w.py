"""Widget layer. Uses PySide6-Fluent-Widgets (modern Windows-11 Fluent look) when installed, and falls back to
plain Qt widgets + a clean stylesheet otherwise. NOTE: qfluentwidgets is GPLv3 for non-commercial use; selling the
software needs its commercial licence (or run on the fallback). See README."""
from PySide6.QtWidgets import QFrame, QLabel, QTableWidget, QVBoxLayout, QWidget
from PySide6.QtWidgets import QLineEdit as PlainLineEdit

try:
    from qfluentwidgets import (CardWidget, CheckBox as QCheckBox, ComboBox as QComboBox, DoubleSpinBox as QDoubleSpinBox, InfoBar, InfoBarPosition,
                                LineEdit as QLineEdit, ListWidget as QListWidget, MessageBox, PrimaryPushButton, PushButton, SpinBox as QSpinBox,
                                SubtitleLabel, TableWidget, TextEdit as QTextEdit, TitleLabel)
    FLUENT = True
except Exception:  # not installed -> plain Qt
    from PySide6.QtWidgets import (QCheckBox, QComboBox, QDoubleSpinBox, QLineEdit, QListWidget, QPushButton as PushButton, QSpinBox, QTextEdit)
    PrimaryPushButton = PushButton; CardWidget = QFrame; TableWidget = None; TitleLabel = SubtitleLabel = None
    InfoBar = MessageBox = InfoBarPosition = None
    FLUENT = False


def new_table(rows, cols):
    if FLUENT:
        t = TableWidget(); t.setRowCount(rows); t.setColumnCount(cols); return t
    return QTableWidget(rows, cols)


def title_label(text):
    if FLUENT: return TitleLabel(text)
    l = QLabel(text); l.setObjectName("h1"); return l


def sub_label(text):
    if FLUENT: return SubtitleLabel(text)
    l = QLabel(text); l.setStyleSheet("font-weight:bold;font-size:11pt;color:#0B2A5B"); return l


class Group(CardWidget):
    """Titled card; put your layout on .body"""
    def __init__(self, title=""):
        super().__init__()
        if not FLUENT: self.setObjectName("card")
        v = QVBoxLayout(self); v.setContentsMargins(16, 12, 16, 14); v.setSpacing(8)
        if title: v.addWidget(sub_label(title))
        self.body = QWidget(); v.addWidget(self.body)
