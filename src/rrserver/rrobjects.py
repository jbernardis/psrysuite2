import logging
import traceback

from rrserver.constants import INPUT_BLOCK, INPUT_BREAKER, INPUT_SIGNALLEVER, INPUT_ROUTEIN, INPUT_HANDSWITCH, INPUT_TURNOUTPOS
from dispatcher.constants import RegAspects, aspectname, aspecttype


def formatRouteDesignator(rtName):
	return "" if rtName is None else "{%s}" % rtName[3:]


SBEAST = 0
SBWEST = 1


class Block:
	def __init__(self, name, district, node, address, east):
		self.name = name
		self.district = district
		self.node = node
		self.address = address
		self.east = east
		self.normalEast = east
		self.osblk = None
		self.bits = []
		self.cleared = False
		self.status = "E"    # E = Empty, C = Cl;eared, O = Occupied, U = Occupied by unknown train
		self.indicators = []
		self.mainBlock = None
		self.mainBlockName = None
		self.subBlocks = []
		self.stoppingBlocks = [None, None]
		self.stoppedBlock = None
		self.route = None
		self.nextBlockEast = None
		self.nextBlockWest = None
		self.handswitches = []
		self.train = None

	def DumpSubs(self):
		if self.mainBlock is None:
			logging.debug("Main block %s Status %s train %s" % (self.Name(), self.status, "NONE" if self.train is None else self.train.Name()))
			for sb in self.subBlocks:
				logging.debug("  sub block %s Status %s train %s" % (sb.Name(), sb.GetStatus(),
																	"NONE" if sb.train is None else sb.train.Name()))

	def GetAllBlocks(self):
		if self.stoppedBlock is not None:
			return self.stoppedBlock.GetAllBlocks()

		blocks = [self] + [sb for sb in self.stoppingBlocks if sb is not None]
		logging.debug("Returning block list: %s" % str([b.Name() for b in blocks]))
		logging.debug("length stoppingBlocks = %d" % len(self.stoppingBlocks))
		return blocks

	def toJson(self):
		return {"name": self.name, "east": 1 if self.east else 0, "cleared": 1 if self.cleared else 0, "statue": self.status}

	def ForBitMap(self):
		indicators = [[ind[3], ind[2]] for ind in self.indicators]
		return {
			self.name: {
				"occupancy": [self.bits, self.address],
				"indicators": indicators
			}
		}

	def SetOS(self, osblk):
		self.osblk = osblk

	def OS(self):
		return self.osblk

	def Name(self):
		return self.name

	def RouteDesignator(self):
		return self.name

	def Address(self):
		return self.address
	
	def District(self):
		return self.district
	
	def InputType(self):
		return INPUT_BLOCK

	def IsOS(self):
		return self.osblk is not None

	def IsNullBlock(self):
		return self.district is None
	
	def SetBlockAddress(self, district, node, address):
		self.district = district
		self.node = node
		self.address = address
	
	def SetMainBlock(self, blk):
		self.mainBlockName = blk.Name()
		self.mainBlock = blk

	def GetMainBlock(self):
		return self if self.mainBlock is None else self.mainBlock
		
	def AddSubBlocks(self, blkl):
		self.subBlocks.extend(blkl)
		for b in blkl:
			b.SetMainBlock(self)

	def IsSubBlock(self):
		return self.mainBlock is not None

	def IsMasterBlock(self):
		return len(self.subBlocks) > 0

	def MainBlockName(self):
		if self.stoppedBlock is not None:
			return self.stoppedBlock.Name()

		if self.mainBlock is not None:
			return self.mainBlock.Name()

		return self.Name()

	def MainHasTrain(self):
		if self.mainBlock is None:
			return False

		return self.mainBlock.Train() is not None

	def MainBlockTrain(self):
		if self.mainBlock is None:
			return None
		return self.mainBlock.Train()

	def MainBlockStatus(self):
		if self.mainBlock is None:
			return "E"

		return self.mainBlock.GetStatus()

	def NextBlock(self, reverse=False):
		east = self.east and not reversed
		if self.osblk is not None:
			return self.osblk.NextBlock(reverse=reverse)

		if self.mainBlock is not None:
			return self.mainBlock.NextBlock(reverse=reverse)

		if self.stoppedBlock is not None:  # this is a stopping block
			return self.stoppedBlock.NextBlock(reverse=reverse)

		if self.east:
			return self.nextBlockWest if reverse else self.nextBlockEast
		else:
			return self.nextBlockEast if reverse else self.nextBlockWest

	def SetTrain(self, tr):
		self.train = tr
		if self.mainBlock is not None:
			self.mainBlock.SetTrain(tr)

	def RemoveFromTrain(self):
		if self.train is None:
			return None

		tr = self.train
		self.train = None
		if self.mainBlock is None:
			tr.RemoveBlock(self)
		else:
			self.mainBlock.CheckForTrainRemoval(tr)
		return tr

	def CheckForTrainRemoval(self, tr):
		ct = 0
		for sb in self.subBlocks:
			if sb.Train() is not None:
				ct += 1

		if ct == 0:
			tr.RemoveBlock(self)
			self.train = None

	def Train(self):
		return self.train

	def AddHandSwitch(self, hs):
		self.handswitches.append(hs)

	def AreHandSwitchesUnlocked(self):
		for hs in self.handswitches:
			if hs.IsUnlocked():
				return True

		return False
		
	def SubBlocks(self):
		return self.subBlocks

	def GetSubBlockNames(self):
		if len(self.subBlocks) == 0:
			return None

		return {self.Name(): [b.Name() for b in self.subBlocks]}
		
	def AddStoppingBlocks(self, sbl):
		for sb in sbl:
			if sb.Name().endswith(".E"):
				self.stoppingBlocks[SBEAST] = sb
				sb.SetStoppedBlock(self)
			elif sb.Name().endswith(".W"):
				self.stoppingBlocks[SBWEST] = sb
				sb.SetStoppedBlock(self)
			
	def StoppingBlocks(self):
		return self.stoppingBlocks
		
	def SetStoppedBlock(self, blk):
		self.stoppedBlock = blk

	def IsCompletelyEmpty(self):
		if self.stoppedBlock is not None:
			return self.stoppedBlock.IsCompletelyEmpty()

		if self.mainBlock is not None:
			return self.mainBlock.IsCompletelyEmpty()

		for sb in self.stoppingBlocks:
			if sb is not None:
				if sb.IsOccupied():
					return False

		for sb in self.subBlocks:
			if sb.IsOccupied():
				return False

		return not self.IsOccupied()
		
	def SetBits(self, bits):
		self.bits = bits
		
	def Bits(self):
		return self.bits
	
	def SetDirection(self, east):
		if self.east == east:
			return False

		self.east = east
		return True
		
	def IsEast(self):
		return self.east

	def East(self):
		return self.east

	def SetEast(self, flag):
		self.east = flag

	def IsReversed(self):
		return self.east != self.normalEast

	def Reset(self):
		self.east = self.normalEast
	
	def SetStatus(self, stat):
		if self.status == stat:
			return False

		self.status = stat

		if self.mainBlock is not None:
			self.mainBlock.DeriveOccupancyFromSubs()

		return True

	def GetStatus(self):
		return self.status

	def SetRoute(self, rtName, blks, sigs):
		bnames = ["NONE" if bn is None else bn.Name() for bn in blks]
		snames = ["NONE" if sn is None else sn.Name() for sn in sigs]
		self.route = rtName

	def DeriveOccupancyFromSubs(self):
		if len(self.subBlocks) > 0:
			# this is the main block - get occupied status from subblocks
			occ = []
			for b in self.subBlocks:
				occ.append(b.GetStatus())

			if "O" in occ and "U" not in occ:
				ov = "O"
			elif "U" in occ and "O" not in occ:
				ov = "U"
			elif "O" in occ and "U" in occ:
				logging.debug("subblocks in block %s have inconsistent statuses" % self.name)
				ov = "U"
			elif "C" in occ:
				ov = "C"
			else:
				ov = "E"

			rc = ov != self.status
			self.status = ov
			return rc
		return False

	def IsOccupied(self):
		return self.status in ["O", "U"]
		
	def SetCleared(self, flag):
		if self.status == "C":
			return False

		self.status = "C"
		return True
		
	def IsCleared(self):
		if self.mainBlock is not None:
			return self.mainBlock.IsCleared()
		'''
		for a block that is subdivided into subblocks, cleared reflects the status of all subblocks or'ed together
		'''
		clr = self.status == "C"
		for b in self.subBlocks:
			clr = True if b.status == "C" else clr
			
		return clr

	def IsBusy(self):
		return self.IsOccupied() or self.IsCleared()

	def SetNextWest(self, blk):
		self.nextBlockWest = blk

	def GetNextWest(self):
		return self.nextBlockWest

	def NextDetectionSectionWest(self):
		if self.osblk is not None:
			return self.osblk.NextDetectionSectionWest()

		if self.mainBlock is not None:
			return self.mainBlock.NextDetectionSectionWest()

		if self.stoppedBlock is None:  # this is a main block
			if self.stoppingBlocks[SBWEST] is not None:
				return self.stoppingBlocks[SBWEST]
			else:
				return self.GetNextWest()
		elif self.name.endswith(".E"):  # this is an east end stopping section
			return self.stoppedBlock
		elif self.name.endswith(".W"):  # this is the west side stopping block
			return self.stoppedBlock.GetNextWest()

		# this should never happen, but just return the next physical block
		return self.GetNextWest()

	def SetNextEast(self, blk):
		self.nextBlockEast = blk

	def NextDetectionSectionEast(self):
		if self.osblk is not None:
			return self.osblk.NextDetectionSectionEast()

		if self.mainBlock is not None:
			return self.mainBlock.NextDetectionSectionEast()

		if self.stoppedBlock is None:  # this is a main block
			if self.stoppingBlocks[SBEAST] is not None:
				return self.stoppingBlocks[SBEAST]
			else:
				return self.GetNextEast()
		elif self.name.endswith(".W"):  # this is a west end stopping section
			return self.stoppedBlock
		elif self.name.endswith(".E"):  # this is the east side stopping block
			return self.stoppedBlock.GetNextEast()

		# this should never happen, but just return the next physical block
		return self.GetNextEast()

	def GetNextEast(self):
		return self.nextBlockEast

	def AddIndicator(self, district, node, address, bits):
		self.indicators.append((district, node, address, bits))
		
	def UpdateIndicators(self):
		'''
		make indicators show the status of this and any stoppingBlocks all or'ed together
		'''
		parentBlk = self
		if self.stoppedBlock is not None:
			parentBlk = self.stoppedBlock
		elif self.mainBlock is not None:
			parentBlk = self.mainBlock

		occ = parentBlk.IsOccupied() # the occupancy status of the block and all sublocks

		for sb in parentBlk.StoppingBlocks():
			if sb is not None:
				occ = True if sb.IsOccupied() else occ

		for ind in parentBlk.indicators:
			district, node, address, bits = ind
			if len(bits) > 0:
				node.SetOutputBit(bits[0][0], bits[0][1], occ)

	def GetEventMessages(self):
		return [self.GetEventMessage()]

	def GetEventMessage(self):
		if self.mainBlock is not None:
			bname = self.mainBlockName
			stat = self.mainBlock.GetStatus()
		else:
			bname = self.name
			stat = self.status

		return {"block": [{ "name": bname, "state": stat, "east": self.east}]}


