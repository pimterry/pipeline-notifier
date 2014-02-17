import unittest
from unittest.mock import Mock
from flask import json

from pipeline_notifier.routes import setup_routes

class RoutesTests(unittest.TestCase):
    def setUp(self):
        self.pipelineA, self.pipelineB = Mock(**{"status": ""}), Mock(**{"status": ""})
        self.notifier = Mock()
        self.app = AppMock()
        setup_routes(self.app, [self.pipelineA, self.pipelineB], self.notifier)

    def test_status_route_returns_ok_initially(self):
        statusResult = self.app['/status']()
        self.assertEqual("ok", json.loads(statusResult)["status"])

    def test_status_route_returns_pipeline_details(self):
        self.pipelineA.status = {"steps": [1], "commits": []}
        self.pipelineB.status = {"steps": [2, 3, 4], "commits": []}

        pipelineStatuses = json.loads(self.app['/status']())["pipelines"]

        self.assertEqual(2, len(pipelineStatuses))
        self.assertEqual(self.pipelineA.status, pipelineStatuses[0])
        self.assertEqual(self.pipelineB.status, pipelineStatuses[1])

class AppMock:
    """
    Acts as a mock flask app, but only recording the routes,
    so they can be then easily accessed for testing later.
    """

    def __init__(self):
        self.routes = {}

    def route(self, route):
        return self.decoratorFor(route)

    def decoratorFor(self, route):
        def decorator(routeTarget):
            self.routes[route] = routeTarget
            return routeTarget
        return decorator

    def __getitem__(self, item):
        return self.routes[item]