import argparse
from contextlib import closing
from datetime import datetime, timezone
from email.message import EmailMessage
import os
from pathlib import Path
import smtplib
import sqlite3
import ssl
import time
from zoneinfo import ZoneInfo

from pydantic import AwareDatetime, BaseModel, Field


EMAIL_SCHEMA = """
CREATE TABLE IF NOT EXISTS follow_up_emails (
    follow_up_id TEXT PRIMARY KEY REFERENCES follow_ups(id),
    recipient TEXT NOT NULL,
    subject TEXT NOT NULL,
    body TEXT NOT NULL,
    send_at TEXT NOT NULL,
    expected_remaining INTEGER,
    status TEXT NOT NULL DEFAULT 'scheduled',
    detail TEXT NOT NULL DEFAULT '',
    sent_at TEXT
);
"""


class ScheduledEmail(BaseModel):
    recipient: str = Field(min_length=3, max_length=254, pattern=r"^[^@\s,;<>]+@[^@\s,;<>]+\.[^@\s,;<>]+$")
    subject: str = Field(min_length=1, max_length=180, pattern=r"^[^\r\n]+$")
    body: str = Field(min_length=1, max_length=5000)
    send_at: AwareDatetime
    expected_remaining: int | None = None


def current_time():
    return datetime.now(timezone.utc)


def utc_now():
    return current_time().isoformat()


def in_send_window(value, day):
    local = value.astimezone(ZoneInfo("Europe/Rome"))
    return local.date().isoformat() == day and 9 <= local.hour < 20


def flag_paid_follow_up_emails(db):
    changed = db.execute("""
        UPDATE follow_up_emails
        SET status = 'paid_review', detail = 'Fattura saldata. Conferma l’annullamento del sollecito.'
        WHERE status IN ('scheduled', 'review') AND follow_up_id IN (
            SELECT f.id FROM follow_ups f
            JOIN invoices i ON i.number = f.invoice_number WHERE i.paid >= i.amount
        )
    """)
    return changed.rowcount


class SendWindowClosed(Exception):
    pass


def send_smtp(row):
    message = EmailMessage()
    message["From"] = os.environ["HOLO_SMTP_FROM"]
    message["To"] = row["recipient"]
    message["Subject"] = row["subject"]
    message.set_content(row["body"])
    with smtplib.SMTP_SSL(
        os.environ["HOLO_SMTP_HOST"], int(os.getenv("HOLO_SMTP_PORT", "465")),
        timeout=20, context=ssl.create_default_context()
    ) as smtp:
        smtp.login(os.environ["HOLO_SMTP_USER"], os.environ["HOLO_SMTP_PASSWORD"])
        if not in_send_window(current_time(), row["planned_day"]):
            raise SendWindowClosed
        smtp.send_message(message)


def process_one(db, send=send_smtp):
    with db:
        db.execute("BEGIN IMMEDIATE")
        flagged = flag_paid_follow_up_emails(db)
        now = current_time()
        row = db.execute("""
            SELECT e.*, f.completed, f.due_date AS planned_day, i.amount - i.paid AS remaining
            FROM follow_up_emails e
            JOIN follow_ups f ON f.id = e.follow_up_id
            LEFT JOIN invoices i ON i.number = f.invoice_number
            WHERE e.status = 'scheduled' AND e.send_at <= ?
            ORDER BY e.send_at, e.follow_up_id LIMIT 1
        """, (now.isoformat(),)).fetchone()
        if row is None:
            return bool(flagged)
        status, detail = "sending", ""
        if row["completed"]:
            status, detail = "cancelled", "Attività completata."
        elif not in_send_window(now, row["planned_day"]) or not in_send_window(
            datetime.fromisoformat(row["send_at"]), row["planned_day"]
        ):
            status, detail = "review", "Finestra di invio superata o non valida. Riprogramma il sollecito."
        elif row["recipient"].casefold() != os.getenv("HOLO_TEST_RECIPIENT", "").strip().casefold():
            status, detail = "review", "Destinatario diverso dalla casella di prova configurata."
        elif row["expected_remaining"] != row["remaining"]:
            status, detail = "review", "Residuo cambiato. Rivedi testo e importo."
        db.execute("UPDATE follow_up_emails SET status = ?, detail = ? WHERE follow_up_id = ?",
                   (status, detail, row["follow_up_id"]))

    if status != "sending":
        return True
    if not in_send_window(current_time(), row["planned_day"]):
        with db:
            db.execute(
                "UPDATE follow_up_emails SET status = 'review', detail = ? WHERE follow_up_id = ?",
                ("Finestra di invio superata. Riprogramma il sollecito.", row["follow_up_id"]),
            )
        return True
    try:
        send(row)
    except SendWindowClosed:
        status, detail = "review", "Finestra di invio superata. Riprogramma il sollecito."
    except (OSError, smtplib.SMTPException, ValueError):
        status, detail = "uncertain", "Invio SMTP incerto o fallito. Verifica la casella e il log del provider."
    else:
        status, detail = "sent", ""
    with db:
        db.execute(
            "UPDATE follow_up_emails SET status = ?, detail = ?, sent_at = ? WHERE follow_up_id = ?",
            (status, detail, utc_now() if status == "sent" else None, row["follow_up_id"]),
        )
    return True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--database", type=Path, default=Path(__file__).resolve().parent / "data" / "holo.sqlite3")
    parser.add_argument("--once", action="store_true")
    args = parser.parse_args()
    names = ("HOLO_TEST_RECIPIENT", "HOLO_SMTP_HOST", "HOLO_SMTP_FROM", "HOLO_SMTP_USER", "HOLO_SMTP_PASSWORD")
    missing = [name for name in names if not os.getenv(name)]
    if missing:
        parser.error("Variabili mancanti: " + ", ".join(missing))
    if not args.database.is_file():
        parser.error("Archivio assente. Avvia prima HOLO RBQ.")
    try:
        with closing(sqlite3.connect(args.database)) as db:
            db.row_factory = sqlite3.Row
            print("Worker email di prova attivo.", flush=True)
            while True:
                while process_one(db):
                    pass
                if args.once:
                    return
                time.sleep(10)
    except KeyboardInterrupt:
        print("Worker fermato.")


if __name__ == "__main__":
    main()
