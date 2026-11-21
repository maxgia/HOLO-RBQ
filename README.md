# HOLO RBQ

### Aggiornamento cache ed etichetta — collaudo utente

AC-01–AC-06 sono stati confermati dall'utente il 21 novembre, inclusi Ollama reale su due scenari e persistenza dopo saldo e riavvio. Il fix `59b8907` aggiunge Cache-Control no-store alla pagina e Non classificato nella Posizione senza punteggio. [CI 44900599652](https://github.com/maxgia/HOLO-RBQ/actions/runs/44900599652): 20 Python, 11 Node, 14 Chromium superati. Registro Excel aggiornato a 37 casi; AC-10 resta da ricontrollare sul PC. La vecchia copia HTML può richiedere Ctrl+F5 una volta dopo l'aggiornamento.


MVP locale per freelance e partite IVA: preventivi, clienti, fatture e incassi dimostrativi, attività e analisi del portafoglio.

## Aggiornamento del 21 novembre 2026

Il modulo **Analisi clienti** confronta valore registrato e criticità degli incassi, con formule visibili, ricerca e dettaglio. Propone azioni interne da regole e, facoltativamente, da Ollama locale. Nessuna nuova integrazione esterna. Disponibile sul ramo `feat/analisi-portafoglio-clienti`, [PR #8](https://github.com/maxgia/HOLO-RBQ/pull/8); integrazione su main ancora da completare.

- [Avvio, aggiornamento e database di collaudo separato](HOLO%20RBQ/documentazione/Runbook.md)
- [Analisi portafoglio: formule, API e limiti](HOLO%20RBQ/documentazione/Analisi-portafoglio-clienti.md)
- [Registro Excel con 37 casi e campi per il nuovo collaudo](HOLO%20RBQ/documentazione/HOLO-RBQ-Registro-test-2026-11-21.xlsx)
- [Esecuzioni del 21 novembre e prove ancora aperte](HOLO%20RBQ/documentazione/Registro-collaudo-2026-11-21.md)
- [Sorgenti](HOLO%20RBQ/codice-sorgente/)
- [Storico MVP](HOLO%20RBQ/documentazione/Storico-MVP.md)
- [Piano punti 5–8 e matrice di tracciabilità](HOLO%20RBQ/documentazione/Piano-5-8.md)
- [Specifica tecnica e requisiti](HOLO%20RBQ/documentazione/Specifica-tecnica-HOLO-RBQ.md)
- [Piano generale e stato delle versioni](HOLO%20RBQ/documentazione/Piano-generale.md)
- [Collaudo usabilità](HOLO%20RBQ/documentazione/Collaudo-usabilita-demo.md)
- [Collaudo email storico](HOLO%20RBQ/documentazione/Collaudo-email-follow-up.md)

Codice verificato `c40639f`: [GitHub Actions 44881200826](https://github.com/maxgia/HOLO-RBQ/actions/runs/44881200826), 19 Python + 11 Node + 13 Chromium superati. SMTP e AI simulati nei test dedicati; modello locale reale e nuovo collaudo utente restano da fare. Per le nuove prove interne lasciare spento il worker email.
