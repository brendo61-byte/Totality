# from Device_Level.Framework.Base_Classes.controller import Controller
# from Device_Level.Framework.Base_Classes.packageTypes import *

from Framework.Base_Classes.controller import Controller
from Framework.Base_Classes.packageTypes import *

import requests
import logging
import traceback
import time


class ManagementController(Controller):
    def __init__(self, pipe, updateInterval, deviceID, DM, registrationURL):
        self.registrationURL = registrationURL
        self.pipe = pipe
        self.updateInterval = updateInterval
        self.deviceID = deviceID
        self.DM = DM
        self.operational = True

    def starter(self):
        while self.operational:
            # ToDo: Should these packets be logged --- well yes but how and where? IS work?
            while not self.pipe.empty():
                package = self.pipe.get()
                packageType = package.getPackageType()

                packageTypes = {
                    registerSensor: self.registration(package=package, packageType="requestGlobalID", url=self.registrationURL)
                }

                try:
                    response = packageTypes[packageType]
                    if response.status_code == 200:
                        logging.debug("Management package returned status 200")
                        command = response.json().get("command")
                        if bool(command):
                            logging.debug("Attempting to execute management package")
                            self.commandExecution(command=command)
                        else:
                            logging.debug("No commands returned for management package")
                    else:
                        logging.warning("Non 200 return on management Controller. Info: {}".format(response.text))

                except Exception as e:
                    logging.warning(
                        "Unable To Push Management Package.\nException: {}\nTraceBack: {}".format(e, traceback))

            time.sleep(self.updateInterval)

    def commandExecution(self, command):
        try:
            commandType = command["commandType"]
            body = command["body"]

            try:
                methodToCall = getattr(self.DM, commandType)
                methodToCall(**body)

                logging.info(
                    "New Command Passed To Manger\nCommand Type: {}".format(commandType))

                return True

            except Exception as e:
                logging.warning(
                    "Failed To Pass New Command To Manager\nCommand Type: {}\ncallBack: {}\nBody: {}\nError Message: {}\n{}".format(
                        commandType,
                        callBack, body,
                        e,
                        traceback.format_exc()))

        except Exception as e:
            logging.warning(
                "Exception Decoding Command. Command Failed\nError Message: {}\nFull Json Command: {}\n{}".format(e,
                                                                                                                  command,
                                                                                                                  traceback.format_exc()))

    def registration(self, package, packageType, url):
        payload = self.packager(package=package, packageType=packageType)
        print(payload)
        return self.post(body=payload, url=url)

    def post(self, body, url):
        return requests.post(url=url, json=body)

    def packager(self, package, packageType):
        body = {
            "data": {
                "package": package.getData(),
            },
            "deviceID": self.deviceID,
            "packageType": packageType
        }

        return body

    def kill(self):
        self.operational = False
