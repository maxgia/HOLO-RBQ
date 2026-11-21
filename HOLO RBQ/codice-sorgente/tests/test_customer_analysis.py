from contextlib import closing
from datetime import date
from pathlib import Path
import json
import sqlite3
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch, MagicMock
from uuid import uuid4

from fastapi import HTTPException
from fastapi.testclient import TestClient

from app import create_app
from customer_analysis import analyse_customers, LocalAdvice
from customer_assistant import local_structured_response


class CustomerAnalysisTests(unittest.TestCase):
    def setUp(self):
        self.folder = TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        self.database = Path(self.folder.name) / "test.sqlite3"
        self.client = TestClient(create_app(self.database))

    def portfolio(self, **params):
        response = self.client.get("/api/customer-analysis", params=params)
        self.assertEqual(response.status_code, 200, response.text)
        return response.json()["customers"]

    def test_scores_match_demo_and_search_keeps_portfolio_rank(self):
        by_value = self.portfolio()
        self.assertEqual(by_value[0]["id"], "studio-rossi")
        rossi = by_value[0]
        self.assertEqual((rossi["invoiced"], rossi["paid"], rossi["remaining"]), (185000, 90000, 95000))
        self.assertEqual((rossi["overdue_remaining"], rossi["oldest_overdue_days"]), (50000, 12))
        self.assertEqual((rossi["value_score"], rossi["risk_score"]), (100, 43))
        result = self.portfolio(q="Martina")
        self.assertEqual(len(result), 1)
        original = next(item for item in by_value if item["id"] == "martina-rossi")
        self.assertEqual(result[0]["rank"], original["rank"])
        self.assertEqual(result[0]["remaining"], 25000)
        self.assertEqual(self.portfolio(sort="risk")[0]["id"], "studio-rossi")
        self.assertEqual(self.client.get("/api/customer-analysis?sort=bad").status_code, 422)

    def test_payment_updates_analysis_and_restart(self):
        response = self.client.post("/api/invoices/F-001/demo-payments", json={
            "request_id": str(uuid4()), "amount": "500",
        })
        self.assertEqual(response.status_code, 201)
        self.client = TestClient(create_app(self.database))
        item = self.portfolio(q="Studio Rossi")[0]
        self.assertEqual(item["risk_score"], 0)
        self.assertEqual(item["overdue_remaining"], 0)
        self.assertEqual(item["remaining"], 45000)
        self.assertIn("continuità", item["suggested_action"])

    @patch("customer_analysis.local_structured_response")
    def test_empty_client_has_no_rank_and_skips_model(self, model):
        client = self.client.post("/api/clients", json={"name": "<Studio nuovo>"}).json()
        item = self.portfolio(q="<Studio")[0]
        self.assertIsNone(item["rank"])
        self.assertIsNone(item["value_score"])
        self.assertIsNone(item["paid_ratio"])
        reply = self.client.post(f"/api/customer-analysis/{client['id']}/advice")
        self.assertEqual(reply.status_code, 200)
        model.assert_not_called()
        self.assertEqual(self.portfolio(q="inesistente"), [])

    def test_zero_totals_and_due_today_are_not_overdue(self):
        with closing(sqlite3.connect(self.database)) as db, db:
            db.row_factory = sqlite3.Row
            db.execute("DELETE FROM invoices")
            db.execute("INSERT INTO invoices VALUES ('Z-1','studio-rossi','2030-01-01',0,0)")
            db.execute("INSERT INTO invoices VALUES ('D-1','martina-rossi','2030-01-01',10000,0)")
            results = {item["id"]: item for item in analyse_customers(db, date(2030, 1, 1))}
        self.assertIsNone(results["studio-rossi"]["value_score"])
        self.assertEqual(results["martina-rossi"]["risk_score"], 0)
        self.assertEqual(results["martina-rossi"]["oldest_overdue_days"], 0)

    @patch("customer_analysis.local_structured_response")
    def test_model_proposal_is_bounded_to_customer_facts(self, model):
        model.return_value = LocalAdvice(action="review_payment")
        response = self.client.post("/api/customer-analysis/studio-rossi/advice")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Ollama locale", response.json()["source"])
        prompt = json.loads(model.call_args.args[1][1]["content"])
        self.assertEqual(prompt["overdue_remaining"], 50000)
        self.assertNotIn("name", prompt)
        model.return_value = LocalAdvice(action="retain")
        self.assertEqual(self.client.post("/api/customer-analysis/studio-rossi/advice").status_code, 502)
        model.side_effect = HTTPException(503, "Ollama non disponibile.")
        self.assertEqual(self.client.post("/api/customer-analysis/studio-rossi/advice").status_code, 503)
        self.assertTrue(self.portfolio())
        self.assertEqual(self.client.post("/api/customer-analysis/missing/advice").status_code, 404)

    @patch("customer_assistant.build_opener")
    def test_structured_model_transport_is_loopback_and_validated(self, opener):
        response = MagicMock()
        response.read.return_value = json.dumps({"message": {"content": '{"action":"retain"}'}}).encode()
        opener.return_value.open.return_value.__enter__.return_value = response
        result = local_structured_response(LocalAdvice, [{"role": "user", "content": "test"}])
        self.assertEqual(result.action, "retain")
        request = opener.return_value.open.call_args.args[0]
        self.assertEqual(request.full_url, "http://127.0.0.1:11434/api/chat")
        response.read.return_value = b'{"message":{"content":"invalid"}}'
        with self.assertRaises(HTTPException) as error:
            local_structured_response(LocalAdvice, [])
        self.assertEqual(error.exception.status_code, 502)
