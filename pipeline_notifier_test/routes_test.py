import unittest
from unittest.mock import Mock, patch
from flask import json

from pipeline_notifier.routes import setup_routes

@patch("flask.request")
class RoutesTests(unittest.TestCase):
    def setUp(self):
        self.pipelineA, self.pipelineB = Mock(**{"status": ""}), Mock(**{"status": ""})
        self.patchBitbucketNotifications()

        self.app = AppMock()
        setup_routes(self.app, [self.pipelineA, self.pipelineB])

    def patchBitbucketNotifications(self):
        bitbucketPatcher = patch("pipeline_notifier.incoming_notifications.BitbucketNotification")
        self.bitbucketNotificationMock = bitbucketPatcher.start()
        self.addCleanup(bitbucketPatcher.stop)

    def test_status_route_returns_ok_initially(self, requestMock):
        statusResult = self.app['/status']()
        self.assertEqual("ok", json.loads(statusResult)["status"])

    def test_status_route_returns_pipeline_details(self, requestMock):
        self.pipelineA.status = {"steps": [1], "commits": []}
        self.pipelineB.status = {"steps": [2, 3, 4], "commits": []}

        pipelineStatuses = json.loads(self.app['/status']())["pipelines"]

        self.assertEqual(2, len(pipelineStatuses))
        self.assertEqual(self.pipelineA.status, pipelineStatuses[0])
        self.assertEqual(self.pipelineB.status, pipelineStatuses[1])

    def test_bitbucket_route_updates_pipeline(self, requestMock):
        requestMock.form.__getitem__.return_value = '{"commits": [1, 2, 3]}'
        self.bitbucketNotificationMock.return_value.commits = ["a commit"]

        self.app['/bitbucket']()

        self.bitbucketNotificationMock.assert_called_once_with({"commits": [1, 2, 3]})
        self.pipelineA.add_commit.assert_called_once_with("a commit")

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