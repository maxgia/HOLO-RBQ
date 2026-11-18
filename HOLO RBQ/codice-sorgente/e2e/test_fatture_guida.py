import re
import unittest
from pathlib import Path
from unittest.mock import patch
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
        expect(messages).to_contain_text(re.compile(r"3 fatture per «Rossi»\. Residuo complessivo 1[.\s]?200,00"))
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
        expect(messages).to_contain_text("Gli incassi reali si registrano nel gestionale.")
        expect(messages).to_contain_text("Fonte: Guida dimostrativa HOLO RBQ · v1 · Registrare un incasso")

        self.ask("Come invio la fattura allo SdI?")
        expect(messages).to_contain_text("La guida dimostrativa non copre questa domanda.")
        expect(messages.get_by_text("Fonte:", exact=False)).to_have_count(1)

    def test_riepilogo_e_navigazione_del_nuovo_layout(self):
        page = self.page
        nav = page.get_by_role("navigation", name="Navigazione principale")
        expect(page.locator("#metric-open")).to_have_text(re.compile(r"^1[.\s]?550,00\s*€$"))
        expect(page.locator("#metric-overdue")).to_have_text(re.compile(r"^500,00\s*€$"))
        expect(page.locator("#metric-drafts")).to_have_text("0")
        invoices = nav.get_by_role("link", name="Fatture e scadenze")
        invoices.click()
        expect(invoices).to_have_attribute("aria-current", "location")
        nav.get_by_role("button", name="Guida operativa").click()
        expect(page.get_by_role("log")).to_contain_text("Registrare un incasso")

    def test_registra_incasso_demo(self):
        page = self.page
        payment = page.locator("#demo-payment")
        payment.get_by_label("Fattura da incassare").select_option("F-001")
        payment.get_by_label("Importo incassato (€)").fill("100")
        payment.get_by_role("button", name="Registra incasso demo").click()
        expect(page.locator("#payment-status")).to_have_text("Incasso demo registrato.")
        expect(page.locator("#metric-overdue")).to_have_text(re.compile(r"^400,00\s*€$"))
        page.reload()
        invoice = page.locator("#invoice-rows").get_by_role("row").filter(has_text="F-001")
        expect(invoice.get_by_role("cell").nth(5)).to_have_text("400,00 €")

    def test_anagrafica_clienti_e_residuo(self):
        page = self.page
        page.get_by_role("link", name="Clienti", exact=True).click()
        directory = page.locator("#clienti")
        directory.get_by_label("Nome cliente").fill("Rossi")
        directory.get_by_role("button", name="Cerca clienti").click()
        results = directory.locator("#client-results").get_by_role("listitem")
        expect(results).to_have_count(2)
        directory.get_by_role("button", name="Studio Rossi", exact=True).click()
        expect(directory.locator("#client-remaining")).to_contain_text("950,00")
        expect(directory.locator("#client-invoices")).to_contain_text("F-001")
        expect(directory.locator("#client-invoices")).not_to_contain_text("F-003")
        directory.get_by_role("button", name="Martina Rossi", exact=True).click()
        expect(directory.locator("#client-remaining")).to_contain_text("250,00")
        expect(directory.locator("#client-invoices")).to_contain_text("F-003")
        expect(directory.locator("#client-invoices")).not_to_contain_text("F-001")

    def test_analisi_cliente_e_sollecito_dopo_incasso(self):
        page = self.page
        directory = page.locator("#clienti")
        directory.get_by_label("Nome cliente").fill("Rossi")
        directory.get_by_role("button", name="Cerca clienti").click()
        directory.get_by_role("button", name="Studio Rossi", exact=True).click()
        directory.get_by_text("Analizza cliente", exact=True).click()
        analysis = directory.locator("#client-analysis")
        table = analysis.get_by_role("table", name="Risultato dell’analisi cliente")
        expect(table.get_by_role("columnheader")).to_have_text(["Indicatore", "Valore"])
        expect(table.get_by_role("row").filter(has_text="Residuo complessivo")).to_contain_text("950,00")
        expect(table.get_by_role("row").filter(has_text="Fattura prioritaria")).to_contain_text("F-001")
        expect(table.get_by_role("row").filter(has_text="Fatture aperte").get_by_role("cell")).to_have_text("2")
        expect(table.get_by_role("row").filter(has_text="Fatture scadute").get_by_role("cell")).to_have_text("1")
        analysis.get_by_role("button", name="Prepara sollecito").click()
        draft = analysis.locator("#client-analysis-text")
        expect(draft).to_have_value(re.compile(r"F-001.*500,00", re.S))
        analysis.get_by_role("button", name="Apri fattura").click()
        expect(page.locator("#invoice-F-001")).to_be_focused()

        payment = page.locator("#demo-payment")
        payment.get_by_label("Fattura da incassare").select_option("F-001")
        payment.get_by_label("Importo incassato (€)").fill("100")
        payment.get_by_role("button", name="Registra incasso demo").click()
        expect(analysis.locator("#client-analysis-summary")).to_contain_text("850,00")
        expect(table.get_by_role("row").filter(has_text="Residuo della fattura")).to_contain_text("400,00")
        expect(draft).to_be_hidden()
        analysis.get_by_role("button", name="Prepara sollecito").click()
        expect(draft).to_have_value(re.compile(r"F-001.*400,00", re.S))

        directory.get_by_role("button", name="Martina Rossi", exact=True).click()
        directory.get_by_text("Analizza cliente", exact=True).click()
        expect(analysis.locator("#client-analysis-summary")).to_contain_text("250,00")
        expect(analysis.locator("#client-analysis-priority")).to_contain_text("F-003")
        expect(analysis.get_by_role("button", name="Prepara sollecito")).to_be_hidden()
        expect(draft).to_be_hidden()

    def test_inserimento_manuale_cliente(self):
        page = self.page
        page.get_by_role("link", name="Clienti", exact=True).click()
        directory = page.locator("#clienti")
        directory.get_by_text("Nuovo cliente", exact=True).click()
        directory.get_by_label("Nome o ragione sociale").fill("Studio Verdi")
        directory.get_by_label("Email (facoltativa)").fill("studio@example.com")
        directory.get_by_role("button", name="Salva cliente").click()
        expect(directory.locator("#client-name")).to_have_text("Studio Verdi")
        expect(directory.locator("#client-contact")).to_have_text("studio@example.com")
        directory.get_by_text("Analizza cliente", exact=True).click()
        expect(directory.locator("#client-analysis-empty")).to_be_visible()
        expect(directory.get_by_role("table", name="Risultato dell’analisi cliente")).to_be_hidden()
        expect(directory.get_by_role("button", name="Apri fattura")).to_be_hidden()
        expect(page.locator('#quote select[name="client"] option').filter(has_text="Studio Verdi")).to_have_count(1)

    def test_follow_up_da_fattura_e_completamento(self):
        page = self.page
        directory = page.locator("#clienti")
        directory.get_by_label("Nome cliente").fill("Studio Rossi")
        directory.get_by_role("button", name="Cerca clienti").click()
        directory.get_by_role("button", name="Studio Rossi", exact=True).click()
        directory.get_by_text("Analizza cliente", exact=True).click()
        directory.get_by_role("button", name="Pianifica follow-up").click()
        expect(directory.get_by_label("Documento collegato")).to_have_value("invoice:F-001")
        directory.get_by_label("Data follow-up").fill("2000-01-01")
        directory.get_by_role("button", name="Salva follow-up").click()
        expect(directory.locator("#client-follow-ups")).to_contain_text("F-001")
        page.reload()
        activity = page.locator("#attivita")
        activity.get_by_label("Stato attività").select_option("overdue")
        row = activity.get_by_role("listitem").filter(has_text="F-001")
        expect(row).to_contain_text("Studio Rossi")
        row.get_by_label("Nuova data").fill("2099-01-01")
        row.get_by_role("button", name="Riprogramma").click()
        expect(row).to_have_count(0)
        activity.get_by_label("Stato attività").select_option("upcoming")
        expect(row).to_contain_text("01/01/2099")
        directory.get_by_label("Nome cliente").fill("Studio Rossi")
        directory.get_by_role("button", name="Cerca clienti").click()
        directory.get_by_role("button", name="Studio Rossi", exact=True).click()
        directory.get_by_role("button", name="Completa", exact=True).click()
        expect(row).to_have_count(0)
        activity.get_by_label("Stato attività").select_option("completed")
        expect(row).to_contain_text("Completata")


    @patch.dict("os.environ", {"HOLO_TEST_RECIPIENT": "collaudo@example.com"})
    def test_pannello_email_si_apre_dopo_salvataggio(self):
        directory = self.page.locator("#clienti")
        directory.get_by_label("Nome cliente").fill("Studio Rossi")
        directory.get_by_role("button", name="Cerca clienti").click()
        directory.get_by_role("button", name="Studio Rossi", exact=True).click()
        directory.get_by_text("Nuovo follow-up", exact=True).click()
        directory.get_by_label("Titolo", exact=True).fill("Collaudo pannello email")
        directory.get_by_label("Data follow-up").fill("2099-01-01")
        directory.get_by_role("button", name="Salva follow-up").click()

        activity = directory.locator("#client-follow-ups").get_by_role("listitem")
        recipient = activity.get_by_label("Destinatario di prova")
        expect(recipient).to_be_visible()
        expect(recipient).to_have_value("collaudo@example.com")
        expect(activity.get_by_label("Oggetto")).to_have_value("Collaudo pannello email")
        activity.get_by_label("Testo", exact=True).fill("Messaggio di collaudo.")
        activity.get_by_role("button", name="Conferma invio programmato").click()
        expect(activity).to_contain_text("Programmata")
