from flask import Flask, request, jsonify
from queue import Queue
#from Back_End.commandController.models import *
from models import *

import datetime
import logging
import traceback

CQ = Queue(maxsize=0)
# ToDo: Should use rabbitmq - w/ a pub/sub type sorting by Device ID
# ToDo: Add to README
# ToDo: Talk to Brad about using a wrapper for method class to handle unexpected exceptions and security clearance

app = Flask(__name__)
logging.basicConfig(level="DEBUG", filename='program.log', filemode='w', format='%(asctime)s - %(levelname)s - %(message)s')


"""
This is the API for pushing new commands and pulling queued commands. There are a number of features that need to be added (see the #ToDo's around). Commands added
to queue will be given to the device with a matching DID and then run on said device. 

The commands "new supervisor", "update supervisor", "stop supervisor", and "get all local supervisor" have the added option of "callBack=True". The idea for this 
is so each command should be added to a the DB (not implemented). If callBack is set to True then the device will reply if that command has been successfully 
executed or not. This reply will to a URL that the data Controller will manage. From there the DB will up dated to reflect if the command was successful.
This is not implemented but the device knows how to handle "callBacks" so a little bit of data piping is all that's require on its end - and of course the backend
needs to be set up too.

"""

# ToDo: Link adding commands to the DB
# ToDO: Add a 'get queued commands from DB' link

def makeCommandFormat(body, commandType, callBack=False):
    CF = {
        "commandType": commandType,
        "body": body,
        "callBack": str(callBack)
    }

    if "deviceID" in CF["body"]:
        del CF["body"]["deviceID"]

    return CF


def validateDeviceExists(deviceID):
    try:
        Device.get(Device.deviceID == deviceID)
        logging.debug("Validate DID: DID '{}' Validate".format(deviceID))
        return True
    except peewee.IntegrityError as PTE:
        logging.info("Validate DID: DID '{}' Failed Validation. Integrity Error.\nException: {}\nTraceBack: {}".format(deviceID, PTE, traceback.format_exc()))
    except peewee.OperationalError as POE:
        logging.info("Validate DID: DID '{}' Failed Validation. Operational Error.\nException: {}\nTraceBack: {}".format(deviceID, POE, traceback.format_exc()))
    except Exception as e:
        logging.warning("Validate DID: DID '{}' Failed Validation. Unknown Error.\nException: {}\nTraceBack: {}".format(deviceID, e, traceback.format_exc()))


def validateCommandAuth(token):
    # ToDo: Ensure whoever is trying make commands is authorized to do so
    return True


def validateDeviceAuth(token):
    # ToDo: Ensure whoever is trying to get commands is authorized to do so
    return True


@app.route('/user/device/newSupervisor', methods=["POST"])
def newSupervisor():
    data = request.get_json()
    supervisorType = data.get('supervisorType')
    supervisorID = data.get('supervisorID')
    # Todo: Supervisor ID should be dynamically created
    deviceID = data.get('deviceID')
    customConfig = data.get('customConfig')
    configStatus = True

    if supervisorType is None:
        logging.info("New Supervisor Hit: No Supervisor Type Provided")
        return jsonify(userMessage="Please Provide A Valid Supervisor Type"), 400
    if deviceID is None:
        logging.info("New Supervisor Hit: No DID Type Provided")
        return jsonify(userMessage="Please Provide A Valid Device ID"), 400
    if customConfig is None:
        logging.info("New Supervisor Hit: Using Base Configuration")
        customConfig = str(customConfig)
        configStatus = False

    if not validateDeviceExists(validateDeviceExists(deviceID)):
        logging.info("New Supervisor Hit: Unable To Verify DID Existence")
        return jsonify(userMessage="New Supervisor Hit: Unable To Verify DID Existence"), 400

    body = {"supervisorType": supervisorType, "supervisorID": supervisorID, "deviceID": deviceID, "customConfig": customConfig}
    CF = makeCommandFormat(body=body, commandType="launcher", callBack=True)
    CQ.put(CF)
    logging.debug("New Supervisor Hit: New Supervisor Command Added To Queue. Info --- Supervisor Type: {}, Supervisor ID: {}, DID: {}, Custom Config: {}".format(
            supervisorType, supervisorID, deviceID, configStatus))

    return jsonify(userMessage="New Supervisor Hit: New Supervisor Command Added To Queue"), 200


