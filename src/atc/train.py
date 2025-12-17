class Trains:
	def __init__(self, rrserver):
		self.RRServer = rrserver
		TrainsJson = rrserver.Get("gettrains", {})

		self.trainlist = []
		self.trainmap = {}
		for tid, trData in TrainsJson.items():
			if len(trData["sequence"]) > 0:
				tr = self.AddTrain(tid, trData["eastbound"])
				tr.SetStartBlock(trData["startblock"])
				tr.SetStartSubBlock(trData["startsubblock"])
				tr.SetStartBlockTime(trData["time"])
				tr.SetSteps(trData["sequence"])

				tr.SetNormalLoco(trData["normalloco"])
				self.trainmap[tid] = tr
			elif trData["template"] is not None:
				p = trData["template"]
				prData = TrainsJson[p]
				tr = self.AddTrain(tid, prData["eastbound"])
				tr.SetStartBlock(prData["startblock"])
				tr.SetStartSubBlock(prData["startsubblock"])
				tr.SetStartBlockTime(prData["time"])
				tr.SetSteps(prData["sequence"])

				tr.SetNormalLoco(trData["normalloco"])
				self.trainmap[tid] = tr

	def __iter__(self):
		self._nx_ = 0
		return self

	def __next__(self):
		if self._nx_ >= len(self.trainlist):
			raise StopIteration

		nx = self._nx_
		self._nx_ += 1
		return self.trainlist[nx]

	def GetTrainList(self):
		return [tr.GetTrainID() for tr in self.trainlist]

	def AddTrain(self, tid, east):
		tr = Train(tid)
		tr.SetDirection(east)
		self.trainlist.append(tr)
		self.trainmap[tid] = tr
		return tr

	def DelTrainByTID(self, tid):
		if tid not in self.trainmap:
			return False

		del self.trainmap[tid]

		newtr = [tr for tr in self.trainlist if tr.GetTrainID() != tid]
		self.trainlist = newtr

	def GetTrainById(self, tid):
		if tid not in self.trainmap:
			return None

		return self.trainmap[tid]


class Train:
	def __init__(self, tid):
		self.tid = tid
		self.east = True
		self.steps = []
		self.startblock = None
		self.startsubblock = None
		self.startblocktime = 5000
		self.normalLoco = None

	def SetDirection(self, direction):
		self.east = direction

	def GetTrainID(self):
		return self.tid

	def IsEast(self):
		return self.east

	def SetSteps(self, steps):
		self.steps = [x for x in steps]

	def GetNSteps(self):
		return len(self.steps)

	def GetSteps(self):
		return [x for x in self.steps]

	def SetStartBlockTime(self, time):
		self.startblocktime = time

	def GetStartBlockTime(self):
		return self.startblocktime

	def SetStartBlock(self, blk):
		self.startblock = blk

	def GetStartBlock(self):
		return self.startblock

	def SetStartSubBlock(self, blk):
		self.startsubblock = blk

	def GetStartSubBlock(self):
		return self.startsubblock

	def SetNormalLoco(self, loco):
		self.normalLoco = loco

	def GetNormalLoco(self):
		return self.normalLoco

	def ToJSON(self):
		return {"eastbound": self.east, "startblock": self.startblock, "startsubblock": self.startsubblock,
				"time": self.startblocktime, "sequence": self.steps}

