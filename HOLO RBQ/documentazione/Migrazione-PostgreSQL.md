# PostgreSQL e trasferimento dei dati HOLO — D10

Richiesta del 21 novembre 2026: sostituire SQLite con PostgreSQL prima della revisione UX/UI e trasferire tutti i dati dell'applicazione corrente. A06 (ricerca del gestionale reale) rimane aperta: PostgreSQL e' l'archivio di HOLO, non sostituisce TeamSystem/Buffetti o la scelta del gestionale.

## Stato e limite della consegna

La versione 0.3.0-postgres prepara runtime e migrazione. I test usano PostgreSQL 17 reale in CI e copie di prova che popolano tutte le tabelle. **L'archivio effettivo dell'utente non e' stato copiato in questa sessione:** non e' disponibile qui una copia aggiornata del suo file, ne' sono noti host, database e accessi PostgreSQL. Il trasferimento avviene sul suo PC, senza inviare i dati in chat o su GitHub.

Il file SQLite della cartella operativa e il backup sono conservati. Finche' non si esegue e verifica la procedura sul PC, la migrazione dei suoi dati rimane aperta. Non avviare il worker email durante il passaggio.

## Cosa viene trasferito

| Tabella | Dati conservati |
|---|---|
| clients | Identificativi, nomi, email e telefoni, inclusi clienti inseriti manualmente. |
| previews | Anteprime non ancora confermate, valori e riferimenti cliente. |
| drafts | Bozze, codici progressivi, importi, sconti, cliente e versione. |
| invoices | Numeri, cliente, date, importi e incassato. |
| demo_payments | Identificativi delle richieste e incassi registrati, per evitare duplicati. |
| follow_ups | Attivita', scadenze, completamento e documenti collegati. |
| edits | Modifiche in preparazione/confermate e controllo di concorrenza. |
| follow_up_emails | Destinatario, oggetto, testo, orari, stato, dettagli e residuo atteso. |

Importi in centesimi BIGINT, identificativi e date ISO restano invariati. Gli stati email sono copiati senza attivarli, annullarli o inviarli. I punteggi clienti sono ricalcolati sui dati, come prima. Codice e documentazione non sono righe del database e restano nel repository.

## Preparazione sul PC dell'utente

1. Identificare la cartella operativa che contiene i dati dei test, evitando copie ZIP vuote o vecchi backup. Il file atteso e' `codice-sorgente/data/holo.sqlite3`.
2. Fermare app e worker con Ctrl+C. Conservare una copia della cartella data e la versione 0.2.0-demo per eventuale ritorno.
3. Disporre di un server PostgreSQL e di un database **vuoto e dedicato**, ad esempio holo_rbq, con un utente proprietario che possa creare le tabelle. Versione verificata in CI: PostgreSQL 17. Non servono credenziali SMTP.
4. Aggiornare l'intera cartella dei sorgenti della versione PostgreSQL, conservando data e .venv. Non basta sostituire app.py e index.html: sono stati aggiunti moduli e dipendenze.

Se PostgreSQL non e' ancora installato, completare prima questo prerequisito. Host, porta, nome database e utente si possono comunicare per preparare le istruzioni; **la password si inserisce solo sul PC**, non in chat.

## Esecuzione guidata

Fare doppio clic su **Configura-Postgres.cmd**. Il programma prepara le dipendenze, chiede host, porta, database, utente e password nascosta. Confermare con MIGRA soltanto dopo aver fermato app e worker.

La procedura legge il file SQLite nella cartella operativa. Per una sorgente diversa, da PowerShell dopo la preparazione delle dipendenze:

```powershell
.\.venv\Scripts\python.exe migrate_to_postgres.py --configure --sqlite "C:\percorso\della\copia\holo.sqlite3"
```

Non inserire la password nel comando. In alternativa all'assistente locale, l'ambiente HOLO_DATABASE_URL puo' fornire una URL SQLAlchemy PostgreSQL; configurazioni e segreti non vanno aggiunti a GitHub.

## Controlli automatici e attivazione

