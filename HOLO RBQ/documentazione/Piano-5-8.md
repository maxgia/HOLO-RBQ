# Piano operativo per i punti 5–8

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

