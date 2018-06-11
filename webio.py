from flask import Flask,render_template
import os,time,sys,gc,json,uuid,socket,struct,fcntl
import urllib ,urllib2
import RPi.GPIO as GPIO

def get_mac_address():
	mac=uuid.UUID(int = uuid.getnode()).hex[-12:].upper()
	return mac

def get_ip_address(ifname):
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	ip=""
	try:
		ip= socket.inet_ntoa(fcntl.ioctl(s.fileno(), 0x8915, struct.pack('256s', ifname[:15]))[20:24])
	except BaseException:
		return ""
	return ip


myaddr=""
mac=get_mac_address()
print mac
wip = get_ip_address('wlan0')
eth = get_ip_address('eth0')
if wip !="" :
	myaddr=wip
else:
	myaddr=eth
print "---------ip:["+myaddr+"]"

upio=12
downio=16
config={}
def read_config():
	global config,serip,devname,key,client,post1,post2
	try:
		
		f1=open("/boot/ser.txt")
		txt=f1.readline()
		f1.close()
		print txt
		config=json.loads(txt)
		serip=config["ip"]
		devname=config["name"]
		key=config["key"]
		client=config["client"]
		p1=open("/home/pi/mjpg.log")
		post1=p1.readline().replace("\n", "");
		p1.close();
		print post1

		p2=open("/home/pi/mjpg-uvc.log")
		post2=p2.readline().replace("\n", "");
		p2.close();
		print post2

		mdata={"name":devname,"key":key,"client":client,"p1":post1,"p2":post2}

	except BaseException:
		print "open error in ser.txt"

read_config()
print(config)

app=Flask(__name__)

@app.route("/")
def main():
    return render_template("index.html",post1=post1,post2=post2,upio=upio,downio=downio)

@app.route("/init")
def init():
	try:
		#response = urllib2.urlopen("http://192.168.10.208:8022/"+u)
		#html = response.read()
		#print html
		read_config()
		pin=26
		GPIO.setmode(GPIO.BCM)
		GPIO.setup(12,GPIO.OUT)
		GPIO.setup(16,GPIO.OUT)
		GPIO.setup(20,GPIO.OUT)
		GPIO.setup(21,GPIO.OUT)

		GPIO.setwarnings(False)
		return '{"ip":"'+myaddr+'","name":"'+devname+'","mac":"'+mac+'","p1":"'+post1+'","p2":"'+post2+'","up":"'+str(upio)+'","down":"'+str(downio)+'"}';
	except BaseException,e:
		print e.message
		return '{"msg":"error","error":"'+e.message+'"}'

@app.route("/setkey/<newkey>")
def setkey(newkey):
	config["key"]=newkey
	devname=name
	strjson=json.dumps(config)
	print strjson
	os.remove("/boot/ser.txt")
	f1=open("/boot/ser.txt","w+")
	f1.write(strjson)
	f1.close()

	return '{"key":"'+newkey+'","msg":"ok"}'

@app.route("/getname")
def getname():
	return '{"name":"'+devname+'","ip":"'+myaddr+'","mac":"'+mac+'"}'

@app.route("/setname/<name>")
def setname(name):
	global config,devname
	config["name"]=name
	devname=name
	strjson=json.dumps(config)
	print strjson
	os.remove("/boot/ser.txt")
	f1=open("/boot/ser.txt","w+")
	f1.write(strjson)
	f1.close()
	return '{"name":"'+name+'","msg":"ok"}'

@app.route("/set/<io>")
def set(io):
	GPIO.setup(int(io),GPIO.OUT)
	return '{"msg":'+io+'}'

@app.route("/on/<io>")
def on(io):
	print(io)
	try:
		GPIO.output(int(io),GPIO.HIGH)
		return '{"msg":"ok"}'
		#return '{"msg":"'+on+'","io":'+str(io)+'}'
	except BaseException,e:
		print e.message
		return '{"msg":"error"}'


@app.route("/off/<io>")
def off(io):
	print(io)

	try:
		GPIO.output(int(io),GPIO.LOW)
		return '{"msg":"ok"}'

#		return '{"msg":"off","io":'+str(io)+'}'

	except BaseException,e:
		print e.message
		msg="error"


@app.route("/post")
def post():
	return post1+","+post2

@app.route("/ck")
def ck():
	return '{"msg":"ok"}'

@app.route("/test")
def test():
	i=0
	while i<10:
		GPIO.output(20,GPIO.HIGH)
		GPIO.output(16,GPIO.LOW)
		time.sleep(0.5)
		GPIO.output(16,GPIO.HIGH)
		GPIO.output(20,GPIO.LOW)
		time.sleep(0.5)
		i=i+1

	GPIO.output(19,GPIO.LOW)
	GPIO.output(26,GPIO.LOW)

	return '123'
@app.route("/app_end")
def app_end():
	sys.exit()

@app.route("/cgi-bin/<getssid>")
def cgi(getssid):
	return '{"result":"success","ssid":"'+name+'","name":"'+name+'","key":"'+key+'","client":"'+client+'","mac":"'+mac+'"}'


if __name__=="__main__":
	app.debug=True
	app.run(host="0.0.0.0",port=8011)
	
