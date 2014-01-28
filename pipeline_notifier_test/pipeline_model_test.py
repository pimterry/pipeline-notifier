import unittest
from unittest.mock import Mock, call
from pipeline_notifier.pipeline_model import Pipeline, BuildStep, Commit

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

        Pipeline("pipeline", [step1, step2], notifier)

        success_callback = step2.add_success_listener.call_args[0][0]
        success_callback(commit)

        notifier.on_success.assert_called_once_with(commit)

    def test_a_failing_step_causes_a_notification(self):
        step1, step2, commit, notifier = Mock(), Mock(), Mock(), Mock()

        Pipeline("pipeline", [step1, step2], notifier)

        failure_callback = step1.add_failure_listener.call_args[0][0]
        failure_callback(commit)

        notifier.on_failure.assert_called_once_with(commit)


class BuildStepTests(unittest.TestCase):
    def test_build_step_passes_calls_callbacks_for_successes(self):
        step = BuildStep("step1")
        commit = Commit("1")
        callback = Mock()

        step.add_success_listener(callback)
        step.add_commit(commit)
        step.succeed()

        callback.assert_called_once_with(commit)

    def test_build_step_passes_calls_callbacks_for_failures(self):
        step = BuildStep("step1")
        commit = Commit("1")
        callback = Mock()

        step.add_failure_listener(callback)
        step.add_commit(commit)
        step.fail()

        callback.assert_called_once_with(commit)

    def test_build_step_doesnt_call_wrong_callbacks(self):
        step = BuildStep("step1")
        success_callback, failure_callback = Mock(), Mock()
        commit1, commit2 = Commit("1"), Commit("2")

        step.add_success_listener(success_callback)
        step.add_failure_listener(failure_callback)
        step.add_commit(commit1)
        step.fail()
        step.add_commit(commit2)
        step.succeed()

        failure_callback.assert_called_once_with(commit1)
        success_callback.assert_called_once_with(commit2)

class CommitTests(unittest.TestCase):
    def test_commit_name_is_saved(self):
        commit = Commit("commit name")
        self.assertEquals(commit.name, "commit name")
