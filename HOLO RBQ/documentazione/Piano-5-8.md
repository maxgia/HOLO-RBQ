# Piano operativo per i punti 5–8

## 5. Esecuzione e revisione

Per ogni incremento, aprire un'attività con ID requisito, perimetro e criteri di accettazione. Chi implementa lavora su un branch. Chi rivede verifica il diff e le regressioni. Il QA raccoglie gli esiti dei test. Il revisore sicurezza valuta i cambiamenti su accessi, dati e dipendenze. Il responsabile del rilascio approva il merge sulla base di queste evidenze.

Quando si introduce un orchestratore multiagente, registrare per ogni esecuzione l'attività, il ruolo, la versione della configurazione, le azioni rilevanti, l'esito, le revisioni e l'approvazione. Conservare riferimenti agli artefatti ed escludere credenziali e dati personali dalle registrazioni. L'orchestrazione resta da implementare.

## 6. Tracciabilità

| Requisito | Componente | Verifica ripetibile |
|---|---|---|
| RBQ-01–04 | Clienti, anteprime, bozze e SQLite | `test_home_and_client_search`, `test_validation_and_cancel`, `test_concurrent_confirmation_and_restart` |
| RBQ-05–06 | Ricerca, dettaglio e modifica bozze | `test_edit_and_stale_preview`, `test_legacy_database` |
| RBQ-07–08 | Ricerca fatture, filtri e residui | `test_invoices` |
| RBQ-09 | Guida operativa e fonte | `test_guide` |
| RBQ-10 | Formulazioni equivalenti nella chat | `chat.test.cjs` e `test_invoices` |

In una pull request indicare ID del requisito, commit, comando di test, esito, eventuali prove manuali e approvazione. Per le prove manuali registrare data, versione, ambiente, risultato atteso e osservato.

## 7. Regressione e usabilità

La suite esegue 7 test Python a livello API, con sottocasi, e 11 test Node sul riconoscimento delle frasi. I test usano database temporanei. I passi per il collaudo nel browser sono nel runbook.

Per il pilota, far svolgere a utenti rappresentativi creazione, modifica, ricerca fatture e uso della guida. Rilevare completamento senza aiuto, tempo, errori e chiarezza della conferma. Un test browser automatizzato e il collaudo con utenti rappresentativi restano da realizzare.

## 8. Sicurezza

La suite copre input non validi, annullamento, concorrenza e conferme ripetute. Prima del pilota definire il modello delle minacce e verificare autenticazione, autorizzazione, accesso tra account, tracciabilità delle azioni, ripristino, dipendenze e gestione dei segreti. Riesaminare l'applicabilità degli obblighi e il perimetro di conformità quando saranno noti soggetto, ambiente e dati. Queste attività e le relative evidenze restano da completare.
