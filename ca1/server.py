from time import sleep
import sys
import dynamodb
from datetime import datetime as dt
from flask import Flask, render_template, jsonify, request, Response
import json
import jsonconverter as jsonc
import datetime
import decimal
import gevent
import gevent.monkey
from gevent.pywsgi import WSGIServer

app = Flask(__name__)

@app.route("/api/getdata",methods = ['POST', 'GET'])
def apidata_getdata():
    if request.method == 'POST':
        try:
            data = {'chart_data': jsonc.data_to_json(dynamodb.get_data_from_dynamodb()), 
             'title': "IOT Data"}
            print(data)
            return jsonify(data)
        except:
            print("apidata_getdata error")
            print(sys.exc_info()[0])
            print(sys.exc_info()[1])

def TOenabled():
    global AlarmTimeOut
    AlarmTimeOut = 1
    return "Enabled"

def TOdisabled():
    global AlarmTimeOut
    AlarmTimeOut = 0
    return "Disabled"

@app.route("/writeTO/<status>")
def writePin(status):
    if status == 'Enable':
        resresult = TOenabled()
    else:
        resresult = TOdisabled()
    return resresult

@app.route("/testRun")
def testRun():
    BellAlert()
    return "Completed"

@app.route("/api/getTO", methods = ['POST', 'GET'])
def apidata_getTO():
    if request.method == 'POST':
        #if AlarmTimeOut == 1:
            #data = {'TOsetting': 'Enabled'}
        #else:
        data = {'TOsetting': 'Disabled'}
        return jsonify(data)

@app.route("/")
def chartsimple():
    return render_template('index.html')

try:
    print('Server waiting for requests')
    http_server = WSGIServer(('0.0.0.0', 8001), app)
    app.debug = True
    http_server.serve_forever()
except:
    print("Exception")
    print(sys.exc_info()[0])
    print(sys.exc_info()[1])