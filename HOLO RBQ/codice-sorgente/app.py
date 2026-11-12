from contextlib import closing
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path
import sqlite3
from typing import Literal
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field, field_validator

from guide import find_articles

ROOT = Path(__file__).resolve().parent
CLIENTS = {
    "studio-rossi": "Studio Rossi",
    "martina-rossi": "Martina Rossi",
    "studio-bianchi": "Studio Bianchi",
}


class QuoteInput(BaseModel):
    draft_id: str | None = None
    draft_version: str | None = None
    client_id: str
    subject: str = Field(min_length=1, max_length=140)
    amount: Decimal = Field(ge=Decimal("0.01"), le=1_000_000, decimal_places=2)
    discount: Decimal = Field(ge=0, le=100, decimal_places=2)

    @field_validator("subject", mode="before")
    @classmethod
    def trim_subject(cls, value):
        return value.strip() if isinstance(value, str) else value


def create_app(database: Path = ROOT / "data" / "holo.sqlite3") -> FastAPI:
    database.parent.mkdir(parents=True, exist_ok=True)

    def connect():
        connection = sqlite3.connect(database)
        connection.row_factory = sqlite3.Row
        return connection

    with closing(connect()) as db, db:
        db.executescript("""
            CREATE TABLE IF NOT EXISTS previews (
                id TEXT PRIMARY KEY, client TEXT NOT NULL, subject TEXT NOT NULL,
                amount INTEGER NOT NULL, discount INTEGER NOT NULL, total INTEGER NOT NULL
            );
            CREATE TABLE IF NOT EXISTS drafts (
                id INTEGER PRIMARY KEY, preview_id TEXT NOT NULL UNIQUE,
                client TEXT NOT NULL, subject TEXT NOT NULL,
                amount INTEGER NOT NULL, discount INTEGER NOT NULL, total INTEGER NOT NULL
            );
            CREATE TABLE IF NOT EXISTS invoices (
                number TEXT PRIMARY KEY, client_id TEXT NOT NULL,
                due_date TEXT NOT NULL, amount INTEGER NOT NULL, paid INTEGER NOT NULL
            );
            CREATE TABLE IF NOT EXISTS edits (
                preview_id TEXT PRIMARY KEY, draft_id INTEGER NOT NULL,
                base_version TEXT NOT NULL, confirmed INTEGER NOT NULL DEFAULT 0
            );
        """)
        db.execute("BEGIN IMMEDIATE")
        today = date.today()
        demo_invoices = (
            ("F-001", "studio-rossi", -12, 80000, 30000),
            ("F-002", "studio-rossi", 15, 45000, 0),
            ("F-003", "martina-rossi", 7, 25000, 0),
            ("F-004", "studio-rossi", -20, 60000, 60000),
            ("F-005", "studio-bianchi", 21, 35000, 0),
        )
        db.executemany(
            "INSERT OR IGNORE INTO invoices VALUES (?, ?, ?, ?, ?)",
            [(number, client, (today + timedelta(days=days)).isoformat(), amount, paid)
             for number, client, days, amount, paid in demo_invoices],
        )
        columns = {row["name"] for row in db.execute("PRAGMA table_info(drafts)")}
        if "version" not in columns:
            db.execute("ALTER TABLE drafts ADD COLUMN version TEXT NOT NULL DEFAULT ''")

    application = FastAPI(title="HOLO RBQ · Preventivi locali")

    def draft_data(row):
        return {
            "id": f"DEMO-{row['id']:03d}",
            "client_id": next((key for key, name in CLIENTS.items() if name == row["client"]), None),
            "version": row["version"],
            **{key: row[key] for key in ("client", "subject", "amount", "discount", "total")},
        }

    def find_draft(db, code):
        row = db.execute(
            "SELECT * FROM drafts WHERE printf('DEMO-%03d', id) = ?", (code.upper(),)
        ).fetchone()
        if row is None:
            raise HTTPException(404, "Bozza non trovata.")
        return row

    @application.get("/", include_in_schema=False)
    def home():
        return FileResponse(ROOT / "index.html")

    @application.get("/api/clients")
    def clients(q: str = ""):
        query = q.strip().casefold()
        return [
            {"id": key, "name": name}
            for key, name in CLIENTS.items()
            if query in name.casefold()
        ]

    @application.post("/api/previews", status_code=201)
    def create_preview(quote: QuoteInput):
        client = CLIENTS.get(quote.client_id)
        if client is None:
            raise HTTPException(404, "Cliente non trovato.")
        amount = int(quote.amount * 100)
        discount = int(quote.discount * 100)
        total = amount - (amount * discount + 5000) // 10000
        preview = dict(id=uuid4().hex, client=client, subject=quote.subject,
                       amount=amount, discount=discount, total=total)
        with closing(connect()) as db, db:
            db.execute("BEGIN IMMEDIATE")
            if quote.draft_id is not None:
                draft = find_draft(db, quote.draft_id)
                if quote.draft_version != draft["version"]:
                    raise HTTPException(409, "Bozza modificata nel frattempo. Riaprila dall’archivio.")
                db.execute(
                    "INSERT INTO edits (preview_id, draft_id, base_version) VALUES (?, ?, ?)",
                    (preview["id"], draft["id"], draft["version"]),
                )
            db.execute("""
                INSERT INTO previews (id, client, subject, amount, discount, total)
                VALUES (:id, :client, :subject, :amount, :discount, :total)
            """, preview)
        return preview

    @application.delete("/api/previews/{preview_id}", status_code=204)
    def cancel_preview(preview_id: str):
        with closing(connect()) as db, db:
            db.execute("DELETE FROM previews WHERE id = ?", (preview_id,))
            db.execute("DELETE FROM edits WHERE preview_id = ? AND confirmed = 0", (preview_id,))

    @application.put("/api/drafts/{preview_id}")
    def confirm_preview(preview_id: str):
        with closing(connect()) as db, db:
            db.execute("BEGIN IMMEDIATE")
            edit = db.execute("SELECT * FROM edits WHERE preview_id = ?", (preview_id,)).fetchone()
            if edit is not None:
                if not edit["confirmed"]:
                    preview = db.execute("SELECT * FROM previews WHERE id = ?", (preview_id,)).fetchone()
                    if preview is None:
                        raise HTTPException(404, "Anteprima annullata o non disponibile.")
                    changed = db.execute("""
                        UPDATE drafts SET client = ?, subject = ?, amount = ?,
                            discount = ?, total = ?, version = ?
                        WHERE id = ? AND version = ?
                    """, (
                        preview["client"], preview["subject"], preview["amount"],
                        preview["discount"], preview["total"], preview_id,
                        edit["draft_id"], edit["base_version"],
                    ))
                    if changed.rowcount != 1:
                        raise HTTPException(409, "Bozza modificata nel frattempo. Riaprila dall’archivio.")
                    db.execute("UPDATE edits SET confirmed = 1 WHERE preview_id = ?", (preview_id,))
                    db.execute("DELETE FROM previews WHERE id = ?", (preview_id,))
                return draft_data(db.execute("SELECT * FROM drafts WHERE id = ?", (edit["draft_id"],)).fetchone())

            db.execute("""
                INSERT INTO drafts (preview_id, client, subject, amount, discount, total)
                SELECT id, client, subject, amount, discount, total
                FROM previews WHERE id = ?
                ON CONFLICT(preview_id) DO NOTHING
            """, (preview_id,))
            draft = db.execute("SELECT * FROM drafts WHERE preview_id = ?", (preview_id,)).fetchone()
            if draft is None:
                raise HTTPException(404, "Anteprima annullata o non disponibile.")
            db.execute("DELETE FROM previews WHERE id = ?", (preview_id,))
            return draft_data(draft)

    @application.get("/api/drafts")
    def drafts(q: str = ""):
        query = q.strip().casefold()
        with closing(connect()) as db:
            records = [draft_data(row) for row in db.execute("SELECT * FROM drafts ORDER BY id")]
        return [
            draft for draft in records
            if any(query in draft[key].casefold() for key in ("id", "client", "subject"))
        ]

    @application.get("/api/drafts/{draft_id}")
    def draft_detail(draft_id: str):
        with closing(connect()) as db:
            return draft_data(find_draft(db, draft_id))

    @application.get("/api/invoices")
    def invoices(q: str = "", status: Literal["all", "open", "overdue", "paid"] = "all"):
        query = q.strip().casefold()
        today = date.today().isoformat()
        filters = {
            "all": lambda invoice: True,
            "open": lambda invoice: invoice["remaining"] > 0,
            "overdue": lambda invoice: invoice["status"] == "Scaduta",
            "paid": lambda invoice: invoice["remaining"] == 0,
        }
        results = []
        with closing(connect()) as db:
            for row in db.execute("SELECT * FROM invoices ORDER BY due_date, number"):
                client = CLIENTS[row["client_id"]]
                if query not in client.casefold() and query not in row["number"].casefold():
                    continue
                remaining = row["amount"] - row["paid"]
                invoice_status = "Saldata" if not remaining else (
                    "Scaduta" if row["due_date"] < today else "Da incassare"
                )
                invoice = dict(row) | {"client": client, "remaining": remaining, "status": invoice_status}
                if filters[status](invoice):
                    results.append(invoice)
        return {"invoices": results, "total_remaining": sum(row["remaining"] for row in results)}

    @application.get("/api/guide")
    def guide(q: str = ""):
        return {"source": "Guida dimostrativa HOLO RBQ · v1", "articles": find_articles(q)}

    return application
