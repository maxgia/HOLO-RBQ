# Avvio locale e collaudo HOLO RBQ

### Applicare la correzione a una copia ZIP già funzionante

Rispetto alla versione con Analisi clienti già in funzione, questa correzione modifica i file di esecuzione `app.py` e `index.html`; non richiede nuove dipendenze. Fermare server e worker, scaricare lo ZIP aggiornato del ramo `feat/analisi-portafoglio-clienti`, estrarlo separatamente e copiare questi due file dalla sua cartella `HOLO RBQ/codice-sorgente` nella cartella `codice-sorgente` usata sul PC. Conservare `data`, `.venv` e gli altri moduli. Riavviare con il comando Uvicorn abituale. Al primo caricamento usare Ctrl+F5 una volta se necessario; dopo un ulteriore riavvio verificare con F5 normale (AC-10). In alternativa installare la nuova copia completa conservando i dati come già descritto nel runbook.

## Aggiornamento dopo il collaudo utente del 21 novembre 2026

**Esiti manuali confermati: AC-01–AC-06.** Verificati valore (Studio Rossi 100), criticità (Martina 71 con F-003 scaduta da 2 giorni), ricerca e omonimi, saldo F-001 di 500 euro con residuo Studio Rossi a 450 euro e scaduto/criticità zero, persistenza anche dopo riavvio e nuovo cliente senza storico. Le prove Ollama reali sul PC dell'utente hanno prodotto verifica incassi per Martina e continuità del rapporto per Studio Bianchi. Modello e SHA della copia ZIP non rilevati; queste prove non certificano la qualità su altri casi. AC-08 è parziale: navigazione verificata, tastiera e finestra stretta ancora da provare.

Il segnale osservato (Analisi clienti ricompare dopo Ctrl+F5) è compatibile con cache HTML, ma la causa sul browser dell'utente non è stata dimostrata. Il nuovo `app.py` serve `/` con **Cache-Control: no-store**. Questo evita nuove copie in cache; non ricarica automaticamente le schede aperte né elimina retroattivamente copie già conservate. Dopo il primo aggiornamento può servire Ctrl+F5 una volta, poi basta un normale F5. La pagina deve essere comunque ricaricata dopo un riavvio se già aperta.

La colonna **Posizione** ora mostra **Non classificato** solo in assenza di punteggio. Nessuna nuova colonna; punteggi non disponibili restano “—”, classifiche e parità rimangono invariate. Requisiti di affinamento RF-18 (cache HTML) e RF-19 (etichetta senza storico).

