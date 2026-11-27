"""Font registry. Drop Bengali TTFs into assets/fonts (e.g. NotoSansBengali-Regular.ttf / -Bold.ttf)."""
from pathlib import Path
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

FONT_DIR = Path(__file__).resolve().parent.parent / "assets" / "fonts"
PT_MM = 25.4 / 72


class FontManager:
    def __init__(self, font_dir=FONT_DIR):
        self.map = {}  # logical name -> (regular rl name, bold rl name)
        for reg in sorted(Path(font_dir).glob("*Regular*.ttf")) if Path(font_dir).exists() else []:
            base = reg.stem.split("-")[0]
            bold = reg.with_name(reg.name.replace("Regular", "Bold"))
            self.register(base, reg, bold if bold.exists() else reg)

    def register(self, name, regular, bold=None):
        r, b = f"{name}-R", f"{name}-B"
        pdfmetrics.registerFont(TTFont(r, str(regular)))
        pdfmetrics.registerFont(TTFont(b, str(bold or regular)))
        self.map[name] = (r, b)

    def rl_name(self, name, bold=False):
        if name in self.map:
            return self.map[name][1 if bold else 0]
        return "Helvetica-Bold" if bold else "Helvetica"

    def measure(self, text, name, size_pt, bold=False):
        """Text width in mm (reportlab metrics; Qt backend supplies its own measure)."""
        return pdfmetrics.stringWidth(text, self.rl_name(name, bold), size_pt) * PT_MM
