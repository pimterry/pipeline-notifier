import unittest
from unittest.mock import patch
from flask import json

from pipeline_notifier.main import build_app

class IntegrationTests(unittest.TestCase):
    def setUp(self):
        self.patchEnvWithMock()
        app = build_app()
        self.client = app.test_client()

    def patchEnvWithMock(self):
        envPatcher = patch("os.environ", new=dict())
        self.envMock = envPatcher.start();
        self.addCleanup(envPatcher.stop)

    def test_status_page_returns_ok(self):
        result = self.client.get('/status')

        status = json.loads(result.data)
        self.assertEqual("ok", status["status"])