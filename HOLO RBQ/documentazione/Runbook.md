# Avvio e aggiornamento HOLO RBQ

## Collaudo del 22 novembre 2026

Migrazione sul PC Windows e primo avvio PostgreSQL confermati dall’utente. Copiate e verificate otto tabelle: 4 clienti, 0 anteprime, 1 bozza, 5 fatture, 1 incasso, 0 follow-up, 1 modifica, 0 email. Assenza dei follow-up accettata. PG-01–02 Superato; PG-03 e AC-11 In corso; PG-04–05 ancora da eseguire sul PC.

[CI 45037721777](https://github.com/maxgia/HOLO-RBQ/actions/runs/45037721777), codice `bc20dfc`: 34 prove funzionali originali rieseguite su PostgreSQL (20 Python e 14 Chromium), tutte superate. Superati anche nove test PostgreSQL specifici, i controlli di configurazione e launcher, gli 11 Node e la regressione SQLite. Sender e AI simulati; nessun accesso al database operativo e nessun invio reale. [Report per caso](Regressione-PostgreSQL-2026-11-22.md).

Registro Excel: 43 casi, 9 nuovi esiti umani Superato complessivi. Le sette conferme precedenti restano storiche. D10 in collaudo; D09 UX/UI segue questo passaggio; A06 resta aperta. Le indicazioni del 21 novembre sul trasferimento ancora da eseguire descrivono lo stato precedente.

## Passaggio PostgreSQL — versione 0.3.0

Prima di usare questa versione completare la [migrazione guidata](Migrazione-PostgreSQL.md) con **Configura-Postgres.cmd**, a server e worker fermi. Serve un database PostgreSQL vuoto e dedicato; l'assistente prepara le dipendenze e chiede i parametri localmente. Il file sorgente e' data/holo.sqlite3 della cartella operativa corrente.

Avvia-HOLO.cmd ora richiede PostgreSQL configurato e una migrazione verificata: non crea un SQLite di ripiego. La password resta nella configurazione locale esclusa da Git. Il trasferimento dei dati effettivi dell'utente non e' ancora stato eseguito in questa sessione; le prove CI usano archivi di collaudo completi. Verificare PG-01–PG-05 prima di riprendere la UX/UI; A06 rimane aperta.

Il codice comprende nuovi moduli e dipendenze: aggiornare l'intera cartella dei sorgenti, conservando data e .venv; la precedente correzione di due file non basta. Per un eventuale ritorno conservare la 0.2 e il backup, ricordando che le nuove scritture PostgreSQL non sono riportate nel vecchio SQLite. Le sezioni seguenti descrivono la consegna 0.2 precedente.


Riferimento: demo consolidata **0.2.0-demo**, ramo di consegna **main** dopo il merge della [PR #8](https://github.com/maxgia/HOLO-RBQ/pull/8). I comandi storici sono conservati nel [runbook precedente](Runbook-storico-20261121.md).

## Una cartella di lavoro riconoscibile

Usare una sola cartella operativa contenente `HOLO RBQ/codice-sorgente`. Conservare le altre copie come backup, senza avviare contemporaneamente server da copie diverse. Il launcher mostra versione, percorso dei sorgenti, database e indirizzo del browser.

## Aggiornare una copia gia' funzionante

1. Fermare Uvicorn e l'eventuale worker email con Ctrl+C. Conservare una copia della cartella `data`.
2. Scaricare **Code → Download ZIP** da [main](https://github.com/maxgia/HOLO-RBQ/tree/main), poi estrarre completamente lo ZIP in una cartella separata.
3. Copiare il contenuto aggiornato di `HOLO RBQ/codice-sorgente` nella cartella operativa, sostituendo i sorgenti. Conservare `data` e `.venv` della copia operativa. Non avviare il programma direttamente dentro lo ZIP.
4. Fare doppio clic su **Avvia-HOLO.cmd**, dentro `codice-sorgente`.

Per una nuova installazione estrarre l'intero ZIP. Se si vogliono ritrovare i dati precedenti, copiare prima la vecchia cartella `data` nei nuovi sorgenti con i processi fermi. Senza quei dati viene inizializzato un nuovo archivio demo.

## Cosa fa il doppio clic

- Cerca o crea l'ambiente `.venv` nella stessa cartella dei sorgenti. Richiede Python 3.10 o successivo.
- Installa le dipendenze al primo avvio o se cambia requirements.txt; questa preparazione richiede accesso Internet. Se il file non cambia non reinstalla.
- Usa esclusivamente il database `data/holo.sqlite3` accanto ai sorgenti. Non cancella o sposta gli archivi esistenti.
- Avvia il server su `127.0.0.1:8002` e apre il browser quando il server e' pronto.
- Non avvia il worker email e non esegue integrazioni esterne.
- Se la porta e' occupata, mostra un errore e non apre una diversa copia dell'applicazione.

Lasciare aperta la finestra del server. Per fermarlo premere **Ctrl+C**. Per ripartire fare nuovamente doppio clic. Una scheda gia' aperta va ricaricata con F5; per eliminare un vecchio HTML precedente alla correzione cache puo' servire Ctrl+F5 una prima volta.

## Porta diversa o apertura manuale del browser

Da PowerShell nella cartella dei sorgenti:

```powershell
.\Avvia-HOLO.cmd -Port 8003
.\Avvia-HOLO.cmd -NoBrowser
```

Eseguire un comando alla volta. Con -NoBrowser aprire manualmente http://127.0.0.1:8002/. Non terminare processi sconosciuti per liberare la porta: chiudere la precedente finestra del server o scegliere una porta diversa.

L'avvio manuale precedente resta disponibile:

```powershell
.\.venv\Scripts\python.exe -m uvicorn app:create_app --factory --host 127.0.0.1 --port 8002
```

## Collaudo AC-11 da eseguire sul PC dell'utente

1. Dopo l'aggiornamento fare doppio clic su Avvia-HOLO.cmd e attendere l'apertura del browser.
2. Verificare che il percorso stampato sia quello operativo e che siano presenti Cliente Test Analisi e gli importi salvati.
3. Chiudere il server con Ctrl+C, riavviare dal file e verificare persistenza e reload normale.
4. Con il primo server attivo, provare una seconda apertura: deve segnalare porta occupata senza avviare un'altra copia.
5. Registrare risultato, data, versione 0.2.0-demo e percorso usato nell'Excel. L'apertura automatica del browser e l'arresto interattivo restano da verificare manualmente sul PC.

La CI Windows ha gia' verificato preparazione, avvio da un'altra cartella con spazi, porta occupata, riavvio e persistenza senza browser o email. Non sostituisce il collaudo del doppio clic sul desktop dell'utente.

## Ripetere i test automatici

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-e2e.txt
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
node --test tests/chat.test.cjs
.\.venv\Scripts\python.exe -m playwright install chromium
.\.venv\Scripts\python.exe -m unittest discover -s e2e -v
```

Attesi **25 Python, 11 Node e 14 Chromium**. Il test Windows aggiuntivo viene eseguito dalla CI con `python tests/windows_launcher_smoke.py`; lavora su una copia temporanea e non sul database dell'utente.

Per casi funzionali e storico consultare il [registro](Registro-collaudo-2026-11-21.md), l'[Excel](HOLO-RBQ-Registro-test-2026-11-21.xlsx) e le [specifiche](Specifica-tecnica-HOLO-RBQ.md). Il [protocollo di usabilita'](Collaudo-usabilita-demo.md) alimentera' la [revisione UX/UI](Piano-UX-UI.md). A06 rimane aperta per la ricerca del gestionale reale.

