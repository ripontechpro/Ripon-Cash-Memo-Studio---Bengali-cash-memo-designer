"""SQLite layer: migrations, atomic numbering, audit trail, backup/restore.
Money is stored as TEXT decimal strings (never floats)."""
import json
import shutil
import sqlite3
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path

MIGRATIONS = [
    # v1
    """
    CREATE TABLE customers(
        id INTEGER PRIMARY KEY, name TEXT NOT NULL, phone TEXT, address TEXT,
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
    CREATE TABLE products(
        id INTEGER PRIMARY KEY, name TEXT NOT NULL, sku TEXT UNIQUE, barcode TEXT,
        category TEXT, brand TEXT, purchase_price TEXT NOT NULL DEFAULT '0',
        selling_price TEXT NOT NULL DEFAULT '0', unit TEXT DEFAULT 'Pcs',
        stock TEXT NOT NULL DEFAULT '0', low_stock_alert TEXT, track_stock INTEGER DEFAULT 0);
    CREATE TABLE templates(
        id INTEGER PRIMARY KEY, name TEXT NOT NULL, doc_type TEXT DEFAULT 'cash_memo',
        definition TEXT NOT NULL, updated_at TEXT NOT NULL);
    CREATE TABLE counters(doc_type TEXT PRIMARY KEY, prefix TEXT NOT NULL, next_no INTEGER NOT NULL);
    CREATE TABLE documents(
        id INTEGER PRIMARY KEY, doc_type TEXT NOT NULL, number TEXT NOT NULL UNIQUE,
        template_id INTEGER REFERENCES templates(id), customer_id INTEGER REFERENCES customers(id),
        customer_name TEXT, customer_phone TEXT, customer_address TEXT,
        issued_at TEXT NOT NULL, payment_method TEXT DEFAULT 'Cash',
        grand_total TEXT NOT NULL, paid TEXT NOT NULL, due TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'issued' CHECK(status IN ('issued','void')),
        payload TEXT NOT NULL, revision INTEGER NOT NULL DEFAULT 1);
    CREATE TABLE audit_log(
        id INTEGER PRIMARY KEY, document_id INTEGER NOT NULL REFERENCES documents(id),
        action TEXT NOT NULL, reason TEXT, snapshot TEXT, at TEXT NOT NULL);
    CREATE INDEX idx_docs_date ON documents(issued_at);
    CREATE INDEX idx_docs_customer ON documents(customer_name);
    """,
    # v2
    """
    CREATE TABLE settings(key TEXT PRIMARY KEY, value TEXT NOT NULL);
    """,
]


