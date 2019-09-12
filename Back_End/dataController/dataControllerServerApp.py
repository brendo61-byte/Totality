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


if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=False, port=8801)
