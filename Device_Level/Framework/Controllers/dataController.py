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

    def __init__(self, pipe, updateInterval, deviceID, dataIngestion_URL, destination, localData, localFileName, headers, localOnly=True):
        """

        :param pipe:
        :param updateInterval:
        :param deviceID:
        :param dataIngestion_URL:
        :param destination:
        :param localData:
        :param localFileName:
        :param headers:
        :param localOnly:
        """
        self.localOnly = localOnly
        self.headers = headers
        self.dataIngestion_URL = dataIngestion_URL
        self.destination = destination
        self.localData = localData
        self.localFileName = localFileName

        self.operational = True
        self.pipe = pipe
        self.updateInterval = updateInterval
        self.deviceID = deviceID

    def starter(self):
        while self.operational:
            logging.debug("Preforming Data-Push")
            allPayloadsInFIFO = []
            noData = True
            while not self.pipe.empty():
                package = self.pipe.get()
                packageType = package.getPackageType()
                packageTypes = {
                    dataPush: self.packager(package=package, packageType=packageType),
                    callBack: self.packager(package=package, packageType=packageType)
                }

                try:
                    assembledPackage = packageTypes.get(packageType)
                    if assembledPackage is not None:
                        allPayloadsInFIFO.append(assembledPackage)
                        if noData:
                            noData = False

                except Exception as e:
                    logging.warning("Unable To Push Package To DB.\nException: {}\nTraceBack: {}".format(e, traceback))

            masterPackage = {"bigLoad": allPayloadsInFIFO}

            self.localCSV(masterPackage=masterPackage["bigLoad"])

            if not self.localOnly:
                if not noData:
                    self.post(package=masterPackage)

            time.sleep(self.updateInterval)

    def post(self, package):
        try:
            print(package)
            requests.post(url=self.dataIngestion_URL, json=package)
        except Exception as e:
            tb = traceback.format_exc()
            logging.warning(f"Unable to push dat to server\nError: {e}\nTraceBack: {tb}")

    def packager(self, package, packageType):

        if packageType is dataPush:
            packageType = "dataPush"

        elif packageType is callBack:
            packageType = "packageYpe"

        else:
            return

        body = {
            "data": {
                "package": package.getData(),
            },
            "deviceID": self.deviceID,
            "packageType": packageType
        }

        return body

    def localCSV(self, masterPackage):
        path = os.path.join(self.localData, self.localFileName)

        try:
            with open(path, 'a') as csvFile:
                writer = csv.DictWriter(csvFile, fieldnames=self.headers)
                # writer.writerow(dataList)

                for package in masterPackage:
                    try:

                        payload = package["data"]["package"]
                        packageType = package["packageType"]

                        if packageType == dataPush:

                            rowDict = {}
                            for headerKey in self.headers:
                                rowDict[headerKey] = (payload[headerKey])

                            writer.writerow(rowDict)

                    except Exception as e:
                        logging.info("Failed to save a Payload Locally.\nError Message: {}\n{}".format(e, traceback.format_exc()))

        except Exception as E:
            logging.warning("Failed To Processes To Save Data Locally.\nError Message: {}\n{}".format(E, traceback.format_exc()))

    def kill(self):
        self.operational = False
