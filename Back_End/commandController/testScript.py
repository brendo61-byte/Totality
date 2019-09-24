import requests

NEW_SUPERVISOR = "http://localhost:8802/user/device/newSupervisor"
UPDATE_SUPERVISOR = "http://localhost:8802/user/device/updateSupervisor"
STOP_SUPERVISOR = "http://localhost:8802/user/device/stopSupervisor"
GET_TAGS = "http://localhost:8802/user/device/getSupervisorTags"
GET_SUPERVISOR_INFO = "http://localhost:8802/user/device/getSupervisorInfo"
GET_ALL_SUPERVISOR_INFO = "http://localhost:8802/user/device/getAllLocalSupervisors"
GET_COMMANDS = "http://localhost:8802/device/commands/getCommands"


# ToDo: All tests will need to soon deal with validation/tokens for security

### TESTS FOR NEW supervisor ###

# tests that a 200 is returned when adding new supervisor command
def testNewSupervisor():
    body = {
        "supervisorType": "intMaker",
        "deviceID": 1
    }
    response = requests.post(url=NEW_SUPERVISOR, json=body)
    assert response.status_code == 200


# tests that a 400 is returned when a supervisorType is not included in body
def testNewSupervisorSupervisorTypeFailure():
    body = {
        "deviceID": 1
    }
    response = requests.post(url=NEW_SUPERVISOR, json=body)

    assert response.status_code == 400


# tests that a 400 is returned when a false deviceID included in the body
def testNewSupervisorFalseDeviceIdFailure():
    body = {
        "supervisorType": "intMaker",
        "deviceID": 1234567890
    }
    response = requests.post(url=NEW_SUPERVISOR, json=body)

    assert response.status_code == 400


### TESTS FOR UPDATE supervisor ###

# tests that a 200 is returned when tyring to update a supervisor
def testUpdateSupervisor():
    body = {
        "supervisorType": "intMaker",
        "supervisorID": 1,
        "deviceID": 1,
        "customConfig": {
            "supervisorName": "Little Thanos"
        }
    }

    response = requests.post(url=UPDATE_SUPERVISOR, json=body)

    assert response.status_code == 200


# tests that a 400 is returned when trying to update a supervisor with a false ID
def testUpdateSupervisorFalseSupervisorID():
    body = {
        "supervisorType": "intMaker",
        "supervisorID": 123456789,
        "deviceID": 1,
        "customConfig": {
            "supervisorName": "Little Thanos"
        }
    }

    response = requests.post(url=UPDATE_SUPERVISOR, json=body)

    assert response.status_code == 400


# tests that a 400 is returned when tyring to update a supervisor with a false device ID
def testUpdateSupervisorFalseDeviceIDFailure():
    body = {
        "supervisorType": "intMaker",
        "supervisorID": 1,
        "deviceID": 1234567890,
        "customConfig": {
            "supervisorName": "Little Thanos"
        }
    }

    response = requests.post(url=UPDATE_SUPERVISOR, json=body)

    assert response.status_code == 400


# tests that a 400 is returned when supervisorType is None
def testUpdateSupervisorSupervisorTypeFailure():
    body = {
        "supervisorID": 1,
        "deviceID": 1,
        "customConfig": {
            "supervisorName": "Little Thanos"
        }
    }

    response = requests.post(url=UPDATE_SUPERVISOR, json=body)

    assert response.status_code == 400


# tests that a 400 is returned when supervisorID is None
def testUpdateSupervisorSupervisorIDFailure():
    body = {
        "supervisorType": "intMaker",
        "deviceID": 1,
        "customConfig": {
            "supervisorName": "Little Thanos"
        }
    }

    response = requests.post(url=UPDATE_SUPERVISOR, json=body)

    assert response.status_code == 400


# tests that a 400 is returned when a deviceID is None
def testUpdateSupervisorDeviceIDFailure():
    body = {
        "supervisorType": "intMaker",
        "supervisorID": 1,
        "customConfig": {
            "supervisorName": "Little Thanos"
        }
    }

    response = requests.post(url=UPDATE_SUPERVISOR, json=body)

    assert response.status_code == 400


# tests that a 400 is returned when a customConfig is None
def testUpdateSupervisorCustomConfigFailure():
    body = {
        "supervisorType": "intMaker",
        "supervisorID": 1,
        "deviceID": 1
    }

    response = requests.post(url=UPDATE_SUPERVISOR, json=body)

    assert response.status_code == 400


### TESTS FOR STOP supervisor ##

# tests that a 200 is returned for supervisor stop command
def testStopSupervisor():
    body = {
        "supervisorID": 1,
        "deviceID": 1
    }

    response = requests.post(url=STOP_SUPERVISOR, json=body)

    assert response.status_code == 200


