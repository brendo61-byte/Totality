from queue import Queue


class DataPipe:
    """
    This class a means to move data from supervisors to the DataController that will in turn store data (whether that be locally, though 4G/LoRa/WiFi to a database etc)
    """

    def __init__(self):
        self.pipe = Queue(maxsize=0)

    def put(self, payload):
        self.pipe.put(payload)

    def get(self):
        return self.pipe.get()

    def empty(self):
        return self.pipe.empty()
