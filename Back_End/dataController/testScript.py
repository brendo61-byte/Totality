import requests
import datetime

URL = "http://localhost:8801/device/dataPush"


# tests that a 200 is returned when trying to add row in RD
def testAddData():
    body = {
        "data": {
            "TEST": 12345
        },
        "deviceID": 1
    }

    response = requests.post(url=URL, json=body)

    assert response.status_code == 200


# tests that a 400 is returned when trying to add a row in RD w/out a deviceID
def testAddDataDeviceIDFailure():
    body = {
        "data": {
            "TEST": 12345
        }
    }

    response = requests.post(url=URL, json=body)

    assert response.status_code == 400


# tests that a 400 is returned when trying to add a row in RD w a false deviceID
def testAddDataFalseDeviceIDFailure():
    body = {
        "data": {
            "TEST": 12345
        },
        "deviceID": 1234567890
    }

    response = requests.post(url=URL, json=body)

    assert response.status_code == 400


# tests that a 400 is returned when trying to add a row in RD w/out data
def testAddDataDataFailure():
    body = {
        "deviceID": 1
    }

    response = requests.post(url=URL, json=body)

    assert response.status_code == 400


# tests that a 200 is returned when trying to add a row in RD w a non-serializable json format where a 'None' type is present
def testAddDataNonData():
    body = {
        "data": {
            "TEST": None
        },
        "deviceID": 1
    }

    response = requests.post(url=URL, json=body)

    assert response.status_code == 200
