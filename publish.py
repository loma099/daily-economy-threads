"""Cloud-only final stage with durable pre-publish records and encrypted renewal.

Not wired into the setup workflow until account/hosting tests have passed.
"""
import base64
import hashlib
import json
import os
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests
from cryptography.fernet import Fernet
from threads_api import ThreadsAPI

KST=timezone(timedelta(hours=9))


class Repository:
    def __init__(self):
        self.repo=os.environ['GITHUB_REPOSITORY']
        self.session=requests.Session()
        self.session.headers.update({'Authorization':'Bearer '+os.environ['GITHUB_TOKEN'],
                                     'Accept':'application/vnd.github+json',
                                     'X-GitHub-Api-Version':'2022-11-28'})

    def get(self,path):
        response=self.session.get(f'https://api.github.com/repos/{self.repo}/contents/{path}',timeout=40)
        if response.status_code==404:
            return None,None
        if not response.ok:
            raise RuntimeError(f'GitHub 상태 읽기 실패 HTTP {response.status_code}')
        data=response.json()
        return base64.b64decode(data['content']),data['sha']

    def put(self,path,body,message):
        _,sha=self.get(path)
        payload={'message':message,'content':base64.b64encode(body).decode()}
        if sha:
            payload['sha']=sha
        response=self.session.put(f'https://api.github.com/repos/{self.repo}/contents/{path}',
                                   json=payload,timeout=40)
        if not response.ok:
            raise RuntimeError(f'GitHub 상태 저장 실패 HTTP {response.status_code}; 게시 중단')


def get_token(repo):
    cipher=Fernet(os.environ['TOKEN_ENCRYPTION_KEY'].encode())
    seed=os.environ['THREADS_ACCESS_TOKEN'].strip()
    seed_hash=hashlib.sha256(seed.encode()).hexdigest()
    stored,_=repo.get('.state/threads-token.enc')
    if stored:
        data=json.loads(cipher.decrypt(stored))
        if data.get('seed_hash')!=seed_hash:
            data={'token':seed,'renewed_at':None,'seed_hash':seed_hash}
    else:
        data={'token':seed,'renewed_at':None,'seed_hash':seed_hash}
    now=datetime.now(timezone.utc)
    renewed=datetime.fromisoformat(data['renewed_at']) if data.get('renewed_at') else None
    if renewed is None or now-renewed>timedelta(days=7):
        # Official endpoint uses query authentication. Never log requests/errors.
        response=requests.get('https://graph.threads.net/refresh_access_token',
                              params={'grant_type':'th_refresh_token','access_token':data['token']},timeout=45)
        if not response.ok:
            # Fresh long-lived tokens cannot be refreshed for their first 24h.
            # Do not hide an expired/revoked token: API identity check below fails.
            if renewed is not None:
                raise RuntimeError(f'Threads 토큰 갱신 실패 HTTP {response.status_code}')
        else:
            data['token']=response.json()['access_token']
            data['renewed_at']=now.isoformat()
            repo.put('.state/threads-token.enc',cipher.encrypt(json.dumps(data).encode()),'Renew encrypted Threads token')
    return data['token']