# tests that a 400 is returned for supervisor stop command when a false deviceId is provided
def testStopSupervisorFalseDeviceID():
    body = {
        "supervisorID": 5,
        "deviceID": 1234567890
    }

    response = requests.post(url=STOP_SUPERVISOR, json=body)

    assert response.status_code == 400


# tests that a 400 is returned when supervisor ID is None
def testStopSupervisorIDFailure():
    body = {
        "deviceID": 1
    }

    response = requests.post(url=STOP_SUPERVISOR, json=body)

    assert response.status_code == 400


# tests that a 400 is returned for supervisor stop command when deviceID is None
def testStopSupervisordeviceIDFailure():
    body = {
        "supervisorID": 5,
    }

    response = requests.post(url=STOP_SUPERVISOR, json=body)

    assert response.status_code == 400


### TESTS FOR GET TAGS ###

# tests that a 200 is returned for get tags
def testGetSupervisorTags():
    body = {
        "supervisorID": 1,
        "deviceID": 1
    }

    response = requests.post(url=GET_TAGS, json=body)

    assert response.status_code == 200


# tests that a 400 is returned with a false supervisor ID
def testGetSupervisorTagsFalseSupervisorID():
    body = {
        "supervisorID": 123456789,
        "deviceID": 1
    }

    response = requests.post(url=GET_TAGS, json=body)

    assert response.status_code == 400


# tests that a 400 is returned when supervisor ID is None
def testGetSupervisorTagsIDFailure():
    body = {
        "supervisorID": 1
    }

    response = requests.post(url=GET_TAGS, json=body)

    assert response.status_code == 400


# tests that a 400 is returned for get tags when deviceID is None
def testGetSupervisorTagsDeviceIDFailure():
    body = {
        "deviceID": 1
    }

    response = requests.post(url=GET_TAGS, json=body)

    assert response.status_code == 400


### TEST FOR GET SUPERVISOR INFO ###

# tests that a 200 is returned for supervisor stop command
def testGetSupervisorInfo():
    body = {
        "supervisorID": 1,
        "deviceID": 1
    }

    response = requests.post(url=GET_SUPERVISOR_INFO, json=body)

    assert response.status_code == 200

# tests that a 400 is returned with a false Supervisor ID
def testGetSupervisorInfoFalseSupervisorID():
    body = {
        "supervisorID": 123456789,
        "deviceID": 1
    }

    response = requests.post(url=GET_SUPERVISOR_INFO, json=body)

    assert response.status_code == 400

# tests that a 400 is returned for supervisor stop command
def testGetSupervisorInfoFalseDeviceIDFail():
    body = {
        "supervisorID": 1,
        "deviceID": 1234567890
    }

    response = requests.post(url=GET_SUPERVISOR_INFO, json=body)

    assert response.status_code == 400


# tests that a 400 is returned when supervisor ID is None
def testGetSupervisorInfoIDFailure():
    body = {
        "deviceID": 1
    }
    response = requests.post(url=GET_SUPERVISOR_INFO, json=body)

    assert response.status_code == 400


# tests that a 400 is returned for supervisor stop command when deviceID is None
def testGetSupervisorInfoDeviceIdFailure():
    body = {
        "supervisorID": 1,
    }

    response = requests.post(url=GET_SUPERVISOR_INFO, json=body)

    assert response.status_code == 400


### TEST GET ALL LOCAL SUPERVISORS ###

# tests that a 200 is returned when all local Supervisors are polled
def testGetAllLocalSupervisors():
    body = {
        "deviceID": 1,
    }
    response = requests.post(url=GET_ALL_SUPERVISOR_INFO, json=body)

    assert response.status_code == 200


# tests that a 400 is returned when all local Supervisors are polled with a false DeviceID
def testGetAllLocalSupervisorsFalseDeviceIDFailure():
    body = {
        "deviceID": 1234567890,
    }
    response = requests.post(url=GET_ALL_SUPERVISOR_INFO, json=body)

    assert response.status_code == 400


# tests that a 200 is returned when all local Supervisors are polled
def testGetAllLocalSupervisorsDeviceIdFailure():
    body = {
    }
    response = requests.post(url=GET_ALL_SUPERVISOR_INFO, json=body)

    assert response.status_code == 400


### TEST GET COMMANDS ###

# tests that a 200 is returned when commands are pulled from DB
def testGetCommands():
    body = {
        "deviceID": 1
    }
    response = requests.post(url=GET_COMMANDS, json=body)

    assert response.status_code == 200


# tests that a 400 is returned when commands all pulled from DB with a false devideID passed in
def testGetCommandsFalseDEviceIDFailure():
    body = {
        "deviceID": 1234567890
    }
    response = requests.post(url=GET_COMMANDS, json=body)

    assert response.status_code == 400


# tests that a 400 is returned when commands are pulled from DB w/out a deviceID
def testGetCommandsDeviceIdFailure():
    body = {
    }
    response = requests.post(url=GET_COMMANDS, json=body)

    assert response.status_code == 400
