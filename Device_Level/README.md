#Totality Documentation
This REAME me is for Device_Level Info Only!

See ../Back_End/README.md for documentation on the back end... This was done deliberately because the device does not need a
back end to operate.

As of (7-19-19) The README is: 100% Up-To-Date

## Intro
Totality is a general usage platform that can be utilized for any IoT project.
The general idea is that there are customers, who own devices, those devices operate supervisors, and supervisors
communicate with sensors connected to the device. This documentation is for all things that operate at the
device and supervisor levels.

The script "launchPad" will begin this program and data logged will locally show up in "Local_Data/".
As well a log file will appear under "Totality/" will all relevant info on what is happening. The backend is not needed
to be operational as the device level was designed to operate independent of any network connection. If the backend is 
running then pushing data, and pulled new commands becomes available (read below).

See below (at bottom) for more info on launcher.

Do note: NO security features have been implemented.

## Getting Started
There are a few elements that need to be understood about the structure of the code before moving forward.

- supervisors: supervisors are an object that communicate with a sensor to collect data. Each supervisor operates as
its own thread and can be accessed when needed. Each supervisor as a base configuration that but custom
configurations can be implemented too (see Framework/Base_supervisor_Config_Files). Each supervisor has a unique
ID.

- Manager: The Manager is a class that is reasonable for spawning supervisors and communicating to them (see
Managers/deviceManager). The Manager is the middle man for anything that wants to talk to a supervisor. It can
access a supervisor by having the proper supervisorID

- Launchers: When the program is run the launcher will start any supervisors in the deviceConfig.json file
(see Framework/Totality_Config). These supervisors can either have base or custom configurations. The purpose of the
Launcher is so that when a device is placed in the field and boots it will start all necessary supervisors.

- Controllers: Controllers operate at the highest level. There are two controllers and each runs in its
own thread:

    1) Command Control: This controller will periodically check with a cloud server to see if any new 
    commands need to be run locally.
        - When POSTing to the cloud for commands the device will identify its self (again by a unique deviceID
        or DID). The cloud will see if any commands are in a queue for that device and return said commands.
        - Currently, cloud pulled commands can: spawn a new supervisor, update a supervisors, stop a supervisor,
        get info about a supervisor, and get a list of all running supervisors.
        
    2) Data Controller: This is responsible for storing data. All data will be stored locally under the
    Local_Data directory. At this time data can also be pushed into a mySQL DB under a "reliable delivery" table.
        
# Device Level:
Few things about this documentation for the Device Level. 
1) If a method does not have a return bullet point it means it will return a none

2) For any argument to a class/method or any return the type that is expected is the bullet directly
underneath

3) Some methods will have a notes if there is something special going on. Most are self documenting.
#Framework
#Base Classes

## Controller Class
All controllers will inherit from this controller class to have the need methods to be started and if
need be stopped.
---

- Class Args:
    - None
    
- Methods
    - starter:
        - Args: None
        - Operation: controllers operate in their own thread and the start method will always begin them

    - kill:
        - args: None
        - Operation: controllers exist in a while loop. The kill method will set the conditions of 
        that loop to False
    
## Data Pipe Class
A simple FIFO queue. All supervisors and the data controller will share a single instance of this class to
move data around.
---

- Class Args:
    - None
    
- Methods:
    - put:
        - args: None 
        - Operation: puts something at the end of the queue
        
    - get:
        - args: None
        - return: The object at the front of the queue
            - type=Package (see Package Class below)
        
    - empty:
        - args: None
        - return: returns True if queue is empty and False otherwise
            - Type=bool

## exceptionClasses
This file will house all custom exceptions that are needed.
---
- supervisorUniqueError: Is thrown when trying to spawn a supervisor with a non unique ID 
    
