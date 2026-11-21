# Specifica tecnica HOLO RBQ

## Aggiornamento dopo il collaudo utente del 21 novembre 2026

**Esiti manuali confermati: AC-01–AC-06.** Verificati valore (Studio Rossi 100), criticità (Martina 71 con F-003 scaduta da 2 giorni), ricerca e omonimi, saldo F-001 di 500 euro con residuo Studio Rossi a 450 euro e scaduto/criticità zero, persistenza anche dopo riavvio e nuovo cliente senza storico. Le prove Ollama reali sul PC dell'utente hanno prodotto verifica incassi per Martina e continuità del rapporto per Studio Bianchi. Modello e SHA della copia ZIP non rilevati; queste prove non certificano la qualità su altri casi. AC-08 è parziale: navigazione verificata, tastiera e finestra stretta ancora da provare.

Il segnale osservato (Analisi clienti ricompare dopo Ctrl+F5) è compatibile con cache HTML, ma la causa sul browser dell'utente non è stata dimostrata. Il nuovo `app.py` serve `/` con **Cache-Control: no-store**. Questo evita nuove copie in cache; non ricarica automaticamente le schede aperte né elimina retroattivamente copie già conservate. Dopo il primo aggiornamento può servire Ctrl+F5 una volta, poi basta un normale F5. La pagina deve essere comunque ricaricata dopo un riavvio se già aperta.

La colonna **Posizione** ora mostra **Non classificato** solo in assenza di punteggio. Nessuna nuova colonna; punteggi non disponibili restano “—”, classifiche e parità rimangono invariate. Requisiti di affinamento RF-18 (cache HTML) e RF-19 (etichetta senza storico).

