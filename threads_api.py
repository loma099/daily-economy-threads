"""Official Threads publishing adapter; not activated by the setup workflow.

The caller must durably save the returned container id BEFORE calling publish.
Never blindly repeat a publish request after an ambiguous transport error.
"""
import os
import requests

BASE = 'https://graph.threads.net/v1.0'


class ThreadsAPI:
    def __init__(self, token=None, user_id=None, session=None):
        self.token = token or os.environ['THREADS_ACCESS_TOKEN']
        self.user_id = user_id or os.environ['THREADS_USER_ID']
        if not self.user_id.isdecimal():
            raise ValueError('Invalid Threads user id')
        self.session = session or requests.Session()

    def call(self, method, path, values=None):
        # Never print response bodies or requests: provider errors can echo data.
        kwargs = {'timeout': 45, 'headers': {'Authorization': f'Bearer {self.token}'}}
        kwargs['params' if method == 'GET' else 'data'] = values or {}
        try:
            response = self.session.request(method, BASE+path, **kwargs)
        except requests.RequestException:
            raise RuntimeError('Threads 통신 불확실: 자동 재전송 금지, 상태 확인 필요') from None
        if not response.ok:
            raise RuntimeError(f'Threads 요청 중단: HTTP {response.status_code}')
        return response.json()

    def create_image(self, image_url, caption):
        if not image_url.startswith('https://') or len(caption) > 500:
            raise ValueError('HTTPS public image URL / caption required')
        return self.call('POST', f'/{self.user_id}/threads', {
            'media_type': 'IMAGE', 'image_url': image_url, 'text': caption})['id']

    def container_status(self, container_id):
        return self.call('GET', '/'+container_id, {'fields': 'status,error_message'})

    def publish(self, container_id):
        return self.call('POST', f'/{self.user_id}/threads_publish',
                         {'creation_id': container_id})['id']

    def post(self, post_id):
        return self.call('GET', '/'+post_id, {'fields': 'id,permalink,timestamp,text'})

