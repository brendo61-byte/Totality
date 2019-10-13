from Device_Level.Framework.Base_Classes.exceptionClasses import *
from threading import Thread
from pathlib import Path

import json
import csv
import os
import importlib
import traceback
import logging

CONFIG_PATH = 'Framework/Base_Supervisor_Config_Files'
supervisor_PATH = 'Framework.Supervisors.'
LOCAL_DATA = 'Local_Data/'

"""
'makesupervisor' can be called with three args: supervisorType - this is the type of supervisor that will be created, supervisorID - the unique ID that is assigned to the supervisor, 
and configAdjust - this can be left as None or if custom configuration is desired then those arguments can be passed in. This will return the supervisor created

'launcher' takes the same args as 'makesupervisor' but the difference is that 'launcher' will start the thread that runs the supervisor. Note also that launcher as the
arg 'restart'. If a user wanted to update the configuration then restart will be set as True, and the corresponding supervisorID thread will be killed and a new supervisor 
will be launched under the same ID

'dirSetUp' will create a directory for a supervisor in 'Local_Data' if a directory does not already exist

'getConfig' loads the json file with the base configuration for that supervisorType. 
NOTE: if the corresponding supervisor configuration file does not have the exact same name as the passed in supervisorType then a FileNotFoundError will be thrown. 
NOTE: if the configure file as extra variables or falsely named variables then a TypeError or a KeyError will be thrown
SUPER NOTE: it is therefor MEGA important to ensure that the base config for a supervisor Type works

'configAdjsut' will overwrite key/vals from the base-config. NOTE: If extra key/vals are used then this will throw a TypeError

'killsupervisor' does exactly what you think it does. All supervisors will have a variable called 'operational' that is set to True. Supervisors are
killed by setting operational to false so the thread will simply run out (see Supervisors)

'getTags' and 'getInfo' need the supervisorID and will return what their respective names are

'getAllLocalsupervisors' will return a dict with keys of all supervisor IDs and vals of the supervisor info. If there are no local supervisors will return an empty dict

'getsupervisorInstance' takes an arg of 'supervisorID' and will return an object that is the instance of that supervisorID

NOTE: There are no try/except blocks so it is the responsibly of whatever calls these methods to use try catch (should include TypeError, KeyError, and 
FileNotFoundError)
"""


# Todo: How to monitor and handle when a thread dies

