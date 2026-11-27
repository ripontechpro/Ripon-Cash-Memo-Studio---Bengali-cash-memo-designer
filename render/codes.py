"""QR matrix and Code128 bar runs, both via reportlab's pure-python encoders (no extra dependency)."""
from reportlab.graphics.barcode import qrencoder
from reportlab.graphics.barcode.code128 import Code128


def qr_matrix(data: str):
    q = qrencoder.QRCode(None, qrencoder.QRErrorCorrectLevel.M)
    q.addData(data); q.make()
    n = q.getModuleCount()
    return [[q.isDark(r, c) for c in range(n)] for r in range(n)]


def code128_runs(data: str):
    """Return list of (is_bar, width_in_modules). Uppercase letter = bar, lowercase = space; A/a=1 ... D/d=4."""
    b = Code128(data); b.validate(); b.encode(); b.decompose()
    return [(ch.isupper(), ord(ch.lower()) - 96) for ch in b.decomposed]
