# Piano generale HOLO RBQ

Aggiornato al 12 novembre 2026. Il target qui assunto è un **pilota a perimetro limitato con un gestionale reale e utenti rappresentativi**, seguito da una decisione sul rilascio. Il gestionale, l'azienda di test e la data di avvio del pilota restano da concordare. Le stime sono giorni-persona, a partire dal completamento della demo. Includono implementazione, revisione, test e aggiornamento della documentazione.

## Attività e avanzamento

| ID | Attività | Stato | Stima | Dipende da | Criterio di completamento |
|---|---|---|---|---|---|
| A01 | MVP locale, repository e runbook | Completata | Consuntivo non rilevato | — | Avvio dal codice GitHub verificato dall'utente. Preventivi, fatture demo e guida disponibili. |
| A02 | Regressione API e riconoscimento delle richieste | Completata | Consuntivo non rilevato | A01 | 7 test Python e 11 test Node superati. |
| A03 | Collaudo browser preventivi e automazione CI | Completata | Consuntivo non rilevato | A01, A02 | E2E verde su GitHub Actions o su una copia pulita. Bozza a 720 €, modifica a 640 €, stesso codice dopo il riavvio. |
| A04 | Estendere il collaudo browser a fatture e guida | Da fare | 2–3 gg | A03 | Filtri e residui corretti, guida con fonte e risposta fuori copertura. Suite ripetibile e documentata. |
| A05 | Sperimentare il flusso di sviluppo multiagente | Da fare | 2–4 gg | A03 | Un'attività con implementazione, revisione, QA, controllo sicurezza, evidenze collegate e approvazione registrata. |
| A06 | Definire il pilota e selezionare il gestionale | Rinviata | 2–4 gg | Disponibilità del referente | Gestionale e operazioni concordati, azienda di test, accesso API, utenti e criteri di accettazione identificati. |
| A07 | Integrare il gestionale in sola lettura | In attesa | 4–7 gg | A06 | Test contrattuali e confronto su anagrafiche, fatture, scadenze, incassato e residui rispetto al gestionale. |
| A08 | Validare qualità dell'assistente e usabilità | Da fare | 3–5 gg | A04, A07 | Utenti rappresentativi completano i flussi concordati. Registrati tempi, errori, casi ambigui e correzioni. |
| A09 | Definire sicurezza e conformità per il pilota | Da fare | 3–5 gg | A06 | Modello delle minacce, ruoli, dati trattati, misure, prove e responsabilità approvati. Valutazioni NIS2 e ISO/IEC 27001 documentate per il perimetro applicabile. |
| A10 | Implementare e verificare i controlli del pilota | In attesa | 4–8 gg | A07, A09 | Verifiche di accesso tra utenti, segreti, audit, dipendenze e ripristino completate. Rischi residui assegnati. |
| A11 | Rilascio pilota e collaudo di accettazione | In attesa | 2–4 gg | A05, A08, A10 | Configurazione riproducibile, suite verde, accettazione utenti e decisione di rilascio registrate. |

**Stima residua di pianificazione: 22–40 giorni-persona** per A04–A11. Con una persona a tempo pieno e attività in sequenza equivale a circa 5–9 settimane lavorative. Sono escluse le attese per scelta del gestionale, accessi, feedback e approvazioni. Mentre A06 è rinviata, A04–A05 possono avanzare con i dati demo. La scrittura nel gestionale, un'eventuale certificazione e il rollout di produzione richiedono un perimetro e una stima dedicati.

## Traguardi e modalità di aggiornamento

| Traguardo | Evidenza di chiusura |
|---|---|
| Demo riproducibile | A01–A04 completate. Runbook aggiornato e regressione registrata su un commit. |
| Sviluppo tracciabile | A05 completata. Ticket, modifiche, revisione, test e decisione collegati. |
| Integrazione verificata | A06–A07 completate con confronto su azienda di test. |
| Pilota accettato | A08–A11 completate. Esiti funzionali, usabilità e sicurezza disponibili per la decisione di rilascio. |

A ogni aggiornamento registrare stato, giorni spesi e residui, blocchi, prossimo passo e collegamenti a PR, commit ed esecuzione dei test. Un'attività passa a **Completata** quando il criterio è verificato. Avanzamento iniziale: **3 attività completate su 11**. Il conteggio misura la chiusura delle attività, che hanno durate diverse. Per i comandi e i casi di collaudo consultare il [runbook](Runbook.md).

Evidenza A03: [GitHub Actions · run 43237001468](https://github.com/maxgia/HOLO-RBQ/actions/runs/43237001468) sul commit `97c0cfa`. Suite API, JavaScript e browser superate.
