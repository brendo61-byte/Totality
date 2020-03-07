from Framework.Base_Classes.sensor import Sensor
from Framework.Base_Classes.package import Package
from Framework.Base_Classes.packageTypes import dataPush

import datetime
import time
import Adafruit_ADS1x15
import logging
import traceback


class ADC1115_Pyra(Sensor):

    def __init__(self, gain, channel, samplePeriod, supervisorName, supervisorType, supervisorID, deviceID, globalID,
                 tags, pipe, delay=0):
        self.operational = True
        self.samplePeriod = samplePeriod
        self.supervisorName = supervisorName
        self.supervisorType = supervisorType
        self.supervisorID = supervisorID
        self.deviceID = deviceID
        self.globalID = globalID
        self.tags = tags
        self.pipe = pipe
        self.delay = delay  # Should always be defaulted to 0
        # The above class variables MUST be present for ALL supervisors
        self.gain = gain
        self.channel = channel
        # The two above class variables are only relevant for this type of supervisor

        self.ADC = Adafruit_ADS1x15.ADS1115()
        # ADC1115 Reader Instance

        # Sensors must update tags based on config settings
        self.tags["deviceID"] = self.deviceID
        self.tags["supervisorName"] = self.supervisorName
        self.tags["supervisorID"] = self.supervisorID

        self.info = {  # ALL supervisors should have a self.info dict of this formatting
            "supervisorName": self.supervisorName,
            "supervisorType": self.supervisorType,
            "supervisorID": self.supervisorID,
            "deviceID": self.deviceID,
            "samplePeriod": self.samplePeriod,
            "gain": self.gain,
            "channel": self.channel,
            "customConfig": self.tags["customConfig"]
        }

    def getBitVal(self):
        bitValRaw = 4.096 / (2 ** 15)
        bitVal = bitValRaw / self.gain
        return bitVal

    def getData(self):
        time.sleep(self.delay)
        while self.operational:
            try:
                rawVoltage = self.ADC.read_adc(self.gain, self.channel)
                voltageFloat = rawVoltage * self.getBitVal()

                val = voltageFloat / 0.0001981

                timeStampStr = datetime.datetime.now().strftime("%m/%d/%Y-%H:%M:%S")

                dataRaw = {
                    "data": voltageFloat,
                    "timeStamp": timeStampStr,
                    "readingType": "raw Voltage",
                    "units": "V",
                    "sensorType": self.supervisorType,
                    "sensorID": self.getGlobalID()
                }

                data = {
                    "data": val,
                    "timeStamp": timeStampStr,
                    "readingType": "solar irradiance",
                    "units": "w/m^2",
                    "sensorType": self.supervisorType,
                    "sensorID": self.getGlobalID(),
                }

                self.package(data=data)
                self.package(data=dataRaw)

            except Exception as e:
                logging.info("Unable to read from ADS1115\nException: {}\nTraceBack: {}".format(e, traceback.format_exc()))

            time.sleep(self.samplePeriod)
