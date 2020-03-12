from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, HttpResponseBadRequest
from .models import *
from django.conf import settings

import json
import datetime
import pytz


@csrf_exempt
def data(request):
    if request.method == 'POST':

        try:
            payload = json.loads(request.body.decode('utf-8'))

            payloads = payload.get("bigLoad")

            for data in payloads:

                packType = data.get("packageType")

                if packType == "dataPush":
                    dataPush(data=data.get("data").get("package"))

            return HttpResponse('')

        except Exception as e:
            return HttpResponseBadRequest()

    else:
        return HttpResponseBadRequest()


def dataPush(data):
    sensor = Sensor.objects.get(pk=data.get("sensorID"))
    data["sensor"] = sensor
    del data["sensorID"]  # use a pop (#, None)

    data["timeStamp"] = datetime.datetime.strptime(data.get("timeStamp"), '%m/%d/%Y-%H:%M:%S').replace(tzinfo=pytz.timezone(settings.TIME_ZONE))

    DataField.objects.create(**data)


# @csrf_exempt
# def registration(request):
#     if request.method == 'POST':
#         try:
#             payload = json.loads(request.body.decode('utf-8'))
#
#
#
#         except:
#             return HttpResponseBadRequest()
#     else:
#         return HttpResponseBadRequest()
