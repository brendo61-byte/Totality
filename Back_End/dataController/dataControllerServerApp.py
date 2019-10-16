from flask import Flask, request, jsonify
# from Back_End.dataController.models import *
from models import *

import traceback
import logging

app = Flask(__name__)

"""
This is the API for data ingestion. This not only means data in terms of readings from senors but also getting information from sensors - like callBacks (see
commandController).
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


@app.route('/device/dataPush', methods=["POST"])
def dataPush():
    data = request.get_json()
    payload = data.get('data')
    deviceID = data.get('deviceID')
    deviceType = data.get('deviceType')

    if payload is None:
        logging.info("Data Push Hit: No Payload Provided")
        jsonify(userMessage="Please Provide A Valid Payload"), 400

    if deviceID is None:
        logging.info("Data Push Hit: No deviceID Provided")
        jsonify(userMessage="Please Provide A Valid DID"), 400

    if not validateDeviceExists(deviceID=deviceID):
        logging.info("Data Push Hit: Unable To Verify DID Existence")
        return jsonify(userMessage="Data Push Hit: Unable To Verify DID Existence"), 400



    try:
        ReliableDelivery.create(payload=payload, deviceOwner=deviceID)
        logging.debug("Data Push Hit: New Entry Into RD")
        return jsonify(userMessage="Payload added to reliable delivery"), 200
    except Exception as e:
        logging.warning("Data Push Hit: Unable To Push Data Into RD.\nException: {}\nTraceBack: {}".format(e,
                                                                                                           traceback.format_exc()))
        return jsonify(userMessage="Unable to Push"), 400

@app.route('/device/requestGlobalID')
def requestGlobalID():
    data = request.get_json()
    payload = data.get('data')
    deviceID = data.get('deviceID')
    commandID = data.get('commandID')




@app.route('/device/callBack', methods=["POST"])
def callBack():
    """
    Hey Wes. So look at this!

    You need to provide the a dict with keys of payload, deviceID, and commandID

    Note that payload must be a 1 or 2
    Note that deviceID should be the DID of the sending device
    Note that commandID need to be the commandID - this way we know that command we are talking about

    :return:
    """
    data = request.get_json()
    payload = data.get('data')
    deviceID = data.get('deviceID')
    commandID = data.get('commandID')

    if payload is None:
        logging.info("Call Back Hit: No Payload Provided")
        jsonify(userMessage="Please Provide A Valid Payload"), 400

    if deviceID is None:
        logging.info("Call Back Hit: No deviceID Provided")
        jsonify(userMessage="Please Provide A Valid DID"), 400

    if not payload == 1 or payload == 2:
        logging.info("Call Back Hit: Invalid payload value")
        jsonify(userMessage="Invalid payload"), 400

    if not validateDeviceExists(deviceID=deviceID):
        logging.info("Call Back Hit: Unable To Verify DID Existence")
        return jsonify(userMessage="Unable To Verify DID Existence"), 400

    try:
        q = Command.select().where(Command.commandID == commandID)

        if q.exists():
            for entry in q:
                if payload == 1:
                    entry.status = 1
                if payload == 2:
                    entry.status = 2
                entry.save()

                logging.debug("Command ID: {} callBack with status no. {}".format(commandID, commandID))
                return jsonify(userMessage="Command status updated"), 200
        else:
            logging.info("Call Back Hit: Unable to find command ID entry")
            return jsonify(userMessage="Unable to find command ID"), 400

    except:
        logging.warning("Call Back Hit: Failed to query database for commands")
        return jsonify(userMessage="Unable to query database for commands"), 400



if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=False, port=8801)
