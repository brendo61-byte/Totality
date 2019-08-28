from Device_Level.Framework.Base_Classes import dataPipe
from Device_Level.Framework.Managers.deviceManager import deviceManager
from Device_Level.Framework.Controllers.commandController import CommandController
from Device_Level.Framework.Controllers.dataController import DataController
from Device_Level.Framework.Launcher.localLauncher import Launcher

from Device_Level.Framework.Test_Sweet.deviceMangerTester import DMTest as DMT

from threading import Thread

import json
import traceback
import logging
import time

CONFIG_PATH = 'Framework/Totality_Config/deviceConfig.json'

"""
Launch Pad is the main starter to run EVERYTHING. It will read in from the configuration file and find 3 things: The launcher, the data Controller, and the 
command controller.

See those respective classes or the README for what they do.
"""

if __name__ == '__main__':
    try:
        with open(CONFIG_PATH) as configFile:
            config = json.load(configFile)
            DID = config["deviceID"]
            logging.basicConfig(level=config["logLevel"], filename='program.log', filemode='w', format='%(asctime)s - %(levelname)s - %(message)s')
            logging.info("\n\nLaunching Program")
            pipe = dataPipe.DataPipe()
            DM = deviceManager(pipe=pipe, deviceID=DID, test=config["test"])

            useLauncher = False
            if config["launcher"]["args"] != 'None' and bool(config["launcher"]["args"]):
                launcher = Launcher(**config["launcher"]["args"], deviceManager=DM)
                useLauncher = True

            commandController = CommandController(**config["commandControl"]["args"], DM=DM, deviceID=DID)
            dataController = DataController(**config["dataControl"]["args"], pipe=pipe, DM=DM, deviceID=DID)

            if useLauncher:
                LT = Thread(target=launcher.starter, name="Launcher_Thread")
                LT.start()

            CCThread = Thread(target=commandController.starter, name="CC_Thread")
            DCThread = Thread(target=dataController.starter, name="DC_Thread")

            CCThread.start()
            DCThread.start()

            logging.info("All Threads Launched Successfully")
            print("All Threads Launched Successfully")

            if config["test"] == "True":
                logging.info("Starting Tests ...")
                print("Starting Tests ...")
                time.sleep(2)
                tester = DMT(DM=DM)
                logging.info("Device_Level Manager Test:")
                print("Device_Level Manager Test:")
                tester.starer()


    except KeyError as KE:
        print("Key Error Occurred While Trying To Start IoT Device_Level. Now Exiting Program.\nError Message: {}\n\n{}".format(KE, traceback.format_exc()))
        logging.critical("Key Error Occurred While Trying To Start IoT Device_Level. Now Exiting Program.\nError Message: {}\n{}".format(KE, traceback.format_exc()))
        exit()

    except TypeError as TE:
        print("Key Error Occurred While Trying To Start IoT Device_Level. Now Exiting Program.\nError Message: {}\n\n{}".format(TE, traceback.format_exc()))
        logging.critical("Key Error Occurred While Trying To Start IoT Device_Level. Now Exiting Program.\nError Message: {}\n{}".format(TE, traceback.format_exc()))
        exit()

    except FileNotFoundError as FNFE:
        print("File Not Found Error Occurred While Trying To Start IoT Device_Level. Now Exiting Program.\nError Message: {}\n{}".format(FNFE, traceback.format_exc()))
        logging.critical(
            "File Not Found Error Occurred While Trying To Start IoT Device_Level. Now Exiting Program.\nError Message: {}\n{}".format(FNFE, traceback.format_exc()))
        exit()

    except NameError as NE:
        print("Name Error Occurred While Trying To Start IoT Device_Level. Now Exiting Program.\nError Message: {}\n{}".format(NE, traceback.format_exc()))
        logging.critical("Name Error Occurred While Trying To Start IoT Device_Level. Now Exiting Program.\nError Message: {}\n{}".format(NE, traceback.format_exc()))
        exit()

    except Exception as e:
        print("Failed To Start IoT Device_Level. Now Exiting Program.\nError Message: {}\n{}".format(e, traceback.format_exc()))
        logging.critical("Failed To Start IoT Device_Level. Now Exiting Program.\nError Message: {}\n{}".format(e, traceback.format_exc()))
        exit()
