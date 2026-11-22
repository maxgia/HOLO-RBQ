"""Dataset interno di collaudo. Anteprima predefinita; nessuna email creata."""
import argparse
from datetime import date, datetime, timedelta
import json
from pathlib import Path
from uuid import NAMESPACE_URL, uuid5
from zoneinfo import ZoneInfo

from sqlalchemy import text

from database import PostgresStore, ROOT, WRITE_LOCK


PREFIX = 'rbq-demo-v1-'


def build_dataset(today):
    clients, invoices, payments, drafts, activities, scenarios = [], [], [], [], [], []
    definitions = [
        ('Cliente consolidato', 'Tre fatture saldate: alto valore registrato, nessuno scaduto.', [(120000, 120000, -60), (150000, 150000, -30), (180000, 180000, -5)]),
        ('Rapporto continuativo', 'Storico misto, prossimo incasso futuro.', [(100000, 100000, -20), (80000, 80000, -7), (90000, 0, 15)]),
        ('Incasso parziale', 'Fattura scaduta con residuo diverso dal totale originario.', [(100000, 40000, -12)]),
        ('Scaduto anziano', 'Due scaduti oltre sessanta giorni; verificare criticità elevata.', [(200000, 0, -90), (100000, 10000, -65)]),
        ('Scadenza oggi', 'La fattura di oggi non è ancora scaduta.', [(75000, 0, 0)]),
        ('Scadenze future', 'Una scadenza entro sette giorni e una successiva.', [(45000, 0, 3), (65000, 0, 25)]),
        ('Senza storico', 'Nessuna fattura o bozza; posizione Non classificato.', []),
        ('Solo preventivi', 'Due bozze senza fatture: niente fatturato e Non classificato.', []),
        ('Studio Aurora', 'Nome simile ad altro cliente: verificare separazione documenti.', [(32000, 0, -3)]),
        ('Aurora Studio', 'Nome simile ad altro cliente, importo e scadenza differenti.', [(64000, 0, 8)]),
        ('Importo minimo', 'Un centesimo: importi e arrotondamenti leggibili.', [(1, 0, 1)]),
        ('Officina & Servizi «Èlite»', 'Accenti, simboli e centesimi nei filtri e nel CSV.', [(123456, 23456, -1)]),
        ('Parità Alfa', 'Una fattura saldata come Parità Beta: stesso punteggio di valore.', [(50000, 50000, -5)]),
        ('Parità Beta', 'Una fattura saldata come Parità Alfa: stessa posizione in valore.', [(50000, 50000, -5)]),
        ('Valore con criticità', 'Incassi consistenti e scaduto: valore e rischio sono distinti.', [(200000, 200000, -60), (200000, 200000, -45), (500000, 0, -35)]),
    ]
    for number, (name, purpose, rows) in enumerate(definitions, 1):
        cid = f'{PREFIX}{number:02}'
        client = {'id': cid, 'name': 'DEMO | ' + name,
                  'email': '' if number in (7, 8) else f'cliente{number:02}@example.invalid', 'phone': ''}
        clients.append(client)
        for index, (amount, paid, days) in enumerate(rows, 1):
            inv = {'number': f'RBQ-D{number:02}-F{index:02}', 'client_id': cid,
                   'due_date': (today + timedelta(days=days)).isoformat(), 'amount': amount, 'paid': paid}
            invoices.append(inv)
            if paid:
                payments.append({'request_id': str(uuid5(NAMESPACE_URL, inv['number'])),
                                 'invoice_number': inv['number'], 'amount': paid})
        total = sum(r[0] for r in rows)
        collected = sum(r[1] for r in rows)
        overdue = sum(a-p for a, p, days in rows if days < 0)
        scenarios.append({'case': f'DEMO-{number:02}', 'client_id': cid, 'client': client['name'],
                          'purpose': purpose, 'invoice_count': len(rows), 'invoiced_cents': total,
                          'paid_cents': collected, 'remaining_cents': total-collected,
                          'overdue_cents_at_reference_date': overdue, 'manual_status': 'Da eseguire'})
    # Stessa aritmetica in centesimi e punti base dei preventivi dell'app.
    for index, (client_number, amount, discount, subject) in enumerate([
        (8, 80000, 1000, 'Consulenza con sconto 10%'),
        (8, 99999, 1250, 'Sconto frazionario 12,50%'),
        (1, 120000, 0, 'Continuità del servizio'),
        (2, 50000, 10000, 'Sconto 100%: totale zero'),
        (12, 12345, 500, 'Servizi «Èlite» & assistenza'),
        (15, 250000, 1500, 'Proposta da rivalutare')], 1):
        client = clients[client_number-1]
        drafts.append({'preview_id': f'{PREFIX}q{index:02}', 'client': client['name'],
                       'client_id': client['id'], 'subject': 'DEMO | ' + subject, 'amount': amount,
                       'discount': discount, 'total': amount - (amount * discount + 5000)//10000,
                       'version': f'{PREFIX}q{index:02}'})
    # La data è quella dell'attività. Nessun record follow_up_emails.
    for index, (client_number, title, days, completed, invoice, draft_key) in enumerate([
        (3, 'Verificare incasso parziale', -2, 0, 'RBQ-D03-F01', None),
        (4, 'Valutare piano di rientro', 0, 0, 'RBQ-D04-F01', None),
        (5, 'Controllare scadenza odierna', 0, 0, 'RBQ-D05-F01', None),
        (6, 'Preparare verifica prossima scadenza', 2, 0, 'RBQ-D06-F01', None),
        (8, 'Rivedere preventivo', 7, 0, None, f'{PREFIX}q01'),
        (1, 'Confronto di continuità', 15, 0, None, None),
        (2, 'Verifica già completata', -1, 1, 'RBQ-D02-F01', None),
        (12, 'Verifica dati «Èlite»', 30, 0, None, None),
        (15, 'Rivedere proposta e scaduto', 5, 0, None, f'{PREFIX}q06')], 1):
        activities.append({'id': f'{PREFIX}a{index:02}', 'client_id': clients[client_number-1]['id'],
                           'title': 'DEMO | ' + title, 'due_date': (today+timedelta(days=days)).isoformat(),
                           'completed': completed, 'invoice_number': invoice, 'draft_key': draft_key})
    return {'dataset': PREFIX, 'reference_date': today.isoformat(), 'clients': clients,
            'invoices': invoices, 'demo_payments': payments, 'drafts': drafts,
            'follow_ups': activities, 'scenarios': scenarios, 'email_records_created': 0}


