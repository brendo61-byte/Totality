from flask import Flask, request, jsonify
from models import *

import logging
import datetime
import traceback
import secrets

app = Flask(__name__)

logging.basicConfig(level="DEBUG", filename='program.log', filemode='w',
                    format='%(asctime)s - %(levelname)s - %(message)s')


@app.route('/keyAPI/authenticateSessionKey', methods=["POST"])
def authenticateSessionKey():
    key = request.get_json().get("key")

    try:
        sessionEntry = SessionKeys.get(SessionKeys.sessionKey == key)
        CID = sessionEntry.customerOwner

        if datetime.datetime.utcnow().timestamp() < int("{}".format(sessionEntry.endLifeTime)):
            logging.debug("CID {} authenticated session key".format(CID))
            return jsonify(usermessage="Session Key Authenticated", data=int("{}".format(CID))), 200

        else:
            sessionEntry.delete_instance(recursive=True)
            logging.info("CID {} session key has expired. Removing expired key".format(CID))
            return jsonify(usermessage="Session Key Has Expired", data=False), 400

    except Exception as e:
        logging.warning("Failed to parse database for authentication\nException: {}\nTraceBack: {}".format(e, traceback.format_exc()))
        return jsonify(usermessage="Failed To Authenticate", data=False), 400


@app.route('/keyAPI/deviceOwnerShip', methods=["POST"])
def deviceOwnerShip():
    CID = request.get_json().get("CID")
    DID = request.get_json().get("DID")

    try:
        fetchedCID = Device.get(Device.deviceID == DID).customerOwner
        if int("{}".format(fetchedCID)) == CID:
            logging.debug("CID {} authorized to access DID {}".format(CID, DID))
            return jsonify(usermessage="Ownership check passed", data=True), 200
        else:
            statement = "Ownership check failed"
            logging.info(statement + ". CID {} tried to access non-associated device ID {}".format(CID, DID))
            return jsonify(usermessage=statement, data=False), 400
    except Exception as e:
        statement = "Failed to query database"
        logging.warning(statement + "\nException: {}\nTraceBack".format(e, traceback.format_exc()))
        return jsonify(usermessage=statement, data=False), 400


@app.route('/keyAPI/generateSessionKey', methods=["POST"])
def generateSessionKey():
    customerName = request.get_json().get("name")
    key = request.get_json().get("key")
    #ToDo: Remove redundant/expired session Keys

    if customerName is None:
        logging.debug("Login Hit: No customerName Provided")
        return jsonify(userMessage="Please Provide A Valid Customer Name", data=False), 400

    if key is None:
        logging.debug("Login Hit: No customerName Provided")
        return jsonify(userMessage="Please Provide A Valid Login Key", data=False), 400

    try:
        ownerID = CustomerKeys.get(CustomerKeys.key == key).customerOwner
        if Customer.get(Customer.customerID == ownerID).name == customerName:
            sessionKey = secrets.token_urlsafe()
            expiration = datetime.datetime.utcnow().timestamp() + 3600
            # Todo: Session Key duration should be read in from a configuration file

            SessionKeys.create(sessionKey=sessionKey, customerOwner=ownerID, endLifeTime=expiration)

            logging.info("CID no. {}, has logged in.".format(ownerID))
            return jsonify(userMessage="Customer has logged in", data=sessionKey), 200
        else:
            return jsonify(userMessage="Customer Login Failed. Incorrect key", data=False), 400
            # ToDo: When would this case occur?

    except Exception as e:
        statement = "Unable to parse database to login customer"
        logging.warning(
            statement + " {}\nException: {}\nTraceBack: {}".format(customerName, e, traceback.format_exc()))
        return jsonify(userMessage=statement, data=False), 400


if __name__ == '__main__':
    # time.sleep(5)
    app.run(host="0.0.0.0", debug=True, port=8805)
