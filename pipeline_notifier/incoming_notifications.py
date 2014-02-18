from pipeline_notifier.pipeline_model import Commit

class BitbucketNotification:
    def __init__(self, notification_data):
        self.pushing_user = notification_data["user"]
        self.commits = [Commit(c["author"], c["branch"], c["message"], c["node"])
                        for c in notification_data["commits"]]

    def update_pipeline(self, pipeline):
        for commit in self.commits:
            pipeline.add_commit(commit)

class JenkinsNotification:
    def __init__(self, notification_data):
        self.step_name = notification_data["name"]
        self.is_passing = notification_data["build"]["status"] == "SUCCESS"

        # Need to check both states because of an intermediate 'COMPLETED' state we want to ignore
        self.is_starting = notification_data["build"]["phase"] == "STARTED"
        self.is_finished = notification_data["build"]["phase"] == "FINISHED"

    def update_pipeline(self, pipeline):
        if self.is_finished:
            if self.is_passing:
                pipeline.pass_step(self.step_name)
            else:
                pipeline.fail_step(self.step_name)

        elif self.is_starting:
            pipeline.start_step(self.step_name)
