import sqlite3
import unittest
from unittest.mock import patch
from uuid import uuid4
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from tempfile import TemporaryDirectory

from fastapi.testclient import TestClient

from app import create_app
from customer_assistant import QuestionIntent


class MVPTests(unittest.TestCase):
    def setUp(self):
        directory = TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.db = Path(directory.name) / "test.sqlite3"
        client = TestClient(create_app(self.db))
        self.client = client.__enter__()
        self.addCleanup(client.__exit__, None, None, None)

    def preview(self, **overrides):
        data = dict(client_id="studio-rossi", subject="Consulenza", amount="800", discount="10")
        response = self.client.post("/api/previews", json=data | overrides)
        self.assertEqual(response.status_code, 201, response.text)
        return response.json()

    def confirm(self, preview):
        return self.client.put("/api/drafts/" + preview["id"])

    @patch("customer_assistant.classify_question")
    def test_customer_assistant_scopes_answers_and_reads_latest_payments(self, classify):
        classify.return_value = QuestionIntent(action="reminder", invoice_number="F-001", tone="cordiale")
        url = "/api/clients/studio-rossi/questions"
        question = {"question": "Scrivi un sollecito cordiale per F-001"}
        self.assertIn("500,00 €", self.client.post(url, json=question).json()["draft"])
        payment = self.client.post(
            "/api/invoices/F-001/demo-payments", json={"request_id": str(uuid4()), "amount": "100"}
        )
        self.assertEqual(payment.status_code, 201)
        self.assertIn("400,00 €", self.client.post(url, json=question).json()["draft"])
        other = self.client.post("/api/clients/martina-rossi/questions", json=question).json()
        self.assertIn("non è presente", other["answer"])
        self.assertNotIn("draft", other)

        client = self.client.post("/api/clients", json={"name": "Studio Verdi"}).json()
        classify.reset_mock()
        empty = self.client.post(f"/api/clients/{client['id']}/questions", json=question)
        self.assertIn("Nessuno storico", empty.json()["answer"])
        classify.assert_not_called()

    def test_home_and_client_search(self):
        self.assertIn("Fatture e scadenze", self.client.get("/").text)
        clients = self.client.get("/api/clients", params={"q": "ROSSI"}).json()
        self.assertEqual(len(clients), 2)

    def test_validation_and_cancel(self):
        base = dict(client_id="studio-rossi", subject="Consulenza", amount="800", discount="10")
        for override, expected in [
            ({"client_id": "ignoto"}, 404), ({"amount": "0.001"}, 422),
            ({"discount": "101"}, 422), ({"subject": " "}, 422),
        ]:
            with self.subTest(override=override):
                self.assertEqual(self.client.post("/api/previews", json=base | override).status_code, expected)
        preview = self.preview()
        self.assertEqual(preview["total"], 72000)
        self.assertEqual(self.client.delete("/api/previews/" + preview["id"]).status_code, 204)
        self.assertEqual(self.confirm(preview).status_code, 404)
        self.assertEqual(self.client.get("/api/drafts").json(), [])

    def test_concurrent_confirmation_and_restart(self):
        preview = self.preview()
        with ThreadPoolExecutor(max_workers=8) as pool:
            responses = list(pool.map(self.confirm, [preview] * 16))
        self.assertTrue(all(r.status_code == 200 for r in responses))
        self.assertEqual({r.json()["id"] for r in responses}, {"DEMO-001"})
        with TestClient(create_app(self.db)) as restarted:
            self.assertEqual(len(restarted.get("/api/drafts").json()), 1)
            self.assertEqual(restarted.put("/api/drafts/" + preview["id"]).json()["total"], 72000)

    def test_edit_and_stale_preview(self):
        draft = self.confirm(self.preview()).json()
        options = dict(draft_id=draft["id"], draft_version=draft["version"])
        cancelled = self.preview(discount="15", **options)
        self.client.delete("/api/previews/" + cancelled["id"])
        self.assertEqual(self.confirm(cancelled).status_code, 404)
        edit = self.preview(discount="20", **options)
        stale = self.preview(discount="30", **options)
        for _ in range(2):
            updated = self.confirm(edit).json()
            self.assertEqual((updated["id"], updated["total"]), (draft["id"], 64000))
        self.assertEqual(self.confirm(stale).status_code, 409)
        with TestClient(create_app(self.db)) as restarted:
            results = restarted.get("/api/drafts", params={"q": "Rossi"}).json()
            self.assertEqual([(item["id"], item["total"]) for item in results], [(draft["id"], 64000)])
            self.assertEqual(restarted.get("/api/drafts/" + draft["id"]).json()["total"], 64000)

    def test_legacy_database(self):
        legacy = self.db.with_name("legacy.sqlite3")
        with sqlite3.connect(legacy) as connection:
            connection.executescript("""
                CREATE TABLE drafts (id INTEGER PRIMARY KEY, preview_id TEXT NOT NULL UNIQUE,
                client TEXT NOT NULL, subject TEXT NOT NULL, amount INTEGER NOT NULL,
                discount INTEGER NOT NULL, total INTEGER NOT NULL);
                INSERT INTO drafts VALUES (1,'old','Studio Rossi','Consulenza',80000,1000,72000);
            """)
        with TestClient(create_app(legacy)) as migrated:
            row = migrated.get("/api/drafts/DEMO-001").json()
            self.assertEqual((row["total"], row["version"]), (72000, ""))

    def test_invoices(self):
        for query, status, count, total in [
            ("Rossi", "open", 3, 120000), ("Studio Rossi", "open", 2, 95000),
            ("Rossi", "overdue", 1, 50000), ("Rossi", "paid", 1, 0),
            ("Verdi", "all", 0, 0),
        ]:
            with self.subTest(query=query, status=status):
                result = self.client.get("/api/invoices", params={"q": query, "status": status}).json()
                self.assertEqual((len(result["invoices"]), result["total_remaining"]), (count, total))
        self.assertEqual(self.client.get("/api/invoices?status=invalid").status_code, 422)
        with TestClient(create_app(self.db)) as restarted:
            self.assertEqual(restarted.get("/api/invoices").json(), self.client.get("/api/invoices").json())

    def test_demo_payment_is_persistent_and_idempotent(self):
        from uuid import uuid4

        endpoint = "/api/invoices/F-001/demo-payments"
        payload = {"request_id": str(uuid4()), "amount": "100.00"}
        with ThreadPoolExecutor(max_workers=2) as pool:
            responses = list(pool.map(lambda _: self.client.post(endpoint, json=payload), range(2)))
        self.assertEqual([r.status_code for r in responses], [201, 201])
        self.assertEqual(self.client.post(endpoint, json=payload | {"amount": "1"}).status_code, 409)
        self.assertEqual(self.client.post(endpoint, json={"request_id": str(uuid4()), "amount": "401"}).status_code, 409)
        self.assertEqual(self.client.post(endpoint, json={"request_id": str(uuid4()), "amount": "0"}).status_code, 422)
        with TestClient(create_app(self.db)) as restarted:
            result = restarted.get("/api/invoices?q=F-001").json()
            self.assertEqual(result["total_remaining"], 40000)
            self.assertEqual(result["invoices"][0]["paid"], 40000)
            self.assertEqual(restarted.post(endpoint, json={"request_id": str(uuid4()), "amount": "400"}).status_code, 201)
            self.assertEqual(restarted.get("/api/invoices?q=F-001&status=paid").json()["invoices"][0]["status"], "Saldata")

    def test_client_details_keep_rossi_accounts_separate(self):
        draft = self.confirm(self.preview()).json()
        studio = self.client.get("/api/clients/studio-rossi").json()
        martina = self.client.get("/api/clients/martina-rossi").json()
        self.assertEqual([item["id"] for item in studio["drafts"]], [draft["id"]])
        self.assertEqual({item["number"] for item in studio["invoices"]}, {"F-001", "F-002", "F-004"})
        self.assertEqual(studio["total_remaining"], 95000)
        self.assertEqual(martina["drafts"], [])
        self.assertEqual([item["number"] for item in martina["invoices"]], ["F-003"])
        self.assertEqual(martina["total_remaining"], 25000)
        self.assertEqual(self.client.get("/api/clients/ignoto").status_code, 404)

    def test_manual_client_persists_and_can_receive_a_quote(self):
        response = self.client.post("/api/clients", json={
            "name": " Studio Verdi ", "email": "studio@example.com", "phone": "+39 06 0000",
        })
        self.assertEqual(response.status_code, 201)
        client = response.json()
        self.assertEqual(client["name"], "Studio Verdi")
        self.assertEqual(self.client.post("/api/clients", json={"name": "studio verdi"}).status_code, 409)
        self.assertEqual(self.client.post("/api/clients", json={"name": "   "}).status_code, 422)
        draft = self.confirm(self.preview(client_id=client["id"])).json()
        with TestClient(create_app(self.db)) as restarted:
            detail = restarted.get("/api/clients/" + client["id"]).json()
            self.assertEqual(detail["email"], "studio@example.com")
            self.assertEqual(detail["phone"], "+39 06 0000")
            self.assertEqual([item["id"] for item in detail["drafts"]], [draft["id"]])
            self.assertEqual(detail["total_remaining"], 0)

    def test_guide(self):
        for question, article in [
            ("Come registro un incasso?", "incasso"),
            ("Come posso registrare un pagamento?", "incasso"),
            ("Come creo un preventivo?", "preventivo"),
            ("Come modifico una bozza?", "modifica-bozza"),
            ("Come vedo le fatture scadute?", "scadenze"),
        ]:
            with self.subTest(question=question):
                result = self.client.get("/api/guide", params={"q": question}).json()
                self.assertTrue(result["source"])
                self.assertEqual(result["articles"][0]["id"], article)
        result = self.client.get("/api/guide", params={"q": "Come invio la fattura allo SdI?"}).json()
        self.assertEqual(result["articles"], [])


if __name__ == "__main__":
    unittest.main()