## Package Class
The package class is a convenient means to include all relevant info needed to transport data to the Data Controller. 
All supervisors will put package objects into the Data Pipe.
---
- Class Args:
    - data: - A dict of the readings that a supervisor as collected for a single sample 
    (see Framework/supervisors)
        - Type=dict
        
    - tags: -A dict of the tags that would be included for an entry into an InfluxDB
        - Type=dict
        
    - timeStamp: datetime object in UTC time
        - Type=datetime
        
    - headers: the headers of the supervisor to be used when writing to its CSV file
        - Type=list
        
    - monitorResponse: Currently None
        - Type=None
        - Notes: At a later date supervisors will be able to monitor data in real time to preform operations.
        For example say a device is connected to an alarm and a temperature sensor. If a temp reading > threshold
        then the alarm is triggered. Simple logic like this should be achievable (any analise work should be handled
        at the cloud level).

        
- Methods:
    - getPayload:
        - args: None
        - return: returns a dict containing the key/val of timeStamp, supervisorID, supervisorName, 
        deviceID, customConfig, and everything included in the arg 'data'
            - Type=dict
      
    - getTags: 
        - args: None
        - return: returns a dict containing that supervisors tags
            -Type=dict
            
    - getHeaders:
        - args: None
        - return: returns the headers of the supervisors that created this package
            - type=list
            
    - getData:
        - args: None
        - return: returns the data attached to the package object
            - type=dict
            
    - getTimeStamp:
        - args: None
        - return: returns a string of the time-stamp when the data (see above) was collected
            - type=string

## supervisor Class
Each supervisor will inherit from this class to have the necessary methods to function. Supervisors will live 
forever in a while loop unless killed - i.e. while=False. Below, the args are not passed into the supervisor class 
but each supervisor spawned will inherit from this base class of supervisor (seee Framework/supervisors/intMaker.py). 
These args will be read in from the base configuration file unless a custom configuration is used 
(see Framework/Base_supervisor_Config_Files/intMaker.json). Everything besides *args is universal for all
supervisors. 
---
- Class Args:
    - samplePeriod: How often the supervisor will sample data
        - Type=int
        
    - supervisorName: The name of the supervisor
        - Type=str or None
        
    - supervisorType: the type of supervisor (currently there is only a type "intMaker")
        - Type=str
        
    - supervisorID: ID of the supervisor (this is the only universal arg that cannot be defied by the 
    base configuration because each supervisor must have a unique ID)
        - Type=int
        
    - device: ID of the device
        - Type=int
        
    - tags type(dict): Tags that will be used when entered into Influx
        - Type=dict
        
    - pipe: The pipe object to add package objects to the queue
        - Type=dict
        
    - delay: Defaulted to 0. Whe a supervisor is 'restarted' what actually happens is the a new 
    supervisor is created and the old one dies (i.e. the thread runs out). But this leaves the 
    potability of two supervisors trying to talk to a sensor at the same time. To avoid this 
    a delay is included so the new supervisor will not start reading for one sample period 
    of the old supervisor to ensure no overlap.
        - Type=float or int
        
    - *args: Any args that are specific to that kind of supervisor (see Framework/supervisor/intMaker.py)
        - Type = *args
    
- Methods:
    - getData:
        - Args: None
        - Operation: The main loop where the supervisor will collect data from a sensor
        
    - getHeaders: 
        -args: None
        - return: returns the headers that will be used for the local CSV file
            - Type=list
    
    - getTags: 
        - Args: None
        - return: returns the supervisors InfluxDB tags
            - Type=dict
        
    - getInfo: 
        - Args: None
        - return: returns all info about the supervisor
            - Type=None
            
    - getID:
        - Args = none
        - return: return the supervisor's ID
            - Type=int
            
    - monitor:
        - Args:
            - data: the data that was collect for the current sample period
                - Type=dict
               
        - return: As of now will always return a None (See above example under package class for monitorResponse)
            - Type=None
    
    - package:
        - Args:
            - Data: the data that was collect for the current sample period
                - Type=dict
            - Timestamp: UTC timestamp when data was collected
                - Type=datetime
        - Operation: creates a package object and adds to the Data Pipe Queue
        
