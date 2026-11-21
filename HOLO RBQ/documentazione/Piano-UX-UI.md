# Revisione UX/UI della demo — D09

Richiesta dell'utente del 21 novembre 2026. Fase successiva al consolidamento D07 e all'avvio semplificato D08; può partire mentre A06 (scelta del gestionale reale e azienda di prova) resta aperta. In questa consegna si pianifica la revisione: il layout non è stato ridisegnato.

## Obiettivo

Rendere la demo leggibile e utilizzabile da freelance e partite IVA durante presentazioni ai prospect. Conservare le funzioni e i calcoli già verificati. L'ispirazione grafica precedente è Linear; la revisione parte dai flussi e dalle difficoltà osservate, poi definisce i dettagli visivi.

| Passo | Attività | Risultato da verificare |
|---|---|---|
| UX-01 | Esaminare navigazione tra clienti, fatture, attività e analisi. Valutare viste dedicate invece di scorrere un'unica pagina. | Selezione nel menu coerente con il contenuto aperto; ritorno al cliente senza perdita del contesto. |
| UX-02 | Definire gerarchia di riepiloghi, tabelle, dettagli e azioni. | Separazione comprensibile tra valore, criticità, posizione e progressivo; nessuna colonna aggiunta senza necessità concordata. |
| UX-03 | Proporre una schermata e un flusso rappresentativi prima di estendere il disegno. | Verifica con l'utente su cliente, fattura prioritaria, incasso e suggerimento AI. |
| UX-04 | Applicare tipografia, spaziatura, contrasto, focus e comportamento delle tabelle su finestre strette. | Test tastiera, etichette, leggibilità, scorrimento e assenza di azioni irraggiungibili. |
| UX-05 | Uniformare caricamento, errore, conferma e assenza dati. Distinguere regole e AI. | Utente capisce cosa e' stato salvato, cosa e' soltanto suggerito e cosa richiede un'azione. Nessun invio implicito. |
| UX-06 | Ripetere regressione e protocollo US-01–US-08 con utenti rappresentativi. | Calcoli e persistenza invariati; annotati completamento autonomo, tempo, aiuti, errori e problemi residui. |

## Evidenze iniziali

- La vecchia colonna Punteggi e dati rendeva poco evidente la criticita'. L'utente ha chiesto di mantenere le colonne e sostituire solo il trattino della posizione con Non classificato: requisito mantenuto.
- Apri scheda cliente cambia il contenuto visibile ma il menu puo' restare selezionato su Analisi clienti: comportamento da riesaminare in UX-01.
- Le copie ZIP e le cartelle di backup hanno generato confusione sul server avviato: D08 affronta l'avvio, non sostituisce la revisione delle schermate.
- AC-01–AC-06 e AC-10 confermati dall'utente; AC-08 resta parziale. I test guidati non equivalgono a una sessione senza aiuto con prospect.

## Perimetro e dipendenze

Nessun gestionale reale e' necessario per disegnare e collaudare questi flussi sui dati demo. Gli adattamenti legati a dati e operazioni reali saranno riesaminati dopo A06–A07. Accessi, ruoli e vincoli di sicurezza del pilota rimangono A09–A10.

Non si introduce ora un nuovo modulo di business o un provider esterno. La stima della revisione va definita dopo UX-01 e la scelta del campione UX-03. [Piano generale](Piano-generale.md), [protocollo di usabilita'](Collaudo-usabilita-demo.md).
