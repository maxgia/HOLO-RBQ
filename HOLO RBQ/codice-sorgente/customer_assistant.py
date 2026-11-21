import json
import os
import re
from typing import Literal
from urllib.error import URLError
from urllib.request import Request, build_opener, ProxyHandler

from fastapi import HTTPException
from pydantic import BaseModel, Field, ValidationError, field_validator


class CustomerQuestion(BaseModel):
    question: str = Field(min_length=1, max_length=400)

    @field_validator("question", mode="before")
    @classmethod
    def trim_question(cls, value):
        return value.strip() if isinstance(value, str) else value


class QuestionIntent(BaseModel):
    action: Literal["balance", "priority", "invoice", "reminder", "summary", "unsupported"]
    invoice_number: str | None
    tone: Literal["cordiale", "formale", "diretto"]


def classify_question(question: str) -> QuestionIntent:
    payload = {
        "messages": [
            {
                "role": "system",
                "content": (
                    "Classifica la domanda sulla scheda cliente attiva. "
                    "balance = totale residuo, priority = quale fattura gestire prima, "
                    "invoice = dettaglio di una fattura specifica, reminder = bozza di sollecito, "
                    "summary = riepilogo di bozze e fatture. "
                    "Per altre richieste, inclusi altri clienti o modifiche ai dati, usa unsupported. "
                    "Riporta il numero fattura solo se esplicitamente presente, altrimenti null. "
                    "Il tono predefinito è formale."
                ),
            },
            {"role": "user", "content": question},
        ],
    }
    return local_structured_response(QuestionIntent, payload["messages"])


def local_structured_response(schema, messages):
    payload = {
        "model": os.getenv("HOLO_OLLAMA_MODEL", "qwen2.5:3b"),
        "stream": False,
        "format": schema.model_json_schema(),
        "options": {"temperature": 0, "num_predict": 128},
        "messages": messages,
    }
    request = Request(
        "http://127.0.0.1:11434/api/chat",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    try:
        with build_opener(ProxyHandler({})).open(request, timeout=30) as response:
            content = json.load(response)["message"]["content"]
        return schema.model_validate_json(content)
    except (URLError, TimeoutError) as error:
        raise HTTPException(
            503, "Ollama non disponibile. Verifica che sia avviato e che il modello sia installato."
        ) from error
    except (ValueError, KeyError, TypeError, ValidationError) as error:
        raise HTTPException(502, "Ollama non ha restituito una risposta utilizzabile. Riprova.") from error


def euro(cents: int) -> str:
    return f"{cents // 100:,}".replace(",", ".") + f",{cents % 100:02d} €"


def answer_customer_question(client: dict, question: str) -> dict:
    invoices = client["invoices"]
    if not invoices and not client["drafts"]:
        return {"answer": "Nessuno storico disponibile per questa scheda cliente."}

    intent = classify_question(question)
    opened = [invoice for invoice in invoices if invoice["remaining"] > 0]
    overdue = [invoice for invoice in opened if invoice["status"] == "Scaduta"]
    total = euro(client["total_remaining"])
    if intent.action == "unsupported":
        return {"answer": "Posso consultare bozze, scadenze e incassi della scheda aperta."}
    # An explicit demo invoice reference takes precedence over the model's classification.
    references = set(re.findall(r"(?<![\w-])F-\d+(?![\w-])", question.upper()))
    if len(references) > 1:
        return {"answer": "Indica una sola fattura per domanda."}
    invoice_number = next(iter(references), intent.invoice_number)
    if intent.action == "balance" and not references:
        return {"answer": f"Il residuo complessivo è di {total}."}
    if intent.action == "summary" and not references:
        return {
            "answer": f"Bozze: {len(client['drafts'])}. Fatture aperte: {len(opened)}, "
            f"di cui scadute: {len(overdue)}. Residuo complessivo: {total}."
        }

    if invoice_number:
        number = invoice_number.strip().casefold()
        invoice = next((row for row in invoices if row["number"].casefold() == number), None)
        if invoice is None:
            return {"answer": "La fattura richiesta non è presente nella scheda cliente aperta."}
    elif intent.action == "invoice":
        return {"answer": "Indica il numero della fattura da consultare."}
    else:
        candidates = overdue or opened
        if not candidates:
            return {"answer": "Non ci sono fatture aperte per questa scheda cliente."}
        invoice = candidates[0]

    due = "/".join(reversed(invoice["due_date"].split("-")))
    amount = euro(invoice["remaining"])
    number = invoice["number"]
    if intent.action == "reminder":
        if invoice["status"] != "Scaduta":
            return {"answer": "Il sollecito è disponibile per le fatture scadute con residuo."}
        closing = {
            "cordiale": "Potreste farmi sapere quando prevedete di saldarla? Grazie per la disponibilità.",
            "formale": "Vi chiedo cortesemente di indicarmi la data prevista per il pagamento.",
            "diretto": "Vi chiedo di comunicarmi la data di pagamento. Grazie.",
        }[intent.tone]
        return {
            "answer": f"Ho preparato una bozza per la fattura {number}.",
            "draft": f"Buongiorno,\n\nla fattura {number}, scaduta il {due}, ha un residuo di {amount}. "
            f"{closing}\n\nCordiali saluti.",
        }
    return {"answer": f"Fattura {number}. Stato: {invoice['status']}. Scadenza: {due}. Residuo: {amount}."}
