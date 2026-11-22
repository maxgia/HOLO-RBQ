# Regressione completa su PostgreSQL — 22 novembre 2026

Richiesta: rieseguire tutti i test disponibili della precedente versione SQLite dopo il passaggio a PostgreSQL. [PR #10](https://github.com/maxgia/HOLO-RBQ/pull/10), codice test `bc20dfc55f814ed2535fc57120af34a23a00932b`, [CI 45037721777](https://github.com/maxgia/HOLO-RBQ/actions/runs/45037721777). Tutti i tre job conclusi con successo. Il codice applicativo resta quello della versione 0.3.0-postgres; sono aggiunti soltanto un runner di test, la sua esecuzione CI e le evidenze.

## Risultati e conteggi

| Gruppo | Esito | Perimetro |
|---|---|---|
| API/funzioni originali su PostgreSQL | 20/20 superati | 13 MVP, 6 analisi clienti, 1 scenario worker con molte asserzioni. |
| Browser originali su PostgreSQL | 14/14 superati | 12 fatture/clienti/analisi/attività/guida, 2 preventivi. |
| Migrazione e concorrenza PostgreSQL | 9/9 superati | Copia completa, digest, identità, pagamenti concorrenti, modifiche stale, rifiuti, rollback, configurazione e worker. |
| Browser specifico post-migrazione | 1/1 superato | Unicode, dati importati, saldo e analisi dopo reload. |
| Configurazione e launcher Python | 7/7 superati | 2 configurazione e 5 launcher. |
| Parser/interazioni JavaScript | 11/11 superati | Suite Node originale. |
| Compatibilità SQLite | 20/20 Python e 14/14 browser superati | Le prove originali sono rieseguite anche sulle fixture SQLite. |
| Preparazione Windows PowerShell 5.1 | Superata | Installazione, percorsi con spazi, configurazione assente e mancato fallback. |

Nel job PostgreSQL la discovery ordinaria esegue 36 Python e 15 browser; segue la nuova esecuzione di 34 test originali su PostgreSQL. I 36 non sono tutti test PostgreSQL: 20 usano le fixture SQLite originali, 9 PostgreSQL e 7 configurazione/launcher. Il runner aggiuntivo copre questa differenza. I conteggi per gruppo descrivono prove e backend, non nuove funzionalità o nuovi collaudi umani. Le prove saltate nel job senza server PostgreSQL non sono contate come superate; le corrispondenti prove sono eseguite nel job PostgreSQL.

## Come viene riutilizzata la suite

`tests/run_postgres_regression.py` carica i moduli originali senza cambiare le asserzioni. Le factory di creazione dell'app e le connessioni dirette delle sole fixture sono sostituite per questa esecuzione. Ogni archivio temporaneo viene inizializzato/aggiornato in SQLite e migrato in uno schema PostgreSQL isolato. Tutte le successive richieste API e manipolazioni funzionali usano PostgreSQL. Il test legacy costruisce prima il suo sorgente SQLite storico e ne verifica l'accesso dopo conversione e trasferimento.

Risultato del runner: **34 prove, zero errori, zero fallimenti, zero skip**, 35 schemi isolati, 43 istanze applicative PostgreSQL. Gli schemi vengono rimossi al termine. Il runner richiede HOLO_TEST_DATABASE_URL e rifiuta nomi database che non terminano in _test e la coincidenza con HOLO_DATABASE_URL. Non legge data/postgres.json e non usa l'archivio del PC utente. Si avvia nella CI con `python tests/run_postgres_regression.py`, dopo le normali dipendenze e Chromium. L'ambiente di prova e' definito nel workflow, non nella configurazione operativa.

Il [JSON originale del runner](Regressione-PostgreSQL-2026-11-22.json) conserva nomi, esiti e durate caso per caso. Lo stesso JSON e' allegato come artifact postgres-regression-results alla CI; questa copia nel repository ne conserva la tracciabilita' anche dopo la scadenza dell'artifact.

## Cosa rimane distinto

- Sender SMTP simulato: autenticazione al provider e consegna reale non vengono ripetute.
- Ollama simulato: trasporto, errori e azioni ammesse sono verificati, la qualita' del modello reale richiede prova sul PC.
- Testo email non confermato perso durante riprogrammazione: T04/D06 resta aperto e non coperto da una prova di correzione.
- Usabilita' strutturata, sicurezza del pilota e conformita' non sono chiuse da questa regressione.
- Le vecchie prove manuali non vengono automaticamente promosse a nuovi esiti umani. L'Excel mantiene le conferme preesistenti e le prove ancora da fare.

## Evidenze locali dell'utente

Il 22 novembre: installazione PostgreSQL e creazione holo_rbq in pgAdmin, individuazione della copia SQLite corretta in OneDrive, otto tabelle trovate, migrazione verificata e successivo Avvia-HOLO.cmd riuscito. Lo screenshot mostra 0.3.0-postgres, configurazione PostgreSQL e API 200. L'utente conferma clienti migrati e accetta assenza follow-up. Nessuna credenziale e' riportata nelle evidenze di progetto.

| Tabella | Righe trasferite verificate |
|---|---:|
| clients | 4 |
| previews | 0 |
| drafts | 1 |
| invoices | 5 |
| demo_payments | 1 |
| follow_ups | 0 |
| edits | 1 |
| follow_up_emails | 0 |

PG-01 e PG-02 sono Superato nel registro, con data 22/11/2026 e versione mostrata 0.3.0-postgres (SHA locale non rilevato). PG-03 e AC-11 sono In corso: confermati clienti e primo avvio, non il confronto completo e tutti i controlli launcher. PG-04 e PG-05 restano Da eseguire. Il 404 favicon riguarda l'icona e resta un difetto cosmetico noto, senza modifica in questo incremento.

## Avanzamento

D10: sviluppo e regressione completati, migrazione locale eseguita, accettazione funzionale sul PC ancora parziale. A06 gestionale reale rimane aperta; D09 UX/UI segue la chiusura dei controlli PostgreSQL concordati. Nessuna nuova integrazione esterna introdotta.

