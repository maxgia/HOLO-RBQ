from contextlib import closing
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path
import sqlite3
from typing import Literal
from uuid import UUID, uuid4

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field, field_validator

from guide import find_articles

ROOT = Path(__file__).resolve().parent
DEMO_CLIENTS = {
    "studio-rossi": "Studio Rossi",
    "martina-rossi": "Martina Rossi",
    "studio-bianchi": "Studio Bianchi",
}


class ClientInput(BaseModel):
    name: str = Field(min_length=1, max_length=140)
    email: str = Field(default="", max_length=254, pattern=r"^(?:[^@\s]+@[^@\s]+\.[^@\s]+)?$")
    phone: str = Field(default="", max_length=40)

    @field_validator("name", "email", "phone", mode="before")
    @classmethod
    def trim_fields(cls, value):
        return value.strip() if isinstance(value, str) else value


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


class PaymentInput(BaseModel):
    request_id: UUID
    amount: Decimal = Field(gt=0, le=1_000_000, decimal_places=2)


def create_app(database: Path = ROOT / "data" / "holo.sqlite3") -> FastAPI:
    database.parent.mkdir(parents=True, exist_ok=True)

    def connect():
        connection = sqlite3.connect(database)
        connection.row_factory = sqlite3.Row
        return connection

    with closing(connect()) as db, db:
        db.executescript("""
            CREATE TABLE IF NOT EXISTS clients (
                id TEXT PRIMARY KEY, name TEXT NOT NULL,
                email TEXT NOT NULL DEFAULT '', phone TEXT NOT NULL DEFAULT ''
            );
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
            CREATE TABLE IF NOT EXISTS demo_payments (
                request_id TEXT PRIMARY KEY,
                invoice_number TEXT NOT NULL REFERENCES invoices(number),
                amount INTEGER NOT NULL CHECK(amount > 0)
            );
            CREATE TABLE IF NOT EXISTS edits (
                preview_id TEXT PRIMARY KEY, draft_id INTEGER NOT NULL,
                base_version TEXT NOT NULL, confirmed INTEGER NOT NULL DEFAULT 0
            );
        """)
        db.execute("BEGIN IMMEDIATE")
        db.executemany("INSERT OR IGNORE INTO clients (id, name) VALUES (?, ?)", DEMO_CLIENTS.items())
        for table in ("drafts", "previews"):
            columns = {row["name"] for row in db.execute(f"PRAGMA table_info({table})")}
            if "client_id" not in columns:
                db.execute(f"ALTER TABLE {table} ADD COLUMN client_id TEXT REFERENCES clients(id)")
                db.executemany(
                    f"UPDATE {table} SET client_id = ? WHERE client = ?", DEMO_CLIENTS.items()
                )
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
            "client_id": row["client_id"],
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
        with closing(connect()) as db:
            return [
                dict(row) for row in db.execute("SELECT id, name FROM clients ORDER BY name, id")
                if query in row["name"].casefold()
            ]

    @application.post("/api/clients", status_code=201)
    def add_client(data: ClientInput):
        client = {"id": uuid4().hex, **data.model_dump()}
        with closing(connect()) as db, db:
            db.execute("BEGIN IMMEDIATE")
            if any(row["name"].casefold() == data.name.casefold() for row in db.execute("SELECT name FROM clients")):
                raise HTTPException(409, "Esiste già un cliente con questo nome. Usa una denominazione distinta.")
            db.execute("INSERT INTO clients VALUES (:id, :name, :email, :phone)", client)
        return client

    @application.post("/api/previews", status_code=201)
    def create_preview(quote: QuoteInput):
        amount = int(quote.amount * 100)
        discount = int(quote.discount * 100)
        total = amount - (amount * discount + 5000) // 10000
        with closing(connect()) as db, db:
            db.execute("BEGIN IMMEDIATE")
            client = db.execute("SELECT name FROM clients WHERE id = ?", (quote.client_id,)).fetchone()
            if client is None:
                raise HTTPException(404, "Cliente non trovato.")
            preview = dict(id=uuid4().hex, client=client["name"], client_id=quote.client_id,
                           subject=quote.subject, amount=amount, discount=discount, total=total)
            if quote.draft_id is not None:
                draft = find_draft(db, quote.draft_id)
                if quote.draft_version != draft["version"]:
                    raise HTTPException(409, "Bozza modificata nel frattempo. Riaprila dall’archivio.")
                db.execute(
                    "INSERT INTO edits (preview_id, draft_id, base_version) VALUES (?, ?, ?)",
                    (preview["id"], draft["id"], draft["version"]),
                )
            db.execute("""
                INSERT INTO previews (id, client, subject, amount, discount, total, client_id)
                VALUES (:id, :client, :subject, :amount, :discount, :total, :client_id)
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
                        UPDATE drafts SET client = ?, client_id = ?, subject = ?, amount = ?,
                            discount = ?, total = ?, version = ?
                        WHERE id = ? AND version = ?
                    """, (
                        preview["client"], preview["client_id"], preview["subject"], preview["amount"],
                        preview["discount"], preview["total"], preview_id,
                        edit["draft_id"], edit["base_version"],
                    ))
                    if changed.rowcount != 1:
                        raise HTTPException(409, "Bozza modificata nel frattempo. Riaprila dall’archivio.")
                    db.execute("UPDATE edits SET confirmed = 1 WHERE preview_id = ?", (preview_id,))
                    db.execute("DELETE FROM previews WHERE id = ?", (preview_id,))
                return draft_data(db.execute("SELECT * FROM drafts WHERE id = ?", (edit["draft_id"],)).fetchone())

            db.execute("""
                INSERT INTO drafts (preview_id, client, subject, amount, discount, total, client_id)
                SELECT id, client, subject, amount, discount, total, client_id
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

    def list_invoices(db, query="", status="all", client_id=None):
        today = date.today().isoformat()
        filters = {
            "all": lambda invoice: True,
            "open": lambda invoice: invoice["remaining"] > 0,
            "overdue": lambda invoice: invoice["status"] == "Scaduta",
            "paid": lambda invoice: invoice["remaining"] == 0,
        }
        results = []
        for row in db.execute("SELECT i.*, c.name AS client FROM invoices i JOIN clients c ON c.id = i.client_id ORDER BY i.due_date, i.number"):
            if client_id is not None and row["client_id"] != client_id:
                continue
            client = row["client"]
            if query not in client.casefold() and query not in row["number"].casefold():
                continue
            remaining = row["amount"] - row["paid"]
            invoice_status = "Saldata" if not remaining else (
                "Scaduta" if row["due_date"] < today else "Da incassare"
            )
            invoice = dict(row) | {"client": client, "remaining": remaining, "status": invoice_status}
            if filters[status](invoice):
                results.append(invoice)
        return results

    @application.get("/api/invoices")
    def invoices(q: str = "", status: Literal["all", "open", "overdue", "paid"] = "all"):
        with closing(connect()) as db:
            results = list_invoices(db, q.strip().casefold(), status)
        return {"invoices": results, "total_remaining": sum(row["remaining"] for row in results)}

    @application.get("/api/clients/{client_id}")
    def client_detail(client_id: str):
        with closing(connect()) as db, db:
            db.execute("BEGIN")
            client = db.execute("SELECT * FROM clients WHERE id = ?", (client_id,)).fetchone()
            if client is None:
                raise HTTPException(404, "Cliente non trovato.")
            client_invoices = list_invoices(db, client_id=client_id)
            client_drafts = [
                draft_data(row) for row in db.execute(
                    "SELECT * FROM drafts WHERE client_id = ? ORDER BY id", (client_id,)
                )
            ]
        return {
            **dict(client), "drafts": client_drafts, "invoices": client_invoices,
            "total_remaining": sum(row["remaining"] for row in client_invoices),
        }

    @application.post("/api/invoices/{number}/demo-payments", status_code=201)
    def register_demo_payment(number: str, payment: PaymentInput):
        amount = int(payment.amount * 100)
        request_id = str(payment.request_id)
        with closing(connect()) as db, db:
            db.execute("BEGIN IMMEDIATE")
            invoice = db.execute("SELECT amount, paid FROM invoices WHERE number = ?", (number,)).fetchone()
            if invoice is None:
                raise HTTPException(404, "Fattura non trovata.")
            existing = db.execute(
                "SELECT invoice_number, amount FROM demo_payments WHERE request_id = ?", (request_id,)
            ).fetchone()
            if existing is not None:
                if (existing["invoice_number"], existing["amount"]) != (number, amount):
                    raise HTTPException(409, "Identificativo già usato per un altro incasso.")
            else:
                if amount > invoice["amount"] - invoice["paid"]:
                    raise HTTPException(409, "L’incasso supera il residuo della fattura.")
                db.execute("INSERT INTO demo_payments VALUES (?, ?, ?)", (request_id, number, amount))
                db.execute("UPDATE invoices SET paid = paid + ? WHERE number = ?", (amount, number))
        return {"request_id": request_id, "invoice_number": number, "amount": amount}

    @application.get("/api/guide")
    def guide(q: str = ""):
        return {"source": "Guida dimostrativa HOLO RBQ · v1", "articles": find_articles(q)}

    return application