@app.route('/user/device/updateSupervisor', methods=["POST"])
def updateSupervisor():
    data = request.get_json()
    supervisorType = data.get('supervisorType')
    supervisorID = data.get('supervisorID')
    deviceID = data.get('deviceID')
    customConfig = data.get('customConfig')

    if supervisorType is None:
        logging.info("Update Supervisor Hit: No Supervisor Type Provided")
        return jsonify(userMessage="Please Provide A Valid Supervisor ID"), 400
    if supervisorID is None:
        logging.info("Update Supervisor Hit: No Supervisor ID Provided")
        return jsonify(userMessage="Please Provide A Valid Supervisor Type"), 400
    if deviceID is None:
        logging.info("Update Supervisor Hit: No DID Provided")
        return jsonify(userMessage="Please Provide A Valid Device ID"), 400
    if customConfig is None:
        configStatus = False
        # ToDo: Should check if custom config is currently True - if it is then a custom configuration does not need to passed in as this should 'reset' the super
        logging.info("Update Supervisor Hit: No Custom Configuration Provided")
        return jsonify(userMessage="Please Provide A Valid Custom Configuration"), 400
    else:
        configStatus = True

    if not validateDeviceExists(validateDeviceExists(deviceID)):
        logging.info("Update Supervisor Hit: Unable To Verify DID Existence")
        return jsonify(userMessage="Unable To Verify DID Existence"), 400

    body = {'supervisorType': supervisorType, 'supervisorID': supervisorID, 'customConfig': customConfig, "restart": True}
    CF = makeCommandFormat(body=body, commandType="launcher",callBack=True)
    CQ.put(CF)
    logging.debug("Update Supervisor Hit: Update Supervisor Command Added To Queue. Info --- Supervisor Type: {}, Supervisor ID: {}, DID: {}, Custom Config: {}".format(
            supervisorType, supervisorID, deviceID, configStatus))

    return jsonify(userMessage="Update Supervisor Command Added To Queue."), 200


@app.route('/user/device/stopSupervisor', methods=["POST"])
def stopSupervisor():
    data = request.get_json()
    supervisorID = data.get('supervisorID')
    deviceID = data.get('deviceID')

    if supervisorID is None:
        logging.info("Stop Supervisor Hit: No Supervisor ID Provided")
        return jsonify(userMessage="Please Provide A Valid Supervisor ID"), 400
    if deviceID is None:
        logging.info("Stop Supervisor Hit: No DID Provided")
        return jsonify(userMessage="Please Provide A Valid Device ID"), 400

    if not validateDeviceExists(validateDeviceExists(deviceID)):
        logging.info("Stop Supervisor Hit: Unable To Verify DID Existence")
        return jsonify(userMessage="Unable To Verify DID Existence"), 400

    body = {"supervisorID": supervisorID}
    CF = makeCommandFormat(body=body, commandType="killSupervisor", callBack=True)
    CQ.put(CF)
    logging.debug("Stop Supervisor Hit: Stop Supervisor Command Added To Queue")

    return jsonify(userMessage="Stop Supervisor Command Added To Queue. DID: {}, Supervisor ID: {}".format(deviceID, supervisorID)), 200


