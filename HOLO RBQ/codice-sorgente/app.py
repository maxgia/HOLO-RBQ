from contextlib import closing
from datetime import date, timedelta, timezone
import os
from decimal import Decimal
from pathlib import Path
import sqlite3
from typing import Literal
from uuid import UUID, uuid4

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field, field_validator

from customer_assistant import CustomerQuestion, answer_customer_question
from guide import find_articles
from follow_up_email import EMAIL_SCHEMA, ScheduledEmail, utc_now

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


class FollowUpInput(BaseModel):
    title: str = Field(min_length=1, max_length=140)
    due_date: date
    invoice_number: str | None = Field(default=None, max_length=40)
    draft_id: str | None = Field(default=None, max_length=40)

    @field_validator("title", mode="before")
    @classmethod
    def trim_title(cls, value):
        return value.strip() if isinstance(value, str) else value


class FollowUpUpdate(BaseModel):
    due_date: date | None = None
    completed: Literal[True] | None = None


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
            CREATE TABLE IF NOT EXISTS follow_ups (
                id TEXT PRIMARY KEY, client_id TEXT NOT NULL REFERENCES clients(id),
                title TEXT NOT NULL, due_date TEXT NOT NULL, completed INTEGER NOT NULL DEFAULT 0,
                invoice_number TEXT REFERENCES invoices(number), draft_id TEXT,
                CHECK (invoice_number IS NULL OR draft_id IS NULL)
            );
            CREATE TABLE IF NOT EXISTS edits (
                preview_id TEXT PRIMARY KEY, draft_id INTEGER NOT NULL,
                base_version TEXT NOT NULL, confirmed INTEGER NOT NULL DEFAULT 0
            );
        """)
        db.executescript(EMAIL_SCHEMA)
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

    @application.get("/api/follow-ups")
    def list_follow_ups(
        status: Literal["all", "today", "overdue", "upcoming", "completed"] = "all",
        client_id: str | None = None,
    ):
        today = date.today().isoformat()
        filters = {
            "all": "1 = 1",
            "today": "f.completed = 0 AND f.due_date = :today",
            "overdue": "f.completed = 0 AND f.due_date < :today",
            "upcoming": "f.completed = 0 AND f.due_date > :today",
            "completed": "f.completed = 1",
        }
        with closing(connect()) as db:
            rows = db.execute(
                "SELECT f.*, c.name AS client, c.email AS client_email, "
                "e.status AS email_status, e.detail AS email_detail, e.recipient AS email_recipient, "
                "e.subject AS email_subject, e.body AS email_body, e.send_at AS email_send_at, e.sent_at AS email_sent_at, "
                "i.amount - i.paid AS remaining, i.due_date AS invoice_due_date "
                "FROM follow_ups f JOIN clients c ON c.id = f.client_id "
                "LEFT JOIN follow_up_emails e ON e.follow_up_id = f.id "
                "LEFT JOIN invoices i ON i.number = f.invoice_number "
                "WHERE (:client_id IS NULL OR f.client_id = :client_id) AND " + filters[status]
                + " ORDER BY f.due_date, f.title, f.id",
                {"client_id": client_id, "today": today},
            )
            return [dict(row) | {"test_recipient": os.getenv("HOLO_TEST_RECIPIENT", "").strip()} for row in rows]

    @application.post("/api/clients/{client_id}/follow-ups", status_code=201)
    def create_follow_up(client_id: str, data: FollowUpInput):
        with closing(connect()) as db, db:
            db.execute("BEGIN IMMEDIATE")
            if not db.execute("SELECT 1 FROM clients WHERE id = ?", (client_id,)).fetchone():
                raise HTTPException(404, "Cliente non trovato.")
            if data.invoice_number is not None and data.draft_id is not None:
                raise HTTPException(422, "Seleziona un solo documento.")
            if data.invoice_number is not None and not db.execute(
                "SELECT 1 FROM invoices WHERE number = ? AND client_id = ?", (data.invoice_number, client_id)
            ).fetchone():
                raise HTTPException(404, "Fattura non presente nella scheda cliente.")
            record = data.model_dump(mode="json") | {"id": uuid4().hex, "client_id": client_id}
            if data.draft_id is not None:
                draft = find_draft(db, data.draft_id)
                if draft["client_id"] != client_id:
                    raise HTTPException(404, "Bozza non presente nella scheda cliente.")
                record["draft_id"] = draft_data(draft)["id"]
            db.execute(
                "INSERT INTO follow_ups (id, client_id, title, due_date, invoice_number, draft_id) "
                "VALUES (:id, :client_id, :title, :due_date, :invoice_number, :draft_id)",
                record,
            )
        return record | {"completed": 0}

    @application.patch("/api/follow-ups/{follow_up_id}", status_code=204)
    def update_follow_up(follow_up_id: str, data: FollowUpUpdate):
        if (data.due_date is None) == (data.completed is None):
            raise HTTPException(422, "Scegli se riprogrammare o completare l’attività.")
        with closing(connect()) as db, db:
            changed = db.execute(
                "UPDATE follow_ups SET due_date = COALESCE(?, due_date), completed = COALESCE(?, completed) "
                "WHERE id = ? AND completed = 0",
                (data.due_date.isoformat() if data.due_date else None, data.completed, follow_up_id),
            )
            if changed.rowcount:
                status = "cancelled" if data.completed else "review"
                detail = "Attività completata." if data.completed else "Data attività cambiata. Conferma un nuovo orario."
                db.execute(
                    "UPDATE follow_up_emails SET status = ?, detail = ? "
                    "WHERE follow_up_id = ? AND status = 'scheduled'", (status, detail, follow_up_id)
                )
            if not changed.rowcount:
                row = db.execute("SELECT * FROM follow_ups WHERE id = ?", (follow_up_id,)).fetchone()
                if row is None:
                    raise HTTPException(404, "Attività non trovata.")
                if not data.completed:
                    raise HTTPException(409, "L’attività è già completata.")

    @application.put("/api/follow-ups/{follow_up_id}/email", status_code=204)
    def schedule_follow_up_email(follow_up_id: str, data: ScheduledEmail):
        allowed = os.getenv("HOLO_TEST_RECIPIENT", "").strip()
        if not allowed:
            raise HTTPException(503, "Configura HOLO_TEST_RECIPIENT per abilitare la prova.")
        if data.recipient.casefold() != allowed.casefold():
            raise HTTPException(422, "È consentito solo il destinatario di prova configurato.")
        send_at = data.send_at.astimezone(timezone.utc).isoformat()
        if send_at <= utc_now() or not data.subject.strip() or not data.body.strip():
            raise HTTPException(422, "Inserisci oggetto, testo e un orario futuro.")
        with closing(connect()) as db, db:
            db.execute("BEGIN IMMEDIATE")
            item = db.execute(
                "SELECT f.completed, i.amount - i.paid AS remaining, e.status "
                "FROM follow_ups f LEFT JOIN invoices i ON i.number = f.invoice_number "
                "LEFT JOIN follow_up_emails e ON e.follow_up_id = f.id WHERE f.id = ?", (follow_up_id,)
            ).fetchone()
            if item is None:
                raise HTTPException(404, "Attività non trovata.")
            if item["completed"] or item["remaining"] == 0 or item["status"] in ("sending", "sent", "uncertain"):
                raise HTTPException(409, "L’attività o l’email non è più programmabile.")
            if data.expected_remaining != item["remaining"]:
                raise HTTPException(409, "Il residuo è cambiato. Ricarica e rivedi la bozza.")
            db.execute("""
                INSERT INTO follow_up_emails
                    (follow_up_id, recipient, subject, body, send_at, expected_remaining)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(follow_up_id) DO UPDATE SET recipient = excluded.recipient,
                    subject = excluded.subject, body = excluded.body, send_at = excluded.send_at,
                    expected_remaining = excluded.expected_remaining, status = 'scheduled', detail = '', sent_at = NULL
            """, (follow_up_id, allowed, data.subject, data.body, send_at, data.expected_remaining))

    @application.delete("/api/follow-ups/{follow_up_id}/email", status_code=204)
    def cancel_follow_up_email(follow_up_id: str):
        with closing(connect()) as db, db:
            result = db.execute(
                "UPDATE follow_up_emails SET status = 'cancelled', detail = '' "
                "WHERE follow_up_id = ? AND status IN ('scheduled', 'review', 'cancelled')", (follow_up_id,)
            )
            if not result.rowcount:
                raise HTTPException(409, "Non c’è un invio annullabile per questa attività.")

    @application.post("/api/clients/{client_id}/questions")
    def ask_customer_question(client_id: str, data: CustomerQuestion):
        return answer_customer_question(client_detail(client_id), data.question)

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
