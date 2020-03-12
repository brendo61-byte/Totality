# from Device_Level.Framework.Base_Classes.exceptionClasses import *
# from Device_Level.Framework.Base_Classes.package import Package
# from Device_Level.Framework.Base_Classes.packageTypes import registersensor

from Framework.Base_Classes.exceptionClasses import *
from Framework.Base_Classes.package import Package
from Framework.Base_Classes.packageTypes import registerSensor

from threading import Thread
from pathlib import Path
import json
import csv
import os
import importlib
import traceback
import logging
import datetime

CONFIG_PATH = 'Framework/Base_Sensor_Config_Files'
sensor_PATH = 'Framework.Sensors.'
LOCAL_DATA = 'Local_Data/'

"""
'makesensor' can be called with three args: sensorType - this is the type of sensor that will be created, sensorID - the unique ID that is assigned to the sensor, 
and configAdjust - this can be left as None or if custom configuration is desired then those arguments can be passed in. This will return the sensor created

'launcher' takes the same args as 'makesensor' but the difference is that 'launcher' will start the thread that runs the sensor. Note also that launcher as the
arg 'restart'. If a user wanted to update the configuration then restart will be set as True, and the corresponding sensorID thread will be killed and a new sensor 
will be launched under the same ID

'dirSetUp' will create a directory for a sensor in 'Local_Data' if a directory does not already exist

'getConfig' loads the json file with the base configuration for that sensorType. 
NOTE: if the corresponding sensor configuration file does not have the exact same name as the passed in sensorType then a FileNotFoundError will be thrown. 
NOTE: if the configure file as extra variables or falsely named variables then a TypeError or a KeyError will be thrown
SUPER NOTE: it is therefor MEGA important to ensure that the base config for a sensor Type works

'configAdjsut' will overwrite key/vals from the base-config. NOTE: If extra key/vals are used then this will throw a TypeError

'killsensor' does exactly what you think it does. All sensors will have a variable called 'operational' that is set to True. Sensors are
killed by setting operational to false so the thread will simply run out (see Sensors)

'getTags' and 'getInfo' need the sensorID and will return what their respective names are

'getAllLocalsensors' will return a dict with keys of all sensor IDs and vals of the sensor info. If there are no local sensors will return an empty dict

'getsensorInstance' takes an arg of 'sensorID' and will return an object that is the instance of that sensorID

NOTE: There are no try/except blocks so it is the responsibly of whatever calls these methods to use try catch (should include TypeError, KeyError, and 
FileNotFoundError)
"""


# Todo: How to monitor and handle when a thread dies

