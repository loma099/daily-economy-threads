"""Check configured credentials without printing any credential or posting."""
import os
from datetime import datetime,timezone,timedelta
from pathlib import Path
import json
from cryptography.fernet import Fernet
from threads_api import ThreadsAPI


def main():
    api=ThreadsAPI()
    identity=api.call('GET','/me',{'fields':'id,username'})
    if identity.get('username')!='lej0954':
        raise RuntimeError('연결된 Threads 계정이 요청한 계정과 다릅니다.')
    Fernet(os.environ['TOKEN_ENCRYPTION_KEY'].encode())
    result={'username':identity['username'],'user_id':identity['id'],
            'checked_at':datetime.now(timezone(timedelta(hours=9))).isoformat(),
            'posting_test':'not performed'}
    Path('build').mkdir(exist_ok=True)
    Path('build/connection_check.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    print('Threads 연결 확인: @'+identity['username']+' / '+identity['id'])


if __name__=='__main__':
    main()