class Database:
    def __init__(self, path):
        self.path = str(path)
        self.conn = sqlite3.connect(self.path, isolation_level=None)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys=ON")
        self.migrate()

    def migrate(self):
        self.conn.execute("CREATE TABLE IF NOT EXISTS schema_version(v INTEGER NOT NULL)")
        current = self.conn.execute("SELECT MAX(v) FROM schema_version").fetchone()[0] or 0
        for i, script in enumerate(MIGRATIONS[current:], start=current + 1):
            with self.tx():
                for stmt in filter(None, (s.strip() for s in script.split(";"))):
                    self.conn.execute(stmt)
                self.conn.execute("INSERT INTO schema_version(v) VALUES(?)", (i,))

    @contextmanager
    def tx(self):
        self.conn.execute("BEGIN IMMEDIATE")
        try:
            yield self.conn
            self.conn.execute("COMMIT")
        except BaseException:
            self.conn.execute("ROLLBACK")
            raise

    def set_counter(self, doc_type, prefix, start=1):
        with self.tx():
            self.conn.execute("INSERT OR REPLACE INTO counters VALUES(?,?,?)", (doc_type, prefix, start))

    def _next_number(self, doc_type):
        row = self.conn.execute("SELECT prefix,next_no FROM counters WHERE doc_type=?", (doc_type,)).fetchone()
        if row:
            prefix, no = row["prefix"], row["next_no"]
        else:
            prefix = {"cash_memo": "CM", "invoice": "INV", "receipt": "RC"}.get(doc_type, "DOC")
            no = 1
            self.conn.execute("INSERT INTO counters VALUES(?,?,1)", (doc_type, prefix))
        self.conn.execute("UPDATE counters SET next_no=next_no+1 WHERE doc_type=?", (doc_type,))
        return f"{prefix}-{no:06d}"

    def issue_document(self, doc_type, totals, payload, customer=None, payment_method="Cash", template_id=None, extra=None):
        customer = customer or {}
        with self.tx():
            number = self._next_number(doc_type)
            cur = self.conn.execute(
                """INSERT INTO documents(doc_type,number,template_id,customer_id,customer_name,customer_phone,
                customer_address,issued_at,payment_method,grand_total,paid,due,payload)
                VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (doc_type, number, template_id, customer.get("id"), customer.get("name"),
                 customer.get("phone"), customer.get("address"), datetime.now().isoformat(timespec="seconds"),
                 payment_method, str(totals.grand_total), str(totals.paid), str(totals.current_due),
                 json.dumps(payload, ensure_ascii=False)))
            self._audit(cur.lastrowid, "issued")
            if extra:
                extra(self.conn)
            return cur.lastrowid, number

    def _audit(self, doc_id, action, reason=None, snapshot=None):
        self.conn.execute("INSERT INTO audit_log(document_id,action,reason,snapshot,at) VALUES(?,?,?,?,?)",
                          (doc_id, action, reason, snapshot, datetime.now().isoformat(timespec="seconds")))

    def revise_document(self, doc_id, totals, payload, reason):
        """Edit an issued document: the old version is preserved in the audit log."""
        if not reason:
            raise ValueError("a reason is required to revise an issued document")
        with self.tx():
            old = self.conn.execute("SELECT * FROM documents WHERE id=?", (doc_id,)).fetchone()
            if old["status"] == "void":
                raise ValueError("cannot revise a void document")
            self._audit(doc_id, "revised", reason, json.dumps(dict(old), ensure_ascii=False))
            self.conn.execute(
                "UPDATE documents SET grand_total=?,paid=?,due=?,payload=?,revision=revision+1 WHERE id=?",
                (str(totals.grand_total), str(totals.paid), str(totals.current_due),
                 json.dumps(payload, ensure_ascii=False), doc_id))

    def void_document(self, doc_id, reason):
        if not reason:
            raise ValueError("a reason is required to void a document")
        with self.tx():
            self.conn.execute("UPDATE documents SET status='void' WHERE id=?", (doc_id,))
            self._audit(doc_id, "void", reason)

    def delete_document(self, doc_id):
        """Permanent delete (document + its audit trail). The UI makes a backup first."""
        with self.tx():
            self.conn.execute("DELETE FROM audit_log WHERE document_id=?", (doc_id,))
            self.conn.execute("DELETE FROM documents WHERE id=?", (doc_id,))

    def clear_all_documents(self, reset_numbers=True):
        """Remove ALL sales history (e.g. test data). Optionally restart memo numbers from 1."""
        with self.tx():
            self.conn.execute("DELETE FROM audit_log")
            self.conn.execute("DELETE FROM documents")
            if reset_numbers:
                self.conn.execute("UPDATE counters SET next_no=1")

    def search_documents(self, number=None, customer=None, date_from=None, date_to=None, status=None):
        sql, args = "SELECT * FROM documents WHERE 1=1", []
        if number:
            sql += " AND number LIKE ?"; args.append(f"%{number}%")
        if customer:
            sql += " AND customer_name LIKE ?"; args.append(f"%{customer}%")
        if date_from:
            sql += " AND issued_at >= ?"; args.append(date_from)
        if date_to:
            sql += " AND issued_at <= ?"; args.append(date_to + "T23:59:59")
        if status:
            sql += " AND status=?"; args.append(status)
        return self.conn.execute(sql + " ORDER BY id DESC", args).fetchall()

    def backup(self, dest):
        dest = Path(dest)
        dest.parent.mkdir(parents=True, exist_ok=True)
        out = sqlite3.connect(str(dest))
        self.conn.backup(out)
        out.close()
        return dest

    def restore(self, src):
        chk = sqlite3.connect(str(src))
        try:
            ok = chk.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
            has = chk.execute("SELECT 1 FROM sqlite_master WHERE name='documents'").fetchone()
        except sqlite3.DatabaseError:
            ok, has = False, None
        finally:
            chk.close()
        if not ok or not has:
            raise ValueError("not a valid Cash Memo Studio backup")
        self.conn.close()
        shutil.copy2(self.path, self.path + ".pre_restore")
        shutil.copy2(str(src), self.path)
        self.__init__(self.path)

    def close(self):
        self.conn.close()