1. Apertura SQLite in sola lettura, integrity_check e backup coerente tramite API SQLite, inclusi eventuali dati nel WAL.
2. Verifica delle otto tabelle e delle colonne note. Tabelle aggiuntive, riferimenti non validi o schemi legacy non supportati fermano il passaggio, evitando omissioni silenziose.
3. Creazione dello schema PostgreSQL in transazione, versione 1. Destinazioni con altre tabelle o dati esistenti vengono rifiutate.
4. Copia delle righe e confronto SHA-256 del contenuto canonico per ciascuna tabella, non soltanto dei conteggi. Riallineamento della sequenza dei progressivi bozze.
5. Registrazione della verifica in _holo_migrations e commit. Errori di copia causano rollback dei dati; nessun processo email viene eseguito.
6. Scrittura di `data/migration-report-*.json` con conteggi, digest, totali e percorso del backup. La configurazione `data/postgres.json` viene attivata **solo dopo la verifica**. Se la scrittura locale della configurazione fallisce dopo il commit, ripetere la configurazione: il caso identico e verificato e' riconosciuto senza duplicare righe.

La configurazione locale contiene la credenziale necessaria all'app: non e' cifrata. Su sistemi POSIX il file viene creato con permessi 0600; su Windows l'accesso dipende dalle ACL della cartella utente. File di configurazione, report e backup restano sotto data, esclusa da Git. Gestione centralizzata dei segreti e ruoli del pilota restano A09–A10.

Una seconda esecuzione identica con dati invariati viene verificata senza duplicazione. Se PostgreSQL e' gia' stato modificato dopo il trasferimento, la reimportazione viene rifiutata: non e' una sincronizzazione continua e non sovrascrive i nuovi dati.

## Primo avvio e accettazione

Dopo Migrazione verificata, fare doppio clic su Avvia-HOLO.cmd. La console deve indicare PostgreSQL 0.3.0-postgres; la password e' mascherata. Non esiste ripiego automatico su SQLite: configurazione mancante, server irraggiungibile o migrazione assente impediscono l'avvio con un messaggio esplicito.

Verificare PG-01–PG-05 nel registro Excel: clienti (compreso Cliente Test Analisi), bozze e versioni, fatture e incassi, attivita' e stati. Per Studio Rossi, se non sono stati registrati altri movimenti dopo l'ultimo collaudo, sono attesi incassato 1.400 euro, residuo 450, scaduto zero. Registrare un'ulteriore operazione di prova e verificare il riavvio e il progressivo della nuova bozza.

Non avviare il worker email finche' non sono state riesaminate eventuali pianificazioni ancora presenti. Il trasferimento conserva gli stati originali, compreso Programmata.

## Ritorno alla versione precedente

Il vecchio SQLite e il backup restano leggibili dalla versione 0.2.0-demo. Dopo nuove operazioni in PostgreSQL, SQLite e' una fotografia precedente: un ritorno automatico perderebbe la visibilita' dei nuovi movimenti. Per questo non viene effettuato alcun fallback. Un eventuale rientro dopo nuove scritture richiede riconciliazione o esportazione dedicata.

## Architettura e verifiche

Backend FastAPI invariato nei contratti; SQLAlchemy 2.0 e psycopg 3 per PostgreSQL. Le transazioni che modificano dati usano un advisory lock di progetto per mantenere la serializzazione della demo precedente; le letture aggregate usano snapshot ripetibile. E' una scelta per la scala MVP, da riesaminare per maggiori volumi. I pool vengono chiusi al termine del ciclo applicativo.

I percorsi SQLite espliciti di create_app(Path) restano solo per fixture, test di compatibilita' e lettura legacy. Avvio e worker normali richiedono PostgreSQL. Il preflight Windows verifica installazione dipendenze e mancata configurazione senza creare un nuovo SQLite. Il funzionamento completo su PostgreSQL viene verificato nel job PostgreSQL reale, inclusi API, concorrenza e browser.

Fonti tecniche: [SQLAlchemy e psycopg](https://docs.sqlalchemy.org/en/20/dialects/postgresql.html#module-sqlalchemy.dialects.postgresql.psycopg), [PostgreSQL advisory locks](https://www.postgresql.org/docs/17/functions-admin.html#FUNCTIONS-ADVISORY-LOCKS). [PR #9](https://github.com/maxgia/HOLO-RBQ/pull/9).