class OSBlock:
	def __init__(self, name, blk):
		self.name = name
		self.block = blk
		self.routes = {}
		self.activeRoute = None
		self.activeRouteName = None
		self.turnouts = set()

	def Name(self):
		return self.name

	def Block(self):
		return self.block

	def Train(self):
		return self.block.Train()

	def SetTrain(self, tr):
		self.block.SetTrain(tr)

	def RouteDesignator(self):
		return formatRouteDesignator(self.activeRouteName)

	def Routes(self):
		return self.routes

	def SetStatus(self, stat):
		self.block.SetStatus(stat)

	def GetStatus(self):
		return self.block.GetStatus()

	def IsOccupied(self):
		return self.block.IsOccupied()

	def IsOS(self):
		return True

	def OS(self):
		return self

	def IsCleared(self):
		return self.block.IsCleared()

	def IsBusy(self):
		return self.IsOccupied() or self.IsCleared()

	def IsReversed(self):
		return self.block.IsReversed()

	def IsEast(self):
		return self.block.IsEast()

	def East(self):
		return self.block.IsEast()

	def SetEast(self, flag):
		self.block.SetEast(flag)

	def Reset(self):
		self.block.Reset()

	def AddRoute(self, rt):
		self.routes[rt.Name()] = rt

	def HasTurnout(self, tn):
		return tn in self.turnouts

	def GetActiveSignals(self):
		if self.activeRoute is None:
			return []
		return self.activeRoute.Signals()

	def LockRoute(self, flag, locker):
		if self.activeRoute is None:
			logging.debug("Trying to lock active route of os %s, but not selected" % self.Name())
			return []
		return self.activeRoute.Lock(flag, locker)

	def DetermineActiveRoute(self, turnouts):
		routeSelected = False
		for rname, rt in self.routes.items():
			routeSelected = True
			for tout, wantedstate in rt.Turnouts():
				trnout = tout.Name()
				currentstate = tout.IsNormal()
				if wantedstate != currentstate:
					routeSelected = False
					break
			if routeSelected:
				return self.SetActiveRoute(rt)

		if not routeSelected:
			return self.SetActiveRoute(None)

		return False

	def NextDetectionSectionWest(self):
		if self.activeRoute is None:
			return None

		blk = self.activeRoute.NextBlockWest()
		# if this block has an east stop section, send that as the next block instead
		sbeast = blk.StoppingBlocks()[SBEAST]
		return blk if sbeast is None else sbeast

	def NextDetectionSectionEast(self):
		if self.activeRoute is None:
			return None

		blk = self.activeRoute.NextBlockEast()
		# if this block has a west stop section, send that as the next block instead
		sbwest = blk.StoppingBlocks()[SBWEST]
		return blk if sbwest is None else sbwest

	def ActiveRoute(self):
		return self.activeRoute

	def ActiveRouteName(self):
		return self.activeRouteName

	def RouteType(self, reverse=False):
		if self.activeRoute is None:
			return None

		return self.activeRoute.RouteType(reverse=reverse)

	def ExitBlock(self, reverse=False):
		if self.activeRoute is None:
			return None

		return self.activeRoute.ExitBlock(reverse=reverse)

	def SetActiveRoute(self, rt):
		if rt is None:
			rc = self.activeRoute is not None
			self.activeRoute = None
			self.activeRouteName = None
			return rc

		rc = not self.activeRouteName == rt.Name()
		self.activeRoute = rt
		self.activeRouteName = rt.Name()
		# each of the two ends of the route need to point back to this OS block
		ar = self.activeRoute
		nxtEast = ar.NextBlockEast()
		if nxtEast is not None:
			nxtEast.SetNextWest(self)

		nxtWest = ar.NextBlockWest()
		if nxtWest is not None:
			nxtWest.SetNextEast(self)

		return rc

	def GetEventMessages(self):
		return [{"setroute": [{"os": self.Name(), "route": self.activeRouteName}]}]


