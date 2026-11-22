from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from playwright.sync_api import sync_playwright, expect
from browser_server import serve


class WorkspaceUXTests(unittest.TestCase):
    def setUp(self):
        folder=TemporaryDirectory();self.addCleanup(folder.cleanup)
        scope=serve(Path(folder.name)/'ux.sqlite3');self.url=scope.__enter__();self.addCleanup(scope.__exit__,None,None,None)
        runtime=sync_playwright();p=runtime.__enter__();self.addCleanup(runtime.__exit__,None,None,None)
        browser=p.chromium.launch();self.addCleanup(browser.close)
        self.page=browser.new_page(viewport={'width':1440,'height':1000});self.errors=[]
        self.page.on('pageerror',lambda e:self.errors.append(str(e)))
        self.page.set_default_timeout(8000)
        self.page.goto(self.url)

    def tearDown(self):
        self.assertEqual(self.errors,[])

    def test_home_navigation_client_tabs_and_small_screen(self):
        page=self.page
        expect(page.locator('[data-page]:visible')).to_have_count(1)
        expect(page.locator('#home')).to_be_visible()
        expect(page.get_by_role('table',name='Priorità e problemi clienti')).to_contain_text('F-001')
        expect(page.get_by_role('table',name='Indicatori sintetici')).to_contain_text('500,00')
        Path('ux-screenshots').mkdir(exist_ok=True)
        page.screenshot(path='ux-screenshots/home.png',full_page=True)
        page.get_by_role('button',name='Apri fattura',exact=True).first.click()
        expect(page.locator('#invoice-section')).to_be_visible()
        expect(page.locator('#home')).to_be_hidden()
        page.go_back()
        expect(page.locator('#home')).to_be_visible()
        page.get_by_label('Cerca un cliente',exact=True).fill('Studio Rossi')
        page.get_by_label('Cerca un cliente',exact=True).press('Enter')
        page.get_by_role('button',name='Studio Rossi',exact=True).click()
        expect(page.locator('[data-client-panel]:visible')).to_have_count(1)
        expect(page.get_by_role('table',name='Riepilogo cliente')).to_contain_text('Fatture aperte')
        page.get_by_role('tab',name='Analisi AI',exact=True).click()
        expect(page.get_by_role('table',name='Risultato dell’analisi cliente')).to_contain_text('950,00')
        page.screenshot(path='ux-screenshots/cliente.png',full_page=True)
        page.get_by_role('tab',name='Analisi AI',exact=True).press('ArrowLeft')
        expect(page.get_by_role('tab',name='Attività',exact=True)).to_have_attribute('aria-selected','true')
        page.set_viewport_size({'width':390,'height':844})
        page.get_by_role('link',name='Home',exact=True).click()
        page.screenshot(path='ux-screenshots/home-mobile.png',full_page=True)
        self.assertLessEqual(page.evaluate('document.documentElement.scrollWidth'),392)
        page.goto(self.url+'#non-esiste')
        expect(page.locator('#home')).to_be_visible()

    def test_calendar_create_follow_up_and_same_activity_in_list(self):
        page=self.page
        page.get_by_role('button',name='Pianifica follow-up',exact=True).click()
        form=page.locator('#global-follow-up')
        form.get_by_label('Cliente',exact=True).select_option('studio-rossi')
        form.get_by_label('Titolo',exact=True).fill('Richiamo calendario')
        form.get_by_label('Data follow-up',exact=True).fill('2032-02-29')
        form.get_by_role('button',name='Salva follow-up',exact=True).click()
        expect(page.locator('#follow-up-list')).to_contain_text('Richiamo calendario')
        page.get_by_role('tab',name='Calendario',exact=True).click()
        page.get_by_label('Data calendario',exact=True).fill('2032-02-29')
        page.get_by_label('Data calendario',exact=True).press('Tab')
        calendar=page.get_by_role('table',name='Calendario follow-up')
        expect(calendar).to_contain_text('Richiamo calendario')
        expect(calendar.get_by_role('cell')).to_have_count(42)
        Path('ux-screenshots').mkdir(exist_ok=True)
        page.screenshot(path='ux-screenshots/calendario.png',full_page=True)
        page.get_by_label('Vista calendario',exact=True).select_option('week')
        expect(calendar.get_by_role('cell')).to_have_count(7)
        page.get_by_label('Vista calendario',exact=True).select_option('day')
        expect(calendar.get_by_role('cell')).to_have_count(1)
        calendar.get_by_role('button',name='Richiamo calendario · Studio Rossi',exact=True).click()
        row=page.locator('#follow-up-list').get_by_role('listitem').filter(has_text='Richiamo calendario')
        expect(row).to_be_visible()
        records=page.request.get(self.url+'api/follow-ups').json()
        self.assertEqual(len(records),1);self.assertIsNone(records[0]['email_status'])
        row.get_by_role('button',name='Completa',exact=True).click()
        expect(row).to_contain_text('Completata')

    def test_report_filter_export_and_dashboard_failure(self):
        page=self.page
        c=page.request.post(self.url+'api/clients',data={'name':'=1+1'}).json()
        page.request.post(self.url+'api/clients/'+c['id']+'/follow-ups',data={'title':'Verifica report','due_date':'2032-02-29'})
        page.get_by_role('link',name='Report',exact=True).click()
        report=page.get_by_role('table',name='Report operativo')
        expect(report).to_contain_text('Verifica report')
        page.get_by_label('Cliente report',exact=True).select_option(c['id'])
        page.get_by_role('button',name='Aggiorna report',exact=True).click()
        expect(report.locator('tbody tr')).to_have_count(1)
        with page.expect_download() as info:page.get_by_role('button',name='Esporta CSV',exact=True).click()
        content=Path(info.value.path()).read_text(encoding='utf-8-sig')
        self.assertIn("'=1+1",content)
        page.get_by_label('Scadenze dal',exact=True).fill('2033-01-01')
        page.get_by_label('Scadenze al',exact=True).fill('2032-01-01')
        page.get_by_role('button',name='Aggiorna report',exact=True).click()
        expect(page.locator('#report-status')).to_contain_text('data iniziale')
        page.get_by_role('link',name='Home',exact=True).click()
        page.route('**/api/invoices?status=all',lambda route:route.fulfill(status=503,json={'detail':'Servizio di prova indisponibile'}))
        page.get_by_role('button',name='Aggiorna cruscotto',exact=True).click()
        expect(page.locator('#home-status')).to_contain_text('non disponibile')
        expect(page.locator('#home-priorities tr')).to_have_count(0)
        expect(page.locator('#metric-open')).to_have_text('—')
