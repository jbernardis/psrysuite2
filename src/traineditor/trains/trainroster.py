
class TrainRoster:
	def __init__(self, rrserver):
		self.RRServer = rrserver
		self.trains = rrserver.Get("gettrains", {})
			
		for tid in self.trains:
			trn = self.trains[tid]
			trn["block"] = None
			trn["loco"] = trn["normalloco"]

	def __iter__(self):
		self.order = sorted(self.trains.keys())
		self._tx = 0
		return self
		
	def __next__(self):
		if self._tx >= len(self.order):
			raise StopIteration
		
		rv = self.order[self._tx]
		self._tx += 1
		return rv
				
	def getTrainList(self):
		return list(self.trains.keys())
	
	def getTrain(self, tid):
		if not tid in self.trains:
			return None
		
		return self.trains[tid]
	
	def getTrainByLoco(self, loco):
		for tid in self.trains:
			if loco == self.trains[tid]["loco"]:
				return tid
			
		return None
