import hipchat

class HipchatNotifier:
    def __init__(self, token, room_id):
        self.hipchatConn = hipchat.HipChat(token=token)
        self.room_id = room_id

    def announce_step_failure(self, step, commits):
        self.hipchatConn.method(url='rooms/message', method='POST', parameters={
            'room_id': self.room_id,
            'from': 'Pipeline Notifier',
            'message': 'Build step %s failed, for commits: %s' %
                        (step.name, ', '.join(c.name for c in commits))
        })