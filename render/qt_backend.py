"""Qt painter backend (production path). Qt uses HarfBuzz, so Bengali conjuncts shape correctly, and the
same code path draws the on-screen preview, the PDF, PNG export and the printer => output matches preview.
Requires PySide6 (not available in the dev sandbox; test on Windows)."""
from pathlib import Path
from PySide6.QtCore import QMarginsF, QPointF, QRectF, QSizeF, Qt
from PySide6.QtGui import (QColor, QFont, QFontDatabase, QFontMetricsF, QImage, QPageLayout, QPageSize,
                           QPainter, QPdfWriter, QPen, QBrush, QPixmap, QPolygonF)
from .codes import qr_matrix, code128_runs

U = 100  # logical units per mm inside paint_page (fonts use integer pixel sizes, so use a fine grid)
PT_TO_MM = 25.4 / 72


def load_fonts(font_dir):
    for f in Path(font_dir).glob("*.ttf"):
        QFontDatabase.addApplicationFont(str(f))


def _font(name, size_pt, bold):
    f = QFont(name or "Noto Sans Bengali")
    f.setFamilies([name or "Noto Sans Bengali", "Noto Sans Bengali", "Nirmala UI", "Kalpurush", "SolaimanLipi", "Vrinda"]); f.setPixelSize(max(1, round(size_pt * PT_TO_MM * U))); f.setBold(bold); return f


def measure_mm(text, name, size_pt, bold=False):
    """Text width in mm, measured at 100 units/mm so it is independent of screen DPI."""
    return QFontMetricsF(_font(name, size_pt, bold)).horizontalAdvance(text) / U


def paint_page(p: QPainter, pg, scale):
    """Draw one laid-out page. scale = device pixels per mm."""
    p.save(); p.scale(scale / U, scale / U)
    S = lambda v: v * U
    for pr in pg["prims"]:
        t = pr["t"]
        if t == "rect":
            p.setBrush(QBrush(QColor(pr["fill"])) if pr.get("fill") else Qt.NoBrush)
            p.setPen(QPen(QColor(pr["stroke"]), S(pr["lw"])) if pr.get("stroke") else Qt.NoPen)
            rect = QRectF(S(pr["x"]), S(pr["y"]), S(pr["w"]), S(pr["h"]))
            if pr.get("r"): p.drawRoundedRect(rect, S(pr["r"]), S(pr["r"]))
            else: p.drawRect(rect)
        elif t == "poly":
            p.setBrush(QBrush(QColor(pr["fill"])) if pr.get("fill") else Qt.NoBrush)
            p.setPen(QPen(QColor(pr["stroke"]), S(pr["lw"])) if pr.get("stroke") else Qt.NoPen)
            p.drawPolygon(QPolygonF([QPointF(S(x_), S(y_)) for x_, y_ in pr["points"]]))
        elif t == "line":
            pen = QPen(QColor(pr["color"]), S(pr["lw"]))
            if pr.get("dash"): pen.setStyle(Qt.DashLine)
            p.setPen(pen); p.drawLine(int(S(pr["x"])), int(S(pr["y"])), int(S(pr["x2"])), int(S(pr["y2"])))
        elif t == "text":
            p.setFont(_font(pr["font"], pr["size"], pr["bold"])); p.setPen(QColor(pr["color"]))
            al = {"left": Qt.AlignLeft, "center": Qt.AlignHCenter, "right": Qt.AlignRight}[pr["align"]]
            p.drawText(QRectF(S(pr["x"]), S(pr["y"]), S(pr["w"]), S(pr["size"] * PT_TO_MM * 1.4)), int(al | Qt.AlignTop), pr["text"])
        elif t == "image":
            img = QImage(pr["path"])
            if not img.isNull():
                p.setRenderHint(QPainter.SmoothPixmapTransform)
                p.drawImage(QRectF(S(pr["x"]), S(pr["y"]), S(pr["w"]), S(pr["h"])), img)
        elif t == "qr":
            m = qr_matrix(pr["data"]); n = len(m); s = pr["size"] / n
            p.setPen(Qt.NoPen); p.setBrush(QColor("#000000"))
            for r in range(n):
                for k in range(n):
                    if m[r][k]: p.drawRect(QRectF(S(pr["x"] + k * s), S(pr["y"] + r * s), S(s), S(s)))
        elif t == "barcode":
            runs = code128_runs(pr["data"]); u = pr["w"] / sum(w for _, w in runs); x = pr["x"]
            p.setPen(Qt.NoPen); p.setBrush(QColor("#000000"))
            for bar, w in runs:
                if bar: p.drawRect(QRectF(S(x), S(pr["y"]), S(w * u), S(pr["h"])))
                x += w * u
    p.restore()


def render_pdf(pages, path, dpi=600):
    w = QPdfWriter(str(path)); w.setResolution(dpi)
    first = pages[0]
    w.setPageSize(QPageSize(QSizeF(first["w"], first["h"]), QPageSize.Millimeter))
    w.setPageMargins(QMarginsF(0, 0, 0, 0))
    p = QPainter(w); scale = dpi / 25.4
    for i, pg in enumerate(pages):
        if i: w.newPage()
        paint_page(p, pg, scale)
    p.end()


def render_png(page, path, dpi=200):
    scale = dpi / 25.4
    img = QImage(int(page["w"] * scale), int(page["h"] * scale), QImage.Format_RGB32); img.fill(Qt.white)
    p = QPainter(img); p.setRenderHint(QPainter.Antialiasing); p.setRenderHint(QPainter.TextAntialiasing)
    paint_page(p, page, scale); p.end(); img.save(str(path))


def print_pages(pages, printer, copies=1):
    """printer: a QPrinter configured by QPrintDialog/QPrintPreviewDialog."""
    printer.setCopyCount(copies)
    p = QPainter(printer); scale = printer.resolution() / 25.4
    for i, pg in enumerate(pages):
        if i: printer.newPage()
        paint_page(p, pg, scale)
    p.end()
