from contextlib import redirect_stdout
from datetime import date
from io import StringIO
import os
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient
from sqlalchemy import text

from app import create_app
from database import engine_for, TABLE_COLUMNS, WRITE_LOCK
from migrate_to_postgres import migrate
from seed_demo import build_dataset, populate, main, PREFIX
from postgres_support import postgres_case


class DemoPlanTests(unittest.TestCase):
    def setUp(self):
        self.data = build_dataset(date(2032, 2, 29))

    def test_dates_money_and_boundary_cases(self):
        self.assertEqual([len(self.data[k]) for k in ('clients','invoices','demo_payments','drafts','follow_ups')], [15,21,12,6,9])
        today = next(i for i in self.data['invoices'] if i['number']=='RBQ-D05-F01')
        self.assertEqual(today['due_date'], '2032-02-29')
        minimum = next(i for i in self.data['invoices'] if i['number']=='RBQ-D11-F01')
        self.assertEqual((minimum['amount'],minimum['due_date']), (1,'2032-03-01'))
        partial = self.data['scenarios'][2]
        self.assertEqual((partial['invoiced_cents'],partial['remaining_cents'],partial['overdue_cents_at_reference_date']), (100000,60000,60000))
        self.assertEqual([q['total'] for q in self.data['drafts'][:4]], [72000,87499,120000,0])

    def test_reserved_identifiers_and_no_external_actions(self):
        self.assertEqual(self.data['email_records_created'],0)
        self.assertNotIn('follow_up_emails',self.data)
        self.assertEqual(len({c['id'] for c in self.data['clients']}),15)
        self.assertTrue(all(c['email']=='' or c['email'].endswith('@example.invalid') for c in self.data['clients']))
        for row in self.data['invoices']:
            self.assertLessEqual(row['paid'],row['amount'])
            self.assertGreater(row['amount'],0)
            self.assertEqual(row['paid'],sum(p['amount'] for p in self.data['demo_payments'] if p['invoice_number']==row['number']))

    def test_preview_does_not_connect_and_cancel_does_not_apply(self):
        with patch('sys.argv',['seed_demo.py']), patch('seed_demo.apply_dataset') as apply, redirect_stdout(StringIO()):
            self.assertEqual(main(),0)
            apply.assert_not_called()
        with patch('sys.argv',['seed_demo.py','--apply']), patch('builtins.input',return_value='NO'), patch('seed_demo.apply_dataset') as apply, redirect_stdout(StringIO()):
            self.assertEqual(main(),0)
            apply.assert_not_called()


@unittest.skipUnless(os.getenv('HOLO_TEST_DATABASE_URL'), 'Serve PostgreSQL reale isolato')
class DemoPostgresTests(unittest.TestCase):
    def setUp(self):
        self.scope=postgres_case();source,self.target=self.scope.__enter__()
        self.addCleanup(self.scope.__exit__,None,None,None)
        migrate(source,self.target)
        self.engine=engine_for(self.target);self.addCleanup(self.engine.dispose)
        self.data=build_dataset(date.today())

    def snapshot(self):
        with self.engine.connect() as db:
            return {table: set(tuple(row) for row in db.execute(text('SELECT * FROM '+table))) for table in TABLE_COLUMNS}

    def load(self):
        with self.engine.begin() as db:
            db.execute(text('SELECT pg_advisory_xact_lock(:key)'),{'key':WRITE_LOCK})
            return populate(db,self.data)

    def test_preserves_existing_records_and_repeat_preserves_user_changes(self):
        before=self.snapshot();self.assertTrue(self.load());after=self.snapshot()
        for table in before:
            self.assertTrue(before[table].issubset(after[table]),table)
        self.assertEqual(before['follow_up_emails'],after['follow_up_emails'])
        self.assertEqual(len(after['clients'])-len(before['clients']),15)
        with self.engine.begin() as db:
            db.execute(text("UPDATE follow_ups SET completed=1,due_date='2099-01-01' WHERE id=:id"),{'id':PREFIX+'a01'})
        changed=self.snapshot()
        self.assertFalse(self.load())
        self.assertEqual(changed,self.snapshot())

    def test_collision_and_partial_dataset_abort_without_partial_writes(self):
        with self.engine.begin() as db:
            db.execute(text("INSERT INTO invoices VALUES ('RBQ-D03-F01','studio-rossi','2099-01-01',900,0)"))
        before=self.snapshot()
        with self.assertRaises(Exception):
            self.load()
        self.assertEqual(before,self.snapshot())
        with self.engine.begin() as db:
            db.execute(text('INSERT INTO clients (id,name,email,phone) VALUES (:id,\'Riservato\',\'\',\'\')'),{'id':PREFIX+'01'})
        partial=self.snapshot()
        with self.assertRaises(ValueError):
            self.load()
        self.assertEqual(partial,self.snapshot())

    def test_seeded_data_supports_real_api_and_payment_flow(self):
        self.load()
        with TestClient(create_app(self.target)) as api:
            self.assertEqual(len(api.get('/api/clients',params={'q':'DEMO |'}).json()),15)
            risks=api.get('/api/customer-analysis?sort=risk').json()['customers']
            severe=next(c for c in risks if c['id']==PREFIX+'04')
            self.assertEqual((severe['remaining'],severe['risk_score']), (290000,100))
            today=next(c for c in risks if c['id']==PREFIX+'05')
            self.assertEqual((today['overdue_remaining'],today['risk_score']), (0,0))
            empty=next(c for c in risks if c['id']==PREFIX+'08')
            self.assertIsNone(empty['rank']);self.assertEqual(empty['draft_count'],2)
            values=api.get('/api/customer-analysis?sort=value').json()['customers']
            ties=[c for c in values if c['id'] in (PREFIX+'13',PREFIX+'14')]
            self.assertEqual(ties[0]['rank'],ties[1]['rank'])
            drafts=api.get('/api/drafts',params={'q':'DEMO |'}).json()
            zero=next(d for d in drafts if d['discount']==10000)
            self.assertEqual(zero['total'],0)
            payment={'request_id':'58627aa9-e2b9-45d7-a4cb-adcfa2cbdb5c','amount':'100.00'}
            self.assertEqual(api.post('/api/invoices/RBQ-D03-F01/demo-payments',json=payment).status_code,201)
            self.assertEqual(api.post('/api/invoices/RBQ-D03-F01/demo-payments',json=payment).status_code,201)
            result=api.get('/api/customer-analysis',params={'q':'DEMO | Incasso parziale'}).json()['customers'][0]
            self.assertEqual(result['remaining'],50000)
            activities=api.get('/api/follow-ups').json()
            demo=[a for a in activities if a['id'].startswith(PREFIX)]
            self.assertEqual(len(demo),9)
            self.assertTrue(all(a['email_status'] is None for a in demo))
