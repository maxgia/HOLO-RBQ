# Registro di collaudo — 21 novembre 2026

Incremento D04 / RF-14–RF-17. [PR #8](https://github.com/maxgia/HOLO-RBQ/pull/8). Codice verificato: `c40639f12d22495292b5175033b4796ce01a711c`.

## Esecuzioni e risultati

| Passo | Ambiente e comando | Esito | Limite |
|---|---|---|---|
| 1 | Python 3.12 locale, `python -m unittest discover -s tests -v` | 19 test superati | Database temporanei; email/AI simulate. |
| 2 | Node, `node --test tests/chat.test.cjs` | 11 test superati | DOM simulato per il riconoscimento. |
| 3 | GitHub Actions, suite API + Node + Chromium | 19 + 11 + 13 superati | [Run 44881200826](https://github.com/maxgia/HOLO-RBQ/actions/runs/44881200826). Navigazione reale headless, modello simulato. |
| 4 | Registro Excel, ricalcolo contatori | Superato | Cambiato temporaneamente AC-01 in Superato, verificato decremento pendenti e incremento superati; ripristinato Da eseguire. Nessun esito umano inventato. |
| 5 | Excel, ricerca errori di formula e anteprime fogli | Superato | Nessun errore formula rilevato. Quattro fogli controllati visivamente; apertura in Excel sul PC utente da confermare. |
| 6 | Modello Ollama reale | Non eseguito | Non disponibile nell'ambiente; AC-06 pendente. |
| 7 | Nuove interazioni esterne | Non eseguite | Nessuna email inviata, nessuna nuova integrazione; A06 e prove esterne rinviate. |

## Registro funzionale

La colonna storico riflette chat e schermate dell'utente, senza ricostruire versioni o date non note. Confermato generale indica un'approvazione del modulo, non un verbale puntuale di quel sottocaso. Le nuove prove utente sono tutte da compilare nell'[Excel](HOLO-RBQ-Registro-test-2026-11-21.xlsx); i casi esterni sono rinviati. **31 casi interni da riprovare, 5 esterni rinviati** non significano 31 difetti: comprendono i controlli di regressione sulla nuova versione.

| ID | Modulo e funzione | Storico utente | Copertura automatica | Nuovo collaudo |
|---|---|---|---|---|
| RBQ-01 | Preventivi — Scelta cliente e omonimi | Confermato generale | API/browser | Da eseguire |
| RBQ-02 | Preventivi — Anteprima e sconto | Confermato generale | API/browser | Da eseguire |
| RBQ-03 | Preventivi — Annullamento | Confermato generale | API/browser | Da eseguire |
| RBQ-04 | Preventivi — Salvataggio e riavvio | Confermato generale | API/browser | Da eseguire |
| RBQ-05-06 | Preventivi — Ricerca e modifica bozza | Confermato generale | API/browser | Da eseguire |
| RBQ-07-08 | Fatture — Filtri e residui | Confermato generale | API/browser | Da eseguire |
| RBQ-09 | Guida — Procedure e fonte | Confermato | API/browser | Da eseguire |
| RBQ-10 | Assistente — Formulazioni equivalenti | Confermato generale | API/browser/Node | Da eseguire |
| CLI-01 | Clienti — Inserimento manuale | Confermato | API/browser | Da eseguire |
| INC-01 | Incassi — Pagamento parziale demo | Confermato generale | API/browser | Da eseguire |
| CLI-02 | Clienti — Analisi tabellare singola scheda | Confermato | API/browser | Da eseguire |
| AI-01 | AI locale — Domanda su singola fattura | Da verificare | API simulata | Da eseguire |
| ATT-01 | Attività — Creazione e filtri | Confermato | API/browser | Da eseguire |
| ATT-02 | Attività — Riprogramma e completa | Confermato | API/browser | Da eseguire |
| UI-01 | Interfaccia — Layout e navigazione | Confermato | API/browser | Da eseguire |
| T01 | Follow-up / email — Pannello e destinatario | Confermato | API/browser | Da eseguire |
| T02 | Follow-up / email — Pianificazione persistente | Confermato | API/browser | Da eseguire |
| T03 | Follow-up / email — Annullamento pianificazione | Confermato | API simulata | Da eseguire |
| T04 | Follow-up / email — Testo non salvato e riprogrammazione | Anomalia aperta | Non coperto | Da eseguire |
| T05 | Follow-up / email — Autenticazione SMTP | Confermato | Non eseguito oggi | Rinviato |
| T06 | Follow-up / email — Esito SMTP incerto | Confermato | API simulata | Rinviato |
| T07 | Follow-up / email — Consegna reale programmata | Confermato | Trasporto simulato | Rinviato |
| T08 | Follow-up / email — Saldo e annullamento sollecito | Confermato | API simulata | Da eseguire |
| T09 | Follow-up / email — Pagamento parziale prima invio | Da verificare | API simulata | Rinviato |
| T10 | Follow-up / email — Finestra oraria e giorno | Da verificare | API simulata | Da eseguire |
| T11 | Follow-up / email — Riavvio worker e duplicazioni | Da verificare | API simulata | Rinviato |
| T12 | Follow-up / email — Invio e completamento distinti | Parziale | API/browser | Da eseguire |
| AC-01 | Analisi portafoglio — Classifica valore | Nuovo | API/browser | Da eseguire |
| AC-02 | Analisi portafoglio — Classifica criticità e dettaglio | Nuovo | API/browser | Da eseguire |
| AC-03 | Analisi portafoglio — Ricerca e omonimi | Nuovo | API/browser | Da eseguire |
| AC-04 | Analisi portafoglio — Aggiornamento dopo saldo | Nuovo | API/browser | Da eseguire |
| AC-05 | Analisi portafoglio — Cliente senza storico e testo sicuro | Nuovo | API/browser | Da eseguire |
| AC-06 | Analisi portafoglio — Modello locale disponibile | Nuovo | Simulato | Da eseguire |
| AC-07 | Analisi portafoglio — Ollama indisponibile | Nuovo | API simulata | Da eseguire |
| AC-08 | Analisi portafoglio — Navigazione e comprensione | Nuovo | Browser parziale; usabilità da fare | Da eseguire |
| AC-09 | Analisi portafoglio — Controlli limiti e AI incoerente | Nuovo | API simulata | Da eseguire |

## Ordine di ripresa e anomalie

1. Conservare i dati con processi fermi, aggiornare il ramo indicato nel runbook e avviare solo Uvicorn.
2. Usare il database di collaudo separato e la porta 8003 per gli importi di riferimento. Non azzerare il database di lavoro.
3. AC-01–03: classifica, dettaglio e ricerca. AC-04: registrare il saldo, verificare ricalcolo e persistenza. AC-05: cliente senza storico.
4. AC-06 solo con modello già disponibile; in alternativa AC-07 per indisponibilità. AC-08 richiede valutazione umana dell'usabilità. AC-09 ha già copertura automatica.
5. Riprendere i casi interni precedenti. Annotare esito, data, commit, atteso/osservato e ogni anomalia nelle celle gialle G:J del foglio Test.

**T04 aperto:** il testo email provvisorio può andare perso usando Riprogramma prima della conferma del messaggio. Non è corretto dichiararlo risolto in questa versione. Il contenuto confermato viene salvato separatamente. Nessun collaudo SMTP è necessario per osservare il difetto.

**Non ancora completati:** usabilità con utenti rappresentativi, qualità del modello locale reale, consolidamento dei rami su main e controlli di sicurezza del pilota. Le prove su saldo/finestra nei test automatici non attestano da sole la consegna reale. Il test reale del 20 novembre è conservato nel [registro email](Collaudo-email-follow-up.md).

