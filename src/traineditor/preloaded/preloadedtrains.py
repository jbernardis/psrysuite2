PRELOADFILE = "preloads.json"


class PreLoadedTrains:
	def __init__(self, rrserver):
		self.trainNames = []
		self.trainMap = {}
		self.RRServer = rrserver
		self.preloadedTrains = rrserver.Get("getfile", {"file": PRELOADFILE})
		if self.preloadedTrains is None:
			self.preloadedTrains = []
		self.setArrays()

	def setArrays(self):
		self.trainNames = sorted([t["name"] for t in self.preloadedTrains])
		self.trainMap = {}
		for tr in self.preloadedTrains:
			self.trainMap[tr["name"]] = tr
		
	def save(self):
		self.RRServer.Post(PRELOADFILE, "data", self.preloadedTrains)
	
	def getPreloadedTrainsList(self):
		return self.preloadedTrains
	
	def add(self, tr):
		trname = tr["name"]
		if trname in self.trainMap:
			return False
		
		self.preloadedTrains.append(tr)
		self.setArrays()
		return True
	
	def delete(self, trname):
		if trname not in self.trainNames:
			return False

		newtl = []
		for tr in self.preloadedTrains:
			if tr["name"] != trname:
				newtl.append(tr)

		self.preloadedTrains = newtl
		self.setArrays()
		return True

	def modify(self, trname, trinfo):
		if trname not in self.trainNames:
			return False

		tr = self.trainMap[trname]
		tr["east"] = trinfo["east"]
		tr["loco"] = trinfo["loco"]
		tr["block"] = trinfo["block"]
		tr["route"] = trinfo["route"]
		return True

