from contextlib import closing
from datetime import date,timedelta
from pathlib import Path
import sqlite3
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch
from uuid import uuid4

from fastapi import HTTPException
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app import create_app
from assistant_service import Conversations, QueryPlan, scope_clients


class AssistantTests(unittest.TestCase):
    def setUp(self):
        self.folder=TemporaryDirectory();self.addCleanup(self.folder.cleanup)
        self.database=Path(self.folder.name)/'assistant.sqlite3'
        self.app=create_app(self.database)
        self.api=TestClient(self.app);self.api.__enter__();self.addCleanup(self.api.__exit__,None,None,None)

    def ask(self, question, operation='client_balance', conversation=None, **plan):
        with patch('assistant_service.local_structured_response',return_value=QueryPlan(operation=operation,**plan)):
            return self.api.post('/api/assistant/query',json={'question':question,**({'conversation_id':conversation} if conversation else {})})

    def test_balance_invoice_precedence_and_fresh_payment(self):
        result=self.ask('Quanto resta da Studio Rossi?',client_query='Studio Rossi').json()
        self.assertEqual(result['rows'][0][3],'950,00 €')
        cid=result['conversation_id']
        detail=self.ask('E sulla fattura F-001?',conversation=cid).json()
        self.assertEqual(detail['operation'],'invoice_detail')
        self.assertEqual(detail['rows'][0][-1],'500,00 €')
        payment={'request_id':str(uuid4()),'amount':'100.00'}
        self.assertEqual(self.api.post('/api/invoices/F-001/demo-payments',json=payment).status_code,201)
        again=self.ask('E il totale del cliente?',conversation=cid).json()
        self.assertEqual(again['rows'][0][3],'850,00 €')
        self.assertIsNotNone(again['read_at']);self.assertNotEqual(again['request_id'],result['request_id'])
        self.assertEqual(self.ask('Dettaglio F-001 e F-003','invoice_detail').status_code,422)

    def test_ambiguity_selection_and_forged_selection(self):
        result=self.ask('Fatture di Rossi','list_invoices',client_query='Rossi').json()
        self.assertEqual(result['status'],'clarification');self.assertEqual(len(result['choices']),2)
        selected=self.api.post('/api/assistant/query',json={'question':'Fatture di Rossi','conversation_id':result['conversation_id'],'selected_client_id':'martina-rossi'})
        self.assertEqual(selected.status_code,200)
        self.assertEqual([r[0] for r in selected.json()['rows']],['F-003'])
        forged=self.api.post('/api/assistant/query',json={'question':'Fatture di Rossi','conversation_id':result['conversation_id'],'selected_client_id':'studio-bianchi'})
        self.assertEqual(forged.status_code,422)

    def test_client_context_followups_and_global_reset(self):
        activity=self.api.post('/api/clients/studio-rossi/follow-ups',json={'title':'Verifica oggi','due_date':date.today().isoformat()}).json()
        first=self.ask('Situazione Studio Rossi',client_query='Studio Rossi').json()
        result=self.ask('E le sue attività aperte?','list_followups',conversation=first['conversation_id'],activity_status='open').json()
        self.assertEqual(result['rows'][0][0],'Verifica oggi')
        self.assertEqual(result['links'][0]['activity_id'],activity['id'])
        global_result=self.ask('Quanto resta per tutti i clienti?',conversation=first['conversation_id']).json()
        self.assertIsNone(global_result['context']['client'])
        self.assertEqual(global_result['rows'][0][0],'TOTALE GENERALE')
        self.assertEqual(global_result['rows'][0][3],'1.550,00 €')

    def test_explicit_invoice_changes_owner_but_named_client_is_enforced(self):
        initial=self.ask('Situazione Studio Rossi',client_query='Studio Rossi').json()
        result=self.ask('Dettaglio fattura F-003',conversation=initial['conversation_id']).json()
        self.assertEqual(result['context']['client'],'Martina Rossi')
        bad=self.ask('Fattura F-003 di Studio Rossi',client_query='Studio Rossi').json()
        self.assertEqual(bad['status'],'empty')
        self.assertNotIn('250,00 €',str(bad['rows']))

    def test_missing_client_and_model_invented_reference(self):
        result=self.ask('Residuo di Pluto',client_query='Pluto').json()
        self.assertEqual(result['status'],'empty')
        self.assertEqual(self.ask('Residuo di Rossi',client_query='Studio Bianchi').status_code,502)
        self.assertEqual(self.ask('Quale fattura?','invoice_detail',invoice_number='F-001').status_code,502)

    def test_catalogue_read_operations_match_current_data(self):
        client=self.ask('Cerca Studio Bianchi','search_clients',client_query='Studio Bianchi').json()
        self.assertEqual(client['rows'][0][0],'Studio Bianchi')
        quote=self.api.post('/api/previews',json={'client_id':'studio-rossi','subject':'Proposta <script>test</script>','amount':'80','discount':'10'}).json()
        self.api.put('/api/drafts/'+quote['id'])
        drafts=self.ask('Bozze per Studio Rossi','list_quotes',client_query='Studio Rossi').json()
        self.assertEqual(drafts['rows'][0][-1],'72,00 €')
        portfolio=self.ask('Classifica clienti per criticità','portfolio_analysis',sort='risk').json()
        self.assertEqual(portfolio['rows'][0][1],'Studio Rossi')
        api=self.api.get('/api/customer-analysis?sort=risk').json()['customers']
        self.assertEqual(portfolio['rows'][0][3],api[0]['risk_score'])

    def test_relative_dates_empty_results_and_invalid_period(self):
        result=self.ask('Fatture nei prossimi sette giorni per tutti i clienti','list_invoices',period='next7').json()
        self.assertEqual([r[0] for r in result['rows']],['F-003'])
        self.assertEqual(result['filters']['date_to'],(date.today()+timedelta(days=7)).isoformat())
        empty=self.ask('Fatture domani','list_invoices',period='tomorrow').json()
        self.assertEqual(empty['status'],'empty');self.assertEqual(empty['rows'],[])
        self.assertEqual(self.ask('Fatture nel periodo','list_invoices',date_from=date(2030,2,1),date_to=date(2030,1,1)).status_code,422)
        self.assertEqual(self.ask('Bozze di oggi','list_quotes',period='today').status_code,422)
        self.assertEqual(self.ask('Classifica oggi','portfolio_analysis',period='today').status_code,422)

    def test_write_requests_are_blocked_before_model_and_database_unchanged(self):
        before=self.api.get('/api/invoices').json()
        for question in ['Cancella F-001','Registra un incasso di 100 euro','DROP TABLE clients','Invia email a Rossi','Crea un follow-up']:
            with patch('assistant_service.local_structured_response') as model:
                response=self.api.post('/api/assistant/query',json={'question':question})
                self.assertEqual(response.json()['status'],'unsupported');model.assert_not_called()
        self.assertEqual(before,self.api.get('/api/invoices').json())

    def test_database_read_only_transaction_is_enforced(self):
        def malicious(db,*args):
            db.execute("INSERT INTO clients (id,name,email,phone) VALUES ('forbidden','Forbidden','','')")
        with patch('assistant_service.local_structured_response',return_value=QueryPlan(operation='search_clients')),patch('app.assistant_answer',side_effect=malicious):
            response=self.api.post('/api/assistant/query',json={'question':'Elenca clienti'})
        self.assertEqual(response.status_code,503)
        self.assertEqual(self.api.get('/api/clients?q=Forbidden').json(),[])

    def test_model_outage_invalid_body_and_no_fake_answer(self):
        with patch('assistant_service.local_structured_response',side_effect=HTTPException(503,'Ollama non disponibile')):
            response=self.api.post('/api/assistant/query',json={'question':'Residuo totale'})
        self.assertEqual(response.status_code,503);self.assertNotIn('rows',response.json())
        for body in [{'question':'   '},{'question':'a'*601},{'question':'Elenca','sql':'SELECT * FROM clients'}]:
            self.assertEqual(self.api.post('/api/assistant/query',json=body).status_code,422)
        with self.assertRaises(ValidationError):QueryPlan(operation='execute_sql')

    def test_log_contains_trace_without_raw_question(self):
        question='Saldo Studio Rossi dato-riservato-987'
        with self.assertLogs('holo.assistant',level='INFO') as logs:
            result=self.ask(question,client_query='Studio Rossi').json()
        self.assertIn(result['request_id'],logs.output[0]);self.assertNotIn(question,logs.output[0])
        self.assertIn('question_hash=',logs.output[0])

    def test_large_result_is_limited_and_declares_total(self):
        for n in range(55):self.api.post('/api/clients',json={'name':f'Cliente prova {n:03}'})
        result=self.ask('Elenca tutti i clienti','search_clients').json()
        self.assertEqual(len(result['rows']),50);self.assertEqual(result['total_rows'],58);self.assertTrue(result['truncated'])

    def test_domain_words_are_not_implicit_demo_clients(self):
        clients=[{'id':'today','name':'DEMO | Scadenza oggi'},{'id':'future','name':'DEMO | Scadenze future'}]
        cid,choices=scope_clients(clients,'Quali fatture in scadenza oggi?',QueryPlan(operation='list_invoices'),{})
        self.assertIsNone(cid);self.assertEqual(choices,[])
        cid,_=scope_clients(clients,'Fatture del cliente Scadenza oggi',QueryPlan(operation='list_invoices'),{})
        self.assertEqual(cid,'today')


class ConversationTests(unittest.TestCase):
    def test_expiry_limit_and_revision_protect_context(self):
        sessions=Conversations(ttl=10,limit=1)
        key,state=sessions.get(None)
        with self.assertRaises(HTTPException):sessions.get(None)
        sessions.put(key,state,{'client_id':'first'})
        with self.assertRaises(HTTPException):sessions.put(key,state,{'client_id':'other'})
        self.assertEqual(sessions.get(key)[1]['context']['client_id'],'first')
        sessions.items[key]['touched']-=11
        with self.assertRaises(HTTPException):sessions.get(key)