class Route:
	def __init__(self, name, osblk, turnouts, signals, ends, rtype):
		self.name = name
		self.osblk = osblk
		self.turnouts = [[x[0], True if x[1] == "N" else False] for x in turnouts]
		self.toMap = {}
		self.signals = [s for s in signals]
		self.ends = [x for x in ends]
		self.rtype = [x for x in rtype]

	def SetOS(self, osblk):
		self.osblk = osblk

	def Name(self):
		return self.name

	def Turnouts(self):
		return self.turnouts

	def Signals(self):
		return self.signals

	def EndPoints(self):
		return self.ends

	def HasSignal(self, sigPrefix):
		for sig in self.signals:
			if sig.startswith(sigPrefix):
				return sig

		return None

	def Lock(self, flag, locker):
		tlocks = []
		for tout, _ in self.turnouts:
			tout.Lock(flag, locker)
			tlocks.append([tout, flag])

		return tlocks

	def NextBlockEast(self):
		if self.osblk.East():
			return self.ends[1]
		else:
			return self.ends[0]

	def NextBlockWest(self):
		if self.osblk.East():
			return self.ends[0]
		else:
			return self.ends[1]

	def SignalEast(self):
		if self.osblk.East():
			return self.signals[1]
		else:
			return self.signals[0]

	def SignalWest(self):
		if self.osblk.East():
			return self.signals[0]
		else:
			return self.signals[1]

	def ExitSignal(self, reverse=False):
		if self.osblk.IsReversed():
			return self.signals[1] if reverse else self.signals[0]
		else:
			return self.signals[0] if reverse else self.signals[1]

	def EntrySignal(self, reverse=False):
		if self.osblk.IsReversed():
			return self.signals[0] if reverse else self.signals[1]
		else:
			return self.signals[1] if reverse else self.signals[0]

	def ExitBlock(self, reverse=False):
		if self.osblk.IsReversed():
			return self.ends[1] if reverse else self.ends[0]
		else:
			return self.ends[0] if reverse else self.ends[1]

	def EntryBlock(self, reverse=False):
		if self.osblk.IsReversed():
			return self.ends[0] if reverse else self.ends[1]
		else:
			return self.ends[1] if reverse else self.ends[0]

	def RouteType(self, reverse=False):
		if self.osblk.IsEast():
			return self.rtype[1] if reverse else self.rtype[0]
		else:
			return self.rtype[0] if reverse else self.rtype[1]


