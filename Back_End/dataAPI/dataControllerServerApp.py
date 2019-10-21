from flask import Flask, request, jsonify
# from Back_End.dataAPI.models import *
from models import *

import traceback
import logging
import requests

app = Flask(__name__)

"""
This is the API for data ingestion. This not only means data in terms of readings from senors but also getting information from sensors - like callBacks (see
commandAPI).
"""

logging.basicConfig(level="DEBUG", filename='program.log', filemode='w',
                    format='%(asctime)s - %(levelname)s - %(message)s')


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


@app.route('/device/dataIngestion', methods=["POST"])
def dataPush():
    package = request.get_json()
    payload = package.get('data')
    deviceID = package.get('deviceID')

    if payload is None:
        statement = "Data Push Hit: No Payload Provided"
        logging.info(statement)
        jsonify(userMessage=statement), 400

    if deviceID is None:
        statement = "Data Push Hit: No deviceID Provided"
        logging.info(statement)
        jsonify(userMessage=statement), 400

    if not validateDeviceExists(deviceID=deviceID):
        statement = "Data Push Hit: Unable To Verify DID Existence"
        logging.info(statement)
        return jsonify(userMessage=statement), 400

    try:
        ReliableDelivery.create(payload=payload, deviceOwner=deviceID)
        logging.debug("Data Push Hit: New Entry Into RD")
        return jsonify(userMessage="Payload added to reliable delivery"), 200
    except Exception as e:
        logging.warning("Data Push Hit: Unable To Push Data Into RD.\nException: {}\nTraceBack: {}".format(e,
                                                                                                           traceback.format_exc()))

        return jsonify(userMessage="Unable to push data into RD"), 400


@app.route('/device/callBack', methods=["POST"])
def callBack():
    package = request.get_json()
    payload = package.get('data')
    deviceID = package.get('deviceID')

    if payload is None:
        statement = "Data Push Hit: No Payload Provided"
        logging.info(statement)
        jsonify(userMessage=statement), 400

    if deviceID is None:
        statement = "Data Push Hit: No deviceID Provided"
        logging.info(statement)
        jsonify(userMessage=statement), 400

    if not validateDeviceExists(deviceID=deviceID):
        statement = "Data Push Hit: Unable To Verify DID Existence"
        logging.info(statement)
        return jsonify(userMessage=statement), 400

    status = payload.get("status")
    refID = payload.get("refID")

    if not status == 1 or status == 2:
        statement = "Call Back Hit: Invalid payload value"
        logging.info(statement)
        return jsonify(userMessage=statement), 400

    try:
        entry = Command.get()(Command.refID == refID)
        entry.status = status
        commandID = entry.CommandID
        entry.refID = 0
        entry.save()

        statement = "Command ID: {} callBack with status no. {}".format(commandID, commandID)
        logging.debug(statement)
        return jsonify(userMessage=statement), 200

    except:
        statement = "Call Back Hit: Failed to query database for commands"
        logging.warning(statement)
        return jsonify(userMessage=statement), 400


if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=False, port=8801)