Codice fix `59b8907ef35629b3e963785ef3795dd245315df5`, [CI 44900599652](https://github.com/maxgia/HOLO-RBQ/actions/runs/44900599652): **20 Python, 11 Node e 14 Chromium superati**. Il test API verifica file HTML aggiornato dopo nuova istanza e richiesta condizionale; Chromium verifica reload normale e dicitura del nuovo cliente. Nessun invio SMTP reale. I test simulati del modello restano distinti dalle prove reali dell'utente.

L'[Excel aggiornato](HOLO-RBQ-Registro-test-2026-11-21.xlsx) contiene **37 casi**, con sei nuovi esiti umani Superato e un caso In corso. **AC-10** registra il collaudo pendente del fix cache e dell'etichetta Non classificato. AC-07 (modello assente), parte di AC-08 e controlli tecnici AC-09 restano aperti nel registro umano; AC-09 è già coperto automaticamente. Le sezioni con la prima consegna sotto sono evidenze storiche.


## Stato corrente — 21 novembre 2026

Requisiti aggiunti oggi: RF-14 confronto portafoglio, RF-15 azioni AI interne, RF-16 registro dei collaudi e RF-17 esclusione di nuove interazioni esterne. [Specifica di dettaglio del modulo](Analisi-portafoglio-clienti.md), [piano aggiornato](Piano-generale.md), [Excel con 36 casi](HOLO-RBQ-Registro-test-2026-11-21.xlsx). Il ramo della PR #8 include i sorgenti e la documentazione consolidata, mentre l'integrazione in main resta aperta.

Evidenza automatica sul commit `c40639f`: [CI 44881200826](https://github.com/maxgia/HOLO-RBQ/actions/runs/44881200826), 19 test Python, 11 Node e 13 Chromium superati. Email e AI simulate; modello reale non disponibile nell'ambiente. Nessuna nuova prova SMTP, usabilità con utenti o attestazione di conformità. Le sezioni datate sotto conservano la cronologia: pannello email, consegna reale e sospensione per saldo sono stati confermati dall'utente il 20 novembre. Restano aperti T04 e i casi indicati nel registro.

**Rilevazione del 13 novembre 2026.** Baseline integrata `main` a `90b2cdf`. Baseline demo più estesa `feat/follow-up-email` a `a6464cd`, che include i rami di analisi cliente e follow-up. I risultati della demo e gli stati di integrazione sono riportati nel [piano generale](Piano-generale.md).

## Obiettivi e contesto

HOLO RBQ supporta freelance e titolari di partita IVA nella preparazione dei preventivi, nella consultazione di fatture e incassi, nella gestione dei clienti e nella pianificazione dei ricontatti. L'MVP locale usa dati demo per le presentazioni ai prospect. La fase successiva prevede un pilota con una partita IVA o azienda di prova e un gestionale reale. TeamSystem e Buffetti sono ipotesi espresse dall'utente. Selezione del prodotto, disponibilità API e azienda di test rientrano in A06, rinviata. Il codice legacy di Holo e la demo esistente sono riferimenti per la ricostruzione delle funzioni.

## Requisiti raccolti e criteri di accettazione

| ID | Requisito | Realizzazione e prova |
|---|---|---|
| RF-01 | Preparare un preventivo, controllarne l'anteprima, annullare o salvare una bozza, poi recuperarla e modificarla. | Su main. Verificare 800 € con sconto 10% → 720 €, modifica al 20% → 640 €, stesso codice e persistenza al riavvio. |
| RF-02 | Consultare fatture e scadenze per cliente, numero o stato, anche con frasi equivalenti. Registrare incassi demo parziali e a saldo. | Su main. F-001 passa da 500 € a 400 € dopo un incasso demo di 100 €. |
| RF-03 | Consultare la guida operativa in modo contestuale. | Su main. La risposta riporta la fonte della guida e segnala le domande fuori copertura. |
| RF-04 | Usare un'interfaccia ispirata a Linear con navigazione tra moduli. | Su main. Verifica browser di navigazione e riepilogo. |
| RF-05 | Consultare l'anagrafica e inserire manualmente un cliente. | Su main. Nome obbligatorio, email e telefono facoltativi. Verificare persistenza, uso nei preventivi e separazione tra Studio Rossi e Martina Rossi. L'inserimento è stato confermato dall'utente. |
| RF-06 | Analizzare il cliente in forma tabellare e poter aprire la fattura prioritaria o preparare una bozza di sollecito. | PR #4. Colonne Indicatore e Valore, conteggi, totale residuo, fattura prioritaria, motivo, scadenza e residuo. Il nuovo cliente senza dati mostra un messaggio dedicato. |
| RF-07 | Fare domande in italiano sulla scheda cliente, distinguendo il totale dal residuo di una fattura citata. Preparare una bozza con tono adattabile. | PR #4. Test con «Quanto resta da incassare sulla fattura F-001?» anche se il classificatore restituisce l'intento di totale. Controllare la scheda corretta e l'importo corrente. |
| RF-08 | Creare follow-up con titolo e data dalla scheda cliente, con collegamento facoltativo a fattura o preventivo. | PR #5. Da una fattura scaduta, Pianifica follow-up propone titolo e documento. L'utente sceglie la data e salva. |
| RF-09 | Consultare le attività per stato, riprogrammarle e completarle. | PR #5. Filtri Tutte, Oggi, Scadute, In programma e Completate. Collaudo browser su F-001 dopo ricarica. L'utente ha confermato il modulo in locale. |
| RF-10 | Scegliere se programmare un'email, modificare oggetto e testo, indicare data e ora, riprogrammare o annullare prima dell'invio. | PR #6. Per il collaudo, destinatario unico configurato e in sola lettura nel pannello. Gli stati sono consultabili in Attività. |
| RF-11 | Verificare automaticamente l'avvenuto saldo tra pianificazione e invio, sospendere il sollecito e chiedere all'utente di annullarlo. | PR #6. Avviso in app, stato Sospesa · fattura saldata e azione Annulla sollecito. Se il residuo varia e resta positivo, il worker richiede revisione. |
| RF-12 | Inviare esclusivamente dalle 09:00 alle 20:00 del giorno pianificato, con possibilità di annullamento fino alla presa in carico. | PR #6. Finestra implementata come 09:00 inclusa e 20:00 esclusa, fuso Europe/Rome. Se superata, serve ripianificare. |
| RF-13 | Consultare e collaudare il flusso con il gestionale reale. | A06–A07. Prima integrazione prevista in sola lettura, con confronto tra anagrafiche, fatture, incassi e scadenze. |
| RF-14 | Confrontare clienti per valore registrato e criticità degli incassi. | PR #8. Punteggi distinti, ricerca, ordinamento e dati di supporto; niente valutazione predittiva o di margine senza dati. AC-01–04. |
| RF-15 | Ottenere suggerimenti AI di azioni interne di gestione e fidelizzazione. | PR #8. Regole sempre disponibili, Ollama locale facoltativo con scelta vincolata e nessun invio. AC-05–07. |
| RF-16 | Riprendere il collaudo senza confondere test automatici e conferme personali. | Excel con 36 casi, storico, passi, attesi, copertura automatica e campi modificabili per nuovo esito, data, versione, osservazioni. |
| RF-17 | Avanzare soltanto su funzionalità interne. | Nessuna nuova integrazione esterna o invio reale; worker non necessario. Test SMTP simulati e prove esterne rinviate. |
| RF-18 | Evitare la riproposizione di HTML vecchio dopo aggiornamento e riavvio. | Risposta `/` con Cache-Control no-store, test API di nuova pagina e browser con reload normale. Una scheda aperta richiede ricaricamento; vecchia cache può richiedere Ctrl+F5 una volta. AC-10. |
| RF-19 | Mantenere le colonne e indicare Non classificato nella posizione del cliente senza storico. | Solo etichetta frontend, nessuna modifica ai punteggi o alle parità. Test Chromium e ricontrollo utente AC-10. |

La modifica dei clienti esistenti, l'analisi predittiva dello storico e la ricerca prospect sono state discusse come possibili evoluzioni.

## Architettura e requisiti tecnici

| ID | Componente | Contratto e responsabilità |
|---|---|---|
| RT-01 | Frontend web | HTML, CSS e JavaScript in `index.html`, serviti dall'app FastAPI. Il browser usa le API JSON dello stesso origin. |
| RT-02 | API e persistenza | `app.py`, factory `create_app`, validazione Pydantic, SQLite locale in `data/holo.sqlite3`. Importi in centesimi interi. Aggiornamenti dello schema all'avvio per archivi legacy. |
| RT-03 | Preventivi | Tabelle `previews`, `drafts`, `edits`. L'anteprima precede la conferma. La versione della bozza protegge da modifiche concorrenti. La conferma ripetuta evita la duplicazione. |
| RT-04 | Clienti, fatture, incassi | `clients`, `invoices`, `demo_payments`. I documenti sono associati per identificativo cliente. L'incasso usa un UUID di richiesta per evitare duplicati e rifiuta importi oltre il residuo. |
| RT-05 | Guida e analisi cliente | `guide.py` fornisce gli articoli demo. La tabella usa dati della scheda. La priorità è la fattura scaduta da più tempo, altrimenti la prossima aperta. |
| RT-06 | Assistente locale | `customer_assistant.py` chiama Ollama su loopback. Modello predefinito `qwen2.5:3b`, configurabile con `HOLO_OLLAMA_MODEL`. Il modello classifica la domanda. FastAPI legge la scheda selezionata e compone la risposta. Un numero esplicito prevale su una classificazione come totale. |
| RT-07 | Follow-up | `follow_ups` conserva cliente, titolo, data, stato e riferimento facoltativo. L'API verifica l'appartenenza del documento. Il completamento è idempotente e protegge da riprogrammazioni successive. |
| RT-08 | Email e orari | `follow_up_emails` conserva messaggio, istante di invio UTC, residuo atteso e stato. `follow_up_email.py` è un worker separato. SMTP con TLS implicito e autenticazione. `tzdata` rende disponibile Europe/Rome anche su Windows. |
| RT-09 | Controlli prima dell'invio | L'incasso a saldo sospende l'email nello stesso aggiornamento SQLite. Il worker ricontrolla anche le fatture saldate già presenti nell'archivio, controlla finestra e destinatario e acquisisce la singola email prima di chiamare SMTP. |
| RT-10 | Esercizio locale | Uvicorn su loopback, worker e app sullo stesso archivio. Il worker controlla ogni 10 secondi quando inattivo. Il PC e il worker devono essere attivi all'orario previsto. |
| RT-11 | Analisi portafoglio | `customer_analysis.py`, sola lettura SQLite in snapshot, importi interi, rapporti Decimal e punteggi spiegabili RBQ-CLIENTI-1. Ranking prima della ricerca e assenza di giudizio con fatturato zero. |
| RT-12 | Consiglio AI vincolato | Trasporto locale condiviso in `customer_assistant.py`; schema JSON e azioni ammesse validate dal server. Solo indicatori aggregati nel prompt, nessun contatto. Regole disponibili anche senza modello. |

### API per area

| Area | Endpoint |
|---|---|
| Anagrafica | `GET /api/clients`, `POST /api/clients`, `GET /api/clients/{client_id}` |
| Preventivi | `POST /api/previews`, `DELETE /api/previews/{preview_id}`, `PUT /api/drafts/{preview_id}`, `GET /api/drafts`, `GET /api/drafts/{draft_id}` |
| Scadenze e incassi | `GET /api/invoices`, `POST /api/invoices/{number}/demo-payments` |
| Assistenza | `GET /api/guide`, `POST /api/clients/{client_id}/questions` |
| Attività | `GET /api/follow-ups`, `POST /api/clients/{client_id}/follow-ups`, `PATCH /api/follow-ups/{follow_up_id}` |
| Email | `PUT /api/follow-ups/{follow_up_id}/email`, `DELETE /api/follow-ups/{follow_up_id}/email`, `GET /api/follow-ups/paid-reminder-count` |
| Analisi portafoglio | `GET /api/customer-analysis?sort=value&q=`, `POST /api/customer-analysis/{client_id}/advice`; `sort=risk` per criticità. |

### Stati del sollecito

| Stato | Transizione o azione |
|---|---|
| Programmata | Il worker attende l'orario. L'utente può riprogrammare o annullare. |
| Sospesa · fattura saldata | Il saldo blocca l'invio. L'utente conferma con Annulla sollecito. |
| Da rivedere | Residuo parziale variato, finestra superata o data attività cambiata. Rivedere contenuto e orario prima di confermare. |
| In invio | Il worker ha acquisito l'email. L'annullamento è disponibile prima di questo stato. |
| Inviata | SMTP ha accettato il messaggio. Verificare la ricezione nella casella di prova. |
| Annullata | Invio eliminato dalla coda. |
| Esito da verificare | Esito SMTP incerto. Verificare casella e provider prima di un nuovo invio. Se il worker cade durante la consegna, lo stato può restare In invio. |

## Tracciabilità, test e fasi successive

Ogni incremento va collegato a requisito o attività, autore o agente, commit, PR, esito revisione, casi di test, ambiente, run CI ed eventuale verifica utente. La prova A05 documenta una sessione multiagente. Per il pilota, i controlli di accesso, isolamento dei dati, segreti, audit, dipendenze, backup e ripristino rientrano in A09–A10. La valutazione di applicabilità NIS2 e ISO/IEC 27001 è da svolgere sul perimetro del pilota.

- **Test automatici.** API Python, riconoscimento richieste JavaScript e browser Chromium. SMTP e classificatore Ollama sono simulati nei test dedicati. Comandi e scenari nel [runbook](Runbook.md).
- **Test manuali.** Usabilità con utenti rappresentativi, comprensione del modello locale e invio reale alla casella di prova. Il percorso email resta aperto sul PC dell'utente perché il pannello non è risultato visibile dopo il salvataggio. La versione più recente mostra la causa quando il server restituisce il relativo stato. [Collaudo email](Collaudo-email-follow-up.md)
- **Roadmap.** Selezione ambiente e gestionale, integrazione in lettura, collaudo tecnico e di usabilità, verifiche di sicurezza, pilota e decisione di rilascio. [Piano generale](Piano-generale.md)

### Apertura del pannello email

Dopo il salvataggio di un follow-up programmabile, la scheda cliente apre il pannello della nuova attività con il destinatario di prova già compilato. Riferimento di implementazione ee1aea5. La consegna viene verificata separatamente con il worker SMTP. [Collaudo](Collaudo-email-follow-up.md)

