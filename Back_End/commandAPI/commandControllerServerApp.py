from flask import Flask, request, jsonify
from queue import Queue
# from Back_End.commandAPI.models import *
from models import *

import datetime
import logging
import traceback
import random
import peewee
import requests
import ast

app = Flask(__name__)
logging.basicConfig(level="DEBUG", filename='program.log', filemode='w',
                    format='%(asctime)s - %(levelname)s - %(message)s')

loginURL = 'http://key_api:8805/keyAPI/generateSessionKey'
authenticationURL = 'http://key_api:8805/keyAPI/authenticateSessionKey'
deviceOwnershipURL = 'http://key_api:8805/keyAPI/deviceOwnerShip'
supervisorAuth = 'http://key_api:8805/keyAPI/supervisorAuth'

"""
This is the API for pushing new commands and pulling queued commands. There are a number of features that need to be added (see the #ToDo's around). Commands added
to queue will be given to the device with a matching DID and then run on said device. 

The commands "new supervisor", "update supervisor", "stop supervisor", and "get all local supervisor" have the added option of "callBack=True". The idea for this 
is so each command should be added to a the DB (not implemented). If callBack is set to True then the device will reply if that command has been successfully 
executed or not. This reply will to a URL that the data Controller will manage. From there the DB will up dated to reflect if the command was successful.
This is not implemented but the device knows how to handle "callBacks" so a little bit of data piping is all that's require on its end - and of course the backend
needs to be set up too.

"""


# ToDO: Add a 'get queued commands from DB' link

def makeCommandFormat(body, commandType, callBack=True, refID=None):
    CF = {
        "commandType": commandType,
        "body": body,
        "callBack": str(callBack),
        "refID": refID
    }

    if "deviceID" in CF["body"]:
        del CF["body"]["deviceID"]

    return CF


def authenticateSessionKey(key):
    body = {
        "key": key
    }

    try:
        response = requests.post(url=authenticationURL, json=body)

        info = response.json()
        data = info.get("data")

        if data:
            return data
        else:
            logging.info("Failed to authenticate Session Key. Reason: {}".format(info.get("userMessage")))
    except Exception as e:
        logging.warning(
            "Failed to reach authentication key API\nException: {}\nTraceBack {}".format(e, traceback.format_exc()))


def deviceOwnerShip(CID, DID):
    body = {
        "CID": CID,
        "DID": DID
    }

    try:
        response = requests.post(url=deviceOwnershipURL, json=body)

        info = response.json()
        data = info.get("data")

        if data:
            return data
        else:
            logging.info("CID {} attempted to access non-associated DID {}\nKey API response: {}".format(CID, DID, info.get("userMessage")))
    except Exception as e:
        logging.warning(
            "Failed to reach Device Ownership key API\nException: {}\nTraceBack {}".format(e, traceback.format_exc()))


def validateSupervisorAuthorization(DID, SID, CID):
    body = {
        "SID": SID,
        "DID": DID
    }

    try:
        response = requests.post(url=supervisorAuth, json=body)

        info = response.json()
        data = info.get("data")

        if data:
            return data
        else:
            logging.info("CID {} attempted to access non-associated SID {}\nKey API response: {}".format(CID, SID, info.get("userMessage")))
    except Exception as e:
        logging.warning(
            "Failed to reach Device Ownership key API\nException: {}\nTraceBack {}".format(e, traceback.format_exc()))


def genSupervisorRefID():
    refID = random.randint(0, 2147483645)
    q = Supervisor.select().where(Supervisor.refID == refID)

    while q.exists():
        refID = random.randint(0, 2147483645)
        q = Supervisor.select().where(Supervisor.refID == refID)

    return refID


def genCommandRefID():
    refID = random.randint(0, 2147483645)
    q = Command.select().where(Command.refID == refID)

    while q.exists():
        refID = random.randint(0, 2147483645)
        q = Command.select().where(Command.refID == refID)

    return refID


