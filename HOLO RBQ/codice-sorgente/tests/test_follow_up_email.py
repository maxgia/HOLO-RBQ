from contextlib import closing
from datetime import date, datetime, timedelta, timezone
import sqlite3
from unittest import TestCase
from unittest.mock import Mock, patch
from tempfile import TemporaryDirectory
from pathlib import Path
from uuid import uuid4

from fastapi.testclient import TestClient

from app import create_app
from follow_up_email import process_one


class ScheduledEmailTests(TestCase):
    @patch.dict("os.environ", {"HOLO_TEST_RECIPIENT": "prova@example.com"})
    def test_schedule_send_cancel_and_check_residual(self):
        with TemporaryDirectory() as folder:
            path = Path(folder) / "test.sqlite3"
            with TestClient(create_app(path)) as client, closing(sqlite3.connect(path)) as db:
                db.row_factory = sqlite3.Row
                send = Mock()

                def schedule(invoice=None, remaining=None):
                    activity = client.post("/api/clients/studio-rossi/follow-ups", json={
                        "title": "Prova email", "due_date": date.today().isoformat(),
                        "invoice_number": invoice,
                    })
                    self.assertEqual(activity.status_code, 201)
                    activity_id = activity.json()["id"]
                    url = f"/api/follow-ups/{activity_id}/email"
                    payload = {
                        "recipient": "prova@example.com", "subject": "Prova", "body": "Test",
                        "send_at": (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat(),
                        "expected_remaining": remaining,
                    }
                    wrong = client.put(url, json=payload | {"recipient": "altro@example.com"})
                    self.assertEqual(wrong.status_code, 422)
                    self.assertEqual(client.put(url, json=payload).status_code, 204)
                    return activity_id, url

                def mark_due(activity_id):
                    with db:
                        db.execute("UPDATE follow_up_emails SET send_at = ? WHERE follow_up_id = ?",
                                   ("2000-01-01T00:00:00+00:00", activity_id))

                def status(activity_id):
                    rows = client.get("/api/follow-ups").json()
                    return next(item["email_status"] for item in rows if item["id"] == activity_id)

                def payment(amount):
                    response = client.post("/api/invoices/F-001/demo-payments", json={
                        "request_id": str(uuid4()), "amount": amount,
                    })
                    self.assertEqual(response.status_code, 201)

                activity_id, _ = schedule()
                self.assertFalse(process_one(db, send))
                mark_due(activity_id)
                self.assertTrue(process_one(db, send))
                self.assertEqual(status(activity_id), "sent")
                self.assertFalse(process_one(db, send))
                send.assert_called_once()

                activity_id, url = schedule()
                self.assertEqual(client.delete(url).status_code, 204)
                mark_due(activity_id)
                self.assertFalse(process_one(db, send))

                activity_id, _ = schedule("F-001", 50000)
                payment("100")
                mark_due(activity_id)
                self.assertTrue(process_one(db, send))
                self.assertEqual(status(activity_id), "review")

                activity_id, _ = schedule("F-001", 40000)
                payment("400")
                mark_due(activity_id)
                self.assertTrue(process_one(db, send))
                self.assertEqual(status(activity_id), "cancelled")
                send.assert_called_once()

                activity_id, _ = schedule()
                mark_due(activity_id)
                failing_sender = Mock(side_effect=OSError)
                self.assertTrue(process_one(db, failing_sender))
                self.assertEqual(status(activity_id), "uncertain")
                self.assertFalse(process_one(db, failing_sender))
                failing_sender.assert_called_once()
