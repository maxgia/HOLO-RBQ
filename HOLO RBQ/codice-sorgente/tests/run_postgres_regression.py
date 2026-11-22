"""Riesegue le prove funzionali SQLite originali su schemi PostgreSQL isolati.

Le asserzioni dei test restano invariate. Solo le factory di storage vengono
sostituite per questa esecuzione. Nessun accesso al database operativo.
"""
from contextlib import closing
import importlib
import json
import os
from pathlib import Path
import sqlite3
import sys
from time import monotonic
from types import SimpleNamespace
import unittest
from uuid import uuid4

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / 'tests'), str(ROOT / 'e2e')]
from app import create_app as original_app
from database import PostgresStore, engine_for, postgres_url
from migrate_to_postgres import migrate
from sqlalchemy.schema import CreateSchema, DropSchema


class Sandbox:
    def __init__(self):
        self.base = postgres_url(os.environ['HOLO_TEST_DATABASE_URL'])
        if not self.base.database or not self.base.database.endswith('_test'):
            raise ValueError('Usare soltanto un database dedicato con nome che termina in _test.')
        operational = os.getenv('HOLO_DATABASE_URL')
        if operational and postgres_url(operational) == self.base:
            raise ValueError('Il database operativo non puo essere usato per la regressione.')
        self.admin = engine_for(self.base)
        self.targets = {}
        self.schemas = []
        self.stores = []
        self.calls = 0

    def application(self, database):
        if not isinstance(database, Path):
            raise ValueError('La suite originale deve fornire una fixture temporanea Path.')
        path = database.resolve()
        if path not in self.targets:
            # Inizializzazione e aggiornamento legacy avvengono solo nella fixture
            # SQLite; tutte le richieste applicative successive usano PostgreSQL.
            original_app(path)
            schema = 'holo_regression_' + uuid4().hex
            with self.admin.begin() as db:
                db.execute(CreateSchema(schema))
            self.schemas.append(schema)
            target = self.base.update_query_dict({'options': '-csearch_path=' + schema})
            migrate(path, target)
            self.targets[path] = target
        app = original_app(self.targets[path])
        if not isinstance(app.state.store, PostgresStore):
            raise AssertionError('Una richiesta applicativa e rimasta su SQLite.')
        self.stores.append(app.state.store)
        self.calls += 1
        return app

    def connect(self, database, *args, **kwargs):
        target = self.targets.get(Path(database).resolve())
        if target is None:
            # Il solo test legacy costruisce qui la propria sorgente SQLite.
            return sqlite3.connect(database, *args, **kwargs)
        store = PostgresStore(target)
        self.stores.append(store)
        return store.connect()

    def close(self):
        for store in self.stores:
            store.engine.dispose()
        try:
            with self.admin.begin() as db:
                for schema in self.schemas:
                    db.execute(DropSchema(schema, cascade=True))
        finally:
            self.admin.dispose()


class RecordedResult(unittest.TextTestResult):
    def startTest(self, test):
        self.started = monotonic()
        self.current = 'passed'
        super().startTest(test)

    def addFailure(self, test, error):
        self.current = 'failed'
        super().addFailure(test, error)

    def addError(self, test, error):
        self.current = 'error'
        super().addError(test, error)

    def addSkip(self, test, reason):
        self.current = 'skipped'
        super().addSkip(test, reason)

    def addSubTest(self, test, subtest, error):
        if error is not None:
            self.current = 'failed'
        super().addSubTest(test, subtest, error)

    def stopTest(self, test):
        records.append({'test': test.id(), 'backend': 'PostgreSQL',
                        'status': self.current, 'seconds': round(monotonic() - self.started, 3)})
        super().stopTest(test)


records = []


def main():
    sandbox = Sandbox()
    suite = unittest.TestSuite()
    names = ['test_mvp', 'test_customer_analysis', 'test_follow_up_email',
             'test_preventivi', 'test_fatture_guida', 'test_workspace_ux']
    try:
        browser = importlib.import_module('browser_server')
        browser.create_app = sandbox.application
        for name in names:
            module = importlib.import_module(name)
            if hasattr(module, 'create_app'):
                module.create_app = sandbox.application
            if hasattr(module, 'sqlite3'):
                module.sqlite3 = SimpleNamespace(connect=sandbox.connect, Row=sqlite3.Row)
            suite.addTests(unittest.defaultTestLoader.loadTestsFromModule(module))
        result = unittest.TextTestRunner(verbosity=2, resultclass=RecordedResult).run(suite)
        passed = result.wasSuccessful() and not result.skipped and sandbox.calls > 0
        report = {'backend': 'PostgreSQL', 'original_assertions': True,
                  'external_email_sent': False, 'ollama': 'mocked',
                  'test_schemas': len(sandbox.schemas), 'postgres_app_instances': sandbox.calls,
                  'tests_run': result.testsRun, 'passed': passed, 'results': records}
        (ROOT / 'postgres-regression-results.json').write_text(
            json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')
        return 0 if passed else 1
    finally:
        sandbox.close()


if __name__ == '__main__':
    raise SystemExit(main())

