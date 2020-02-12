from Framework.Base_Classes.supervisor import Supervisor
from Framework.Base_Classes.package import Package
from Framework.Base_Classes.packageTypes import dataPush

import random
import datetime
import time
import adafruit_bme280
import logging
import traceback
import board
import busio


class BME280(Supervisor):
    """
    Note: that the class name is EXACTLY the same of the file its in and the same as its corresponding config file -- class 'intMaker' in file 'intMaker.py' with
    'intMaker.json'

    Note: The base config for EVERY supervisor will contain all information besides supervisor ID - This assumes that the supervisor will be working in an isolated
    local environment - so if that is not the case the fields 'deviceName' and 'deviceID' should be filled out too. See deviceManger in Framework.

    Note: EVERY supervisor MUST have a self.info that contains all configuration data.

    --- THE BELOW ARGS ARE UNIVERSAL AND ALL supervisorS WILL NEED THEM ---
    samplePeriod: Sleep time between data readings
    supervisorName: The Name Of The supervisor (While The ID Defines The Unique Identity Of The Totality 'deviceName' Is For Human Use)
    supervisorType: Names The Type Of supervisor
    supervisorID: The ID Of The supervisor
    deviceID: ID to know device
    tags: A json of descriptive tags Defining The supervisor
    pipe: An object of the dataPipe class. All supervisors will share the same pipe object -- meaning all supervisors will put data on the same queue
    delay: If a supervisor is 'restarted' then the new supervisor can the old supervisor cannot talk to a device at the same time. To avoid this the new supervisor will wait a full
    sample period of the old supervisor to ensure that it has died. Defaulted to zero

    ______________________________________________________________________________________________________________________________________________________________

    lowEnd: The min integer that will be randomly generated
    highEnd: The (exclusive) max integer that will be randomly generated
    """

    def __init__(self, samplePeriod, supervisorName, supervisorType, supervisorID, deviceID, tags, pipe, globalID, delay=0):
        self.globalID = globalID
        self.operational = True

        self.samplePeriod = samplePeriod
        self.supervisorName = supervisorName
        self.supervisorType = supervisorType
        self.supervisorID = supervisorID
        self.deviceID = deviceID
        self.tags = tags
        self.pipe = pipe
        self.delay = delay  # Should always be defaulted to 0
        # The above class variables MUST be present for ALL supervisors
        # self.lowEnd = lowEnd
        # self.highEnd = highEnd
        # The two above class variables are only relevant for this type of supervisor

        i2c = busio.I2C(board.SCL, board.SDA)
        self.BME = adafruit_bme280.Adafruit_BME280_I2C(i2c)
        self.BME.sea_level_pressure = 1013.25

        # Supervisors must update tags based on config settings
        self.tags["deviceID"] = self.deviceID
        self.tags["supervisorName"] = self.supervisorName
        self.tags["supervisorID"] = self.supervisorID

        self.info = {  # ALL supervisors should have a self.info dict of this formatting
            "supervisorName": self.supervisorName,
            "supervisorType": self.supervisorType,
            "supervisorID": self.supervisorID,
            "deviceID": self.deviceID,
            "samplePeriod": self.samplePeriod,
            # "lowEndInt": self.lowEnd,
            # "highEndInt": self.highEnd,
            "customConfig": self.tags["customConfig"]
        }

        self.headers = ["data", "timeStamp", "dataType", "units", "sensorType", "supervisorID"]
        """
                ALL Supervisors need a headers list
        Must have the values being collected -- in this case 'someInt' --- followed by supervisorID, supervisorName, supervisorOwner, customConfig, TimeStamp
        Order does not matter but let's set a standard example of having collection fields, 'someInt' followed by supervisorID, supervisorName etc (see above) and ending
        with a timeStamp
        These are the headers to the CSV file that will store data for this supervisor instance
        Program assumes ALL timestamps will be in UTC time -- do this too b/c timezones can be a pain and the UI can adjust this value easily
        """

        # HERE

    def getData(self):
        time.sleep(self.delay)
        while self.operational:
            try:
                temperatureFloat = self.BME.temperature  # does this work???
                humidityFloat = self.BME.humidity
                pressureFloat = self.BME.pressure
                altitudeFloat = self.BME.altitude

                temperatureSigFigs = round(temperatureFloat, 2)
                humiditySigFigs = round(humidityFloat, 2)
                pressureSigFigs = round(pressureFloat, 2)
                altitudeSigFig = round(altitudeFloat, 2)

                timeStamp = datetime.datetime.utcnow()
                timeStampStr = timeStamp.strftime("%m/%d/%Y-%H:%M:%S")

                data1 = {
                    "data": temperatureSigFigs,  # the data you are sending - needs to be a int or float
                    "timeStamp": timeStampStr,  # a time stamp of the data - copy this code here - needs to be a str
                    "dataType": "Temperature", # the type of data - i.e. Voltage, Pressure, Humidity, etc - needs to be a string
                    "units": "C",  # the units of the data - i.e. mV, PSI, %, etc - needs to be a string
                    "sensorType": self.supervisorType,  # the type of supervisor it is - needs to be a string
                    "supervisorID": self.getGlobalID(),  # the global ID of the supervisor - needs to be an int
                    "supervisorIDLocal": self.getSupervisorID()
                }
                data2 = {
                    "data": humiditySigFigs,
                    "timeStamp": timeStampStr,
                    "dataType": "Humidity",
                    "units": "%",
                    "sensorType": self.supervisorType,
                    "supervisorID": self.getGlobalID(),
                    "supervisorIDLocal": self.getSupervisorID()
                }
                data3 = {
                    "data": pressureSigFigs,
                    "timeStamp": timeStampStr,
                    "dataType": "Pressure",
                    "units": "hPa",
                    "sensorType": self.supervisorType,
                    "supervisorID": self.getGlobalID(),
                    "supervisorIDLocal": self.getSupervisorID()
                }
                data4 = {
                    "data": altitudeSigFig,
                    "timeStamp": timeStampStr,
                    "dataType": "Elevation",
                    "units": "m",
                    "sensorType": self.supervisorType,
                    "supervisorID": self.getGlobalID(),
                    "supervisorIDLocal": self.getSupervisorID()
                }

                self.package(data=data1, timeStamp=timeStamp)
                self.package(data=data2, timeStamp=timeStamp)
                self.package(data=data3, timeStamp=timeStamp)
                self.package(data=data4, timeStamp=timeStamp)

            except Exception as e:
                logging.info("Unable to read from BME280\nException: {}\nTraceBack: {}".format(e, traceback.format_exc()))

            time.sleep(self.samplePeriod)

    def getSupervisorHeaders(self):
        return self.headers

    def getSupervisorTags(self):
        return self.tags

    def getSupervisorInfo(self):
        return self.info

    def getSupervisorID(self):
        return self.supervisorID

    def getGlobalID(self):
        return self.globalID

    def updateGlobalID(self, globalID):
        self.globalID = globalID

    def monitor(self, data):
        # ToDo: Figure out how to implement monitor
        """
        In future this method will be able to evaluate data that was just collected to see if something but be done.
        Ex: Check battery voltage to see if it's low and the system needs to be turned off
        Ex: Check if a reading is out of a set threshold and someone/thing needs to be notified
        That sort of stuff will go here
        """
        return None

    def package(self, data, timeStamp):
        package = Package(data=data, tags=self.tags, timeStamp=timeStamp, monitorResponse=self.monitor(data=data),
                          headers=self.headers, packageType=dataPush)
        self.pipe.put(payload=package)
