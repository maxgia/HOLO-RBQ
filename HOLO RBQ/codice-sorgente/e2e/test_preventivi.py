import re
import socket
import unittest
from contextlib import contextmanager
from pathlib import Path
from tempfile import TemporaryDirectory
from threading import Thread
from time import monotonic, sleep

import uvicorn
from playwright.sync_api import expect, sync_playwright

from app import create_app


@contextmanager
def serve(database):
    app = create_app(database)
    server = uvicorn.Server(uvicorn.Config(app, log_level="warning"))
    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        address, port = listener.getsockname()
        worker = Thread(target=server.run, kwargs={"sockets": [listener]}, daemon=True)
        worker.start()
        try:
            deadline = monotonic() + 10
            while not server.started:
                if not worker.is_alive() or monotonic() >= deadline:
                    raise RuntimeError("Uvicorn non ha avviato il server di test.")
                sleep(0.02)
            yield f"http://{address}:{port}/"
        finally:
            server.should_exit = True
            worker.join(timeout=10)
            if worker.is_alive():
                raise RuntimeError("Uvicorn non ha arrestato il server di test.")


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
                    expect(page.locator("#messages")).to_contain_text("Studio Rossi e Martina Rossi")
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
