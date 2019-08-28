# Back End
## Running The Back End
- To start the docker-network and run the back-end preform a ./m start
- For info on what ./m can do execute the command ./m help
## Intro
The back-end is separate from the device level because the device level is built to run without a back-end. As the backend stands
right now it is broken into 3 parts:
## 1) Command Controller (CC)
 - The CC is an API for customers to push commands and interface remotely to their devices.
 - In the database (see models in CC) under the device table there are columns called "timeOfLastCheckIn" and "commandTimeWindow",
 This is used to track the "heart beat" of the device. Meaning that the device is configured to check in with the CC every N
 seconds. So if it misses a chick in then a "heart beat" has been missed - i.e. commandTimeWindow > timeOfLastCheckIn + N.
 CC will update these two fields every time the device checks in to see if new commands are needed.
    - Note that the CC does not change the "status" field in the DB if commandTimeWindow > timeOfLastCheckIn + N.
## 2) Data Controller (DC)
 - The DC will ingest all information from the device. This could be readings from sensors, callBacks (see /commandController)
 - The DC puts all readings from sensor into a reliable delivery table in the DB
## 3) Creation API (CAPI)
 - The CAPI will create customers. In turn those customers will be able to create devices associated to them.
 - The creation API cannot create supervisors - this is done by the CC.