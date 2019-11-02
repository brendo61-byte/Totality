from flask import Flask, request, jsonify
# from Back_End.creationAPI.models import *
from models import *

import logging
import traceback
import datetime
import re
import secrets

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
        CID = Customer.get(Customer.name == name).customerID

        key = secrets.token_urlsafe()

        CustomerKeys.create(key=key, customerOwner=CID)

        logging.info("New Customer Hit: Success. New Customer Has Been Created. Name: {}".format(name))
        return jsonify(
            userMessage="Customer Has Been Created\nCustomer ID: {}\nLogin Key: {}".format(CID, key)), 200
    except Exception as e:
        logging.warning(
            "New Customer Hit: Unable To Create Customer In DB.\nException: {}\nTrackBack: {}".format(e, traceback))
        return jsonify(userMessage="Invalid Request"), 400


def validPhoneNumber(phone_nuber):
    pattern = re.compile("^[\dA-Z]{3}-[\dA-Z]{3}-[\dA-Z]{4}$", re.IGNORECASE)
    return pattern.match(phone_nuber) is not None


@app.route('/customer/login', methods=["POST"])
def customerLogin():
    customerName = request.get_json().get("name")
    key = request.get_json().get("key")

    if customerName is None:
        logging.info("Login Hit: No customerName Provided")
        return jsonify(userMessage="Please Provide A Valid Customer Name"), 400

    if key is None:
        logging.info("Login Hit: No customerName Provided")
        return jsonify(userMessage="Please Provide A Valid Login Key"), 400

    try:
        ownerID = CustomerKeys.get(CustomerKeys.key == key).customerOwner
        if Customer.get(Customer.customerID == ownerID).name == customerName:
            sessionKey = secrets.token_urlsafe()
            expiration = datetime.datetime.utcnow().timestamp() + 3600
            # Todo: Session Key duration should be read in from a configuration file

            SessionKeys.create(sessionKey=sessionKey, customerOwner=ownerID, endLifeTime=expiration)

            logging.info("Login Hit: {}, CID no. {}, has logged in.")

            return jsonify(userMessage="Login Successful.\nSessionKey: {}".format(sessionKey))
    except Exception as e:
        logging.info(
            "Login Hit: Unable to log a customer in.\nException: {}\nTraceBack: {}".format(e, traceback.format_exc()))
        return jsonify(userMessage="Unable to log Customer in"), 400


def authenticateSessionKey(key):
    try:
        sessionEntry = SessionKeys.get(SessionKeys.sessionKey == key)

        if datetime.datetime.utcnow().timestamp() < sessionEntry.endLifeTime:
            CID = sessionEntry.customerOwner
            return CID
    except:
        return False


@app.route('/customer/dropCustomer', methods=["POST"])
def dropCustomer():
    key = request.get_json().get("key")

    CID = authenticateSessionKey(key=key)

    if not CID:
        logging.info("Drop Customer Hit: Unable to validate sessionKey")
        return jsonify(userMessage="Unable to validate Session Key"), 400

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
    key = request.get_json().get("key")

    CID = authenticateSessionKey(key=key)

    if not CID:
        logging.info("Drop Customer Hit: Unable to validate sessionKey")
        return jsonify(userMessage="Unable to validate Session Key"), 400

    if CID is None:
        logging.info("Get Customer Hit: No CID Provided")
        return jsonify(userMessage="Please Provide A Valid CID"), 400

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

# ToDo: Need a 'list all devices URL'
@app.route('/device/newDevice', methods=["POST"])
def newDevice():
    key = request.get_json().get("key")

    CID = authenticateSessionKey(key=key)

    if not CID:
        logging.info("Drop Customer Hit: Unable to validate sessionKey")
        return jsonify(userMessage="Unable to validate Session Key"), 400

    data = request.get_json()
    name = data.get("name")
    location = data.get("location")
    latitude = data.get("latitude")
    longitude = data.get("longitude")

    dataControllerPeriod = data.get("dataControllerPeriod", 5)
    commandControllerPeriod = data.get("commandControllerPeriod", 5)
    commandTimeWindow = datetime.datetime.utcnow() + datetime.timedelta(seconds=commandControllerPeriod)

    if name is None:
        logging.info("New Device Hit: No Name Provided")
        return jsonify(userMessage="Please Provide A Valid Name"), 400
    if location is None:
        logging.info("New Device Hit: No Location Provided")
        return jsonify(userMessage="Please Provide A Valid Location"), 400

    try:
        Device.create(name=name, location=location, latitude=latitude, longitude=longitude,
                      dataControllerPeriod=dataControllerPeriod,
                      commandControllerPeriod=commandControllerPeriod, commandTimeWindow=commandTimeWindow,
                      customerOwner=CID)
        logging.info(
            "New Device Hit: Success. New Device Has Been Created. Name: {}\nUnder Customer ID: {}".format(name, CID))
        return jsonify(userMessage="Successful Device Creation."), 200
    except Exception as e:
        logging.warning("Error In Device Creation.\nException: {}\nTraceBack: {}".format(e, traceback.format_exc()))
        return jsonify(userMessage="Error In Device Creation"), 400


def deviceOwnerShip(CID, DID):
    try:
        fetchedCID = Device.get(Device.deviceID == DID).customerOwner
        if fetchedCID == CID:
            return True
    except:
        return False


@app.route('/device/dropDevice', methods=["POST"])
def dropDevice():
    DID = request.get_json().get("DID")
    key = request.get_json().get("key")

    CID = authenticateSessionKey(key=key)

    if not CID:
        logging.info("Drop Customer Hit: Unable to validate sessionKey")
        return jsonify(userMessage="Unable to validate Session Key"), 400

    if DID is None:
        logging.info("Drop Device Hit: No DID Provided")
        return jsonify(userMessage="Please Provide A Valid Device ID"), 400

    if not deviceOwnerShip(CID=CID, DID=DID):
        logging.info("Device Drop Hit: Unauthorized access on DID {} from CID {}".format(DID, CID))

    try:
        device = Device.get(Device.deviceID == DID)
        device.delete_instance(recursive=True)
        # ToDo: Send a shutdown command to the device? --- Team Question!
        logging.info("Drop Device Hit: Device Has Been Deleted. DID: {}".format(DID))
        return jsonify(userMessage="Device Has Been Deleted"), 200
    except Exception as e:
        logging.warning("Drop Device Hit: Unable To Delete Device. DID: {}\nException: {}\nTraceBack: {}".format(DID, e,
                                                                                                                 traceback.format_exc()))
        return jsonify(userMessage="Please Provide A True Device ID"), 400


@app.route('/device/getDeviceInfo', methods=["POST"])
def getDeviceInfo():
    DID = request.get_json().get("DID")
    key = request.get_json().get("key")

    CID = authenticateSessionKey(key=key)

    if not CID:
        logging.info("Drop Customer Hit: Unable to validate sessionKey")
        return jsonify(userMessage="Unable to validate Session Key"), 400

    if DID is None:
        logging.info("Get Device Info Hit: No DID Provided")
        return jsonify(userMessage="Please Provide A Valid Device ID"), 400

    if not deviceOwnerShip(CID=CID, DID=DID):
        logging.info("Device Info Hit: Unauthorized access on DID {} from CID {}".format(DID, CID))

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
            "commandTimeWindow": device.commandTimeWindow.strftime("%m/%d/%Y, %H:%M:%S"),
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