def main():
    if os.environ.get('ENABLE_PUBLISH')!='true':
        raise RuntimeError('실제 게시 연결 미활성: 시험 통과 후에만 활성화합니다.')
    ready=json.loads(Path('build/ready.json').read_text(encoding='utf-8'))
    today=datetime.now(KST).date().isoformat()
    if ready['date']!=today:
        raise RuntimeError('오늘 자료가 아닙니다.')
    checked=datetime.fromisoformat(ready['checked_at'])
    if datetime.now(KST)-checked>timedelta(hours=2):
        raise RuntimeError('검토 마감 이후 2시간 경과: 재검토 필요')
    repo=Repository()
    receipt_path=f'.state/{today}.json'
    existing,_=repo.get(receipt_path)
    if existing:
        receipt=json.loads(existing)
        if receipt.get('status')=='published':
            print('당일 게시 영수증 확인: 중복 게시하지 않음')
            return
        raise RuntimeError('당일 게시 시도 이력 있음: 상태 확인 전 재전송 금지')
    api=ThreadsAPI(get_token(repo))
    identity=api.call('GET','/me',{'fields':'id,username'})
    if (api.user_id!='0' and identity['id']!=api.user_id) or identity.get('username')!=os.environ['THREADS_USERNAME']:
        raise RuntimeError('게시 계정 불일치')
    api.user_id=identity['id']
    from connection_check import validate_token_metadata
    validate_token_metadata(api.call('GET','/debug_token',{'input_token':api.token})['data'])
    recent=api.call('GET',f'/{api.user_id}/threads',{'fields':'id,text,timestamp,permalink','limit':25})
    for post in recent.get('data',[]):
        try:
            stamp=datetime.fromisoformat(post.get('timestamp','').replace('Z','+00:00'))
        except ValueError:
            continue
        text=post.get('text','').replace(' ','')
        if stamp.astimezone(KST).date().isoformat()==today and '경제브리핑' in text:
            receipt={'date':today,'status':'published','post_id':post['id'],
                     'permalink':post.get('permalink'),'source':'existing_same_day_briefing',
                     'checked_at':datetime.now(KST).isoformat()}
            repo.put(receipt_path,json.dumps(receipt,ensure_ascii=False).encode(),f'Record existing briefing {today}')
            print('당일 기존 브리핑 확인: 중복 게시하지 않음 '+str(post.get('permalink','')))
            return
    png=Path('build')/ready['png']
    content=png.read_bytes()
    image_path=f'public/briefing_{today}.png'
    repo.put(image_path,content,f'Publish verified infographic {today}')
    sources=json.loads(Path('build/sources.json').read_text(encoding='utf-8'))
    source_list='\n'.join(f"- {s['publisher']} | 관측/발행일: {s.get('observed_date') or s.get('published') or '확인 불가'} | {s['url']}" for s in sources['sources'])
    # Publish URLs and dates only, never scraped full articles or auth data.
    repo.put(f'public/sources_{today}.md',
             (f"# {today}\n기준 시각: {sources['checked_at']}\n\n"+source_list).encode('utf-8'),
             f'Add source links {today}')
    url=f'https://raw.githubusercontent.com/{repo.repo}/main/{image_path}'
    for _ in range(8):
        response=requests.get(url,timeout=30)
        if response.ok and response.content==content and response.headers.get('content-type','').startswith('image/'):
            break
        time.sleep(5)
    else:
        raise RuntimeError('공개 PNG 원본 확인 실패: 게시 중단')
    target=datetime.now(KST).replace(hour=7,minute=0,second=0,microsecond=0)
    while datetime.now(KST)<target:
        time.sleep(min(30,(target-datetime.now(KST)).total_seconds()))
    if datetime.now(KST).date().isoformat()!=today:
        raise RuntimeError('게시 전 날짜 변경됨')
    caption=ready['caption']
    if today not in caption:
        caption=today+' 경제 브리핑\n'+caption
    container=api.create_image(url,caption)
    pending={'date':today,'status':'prepared','container_id':container,
             'image_sha256':hashlib.sha256(content).hexdigest(),'image_url':url,
             'attempted_at':datetime.now(KST).isoformat()}
    repo.put(receipt_path,json.dumps(pending,ensure_ascii=False).encode(),'Record Threads container before publish')
    for _ in range(12):
        status=api.container_status(container).get('status')
        if status=='FINISHED':
            break
        if status in ('ERROR','EXPIRED','PUBLISHED'):
            raise RuntimeError('Threads 컨테이너 상태 확인 필요: '+status)
        time.sleep(5)
    else:
        raise RuntimeError('이미지 처리 대기 시간 초과: 자동 재게시 금지')
    # A durable pending receipt exists before this non-idempotent request.
    post_id=api.publish(container)
    post=api.post(post_id)
    pending.update({'status':'published','post_id':post_id,'permalink':post['permalink'],
                    'published_at':datetime.now(KST).isoformat()})
    repo.put(receipt_path,json.dumps(pending,ensure_ascii=False).encode(),f'Record successful Threads post {today}')
    print('Threads 게시 및 영수증 저장 완료: '+post['permalink'])


if __name__=='__main__':
    try:
        main()
    except requests.RequestException:
        # Avoid request exceptions exposing query-authenticated renewal URLs.
        raise SystemExit('외부 통신 실패: 자동 재전송 없이 중단합니다.')
