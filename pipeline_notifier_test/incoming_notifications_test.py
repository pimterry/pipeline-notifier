import unittest

from pipeline_notifier.incoming_notifications import BitbucketNotification

class BitbucketNotificationTests(unittest.TestCase):
    def test_notification_parses_pushing_user_name(self):
        notification = BitbucketNotification(self.exampleNotificationJson)

        self.assertEquals(notification.pushing_user, "marcus")

    def test_notification_parses_commit_details(self):
        notification = BitbucketNotification(self.exampleNotificationJson)

        self.assertEquals(len(notification.commits), 1)
        self.assertEquals(notification.commits[0].author, "marcus")
        self.assertEquals(notification.commits[0].branch, "master")
        self.assertEquals(notification.commits[0].message, "Added some more things to somefile.py\n")

    @property
    def exampleNotificationJson(self):
        # Taken straight from the bitbucket docs
        return {
            "canon_url": "https://bitbucket.org",
            "commits": [
                {
                    "author": "marcus",
                    "branch": "master",
                    "files": [
                        {
                            "file": "somefile.py",
                            "type": "modified"
                        }
                    ],
                    "message": "Added some more things to somefile.py\n",
                    "node": "620ade18607a",
                    "parents": [
                        "702c70160afc"
                    ],
                    "raw_author": "Marcus Bertrand <marcus@somedomain.com>",
                    "raw_node": "620ade18607ac42d872b568bb92acaa9a28620e9",
                    "revision": None,
                    "size": -1,
                    "timestamp": "2012-05-30 05:58:56",
                    "utctimestamp": "2012-05-30 03:58:56+00:00"
                }
            ],
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