## Tester
A base class for all testers (see Framework/Test_Sweet) (note the test sweet only has tests
for the deviceManager).

- Class args: None

- Methods:
    - starter:
        - Args: None
        - Operation: starts all subsequent scripts that need to run to test things
    - results:
        - Args: None
        - Operation: starter will call results once testing is down to print out result data
    - cleanUp
        - Args: None
        - Operation: Removes any changes the test make while running
    
#Base_supervisor_Config_Files
Contains the base configuration for each supervisor type. Notice that the name of the base config json file
is the same as the python file in Framework/supervisors and is the same as the class in that respective
python file.

- Framework/Base_supervisor_Config_Files/intMaker.json
- Framework/supervisor/intMaker.py
- The above python file has the class "intMaker"

This naming convention MUST be followed!


#Controllers


## Command_Controller
As stated above this class will communicate to a cloud server and get commands.

## Data Controller
The Data Controller saves data to a local CSV file and pushed data to a mySQL DB.
The DB does not have to be live - as the device can operate without a network connection.
---
- Class Args:
    - updateInterval: How often the queue will be emptied and added to the CSV file
        - Type=int
    - DM: The instance of device manager to talk to supervisors. The same instance will be used between 
    supervisors and launchers (see below under Manager and Framework/Managers/deviceManger.py)
        - Type=deviceManager
        
- Methods:
    - starter:
        - Args: None
        - Operation: Main loop that will empty queue and give data to local CSV to save to a file and push to DB
    
    - localCSV:
        - args:
            - package: The package that was just pulled from the queue
                - Type=package
        - Operation: Ensures that the data to be added to the CSV is the same format and order
        as how the CSV headers are shown. Then saves that data to the CSV
        - Note: Each supervisor has it's own directory to save save CSV files to. Future updates will have
        CSV roll overs at some configurable time interval
        
    - RDPush:
        - args: Package
            - type=package
        - Operation: Pushed data to an API that will in turn add the pushed data to a "reliable delivery table" in
        the mySQL DB.
        
    - packager:
        - args: Package
            - type=package
        - return: Returns a dict with key/val pairs for the dataControllerServerAPI to except. All info to be used on the
        server side must be under the "data" key and this should include the raw data collected, a timestamp, and tags for
        influx. Must also include a key of "deviceID".
            - type=dict
        
    - kill:
        - Args: None
        - Operation: The starter method runs in a while loop while while True. The Kill method
        sets that loop to False
        
        
#Launcher


## Local Launcher
The local launcher inherits from the controller base class and is responsible for launching all supervisors 
in the deviceConfig.json file (see Framework/Totality_Config/deviceConfig.json). The supervisors can either spawn 
with a base configuration or a custom configuration variant can be used (again see 
Framework/Totality_Config/deviceConfig.json). Also note that custom configurations can override a single setting. For
example if everything in the base config is okay besides a sample rate then only the sample rates needs to be
added under the custom configuration.
___
- Class Args:
    - supervisorList: from deviceConfig.json info pertaining to launching supervisors
        - Type=dict
    - deviceManager: The deviceManager instance that communicates to supervisors
        - Type=deviceManager
        
- Methods:
    - spawnsupervisors:
        - Args: None
        - Operation: As the name suggests this method will spawn all supervisors as instructed by the
        supervisorList
    - starter:
        - Args: None
        - Operation: Calls spawnsupervisors
    - jsonToStr:
        - Args:
            - supervisorConfig: configuration setting trying to be used to spawn a supervisor
                - Type:dict
        - Operation: 
 
        
#Managers


## deviceManager
The deviceManager is responsible for maintaining a dict of what supervisors are in operation and being a middle
man for an controllers or launchers that want to talk to supervisors.
---
- Class Args:
    - pipe: The data Pipe as referenced from the base classes above
        - Type=data Pipe
    - deviceID: DID
        - type=int
    - test: A Str of "True" or "False" to change some minor settings based on if the run is a test or not
        - type=str
        
