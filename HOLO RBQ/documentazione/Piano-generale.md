# Piano generale HOLO RBQ

## D12 — dataset dimostrativo esteso, 22 novembre 2026

Preparati 15 clienti sintetici, 21 fatture, 12 incassi, 6 bozze e 9 attività, riconoscibili da DEMO |. Caricatore additivo con anteprima, conferma locale, transazione, protezione dai duplicati e nessuna email creata. [Casi e procedura](Dataset-demo-v1.md), [registro scenari per Excel](Scenari-demo-v1.csv). Il caricamento sul PC è ancora da eseguire; i dati esistenti non sono stati raggiunti.

La prima verifica locale del piano dati è superata; integrazione PostgreSQL da verificare in CI. Il dataset amplia i casi del collaudo, non chiude i test umani. UX-01 e UX-02 sono stati confermati nella prima sessione; l’utente ha chiesto di ripartire da UX-01 al prossimo incontro. UX-03–UX-05 restano da eseguire. Il logo è stato confermato sul PC. A06 e pubblicazione online rimangono rinviate.

## D09 — nuova esperienza operativa, 22 novembre 2026

Implementate Home sintetica, pagine dedicate, scheda cliente a tab, pianificazione follow-up con calendario e Report con esportazione CSV. Dati calcolati e proposte AI sono in tabelle. Grafica scura con accenti lavanda, azioni principali evidenti e tabelle scorrevoli. [Specifica e passi di prova](UX-UI-D09.md), [PR #12](https://github.com/maxgia/HOLO-RBQ/pull/12).

Codice `fcd9643`, [CI 45042571780](https://github.com/maxgia/HOLO-RBQ/actions/runs/45042571780): 36 Python, 11 Node, 20 Chromium superati; 39 prove funzionali ripetute su PostgreSQL reale e preflight Windows superati. AI e SMTP simulati. Registro Excel aggiornato a 48 casi: nove esiti umani Superato preservati, cinque nuovi casi UX-01–UX-05 Da eseguire. PG-03/AC-11 restano In corso, PG-04–05 e T04 non chiusi dal collaudo automatico.

D09 implementato, da validare sul PC. A06 gestionale resta aperta. Il Report fotografa lo stato corrente: lo storico completo richiede D11, ancora da pianificare. Nessuna modifica al database, nuova migrazione o nuovo invio esterno.

## D06 / T04 — correzione del 22 novembre 2026

Corretto il testo email perso durante la riprogrammazione: una bozza per attività conserva oggetto, testo, ora e apertura pannello nelle due viste. Il cambio giorno mantiene l’ora scelta. Non programma invii e non scrive automaticamente sul database; F5 o chiusura pagina perdono il testo non confermato. Conferma, annullamento e completamento eliminano la bozza dopo successo.

[PR #11](https://github.com/maxgia/HOLO-RBQ/pull/11), codice `4cf953d`, [CI 45039238415](https://github.com/maxgia/HOLO-RBQ/actions/runs/45039238415): 36 Python, 11 Node, 17 Chromium e 36 prove funzionali del runner PostgreSQL, oltre al preflight Windows. Due scenari browser nuovi verificano T04 su SQLite e PostgreSQL. Nessun invio reale; schema e backend invariati. [Passi di collaudo e limiti](Correzione-bozza-email-D06.md).

D06 implementato e verificato automaticamente, T04 utente ancora Da eseguire. Excel: 43 casi e nove esiti umani Superato invariati. PG-03–05 restano nei rispettivi stati; A06 gestionale resta aperta, D09 UX/UI ancora pianificata.

## Collaudo del 22 novembre 2026

Migrazione sul PC Windows e primo avvio PostgreSQL confermati dall’utente. Copiate e verificate otto tabelle: 4 clienti, 0 anteprime, 1 bozza, 5 fatture, 1 incasso, 0 follow-up, 1 modifica, 0 email. Assenza dei follow-up accettata. PG-01–02 Superato; PG-03 e AC-11 In corso; PG-04–05 ancora da eseguire sul PC.

[CI 45037721777](https://github.com/maxgia/HOLO-RBQ/actions/runs/45037721777), codice `bc20dfc`: 34 prove funzionali originali rieseguite su PostgreSQL (20 Python e 14 Chromium), tutte superate. Superati anche nove test PostgreSQL specifici, i controlli di configurazione e launcher, gli 11 Node e la regressione SQLite. Sender e AI simulati; nessun accesso al database operativo e nessun invio reale. [Report per caso](Regressione-PostgreSQL-2026-11-22.md).

Registro Excel: 43 casi, 9 nuovi esiti umani Superato complessivi. Le sette conferme precedenti restano storiche. D10 in collaudo; D09 UX/UI segue questo passaggio; A06 resta aperta. Le indicazioni del 21 novembre sul trasferimento ancora da eseguire descrivono lo stato precedente.

## Nuova priorita': D10 PostgreSQL, poi D09 UX/UI

Su richiesta del 21 novembre, prima del ridisegno si passa a PostgreSQL e si trasferisce l'archivio attuale. Backend e procedura della versione 0.3.0-postgres sono preparati e verificati su PostgreSQL 17 reale. **Il trasferimento dei dati effettivi dell'utente e' ancora da eseguire sul suo PC**: servono server/database PostgreSQL e il file SQLite della copia operativa. A06 resta APERTA, distinta da questo cambio di database.

La [PR #9](https://github.com/maxgia/HOLO-RBQ/pull/9) contiene runtime PostgreSQL, configurazione guidata, backup e copia delle otto tabelle con digest, tutela della destinazione non vuota e riallineamento progressivi. Nessuna nuova email inviata. [Procedura](Migrazione-PostgreSQL.md).

[CI 44936628150](https://github.com/maxgia/HOLO-RBQ/actions/runs/44936628150), codice `569ec22`: **36 Python (9 specifici PostgreSQL), 11 Node e 15 Chromium (uno specifico PostgreSQL) superati**. Preflight Windows superato per dipendenze e configurazione assente senza fallback SQLite. L'avvio completo sul PC utente viene collaudato dopo la migrazione.

Registro Excel esteso a **43 casi**. Le sette conferme utente precedenti rimangono evidenze sulla versione SQLite 0.2; PG-01–PG-05 sono tutti pendenti. D09 riparte dopo verifica dei dati PostgreSQL. D10 non e' compreso automaticamente nelle vecchie stime del pilota.

Aggiornato il 21 novembre 2026 dopo il collaudo utente e la preparazione della demo consolidata 0.2.0-demo. Il punto di rilascio e' la [PR #8](https://github.com/maxgia/HOLO-RBQ/pull/8), indirizzata a main per riunire le funzioni e i documenti dei rami precedenti. Il materiale precedente e' conservato nel [piano storico](Piano-generale-storico-20261121.md).

**A06 resta aperta:** l'utente sta cercando un gestionale reale. TeamSystem e Buffetti restano ipotesi; prodotto, azienda/partita IVA di prova, accessi API e tempi non sono definiti. Nessuna nuova integrazione esterna viene sviluppata in questa fase.

## Avanzamento rispetto al piano originario

| ID | Attivita' | Stato attuale | Condizione per chiuderla |
|---|---|---|---|
| A01 | MVP locale, repository e runbook | Realizzata | Conservare avvio riproducibile e documentazione a ogni rilascio. |
| A02 | Regressione API e riconoscimento | Realizzata, estesa | Suite corrente 36 Python e 11 Node. |
| A03 | Collaudo browser preventivi e CI | Realizzata | Regressione mantenuta sul rilascio. |
| A04 | Browser fatture e guida | Realizzata, estesa | Suite corrente 20 Chromium e collaudo avvio Windows. |
| A05 | Prima prova di sviluppo multiagente | Prova storica eseguita | Non equivale a orchestrazione continuativa: questa resta da progettare e sviluppare. |
| A06 | Gestionale reale e definizione pilota | APERTA, ricerca in corso | Identificare prodotto, referente, azienda di prova, accessi e criteri di accettazione. |
| A07 | Integrazione gestionale in lettura | In attesa di A06 | Confronto anagrafiche, fatture, scadenze e incassi con dati reali. |
| A08 | Qualita' assistente e usabilita' | Collaudo demo parziale | Completare casi mancanti e prove con utenti rappresentativi; estendere al gestionale dopo A07. |
| A09 | Sicurezza e applicabilita' conformita' | Da definire per pilota | Perimetro, minacce, ruoli, dati e responsabilita' approvati. |
| A10 | Controlli e verifiche del pilota | In attesa del perimetro | Accessi, isolamento, segreti, audit, dipendenze e ripristino verificati. |
| A11 | Pilota e decisione rilascio | In attesa | Accettazione funzionale, usabilita' e rischi residui registrati. |

## Incrementi aggiunti durante la demo

| ID | Incremento | Stato | Passo residuo |
|---|---|---|---|
| D01 | Clienti manuali e incassi demo | Implementato, confermato utente | Mantenere regressione. |
| D02 | Analisi scheda, domande e attivita' | Implementato, confermato nei flussi provati | Valutare qualita' su piu' casi. |
| D03 | Email programmate e verifica saldo | Implementato; collaudo storico parziale | Prove esterne rinviate; worker non avviato da D08. |
| D04 | Classifiche clienti e azioni AI locali | Implementato; AC-01–06 e AC-10 confermati | AC-07 e usabilita' AC-08 ancora aperti; AC-09 coperto automaticamente. |
| D05 | Tracciabilita' e registro Excel | Aggiornato, 48 casi | Registrare ogni nuova prova con data, versione e osservato. |
| D06 | Conservazione testo email non confermato | Fix verificato automaticamente | Collaudo manuale T04 da eseguire; bozza limitata alla pagina aperta. |
| D07 | Consolidamento della demo | Incluso nel rilascio della PR #8 su main | Verificare esito merge e conservare riferimento al rilascio. |
| D08 | Avvio locale semplificato | Implementato; verificato su Windows in CI | Collaudo utente AC-11 del doppio clic e dell'apertura browser. |
| D09 | Revisione UX/UI | Implementata e verificata in CI | UX-01–UX-05 sul PC e usabilità con utenti rappresentativi. |
| D10 | PostgreSQL e trasferimento archivio | Migrazione e primo avvio utente confermati | PG-03 in corso, PG-04–05 da eseguire. |
| D11 | Registro storico delle operazioni | Da pianificare | Definire eventi, autori, date, conservazione e prove; nessuna ricostruzione retroattiva. |

## Prossima verifica: D09 sul PC, senza attendere A06

La [fase D09](UX-UI-D09.md) è implementata. Seguire i cinque nuovi casi dell’Excel e il protocollo di usabilità, annotando autonomia, tempi, aiuti ed errori. Conservare il contesto PostgreSQL e lasciare il worker spento. Dopo la revisione utente, pianificare D11 e i controlli interni del pilota; A07 rimane dipendente dalla scelta A06.

## Evidenze della consegna

- Codice di avvio: `10a57d80f787b6d7d0deaf1f20ebf58319c1665d`.
- [CI 44903612254](https://github.com/maxgia/HOLO-RBQ/actions/runs/44903612254): **25 Python + 11 Node + 14 Chromium superati**, oltre al collaudo Windows PowerShell 5.1.
- Windows: creazione .venv da copia pulita con spazi nel percorso, avvio da altra directory, porta occupata rifiutata, persistenza al riavvio e nessuna reinstallazione con requisiti invariati.
- Utente: sette casi AC-01–AC-06 e AC-10 superati. AC-10 confermato dopo aggiornamento dei file nella cartella effettiva; include F5 normale dopo riavvio e Non classificato.
- Nessun nuovo invio SMTP o collegamento a gestionale reale. Test automatici dell'AI con simulazioni; due scenari Ollama reali verificati dall'utente.
- [Registro Excel](HOLO-RBQ-Registro-test-2026-11-21.xlsx), [registro delle prove](Registro-collaudo-2026-11-21.md), [avvio](Runbook.md).

## Tempi e dipendenze

La precedente stima A06–A11 di **18–33 giorni-persona** resta una previsione da rivedere quando sara' definito il pilota; non e' una data di consegna e non include automaticamente tutti gli ampliamenti. La stima precedente D06 era 0,5–1 giorno-persona, da verificare all'avvio. La prima implementazione D09 è consegnata; tempi del collaudo umano, correzioni e D11 saranno stimati separatamente.

La disponibilita' del gestionale condiziona integrazione e pilota, non il perfezionamento interno della demo. Nessuna percentuale complessiva viene ricavata contando attivita' di dimensioni diverse.

