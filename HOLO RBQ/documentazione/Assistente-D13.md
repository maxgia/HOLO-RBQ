# D13 — Assistente conversazionale consultivo

Prima versione realizzata il 23 novembre 2026, richiesta dopo il caricamento del dataset DEMO. Interroga l’archivio locale da una chat trasversale. Risultati, dati calcolati e metadati sono tabellari. Non richiede un gestionale esterno e non programma email.

## Funzioni disponibili

| Operazione | Esempio | Risultato |
|---|---|---|
| Ricerca clienti | Cerca Studio Bianchi | Anagrafica con contatti registrati. |
| Saldo cliente | Quanto resta da incassare da Studio Rossi? | Fatturato, incassato cumulato, residuo, scaduto e numero fatture nel filtro. |
| Dettaglio fattura | Quanto resta sulla fattura RBQ-D03-F01? | Documento, cliente, scadenza, stato e importi. |
| Elenco fatture | Quali fatture scadono nei prossimi sette giorni per tutti i clienti? | Fatture nel periodo e filtri espliciti. |
| Bozze | Mostra le bozze di Studio Rossi | Importi, sconto e totale, con accesso al documento. |
| Attività | E le sue attività aperte? | Attività del cliente nel contesto, scadenze e stato corrente. |
| Classifica | Quali clienti hanno maggiori criticità? | Classifica RBQ-CLIENTI-1 dell’archivio corrente. |

I pulsanti Residuo cliente, Prossime scadenze e Criticità clienti compilano una domanda di esempio. L’utente preme Interroga HOLO per inviarla. I precedenti strumenti per preventivi e guida restano nella sezione espandibile Strumenti guidati e guida operativa. Il menu Guida operativa apre quella sezione.

## Architettura e contratti

`POST /api/assistant/query` riceve question (1–600 caratteri dopo trim), conversation_id UUID facoltativo e selected_client_id solo per rispondere a una scelta pendente. Campi inattesi sono rifiutati. Nessun SQL, URL di servizio o credenziale può essere passato nel corpo.

`assistant_service.py` definisce QueryPlan Pydantic: operazione da catalogo chiuso, porzione letterale del nome cliente, numero documento, stati ammessi, periodo relativo/date esplicite e ordinamento valore/criticità. `customer_assistant.py` riusa il trasporto a Ollama locale su loopback, con schema JSON, temperatura zero, timeout e budget di 384 token per il piano D13. Il budget precedente resta invariato per gli altri moduli.

Il modello interpreta la richiesta, non produce importi o HTML. Il backend risolve il cliente, valida il documento, applica filtri e calcoli in centesimi interi e costruisce columns/rows/links. Per la classifica riusa analyse_customers; arrotondamenti e parità sono quelli già applicati da HOLO. La risoluzione del cliente non invia l’elenco di anagrafiche o documenti al modello: il prompt comprende domanda, cliente/fattura del contesto e istruzioni.

Le query sono statiche, con parametri per i valori dove necessari; non viene eseguito SQL proposto dal modello. Letture ampie del piccolo archivio vengono filtrate in Python e limitate a 50 righe in risposta, con total_rows e truncated espliciti. Il saldo globale è calcolato prima del limite. Questa versione non è ottimizzata per archivi grandi: paging lato database e ottimizzazione delle query restano evoluzioni.

`app.py` termina l’interpretazione prima di aprire una transazione breve PostgreSQL `READ ONLY` / `REPEATABLE READ`. Ogni domanda apre una nuova fotografia. `database.py` aggiunge il relativo comando all’adattatore. Nei test SQLite si usa query_only. Anche un tentativo di INSERT introdotto artificialmente nel componente di lettura viene rifiutato e non lascia dati.

La risposta include status, operation, colonne/righe, filtri, origine, istante UTC della lettura, ID richiesta, ID conversazione e contesto. Il browser mostra l’ora italiana e rende stringhe con textContent, senza innerHTML o codice del modello. I link aprono record nelle pagine operative; eventuali modifiche successive restano azioni manuali dell’utente in quelle pagine.

## Coerenza, ambiguità e contesto

- Un numero F-001 o RBQ-D03-F01 scritto nella domanda prevale su una classificazione di totale cliente, salvo richiesta non supportata. Più fatture nella stessa domanda richiedono una domanda più specifica.
- Cliente nominato/scelto e documento devono appartenersi. Un documento esplicito senza cliente sposta il contesto al proprietario effettivo, anche dopo una domanda su altro cliente.
- Rossi o Aurora possono identificare più clienti: vengono proposte scelte esplicite, senza sommare importi. Sono accettate soltanto le scelte ancora pendenti di quella conversazione e domanda.
- I termini temporali presenti nei nomi DEMO non devono diventare filtri cliente impliciti. Usare il nome completo, incluso DEMO |, se un nome coincide con un’espressione operativa.
- Il contesto conserva cliente e ultima fattura. Non conserva uno storico illimitato e i filtri temporali vengono ricavati per ogni nuova domanda. Tutti i clienti o totale generale azzerano l’ambito cliente. Nuova conversazione azzera il contesto del browser.
- Le sessioni sono in memoria nel singolo processo: massimo 200, scadenza 30 minuti dall’ultimo esito salvato. Revisioni impediscono che risposte concorrenti sovrascrivano un contesto più recente. Il riavvio elimina il contesto; F5 avvia una nuova conversazione dal browser. Non è predisposta la condivisione tra più processi o istanze.
- Nessun login o isolamento per organizzazione viene aggiunto. I token casuali delle conversazioni non sostituiscono l’autenticazione. L’uso previsto resta locale su loopback; la pubblicazione online è rinviata e richiede accessi protetti.