- Methods:
    - launcher:
        - Args:
            - supervisorType: The type of supervisor that will be created
                - Type=str
            - supervisorID: the ID of the supervisor
                - Type=int
            - customConfig=False: Custom configuration. Default to False
                - Type=dict
            - restart=False: To update a supervisor's configuration setting the supervisor is "reset" (really
            meaning the supervisor is killed and restarted with the new configuration). When a supervisor is
            "updated" this arg will be set to True this method will then call killsupervisor
                - Type=bool
        - Operation: The main launching method to start supervisor threads. Will call makesupervisor
        to get a configured supervisor object. Will make sure that the supervisorId arg is not
        an ID that is already in use; if the supervisorId arg is in use a 'supervisorUniqueError' 
        exception will be thrown (see exceptionClasses).
    - makesupervisor:
        - Args:
            - supervisorType: See launcher above
            - supervisorID: See launcher above
            - customConfig: See launcher above. When passed in with a none empty dict that does != 'None'
            - restart: See launcher above
            will call customConfiguration
        - return: creates an instance of the supervisorType by calling getsupervisorClass and passing in the needed
        configuration args. If restart is True then a delay arg will be passed into the supervisor.
            - Type=supervisor
    - dirSetUp:
        - Args:
            - supervisorID: the supervisorID
                - Type=int
            - supervisor: the instance of a supervisor
                - Type=supervisor
        - Operation: Each supervisor save its CSV file to a directory called "supervisorID_'ID'/". This method
        will check if that directory exists. If it does not it will create it and in that dir create a CSV
        file with the headers of the supervisor
    - getConfig:
        - Args:
            - supervisorType: the type of supervisor that is to be created
        - return: loads and returns the base configuration for that supervisorType
            - Type=dict
    - customConfiguration:
        - Args:
            - baseConfig: the base configuration of the supervisorType
                -Type=dict
            - customConfig: the custom configuration desired
                -Type=dict
        - return: Will overwrite base configuration with custom configuration. Custom configuration only
        needs the key/val paris that will override the base configuration settings.
            - Type=dict
    - getsupervisorClass:
        - Args:
            - supervisorType: the type of supervisor that is to be created
                - Type=str
        - return: Will return an instance of the supervisorType
            -Type=supervisor
    - killsupervisor:
        - Args:
            - supervisorID: the Id of the supervisor that is to be killed
                - Type=int
        - Operation: Will kill the supervisor with a matching ID
    - getTags:
        - Args:
            - supervisorID: the ID of the supervisor
                - type=int
        - return: the tags of the supervisor with a matching ID
            - Type=dict
    - getsupervisorInfo:
        - Args:
            - supervisorID: the ID of the supervisor
        - return: the info of the supervisor with a matching ID
            - Type=dict
    - getAllLocalsupervisors:
        - Args: None
        - return: a dict of all supervisors with key=supervisorID and val=supervisorInfo
            - Type=dict
    - getsupervisorInstance:
        - Args:
            - supervisorID: ID of the supervisor
                - Type=int
        - return: the supervisor instance with matching ID
            - Type=supervisor
            

#Totality Config


## device Config
This is the main json config file that starts everything. My this point it should be self expanitory what
is happening in the file so see Framework/Totality_Config.json


#Test Sweet


# Device Manager Tester
This will run tests to ensure that the deviceManger runs to spec. Will print a dict with
info for any test that is failed.


# Local Data
All supervisor CSV files will be stored in a sub-dir of this dir


# Launch Pad
Launch Pad is how this program is started (simply run "python launchPad.py" to see
it in action - ensure you use python 3.7). It reads the deviceConfig.json file and executes based on 
its contents starting any launchers and controllers it needs with their respective args.