class deviceManager:
    def __init__(self, pipe, deviceID, test, threadLimit, configPath, manegementPipe, localOnly):
        self.MastersensorDict = {}
        self.NAT = {}
        self.manegementPipe = manegementPipe
        self.datapipe = pipe
        self.configPath = configPath
        self.deviceID = deviceID
        self.threadLimit = threadLimit
        self.storageSet()
        self.localOnly = localOnly

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

    def getsensorID(self):
        return len(self.MastersensorDict) + 1

    def launcher(self, sensorType, sensorID=None, globalID=0, customConfig=None, restart=False, callBack=False):
        if len(self.MastersensorDict) >= self.threadLimit:
            SensorThreadLimit()

        if sensorID == None or sensorID == 0:
            logging.info("sensor being created with global SID: {}".format(globalID))
            logging.info("sensor does not have a local SID")
            sensorID = self.getsensorID()
            logging.info("Generated sensorID is: {}".format(sensorID))

        sensor = self.makesensor(sensorType=sensorType, sensorID=sensorID, customConfig=customConfig, restart=restart, globalID=globalID)
        self.MastersensorDict[sensorID] = sensor

        if callBack:
            self.addSensorToConf(sensorType=sensorType, sensorID=sensorID, globalID=globalID, customConfig=customConfig)
            self.NAT[globalID] = sensorID

        if globalID == 0 and not self.localOnly:
            logging.info("No global ID. Requesting sensor Registration")
            data = {
                "sensorType": sensorType,
                "deviceID": self.deviceID,
                "customConfig": customConfig,
                "localID": sensorID
            }

            package = Package(data=data, packageType=registerSensor)
            self.manegementPipe.put(payload=package)

        thread = Thread(target=sensor.getData, name=sensorID)

        thread.start()

        logging.info("New sensor Spawned. sensor Info: {}\n".format(
            json.dumps(sensor.getInfo(), indent=4, sort_keys=True)))

    def supervisorGlobalRegistration(self, globalID, localID):
        self.NAT[globalID] = localID
        self.updatesensorConfGlobalID(globalID=globalID, sensorID=localID)

        self.getsensorInstanceFromGlobal(globalID=globalID).updateGlobalID(globalID=globalID)

    def updatesensorConfGlobalID(self, globalID, sensorID):
        raw = open(self.configPath, "r")
        confRaw = json.load(raw)
        conf = confRaw
        raw.close()

        with open(self.configPath, "r+") as confFile:
            tempconf = confRaw["launcher"]["args"]["sensorList"]
            temp = tempconf
            tempsensor = True

            for entry in temp:
                if entry.get("sensorID") == sensorID:
                    tempconf.remove(entry)
                    entry["globalID"] = globalID
                    tempconf.append(entry)
                    tempsensor = False
                    break

            if not tempsensor:
                conf["launcher"]["args"]["sensorList"] = tempconf
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

    def addSensorToConf(self, sensorType, sensorID, globalID, customConfig=None):
        raw = open(self.configPath, "r")
        confRaw = json.load(raw)
        raw.close()

        with open(self.configPath, "r+") as confFile:
            conf = confRaw
            try:
                body = {}
                body["sensorType"] = sensorType
                body["sensorID"] = sensorID
                body["customConfig"] = customConfig
                body["globalID"] = globalID

                sensorList = conf["launcher"]["args"]["sensorList"]
                sensorList.append(body)
                conf["launcher"]["args"]["sensorList"] = sensorList

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

    def removesensorFromConf(self, globalID):
        raw = open(self.configPath, "r")
        confRaw = json.load(raw)
        raw.close()

        with open(self.configPath, "r+") as confFile:
            conf = confRaw
            try:

                sensorList = conf["launcher"]["args"]["sensorList"]
                tempList = sensorList

                for entry in tempList:
                    if entry.get("globalID") == globalID:
                        sensorList.remove(entry)

                conf["launcher"]["args"]["sensorList"] = sensorList

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

    def makesensor(self, sensorType, sensorID, globalID, customConfig, restart):
        config = self.getConfig(sensorType=sensorType)
        config['sensorID'] = sensorID
        config["globalID"] = globalID

        if customConfig != 'None' and bool(customConfig):
            config = self.customConfiguration(baseConfig=config, customConfig=customConfig)

            # ToDo: Clean this up - don't loops to handle

        sensorClass = self.getsensorClass(sensorType=sensorType)

        if restart:
            config["delay"] = self.getsensorInstance(sensorID=sensorID).getsensorInfo()["samplePeriod"]
            self.killsensor(sensorID=sensorID)

        else:
            for ID in self.MastersensorDict:
                sensor = self.getsensorInstance(sensorID=ID)
                if sensor.getSensorID() == sensorID:
                    raise SensorUniqueError

        sensor = sensorClass(**config, pipe=self.datapipe, deviceID=self.deviceID)

        return sensor

    # def dirSetUp(self, sensorID, sensor):
    #     if not Path(os.path.join(LOCAL_DATA, "sensorID_" + str(sensorID))).is_dir():
    #         pathDir = "{}sensorID_{}".format(LOCAL_DATA, sensorID)
    #         os.system("mkdir {}".format(pathDir))
    #         csvPath = os.path.join(pathDir, "localCSV.csv")
    #         with open(csvPath, 'a') as csvFile:
    #             writer = csv.writer(csvFile, delimiter=',')
    #             writer.writerow(sensor.getsensorHeaders())

    def getConfig(self, sensorType):
        with open(os.path.join(CONFIG_PATH, sensorType + ".json")) as configData:
            config = json.load(configData)
            return config

    def customConfiguration(self, baseConfig, customConfig):
        for key in customConfig.keys():
            baseConfig[key] = customConfig[key]

        return baseConfig

    def getsensorClass(self, sensorType):
        moduleName = sensor_PATH + sensorType
        module = importlib.import_module(moduleName)
        sensorClass = getattr(module, sensorType)
        return sensorClass

    def killsensor(self, sensorID):
        sensorID = self.NAT[sensorID]
        sensor = self.getsensorInstance(sensorID=sensorID)
        sensor.operational = False
        del self.MastersensorDict[sensorID]

        logging.info("sensor Killed. Dead sensorID: {}".format(sensorID))

    def getsensorTags(self, sensorID):
        sensorID = self.NAT[sensorID]
        sensor = self.MastersensorDict[sensorID]
        return sensor.getsensorTags()

    def getsensorInfo(self, sensorID):
        sensorID = self.NAT[sensorID]
        sensor = self.MastersensorDict[sensorID]
        return sensor.getsensorInfo()

    def getAllLocalsensors(self, ):
        allInfo = {}

        for ID in self.MastersensorDict.keys():
            sensor = self.MastersensorDict[ID]

            allInfo[sensor.sensorID] = sensor.getsensorInfo()

        return allInfo

    def getsensorInstance(self, sensorID):
        return self.MastersensorDict[sensorID]

    def getsensorInstanceFromGlobal(self, globalID):
        localID = self.NAT[globalID]
        return self.MastersensorDict[localID]
