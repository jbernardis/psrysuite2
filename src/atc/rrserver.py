import requests
import logging

class RRServer(object):
	def __init__(self):
		self.ipAddr = None
	
	def SetServerAddress(self, ip, port):
		self.ipAddr = "http://%s:%s" % (ip, port)

	def SendRequest(self, req):
		for cmd, parms in req.items():
			try:
				requests.get(self.ipAddr + "/" + cmd, params=parms, timeout=0.5)
			except requests.exceptions.ConnectionError:
				logging.error("Unable to send request  is rr server running?")
				
	def Get(self, cmd, parms):
		try:
			r = requests.get(self.ipAddr + "/" + cmd, params=parms, timeout=4.0)
		except requests.exceptions.ConnectionError:
			logging.error("Unable to send request  is rr server running?")
			return None
		
		if r.status_code >= 400:
			logging.error("HTTP Error %d" % r.status_code)
			return None
		
		return r.json()