class StopRelay:
	def __init__(self, name, district, node, address):
		self.name = name
		self.district = district
		self.node = node
		self.address = address
		self.activated = False
		
	def SetBits(self, bits):
		self.bits = bits
		
	def Bits(self):
		return self.bits
		
	def Activate(self, flag):
		self.activated = flag
		
	def IsActivated(self):
		return self.activated
	
	def GetEventMessages(self):
		return [self.GetEventMessage()]
	
	def GetEventMessage(self):
		return {"relay": [{ "name": self.name, "state": 1 if self.activated else 0}]}


class Breaker:
	def __init__(self, name, district, node, address):
		self.name = name
		self.district = district
		self.node = node
		self.address = address
		self.bits = []
		self.status = True  # not tripped
		self.indicators = []
		self.proxy = None   # proxy - this breaker shows its status via a proxy breaker

	def ForBitMap(self):
		indicators = [[ind[3], ind[2]] for ind in self.indicators]
		return {self.name: {"status": [self.bits, self.address], "indicators": indicators}}
		
	def Name(self):
		return self.name
		
	def Address(self):
		return self.address
	
	def InputType(self):
		return INPUT_BREAKER
		
	def IsNullBreaker(self):
		return self.district is None
	
	def SetBreakerAddress(self, district, node, address):
		self.district = district
		self.node = node
		self.address = address
		
	def SetBits(self, bits):
		self.bits = bits
		
	def Bits(self):
		return self.bits

	def SetStatus(self, flag):
		if self.status == flag:
			return False
		
		self.status = flag
		return True
	
	def SetTripped(self, flag):
		return self.SetStatus(not flag)
	
	def SetOK(self, flag):
		return self.SetStatus(flag)

	def SetProxy(self, bname):
		self.proxy = bname
		
	def HasProxy(self):
		return self.proxy is not None
	
	def IsTripped(self):
		return not self.status
		
	def IsOK(self):
		return self.status
	
	def AddIndicator(self, district, node, address, bits):
		self.indicators.append((district, node, address, bits))

	def UpdateIndicators(self):
		if len(self.indicators) == 0:
			return False
		
		for ind in self.indicators:
			district, node, address, bits = ind
			if len(bits) > 0:
				node.SetOutputBit(bits[0][0], bits[0][1], 0 if self.status else 1)
		return True

	def GetEventMessage(self):
		return {"breaker": [{ "name": self.name, "value": 1 if self.status else 0}]}

	def dump(self):
		addr = "None" if self.address is None else ("%x" % self.address)
		logging.info("%s: district: %s  addr: %s, bits: %s" % (self.name, "None" if self.district is None else self.district.name, addr, str(self.bits)))
		logging.info("	 status: %s " % (str(self.status)))
		logging.info("	 # indicators:	%d" % len(self.indicators))
		if self.district is None:
			logging.info("<===== NULL BREAKER DEFINITION")


