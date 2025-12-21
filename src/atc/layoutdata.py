import json


class LayoutData:
	def __init__(self, rrserver):
		self.rrserver = rrserver
		self.layout = rrserver.Get("getlayout", {})
		self.subblocks = rrserver.Get("getsubblocks", {})
		self.iobits = self.rrserver.Get("getiobits", {})

		if self.layout is None or self.subblocks is None or self.iobits is None:
			self.RRConnected = False
			print("Unable to retrieve layout, subblock and/or iobits information from server")
			return

		self.RRConnected = True

		self.routes = self.layout["routes"]
		self.crossovers = self.layout["crossover"]
		self.blocks = self.layout["blocks"]

	def IsConnected(self):
		return self.RRConnected

	def GetOSActiveRoute(self, rtName):
		rt = self.routes.get(rtName, None)
		return rt