Codice fix `59b8907ef35629b3e963785ef3795dd245315df5`, [CI 44900599652](https://github.com/maxgia/HOLO-RBQ/actions/runs/44900599652): **20 Python, 11 Node e 14 Chromium superati**. Il test API verifica file HTML aggiornato dopo nuova istanza e richiesta condizionale; Chromium verifica reload normale e dicitura del nuovo cliente. Nessun invio SMTP reale. I test simulati del modello restano distinti dalle prove reali dell'utente.

L'[Excel aggiornato](HOLO-RBQ-Registro-test-2026-11-21.xlsx) contiene **37 casi**, con sei nuovi esiti umani Superato e un caso In corso. **AC-10** registra il collaudo pendente del fix cache e dell'etichetta Non classificato. AC-07 (modello assente), parte di AC-08 e controlli tecnici AC-09 restano aperti nel registro umano; AC-09 è già coperto automaticamente. Le sezioni con la prima consegna sotto sono evidenze storiche.


## Ripresa del 21 novembre 2026 — sole funzioni interne

Il nuovo modulo **Analisi clienti** si trova sul ramo `feat/analisi-portafoglio-clienti`, [PR #8](https://github.com/maxgia/HOLO-RBQ/pull/8); non è ancora su main. La suite su codice `c40639f` è verde: [19 Python, 11 Node, 13 Chromium](https://github.com/maxgia/HOLO-RBQ/actions/runs/44881200826). Leggere [specifica e limiti del confronto](Analisi-portafoglio-clienti.md) e compilare l'[Excel di ripresa](HOLO-RBQ-Registro-test-2026-11-21.xlsx).

Con server e worker fermi, conservare una copia della cartella `data`. Da una copia Git già installata, senza modifiche locali da preservare, nella cartella `HOLO RBQ\codice-sorgente`:

```powershell
git fetch origin
git switch feat/analisi-portafoglio-clienti
git pull --ff-only origin feat/analisi-portafoglio-clienti
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn app:create_app --factory --host 127.0.0.1 --port 8002
```

Se Git segnala modifiche locali, conservarle prima di cambiare ramo. Non usare reset o eliminazione della cartella dati per aggiornare. Per una prima installazione creare l'ambiente come descritto sotto. Per una copia ZIP scaricare il ramo corretto da GitHub e conservare separatamente i dati già usati.

Aprire [l'app locale](http://127.0.0.1:8002/) e premere Ctrl+F5. Nel menu **Analisi clienti**, provare valore, criticità, ricerca, **Analizza** e **Apri scheda cliente**. La classifica e l'azione da regole funzionano senza Ollama. Il pulsante AI usa soltanto il modello locale già installato e mostra un errore gestito se assente. Non avviare `follow_up_email.py`: i nuovi test non richiedono SMTP.

### Archivio di collaudo separato

Per verificare gli importi attesi senza modificare il database di lavoro, usare una seconda copia di collaudo sulla porta 8003. Dalla stessa cartella, questo comando crea un nuovo database distinto se il percorso non esiste:

```powershell
.\.venv\Scripts\python.exe -c "from pathlib import Path; from app import create_app; import uvicorn; uvicorn.run(create_app(Path('data-collaudo/analisi-20261121.sqlite3')), host='127.0.0.1', port=8003)"
```

Aprire [la copia di collaudo](http://127.0.0.1:8003/). Su un archivio nuovo Studio Rossi ha fatturato 1.850 euro, incassato 900, residuo 950, scaduto 500; valore 100 e criticità 43. Seguire AC-01–03 prima del saldo AC-04. Riutilizzare lo stesso percorso per verificare persistenza; usare un nome distinto per una nuova inizializzazione, senza cancellare archivi esistenti.

Nel foglio **Test** filtrare Ambito = Interno e compilare G:J per ogni nuova prova; il foglio **Passi** contiene il caso con lo stesso ID. Le conferme storiche non cambiano automaticamente in base ai nuovi test automatici. La prova reale Ollama e la valutazione di usabilità restano aperte; T04 è un difetto noto ancora da correggere.

Per il ramo da provare e i relativi esiti, consulta il [piano generale](Piano-generale.md). Incassi e Clienti sono su main. Le sezioni Analizza cliente, Attività e follow-up ed Email descrivono incrementi disponibili sui rispettivi rami di sviluppo.

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

Per la suite JavaScript serve Node.js 18 o successivo. Il server locale può essere spento durante i test. Sul ramo `feat/analisi-portafoglio-clienti` il risultato atteso è 19 test Python e 11 test Node superati; la suite browser completa esegue 13 test. I test Node verificano il riconoscimento delle frasi in un ambiente simulato. Per le prove dell'interfaccia usa i passi del collaudo funzionale.

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

## Analizza cliente

Apri **Clienti**, cerca **Studio Rossi**, apri la scheda e seleziona **Analizza cliente**. Su un archivio demo appena inizializzato la tabella **Indicatore / Valore** mostra bozze, fatture aperte e scadute, 950 € complessivi e la F-001 con scadenza, motivo della priorità e residuo di 500 €. **Apri fattura** porta alla riga corrispondente. **Prepara sollecito** genera una bozza locale modificabile tramite un modello di testo, con numero, data e residuo. Nessun invio è previsto.

Le fatture aperte sono ordinate per scadenza. La fattura scaduta da più tempo ha priorità. Se tutte le fatture aperte sono ancora nei termini, viene proposta la prossima scadenza. La sintesi usa i dati della scheda e regole locali.

Il collaudo browser verifica il passaggio a 400 € sulla F-001 e 850 € complessivi dopo un incasso demo di 100 €, la separazione di Martina Rossi e il messaggio per i nuovi clienti senza bozze o fatture. Eseguire la suite browser con i comandi indicati sopra.


### Domande sulla scheda con Ollama

Installa [Ollama per Windows](https://ollama.com/download/windows) e avvialo. In PowerShell scarica il modello con `ollama pull qwen2.5:3b`. Riavvia HOLO RBQ con il comando di avvio abituale. Per scegliere un altro modello locale già scaricato, imposta `$env:HOLO_OLLAMA_MODEL = "nome-modello"` prima di avviare Uvicorn.

In **Clienti → Studio Rossi → Analizza cliente**, usa **Fai una domanda su questo cliente**. Esempi: «Quanto resta da incassare?», «Quale fattura devo gestire per prima?» e «Scrivi un sollecito cordiale per F-001». Il modello locale classifica soltanto la domanda. FastAPI usa i dati della scheda selezionata per comporre importi, scadenze e bozze. L'app chiama Ollama su 127.0.0.1:11434. La bozza è modificabile nella scheda.

La regressione automatica usa un classificatore simulato e verifica che, dopo un incasso demo di 100 €, la bozza riporti 400 € per F-001. Verifica anche che la stessa fattura non sia esposta nella scheda Martina Rossi e che un nuovo cliente mostri l'assenza di storico. Il collaudo con il modello reale si esegue con le domande di esempio dopo aver installato Ollama.

Per verificare la distinzione tra residuo del cliente e residuo della fattura, chiedi «Quanto resta da incassare?» e poi «Quanto resta da incassare sulla fattura F-001?». Su un archivio demo appena inizializzato, Studio Rossi mostra rispettivamente 950 € e 500 €. Dopo un incasso demo di 100 € sulla F-001, il residuo della fattura è 400 €. Il test di regressione simula il caso in cui Ollama classifichi entrambe le domande come richieste di saldo complessivo.

## Attività e follow-up

Dalla scheda cliente, apri **Nuovo follow-up**, inserisci titolo e data e scegli facoltativamente una fattura o una bozza del cliente. In **Studio Rossi → Analizza cliente → Pianifica follow-up**, l’app propone F-001 su un archivio demo appena inizializzato. La data è scelta dall’utente e **Salva follow-up** registra l’attività in SQLite. La funzionalità richiede soltanto il server HOLO RBQ.

In **Attività**, usa i filtri **Oggi**, **Scadute**, **In programma** e **Completate**. I filtri usano la data locale del server. Per riprogrammare un’attività aperta, modifica **Nuova data** e premi **Riprogramma**. Puoi completare il follow-up sia dalla vista generale sia dalla scheda cliente.

Il test browser crea un follow-up per F-001 con data passata, ricarica la pagina, verifica il filtro **Scadute**, lo sposta in **In programma** e lo chiude dalla scheda cliente. Per eseguire la suite usa i comandi del collaudo browser riportati sopra.

## Solleciti email programmati

Per casella di prova, worker SMTP e prove di sospensione e annullamento, segui il [collaudo email](Collaudo-email-follow-up.md). Per interviste e prove con prospect, usa il [protocollo demo](Collaudo-usabilita-demo.md).

Dopo aver salvato un nuovo follow-up, cerca le opzioni email nella nuova attività della scheda cliente. Se il destinatario di prova è configurato e l’attività è programmabile, il pannello si apre automaticamente. [Collaudo email](Collaudo-email-follow-up.md)


