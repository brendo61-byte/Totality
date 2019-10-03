from Device_Level.Framework.Base_Classes.exceptionClasses import *
from threading import Thread
from pathlib import Path

import json
import csv
import os
import importlib
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
    def __init__(self, pipe, deviceID, test, threadLimit):
        self.MasterSupervisorDict = {}
        self.datapipe = pipe
        self.deviceID = deviceID
        self.threadLimit = threadLimit
        if test == "True":
            os.system("rm -r Local_Data")
            os.system("mkdir Local_Data")

    def launcher(self, supervisorType, supervisorID, customConfig=None, restart=False, callBack=False):
        if len(self.MasterSupervisorDict) >= self.threadLimit:
            SupervisorThreadLimit()
            # ToDo: Test This --- exception CLass updated --- deviceConfig --- Update README

        supervisor = self.makeSupervisor(supervisorType=supervisorType, supervisorID=supervisorID,
                                         customConfig=customConfig, restart=restart)
        self.MasterSupervisorDict[supervisorID] = supervisor
        self.dirSetUp(supervisorID=supervisorID, supervisor=supervisor)

        thread = Thread(target=supervisor.getData, name=supervisorID)
        thread.start()

        logging.info("New supervisor Spawned. supervisor Info: {}\n".format(
            json.dumps(supervisor.getSupervisorInfo(), indent=4, sort_keys=True)))

    def makeSupervisor(self, supervisorType, supervisorID, customConfig, restart):
        config = self.getConfig(supervisorType=supervisorType)
        config['supervisorID'] = supervisorID

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
            with open(csvPath, 'w') as csvFile:
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

    # ToDo: Want a way to stop a supervisor AND to kill one
    # This killing means that it is removed from the start-up config
    # Stopping, as the name implies only stops it
    # A restart command could then start that supervisor back up
    def killSupervisor(self, supervisorID, callBack=False):
        supervisor = self.getSupervisorInstance(supervisorID=supervisorID)
        supervisor.operational = False
        del self.MasterSupervisorDict[supervisorID]

        logging.info("supervisor Killed. Dead supervisorID: {}".format(supervisorID))

    def getSupervisorTags(self, supervisorID, callBack):
        supervisor = self.MasterSupervisorDict[supervisorID]
        return supervisor.getSupervisorTags()

    def getSupervisorInfo(self, supervisorID, callBack):
        supervisor = self.MasterSupervisorDict[supervisorID]
        return supervisor.getSupervisorInfo()

    def getAllLocalSupervisors(self, callBack):
        allInfo = {}

        for ID in self.MasterSupervisorDict.keys():
            supervisor = self.MasterSupervisorDict[ID]

            allInfo[supervisor.supervisorID] = supervisor.getSupervisorInfo()

        return allInfo

    def getSupervisorInstance(self, supervisorID):
        print("Supervisor ID: {}\nMASTER LIST: {}".format(supervisorID, self.MasterSupervisorDict))
        return self.MasterSupervisorDict[supervisorID]
