# HOLO RBQ · MVP locale

Demo per freelance e partite IVA con anagrafiche fittizie. L’assistente interpreta richieste di esempio con regole predefinite. FastAPI valida e calcola il preventivo. SQLite conserva le bozze in `data/holo.sqlite3`.

## Avvio su Windows

Estrai lo ZIP. Apri PowerShell nella cartella `holo-rbq-local`, dove si trova `app.py`. Usa Python 3.10 o successivo.

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn app:create_app --factory --host 127.0.0.1 --port 8001
```

Apri [http://127.0.0.1:8001/](http://127.0.0.1:8001/). Premi **Ctrl+C** in PowerShell per fermare il server. La documentazione interattiva delle API è su [http://127.0.0.1:8001/docs](http://127.0.0.1:8001/docs).

## Prova del flusso

1. Premi **Usa una richiesta di esempio** e **Invia**. Scegli uno dei due clienti Rossi.
2. Premi **Mostra anteprima**. Con 800 € e sconto del 10% il totale atteso è 720 €.
3. Premi **Annulla anteprima** e controlla che l’elenco bozze non cambi.
4. Mostra di nuovo l’anteprima e salva la bozza. Riavvia il server con l’ultimo comando e ricarica la pagina. La bozza deve essere ancora presente.

## Tracciabilità di questo incremento

| Requisito | Modifica | Verifica |
|---|---|---|
| RBQ-01 · Cercare clienti fittizi | `GET /api/clients` e assistente nel frontend | Rossi restituisce due clienti |
| RBQ-02 · Validare e calcolare sul server | `POST /api/previews` | 800 € con sconto 10% produce 720 €. Cliente sconosciuto e sconto fuori intervallo vengono respinti |
| RBQ-03 · Annullare e salvare una sola bozza per anteprima | `DELETE /api/previews/{id}` e `PUT /api/drafts/{id}` | L’anteprima annullata non si può confermare. Conferme concorrenti restituiscono la stessa bozza |
| RBQ-04 · Conservare la bozza al riavvio | SQLite e `GET /api/drafts` | Una nuova istanza dell’applicazione legge la bozza dal medesimo database |

I controlli riportati sono stati eseguiti a livello API. Le bozze del prototipo precedente erano salvate nel browser. Questo MVP usa un nuovo archivio SQLite e non le importa. Il perimetro è locale e dimostrativo. Accessi utenti, integrazioni gestionali e orchestrazione multiagente sono fasi successive.

## Aggiornamento e modifica delle bozze

Ferma il server con Ctrl+C. Estrai l'archivio e copia i file aggiornati nella cartella esistente che contiene `app.py`, `data` e `.venv`. Conserva la cartella `data` per ritrovare le bozze. Riavvia con il comando Uvicorn indicato sopra e ricarica la pagina.

1. Nella chat scrivi «Mostrami i preventivi di Studio Rossi» oppure cerca «Rossi» nel campo **Bozze salvate**.
2. Premi **Apri** accanto al codice della bozza. Cambia lo sconto dal 10% al 20% se l'importo è 800 €.
3. Genera l'anteprima e conferma. Il totale atteso è 640 € e il codice resta lo stesso.
4. Riavvia il server e cerca lo stesso codice per verificare la persistenza.

| Requisito | Modifica | Verifica API |
|---|---|---|
| RBQ-05 · Ricercare e aprire una bozza | Filtro per cliente, oggetto o codice e dettaglio per codice | Ricerca su un database della versione precedente |
| RBQ-06 · Modificare una bozza dopo conferma | Anteprima di modifica e aggiornamento sullo stesso codice | Annullamento, retry, conflitto tra modifiche e persistenza dopo riavvio |

## Fatture, incassi e scadenze

Nella chat scrivi «Quali fatture di Rossi sono ancora da incassare?». La sezione **Fatture e scadenze** mostra tre fatture con un residuo complessivo di 1.200 €. La fattura F-001 mostra 800 € di importo, 300 € incassati e 500 € residui. Puoi cercare anche per numero e filtrare per stato.

Le fatture sono dimostrative e consultabili in sola lettura. Le scadenze sono fissate al primo avvio dell'aggiornamento e lo stato viene calcolato rispetto alla data del server.

| Requisito | Modifica | Verifica |
|---|---|---|
| RBQ-07 · Consultare fatture e scadenze | `GET /api/invoices`, filtri e ricerca dalla chat | Rossi con residuo restituisce tre fatture e 1.200 € |
| RBQ-08 · Visualizzare incassato e residuo | Importi in centesimi e stato calcolato sul server | F-001 mostra 500 € residui. Le fatture saldate hanno residuo zero |

## Guida operativa

In chat seleziona **Prova la guida**, poi **Invia**, oppure scrivi «Come registro un incasso?». La risposta indica i passaggi, il perimetro della demo e la voce della **Guida dimostrativa HOLO RBQ · v1**. Sono disponibili anche istruzioni per creare un preventivo, modificare una bozza e consultare le scadenze. Le domande riconosciute come richieste di guida e prive di una voce corrispondente ricevono un messaggio di mancata copertura.

La guida è redatta per la demo. La registrazione dell'incasso avviene nel gestionale. La demo mostra le fatture in sola lettura.

| Requisito | Modifica | Verifica |
|---|---|---|
| RBQ-09 · Rispondere con una procedura e la fonte | `guide.py`, `GET /api/guide` e risposta in chat | Quattro procedure, variante della domanda sull'incasso e richieste fuori perimetro verificate via API |

## Ricerca fatture con frasi equivalenti

«Cosa deve ancora pagare Rossi?» e «Quali fatture di Rossi sono ancora da incassare?» mostrano tre fatture per un residuo di 1.200 €. «Quanto resta da incassare da Studio Rossi?» mostra due fatture per 950 €. Il cognome Rossi include entrambi i clienti omonimi. Il nome completo restringe la ricerca. La chat riepiloga il risultato e la tabella mostra il dettaglio.

| Requisito | Modifica | Verifica |
|---|---|---|
| RBQ-10 · Capire più formulazioni per le fatture | Riconoscimento di frasi equivalenti nel frontend e riuso dell’API fatture | Otto formulazioni verificate in JavaScript, totali e risultato vuoto verificati via API |

## Incrementi successivi


## Incrementi demo e verifiche

| Incremento | Stato GitHub | Evidenza | Verifica manuale |
|---|---|---|---|
| Incassi e clienti | Integrato in main con [PR #2](https://github.com/maxgia/HOLO-RBQ/pull/2) | [CI 43398404064](https://github.com/maxgia/HOLO-RBQ/actions/runs/43398404064) | Inserimento manuale confermato. |
| Analisi tabellare e domande con Ollama | [PR #4](https://github.com/maxgia/HOLO-RBQ/pull/4) aperta verso main | [CI 43412370009](https://github.com/maxgia/HOLO-RBQ/actions/runs/43412370009) | Tabella verificata. Correzione residuo per singola fattura verificata in CI con classificatore simulato. |
| Attività e follow-up | [PR #5](https://github.com/maxgia/HOLO-RBQ/pull/5) aperta sul ramo della PR #4 | [CI 43414950861](https://github.com/maxgia/HOLO-RBQ/actions/runs/43414950861) | Modulo confermato dall'utente. |
| Solleciti programmati | [PR #6](https://github.com/maxgia/HOLO-RBQ/pull/6) aperta sul ramo della PR #5 | [CI 43419536920](https://github.com/maxgia/HOLO-RBQ/actions/runs/43419536920) | Pannello email da verificare sul PC dell'utente. Consegna SMTP reale da collaudare. |
| Usabilità demo | Protocollo nella [PR #3](https://github.com/maxgia/HOLO-RBQ/pull/3), consolidato in questa revisione documentale | [Protocollo](Collaudo-usabilita-demo.md) | Sessioni strutturate con 3–5 utenti rappresentativi da eseguire. |

La stima A06–A11 resta quella della precedente pianificazione. Attese per accessi al gestionale, collaudo SMTP e consolidamento dei rami vanno registrate al prossimo aggiornamento. Il prossimo passo sulla demo è diagnosticare la visibilità del pannello tramite la guida email e completare MAIL-01, MAIL-06 e MAIL-07.

Il 18 novembre 2026 è stata aggiunta l’apertura del pannello email nella nuova attività della scheda cliente. Il collaudo SMTP sul PC resta aperto. [PR #6](https://github.com/maxgia/HOLO-RBQ/pull/6)
