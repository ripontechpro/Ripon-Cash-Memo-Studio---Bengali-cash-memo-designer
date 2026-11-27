from .i18n import T
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QAbstractItemView, QHeaderView, QMessageBox, QTableWidgetItem
from . import w


def h1(text): return w.title_label(text)


def button(text, slot=None, secondary=False, danger=False):
    b = w.PushButton(text) if (secondary or danger or not w.FLUENT) else w.PrimaryPushButton(text)
    if danger: b.setStyleSheet("QPushButton{background:#C0392B;color:white;border-radius:5px;padding:6px 14px}")
    elif not w.FLUENT:
        b.setProperty("secondary" if secondary else "primary", True)
    if slot: b.clicked.connect(lambda _=False: slot())
    return b


def table(headers):
    t = w.new_table(0, len(headers)); t.setHorizontalHeaderLabels(headers)
    t.setAlternatingRowColors(True); t.setEditTriggers(QAbstractItemView.NoEditTriggers)
    t.setSelectionBehavior(QAbstractItemView.SelectRows); t.verticalHeader().setVisible(False)
    t.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
    if w.FLUENT:
        t.setBorderVisible(True); t.setBorderRadius(8)
    return t


def fill_table(t, rows):
    t.setRowCount(0)
    for r in rows:
        i = t.rowCount(); t.insertRow(i)
        for c, v in enumerate(r):
            t.setItem(i, c, QTableWidgetItem(str(v)))


def ask(parent, title, text):
    if w.FLUENT:
        m = w.MessageBox(title, text, parent.window()); m.yesButton.setText(T("হ্যাঁ")); m.cancelButton.setText(T("না")); return bool(m.exec())
    return QMessageBox.question(parent, title, text) == QMessageBox.Yes


def _bar(kind, parent, title, text):
    if w.FLUENT:
        getattr(w.InfoBar, kind)(title=title, content=str(text), orient=Qt.Horizontal, isClosable=True, position=w.InfoBarPosition.TOP, duration=4500, parent=parent.window())
    else:
        QMessageBox.information(parent, title, str(text))


def error(parent, text): _bar("error", parent, T("ত্রুটি"), text)


def success(parent, text): _bar("success", parent, T("সফল"), text)