class Indicator:
	def __init__(self, name, district, node, address):
		self.name = name
		self.district = district
		self.node = node
		self.address = address
		self.status = False

	def SetBits(self, bits):
		self.bits = bits
		
	def Bits(self):
		return self.bits
		
	def SetOn(self, flag):
		self.status = flag
		
	def IsOn(self):
		return self.status
	
	def GetEventMessage(self):
		return {"indicator": [{ "name": self.name, "state": 1 if self.status else 0}]}


class ODevice:
	def __init__(self, name, district, node, address):
		self.name = name
		self.district = district
		self.node = node
		self.address = address
		self.status = False
		self.bits = None
		
	def SetBits(self, bits):
		self.bits = bits
		
	def Bits(self):
		return self.bits
		
	def SetOn(self, flag):
		if self.status == flag:
			return False
	
		self.status = flag
		return True
		
	def IsOn(self):
		return self.status


class Lock:
	def __init__(self, name, district, node, address):
		self.name = name
		self.district = district
		self.node = node
		self.address = address
		self.status = False

	def SetBits(self, bits):
		self.bits = bits
		
	def Bits(self):
		return self.bits
		
	def SetOn(self, flag):
		if self.status == flag:
			return False
		
		self.status = flag
		return True
		
	def IsOn(self):
		return self.status
	

class Signal:
	def __init__(self, name, district, node, address):
		self.name = name
		self.district = district
		self.node = node
		self.address = address
		self.aspect = 0
		self.frozenaspect = None
		self.aspectType = RegAspects
		self.bits = []
		self.led = []
		self.locked = False
		self.lockBits = []
		self.indicators = []
		self.east = True
		self.callon = False
		self.fleeted = False

	def IsNullSignal(self):
		return self.district is None
	
	def SetSignalAddress(self, district, node, address):
		self.district = district
		self.node = node
		self.address = address
		
	def SetBits(self, bits):
		self.bits = bits
		
	def Bits(self):
		return self.bits
	
	def SetAspect(self, aspect, callon=False):
		if self.aspect == aspect:
			return False
		
		self.aspect = aspect
		if aspect == 0:
			self.callon = False
		else:
			self.callon = callon

		lb = len(self.bits)
		if lb == 0:
			self.district.SetAspect(self, aspect)
		else:
			if lb == 1:
				vals = [1 if aspect != 0 else 0]
			elif lb == 2:
				vals = [aspect & 0x02, aspect & 0x01]
			elif lb == 3:
				vals = [aspect & 0x04, aspect & 0x02, aspect & 0x01]
			else:
				logging.warning("Unknown bits length for signal %s: %d" % (self.Name(), len(self.bits)))
				return False

			for (vbyte, vbit), val in zip(self.bits, vals):
				self.node.SetOutputBit(vbyte, vbit, 1 if val != 0 else 0)

		self.UpdateIndicators()  # make sure all indicators reflect this change
		return True

	def IsCallon(self):
		return self.callon
	
	def SetAspectType(self, atype):
		self.aspectType = atype
		
	def SetFrozenAspect(self, fa):
		self.frozenaspect = fa
		
	def GetAspectType(self):
		return self.AspectType()

	def AspectType(self):
		return self.aspectType

	def AspectName(self):
		return "%s (%s)" % (aspectname(self.aspect, self.aspectType), aspecttype(self.aspectType))

		
	def Aspect(self):
		return self.aspect
	
	def Name(self):
		return self.name

	def East(self):
		return self.east

	def SetEast(self, flag):
		self.east = flag

	def SetFleet(self, flag):
		self.fleeted = flag

	def Fleeted(self):
		return self.fleeted

	def District(self):
		return self.district

	def SetLockBits(self, bits):
		self.lockBits = bits
		
	def LockBits(self):
		return self.lockBits

	def Lock(self, locked):
		if self.locked == locked:
			return False
		
		self.locked = locked
		return True
		
	def IsLocked(self):
		return self.locked
	
	def AddIndicator(self, district, node, address, bits):
		self.indicators.append((district, node, address, bits))
		
	def UpdateIndicators(self):
		for ind in self.indicators:
			district, node, address, bits = ind
			if len(bits) > 0:
				node.SetOutputBit(bits[0][0], bits[0][1], 1 if self.aspect != 0 else 0)
				
	def GetEventMessages(self):
		return [self.GetEventMessage()]
	
	def GetEventMessage(self):
		msg = {"showaspect": [{ "signal": self.name, "aspect": self.aspect, "aspecttype": self.aspectType, "frozenaspect": self.frozenaspect}]}

		return msg
		
	def dump(self):
		addr = "None" if self.address is None else ("%x" % self.address)
		logging.info("%s: district: %s  addr: %s, bits: %s" % (self.name, "None" if self.district is None else self.district.name, addr, str(self.bits)))
		logging.info("	 LED: %s   locked: %s/%s" % (str(self.led), str(self.locked), str(self.lockBits)))
		if self.district is None:
			logging.info("<===== NULL SIGNAL DEFINITION")


