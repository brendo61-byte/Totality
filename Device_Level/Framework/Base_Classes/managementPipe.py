from queue import Queue


class ManagementPipe:
    """
    For movement of management packages
    """

    def __init__(self):
        self.pipe = Queue(maxsize=0)

    def put(self, payload):
        self.pipe.put(payload)

    def get(self):
        return self.pipe.get()

    def empty(self):
        return self.pipe.empty()