## Significato di tempo reale e periodi

Tempo reale significa una nuova lettura per domanda, non aggiornamento continuo di una risposta già visualizzata. Un incasso confermato prima della lettura deve comparire nella risposta successiva. Le risposte precedenti mantengono il proprio istante e non vengono aggiornate retroattivamente.

I periodi riguardano le scadenze di fatture e attività. next7 va da oggi a oggi+7 inclusi; next30 da oggi a oggi+30 inclusi. Oggi non è scaduto. Le date relative seguono Europe/Rome. Date esplicite e periodo relativo insieme, o intervalli invertiti, vengono rifiutati. Bozze e anagrafiche non hanno date storiche utilizzabili per questo filtro; la classifica usa tutto l’archivio.

Non sono disponibili margini, costi, redditività, solvibilità, puntualità storica, previsioni o incassi per mese/data di effettiva registrazione. Richieste di questo tipo vengono respinte dal catalogo o richiedono una riformulazione. La classifica misura valore registrato e scaduto corrente. Nessuna posizione implica un giudizio assoluto di affidabilità.

## Errori e tracciabilità

Richieste di modifica, cancellazione, pianificazione o invio non vengono eseguite. Classificazione non valida/documenti inventati producono 502; Ollama o archivio indisponibili 503; input/filtri non validi 422; contesto scaduto o conflitto di revisione 409; limite di sessioni 429. La UI mostra una tabella di errore per la nuova domanda senza ricostruire importi da risposte precedenti.

Il logger holo.assistant scrive su console ID richiesta, hash abbreviato della domanda, operazione, filtri, esito e durata. Non scrive domanda integrale, password, SQL o risultati finanziari nei nuovi log di assistente. Per conservare questi eventi occorre acquisire i log di esercizio: non costituiscono il registro storico completo D11, non attribuiscono l’operazione a un utente autenticato e non sono un audit normativo.

## Aggiornamento sul PC

1. Conservare la cartella operativa e un backup PostgreSQL. Fermare server e worker con Ctrl+C. Lasciare spento il worker.
2. Dallo ZIP main aggiornare **app.py, database.py, customer_assistant.py, assistant_service.py e index.html** dentro codice-sorgente. Si può aggiornare l’intera cartella sorgenti conservando data/postgres.json e .venv. Il modulo assistant_service.py è nuovo.
3. Non ripetere Configura-Postgres.cmd, la migrazione o il caricamento DEMO. Non è richiesto alcun cambio di schema o nuova dipendenza.
4. Avviare Ollama come nelle precedenti prove AI. Con `ollama list` verificare che il modello configurato sia disponibile. Il default è qwen2.5:3b, oppure HOLO_OLLAMA_MODEL già impostato nell’ambiente del server.
5. Eseguire Avvia-HOLO.cmd. Aprire http://127.0.0.1:8002/#assistant e ricaricare la pagina. Inviare una domanda nel campo Domanda sui dati.
6. In caso di errore sul modello, verificare Ollama e modello prima di modificare PostgreSQL. In caso di conversazione scaduta usare Nuova conversazione.

## Collaudo e ripresa

| Caso Excel | Prova utente |
|---|---|
| AS-01 | Saldo cliente, confronto scheda, piccolo incasso manuale su copia di collaudo, nuova domanda aggiornata. |
| AS-02 | Residuo di una fattura esplicita; cliente diverso nominato insieme allo stesso documento. |
| AS-03 | Rossi ambiguo, scelta, domanda successiva, tutti i clienti e Nuova conversazione. |
| AS-04 | Prossime scadenze, filtri dichiarati e periodi non supportati. |
| AS-05 | Bozze e attività; apertura dei record corretti. |
| AS-06 | Confronto classifica con Analisi clienti e domanda su redditività non disponibile. |
| AS-07 | Scrittura respinta, Ollama indisponibile e formulazioni reali del modello. |
| AS-08 | Tabelle, origine/ora/ID, filtri, finestra stretta e tastiera. |

Il registro Excel contiene 58 casi, con 11 nuovi esiti umani Superato complessivi. Logo BR-01 e caricamento DM-01 sono confermati dall’utente; i 15 scenari analitici del CSV restano da verificare. La prima sessione UX-01 e UX-02 è registrata come storica, mentre la ripetizione resta Da eseguire, come richiesto. AS-01–AS-08 sono tutti Da eseguire.

Le prove automatiche comprendono 15 nuovi controlli backend e tre Chromium. Sono rieseguite anche sul runner PostgreSQL insieme alla regressione precedente. Il modello è simulato: la CI verifica i contratti, i dati e i flussi, non la qualità linguistica del modello reale. Nessuna email reale, accesso al PC utente o nuova integrazione esterna.

Codice `c9baaaf`, [CI 45122619109](https://github.com/maxgia/HOLO-RBQ/actions/runs/45122619109): 57 Python, 11 Node, 23 Chromium e 57 prove funzionali ripetute sul runner PostgreSQL, tutti superati. Preflight Windows superato. [Risultati PostgreSQL per caso](Regressione-Assistente-2026-11-23.json). A06 gestionale, pubblicazione online e D11 audit storico restano aperti. L’orchestrazione multiagente continuativa non è introdotta da D13.
