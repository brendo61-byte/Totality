from Device_Level.Framework.Base_Classes.controller import Controller

import os
import csv
import time
import logging
import traceback
import requests

RDURL = "http://localhost:8801/device/dataPush"
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

                # Put data wherever it needs to go
                # This means locally
                self.localCSV(package=package)
                # And to a TS-DB
                self.RDPush(package=package)

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

    def RDPush(self, package):
        body = self.packager(package=package)
        try:
            requests.post(url=RDURL, json=body)
        except Exception as e:
            logging.warning("Unable To Push Package To DB.\nException: {}\nTraceBack: {}".format(e, traceback))

    def packager(self, package):
        body = {
            "data": {
                "package": package.getData(),
                "tags": package.getSupervisorTags(),
                "timeStamp": package.getTimeStamp()
            },
            "deviceID": self.deviceID
        }

        return body

    def kill(self):
        self.operational = False