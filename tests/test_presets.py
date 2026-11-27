import re, tempfile, unittest
from pathlib import Path
from db.database import Database
from render.context import make_context
from render.fonts import FontManager
from render.layout import layout
from render.pdf_backend import render_pdf
from services.memo_service import issue_memo
from services.repositories import Templates
from templates_lib.bn_presets import SPECS, all_templates, NOTES
from templates_lib.model import sample_payload, SAMPLE_DOC, validate

LOGO = str(Path(__file__).resolve().parent.parent / "assets" / "logo_rc.png")
BIZ = {"business_name": "Ripon Computer", "business_subtitle": "Your Trusted Tech Partner", "address": "ভাদ্দা বাজার, নাগরপুর, টাঙ্গাইল", "phone": "01903888515"}
KNOWN = {"business_name", "business_subtitle", "address", "phone", "memo_number", "date", "time", "customer_name", "customer_phone", "customer_address"}


class PresetTests(unittest.TestCase):
    def setUp(self): self.fm = FontManager(); self.m = lambda a, b, c, d: self.fm.measure(a, b, c, d)

    def test_count_and_valid(self):
        ts = all_templates("bn")
        self.assertGreaterEqual(len(ts), 10); self.assertLessEqual(len(ts), 20)
        self.assertEqual(len({t["name"] for t in ts}), len(ts))
        for t in ts: validate(t)

    def test_bengali_labels_present(self):
        for t in all_templates("bn"):
            texts = " ".join(e.get("text", "") + e.get("label", "") for e in t["elements"]) + " ".join(c["label"] for e in t["elements"] if e["type"] == "table" for c in e["columns"])
            self.assertTrue(re.search(r"[\u0980-\u09FF]", texts), t["name"])
            self.assertTrue(re.search(r"পণ্যের বিবরণ|টাকা", texts) or t["doc_type"] == "receipt", t["name"])

    def test_placeholders_known_and_shop_info_not_hardcoded(self):
        for t in all_templates("bn"):
            for e in t["elements"]:
                for ph in re.findall(r"\{(\w+)\}", str(e.get("text", "")) + str(e.get("data", ""))):
                    self.assertIn(ph, KNOWN, (t["name"], ph))
                self.assertNotIn("01903888515", str(e.get("text", "")))

    def test_every_template_renders_one_page_inside_bounds(self):
        ctx = make_context(BIZ, SAMPLE_DOC, sample_payload())
        tmp = Path(tempfile.mkdtemp())
        for i, t in enumerate(all_templates("bn")):
            pages = layout(t, ctx, self.m, {"logo": LOGO})
            self.assertEqual(len(pages), 1, t["name"])
            for p in pages[0]["prims"]:
                if p["t"] in ("rect", "text", "image"):
                    self.assertLessEqual(p["x"] + p.get("w", 0), pages[0]["w"] + 0.6, (t["name"], p))
                    self.assertLessEqual(p["y"] + p.get("h", 0), pages[0]["h"] + 0.6, (t["name"], p))
            render_pdf(pages, tmp / f"{i}.pdf", self.fm)

    def test_blank_rows_numbered_and_payment_tick(self):
        t = all_templates("bn")[0]
        ctx = make_context(BIZ, SAMPLE_DOC, sample_payload())
        pages = layout(t, ctx, self.m, {"logo": LOGO})
        nums = [p["text"] for p in pages[0]["prims"] if p["t"] == "text" and p["text"].isdigit() and len(p["text"]) <= 2]
        self.assertIn("15", nums)
        filled = [p for p in pages[0]["prims"] if p["t"] == "rect" and p.get("fill") == "#0B2A5B" and abs(p["w"] - p["h"]) < 0.01 and p["w"] < 3]
        self.assertEqual(len(filled), 1)  # only bKash (sample) is ticked

    def test_long_memo_still_paginates_with_preset(self):
        db = Database(Path(tempfile.mkdtemp()) / "t.db")
        rows = [{"name": f"পণ্য {i}", "qty": "1", "price": "10"} for i in range(60)]
        doc_id, *_ = issue_memo(db, rows, {}, {"name": "রহিম"})
        row = db.conn.execute("SELECT * FROM documents").fetchone()
        pages = layout(all_templates("bn")[0], make_context(BIZ, row), self.m, {"logo": LOGO})
        self.assertGreater(len(pages), 1)
        last = [p["text"] for p in pages[-1]["prims"] if p["t"] == "text"]
        self.assertIn("স্বাক্ষর", last)

    def test_seed_roundtrip_in_db(self):
        db = Database(Path(tempfile.mkdtemp()) / "t.db"); tpl = Templates(db)
        for t in all_templates("bn"): tpl.save(t["name"], t, doc_type=t["doc_type"])
        self.assertEqual(len(tpl.list()), len(SPECS))
        tid = tpl.list()[0]["id"]; self.assertEqual(tpl.get(tid)[1]["elements"][0]["type"], "rect")


if __name__ == "__main__":
    unittest.main()
