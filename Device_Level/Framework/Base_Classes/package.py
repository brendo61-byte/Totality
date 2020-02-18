class Package:
    """
    A convenient means of transporting data internal with all needed information to upload to Influx, save as a CSV, or do whatever is needed
    """

    def __init__(self, data, packageType):
        self.data = data
        self.packageType = packageType

    def getPayload(self):  # Payload if for
        payload = {}

        for key in self.data.keys():
            payload[key] = self.data[key]

        return payload

    def getData(self):
        return self.data

    def getPackageType(self):
        return self.packageType
