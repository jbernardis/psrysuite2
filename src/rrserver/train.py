import logging


class Train:
	tx = 0

	def __init__(self):
		self.iname = Train.NextName()  # the internal ?? name initially assigned to ALL trains
		self.rname = None  # the name are retrieved from the train roster database - or provided by the usewr
		self.roster = None
		self.east = True
		self.loco = None
		self.engineer = None
		self.blocks = []

	def IsIdentified(self):
		return self.rname is not None

	def Name(self):
		return self.iname if self.rname is None else self.rname

	def IName(self):
		return self.iname

	def SetName(self, name, roster=None):
		self.roster = roster
		self.rname = name

	def IsEast(self):
		return self.east

	def SetEast(self, east):
		self.east = east

	def Engineer(self):
		return self.engineer

	def SetEngineer(self, e):
		self.engineer = e

	def Loco(self):
		return self.loco

	def SetLoco(self, l):
		self.loco = l

	def Blocks(self):
		return self.blocks

	def AddBlock(self, b, rear=False):
		blk = b.GetMainBlock()
		# the first block in the train is the rear of the train
		if rear:
			self.blocks = [blk] + self.blocks
		else:
			self.blocks.append(blk)

	def RemoveBlock(self, rblk):
		logging.debug("we want to remove block %s from train %s" % (rblk.Name(), self.Name()))
		logging.debug("before train blocks = %s" % ", ".join([blk.Name() for blk in self.blocks]))
		# rblk.SetTrain(None)
		self.blocks = [blk for blk in self.blocks if blk.Name() != rblk.Name()]
		logging.debug("after train blocks = %s" % ", ".join([blk.Name() for blk in self.blocks]))

	@classmethod
	def NextName(cls):
		rv = "??%s" % Train.tx
		Train.tx += 1
		return rv

	def GetEventMessage(self):
		parms = {
			"iname": self.iname,
			"rname": self.rname,
			"east": self.east,
			"loco": self.loco,
			"engineer": self.engineer,
			"blocks": [b.Name() for b in self.blocks]
		}
		return {"train": [parms]}

