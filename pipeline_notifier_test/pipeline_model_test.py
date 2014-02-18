import unittest
from unittest.mock import Mock, call

from pipeline_notifier.pipeline_model import Pipeline, BuildStep, Commit
from pipeline_notifier_test.test_utils import *

class PipelineTests(unittest.TestCase):
    def test_callbacks_are_set_on_build_steps(self):
        step, notifier = Mock(), Mock()

        Pipeline("pipeline", [step], notifier)

        self.assertEquals(1, len(step.add_success_listener.mock_calls))
        self.assertEquals(1, len(step.add_failure_listener.mock_calls))

    def test_an_intermediate_successful_step_is_told_to_call_the_next_step(self):
        step1, step2, notifier = Mock(), Mock(), Mock()

        Pipeline("pipeline", [step1, step2], notifier)

        self.assertEquals(step1.add_success_listener.mock_calls[0], call(step2.add_commit))

    def test_a_final_successful_step_causes_a_notification(self):
        step1, step2, commit, notifier = Mock(), Mock(), Mock(), Mock()

        pipeline = Pipeline("pipeline", [step1, step2], notifier)

        success_callback = step2.add_success_listener.call_args[0][0]
        success_callback(commit)

        notifier.announce_pipeline_success.assert_called_once_with(pipeline, commit)

    def test_a_failing_step_causes_a_notification(self):
        step1, step2, commit, notifier = Mock(), Mock(), Mock(), Mock()

        pipeline = Pipeline("pipeline", [step1, step2], notifier)

        failure_callback = step1.add_failure_listener.call_args[0][0]
        failure_callback(commit)

        notifier.announce_step_failure.assert_called_once_with(pipeline, commit)

    def test_pipeline_status_describes_pipeline_name(self):
        step1, notifier = Mock(**{"status": ""}), Mock()

        pipeline = Pipeline("my first pipeline", [step1], notifier)

        self.assertEqual(pipeline.status["name"], "my first pipeline")

    def test_pipeline_status_describes_steps(self):
        step1, step2, notifier = Mock(**{"status": "status 1"}), Mock(**{"status": "status 2"}), Mock()

        pipeline = Pipeline("pipeline", [step1, step2], notifier)

        self.assertEqual(len(pipeline.status["steps"]), 2)
        self.assertEqual(pipeline.status["steps"][0], "status 1")
        self.assertEqual(pipeline.status["steps"][1], "status 2")

    def test_adding_commit_to_pipeline_adds_to_the_first_step(self):
        step1, step2, notifier = Mock(), Mock(), Mock()
        commit1 = MockCommit("commit1")

        pipeline = Pipeline("pipeline", [step1, step2], notifier)

        pipeline.add_commit(commit1)
        step1.add_commit.assert_called_once_with(commit1)
        self.assertEquals(0, step2.add_commit.call_count)


class BuildStepTests(unittest.TestCase):
    def test_build_step_passes_call_success_callbacks(self):
        step, commit, callback = BuildStep("step1"), MockCommit("1"), Mock()
        step.add_success_listener(callback)

        step.add_commit(commit)
        step.start()
        step.succeed()

        callback.assert_called_once_with(commit)

    def test_build_step_failures_call_failure_callbacks(self):
        step, commit, callback = BuildStep("step1"), MockCommit("1"), Mock()
        step.add_failure_listener(callback)

        step.add_commit(commit)
        step.start()
        step.fail()

        callback.assert_called_once_with(commit)

    def test_build_steps_only_passes_commits_present_when_the_step_was_started(self):
        step, commit1, commit2, callback = BuildStep("step1"), MockCommit("1"), MockCommit("2"), Mock()
        step.add_success_listener(callback)

        step.add_commit(commit1)
        step.start()
        step.add_commit(commit2)
        step.succeed()

        callback.assert_called_once_with(commit1)

    def test_build_steps_only_fails_commits_present_when_the_step_was_started(self):
        step, commit1, commit2, callback = BuildStep("step1"), MockCommit("1"), MockCommit("2"), Mock()
        step.add_failure_listener(callback)

        step.add_commit(commit1)
        step.start()
        step.add_commit(commit2)
        step.fail()

        callback.assert_called_once_with(commit1)

    def test_build_step_doesnt_call_wrong_callbacks(self):
        step = BuildStep("step1")
        commit1, commit2 = MockCommit("1"), MockCommit("2")
        success_callback, failure_callback = Mock(), Mock()
        step.add_success_listener(success_callback)
        step.add_failure_listener(failure_callback)

        step.add_commit(commit1)
        step.start()
        step.fail()

        step.add_commit(commit2)
        step.start()
        step.succeed()

        failure_callback.assert_called_once_with(commit1)
        success_callback.assert_called_once_with(commit2)

    def test_step_status_lists_waiting_commits(self):
        step = BuildStep("a step")
        commit1, commit2 = Mock(**{"status":"commit 1"}), Mock(**{"status":"commit 2"})

        step.add_commit(commit1)
        step.start()
        step.succeed()
        step.add_commit(commit2)

        self.assertEqual(step.status["waiting"], ["commit 2"])

    def test_step_status_lists_in_progress_commits(self):
        step = BuildStep("a step")
        commit1 = Mock(**{"status": "commit status"})

        step.add_commit(commit1)
        step.start()

        self.assertEqual(step.status["waiting"], [])
        self.assertEqual(step.status["in-progress"], ["commit status"])

    def test_step_status_includes_step_name(self):
        step = BuildStep("my build step")

        self.assertEqual(step.status["name"], "my build step")

class CommitTests(unittest.TestCase):
    def test_commit_name_is_saved(self):
        commit = Commit("author", "branch", "message", "hash")
        self.assertEquals(commit.author, "author")
        self.assertEquals(commit.branch, "branch")
        self.assertEquals(commit.message, "message")
        self.assertEquals(commit.hash, "hash")

    def test_commit_description_contains_user__branch_and_short_message(self):
        commit = Commit("A User", "master", "My Commit Message\nSome more message", "123qwe")

        self.assertEquals(commit.description, "A User on 'master': My Commit Message")

    def test_commit_status_contains_user_and_hash(self):
        commit = Commit("A User", "master", "My Commit Message\nSome more message", "123qwe")

        self.assertEquals(commit.status, "123qwe by 'A User'")