class SignalLever:
	def __init__(self, name, district, node, address):
		self.name = name
		self.district = district
		self.node = node
		self.address = address
		self.led = None
		self.state = "N"
		self.callon = False
		self.bits = []

	def ForBitMap(self):
		if self.led is None:
			return {self.name: {"position": [self.bits, self.address]}}
		else:
			bits, _, _, addr = self.led
			return {self.name: {"position": [self.bits, self.address], "led": [bits, addr]}}

	def IsNullLever(self):
		return self.district is None
	
	def SetLeverAddress(self, district, node, address):
		self.district = district
		self.node = node
		self.address = address

	def Name(self):
		return self.name
		
	def Address(self):
		return self.address

	def District(self):
		return self.district
	
	def InputType(self):
		return INPUT_SIGNALLEVER

	def SetBits(self, bits):
		self.bits = bits
		
	def Node(self):
		return self.node
		
	def Bits(self):
		return self.bits

	def SetLed(self, bits, district, node, addr):
		self.led = [bits, district, node, addr]
		self.UpdateLed(0, 0)
		
	def LedBits(self):
		return self.led
	
	def SetLever(self, bits):
		self.bits = bits
		
	def LeverBits(self):
		return self.bits
	
	def SetLeverState(self, rbit, cbit, lbit):
		lastRBit = 1 if self.state == 'R' else 0
		lastLBit = 1 if self.state == 'L' else 0
		lastCBit = 1 if self.callon else 0

		nCallOn = cbit == 1

		self.callon = cbit == 1
		nstate = self.state
		if lbit is not None and lbit != 0:
			nstate = "L"
		elif rbit is not None and rbit != 0:
			nstate = "R"
		elif (lbit is None or lbit == 0) and (rbit is None or rbit == 0):
			nstate = "N"

		if nstate != self.state:
			self.state = nstate
			return True
		
		return False
	
	def UpdateLed(self, raspect, laspect):
		if self.led is not None:
			bits, district, node, addr = self.led
			bt = bits[0]
			if bt:
				node.SetOutputBit(bt[0], bt[1], 1 if raspect != 0 else 0)
			bt = bits[1]
			if bt:
				node.SetOutputBit(bt[0], bt[1], 1 if raspect+laspect == 0 else 0)
			bt = bits[2]
			if bt:
				node.SetOutputBit(bt[0], bt[1], 1 if laspect != 0 else 0)
				
	def GetState(self):
		return self.state
				
	def GetEventMessages(self):
		return [self.GetEventMessage()]

	def GetEventMessage(self):
		return {"siglever": [{ "name": self.name+".lvr", "state": self.state, "callon": 1 if self.callon else 0}]}


class RouteIn:
	def __init__(self, name, district, node, address):
		self.name = name
		self.district = district
		self.node = node
		self.address = address
		self.state = False

	def ForBitMap(self):
		return {self.name: {"status": [self.bits, self.address]}}

	def Name(self):
		return self.name
		
	def Address(self):
		return self.address
	
	def InputType(self):
		return INPUT_ROUTEIN
	
	def SetBits(self, bits):
		self.bits = bits
		
	def Bits(self):
		return self.bits

	def SetState(self, state):
		self.state = state
		
	def GetState(self):
		return self.state
	
	def GetEventMessage(self):
		return None


