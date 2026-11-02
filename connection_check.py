"""Check configured credentials without printing any credential or posting."""
import os
from datetime import datetime,timezone,timedelta
from pathlib import Path
import json
from cryptography.fernet import Fernet
from threads_api import ThreadsAPI


def validate_token_metadata(data):
    app_id=data.get('app_id') or data.get('client_id') or data.get('application_id')
    app_matches=(str(app_id) in {'1441693181500200','976266151698671'} if app_id
                 else data.get('application')=='Daily Economy Briefing')
    if data.get('is_valid') is not True or not app_matches:
        raise RuntimeError('토큰이 유효하지 않거나 전용 앱 토큰이 아닙니다.')
    allowed={'threads_basic','threads_content_publish'}
    scopes=set(data.get('scopes',[]))
    if scopes!=allowed:
        raise RuntimeError('기본 프로필·게시 두 권한만 필요합니다. 현재 권한: '+', '.join(sorted(scopes)))
    expires=int(data.get('expires_at') or 0)
    if expires-datetime.now(timezone.utc).timestamp()<2*86400:
        raise RuntimeError('장기 토큰의 유효기간을 확인할 수 없거나 2일 미만입니다.')
    return {'scopes':sorted(scopes),'expires_at':expires}


def main():
    api=ThreadsAPI()
    identity=api.call('GET','/me',{'fields':'id,username'})
    if identity.get('username')!='lej0954':
        raise RuntimeError('연결된 Threads 계정이 요청한 계정과 다릅니다.')
    debug=api.call('GET','/debug_token',{'input_token':api.token})['data']
    print('Token metadata (no credentials): '+json.dumps({k:debug.get(k) for k in
          ('app_id','application','is_valid','scopes','expires_at')},ensure_ascii=False))
    metadata=validate_token_metadata(debug)
    Fernet(os.environ['TOKEN_ENCRYPTION_KEY'].encode())
    result={'username':identity['username'],'user_id':identity['id'],
            'checked_at':datetime.now(timezone(timedelta(hours=9))).isoformat(),
            'posting_test':'not performed',**metadata}
    Path('build').mkdir(exist_ok=True)
    Path('build/connection_check.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    print('Threads 연결 확인: @'+identity['username']+' / '+identity['id'])


if __name__=='__main__':
    main()
