import logging
import copy

ST_FWD    = "f"
ST_FWD128 = "F"
ST_REV    = "r"
ST_REV128 = "R"
ST_STOP   = "s"
ST_ESTOP  = "e"

from dispatcher.constants import REAR


# def formatThrottle(speed, speedType):
# 	speedStr = "%3d" % int(speed)
#
# 	if speedType == ST_FWD128:
# 		return speedStr
# 	elif speedType == ST_FWD:
# 		return "%s/28" % speedStr
# 	elif speedType == ST_REV128:
# 		return "(%s)" % speedStr
# 	elif speedType == ST_REV:
# 		return "(%s/28)" % speedStr
# 	else:
# 		return speedStr
#
#
# def CopyTrainReferences(tl):
# 	copylist = []
# 	for trid, trinfo in tl.items():
# 		try:
# 			route = trinfo["route"]
# 		except KeyError:
# 			route = None
#
# 		if route is not None:
# 			if route not in tl:
# 				logging.debug("removing train %s as the base route for train %s" % (route, trid))
# 				tl[trid]["route"] = None
# 			else:
# 				copylist.append([trid, route])
#
# 	for trid, route in copylist:
# 		tl[trid] = copy.deepcopy(tl[route])
# 		tl[trid]["route"] = route

class Train:
	def __init__(self, iname, rname, east, loco, engineer):
		self.iname = iname
		self.rname = rname
		self.east = east
		self.loco = loco
		self.engineer = engineer
		self.roster = None
		self.stopped = False
		self.aspect = None
		self.aspectType = None
		self.pastSignal = False
		self.atc = False
		self.ar = False
		self.signal = None
		self.templateTrain = None
		self.pinpoint = False
		self.misrouted = False

		self.blocks = []

	def Name(self):
		if self.rname is not None:
			return self.rname

		return self.iname

	def IName(self):
		return self.iname

	def RName(self):
		return self.rname

	def IsIdentified(self):
		return self.rname is not None

	def Loco(self):
		if self.loco is None:
			return "??"
		else:
			return self.loco

	def SetRName(self, rname):
		self.rname = rname

	def SetEast(self, east):
		self.east = east

	def IsEast(self):
		return self.east

	def East(self):
		return self.east

	def SetLoco(self, loco):
		self.loco = loco

	def SetEngineer(self, engineer):
		self.engineer = engineer

	def Engineer(self):
		return self.engineer

	def SetSignal(self, sn):
		self.signal = sn

	def Signal(self):
		return self.signal

	def SetRoster(self, rname, roster):
		self.rname = rname
		self.roster = roster

	def SetTemplateTrain(self, tn):
		self.templateTrain = tn

	def TemplateTrain(self):
		return self.templateTrain

	def SetStopped(self, flag):
		self.stopped = flag

	def Stopped(self):
		return self.stopped

	def SetATC(self, flag):
		self.atc = flag

	def ATC(self):
		return self.atc

	def SetAR(self, flag):
		self.ar = flag

	def AR(self):
		return self.ar

	def SetAspect(self, aspect, aspecttype, pastSignal=None):
		self.aspect = aspect
		self.aspectType = aspecttype
		if pastSignal is not None:
			self.pastSignal = pastSignal

	def Aspect(self):
		return self.aspect, self.aspectType, self.pastSignal

	def SetBlocks(self, blocks):
		delblocks = [bn for bn in self.blocks if bn not in blocks]
		newblocks = [bn for bn in blocks if bn not in self.blocks]
		self.blocks = blocks
		return delblocks, newblocks

	def Blocks(self):
		return self.blocks

	def FrontBlock(self):
		if self.BlockCount() == 0:
			return None

		return self.blocks[-1]

	def BlockCount(self):
		return len(self.blocks)

	def SetPinpoint(self, flag=True):
		if self.pinpoint == flag:
			return False
		self.pinpoint = flag
		return True

	def PinPoint(self):
		return self.pinpoint

	def MisRouted(self):
		return self.misrouted

