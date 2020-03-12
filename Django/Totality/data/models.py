from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class Device(models.Model):
    name = models.CharField(max_length=64, unique=True)
    location = models.CharField(max_length=64)
    supervisor = models.ForeignKey(User, on_delete=models.CASCADE)
    dateCreated = models.DateTimeField(default=timezone.now)
    lastCheckInTime = models.DateTimeField(blank=True, default=None, null=True)


class Sensor(models.Model):
    name = models.CharField(max_length=50)
    dateCreated = models.DateTimeField(default=timezone.now)
    device = models.ForeignKey(Device, on_delete=models.CASCADE)


class DataField(models.Model):
    data = models.FloatField()
    readingType = models.CharField(max_length=32)  # Todo: Call this readingType or something else to not piss Jerry off
    units = models.CharField(max_length=32)
    sensorType = models.CharField(max_length=32)
    timeStamp = models.DateTimeField()
    injectionTimeStamp = models.DateTimeField(blank=True, default=timezone.now)
    sensor = models.ForeignKey(Sensor, on_delete=models.CASCADE)
