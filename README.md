# HOLO RBQ — PostgreSQL

Versione **0.3.0-postgres** per freelance e partite IVA. Backend Python/FastAPI, frontend HTML/CSS/JavaScript, database PostgreSQL con SQLAlchemy e psycopg. Le funzionalita' di clienti, preventivi, incassi, attivita' e analisi sono mantenute.

## Prima dell'avvio: migrare l'archivio corrente

1. Conservare la copia funzionante 0.2 e il suo file `data/holo.sqlite3`. Fermare server e worker email.
2. Preparare un database PostgreSQL **vuoto e dedicato**, con accessi locali disponibili.
3. Aggiornare l'intera cartella dei sorgenti, conservando data e .venv.
4. Fare doppio clic su **Configura-Postgres.cmd** e seguire la [procedura di migrazione](HOLO%20RBQ/documentazione/Migrazione-PostgreSQL.md). La password si inserisce sul PC, non in chat.
5. Dopo **Migrazione verificata**, usare **Avvia-HOLO.cmd**.

La procedura conserva un backup, copia tutte le otto tabelle, confronta contenuti e conteggi, riallinea i progressivi e attiva PostgreSQL solo dopo la verifica. Non invia email. Una destinazione gia' popolata non viene sovrascritta. Non esiste fallback automatico su SQLite.

**I dati effettivi dell'utente non sono ancora trasferiti:** la copia va eseguita sul PC con il database sorgente corretto e il server PostgreSQL scelto. La CI verifica archivi completi di collaudo, non una copia privata del suo database.

## Stato e verifiche

[PR #9](https://github.com/maxgia/HOLO-RBQ/pull/9), [CI 44936628150](https://github.com/maxgia/HOLO-RBQ/actions/runs/44936628150), codice `569ec22`: 36 Python, 11 Node, 15 Chromium superati, con nove test Python e un browser specifici su PostgreSQL reale. Preflight PowerShell Windows superato; migrazione e avvio completi sul PC utente ancora da collaudare.

A06 resta aperta per la ricerca del gestionale reale. D10 PostgreSQL precede la revisione UX/UI D09. Sette conferme utente sulla precedente versione restano evidenze storiche; PG-01–PG-05 sono nuove prove aperte.

## Documentazione

- [Migrazione, backup e ritorno alla versione precedente](HOLO%20RBQ/documentazione/Migrazione-PostgreSQL.md)
- [Avvio e aggiornamento](HOLO%20RBQ/documentazione/Runbook.md)
- [Piano generale](HOLO%20RBQ/documentazione/Piano-generale.md)
- [Specifica tecnica](HOLO%20RBQ/documentazione/Specifica-tecnica-HOLO-RBQ.md)
- [Registro Excel, 43 casi](HOLO%20RBQ/documentazione/HOLO-RBQ-Registro-test-2026-11-21.xlsx)
- [Evidenze dei test](HOLO%20RBQ/documentazione/Registro-collaudo-2026-11-21.md)
- [Piano UX/UI](HOLO%20RBQ/documentazione/Piano-UX-UI.md)

Il file SQLite rimane soltanto per migrazione, backup e fixture esplicite di test. Il runtime normale e il worker usano PostgreSQL. Non avviare il worker finche' non siano state riesaminate le pianificazioni trasferite.
