from datetime import date
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from fastapi import HTTPException
from playwright.sync_api import sync_playwright,expect

from assistant_service import QueryPlan
from browser_server import serve


class AssistantBrowserTests(unittest.TestCase):
    def setUp(self):
        folder=TemporaryDirectory();self.addCleanup(folder.cleanup)
        server=serve(Path(folder.name)/'chat.sqlite3');self.url=server.__enter__();self.addCleanup(server.__exit__,None,None,None)
        runtime=sync_playwright();p=runtime.__enter__();self.addCleanup(runtime.__exit__,None,None,None)
        browser=p.chromium.launch();self.addCleanup(browser.close)
        self.page=browser.new_page(viewport={'width':1440,'height':1000});self.page.set_default_timeout(8000)
        self.errors=[];self.page.on('pageerror',lambda e:self.errors.append(str(e)))
        self.page.goto(self.url+'#assistant')

    def tearDown(self):
        self.assertEqual(self.errors,[])

    def send(self,question):
        self.page.get_by_label('Domanda sui dati',exact=True).fill(question)
        self.page.get_by_role('button',name='Interroga HOLO',exact=True).click()
        expect(self.page.get_by_role('button',name='Interroga HOLO',exact=True)).to_be_enabled()
        return self.page.locator('.assistant-result').last

    def test_ambiguity_context_payment_and_safe_navigation(self):
        with patch('assistant_service.local_structured_response',return_value=QueryPlan(operation='list_invoices',client_query='Rossi')):
            panel=self.send('Fatture di Rossi')
        expect(panel.get_by_role('button',name='Seleziona Studio Rossi',exact=True)).to_be_visible()
        panel.get_by_role('button',name='Seleziona Studio Rossi',exact=True).click()
        expect(self.page.locator('.assistant-result').last.get_by_role('table',name='Risultato della domanda')).to_contain_text('F-001')
        expect(self.page.locator('#assistant-context')).to_contain_text('Studio Rossi')
        with patch('assistant_service.local_structured_response',return_value=QueryPlan(operation='client_balance')):
            panel=self.send('E il suo residuo?')
        expect(panel.get_by_role('table',name='Risultato della domanda')).to_contain_text('950,00')
        payment={'request_id':'5b5aec35-bfa1-4d99-a73b-e721befc41e8','amount':'100'}
        self.assertEqual(self.page.request.post(self.url+'api/invoices/F-001/demo-payments',data=payment).status,201)
        with patch('assistant_service.local_structured_response',return_value=QueryPlan(operation='client_balance')):
            panel=self.send('E adesso il residuo?')
        expect(panel.get_by_role('table',name='Risultato della domanda')).to_contain_text('850,00')
        panel.get_by_role('button',name='Apri scheda cliente',exact=True).click()
        expect(self.page.locator('#client-name')).to_have_text('Studio Rossi')
        self.page.get_by_role('link',name='Assistente',exact=True).click()
        self.page.get_by_role('button',name='Nuova conversazione',exact=True).click()
        expect(self.page.locator('.assistant-result')).to_have_count(0)
        expect(self.page.locator('#assistant-context')).to_have_text('Contesto: tutti i clienti')

    def test_errors_unsupported_and_mobile_tables_are_safe(self):
        panel=self.send('Cancella la fattura F-001')
        expect(panel.get_by_role('table',name='Risultato della domanda')).to_contain_text('Non modifica dati')
        with patch('assistant_service.local_structured_response',side_effect=HTTPException(503,'Ollama non disponibile')):
            panel=self.send('Quanto resta da incassare?')
        expect(panel.get_by_role('table',name='Errore della domanda')).to_contain_text('Ollama non disponibile')
        self.page.set_viewport_size({'width':390,'height':844})
        with patch('assistant_service.local_structured_response',return_value=QueryPlan(operation='list_invoices',client_query='Studio Rossi')):
            panel=self.send('Fatture di Studio Rossi')
        expect(panel.get_by_role('table',name='Risultato della domanda')).to_contain_text('F-001')
        self.assertLessEqual(self.page.evaluate('document.documentElement.scrollWidth'),392)
        self.assertEqual(self.page.locator('#assistant-results script').count(),0)

    def test_quotes_followups_examples_and_trace_table(self):
        activity=self.page.request.post(self.url+'api/clients/studio-rossi/follow-ups',data={'title':'Attività <script>finta</script>','due_date':date.today().isoformat()})
        self.assertEqual(activity.status,201)
        with patch('assistant_service.local_structured_response',return_value=QueryPlan(operation='list_followups',client_query='Studio Rossi',activity_status='open')):
            panel=self.send('Attività aperte di Studio Rossi')
        expect(panel.get_by_role('table',name='Risultato della domanda')).to_contain_text('<script>finta</script>')
        expect(panel.get_by_role('table',name='Tracciabilità della risposta')).to_contain_text('list_followups')
        self.assertEqual(panel.locator('script').count(),0)
        Path('ux-screenshots').mkdir(exist_ok=True)
        self.page.screenshot(path='ux-screenshots/assistente.png',full_page=True)
        self.page.get_by_role('button',name='Prossime scadenze',exact=True).click()
        expect(self.page.get_by_label('Domanda sui dati',exact=True)).to_have_value('Quali fatture scadono nei prossimi sette giorni per tutti i clienti?')
        panel.get_by_role('button',name='Apri Attività <script>finta</script>',exact=True).click()
        expect(self.page.locator('#follow-up-list')).to_contain_text('Attività <script>finta</script>')
