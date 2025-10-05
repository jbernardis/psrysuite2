import requests
import logging

class DCCServer(object):
	def __init__(self):
		self.ipAddr = None
	
	def SetServerAddress(self, ip, port):
		self.ipAddr = "http://%s:%s" % (ip, port)

	def SendRequest(self, req):
		for cmd, parms in req.items():
			try:
				logging.info("sending to dcc server: %s %s" % (cmd, str(parms)))
				requests.get(self.ipAddr + "/" + cmd, params=parms, timeout=0.5)
			except:
				logging.error("Unable to send request  is dcc server running?")

