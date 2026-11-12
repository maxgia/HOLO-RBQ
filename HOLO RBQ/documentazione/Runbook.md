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
| RBQ-10 | «Cosa deve ancora pagare Rossi?» dà tre fatture e 1.200 €. «Quanto resta da incassare da Studio Rossi?» dà due fatture e 950 €. Un cliente assente restituisce un elenco vuoto. | Otto formulazioni in JavaScript e importi via API. Collaudo in browser da registrare |

## Verifiche tecniche svolte

- Demo HTML iniziale. Verificati in JavaScript disambiguazione, calcolo, annullamento e salvataggio singolo. La demo usa il browser per la persistenza. L'utente ha confermato l'avvio locale.
- Backend. Verificati ricerca clienti, dati non validi, anteprima annullata, 16 conferme concorrenti, retry e persistenza SQLite dopo riavvio. Verificato l'avvio HTTP su porta 8001 con risposta 200 per pagina iniziale e API clienti.
- Modifica. Verificati migrazione di un archivio della prima versione, ricerca, dettaglio, annullamento, retry, conflitto tra aggiornamenti, conservazione del codice e nuova lettura dopo riavvio.
- Fatture. Verificati filtri aperte, scadute e saldate, cliente assente, filtro invalido, residuo e stabilità dei dati al riavvio.
- Guida. Verificate quattro procedure, una formulazione alternativa, indicazione della fonte e domande fuori perimetro.
- Chat fatture. Verificate otto formulazioni in JavaScript, tre comandi esistenti esclusi dal riconoscimento fatture e risultati API per Rossi, Studio Rossi e cliente sconosciuto.

Fatture e anagrafiche sono dimostrative. Lo stato delle scadenze dipende dalla data del server. Il materiale operativo e i dettagli dei singoli incrementi sono in [Storico-MVP.md](Storico-MVP.md).
