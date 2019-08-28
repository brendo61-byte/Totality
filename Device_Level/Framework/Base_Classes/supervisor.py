class Supervisor:
    """
    Each supervisor Will inherit from this supervisor class
    The deviceManager will launch a thread with this class and call 'getData'
    Data will be 'packaged' (see package class) and put in a 'dataPipe' (see dataPipe) queue to be shipped off
    """

    def getData(self):
        return

    def getSupervisorHeaders(self):
        return

    def getSupervisorTags(self):
        return

    def getSupervisorInfo(self):
        return

    def getSupervisorID(self):
        return

    def monitor(self, data):
        return None

    def package(self, data, TS):
        return
