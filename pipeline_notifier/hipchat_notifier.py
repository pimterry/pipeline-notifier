import hipchat

class HipchatNotifier:
    def __init__(self, token, room_id):
        self.hipchatConn = hipchat.HipChat(token=token)
        self.room_id = room_id

    def announce_pipeline_success(self, pipeline, commits):
        self.hipchatConn.method(url='rooms/message', method='POST', parameters={
            'room_id': self.room_id,
            'from': 'Build Pipeline',
            'message': 'Build completed, for commits: %s' %
                       (', '.join(c.description for c in commits))
        })

    def announce_step_failure(self, step, commits):
        self.hipchatConn.method(url='rooms/message', method='POST', parameters={
            'room_id': self.room_id,
            'from': 'Build Pipeline',
            'message': 'Build step %s failed, for commits: %s' %
                        (step.name, ', '.join(c.description for c in commits))
        })