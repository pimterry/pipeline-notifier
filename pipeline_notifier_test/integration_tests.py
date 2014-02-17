import unittest
from unittest.mock import patch
from flask import json

from pipeline_notifier_test.test_utils import *

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

    @unittest.skip("Commit & build notifications not yet implemented")
    def test_single_step_pipeline_notifies_successes(self):
        client = self.buildClient({"PIPELINE_NOTIFIER_PIPELINES": json.dumps([
            {"name": "Pipeline", "steps": ["Step 1"]},
        ])})

        self.announceCommit(client)
        self.announceStepStart("Step 1", client)
        self.announceStepSuccess("Step 1", client)

        self.assertHipchatNotificationSent(Matches(lambda message: "completed" in message and
                                                                   "failed" not in message))

    def getHipchatNotificationsSent(self):
        return [c for c in self.hipchatMock.return_value.method.call_args_list]

    def assertHipchatNotificationSent(self, matcher = Matches(lambda m: True)):
        self.hipchatMock.assert_called_once_with(token=self.hipchat_token)

        calls = hipchatCallsTo(self.hipchatMock)
        self.assertEquals(len(calls), 1)

        notificationParameters = calls[0][1]["parameters"]
        self.assertEquals(notificationParameters["room_id"], self.hipchat_room_id)

        message = notificationParameters["message"]
        self.assertEquals(message, matcher)

    def buildClient(self, envSettings={}):
        defaultEnv = {"PIPELINE_NOTIFIER_PIPELINES": "[]",
                      "PIPELINE_NOTIFIER_HIPCHAT_ROOM": 123,
                      "PIPELINE_NOTIFIER_HIPCHAT_TOKEN": "qwe"}
        defaultEnv.update(envSettings)

        # Backup hipchat config for later assertions
        self.hipchat_room_id = defaultEnv["PIPELINE_NOTIFIER_HIPCHAT_ROOM"]
        self.hipchat_token = defaultEnv["PIPELINE_NOTIFIER_HIPCHAT_TOKEN"]

        self.patchEnvWithMock(defaultEnv)
        self.patchHipchatWithMock()
        app = build_app()
        return app.test_client()

    def patchEnvWithMock(self, envMock):
        envPatcher = patch("os.environ", new=envMock)
        self.envMock = envPatcher.start();
        self.addCleanup(envPatcher.stop)

    def patchHipchatWithMock(self):
        hipchatPatcher = patch("hipchat.HipChat")
        self.hipchatMock = hipchatPatcher.start()
        self.addCleanup(hipchatPatcher.stop)

    def announceCommit(self, client):
        client.post('/bitbucket', data={"payload": json.dumps({
            "commits": [{
                "author": "Bob",
                "branch": "master",
                "files": [{
                              "file": "somefileA.py",
                              "type": "modified"
                          }],
                "message": "Fixed bug 4",
                "node": "620ade18607a",
                "timestamp": "2013-11-25 19:21:21+00:00",
                "utctimestamp": "2013-11-25 19:21:21Z"
            }],
            "repository": {
                "absolute_url": "/project/path/",
                "fork": False,
                "is_private": False,
                "name": "Project Name",
                "owner": "Mr Project Owner",
                "scm": "git",
                "slug": "project-name",
                "website": "https://project-website.com/"
            },
            "user": "Bob"
        })})

    def announceStepStart(self, stepName, client):
        client.post('/jenkins', data=json.dumps({
            "name": stepName,
            "url": "http://jenkins.example.com/step1",
            "build": {
                "number": 1,
                "phase": "STARTED",
                "status": "SUCCESS",
                "url": "job/project/5",
                "full_url": "http://ci.jenkins.org/job/project/5",
                "parameters": {"branch":"master"}
            }
        }))

    def announceStepSuccess(self, stepName, client):
        client.post('/jenkins', data=json.dumps({
            "name": stepName,
            "url": "http://jenkins.example.com/step1",
            "build": {
                "number": 1,
                "phase": "FINISHED",
                "status": "SUCCESS",
                "url": "job/project/5",
                "full_url": "http://ci.jenkins.org/job/project/5",
                "parameters": {"branch":"master"}
            }
        }))

    def announceStepFailure(self, stepName, client):
        client.post('/jenkins', data=json.dumps({
            "name": stepName,
            "url": "http://jenkins.example.com/step",
            "build": {
                "number": 1,
                "phase": "FINISHED",
                "status": "FAILED",
                "url": "job/project/5",
                "full_url": "http://ci.jenkins.org/job/project/5",
                "parameters": {"branch":"master"}
            }
        }))
