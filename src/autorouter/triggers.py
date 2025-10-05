from traineditor.generators import GenerateAR

TriggerPointFront = 'F'  # front of train
TriggerPointRear = 'R'  # rear of train


class Triggers:
	def __init__(self, trainSeq):
		self.trainSeq = trainSeq
		self.triggerTable = {}
			
	def AddTrain(self, trid, route=None):
		rttr = trid if route is None else route
		tr = self.trainSeq.GetTrainById(rttr)
		_, script = GenerateAR(tr, None)
		self.triggerTable[trid] = script
		
	def RemoveTrain(self, trid):
		try:
			del self.triggerTable[trid]
		except:
			pass	

	def GetRoute(self, train, block):
		if train not in self.triggerTable:
			return None

		if block not in self.triggerTable[train]:
			return None

		return self.triggerTable[train][block]["route"]

	def GetTriggerPoint(self, train, block):
		if train not in self.triggerTable:
			return TriggerPointFront

		if block not in self.triggerTable[train]:
			return TriggerPointFront

		return self.triggerTable[train][block]["trigger"]
	
	def IsOrigin(self, train, block):
		if train not in self.triggerTable:
			return False
		
		return block == self.triggerTable[train]["origin"]
	
	def GetOrigin(self, train):
		if train not in self.triggerTable:
			return None
		
		return self.triggerTable[train]["origin"]
	
	def IsTerminus(self, train, block):
		if train not in self.triggerTable:
			return False
		
		return block == self.triggerTable[train]["terminus"]
	
	def GetTerminus(self, train):
		if train not in self.triggerTable:
			return None
		
		return self.triggerTable[train]["terminus"]
