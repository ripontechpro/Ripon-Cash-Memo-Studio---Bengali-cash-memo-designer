from .i18n import T, LANG
from templates_lib.bn_presets import display_name
"""Template Studio (property-grid editor + live preview). Visual drag-and-drop canvas is the next phase."""
import copy
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QFormLayout, QHBoxLayout, QInputDialog, QLabel, QVBoxLayout, QWidget, QScrollArea, QTabWidget
from .w import QCheckBox, QComboBox, QLineEdit, QListWidget, Group as QGroupBox
from core.constants import PAPER_MM
from render import qt_backend as qb
from render.context import make_context
from render.layout import layout
from templates_lib.model import default_template, validate, sample_payload, SAMPLE_DOC, PRESETS
from .common import h1, button, table, fill_table, ask, error, success
from .preview import PreviewDialog, sample_pages

NEW_ELEMENTS = {
    "text": {"type": "text", "text": T("কাস্টম লেখা"), "x": 12, "y": 20, "w": 80, "h": 6, "size": 10, "bold": False, "color": "#000000", "align": "left", "font": "Noto Sans Bengali", "pages": "first"},
    "line": {"type": "line", "x": 12, "y": 30, "x2": 100, "y2": 30, "color": "#000000", "lw": 0.3, "pages": "first"},
    "rect": {"type": "rect", "x": 12, "y": 30, "w": 50, "h": 20, "fill": "#EAF2FB", "stroke": "#0B6BCB", "lw": 0.3, "pages": "first"},
    "image": {"type": "image", "src": "logo", "x": 12, "y": 12, "w": 25, "h": 25, "align": "left", "pages": "first"},
    "qr": {"type": "qr", "data": "{memo_number}", "x": 170, "y": 250, "size": 24, "pages": "last"},
    "barcode": {"type": "barcode", "data": "{memo_number}", "x": 12, "y": 250, "w": 60, "h": 12, "pages": "last"},
}


