"""ReportLab PDF backend. NOTE: ReportLab does not do complex-script shaping, so Bengali conjuncts can
render incorrectly here. The Qt backend (render/qt_backend.py) is the production path for Bengali and
for print preview; this backend is used for tests, English documents and headless export."""
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.lib.units import mm
from .codes import qr_matrix, code128_runs
from .fonts import FontManager, PT_MM


def render_pdf(pages, path, fonts: FontManager):
    c = canvas.Canvas(str(path))
    for pg in pages:
        W, H = pg["w"], pg["h"]
        c.setPageSize((W * mm, H * mm))
        Y = lambda y: (H - y) * mm
        for p in pg["prims"]:
            t = p["t"]
            if t == "rect":
                if p.get("fill"): c.setFillColor(HexColor(p["fill"]))
                if p.get("stroke"): c.setStrokeColor(HexColor(p["stroke"])); c.setLineWidth(p["lw"] * mm)
                if p.get("r"):
                    c.roundRect(p["x"] * mm, Y(p["y"] + p["h"]), p["w"] * mm, p["h"] * mm, p["r"] * mm, stroke=int(bool(p.get("stroke"))), fill=int(bool(p.get("fill"))))
                else:
                    c.rect(p["x"] * mm, Y(p["y"] + p["h"]), p["w"] * mm, p["h"] * mm, stroke=int(bool(p.get("stroke"))), fill=int(bool(p.get("fill"))))
            elif t == "poly":
                if p.get("fill"): c.setFillColor(HexColor(p["fill"]))
                path = c.beginPath(); pts = p["points"]; path.moveTo(pts[0][0] * mm, Y(pts[0][1]))
                for x_, y_ in pts[1:]: path.lineTo(x_ * mm, Y(y_))
                path.close()
                if p.get("stroke"): c.setStrokeColor(HexColor(p["stroke"])); c.setLineWidth(p["lw"] * mm)
                c.drawPath(path, stroke=int(bool(p.get("stroke"))), fill=int(bool(p.get("fill"))))
            elif t == "line":
                c.setStrokeColor(HexColor(p["color"])); c.setLineWidth(p["lw"] * mm); c.setDash(*( ([1.2 * mm, 1.2 * mm], 0) if p.get("dash") else ([], 0) ))
                c.line(p["x"] * mm, Y(p["y"]), p["x2"] * mm, Y(p["y2"]))
            elif t == "text":
                name = fonts.rl_name(p["font"], p["bold"])
                c.setFont(name, p["size"]); c.setFillColor(HexColor(p["color"]))
                base = Y(p["y"] + p["size"] * PT_MM * 0.85)
                tw = fonts.measure(p["text"], p["font"], p["size"], p["bold"])
                x = p["x"] + {"left": 0, "center": (p["w"] - tw) / 2, "right": p["w"] - tw}[p["align"]]
                c.drawString(x * mm, base, p["text"])
            elif t == "image":
                c.drawImage(p["path"], p["x"] * mm, Y(p["y"] + p["h"]), p["w"] * mm, p["h"] * mm, mask="auto")
            elif t == "qr":
                m = qr_matrix(p["data"]); n = len(m); s = p["size"] / n
                c.setFillColor(HexColor("#000000"))
                for r in range(n):
                    for k in range(n):
                        if m[r][k]: c.rect((p["x"] + k * s) * mm, Y(p["y"] + (r + 1) * s), s * mm, s * mm, stroke=0, fill=1)
            elif t == "barcode":
                runs = code128_runs(p["data"]); total = sum(w for _, w in runs); u = p["w"] / total; x = p["x"]
                c.setFillColor(HexColor("#000000"))
                for bar, w in runs:
                    if bar: c.rect(x * mm, Y(p["y"] + p["h"]), w * u * mm, p["h"] * mm, stroke=0, fill=1)
                    x += w * u
        c.showPage()
    c.save()
    return path
