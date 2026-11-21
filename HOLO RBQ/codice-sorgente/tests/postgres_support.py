from contextlib import contextmanager
import os
from pathlib import Path
from tempfile import TemporaryDirectory
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.engine import make_url
from sqlalchemy.schema import CreateSchema, DropSchema

from app import create_app
from database import engine_for


@contextmanager
def postgres_case():
    base = os.environ['HOLO_TEST_DATABASE_URL']
    schema = 'holo_test_' + uuid4().hex
    admin = engine_for(base)
    with admin.begin() as db:
        db.execute(CreateSchema(schema))
    target = make_url(base).update_query_dict({'options': '-csearch_path=' + schema})
    try:
        with TemporaryDirectory() as folder:
            source = Path(folder) / 'holo.sqlite3'
            with TestClient(create_app(source)) as api:
                api.post('/api/clients', json={'name': 'Cliente migrazione Ω', 'email': 'prova@example.com'})
                quote = {'client_id': 'studio-rossi', 'subject': "Consulenza O'Reilly Ω", 'amount': '100.25', 'discount': '15'}
                preview = api.post('/api/previews', json=quote).json()
                draft = api.put('/api/drafts/' + preview['id']).json()
                api.post('/api/previews', json=quote | {'draft_id': draft['id'], 'draft_version': draft['version']})
                api.post('/api/invoices/F-001/demo-payments', json={'request_id': str(uuid4()), 'amount': '100'})
                activity = api.post('/api/clients/studio-rossi/follow-ups', json={
                    'title': 'Attività da preservare', 'due_date': '2099-07-02', 'invoice_number': 'F-001'
                }).json()
                import sqlite3
                with sqlite3.connect(source) as db:
                    db.execute('INSERT INTO follow_up_emails VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
                               (activity['id'], 'prova@example.com', 'Da non spedire', 'Testo con accento è',
                                '2099-07-02T08:00:00+00:00', 40000, 'scheduled', '', None))
            yield source, target
    finally:
        with admin.begin() as db:
            db.execute(DropSchema(schema, cascade=True))
        admin.dispose()
