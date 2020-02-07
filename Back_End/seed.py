import requests

"""
This script will seed the DB with a customer and a device associated with said customer.
"""

NEW_CUSTOMER = "http://localhost/creation/customer/newCustomer"
LOGIN = "http://0.0.0.0/creation/customer/login"
NEW_DEVICE = "http://localhost/creation/device/newDevice"

newCustomerBody = {
    "name": "FizzBuzz Inc",
    "address": "700 Holiday Drive",
    "phone": "314-159-2653",
}

newDeviceBody = {
    "name": "Deep Blue",
    "location": "Tatooine"
}
global loginKey

print("Begin Seeding")
try:
    result = requests.post(url=NEW_CUSTOMER, json=newCustomerBody)
    if result.status_code == 200:
        print("Seeded New Customer")
        loginKey = result.json().get("data")
    else:
        print("Failed To See New Customer. Now Exiting Seeding Script.\nResult: {}".format(result.raw()))
        exit()
except Exception as e:
    print("Failed To See New Customer. Now Exiting Seeding Script.\nException: {}".format(e))
    exit()

# login
loginBody = {
    "name": newCustomerBody.get("name"),
    "key": loginKey
}
result = requests.post(url=LOGIN, json=loginBody)
sessionKey = result.json().get("data")

try:
    newDeviceBody["key"] = sessionKey
    result = requests.post(url=NEW_DEVICE, json=newDeviceBody)
    if result.status_code == 200:
        print("Seeded New Device")
    else:
        print("Failed To Seed New Customer. Now Exiting Seeding Script.\nResult: {}".format(result.raw()))
except Exception as e:
    print("Failed To Seed New Customer. Now Exiting Seeding Script.\nException: {}".format(e))