class TemplateEditor(QDialog):
    def __init__(self, app, name, tpl, parent=None):
        super().__init__(parent); self.app, self.tpl, self.name = app, copy.deepcopy(tpl), name
        self.setWindowTitle(T("টেমপ্লেট স্টুডিও — {}").format(name)); self.resize(1000, 700); self.cur = -1
        root = QHBoxLayout(self)
        left = QVBoxLayout(); root.addLayout(left, 1)
        pg = QGroupBox(T("পৃষ্ঠা")); f = QFormLayout(pg.body); P = self.tpl["page"]
        self.size = QComboBox(); self.size.addItems(list(PAPER_MM) + ["Custom"]); self.size.setCurrentText(P.get("size", "A4"))
        self.orient = QComboBox(); self.orient.addItems(["portrait", "landscape"]); self.orient.setCurrentText(P.get("orientation", "portrait"))
        self.cw, self.ch, self.margin = QLineEdit(str(P.get("width_mm", 210))), QLineEdit(str(P.get("height_mm", 297))), QLineEdit(str(P.get("margin_mm", 10)))
        self.bg = QLineEdit(P.get("bg_color", "#FFFFFF")); self.bw = QLineEdit(str(P.get("border", {}).get("width", 0))); self.bc = QLineEdit(P.get("border", {}).get("color", "#0B6BCB"))
        for l, w in ((T("সাইজ"), self.size), (T("ওরিয়েন্টেশন"), self.orient), (T("কাস্টম প্রস্থ মিমি"), self.cw), (T("কাস্টম উচ্চতা মিমি"), self.ch), (T("মার্জিন মিমি"), self.margin), (T("ব্যাকগ্রাউন্ড"), self.bg), (T("বর্ডারের পুরুত্ব"), self.bw), ("Border color", self.bc)): f.addRow(l, w)
        left.addWidget(pg)
        self.lst = QListWidget(); self.lst.currentRowChanged.connect(self.select); left.addWidget(QLabel(T("উপাদানসমূহ"))); left.addWidget(self.lst, 1)
        r1 = QHBoxLayout(); self.add_type = QComboBox(); self.add_type.addItems(NEW_ELEMENTS); r1.addWidget(self.add_type); r1.addWidget(button(T("যোগ করুন"), self.add_el)); left.addLayout(r1)
        r2 = QHBoxLayout()
        for t, s in ((T("কপি করুন"), self.dup), (T("মুছুন"), self.delete), ("▲", lambda: self.move(-1)), ("▼", lambda: self.move(1))): r2.addWidget(button(t, s, True))
        left.addLayout(r2)

        right = QVBoxLayout(); root.addLayout(right, 2)
        self.tabs = QTabWidget(); right.addWidget(self.tabs, 1)
        self.props_host = QWidget(); self.props = QFormLayout(self.props_host); sc = QScrollArea(); sc.setWidgetResizable(True); sc.setWidget(self.props_host); self.tabs.addTab(sc, T("বৈশিষ্ট্য"))
        self.cols = table(["key", "label", "width_mm", "align"])
        from PySide6.QtWidgets import QAbstractItemView
        self.cols.setEditTriggers(QAbstractItemView.AllEditTriggers); ctab = QWidget(); cl = QVBoxLayout(ctab); cl.addWidget(QLabel(T("টেবিলের কলাম (key: sn, name, qty, unit, price, discount, total অথবা নিজের কোনো key)"))); cl.addWidget(self.cols)
        cb = QHBoxLayout()
        for t, s in ((T("কলাম যোগ"), self.add_col), (T("মুছুন"), self.del_col), (T("◀ বামে"), lambda: self.move_col(-1)), (T("ডানে ▶"), lambda: self.move_col(1))): cb.addWidget(button(t, s, True))
        cl.addLayout(cb); self.tabs.addTab(ctab, T("টেবিলের কলাম")); self.refresh_cols()
        self.fields = {}
        bb = QHBoxLayout(); bb.addStretch()
        bb.addWidget(button(T("প্রিভিউ"), self.preview, True)); bb.addWidget(button(T("টেমপ্লেট সংরক্ষণ"), self.save)); right.addLayout(bb)
        self.reload_list()

    # --- element list
    def reload_list(self, keep=0):
        self.lst.blockSignals(True); self.lst.clear()
        for e in self.tpl["elements"]:
            self.lst.addItem(f"{e['type']}: {str(e.get('text') or e.get('label') or e.get('data') or e.get('src') or '')[:28]}")
        self.lst.blockSignals(False)
        if self.tpl["elements"]: self.lst.setCurrentRow(min(keep, len(self.tpl["elements"]) - 1)); self.select(self.lst.currentRow())

    def commit_props(self):
        if self.cur < 0 or self.cur >= len(self.tpl["elements"]): return
        e = self.tpl["elements"][self.cur]
        for k, w in self.fields.items():
            old = e.get(k)
            if isinstance(w, QCheckBox): e[k] = w.isChecked()
            elif isinstance(old, bool): e[k] = w.text().lower() in ("1", "true", "yes")
            elif isinstance(old, (int, float)):
                try: e[k] = float(w.text()) if "." in w.text() else int(w.text())
                except ValueError: pass
            elif k in ("columns", "rows"): pass
            else: e[k] = w.text()
        self.commit_cols()

    def select(self, row):
        self.commit_props(); self.cur = row
        while self.props.rowCount(): self.props.removeRow(0)
        self.fields = {}
        if row < 0: return
        e = self.tpl["elements"][row]
        for k, v in e.items():
            if k in ("columns", "rows", "type"): continue
            w = QCheckBox() if isinstance(v, bool) else QLineEdit("" if v is None else str(v))
            if isinstance(v, bool): w.setChecked(v)
            self.fields[k] = w; self.props.addRow(k, w)
        self.refresh_cols()

    def add_el(self):
        self.commit_props(); self.tpl["elements"].append(copy.deepcopy(NEW_ELEMENTS[self.add_type.currentText()])); self.reload_list(len(self.tpl["elements"]) - 1)

    def dup(self):
        if self.cur >= 0: self.commit_props(); self.tpl["elements"].insert(self.cur + 1, copy.deepcopy(self.tpl["elements"][self.cur])); self.reload_list(self.cur + 1)

    def delete(self):
        if self.cur >= 0 and ask(self, T("মুছুন"), T("এই উপাদান মুছবেন?")):
            del self.tpl["elements"][self.cur]; self.cur = -1; self.reload_list(0)

    def move(self, d):
        i = self.cur; j = i + d
        if 0 <= i < len(self.tpl["elements"]) and 0 <= j < len(self.tpl["elements"]):
            self.commit_props(); E = self.tpl["elements"]; E[i], E[j] = E[j], E[i]; self.reload_list(j)

    # --- columns
    def table_el(self):
        return next((e for e in self.tpl["elements"] if e["type"] == "table"), None)

    def refresh_cols(self):
        t = self.table_el(); fill_table(self.cols, [[c["key"], c["label"], c["width_mm"], c.get("align", "left")] for c in t["columns"]] if t else [])
        from PySide6.QtCore import Qt as _Q
        for r in range(self.cols.rowCount()):
            for c in range(4): self.cols.item(r, c).setFlags(self.cols.item(r, c).flags() | _Q.ItemIsEditable)

    def commit_cols(self):
        t = self.table_el()
        if not t or self.cols.rowCount() == 0: return
        cols = []
        for r in range(self.cols.rowCount()):
            g = lambda c: self.cols.item(r, c).text().strip()
            try: w = float(g(2))
            except ValueError: w = 20
            cols.append({"key": g(0) or f"col{r}", "label": g(1), "width_mm": max(w, 5), "align": g(3) if g(3) in ("left", "center", "right") else "left"})
        t["columns"] = cols

    def add_col(self):
        self.commit_cols(); t = self.table_el()
        if t: t["columns"].append({"key": f"custom{len(t['columns'])}", "label": T("নতুন কলাম"), "width_mm": 20, "align": "center"}); self.refresh_cols()

    def del_col(self):
        r = self.cols.currentRow(); t = self.table_el()
        if t and r >= 0 and len(t["columns"]) > 1: self.commit_cols(); del t["columns"][r]; self.refresh_cols()

    def move_col(self, d):
        r = self.cols.currentRow(); t = self.table_el()
        if t and 0 <= r + d < len(t["columns"]) and r >= 0:
            self.commit_cols(); c = t["columns"]; c[r], c[r + d] = c[r + d], c[r]; self.refresh_cols(); self.cols.selectRow(r + d)

    # --- apply / preview / save
    def apply_page(self):
        self.commit_props(); P = self.tpl["page"]
        try:
            P.update(size=self.size.currentText(), orientation=self.orient.currentText(), margin_mm=float(self.margin.text()), bg_color=self.bg.text(),
                     border={"width": float(self.bw.text()), "color": self.bc.text()})
            if P["size"] == "Custom": P.update(width_mm=float(self.cw.text()), height_mm=float(self.ch.text()))
        except ValueError: raise ValueError(T("পৃষ্ঠার মান সংখ্যায় দিতে হবে"))
        validate(self.tpl)

    def preview(self):
        try: self.apply_page()
        except ValueError as e: return error(self, e)
        biz = self.app.business(); ctx = make_context(biz, SAMPLE_DOC, sample_payload())
        PreviewDialog(self.app, lambda l, f_: sample_pages(self.app, self.tpl, l, f_), T("টেমপ্লেট প্রিভিউ"), self).exec()

    def save(self):
        try: self.apply_page()
        except ValueError as e: return error(self, e)
        self.result_tpl = self.tpl; self.accept()


