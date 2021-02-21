# from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
from time import sleep
# from gpiozero import MCP3008
import configparser
import sys
from iot_component import node
import multiprocessing

# adc = MCP3008(channel=0)

# Global Variables
RPICFG = "etc/host.cfg"
NODE_P = None
N_TERMINATE = None

def bootstrap():
    global N_TERMINATE
    N_TERMINATE = multiprocessing.Lock()

    # Start the collector to send to AWS
    node_start()

    # Flask etc
    # Code will be blocked here until Ctrl-C
    display_start()

    # After Ctrl-C, stop the node
    node_stop()

    pass

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
        elif list(rpicfg["TELEBOT"].keys()) != ["buttok", "phoneid"]:
            raise configparser.ParsingError("RPICFG Section Key Error")

        # Set ConfigParser Object
        RPICFG = rpicfg

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
        rpicfg["TELEBOT"] = {
            "bottok": "1487998228:AAEeVn6LyRfF1HpcicSlHljt9hidMdJ5rSs",
            "phoneid": "903351528"
        }
        RPICFG = rpicfg

def node_conf():
    global RPICFG
    # Build up vars
    kwargs = {
        "HOST": dict(RPICFG["HOST"])
    }
    return kwargs

def node_start():
    global NODE_P
    global N_TERMINATE

    kwargs = {
        "config": node_conf()
    }

    N_TERMINATE.acquire(block=False)
    NODE_P = multiprocessing.Process(target=node.node, name="IoT Node", daemon=True, args=(N_TERMINATE), kwargs=kwargs)
    NODE_P.start()

    if N_TERMINATE.acquire(timeout=5):
        print("Node failed to start")
        return 1

def node_stop():
    global NODE_P
    global N_TERMINATE

    if not N_TERMINATE.aquire(block=False):
        print("Signal Node to Terminate")
        N_TERMINATE.release()
    else:
        # Something else happen to Node
        print("Node failed unexpectedly")
        pass

    NODE_P.join()
    NODE_P.close()
    print("Node Terminated")

def display_start():
    pass

if __name__ == "__main__":
    confparse()

    # Entry Point of Program
    bootstrap()

    print("Finish")