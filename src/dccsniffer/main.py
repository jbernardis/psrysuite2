import os, sys
cmdFolder = os.getcwd()
if cmdFolder not in sys.path:
	sys.path.insert(0, cmdFolder)

import time
import queue

# ofp = open(os.path.join(os.getcwd(), "output", "dccsniffer.out"), "w")
# efp = open(os.path.join(os.getcwd(), "output", "dccsniffer.err"), "w")
# sys.stdout = ofp
# sys.stderr = efp

import json
import logging
logging.basicConfig(filename=os.path.join(os.getcwd(), "logs", "dccsniffer.log"), filemode='w', format='%(asctime)s %(message)s', level=logging.DEBUG)

from dispatcher.settings import Settings
from dccsniffer.sniffer import Sniffer
from dccsniffer.rrserver import RRServer
from dccsniffer.listener import Listener
from dccsniffer.ticker import Ticker


class MainUnit:
	def __init__(self):
		self.settings = Settings()
		self.identified = False
		self.connected = False
		self.locoMap = {}

		self.cmdQ = queue.Queue()

		self.rrServer = RRServer()
		self.rrServer.SetServerAddress(self.settings.ipaddr, self.settings.serverport)

		self.ticker = Ticker(self, interval=self.settings.dccsniffer.interval)
		
		self.sniffer = Sniffer(self)
		self.sniffer.connect(self.settings.dccsniffer.tty)
		if not self.sniffer.isConnected():
			logging.error("Unable to connect to port %s for DCC sniffer" % self.settings.dccsniffer.tty)

		else:			
			self.listener = Listener(self, self.settings.ipaddr, self.settings.socketport)
			if not self.listener.connect():
				logging.error("Unable to establish connection with railroad server")
				self.listener = None

			else:
				logging.info("Connection with railroad server successfully created")
				self.connected = True
	
	def IsConnected(self):
		return self.connected

	def start(self):
		logging.info("starting listener thread")
		self.listener.start()

	def run(self):
		# wait until handshake with server is complete
		while not self.identified:
			time.sleep(0.001)
			
		logging.info("starting sniffer thread")
		self.sniffer.start()

		logging.info("starting poller thread")
		self.ticker.start()

		while self.sniffer.isRunning():
			while not self.cmdQ.empty():
				self.ProcessCommand(self.cmdQ.get())

			try:
				time.sleep(0.001)
			except KeyboardInterrupt:
				self.sniffer.kill()

		self.terminateAll()

	def raiseIntervalEvent(self): # thread context
		self.cmdQ.put({"cmd": "interval"})

	def raiseDCCEvent(self, cmd): # thread context
		self.cmdQ.put(cmd)

	def ProcessCommand(self, cmd):
		command = cmd["cmd"]

		if command == "interval":
			# interval - construct and send a message of new or changed speed values
			msgMap = {}
			for loco, locomap in self.locoMap.items():
				if locomap["speed"] != locomap["lastspeed"] or locomap["stype"] != locomap["laststype"]:
					msgMap[loco] = {"speed": locomap["speed"], "speedtype": locomap["stype"]}
					locomap["lastspeed"] = locomap["speed"]
					locomap["laststype"] = locomap["stype"]

			if len(msgMap) > 0:
				msgData = {lid: [linfo["speed"], linfo["speedtype"]] for lid, linfo in msgMap.items()}
				msg = {"dccspeeds": msgData}
				self.rrServer.SendRequest(msg)

		elif command == "dccspeed":
			# dcc speed command from the dcc bus = record the information
			loco = cmd["loco"]
			if loco not in self.locoMap:
				self.locoMap[loco] = {"lastspeed": None, "laststype": None}
			self.locoMap[loco]["speed"] = cmd["speed"]
			self.locoMap[loco]["stype"] = cmd["stype"]

	def raiseDeliveryEvent(self, data):  # thread context
		jdata = json.loads(data)
		for cmd, parms in jdata.items():
			if cmd == "sessionID":
				self.sessionid = int(parms)
				logging.info("session ID %d" % self.sessionid)
				self.rrServer.SendRequest({"identify": {"SID": self.sessionid, "function": "DCCSNIFFER"}})
				self.identified = True
		
	def raiseDisconnectEvent(self): # thread context
		self.terminateAll()

	def terminateAll(self):
		logging.info("Terminating sniffer")
		try:
			self.sniffer.kill()
		except:
			pass

		logging.info("Terminating poller")
		try:
			self.poller.kill()
		except:
			pass

		logging.info("Terminating listener thread")
		try:
			self.listener.kill()
		except:
			pass

		sys.exit(0)


main = MainUnit()
if main.IsConnected():
	main.start()
	main.run()
	
