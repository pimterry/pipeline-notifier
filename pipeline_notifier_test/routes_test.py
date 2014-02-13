import unittest
from unittest.mock import Mock
from pipeline_notifier.routes import setup_routes

class RoutesTests(unittest.TestCase):
    def test_route_setup_works(self):
        setup_routes(Mock(), [])