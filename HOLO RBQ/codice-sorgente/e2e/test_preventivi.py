import re
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from playwright.sync_api import expect, sync_playwright

from browser_server import serve


class PreventiviBrowserTest(unittest.TestCase):
    def test_creazione_modifica_e_persistenza(self):
        with TemporaryDirectory() as folder, sync_playwright() as playwright:
            database = Path(folder) / "holo-e2e.sqlite3"
            browser = playwright.chromium.launch()
            try:
                with serve(database) as url:
                    page = browser.new_page()
                    page.goto(url)
                    page.get_by_role("button", name="Usa una richiesta di esempio").click()
                    page.locator("#chat").get_by_role("button", name="Invia").click()
                    expect(page.locator("#messages")).to_contain_text(
                        re.compile(r"Studio Rossi e Martina Rossi|Martina Rossi e Studio Rossi")
                    )
                    page.locator("#quote").get_by_label("Cliente").select_option("studio-rossi")
                    page.get_by_role("button", name="Mostra anteprima").click()
                    expect(page.locator("#preview")).to_contain_text("720,00")
                    page.get_by_role("button", name="Conferma e salva bozza").click()
                    archive = page.locator("#drafts")
                    expect(archive.get_by_role("listitem")).to_have_count(1)
                    row = archive.get_by_role("listitem")
                    expect(row).to_contain_text("720,00")
                    draft_id = re.search(r"DEMO-\d+", row.inner_text()).group()

                    page.locator("#query").fill("Studio Rossi")
                    page.locator("#search").get_by_role("button", name="Cerca").click()
                    archive.get_by_role("button", name=f"Apri {draft_id}").click()
                    expect(page.locator("#quote-heading")).to_contain_text(draft_id)
                    page.get_by_label("Sconto (%)").fill("20")
                    page.get_by_role("button", name="Mostra anteprima").click()
                    expect(page.locator("#preview")).to_contain_text("640,00")
                    page.get_by_role("button", name="Conferma e salva bozza").click()
                    expect(row).to_contain_text("640,00")
                    expect(row).to_contain_text(draft_id)
                    page.close()

                with serve(database) as url:
                    page = browser.new_page()
                    page.goto(url)
                    rows = page.locator("#drafts").get_by_role("listitem")
                    expect(rows).to_have_count(1)
                    expect(rows).to_contain_text(draft_id)
                    expect(rows).to_contain_text("640,00")
            finally:
                browser.close()

    def test_annullamento_anteprima_senza_bozza(self):
        with TemporaryDirectory() as folder, sync_playwright() as playwright:
            database = Path(folder) / "holo-e2e.sqlite3"
            with serve(database) as url:
                browser = playwright.chromium.launch()
                try:
                    page = browser.new_page()
                    page.goto(url)
                    quote = page.locator("#quote")
                    quote.get_by_label("Cliente").select_option("studio-rossi")
                    quote.get_by_label("Oggetto").fill("Consulenza da annullare")
                    quote.get_by_label("Importo").fill("800")
                    page.get_by_role("button", name="Mostra anteprima").click()
                    preview = page.locator("#preview")
                    save = page.get_by_role("button", name="Conferma e salva bozza")
                    expect(preview).to_be_visible()
                    expect(save).to_be_enabled()

                    with page.expect_response(
                        lambda response: response.request.method == "DELETE"
                        and "/api/previews/" in response.url
                    ) as cancelled:
                        page.get_by_role("button", name="Annulla anteprima").click()
                    self.assertEqual(cancelled.value.status, 204)
                    preview_id = cancelled.value.url.rsplit('/', 1)[-1]
                    retry = page.request.put(f'{url}api/drafts/{preview_id}')
                    self.assertEqual(retry.status, 404)
                    expect(page.locator("#status")).to_have_text("Anteprima annullata.")
                    expect(preview).to_be_hidden()
                    expect(save).to_be_disabled()

                    with page.expect_response(
                        lambda response: response.request.method == "GET"
                        and "/api/drafts?" in response.url
                    ) as archive:
                        page.reload()
                    self.assertEqual(archive.value.json(), [])
                    expect(page.locator("#empty")).to_be_visible()
                    expect(page.locator("#drafts").get_by_role("listitem")).to_have_count(0)
                finally:
                    browser.close()
