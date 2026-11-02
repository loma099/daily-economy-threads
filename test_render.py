import tempfile
import unittest
from pathlib import Path
from PIL import Image
from render import render

TOPICS = ['미국 증시','미국 국채','국제 유가','중앙은행','환율','금·비트코인',
          '지정학','기업 실적·AI','주요국 경제','시장 전망','이번 주 경제지표 일정']


def sample():
    return {'date':'2026-11-02','checked_at':'렌더링 시험 · 실제 뉴스 아님',
            'comment':'배치·한글·날짜 렌더링 시험입니다. 실제 뉴스가 아닙니다.',
            'sections':[{'number':n,'topic':topic,'title':'연결 시험',
                         'status':'확인 불가','bullets':['검증 자료 연결 전입니다.'],
                         'impact':'확인 전 시장 방향 단정 금지','source_ids':[]}
                        for n,topic in enumerate(TOPICS,1)]}


class LayoutChecks(unittest.TestCase):
    def test_korean_render_and_image_size(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as folder:
            target=Path(folder)/'test.png'
            data=sample()
            data['sections'][0]['table']={'headers':['지수','기준','값'],
                                         'rows':[['S&P500','시험','확인 불가']]}
            data['sections'][9].update(positive=['검증 후 판단'],negative=['단정 금지'],
                                      ideas=['조건 확인 후 관찰','원문과 수치 확인','발표 시각 확인'])
            data['sections'][10]['table']={'headers':['한국 날짜','시간','일정'],
                                          'rows':[['검증 전','미정','연결 시험']]}
            render(data,target)
            with Image.open(target) as image:
                self.assertEqual(image.size,(2766,4146))
                self.assertEqual(image.format,'PNG')

    def test_overflow_stops_generation(self):
        data=sample()
        data['sections'][0]['bullets']=['매우 긴 글자 '*100]
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as folder:
            with self.assertRaisesRegex(ValueError,'세로 넘침'):
                render(data,Path(folder)/'must-not-publish.png')


if __name__=='__main__':
    unittest.main()
