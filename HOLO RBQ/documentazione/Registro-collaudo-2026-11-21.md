# Registro di collaudo — 21 novembre 2026

## D06 / T04 — correzione del 22 novembre 2026

Corretto il testo email perso durante la riprogrammazione: una bozza per attività conserva oggetto, testo, ora e apertura pannello nelle due viste. Il cambio giorno mantiene l’ora scelta. Non programma invii e non scrive automaticamente sul database; F5 o chiusura pagina perdono il testo non confermato. Conferma, annullamento e completamento eliminano la bozza dopo successo.

[PR #11](https://github.com/maxgia/HOLO-RBQ/pull/11), codice `4cf953d`, [CI 45039238415](https://github.com/maxgia/HOLO-RBQ/actions/runs/45039238415): 36 Python, 11 Node, 17 Chromium e 36 prove funzionali del runner PostgreSQL, oltre al preflight Windows. Due scenari browser nuovi verificano T04 su SQLite e PostgreSQL. Nessun invio reale; schema e backend invariati. [Passi di collaudo e limiti](Correzione-bozza-email-D06.md).

D06 implementato e verificato automaticamente, T04 utente ancora Da eseguire. Excel: 43 casi e nove esiti umani Superato invariati. PG-03–05 restano nei rispettivi stati; A06 gestionale resta aperta, D09 UX/UI ancora pianificata.

## Collaudo del 22 novembre 2026

Migrazione sul PC Windows e primo avvio PostgreSQL confermati dall’utente. Copiate e verificate otto tabelle: 4 clienti, 0 anteprime, 1 bozza, 5 fatture, 1 incasso, 0 follow-up, 1 modifica, 0 email. Assenza dei follow-up accettata. PG-01–02 Superato; PG-03 e AC-11 In corso; PG-04–05 ancora da eseguire sul PC.

[CI 45037721777](https://github.com/maxgia/HOLO-RBQ/actions/runs/45037721777), codice `bc20dfc`: 34 prove funzionali originali rieseguite su PostgreSQL (20 Python e 14 Chromium), tutte superate. Superati anche nove test PostgreSQL specifici, i controlli di configurazione e launcher, gli 11 Node e la regressione SQLite. Sender e AI simulati; nessun accesso al database operativo e nessun invio reale. [Report per caso](Regressione-PostgreSQL-2026-11-22.md).

Registro Excel: 43 casi, 9 nuovi esiti umani Superato complessivi. Le sette conferme precedenti restano storiche. D10 in collaudo; D09 UX/UI segue questo passaggio; A06 resta aperta. Le indicazioni del 21 novembre sul trasferimento ancora da eseguire descrivono lo stato precedente.

## D10 — PostgreSQL prima della UX/UI

Codice `569ec22985a403c99c99895b937d18c7e4b6832b`, [CI 44936628150](https://github.com/maxgia/HOLO-RBQ/actions/runs/44936628150) verde: 36 Python, 11 Node, 15 Chromium e preflight PowerShell Windows. Il job PostgreSQL reale esegue tutti i 36 test Python senza saltare i nove casi PostgreSQL; il browser comprende un nuovo caso sul database migrato. Nel job senza PostgreSQL i casi dedicati vengono esplicitamente saltati, non considerati superati.

Verificati: copia di tutte le tabelle con contenuti Unicode e bozze in modifica; digest e sorgente invariata; sequenza della nuova bozza; parita' API e analisi; incassi concorrenti idempotenti; conferme concorrenti e conflitti di modifica; rifiuto destinazione gia' modificata; rifiuto schema sorgente ignoto; rollback di schema/righe su errore; worker su PostgreSQL con email futura e trasporto fittizio non invocato; salvataggio della configurazione locale dopo copia riuscita. Il browser verifica dati migrati, cliente senza storico e ricalcolo dopo saldo.

**Nessun dato reale dell'utente e' stato ancora migrato.** Registro a 43 casi: sette conferme storiche restano sulla 0.2 SQLite; cinque nuovi casi PG sono da eseguire sul suo PC. La CI prova la procedura con un archivio completo di collaudo, non con la sua copia privata. Nessuna email inviata.

| ID | Prova manuale da eseguire | Stato |
|---|---|---|
| PG-01 | Server/database dedicato e sorgente corretta, app e worker fermi | Da eseguire |
| PG-02 | Configurazione guidata, backup, report otto tabelle e attivazione | Da eseguire |
| PG-03 | Confronto clienti, bozze, fatture, incassi, attivita' e stati | Da eseguire |
| PG-04 | Nuove operazioni, progressivi e persistenza dopo riavvio | Da eseguire |
| PG-05 | Riesecuzione senza duplicati e rifiuto sovrascrittura dopo modifiche | Da eseguire |

[Procedura dettagliata](Migrazione-PostgreSQL.md). A06 resta aperta e UX/UI attende il completamento di D10.

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


Incremento D04 / RF-14–RF-17. [PR #8](https://github.com/maxgia/HOLO-RBQ/pull/8). Codice verificato: `c40639f12d22495292b5175033b4796ce01a711c`.

## Esecuzioni e risultati

| Passo | Ambiente e comando | Esito | Limite |
|---|---|---|---|
| 1 | Python 3.12 locale, `python -m unittest discover -s tests -v` | 19 test superati | Database temporanei; email/AI simulate. |
| 2 | Node, `node --test tests/chat.test.cjs` | 11 test superati | DOM simulato per il riconoscimento. |
| 3 | GitHub Actions, suite API + Node + Chromium | 19 + 11 + 13 superati | [Run 44881200826](https://github.com/maxgia/HOLO-RBQ/actions/runs/44881200826). Navigazione reale headless, modello simulato. |
| 4 | Registro Excel, ricalcolo contatori | Superato | Cambiato temporaneamente AC-01 in Superato, verificato decremento pendenti e incremento superati; ripristinato Da eseguire. Nessun esito umano inventato. |
| 5 | Excel, ricerca errori di formula e anteprime fogli | Superato | Nessun errore formula rilevato. Quattro fogli controllati visivamente; apertura in Excel sul PC utente da confermare. |
| 6 | Modello Ollama reale | Non eseguito | Non disponibile nell'ambiente; AC-06 pendente. |
| 7 | Nuove interazioni esterne | Non eseguite | Nessuna email inviata, nessuna nuova integrazione; A06 e prove esterne rinviate. |

## Registro funzionale

La colonna storico riflette chat e schermate dell'utente, senza ricostruire versioni o date non note. Confermato generale indica un'approvazione del modulo, non un verbale puntuale di quel sottocaso. Le nuove prove utente sono tutte da compilare nell'[Excel](HOLO-RBQ-Registro-test-2026-11-21.xlsx); i casi esterni sono rinviati. **31 casi interni da riprovare, 5 esterni rinviati** non significano 31 difetti: comprendono i controlli di regressione sulla nuova versione.

| ID | Modulo e funzione | Storico utente | Copertura automatica | Nuovo collaudo |
|---|---|---|---|---|
| RBQ-01 | Preventivi — Scelta cliente e omonimi | Confermato generale | API/browser | Da eseguire |
| RBQ-02 | Preventivi — Anteprima e sconto | Confermato generale | API/browser | Da eseguire |
| RBQ-03 | Preventivi — Annullamento | Confermato generale | API/browser | Da eseguire |
| RBQ-04 | Preventivi — Salvataggio e riavvio | Confermato generale | API/browser | Da eseguire |
| RBQ-05-06 | Preventivi — Ricerca e modifica bozza | Confermato generale | API/browser | Da eseguire |
| RBQ-07-08 | Fatture — Filtri e residui | Confermato generale | API/browser | Da eseguire |
| RBQ-09 | Guida — Procedure e fonte | Confermato | API/browser | Da eseguire |
| RBQ-10 | Assistente — Formulazioni equivalenti | Confermato generale | API/browser/Node | Da eseguire |
| CLI-01 | Clienti — Inserimento manuale | Confermato | API/browser | Da eseguire |
| INC-01 | Incassi — Pagamento parziale demo | Confermato generale | API/browser | Da eseguire |
| CLI-02 | Clienti — Analisi tabellare singola scheda | Confermato | API/browser | Da eseguire |
| AI-01 | AI locale — Domanda su singola fattura | Da verificare | API simulata | Da eseguire |
| ATT-01 | Attività — Creazione e filtri | Confermato | API/browser | Da eseguire |
| ATT-02 | Attività — Riprogramma e completa | Confermato | API/browser | Da eseguire |
| UI-01 | Interfaccia — Layout e navigazione | Confermato | API/browser | Da eseguire |
| T01 | Follow-up / email — Pannello e destinatario | Confermato | API/browser | Da eseguire |
| T02 | Follow-up / email — Pianificazione persistente | Confermato | API/browser | Da eseguire |
| T03 | Follow-up / email — Annullamento pianificazione | Confermato | API simulata | Da eseguire |
| T04 | Follow-up / email — Testo non salvato e riprogrammazione | Anomalia aperta | Non coperto | Da eseguire |
| T05 | Follow-up / email — Autenticazione SMTP | Confermato | Non eseguito oggi | Rinviato |
| T06 | Follow-up / email — Esito SMTP incerto | Confermato | API simulata | Rinviato |
| T07 | Follow-up / email — Consegna reale programmata | Confermato | Trasporto simulato | Rinviato |
| T08 | Follow-up / email — Saldo e annullamento sollecito | Confermato | API simulata | Da eseguire |
| T09 | Follow-up / email — Pagamento parziale prima invio | Da verificare | API simulata | Rinviato |
| T10 | Follow-up / email — Finestra oraria e giorno | Da verificare | API simulata | Da eseguire |
| T11 | Follow-up / email — Riavvio worker e duplicazioni | Da verificare | API simulata | Rinviato |
| T12 | Follow-up / email — Invio e completamento distinti | Parziale | API/browser | Da eseguire |
| AC-01 | Analisi portafoglio — Classifica valore | Nuovo | API/browser | Superato utente 21/11 |
| AC-02 | Analisi portafoglio — Classifica criticità e dettaglio | Nuovo | API/browser | Superato utente 21/11 su dati esistenti |
| AC-03 | Analisi portafoglio — Ricerca e omonimi | Nuovo | API/browser | Superato utente 21/11 |
| AC-04 | Analisi portafoglio — Aggiornamento dopo saldo | Nuovo | API/browser | Superato utente 21/11, anche riavvio |
| AC-05 | Analisi portafoglio — Cliente senza storico e testo sicuro | Nuovo | API/browser | Superato utente; nome con HTML solo automatico |
| AC-06 | Analisi portafoglio — Modello locale disponibile | Nuovo | Simulato in CI | Superato utente con Ollama reale, due scenari |
| AC-07 | Analisi portafoglio — Ollama indisponibile | Nuovo | API simulata | Da eseguire |
| AC-08 | Analisi portafoglio — Navigazione e comprensione | Nuovo | Browser parziale; usabilità da fare | In corso: apertura scheda verificata |
| AC-09 | Analisi portafoglio — Controlli limiti e AI incoerente | Nuovo | API simulata | Da eseguire |
| AC-10 | Interfaccia — Cache e Non classificato | Nuovo | API e Chromium, CI 44900599652 | Superato utente: etichetta e F5 dopo riavvio |
| AC-11 | Avvio locale — Doppio clic e preparazione guidata | Nuovo | CI Windows 44903612254 e cinque test Python | Da eseguire sul desktop utente |

## Ordine di ripresa e anomalie

1. Conservare i dati con processi fermi, aggiornare il ramo indicato nel runbook e avviare solo Uvicorn.
2. Usare il database di collaudo separato e la porta 8003 per gli importi di riferimento. Non azzerare il database di lavoro.
3. AC-01–03: classifica, dettaglio e ricerca. AC-04: registrare il saldo, verificare ricalcolo e persistenza. AC-05: cliente senza storico.
4. AC-06 solo con modello già disponibile; in alternativa AC-07 per indisponibilità. AC-08 richiede valutazione umana dell'usabilità. AC-09 ha già copertura automatica.
5. Riprendere i casi interni precedenti. Annotare esito, data, commit, atteso/osservato e ogni anomalia nelle celle gialle G:J del foglio Test.

**T04 aperto:** il testo email provvisorio può andare perso usando Riprogramma prima della conferma del messaggio. Non è corretto dichiararlo risolto in questa versione. Il contenuto confermato viene salvato separatamente. Nessun collaudo SMTP è necessario per osservare il difetto.

**Non ancora completati:** usabilità con utenti rappresentativi, qualità del modello locale reale, consolidamento dei rami su main e controlli di sicurezza del pilota. Le prove su saldo/finestra nei test automatici non attestano da sole la consegna reale. Il test reale del 20 novembre è conservato nel [registro email](Collaudo-email-follow-up.md).

