from pipeline_notifier.hipchat_notifier import HipchatNotifier

import unittest
from unittest.mock import patch, Mock

from pipeline_notifier_test.test_utils import *

@patch("hipchat.HipChat")
class HipchatNotifierTests(unittest.TestCase):
    def test_hipchat_token_is_used(self, hipchatMock):
        HipchatNotifier("token123abc", 123)

        hipchatMock.assert_called_once_with(token="token123abc")

    def test_success_sends_message_to_room(self, hipchatMock):
        notifier = HipchatNotifier("token", 123)

        notifier.announce_pipeline_success(Mock(name="pipeline"), [MockCommit("commit")])

        self.assert_one_message_posted(hipchatCallsTo(hipchatMock),
                                       Matches(lambda m: m["parameters"]["room_id"] == 123))


    def test_success_sends_message_describing_passed_commits(self, hipchatMock):
        notifier = HipchatNotifier("token", 123)

        notifier.announce_pipeline_success(Mock(name="pipeline"),
                                           [MockCommit("commit1"), MockCommit("commit2")])

        isExpectedMessage = lambda m: ("failed" not in m and
                                       "commit1" in m and
                                       "commit2" in m)
        self.assert_one_message_posted(hipchatCallsTo(hipchatMock),
                                    Matches(lambda m: isExpectedMessage(m["parameters"]["message"])))

    def test_failure_sends_message_to_room(self, hipchatMock):
        notifier = HipchatNotifier("token", 123)

        notifier.announce_step_failure(Mock(), [MockCommit("commit")])

        self.assert_one_message_posted(hipchatCallsTo(hipchatMock),
                                    Matches(lambda m: m["parameters"]["room_id"] == 123))

    def test_failure_sends_message_describing_failed_commits(self, hipchatMock):
        notifier = HipchatNotifier("token", 123)

        notifier.announce_step_failure(Mock(), [MockCommit("commit 1"), MockCommit("commit 2")])

        isExpectedMessage = lambda m: "failed" in m and "commit 1" in m and "commit 2" in m
        self.assert_one_message_posted(hipchatCallsTo(hipchatMock),
                                Matches(lambda m: isExpectedMessage(m["parameters"]["message"])))

    def test_failure_sends_message_describing_failed_build_step(self, hipchatMock):
        notifier = HipchatNotifier("token", 123)
        buildStep = Mock()
        buildStep.configure_mock(name="Step name")

        notifier.announce_step_failure(buildStep, [MockCommit("commit 1")])

        isExpectedMessage = lambda m: "failed" in m and buildStep.name in m
        self.assert_one_message_posted(hipchatCallsTo(hipchatMock),
                                Matches(lambda m: isExpectedMessage(m["parameters"]["message"])))

    def test_failure_sends_message_for_failed_builds_without_commits(self, hipchatMock):
        notifier = HipchatNotifier("token", 123)

        notifier.announce_step_failure(Mock(), [])

        self.assert_one_message_posted(hipchatCallsTo(hipchatMock))

    def test_from_name_must_be_less_than_15_characters(self, hipchatMock):
        notifier = HipchatNotifier("token", 123)

        notifier.announce_pipeline_success(Mock(), [])
        notifier.announce_step_failure(Mock(), [])

        calls = hipchatCallsTo(hipchatMock)
        self.assertLess(len(calls[0][1]["parameters"]["from"]), 15)
        self.assertLess(len(calls[1][1]["parameters"]["from"]), 15)

    def assert_one_message_posted(self, hipchatCalls, matcher=Matches(lambda x: True)):
        self.assertEqual(1, len(hipchatCalls))
        call = hipchatCalls[0]
        args = dict(list(enumerate(call[0])) + list(call[1].items()))

        self.assertEqual(args["url"], 'rooms/message')
        self.assertEqual(args["method"], 'POST')
        self.assertEqual(args, matcher)