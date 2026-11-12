import re
from unicodedata import combining, normalize

GUIDE = {
    "incasso": {
        "title": "Registrare un incasso",
        "keywords": ("incasso", "incassi", "pagamento", "pagamenti"),
        "steps": [
            "In HOLO RBQ, apri Fatture e scadenze e cerca il numero della fattura.",
            "Controlla cliente, importo già incassato e residuo.",
            "Nel gestionale che emette la fattura, apri il documento e usa la funzione di registrazione dell’incasso. Indica l’importo effettivamente ricevuto e la data del pagamento.",
            "Verifica nel gestionale che il residuo sia aggiornato. Se l’incasso è parziale, controlla che resti visibile l’importo ancora dovuto.",
        ],
        "scope": "In HOLO RBQ le fatture dimostrative sono consultabili in sola lettura. La registrazione si esegue nel gestionale. I nomi dei menu dipendono dal prodotto.",
    },
    "preventivo": {
        "title": "Creare un preventivo in bozza",
        "keywords": ("preventivo", "preventivi", "bozza", "bozze"),
        "steps": [
            "Nel modulo Nuovo preventivo, scegli il cliente.",
            "Inserisci l’oggetto, l’importo e l’eventuale sconto.",
            "Seleziona Mostra anteprima e controlla il totale.",
            "Seleziona Conferma e salva bozza. La ritrovi in Bozze salvate.",
        ],
        "scope": "Procedura disponibile nella demo locale HOLO RBQ.",
    },
    "modifica-bozza": {
        "title": "Modificare una bozza",
        "keywords": ("preventivo", "preventivi", "bozza", "bozze"),
        "steps": [
            "In Bozze salvate cerca per cliente, oggetto o codice.",
            "Apri la bozza e modifica i campi interessati.",
            "Controlla l’anteprima e conferma. La bozza mantiene il suo codice.",
        ],
        "scope": "Procedura disponibile nella demo locale HOLO RBQ.",
    },
    "scadenze": {
        "title": "Consultare le fatture in scadenza o da incassare",
        "keywords": ("fattura", "fatture", "scadenza", "scadenze", "residuo"),
        "steps": [
            "Apri Fatture e scadenze.",
            "Cerca per cliente o numero di fattura.",
            "Scegli Da incassare per vedere tutte le fatture con residuo oppure Scadute per quelle oltre la scadenza.",
            "Controlla per ciascuna fattura la scadenza, l’incassato e il residuo.",
        ],
        "scope": "La sezione mostra fatture dimostrative in sola lettura.",
    },
}


def find_articles(question: str) -> list[dict]:
    plain = "".join(char for char in normalize("NFKD", question.casefold()) if not combining(char))
    words = set(re.findall(r"[a-z]+", plain))
    matches = set()

    if words & {"registrare", "registro", "registra", "inserire", "inserisco", "contabilizzare"}:
        if words.intersection(GUIDE["incasso"]["keywords"]):
            matches.add("incasso")
    if words.intersection(GUIDE["preventivo"]["keywords"]):
        if words & {"creare", "creo", "preparo", "preparare", "salvare", "salvo"}:
            matches.add("preventivo")
        if words & {"modificare", "modifico", "aggiornare", "aggiorno", "correggere"}:
            matches.add("modifica-bozza")
    if words.intersection(GUIDE["scadenze"]["keywords"]):
        if words & {"consultare", "consulto", "vedo", "vedere", "cercare", "cerco", "controllare", "controllo", "trovo", "trovare", "visualizzare", "visualizzo"}:
            matches.add("scadenze")

    return [
        {"id": key, "title": article["title"], "steps": article["steps"], "scope": article["scope"]}
        for key, article in GUIDE.items() if key in matches
    ]
