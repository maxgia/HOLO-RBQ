# Piano operativo per i punti 5–8

## D06 / T04 — correzione del 22 novembre 2026

Corretto il testo email perso durante la riprogrammazione: una bozza per attività conserva oggetto, testo, ora e apertura pannello nelle due viste. Il cambio giorno mantiene l’ora scelta. Non programma invii e non scrive automaticamente sul database; F5 o chiusura pagina perdono il testo non confermato. Conferma, annullamento e completamento eliminano la bozza dopo successo.

[PR #11](https://github.com/maxgia/HOLO-RBQ/pull/11), codice `4cf953d`, [CI 45039238415](https://github.com/maxgia/HOLO-RBQ/actions/runs/45039238415): 36 Python, 11 Node, 17 Chromium e 36 prove funzionali del runner PostgreSQL, oltre al preflight Windows. Due scenari browser nuovi verificano T04 su SQLite e PostgreSQL. Nessun invio reale; schema e backend invariati. [Passi di collaudo e limiti](Correzione-bozza-email-D06.md).

D06 implementato e verificato automaticamente, T04 utente ancora Da eseguire. Excel: 43 casi e nove esiti umani Superato invariati. PG-03–05 restano nei rispettivi stati; A06 gestionale resta aperta, D09 UX/UI ancora pianificata.

## Collaudo del 22 novembre 2026

Migrazione sul PC Windows e primo avvio PostgreSQL confermati dall’utente. Copiate e verificate otto tabelle: 4 clienti, 0 anteprime, 1 bozza, 5 fatture, 1 incasso, 0 follow-up, 1 modifica, 0 email. Assenza dei follow-up accettata. PG-01–02 Superato; PG-03 e AC-11 In corso; PG-04–05 ancora da eseguire sul PC.

[CI 45037721777](https://github.com/maxgia/HOLO-RBQ/actions/runs/45037721777), codice `bc20dfc`: 34 prove funzionali originali rieseguite su PostgreSQL (20 Python e 14 Chromium), tutte superate. Superati anche nove test PostgreSQL specifici, i controlli di configurazione e launcher, gli 11 Node e la regressione SQLite. Sender e AI simulati; nessun accesso al database operativo e nessun invio reale. [Report per caso](Regressione-PostgreSQL-2026-11-22.md).

Registro Excel: 43 casi, 9 nuovi esiti umani Superato complessivi. Le sette conferme precedenti restano storiche. D10 in collaudo; D09 UX/UI segue questo passaggio; A06 resta aperta. Le indicazioni del 21 novembre sul trasferimento ancora da eseguire descrivono lo stato precedente.

## Aggiornamento PostgreSQL — 0.3.0

D10 anticipa la revisione UX/UI D09. Runtime PostgreSQL e migrazione verificata delle otto tabelle implementati; trasferimento dei dati effettivi e collaudo sul PC ancora aperti. CI reale 44936628150: 36 Python, 11 Node e 15 Chromium superati; Windows preflight superato. Registro Excel 43 casi, PG-01–05 da eseguire. A06 resta aperta. [Procedura](Migrazione-PostgreSQL.md). Le consegne successive in questo documento sono storiche.

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


## Aggiornamento del 21 novembre 2026

Per l'incremento interno D04 sono collegati RF-14–RF-17, [PR #8](https://github.com/maxgia/HOLO-RBQ/pull/8), commit `c40639f` e [CI 44881200826](https://github.com/maxgia/HOLO-RBQ/actions/runs/44881200826): 19 test Python, 11 Node e 13 Chromium superati. L'implementazione e la verifica di questa sessione sono svolte dall'assistente; non si registra una revisione indipendente o una nuova esecuzione multiagente. La prova A05 citata sotto è storica.

| Requisito | Componente | Verifica |
|---|---|---|
| RF-14 / AC-01–05 | `customer_analysis.py`, API e tabella frontend | Importi, punteggi, filtro, omonimi, saldo persistente, zero dati e scadenza odierna; test API e browser. |
| RF-15 / AC-06–07,09 | Trasporto Ollama condiviso e azioni ammesse | Test simulati di JSON, loopback, assenza modello e azione incoerente; modello reale da provare. |
| RF-16 | Registro Excel, 36 casi | Contatori ricalcolati dopo modifica di un esito e ripristinati; controlli formula e anteprime. Nessun nuovo esito umano assegnato. |
| RF-17 | Perimetro interno | Nessun nuovo invio o provider esterno; SMTP simulato nei test; integrazione gestionale rinviata. |

Il registro distingue conferme esplicite, conferme generali, anomalie e prove pendenti. Ogni nuova prova umana deve contenere data, versione e risultato osservato. Le verifiche tecniche nuove coprono escaping DOM tramite testo, cliente per ID, limiti dei dati e output AI vincolato; non sostituiscono i controlli del pilota A09–A10. [Specifica del modulo](Analisi-portafoglio-clienti.md), [piano](Piano-generale.md), [Excel](HOLO-RBQ-Registro-test-2026-11-21.xlsx). I conteggi nelle sezioni seguenti descrivono la prima suite storica.

## 5. Esecuzione e revisione

Per ogni incremento, aprire un'attività con ID requisito, perimetro e criteri di accettazione. Chi implementa lavora su un branch. Chi rivede verifica il diff e le regressioni. Il QA raccoglie gli esiti dei test. Il revisore sicurezza valuta i cambiamenti su accessi, dati e dipendenze. Il responsabile del rilascio approva il merge sulla base di queste evidenze.

Quando si introduce un orchestratore multiagente, registrare per ogni esecuzione l'attività, il ruolo, la versione della configurazione, le azioni rilevanti, l'esito, le revisioni e l'approvazione. Conservare riferimenti agli artefatti ed escludere credenziali e dati personali dalle registrazioni. L'orchestrazione resta da implementare.

La [prova A05](Prova-A05.md) documenta il primo passaggio tra implementazione, revisione, QA, controllo di sicurezza e approvazione.

## 6. Tracciabilità

| Requisito | Componente | Verifica ripetibile |
|---|---|---|
| RBQ-01–04 | Clienti, anteprime, bozze e SQLite | `test_home_and_client_search`, `test_validation_and_cancel`, `test_concurrent_confirmation_and_restart` |
| RBQ-05–06 | Ricerca, dettaglio e modifica bozze | `test_edit_and_stale_preview`, `test_legacy_database` |
| RBQ-07–08 | Ricerca fatture, filtri e residui | `test_invoices`, `test_fatture_da_chat_e_filtri` |
| RBQ-09 | Guida operativa e fonte | `test_guide`, `test_guida_con_fonte_e_domanda_fuori_copertura` |
| RBQ-10 | Formulazioni equivalenti nella chat | `chat.test.cjs` e `test_invoices` |

In una pull request indicare ID del requisito, commit, comando di test, esito, eventuali prove manuali e approvazione. Per le prove manuali registrare data, versione, ambiente, risultato atteso e osservato.

## 7. Regressione e usabilità

La suite esegue 7 test Python a livello API, con sottocasi, e 11 test Node sul riconoscimento delle frasi. I test usano database temporanei. I passi per il collaudo nel browser sono nel runbook.

Per il pilota, far svolgere a utenti rappresentativi creazione, modifica, ricerca fatture e uso della guida. Rilevare completamento senza aiuto, tempo, errori e chiarezza della conferma. I quattro test browser coprono preventivi, fatture e guida operativa. L’esito E2E è registrato nel [piano generale](Piano-generale.md). Resta il collaudo con utenti rappresentativi.

## 8. Sicurezza

La suite copre input non validi, annullamento, concorrenza e conferme ripetute. Prima del pilota definire il modello delle minacce e verificare autenticazione, autorizzazione, accesso tra account, tracciabilità delle azioni, ripristino, dipendenze e gestione dei segreti. Riesaminare l'applicabilità degli obblighi e il perimetro di conformità quando saranno noti soggetto, ambiente e dati. Queste attività e le relative evidenze restano da completare.

## Collegamenti a requisiti e verifiche

La [specifica tecnica](Specifica-tecnica-HOLO-RBQ.md) collega requisiti funzionali e tecnici. Il [piano generale](Piano-generale.md) registra stato dei rami, evidenze automatiche e prove manuali aperte. I controlli di sicurezza e la valutazione di conformità del pilota rientrano in A09–A10.

