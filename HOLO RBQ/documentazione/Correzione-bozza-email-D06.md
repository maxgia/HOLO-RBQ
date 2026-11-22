# D06 / T04 — testo email durante la riprogrammazione

## Comportamento

La riprogrammazione dell’attività ricreava il pannello email partendo dai valori confermati sul server, perdendo oggetto e testo non confermati. La correzione mantiene una bozza per identificativo attività nella memoria della pagina e la ripropone nelle viste Attività e scheda cliente.

Oggetto, testo, ora selezionata e apertura pannello sono conservati durante aggiornamenti delle liste, cambio filtro e riprogrammazione. Se cambia il giorno dell’attività, il giorno della bozza email viene allineato conservando l’ora scelta; una data lasciata vuota resta vuota e deve essere completata. Campi cancellati intenzionalmente restano vuoti, senza ricomparsa automatica dei valori predefiniti.

Nessuna email viene pianificata mentre si modifica il testo o si riprogramma l’attività. Serve ancora **Conferma invio programmato**. Una pianificazione esistente soggetta a revisione segue gli stati e i controlli del server già implementati.

La conferma email, l’annullamento dell’invio e il completamento attività eliminano la bozza locale dopo la riuscita dell’operazione. Un errore della richiesta conserva i campi. Attività diverse non condividono il testo. I valori sono assegnati ai campi del form, senza interpretare HTML inserito dall’utente.

## Limite della bozza non confermata

La bozza vive nella pagina aperta: **F5, chiusura della scheda o uscita dal browser eliminano il testo non confermato**. Un avviso nel pannello lo indica. Una pianificazione confermata rimane invece in PostgreSQL e viene riletta dopo il riavvio. Non si introduce salvataggio automatico né persistenza in localStorage.

## Collaudo manuale T04

Usare una nuova attività di prova e lasciare spento il worker email.

1. Aprire un cliente, creare un follow-up con una data futura e aprire Programma email di prova.
2. Scrivere oggetto e testo riconoscibili, scegliere un orario tra le 09:00 e le 19:59 e **non confermare l’invio**.
3. Cambiare Nuova data e premere Riprogramma.
4. Verificare che il pannello rimanga aperto, oggetto e testo siano invariati e l’invio proposto abbia il nuovo giorno e la stessa ora.
5. Consultare la stessa attività nell’altra vista: il testo deve restare disponibile. Aprire un’altra attività: non deve contenere quel testo.
6. Cancellare volontariamente l’oggetto, riprogrammare e verificare che resti vuoto. Una conferma con campi obbligatori vuoti deve essere rifiutata.
7. Per verificare la persistenza definitiva, compilare nuovamente, confermare l’invio con worker spento e ricaricare la pagina: i dati confermati devono essere presenti. Annullare poi la pianificazione di prova.

Registrare nell’Excel esito, data, versione e osservazioni sulla riga T04. Non trasformare il risultato automatico in una conferma manuale.

## Aggiornamento locale

La modifica applicativa è in index.html. Aggiornare tale file dalla versione pubblicata, oppure aggiornare l’intera cartella dei sorgenti conservando data (incluso postgres.json), .venv e backup. Ricaricare la pagina prima di iniziare il nuovo test: eventuali testi non confermati presenti nella vecchia pagina vanno prima copiati. Non ripetere la migrazione PostgreSQL.

## Verifiche automatiche

Nella prima esecuzione CI 45038907116 i nuovi test non raggiungevano il pannello perche mancava HOLO_TEST_RECIPIENT nella fixture. Corretto il prerequisito dei test e aggiunta attesa del giorno aggiornato; nessun invio reale.

Due test browser riproducono il problema e coprono errore PATCH e successivo tentativo, conservazione di oggetto/testo/ora, pannello aperto, allineamento giorno, passaggio alla scheda cliente, separazione attività e assenza di pianificazione implicita. Verificano anche campi vuoti, validazione, conferma con rilettura dopo reload e cancellazione delle modifiche provvisorie dopo annullamento.

Le stesse prove sono eseguite nelle fixture SQLite e sul runtime PostgreSQL tramite il runner di regressione. Nessun sender SMTP o modello reale è invocato. Non cambia lo schema PostgreSQL né il backend.

[PR #11](https://github.com/maxgia/HOLO-RBQ/pull/11). Il risultato della CI e il riferimento al codice sono riportati nel registro di collaudo e nell’Excel. T04 resta da verificare dall’utente anche dopo il successo automatico.
