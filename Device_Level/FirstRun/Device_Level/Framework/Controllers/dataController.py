# from Device_Level.Framework.Base_Classes.controller import Controller
# from Device_Level.Framework.Base_Classes.packageTypes import *

from Framework.Base_Classes.controller import Controller
from Framework.Base_Classes.packageTypes import *

import os
import csv
import time
import logging
import traceback
import requests


class DataController(Controller):
    """
    This class will save data in the queue to a local CSV file. If other operations are needed, like moving data to an influxDB, then those will be preformed here.
    NOTE: Uploading to an InfluxDB will be implemented later
    """

    def __init__(self, pipe, updateInterval, deviceID, dataIngestion_URL, callBack_URL, destination, localData, localFileName):
        self.dataIngestion_URL = dataIngestion_URL
        self.callBack_URL = callBack_URL
        self.destination = destination
        self.localData = localData
        self.localFileName = localFileName

        self.operational = True
        self.pipe = pipe
        self.updateInterval = updateInterval
        self.deviceID = deviceID

    def starter(self):
        # ToDo: Have batch uploads
        while self.operational:
            logging.debug("Preforming Data-Push")
            while not self.pipe.empty():
                package = self.pipe.get()
                packageType = package.getPackageType()
                packageTypes = {
                    dataPush: self.post(package=package, packageType="dataPush", URL=self.dataIngestion_URL),
                    callBack: self.post(package=package, packageType="callBack", URL=self.callBack_URL),
                }

                try:
                    packageTypes.get(packageType)
                except KeyError:
                    logging.warning("Invalid package type provided: {}".format(packageType))
                except Exception as e:
                    logging.warning("Unable To Push Package To DB.\nException: {}\nTraceBack: {}".format(e, traceback))

                if packageType == dataPush:
                    self.localCSV(package=package)

            time.sleep(self.updateInterval)

    def post(self, package, packageType, URL):
        time.sleep(0.05)
        requests.post(url=URL, json=self.packager(package=package, packageType=packageType))

    def packager(self, package, packageType):
        body = {
            "data": {
                "package": package.getData(),
                "tags": package.getSupervisorTags(),
                "timeStamp": package.getTimeStamp()
            },
            "deviceID": self.deviceID,
            "packageType": packageType
        }

        return body

    def localCSV(self, package):
        payload = package.getPayload()
        path = os.path.join(self.localData, "supervisorID_" + str(payload["supervisorIDLocal"]), self.localFileName)
        dataList = []

        try:
            for headerKey in package.getSupervisorHeaders():
                dataList.append(payload[headerKey])

            with open(path, 'a') as csvFile:
                writer = csv.writer(csvFile)
                writer.writerow(dataList)

        except FileNotFoundError as FNFE:
            logging.warning(
                "File Not Error Occurred When Trying To Save Data Locally.\nError Message: {}\n{}".format(FNFE,
                                                                                                          traceback.format_exc()))
        except AttributeError as AE:
            logging.warning("Attribute Error Occurred When Trying To Save Data Locally\nError Message: {}\n{}".format(AE,
                                                                                                                      traceback.format_exc()))
        except Exception as E:
            logging.warning("Failed To Save Data Locally.\nError Message: {}\n{}".format(E, traceback.format_exc()))

    def kill(self):
        self.operational = False
