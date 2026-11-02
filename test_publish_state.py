import json
import unittest
from datetime import datetime
from unittest.mock import Mock,patch

from publish import main,KST


class ReceiptChecks(unittest.TestCase):
    def test_published_receipt_prevents_any_threads_call(self):
        now=datetime.now(KST)
        ready={'date':now.date().isoformat(),'checked_at':now.isoformat()}
        repo=Mock()
        repo.get.return_value=(b'{"status":"published"}','existing-sha')
        with patch.dict('os.environ',{'ENABLE_PUBLISH':'true'}), \
             patch('publish.Path.read_text',return_value=json.dumps(ready)), \
             patch('publish.Repository',return_value=repo), \
             patch('publish.ThreadsAPI') as api:
            main()
        api.assert_not_called()
        repo.put.assert_not_called()


if __name__=='__main__':
    unittest.main()
