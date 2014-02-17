import unittest
from flask import json

from pipeline_notifier import main

class IntegrationTests(unittest.TestCase):
    def setUp(self):
        self.app = main.app.test_client()

    def test_status_page_returns_ok(self):
        result = self.app.get('/status')

        status = json.loads(result.data)
        self.assertEqual("ok", status["status"])