import sys,uuid,socket
import fcntl,struct,json
import urllib,urllib2,time,gc,os

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

def get_time():
	return  time.strftime("%Y%m%d_%H%M%S", time.localtime())

#time.sleep(20)
serip=""
name=""
key=""
client=""
mdata={}
def read_ser():
	try:
		global serip,name,key,client,mdata
		print("read_ser")
		f1=open("/boot/ser.txt")
		txt=f1.readline()
		f1.close()
		config=json.loads(txt)
		serip=config["ip"]
		name=config["name"]
		key=config["key"]
		client=config["client"]
		mdata={"name":name,"key":key,"client":client,"p1":post1,"p2":post2}

	except BaseException:
		print "open error in ser.txt"

read_ser()

ff=time.strftime("%Y%m%d_%H%M%S", time.localtime())+'.txt' ;
fo1=open("/home/pi/log/"+ff,"w+")
fo1.write(get_time())
fo1.write('10s\n')

myaddr=""
mac=get_mac_address()
wip = get_ip_address('wlan0')
eth = get_ip_address('eth0')
if wip !="" :
	myaddr=wip
else:
	myaddr=eth
print myaddr
fo1.write(myaddr+'\n')

p1=open("/home/pi/mjpg.log")
post1=p1.readline().replace("\n", "");
p1.close();
print post1

p2=open("/home/pi/mjpg-uvc.log")
post2=p2.readline().replace("\n", "");
p2.close();
print post2




while True:
    try:
	read_ser()
        t=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        u= urllib.urlencode({'t':t ,'ip':myaddr,'name':name,'mac':mac,'key':key,'client':client})
	print(u)
        url="http://dev.cmx666.cn/reg?"+u        
        response = urllib2.urlopen(url)
        html = response.read()
	print html
	
	urldata = urllib.urlencode(mdata)
	url = 'http://'+serip+'/reg?'+urldata 
	print(url)
	response = urllib2.urlopen(url)
	html = response.read()

	response.close()
	fo1.write(get_time()+"	"+html)

        response.close()
        del response	
        gc.collect()
        time.sleep(10)

    except BaseException,e:
	print(e)	
	time.sleep(30)
	
		