class Turnout:
	def __init__(self, name, district, node, address):
		self.name = name
		self.district = district
		self.node = node
		self.address = address
		self.normal = True
		self.lastReadNormal = None
		self.bits = []
		self.led = None
		self.lever = None
		self.position = None
		self.leverState = 'N'
		self.disabled = False
		self.locked = False
		self.lockBits = None
		self.force = False
		self.lockers = []
		self.lockBitValue = 0
		self.pairedTurnout = None

	def Name(self):
		return self.name
		
	def Address(self):
		return self.address
	
	def InputType(self):
		return INPUT_TURNOUTPOS

	def SetPairedTurnout(self, pname):
		self.pairedTurnout = pname

	def PairedName(self):
		return self.pairedTurnout
		
	def dump(self):
		addr = "None" if self.address is None else ("%x" % self.address)
		logging.info("%s: district: %s  addr: %s, bits: %s" % (self.name, "None" if self.district is None else self.district.name, addr, str(self.bits)))
		logging.info("	 normal: %s   locked: %s/%s" % (str(self.normal), self.locked, str(self.lockBits)))
		logging.info("	 led:	%s" % str(self.led))
		logging.info("	 lever:  %s/%s" % (self.leverState, str(self.lever)))
		logging.info("	 pos:	%s" % self.position)
		if self.district is None:
			logging.info("<===== NULL TURNOUT DEFINITION")

	def ForBitMap(self):
		if self.position is None:
			position = None
		else:
			position = [self.position[0], self.position[3]]
		if self.lockBits is None:
			lockbits = None
		else:
			lockbits = [self.lockBits[0], self.lockBits[3]]
		if self.lever is None:
			lever = None
		else:
			lever = [self.lever[0], self.lever[3]]
		if self.led is None:
			led = None
		else:
			led = [self.led[0], self.led[3]]
		return {self.name:
					{
						"control": [self.bits, self.address],
						"position": position,
						"lock": lockbits,
						"lever": lever,
						"led": led
					}
				}

	def IsNullTurnout(self):
		return self.district is None
	
	def SetTurnoutAddress(self, district, node, address):
		self.district = district
		self.node = node
		self.address = address
		
	def SetBits(self, bits):
		self.bits = bits
		
	def Bits(self):
		return self.bits
	
	def SetNormal(self, normal):
		if self.normal == normal:
			return False
		
		self.normal = normal
		return True
		
	def IsNormal(self):
		return self.normal
	
	def SetLed(self, bits, district, node, addr):
		self.led = [bits, district, node, addr]
		self.UpdateLed()
		
	def LedBits(self):
		return self.led
	
	def UpdateLed(self):
		if self.led is not None:
			bits, district, node, addr = self.led
			bt = bits[0]
			if bt:
				node.SetOutputBit(bt[0], bt[1], 1 if self.normal else 0)
			bt = bits[1]
			if bt:
				node.SetOutputBit(bt[0], bt[1], 0 if self.normal else 1)

	def SetLever(self, bits, district, node, addr):
		self.lever = [bits, district, node, addr]
		
	def LeverBits(self):
		return self.lever
	
	def HasLever(self):
		return self.lever is not None
	
	def SetLeverState(self, state):
		if state != self.leverState:
			self.leverState = state
			return True
		
		return False
	
	def SetPosition(self, bits, district, node, addr):
		self.position = [bits, district, node, addr]
		if len(bits) == 2:
			node.SetInputBit(bits[0][0], bits[0][1], 1)
		
	def Position(self):
		return self.position
	
	def SetLockBits(self, bits, district, node, addr):
		self.lockBits = [bits, district, node, addr]
		
	def UpdateLockBits(self, release=False):
		if self.lockBits is None:
			return
		bits, district, node, addr = self.lockBits
		
		newLockBit = 0 if release else 1 if self.locked else 0
		if newLockBit != self.lockBitValue:
			node.SetOutputBit(bits[0][0], bits[0][1], newLockBit)
			self.lockBitValue = newLockBit

	def LockBits(self):
		return self.lockBits

	def ClearLock(self):
		self.locked = False
		self.lockers = []
	
	def Lock(self, lockFlag, locker):
		action = "Locking" if lockFlag else "Unlocking"
		# Return value indicates whether or not the locked value changes
		if lockFlag:
			if locker not in self.lockers:
				self.lockers.append(locker)
				if self.locked:
					return False
				self.locked = True
				return True
			else:
				return False
		else:
			if locker not in self.lockers:
				return False

			self.lockers.remove(locker)
			if len(self.lockers) == 0:
				self.locked = False
				return True
			else:
				return False

	def Lockers(self):
		return self.lockers

	def IsLocked(self):
		return self.locked

	def IsDisabled(self):
		return self.disabled

	def GetEventMessages(self, force=False):
		self.force = force
		msg = {"turnout": [{ "name": self.name, "state": "N" if self.normal else "R", "force": self.force, "locked": self.locked}]}
		if self.pairedTurnout is not None:
			msgp = {"turnout": [{ "name": self.pairedTurnout, "state": "N" if self.normal else "R", "force": self.force, "locked": self.locked}]}
			msgs = [msg, msgp]
		else:
			msgs = [msg]

		return msgs


