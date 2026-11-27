import tempfile, unittest
from pathlib import Path
from core.calculation import LineItem, calculate
from db.database import Database


class DbTests(unittest.TestCase):
    def setUp(self):
        self.dir = Path(tempfile.mkdtemp())
        self.db = Database(self.dir / "t.db")
        self.t = calculate([LineItem("2", "250")])

    def issue(self):
        return self.db.issue_document("cash_memo", self.t, {"items": []}, {"name": "রিপন"})

    def test_sequential_unique_numbers(self):
        _, a = self.issue(); _, b = self.issue()
        self.assertEqual((a, b), ("CM-000001", "CM-000002"))

    def test_bengali_roundtrip_and_search(self):
        self.issue()
        self.assertEqual(len(self.db.search_documents(customer="রিপ")), 1)

    def test_void_requires_reason_and_audits(self):
        i, _ = self.issue()
        with self.assertRaises(ValueError): self.db.void_document(i, "")
        self.db.void_document(i, "wrong entry")
        acts = [r["action"] for r in self.db.conn.execute("SELECT action FROM audit_log")]
        self.assertEqual(acts, ["issued", "void"])

    def test_revise_keeps_history(self):
        i, _ = self.issue()
        self.db.revise_document(i, calculate([LineItem("1", "10")]), {"items": [1]}, "price fix")
        row = self.db.conn.execute("SELECT revision,grand_total FROM documents").fetchone()
        self.assertEqual((row[0], row[1]), (2, "10.00"))
        self.assertEqual(self.db.conn.execute("SELECT COUNT(*) FROM audit_log WHERE action='revised'").fetchone()[0], 1)

    def test_backup_restore(self):
        self.issue()
        b = self.db.backup(self.dir / "bk" / "b.db")
        self.issue()
        self.db.restore(b)
        self.assertEqual(len(self.db.search_documents()), 1)
        bad = self.dir / "bad.db"; bad.write_text("nope")
        with self.assertRaises(Exception): self.db.restore(bad)

    def test_rollback_on_failure(self):
        try:
            with self.db.tx():
                self.db.conn.execute("INSERT INTO customers(name) VALUES('x')")
                raise RuntimeError
        except RuntimeError: pass
        self.assertEqual(self.db.conn.execute("SELECT COUNT(*) FROM customers").fetchone()[0], 0)


if __name__ == "__main__":
    unittest.main()


class DeleteTests(unittest.TestCase):
    def test_delete_and_clear(self):
        db = Database(Path(tempfile.mkdtemp()) / "d.db"); t = calculate([LineItem("1", "10")])
        a, _ = db.issue_document("cash_memo", t, {"items": []}); db.issue_document("cash_memo", t, {"items": []})
        db.delete_document(a)
        self.assertEqual(len(db.search_documents()), 1)
        self.assertEqual(db.conn.execute("SELECT COUNT(*) FROM audit_log WHERE document_id=?", (a,)).fetchone()[0], 0)
        db.clear_all_documents()
        self.assertEqual(len(db.search_documents()), 0)
        _, n = db.issue_document("cash_memo", t, {"items": []}); self.assertEqual(n, "CM-000001")
