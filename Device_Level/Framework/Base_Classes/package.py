class Package:
    """
    A convenient means of transporting data internal with all needed information to upload to Influx, save as a CSV, or do whatever is needed
    """

    def __init__(self, data, timeStamp, tags=None, headers=0, monitorResponse=None):
        self.data = data
        self.tags = tags
        self.timeStamp = timeStamp
        self.headers = headers
        self.monitor = monitorResponse

    def getPayload(self):  # Payload if for
        payload = {
            "timeStamp(UTC)": self.timeStamp.strftime("%m/%d/%Y-%H:%M:%S"),
            "supervisorID": self.tags["supervisorID"],
            "supervisorName": self.tags["supervisorName"],
            "deviceID": self.tags["deviceID"],
            "customConfig": self.tags["customConfig"]
        }

        for key in self.data.keys():
            payload[key] = self.data[key]

        # ToDo: Figure out how to include monitor info in with csv data in an easy to understand way
        if self.monitor is not None:
            payload["monitor"] = self.monitor

        return payload

    def getSupervisorTags(self):
        return self.tags

    def getData(self):
        return self.data

    def getTimeStamp(self):
        return self.timeStamp.strftime("%m/%d/%Y-%H:%M:%S")

    def getSupervisorHeaders(self):
        return self.headers
