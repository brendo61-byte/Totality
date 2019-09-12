from flask import Flask, request, jsonify
# from Back_End.creationAPI.models import *
from models import *

import logging
import traceback
import datetime
import re

app = Flask(__name__)

"""
This API handles the creation of customers and devices. This also means dropping customers and devices too. The idea is that you have customers and customers own
actual (actual hardware). 
"""

logging.basicConfig(level="DEBUG", filename='program.log', filemode='w',
                    format='%(asctime)s - %(levelname)s - %(message)s')


@app.route('/customer/newCustomer', methods=["POST"])
def newCustomer():
    data = request.get_json()
    name = data.get("name")
    address = data.get("address")
    phone = data.get("phone")
    # ToDo: Ensure that phone number is valid --- TEST THIS --- UPDATE README
    # ToDo: Ensure that address is valid --- This needs Google's APIs --- Pricing is involved

    if name is None:
        logging.info("New Customer Hit: No Name Provided")
        return jsonify(userMessage="Please Provide A Valid Name"), 400
    if address is None:
        logging.info("New Customer Hit: No Address Provided")
        return jsonify(userMessage="Please Provide A Valid Address"), 400
    if phone is None or not validPhoneNumber(phone_nuber=phone):
        logging.info("New Customer Hit: No Phone Provided")
        return jsonify(userMessage="Please Provide A Valid Phone Number"), 400

    try:
        Customer.get(Customer.name == name)
        logging.info("New Customer Hit: Name Integrity Failed")
        return jsonify(userMessage="That Customer Name Already Exists"), 400
    except:
        logging.debug("New Customer Hit:. Name Integrity Passed")
        pass

    try:
        Customer.create(name=name, address=address, phone=phone)
        logging.info("New Customer Hit: Success. New Customer Has Been Created. Name: {}".format(name))
        return jsonify(userMessage="Customer Has Been Created"), 200
    except Exception as e:
        logging.warning(
            "New Customer Hit: Unable To Create Customer In DB.\nException: {}\nTrackBack: {}".format(e, traceback))
        return jsonify(userMessage="Invalid Request"), 400


def validPhoneNumber(phone_nuber):
    pattern = re.compile("^[\dA-Z]{3}-[\dA-Z]{3}-[\dA-Z]{4}$", re.IGNORECASE)
    return pattern.match(phone_nuber) is not None


@app.route('/customer/dropCustomer', methods=["POST"])
def dropCustomer():
    CID = request.get_json().get("CID")

    if CID is None:
        logging.info("Drop Customer Hit: No CID Provided")
        return jsonify(usserMessage="Please Provide A Valid CID")

    try:
        customerToDrop = Customer.get(Customer.customerID == CID)
        customerToDrop.delete_instance(recursive=True)
        logging.info("Drop Customer Hit: Customer Has Been Deleted. Customer ID: {}".format(CID))
        return jsonify(userMessage="Customer Has Been Deleted. All Associated Devices Removed")
    except Exception as e:
        logging.warning("Drop Customer Hit: Unable To Drop Customer. CID: {}.\nException: {}\nTraceBack".format(CID, e,
                                                                                                                traceback.format_exc()))
        return jsonify(userMessage="Please Provide A True CID")


@app.route('/customer/getCustomer', methods=["POST"])
def getCustomerInfo():
    CID = request.get_json().get("CID")

    if CID is None:
        logging.info("Get Customer Hit: No CID Provided")
        return jsonify(usserMessage="Please Provide A Valid CID")

    try:
        customerToGetInfo = Customer.get(Customer.customerID == CID)
        body = {
            "name": customerToGetInfo.name,
            "address": customerToGetInfo.address,
            "phone": customerToGetInfo.phone
        }
        logging.debug("Get Customer Hit: Get Customer Info Request Completed. CID: {}".format(CID))
        return jsonify(userMessage=body), 200
    except Exception as e:
        logging.warning(
            "Get Customer Hit: Unable To Get Customer Info. CID: {}\nException: {}\nTraceBack: {}".format(CID, e,
                                                                                                          traceback.format_exc()))
        return jsonify(userMessage="Please Provide A Valid CID"), 400