#
# class Train:
# 	tx = 0
#
# 	def __init__(self, name=None):
# 		if name:
# 			self.name = name
# 		else:
# 			self.name = Train.NextName()
# 		self.loco = "??"
# 		self.atc = False
# 		self.ar = False
# 		self.sbActive = False
# 		self.blocks = {}
# 		self.blockOrder = []
# 		self.signal = None
# 		self.throttle = ""
# 		self.east = True
# 		self.aspect = None
# 		self.engineer = None
# 		self.beingEdited = False
# 		self.time = None
# 		self.chosenRoute = None
# 		self.hilite = False
# 		self.misrouted = False
#
# 	def SetTime(self, t):
# 		self.time = t
#
# 	def SetMisrouted(self, flag):
# 		if flag == self.misrouted:
# 			return
#
# 		self.misrouted = flag
# 		self.Draw()
#
# 	def AddTime(self, delta=1):
# 		if self.time is not None:
# 			self.time += delta
# 			return True
# 		return False
#
# 	def GetTime(self):
# 		return self.time
#
# 	def SetBeingEdited(self, flag):
# 		self.beingEdited = flag
#
# 	def IsBeingEdited(self):
# 		return self.beingEdited
#
# 	def dump(self):
# 		print("Train %s: %s %s %s" % (self.name, self.loco, self.blockInfo(), self.signalInfo()))
#
# 	def forSnapshot(self):
# 		return { "name": self.name,
# 			"loco": self.loco,
# 			"east": self.east,
# 			"route": self.chosenRoute,
# 			"blocks": self.blockOrder }
#
# 	def blockInfo(self):
# 		bl = [bl for bl in self.blocks]
# 		return "[" + ", ".join(bl) + "]"
#
# 	def signalInfo(self):
# 		if self.signal is None:
# 			return "None"
#
# 		return "%s: %d" % (self.signal.GetName(), self.aspect)
#
# 	@classmethod
# 	def ResetTX(cls):
# 		Train.tx = 0
#
# 	@classmethod
# 	def NextName(cls):
# 		rv = "??%s" % Train.tx
# 		Train.tx += 1
# 		return rv
#
# 	def GetEast(self):
# 		return self.east
#
# 	def SetEast(self, flag=True):
# 		self.east = flag
#
# 	def tstring(self):
# 		return "%s/%s (%s)" % (self.name, self.loco, str(self.blockOrder))
#
# 	def SetName(self, name):
# 		self.name = name
#
# 	def SetAR(self, flag):
# 		self.ar = flag
#
# 	def IsOnAR(self):
# 		return self.ar
#
# 	def SetATC(self, flag=True):
# 		self.atc = flag
#
# 	def IsOnATC(self):
# 		return self.atc
#
# 	def SetLoco(self, loco):
# 		self.loco = loco
# 		logging.info("changing loco to %s for train %s" % (loco, self.name))
#
# 	def SetEngineer(self, engineer):
# 		if engineer is None:
# 			self.time = None
# 		elif self.engineer is None:
# 			self.time = 0
# 		self.engineer = engineer
#
# 	def GetEngineer(self):
# 		return self.engineer
#
# 	def GetName(self):
# 		return self.name
#
# 	def GetChosenRoute(self):
# 		return self.chosenRoute
#
# 	def SetChosenRoute(self, rt):
# 		self.chosenRoute = rt
#
# 	def GetLoco(self):
# 		return self.loco
#
# 	def SetSignal(self, sig):
# 		self.signal = sig
# 		self.aspect = 0 if sig is None else sig.GetAspect()
#
# 	def GetSignal(self):
# 		return self.signal, self.aspect, None if self.signal is None else self.signal.GetFrozenAspect()
#
# 	def SetThrottle(self, speed, speedtype):
# 		self.throttle = formatThrottle(speed, speedtype)
#
# 	def GetThrottle(self):
# 		return self.throttle
#
# 	def GetBlockNameList(self):
# 		bnl = []
# 		for bn in self.blockOrder:
# 			blk = self.blocks[bn]
# 			if blk.IsOS():
# 				bnl.append(blk.GetRouteDesignator())
# 			else:
# 				bnl.append(bn)
#
# 		return bnl
#
# 	def ValidateStoppingSections(self):
# 		if len(self.blockOrder) < 1:
# 			return
#
# 		rbn = list(reversed(self.blockOrder))
#
# 		startbn = rbn[0]
# 		blk = self.blocks[startbn]
# 		#  blk.ClearStoppingSections()
# 		blk.EvaluateStoppingSections()
# 		self.SetSBActive(blk.IsStopped())
#
# 		if len(rbn) == 1:
# 			return
#
# 		for bn in rbn[1:]:
# 			blk = self.blocks[bn]
# 			blk.ClearStoppingSections()
#
# 	def GetSetTrainCommand(self):
# 		stParams = {"blocks": self.blockOrder, "name": self.name, "loco": self.loco, "atc": self.atc, "east": self.east}
# 		if self.chosenRoute is not None:
# 			stParams["route"] = self.chosenRoute
# 		return {"settrain": stParams}
#
# 	def GetDesignatorMap(self):
# 		dmap = {}
# 		for bn in self.blockOrder:
# 			blk = self.blocks[bn]
# 			if blk.IsOS():
# 				dmap[blk.GetRouteDesignator()] = bn
# 		return dmap
#
# 	def GetBlockList(self):
# 		return self.blocks
#
# 	def ReverseBlockOrder(self):
# 		self.blockOrder = list(reversed(self.blockOrder))
#
# 	def GetBlockOrderList(self):
# 		return self.blockOrder
#
# 	def GetBlockOrder(self):
# 		return { "name": self.name,
# 			"east": self.east,
# 			"blocks": self.blockOrder }
#
# 	def SetBlockOrder(self, order):
# 		self.blockOrder = [b for b in order if b in self.blocks]
#
# 	def GetBlockCount(self):
# 		return len(self.blocks)
#
# 	def GetNameAndLoco(self):
# 		return self.name, self.loco
#
# 	def SetSBActive(self, flag):
# 		self.sbActive = flag
#
# 	def GetSBActive(self):
# 		return self.sbActive
#
# 	def SetHilite(self, flag=True):
# 		if self.hilite == flag:
# 			return False
# 		self.hilite = flag
# 		self.Draw()
# 		return True
#
# 	def Draw(self):
# 		for blk in self.blocks.values():
# 			blk.DrawTrain(hilite=self.hilite)
#
# 	def SetBlocksDirection(self):
# 		lastBlock = self.blockOrder[-1]
# 		effectiveDirection = self.east
# 		for bn in reversed(self.blockOrder): # move from the front of the train to the rear
# 			blk = self.blocks[bn]
# 			blk.SetEast(effectiveDirection)
# 			blk.Draw()
#
# 	def AddToBlock(self, blk, action):
# 		bn = blk.GetName()
# 		if bn in self.blocks:
# 			return
#
# 		self.blocks[bn] = blk
# 		blk.SetTrain(self)
# 		if action == REAR:
# 			self.blockOrder.insert(0, bn)
# 		else:
# 			self.blockOrder.append(bn)
#
# 		logging.debug("Added block %s to %s of train %s, new block list = %s" % (bn, "rear" if action == REAR else "front", self.name, str(self.blockOrder)))
#
# 	def RemoveFromBlock(self, blk):
# 		bn = blk.GetName()
# 		if bn not in self.blocks:
# 			return False
#
# 		blk.SetTrain(None)
# 		del self.blocks[bn]
# 		try:
# 			self.blockOrder.remove(bn)
# 		except ValueError:
# 			pass
# 		logging.debug("Removed block %s from train %s, new block list = %s" % (bn, self.name, str(self.blockOrder)))
# 		return True
#
# 	def IsContiguous(self):
# 		bnames = list(self.blocks.keys())
# 		print("blocks: %s" % str(bnames))
# 		countBlocks = len(bnames)
# 		if countBlocks <= 1:
# 			# only occupying 1 block - contiguous by default
# 			logging.info("is contiguous returning true because countblocks = %d" % countBlocks)
# 			return True
#
# 		count1 = 0
# 		count2 = 0
# 		# for each block the train is in, count how many blocks adjacent to that block contain the same train
# 		adjStr = ""
# 		blkAdj = ""
# 		for blk in self.blocks.values():
# 			adje, adjw = blk.GetAdjacentBlocks()
# 			adjc = 0
# 			blkAdj += "%s: %s,%s  " % (blk.GetName(), "None" if adje is None else adje.GetName(), "None" if adjw is None else adjw.GetName())
# 			for adj in adje, adjw:
# 				if adj is None:
# 					continue
# 				if adj.GetName() in bnames:
# 					adjc += 1
# 			adjStr += "%s: %s, " % (blk.GetName(), adjc)
# 			print(adjStr)
#
# 			# the count is either 1 (for the blocks at the beginning and the end of the train)
# 			# or two for all of the blocks in between
# 			if adjc == 1:
# 				count1 += 1
# 			elif adjc == 2:
# 				count2 += 1
# 			else:
# 				logging.error("block %s in train %s adjacent count = %d" % (blk.GetName(), self.GetName(), adjc))
#
# 		# so when we reach here, there MUST be 2 blocks whose adjacent count is 1 - the first and last blocks
# 		# there must also be countBlocks-2 blocks whose count is 2 - this is all the blocks mid train
# 		print("after block loop, counts = %d, %d" % (count1, count2))
# 		if count1 != 2 or count2 != countBlocks-2:
# 			logging.info("=============================================")
# 			logging.info("train %s is non contiguous, blocks=%s c1=%d c2=%d countblocks=%d" % (self.GetName(), str(bnames), count1, count2, countBlocks))
# 			logging.info(adjStr)
# 			logging.info(blkAdj)
# 			logging.info("=============================================")
# 			return False
#
# 		return True
#
# 	def FrontInBlock(self, bn):
# 		if len(self.blockOrder) == 0:
# 			return False
# 		return bn == self.blockOrder[-1]
#
# 	def FrontBlock(self):
# 		if len(self.blockOrder) == 0:
# 			return None
# 		bn = self.blockOrder[-1]
# 		return self.blocks[bn]
#
# 	def IsInBlock(self, blk):
# 		bn = blk.GetName()
# 		return bn in self.blocks
#
# 	def IsInNoBlocks(self):
# 		l = len(self.blocks)
# 		if l == 0:
# 			return True
#
# 		if l != 1:
# 			return False
#
# 		bn = list(self.blocks.keys())[0]
# 		return bn in [ "KOSN10S11", "KOSN20S21" ]
#
#
