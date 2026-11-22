# Dataset dimostrativo esteso — DEMO v1

Richiesta del 22 novembre 2026: popolare il PostgreSQL locale con casi rappresentativi dell’MVP, senza invii o altre interazioni esterne. Dati interamente sintetici, nomi riconoscibili da DEMO | e contatti riservati example.invalid. Nessun dato reale copiato in questo dataset.

## Perimetro

15 clienti, 21 fatture, 12 registrazioni di incasso, 6 bozze e 9 attività. Nessuna anteprima incompleta e nessuna pianificazione email creata. Le date sono relative al giorno di caricamento, nel fuso Europe/Rome; --date YYYY-MM-DD permette un riferimento esplicito. Il report locale registra la data scelta.

| Caso | Cliente | Verifica |
|---|---|---|
| DEMO-01 | DEMO — Cliente consolidato | Tre fatture saldate: alto valore registrato, nessuno scaduto. |
| DEMO-02 | DEMO — Rapporto continuativo | Storico misto, prossimo incasso futuro. |
| DEMO-03 | DEMO — Incasso parziale | Fattura scaduta con residuo diverso dal totale originario. |
| DEMO-04 | DEMO — Scaduto anziano | Due scaduti oltre sessanta giorni; verificare criticità elevata. |
| DEMO-05 | DEMO — Scadenza oggi | La fattura di oggi non è ancora scaduta. |
| DEMO-06 | DEMO — Scadenze future | Una scadenza entro sette giorni e una successiva. |
| DEMO-07 | DEMO — Senza storico | Nessuna fattura o bozza; posizione Non classificato. |
| DEMO-08 | DEMO — Solo preventivi | Due bozze senza fatture: niente fatturato e Non classificato. |
| DEMO-09 | DEMO — Studio Aurora | Nome simile ad altro cliente: verificare separazione documenti. |
| DEMO-10 | DEMO — Aurora Studio | Nome simile ad altro cliente, importo e scadenza differenti. |
| DEMO-11 | DEMO — Importo minimo | Un centesimo: importi e arrotondamenti leggibili. |
| DEMO-12 | DEMO — Officina & Servizi «Èlite» | Accenti, simboli e centesimi nei filtri e nel CSV. |
| DEMO-13 | DEMO — Parità Alfa | Una fattura saldata come Parità Beta: stesso punteggio di valore. |
| DEMO-14 | DEMO — Parità Beta | Una fattura saldata come Parità Alfa: stessa posizione in valore. |
| DEMO-15 | DEMO — Valore con criticità | Incassi consistenti e scaduto: valore e rischio sono distinti. |

Le bozze includono sconto 0%, 10%, 12,50% e 100%, centesimi e totale zero. Le attività comprendono scadute, odierne, future e completate, collegate a fatture, preventivi o solo cliente. Le viste Home e Report/calendario usano gli stessi record.

## Procedura sul PC

1. Conservare un backup PostgreSQL della copia operativa. Fermare server e worker con Ctrl+C. Lasciare il worker spento.
2. Dall’ultimo ZIP main copiare seed_demo.py e Carica-Dati-Demo.cmd nella cartella operativa codice-sorgente. Conservare data/postgres.json e .venv; non ripetere la migrazione.
3. Per vedere l’anteprima, da PowerShell eseguire `.\.venv\Scripts\python.exe seed_demo.py`. Non apre connessioni al database e non modifica nulla.
4. Fare doppio clic su Carica-Dati-Demo.cmd, oppure eseguire `.\.venv\Scripts\python.exe seed_demo.py --apply`. Confermare localmente con CARICA DEMO.
5. Attendere Caricamento completato. I dati attesi e le date sono in data/demo-v1-report.json. L’esecuzione non contiene password nei messaggi o nel report.
6. Avviare Avvia-HOLO.cmd e ricaricare il browser. Cercare DEMO | nell’anagrafica. Il numero clienti esistenti aumenta di 15.
7. Riprendere UX-01 dal principio come richiesto, usando anche questi casi. Registrare osservazioni nel CSV [Scenari-demo-v1.csv](Scenari-demo-v1.csv), apribile con Excel. Tutti i nuovi esiti umani sono Da eseguire.

## Preservazione e ripetibilità

La scrittura avviene in un’unica transazione, protetta dallo stesso lock PostgreSQL dell’applicazione. Errori o collisioni annullano l’intero caricamento; non vengono saltati silenziosamente record in conflitto. Il database deve essere già migrato e configurato. Il comando non modifica schema, configurazione o record preesistenti.

Se tutti i clienti del dataset sono presenti, una seconda esecuzione non carica duplicati e non modifica date, incassi o attività già provate. Se il dataset è presente solo in parte, si ferma: non eliminare record per forzare un nuovo caricamento. Non è previsto un comando distruttivo di reset. Per ripartire da zero usare una copia separata del database o un backup concordato.

Gli importi sono in centesimi interi e gli sconti in punti base. Gli incassi sintetici sono coerenti con il cumulato pagato delle fatture; non attestano vere transazioni o puntualità storica. Gli ID delle nuove bozze vengono assegnati da PostgreSQL: non assumere un progressivo fisso nel collaudo.

**Home, totali e classifiche cambieranno**, perché includono anche i dati DEMO. I vecchi risultati numerici sono evidenze del precedente archivio e non vanno confrontati alla cieca con i nuovi totali. La posizione per valore dipende dall’intero portafoglio; le parità restano parità. Il CSV contiene gli attesi iniziali per singolo cliente alla data di riferimento; gli scaduti e gli stati temporali cambiano naturalmente nei giorni successivi. Il caricamento successivo non riallinea le date.

Il dataset non copre test negativi (importi non validi, riferimenti a clienti errati, collisioni concorrenti) mediante dati corrotti: questi restano prove automatiche o azioni controllate. Non prova email reali, integrazione gestionale A06, autenticazione cloud o conformità normativa. La generazione AI rimane subordinata a Ollama locale, non viene attivata dal caricatore.

## Verifiche automatiche

Tre test di piano verificano conteggi, date bisestili, centesimi/sconti, coerenza incassi, identificativi e anteprima/annullamento senza database. Tre test PostgreSQL isolati verificano preservazione dell’archivio, ripetizione dopo modifiche utente, rollback su collisioni/dataset parziale, ranking, scadenza odierna, bozze e incasso idempotente tramite API reali. Nessun accesso al database operativo durante la CI.

Verifica completata: codice `6826399`, [CI 45046830014](https://github.com/maxgia/HOLO-RBQ/actions/runs/45046830014) superata nei tre job regressione, PostgreSQL e avvio Windows. Superati tutti i sei nuovi test, inclusi i tre PostgreSQL reali, e la regressione precedente. Il caricamento sul PC utente resta da eseguire e non viene dichiarato completato.
