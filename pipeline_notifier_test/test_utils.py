class Matches:
    def __init__(self, matcher):
        self.matcher = matcher
    def __eq__(self, other):
        return self.matcher(other)

def hipchatCallsTo(hipchatMock):
    return hipchatMock.return_value.method.call_args_list