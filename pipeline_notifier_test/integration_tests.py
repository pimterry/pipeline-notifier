import unittest
from unittest.mock import patch
from flask import json

from pipeline_notifier.main import build_app

class IntegrationTests(unittest.TestCase):
    def test_status_page_returns_ok(self):
        client = self.buildClient()
        result = client.get('/status')

        status = json.loads(result.data)
        self.assertEqual("ok", status["status"])

    def test_status_page_returns_pipeline_details(self):
        client = self.buildClient({"PIPELINE_NOTIFIER_PIPELINES": json.dumps([
            {"name": "Pipeline A", "steps": ["Step 1"]},
            {"name": "Pipeline B", "steps": ["Step 2", "Step 3"]}
        ])})

        result = client.get('/status')

        status = json.loads(result.data)
        self.assertEqual(status["pipelines"], [
            {"name": "Pipeline A", "steps": [
                {"name": "Step 1", "waiting": [], "in-progress": []}
            ]},
            {"name": "Pipeline B", "steps": [
                {"name": "Step 2", "waiting": [], "in-progress": []},
                {"name": "Step 3", "waiting": [], "in-progress": []}
            ]}
        ])

    def buildClient(self, envSettings={}):
        defaultEnv = {"PIPELINE_NOTIFIER_PIPELINES": "[]"}
        defaultEnv.update(envSettings)

        self.patchEnvWithMock(defaultEnv)
        app = build_app()
        return app.test_client()

    def patchEnvWithMock(self, envMock):
        envPatcher = patch("os.environ", new=envMock)
        self.envMock = envPatcher.start();
        self.addCleanup(envPatcher.stop)