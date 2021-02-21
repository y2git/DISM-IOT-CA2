from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
from time import sleep
# from gpiozero import MCP3008
import telepot
import configparser
import sys
from datetime import datetime as dt
import json
from gpiozero import LED, Button, MCP3008
import boto3
from boto3.dynamodb.conditions import Key, Attr
import copy
import threading


# Global Variables
RPICFG = "etc/host.cfg"
BOT = None
PHONEID = None
MYRPI = None
ADC = MCP3008(channel=0)
LEDRED = LED(26)
LEDYELLOW = LED(13)
BUTTON = Button(21, pull_up=False)
DYNAMODB = boto3.resource('dynamodb', region_name='us-east-1')
TABLE = DYNAMODB.Table('ButtonPress')
ALARMTIMEOUT = 1
AWS_P = None

def bootstrap():

    # Listens for actions
    node_start()

    # Sends Real Time data
    realtime_start()


def node_start():
    global BOT
    global BUTTON
    global STOP_THREAD
    global AWS_P

    # Listen for RPI Actions
    BOT.message_loop(Telegram)
    BUTTON.when_pressed = BellAlert

    # Listen for AWS Actions
    AWS_P = threading.Thread(target=aws_check)
    AWS_P.daemon = True
    AWS_P.start()

def realtime_start():
    global MYRPI
    global ADC

    try:
        while True:
            timestamp = dt.now()
            sensor_value = (1024 * (1.0 - ADC.value))
            sensor_value = round(sensor_value)
            message = {}

            # Todo: Save Light Value and Datetime into DB database
            message["id"] = "realtime"
            message["datetimeinfo"] = timestamp.isoformat()
            message["value"] = sensor_value

            MYRPI.publish("sensors/light", json.dumps(message), 1)
            sleep(5)
    except KeyboardInterrupt:
        print("Keyboard Interupt")

def Telegram(msg):
    # Todo: Show red light if Day mode, Red and Yellow blink if night mode
    content_type, chat_type, chat_id = telepot.glance(msg)
    print(msg)

    if content_type != "text":
        print(msg)
        return
    elif msg['text'] != "1":
        print(msg)
        return

    # Todo: Turn red light on
    global LEDRED
    global LEDYELLOW
    if LEDYELLOW.is_lit:
        LEDYELLOW.off()
    LEDRED.on()
    sleep(3)
    LEDRED.off()

def BellAlert():
    global MYRPI
    global LEDYELLOW
    global LEDRED
    global BOT
    global PHONEID
    global ADC
    global ALARMTIMEOUT

    timestamp = dt.now()
    sensor_value = (1024*(1.0-ADC.value))
    sensor_value = round(sensor_value)
    message = {}

    # Todo: Save Light Value and Datetime into DB database
    message["id"] = "assignment"
    message["datetimeinfo"] = timestamp.isoformat()
    message["value"] = sensor_value

    MYRPI.publish("sensors/light", json.dumps(message), 1)

    LEDYELLOW.on()
    BOT.sendMessage(PHONEID, 'Door Bell, reply 1 to reply unable to answer')
    sleep(15)
    if LEDYELLOW.is_lit and sensor_value > 100 and ALARMTIMEOUT == 1:
        LEDYELLOW.off()
        LEDRED.on()
        sleep(1)
        LEDRED.off()
        sleep(1)
        LEDRED.on()
        sleep(1)
        LEDRED.off()
        sleep(1)
        LEDRED.on()
        sleep(1)
        LEDRED.off()
    elif LEDYELLOW.is_lit:
        LEDYELLOW.off()

def aws_check():
    global TABLE
    global ALARMTIMEOUT
    #todo: make another config for startdate
    startdate = '2021-02'
    localtimeout = copy.deepcopy(ALARMTIMEOUT)

    try:
        while True:
            response = TABLE.query(
                KeyConditionExpression=Key('id').eq('TO')
                                       & Key('datetimeinfo').begins_with(startdate),
                ScanIndexForward=False
            )
            items = response["Items"]
            n = 1
            data = items[:n]
            if data and localtimeout != int(data[0]["TOsetting"]):
                localtimeout = int(data[0]["TOsetting"])
                ALARMTIMEOUT = int(data[0]["TOsetting"])
            sleep(10)

    except KeyboardInterrupt:
        print("Stopping")
    except Exception as e:
        print("Exception on aws_check")
        print(e)

def confparse():
    global RPICFG

    rpicfg = configparser.ConfigParser()
    try:
        rpicfg.read(RPICFG)

        # Verify Section
        if rpicfg.sections() != ["HOST", "TELEBOT"]:
            raise configparser.ParsingError("RPICFG Section Error")

        # Verify Section Keys
        if list(rpicfg["HOST"].keys()) != ["rootca", "certificate", "privatekey", "hostname", "rpi"]:
            raise configparser.ParsingError("RPICFG Section Key Error")
        elif list(rpicfg["TELEBOT"].keys()) != ["bottok", "phoneid"]:
            raise configparser.ParsingError("RPICFG Section Key Error")

        # Set ConfigParser Object
        RPICFG = {
            "HOST": dict(rpicfg["HOST"]),
            "TELEBOT": dict(rpicfg["TELEBOT"])
        }
        RPICFG["TELEBOT"]["phoneid"] = int(rpicfg["TELEBOT"]["phoneid"])

    except configparser.ParsingError:
        # Reset RPICFG
        """
        python3 builtin print but outputs to sys.stderr
        """
        print("Rewriting to Default Host")
        rpicfg.clear()
        rpicfg["HOST"] = {
            "rootca": "AWSCert/rootca.pem",
            "certificate": "AWSCert/certificate.pem.crt",
            "privatekey": "AWSCert/private.pem.key",
            "hostname": "a2jmdmmdzxnqz9-ats.iot.us-east-1.amazonaws.com",
            "rpi": "YLRasp"
        }
        rpicfg["TELEBOT"] = {
            "bottok": "1487998228:AAEeVn6LyRfF1HpcicSlHljt9hidMdJ5rSs",
            "phoneid": "903351528"
        }
        RPICFG = {
            "HOST": dict(rpicfg["HOST"]),
            "TELEBOT": dict(rpicfg["TELEBOT"])
        }
        RPICFG["TELEBOT"]["phoneid"] = int(rpicfg["TELEBOT"]["phoneid"])

def customcallback(client, userdata, message):
    print("Sent to AWS: ")
    print(message.payload)
    print("of topic: ")
    print(message.topic)
    print("--------------\n\n")

def setglobvar():
    global RPICFG
    global BOT
    global MYRPI
    global PHONEID

    BOT = telepot.Bot(str(RPICFG["TELEBOT"]["bottok"]))
    PHONEID = int(RPICFG["TELEBOT"]["phoneid"])

    MYRPI = AWSIoTMQTTClient(RPICFG["HOST"]["rpi"])
    MYRPI.configureEndpoint(RPICFG["HOST"]["hostname"], 8883)
    MYRPI.configureCredentials(RPICFG["HOST"]["rootca"], RPICFG["HOST"]["privatekey"], RPICFG["HOST"]["certificate"])
    MYRPI.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
    MYRPI.configureDrainingFrequency(2)  # Draining: 2 Hz
    MYRPI.configureConnectDisconnectTimeout(10)  # 10 sec
    MYRPI.configureMQTTOperationTimeout(5)
    MYRPI.connect()
    MYRPI.subscribe("sensors/light", 1, customcallback)


if __name__ == "__main__":
    confparse()

    setglobvar()

    # Entry Point of Program
    bootstrap()

    print("Finish")
