from flask import Flask, request, jsonify
# from Back_End.dataAPI.models import *
from models import *

import traceback
import logging
import peewee
import random

app = Flask(__name__)

"""
This API is for management of devices. This will include supervisor registration, firmware updates, and base configuration,
monitoring.
"""

logging.basicConfig(level="DEBUG", filename='program.log', filemode='w',
                    format='%(asctime)s - %(levelname)s - %(message)s')


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


def genCommandRefID():
    refID = random.randint(0, 2147483645)
    q = Command.select().where(Command.refID == refID)

    while q.exists():
        refID = random.randint(0, 2147483645)
        q = Command.select().where(Command.refID == refID)

    return refID


def validateDeviceAuth(token):
    # ToDo: Ensure whoever is trying to get commands is authorized to do so
    return True


def validateDeviceExists(deviceID):
    try:
        Device.get(Device.deviceID == deviceID)
        logging.debug("Validate DID: DID '{}' Validate".format(deviceID))
        return True
    except peewee.IntegrityError as PTE:
        logging.info(
            "Validate DID: DID '{}' Failed Validation. Integrity Error.\nException: {}\nTraceBack: {}".format(deviceID,
                                                                                                              PTE,
                                                                                                              traceback.format_exc()))
    except peewee.OperationalError as POE:
        logging.info(
            "Validate DID: DID '{}' Failed Validation. Operational Error.\nException: {}\nTraceBack: {}".format(
                deviceID, POE, traceback.format_exc()))
    except Exception as e:
        logging.warning(
            "Validate DID: DID '{}' Failed Validation. Unknown Error.\nException: {}\nTraceBack: {}".format(deviceID, e,

                                                                                                            traceback.format_exc()))


def genSupervisorRefID():
    refID = random.randint(0, 2147483645)
    q = Supervisor.select().where(Supervisor.refID == refID)

    while q.exists():
        refID = random.randint(0, 2147483645)
        q = Supervisor.select().where(Supervisor.refID == refID)

    return refID


@app.route('/device/management/supervisorRegistration', methods=["POST"])
def supervisorRegistration():
    package = request.get_json()
    data = package.get("data").get("package")

    supervisorType = data.get('supervisorType')
    localID = data.get('localID')
    deviceID = data.get('deviceID')
    customConfig = data.get('customConfig')

    if supervisorType is None:
        logging.info("Supervisor Registration Hit: No Supervisor Type Provided")
        return jsonify(userMessage="Please Provide A Valid Supervisor Type"), 400
    if deviceID is None:
        logging.info("Supervisor Registration Hit: No DID Type Provided")
        return jsonify(userMessage="Please Provide A Valid Device ID"), 400
    if customConfig is None:
        logging.info("Supervisor Registration Hit: Using Base Configuration")

    if not validateDeviceExists(validateDeviceExists(deviceID)):
        statement = "Supervisor Registration Hit: Unable To Verify DID Existence"
        logging.info(statement)
        return jsonify(userMessage=statement), 400

    refID = genSupervisorRefID()
    logging.debug("Supervisor Registration Hit: refID generated: {}".format(refID))

    supervisorID = None
    #ToDo: include local ID into supervisor field - check if supervisor has been registered

    try:
        Supervisor.create(deviceOwner=deviceID, refID=refID, supervisorType=supervisorType,
                          customConfig=str(customConfig))
        # ToDo: Use fsting (python 3.6) - cleaner way of putting variables in strings
        logging.debug("Supervisor Registration Hit: Supervisor Created in DB. RefID: {}".format(refID))

    except Exception as e:
        statement = "Supervisor Registration Hit: Unable to create new supervisor in DB.\nException: {}\nTraceBack: {}".format(
            e, traceback.format_exc())
        logging.info(statement)
        return jsonify(userMesage=statement), 400

    try:
        entry = Supervisor.get(Supervisor.refID == refID)
        supervisorID = entry.supervisorID
        entry.refID = 0
        entry.save()

    except Exception as e:
        statement = "Supervisor Registration Hit: Unable to assign supervisor an ID.\nException: {}\nTraceBack: {}".format(
            e,
            traceback.format_exc())
        logging.info(statement)
        return jsonify(userMessage=statement), 400
        # ToDo: How to handle a new supervisor being created if the command is not passed to the device

    body = {"globalID": supervisorID, "localID": localID}

    CF = makeCommandFormat(callBack=True, body=body, commandType="supervisorGlobalRegistration")
    statement = "Supervisor Registration Hit: Supervisor Has been registered in the database"
    logging.info(statement)
    return jsonify(userMessage=statement, command=CF), 200


if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=False, port=8804)
