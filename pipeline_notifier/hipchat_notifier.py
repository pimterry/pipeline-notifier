import hipchat

class HipchatNotifier:
    def __init__(self, token, room_id):
        self.hipchatConn = hipchat.HipChat(token=token)
        self.room_id = room_id

    def announce_pipeline_success(self, pipeline, commits):
        self.hipchatConn.method(url='rooms/message', method='POST', parameters={
            'room_id': self.room_id,
            'from': 'Build Pipeline',
            'message_format': 'html',
            'notify': False,
            'color': 'green',
            'message': "Build completed successfully for commits: <ul>%s</ul>" %
                       (''.join('<li>%s</li>' % c.description for c in commits))
        })

    def announce_step_failure(self, step, commits):
        if len(commits) > 0:
            commits = "for commits: <ul>%s</ul>" % \
                         ''.join('<li>%s</li>' % c.description for c in commits)
        else:
            commits = "with no new commits"

        self.hipchatConn.method(url='rooms/message', method='POST', parameters={
            'room_id': self.room_id,
            'from': 'Build Pipeline',
            'message_format': 'html',
            'notify': True,
            'color': 'red',
            'message': ("<strong>Build failed</strong> at '%s', " % step.name) +
                       commits
        })