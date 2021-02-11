# Imports
import telepot
from gpiozero import LED, Button, MCP3008
from signal import pause
from time import sleep
import mysql.connector
import sys
from datetime import datetime as dt
from flask import Flask, render_template, jsonify, request, Response
import json
import numpy
import datetime
import decimal
import gevent
import gevent.monkey
from gevent.pywsgi import WSGIServer

gevent.monkey.patch_all()

# Initialise Class
class GenericEncoder(json.JSONEncoder):
    def default(self, obj):  
        if isinstance(obj, numpy.generic):
            return numpy.asscalar(obj) 
        elif isinstance(obj, datetime.datetime):  
            return obj.strftime('%Y-%m-%d %H:%M:%S') 
        elif isinstance(obj, decimal.Decimal):
            return float(obj)
        else:  
            return json.JSONEncoder.default(self, obj) 

# Initialise def
def data_to_json(data):
    json_data = json.dumps(data,cls=GenericEncoder)
    return json_data

def connect_to_mysql(host,user,password,database):
    try:
        cnx = mysql.connector.connect(host=host,user=user,password=password,database=database)

        cursor = cnx.cursor()
        print("Successfully connected to database!")

        return cnx,cursor

    except:
        print(sys.exc_info()[0])
        print(sys.exc_info()[1])

        return None

def fetch_fromdb_as_json(cnx,cursor,sql):
    
    try:
        cursor.execute(sql)
        row_headers=[x[0] for x in cursor.description] 
        results = cursor.fetchall()
        data = []
        for result in results:
            data.append(dict(zip(row_headers,result)))
        
        data_reversed = data[::-1]

        data = {'data':data_reversed}

        return data_to_json(data)

    except:
        print(sys.exc_info()[0])
        print(sys.exc_info()[1])
        return None

def Telegram(msg):
    # Todo: Show red light if Day mode, Red and Yellow blink if night mode
    content_type, chat_type, chat_id = telepot.glance(msg)

    if content_type != "text":
        return
    elif msg['text'] != "1":
        return
    
    # Todo: Turn red light on
    if led_yellow.is_lit:
        led_yellow.off()
    led_red.on()
    sleep(3)
    led_red.off()

def BellAlert():
    # Todo: Record Light Value and Datetime
    timestamp = dt.now().strftime('%Y-%m-%d %H:%M:%S')
    sensor_value = (1024*(1.0-mcp3008.value))
    sensor_value = round(sensor_value)

    # Todo: Save Light Value and Datetime into MySQL database
    try:
        host='localhost'; user='auser'; password='auseriot'; database='AssignmentIoT'
        sql = "INSERT INTO ButtonPress (datetimeinfo, lightvalue) VALUES (%s, %s)"
        cnx,cursor = connect_to_mysql(host,user,password,database)
        data = (timestamp, sensor_value)
        cursor.execute(sql, data)
        cnx.commit()
        cursor.close()
        cnx.close()
    except mysql.connector.Error as err:
        print(err)
    except:
        print("Error while inserting data...")
        print(sys.exc_info()[0])
        print(sys.exc_info()[1])
    led_yellow.on()
    bot.sendMessage(my_phone_id, 'Door Bell, reply 1 to reply unable to answer') 
    sleep(15)
    if led_yellow.is_lit and sensor_value > 100 and AlarmTimeOut == 1:
        led_yellow.off()
        led_red.on()
        sleep(1)
        led_red.off()
        sleep(1)
        led_red.on()
        sleep(1)
        led_red.off()
        sleep(1)
        led_red.on()
        sleep(1)
        led_red.off()
    elif led_yellow.is_lit:
        led_yellow.off()

        # Maybe Todo: Implement Sound if light value is (>something)


app = Flask(__name__)

@app.route("/api/getdata",methods = ['POST', 'GET'])
def apidata_getdata():
    if request.method == 'POST':
        try:
            rsensor_value = (1024*(1.0-mcp3008.value))
            rsensor_value = round(rsensor_value)
            host='localhost'; user='auser'; password='auseriot'; database='AssignmentIoT'
            sql="SELECT * FROM ButtonPress ORDER BY datetimeinfo DESC LIMIT 10"
            cnx,cursor = connect_to_mysql(host,user,password,database)
            json_data = fetch_fromdb_as_json(cnx,cursor,sql)
            loaded_r = json.loads(json_data)
            data = {'chart_data': loaded_r, 'lightnow': rsensor_value, 'title': "IOT Data"}
            cursor.close()
            cnx.close()
            return jsonify(data)
        except:
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
        if AlarmTimeOut == 1:
            data = {'TOsetting': 'Enabled'}
        else:
            data = {'TOsetting': 'Disabled'}
        return jsonify(data)

@app.route("/")
def chartsimple():
    return render_template('index.html')

if __name__ == '__main__':
    my_bot_token = '1487998228:AAEeVn6LyRfF1HpcicSlHljt9hidMdJ5rSs'
    my_phone_id = '903351528'

    button = Button(21, pull_up=False)

    led_red = LED(26)
    led_yellow = LED(13)

    mcp3008 = MCP3008(channel=0)

    bot = telepot.Bot(my_bot_token)
    bot.message_loop(Telegram)
    button.when_pressed = BellAlert
    AlarmTimeOut = 1

    try:
        print('Server waiting for requests')
        http_server = WSGIServer(('192.168.1.10', 8001), app)
        app.debug = True
        http_server.serve_forever()
    except:
        print("Exception")
        import sys
        print(sys.exc_info()[0])
        print(sys.exc_info()[1])