@app.route('/device/newDevice', methods=["POST"])
def newDevice():
    data = request.get_json()
    name = data.get("name")
    location = data.get("location")
    latitude = data.get("latitude")
    longitude = data.get("longitude")
    customerOwner = data.get("customerOwner")

    dataControllerPeriod = data.get("dataControllerPeriod", 5)
    commandControllerPeriod = data.get("commandControllerPeriod", 5)
    commandTimeWindow = datetime.datetime.utcnow() + datetime.timedelta(seconds=commandControllerPeriod)

    if name is None:
        logging.info("New Device Hit: No Name Provided")
        return jsonify(userMessage="Please Provide A Valid Name"), 400
    if location is None:
        logging.info("New Device Hit: No Location Provided")
        return jsonify(userMessage="Please Provide A Valid Location"), 400
    if customerOwner is None:
        logging.info("New Device Hit: No Customer Owner Provided")
        return jsonify(userMessage="Please Provide A Valid Customer Owner"), 400

    try:
        Device.create(name=name, location=location, latitude=latitude, longitude=longitude,
                      dataControllerPeriod=dataControllerPeriod,
                      commandControllerPeriod=commandControllerPeriod, commandTimeWindow=commandTimeWindow,
                      customerOwner=customerOwner)
        logging.info("New Device Hit: Success. New Device Has Been Created. Name: {}".format(name))
        return jsonify(userMessage="Successful Device Creation."), 200
    except Exception as e:
        logging.warning("Error In Device Creation.\nException: {}\nTraceBack: {}".format(e, traceback.format_exc()))
        return jsonify(userMessage="Error In Device Creation"), 400


@app.route('/device/dropDevice', methods=["POST"])
def dropDevice():
    DID = request.get_json().get("DID")

    if DID is None:
        logging.info("Drop Device Hit: No DID Provided")
        return jsonify(userMessage="Please Provide A Valid Device ID")

    try:
        device = Device.get(Device.deviceID == DID)
        device.delete_instance()
        # ToDo: Send a shutdown command to the device? --- Team Question!
        logging.info("Drop Device Hit: Device Has Been Deleted. DID: {}".format(DID))
        return jsonify(userMessage="Device Has Been Deleted")
    except Exception as e:
        logging.warning("Drop Device Hit: Unable To Delete Device. DID: {}\nException: {}\nTraceBack: {}".format(DID, e,
                                                                                                                 traceback.format_exc()))
        return jsonify(userMessage="Please Provide A True Device ID")


@app.route('/device/getDeviceInfo', methods=["POST"])
def getDeviceInfo():
    DID = request.get_json().get("DID")

    if DID is None:
        logging.info("Get Device Info Hit: No DID Provided")
        return jsonify(userMessage="Please Provide A Valid Device ID"), 400

    try:
        device = Device.get(Device.deviceID == DID)
        body = {
            "name": device.name,
            "location": device.location,
            "latitude": device.latitude,
            "longitude": device.longitude,
            "customerOwner": device.customerOwner.customerID,
            "dataControllerPeriod": device.dataControllerPeriod,
            "commandControllerPeriod": device.commandControllerPeriod,
            "missedCommands": device.missedCommands,
            "ccommandTimeWindow": device.commandTimeWindow.strftime("%m/%d/%Y, %H:%M:%S"),
            "status": device.status
        }

        for key in body:
            if key is None:
                body[key] = "None"

        logging.debug("Get Device Info Hit: Get Device Info Request Completed. DID: {}".format(DID))
        return jsonify(userMessage=body), 200
    except Exception as e:
        logging.warning(
            "Get Device Info Hit: Unable To Get Customer Info. DID: {}\nException: {}\nTraceBack: {}".format(DID, e,
                                                                                                             traceback.format_exc()))
        return jsonify(userMessage="Please Provide A True Device ID"), 400


if __name__ == '__main__':
    # time.sleep(5)
    app.run(host="0.0.0.0", debug=True, port=8803)
