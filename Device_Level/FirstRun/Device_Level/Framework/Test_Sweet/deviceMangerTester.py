# from Device_Level.Framework.Base_Classes.tester import Tester
# from Device_Level.Framework.Base_Classes.exceptionClasses import *

from Framework.Base_Classes.tester import Tester
from Framework.Base_Classes.exceptionClasses import *

import json
import traceback
import time
import random
import logging
import os

CLEANPATH = 'LOCAL_DATA/supervisorID_'


class DMTest(Tester):
    def __init__(self, DM):
        self.DM = DM
        self.resultsDict = {}
        self.IdList = []
        self.realIDs = []

    def starer(self):
        time.sleep(1)
        self.testgetAllLocalSupervisors()
        self.testlauncher()
        self.testkillSupervisor()
        self.testgetTags()
        self.testgetSupervisorInfo()

        self.cleanUp()
        self.results()

    def results(self):
        if bool(self.resultsDict):
            log = json.dumps(self.resultsDict, indent=4, sort_keys=True)
            print("deviceMangerTester: Test(s) failed - Results:\n" + log)
            logging.debug("deviceMangerTester: Test(s) failed - Results:\n" + log)
        else:
            print("deviceMangerTester: All Tests Passed Successfully\n")
            logging.debug("deviceManagerTester: All Tests Passed Successfully\n")

    def cleanUp(self):
        print("Starting CleanUp")
        logging.debug("Starting CleanUp")
        status = True
        killDict = {}
        print("\nID List To Clean: {}".format(self.IdList))
        while bool(self.IdList):
            ID = self.IdList.pop()
            print("Cleaning Supervisor ID: {}".format(ID))
            logging.debug("Cleaning Supervisor ID: {}".format(ID))
            try:
                supervisorThreadTimeOut = self.DM.getSupervisorInstance(supervisorID=ID).getSupervisorInfo()["samplePeriod"] * 2
                self.DM.killSupervisor(supervisorID=ID)
                time.sleep(supervisorThreadTimeOut)
                path = CLEANPATH + str(ID)
                os.system("rm -r {}".format(path))

            except Exception as e:
                status = False
                killDict[ID] = {
                    "info": "Failed To Clean Up Supervisor ID".format(ID),
                    "Exception": str(e),
                    "traceback": traceback.format_exc()
                }

        if status:
            print("deviceMangerTester: CleanUp Complete\n")
            logging.debug("deviceMangerTester: CleanUp Complete\n")

        else:
            print(killDict)
            print()
            log = json.dumps(killDict, indent=4, sort_keys=True)
            print("deviceMangerTester: Failed to kill all Supervisors launched for testing. See below for details:\n" + log)
            logging.debug("deviceMangerTester: Failed to kill all Supervisors launched for testing. See below for details:\n" + log)

        # print("\n\n\n")
        # print(self.DM.getAllLocalSupervisors())
        # print(self.DM.MasterSupervisorDict)
        # x = self.DM.MasterSupervisorDict
        # for key in x.keys():
        #     print(key)

    def genNewID(self, save=False):
        ID = random.randint(1000, 1100)
        while ID in self.IdList or ID in self.realIDs:
            ID = random.randint(1000, 1100)

        if save:
            self.IdList.append(ID)
            print("New Supervisor ID: {}".format(ID))
        return ID

    def genRedundantID(self):
        return self.IdList[0]

    def testlauncher(self):
        # test 1: Base Config
        try:
            self.DM.launcher(supervisorID=self.genNewID(save=True), supervisorType="intMaker")
        except Exception as e:
            self.resultsDict["testlauncher_Test1"] = {
                "test": "Tests that a Supervisor with base configuration can be launched",
                "Exception": str(e),
                "traceback": traceback.format_exc()

            }

        # test 2: Custom Config
        try:
            self.DM.launcher(supervisorID=self.genNewID(save=True), supervisorType="intMaker", customConfig={"supervisorName": "TestSupervisor"})
        except Exception as e:
            self.resultsDict["testlauncher_Test2"] = {
                "test": "Tests taht a Supervisor with custom configuration can be launched",
                "Exception": str(e),
                "traceback": traceback.format_exc()
            }

        # test 3: Supervisor Update
        try:
            self.DM.launcher(supervisorID=self.genRedundantID(), supervisorType="intMaker", customConfig={"supervisorName": "UpdatedSupervisor"}, restart=True)
        except Exception as e:
            self.resultsDict["testlauncher_Test3"] = {
                "test": "Tests that a Supervisor can be updated",
                "Exception": str(e),
                "traceback": traceback.format_exc()

            }

        # test 4: Raise SupervisorUniqueError
        try:
            self.DM.launcher(supervisorID=self.genRedundantID(), supervisorType="intMaker")
        except SupervisorUniqueError:
            pass
        except Exception as e:
            self.resultsDict["testlauncher_Test4"] = {
                "test": "Test is a Supervisor being made under the same ID will throw a SupervisorUniqueError",
                "Exception": str(e),
                "traceback": traceback.format_exc()
            }

        # test 5: Raise TypeError
        try:
            self.DM.launcher(supervisorID=self.genNewID(), supervisorType="intMaker", customConfig={"dog": "Koda"})
        except TypeError:
            pass
        except Exception as e:
            self.resultsDict["testlauncher_Test5"] = {
                "test": "Tests that a TypeError will be thrown when unknown parameters are passed into the Supervisor",
                "Exception": str(e),
                "traceback": traceback.format_exc()
            }

    def testmakeSupervisor(self):
        # This is testing by testlauncher
        return

    def testdirSetUp(self):
        # This is testing by testlauncher
        return

    def testgetConfig(self):
        # This is testing by testlauncher
        return

    def testcustomConfiguration(self):
        # This is testing by testlauncher
        return

    def testgetSupervisorClass(self):
        # This is testing by testlauncher
        return

    def testkillSupervisor(self):
        # cleanUp will test that Supervisors can be killed properly
        # Test 1: KeyError with kill Supervisor
        try:
            self.DM.killSupervisor(supervisorID=self.genNewID())
        except KeyError:
            pass
        except Exception as e:
            self.resultsDict["testkillSupervisor_Test1"] = {
                "test": "Tests that a keyError is properly thrown when trying to kill a Supervisor with a false ID",
                "Exception": str(e),
                "traceback": traceback.format_exc()
            }

    def testgetTags(self):
        # Test 1: get Supervisor tags
        try:
            self.DM.getSupervisorTags(supervisorID=self.genRedundantID())
        except Exception as e:
            self.resultsDict["testgetTags_Test1"] = {
                "test": "Tests that Supervisor tags can be retrieved",
                "Exception": str(e),
                "traceback": traceback.format_exc()
            }

        # Test 2: KeyError with getting Supervisor tags
        try:
            self.DM.getSupervisorTags(supervisorID=self.genNewID())
        except KeyError:
            pass
        except Exception as e:
            self.resultsDict["testgetTags_Test2"] = {
                "test": "Tests that a keyError is properly thrown when trying to get tags from a Supervisor with a false ID",
                "Exception": str(e),
                "traceback": traceback.format_exc()
            }

    def testgetSupervisorInfo(self):
        # Test 1: gets Supervisor info
        try:
            self.DM.getSupervisorInfo(supervisorID=self.genRedundantID())
        except Exception as e:
            self.resultsDict["testgerSupervisorInfo_Test1"] = {
                "test": "Tests that Supervisor info can be retrieved",
                "Exception": str(e),
                "traceback": traceback.format_exc()
            }

        # Test 2: KeyError with get Supervisor info
        try:
            self.DM.getSupervisorInfo(supervisorID=self.genNewID())
        except KeyError:
            pass
        except Exception as e:
            self.resultsDict["testgerSupervisorInfo_Test2"] = {
                "test": "Tests that a keyError is properly thrown when trying to get info from a Supervisor with a false ID",
                "Exception": str(e),
                "traceback": traceback.format_exc()
            }

    def testgetAllLocalSupervisors(self):
        try:
            t = self.DM.getAllLocalSupervisors()
            if type(t) is not dict:
                print("WARNING: Testing integrity compromised. Unknown Supervisor IDs in use.")
                self.resultsDict["testgetAllLocalSupervisors"] = {
                    "test": "Tests that a dict of all local Supervisors can be retrieved",
                    "WARNING": "TEST INTEGRITY COMPROMISED",
                    "return": str(t)
                }
            else:
                for ID in t.keys():
                    self.realIDs.append(ID)
        except:
            print("WARNING: Testing integrity compromised. Unknown Supervisor IDs in use.")
            self.resultsDict["testgetAllLocalSupervisors"] = {
                "test": "Tests that a dict of all local Supervisors can be retrieved",
                "WARNING": "TEST INTEGRITY COMPROMISED",
            }

    def testgetSupervisorInstance(self):
        return
