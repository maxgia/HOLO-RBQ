# Analisi del portafoglio clienti — specifica e collaudo

## Aggiornamento dopo il collaudo utente del 21 novembre 2026

**Esiti manuali confermati: AC-01–AC-06.** Verificati valore (Studio Rossi 100), criticità (Martina 71 con F-003 scaduta da 2 giorni), ricerca e omonimi, saldo F-001 di 500 euro con residuo Studio Rossi a 450 euro e scaduto/criticità zero, persistenza anche dopo riavvio e nuovo cliente senza storico. Le prove Ollama reali sul PC dell'utente hanno prodotto verifica incassi per Martina e continuità del rapporto per Studio Bianchi. Modello e SHA della copia ZIP non rilevati; queste prove non certificano la qualità su altri casi. AC-08 è parziale: navigazione verificata, tastiera e finestra stretta ancora da provare.

Il segnale osservato (Analisi clienti ricompare dopo Ctrl+F5) è compatibile con cache HTML, ma la causa sul browser dell'utente non è stata dimostrata. Il nuovo `app.py` serve `/` con **Cache-Control: no-store**. Questo evita nuove copie in cache; non ricarica automaticamente le schede aperte né elimina retroattivamente copie già conservate. Dopo il primo aggiornamento può servire Ctrl+F5 una volta, poi basta un normale F5. La pagina deve essere comunque ricaricata dopo un riavvio se già aperta.

La colonna **Posizione** ora mostra **Non classificato** solo in assenza di punteggio. Nessuna nuova colonna; punteggi non disponibili restano “—”, classifiche e parità rimangono invariate. Requisiti di affinamento RF-18 (cache HTML) e RF-19 (etichetta senza storico).

