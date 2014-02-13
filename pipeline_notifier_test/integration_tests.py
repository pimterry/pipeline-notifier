import unittest
from pipeline_notifier import main

class IntegrationTests(unittest.TestCase):
    def setUp(self):
        self.app = main.app.test_client()

    def test_root_page_returns_something(self):
        result = self.app.get('/')
        self.assertNotEqual(len(result.data), 0)