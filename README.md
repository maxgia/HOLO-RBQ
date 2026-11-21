# HOLO RBQ

Demo locale per freelance e partite IVA, versione **0.2.0-demo**. Preventivi, anagrafica clienti, fatture e incassi demo, attivita', follow-up e analisi del portafoglio con suggerimenti AI locali.

## Avvio semplice su Windows

1. Scarica **Code → Download ZIP** da [main](https://github.com/maxgia/HOLO-RBQ/tree/main) ed estrai l'archivio.
2. Per aggiornare una copia esistente segui il [runbook](HOLO%20RBQ/documentazione/Runbook.md), conservando `data` e `.venv`.
3. Apri `HOLO RBQ/codice-sorgente` e fai doppio clic su **Avvia-HOLO.cmd**.
4. Attendi l'apertura del browser. Per fermare il server premi Ctrl+C nella sua finestra.

Serve Python 3.10 o successivo. Il launcher prepara le dipendenze al primo avvio o quando cambiano; questa operazione richiede Internet. Mostra cartella e database in uso e rifiuta una porta occupata. Non avvia il worker email.

## Stato del progetto

- Consegna consolidata nella [PR #8](https://github.com/maxgia/HOLO-RBQ/pull/8), con main come riferimento per i prossimi aggiornamenti.
- **A06 aperta:** ricerca del gestionale reale e dell'azienda di prova ancora in corso; TeamSystem e Buffetti restano ipotesi.
- **D09 pianificata:** revisione UX/UI dopo il consolidamento, con audit dei flussi, campione di schermata e test. Puo' procedere senza attendere il gestionale.
- AC-01–AC-06 e AC-10 confermati dall'utente; avvio guidato AC-11 da verificare sul suo desktop.
- [CI 44903612254](https://github.com/maxgia/HOLO-RBQ/actions/runs/44903612254): 25 Python, 11 Node, 14 Chromium e collaudo PowerShell Windows superati.

## Documentazione

- [Avvio e aggiornamento](HOLO%20RBQ/documentazione/Runbook.md)
- [Piano generale corrente](HOLO%20RBQ/documentazione/Piano-generale.md)
- [Piano UX/UI](HOLO%20RBQ/documentazione/Piano-UX-UI.md)
- [Registro Excel, 38 casi](HOLO%20RBQ/documentazione/HOLO-RBQ-Registro-test-2026-11-21.xlsx)
- [Esecuzioni e risultati](HOLO%20RBQ/documentazione/Registro-collaudo-2026-11-21.md)
- [Specifica tecnica e requisiti](HOLO%20RBQ/documentazione/Specifica-tecnica-HOLO-RBQ.md)
- [Analisi portafoglio e formule](HOLO%20RBQ/documentazione/Analisi-portafoglio-clienti.md)
- [Tracciabilita' e test](HOLO%20RBQ/documentazione/Piano-5-8.md)
- [Protocollo di usabilita'](HOLO%20RBQ/documentazione/Collaudo-usabilita-demo.md)
- [Collaudo email storico](HOLO%20RBQ/documentazione/Collaudo-email-follow-up.md)
- [Storico MVP](HOLO%20RBQ/documentazione/Storico-MVP.md)

L'archivio resta locale e dimostrativo. Pilota, controlli di sicurezza e integrazione gestionale hanno le attivita' aperte indicate nel piano.
