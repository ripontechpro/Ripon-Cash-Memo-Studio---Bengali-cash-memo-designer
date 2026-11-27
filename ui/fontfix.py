"""Fluent widgets carry their own stylesheet font ('Segoe UI' 14px), which makes Bengali tiny and inconsistent with
the rest of the app. This filter gives every Fluent widget our Bengali font family and a readable size when it is shown."""
from PySide6.QtCore import QEvent, QObject
from PySide6.QtWidgets import QWidget
from .fonts import ui_family

SIZE_PX = 15
_TEXT_WIDGETS = ("LineEdit", "ComboBox", "SpinBox", "CheckBox", "TextEdit", "ListWidget", "TableWidget", "PushButton", "PrimaryPushButton", "SearchLineEdit")


class FontFixer(QObject):
    def __init__(self, parent=None):
        super().__init__(parent); self.family = ui_family()

    def eventFilter(self, obj, ev):
        if ev.type() == QEvent.Show and isinstance(obj, QWidget) and not obj.property("_fontfix"):
            mod = type(obj).__module__ or ""
            if mod.startswith("qfluentwidgets"):
                obj.setProperty("_fontfix", True)
                names = {c.__name__ for c in type(obj).__mro__}
                size = f"font-size:{SIZE_PX}px;" if names & set(_TEXT_WIDGETS) else ""
                css = f"* {{ font-family: '{self.family}'; {size} }}"
                try:
                    from qfluentwidgets import setCustomStyleSheet
                    setCustomStyleSheet(obj, css, css)
                except Exception:
                    obj.setStyleSheet(obj.styleSheet() + css)
        return False


def install(app):
    f = FontFixer(app); app.installEventFilter(f); app._fontfixer = f
