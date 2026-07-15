import requests


class RRServer(object):
	def __init__(self):
		self.ipAddr = None
	
	def SetServerAddress(self, ip, port):
		self.ipAddr = "http://%s:%s" % (ip, port)

	def Request(self, req):
		rc = True
		for cmd, parms in req.items():
			try:
				r = requests.get(self.ipAddr + "/" + cmd, params=parms, timeout=0.5)
			except requests.exceptions.ConnectionError:
				rc = False
		if rc:
			print("URL: %s" % str(r.url), flush=True)
		return rc

	def Get(self, cmd, parms):
		try:
			r = requests.get(self.ipAddr + "/" + cmd, params=parms, timeout=4.0)
		except requests.exceptions.ConnectionError:
			return None

		if r.status_code >= 400:
			return None

		return r.json()

