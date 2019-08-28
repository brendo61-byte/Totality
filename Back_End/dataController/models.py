import peewee
import os
import datetime
import time

db_test = os.environ.get("TEST", False)
if db_test:
    db = peewee.MySQLDatabase("IoT", host='localhost', port=3306, user='root', passwd='example')
else:
    db = peewee.MySQLDatabase("IoT", host='db', port=3306, user='root', passwd='example')


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
    missedCommands = peewee.IntegerField(default=0, null=False)  # If device doesn't check-in with Command-Server during a command period then count += 1
    commandTimeWindow = peewee.DateTimeField(null=False)  # Time that device must check in before missedCommand is incremented.
    status = peewee.IntegerField(default=0, null=False)
    # 0=No Connection has not been established,
    # 1=connection stable - missed command periods between 0-3
    # 2=Last known connection was stable - missed 3-9 command periods
    # 3=Connection Lost - missed >10 command periods


class ReliableDelivery(BaseModel):
    timeStamp = peewee.DateTimeField(default=datetime.datetime.utcnow(), null=False)  # when payload was put into Db
    payload = peewee.CharField(null=False)  # payload for delivery
    sent = peewee.BooleanField(default=False)  # if the payload has been successfully sent
    deviceOwner = peewee.ForeignKeyField(Device, backref='reliableDelivery', null=False)  # Back ref to know who owns the payload


# This is a reader. All reader types will need a table in the DB
class intMaker(BaseModel):
    name = peewee.CharField(default='intMaker', null=False)
    supervisorID = peewee.AutoField(primary_key=True)  # Supervisor ID
    samplePeriod = peewee.IntegerField(default=1, null=False)
    deviceOwner = peewee.ForeignKeyField(Device, backref='intMaker', null=False)
    customConfig = peewee.BooleanField(default=False, null=False)
    # The above columns are static and ALL reader tables must include them
    # the following will be alarms
    badNum = peewee.IntegerField(default=0, null=False)
    # For this fake reader that generates random integers if the number 5 is generated the alarm will trigger (0=alarm off, 1=alarm on)
    # Logic to turn the the alarm off will be in the *** WHO!?


def makeTables():
    retires = 5
    while retires >= 0:
        try:
            models = [Customer, Device, ReliableDelivery, intMaker]
            db.create_tables(models, safe=True)
            break
        except:
            time.sleep(3)
            retires -= 1


makeTables()