@app.route('/user/device/newSupervisor', methods=["POST"])
def newSupervisor():
    data = request.get_json()
    supervisorType = data.get('supervisorType')
    customConfig = data.get('customConfig')

    key = request.get_json().get("key")
    DID = request.get_json().get("DID")

    CID = authenticateSessionKey(key=key)

    if not CID:
        logging.info("Get All Devices Hit: Unable to validate sessionKey")
        return jsonify(userMessage="Unable to validate Session Key"), 400

    if DID is None:
        statement = "New Supervisor Hit: No DID Type Provided"
        logging.info(statement)
        return jsonify(userMessage=statement), 400

    if not deviceOwnerShip(CID=CID, DID=DID):
        logging.info("Device Drop Hit: Unauthorized access on DID {} from CID {}".format(DID, CID))
        return jsonify(userMessage="Please Provide A Valid Device ID"), 400

    if supervisorType is None:
        statement = "New Supervisor Hit: No Supervisor Type Provided"
        logging.info(statement)
        return jsonify(userMessage=statement), 400

    if customConfig is None:
        logging.info("New Supervisor Hit: Using Base Configuration")

    refID = genSupervisorRefID()
    logging.debug("New Supervisor Hit: refID generated: {}".format(refID))

    supervisorID = None

    try:
        Supervisor.create(deviceOwner=DID, refID=refID, supervisorType=supervisorType, customConfig=str(customConfig))
        # ToDo: Use fsting (python 3.6) - cleaner way of putting variables in strings
        logging.debug("New Supervisor Hit: Supervisor Created in DB. RefID: {}".format(refID))

    except Exception as e:
        statement = "New Supervisor Hit: Unable to create new supervisor in DB.\nException: {}\nTraceBack: {}".format(
            e, traceback.format_exc())
        logging.info(statement)
        return jsonify(userMesage=statement), 400

    try:
        logging.debug("New Supervisor Hit: Fetching SID based on refID")
        entry = Supervisor.get(Supervisor.refID == refID)
        supervisorID = entry.supervisorID
        entry.refID = 0
        entry.save()
        logging.debug("New Supervisor Hit: SID Fetched: {}".format(supervisorID))

    except Exception as e:
        statement = "New Supervisor Hit: Unable to assign supervisor an ID.\nException: {}\nTraceBack: {}".format(e,
                                                                                                                  traceback.format_exc())
        logging.info(statement)
        return jsonify(userMessage=statement), 400
        # ToDo: How to handle a new supervisor being created if the command is not passed to the device

    try:

        body = {"supervisorType": supervisorType, "globalID": supervisorID, "deviceID": DID,
                "customConfig": customConfig}

        refID = genCommandRefID()
        CF = str(makeCommandFormat(body=body, commandType="launcher", callBack=True, refID=refID)).replace("'", "\'")
        Command.create(command=CF, deviceOwner=DID, refID=refID)
        logging.debug(
            "New Supervisor Hit: New Supervisor Command Added. Info --- Supervisor Type: {}, Supervisor ID: {}, DID: {}, Custom Config: {}".format(
                supervisorType, supervisorID, DID, customConfig))

        return jsonify(userMessage="New Supervisor Hit: New Supervisor Command Added To Queue"), 200

    except Exception as e:
        logging.info("New Supervisor Hit: Unable to assign supervisor an ID.\nException: {}\nTraceBack: {}".format(
            e, traceback.format_exc()))

        return jsonify(
            userMessage="New Supervisor Hit: Unable to assign supervisor an ID.\nException: {}\nTraceBack: {}".format(
                e, traceback.format_exc())), 400


@app.route('/user/device/updateSupervisor', methods=["POST"])
def updateSupervisor():
    data = request.get_json()
    supervisorType = data.get('supervisorType')
    customConfig = data.get('customConfig')

    key = data.get("key")
    DID = data.get("DID")
    SID = data.get("SID")

    CID = authenticateSessionKey(key=key)

    if not CID:
        logging.info("Update Supervisor Hit: Unable to validate sessionKey")
        return jsonify(userMessage="Unable to validate Session Key"), 400

    if DID is None:
        statement = "Update Supervisor Hit: No DID Type Provided"
        logging.info(statement)
        return jsonify(userMessage=statement), 400

    if not deviceOwnerShip(CID=CID, DID=DID):
        logging.info("Update Supervisor Hit: Unauthorized access on DID {} from CID {}".format(DID, CID))
        return jsonify(userMessage="Please Provide A Valid Device ID"), 400

    if not validateSupervisorAuthorization(SID=SID, DID=DID, CID=CID):
        logging.info("Update Supervisor Hit: Unauthorized access on SID {} from CID {}".format(SID, CID))
        return jsonify(userMessage="Please Provide a Valid Supervisor ID"), 400

    if supervisorType is None:
        logging.info("Update Supervisor Hit: No Supervisor Type Provided")
        return jsonify(userMessage="Please Provide A Valid Supervisor ID"), 400

    if customConfig is None:
        logging.info("Update Supervisor Hit: No Custom Configuration Provided")
        return jsonify(userMessage="Please Provide A Valid Custom Configuration"), 400

    try:
        entry = Supervisor.get(Supervisor.supervisorID == DID)
        entry.customConfig = str(customConfig)
        entry.customConfig = 'True'
        entry.save()

    except:
        statement = "Update Supervisor Hit: Unable to update supervisor in DB"
        logging.warning(statement)
        return jsonify(userMessage=statement), 400

    body = {'supervisorType': supervisorType, 'supervisorID': SID, 'customConfig': customConfig,
            "restart": True}

    refID = genCommandRefID()
    CF = makeCommandFormat(body=body, commandType="launcher", callBack=True, refID=refID)
    Command.create(command=CF, deviceOwner=DID, refID=refID)
    logging.debug(
        "Update Supervisor Hit: Update Supervisor Command Added To Queue. Info --- Supervisor Type: {}, Supervisor ID: {}, DID: {}, Custom Config: {}".format(
            supervisorType, SID, DID, configStatus))

    return jsonify(userMessage="Update Supervisor Command Added To Queue."), 200


