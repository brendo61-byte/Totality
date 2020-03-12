# import pandas as pd
import time, datetime, os, logging, smtplib, ssl, sys, socket, subprocess
from email.mime.multipart import MIMEMultipart
# import CommonMethods, gpsControl

import time


class Ping(object):
    def __init__(self):
        self.ipSender()
        ISOFFLINE = False

    def ipSender(self):
        gw = os.popen("ip -4 route show default").read().split()
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect((gw[2], 0))
        ipaddr = s.getsockname()[0]
        gateway = gw[2]
        host = socket.gethostname()
        # print("IP:", ipaddr, " GW:", gateway, " Host:", host)
        # lfile.write("Node " + str(nodeid) + " has ip " + (str(ipaddr)))
        msg = MIMEMultipart()
        sender = receiver = "brendon.stanley16@gmail.com"
        msg['From'] = sender
        msg['To'] = receiver
        msg['Subject'] = 'Node IP'
        data = ("Node has ip {} ").format(ipaddr)
        port = 587
        psk = "sgmsvmfkpnyowklk"
        smtp_server = "smtp.gmail.com"
        context = ssl.create_default_context()

        with smtplib.SMTP(smtp_server, port) as server:
            server.starttls(context=context)
            server.login("brendon.stanley16@gmail.com", psk)
            server.sendmail(sender, receiver, data)
            server.quit()
        return ipaddr

    def main(self):
        self.ipSender()


def program():
    while True:
        program = Ping()
        program.main()
        time.sleep(18000)


if __name__ == "__main__":
    program()
