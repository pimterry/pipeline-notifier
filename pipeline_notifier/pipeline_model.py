class Pipeline:
    def __init__(self, name, steps, notifier):
        self.name = name
        self._steps = steps

        for step in steps:
            step.add_failure_listener(notifier.on_failure)

        for step, nextStep in zip(steps, steps[1:]):
            step.add_success_listener(nextStep.add_commit)

        steps[-1].add_success_listener(notifier.on_success)

    @property
    def status(self):
        return {
            "name": self.name,
            "steps": [s.status for s in self._steps]
        }

class BuildStep:
    def __init__(self, name):
        self.name = name
        self.waiting_commits = []
        self.success_callbacks = []
        self.failure_callbacks = []

    def add_success_listener(self, callback):
        self.success_callbacks.append(callback)

    def add_failure_listener(self, callback):
        self.failure_callbacks.append(callback)

    def add_commit(self, commit):
        self.waiting_commits.append(commit)

    def succeed(self):
        tested_commits = self.waiting_commits[:]
        self.waiting_commits.clear()

        for commit in tested_commits:
            for callback in self.success_callbacks:
                callback(commit)

    def fail(self):
        tested_commits = self.waiting_commits[:]
        self.waiting_commits.clear()

        for commit in tested_commits:
            for callback in self.failure_callbacks:
                callback(commit)

    @property
    def status(self):
        return {
            "waiting": [c.name for c in self.waiting_commits]
        }

class Commit:
    def __init__(self, name):
        self.name = name