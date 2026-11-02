"""Read-only provider availability check; never prints the API key."""
import json
import os
from pathlib import Path
import requests


def main():
    key=os.environ['GEMINI_API_KEY']
    response=requests.get('https://generativelanguage.googleapis.com/v1beta/models',
                          headers={'x-goog-api-key':key},timeout=40)
    if not response.ok:
        raise RuntimeError(f'AI 모델 목록 확인 실패 HTTP {response.status_code}')
    names=[m['name'].removeprefix('models/') for m in response.json().get('models',[])
           if 'generateContent' in m.get('supportedGenerationMethods',[])]
    known_free=['gemini-3.8-flash','gemini-3.6-flash','gemini-3.1-flash-lite','gemini-3.5-flash-lite']
    matches=[name for name in known_free if name in names]
    Path('build').mkdir(exist_ok=True)
    Path('build/provider_models.json').write_text(json.dumps({'available_known_free_models':matches},indent=2),encoding='utf-8')
    print('무료 지원 후보 중 연결된 프로젝트에서 보이는 모델: '+', '.join(matches))
    if not matches:
        raise RuntimeError('확인된 무료 지원 모델 없음: 유료 전환하지 않습니다.')


if __name__=='__main__':
    main()
