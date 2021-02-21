# from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
from time import sleep
# from gpiozero import MCP3008
import configparser
import sys

# adc = MCP3008(channel=0)

# Global Variables
RPICFG = "etc/host.cfg"
ROOTCA = None
CERTIFICATE = None
PRIVATEKEY = None
HOSTNAME = None
RPI = None

def confparse():
    global RPICFG
    global ROOTCA
    global CERTIFICATE
    global PRIVATEKEY
    global HOSTNAME
    global RPI

    rpicfg = configparser.ConfigParser()
    try:
        rpicfg.read(RPICFG)

        # Verify Section
        if rpicfg.sections() != ["HOST"]:
            raise configparser.ParsingError("RPICFG Section Error")

        # Verify Section Keys
        if list(rpicfg["HOST"].keys()) != ["rootca", "certificate", "privatekey", "hostname", "rpi"]:
            raise configparser.ParsingError("RPICFG Section Key Error")

        # Set ConfigParser Object
        RPICFG = rpicfg
        ROOTCA = rpicfg["HOST"]["rootca"]
        CERTIFICATE = rpicfg["HOST"]["certificate"]
        PRIVATEKEY = rpicfg["HOST"]["privatekey"]
        HOSTNAME = rpicfg["HOST"]["hostname"]
        RPI = rpicfg["HOST"]["rpi"]

    except configparser.ParsingError:
        # Reset RPICFG
        """
        python3 builtin print but outputs to sys.stderr
        """
        print("Rewriting to Default Host", sep=' ', end='\n', file=sys.stderr)
        rpicfg.clear()
        rpicfg["HOST"] = {
            "rootca": "AWSCert/rootca.pem",
            "certificate": "AWSCert/certificate.pem.crt",
            "privatekey": "AWSCert/private.pem.key",
            "hostname": "a2jmdmmdzxnqz9-ats.iot.us-east-1.amazonaws.com",
            "rpi": "YLRasp"
        }
        RPICFG = rpicfg
        ROOTCA = rpicfg["HOST"]["rootca"]
        CERTIFICATE = rpicfg["HOST"]["certificate"]
        PRIVATEKEY = rpicfg["HOST"]["privatekey"]
        HOSTNAME = rpicfg["HOST"]["hostname"]
        RPI = rpicfg["HOST"]["rpi"]

def boot_loader():
    pass

if __name__ == "__main__":
    confparse()

    # Entry Point of Program
    boot_loader()

    print("Finish")