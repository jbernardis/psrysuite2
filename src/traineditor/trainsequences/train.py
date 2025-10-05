import json
import os

from dispatcher.train import CopyTrainReferences

class Train:
	def __init__(self, tid):
		self.tid = tid
		self.east = True
		self.steps = []
		self.startblock = None
		self.startsubblock = None
		self.startblocktime = 5000
		self.normalLoco = None
		self.route = None
		
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

	def SetRoute(self, route):
		self.route = route

	def GetRoute(self):
		return self.route

	def ToJSON(self):
		return {"eastbound": self.east, "startblock": self.startblock, "startsubblock": self.startsubblock, "time": self.startblocktime, "sequence": self.steps, "route": self.route}


class Trains:
	def __init__(self, rrserver, copyrefs=False):
		self.RRServer = rrserver
		TrainsJson = rrserver.Get("gettrains", {})
		if copyrefs:
			CopyTrainReferences(TrainsJson)

		self.trainlist = []
		self.trainmap = {}
		for tid, trData in TrainsJson.items():
			if "route" not in trData:
				trData["route"] = None

			tr = self.AddTrain(tid, trData["eastbound"])
			tr.SetStartBlock(trData["startblock"])
			tr.SetStartSubBlock(trData["startsubblock"])
			tr.SetStartBlockTime(trData["time"])
			tr.SetSteps(trData["sequence"])
			tr.SetRoute(trData["route"])

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
		
	def Save(self):
		TrainsJson = self.RRServer.Get("gettrains", {})

		delList = []
		for tid in TrainsJson:
			if tid not in self.trainmap:
				delList.append(tid)
				
		for tid in delList:
			TrainsJson[tid]["sequence"] = []
			TrainsJson[tid]["startblock"] = None
			TrainsJson[tid]["startsubblock"] = None
			TrainsJson[tid]["time"] = None
			
		for tr in self.trainlist:
			tid = tr.GetTrainID()
			if tid not in TrainsJson:
				# put in default values for all of the traintracker fields
				TrainsJson[tid] = {
					"tracker": [],
					"block": None,
					"cutoff": False,
					"desc": None,
					"loco": None,
					"route": None,
					"normalloco": None,
					"origin": { "loc": None, "track": None },
					"terminus": { "loc": None, "track": None }
					}


			TrainsJson[tid].update(tr.ToJSON())
			
		self.RRServer.Post("trains.json", "data", TrainsJson)
		
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
	