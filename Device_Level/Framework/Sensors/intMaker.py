# from Device_Level.Framework.Base_Classes.sensor import sensor
# from Device_Level.Framework.Base_Classes.package import Package
# from Device_Level.Framework.Base_Classes.packageTypes import dataPush

from Framework.Base_Classes.sensor import Sensor

import random
import datetime
import time


class intMaker(Sensor):
    """
    Note: that the class name is EXACTLY the same of the file its in and the same as its corresponding config file -- class 'intMaker' in file 'intMaker.py' with
    'intMaker.json'

    Note: The base config for EVERY sensor will contain all information besides sensor ID - This assumes that the sensor will be working in an isolated
    local environment - so if that is not the case the fields 'deviceName' and 'deviceID' should be filled out too. See deviceManger in Framework.

    Note: EVERY sensor MUST have a self.info that contains all configuration data.

    --- THE BELOW ARGS ARE UNIVERSAL AND ALL sensorS WILL NEED THEM ---
    samplePeriod: Sleep time between data readings
    sensorName: The Name Of The sensor (While The ID Defines The Unique Identity Of The Totality 'deviceName' Is For Human Use)
    sensorType: Names The Type Of sensor
    sensorID: The ID Of The sensor -- this is a local refrence only
    globalID: The ID of sensor as dedicated by the database.
    deviceID: ID to know device
    tags: A json of descriptive tags Defining The sensor
    pipe: An object of the dataPipe class. All sensors will share the same pipe object -- meaning all sensors will put data on the same queue
    delay: If a sensor is 'restarted' then the new sensor can the old sensor cannot talk to a device at the same time. To avoid this the new sensor will wait a full
    sample period of the old sensor to ensure that it has died. Defaulted to zero

    ______________________________________________________________________________________________________________________________________________________________

    lowEnd: The min integer that will be randomly generated
    highEnd: The (exclusive) max integer that will be randomly generated
    """

    def __init__(self, lowEnd, highEnd, samplePeriod, sensorName, sensorType, sensorID, deviceID, globalID, pipe, delay=0):
        self.operational = True
        self.samplePeriod = samplePeriod
        self.sensorName = sensorName
        self.sensorType = sensorType
        self.sensorID = sensorID
        self.deviceID = deviceID
        self.globalID = globalID
        self.pipe = pipe
        self.delay = delay  # Should always be defaulted to 0
        # The above class variables MUST be present for ALL sensors
        self.lowEnd = lowEnd
        self.highEnd = highEnd
        # The two above class variables are only relevant for this type of sensor

        self.info = {  # ALL sensors should have a self.info dict of this formatting
            "sensorName": self.sensorName,
            "sensorType": self.sensorType,
            "sensorID": self.sensorID,
            "deviceID": self.deviceID,
            "samplePeriod": self.samplePeriod,
            "lowEndInt": self.lowEnd,
            "highEndInt": self.highEnd
        }

    def getData(self):
        time.sleep(self.delay)
        while self.operational:
            someInt = random.randint(self.lowEnd, self.highEnd)  # Replace this later on with a Fake Totality

            timeStamp = datetime.datetime.now()
            timeStampStr = timeStamp.strftime("%m/%d/%Y-%H:%M:%S")

            # Data should be in a dict form with key/val being "name of sample"/"value of sample" -- i.e. {"Voltage":12.345, "temp(C)":67.89}
            data1 = {
                "data": someInt,  # the data you are sending - needs to be a int or float
                "timeStamp": timeStampStr,  # a time stamp of the data - copy this code here - needs to be a str
                "dataType": "randomInt",  # the type of data - i.e. Voltage, Pressure, Humidity, etc - needs to be a string
                "units": "n/a",  # the units of the data - i.e. mV, PSI, %, etc - needs to be a string
                "sensorType": self.sensorType,  # the type of sensor it is - needs to be a string
                "sensorID": self.getGlobalID()  # the global ID of the sensor - needs to be an int
            }

            data2 = {
                "data": someInt,  # the data you are sending - needs to be a int or float
                "timeStamp": timeStampStr,  # a time stamp of the data - copy this code here - needs to be a str
                "dataType": "randomInt",  # the type of data - i.e. Voltage, Pressure, Humidity, etc - needs to be a string
                "units": "n/a",  # the units of the data - i.e. mV, PSI, %, etc - needs to be a string
                "sensorType": self.sensorType,  # the type of sensor it is - needs to be a string
                "sensorID": self.getGlobalID()  # the global ID of the sensor - needs to be an int
            }

            self.package(data=data1, timeStamp=timeStamp)
            self.package(data=data2, timeStamp=timeStamp)

            time.sleep(self.samplePeriod)
