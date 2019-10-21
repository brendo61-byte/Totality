import requests

"""
This script will seed the DB with a customer and a device associated with said customer.
"""

NEW_CUSTOMER = "http://localhost:8803/customer/newCustomer"
NEW_DEVICE = "http://localhost:8803/device/newDevice"

newCustomerBody = {
    "name": "FizzBuzz Inc",
    "address": "700 Holiday Drive",
    "phone": "314-159-2653",
}

newDeviceBody = {
    "name": "Deep Blue",
    "location": "Tatooine",
    "customerOwner": 1
}

print("Begin Seeding")
try:
    result = requests.post(url=NEW_CUSTOMER, json=newCustomerBody)
    if result.status_code == 200:
        print("Seeded New Customer")
    else:
        print("Failed To See New Customer. Now Exiting Seeding Script.\nException: {}".format(e))
        exit()
except Exception as e:
    print("Failed To See New Customer. Now Exiting Seeding Script.\nException: {}".format(e))
    exit()

try:
    result = requests.post(url=NEW_DEVICE, json=newDeviceBody)
    if result.status_code == 200:
        print("Seeded New Device")
    else:
        print("Failed To Seed New Customer. Now Exiting Seeding Script.\nException: {}".format(e))
except Exception as e:
    print("Failed To Seed New Customer. Now Exiting Seeding Script.\nException: {}".format(e))