Codice fix `59b8907ef35629b3e963785ef3795dd245315df5`, [CI 44900599652](https://github.com/maxgia/HOLO-RBQ/actions/runs/44900599652): **20 Python, 11 Node e 14 Chromium superati**. Il test API verifica file HTML aggiornato dopo nuova istanza e richiesta condizionale; Chromium verifica reload normale e dicitura del nuovo cliente. Nessun invio SMTP reale. I test simulati del modello restano distinti dalle prove reali dell'utente.

L'[Excel aggiornato](HOLO-RBQ-Registro-test-2026-11-21.xlsx) contiene **37 casi**, con sei nuovi esiti umani Superato e un caso In corso. **AC-10** registra il collaudo pendente del fix cache e dell'etichetta Non classificato. AC-07 (modello assente), parte di AC-08 e controlli tecnici AC-09 restano aperti nel registro umano; AC-09 è già coperto automaticamente. Le sezioni con la prima consegna sotto sono evidenze storiche.


Aggiornamento: 21 novembre 2026. Requisiti RF-14–RF-17. Incremento D04, [PR #8](https://github.com/maxgia/HOLO-RBQ/pull/8), ramo `feat/analisi-portafoglio-clienti`. Il codice verificato è `c40639f12d22495292b5175033b4796ce01a711c`. Il modulo è implementato e verificato automaticamente; accettazione manuale e prova del modello reale restano aperte.

## Obiettivo e perimetro

Confrontare i clienti per valore economico registrato e criticità degli incassi, spiegare le priorità e preparare azioni interne di gestione e fidelizzazione. Un cliente può avere insieme valore elevato e scaduto elevato. L'app evita di definirlo buono o cattivo sulla base di un solo punteggio.

La pagina **Analisi clienti**, accessibile dal menu laterale, mostra posizione, nome, punteggi, quantità dello storico, fatturato, incassato, residuo e scaduto. Consente ordinamento, ricerca, dettaglio, fattura prioritaria e apertura della scheda corretta. Le bozze vengono conteggiate separatamente e non sono ricavi. Il salvataggio di un cliente, di una bozza o di un incasso aggiorna il confronto.

Il confronto considera tutto l'archivio locale. Non sono presenti filtri di periodo, margini, costi delle prestazioni, insolvenza stimata o misure di puntualità storica: mancano i relativi dati. Le scadenze demo sono inizializzate in rapporto alla data del primo avvio del database. I risultati cambiano con la data e con gli incassi.

## Metodo spiegabile RBQ-CLIENTI-1

Gli importi provengono da SQLite in centesimi interi. I rapporti e l'arrotondamento dei punteggi usano Decimal, arrotondamento alla metà verso l'alto. Le letture di clienti, fatture e bozze avvengono nella stessa transazione di lettura. Nessuna scrittura è effettuata dalle API di analisi.

| Indicatore | Regola |
|---|---|
| Fatturato | Somma degli importi delle fatture del cliente. |
| Incassato | Somma degli incassi registrati sulle fatture del cliente. |
| Residuo | Fatturato meno incassato. |
| Scaduto | Somma dei residui positivi con scadenza precedente alla data del server. Una fattura in scadenza oggi non è ancora scaduta. |
| Ritardo aperto massimo | Giorni dalla più vecchia scadenza con residuo positivo; zero se non esiste scaduto. Non è la media dei ritardi nei pagamenti storici. |
| Valore, 0–100 | 70 × incassato / massimo incassato del portafoglio + 30 × numero fatture / massimo numero fatture del portafoglio. Un termine con denominatore zero vale zero. |
| Criticità, 0–100 | 70 × scaduto / residuo + 30 × min(ritardo massimo / 60, 1). Il rapporto scaduto/residuo vale zero se non esiste residuo. |
| Storico | Nessuna fattura, Storico limitato (1–2 fatture), Almeno 3 fatture. Non è una misura di affidabilità statistica. |

Se il fatturato è zero, punteggi, posizione e quota incassata non sono disponibili. Non si assegna un buon giudizio al cliente per l'assenza di dati. Le posizioni si calcolano sull'intero portafoglio prima della ricerca. Punteggi uguali condividono la posizione; importi e nome determinano un ordine stabile. Per esempio, la ricerca di un solo cliente non lo trasforma automaticamente nel primo classificato.

## Regole e AI locale

Il dettaglio mostra sempre un'azione ricavata da regole locali: completare lo storico, verificare incassi, preparare un piano di rientro, preparare continuità del rapporto o approfondire opportunità già note. Le soglie di 30 giorni per l'azione di rientro e di 60 punti per la continuità sono euristiche demo, modificabili in una futura calibrazione; non sono valutazioni creditizie validate.

Il pulsante **Suggerisci azione con AI locale** usa facoltativamente il modello Ollama già installato sul PC. L'AI sceglie tra le azioni ammesse dalla situazione corrente; il server restituisce un testo fisso coerente con la scelta. Non genera importi, comunicazioni o analisi predittive. Con scaduto positivo sono ammesse verifica degli incassi o preparazione del piano; senza scaduto continuità o approfondimento delle opportunità. Senza storico l'app risponde direttamente senza interrogare il modello.

Il modello riceve soltanto indicatori aggregati, giorni e azioni ammesse: nome, contatti, testi delle bozze e dettagli personali del cliente non sono inclusi nel prompt. L'endpoint è fisso su `http://127.0.0.1:11434/api/chat`, con proxy disabilitati, timeout 30 secondi, schema JSON Pydantic, temperatura zero e limite di generazione. Le risposte non valide o incoerenti sono rifiutate; se Ollama è assente la classifica e le regole restano utilizzabili. Il codice non scarica modelli e non chiama provider AI esterni.

## Contratti tecnici

| Endpoint | Risultato / errori |
|---|---|
| `GET /api/customer-analysis?sort=value&q=` | Data, metodo e clienti con indicatori e posizione. `sort=risk` ordina per criticità; ordinamento diverso rifiutato 422. Ricerca senza corrispondenze restituisce un elenco vuoto. |
| `POST /api/customer-analysis/{client_id}/advice` | Azione e fonte, calcolate rileggendo lo stato corrente. 404 cliente inesistente, 503 modello non disponibile, 502 output inutilizzabile o non ammesso. Non modifica il database. |

Componenti: `customer_analysis.py`, funzione condivisa `local_structured_response` in `customer_assistant.py`, API in `app.py`, interfaccia in `index.html`. Il frontend inserisce i nomi con `textContent`, mantiene distinti gli identificativi dei clienti e scarta risposte asincrone superate durante ricerca o cambio selezione.

## Collaudo eseguito

[GitHub Actions 44881200826](https://github.com/maxgia/HOLO-RBQ/actions/runs/44881200826): **19 test Python, 11 test Node, 13 test browser Chromium superati**. Le nuove verifiche comprendono:

- Confronto indipendente degli importi demo e dei punteggi; ricerca senza cambio della posizione e separazione degli omonimi.
- Ricalcolo dopo saldo F-001 e persistenza dopo nuova apertura dell'app.
- Nuovo cliente senza fatture, denominatore zero, scadenza oggi e ricerca vuota.
- Scelta AI simulata coerente, scelta incoerente respinta, assenza modello, JSON invalido e controllo dell'endpoint loopback.
- Navigazione reale in Chromium, ordinamento e ricerca, apertura dettaglio e scheda, risposta AI simulata, aggiornamento tabella dopo saldo e nuovo cliente con caratteri HTML nel nome.

I test usano database temporanei e trasporti simulati per email e AI. Nessuna email è stata inviata in questa sessione. L'ambiente non dispone di Ollama: qualità e tempi del modello reale non sono stati verificati. Non è stato svolto un test di usabilità con utenti né un penetration test; non si attesta conformità o certificazione.

## Ripresa del collaudo utente

L'Excel [Registro test](HOLO-RBQ-Registro-test-2026-11-21.xlsx) censisce 36 casi, tra storico e nuove prove. Per ogni ID il foglio **Passi** contiene preparazione, azioni e risultato atteso; **Test** separa conferme storiche, copertura automatica e nuovo esito umano. Compilare le celle gialle G:J con esito, data, commit e osservazioni. Le conferme generiche precedenti sono indicate come tali; il commit della vecchia copia Windows non è noto.

Eseguire AC-01–03 su una copia demo nuova prima di AC-04, che registra un saldo. Su archivio nuovo Studio Rossi ha 1.850 euro fatturati, 900 incassati, 950 residui, 500 scaduti, 12 giorni di scaduto aperto, valore 100 e criticità 43. Dopo un incasso a saldo di 500 euro sulla F-001 restano 450 euro complessivi, scaduto zero e criticità zero. Un archivio già usato deve essere valutato sui suoi dati reali, senza aspettarsi questi importi.

Per le prove interne lasciare spento `follow_up_email.py`. Non servono credenziali SMTP. AC-06 richiede un modello locale già installato; in sua assenza registrare Bloccato o provare AC-07. Restano aperti T04 (perdita testo email non confermato durante riprogrammazione), prove esterne differite, consolidamento su main, usabilità e controlli del pilota.
