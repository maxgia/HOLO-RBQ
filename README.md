# HOLO RBQ — PostgreSQL

## Nuova UX D09 — Home e pagine operative

Home sintetica con urgenze e azioni; pagine dedicate; Clienti a tab; Attività con calendario Mese/Settimana/Giorno; analisi AI e calcoli in tabelle; Report dello stato corrente con CSV. Tema scuro e accenti lavanda. [Specifica e collaudo](HOLO%20RBQ/documentazione/UX-UI-D09.md).

**Se PostgreSQL è già configurato, non migrare di nuovo:** aggiornare index.html o i sorgenti da main conservando data/postgres.json e .venv. Avviare Avvia-HOLO.cmd e ricaricare la pagina. Worker spento per queste prove.

[CI 45042571780](https://github.com/maxgia/HOLO-RBQ/actions/runs/45042571780): 36 Python, 11 Node, 20 Chromium e 39 prove funzionali PostgreSQL superati; anche preflight Windows. Nessun invio reale; AI simulata. Excel: 48 casi, nove conferme umane preservate, UX-01–UX-05 da eseguire. D09 implementato, verifica utente aperta; D11 storico completo da pianificare; A06 gestionale aperto.

## Collaudo del 22 novembre 2026

Migrazione sul PC Windows e primo avvio PostgreSQL confermati dall’utente. Copiate e verificate otto tabelle: 4 clienti, 0 anteprime, 1 bozza, 5 fatture, 1 incasso, 0 follow-up, 1 modifica, 0 email. Assenza dei follow-up accettata. PG-01–02 Superato; PG-03 e AC-11 In corso; PG-04–05 ancora da eseguire sul PC.

[CI 45037721777](https://github.com/maxgia/HOLO-RBQ/actions/runs/45037721777), codice `bc20dfc`: 34 prove funzionali originali rieseguite su PostgreSQL (20 Python e 14 Chromium), tutte superate. Superati anche nove test PostgreSQL specifici, i controlli di configurazione e launcher, gli 11 Node e la regressione SQLite. Sender e AI simulati; nessun accesso al database operativo e nessun invio reale. [Report per caso](HOLO%20RBQ/documentazione/Regressione-PostgreSQL-2026-11-22.md).

Registro Excel: 43 casi, 9 nuovi esiti umani Superato complessivi. Le sette conferme precedenti restano storiche. D10 in collaudo; D09 UX/UI segue questo passaggio; A06 resta aperta. Le indicazioni del 21 novembre sul trasferimento ancora da eseguire descrivono lo stato precedente.

Versione **0.3.0-postgres** per freelance e partite IVA. Backend Python/FastAPI, frontend HTML/CSS/JavaScript, database PostgreSQL con SQLAlchemy e psycopg. Le funzionalita' di clienti, preventivi, incassi, attivita' e analisi sono mantenute.

## Prima dell'avvio: migrare l'archivio corrente

1. Conservare la copia funzionante 0.2 e il suo file `data/holo.sqlite3`. Fermare server e worker email.
2. Preparare un database PostgreSQL **vuoto e dedicato**, con accessi locali disponibili.
3. Aggiornare l'intera cartella dei sorgenti, conservando data e .venv.
4. Fare doppio clic su **Configura-Postgres.cmd** e seguire la [procedura di migrazione](HOLO%20RBQ/documentazione/Migrazione-PostgreSQL.md). La password si inserisce sul PC, non in chat.
5. Dopo **Migrazione verificata**, usare **Avvia-HOLO.cmd**.

La procedura conserva un backup, copia tutte le otto tabelle, confronta contenuti e conteggi, riallinea i progressivi e attiva PostgreSQL solo dopo la verifica. Non invia email. Una destinazione gia' popolata non viene sovrascritta. Non esiste fallback automatico su SQLite.

**22 novembre: migrazione locale verificata e clienti visibili confermati dall’utente.** Assenza follow-up accettata. Restano confronto completo e nuove operazioni/riavvio sul PC (PG-03–05). La CI usa esclusivamente archivi isolati di collaudo.

## Stato e verifiche

[PR #9](https://github.com/maxgia/HOLO-RBQ/pull/9), [CI 44936628150](https://github.com/maxgia/HOLO-RBQ/actions/runs/44936628150), codice `569ec22`: 36 Python, 11 Node, 15 Chromium superati, con nove test Python e un browser specifici su PostgreSQL reale. Preflight PowerShell Windows superato; migrazione e avvio completi sul PC utente ancora da collaudare.

A06 resta aperta per la ricerca del gestionale reale. D10 PostgreSQL precede la revisione UX/UI D09. Sette conferme utente sulla precedente versione restano evidenze storiche; PG-01–02 superati sul PC; PG-03 in corso e PG-04–05 da eseguire.

## Documentazione

- [Migrazione, backup e ritorno alla versione precedente](HOLO%20RBQ/documentazione/Migrazione-PostgreSQL.md)
- [Avvio e aggiornamento](HOLO%20RBQ/documentazione/Runbook.md)
- [Piano generale](HOLO%20RBQ/documentazione/Piano-generale.md)
- [Specifica tecnica](HOLO%20RBQ/documentazione/Specifica-tecnica-HOLO-RBQ.md)
- [Registro Excel, 48 casi](HOLO%20RBQ/documentazione/HOLO-RBQ-Registro-test-2026-11-21.xlsx)
- [Evidenze dei test](HOLO%20RBQ/documentazione/Registro-collaudo-2026-11-21.md)
- [Piano UX/UI](HOLO%20RBQ/documentazione/Piano-UX-UI.md)

Il file SQLite rimane soltanto per migrazione, backup e fixture esplicite di test. Il runtime normale e il worker usano PostgreSQL. Non avviare il worker finche' non siano state riesaminate le pianificazioni trasferite.

