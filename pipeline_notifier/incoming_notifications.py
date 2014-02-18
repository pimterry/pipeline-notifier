from pipeline_notifier.pipeline_model import Commit

class BitbucketNotification:
    def __init__(self, notificationData):
        self.pushing_user = notificationData["user"]
        self.commits = [Commit(c["author"], c["branch"], c["message"], c["node"])
                        for c in notificationData["commits"]]

class JenkinsNotification:
    def __init__(self, notificationData):
        pass