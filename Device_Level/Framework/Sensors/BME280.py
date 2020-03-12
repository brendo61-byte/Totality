from Framework.Base_Classes.sensor import Sensor
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


class BME280(Sensor):
    def __init__(self, samplePeriod, supervisorName, supervisorType, sensorID, deviceID, pipe, globalID, delay=0):
        self.globalID = globalID
        self.operational = True

        self.samplePeriod = samplePeriod
        self.supervisorName = supervisorName
        self.supervisorType = supervisorType
        self.sensorID = sensorID
        self.deviceID = deviceID
        self.pipe = pipe
        self.delay = delay  # Should always be defaulted to 0

        i2c = busio.I2C(board.SCL, board.SDA)
        self.BME = adafruit_bme280.Adafruit_BME280_I2C(i2c)
        self.BME.sea_level_pressure = 1013.25

        self.info = {  # ALL sensors should have a self.info dict of this formatting
            "supervisorName": self.supervisorName,
            "supervisorType": self.supervisorType,
            "sensorID": self.sensorID,
            "deviceID": self.deviceID,
            "samplePeriod": self.samplePeriod,
        }

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
                    "data": temperatureSigFigs,
                    "timeStamp": timeStampStr,
                    "readingType": "Temperature",
                    "units": "C",
                    "sensorType": self.supervisorType,
                    "sensorID": self.getGlobalID()
                }
                data2 = {
                    "data": humiditySigFigs,
                    "timeStamp": timeStampStr,
                    "readingType": "Humidity",
                    "units": "%",
                    "sensorType": self.supervisorType,
                    "sensorID": self.getGlobalID(),
                }
                data3 = {
                    "data": pressureSigFigs,
                    "timeStamp": timeStampStr,
                    "readingType": "Pressure",
                    "units": "hPa",
                    "sensorType": self.supervisorType,
                    "sensorID": self.getGlobalID(),
                }
                data4 = {
                    "data": altitudeSigFig,
                    "timeStamp": timeStampStr,
                    "readingType": "Elevation",
                    "units": "m",
                    "sensorType": self.supervisorType,
                    "sensorID": self.getGlobalID(),
                }

                self.package(data=data1)
                self.package(data=data2)
                self.package(data=data3)
                self.package(data=data4)

            except Exception as e:
                logging.info("Unable to read from BME280\nException: {}\nTraceBack: {}".format(e, traceback.format_exc()))

            time.sleep(self.samplePeriod)
