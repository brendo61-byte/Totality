import requests

"""
This script will seed the DB with a customer and a device associated with said customer.
"""

NEW_CUSTOMER = "http://localhost:8803/customer/newCustomer"
NEW_DEVICE = "http://localhost:8803/device/newDevice"

newCustomerBody = {
    "name": "FizzBuzz Inc",
    "address": "1523 Holiday Drive",
    "phone": "314-159-2653",
}

newDeviceBody = {
    "name": "Brendon's MEGA Machine",
    "location": "Planet Drron",
    "customerOwner": 1
}


print("Begin Seeding")
try:
    requests.post(url=NEW_CUSTOMER, json=newCustomerBody)
    print("Seeded New Customer")
except Exception as e:
    print("Failed To See New Customer.Now Exiting Seeding Script.\nException: {}".format(e))
    exit()

try:
    requests.post(url=NEW_DEVICE, json=newDeviceBody)
    print("Seeded New Device")
except Exception as e:
    print("Failed To Seed New Customer. Now Exiting Seeding Script.\nException: {}".format(e))
