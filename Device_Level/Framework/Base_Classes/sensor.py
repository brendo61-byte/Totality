from Framework.Base_Classes.package import Package
from Framework.Base_Classes.packageTypes import dataPush


class Sensor:
    """
    Each supervisor Will inherit from this supervisor class
    The deviceManager will launch a thread with this class and call 'getData'
    Data will be 'packaged' (see package class) and put in a 'dataPipe' (see dataPipe) queue to be shipped off
    """

    def getData(self):
        return

    def getInfo(self):
        return self.info

    def getSensorID(self):
        return self.getSensorID

    def getGlobalID(self):
        return self.globalID

    def updateGlobalID(self, globalID):
        self.globalID = globalID

    def package(self, data):
        package = Package(data=data, packageType=dataPush)
        self.pipe.put(payload=package)
