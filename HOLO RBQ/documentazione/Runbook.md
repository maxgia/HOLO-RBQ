# Avvio locale e collaudo HOLO RBQ

## Prima installazione Windows

Apri PowerShell dentro `HOLO RBQ\codice-sorgente`, dove si trovano `app.py`, `guide.py`, `index.html` e `requirements.txt`. Usa Python 3.10 o successivo.

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn app:create_app --factory --host 127.0.0.1 --port 8001
```

Se `py` non è disponibile, usa `python -m venv .venv`. Apri [HOLO RBQ](http://127.0.0.1:8001/) dopo il messaggio di avvio di Uvicorn. Per fermare premi Ctrl+C. Per riavviare ripeti l'ultimo comando dalla stessa cartella. [Swagger UI](http://127.0.0.1:8001/docs) permette di provare le API.

## Aggiornamento e conservazione dati

Ferma il server. Se provieni dallo ZIP precedente, puoi copiare i sorgenti aggiornati nella cartella che contiene già `app.py`, oppure copiare la tua cartella `data` nella nuova cartella dei sorgenti mentre il server è fermo. Conserva una copia del database `data\holo.sqlite3`. Riavvia e ricarica il browser con Ctrl+F5. Un nuovo percorso senza `data` inizializza un nuovo archivio. Un 404 di `favicon.ico` riguarda l'icona del browser. Se mancano le bozze, consulta [l'API delle bozze](http://127.0.0.1:8001/api/drafts) e verifica il percorso del database.

## Collaudi funzionali

| ID | Passi e risultato atteso | Evidenza storica |
|---|---|---|
| RBQ-01–04 | Usa la richiesta di esempio. Seleziona uno dei due Rossi. Anteprima di 800 € con sconto 10% produce 720 €. Annulla e verifica che l'archivio non cambi. Rigenera, conferma e riavvia. La bozza resta visibile. | API e prova locale sul PC dell'utente |
| RBQ-05–06 | Cerca Rossi in Bozze salvate o chiedi «Mostrami i preventivi di Studio Rossi». Apri la bozza da 800 €, applica 20%, conferma e riavvia. Stesso codice, 640 €. | API e prova locale sul PC dell'utente |
| RBQ-07–08 | Chiedi «Quali fatture di Rossi sono ancora da incassare?». Attese tre fatture e 1.200 € di residuo. F-001 ha 300 € incassati e 500 € residui. Controlla filtri scadute e saldate. | API e prova locale sul PC dell'utente |
| RBQ-09 | Premi Prova la guida e invia «Come registro un incasso?». Verifica passaggi, indicazione del gestionale e fonte Guida dimostrativa HOLO RBQ · v1. Prova anche creazione e modifica bozza, scadenze e una richiesta fuori copertura. | Quattro procedure e richieste fuori copertura via API. L'utente ha confermato il funzionamento della guida |
| RBQ-10 | «Cosa deve ancora pagare Rossi?» dà tre fatture e 1.200 €. «Quanto resta da incassare da Studio Rossi?» dà due fatture e 950 €. Un cliente assente restituisce un elenco vuoto. | Otto formulazioni in JavaScript e importi via API. Collaudo browser delle formulazioni equivalenti superato |

## Verifiche tecniche svolte

- Demo HTML iniziale. Verificati in JavaScript disambiguazione, calcolo, annullamento e salvataggio singolo. La demo usa il browser per la persistenza. L'utente ha confermato l'avvio locale.
- Backend. Verificati ricerca clienti, dati non validi, anteprima annullata, 16 conferme concorrenti, retry e persistenza SQLite dopo riavvio. Verificato l'avvio HTTP su porta 8001 con risposta 200 per pagina iniziale e API clienti.
- Modifica. Verificati migrazione di un archivio della prima versione, ricerca, dettaglio, annullamento, retry, conflitto tra aggiornamenti, conservazione del codice e nuova lettura dopo riavvio.
- Fatture. Verificati filtri aperte, scadute e saldate, cliente assente, filtro invalido, residuo e stabilità dei dati al riavvio.
- Guida. Verificate quattro procedure, una formulazione alternativa, indicazione della fonte e domande fuori perimetro.
- Chat fatture. Verificate otto formulazioni in JavaScript, tre comandi esistenti esclusi dal riconoscimento fatture e risultati API per Rossi, Studio Rossi e cliente sconosciuto.

Fatture e anagrafiche sono dimostrative. Lo stato delle scadenze dipende dalla data del server. Il materiale operativo e i dettagli dei singoli incrementi sono in [Storico-MVP.md](Storico-MVP.md).

## Regressione automatizzata

Da PowerShell in `HOLO RBQ\codice-sorgente`, con l'ambiente virtuale già creato, esegui:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-test.txt
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
node --test tests/chat.test.cjs
```

