import unittest
from unittest.mock import Mock,patch
from datetime import datetime,timezone,timedelta
from briefing import official_market_sources,available_model


class DataChecks(unittest.TestCase):
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
