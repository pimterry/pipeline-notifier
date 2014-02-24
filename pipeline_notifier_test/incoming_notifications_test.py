import unittest
from unittest.mock import Mock

from pipeline_notifier.incoming_notifications import BitbucketNotification, JenkinsNotification

class BitbucketNotificationTests(unittest.TestCase):
    def test_notification_parses_pushing_user_name(self):
        notification = BitbucketNotification(self.exampleNotificationJson("message"))

        self.assertEquals(notification.pushing_user, "marcus")

    def test_notification_parses_commit_details(self):
        notification = BitbucketNotification(self.exampleNotificationJson("Commit message"))

        self.assertEquals(len(notification.commits), 1)
        self.assertEquals(notification.commits[0].author, "marcus")
        self.assertEquals(notification.commits[0].branch, "master")
        self.assertEquals(notification.commits[0].message, "Commit message")

    def test_notification_adds_commits_to_pipeline(self):
        pipeline = Mock()
        notification = BitbucketNotification(self.exampleNotificationJson("commit 1", "commit 2"))

        notification.update_pipeline(pipeline)

        self.assertEquals(pipeline.add_commit.call_count, 2)
        added_commit_messages = [call[0][0].message for call in pipeline.add_commit.call_args_list]
        self.assertEquals(added_commit_messages, ["commit 1", "commit 2"])

    def exampleNotificationJson(self, *messages):
        return {
            "canon_url": "https://bitbucket.org",
            "commits": [self.exampleNotificationCommitJson(msg) for msg in messages],
            "repository": {
                "absolute_url": "/marcus/project-x/",
                "fork": False,
                "is_private": True,
                "name": "Project X",
                "owner": "marcus",
                "scm": "git",
                "slug": "project-x",
                "website": "https://atlassian.com/"
            },
            "user": "marcus"
        }

    def exampleNotificationCommitJson(self, message):
        return {
            "author": "marcus",
            "branch": "master",
            "files": [{ "file": "somefile.py", "type": "added" }],
            "message": message,
            "node": "620ade18607a",
            "parents": ["702c70160afc"],
            "raw_author": "Marcus Bertrand <marcus@somedomain.com>",
            "raw_node": "620ade18607ac42d872b568bb92acaa9a28620e9",
            "revision": None,
            "size": -1,
            "timestamp": "2012-05-30 05:58:56",
            "utctimestamp": "2012-05-30 03:58:56+00:00"
        }

class JenkinsNotificationTests(unittest.TestCase):
    def setUp(self):
        self.pipeline = Mock()

    def test_notification_parses_step_phase(self):
        started_notification= JenkinsNotification(self.buildJenkinsNotificationJson("step1", phase="STARTED"))
        completed_notification = JenkinsNotification(self.buildJenkinsNotificationJson("step2", phase="COMPLETED"))
        finished_notification = JenkinsNotification(self.buildJenkinsNotificationJson("step2", phase="FINISHED"))

        self.assertEquals(finished_notification.is_starting, False)
        self.assertEquals(finished_notification.is_finished, True)

        self.assertEquals(completed_notification.is_starting, False)
        self.assertEquals(completed_notification.is_finished, False)

        self.assertEquals(started_notification.is_starting, True)
        self.assertEquals(started_notification.is_finished, False)

    def test_notification_parses_step_status(self):
        successful_notification = JenkinsNotification(self.buildJenkinsNotificationJson("step1", status="SUCCESS"))
        failing_notification = JenkinsNotification(self.buildJenkinsNotificationJson("step2", status="FAILED"))

        self.assertEquals(successful_notification.is_passing, True)
        self.assertEquals(failing_notification.is_passing, False)

    def test_notification_parses_step_name(self):
        notification = JenkinsNotification(self.buildJenkinsNotificationJson("my first step"))
        self.assertEquals(notification.step_name, "my first step")

    def test_notification_parses_build_url(self):
        notification = JenkinsNotification(self.buildJenkinsNotificationJson("build-step"))
        self.assertEquals(notification.build_url, "http://jenkins.example.com/job/build-step/5")

    def test_notification_updates_passing_pipeline_steps(self):
        jenkins_json = self.buildJenkinsNotificationJson("step1", phase="FINISHED", status="SUCCESS")
        notification = JenkinsNotification(jenkins_json)

        notification.update_pipeline(self.pipeline)

        self.assertEqual(len(self.pipeline.mock_calls), 1)
        self.pipeline.pass_step.assert_called_once_with("step1")

    def test_notification_updates_failing_pipeline_steps(self):
        jenkins_json = self.buildJenkinsNotificationJson("step1", phase="FINISHED", status="FAILED")
        notification = JenkinsNotification(jenkins_json)

        notification.update_pipeline(self.pipeline)

        self.assertEqual(len(self.pipeline.mock_calls), 1)
        self.pipeline.fail_step.assert_called_once_with("step1")

    def test_notification_updates_starting_pipeline_steps(self):
        jenkins_json = self.buildJenkinsNotificationJson("step1", phase="STARTED", status="SUCCESS")
        notification = JenkinsNotification(jenkins_json)

        notification.update_pipeline(self.pipeline)

        self.assertEqual(len(self.pipeline.mock_calls), 1)
        self.pipeline.start_step.assert_called_once_with("step1")

    def test_notification_updates_starting_pipeline_steps_ignoring_previous_errors(self):
        jenkins_json = self.buildJenkinsNotificationJson("step1", phase="STARTED", status="FAILED")
        notification = JenkinsNotification(jenkins_json)

        notification.update_pipeline(self.pipeline)

        self.assertEqual(len(self.pipeline.mock_calls), 1)
        self.pipeline.start_step.assert_called_once_with("step1")

    def test_notification_ignores_completed_but_not_finished_steps(self):
        jenkins_json = self.buildJenkinsNotificationJson("step1", phase="COMPLETED", status="FAILED")
        notification = JenkinsNotification(jenkins_json)

        notification.update_pipeline(self.pipeline)

        self.assertEqual(len(self.pipeline.mock_calls), 0)

    def buildJenkinsNotificationJson(self, step_name, phase = "FINISHED", status = "SUCCESS"):
        return {
            "name": step_name,
            "url": "http://jenkins.example.com/" + step_name,
            "build":{
                "number": 1,
                "phase": phase,
                "status": status,
                "url": "job/project/5",
                "full_url": "http://jenkins.example.com/job/" + step_name + "/5",
                "parameters": { "branch": "master" }
            }
        }