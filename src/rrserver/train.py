import logging
import time

from dispatcher.constants import aspectname, aspecttype, RegAspects


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
		self.aspect = None
		self.aspectType = None
		self.pastSignal = False
		self.stopped = False
		self.templateTrain = None
		self.templateSeq = []
		self.signal = None
		self.assigntime = None

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

	def WantedRoute(self, osname):
		seq = self.Sequence()
		if seq is None or len(seq) == 0:
			return None

		for step in seq:
			if osname == step["os"]:
				return step["route"]

		return None

	def WantedRouteFromFrontBlock(self):
		seq = self.Sequence()
		if seq is None or len(seq) == 0:
			return None

		fb = self.FrontBlock().Name()
		if fb.endswith(".E") or fb.endswith(".W"):
			fb = fb[:-2]

		for sx in range(len(seq)):
			step = seq[sx]
			if fb == step["block"]:
				# we found it - but we need to look at the next step to get the route name
				if sx < len(seq)-1:
					step = seq[sx+1]
					return step["route"]
				else:
					return None

		return None

	def SetName(self, name, roster=None):
		self.roster = roster
		self.rname = name

	def SetSignal(self, sig):
		# first remove the train from its old controlling signal
		if self.signal is not None:
			tr = self.signal.Train()
			if tr is not None and tr.Name() == self.Name():
				self.signal.SetTrain(None)

		self.signal = sig
		if sig is None:
			self.aspect = 0
			self.aspectType = RegAspects
			self.pastSignal = False
		else:
			self.aspect = sig.Aspect()
			self.aspectType = sig.AspectType()
			self.pastSignal = False
			sig.SetTrain(self)

	def SetAspect(self, aspect, aspectType, force=False):
		if force or not self.pastSignal:
			self.aspect = aspect
			self.aspectType = aspectType

	def PassSignal(self, flag=True):
		self.pastSignal = flag

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
		if e is None:
			self.assigntime = None
		else:
			if self.engineer != e:
				self.assigntime = time.time()
		self.engineer = e

	def SetTemplateTrain(self, tn):
		self.templateTrain = tn

	def TemplateTrain(self):
		return self.templateTrain

	def SetTemplateSeq(self, seq):
		self.templateSeq = seq

	def Sequence(self):
		if self.templateTrain is not None:
			return self.templateSeq

		if self.roster:
			return self.roster["sequence"]

		return []

	def Loco(self):
		return self.loco

	def SetLoco(self, l):
		self.loco = l

	def AspectName(self):
		if self.aspect is None or self.aspectType is None:
			return None

		return "%s (%s)" % (aspectname(self.aspect, self.aspectType), aspecttype(self.aspectType))

	def Blocks(self):
		return self.blocks

	def AddBlock(self, b, rear=False):
		blk = b.GetMainBlock()
		# the first block in the train is the rear of the train
		if rear:
			self.blocks = [blk] + self.blocks
		else:
			self.blocks.append(blk)

	def FrontBlock(self):
		if len(self.blocks) == 0:
			return None

		return self.blocks[-1]

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
			"template": self.templateTrain,
			"loco": self.loco,
			"engineer": self.engineer,
			"blocks": [b.Name() for b in self.blocks],
			"stopped": self.stopped,
			"signal": None if self.signal is None else self.signal.Name(),
			"aspect": self.aspect,
			"aspecttype": self.aspectType,
			"pastsignal": self.pastSignal,
			"assigntime": self.assigntime
		}

		return {"train": [parms]}