@app.route('/user/device/stopSupervisor', methods=["POST"])
def stopSupervisor():
    data = request.get_json()

    DID = data.get("DID")
    key = data.get("key")
    SID = data.get("SID")

    CID = authenticateSessionKey(key=key)

    if not CID:
        logging.info("Drop Customer Hit: Unable to validate sessionKey")
        return jsonify(userMessage="Unable to validate Session Key"), 400

    if DID is None:
        logging.info("Drop Device Hit: No DID Provided")
        return jsonify(userMessage="Please Provide A Valid Device ID"), 400

    if not deviceOwnerShip(CID=CID, DID=DID):
        logging.info("Device Drop Hit: Unauthorized access on DID {} from CID {}".format(DID, CID))
        return jsonify(userMessage="Please Provide A Valid Device ID"), 400

    if not validateSupervisorAuthorization(SID=SID, DID=DID, CID=CID):
        logging.info("Update Supervisor Hit: Unauthorized access on SID {} from CID {}".format(SID, CID))
        return jsonify(userMessage="Please Provide a Valid Supervisor ID"), 400

    body = {"supervisorID": SID}
    refID = genCommandRefID()
    CF = makeCommandFormat(body=body, commandType="killSupervisor", callBack=True, refID=refID)
    Command.create(command=CF, deviceOwner=DID, refID=refID)
    logging.debug("Stop Supervisor Hit: Stop Supervisor Command Added To Queue")

    return jsonify(userMessage="Stop Supervisor Command Added To Queue. DID: {}, Supervisor ID: {}".format(DID, SID)), 200


def generateDeviceCommands(deviceID):
    query = Command.select().where(Command.deviceOwner == deviceID)
    logging.debug("Get Commands  Hit: Generating DB querry")
    if not query.exists():
        logging.debug("Get Commands  Hit: No commands in DB")
        return None
    else:
        return convertCommandsToDict(query=query, deviceID=deviceID)


def convertCommandsToDict(query, deviceID):
    commandList = []
    backUpCommand = None
    logging.debug("Get Commands  Hit: Parsing commands")
    try:
        for entry in query:
            if entry.delivery == 0:
                command = str(entry.command).replace("'", "\"")
                command = ast.literal_eval(command)
                command["commandID"] = entry.commandID
                command = str(command)
                # This is dumb but we need to put the commandID into the package for the device to ref it for call back

                backUpCommand = command
                logging.debug("Get Commands: DID no. {} has new command.\nCommand: {}".format(deviceID, command))
                entry.delivery = 1
                entry.save()
                commandList.append(ast.literal_eval(command))

    except Exception as e:
        logging.warning(
            "Get Commands: Unable to parse query to get DID no. {} commands\nException: {}\nTraceBack: {}\nCommand: {}".format(
                deviceID,
                e,
                traceback.format_exc(), backUpCommand))

    logging.debug("Get Commands Hit: Command List for DID no. {}:\nCL:{}".format(deviceID, commandList))

    return commandList


@app.route('/device/commands/getCommands', methods=["POST"])
def deviceGetCommands():
    deviceID = request.get_json().get("deviceID")

    if deviceID is None:
        logging.info("Get Commands Hit: No DID Provided")
        return jsonify(userMessage="Please Provide A Valid Device ID"), 400

    if not validateDeviceExists(validateDeviceExists(deviceID)):
        logging.info("Get Commands Hit: Unable To Verify DID Existence")
        return jsonify(userMessage="Unable To Verify DID Existence"), 400

    try:
        device = Device.get(Device.deviceID == deviceID)
        device.missedCommands = 0
        device.timeOfLastCheckIn = datetime.datetime.utcnow()
        device.commandTimeWindow = datetime.datetime.utcnow() + datetime.timedelta(
            seconds=device.commandControllerPeriod)
        device.save()
    except Exception as e:
        logging.warning(
            "Get Commands Hit: Could Not Update Device In Data Base. DID: {}\nException: {}\nTraceBack: {}".format(
                deviceID, e, traceback.format_exc()))
        return jsonify(userMessge="Unable To Update Device In Data Base"), 400

    commandList = generateDeviceCommands(deviceID=deviceID)

    if commandList:
        logging.debug("Get Commands  Hit: Returning Commands To DID: {}".format(deviceID))
        return jsonify(userMessage="Returning Commands", commands=commandList), 200
    else:
        logging.debug("Get Commands Hit: No New Commands For DID: {}".format(deviceID))
        return jsonify(userMessage="No Commands To Execute"), 200


if __name__ == '__main__':
    # time.sleep(5)
    app.run(host="0.0.0.0", debug=True, port=8802)