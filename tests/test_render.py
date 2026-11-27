import json, tempfile, unittest
from pathlib import Path
from core.calculation import Adjustments
from db.database import Database
from services.memo_service import issue_memo
from services.repositories import Templates, Customers, Products, Settings
from templates_lib.model import default_template, validate
from render.context import make_context
from render.fonts import FontManager
from render.layout import layout
from render.pdf_backend import render_pdf
from reports import reports
from exporters import export

LOGO = str(Path(__file__).resolve().parent.parent / "assets" / "logo.png")
BIZ = {"business_name": "RIPON COMPUTER AND ELECTRONICS", "business_subtitle": "Your Trusted Tech Partner",
       "address": "Savar, Dhaka", "phone": "01XXXXXXXXX", "terms": "Warranty as per policy.", "thank_you": "Thank you!"}


class RenderTests(unittest.TestCase):
    def setUp(self):
        self.dir = Path(tempfile.mkdtemp()); self.db = Database(self.dir / "t.db"); self.fm = FontManager()

    def memo(self, n=3):
        rows = [{"name": f"Item {i}", "description": "long description " * 6 if i == 0 else "", "qty": "2", "price": "250", "unit": "Pcs"} for i in range(n)]
        return issue_memo(self.db, rows, {"vat_percent": "5", "paid": "100"}, {"name": "Karim"}, "bKash")

    def pages(self, n=3, **kw):
        doc_id, number, totals, payload = self.memo(n)
        row = self.db.conn.execute("SELECT * FROM documents WHERE id=?", (doc_id,)).fetchone()
        ctx = make_context(BIZ, row)
        return layout(default_template(), ctx, lambda t, f, s, b: self.fm.measure(t, f, s, b), {"logo": LOGO}), ctx

    def test_layout_single_page_and_totals(self):
        pages, ctx = self.pages(3)
        self.assertEqual(len(pages), 1)
        texts = [p["text"] for p in pages[0]["prims"] if p["t"] == "text"]
        self.assertIn("RIPON COMPUTER AND ELECTRONICS", texts)
        self.assertIn(ctx["grand_total"], texts)
        self.assertEqual(ctx["grand_total"], "1,575.00")

    def test_pagination_many_rows_repeats_header(self):
        pages, _ = self.pages(45)
        self.assertGreater(len(pages), 1)
        for pg in pages:
            texts = [p["text"] for p in pg["prims"] if p["t"] == "text"]
            if any(t.startswith("Item") for t in texts):  # every page that has rows repeats the header
                self.assertIn("Product Description", texts)
        last = [p["text"] for p in pages[-1]["prims"] if p["t"] == "text"]
        self.assertIn("Authorized Signature", last)
        self.assertNotIn("Authorized Signature", [p["text"] for p in pages[0]["prims"] if p["t"] == "text"])

    def test_nothing_outside_page(self):
        pages, _ = self.pages(45)
        for pg in pages:
            for p in pg["prims"]:
                if p["t"] in ("rect", "text", "image"):
                    self.assertLessEqual(p["y"], pg["h"]); self.assertLessEqual(p["x"] + p.get("w", 0), pg["w"] + 0.01)

    def test_pdf_export(self):
        pages, _ = self.pages(12)
        out = render_pdf(pages, self.dir / "m.pdf", self.fm)
        self.assertTrue(out.read_bytes().startswith(b"%PDF"))
        self.assertGreater(out.stat().st_size, 5000)

    def test_custom_column_and_landscape_a5(self):
        t = default_template()
        t["page"].update(size="A5", orientation="landscape")
        t["elements"] = [e for e in t["elements"] if e["type"] in ("table", "text") and e.get("pages") != "last"]
        tb = next(e for e in t["elements"] if e["type"] == "table")
        tb["columns"].append({"key": "warranty", "label": "Warranty", "width_mm": 20, "align": "center"})
        validate(t)
        doc_id, *_ = self.memo(2)
        row = self.db.conn.execute("SELECT * FROM documents WHERE id=?", (doc_id,)).fetchone()
        pages = layout(t, make_context(BIZ, row), lambda a, b, c, d: self.fm.measure(a, b, c, d))
        self.assertEqual((pages[0]["w"], pages[0]["h"]), (210, 148))

    def test_template_save_load_duplicate(self):
        tpl = Templates(self.db); tid = tpl.save("A", default_template())
        did = tpl.duplicate(tid)
        self.assertEqual(tpl.get(did)[0], "A (Copy)")
        self.assertEqual(tpl.get(tid)[1], default_template())

    def test_bad_template_rejected(self):
        with self.assertRaises(ValueError): validate({"page": {"size": "A4"}, "elements": [{"type": "bogus"}]})

    def test_reports_and_exports(self):
        self.memo(); self.memo()
        s = reports.sales_by_period(self.db, "month")
        self.assertEqual(s[0]["count"], 2)
        self.assertEqual(reports.by_payment_method(self.db)[0]["method"], "bKash")
        self.assertEqual(reports.by_product(self.db)[0]["qty"], 4)
        export.to_csv(s, self.dir / "r.csv"); export.to_xlsx(s, self.dir / "r.xlsx")
        self.assertTrue((self.dir / "r.xlsx").exists())

    def test_products_customers_stock(self):
        pid = Products(self.db).add("Mouse", "500", "300", stock="5", low_stock_alert="3", track_stock=True)
        rows = [{"name": "Mouse", "qty": "3", "price": "500", "product_id": pid}]
        issue_memo(self.db, rows)
        self.assertEqual(self.db.conn.execute("SELECT stock FROM products").fetchone()[0], "2")
        self.assertEqual(len(Products(self.db).low_stock()), 1)
        from core.calculation import CalculationError
        with self.assertRaises(CalculationError): issue_memo(self.db, [{"name": "Mouse", "qty": "9", "price": "500", "product_id": pid}])
        self.assertEqual(self.db.conn.execute("SELECT COUNT(*) FROM documents").fetchone()[0], 1)  # rolled back
        cid = Customers(self.db).add("Rahim", "017")
        issue_memo(self.db, [{"name": "X", "qty": "1", "price": "100"}], {"paid": "40"}, {"id": cid, "name": "Rahim"})
        self.assertEqual(str(Customers(self.db).summary(cid)["outstanding"]), "60.00")


if __name__ == "__main__":
    unittest.main()