class StudioPage(QWidget):
    def __init__(self, app):
        super().__init__(); self.setObjectName("page"); self.app = app; v = QVBoxLayout(self); v.addWidget(h1(T("টেমপ্লেট স্টুডিও ও সংরক্ষিত টেমপ্লেট")))
        bar = QHBoxLayout()
        for t, s, sec in ((T("নতুন টেমপ্লেট"), self.new, False), (T("সম্পাদনা"), self.edit, True), (T("কপি করুন"), self.dup, True), (T("মুছুন"), self.delete, True)): bar.addWidget(button(t, s, sec))
        bar.addStretch(); v.addLayout(bar); self.t = table(["ID", T("নাম"), T("ধরন"), T("হালনাগাদ")]); v.addWidget(self.t)

    def refresh(self): fill_table(self.t, [[r["id"], display_name(r["name"], LANG), r["doc_type"], r["updated_at"]] for r in self.app.templates.list()])

    def sel(self):
        r = self.t.currentRow(); return int(self.t.item(r, 0).text()) if r >= 0 else None

    def new(self):
        name, ok = QInputDialog.getText(self, T("নতুন টেমপ্লেট"), T("টেমপ্লেটের নাম:"))
        if not (ok and name.strip()): return
        btype, ok = QInputDialog.getItem(self, T("ব্যবসার প্রিসেট"), T("শুরু করুন:"), ["General"] + list(PRESETS), 0, False)
        if not ok: return
        tpl = default_template()
        if btype in PRESETS:
            for e in tpl["elements"]:
                if e.get("text") == "{terms}": e["text"] = PRESETS[btype]["terms"]
                if e.get("text") == "{thank_you}": e["text"] = PRESETS[btype]["thank_you"]
        self.run(name.strip(), tpl, None)

    def edit(self):
        i = self.sel()
        if i: name, tpl = self.app.templates.get(i); self.run(name, tpl, i)

    def run(self, name, tpl, tid):
        d = TemplateEditor(self.app, name, tpl, self)
        if d.exec(): self.app.templates.save(name, d.result_tpl, tid); self.refresh()

    def dup(self):
        i = self.sel()
        if i: self.app.templates.duplicate(i); self.refresh()

    def delete(self):
        i = self.sel()
        if i and ask(self, T("মুছুন"), T("এই টেমপ্লেট মুছবেন? সংরক্ষিত মেমো ডিফল্ট ডিজাইনে প্রিন্ট হবে।")): self.app.templates.delete(i); self.refresh()
