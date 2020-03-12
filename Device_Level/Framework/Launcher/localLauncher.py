# from Device_Level.Framework.Base_Classes.controller import Controller
from Framework.Base_Classes.controller import Controller

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
    def __init__(self, sensorList, deviceManager):
        self.sensorListList = sensorList
        self.deviceManager = deviceManager

    def spawnSupervisor(self):
        status = True
        for sensorConfig in self.sensorListList:

            try:

                self.deviceManager.launcher(**sensorConfig)

            except Exception as e:
                status = False
                logging.critical(
                    "Failed To Start supervisor. supervisor Config: {}.\nError Message: {}\n\n{}".format(
                        sensorConfig,
                        e,
                        traceback.format_exc()))

        if status:
            logging.info("All Launch Sensors Spawned Successfully")
        else:
            print("ERROR: Unable to spawn launch supervisors. See Logs.")


            logging.warning(
                "Launch supervisorr Spanning Complete. Some Sensors Did Not Spawn Successfully. See logs")

    def starter(self):
        self.spawnSupervisor()

    def jsonToStr(self, supervisorConfig):
        if bool(supervisorConfig) and type(supervisorConfig) is dict:
            return json.dumps(supervisorConfig, indent=4, sort_keys=True)
