from Device_Level.Framework.Base_Classes.controller import Controller

import requests
import time
import logging
import json
import traceback

# ToDo: Make this an env variable --- This will be done during/around deployment
CommandServerEndPoint = 'http://localhost:8802/device/commands/getCommands'


class CommandController(Controller):
    """
    In future this class will be able to talk to a cloud once a 'heartBeatInterval' to see if new commands need to be run on the device.
    """

    def __init__(self, heartBeatInterval, deviceID, DM):
        self.operational = True
        self.heartBeatInterval = heartBeatInterval
        self.deviceID = deviceID
        self.DM = DM

    def starter(self):
        while self.operational:
            commands = self.pullCommands()
            if commands is not None:
                if bool(commands.get("commands")):
                    logging.info("New Commands Received.\nCommands: {}".format(json.dumps(commands["commands"], indent=4)))
                    self.commandParser(commands=commands)
                else:
                    logging.debug("No New Commands To Execute")

            time.sleep(self.heartBeatInterval)

    def pullCommands(self):
        try:
            commands = requests.post(CommandServerEndPoint, json={"deviceID": self.deviceID})
            jsonCommands = commands.json()
            if commands.status_code != 200:
                logging.warning(
                    "Connection Error To Command Server. Response Code: {}\nJson return: {}\nFull text: {}".format(
                        commands.status_code,
                        json.dumps(obj=commands.json()),
                        commands.text))
            else:
                logging.debug("'Get' From Command Server Returned Status 200 Okay")

            return jsonCommands

        except Exception as e:
            logging.warning(
                "Critical Error Has Occurred While Trying To Connect To Command Server. Error Message: {}\n{}".format(e,
                                                                                                                      traceback.format_exc()))
            return None

    def commandParser(self, commands):
        for command in commands.get("commands"):
            if self.executeCommands(command=command):
                pass  # Create new success package
            else:
                pass  # Create new fail package

    def createSuccessPackage(self):
        pass

    def createFailPackage(self):
        pass

    def executeCommands(self, command):
        try:
            commandType = command["commandType"]
            body = command["body"]
            commandID = command["commandID"]
            """
            Hey Wes!
            
            Use this commandID as the reference for what command ID you are trying to execute
            
            This should be passed as a value into the data controller -- though a package of type callBack
            
            """
            callBack = self.checkCallBack(callBackStr=command["callBack"])
            if callBack:
                print("HERE")
                body["callBack"] = True

            try:
                print("Command: {}".format(command))
                methodToCall = getattr(self.DM, commandType)
                methodToCall(**body)

                logging.info(
                    "New Command Passed To Manger\nCommand Type: {}\nCall Back {}".format(commandType, callBack))

                return True

            except Exception as e:
                logging.warning(
                    "Failed To Pass New Command To Manager\nCommand Type: {}\ncallBack: {}\nBody: {}\nError Message: {}\n{}".format(
                        commandType,
                        callBack, body,
                        e,
                        traceback.format_exc()))
        except KeyError as KE:
            logging.warning(
                "KeyError Decoding Command. Command Failed\n Error Message: {}\nFull Command Json: {}\n{}".format(
                    KE, command,
                    traceback.format_exc()))

        except Exception as e:
            logging.warning(
                "Exception Decoding Command. Command Failed\nError Message: {}\nFull Json Command: {}\n{}".format(e,
                                                                                                                  command,
                                                                                                                  traceback.format_exc()))

    def kill(self):
        return

    def checkCallBack(self, callBackStr):
        if callBackStr == "True":
            return True
        else:
            return False
