from pipeline_notifier.hipchat_notifier import HipchatNotifier
from pipeline_notifier.pipeline_model import Commit

import unittest
from unittest.mock import patch, Mock

class Matches:
    def __init__(self, matcher):
        self.matcher = matcher
    def __eq__(self, other):
        return self.matcher(other)

def hipchatCallsTo(hipchatMock):
    return hipchatMock.return_value.method.call_args_list

@patch("hipchat.HipChat")
class HipchatNotifierTests(unittest.TestCase):
    def test_hipchat_token_is_used(self, hipchatMock):
        HipchatNotifier("token123abc", 123)

        hipchatMock.assert_called_once_with(token="token123abc")

    def test_failure_sends_message_to_room(self, hipchatMock):
        notifier = HipchatNotifier("token", 123)

        notifier.announce_step_failure(Mock(), [Commit("commit")])

        self.assert_one_message_posted(hipchatCallsTo(hipchatMock),
                                    Matches(lambda m: m["parameters"]["room_id"] == 123))

    def test_failure_sends_message_describing_failed_commits(self, hipchatMock):
        notifier = HipchatNotifier("token", 123)

        notifier.announce_step_failure(Mock(), [Commit("commit 1"), Commit("commit 2")])

        isExpectedMessage = lambda m: "failed" in m and "commit 1" in m and "commit 2" in m
        self.assert_one_message_posted(hipchatCallsTo(hipchatMock),
                                Matches(lambda m: isExpectedMessage(m["parameters"]["message"])))

    def test_failure_sends_message_describing_failed_build_step(self, hipchatMock):
        notifier = HipchatNotifier("token", 123)
        buildStep = Mock()
        buildStep.configure_mock(name="Step name")

        notifier.announce_step_failure(buildStep, [Commit("commit 1")])

        isExpectedMessage = lambda m: "failed" in m and buildStep.name in m
        self.assert_one_message_posted(hipchatCallsTo(hipchatMock),
                                Matches(lambda m: isExpectedMessage(m["parameters"]["message"])))

    def test_failure_sends_message_for_failed_builds_without_commits(self, hipchatMock):
        notifier = HipchatNotifier("token", 123)

        notifier.announce_step_failure(Mock(), [])

        self.assert_one_message_posted(hipchatCallsTo(hipchatMock))

    def assert_one_message_posted(self, hipchatCalls, matcher=Matches(lambda x: True)):
        self.assertEqual(1, len(hipchatCalls))
        call = hipchatCalls[0]
        args = dict(list(enumerate(call[0])) + list(call[1].items()))

        self.assertEqual(args["url"], 'rooms/message')
        self.assertEqual(args["method"], 'POST')
        self.assertEqual(args, matcher)