@app.route('/user/device/getSupervisorTags', methods=["POST"])
def getSupervisorTags():
    data = request.get_json()
    supervisorID = data.get('supervisorID')
    deviceID = data.get('deviceID')

    if supervisorID is None:
        logging.info("Get Supervisor Tags Hit: No Supervisor ID Provided")
        return jsonify(userMessage="Please Provide A Valid Supervisor ID"), 400
    if deviceID is None:
        logging.info("Get Supervisor Tags Hit: No DID Provided")
        return jsonify(userMessage="Please Provide A Valid Device ID"), 400

    if not validateDeviceExists(validateDeviceExists(deviceID)):
        logging.info("Get Supervisor Tags Hit: Unable To Verify DID Existence")
        return jsonify(userMessage="Unable To Verify DID Existence"), 400

    body = {"supervisorID": supervisorID}
    CF = makeCommandFormat(body=body, commandType="getTags")
    CQ.put(CF)
    logging.debug("Get Supervisor Tags Hit: Get Supervisor Tags Command Added To Queue")

    return jsonify(userMessage="Get Tags Command Added To Queue. DID: {}, Supervisor ID: {}".format(deviceID, supervisorID)), 200


@app.route('/user/device/getSupervisorInfo', methods=["POST"])
def getSupervisorInfo():
    data = request.get_json()
    supervisorID = data.get('supervisorID')
    deviceID = data.get('deviceID')

    if supervisorID is None:
        logging.info("Get Supervisor Info Hit: No Supervisor ID Provided")
        return jsonify(userMessage="Please Provide A Valid Supervisor ID"), 400
    if deviceID is None:
        logging.info("Get Supervisor Info Hit: No DID Provided")
        return jsonify(userMessage="Please Provide A Valid Device ID"), 400

    if not validateDeviceExists(validateDeviceExists(deviceID)):
        logging.info("Get Supervisor Info Hit: Unable To Verify DID Existence")
        return jsonify(userMessage="Unable To Verify DID Existence"), 400

    body = {"supervisorID": supervisorID}
    CF = makeCommandFormat(body=body, commandType="getSupervisorInfo")
    CQ.put(CF)
    logging.debug("Get Supervisor Info Hit: Get Supervisor Info: Get Supervisor Info Command Added To Queue")

    return jsonify(userMessage="Get Supervisor Info Command Added To Queue. DID: {}, Supervisor ID: {}".format(deviceID, supervisorID)), 200


@app.route('/user/device/getAllLocalSupervisors', methods=["POST"])
def getAllLocalSupervisor():
    data = request.get_json()
    deviceID = data.get('deviceID')

    if deviceID is None:
        logging.info("Get All Local Supervisors Hit: No DID Provided")
        return jsonify(userMessage="Please Provide A Valid Device ID"), 400

    if not validateDeviceExists(validateDeviceExists(deviceID)):
        logging.info("Get All Local Supervisors Hit: Unable To Verify DID Existence")
        return jsonify(userMessage="Unable To Verify DID Existence"), 400

    body = str(None)
    CF = makeCommandFormat(body=body, commandType="getAllLocalSupervisor", callBack=True)
    CQ.put(CF)
    logging.debug("Get All Local Supervisors Hit: Get All Local Supervisors: ")

    return jsonify(userMessage="Get ALL Supervisor Info Command Added To Queue"), 200


def generateDeviceCommands():
    # ToDo: Use a pub-sub module for sending commands
    commandList = []
    while not CQ.empty():
        commandList.append(CQ.get())

    return commandList


@app.route('/device/commands/getCommands', methods=["POST"])
def deviceGetCommands():
    deviceID = request.get_json().get('deviceID')

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
        device.commandTimeWindow = datetime.datetime.utcnow() + datetime.timedelta(seconds=device.commandControllerPeriod)
        device.save()
    except Exception as e:
        logging.warning("Get Commands Hit: Could Not Update Device In Data Base. DID: {}\nException: {}\nTraceBack: {}".format(deviceID, e, traceback.format_exc()))
        return jsonify(userMessge="Unable To Update Device In Data Base"), 400

    commandList = generateDeviceCommands()

    if commandList:
        logging.debug("Get Commands  Hit: Returning Commands To DID: {}".format(deviceID))
        return jsonify(userMessage="Returning Commands", commands=commandList), 200
    else:
        logging.debug("Get Commands Hit: No New Commands For DID: {}".format(deviceID))
        return jsonify(userMessage="No Commands To Execute"), 200


if __name__ == '__main__':
    # time.sleep(5)
    app.run(host="0.0.0.0", debug=True, port=8802)
