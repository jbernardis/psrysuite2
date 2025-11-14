import logging
from dispatcher.constants import aspectname, aspecttype


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
		self.lastAspect = None
		self.lastAspectType = None
		self.stopped = False
		self.atc = False
		self.ar = False
		self.templateTrain = None
		self.signal = None

	def IsIdentified(self):
		return self.rname is not None

	def SetStopped(self, flag):
		rc = flag != self.stopped  # True indicates a value was changed
		self.stopped = flag
		return rc

	def Stopped(self):
		return self.stopped

	def Name(self):
		return self.iname if self.rname is None else self.rname

	def SetRoster(self, roster):
		self.roster = roster

	def IName(self):
		return self.iname

	def RName(self):
		return self.rname

	def Roster(self):
		return self.roster

	def SetName(self, name, roster=None):
		self.roster = roster
		self.rname = name

	def SetSignal(self, sig):
		self.signal = sig

	def Signal(self):
		return self.signal

	def IsEast(self):
		return self.East()

	def East(self):
		return self.east

	def SetEast(self, east):
		if east is None:
			return

		self.east = east

	def Engineer(self):
		return self.engineer

	def SetEngineer(self, e):
		self.engineer = e

	def SetTemplateTrain(self, tn):
		self.templateTrain = tn

	def TemplateTrain(self):
		return self.templateTrain

	def Loco(self):
		return self.loco

	def SetLoco(self, l):
		self.loco = l

	def SetATC(self, atc):
		if atc is None:
			return

		self.atc = atc

	def ATC(self):
		return self.atc

	def SetAR(self, ar):
		if ar is None:
			return

		self.ar = ar

	def AR(self):
		return self.ar

	def SetLastAspect(self, aspect, aspectType):
		self.lastAspect = aspect
		self.lastAspectType = aspectType
		logging.debug("%s set lastaspect to %s and lastaspecttype to %s" % (self.iname, aspect, aspectType))

	def AspectName(self):
		logging.debug("%s aspectname lastaspect to %s and lastaspecttype to %s" % (self.iname, self.lastAspect, self.lastAspectType))
		if self.lastAspect is None or self.lastAspectType is None:
			return None

		return "%s (%s)" % (aspectname(self.lastAspect, self.lastAspectType), aspecttype(self.lastAspectType))

	def Blocks(self):
		return self.blocks

	def AddBlock(self, b, rear=False):
		blk = b.GetMainBlock()
		# the first block in the train is the rear of the train
		if rear:
			self.blocks = [blk] + self.blocks
		else:
			self.blocks.append(blk)

	def ReverseBlocks(self):
		self.blocks = list(reversed(self.blocks))

	def BlockCount(self):
		return len(self.blocks)

	def ClearBlocks(self):
		self.blocks = []

	def RemoveBlock(self, rblk):
		self.blocks = [blk for blk in self.blocks if blk.Name() != rblk.Name()]

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
			"blocks": [b.Name() for b in self.blocks],
			"stopped": self.stopped,
			"atc": self.atc,
			"ar": self.ar,
			"signal": self.signal.Name(),
			"aspect": self.lastAspect,
			"aspecttype": self.lastAspectType
		}
		return {"train": [parms]}

