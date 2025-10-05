import logging

class RouteRequest:
	def __init__(self, train, route, entryblk):
		self.train = train
		self.route = route
		self.entryblk = entryblk
		logging.info("Generating route request: %s" % self.toString())

	def GetName(self):
		return self.route.GetName()

	def GetOS(self):
		return self.route.GetOS()

	def GetTrain(self):
		return self.train

	def GetEntryBlock(self):
		return self.entryblk
	
	def toString(self):
		return "Route Request: Trn:%s Rte:%s OS:%s Blk:%s" % (self.train, self.route.GetName(), self.route.GetOS(), self.entryblk)

	def Print(self):
		print(self.toString())
		self.route.Print()