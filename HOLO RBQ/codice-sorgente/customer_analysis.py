from datetime import date
from decimal import Decimal, ROUND_HALF_UP
import json
from typing import Literal

from customer_assistant import local_structured_response
from pydantic import BaseModel
from fastapi import HTTPException


ACTION_TEXT = {
    "review_payment": "Verifica internamente la fattura scaduta e le registrazioni di incasso.",
    "discuss_plan": "Prepara un piano di rientro da valutare prima del prossimo contatto.",
    "retain": "Prepara una proposta di continuità del rapporto, basata sui servizi già richiesti.",
    "explore": "Rivedi le bozze e individua un servizio da proporre al prossimo confronto.",
    "collect": "Completa lo storico prima di formulare una valutazione commerciale.",
}


class LocalAdvice(BaseModel):
    action: Literal["review_payment", "discuss_plan", "retain", "explore", "collect"]


def rounded_score(value):
    return int(Decimal(value).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def analyse_customers(db, today=None):
    today = today or date.today()
    clients = [dict(row) for row in db.execute("SELECT id, name FROM clients ORDER BY name, id")]
    invoices = db.execute("SELECT * FROM invoices ORDER BY due_date, number").fetchall()
    draft_counts = {
        row["client_id"]: row["count"]
        for row in db.execute("SELECT client_id, COUNT(*) AS count FROM drafts GROUP BY client_id")
    }
    # Group by immutable identifier to keep customers with similar names separate.
    grouped = {client["id"]: [] for client in clients}
    for row in invoices:
        if row["client_id"] in grouped:
            grouped[row["client_id"]].append(row)

    results = []
    for client in clients:
        rows = grouped[client["id"]]
        opened = [row for row in rows if row["amount"] > row["paid"]]
        overdue = [row for row in opened if row["due_date"] < today.isoformat()]
        total = sum(row["amount"] for row in rows)
        paid = sum(row["paid"] for row in rows)
        remaining = total - paid
        overdue_total = sum(row["amount"] - row["paid"] for row in overdue)
        oldest_days = max(
            ((today - date.fromisoformat(row["due_date"])).days for row in overdue), default=0
        )
        overdue_ratio = Decimal(overdue_total) / remaining if remaining else Decimal(0)
        risk = rounded_score(70 * overdue_ratio + 30 * min(Decimal(oldest_days) / 60, 1)) if total else None
        evidence = "Storico limitato" if rows else "Nessuna fattura"
        if len(rows) >= 3:
            evidence = "Almeno 3 fatture"
        priority = (overdue or opened)
        results.append({
            **client, "invoice_count": len(rows), "draft_count": draft_counts.get(client["id"], 0),
            "invoiced": total, "paid": paid, "remaining": remaining,
            "overdue_remaining": overdue_total, "oldest_overdue_days": oldest_days,
            "paid_ratio": float(Decimal(paid) / total) if total else None,
            "risk_score": risk, "evidence": evidence,
            "priority_invoice": priority[0]["number"] if priority else None,
        })

    max_paid = max((item["paid"] for item in results), default=0)
    max_count = max((item["invoice_count"] for item in results), default=0)
    for item in results:
        paid_part = Decimal(item["paid"]) / max_paid if max_paid else Decimal(0)
        count_part = Decimal(item["invoice_count"]) / max_count if max_count else Decimal(0)
        item["value_score"] = rounded_score(70 * paid_part + 30 * count_part) if item["invoiced"] else None
        item["criticality"] = "Scaduto presente" if item["overdue_remaining"] else (
            "Nessuno scaduto aperto" if item["invoiced"] else "Dati insufficienti"
        )
        if not item["invoiced"]:
            action = "collect"
        elif item["overdue_remaining"]:
            action = "discuss_plan" if item["oldest_overdue_days"] >= 30 else "review_payment"
        elif item["value_score"] >= 60:
            action = "retain"
        else:
            action = "explore"
        item["suggested_action"] = ACTION_TEXT[action]
        item["allowed_actions"] = (
            ["collect"] if not item["invoiced"]
            else ["review_payment", "discuss_plan"] if item["overdue_remaining"]
            else ["retain", "explore"]
        )
    return results


def local_customer_advice(item):
    if item["allowed_actions"] == ["collect"]:
        return {"action": ACTION_TEXT["collect"], "source": "Regole locali · storico insufficiente"}
    # The model sees aggregate facts only. It chooses a bounded action rather than generating amounts.
    facts = {key: item[key] for key in (
        "invoice_count", "paid", "remaining", "overdue_remaining",
        "oldest_overdue_days", "value_score", "risk_score", "allowed_actions"
    )}
    advice = local_structured_response(LocalAdvice, [
        {"role": "system", "content": (
            "Seleziona una sola azione di gestione cliente tra allowed_actions. "
            "review_payment=verifica interna dei pagamenti, discuss_plan=preparazione piano di rientro, "
            "retain=continuità del rapporto, explore=approfondimento opportunità. "
            "Usa solo i dati forniti. Gli importi sono centesimi. Restituisci JSON."
        )},
        {"role": "user", "content": json.dumps(facts)},
    ])
    if advice.action not in item["allowed_actions"]:
        raise HTTPException(502, "Il modello ha proposto un’azione incoerente con i dati. Riprova.")
    return {"action": ACTION_TEXT[advice.action], "source": "Ollama locale · proposta da valutare"}
