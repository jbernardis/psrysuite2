import sys
import serial
import select
import time
import logging
from threading import Thread
from socketserver import ThreadingMixIn 
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs


FORWARD = 0x04
REVERSE = 0x03

MAXTRIES = 3

def formatLocoID(lid):
	lidhi = (lid >> 8) | 0xc0
	lidlo = lid % 256
	return [lidhi, lidlo]

class Loco:
	def __init__(self, lid):
		self.locoid = lid
		self.dpeed = 0
		self.direction = FORWARD
		self.headlight = False
		self.horn = False
		self.bell = False
		
	def GetID(self):
		return self.locoid
		
	def SetSpeed(self, speed):
		self.speed = speed
		
	def GetSpeed(self):
		return self.speed
	
	def SetDirection(self, dval):
		self.direction = dval
		
	def GetDirection(self):
		return self.direction
	
	def SetBell(self, bell):
		self.bell = bell
		
	def GetBell(self):
		return self.bell
	
	def SetHorn(self, horn):
		self.horn = horn
		
	def GetHorn(self):
		return self.horn
		
	def SetHeadlight(self, headlight):
		self.headlight = headlight
		
	def GetHeadlight(self):
		return self.headlight

class DCCHandler(BaseHTTPRequestHandler):
	def do_GET(self):
		app = self.server.getApp()
		req = "%s:%s - \"%s\"" % (self.client_address[0], self.client_address[1], self.requestline)

		parsed_path = urlparse(self.path)
		cmdDict = parse_qs(parsed_path.query)
		cmd = parsed_path.path
		if cmd.startswith('/'):
			cmd = cmd[1:]
			
		cmdDict['cmd'] = [cmd]
		rc, b = app.dispatch(cmdDict)
		try:
			body = b.encode()
		except:
			body = b

		if rc == 200:
			self.send_response(200)
			self.send_header("Content-type", "text/plain")
			self.end_headers()
			try:
				self.wfile.write(body)
			except ConnectionAbortedError:
				logging.error("DCC Server connection aborted while sending %s" % str(cmdDict))
		else:
			self.send_response(400)
			self.send_header("Content-type", "text/plain")
			self.end_headers()
			self.wfile.write(body)

class DCCThreadingHTTPServer(ThreadingMixIn, HTTPServer):
	def serve_dcc(self):
		self.haltServer = False
		while self.haltServer == False:
			r = select.select([self.socket], [], [], 0)[0]
			if r and len(r) > 0:
				self.handle_request()
			else:
				pass #time.sleep(0.0001) # yield to other threads

	def setApp(self, app):
		self.app = app

	def getApp(self):
		return self.app

	def shut_down(self):
		self.haltServer = True

class DCCHTTPServer:
	def __init__(self, ip, port, tty):
		self.failed = False
		self.locos = {}
		self.tty = tty
		try:
			self.port = serial.Serial(port=self.tty,
					baudrate=9600,
					bytesize=serial.EIGHTBITS,
					parity=serial.PARITY_NONE,
					stopbits=serial.STOPBITS_ONE, 
					timeout=0)

		except serial.SerialException:
			self.port = None
			logging.error("Unable to Connect to serial port %s" % self.tty)
			self.failed = True

		if not self.failed:
			self.server = DCCThreadingHTTPServer((ip, port), DCCHandler)
			self.server.setApp(self)
			self.thread = Thread(target=self.server.serve_dcc)
			self.thread.start()
			logging.info("DCC server started")
			
	def SetupFailed(self):
		return self.failed
	
	def IsConnected(self):
		return self.port is not None

	def getThread(self):
		return self.thread

	def getServer(self):
		return self.server

	def dispatch(self, cmd):
		self.ProcessDCCCommand(cmd)
		
		rc = 200
		body = b'request received'
		return rc, body

	def close(self):
		self.server.shut_down()
		try:
			self.port.close()
		except:
			pass
		
	def ProcessDCCCommand(self, cmdString):
		logging.info("DCC Command receipt: (%s)" % str(cmdString))
		cmd = cmdString["cmd"][0].lower()

		if cmd == "throttle":
			try:
				locoid = int(cmdString["loco"][0])
			except:
				locoid = None
				
			if locoid is None:
				logging.error("unable to parse locomotive ID: %s" % cmdString["loco"][0])
				return
				
			try:
				speed = int(cmdString["speed"][0])
			except:
				speed = None
				
			try:
				direction = cmdString["direction"][0]
			except:
				direction = None
				
			self.SetSpeedAndDirection(locoid, speed, direction)
		
		elif cmd == "function":
			try:
				locoid = int(cmdString["loco"][0])
			except:
				locoid = None
				
			if locoid is None:
				logging.error("unable to parse locomotive ID: %s" % cmdString["loco"][0])
				return
				
			try:
				headlight = int(cmdString["light"][0])
			except:
				headlight = None
				
			try:
				horn = int(cmdString["horn"][0])
			except:
				horn = None
				
			try:
				bell = int(cmdString["bell"][0])
			except:
				bell = None
				
			self.SetFunction(locoid, headlight, horn, bell)
						
	def SetSpeedAndDirection(self, lid, speed=None, direction=None):
		try:
			loco = self.locos[lid]
		except KeyError:
			loco = Loco(lid)
			self.locos[lid] = loco
			
		if speed is not None:
			loco.SetSpeed(speed)
			
		if direction is not None:
			loco.SetDirection(REVERSE if direction == "R" else FORWARD)
	
		speed = loco.GetSpeed()
		direction = loco.GetDirection()
		
		outb = [ 0xa2 ] + formatLocoID(lid) + [ direction, speed if speed > 4 else 0 ]
		
		self.SendDCC(outb)
		
	def SetFunction(self, lid, headlight=None, horn=None, bell=None):
		try:
			loco = self.locos[lid]
		except KeyError:
			loco = Loco(lid)
			self.locos[lid] = loco
			
		if headlight is not None:
			loco.SetHeadlight(headlight == 1)
			
		if horn is not None:
			loco.SetHorn(horn == 1)
			
		if bell is not None:
			loco.SetBell(bell == 1)
			
		function = 0
		if loco.GetBell():
			function += 0x01
			
		if loco.GetHorn():
			function += 0x02
			
		if loco.GetHeadlight():
			function += 0x10

		outb = [ 0xa2 ] + formatLocoID(lid) + [ 0x07, function & 0xff ]

		self.SendDCC(outb)
		
	def SendDCC(self, outb):
		if self.port is None:
			logging.error("DCC port not open")
			return False
		
		n = self.port.write(bytes(outb))
		if n != len(outb):
			logging.error("incomplete write.  expected to send %d bytes, but sent %d" % (len(outb), n))
		
		tries = 0
		inbuf = []
		while tries < MAXTRIES and len(inbuf) < 1:
			b = self.port.read(1)
			if len(b) == 0:
				tries += 1
				time.sleep(0.001)
			else:
				tries = 0
				inbuf.append(b)
				
		if len(inbuf) != 1:
			return False

		return True



