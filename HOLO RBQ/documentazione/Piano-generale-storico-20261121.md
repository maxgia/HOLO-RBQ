# Piano generale HOLO RBQ

## Aggiornamento dopo il collaudo utente del 21 novembre 2026

**Esiti manuali confermati: AC-01–AC-06.** Verificati valore (Studio Rossi 100), criticità (Martina 71 con F-003 scaduta da 2 giorni), ricerca e omonimi, saldo F-001 di 500 euro con residuo Studio Rossi a 450 euro e scaduto/criticità zero, persistenza anche dopo riavvio e nuovo cliente senza storico. Le prove Ollama reali sul PC dell'utente hanno prodotto verifica incassi per Martina e continuità del rapporto per Studio Bianchi. Modello e SHA della copia ZIP non rilevati; queste prove non certificano la qualità su altri casi. AC-08 è parziale: navigazione verificata, tastiera e finestra stretta ancora da provare.

Il segnale osservato (Analisi clienti ricompare dopo Ctrl+F5) è compatibile con cache HTML, ma la causa sul browser dell'utente non è stata dimostrata. Il nuovo `app.py` serve `/` con **Cache-Control: no-store**. Questo evita nuove copie in cache; non ricarica automaticamente le schede aperte né elimina retroattivamente copie già conservate. Dopo il primo aggiornamento può servire Ctrl+F5 una volta, poi basta un normale F5. La pagina deve essere comunque ricaricata dopo un riavvio se già aperta.

La colonna **Posizione** ora mostra **Non classificato** solo in assenza di punteggio. Nessuna nuova colonna; punteggi non disponibili restano “—”, classifiche e parità rimangono invariate. Requisiti di affinamento RF-18 (cache HTML) e RF-19 (etichetta senza storico).

