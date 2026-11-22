# Revisione UX/UI — D09

Aggiornamento del 22 novembre 2026, successivo alla migrazione e al primo avvio PostgreSQL confermati dall’utente. La realizzazione è descritta in [UX-UI-D09.md](UX-UI-D09.md). Nessuna dipendenza dalla scelta A06 del gestionale reale.

| Caso Excel | Verifica utente | Stato |
|---|---|---|
| UX-01 | Home, priorità, accessi rapidi, menu, Indietro e ricerca cliente. | Da eseguire |
| UX-02 | Scheda cliente a tab e informazioni calcolate/AI in tabelle. | Da eseguire |
| UX-03 | Creazione da cliente/fattura/Home, calendario Mese/Settimana/Giorno, stesso record nell’elenco. | Da eseguire |
| UX-04 | Report, filtri cliente/scadenza, CSV e chiarezza del limite sullo storico. | Da eseguire |
| UX-05 | Tastiera, finestra stretta, errori, assenza dati e leggibilità. | Da eseguire |

La CI copre i flussi e la regressione (36 Python, 11 Node, 20 Chromium e 39 prove funzionali PostgreSQL). Non sostituisce il giudizio dell’utente né una sessione con prospect. I dettagli ripetibili e i campi esito/data/versione/osservazioni sono nel registro Excel da 48 casi.

Conservati punteggi e parità della classifica, Non classificato, importi, controlli email e bozza D06 nella pagina aperta. A06 resta aperta; lo storico completo D11 è da pianificare. Prima di F5 salvare testi non confermati. Per il collaudo lasciare spento il worker.

Per utenti rappresentativi eseguire anche [US-01–US-08](Collaudo-usabilita-demo.md), annotando completamento autonomo, tempo, aiuti, errori e problemi residui. Non viene dichiarata una certificazione di accessibilità.
