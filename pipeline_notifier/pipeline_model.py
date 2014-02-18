class Pipeline:
    def __init__(self, name, steps, notifier):
        self.name = name
        self._steps = steps

        for step in steps:
            step.add_failure_listener(lambda commits: notifier.announce_step_failure(self, commits))

        for step, nextStep in zip(steps, steps[1:]):
            step.add_success_listener(nextStep.add_commit)

        if len(steps) > 0:
            steps[-1].add_success_listener(lambda commits: notifier.announce_pipeline_success(self, commits))

    @property
    def status(self):
        return {
            "name": self.name,
            "steps": [s.status for s in self._steps]
        }

# TODO: Actively deal with concurrency here (just wrap steps with locking? message passing?)
class BuildStep:
    def __init__(self, name):
        self.name = name

        self.waiting_commits = []
        self.in_progress_commits = []

        self.success_callbacks = []
        self.failure_callbacks = []

    def add_success_listener(self, callback):
        self.success_callbacks.append(callback)

    def add_failure_listener(self, callback):
        self.failure_callbacks.append(callback)

    def add_commit(self, commit):
        self.waiting_commits.append(commit)

    def start(self):
        self.in_progress_commits.extend(self.waiting_commits)
        self.waiting_commits.clear()

    def succeed(self):
        tested_commits = self.in_progress_commits[:]
        self.in_progress_commits.clear()

        for commit in tested_commits:
            for callback in self.success_callbacks:
                callback(commit)

    def fail(self):
        tested_commits = self.in_progress_commits[:]
        self.in_progress_commits.clear()

        for commit in tested_commits:
            for callback in self.failure_callbacks:
                callback(commit)

    @property
    def status(self):
        return {
            "name": self.name,
            "waiting": [c.status for c in self.waiting_commits],
            "in-progress": [c.status for c in self.in_progress_commits]
        }

class Commit:
    def __init__(self, author, branch, message, hash):
        self.author = author
        self.branch = branch
        self.message = message
        self.hash = hash

    @property
    def description(self):
        return "%s on '%s': %s" % (self.author, self.branch, self.message.split("\n")[0])

    @property
    def status(self):
        return "%s by '%s'" % (self.hash, self.author)