Codice fix `59b8907ef35629b3e963785ef3795dd245315df5`, [CI 44900599652](https://github.com/maxgia/HOLO-RBQ/actions/runs/44900599652): **20 Python, 11 Node e 14 Chromium superati**. Il test API verifica file HTML aggiornato dopo nuova istanza e richiesta condizionale; Chromium verifica reload normale e dicitura del nuovo cliente. Nessun invio SMTP reale. I test simulati del modello restano distinti dalle prove reali dell'utente.

L'[Excel aggiornato](HOLO-RBQ-Registro-test-2026-11-21.xlsx) contiene **37 casi**, con sei nuovi esiti umani Superato e un caso In corso. **AC-10** registra il collaudo pendente del fix cache e dell'etichetta Non classificato. AC-07 (modello assente), parte di AC-08 e controlli tecnici AC-09 restano aperti nel registro umano; AC-09 è già coperto automaticamente. Le sezioni con la prima consegna sotto sono evidenze storiche.


Aggiornato al 21 novembre 2026. Il target qui assunto è un **pilota a perimetro limitato con un gestionale reale e utenti rappresentativi**, seguito da una decisione sul rilascio. Il gestionale, l'azienda di test e la data di avvio del pilota restano da concordare. Le stime sono giorni-persona, a partire dal completamento della demo. Includono implementazione, revisione, test e aggiornamento della documentazione. Le sezioni datate conservano gli esiti storici; lo stato corrente è nel quadro seguente.

## Stato corrente — 21 novembre 2026

Su richiesta dell'utente si procede soltanto con funzioni interne. A06 e le integrazioni esterne restano rinviate. Il worker SMTP non serve ai nuovi collaudi e deve restare spento. Il nuovo modulo è pubblicato sul ramo `feat/analisi-portafoglio-clienti`, [PR #8](https://github.com/maxgia/HOLO-RBQ/pull/8), derivato da `feat/follow-up-email`: la pubblicazione del ramo non equivale all'integrazione in main.

| Incremento | Stato verificabile | Prossima azione | Impegno residuo indicativo |
|---|---|---|---|
| D01 — Incassi e clienti manuali | Implementato e confermato nelle sessioni precedenti; regressione verde | Nuovo smoke test sulla versione da consolidare | Compreso nella sessione utente |
| D02 — Analisi scheda e attività | Implementato; conferme precedenti; regressione verde | Consolidare i rami, conservando le funzioni | D07 |
| D03 — Solleciti email | Consegna reale e sospensione per saldo confermate il 20/11 | Prove esterne sospese; mantenere evidenze T01–T12 | Non pianificato ora |
| D04 — Valutazione clienti e fidelizzazione interna | Implementato; ranking, azioni da regole e AI locale opzionale; collaudo automatico superato | Collaudo utente AC-01–09, incluso modello reale | 45–60 min stimati per la prima sessione, esclusa installazione modello |
| D05 — Registro Excel | 36 casi con stato storico distinto dal nuovo collaudo e passi ripetibili | Compilare esito, data, versione, osservazioni a ogni prova | Aggiornamento continuativo |
| D06 — Testo email non confermato | Difetto T04 aperto, nessuna correzione inclusa in D04 | Conservazione locale e test browser di riprogrammazione | 0,5–1 giorno-persona stimato |
| D07 — Consolidamento main | PR #4–#8 ancora da consolidare; documentazione #7 riportata nel ramo #8 | Verifica catena, integrazione e regressione finale | 0,5–1 giorno-persona stimato |

Evidenza D04: [CI 44881200826](https://github.com/maxgia/HOLO-RBQ/actions/runs/44881200826), commit `c40639f12d22495292b5175033b4796ce01a711c`: **19 Python + 11 Node + 13 Chromium superati**. Modello AI e trasporto email simulati; nessun invio esterno eseguito. La qualità del modello reale e l'accettazione utente sono aperte. Formula, limiti e API sono nella [specifica del modulo](Analisi-portafoglio-clienti.md); [Excel di ripresa](HOLO-RBQ-Registro-test-2026-11-21.xlsx).

La stima precedente A06–A11 (18–33 giorni-persona) resta una previsione di perimetro pilota da riesaminare dopo A06. D06–D07 sono lavoro aggiuntivo interno: le stime sono separate, non una data promessa di completamento. Non si ricava una percentuale globale dalla somma di attività di dimensioni diverse. Nessun consuntivo in ore è stato rilevato in modo affidabile.

## Attività e avanzamento

| ID | Attività | Stato | Stima | Dipende da | Criterio di completamento |
|---|---|---|---|---|---|
| A01 | MVP locale, repository e runbook | Completata | Consuntivo non rilevato | — | Avvio dal codice GitHub verificato dall'utente. Preventivi, fatture demo e guida disponibili. |
| A02 | Regressione API e riconoscimento delle richieste | Completata | Consuntivo non rilevato | A01 | 7 test Python e 11 test Node superati. |
| A03 | Collaudo browser preventivi e automazione CI | Completata | Consuntivo non rilevato | A01, A02 | E2E verde su GitHub Actions o su una copia pulita. Bozza a 720 €, modifica a 640 €, stesso codice dopo il riavvio. |
| A04 | Estendere il collaudo browser a fatture e guida | Completata | Consuntivo non rilevato | A03 | Filtri e residui corretti, guida con fonte e risposta fuori copertura. Suite ripetibile e documentata. |
| A05 | Sperimentare il flusso di sviluppo multiagente | Completata | Consuntivo non rilevato | A03 | Un'attività con implementazione, revisione, QA, controllo sicurezza, evidenze collegate e approvazione registrata. |
| A06 | Definire il pilota e selezionare il gestionale | Rinviata | 2–4 gg | Disponibilità del referente | Gestionale e operazioni concordati, azienda di test, accesso API, utenti e criteri di accettazione identificati. |
| A07 | Integrare il gestionale in sola lettura | In attesa | 4–7 gg | A06 | Test contrattuali e confronto su anagrafiche, fatture, scadenze, incassato e residui rispetto al gestionale. |
| A08 | Validare qualità dell'assistente e usabilità | Protocollo demo pronto | 3–5 gg | A04, A07 | Utenti rappresentativi completano i flussi concordati. Registrati tempi, errori, casi ambigui e correzioni. |
| A09 | Definire sicurezza e conformità per il pilota | Da fare | 3–5 gg | A06 | Modello delle minacce, ruoli, dati trattati, misure, prove e responsabilità approvati. Valutazioni NIS2 e ISO/IEC 27001 documentate per il perimetro applicabile. |
| A10 | Implementare e verificare i controlli del pilota | In attesa | 4–8 gg | A07, A09 | Verifiche di accesso tra utenti, segreti, audit, dipendenze e ripristino completate. Rischi residui assegnati. |
| A11 | Rilascio pilota e collaudo di accettazione | In attesa | 2–4 gg | A05, A08, A10 | Configurazione riproducibile, suite verde, accettazione utenti e decisione di rilascio registrate. |

**Stima residua di pianificazione: 18–33 giorni-persona** per A06–A11. Con una persona a tempo pieno e attività in sequenza equivale a circa 4–7 settimane lavorative. Sono escluse le attese per scelta del gestionale, accessi, feedback e approvazioni. Mentre A06 è rinviata, la prova A05 è stata eseguita con i dati demo. La scrittura nel gestionale, un'eventuale certificazione e il rollout di produzione richiedono un perimetro e una stima dedicati.

## Traguardi e modalità di aggiornamento

| Traguardo | Evidenza di chiusura |
|---|---|
| Demo riproducibile | A01–A04 completate. Runbook aggiornato e regressione registrata su un commit. |
| Sviluppo tracciabile | A05 completata. Ticket, modifiche, revisione, test e decisione collegati. |
| Integrazione verificata | A06–A07 completate con confronto su azienda di test. |
| Pilota accettato | A08–A11 completate. Esiti funzionali, usabilità e sicurezza disponibili per la decisione di rilascio. |

A ogni aggiornamento registrare stato, giorni spesi e residui, blocchi, prossimo passo e collegamenti a PR, commit ed esecuzione dei test. Un'attività passa a **Completata** quando il criterio è verificato. Avanzamento: **5 attività completate su 11**. Il conteggio misura la chiusura delle attività, che hanno durate diverse. Per i comandi e i casi di collaudo consultare il [runbook](Runbook.md).

Evidenza A03: [GitHub Actions · run 43237001468](https://github.com/maxgia/HOLO-RBQ/actions/runs/43237001468) sul commit `97c0cfa`. Suite API, JavaScript e browser superate.

Evidenza A04: [GitHub Actions · run 43239189016](https://github.com/maxgia/HOLO-RBQ/actions/runs/43239189016) sul commit `c0d5e88`. Superati 7 test API, 11 test JavaScript e 3 test browser Chromium.

Evidenza A05: [prova multiagente e decisione](./Prova-A05.md). Implementazione, revisione e QA completati. Rilascio autorizzato dall’utente il 12 novembre 2026 tramite richiesta di pubblicazione su GitHub.


## Incrementi demo e verifiche

| Incremento | Stato GitHub | Evidenza | Verifica manuale |
|---|---|---|---|
| Incassi e clienti | Integrato in main con [PR #2](https://github.com/maxgia/HOLO-RBQ/pull/2) | [CI 43398404064](https://github.com/maxgia/HOLO-RBQ/actions/runs/43398404064) | Inserimento manuale confermato. |
| Analisi tabellare e domande con Ollama | [PR #4](https://github.com/maxgia/HOLO-RBQ/pull/4) aperta verso main | [CI 43412370009](https://github.com/maxgia/HOLO-RBQ/actions/runs/43412370009) | Tabella verificata. Correzione residuo per singola fattura verificata in CI con classificatore simulato. |
| Attività e follow-up | [PR #5](https://github.com/maxgia/HOLO-RBQ/pull/5) aperta sul ramo della PR #4 | [CI 43414950861](https://github.com/maxgia/HOLO-RBQ/actions/runs/43414950861) | Modulo confermato dall'utente. |
| Solleciti programmati | [PR #6](https://github.com/maxgia/HOLO-RBQ/pull/6) aperta sul ramo della PR #5 | [CI 43419536920](https://github.com/maxgia/HOLO-RBQ/actions/runs/43419536920) | Pannello email da verificare sul PC dell'utente. Consegna SMTP reale da collaudare. |
| Usabilità demo | Protocollo nella [PR #3](https://github.com/maxgia/HOLO-RBQ/pull/3), consolidato in questa revisione documentale | [Protocollo](Collaudo-usabilita-demo.md) | Sessioni strutturate con 3–5 utenti rappresentativi da eseguire. |

La stima A06–A11 resta quella della precedente pianificazione. Attese per accessi al gestionale, collaudo SMTP e consolidamento dei rami vanno registrate al prossimo aggiornamento. Il prossimo passo sulla demo è diagnosticare la visibilità del pannello tramite la guida email e completare MAIL-01, MAIL-06 e MAIL-07.

## Avanzamento del 18 novembre 2026

1. **Solleciti email in collaudo.** La scheda apre il pannello email subito dopo il salvataggio di un follow-up programmabile. Aggiunto un test browser per il destinatario e la conferma. Restano la prova su Windows e la consegna SMTP reale. [PR #6](https://github.com/maxgia/HOLO-RBQ/pull/6)
2. **Consolidamento demo in attesa del collaudo.** Le PR #4–#7 sono aperte.
3. **Valutazione clienti e fidelizzazione pianificate.** Prima versione con indicatori spiegabili e suggerimenti di azioni da confermare.
4. **Pilota con gestionale in attesa di A06.** Restano da scegliere gestionale e azienda di prova.

### Collaudo solleciti — aggiornamento

Pannello e destinatario di prova confermati dall’utente. La conferma non è ancora passata a **Programmata** sul suo PC. La PR #6 mostra ora l’errore vicino al pulsante. Consegna SMTP ancora da verificare.

## Esito del collaudo SMTP del 20 novembre 2026

L’utente ha confermato la ricezione dell’email del follow-up «riproviamo invio», pianificata alle 18:55 italiane. La schermata mostra **Email: Inviata · 20/11/2026, 18:55:04**. Il test di consegna reale alla casella di prova è superato. L’autenticazione Gmail con la nuova password per le app era riuscita sulle porte 465 e 587. L’attività resta Aperta fino al completamento manuale. Restano da verificare manualmente sospensione per saldo prima dell’invio, annullamento e finestra oraria.

### Sospensione del sollecito per saldo — 20 novembre 2026

L’utente ha confermato il corretto funzionamento del test guidato: pianificazione del sollecito su fattura con residuo, registrazione del saldo prima dell’invio, sospensione e annullamento manuale. Esito del collaudo manuale confermato in chat. Restano da registrare le prove manuali dedicate al residuo parziale e ai limiti della finestra oraria. Il consolidamento della demo resta il passo successivo del piano.

## Chiusura sessione del 20 novembre 2026

Confermati manualmente pannello e destinatario, pianificazione, annullamento, autenticazione Gmail, consegna reale alle 18:55:04 e sospensione per saldo con annullamento. Il [registro di collaudo](Collaudo-email-follow-up.md) descrive T01–T12 con passi, risultati attesi, osservazioni e prove aperte. Restano da eseguire manualmente pagamento parziale, limiti orari e ripartenza worker. La conservazione del testo email non ancora confermato durante la riprogrammazione resta un miglioramento aperto. Consolidamento su main e valutazione clienti sono i passi successivi.


