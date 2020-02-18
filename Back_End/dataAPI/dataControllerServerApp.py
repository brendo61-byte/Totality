from flask import Flask, request, jsonify, send_file
from models import *

import traceback
import logging
import csv
import datetime

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


@app.route('/data/device/getAllDeviceData/<int:deviceID>', methods=["GET"])
def collectData(deviceID):
    if deviceID is None:
        statement = "Data Push Hit: No deviceID Provided"
        logging.info(statement)
        return jsonify(userMessage=statement), 400

    if not validateDeviceExists(deviceID=deviceID):
        statement = "Data Push Hit: Unable To Verify DID Existence"
        logging.info(statement)
        return jsonify(userMessage=statement), 400

    try:
        logging.debug("Data being collected from sensorID {}".format(deviceID))

        rawData = ReliableDelivery.select().where(ReliableDelivery.deviceOwner == deviceID)
        formattedData = []

        for entry in rawData:
            tempData = {
                "timeStamp": entry.timeStamp,
                "dataType": entry.dataType,
                "units": entry.units,
                "data": entry.data,
                "sensorType": entry.sensorType,
                "sensorID": entry.sensorID_id
            }

            formattedData.append(tempData)

        fileName = "deviceID:{}_on_{}.csv".format(deviceID, datetime.datetime.now().strftime("%m/%d/%Y-%H:%M:%S"))
        fieldNames = ["timeStamp", "dataType", "units", "data", "sensorType", "sensorID"]

        with open('data.csv', 'w') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=fieldNames)
            writer.writeheader()
            writer.writerows(formattedData)

        # logging.debug("\n\n\nFormatted Data: {}\n\nFile Name: {}\n\nField Names: {}\n\n\n".format(formattedData, fileName, feildNames))

        return send_file("data.csv", attachment_filename=fileName)

    except Exception as e:
        statement = "Unable to return csv file."

        logging.info("statement\nException: {}\nTraceBack: {}".format(e, traceback.format_exc()))
        return jsonify(userMessage=statement), 400


@app.route('/data/device/dataIngestion', methods=["POST"])
def dataPush():
    package = request.get_json()
    data = package.get('data').get('package')
    payload = package.get('data')
    deviceID = package.get('deviceID')
    packageType = package.get("packageType")

    if data is None:
        statement = "Data Push Hit: No Payload Provided"
        logging.info(statement)
        return jsonify(userMessage=statement), 400

    if deviceID is None:
        statement = "Data Push Hit: No deviceID Provided"
        logging.info(statement)
        return jsonify(userMessage=statement), 400

    if not packageType == "dataPush" or not packageType == "callBack":
        statement = "Data Push Hit: No PackageType"
        logging.info(statement)
        return jsonify(userMessage=statement), 400

    if not validateDeviceExists(deviceID=deviceID):
        statement = "Data Push Hit: Unable To Verify DID Existence"
        logging.info(statement)
        return jsonify(userMessage=statement), 400

    logging.debug("\nDATA: {}\nTIMESTAMP: {}\n".format(data, data.get("timeStamp")))

    if packageType == "dataPush":
        dataPush(data=data, deviceID=deviceID)

    elif packageType == "dataPush":
        callBack(payload=payload)


def dataPush(data, deviceID):
    try:
        ReliableDelivery.create(timeStamp=data.get("timeStamp"), dataType=data.get("dataType"), units=data.get("units"), data=data.get("data"), deviceOwner=deviceID,
                                sensorType=data.get("sensorType"), sensorID=data.get("sensorID"))
        logging.debug("Data Push Hit: New Entry Into RD")
        return jsonify(userMessage="Payload added to reliable delivery"), 200
    except Exception as e:
        logging.warning("Data Push Hit: Unable To Push Data Into RD.\nException: {}\nTraceBack: {}".format(e,
                                                                                                           traceback.format_exc()))

        return jsonify(userMessage="Unable to push data into RD"), 400


def callBack(payload):
    # payload = package.get('data')

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

    except Exception:
        statement = "Call Back Hit: Failed to query database for commands"
        logging.warning(statement)
        return jsonify(userMessage=statement), 400


if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True, port=8999)
