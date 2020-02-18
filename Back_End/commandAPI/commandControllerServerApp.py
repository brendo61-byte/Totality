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
import os

app = Flask(__name__)
logging.basicConfig(level="DEBUG", filename='program.log', filemode='w',
                    format='%(asctime)s - %(levelname)s - %(message)s')

nginxIPAddr = os.environ.get("nginxIPAddr", "172.28.1.6")
loginURL = os.environ.get('loginURL', 'http://{}/keyAPI/generateSessionKey'.format(nginxIPAddr))
authenticationURL = os.environ.get('authenticationURL', 'http://{}/keyAPI/authenticateSessionKey'.format(nginxIPAddr))
deviceOwnershipURL = os.environ.get('deviceOwnershipURL', 'http://{}/keyAPI/deviceOwnerShip'.format(nginxIPAddr))
sensorAuth = os.environ.get('sensorAuth', 'http://{}/keyAPI/sensorAuth'.format(nginxIPAddr))

"""
This is the API for pushing new commands and pulling queued commands. There are a number of features that need to be added (see the #ToDo's around). Commands added
to queue will be given to the device with a matching DID and then run on said device. 

The commands "new sensor", "update sensor", "stop sensor", and "get all local sensor" have the added option of "callBack=True". The idea for this 
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


def validateSensorAuthorization(DID, SID, CID):
    body = {
        "SID": SID,
        "DID": DID
    }

    try:
        response = requests.post(url=sensorAuth, json=body)

        info = response.json()
        data = info.get("data")

        if data:
            return data
        else:
            logging.info("CID {} attempted to access non-associated SID {}\nKey API response: {}".format(CID, SID, info.get("userMessage")))
    except Exception as e:
        logging.warning(
            "Failed to reach Device Ownership key API\nException: {}\nTraceBack {}".format(e, traceback.format_exc()))


def genSensorRefID():
    refID = random.randint(0, 2147483645)
    q = Sensor.select().where(Sensor.refID == refID)

    while q.exists():
        refID = random.randint(0, 2147483645)
        q = Sensor.select().where(Sensor.refID == refID)

    return refID


def genCommandRefID():
    refID = random.randint(0, 2147483645)
    q = Command.select().where(Command.refID == refID)

    while q.exists():
        refID = random.randint(0, 2147483645)
        q = Command.select().where(Command.refID == refID)

    return refID


@app.route('/command/user/device/newSensor', methods=["POST"])
def newSensor():
    data = request.get_json()
    sensorType = data.get('sensorType')
    customConfig = data.get('customConfig')

    key = request.get_json().get("key")
    DID = request.get_json().get("DID")

    CID = authenticateSessionKey(key=key)

    if not CID:
        logging.info("Get All Devices Hit: Unable to validate sessionKey")
        return jsonify(userMessage="Unable to validate Session Key"), 400

    if DID is None:
        statement = "New Sensor Hit: No DID Type Provided"
        logging.info(statement)
        return jsonify(userMessage=statement), 400

    if not deviceOwnerShip(CID=CID, DID=DID):
        logging.info("Device Drop Hit: Unauthorized access on DID {} from CID {}".format(DID, CID))
        return jsonify(userMessage="Please Provide A Valid Device ID"), 400

    if sensorType is None:
        statement = "New Sensor Hit: No Sensor Type Provided"
        logging.info(statement)
        return jsonify(userMessage=statement), 400

    if customConfig is None:
        logging.info("New Sensor Hit: Using Base Configuration")

    refID = genSensorRefID()
    logging.debug("New Sensor Hit: refID generated: {}".format(refID))

    sensorID = None

    try:
        Sensor.create(deviceOwner=DID, refID=refID, sensorType=sensorType, customConfig=str(customConfig))
        # ToDo: Use fsting (python 3.6) - cleaner way of putting variables in strings
        logging.debug("New Sensor Hit: Sensor Created in DB. RefID: {}".format(refID))

    except Exception as e:
        statement = "New Sensor Hit: Unable to create new sensor in DB.\nException: {}\nTraceBack: {}".format(
            e, traceback.format_exc())
        logging.info(statement)
        return jsonify(userMesage=statement), 400

    try:
        logging.debug("New Sensor Hit: Fetching SID based on refID")
        entry = Sensor.get(Sensor.refID == refID)
        sensorID = entry.sensorID
        entry.refID = 0
        entry.save()
        logging.debug("New Sensor Hit: SID Fetched: {}".format(sensorID))

    except Exception as e:
        statement = "New Sensor Hit: Unable to assign sensor an ID.\nException: {}\nTraceBack: {}".format(e,
                                                                                                                  traceback.format_exc())
        logging.info(statement)
        return jsonify(userMessage=statement), 400
        # ToDo: How to handle a new sensor being created if the command is not passed to the device

    try:

        body = {"sensorType": sensorType, "globalID": sensorID, "deviceID": DID,
                "customConfig": customConfig}

        refID = genCommandRefID()
        CF = str(makeCommandFormat(body=body, commandType="launcher", callBack=True, refID=refID)).replace("'", "\'")
        Command.create(command=CF, deviceOwner=DID, refID=refID)
        logging.debug(
            "New Sensor Hit: New Sensor Command Added. Info --- Sensor Type: {}, Sensor ID: {}, DID: {}, Custom Config: {}".format(
                sensorType, sensorID, DID, customConfig))

        return jsonify(userMessage="New Sensor Hit: New Sensor Command Added To Queue"), 200

    except Exception as e:
        logging.info("New Sensor Hit: Unable to assign sensor an ID.\nException: {}\nTraceBack: {}".format(
            e, traceback.format_exc()))

        return jsonify(
            userMessage="New Sensor Hit: Unable to assign sensor an ID.\nException: {}\nTraceBack: {}".format(
                e, traceback.format_exc())), 400


@app.route('/command/user/device/updateSensor', methods=["POST"])
def updateSensor():
    data = request.get_json()
    sensorType = data.get('sensorType')
    customConfig = data.get('customConfig')

    key = data.get("key")
    DID = data.get("DID")
    SID = data.get("SID")

    CID = authenticateSessionKey(key=key)

    if not CID:
        logging.info("Update Sensor Hit: Unable to validate sessionKey")
        return jsonify(userMessage="Unable to validate Session Key"), 400

    if DID is None:
        statement = "Update Sensor Hit: No DID Type Provided"
        logging.info(statement)
        return jsonify(userMessage=statement), 400

    if not deviceOwnerShip(CID=CID, DID=DID):
        logging.info("Update Sensor Hit: Unauthorized access on DID {} from CID {}".format(DID, CID))
        return jsonify(userMessage="Please Provide A Valid Device ID"), 400

    if not validateSensorAuthorization(SID=SID, DID=DID, CID=CID):
        logging.info("Update Sensor Hit: Unauthorized access on SID {} from CID {}".format(SID, CID))
        return jsonify(userMessage="Please Provide a Valid Sensor ID"), 400

    if sensorType is None:
        logging.info("Update Sensor Hit: No Sensor Type Provided")
        return jsonify(userMessage="Please Provide A Valid Sensor ID"), 400

    if customConfig is None:
        logging.info("Update Sensor Hit: No Custom Configuration Provided")
        return jsonify(userMessage="Please Provide A Valid Custom Configuration"), 400

    try:
        entry = Sensor.get(Sensor.sensorID == DID)
        entry.customConfig = str(customConfig)
        entry.customConfig = 'True'
        entry.save()

    except:
        statement = "Update Sensor Hit: Unable to update sensor in DB"
        logging.warning(statement)
        return jsonify(userMessage=statement), 400

    body = {'sensorType': sensorType, 'sensorID': SID, 'customConfig': customConfig,
            "restart": True}

    refID = genCommandRefID()
    CF = makeCommandFormat(body=body, commandType="launcher", callBack=True, refID=refID)
    Command.create(command=CF, deviceOwner=DID, refID=refID)
    logging.debug(
        "Update Sensor Hit: Update Sensor Command Added To Queue. Info --- Sensor Type: {}, Sensor ID: {}, DID: {}, Custom Config: {}".format(
            sensorType, SID, DID, configStatus))

    return jsonify(userMessage="Update Sensor Command Added To Queue."), 200


@app.route('/command/user/device/stopSensor', methods=["POST"])
def stopSensor():
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

    if not validateSensorAuthorization(SID=SID, DID=DID, CID=CID):
        logging.info("Update Sensor Hit: Unauthorized access on SID {} from CID {}".format(SID, CID))
        return jsonify(userMessage="Please Provide a Valid Sensor ID"), 400

    body = {"sensorID": SID}
    refID = genCommandRefID()
    CF = makeCommandFormat(body=body, commandType="killSensor", callBack=True, refID=refID)
    Command.create(command=CF, deviceOwner=DID, refID=refID)
    logging.debug("Stop Sensor Hit: Stop Sensor Command Added To Queue")

    return jsonify(userMessage="Stop Sensor Command Added To Queue. DID: {}, Sensor ID: {}".format(DID, SID)), 200


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


@app.route('/command/device/getCommands', methods=["POST"])
def deviceGetCommands():
    deviceID = request.get_json().get("deviceID")

    if deviceID is None:
        logging.info("Get Commands Hit: No DID Provided")
        return jsonify(userMessage="Please Provide A Valid Device ID"), 400

    try:
        device = Device.get(Device.deviceID == deviceID)
        device.missedCommands = 0
        device.timeOfLastCheckIn = datetime.datetime.utcnow()
        device.commandTimeWindow = datetime.datetime.utcnow() + datetime.timedelta(
            seconds=device.commandControllerPeriod)
        device.save()
    except Exception as e:
        logging.warning(
            "Get Commands Hit: Could Not Get Device Commands In Data Base. DID: {}\nException: {}\nTraceBack: {}".format(
                deviceID, e, traceback.format_exc()))
        return jsonify(userMessge="Unable To Get Device Commands In Data Base"), 400

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
