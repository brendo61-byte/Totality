from Device_Level.Framework.Base_Classes.controller import Controller

import logging
import json
import traceback

"""
Local Launcher is responsible for starting supervisorr(s) on a device.
This script knows what supervisorrs to spawn based on the Device_Level Config file (see Totality/Framework/Totality_Config/deviceConfig)

If there is a bad config passed in for a supervisorr then it will catch the error.

NOTE: If the base config is used for a supervisorr it WILL work (b/c you have to test that it will - therefor only custom configs can cause supervisorr spawning to fail)
"""


class Launcher(Controller):
    def __init__(self, supervisorList, deviceManager):
        self.supervisorListList = supervisorList
        self.deviceManager = deviceManager

    def spawnSupervisor(self):
        status = True
        try:
            for supervisorConfig in self.supervisorListList:
                self.deviceManager.launcher(**supervisorConfig)

        except KeyError as KE:
            logging.critical(
                "Key Error Occurred While Trying To supervisorr. supervisorr Config: {}.\nError Message: {}\n\n{}".format(None, KE, traceback.format_exc()))

        except TypeError as TE:
            logging.critical(
                "Key Error Occurred While Trying To Start supervisorr. supervisorr Config: {}.\nError Message: {}\n\n{}".format(None, TE, traceback.format_exc()))

        except FileNotFoundError as FNFE:
            logging.critical(
                "File Not Found Error Occurred While Trying To Start supervisorr. supervisorr Config: {}.\nError Message: {}\n\n{}".format(None, FNFE,
                                                                                                                                 traceback.format_exc()))

        except Exception as e:
            logging.critical("Failed To Start supervisorr. supervisorr Config: {}.\nError Message: {}\n\n{}".format(None, e, traceback.format_exc()))

        if status:
            logging.info("All Launch Supervisors Spawned Successfully")
        else:
            logging.warning("Launch supervisorr Spanning Complete. Some Supervisors Did Not Spawn Successfully. See logs")

    def starter(self):
        self.spawnSupervisor()

    def jsonToStr(self, supervisorConfig):
        if bool(supervisorConfig) and type(supervisorConfig) is dict:
            return json.dumps(supervisorConfig, indent=4, sort_keys=True)
