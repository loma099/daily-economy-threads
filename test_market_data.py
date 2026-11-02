import unittest
from unittest.mock import Mock,patch
from datetime import datetime,timezone,timedelta
from briefing import official_market_sources,available_model,generate,quarantine_unsupported,attach_official_tables,TOPICS


class DataChecks(unittest.TestCase):
    def test_official_yield_table_keeps_value_date_and_bp_unit(self):
        doc={'sections':[{'number':n,'topic':topic,'status':'확인 불가'}
                         for n,topic in enumerate(TOPICS,1)]}
        record={'id':7,'series_id':'DGS10','observed_date':'2026-10-30',
                'value':'4.08','change':'-2.00','article_text':'미국 국채 10년 고정만기 수익률; 연 4.08%; -2.00bp'}
        attach_official_tables(doc,[record])
        section=doc['sections'][1]
        self.assertEqual(section['table']['headers'],['만기·관측일','연 %','변동 bp'])
        self.assertEqual(section['table']['rows'],[['10년 10-30','4.08','-2.00']])
        self.assertEqual(section['source_ids'],[7])

    def test_temporary_ai_overload_retries_creation_only(self):
        busy=Mock(status_code=503,ok=False)
        ready=Mock(status_code=200,ok=True)
        ready.json.return_value={'candidates':[{'content':{'parts':[{'text':'{"approved":true}'}]}}]}
        with patch.dict('os.environ',{'GEMINI_API_KEY':'test-only'}),patch('briefing.available_model',return_value='gemini-3.8-flash'),patch('briefing.requests.post',side_effect=[busy,ready]) as post,patch('briefing.time.sleep'):
            self.assertEqual(generate('test'),{'approved':True})
        self.assertEqual(post.call_count,2)

    def test_unverified_number_is_withheld_without_relaxing_validation(self):
        sections=[{'number':n,'topic':topic,'status':'확인 불가','source_ids':[],
                   'title':'확인 불가','bullets':[]} for n,topic in enumerate(TOPICS,1)]
        sections[8].update(status='확인',source_ids=[1],bullets=['성장률 32%'],
                           evidence_quotes=[{'source_id':1,'text':'growth was 3.2 percent'}])
        sections[9].update(positive=[],negative=[],ideas=['관찰']*3)
        data={'date':'2026-11-02','sections':sections,'caption':''}
        quarantine_unsupported(data,[{'id':1,'article_text':'growth was 3.2 percent'}],'2026-11-02')
        self.assertEqual(sections[8]['status'],'확인 불가')
        self.assertNotIn('32',str(sections[8]['bullets']))

    def test_yield_change_is_basis_points_and_has_observation_date(self):
        response=Mock(text='observation_date,DGS10\n2026-10-29,4.10\n2026-10-30,4.08\n')
        with patch('briefing.SERIES',[('DGS10','미국 10년','연 %')]),patch('briefing.requests.get',return_value=response):
            records=official_market_sources(datetime(2026,11,2,tzinfo=timezone(timedelta(hours=9))))
        self.assertEqual(records[0]['observed_date'],'2026-10-30')
        self.assertIn('-2.00bp',records[0]['article_text'])
        self.assertIsNone(records[0]['published'])

    def test_stale_data_is_not_relabelled_as_current(self):
        response=Mock(text='observation_date,CBBTCUSD\n2024-11-28,90000\n2024-11-29,91000\n')
        with patch('briefing.SERIES',[('CBBTCUSD','BTC','USD')]),patch('briefing.requests.get',return_value=response):
            records=official_market_sources(datetime(2026,11,2,tzinfo=timezone.utc))
        self.assertEqual(records,[])

    def test_paid_only_models_are_not_selected(self):
        response=Mock(ok=True)
        response.json.return_value={'models':[{'name':'models/gemini-4-argon','supportedGenerationMethods':['generateContent']}]}
        available_model.cache_clear()
        with patch.dict('os.environ',{'GEMINI_API_KEY':'test-only','GEMINI_MODEL':'gemini-4-argon'}),patch('briefing.requests.get',return_value=response):
            with self.assertRaisesRegex(RuntimeError,'무료 모델'):
                available_model()
        available_model.cache_clear()


if __name__=='__main__':
    unittest.main()
