#!/usr/bin/python
import Adafruit_DHT
import time
import sys
import httplib, urllib
import json
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(24,GPIO.IN,pull_up_down=GPIO.PUD_UP)

deviceId = "D05kX4YK"
deviceKey = "LfsEmRyTA47SkYHy" 
def post_to_mcs(payload): 
	headers = {"Content-type": "application/json", "deviceKey": deviceKey} 
	not_connected = 1 
	while (not_connected):
		try:
			conn = httplib.HTTPConnection("api.mediatek.com:80")
			conn.connect() 
			not_connected = 0 
		except (httplib.HTTPException, socket.error) as ex: 
			print ("Error: %s" % ex)
			time.sleep(10)
			 # sleep 10 seconds 
	conn.request("POST", "/mcs/v2/devices/" + deviceId + "/datapoints", json.dumps(payload), headers) 
	response = conn.getresponse() 
	print( response.status, response.reason, json.dumps(payload), time.strftime("%c")) 
	data = response.read() 
	conn.close() 
sensor_args = { '11': Adafruit_DHT.DHT11,
                '22': Adafruit_DHT.DHT22,
                '2302': Adafruit_DHT.AM2302 }
if len(sys.argv) == 3 and sys.argv[1] in sensor_args:
    sensor = sensor_args[sys.argv[1]]
    pin = sys.argv[2]
else:
    print('Usage: sudo ./Adafruit_DHT.py [11|22|2302] <GPIO pin number>')
    print('Example: sudo ./Adafruit_DHT.py 2302 4 - Read from an AM2302 connected to GPIO pin #4')
    sys.exit(1)
 
while 1:
	humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)
	SwitchStatus=GPIO.input(24)
	if SwitchStatus==0:
		print("Button pressed")
		print('Temp={0:0.1f}*  Humidity={1:0.1f}%'.format(temperature, humidity))
		payload = {"datapoints":[{"dataChnId":"Humidity","values":{"value":humidity}},{"dataChnId":"Temperature","values":{"value":temperature}},{"dataChnId":"SwitchStatus",
			"values":{"value":SwitchStatus}}]}
		post_to_mcs(payload)
		time.sleep(2)

	else:
		print("Button released")
		payload = {"datapoints":[{"dataChnId":"SwitchStatus",
			"values":{"value":SwitchStatus}}]}
                post_to_mcs(payload)
                time.sleep(2)
