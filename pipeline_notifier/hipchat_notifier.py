import hipchat

class HipchatNotifier:
    def __init__(self, token, room_id):
        self.hipchatConn = hipchat.HipChat(token=token)
        self.room_id = room_id

    def announce_step_failure(self, commits):
        self.hipchatConn.method(url='rooms/message', method='POST', parameters={
            'room_id': self.room_id,
            'from': 'Pipeline Notifier',
            'message': 'Test message'
        })