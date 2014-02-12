from pipeline_notifier.hipchat_notifier import HipchatNotifier
from pipeline_notifier.pipeline_model import Commit

import unittest
from unittest.mock import patch

class Matches:
    def __init__(self, matcher):
        self.matcher = matcher
    def __eq__(self, other):
        return self.matcher(other)

@patch("hipchat.HipChat")
class HipchatNotifierTests(unittest.TestCase):
    def test_hipchat_token_is_used(self, hipchatMock):
        HipchatNotifier("token123abc", 123)

        hipchatMock.assert_called_once_with(token="token123abc")

    def test_failure_sends_message_to_room(self, hipchatMock):
        notifier = HipchatNotifier("token", 123)

        notifier.announce_step_failure([Commit("commit 1"), Commit("commit 2")])

        hipchatCalls = hipchatMock.return_value.method.call_args_list
        self.assert_one_message_posted(hipchatCalls,
                                    Matches(lambda m: m["parameters"]["room_id"] == 123))

    def test_failure_sends_message_describing_failed_commits(self, hipchatMock):
        notifier = HipchatNotifier("token", 123)

        notifier.announce_step_failure([Commit("commit 1"), Commit("commit 2")])

        hipchatCalls = hipchatMock.return_value.method.call_args_list
        self.assert_one_message_posted(hipchatCalls,
                                    Matches(lambda m: len(m["parameters"]["message"]) > 0))

    def assert_one_message_posted(self, hipchatCalls, matcher=Matches(lambda: True)):
        self.assertEqual(1, len(hipchatCalls))
        call = hipchatCalls[0]
        args = dict(list(enumerate(call[0])) + list(call[1].items()))

        self.assertEqual(args["url"], 'rooms/message')
        self.assertEqual(args["method"], 'POST')
        self.assertEqual(args, matcher)