class OutNXButton:
	def __init__(self, name, district, node, address):
		self.name = name
		self.district = district
		self.node = node
		self.address = address
		self.bits = []
		
	def Name(self):
		return self.name
		
	def SetBits(self, bits):
		self.bits = bits
		
	def Bits(self):
		return self.bits


class Handswitch:
	def __init__(self, name, district, node, address, blocknm):
		self.name = name
		self.district = district
		self.node = node
		self.address = address
		self.normal = True
		self.bits = []
		self.indicators = []
		self.unlocked = False
		self.reverseIndicators = []
		self.unlock = None
		self.blocknm = blocknm
		self.block = None

	def Name(self):
		return self.name
		
	def Address(self):
		return self.address
	
	def District(self):
		return self.district
	
	def InputType(self):
		return INPUT_HANDSWITCH
		
	def dump(self):
		addr = "None" if self.address is None else ("%x" % self.address)
		logging.info("%s: district: %s  addr: %s" % (self.name, "None" if self.district is None else self.district.name, addr))
		logging.info("	 normal: %s   locked: %s" % (str(self.normal), self.locked))
		logging.info("	 ind:	%s" % str(self.indBits))
		logging.info("	 pos:	%s" % self.bits)

		if self.district is None:
			logging.info("<===== NULL HANDSWITCH DEFINITION")

	def IsNullHandswitch(self):
		return self.district is None
	
	def SetHandswitchAddress(self, district, node, address, blocknm):
		self.district = district
		self.node = node
		self.address = address
		self.blocknm = blocknm

	def ResolveBlock(self, blocks):
		self.block = blocks.get(self.blocknm, None)

	def Block(self):
		return self.block

	def BlockName(self):
		return self.blocknm

	def SetNormal(self, normal):
		if self.normal == normal:
			return False
		
		self.normal = normal
		self.UpdateReverseIndicators()
		return True
		
	def IsNormal(self):
		return self.normal
	
	def AddIndicator(self, district, node, addr, bits, inverted):
		self.indicators.append([district, node, addr, bits, inverted])
		self.UpdateIndicators()

	def UpdateIndicators(self):
		if len(self.indicators) == 0:
			return False
		# indicators with one bit: simple on/off led to show lock status
		# indicators with 2 bits: panel indicators with one being the inverted value of the other
		lval = 1 if self.unlocked else 0
		for ind in self.indicators:
			district, node, address, bits, inverted = ind
			if len(bits) == 1:
				node.SetOutputBit(bits[0][0], bits[0][1], 1-lval if inverted else lval)
			elif len(bits) == 2:
				node.SetOutputBit(bits[0][0], bits[0][1], 1-lval if inverted else lval)
				node.SetOutputBit(bits[1][0], bits[1][1], lval if inverted else 1-lval)
			else:
				logging.warning("Hand switch indicator for %s has an unexpected number of bits")
			
		return True

	def AddReverseIndicator(self, district, node, addr, bits):
		#  this indicates if the handswitch turnout is in the reverse position versus normal
		self.reverseIndicators.append([district, node, addr, bits])
		self.UpdateReverseIndicators()

	def UpdateReverseIndicators(self):
		if len(self.reverseIndicators) == 0:
			return False
		rval = 0 if self.normal else 1
		for ind in self.reverseIndicators:
			district, node, address, bits = ind
			if len(bits) == 1:
				node.SetOutputBit(bits[0][0], bits[0][1], rval)
			
		return True

	def AddUnlock(self, district, node, addr, bits):
		self.unlock = [district, node, addr, bits]
		
	def GetUnlock(self):
		return self.unlock

	def SetBits(self, bits):
		self.bits = bits  # the position is where we read the switch position
		self.node.SetInputBit(bits[0][0], bits[0][1], 1)
		
	def Bits(self):
		return self.bits
		
	def Position(self):
		return [self.district, self.node, self.address, self.bits]
	
	def Unlock(self, unlocked):
		if self.unlocked == unlocked:
			return False
		
		self.unlocked = unlocked
		return True
		
	def IsUnlocked(self):
		return self.unlocked

	def ForBitMap(self):
		indicators = [[ind[3], ind[2], ind[4]] for ind in self.indicators]
		rindicators = [[ind[3], ind[2]] for ind in self.reverseIndicators]
		if self.unlock is None:
			unlock = []
		else:
			unlock = [self.unlock[3], self.unlock[2]]

		return {self.name: {
			"position": [self.bits, self.address],
			"indicators": indicators,
			"revindicators": rindicators,
			"unlock": unlock
		}}

	def GetEventMessage(self, lock=False):
		if lock:
			return {"handswitch": [{ "name": self.name+".hand", "state": 1 if self.unlocked else 0}]}
		else:
			return {"turnout": [{ "name": self.name, "state": "N" if self.normal else "R"}]}
 

