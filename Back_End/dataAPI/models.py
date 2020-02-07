import peewee
import os
import datetime
import time

db_name = os.environ.get("db_name", "IoT")
db_host = os.environ.get("db_host", "db")
db_post = int(os.environ.get("db_port"))
db_user = os.environ.get("db_user")
db_paswd = os.environ.get("db_paswd")

db = peewee.MySQLDatabase(db_name, host=db_host, port=db_post, user=db_user, passwd=db_paswd)


class BaseModel(peewee.Model):
    class Meta:
        database = db


class Customer(BaseModel):
    customerID = peewee.AutoField(primary_key=True)
    name = peewee.CharField(unique=True)
    address = peewee.CharField(null=False)
    phone = peewee.CharField(null=False)


class Device(BaseModel):
    name = peewee.CharField(null=False)
    location = peewee.CharField(null=False)
    latitude = peewee.FloatField(null=True)
    longitude = peewee.FloatField(null=True)
    deviceID = peewee.AutoField(primary_key=True)  # Device_Level ID
    customerOwner = peewee.ForeignKeyField(Customer, backref='devices')  # IDs who owns the device
    dataControllerPeriod = peewee.FloatField(null=False)  # How often data will be regularly pushed -- in seconds
    commandControllerPeriod = peewee.FloatField(null=False)  # How often commands will be regularly pulled -- in seconds
    timeOfLastCheckIn = peewee.DateTimeField(null=True)  # Date time object
    missedCommands = peewee.IntegerField(default=0,
                                         null=False)  # If device doesn't check-in with Command-Server during a command period then count += 1
    commandTimeWindow = peewee.DateTimeField(
        null=False)  # Time that device must check in before missedCommand is incremented.
    status = peewee.IntegerField(default=0, null=False)
    # Todo: Get the status field working --- though dataAPI API
    # 0=No Connection has not been established,
    # 1=connection stable - missed command periods between 0-3
    # 2=Last known connection was stable - missed 3-9 command periods
    # 3=Connection Lost - missed >10 command periods


class Command(BaseModel):
    commandID = peewee.AutoField(primary_key=True)
    refID = peewee.IntegerField(null=False)
    command = peewee.TextField(null=False)  # str of the command dict (see command API)
    timeStamp = peewee.DateTimeField(default=datetime.datetime.utcnow(), null=False)  # TS of when command was added
    delivery = peewee.IntegerField(default=0, null=False)
    # 0 = No replay - i.e. was just delivered
    # 1 = Failed to deploy command
    # 2 = Successful deployment of command
    # 3 = Command has timed out
    status = peewee.IntegerField(default=0, null=False)  # If the command has been executed yet. 0=F, 1=T
    deviceOwner = peewee.ForeignKeyField(Device, backref='command',
                                         null=False)  # Back ref to know who gets the command


class Supervisor(BaseModel):
    name = peewee.CharField(null=True)
    refID = peewee.IntegerField(null=True)
    supervisorType = peewee.CharField(null=False)
    supervisorID = peewee.AutoField(primary_key=True)  # Supervisor ID
    samplePeriod = peewee.IntegerField(default=1, null=False)
    deviceOwner = peewee.ForeignKeyField(Device, backref='supervisor', null=False)
    customConfig = peewee.CharField(null=True)


class ReliableDelivery(BaseModel):
    inputTimeStamp = peewee.DateTimeField(default=datetime.datetime.utcnow(), null=False)  # when payload was put into Db

    timeStamp = peewee.CharField()  # when data was collected in local time
    dataType = peewee.CharField()  # what type of data it is
    units = peewee.CharField()  # units data is measured in
    data = peewee.FloatField()  # the data its self
    sensorType = peewee.CharField()  # the supervisor type that generated this data
    supervisorID = peewee.ForeignKeyField(Supervisor, backref='reliableDelivery', null=False)  # globalID of supervisor

    deviceOwner = peewee.ForeignKeyField(Device, backref='reliableDelivery',
                                         null=False)  # Back ref to know who owns the payload


class CustomerKeys(BaseModel):
    key = peewee.CharField(null=False)
    customerOwner = peewee.ForeignKeyField(Customer, backref='customerKeys')  # IDs who owns the device


class SessionKeys(BaseModel):
    sessionKey = peewee.CharField(null=False)
    customerOwner = peewee.ForeignKeyField(Customer, backref='SessionKeys')  # IDs who owns the device
    endLifeTime = peewee.IntegerField(null=False)


def makeTables():
    retires = 5
    while retires >= 0:
        try:
            models = [Customer, Device, ReliableDelivery, Supervisor, Command, CustomerKeys, SessionKeys]
            db.create_tables(models, safe=True)
            break
        except:
            time.sleep(3)
            retires -= 1


makeTables()
