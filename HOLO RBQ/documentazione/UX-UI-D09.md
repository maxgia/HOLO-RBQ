# D09 — Home e pagine operative HOLO RBQ

Richiesta del 22 novembre 2026: ridurre le informazioni mostrate insieme, facilitare l’accesso alle azioni, presentare dati calcolati e AI in tabelle, organizzare follow-up in Attività con elenco/calendario e predisporre un report. [PR #12](https://github.com/maxgia/HOLO-RBQ/pull/12).

## Marchio RBQ — aggiornamento del 22 novembre 2026

Su richiesta dell’utente, il logo allegato è adattato su fondo trasparente e inserito nella navigazione condivisa. Rimane visibile in tutte le otto aree, compresi Home, Clienti, Attività e Report. Il collegamento del marchio riporta a Home; testo alternativo e focus da tastiera sono presenti. Dimensioni adattate alle finestre strette.

Il PNG con alpha è incorporato in index.html: per aggiornare non servono file asset aggiuntivi, dipendenze o modifiche PostgreSQL. Nessuna richiesta a servizi esterni durante l’uso del logo. La prova browser UX verifica visibilità e caricamento del logo su tutte le route; il parser Node conserva le undici prove. Gli esiti umani restano invariati: verificare aspetto e leggibilità durante UX-01 e UX-05, poi proseguire con gli altri casi ancora aperti. Nessun worker necessario.

Verifica marchio: codice `ce91706`, [CI 45045149166](https://github.com/maxgia/HOLO-RBQ/actions/runs/45045149166) superata nei tre job (regressione, PostgreSQL, avvio Windows). Controllate anche le schermate Chromium desktop e mobile. Il primo controllo aveva un URL di test con doppia barra: corretto nel test senza modificare il codice applicativo. Gli esiti utente del registro Excel restano aperti e invariati.

## Organizzazione realizzata

| Pagina | Contenuto e azioni |
|---|---|
| Home | Quattro indicatori tabellari, massimo otto segnalazioni prioritarie, accesso a preventivo, cliente e pianificazione follow-up. |
| Clienti | Ricerca, inserimento manuale e scheda con Riepilogo, Documenti e incassi, Attività, Analisi AI. |
| Preventivi | Compilazione, anteprima tabellare e archivio bozze nella stessa area. |
| Fatture e scadenze | Ricerca, importi e riepilogo tabellari, incassi, pianificazione follow-up con cliente/fattura precompilati. |
| Attività | Elenco operativo, filtri esistenti, creazione follow-up, calendario Mese/Settimana/Giorno. |
| Analisi clienti | Classifica e dettaglio tabellari, azione dalle regole distinta dalla proposta AI locale. |
| Report | Stato corrente di fatture, attività e bozze, filtro cliente e periodo di scadenza, esportazione CSV. |
| Assistente | Richieste e guida. Risposte informative in tabelle; i moduli operativi sono raggiungibili dal menu. |

È visibile una sola pagina alla volta. La navigazione usa frammenti URL e mantiene i form nel DOM: passare tra aree non equivale a ricaricare la pagina. Indietro, link diretti e URL non riconosciuto sono gestiti. La Home è la pagina iniziale. Le bozze salvate non hanno più una voce autonoma nel menu: sono dentro Preventivi. Guida operativa apre l’assistente contestualizzato alla guida.

Il visual mantiene il tema scuro richiesto, con gerarchia più netta, accenti viola, segnalazioni arancio e azioni leggibili. Nessuna immagine o font esterno richiesto. Tabelle larghe scorrono nel loro contenitore; su finestre strette il menu diventa orizzontale. I tab supportano frecce, Home/End, stato selezionato e focus; le animazioni rispettano la preferenza di movimento ridotto.

## Home e significato delle segnalazioni

Gli indicatori sono ricavati dagli endpoint correnti: residuo totale delle fatture, residuo scaduto, attività aperte con data odierna, numero bozze. Non sono output del modello.

Le priorità includono fatture scadute, fatture aperte in scadenza nei prossimi sette giorni, follow-up aperti scaduti/odierni e pianificazioni email Da rivedere, Sospese per saldo, Esito da verificare o In invio. Le segnalazioni riportano cliente, motivo, data, origine e azione. Le condizioni più urgenti precedono quelle future; la Home mostra le prime otto e dichiara il totale. Le altre sono consultabili nelle pagine operative.

Questo rileva problemi rappresentati dai dati disponibili, non qualsiasi problema commerciale o relazionale non registrato. Non si attribuisce insolvenza o affidabilità al cliente. Un errore di lettura mostra un messaggio e rimuove i riepiloghi non verificati, senza sostituirli con zeri rassicuranti. Il cruscotto si aggiorna all’apertura, su richiesta e dopo le operazioni collegate. Non è una sincronizzazione in tempo reale con il gestionale.

## Pianificazione follow-up

Si può creare da Home, dall’area Attività, dalla scheda cliente o dalla riga di una fattura. Il documento viene validato dal backend per il cliente selezionato. Tutti gli accessi creano/consultano gli stessi record follow_ups.

Il calendario mostra la **data dell’attività**, distinta da giorno/ora dell’email. Un clic sul giorno prepara la creazione; un clic su un’attività apre lo stesso record nell’elenco, dove restano disponibili Riprogramma e Completa. Il calendario mensile usa 42 celle, la settimana parte dal lunedì; sono gestiti anche mesi e anni bisestili. Nessuna funzione drag-and-drop introdotta.

La creazione non pianifica email. La conferma email resta esplicita, con le verifiche preesistenti di destinatario, residuo, giorno e finestra oraria. D06 conserva le bozze non confermate durante aggiornamenti delle viste nella stessa pagina. Un F5/chiusura perde il testo non confermato; la pianificazione confermata resta su PostgreSQL.

## Risultati in forma tabellare

Anteprime e totali preventivo, indicatori Home, importi delle bozze e fatture, riepilogo cliente, analisi singola scheda, classifica portafoglio e risposte informative dell’assistente sono in tabelle. Dati della scheda, calcoli/regole e proposte AI sono distinti. Una proposta è da valutare e non viene eseguita automaticamente. Le bozze di sollecito rimangono testi modificabili in un campo dedicato: non sono una tabella di indicatori.

## Report: perimetro e limite

Il report è una fotografia dei record presenti. Mostra fatture con importo, incassato cumulato e residuo; attività completate o da fare; bozze da rivedere. Il periodo filtra le scadenze delle fatture e delle attività, **non** le date di registrazione degli incassi o di completamento, che non sono disponibili. Le bozze senza data sono incluse e identificate. Intervalli invertiti vengono rifiutati.

Il CSV è generato nel browser, senza invii esterni, con intestazioni e valori quotati e protezione dei campi che iniziano con caratteri interpretabili come formule. Nessun file viene importato automaticamente in altri sistemi.

Il report **non ricostruisce tutte le modifiche storiche**, gli elementi cancellati o l’autore delle operazioni. Per questo viene registrato D11, registro storico delle operazioni, ancora da pianificare. Non vengono inventate date o prove retroattive.

## Collaudo automatico

Codice `fcd9643`, [CI 45042571780](https://github.com/maxgia/HOLO-RBQ/actions/runs/45042571780): 36 Python, 11 Node, 20 Chromium e runner PostgreSQL di 39 prove funzionali. Windows PowerShell preflight verificato. Il runner usa solo database e schemi di collaudo isolati; il database operativo dell’utente non è raggiunto.

Le prove precedenti conservano le asserzioni di business, con navigazione esplicita tra le nuove pagine. I test del parser JavaScript compilano lo script completo e verificano le stesse undici richieste, senza dipendere da un falso DOM incompleto.

Tre nuovi scenari verificano Home/route/Indietro/ricerca/tastiera/mobile, calendario bisestile e creazione della stessa attività, report/filtri/CSV e stato di errore. Le schermate reali dei test sono conservate come artifact ux-screenshots. Le anteprime usano dati di collaudo, non una copia del database utente. Modello AI simulato; nessun invio email reale.

Nelle prime verifiche sono emersi controlli senza nome accessibile stabile e un passaggio di test rimasto sulla pagina precedente: corretti con etichette esplicite e navigazione coerente. Il collaudo umano di usabilità resta distinto dalla CI.

## Prova sul PC — UX-01–UX-05

1. Conservare la cartella operativa e data, incluso postgres.json. Aggiornare index.html da main (oppure i sorgenti completi preservando data e .venv). Nessuna nuova migrazione PostgreSQL.
2. Ricaricare la pagina prima di iniziare il collaudo; salvare prima eventuali testi non confermati. Deve apparire Home con il nuovo menu.
3. Seguire UX-01–UX-05 nell’Excel: Home e priorità, scheda cliente e tabelle AI, pianificazione/calendario, report/esportazione, finestra stretta e tastiera.
4. Lasciare spento il worker email. Per il test delle nuove attività non serve programmare alcuna email.
5. Registrare esito, data, versione e osservazioni. I precedenti esiti umani restano evidenze delle versioni precedenti e non chiudono automaticamente questo collaudo.

D09 implementato e verificato automaticamente; revisione utente ancora da eseguire. A06 gestionale reale rimane aperta; D11 audit storico da pianificare. Le prove umane PostgreSQL e T04 rimangono nei rispettivi stati.