def populate(db, data):
    """Chiamare in una transazione già aperta e serializzata con WRITE_LOCK."""
    ids = {c['id'] for c in data['clients']}
    existing = set(db.execute(text('SELECT id FROM clients')).scalars()) & ids
    if existing == ids:
        return False  # Preserva anche le modifiche effettuate nei test precedenti.
    if existing:
        raise ValueError('Dataset DEMO presente solo in parte: nessuna modifica. Non cancellare record per forzare il caricamento.')
    # Qualunque collisione nei record figli provoca rollback, senza ON CONFLICT che nasconda incongruenze.
    for c in data['clients']:
        db.execute(text('INSERT INTO clients (id,name,email,phone) VALUES (:id,:name,:email,:phone)'), c)
    for inv in data['invoices']:
        db.execute(text('INSERT INTO invoices (number,client_id,due_date,amount,paid) VALUES (:number,:client_id,:due_date,:amount,:paid)'), inv)
    for payment in data['demo_payments']:
        db.execute(text('INSERT INTO demo_payments (request_id,invoice_number,amount) VALUES (:request_id,:invoice_number,:amount)'), payment)
    draft_ids = {}
    for draft in data['drafts']:
        draft_ids[draft['preview_id']] = db.execute(text('INSERT INTO drafts (preview_id,client,subject,amount,discount,total,client_id,version) VALUES (:preview_id,:client,:subject,:amount,:discount,:total,:client_id,:version) RETURNING id'), draft).scalar_one()
    for activity in data['follow_ups']:
        row = {k: v for k, v in activity.items() if k != 'draft_key'}
        row['draft_id'] = str(draft_ids[activity['draft_key']]) if activity['draft_key'] else None
        db.execute(text('INSERT INTO follow_ups (id,client_id,title,due_date,completed,invoice_number,draft_id) VALUES (:id,:client_id,:title,:due_date,:completed,:invoice_number,:draft_id)'), row)
    return True


def apply_dataset(data):
    # Usa solo il PostgreSQL operativo già migrato, come l'applicazione.
    from database import postgres_url
    store = PostgresStore(postgres_url())
    try:
        with store.engine.begin() as db:
            db.execute(text('SELECT pg_advisory_xact_lock(:key)'), {'key': WRITE_LOCK})
            return populate(db, data)
    finally:
        store.engine.dispose()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apply', action='store_true', help='Aggiunge il dataset dopo conferma locale.')
    parser.add_argument('--date', type=date.fromisoformat, help='Data di riferimento ISO; predefinita: oggi in Italia.')
    args = parser.parse_args()
    data = build_dataset(args.date or datetime.now(ZoneInfo('Europe/Rome')).date())
    counts = {k: len(data[k]) for k in ('clients', 'invoices', 'demo_payments', 'drafts', 'follow_ups')}
    print('Dataset DEMO v1 — data di riferimento:', data['reference_date'])
    print(json.dumps(counts, ensure_ascii=False))
    print('Email create: 0. Dati esistenti preservati. Le classifiche globali cambieranno.')
    if not args.apply:
        print('Solo anteprima: nessuna connessione al database. Usa --apply per caricare.')
        for scenario in data['scenarios']:
            print(scenario['case'] + ' | ' + scenario['client'] + ' | ' + scenario['purpose'])
        return 0
    print('Ferma server e worker; conserva un backup prima di procedere.')
    if input('Scrivi CARICA DEMO per aggiungere questi casi al PostgreSQL configurato: ').strip() != 'CARICA DEMO':
        print('Operazione annullata, nessun dato modificato.')
        return 0
    try:
        inserted = apply_dataset(data)
    except Exception:
        print('Caricamento non completato: transazione annullata. Verifica PostgreSQL/configurazione e possibili collisioni; nessuna credenziale viene mostrata.')
        return 1
    if not inserted:
        print('Dataset già presente: nessun duplicato, nessuna data o modifica di collaudo sovrascritta.')
        return 0
    report = ROOT / 'data' / 'demo-v1-report.json'
    try:
        report.parent.mkdir(exist_ok=True)
        temporary = report.with_suffix('.tmp')
        temporary.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
        temporary.replace(report)
        print('Caricamento completato. Date e attesi iniziali registrati in data/demo-v1-report.json.')
    except OSError:
        print('Dati caricati correttamente, ma report locale non salvato. Non rilanciare per ripristinare le date; il dataset resta nel database.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