Per la suite JavaScript serve Node.js 18 o successivo. Il server locale può essere spento durante i test. Risultato atteso: 7 test Python e 11 test Node superati. I test Node verificano il riconoscimento delle frasi in un ambiente simulato. Per le prove dell'interfaccia usa i passi del collaudo funzionale.

## Test end-to-end dei preventivi nel browser

Requisiti RBQ-01–06. Il test avvia Uvicorn su una porta libera con un database temporaneo. Verifica richiesta di esempio, scelta cliente, creazione a 720 €, ricerca, modifica a 640 €, mantenimento del codice e rilettura dopo arresto e nuovo avvio del server.

Da PowerShell, nella cartella dei sorgenti:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-e2e.txt
.\.venv\Scripts\python.exe -m playwright install chromium
.\.venv\Scripts\python.exe -m unittest discover -s e2e -v
```

La suite è configurata anche in GitHub Actions, con i test Python e Node. Per registrare un esito, annotare commit, ambiente e risultato o link al run. Per dipendenze e traguardi consultare il [piano generale](Piano-generale.md).

Esito del 12 novembre 2026: [GitHub Actions · run 43237001468](https://github.com/maxgia/HOLO-RBQ/actions/runs/43237001468) sul commit `97c0cfa`. Passati 7 test Python, 11 test Node e il test browser Chromium.

## Test end-to-end di fatture e guida operativa

Lo stesso comando della suite browser esegue anche i test RBQ-07–10. Per le fatture verifica richieste equivalenti in chat, filtro per cliente, scadute, saldate, importo residuo e ricerca senza risultati. Per la guida verifica i passaggi per registrare un incasso, la fonte e la risposta a una domanda fuori copertura.

Esito del 12 novembre 2026: [GitHub Actions · run 43239189016](https://github.com/maxgia/HOLO-RBQ/actions/runs/43239189016) sul commit `c0d5e88`. Superati 7 test API, 11 test JavaScript e 3 test browser Chromium.

## Annullamento dell’anteprima nel browser

Il test RBQ-03 genera un’anteprima con dati dimostrativi, la annulla e verifica che il pulsante di salvataggio sia disabilitato. Controlla la risposta HTTP 204 alla cancellazione, il rifiuto HTTP 404 di un successivo tentativo di salvare la stessa anteprima e l’archivio vuoto dopo il ricaricamento. Si esegue con lo stesso comando della suite browser e usa un database temporaneo.

Esito del 12 novembre 2026: [GitHub Actions · run 43239996580](https://github.com/maxgia/HOLO-RBQ/actions/runs/43239996580) sul commit `2c4773f`. Superati 7 test API, 11 test JavaScript e 4 test browser Chromium.

## Interfaccia MVP con navigazione laterale

La barra laterale apre Assistente, Preventivi, Bozze salvate, Fatture e scadenze e Guida operativa. Il riepilogo mostra gli importi da incassare e scaduti, oltre al numero delle bozze salvate. Le API di FastAPI alimentano le schermate e le bozze restano nell’archivio SQLite. Il collaudo browser verifica anche importi del riepilogo, navigazione e avvio della guida dalla barra laterale. [Verifiche della pull request #1](https://github.com/maxgia/HOLO-RBQ/pull/1/checks)

## Incassi dimostrativi

In Fatture e scadenze seleziona F-001 e registra 100 €. Su un database appena inizializzato il residuo passa da 500 € a 400 €. Al ricaricamento il nuovo residuo resta disponibile. La registrazione aggiorna il database locale dimostrativo. Il test API verifica persistenza, incassi parziali, saldo, importi non validi e ripetizione della richiesta. Il test browser verifica registrazione, riepilogo e rilettura del residuo.

## Anagrafica clienti dimostrativa

Apri **Clienti** e cerca Rossi. La scheda **Studio Rossi** mostra le fatture F-001, F-002 e F-004 e, su un database appena inizializzato, 950 € di residuo. La scheda **Martina Rossi** mostra F-003 e 250 €. Le bozze si aprono dalla scheda del cliente. La scheda si aggiorna dopo un salvataggio o un incasso demo. L’anagrafica usa i clienti dimostrativi esistenti e consente di inserire nuovi clienti. Il collaudo verifica separazione degli omonimi, collegamento alle bozze e importi residui.

### Inserire un cliente

In **Clienti → Nuovo cliente** inserisci il nome o la ragione sociale. Email e telefono sono facoltativi. Dopo **Salva cliente** si apre la scheda e il cliente è selezionabile nei preventivi. Usa una denominazione distinta se esiste già un cliente con lo stesso nome. I dati sono salvati nell’archivio SQLite locale. Al primo avvio l’app aggiorna il database e associa ai clienti dimostrativi le bozze già presenti.
