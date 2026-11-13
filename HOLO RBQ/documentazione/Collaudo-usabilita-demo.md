# Collaudo di usabilità della demo

Questa sessione anticipa la parte dimostrativa di A08 per freelance e partite IVA. La prova di accettazione con il gestionale e gli utenti del pilota segue A07. Usa nominativi di fantasia e un archivio SQLite di prova, per esempio da un clone separato appena avviato. Per installazione e avvio segui il [runbook](Runbook.md).

## Come eseguire la sessione

Prova con 3–5 persone del pubblico previsto. Chiedi a ciascuna di leggere un compito alla volta e di svolgerlo senza mostrare i passaggi del runbook. L'osservatore avvia il cronometro alla lettura del compito, registra gli errori e annota ogni suggerimento. Usa un archivio appena inizializzato per ogni sessione così che gli importi di partenza siano ripetibili. Registra il commit provato e il browser.

| ID | Compito da leggere al partecipante | Risultato da controllare |
|---|---|---|
| US-01 | Inserisci un nuovo cliente con un nome di fantasia. | La scheda del nuovo cliente è visibile e il cliente è selezionabile nei preventivi. |
| US-02 | Per il nuovo cliente salva una bozza da 800 € con sconto del 10%. Ritrovala nell'applicazione dopo aver ricaricato la pagina. | Bozza a 720 €, associata al cliente corretto. |
| US-03 | Cerca Rossi e individua quanto resta da incassare da Studio Rossi e da Martina Rossi. | Studio Rossi 950 €, Martina Rossi 250 €. |
| US-04 | Registra nella demo un incasso di 100 € sulla fattura F-001 di Studio Rossi. Controlla il residuo dopo il ricaricamento. | Il residuo della fattura passa da 500 € a 400 €. La scheda Studio Rossi mostra 850 €. |
| US-05 | Chiedi all'assistente come registrare un incasso. Poi ponigli una domanda fuori ambito, per esempio come cambiare l'IBAN nel gestionale. | La guida indica dove registrare l'incasso, cita la fonte e segnala quando la domanda è fuori copertura. |

## Scheda da compilare per ogni sessione

Partecipante (codice anonimo) · data · profilo · commit · browser

| Caso | Esito | Tempo | Errori, aiuto e osservazioni |
|---|---|---|---|
| US-01 | | | |
| US-02 | | | |
| US-03 | | | |
| US-04 | | | |
| US-05 | | | |

Usa gli esiti **Autonomo**, **Con aiuto** e **Non completato**. A fine sessione chiedi quale passaggio è stato meno chiaro e quale informazione è mancata. Come soglia iniziale proposta, cerca almeno l'80% di completamenti autonomi per ciascun caso e zero errori di associazione cliente o importo confermati. Registra gli ostacoli in ticket collegati al caso e ripeti le prove interessate dopo la correzione.

## Evidenze disponibili

- Inserimento manuale del cliente verificato dall'utente e confermato in chat. Tempi ed errori della sessione non rilevati.
- Regressione automatizzata di Incassi e Clienti superata sul commit `a662166`. [GitHub Actions](https://github.com/maxgia/HOLO-RBQ/actions/runs/43398404064)
- Sessioni strutturate US-01–US-05 da eseguire con utenti rappresentativi.
