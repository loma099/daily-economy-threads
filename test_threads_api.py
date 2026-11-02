import unittest
from unittest.mock import Mock
import requests
from threads_api import ThreadsAPI


class PublishingChecks(unittest.TestCase):
    def test_image_creation_does_not_publish(self):
        session = Mock()
        response = Mock(ok=True)
        response.json.return_value = {'id': '1234'}
        session.request.return_value = response
        api = ThreadsAPI('test-secret', '99', session)
        self.assertEqual(api.create_image('https://example.org/today.png', '오늘 브리핑'), '1234')
        self.assertEqual(session.request.call_count, 1)
        args, kwargs = session.request.call_args
        self.assertTrue(args[1].endswith('/99/threads'))
        self.assertNotIn('test-secret', args[1])
        self.assertEqual(kwargs['data']['media_type'], 'IMAGE')

    def test_timeout_is_not_retried_or_secret_exposed(self):
        session = Mock()
        session.request.side_effect = requests.Timeout('test-secret')
        api = ThreadsAPI('test-secret', '99', session)
        with self.assertRaises(RuntimeError) as caught:
            api.publish('1234')
        self.assertNotIn('test-secret', str(caught.exception))
        self.assertEqual(session.request.call_count, 1)

    def test_rejects_nonpublic_url_before_request(self):
        session = Mock()
        api = ThreadsAPI('test-secret', '99', session)
        with self.assertRaises(ValueError):
            api.create_image('file:///private.png', 'caption')
        session.request.assert_not_called()


if __name__ == '__main__':
    unittest.main()
