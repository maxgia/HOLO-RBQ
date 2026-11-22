import os
from pathlib import Path
import sys
import unittest

from playwright.sync_api import sync_playwright, expect
from browser_server import serve

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tests'))
from postgres_support import postgres_case
from migrate_to_postgres import migrate


@unittest.skipUnless(os.getenv('HOLO_TEST_DATABASE_URL'), 'Serve PostgreSQL reale')
class PostgresBrowserTests(unittest.TestCase):
    def test_migrated_data_payment_and_analysis_in_real_browser(self):
        with postgres_case() as (source, target):
            migrate(source, target)
            with serve(target) as url, sync_playwright() as browser_api:
                browser = browser_api.chromium.launch()
                try:
                    page = browser.new_page()
                    page.goto(url)
                    page.get_by_role('link', name='Analisi clienti', exact=True).click()
                    table = page.get_by_role('table', name='Confronto clienti')
                    expect(table).to_contain_text('Cliente migrazione Ω')
                    expect(table).to_contain_text('Non classificato')
                    page.get_by_role('link',name='Fatture e scadenze',exact=True).click()
                    form = page.locator('#demo-payment')
                    form.get_by_label('Fattura da incassare').select_option('F-001')
                    form.get_by_label('Importo incassato (€)').fill('400')
                    form.get_by_role('button', name='Registra incasso demo').click()
                    page.get_by_role('link',name='Analisi clienti',exact=True).click()
                    rossi = table.get_by_role('row').filter(has_text='Studio Rossi')
                    expect(rossi.get_by_role('cell').nth(6)).to_have_text('0,00 €')
                    page.reload()
                    expect(rossi).to_contain_text('450,00')
                finally:
                    browser.close()
