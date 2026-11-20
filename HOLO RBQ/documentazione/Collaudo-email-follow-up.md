# Collaudo dell’invio programmato dei follow-up

La prova usa due finestre PowerShell, una per HOLO RBQ e una per il worker. Usa una tua casella come destinatario e una casella mittente con autenticazione SMTP su TLS implicito. Recupera dal provider host, porta, nome utente e credenziale SMTP. Il worker usa la porta 465 di default. La configurazione richiede un provider compatibile con autenticazione SMTP tramite nome utente e password.

## 1. Aggiorna e avvia HOLO RBQ

Ferma il server precedente con **Ctrl+C**. Apri PowerShell nella cartella `HOLO RBQ\codice-sorgente`. I comandi presuppongono l’ambiente virtuale dell’MVP già installato.

```powershell
git fetch origin
git switch feat/follow-up-email
git pull --ff-only origin feat/follow-up-email
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
$env:HOLO_TEST_RECIPIENT = "tua-casella@example.com"
.\.venv\Scripts\python.exe -m uvicorn app:create_app --factory --host 127.0.0.1 --port 8002
```

Sostituisci l’indirizzo di esempio prima dell’avvio. Lascia la finestra aperta. Apri [HOLO RBQ](http://127.0.0.1:8002/) quando appare `Uvicorn running`. Se la porta è occupata, usa 8003 sia nel comando sia nel browser.

## 2. Avvia il worker SMTP

Apri un’altra finestra PowerShell nella stessa cartella. Usa lo stesso indirizzo di prova. Adatta dominio, porta e credenziali al tuo provider.

```powershell
$env:HOLO_TEST_RECIPIENT = "tua-casella@example.com"
$env:HOLO_SMTP_HOST = "smtp.example.com"
$env:HOLO_SMTP_PORT = "465"
$env:HOLO_SMTP_FROM = "mittente@example.com"
$env:HOLO_SMTP_USER = "mittente@example.com"
$secret = Read-Host "Credenziale SMTP" -AsSecureString
$env:HOLO_SMTP_PASSWORD = [System.Net.NetworkCredential]::new("", $secret).Password
try {
    .\.venv\Scripts\python.exe follow_up_email.py
} finally {
    Remove-Item Env:HOLO_SMTP_PASSWORD -ErrorAction SilentlyContinue
    Remove-Variable secret -ErrorAction SilentlyContinue
}
```

Attendi il messaggio **Worker email di prova attivo**. Il worker legge lo stesso SQLite dell’app e controlla gli invii ogni 10 secondi quando è inattivo. Il browser converte l’orario inserito in UTC. Per il collaudo imposta Windows sul fuso italiano. App e worker consentono l’invio dalle 09:00 fino alle 20:00 escluse, ora italiana, nel giorno del follow-up. Se il worker riparte a finestra conclusa, l’email va in revisione. Il PC deve restare acceso e il worker attivo. Puoi chiudere il browser.

## 3. Esegui le prove

| Caso | Passi | Risultato atteso |
|---|---|---|
| MAIL-01 · Invio | In **Clienti → Studio Rossi**, crea un nuovo follow-up. Apri **Programma email di prova**, inserisci oggetto riconoscibile e testo fittizio, scegli un orario 2–3 minuti in avanti e conferma. | Prima dell’orario lo stato è **Programmata** e la casella è vuota. Dopo l’orario, ricarica la pagina e apri **Attività**. Lo stato è **Inviata** dopo accettazione SMTP. Controlla la ricezione e la cartella spam. |
| MAIL-02 · Annullamento | Crea un secondo follow-up e programma un’altra email. Riapri il pannello e scegli **Annulla invio** prima dell’orario. | Lo stato è **Annullata**. All’orario previsto la seconda email non arriva. |
| MAIL-03 · Riprogrammazione | Programma un terzo invio, riapri il pannello, imposta un nuovo orario più avanti e conferma. | L’invio resta programmato per il nuovo orario. Arriva una sola email. |
| MAIL-04 · Riavvio | Programma un invio e ferma il worker prima della scadenza. Riavvialo dopo la scadenza con i comandi del punto 2. | L’invio ancora programmato viene elaborato alla ripartenza. Un ulteriore riavvio non lo spedisce di nuovo. |
| MAIL-05 · Residuo cambiato | Con un archivio demo in cui F-001 ha ancora residuo, crea un follow-up dalla fattura e programma l’email. Registra un incasso parziale prima dell’orario. | Dopo l’orario, lo stato è **Da rivedere**. Correggi il testo con il nuovo importo e conferma un nuovo orario se vuoi continuare. |
| MAIL-06 · Fattura saldata | Programma un nuovo invio su F-001 con un residuo positivo, poi registra l’incasso dell’intero residuo prima dell’orario. | Subito dopo il saldo l’email è **Sospesa · fattura saldata**. L’avviso compare entro circa 10 secondi. Apri **Attività** e scegli **Annulla sollecito**. Lo stato diventa **Annullata** e l’email non arriva. |
| MAIL-07 · Finestra di invio | Prova a confermare alle 08:59, alle 20:00 oppure il giorno successivo al follow-up. | L’app rifiuta la pianificazione. |

Per verificare MAIL-05 e MAIL-06 in sequenza, annulla prima l’email rimasta **Da rivedere**. Registra per ogni caso il commit (`git rev-parse --short HEAD`), l’orario impostato, l’esito in app, l’eventuale ricezione e il risultato Osservato/Atteso. Usa oggetti distinti per ogni prova.

## 4. Leggi gli esiti e termina

- Se manca **Programma email di prova**, verifica `HOLO_TEST_RECIPIENT` nella finestra del server e riavvia Uvicorn. Per le attività completate o le fatture saldate l’invio non è programmabile.
- Se lo stato resta **Programmata**, verifica che il worker sia attivo, che abbia lo stesso database e destinatario e che l’orario sia già passato. Ricarica la pagina.
- **Esito da verificare** indica un errore o esito SMTP incerto. **In invio** può restare visibile se il worker viene interrotto durante la consegna. In entrambi i casi controlla casella e log del provider prima di creare un nuovo invio. Il worker evita il reinvio automatico di queste email.
- A fine prova ferma il worker con **Ctrl+C** e chiudi la relativa finestra. I test automatici usano un trasporto fittizio e coprono l’orario, l’annullamento, il destinatario consentito, i cambi di residuo e l’esito SMTP incerto. La conferma della consegna reale si ottiene eseguendo MAIL-01 con il proprio provider.

Dopo **Salva follow-up**, HOLO RBQ apre il pannello email direttamente nella nuova attività della scheda cliente se l’invio è programmabile. Il destinatario viene dalla configurazione del server. Il test browser verifica apertura, destinatario e conferma della pianificazione senza avviare il worker SMTP.

## Verifica della versione di collaudo

La versione con apertura automatica del pannello è disponibile dal commit `ee1aea5`.

Se il pannello non si apre, verifica il ramo e il commit con `git branch --show-current` e `git rev-parse --short HEAD`. Controlla che `HOLO_TEST_RECIPIENT` sia impostata nella finestra di Uvicorn e ricarica la pagina.


## Registro ripetibile del collaudo del 20 novembre 2026

Ambiente dichiarato dall’utente: Windows, PowerShell 5.1, HOLO RBQ su 127.0.0.1:8002, SQLite locale e worker separato. La copia in uso è stata recuperata da una versione precedente. Il commit locale effettivo non è stato rilevato nella sessione. Le conferme manuali seguenti sono state fornite in chat e tramite schermate.

Per ripetere ogni prova annotare data, ora italiana, commit o versione dello ZIP, titolo univoco del follow-up, eventuale numero fattura, residuo iniziale, stato osservato ed eventuale ricezione. Le operazioni di incasso modificano i dati demo. Prima di una nuova sessione conservare una copia del database con app e worker fermi.

| Caso | Preparazione e passi operativi | Risultato atteso | Esito della sessione |
|---|---|---|---|
| T01 · Avvio e destinatario | Avviare Uvicorn nella cartella contenente app.py dopo aver impostato HOLO_TEST_RECIPIENT sulla propria casella. Aprire Clienti → Studio Rossi. Creare un follow-up aperto senza documento. | Il pannello Programma email di prova espone il destinatario configurato. | Superato. L'indirizzo di esempio iniziale è stato sostituito nella configurazione locale. |
| T02 · Pianificazione e persistenza | Inserire oggetto e testo. Scegliere un giorno futuro per il follow-up e la stessa data alle 10:00 per l'email. Confermare, ricaricare, riaprire il pannello. | Stato Programmata. Data, oggetto e testo salvati sono rileggibili. | Confermato dall'utente. Nella schermata il follow-up del 21 novembre risultava programmato alle 09:00. |
| T03 · Annullamento prima dell'invio | Con email Programmata e worker fermo, aprire il pannello e premere Annulla invio. Ricaricare. | Email Annullata. Il follow-up può restare Aperto. | Superato. La schermata mostra Test pannello email con Email Annullata. |
| T04 · Modifica data con testo non confermato | Scrivere testo nel pannello e usare Riprogramma sulla data dell'attività prima di confermare l'email. Riaprire il pannello. | Rilevare se il testo provvisorio sopravvive al ricaricamento dell'attività. | Osservata perdita del testo non salvato. Dopo il reinserimento e la conferma il flusso ha funzionato. Conservazione automatica del testo provvisorio ancora da implementare e collaudare. |
| T05 · Diagnosi autenticazione SMTP | Nella finestra worker configurare mittente e credenziale locale. Eseguire una prova di connessione e login su 465 con TLS implicito e su 587 con STARTTLS. Registrare solo la fase e l'esito. | Connessione protetta e autenticazione riuscite. | Prima prova interrotta durante il login su entrambe le porte. Dopo l'inserimento della nuova password per le app Google, autenticazione riuscita su entrambe. La causa iniziale non è stata determinata oltre questa evidenza. |
| T06 · Nuovo invio dopo esito incerto | Lasciare l'email con esito incerto come evidenza storica. Dopo la verifica delle credenziali, creare un nuovo follow-up e programmare un nuovo messaggio con oggetto distinto. | La nuova pianificazione viene salvata. Il precedente invio incerto resta riconoscibile. | Superato. Il precedente prova invio mail restava con Esito da verificare. |
| T07 · Consegna SMTP reale | Avviare il worker nella stessa finestra in cui sono configurate le credenziali corrette. Pianificare oggi un nuovo messaggio almeno 5 minuti nel futuro, entro le 19:59. Lasciare il PC e il worker attivi. Dopo l'orario ricaricare e controllare Gmail. | Email Inviata e messaggio ricevuto nella casella di prova. | Superato. riproviamo invio programmata alle 18:55 del 20 novembre. La schermata mostra Inviata alle 18:55:04. Ricezione confermata dall'utente. |
| T08 · Saldo prima dell'invio | Scegliere una fattura demo con residuo positivo e creare un follow-up collegato. Programmare almeno 10 minuti nel futuro, dentro la finestra consentita. Registrare un incasso pari all'intero residuo prima dell'orario. Aprire Attività, verificare Sospesa · fattura saldata, poi premere Annulla sollecito. Controllare l'assenza del messaggio dopo l'orario previsto. | Sospensione, richiesta di annullamento, stato Annullata e mancato invio. | L'utente ha confermato che il test guidato funziona. Numero fattura, residuo e orari della prova non sono stati registrati. |
| T09 · Pagamento parziale | Programmare su fattura aperta, poi registrare una quota inferiore al residuo. Attendere il controllo del worker. | Da rivedere. Prima di riprogrammare, verificare e aggiornare il testo con il residuo corrente. | Da eseguire manualmente. Copertura automatica con trasporto simulato già disponibile. |
| T10 · Limiti orari e giorno | Provare un orario futuro alle 08:59, alle 20:00 e una data diversa da quella del follow-up. | Rifiuto della pianificazione con spiegazione. | Da eseguire manualmente. Finestra implementata 09:00 inclusa–20:00 esclusa, Europe/Rome. |
| T11 · Arresto e ripartenza worker | Pianificare un'email, fermare il worker e riavviarlo dopo l'orario nello stesso giorno dentro la finestra. Ripetere separatamente con ripartenza fuori finestra. | Dentro finestra il worker elabora la coda. Fuori finestra richiede revisione. Un invio già concluso non riparte. | Da eseguire manualmente. |
| T12 · Completamento del follow-up | Dopo Email Inviata, osservare il follow-up Aperto e premere Completa. Ricaricare. | Email Inviata e attività Completata rappresentano i due esiti separati. | Stato Aperto dopo invio osservato. Completamento manuale già collaudato nel modulo attività, da rilevare nuovamente su questo messaggio se necessario. |

### Procedura di chiusura della sessione

1. Controllare gli invii ancora Programmati. Per sospendere definitivamente una prova usare Annulla invio. L'arresto del worker conserva la coda.
2. Nella finestra di follow_up_email.py premere Ctrl+C e attendere Worker fermato e il ritorno del prompt PowerShell. Se un invio è in corso, attendere l'esito prima di arrestare il processo.
3. Nella finestra Uvicorn premere Ctrl+C e attendere la chiusura del server.
4. Chiudere le finestre PowerShell. Le credenziali impostate con $env: in quelle sessioni terminano con il processo.
5. Per il prossimo collaudo riavviare app e worker con la configurazione prevista. Il worker può elaborare una pianificazione già scaduta se è ancora nel giorno e nella finestra consentiti.

A fine sessione risulta ancora visibile una prova programmata per il 21 novembre alle 09:00. Se non si vuole eseguirla alla prossima accensione del worker, annullarla nell'app prima della chiusura.
