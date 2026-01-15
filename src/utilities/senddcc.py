import requests


class RRServer(object):
	def __init__(self):
		self.ipAddr = None

	def SetServerAddress(self, ip, port):
		self.ipAddr = "http://%s:%s" % (ip, port)

	def SendRequest(self, req):
		for cmd, parms in req.items():
			try:
				r = requests.get(self.ipAddr + "/" + cmd, params=parms, timeout=0.5)
				print("%s" % r.url)
			except requests.exceptions.ConnectionError:
				print("Unable to send request  is rr server running?")


rrs = RRServer()
rrs.SetServerAddress("192.168.68.81", "9000")

msgData = {"226": [50, "F"], "277": [60, "R"]}
msg = {"dccspeeds": msgData}
rrs.SendRequest(msg)
