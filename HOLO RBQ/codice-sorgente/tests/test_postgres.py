from concurrent.futures import ThreadPoolExecutor
from contextlib import closing
import hashlib
import os
import sqlite3
import unittest
from io import StringIO
from contextlib import redirect_stdout
from unittest.mock import patch
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy import inspect, text

from app import create_app
from database import engine_for, TABLE_COLUMNS, postgres_url
from follow_up_email import process_one
from migrate_to_postgres import migrate
import migrate_to_postgres
from postgres_support import postgres_case


@unittest.skipUnless(os.getenv('HOLO_TEST_DATABASE_URL'), 'Serve PostgreSQL reale dedicato ai test')
class PostgreSQLTests(unittest.TestCase):
    def setUp(self):
        self.scope = postgres_case()
        self.source, self.target = self.scope.__enter__()
        self.addCleanup(self.scope.__exit__, None, None, None)
        self.engine = engine_for(self.target)
        self.addCleanup(self.engine.dispose)

    def copy(self):
        return migrate(self.source, self.target)

    def test_complete_copy_checksums_source_unchanged_and_no_smtp(self):
        before = hashlib.sha256(self.source.read_bytes()).hexdigest()
        report = self.copy()
        self.assertEqual(before, hashlib.sha256(self.source.read_bytes()).hexdigest())
        self.assertEqual(set(report['tables']), set(TABLE_COLUMNS))
        self.assertTrue(all(item['rows'] > 0 for item in report['tables'].values()))
        self.assertFalse(report['email_worker_started'])
        self.assertTrue(self.copy()['already_verified'])
        with self.engine.connect() as db:
            self.assertEqual(db.execute(text('SELECT status FROM follow_up_emails')).scalar(), 'scheduled')

    def test_api_parity_identity_and_postgres_restart(self):
        self.copy()
        with TestClient(create_app(self.source)) as old, TestClient(create_app(self.target)) as new:
            for path in ['/api/clients', '/api/drafts', '/api/invoices', '/api/clients/studio-rossi', '/api/follow-ups', '/api/customer-analysis?sort=risk']:
                with self.subTest(path=path):
                    self.assertEqual(old.get(path).json(), new.get(path).json())
            preview = new.post('/api/previews', json={'client_id': 'studio-rossi', 'subject': 'Nuova bozza', 'amount': '80', 'discount': '10'}).json()
            draft = new.put('/api/drafts/' + preview['id']).json()
            self.assertEqual(draft['id'], 'DEMO-002')
            self.assertEqual(draft['total'], 7200)
        with TestClient(create_app(self.target)) as restarted:
            self.assertEqual(len(restarted.get('/api/drafts').json()), 2)

    def test_payment_concurrency_idempotency_and_analysis(self):
        self.copy()
        with TestClient(create_app(self.target)) as api:
            payment = {'request_id': str(uuid4()), 'amount': '400'}
            with ThreadPoolExecutor(max_workers=8) as executor:
                statuses = list(executor.map(lambda _: api.post('/api/invoices/F-001/demo-payments', json=payment).status_code, range(8)))
            self.assertEqual(statuses, [201] * 8)
            rossi = api.get('/api/customer-analysis?q=Studio Rossi').json()['customers'][0]
            self.assertEqual((rossi['remaining'], rossi['overdue_remaining'], rossi['risk_score']), (45000, 0, 0))
            self.assertEqual(api.get('/api/follow-ups').json()[0]['email_status'], 'paid_review')

    def test_concurrent_draft_confirmation_and_edit_conflict(self):
        self.copy()
        with TestClient(create_app(self.target)) as api:
            quote = {'client_id': 'studio-rossi', 'subject': 'Bozza concorrente', 'amount': '80', 'discount': '10'}
            preview = api.post('/api/previews', json=quote).json()
            with ThreadPoolExecutor(max_workers=8) as executor:
                replies = list(executor.map(lambda _: api.put('/api/drafts/' + preview['id']).json(), range(8)))
            self.assertEqual({row['id'] for row in replies}, {'DEMO-002'})
            a = api.post('/api/previews', json=quote | {'draft_id': 'DEMO-002', 'draft_version': ''}).json()
            b = api.post('/api/previews', json=quote | {'draft_id': 'DEMO-002', 'draft_version': ''}).json()
            self.assertEqual(api.put('/api/drafts/' + a['id']).status_code, 200)
            self.assertEqual(api.put('/api/drafts/' + b['id']).status_code, 409)

    def test_nonempty_target_is_not_overwritten(self):
        self.copy()
        with TestClient(create_app(self.target)) as api:
            api.post('/api/clients', json={'name': 'Dato nuovo PostgreSQL'})
            with self.assertRaises(ValueError):
                self.copy()
            self.assertEqual(len(api.get('/api/clients').json()), 5)

    def test_unknown_source_table_rejected_before_copy(self):
        with sqlite3.connect(self.source) as db:
            db.execute('CREATE TABLE dati_extra (id INTEGER)')
        with self.assertRaises(ValueError):
            self.copy()
        with self.engine.connect() as db:
            self.assertEqual(inspect(db).get_table_names(), [])

    def test_failed_insert_rolls_back_schema_and_rows(self):
        with sqlite3.connect(self.source) as db:
            db.execute("UPDATE invoices SET amount='valore non numerico' WHERE number='F-001'")
        with self.assertRaises(Exception):
            self.copy()
        with self.engine.connect() as db:
            self.assertEqual(inspect(db).get_table_names(), [])

    def test_worker_uses_same_postgres_without_sending_future_mail(self):
        self.copy()
        app = create_app(self.target)
        with closing(app.state.store.connect()) as db:
            calls = []
            self.assertFalse(process_one(db, lambda row: calls.append(row)))
            self.assertEqual(calls, [])

    def test_configuration_is_written_only_after_verified_copy(self):
        root = self.source.parent / 'config locale'
        config = root / 'data' / 'postgres.json'
        with patch('sys.argv', ['migrate_to_postgres.py', '--configure', '--sqlite', str(self.source)]), \
             patch('migrate_to_postgres.configure_target', return_value=self.target), \
             patch('builtins.input', return_value='MIGRA'), \
             patch('migrate_to_postgres.ROOT', root), patch('migrate_to_postgres.CONFIG', config), \
             redirect_stdout(StringIO()) as output:
            self.assertEqual(migrate_to_postgres.main(), 0)
        self.assertTrue(config.is_file())
        self.assertNotIn('holo-ci-only', output.getvalue())
