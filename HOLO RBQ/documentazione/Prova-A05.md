# Prova A05 · Annullamento dell’anteprima

Data: 12 novembre 2026. Requisito RBQ-03. Il caso è concluso tecnicamente quando il browser conferma l’annullamento, l’API rifiuta il successivo salvataggio della stessa anteprima e dopo il ricaricamento l’archivio è vuoto.

| Passaggio | Evidenza | Esito |
|---|---|---|
| Implementazione | Test Playwright aggiunto in `e2e/test_preventivi.py`, commit `8a286b9` | Completata |
| Revisione indipendente | Agente revisore. Verificati selettori, attese della risposta e isolamento del caso. | Nessun rilievo bloccante |
| QA e sicurezza del caso | Secondo agente. Verificati database temporaneo, dati dimostrativi e assenza di accesso a dati locali dell’utente. Suggerito il tentativo di salvataggio dopo annullamento, recepito in `2c4773f`. | Risposta 404 verificata |
| Regressione | [GitHub Actions · run 43239996580](https://github.com/maxgia/HOLO-RBQ/actions/runs/43239996580). 7 test API, 11 JavaScript e 4 browser. | Superata |
| Decisione di rilascio | [Pull request #1](https://github.com/maxgia/HOLO-RBQ/pull/1). | Approvazione umana in attesa |

La prova copre l’annullamento di una singola anteprima in ambiente dimostrativo. La valutazione di sicurezza del pilota rimane in A09–A10.
