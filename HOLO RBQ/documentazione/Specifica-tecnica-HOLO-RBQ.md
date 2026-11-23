# Specifica tecnica HOLO RBQ

## D13 — assistente conversazionale consultivo, 23 novembre 2026

Implementata la prima versione trasversale: clienti, saldo, singola fattura, scadenze, bozze, attività e classifica. Risposte tabellari, ambiguità con scelta, contesto temporaneo e lettura PostgreSQL READ ONLY / REPEATABLE READ a ogni domanda. Modello Ollama locale interpreta soltanto un piano validato; nessun SQL libero o invio. [Specifica, limiti e prova sul PC](Assistente-D13.md), [PR #15](https://github.com/maxgia/HOLO-RBQ/pull/15).

Registro Excel aggiornato a 58 casi. Confermati sul PC logo e caricamento del dataset (BR-01 e DM-01), con 11 esiti umani Superato complessivi. La prima sessione UX-01/02 resta evidenza storica; la ripetizione da UX-01 è ancora da fare come richiesto. Otto nuovi casi AS-01–AS-08 Da eseguire con Ollama reale. Modello simulato nella CI; i risultati automatici non diventano conferme utente.

D13 implementato, collaudo utente aperto. Nessuna migrazione o nuova dipendenza. Per aggiornare servono app.py, database.py, customer_assistant.py, il nuovo assistant_service.py e index.html; conservare data/postgres.json e .venv. A06 gestionale, pubblicazione online e D11 audit storico restano rinviati o da pianificare.

## D09 — nuova esperienza operativa, 22 novembre 2026

Implementate Home sintetica, pagine dedicate, scheda cliente a tab, pianificazione follow-up con calendario e Report con esportazione CSV. Dati calcolati e proposte AI sono in tabelle. Grafica scura con accenti lavanda, azioni principali evidenti e tabelle scorrevoli. [Specifica e passi di prova](UX-UI-D09.md), [PR #12](https://github.com/maxgia/HOLO-RBQ/pull/12).

Codice `fcd9643`, [CI 45042571780](https://github.com/maxgia/HOLO-RBQ/actions/runs/45042571780): 36 Python, 11 Node, 20 Chromium superati; 39 prove funzionali ripetute su PostgreSQL reale e preflight Windows superati. AI e SMTP simulati. Registro Excel aggiornato a 48 casi: nove esiti umani Superato preservati, cinque nuovi casi UX-01–UX-05 Da eseguire. PG-03/AC-11 restano In corso, PG-04–05 e T04 non chiusi dal collaudo automatico.

D09 implementato, da validare sul PC. A06 gestionale resta aperta. Il Report fotografa lo stato corrente: lo storico completo richiede D11, ancora da pianificare. Nessuna modifica al database, nuova migrazione o nuovo invio esterno.

## D06 / T04 — correzione del 22 novembre 2026

Corretto il testo email perso durante la riprogrammazione: una bozza per attività conserva oggetto, testo, ora e apertura pannello nelle due viste. Il cambio giorno mantiene l’ora scelta. Non programma invii e non scrive automaticamente sul database; F5 o chiusura pagina perdono il testo non confermato. Conferma, annullamento e completamento eliminano la bozza dopo successo.

[PR #11](https://github.com/maxgia/HOLO-RBQ/pull/11), codice `4cf953d`, [CI 45039238415](https://github.com/maxgia/HOLO-RBQ/actions/runs/45039238415): 36 Python, 11 Node, 17 Chromium e 36 prove funzionali del runner PostgreSQL, oltre al preflight Windows. Due scenari browser nuovi verificano T04 su SQLite e PostgreSQL. Nessun invio reale; schema e backend invariati. [Passi di collaudo e limiti](Correzione-bozza-email-D06.md).

D06 implementato e verificato automaticamente, T04 utente ancora Da eseguire. Excel: 43 casi e nove esiti umani Superato invariati. PG-03–05 restano nei rispettivi stati; A06 gestionale resta aperta, D09 UX/UI ancora pianificata.

## Collaudo del 22 novembre 2026

Migrazione sul PC Windows e primo avvio PostgreSQL confermati dall’utente. Copiate e verificate otto tabelle: 4 clienti, 0 anteprime, 1 bozza, 5 fatture, 1 incasso, 0 follow-up, 1 modifica, 0 email. Assenza dei follow-up accettata. PG-01–02 Superato; PG-03 e AC-11 In corso; PG-04–05 ancora da eseguire sul PC.

[CI 45037721777](https://github.com/maxgia/HOLO-RBQ/actions/runs/45037721777), codice `bc20dfc`: 34 prove funzionali originali rieseguite su PostgreSQL (20 Python e 14 Chromium), tutte superate. Superati anche nove test PostgreSQL specifici, i controlli di configurazione e launcher, gli 11 Node e la regressione SQLite. Sender e AI simulati; nessun accesso al database operativo e nessun invio reale. [Report per caso](Regressione-PostgreSQL-2026-11-22.md).

Registro Excel: 43 casi, 9 nuovi esiti umani Superato complessivi. Le sette conferme precedenti restano storiche. D10 in collaudo; D09 UX/UI segue questo passaggio; A06 resta aperta. Le indicazioni del 21 novembre sul trasferimento ancora da eseguire descrivono lo stato precedente.

## Versione PostgreSQL 0.3.0 — stato corrente

La [PR #9](https://github.com/maxgia/HOLO-RBQ/pull/9) sostituisce il database runtime con PostgreSQL tramite SQLAlchemy 2.0 e psycopg 3. SQLite rimane solo come sorgente di migrazione e fixture esplicita di test. Nessun fallback automatico. [Procedura, schema, credenziali e limiti](Migrazione-PostgreSQL.md).

Tutte le otto tabelle applicative sono copiate e confrontate per contenuto, con backup e transazione PostgreSQL. Date ISO, stati, importi in centesimi e identificativi sono preservati. Le letture aggregate usano snapshot ripetibile; per la scala MVP le scritture sono serializzate da un advisory lock di progetto. La configurazione viene attivata soltanto dopo la verifica. Schema versione 1 tracciato in _holo_migrations.

Trasferimento effettivo dell'archivio utente: **da eseguire sul suo PC**, non completato dalle prove CI. Nuovo requisito RF-22: PostgreSQL e migrazione completa prima di UX/UI, senza invii, senza omettere tabelle e senza sovrascrivere una destinazione popolata. Test PG-01–PG-05 nell'Excel di 43 casi. A06 resta aperta.

Evidenza `569ec22`, CI 44936628150: 36 Python, 11 Node, 15 Chromium e preflight Windows superati; nove test Python e un test browser su PostgreSQL reale. I paragrafi della 0.2 sottostanti restano cronologia.

## Consegna consolidata 0.2.0-demo — 21 novembre 2026

La PR #8 riunisce su main le funzioni della demo e la documentazione. Aggiunto avvio guidato con Avvia-HOLO.cmd / Avvia-HOLO.ps1 e start_local.py: preparazione .venv, dipendenze solo se cambiano, percorso database esplicito, porta occupata rifiutata e browser a server pronto. Il worker email non viene avviato.

[CI 44903612254](https://github.com/maxgia/HOLO-RBQ/actions/runs/44903612254), codice `10a57d8`: 25 Python, 11 Node e 14 Chromium superati; collaudo Windows PowerShell 5.1 superato per prima installazione, percorsi con spazi, avvio da altra cartella, porta occupata, riavvio e persistenza. Apertura browser e arresto interattivo sul desktop dell'utente da collaudare in AC-11. Le dipendenze richiedono Internet solo durante la preparazione.

Sette casi utente AC-01–AC-06 e AC-10 confermati. Registro Excel esteso a 38 casi; AC-11 nuovo e pendente. A06 rimane APERTA per la ricerca del gestionale e dell'azienda di prova. La revisione UX/UI e' pianificata in D09 dopo il consolidamento, senza attendere A06: [piano UX/UI](Piano-UX-UI.md), [piano corrente](Piano-generale.md), [avvio](Runbook.md). Non e' stato ancora eseguito il ridisegno grafico. Le sezioni seguenti mantengono gli stati delle consegne precedenti.


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

Nuovo RF-23: conservare oggetto, testo e ora non confermati durante riprogrammazione e aggiornamento delle viste, separati per attività, senza programmazione implicita. Limite: memoria della pagina fino a ricaricamento. Test automatici in e2e/test_fatture_guida.py; collaudo utente T04 pendente.

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
| RF-20 | Avviare la demo da una copia ZIP senza dover ricostruire manualmente ambiente e comandi. | Launcher .cmd e PowerShell con percorso stabile, .venv e preparazione dipendenze, controllo porta e apertura browser; AC-11. |
| RF-21 | Rivedere UX/UI dopo il consolidamento, mantenendo aperta la ricerca del gestionale. | D09 implementata; verifica utente UX-01–UX-05 ancora da eseguire. |
| RF-24 | Home sintetica con urgenze, azioni e problemi cliente rappresentati dai dati. | Massimo otto segnalazioni prioritarie con totale dichiarato, origine e collegamento operativo. Nessun giudizio su problemi non registrati. |
| RF-25 | Mostrare tutte le informazioni calcolate e dedotte dall’AI in forma tabellare. | Home, anteprima, importi, scheda, classifica, proposte e risposte informative in tabelle; origine distinta. |
| RF-26 | Pianificare follow-up in un’area dedicata e accedervi dal contesto. | Attività con Elenco e Calendario Mese/Settimana/Giorno; stesso record da Home, cliente o fattura. Nessun invio implicito. |
| RF-27 | Report finale delle cose fatte e da fare. | Prima realizzazione come fotografia dei record presenti, filtri sulle scadenze e CSV; D11 necessario per audit storico completo. |

La modifica dei clienti esistenti, l'analisi predittiva dello storico e la ricerca prospect sono state discusse come possibili evoluzioni.

## Contratti tecnici D09

Frontend nello stesso index.html, con una sola pagina visibile e routing hash; tab cliente con navigazione da tastiera. Si riusano API e tabelle PostgreSQL correnti, senza nuovi endpoint o migrazioni. Il calendario rappresenta la data attività, non l’ora email. Il report filtra scadenze, non date di incasso/completamento indisponibili; CSV con neutralizzazione delle formule. Richieste obsolete non sovrascrivono le più recenti; errori di lettura eliminano gli indicatori non verificati. Dettagli e limiti in [UX-UI-D09.md](UX-UI-D09.md).

## Requisiti aggiuntivi D13

| ID | Requisito | Realizzazione e verifica |
|---|---|---|
| RF-28 | Interrogare trasversalmente l’applicazione in italiano con dati aggiornati. | Endpoint POST /api/assistant/query; nuovo snapshot dopo l’interpretazione di ogni domanda. AS-01 e AS-02. |
| RF-29 | Chiarire nomi ambigui e mantenere un contesto temporaneo. | Scelte validate per domanda/conversazione; contesto cliente/documento e Nuova conversazione. AS-03. |
| RF-30 | Risultati calcolati tabellari, verificabili e con accesso ai record. | Colonne/righe, origine, ora, filtri, ID richiesta e link locali; massimo 50 righe dichiarato. AS-04–AS-06 e AS-08. |
| RF-31 | Prima versione esclusivamente consultiva. | Catalogo chiuso, richieste scrittura/invio rifiutate e transazione READ ONLY. AS-07. |
| RF-32 | Distinguere dati mancanti ed errori da risultati validi. | Nessuna risposta ricostruita dopo 502/503; metriche e periodi non disponibili respinti. AS-04 e AS-07. |

Tecnica: assistant_service.py valida un QueryPlan Pydantic; customer_assistant.py riusa Ollama loopback con JSON Schema e budget D13 separato. Il modello non vede credenziali o intero archivio e non genera importi/SQL. database.py supporta BEGIN READ ONLY; app.py governa snapshot e errori. Sessioni in memoria, 30 minuti, massimo 200, revisione contro risposte concorrenti obsolete. Logging con ID/hash domanda/filtri/esito/durata su console. Nessun nuovo schema o autenticazione; esercizio locale a singolo processo. [Contratto completo e limiti](Assistente-D13.md).

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

