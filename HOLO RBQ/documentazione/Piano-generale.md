# Piano generale HOLO RBQ

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
| A02 | Regressione API e riconoscimento | Realizzata, estesa | Suite corrente 25 Python e 11 Node. |
| A03 | Collaudo browser preventivi e CI | Realizzata | Regressione mantenuta sul rilascio. |
| A04 | Browser fatture e guida | Realizzata, estesa | Suite corrente 14 Chromium e collaudo avvio Windows. |
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
| D05 | Tracciabilita' e registro Excel | Aggiornato, 38 casi | Registrare ogni nuova prova con data, versione e osservato. |
| D06 | Conservazione testo email non confermato | Da sviluppare, difetto T04 aperto | Correggere e testare riprogrammazione senza invii reali. |
| D07 | Consolidamento della demo | Incluso nel rilascio della PR #8 su main | Verificare esito merge e conservare riferimento al rilascio. |
| D08 | Avvio locale semplificato | Implementato; verificato su Windows in CI | Collaudo utente AC-11 del doppio clic e dell'apertura browser. |
| D09 | Revisione UX/UI | PIANIFICATA, dopo D10 | Analisi dei flussi, campione di interfaccia, revisione e test dopo copia e verifica dei dati. |
| D10 | PostgreSQL e trasferimento archivio | Codice verificato; migrazione reale APERTA | Configurazione sul PC, PG-01–PG-05 e accettazione dei dati copiati. |

## Prossima fase: UX/UI senza attendere A06

La [fase D09](Piano-UX-UI.md) affronta navigazione, gerarchia delle informazioni, leggibilita' delle tabelle, distinzione tra regole e AI, stati di caricamento/errore/assenza dati, tastiera e finestre strette. Prima si verifica un campione con l'utente, poi si estende il disegno. Il riferimento grafico precedente resta Linear.

La revisione demo puo' procedere mentre la ricerca del gestionale e' aperta. Dopo A06–A07 si adatteranno i flussi alle operazioni e ai dati reali. Non sono ancora state applicate modifiche grafiche della fase D09.

## Evidenze della consegna

- Codice di avvio: `10a57d80f787b6d7d0deaf1f20ebf58319c1665d`.
- [CI 44903612254](https://github.com/maxgia/HOLO-RBQ/actions/runs/44903612254): **25 Python + 11 Node + 14 Chromium superati**, oltre al collaudo Windows PowerShell 5.1.
- Windows: creazione .venv da copia pulita con spazi nel percorso, avvio da altra directory, porta occupata rifiutata, persistenza al riavvio e nessuna reinstallazione con requisiti invariati.
- Utente: sette casi AC-01–AC-06 e AC-10 superati. AC-10 confermato dopo aggiornamento dei file nella cartella effettiva; include F5 normale dopo riavvio e Non classificato.
- Nessun nuovo invio SMTP o collegamento a gestionale reale. Test automatici dell'AI con simulazioni; due scenari Ollama reali verificati dall'utente.
- [Registro Excel](HOLO-RBQ-Registro-test-2026-11-21.xlsx), [registro delle prove](Registro-collaudo-2026-11-21.md), [avvio](Runbook.md).

## Tempi e dipendenze

La precedente stima A06–A11 di **18–33 giorni-persona** resta una previsione da rivedere quando sara' definito il pilota; non e' una data di consegna e non include automaticamente tutti gli ampliamenti. La stima precedente D06 era 0,5–1 giorno-persona, da verificare all'avvio. D09 verra' stimata dopo analisi dei flussi e scelta del campione.

La disponibilita' del gestionale condiziona integrazione e pilota, non il perfezionamento interno della demo. Nessuna percentuale complessiva viene ricavata contando attivita' di dimensioni diverse.

