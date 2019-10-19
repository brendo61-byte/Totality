from Device_Level.Framework.Base_Classes.controller import Controller
from Device_Level.Framework.Base_Classes.packageTypes import *

import os
import csv
import time
import logging
import traceback
import requests

RDURL = "http://localhost:8801/device/dataIngestion"
DESTINATION = "Local_Data/dataRepo.json"
LOCAL_DATA = 'Local_Data/'
LOCAL_FILE_NAME = 'localCSV.csv'


class DataController(Controller):
    """
    This class will save data in the queue to a local CSV file. If other operations are needed, like moving data to an influxDB, then those will be preformed here.
    NOTE: Uploading to an InfluxDB will be implemented later
    """

    def __init__(self, pipe, updateInterval, DM, deviceID):
        self.operational = True
        self.pipe = pipe
        self.updateInterval = updateInterval
        self.DM = DM
        self.deviceID = deviceID

    def starter(self):
        while self.operational:
            logging.debug("Preforming Data-Push")
            while not self.pipe.empty():
                package = self.pipe.get()
                packageType = package.getPackageType()
                packageTypes = {
                    dataPush: self.packager(package=package, packageType="dataPush"),
                    callBack: self.packager(package=package, packageType="callBack"),
                    registerSupervisor: self.packager(package=package, packageType="requestGlobalID")
                }

                try:
                    body = packageTypes.get(packageType)
                    self.post(body=body)

                except:
                    logging.warning("Invalid package type provided: {}".format(packageType))

                if packageType == dataPush:
                    self.localCSV(package=package)

            time.sleep(self.updateInterval)

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
            logging.warning("Attribute Error Occured When Trying To Save Data Locally\nError Message: {}\n{}".format(AE,
                                                                                                                     traceback.format_exc()))
        except Exception as E:
            logging.warning("Failed To Save Data Locally.\nError Message: {}\n{}".format(E, traceback.format_exc()))

    def post(self, body):
        try:
            requests.post(url=RDURL, json=body)
        except Exception as e:
            logging.warning("Unable To Push Package To DB.\nException: {}\nTraceBack: {}".format(e, traceback))

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

    def kill(self):
        self.operational = False
