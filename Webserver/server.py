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
from boto3.dynamodb.conditions import Key, Attr
import boto3

DYNAMODB = boto3.resource('dynamodb', region_name='us-east-1')
TABLE = DYNAMODB.Table('ButtonPress')
DYNAMODBCLI = boto3.client('dynamodb', region_name='us-east-1')

def real_time():
    startdate = '2021-02'
    response = TABLE.query(
        KeyConditionExpression=Key('id').eq('realtime')
                               & Key('datetimeinfo').begins_with(startdate),
        ScanIndexForward=False
    )
    items = response["Items"]
    n = 1
    data = items[:n]
    if data:
        return int(data[0]["value"])
    else:
        return 0

app = Flask(__name__)

@app.route("/api/getdata",methods = ['POST', 'GET'])
def apidata_getdata():
    if request.method == 'POST':
        try:
            data = {'chart_data': jsonc.data_to_json(dynamodb.get_data_from_dynamodb()),
                    'lightnow': real_time(),
                    'title': "IOT Data"}
            print(data)
            return jsonify(data)
        except:
            print("apidata_getdata error")
            print(sys.exc_info()[0])
            print(sys.exc_info()[1])

def TOenabled():
    now = datetime.datetime.now().isoformat()
    DYNAMODBCLI.put_item(TableName='ButtonPress', Item={'id': {'S': 'TO'}, 'datetimeinfo': {'S': str(now)},
                                                     'TOsetting': {'S': '1'}})
    return "Enabled"

def TOdisabled():
    now = datetime.datetime.now().isoformat()
    DYNAMODBCLI.put_item(TableName='ButtonPress', Item={'id': {'S': 'TO'}, 'datetimeinfo': {'S': str(now)},
                                                     'TOsetting': {'S': '0'}})
    return "Disabled"

@app.route("/writeTO/<status>")
def writePin(status):
    if status == 'Enable':
        resresult = TOenabled()
    else:
        resresult = TOdisabled()
    return resresult

@app.route("/api/getTO", methods = ['POST', 'GET'])
def apidata_getTO():
    if request.method == 'POST':
        startdate = '2021-02'
        response = TABLE.query(
            KeyConditionExpression=Key('id').eq('TO')
                                   & Key('datetimeinfo').begins_with(startdate),
            ScanIndexForward=False
        )
        items = response["Items"]
        n = 1
        data = items[:n]
        if not data or int(data[0]["TOsetting"]) == 1:
            output = {'TOsetting': 'Enabled'}
        else:
            output = {'TOsetting': 'Disabled'}
        return jsonify(output)

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