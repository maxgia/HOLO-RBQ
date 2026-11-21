"""Migrazione atomica e verificata delle otto tabelle HOLO, senza invii o modifiche alla sorgente."""
import argparse
from contextlib import closing
from datetime import datetime, timezone
import getpass
import hashlib
import json
import os
from pathlib import Path
import sqlite3
from uuid import uuid4

from sqlalchemy import inspect, text
from sqlalchemy.engine import URL

from database import CONFIG, ROOT, ORDER, TABLE_COLUMNS, WRITE_LOCK, create_schema, engine_for, postgres_url


def fingerprint(rows):
    canonical = sorted(json.dumps(row, sort_keys=True, ensure_ascii=False, separators=(',', ':')) for row in rows)
    return hashlib.sha256('\n'.join(canonical).encode()).hexdigest()


def snapshot(source, backup_dir):
    source = source.resolve(strict=True)
    backup_dir.mkdir(parents=True, exist_ok=True)
    backup = backup_dir / (source.stem + '-' + uuid4().hex + '.sqlite3')
    with closing(sqlite3.connect(source.as_uri() + '?mode=ro', uri=True)) as original:
        if original.execute('PRAGMA integrity_check').fetchone()[0] != 'ok':
            raise ValueError('Archivio SQLite non integro: migrazione interrotta.')
        with closing(sqlite3.connect(backup)) as copy:
            original.backup(copy)
    records = {}
    with closing(sqlite3.connect(backup.as_uri() + '?mode=ro', uri=True)) as db:
        db.row_factory = sqlite3.Row
        tables = {row[0] for row in db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")}
        if tables != set(TABLE_COLUMNS):
            raise ValueError('Schema SQLite non riconosciuto: tabelle mancanti o aggiuntive. Nessun dato e stato copiato.')
        if db.execute('PRAGMA foreign_key_check').fetchall():
            raise ValueError('Riferimenti SQLite non validi: correggere prima della migrazione.')
        for table, columns in TABLE_COLUMNS.items():
            actual = {row['name'] for row in db.execute(f'PRAGMA table_info({table})')}
            if actual != set(columns):
                raise ValueError('Versione SQLite non supportata: ' + table + '. Aggiornare la copia con la versione precedente prima di migrare.')
            records[table] = [dict(row) for row in db.execute('SELECT * FROM ' + table)]
    return backup, records


def migrate(source, target, backup_dir=None):
    source = Path(source)
    backup, records = snapshot(source, Path(backup_dir or source.parent / 'migration-backups'))
    hashes = {table: fingerprint(rows) for table, rows in records.items()}
    source_digest = fingerprint([hashes])
    engine = engine_for(target)
    try:
        with engine.begin() as db:
            db.execute(text('SELECT pg_advisory_xact_lock(:key)'), {'key': WRITE_LOCK})
            if set(inspect(db).get_table_names()) - (set(TABLE_COLUMNS) | {'_holo_migrations'}):
                raise ValueError('La destinazione contiene tabelle estranee a HOLO: usare un database dedicato vuoto.')
            create_schema(db)
            previous = db.execute(text('SELECT * FROM _holo_migrations')).mappings().all()
            existing = {table: [dict(row) for row in db.execute(text('SELECT * FROM ' + table)).mappings()] for table in ORDER}
            if previous:
                if len(previous) == 1 and previous[0]['source_digest'] == source_digest and all(fingerprint(existing[t]) == hashes[t] for t in ORDER):
                    return json.loads(previous[0]['report_json']) | {'already_verified': True, 'backup': str(backup)}
                raise ValueError('Destinazione gia migrata o modificata. Nessuna sovrascrittura: usare un database vuoto dedicato.')
            if any(existing.values()):
                raise ValueError('Destinazione non vuota. Nessuna sovrascrittura effettuata.')
            for table in ORDER:
                columns = TABLE_COLUMNS[table]
                statement = text(f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({', '.join(':' + c for c in columns)})")
                if records[table]:
                    db.execute(statement, records[table])
            maximum = max((row['id'] for row in records['drafts']), default=0)
            db.execute(text("SELECT setval(pg_get_serial_sequence('drafts','id'), :value, :called)"),
                       {'value': max(1, maximum), 'called': maximum > 0})
            for table in ORDER:
                copied = [dict(row) for row in db.execute(text('SELECT * FROM ' + table)).mappings()]
                if fingerprint(copied) != hashes[table]:
                    raise ValueError('Confronto dei dati fallito: rollback completo, tabella ' + table)
            report = {
                'schema_version': 1, 'source_digest': source_digest,
                'completed_at': datetime.now(timezone.utc).isoformat(),
                'source_file': source.name, 'backup': str(backup),
                'tables': {table: {'rows': len(records[table]), 'sha256': hashes[table]} for table in ORDER},
                'invoice_amount_cents': sum(row['amount'] for row in records['invoices']),
                'invoice_paid_cents': sum(row['paid'] for row in records['invoices']),
                'email_worker_started': False,
            }
            db.execute(text('INSERT INTO _holo_migrations VALUES (:digest, 1, :report)'),
                       {'digest': source_digest, 'report': json.dumps(report, ensure_ascii=False)})
        return report
    finally:
        engine.dispose()


def configure_target():
    def ask(label, default):
        return input(f'{label} [{default}]: ').strip() or default
    host = ask('Host PostgreSQL', '127.0.0.1')
    port = int(ask('Porta', '5432'))
    name = ask('Database gia creato', 'holo_rbq')
    user = ask('Utente PostgreSQL', 'holo_rbq')
    password = getpass.getpass('Password PostgreSQL (non viene mostrata): ')
    return URL.create('postgresql+psycopg', username=user, password=password, host=host, port=port, database=name)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sqlite', type=Path, default=ROOT / 'data' / 'holo.sqlite3')
    parser.add_argument('--configure', action='store_true', help='Chiede localmente i parametri PostgreSQL e salva la configurazione solo dopo la verifica.')
    args = parser.parse_args()
    if not args.sqlite.is_file():
        parser.error('Archivio sorgente non trovato. Indicare il file SQLite effettivamente usato.')
    try:
        target = configure_target() if args.configure else postgres_url()
        print('Ferma app e worker prima di continuare. La sorgente viene letta e copiata, non modificata.')
        if args.configure and input('App e worker sono fermi? Scrivi MIGRA per continuare: ').strip() != 'MIGRA':
            print('Operazione annullata.')
            return 1
        report = migrate(args.sqlite, target)
        data = ROOT / 'data'
        data.mkdir(parents=True, exist_ok=True)
        report_path = data / ('migration-report-' + uuid4().hex + '.json')
        report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')
        if args.configure:
            temp = CONFIG.with_suffix('.json.tmp')
            with temp.open('w', encoding='utf-8', opener=lambda path, flags: os.open(path, flags, 0o600)) as stream:
                json.dump({'url': target.render_as_string(hide_password=False)}, stream)
            os.replace(temp, CONFIG)
        print('Migrazione verificata. Report: ' + str(report_path))
        print('Il vecchio SQLite e il backup restano disponibili. Nessuna email inviata.')
        return 0
    except Exception as error:
        if isinstance(error, ValueError):
            print(str(error))
        else:
            print('Migrazione non completata: ' + type(error).__name__ + '. Verificare connessione, permessi e integrita dei dati. Configurazione non attivata.')
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
