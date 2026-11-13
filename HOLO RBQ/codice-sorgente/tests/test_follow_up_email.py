from contextlib import closing
from datetime import datetime, timezone
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
    @patch("follow_up_email.current_time")
    @patch("app.utc_now", return_value="2030-07-02T07:00:00+00:00")
    def test_schedule_send_cancel_and_check_residual(self, api_clock, clock):
        clock.return_value = datetime(2030, 7, 2, 7, tzinfo=timezone.utc)
        with TemporaryDirectory() as folder:
            path = Path(folder) / "test.sqlite3"
            with TestClient(create_app(path)) as client, closing(sqlite3.connect(path)) as db:
                db.row_factory = sqlite3.Row
                send = Mock()

                def schedule(invoice=None, remaining=None):
                    activity = client.post("/api/clients/studio-rossi/follow-ups", json={
                        "title": "Prova email", "due_date": "2030-07-02",
                        "invoice_number": invoice,
                    })
                    self.assertEqual(activity.status_code, 201)
                    activity_id = activity.json()["id"]
                    url = f"/api/follow-ups/{activity_id}/email"
                    payload = {
                        "recipient": "prova@example.com", "subject": "Prova", "body": "Test",
                        "send_at": "2030-07-02T08:00:00+00:00",
                        "expected_remaining": remaining,
                    }
                    wrong = client.put(url, json=payload | {"recipient": "altro@example.com"})
                    self.assertEqual(wrong.status_code, 422)
                    for invalid_time in ("2030-07-02T06:59:00+00:00", "2030-07-02T18:00:00+00:00",
                                         "2030-07-03T08:00:00+00:00"):
                        self.assertEqual(client.put(url, json=payload | {"send_at": invalid_time}).status_code, 422)
                    self.assertEqual(client.put(url, json=payload).status_code, 204)
                    return activity_id, url

                def mark_due(activity_id):
                    with db:
                        db.execute("UPDATE follow_up_emails SET send_at = ? WHERE follow_up_id = ?",
                                   ("2030-07-02T07:00:00+00:00", activity_id))

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

                activity_id, url = schedule("F-001", 40000)
                payment("400")
                self.assertEqual(status(activity_id), "paid_review")
                self.assertEqual(client.delete(url).status_code, 204)
                mark_due(activity_id)
                self.assertFalse(process_one(db, send))
                self.assertEqual(status(activity_id), "cancelled")
                send.assert_called_once()

                activity_id, _ = schedule()
                mark_due(activity_id)
                failing_sender = Mock(side_effect=OSError)
                self.assertTrue(process_one(db, failing_sender))
                self.assertEqual(status(activity_id), "uncertain")
                self.assertFalse(process_one(db, failing_sender))
                failing_sender.assert_called_once()

                with db:
                    db.execute("UPDATE invoices SET paid = 30000 WHERE number = 'F-001'")
                activity_id, _ = schedule("F-001", 50000)
                with db:
                    db.execute("UPDATE invoices SET paid = amount WHERE number = 'F-001'")
                self.assertTrue(process_one(db, send))
                self.assertEqual(status(activity_id), "paid_review")
                self.assertEqual(client.get("/api/follow-ups/paid-reminder-count").json(), {"count": 1})
                send.assert_called_once()

                activity_id, _ = schedule()
                clock.return_value = datetime(2030, 7, 2, 18, tzinfo=timezone.utc)
                self.assertTrue(process_one(db, send))
                self.assertEqual(status(activity_id), "review")
                send.assert_called_once()