class deviceManager:
    def __init__(self, pipe, deviceID, test, threadLimit, configPath):
        self.MasterSupervisorDict = {}
        self.NAT = {}
        self.datapipe = pipe
        self.configPath = configPath
        self.deviceID = deviceID
        self.threadLimit = threadLimit
        self.storageSet()
        if test == "True":
            self.storageReset()

    def getNAT(self):
        return self.NAT

    def updateNAT(self, key, val):
        self.NAT[key] = val

    def storageSet(self):
        if not os.path.isdir("Local_Data"):
            logging.info("No Local Data directory found. Creating new directory now.")
            os.system("mkdir Local_Data")

    def storageReset(self):
        os.system("rm -r Local_Data")
        os.system("mkdir Local_Data")

    def getSupervisorID(self):
        return len(self.MasterSupervisorDict) + 1

    def launcher(self, supervisorType, supervisorID=None, globalID=0, customConfig=None, restart=False, callBack=False):
        if callBack:
            globalID = supervisorID
            supervisorID = self.NAT[globalID]

        if supervisorID == None or supervisorID == 0:
            supervisorID = self.getSupervisorID()

        if len(self.MasterSupervisorDict) >= self.threadLimit:
            SupervisorThreadLimit()
            # ToDo: Test This --- exception CLass updated --- deviceConfig --- Update README

        supervisor = self.makeSupervisor(supervisorType=supervisorType, supervisorID=supervisorID,
                                         customConfig=customConfig, restart=restart, globalID=globalID)
        self.MasterSupervisorDict[supervisorID] = supervisor

        if globalID != 0:
            print("HERE")
            self.NAT[globalID] = supervisorID
            self.updateSupervisorConfGlobalID(globalID=globalID, supervisorID=supervisorID)

        self.dirSetUp(supervisorID=supervisorID, supervisor=supervisor)

        thread = Thread(target=supervisor.getData, name=supervisorID)

        if callBack:
            self.addSupervisorToConf(supervisorType=supervisorType, supervisorID=supervisorID,
                                     customConfig=customConfig, globalID=globalID)

        thread.start()

        logging.info("New supervisor Spawned. supervisor Info: {}\n".format(
            json.dumps(supervisor.getSupervisorInfo(), indent=4, sort_keys=True)))

    def updateSupervisorConfGlobalID(self, globalID, supervisorID):
        raw = open(self.configPath, "r")
        confRaw = json.load(raw)
        conf = confRaw
        raw.close()

        with open(self.configPath, "r+") as confFile:
            tempconf = confRaw["launcher"]["args"]["supervisorList"]
            temp = tempconf
            tempSupervisor = True

            for entry in temp:
                if entry.get("supervisorID") == supervisorID:
                    tempconf.remove(entry)
                    entry["globalID"] = globalID
                    tempconf.append(entry)
                    tempSupervisor = False
                    break

            if not tempSupervisor:
                conf["launcher"]["args"]["supervisorList"] = tempconf
                try:
                    json.dump(conf, confFile, indent=4)
                    # ToDo: How to deal with failed updated conf file?
                except Exception as e:
                    logging.warning(
                        "Unable to update deviceConfig.json file. Resetting to previous state.\nError: {}\nTraceBack: {}".format(
                            e, traceback.format_exc()))
                    try:
                        json.dump(confRaw, confFile, indent=4)
                        return ConfigurationUpdateFailure
                    except Exception as e:
                        logging.critical(
                            "Unable to revert deviceConfig.json to previous state. It is now broken :(\nError: {}\nTraceBack: {}".format(
                                e, traceback.format_exc()))
                        return ConfigurationBackupFailure

    def addSupervisorToConf(self, supervisorType, supervisorID, globalID, customConfig=None):
        raw = open(self.configPath, "r")
        confRaw = json.load(raw)
        raw.close()

        with open(self.configPath, "r+") as confFile:
            conf = confRaw
            try:
                body = {}
                body["supervisorType"] = supervisorType
                body["supervisorID"] = supervisorID
                body["customConfig"] = customConfig
                body["globalID"] = globalID

                supervisorList = conf["launcher"]["args"]["supervisorList"]
                supervisorList.append(body)
                conf["launcher"]["args"]["supervisorList"] = supervisorList

                json.dump(conf, confFile, indent=4)
                # ToDo: How to deal with failed updated conf file?
            except Exception as e:
                logging.warning(
                    "Unable to update deviceConfig.json file. Resetting to previous state.\nError: {}\nTraceBack: {}".format(
                        e, traceback.format_exc()))
                try:
                    json.dump(confRaw, confFile, indent=4)
                    return ConfigurationUpdateFailure
                except Exception as e:
                    logging.critical(
                        "Unable to revert deviceConfig.json to previous state. It is now broken :(\nError: {}\nTraceBack: {}".format(
                            e, traceback.format_exc()))
                    return ConfigurationBackupFailure

    def removeSupervisorFromConf(self, globalID):
        raw = open(self.configPath, "r")
        confRaw = json.load(raw)
        raw.close()

        with open(self.configPath, "r+") as confFile:
            conf = confRaw
            try:

                supervisorList = conf["launcher"]["args"]["supervisorList"]
                tempList = supervisorList

                for entry in tempList:
                    if entry.get("globalID") == globalID:
                        supervisorList.remove(entry)

                conf["launcher"]["args"]["supervisorList"] = supervisorList

                json.dump(conf, confFile, indent=4)
                # ToDo: How to deal with failed updated conf file?
            except Exception as e:
                logging.warning(
                    "Unable to update deviceConfig.json file. Resetting to previous state.\nError: {}\nTraceBack: {}".format(
                        e, traceback.format_exc()))

                try:
                    json.dump(confRaw, confFile, indent=4)
                    return ConfigurationUpdateFailure

                except Exception as e:
                    logging.critical(
                        "Unable to revert deviceConfig.json to previous state. It is now broken :(\nError: {}\nTraceBack: {}".format(
                            e, traceback.format_exc()))

                    return ConfigurationBackupFailure

    def makeSupervisor(self, supervisorType, supervisorID, globalID, customConfig, restart):
        config = self.getConfig(supervisorType=supervisorType)
        config['supervisorID'] = supervisorID
        config["globalID"] = globalID

        if customConfig != 'None' and bool(customConfig):
            config['tags']['customConfig'] = 'True'
            config = self.customConfiguration(baseConfig=config, customConfig=customConfig)

        supervisorClass = self.getSupervisorClass(supervisorType=supervisorType)

        if restart:
            config["delay"] = self.getSupervisorInstance(supervisorID=supervisorID).getSupervisorInfo()["samplePeriod"]
            self.killSupervisor(supervisorID=supervisorID)

        else:
            for ID in self.MasterSupervisorDict:
                supervisor = self.getSupervisorInstance(supervisorID=ID)
                if supervisor.getSupervisorID() == supervisorID:
                    raise SupervisorUniqueError

        supervisor = supervisorClass(**config, pipe=self.datapipe, deviceID=self.deviceID)

        return supervisor

    def dirSetUp(self, supervisorID, supervisor):
        if not Path(os.path.join(LOCAL_DATA, "supervisorID_" + str(supervisorID))).is_dir():
            pathDir = "{}supervisorID_{}".format(LOCAL_DATA, supervisorID)
            os.system("mkdir {}".format(pathDir))
            csvPath = os.path.join(pathDir, "localCSV.csv")
            with open(csvPath, 'a') as csvFile:
                writer = csv.writer(csvFile, delimiter=',')
                writer.writerow(supervisor.getSupervisorHeaders())

    def getConfig(self, supervisorType):
        with open(os.path.join(CONFIG_PATH, supervisorType + ".json")) as configData:
            config = json.load(configData)
            return config

    def customConfiguration(self, baseConfig, customConfig):
        for key in customConfig.keys():
            baseConfig[key] = customConfig[key]

        return baseConfig

    def getSupervisorClass(self, supervisorType):
        moduleName = supervisor_PATH + supervisorType
        module = importlib.import_module(moduleName)
        supervisorClass = getattr(module, supervisorType)
        return supervisorClass

    def killSupervisor(self, supervisorID, callBack=False):
        supervisor = self.getSupervisorInstance(supervisorID=supervisorID)
        supervisor.operational = False
        del self.MasterSupervisorDict[supervisorID]

        logging.info("supervisor Killed. Dead supervisorID: {}".format(supervisorID))

    def getSupervisorTags(self, supervisorID, callBack=False):
        supervisor = self.MasterSupervisorDict[supervisorID]
        return supervisor.getSupervisorTags()

    def getSupervisorInfo(self, supervisorID, callBack=False):
        supervisor = self.MasterSupervisorDict[supervisorID]
        return supervisor.getSupervisorInfo()

    def getAllLocalSupervisors(self, callBack=False):
        allInfo = {}

        for ID in self.MasterSupervisorDict.keys():
            supervisor = self.MasterSupervisorDict[ID]

            allInfo[supervisor.supervisorID] = supervisor.getSupervisorInfo()

        return allInfo

    def getSupervisorInstance(self, supervisorID):
        return self.MasterSupervisorDict[supervisorID]
