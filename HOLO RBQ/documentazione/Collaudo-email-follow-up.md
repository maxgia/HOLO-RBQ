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
