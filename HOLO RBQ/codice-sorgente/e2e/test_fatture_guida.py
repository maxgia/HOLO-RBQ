import re
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from playwright.sync_api import expect, sync_playwright

from browser_server import serve


class FattureGuidaBrowserTest(unittest.TestCase):
    def setUp(self):
        folder = TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        manager = sync_playwright()
        playwright = manager.__enter__()
        self.addCleanup(manager.__exit__, None, None, None)
        browser = playwright.chromium.launch()
        self.addCleanup(browser.close)
        server = serve(Path(folder.name) / "holo-e2e.sqlite3")
        url = server.__enter__()
        self.addCleanup(server.__exit__, None, None, None)
        self.page = browser.new_page()
        self.page.goto(url)

    def ask(self, question):
        chat = self.page.locator("#chat")
        chat.get_by_label("Richiesta").fill(question)
        chat.get_by_role("button", name="Invia").click()

    def test_fatture_da_chat_e_filtri(self):
        page = self.page
        rows = page.locator("#invoice-rows").get_by_role("row")
        messages = page.get_by_role("log")
        self.ask("Cosa deve ancora pagare Rossi?")
        expect(messages).to_contain_text("3 fatture per «Rossi». Residuo complessivo 1.200,00")
        expect(rows).to_have_count(3)

        self.ask("Quanto resta da incassare da Studio Rossi?")
        expect(messages).to_contain_text("2 fatture per «Studio Rossi». Residuo complessivo 950,00")
        expect(rows).to_have_count(2)
        expect(rows.filter(has_text="F-003")).to_have_count(0)

        search = page.locator("#invoice-search")
        search.get_by_label("Stato").select_option("overdue")
        search.get_by_role("button", name="Cerca fatture").click()
        expect(rows).to_have_count(1)
        expect(rows.first.get_by_role("cell")).to_have_text([
            "F-001", "Studio Rossi", re.compile(r"\d{2}/\d{2}/\d{4}"),
            "800,00 €", "300,00 €", "500,00 €", "Scaduta",
        ])
        search.get_by_label("Stato").select_option("paid")
        search.get_by_role("button", name="Cerca fatture").click()
        expect(rows).to_have_count(1)
        expect(rows.first).to_contain_text("F-004")
        expect(rows.first).to_contain_text("Saldata")
        expect(page.locator("#invoice-summary")).to_have_text("Totale residuo: 0,00 €")

        search.get_by_label("Cliente o numero fattura").fill("Cliente assente")
        search.get_by_role("button", name="Cerca fatture").click()
        expect(page.locator("#invoice-summary")).to_have_text("Nessuna fattura corrispondente.")
        expect(page.locator("#invoice-table")).to_be_hidden()

    def test_guida_con_fonte_e_domanda_fuori_copertura(self):
        messages = self.page.get_by_role("log")
        self.ask("Come registro un incasso?")
        expect(messages).to_contain_text("In HOLO RBQ, apri Fatture e scadenze")
        expect(messages).to_contain_text("La registrazione si esegue nel gestionale.")
        expect(messages).to_contain_text("Fonte: Guida dimostrativa HOLO RBQ · v1 · Registrare un incasso")

        self.ask("Come invio la fattura allo SdI?")
        expect(messages).to_contain_text("La guida dimostrativa non copre questa domanda.")
        expect(messages.get_by_text("Fonte:", exact=False)).to_have_count(1)
