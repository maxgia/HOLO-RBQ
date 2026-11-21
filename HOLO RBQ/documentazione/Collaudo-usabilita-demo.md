# Collaudo di usabilità della demo

## Consegna consolidata 0.2.0-demo — 21 novembre 2026

La PR #8 riunisce su main le funzioni della demo e la documentazione. Aggiunto avvio guidato con Avvia-HOLO.cmd / Avvia-HOLO.ps1 e start_local.py: preparazione .venv, dipendenze solo se cambiano, percorso database esplicito, porta occupata rifiutata e browser a server pronto. Il worker email non viene avviato.

[CI 44903612254](https://github.com/maxgia/HOLO-RBQ/actions/runs/44903612254), codice `10a57d8`: 25 Python, 11 Node e 14 Chromium superati; collaudo Windows PowerShell 5.1 superato per prima installazione, percorsi con spazi, avvio da altra cartella, porta occupata, riavvio e persistenza. Apertura browser e arresto interattivo sul desktop dell'utente da collaudare in AC-11. Le dipendenze richiedono Internet solo durante la preparazione.

Sette casi utente AC-01–AC-06 e AC-10 confermati. Registro Excel esteso a 38 casi; AC-11 nuovo e pendente. A06 rimane APERTA per la ricerca del gestionale e dell'azienda di prova. La revisione UX/UI e' pianificata in D09 dopo il consolidamento, senza attendere A06: [piano UX/UI](Piano-UX-UI.md), [piano corrente](Piano-generale.md), [avvio](Runbook.md). Non e' stato ancora eseguito il ridisegno grafico. Le sezioni seguenti mantengono gli stati delle consegne precedenti.


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

I casi US-01–US-05 sono eseguibili su main. Per testare anche analisi cliente, follow-up o email usa il ramo indicato nel [piano generale](Piano-generale.md) e registra il commit effettivo.

## Estensione analisi clienti — 21 novembre 2026

Sessioni con utenti ancora da eseguire. Per US-06–US-08 usare il ramo della PR #8, worker spento e archivio demo separato del runbook. Registrare esito, tempo, aiuto, errori e spiegazione fornita dal partecipante; nessuna nuova prova SMTP.

| ID | Compito | Risultato da osservare |
|---|---|---|
| US-06 | Individua il cliente con maggior valore registrato e spiega i dati usati. | Raggiunge Analisi clienti, trova Studio Rossi e distingue incassato, residuo e valore. |
| US-07 | Individua la priorità negli incassi e spiega perché un cliente di valore può anche avere criticità. | Ordina per criticità, apre F-001 e distingue valore da scaduto corrente senza interpretarli come rating creditizio. |
| US-08 | Valuta un nuovo cliente senza fatture e, se disponibile, richiedi un'azione all'AI locale. | Riconosce i dati insufficienti, la fonte del suggerimento e che nessuna azione viene eseguita automaticamente. |

Queste prove completano AC-08 del registro Excel, ma non sono sostituite dai 13 test automatici Chromium. La soglia iniziale del protocollo resta proposta e non è stata misurata. [Registro aggiornato](Registro-collaudo-2026-11-21.md).

