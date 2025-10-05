import logging
import json
from dispatcher.constants import FRONT, REPLACE

class TrainList:
	def __init__(self, parent):
		self.parent = parent
		self.trains = {}

	def SetAtc(self, train, atcflag):
		if train not in self.trains:
			return 
		
		self.trains[train]["atc"] = atcflag

	def Update(self, train, loco, blocks, east, action, route=None):
		if len(blocks) == 0:
			return

		if train is None:
			# search for and remove the block from the table
			dellist = []
			for tr in self.trains:
				for b in blocks:
					if b in self.trains[tr]["blocks"]:
						self.trains[tr]["blocks"].remove(b)
						try:
							self.trains[tr]["blockorder"].remove(b)
						except:
							pass
						if len(self.trains[tr]["blocks"]) == 0:
							dellist.append(tr)
				if len(self.trains[tr]["blocks"]) == 1:
					bn = self.trains[tr]["blocks"][0]
					if bn in [ "KOSN10S11", "KOSN20S21" ]:
						dellist.append(tr)

			for tr in dellist:
				del(self.trains[tr])

		else:
			if train in self.trains:
				if action == REPLACE:
					self.trains[train]["blocks"] = [b for b in blocks]
					self.trains[train]["blockorder"] = [b for b in blocks]
				else:
					for b in blocks:
						if b not in self.trains[train]["blocks"]:
							if action == FRONT:
								self.trains[train]["blocks"].append(b)
								self.trains[train]["blockorder"].append(b)
							else:
								self.trains[train]["blocks"] = [b] + self.trains[train]["blocks"]
								self.trains[train]["blockorder"] = [b] + self.trains[train]["blockorder"]
				if loco:
					self.trains[train]["loco"] = loco
				self.trains[train]["east"] = east
				self.trains[train]["route"] = route
			else:
				self.trains[train] = {"blocks": [b for b in blocks], "blockorder": [b for b in blocks], "loco": loco, "atc": False, "signal": None, "aspect": 0, "east": east, "route": route}

	def DeleteTrain(self, trid):
		try:
			del self.trains[trid]
		except KeyError:
			pass

	def Dump(self):
		print("==========================start of trains dump")
		for trid in self.trains:
			print("%s: %s" % (trid, json.dumps(self.trains[trid])))
		print("==========================end of trains dump", flush=True)
				
	def UpdateSignal(self, train, signal, aspect):
		if train not in self.trains:
			return 
		
		self.trains[train]["signal"] = signal
		self.trains[train]["aspect"] = int(aspect)
				
	def UpdateEngineer(self, train, engineer):
		if train not in self.trains:
			return 
		
		self.trains[train]["engineer"] = engineer

	def UpdateTrainBlockOrder(self, train, blocks):
		if train not in self.trains:
			return

		self.trains[train]["blockorder"] = [b for b in blocks]
		logging.debug("updating train block order to %s" % str(blocks))

	def FindTrainInBlock(self, block):
		for tr, trinfo in self.trains.items():
			if block in trinfo["blocks"]:
				return tr, trinfo["loco"]

		return None, None

	def RemoveTrainFromBlock(self, trn, blk):
		try:
			trinfo = self.trains[trn]
		except KeyError:
			return False

		try:
			trinfo["blocks"].remove(blk)
		except ValueError:
			return False

		if len(trinfo["blocks"]) == 0:
			del self.trains[trn]

		return True
	
	def GetTrainInfo(self, trid):
		if trid in self.trains:
			return self.trains[trid]
		
		return None

	def GetTrainBlocks(self, trid):
		try:
			return self.trains[trid]["blocks"]
		except KeyError:
			return []

	def HasTrain(self, trid):
		return trid in self.trains

	def GetLocoForTrain(self, trn):
		for tr, trinfo in self.trains.items():
			if tr == trn:
				return trinfo["loco"]

		return None

	def RenameTrain(self, oname, nname, oloco, nloco, oroute, nroute, east):
		if oname == nname and oloco == nloco:
			rc = False
			try:
				croute = self.trains[oname]["route"]
			except KeyError:
				croute = None
			if nroute != croute:
				self.trains[oname]["route"] = nroute
				rc = True

			if east is not None:
				self.trains[oname]["east"] = east
				return True
			else:
				return rc
			
		if oname != nname:
			if oname not in self.trains:
				# we can't do anything if we can't find the original record
				return False

			if nname in self.trains:
				# in this case, we retain the old information, but merge the block lists
				for b in self.trains[oname]["blocks"]:
					if b not in self.trains[nname]["blocks"]:
						self.trains[nname]["blocks"].append(b)
			else:
				self.trains[nname] = self.trains[oname]

			del(self.trains[oname])

		else:
			# the old name and the new name are the same - make sure the train exists
			if nname not in self.trains:
				logging.error("Trying to change parameters on a non-existant train: %s" % nname)
				return False

		if nroute is not None:
			self.trains[nname]["route"] = nroute

		if nloco is not None:
			self.trains[nname]["loco"] = nloco
			
		if east is not None:
			self.trains[nname]["east"] = east

		return True

	def SetEast(self, name,east):
		if name not in self.trains:
			return

		if east is not None:
			self.trains[name]["east"] = east
	
	def GetTrainList(self):
		return self.trains

	def GetSetTrainCmds(self, train=None, nameonly=False):
		nameflag = "1" if nameonly else "0"
		for tr, trinfo in self.trains.items():
			if train is None or train == tr:
				loco = trinfo["loco"]
				blocks = trinfo["blockorder"]
				if len(blocks) == 0:
					frontblock = None
				else:
					frontblock = blocks[-1]
				atc = trinfo["atc"]
				signal = trinfo["signal"]
				aspect = "%d" % trinfo["aspect"]
				east = trinfo["east"]
				stParams = {"blocks": blocks, "name": tr, "loco": loco, "atc": atc, "east": east, "nameonly": nameflag}
				if trinfo["route"] is not None:
					stParams["route"] = trinfo["route"]
				yield ({"settrain": stParams})
				yield({"trainsignal": {"train": tr, "block": frontblock, "signal": signal, "aspect": aspect}})

				try:
					eng = trinfo["engineer"]
				except KeyError:
					eng = None
					
				p = {"train": tr, "reassign": 0}
				if eng is not None:
					p["engineer"] = eng
				
				yield({"assigntrain": [p]})
				
				
