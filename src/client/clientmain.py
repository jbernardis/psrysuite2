
import time
import json
import logging
import threading
import queue


from client.listener import Listener
from client.rrserver import RRServer


class ClientMain:
	def __init__(self, settings):
		self.settings = settings
		self.clientForever = True
		self.delay = 5  # wait 5 cycles before delayed startup
		self.pause = 0

		self.sessionid = None

		self.cmdQ = queue.Queue()

		self.listener = None

		self.rrServer = RRServer()
		self.rrServer.SetServerAddress(self.settings.ipaddr, self.settings.serverport)

	def AtInterval(self):
		if self.clientForever:
			threading.Timer(0.50, self.AtInterval).start()
			if self.delay is None or self.delay <= 0:
				self.cmdQ.put({"interval": []})
			elif self.delay > 0:
				self.delay -= 1
				if self.delay <= 0:
					self.delay = None
					logging.debug("posting delayed startup command<=====================================")
					self.cmdQ.put({"delayedstartup": []})

	def forever(self):
		logging.info("forever starting")
		self.clientForever = True
		self.delay = 5  # wait 5 cycles before delayed startup
		self.pause = 0
		self.AtInterval()
		while self.clientForever:
			while not self.cmdQ.empty():
				self.ProcessCommand(self.cmdQ.get())
			time.sleep(0.005)

		logging.debug("terminating client")
		self.DisconnectServer()
		logging.info("completed - continuing with shutdown")

	def ProcessCommand(self, msg):
		logging.debug("Process message: %s" % str(msg))
		for cmd, parms in msg.items():
			logging.debug("Dispatch: %s %s" % (cmd, str(parms)))
			if cmd == "delayedstartup":
				logging.debug("starting listener")
				self.listener = Listener(self, self.settings.ipaddr, self.settings.socketport)
				if not self.listener.connect():
					logging.error("Unable to establish connection with server")
					self.listener = None
					return
				self.listener.start()
				logging.debug("listener started")

			elif cmd == "sessionID":
				self.sessionid = int(parms)
				self.Request({"identify": {"SID": self.sessionid, "function": "CLIENT"}})
				self.Request({"refresh": {"SID": self.sessionid}})

	def DisconnectServer(self):
		self.listener.kill()
		self.listener.join()
		self.listener = None

	def raiseDeliveryEvent(self, data):  # thread context
		logging.debug("delivery event: %s" % str(data))
		try:
			jdata = json.loads(data)
		except json.decoder.JSONDecodeError:
			logging.debug("json decode error")
			return
		self.cmdQ.put(jdata)

	def raiseDisconnectEvent(self): # thread context
		print("disconnect event")
		self.clientForever = False

	def Request(self, req):
		logging.debug("sending command: %s" % str(req))
		self.rrServer.SendRequest(req)

	def onDisconnectEvent(self, _):
		self.DisconnectServer()
		exit(1)
