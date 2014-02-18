import unittest
from unittest.mock import Mock, patch
from flask import json

from pipeline_notifier.routes import setup_routes

@patch("flask.request")
class RoutesTests(unittest.TestCase):
    def setUp(self):
        self.pipeline = Mock(**{"status": ""})
        self.patchBitbucketNotifications()
        self.patchJenkinsNotifications()

        self.app = AppMock()
        setup_routes(self.app, [self.pipeline])

    def patchBitbucketNotifications(self):
        bitbucketPatcher = patch("pipeline_notifier.incoming_notifications.BitbucketNotification")
        self.bitbucketNotificationMock = bitbucketPatcher.start()
        self.addCleanup(bitbucketPatcher.stop)

    def patchJenkinsNotifications(self):
        jenkinsPatcher = patch("pipeline_notifier.incoming_notifications.JenkinsNotification")
        self.jenkinsNotificationMock = jenkinsPatcher.start()
        self.addCleanup(jenkinsPatcher.stop)

    def test_status_route_returns_ok_initially(self, requestMock):
        statusResult = self.app['/status']()
        self.assertEqual("ok", json.loads(statusResult)["status"])

    def test_status_route_returns_pipeline_details(self, requestMock):
        self.pipeline.status = {"steps": [1, 2, 3], "commits": []}

        pipelineStatuses = json.loads(self.app['/status']())["pipelines"]

        self.assertEqual(1, len(pipelineStatuses))
        self.assertEqual(self.pipeline.status, pipelineStatuses[0])

    def test_bitbucket_route_updates_pipeline(self, requestMock):
        requestMock.form.__getitem__.return_value = '{"commits": [1, 2, 3]}'
        self.bitbucketNotificationMock.return_value.commits = ["a commit"]

        self.app['/bitbucket']()

        self.bitbucketNotificationMock.assert_called_once_with({"commits": [1, 2, 3]})
        bitbucketNotification = self.bitbucketNotificationMock.return_value
        self.assertEquals(bitbucketNotification.update_pipeline.call_count, 1)
        
    def test_jenkins_route_starts_build_steps(self, requestMock):
        requestMock.data = '{"step": "a step"}'
        self.jenkinsNotificationMock.return_value.step_name = "step name"
        self.jenkinsNotificationMock.return_value.step_status = "started"

        self.app['/jenkins']()

        self.jenkinsNotificationMock.assert_called_once_with({"step": "a step"})
        jenkinsNotification = self.jenkinsNotificationMock.return_value
        self.assertEquals(jenkinsNotification.update_pipeline.call_count, 1)

class AppMock:
    """
    Acts as a mock flask app, but only recording the routes,
    so they can be then easily accessed for testing later.
    """

    def __init__(self):
        self.routes = {}

    def route(self, route, *args, **kwargs):
        return self.decoratorFor(route)

    def decoratorFor(self, route):
        def decorator(routeTarget):
            self.routes[route] = routeTarget
            return routeTarget
        return decorator

    def __getitem__(self, item):
        return self.routes[item]