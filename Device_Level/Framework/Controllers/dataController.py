from Framework.Base_Classes.controller import Controller
from Framework.Base_Classes.packageTypes import *

import os
import csv
import time
import logging
import traceback
import requests

dataIngestion_URL = "http://localhost:8801/device/dataIngestion"
callBack_URL = "http://localhost:8801/device/callBack"

DESTINATION = "Local_Data/dataRepo.json"
LOCAL_DATA = 'Local_Data/'
LOCAL_FILE_NAME = 'localCSV.csv'


class DataController(Controller):
    """
    This class will save data in the queue to a local CSV file. If other operations are needed, like moving data to an influxDB, then those will be preformed here.
    NOTE: Uploading to an InfluxDB will be implemented later
    """

    def __init__(self, pipe, updateInterval, deviceID, localOnly=False):
        self.operational = True
        self.pipe = pipe
        self.updateInterval = updateInterval
        self.deviceID = deviceID
        self.localOnly = localOnly

    def starter(self):
        # ToDo: Have batch uploads
        while self.operational:
            logging.debug("Preforming Data-Push")
            while not self.pipe.empty():
                package = self.pipe.get()
                packageType = package.getPackageType()

                try:

                    if packageType == dataPush:
                        if not self.localOnly:
                            self.toDataAPI(package=package, packageType="dataPush", URL=dataIngestion_URL)
                        self.localCSV(package=package)

                    if packageType == callBack:
                        if not self.localOnly:
                            self.toDataAPI(package=package, packageType="callBack", URL=callBack_URL)


                except Exception as e:
                    logging.warning("Unable To Push Package To DB.\nException: {}\nTraceBack: {}".format(e, traceback))

            time.sleep(self.updateInterval)

    def toDataAPI(self, package, packageType, URL):
        body = self.packager(package=package, packageType=packageType)
        requests.post(url=URL, json=body)

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
        path = os.path.join(LOCAL_DATA, "SupervisorId_" + str(payload["supervisorID"]), LOCAL_FILE_NAME)
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
            logging.warning(
                "Attribute Error Occurred When Trying To Save Data Locally\nError Message: {}\n{}".format(AE,
                                                                                                          traceback.format_exc()))
        except Exception as E:
            logging.warning("Failed To Save Data Locally.\nError Message: {}\n{}".format(E, traceback.format_exc()))

    def kill(self):
        self.operational = False
