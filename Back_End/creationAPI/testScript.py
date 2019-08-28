import requests

NEW_CUSTOMER = "http://localhost:8803/customer/newCustomer"
DROP_CUSTOMER = "http://localhost:8803/customer/dropCustomer"
GET_CUST_INFO = "http://localhost:8803/customer/getCustomer"
NEW_DEVICE = "http://localhost:8803/device/newDevice"
DROP_DEVICE = "http://localhost:8803/device/dropDevice"
GET_DEV_INFO = "http://localhost:8803/device/getDeviceInfo"


# tests that a 200 is returned when a customer is successfully created
def testCustomerCreation():
    body = {
        "name": "FizzBuzz Inc",
        "address": "1523 Holiday Drive",
        "phone": "314-159-2653",
    }

    response = requests.post(url=NEW_CUSTOMER, json=body)

    assert response.status_code == 200


CID = 1

# tests that a 400 is returned when a customer is created without a Name
def testCustomerCreationNameFail():
    body = {
        "address": "1523 Holiday Drive",
        "phone": "314-159-2653",
        "CID": CID
    }

    response = requests.post(url=NEW_CUSTOMER, json=body)

    assert response.status_code == 400


# tests that a 400 is returned when a customer is created without an address
def testCustomerCreationAddressFail():
    body = {
        "name": "FizzBuzz Inc",
        "phone": "314-159-2653",
        "CID": CID
    }

    response = requests.post(url=NEW_CUSTOMER, json=body)

    assert response.status_code == 400


# tests that a 400 is returned when a customer is created without a Phone
def testCustomerCreationPhoneFail():
    body = {
        "name": "FizzBuzz Inc",
        "address": "1523 Holiday Drive",
        "CID": CID
    }

    response = requests.post(url=NEW_CUSTOMER, json=body)

    assert response.status_code == 400


# tests that a 400 is returned when a customer is created with a name that is already in use
def testCustomerUneiqueError():
    body = {
        "name": "FizzBuzz Inc",
        "address": "1523 Holiday Drive",
        "phone": "314-159-2653",
        "CID": CID
    }

    response = requests.post(url=NEW_CUSTOMER, json=body)

    assert response.status_code == 400


# tests that a 200 is returned when trying to get customer info with a valid CID
def testGetCustomerInfo():
    body = {
        "CID": CID
    }

    response = requests.post(url=GET_CUST_INFO, json=body)

    assert response.status_code == 200


# tests that a 400 is returned when trying to get customer info with an invalid CID
def testGetCustomerInfoCIDFail():
    body = {
    }

    response = requests.post(url=GET_CUST_INFO, json=body)

    assert response.status_code == 200



###################################### BREAK POINT #######################################


# test that a 200 is returned when a device is successfully created
def testDevieCreation():
    body = {
        "name": "Brendon's MEGA Machine",
        "location": "Planet Drron",
        "customerOwner": CID
    }

    response = requests.post(url=NEW_DEVICE, json=body)

    assert response.status_code == 200


# tests that a 400 is returned when trying to make a device when no name is provided
def testDevieCreationNameFail():
    body = {
        "location": "Planet Drron",
        "customerOwner": CID
    }

    response = requests.post(url=NEW_DEVICE, json=body)

    assert response.status_code == 400


# tests that a 400 is returned when trying to make a device when no location is provided
def testDevieCreationLocationFail():
    body = {
        "name": "Brendon's MEGA Machine",
        "customerOwner": CID
    }

    response = requests.post(url=NEW_DEVICE, json=body)

    assert response.status_code == 400


# tests that a 400 is returned when trying to make a device when no customer owner is provided
def testDevieCreationCustomerOwnerFail():
    body = {
        "name": "Brendon's MEGA Machine",
        "location": "Planet Drron"
    }

    response = requests.post(url=NEW_DEVICE, json=body)

    assert response.status_code == 400


# tests that a 400 is returned when trying to make a device when a false CID is provided
def testDevieCreationFalseCustomerOwnerFail():
    body = {
        "name": "Brendon's MEGA Machine",
        "location": "Planet Drron",
        "customerOwner": 1234567890
    }

    response = requests.post(url=NEW_DEVICE, json=body)

    assert response.status_code == 400


DID = 1


# tests that a 200 is returned when trying to get device Info
def testGetDeviceInfo():
    body = {
        "DID": DID
    }

    response = requests.post(url=GET_DEV_INFO, json=body)

    assert response.status_code == 200


# tests that a 400 is returned when trying to get device Info without a DID
def testGetDeviceInfoDIDFail():
    body = {
    }

    response = requests.post(url=GET_DEV_INFO, json=body)

    assert response.status_code == 400


# tests that a 400 is returned when trying to get device Info with a false a DID
def testGetDeviceInfoDIDFalseFail():
    body = {
        "DID": 1234567890
    }

    response = requests.post(url=GET_DEV_INFO, json=body)

    assert response.status_code == 400


################# BREAK POINT #######################
"""
# tests that a 200 is returned when a device is dropped
def testDropDevice():
    body = {
        "DID": 1
    }

    response = requests.post(url=DROP_DEVICE, json=body)

    assert response.status_code == 200


# tests that a 400 is returned when trying to drop a device w/out a DID
def testDropDeviceDIDFail():
    body = {
    }

    response = requests.post(url=DROP_DEVICE, json=body)

    assert response.status_code == 400


# tests that a 400 is returned when trying to drop a device w/ a false DID
def testDropDeviceDIDFalseFail():
    body = {
        "DID": 2435467456
    }

    response = requests.post(url=DROP_DEVICE, json=body)

    assert response.status_code == 400

# tests that a 200 is returned when a customer is dropped
def testDropCustomer():
    body = {
        "CID": CID
    }

    response = requests.post(url=DROP_CUSTOMER, json=body)

    assert response == 200

# tests that a 400 is returned when trying to drop a customer without providing a CID
def testDropCustomerCIDFail():
    body = {
    }

    response = requests.post(url=DROP_CUSTOMER, json=body)

    assert response == 400

# tests that a 400 is returned when trying to drop a customer with a false CID
def testDropCustomerCIDFalseFail():
    body = {
        "CID": 2435467456
    }

    response = requests.post(url=DROP_CUSTOMER, json=body)

    assert response == 400
"""
