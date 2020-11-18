class Request:
    def __init__(self, scope, receive, send):
        self.scope = scope
        self.receive = receive
        self.send = send
