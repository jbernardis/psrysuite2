import logging
import re
import os
import json


from rrserver.districts.yard import Yard
from rrserver.districts.latham import Latham
from rrserver.districts.dell import Dell
from rrserver.districts.shore import Shore
from rrserver.districts.krulish import Krulish
from rrserver.districts.nassau import Nassau
from rrserver.districts.bank import Bank
from rrserver.districts.cliveden import Cliveden
from rrserver.districts.cliff import Cliff
from rrserver.districts.hyde import Hyde
from rrserver.districts.port import Port

from rrserver.train import Train

from rrserver.constants import INPUT_BLOCK, INPUT_TURNOUTPOS, INPUT_BREAKER, INPUT_SIGNALLEVER, \
	INPUT_HANDSWITCH, INPUT_ROUTEIN, nodeNames

from rrserver.rrobjects import Block, OSBlock, Route, StopRelay, Signal, SignalLever, RouteIn, Turnout, \
			OutNXButton, Handswitch, Breaker, Indicator, ODevice, Lock

from dispatcher.constants import RegAspects, RegSloAspects, AdvAspects, SloAspects, \
	MAIN, SLOW, DIVERGING, RESTRICTING, \
	CLEARED, OCCUPIED, STOP, OVERSWITCH, \
	restrictedaspect, routetype, statusname, aspectname, aspecttype

EWCrossoverPoints = [
	["COSSHE", "C20"],
	["YOSCJE", "P50"],
	["YOSCJW", "P50"],
	["POSSJ1", "P30"],
	["SOSE",   "P32"],
	["SOSW",   "P32"],
	["YOSKL4", "Y30"],
	["YOSWYW", "Y87"],
]


def CrossingEastWestBoundary(osblk, blk):
	if osblk is None or blk is None:
		return False
	blkNm = blk.Name()
	osNm = osblk.Name()
	return [osNm, blkNm] in EWCrossoverPoints or [blkNm, osNm] in EWCrossoverPoints


class Railroad:
	def __init__(self, parent, cbEvent, settings):
		self.parent = parent
		self.cbEvent = cbEvent
		self.settings = settings
		self.districts = {}
		self.nodes = {}

		self.debug = self.settings.debug

		self.districtList = [
			[ Yard, "Yard" ],
			[ Latham, "Latham" ],
			[ Dell, "Dell" ],
			[ Shore, "Shore" ],
			[ Krulish, "Krulish" ],
			[ Nassau, "Nassau" ],
			[ Bank, "Bank" ],
			[ Cliveden, "Cliveden" ],
			[ Cliff, "Cliff" ],
			[ Hyde, "Hyde" ],
			[ Port, "Port" ],
		]

		self.ignoredBlocks = self.settings.rrserver.ignoredblocks
		
		self.controlOptions = {}
		self.signals = {}
		self.signalLevers = {}
		self.blocks = {}
		self.osblocks = {}
		self.turnouts = {}
		self.turnoutPairs = {}
		self.handswitches = {}
		self.breakers = {}
		self.stopRelays = {}
		self.outNxButtons = {}
		self.routesIn = {}
		self.osRoutes = {}
		self.indicators = {}
		self.odevices = {}
		self.locks = {}
		self.pendingDetectionLoss = PendingDetectionLoss(self)
		self.PendingFleetActions = {}
		self.reSigName = re.compile("([A-Z][0-9]*)([A-Z])")
		self.loRoutes = {}
		self.loBlocks = {}
		self.to2osMap = {}
		self.lastValues = {}

		self.pulsedOutputs = {} 
		self.topulselen = self.settings.rrserver.topulselen
		self.topulsect = self.settings.rrserver.topulsect
		self.nxbpulselen = self.settings.rrserver.nxbpulselen
		self.nxbpulsect = self.settings.rrserver.nxbpulsect

		self.fleetedSignals = {}
		self.districtLock = {"NWSL": [0, 0, 0, 0], "NESL": [0, 0, 0]}
		self.enableSendIO = True
		self.osslocks = True

		self.addrList = []

		# load in the train roster
		fn = os.path.join(os.getcwd(), "data", "trains.json")
		logging.info("Retrieving trains information from file (%s)" % fn)
		try:
			with open(fn, "r") as jfp:
				self.trainRoster = json.load(jfp)
		except FileNotFoundError:
			print("Unable to open train roster file %s" % fn)
			logging.fatal("Unable to open train roster file %s" % fn)
			exit(1)

		print(json.dumps(self.trainRoster, indent=4))
		self.trains = {}

		for dclass, name in self.districtList:
			logging.info("Creating District %s" % name)
			self.districts[name] = dclass(self, name, self.settings)
			self.nodes[name] = self.districts[name].GetNodes()
			self.addrList.extend([[addr, self.districts[name], node] for addr, node, in self.districts[name].GetNodes().items()])

		for hsnm, hs in self.handswitches.items():
			hs.ResolveBlock(self.blocks)
			blk = hs.Block()
			if blk is not None:
				blk.AddHandSwitch(hs)

		fn = os.path.join(os.getcwd(), "data", "layout.json")
		logging.info("Retrieving layout information from file (%s)" % fn)
		try:
			with open(fn, "r") as jfp:
				j = json.load(jfp)
		except FileNotFoundError:
			logging.info("File not found")
			j = None

		if j is None:
			print("Unable to load layout information")
			logging.fatal("Unable to load layout file")
			exit(1)

		self.loRoutes = j["routes"]
		self.loBlocks = j["blocks"]
		self.loSignals = j["signals"]

		# build the subblock table
		self.subBlocks = {}
		for bn, b in self.blocks.items():
			sb = b.GetSubBlockNames()
			if sb is not None:
				self.subBlocks.update(sb)

		fn = os.path.join(os.getcwd(), "data", "subblocks.json")
		logging.info("Saving subblock information to file (%s)" % fn)
		try:
			with open(fn, "w") as jfp:
				json.dump(self.subBlocks, jfp, indent=2)
		except Exception as e:
			logging.info("Error %s saving subblocks file" % str(e))

		self.lvrToOSMap = {}
		self.sigToOSMap = {}
		self.to2osMap = {}
		self.routes = {}
		for rtName, rt in self.loRoutes.items():
			osBlockName = rt["os"]

			tl = rt["turnouts"]
			toList = [[self.turnouts[tn], tv] for tn, tv in rt["turnouts"]]
			sigList = rt["signals"]

			try:
				osBlock = self.osblocks[osBlockName]
			except KeyError:
				osBlock = None
			try:
				blk = self.blocks[osBlockName]
			except KeyError:
				blk = None

			if osBlock is None:
				osBlock = None if blk is None else OSBlock(osBlockName, blk)

				if osBlock is not None:
					self.osblocks[osBlockName] = osBlock

			if osBlock is None or blk is None:
				continue

			blk.SetOS(osBlock)

			for sn in sigList:
				if sn not in self.sigToOSMap:
					self.sigToOSMap[sn] = []
				self.sigToOSMap[sn].append(osBlock)

				z = re.match("([A-Za-z]+[0-9]+[A-Za-z])", sn)
				if z is None or len(z.groups()) < 1:
					continue
				lvr = z.groups()[0]
				if lvr in self.lvrToOSMap:
					if osBlockName not in self.lvrToOSMap[lvr]:
						self.lvrToOSMap[lvr].append(osBlockName)
				else:
					self.lvrToOSMap[lvr] = [osBlockName]

			for tout, _ in toList:
				tn = tout.Name()
				if tn not in self.to2osMap:
					self.to2osMap[tn] = [osBlockName]
				else:
					if osBlockName not in self.to2osMap[tn]:
						self.to2osMap[tn].append(osBlockName)

			endBlocks = [None if x not in self.blocks else self.blocks[x] for x in rt["ends"]]
			r = Route(rtName, osBlock, toList, sigList, endBlocks, rt["type"])
			self.routes[rtName] = r
			osBlock.AddRoute(r)

		for osBlock in self.osblocks.values():
			osBlock.DetermineActiveRoute(self.turnouts)

		for sn, siginfo in self.loSignals.items():
			try:
				s = self.signals[sn]
				at = siginfo.get("aspecttype", None)
				east = siginfo.get("east", True)
				s.SetAspectType(at)
				s.SetEast(east)
				if at is None:
					logging.debug("Signal %s, aspect type set to None" % sn)

			except KeyError:
				logging.debug("Unable to find signal %s" % sn)

		self.sbToSigMap = {}
		self.sigToSbMap = {}
		for bn, blkinfo in self.loBlocks.items():
			try:
				blk = self.blocks[bn]
			except KeyError:
				blk = None

			if blk is not None:
				snWest = blkinfo["sbsigwest"]
				if snWest is None:
					sigWest = None
				else:
					try:
						sigWest = self.signals[snWest]
					except KeyError:
						logging.error("Unable to find signal %s from layout file" % snWest)
						sigWest = None

				snEast = blkinfo["sbsigeast"]
				if snEast is None:
					sigEast = None
				else:
					try:
						sigEast = self.signals[snEast]
					except KeyError:
						logging.error("Unable to find signal %s from layout file" % snEast)
						sigEast = None

				self.sbToSigMap[bn] = [sigWest, sigEast]
				if sigWest is not None:
					self.sigToSbMap[snWest] = [blk, False]
				if sigEast is not None:
					self.sigToSbMap[snEast] = [blk, True]

		blist = {}
		for blk in self.blocks.values():
			blist.update(blk.ForBitMap())

		tlist = {}
		for tout in self.turnouts.values():
			tlist.update(tout.ForBitMap())

		brklist = {}
		for brk in self.breakers.values():
			brklist.update(brk.ForBitMap())

		rilist = {}
		for rt in self.routesIn.values():
			rilist.update(rt.ForBitMap())

		sllist = {}
		for sl in self.signalLevers.values():
			sllist.update(sl.ForBitMap())

		hslist = {}
		for hs in self.handswitches.values():
			hslist.update(hs.ForBitMap())

		ioBits = {
			"blocks": blist,
			"turnouts": tlist,
			"breakers": brklist,
			"routesin": rilist,
			"siglevers": sllist,
			"handswitches": hslist
		}
		fn = os.path.join(os.getcwd(), "data", "iobits.json")
		logging.info("Saving IO Bit information to file (%s)" % fn)
		try:
			with open(fn, "w") as jfp:
				json.dump(ioBits, jfp, indent=2)
		except Exception as e:
			logging.info("Error %s saving io bits file" % str(e))

		# self.AuditRoutes()

	def AuditRoutes(self):
		for osblknm, osblk in self.osblocks.items():
			east = osblk.East()
			logging.debug("==========================================")
			logging.debug("determine initial route for OS %s(%s)" % (osblknm, east))
			ar = osblk.ActiveRoute()
			if ar is None:
				logging.debug("  OS %s - NO active route.  Potential routes:")
				for rt in osblk.Routes():
					logging.debug("    %s" % str(rt))
			else:
				logging.debug("  Active Route: %s" % osblk.ActiveRouteName())
				for ep in ar.EndPoints():
					if ep is None:
						logging.debug("    End point is NONE")
					else:
						epeast = ep.East()
						logging.debug("    End point: %s(%s)" % (ep.Name(), epeast))
						nbe = ep.NextBlock(False)
						nben = "None" if nbe is None else nbe.Name()
						nbw = ep.NextBlock(True)
						nbwn = "None" if nbw is None else nbw.Name()
						logging.debug("      nbe: %s" % nben)
						logging.debug("      nbw: %s" % nbwn)
						if osblknm not in [nben, nbwn]:
							logging.debug("Block %s does not point back to the proper OS %s  <==============================" % (ep.Name(), osblknm))

	def SetDebugFlag(self,	showaspectcalculation = False, blockoccupancy = False, identifytrain = False):
		self.debug.showaspectcalculation = showaspectcalculation
		self.debug.blockoccupancy = blockoccupancy
		self.debug.identifytrain = identifytrain

	def GetNodeStatuses(self):
		retval = []
		for addr, dist, node in self.addrList:
			retval.append([addr, nodeNames[addr], 1 if node.IsEnabled() else 0])
		return retval

	def EnableNode(self, name, addr, enable):
		for a, _, nd in self.addrList:
			if addr == a:
				nd.Enable(enable)
				return
		logging.error("unable to find node %s(0x%2x) to set enabled to %s" % (name, addr, enable))

	def GetBlockInfo(self):
		blks = []
		for blknm, blk in self.blocks.items():
			if blk.District() is not None:
				blks.append([blknm, 1 if blk.IsEast() else 0])
		return sorted(blks)

	def dump(self):
		logging.info("================================SIGNALS")
		for s in self.signals.values():
			s.dump()

		logging.info("================================BLOCKS")
		for b in self.blocks.values():
			b.dump()

		logging.info("==============================TURNOUTS")
		for t in self.turnouts.values():
			t.dump()

		logging.info("==============================BREAKERS")
		for b in self.breakers.values():
			b.dump()
			
	def Initialize(self):	
		for d in self.districts.values():
			d.Initialize()
			
		self.SetControlOption("nassau", self.settings.control.nassau)
		self.SetControlOption("cliff", self.settings.control.cliff)
		self.SetControlOption("yard", self.settings.control.yard)
		self.SetControlOption("c13auto", self.settings.control.c13auto)
		self.SetControlOption("bank.fleet", 0)
		self.SetControlOption("carlton.fleet", 0)
		self.SetControlOption("cliff.fleet", 0)
		self.SetControlOption("cliveden.fleet", 0)
		self.SetControlOption("foss.fleet", 0)
		self.SetControlOption("hyde.fleet", 0)
		self.SetControlOption("hydejct.fleet", 0)
		self.SetControlOption("krulish.fleet", 0)
		self.SetControlOption("latham.fleet", 0)
		self.SetControlOption("nassau.fleet", 0)
		self.SetControlOption("shore.fleet", 0)
		self.SetControlOption("valleyjct.fleet", 0)
		self.SetControlOption("yard.fleet", 0)
		self.SetControlOption("osslocks", 1)

		logging.debug("End of initialize: N20 status = %s" % self.DumpN20())

		return True

	def DelayedStartup(self):
		for d in self.districts.values():
			d.DelayedStartup()

	def DumpN20(self):
		return self.blocks["N20"].GetStatus()
			
	def OccupyBlock(self, blknm, state):
		'''
		this method is solely for simulation - to set a block as occupied or not
		'''
		try:
			blist = [ self.blocks[blknm] ]
		except KeyError:
			try:
				blist = [self.GetBlock(x) for x in self.subBlocks[blknm]]
			except KeyError:
				logging.warning("Ignoring occupy command - unknown block name: %s" % blknm)
				return

		newstate = 1 if state != 0 else 0
		for blk in blist:
			if len(blk.Bits()) > 0:
				vbyte, vbit = blk.Bits()[0]
				blk.node.SetInputBit(vbyte, vbit, newstate)
			else:
				'''
				block has sub blocks - occupy all of them as per state
				'''
				sbl = blk.SubBlocks()
				for sb in sbl:
					if len(sb.Bits()) > 0:
						vbyte, vbit = sb.Bits()[0]
						sb.node.SetInputBit(vbyte, vbit, newstate)
		
	def SetTurnoutPos(self, tonm, normal):
		'''
		this method is for simulation - to set a turnout to normal or reverse position - this is also used for handswitches
		'''
		try:
			tout = self.turnouts[tonm]
		except KeyError:
			try:
				tout = self.handswitches[tonm]

			except KeyError:			
				logging.warning("Ignoring turnoutpos command - unknown turnoutname: %s" % tonm)
				return
	
		pos = tout.Position()
		if pos is None:
			logging.warning("Turnout definition does not have position - ignoring turnoutpos command")
			return 
		
		bits, district, node, addr = pos
		node.SetInputBit(bits[0][0], bits[0][1], 1 if normal else 0)
		node.SetInputBit(bits[1][0], bits[1][1], 0 if normal else 1)
			
	def SetBreaker(self, brkrnm, state):
		'''
		this method is solely for simulation - to set a breaker as on or not
		'''
		try:
			brkr = self.breakers[brkrnm]
		except KeyError:
			logging.warning("Ignoring breaker command - unknown breaker name: %s" % brkrnm)
			return
		
		try:
			vbyte, vbit = brkr.Bits()[0]
		except IndexError:
			logging.warning("Breaker definition incomplete - ignoring breaker command")
			return 

		brkr.node.SetInputBit(vbyte, vbit, 1 if state == 0 else 0)
		
	def SetInputBit(self, distName, vbyte, vbit, val):
		pass

	def SetIndicator(self, indname, state):
		'''
		turn an indicator on/off
		'''
		try:
			ind = self.indicators[indname]
		except KeyError:
			logging.warning("Ignoring indicator command - unknown indicator: %s" % indname)
			return
		
		if state == ind.IsOn():
			return False
	
		ind.SetOn(state)	
		bits = ind.Bits()
		if len(bits) > 0:
			vbyte, vbit = bits[0]
			ind.node.SetOutputBit(vbyte, vbit, 1 if state else 0)
		return True

	def SetODevice(self, odname, state):
		'''
		turn an output device on/off
		'''
		try:
			od = self.odevices[odname]
		except KeyError:
			logging.warning("Ignoring output device command - unknown output device: %s" % odname)
			return
		
		vbyte, vbit = od.Bits()[0]
		od.node.SetOutputBit(vbyte, vbit, 1 if state != 0 else 0)

	def GetRelays(self):
		return {rn: self.stopRelays[rn].IsActivated() for rn in self.stopRelays.keys()}

	def SetRelay(self, relayname, state):
		'''
		turn a stopping relay on/off
		'''
		try:
			r = self.stopRelays[relayname]
		except KeyError:
			logging.warning("Ignoring stoprelay command - unknown relay: %s" % relayname)
			return

		bits = r.Bits()
		if len(bits) > 0:		
			vbyte, vbit = bits[0]
			r.node.SetOutputBit(vbyte, vbit, 1 if state != 0 else 0)
			r.Activate(state != 0)
		
	def GetRouteIn(self, rtnm):
		try:
			return self.routesIn[rtnm]
		except KeyError:
			return None
		
	def GetBreaker(self, brknm):
		try:
			return self.breakers[brknm]
		except KeyError:
			return None
			
	def SetRouteIn(self, rtnm):
		'''
		this method is solely for simulation - to set the current inbound route
		'''
		try:
			rt = self.routesIn[rtnm]
		except KeyError:
			logging.warning("Ignoring route in command - unknown route name: %s" % rtnm)
			return
		
		offRts = rt.district.SelectRouteIn(rt)
		if offRts is None:
			return 

		for rtenm in offRts:
			rte = self.routesIn[rtenm]
			bt = rte.Bits()
			rte.node.SetInputBit(bt[0][0], bt[0][1], 0)
			
		bt = rt.Bits()
		rt.node.SetInputBit(bt[0][0], bt[0][1], 1)
		
	def ClearAllRoutes(self, rtList):
		for rtenm in rtList:
			rte = self.routesIn[rtenm]
			bt = rte.Bits()
			rte.node.SetInputBit(bt[0][0], bt[0][1], 0)

	def SignalClick(self, signm, callon=False):
		logging.debug("======================================in signal %s click, callon = %s" % (signm, callon))
		try:
			sig = self.signals[signm]
		except KeyError:
			logging.error("Unknown signal: %s" % signm)
			return

		district = sig.District()
		if not district.SignalClick(sig, callon):
			return

		currentAspect = 0
		if sig is not None:
			currentAspect = sig.Aspect()

		if sig.District().ControlRestrictedSignal(signm):
			self.Alert(sig.District().ControlRestrictedMessage())
			return

		osName = self.DetermineSignalOS(signm)
		if osName is None:
			return

		msgs = []
		try:
			moving = currentAspect != 0  # Are we requesting a stop signal?
			aspect = self.CalculateAspect(sig, osName, moving, callon, None, silent=False)
			if aspect is None:
				return

			msgs.extend(self.ApplyAspect(aspect, sig, osName, callon))
			msgs.extend(sig.GetEventMessages())

		except Exception as e:
			logging.warning("Exception %s in calc aspect %s" % (str(e), signm))
			return

		for m in msgs:
			self.RailroadEvent(m)

		district.EvaluateDistrictLocks(sig, None)
		self.EvaluatePreviousSignals(sig)

	def DetermineSignalOS(self, signm):
		osList = (self.sigToOSMap[signm])
		logging.debug("oslist = %s" % str(osList))
		for osblk in osList:
			osName = osblk.Name()

			activeRoute = osblk.ActiveRoute()
			if activeRoute is not None and activeRoute.HasSignal(signm):
				return osName
		else:
			self.Alert("No available route for signal %s" % signm)
			return None

	def TurnoutClick(self, toname, status):
		#  TODO: Need to do some checking here to make sure the route is not busy
		tout = self.turnouts.get(toname, None)
		if tout is None:
			return

		if tout.IsLocked() or tout.IsDisabled():
			self.Alert("Turnout %s is locked" % toname)
			return

		self.SetOutPulseTo(toname, status)

	def SetOutPulseTo(self, toname, state):
		try:
			turnout = self.turnouts[toname]
		except KeyError:
			logging.warning("Unknown turnout: %s" % toname)
			return		
			
		Nval = 0 if state == "R" else 1
		Rval = 1 if state == "R" else 0

		bits = turnout.Bits()
		if len(bits) > 0:
			try:
				Nbyte, Nbit = bits[0]
			except IndexError:
				logging.error("index error on turnout %s" % toname)
				return
			
			Rbyte, Rbit = bits[1]
			pbyte = Nbyte if Nval == 1 else Rbyte
			pbit =  Nbit  if Nval == 1 else Rbit
				
			self.pulsedOutputs[toname] = PulseCounter(pbyte, pbit, self.topulsect, self.topulselen, turnout.node)
			
			turnout.node.SetOutputBit(Nbyte, Nbit, Nval)
			turnout.node.SetOutputBit(Rbyte, Rbit, Rval)
		
		if self.settings.rrserver.simulation:
			'''
			if simulation, set the corresponding input bits to show switch position change
			if there is no position information, defer to the district logic
			'''
			pos = turnout.Position()
			if pos is None:
				turnout.SetNormal(state == "N")
				turnout.district.CheckTurnoutPosition(turnout)
			else:
				bits, district, node, addr = pos
				node.SetInputBit(bits[0][0], bits[0][1], Nval)
				node.SetInputBit(bits[1][0], bits[1][1], Rval)
			
	def SetOutPulseNXB(self, bname):
		try:
			btn = self.outNxButtons[bname]
		except KeyError:
			logging.warning("Attempt to change state on unknown button: %s" % bname)
			return

		bits = btn.Bits()
		Bbyte, Bbit = bits[0]
			
		self.pulsedOutputs[bname] = PulseCounter(Bbyte, Bbit, self.nxbpulsect, self.nxbpulselen, btn.node)
		
		btn.node.SetOutputBit(Bbyte, Bbit, 1)
		if self.settings.rrserver.simulation:
			'''
			let the district code determine the course of action to simulate the route
			'''
			btn.district.PressButton(btn)

	def SetLock(self, lname, state):
		try:
			lk = self.locks[lname]
		except KeyError:
			logging.warning("Attempt to change lock state on unknown lock: %s" % lname)
			return False
			
		if lk.SetOn(state):
			bits = lk.Bits()
			lk.node.SetOutputBit(bits[0][0], bits[0][1], 1 if state else 0)
			return True
			
		return False

	def SetTurnoutLock(self, toname, state, locker=None):
		aturnout = True
		try:
			tout = self.turnouts[toname]
		except KeyError:
			aturnout = False
			try:
				tout = self.turnoutPairs[toname]
			except KeyError:
				logging.warning("Attempt to change lock state on unknown turnout: %s" % toname)
				return

		if aturnout:
			release = tout.district.Released(tout)
			if tout.Lock(state == 1, locker):
				tout.UpdateLockBits(release=release)

		msg = tout.GetEventMessage(lock=True, locker=locker)

		if not aturnout:
			msg["turnoutlock"][0]["name"] = toname
			logging.warning(str(msg))

		self.RailroadEvent(msg)

	def SetAspect(self, signm, aspect):
		try:
			sig = self.signals[signm]
		except KeyError:
			logging.error("cannot find signal %s" % signm)
			sig = None

		if sig is None:
			return

		sig.SetAspect(aspect)

	def UpdateSignalLeverLEDs(self, sig, aspect, callon):
		r = self.reSigName.findall(sig.Name())
		if len(r) != 1 or len(r[0]) != 2:
			return 
		
		try:
			sl = self.signalLevers[r[0][0]]
		except KeyError:
			return

		if aspect == 0:
			lbit = 0
			rbit = 0
		elif r[0][1] == "L":
			lbit = 1
			rbit = 0
		elif r[0][1] == "R":
			lbit = 0
			rbit = 1
		else:
			lbit = 0
			rbit = 0
					
		sl.SetLeverState(rbit, 1 if callon else 0, lbit)
		sl.UpdateLed(rbit, lbit)
		
	def SetSignalLock(self, signame, lock):
		try:
			sig = self.signals[signame]
		except KeyError:
			logging.warning("Ignoring set signal lock - unknown signal name: %s" % signame)
			return
		
		b = sig.LockBits()
		if len(b) > 0:
			for vbyte, vbit in b:
				sig.node.SetOutputBit(vbyte, vbit, lock)
		
		if sig.Lock(lock):
			self.RailroadEvent(sig.GetEventMessage(lock=True))
			
	def SetHandswitch(self, hsname, state):
		hsnameKey = hsname.split(".")[0] # strip off the ".hand" suffix

		try:
			hs = self.handswitches[hsnameKey]
		except KeyError:
			logging.warning("Ignoring set handswitch- unknown switch name: %s" % hsname)
			return
		
		if hs.Unlock(state == 1):
			self.RailroadEvent(hs.GetEventMessage(lock=True))
			if not hs.UpdateIndicators():
				hs.District().SetHandswitch(hsnameKey, state)

	def SetSignalFleet(self, signame, flag):
		sig = self.signals.get(signame, None)
		if sig is None:
			return

		self.fleetedSignals[signame] = flag
		sig.SetFleet(flag)

	def SetOSRoute(self, blknm, rtname, ends, signals):
		self.osRoutes[blknm] = [rtname, ends, signals]
		print("OS Route: %s: Route %s  Turnouts: %s  Signals: %s" % (blknm, rtname, ends, signals))

	def GetOSRoutes(self):
		return self.osRoutes
		
	def SetControlOption(self, name, value):
		self.controlOptions[name] = value
		if name == "osslocks":
			self.osslocks = value == 1
		for d in self.districts.values():
			d.UpdateControlOption()

	def GetControlOptions(self):
		return self.controlOptions

	def GetControlOption(self, name):
		try:
			return self.controlOptions[name]
		except (KeyError, IndexError):
			return 0
		
	def SetBlockDirection(self, blknm, direction):
		try:
			blk = self.blocks[blknm]
		except KeyError:
			logging.warning("ignoring block direction - unknown block: %s" % blknm)
			return

		blk.SetDirection(direction == "E")
		#
		# if blk.SetDirection(direction == "E"):
		# 	self.RailroadEvent(blk.GetEventMessage(direction=True))

	def SetBlockClear(self, blknm, clear):
		if blknm in ["N20", "S11"]:
			logging.debug("==================================Set Block Clear %s" % blknm)
		try:
			blk = self.blocks[blknm]
		except KeyError:
			logging.warning("ignoring block clear - unknown block: %s" % blknm)
			logging.debug("Block not found")
			return

		blk.SetCleared(clear)
		#
		# if blk.SetCleared(clear):
		# 	self.RailroadEvent(blk.GetEventMessage(clear=True))
		
	def SetDistrictLock(self, name, value):
		if self.districtLock[name] == value:
			return False

		self.districtLock[name] = value
		msg = {"districtlock": {name: value}}
		self.RailroadEvent(msg)
		return True

	def FindRoute(self, sig):
		signm = sig.Name()
		# print("find route for signal %s" % signm)
		# print("possible routes: %s" % json.dumps(sig.possibleRoutes))
		for osblknm, osblk in self.osblocks.items():
			ar = osblk.ActiveRoute()
			if ar is None:
				continue

			# print("block, sigs = %s %s" % (blknm, str(siglist)))
			if signm in ar.signals:
				rname = osblk.ActiveRouteName()

				rt = self.routes[rname]
				return rt, osblk

		# print("no route found")
		return None, None

	def AddBlock(self, name, district, node, address, bits, east):
		try:
			b = self.blocks[name]
				
		except KeyError:
			# this is the normal scenario
			b = None
			
		if b is None:
			b = Block(name, district, node, address, east)
		else:
			if b.IsNullBlock():
				b.SetBlockAddress(district, node, address)
				b.SetDirection(east)
			else:
				logging.warning("Potential duplicate block: %s" % name)
				
		b.SetBits(bits)
		self.blocks[name] = b
		if len(bits) > 0:
			node.AddInputToMap(bits[0], [b])
		return b
					
	def AddBlockInd(self, name, district, node, address, bits):
		try:
			b = self.blocks[name]
		except KeyError:
			b = Block(name, None, None, None, True)
			self.blocks[name] = b
			
		b.AddIndicator(district, node, address, bits)
		return b

	def AddIndicator(self, name, district, node, address, bits):
		if name in self.indicators:
			logging.warning("Duplicate definition for indicator %s" % name)
			return self.indicators[name]
			
		i = Indicator(name, district, node, address)
		i.SetBits(bits)
		self.indicators[name] = i
		return i

	def AddOutputDevice(self, name, district, node, address, bits):
		if name in self.odevices:
			logging.warning("Duplicate definition for output device %s" % name)
			return self.odevices[name]
			
		i = ODevice(name, district, node, address)
		i.SetBits(bits)
		self.odevices[name] = i
		return i

	def AddLock(self, name, district, node, address, bits):
		if name in self.locks:
			logging.warning("Duplicate definition for lock%s" % name)
			return self.odevices[name]
			
		i = Lock(name, district, node, address)
		i.SetBits(bits)
		self.locks[name] = i
		return i

	def AddStopRelay(self, name, district, node, address, bits):
		if name in self.stopRelays:
			logging.warning("Duplicate definition for stopping relay %s" % name)
			return self.stopRelays[name]
			
		r = StopRelay(name, district, node, address)
		r.SetBits(bits)
		self.stopRelays[name] = r
		return r
	
	def AddSignal(self, name, district, node, address, bits):
		try:
			s = self.signals[name]
				
		except KeyError:
			# this is the normal scenario
			s = None
			
		if s is None:
			s = Signal(name, district, node, address)
		else:
			if s.IsNullSignal():
				s.SetSignalAddress(district, node, address)
			else:
				logging.warning("Potential duplicate signal: %s" % name)

		s.SetBits(bits)
		self.signals[name] = s
		return s

	def AddSignalInd(self, name, district, node, address, bits):
		try:
			s = self.signals[name]
		except KeyError:
			s = Signal(name, None, None, None)
			self.signals[name] = s
				
		s.AddIndicator(district, node, address, bits)
		return s

	def AddSignalLever(self, name, district, node, address, bits):
		try:
			s = self.signalLevers[name]
				
		except KeyError:
			# this is the normal scenario
			s = None
			
		if s is None:
			s = SignalLever(name, district, node, address)
		else:
			if s.IsNullLever():
				s.SetLeverAddress(district, node, address)
			else:
				logging.warning("Potential duplicate signal lever: %s" % name)
				
		s.SetBits(bits)
		self.signalLevers[name] = s
		if bits[0] is not None:
			node.AddInputToMap(bits[0], [s, 'R'])
		if bits[1] is not None:
			node.AddInputToMap(bits[1], [s, 'C'])
		if bits[2] is not None:
			node.AddInputToMap(bits[2], [s, 'L'])
		return s

	def AddSignalLED(self, name, district, node, address, bits):
		try:
			s = self.signalLevers[name]
		except KeyError:
			s = SignalLever(name, None, None, None)
			self.signalLevers[name] = s
				
		s.SetLed(bits, district, node, address)
		return s
		
	def AddTurnout(self, name, district, node, address, bits):
		try:
			t = self.turnouts[name]
				
		except KeyError:
			# this is the normal scenario
			t = None
			
		if t is None:
			t = Turnout(name, district, node, address)
		else:
			if t.IsNullTurnout():
				t.SetTurnoutAddress(district, node, address)
			else:
				logging.warning("Potential duplicate turnout: %s" % name)
				
		t.SetBits(bits)
		self.turnouts[name] = t
		return t

	def AddTurnoutPair(self, aname, bname):
		try:
			ta = self.turnouts[aname]
		except KeyError:
			logging.warning("Invalid turnout pair %s:%s - turnout %s does not exist" % (aname, bname, aname))
			return

		self.turnoutPairs[bname] = ta
		ta.SetPairedTurnout(bname)

	def AddTurnoutPosition(self, name, district, node, address, bits):
		try:
			t = self.turnouts[name]
		except KeyError:
			t = Turnout(name, None, None, None)
			self.turnouts[name] = t
				
		t.SetPosition(bits, district, node, address)
		if len(bits) == 2:
			node.AddInputToMap(bits[0], [t, 'N'])
			node.AddInputToMap(bits[1], [t, 'R'])
		return t

	def AddTurnoutLock(self, name, district, node, address, bits):
		try:
			t = self.turnouts[name]
		except KeyError:
			t = Turnout(name, None, None, None)
			self.turnouts[name] = t
				
		t.SetLockBits(bits, district, node, address)
		return t

	def AddTurnoutLever(self, name, district, node, address, bits):
		try:
			t = self.turnouts[name]
		except KeyError:
			t = Turnout(name, None, None, None)
			self.turnouts[name] = t
				
		t.SetLever(bits, district, node, address)
		return t

	def AddTurnoutLED(self, name, district, node, address, bits):
		try:
			t = self.turnouts[name]
		except KeyError:
			t = Turnout(name, None, None, None)
			self.turnouts[name] = t
				
		t.SetLed(bits, district, node, address)
		return t

	def AddOutNXButton(self, name, district, node, address, bits):
		if name in self.outNxButtons:
			logging.warning("Duplicate definition for Out NX Button %s" % name)
			return self.outNxButtons[name]

		b = OutNXButton(name, district, node, address)
		self.outNxButtons[name] = b			
		b.SetBits(bits)
		return b
	
	def AddHandswitch(self, name, district, node, address, bits, blocknm):
		try:
			t = self.handswitches[name]
				
		except KeyError:
			# this is the normal scenario
			t = None
			
		if t is None:
			t = Handswitch(name, district, node, address, blocknm)
		else:
			if t.IsNullHandswitch():
				t.SetHandswitchAddress(district, node, address, blocknm)
			else:
				logging.warning("Potential duplicate handset: %s" % name)

		self.handswitches[name] = t		
		t.SetBits(bits)
		node.AddInputToMap(bits[0], [t, 'N'])
		node.AddInputToMap(bits[1], [t, 'R'])

	def AddHandswitchInd(self, name, district, node, address, bits, inverted=False):
		try:
			s = self.handswitches[name]
		except KeyError:
			s = Handswitch(name, None, None, None, None)
			self.handswitches[name] = s
			
		s.AddIndicator(district, node, address, bits, inverted)
		return s
					
	def AddHandswitchReverseInd(self, name, district, node, address, bits):
		try:
			s = self.handswitches[name]
		except KeyError:
			s = Handswitch(name, None, None, None, None)
			self.handswitches[name] = s
			
		s.AddReverseIndicator(district, node, address, bits)
		return s
					
	def AddHandswitchUnlock(self, name, district, node, address, bits):
		try:
			s = self.handswitches[name]
		except KeyError:
			s = Handswitch(name, None, None, None, None)
			self.handswitches[name] = s
			
		s.AddUnlock(district, node, address, bits)
		node.AddInputToMap(bits[0], [s, 'L'])
		return s
					
	def AddRouteIn(self, name, district, node, address, bits):
		if name in self.routesIn:
			logging.warning("Duplicate definition for Route In %s" % name)
			return self.routesIn[name]

		b = RouteIn(name, district, node, address)
		self.routesIn[name] = b		
		b.SetBits(bits)
		node.AddInputToMap(bits[0], [b])
		
		return b

	def AddBreaker(self, name, district, node, address, bits):
		try:
			b = self.breakers[name]
				
		except KeyError:
			# this is the normal scenario
			b = None
			
		if b is None:
			b = Breaker(name, district, node, address)
		else:
			if b.IsNullBreaker():
				b.SetBreakerAddress(district, node, address)
			else:
				logging.warning("Potential duplicate breaker: %s" % name)
				
		b.SetBits(bits)
		self.breakers[name] = b
		if len(bits) > 0:
			node.AddInputToMap(bits[0], [b])
			
		return b
					
	def AddBreakerInd(self, name, district, node, address, bits):
		try:
			b = self.breakers[name]
		except KeyError:
			b = Breaker(name, None, None, None)
			self.breakers[name] = b
			
		b.AddIndicator(district, node, address, bits)
		return b
	
	def setBus(self, bus):
		self.rrBus = bus
		for _, dobj in self.districts.items():
			dobj.setBus(bus)

	def GetCurrentValues(self):
		'''
		set turnouts/routes/blocks BEFORE signals
		'''					
		for l in [self.blocks, self.turnouts, self.signals]:  # , self.signalLevers, self.stopRelays]:
			for s in l.values():
				mlist = s.GetEventMessages()
				if mlist is not None:
					for m in mlist:
						yield m
		
		'''
		routes in are essentially a set of turnouts - send that information
		'''
		for r in self.routesIn.values():
			if r.GetState() == 1:
				msg = r.district.GetRouteInMsg(r)
				if msg is not None:
					yield msg
					
		for s in self.breakers.values():
			if not s.HasProxy(): # skip breakers that use a proxy
				m = s.GetEventMessage()
				if m is not None:
					yield m

		for osnm, osblk in self.osblocks.items():
			activeRouteName = osblk.ActiveRouteName()
			if activeRouteName is not None:
				m = {"setroute": [{ "os": osnm, "route": activeRouteName}]}
				yield m

		for signm, flag in self.fleetedSignals.items():
			m = {"fleet": [{ "name": signm, "value": flag}]}
			yield m

	def PlaceTrain(self, blknm):
		try:
			blk = self.blocks[blknm]
		except KeyError:
			logging.warning("Skipping train placement for block %s: unknown block" % blknm)
			return

		if blk.SetOccupied(True):
			self.RailroadEvent(blk.GetEventMessage())

	def RemoveTrain(self, blknm):
		try:
			blk = self.blocks[blknm]
		except KeyError:
			logging.warning("Skipping remove train for block %s: unknown block" % blknm)
			return

		if blk.SetOccupied(False):
			self.RailroadEvent(blk.GetEventMessage())

	def GetDistrictLock(self, name):  # only used in nassau - reserve judgement until then
		if name in self.districtLock:
			return self.districtLock[name]

		return None

	def GetBlocks(self):
		return {bn: self.blocks[bn].toJson() for bn in self.blocks}

	def GetBlock(self, blknm):
		try:
			return self.blocks[blknm]
		except KeyError:
			return None

	def GetStopRelay(self, blknm):
		try:
			return self.stopRelays[blknm]
		except KeyError:
			return None

	def GetSignals(self):
		result = {}
		for sn, s in self.signals.items():
			result[s.Name()] = {"aspect": s.Aspect(), "aspecttype": s.AspectType()}
		return result

	def GetTurnoutPositions(self):
		result = []
		for trnm, trn in self.turnouts.items():
			result.append({trnm: {"state": ("1" if trn.normal else "0"), "position": ("1" if trn.Position() is not None else "0")}})

		return result

	def GetTurnoutLock(self, name, pairedname):
		try:
			tout = self.turnouts[name]
		except KeyError:
			tout = None

		try:
			ptout = self.turnouts[pairedname]
		except KeyError:
			ptout = None

		if tout is None:
			mlocked = False
			mlockers = []
		else:
			mlocked = tout.IsLocked()
			mlockers = tout.Lockers()

		if ptout is None:
			plocked = False
			plockers = []
		else:
			plocked = ptout.IsLocked()
			plockers = ptout.Lockers()

		if tout is None and ptout is None:
			return {"turnoutlock": {"message": "turnout %s not found" % name}}

		locked = mlocked or plocked
		lockers = list(set(mlockers + plockers))

		return {"turnoutlock": {"name": name, "locked": locked, "lockers": lockers}}

	def GetTurnout(self, tonm):
		try:
			return self.turnouts[tonm]
		except KeyError:
			return None

	def GetHandswitch(self, hsnm):
		try:
			return self.handswitches[hsnm]
		except KeyError:
			return None

	def GetIndicator(self, indnm):
		try:
			return self.indicators[indnm]
		except KeyError:
			return None

	def GetSignal(self, signm):
		try:
			return self.signals[signm]
		except KeyError:
			return None
		
	def GetSignalLevers(self):
		rv = {}
		for n, sl in self.signalLevers.items():
			node = sl.Node()
			ivals = node.GetInputBits(sl.Bits())
			rv[n] = ivals
		return rv

	def GetOutputDevice(self, onm):
		try:
			return self.odevices[onm]
		except KeyError:
			return None
			
	def GetNodeBits(self, addr):
		'''
		this routine handles the getbits command from HTTP server
		'''
		for dnodes in self.nodes.values():
			if addr in dnodes:
				return dnodes[addr].GetAllBits()
			
		return 0, [], []

	def SetInputBitByAddr(self, addr, vbytes, vbits, vals):
		# this routine handles the setinbit command from HTTP server
		logging.debug("setinputbit addr %s bytes %s  bits %s vals %s" % (addr, str(vbytes), str(vbits), str(vals)))
		for dnodes in self.nodes.values():
			if addr in dnodes:
				for i in range(len(vbytes)):
					dnodes[addr].SetInputBit(vbytes[i], vbits[i], 1 if vals[i] != 0 else 0)

	def OutIn(self):
		delList = []
		for toname, ctr in self.pulsedOutputs.items():
			if not ctr.tally():
				delList.append(toname)
				
		for toname in delList:
			del self.pulsedOutputs[toname]

		self.pendingDetectionLoss.NextCycle()

		for district in self.districts.values():
			district.OutIn()

		self.ExamineInputs()

	def UpdateDistrictTurnoutLocksByNode(self, districtName, released, addressList):
		for t in self.turnouts.values():
			if t.district is None:
				continue
			
			if t.district.Name() == districtName and t.address in addressList:
				t.UpdateLockBits(released)
		
	def UpdateDistrictTurnoutLocks(self, districtName, released):
		for t in self.turnouts.values():
			if t.district is None:
				continue
			
			if t.district.Name() == districtName:
				t.UpdateLockBits(released)

	def UpdateIgnoreList(self):
		self.ignoredBlocks = self.settings.rrserver.ignoredblocks
		logging.info("railroad ignore blocks list: %s" % str(self.ignoredBlocks))
		
	def ExamineInputs(self):
		for addr, district, node in self.addrList:
			skiplist, resumelist = district.GetControlOption()
			changedBits = node.GetChangedInputs()
			for node, vbyte, vbit, objparms, newval in changedBits:
				obj = objparms[0]
				objType = obj.InputType()
				objName = obj.Name()
				# logging.debug("changed bit: %s(%s) %x %s %s %s" % (objName, objType, node.Address(), vbyte, vbit, newval))

				if objType == INPUT_BLOCK:
					self.InputBlock(district, obj, objName, newval)

				elif objType == INPUT_TURNOUTPOS:
					pos = obj.Position()
					if pos:
						bits, district, node, address = pos
						nflag = node.GetInputBit(bits[0][0], bits[0][1])
						rflag = node.GetInputBit(bits[1][0], bits[1][1])
						'''
						the switch itself is telling us what position it is it.  This
						must be forced on all display programs
						'''
						if obj.IsNormal():
							if nflag == 0 and rflag == 1:
								if obj.SetNormal(False):
									msgs = obj.GetEventMessages()
									msgs.extend(self.UpdateRoutesForTurnout(obj))
									obj.UpdateLed()
									for m in msgs:
										self.RailroadEvent(m)
						else:
							if nflag == 1 and rflag == 0:
								if obj.SetNormal(True):
									msgs = obj.GetEventMessages()
									msgs.extend(self.UpdateRoutesForTurnout(obj))
									obj.UpdateLed()
									for m in msgs:
										self.RailroadEvent(m)

					if obj.HasLever():
						bt = obj.Bits()
						if len(bt) > 0:
							nbit, rbit = node.GetInputBits(bt)
							if obj.SetLeverState('R' if nbit == 0 else 'N'):
								obj.district.TurnoutLeverChange(obj)

				elif objType == INPUT_BREAKER:
					if obj.SetStatus(newval == 1):
						if obj.HasProxy():
							# use the proxy to show updated breaker status
							obj.district.ShowBreakerState(obj)
						else:
							obj.UpdateIndicators()
							self.RailroadEvent(obj.GetEventMessage())
	
				elif objType == INPUT_SIGNALLEVER:
					if obj.Name() not in skiplist: # bypass levers that are skipped because of a control option
						self.ProcessSignalLever(obj, node)
					else:
						self.Alert(district.ControlRestrictedMessage(), locale=district.Locale())

				elif objType == INPUT_HANDSWITCH:
					dataType = objparms[1]
					if dataType == "L":  # handswitch unlock switch
						objnm = obj.Name()
						if objName in skiplist:
							self.Alert(district.ControlRestrictedMessage(), locale=district.Locale())
						else:
							if objnm in [ "CSw21ab", "PBSw15ab" ]:
								if obj.Unlock(newval != 0):
									obj.UpdateIndicators()
								unlock = obj.GetUnlock()
								if unlock:
									district, node, addr, bits = unlock
									district.SetHandswitchIn(obj, newval)
							else:
								unlock = obj.GetUnlock()
								if unlock:
									district, node, addr, bits = unlock
									uflag = node.GetInputBit(bits[0][0], bits[0][1])
									if obj.Unlock(uflag != 0):
										self.RailroadEvent(obj.GetEventMessage(lock=True))
										obj.UpdateIndicators()
					
					else:  # handswitch turnout position
						pos = obj.Position()
						if pos:
							district, node, address, bits = pos
							nflag = node.GetInputBit(bits[0][0], bits[0][1])
							rflag = node.GetInputBit(bits[1][0], bits[1][1])
							if obj.IsNormal():
								if nflag == 0 and rflag == 1:
									if obj.SetNormal(False):
										self.RailroadEvent(obj.GetEventMessage())
							else:
								if nflag == 1 and rflag == 0:
									if obj.SetNormal(True):
										self.RailroadEvent(obj.GetEventMessage())
		
				elif objType == INPUT_ROUTEIN:
					bt = obj.Bits()
					if len(bt) > 0:
						stat = node.GetInputBit(bt[0][0], bt[0][1])
						osName = obj.district.RouteIn(obj, stat, self.turnouts)
						if osName is not None and osName not in ["NWOSCY"]:
							msgs = self.UpdateRoutesForOS(osName)
							for m in msgs:
								logging.debug("Sending %s" % str(m))
								self.RailroadEvent(m)

			'''
			The resume list is a list of objects - signal levers, or handswitch unlocks - that have been ignored because of the
			control setting for this district, but now need to be considered because the control value has changed.  We need to 
			react to the current value of these objects as if they were just now set to their current value
			'''
			for o in resumelist:
				try:
					obj = self.signalLevers[o]
				except KeyError:
					try:
						obj = self.handswitches[o]
					except KeyError:
						logging.error("Unknown object name: %s in resume list" % o)
						
					else:
						if o == "CSw21ab":
							olist = ["CSw21a", "CSw21b"]
						elif o == "PBSw15ab":
							olist = ["PBSw15a", "PBSw15b"]
						else:
							olist = None
							
						unlock = obj.GetUnlock()
						if unlock:
							district, node, addr, bits = unlock
							uflag = node.GetInputBit(bits[0][0], bits[0][1])
							if obj.Unlock(uflag == 1):
								if olist is None:
									self.RailroadEvent(obj.GetEventMessage(lock=True))
								else:
									for obn in olist:
										obj2 = self.handswitches[obn]
										obj2.Lock(uflag == 1)
										self.RailroadEvent(obj2.GetEventMessage(lock=True))
					
				else:
					self.ProcessSignalLever(obj, obj.node)

	def InputBlock(self, district, obj, objName, newval):
		if objName.split(".")[0] in self.ignoredBlocks:
			logging.info("Ignoring block %s as per ignore list" % objName)
			return

		if newval != 0:  # if block has changed to occupied
			# remove any pending detection loss
			self.pendingDetectionLoss.Remove(objName)

			if obj.osblk is not None:
				# we've entered an OS block - turn the entry signal back to red and record the signal aspect and exit
				# for future fleeting if fleeting is enabled for the signal
				rte = obj.osblk.ActiveRoute()
				if rte is not None:
					sigEnt = rte.EntrySignal()
					sig = self.signals.get(sigEnt, None)
					blkExit = rte.ExitBlock()
					exbn = "None" if blkExit is None else blkExit.Name()

					if sig is not None and blkExit is not None and sig.Aspect() != 0 and sig.Fleeted():
						self.Alert("Recording PFA for %s: %s %s" % (sigEnt, obj.osblk.Name(), obj.osblk.ActiveRouteName()))
						self.PendingFleetActions[exbn] = [sig, obj.osblk, obj.osblk.ActiveRouteName()]
					else:
						self.Alert("not recorded, sig = %s" % ("None" if sig is None else sig.Name()))
						self.Alert("exit block = %s" % exbn)
						if sig is not None:
							self.Alert("aspect: %s  fleeted: %s" % (sig.Aspect(), sig.Fleeted()))

					sig.SetAspect(0)
					self.RailroadEvent((sig.GetEventMessage()))

				if obj.IsSubBlock() and obj.MainHasTrain():
					obj.SetTrain(obj.MainBlockTrain())
					obj.SetStatus(obj.MainBlockStatus())
				return

			# entry into a non-OS block
			self.Alert("checking block %s" % objName)
			if objName in ["S11.E", "S21.E", "N10.W", "N20.W"]:
				self.CheckShoreTunnelSignals(obj, objName)

			if obj.SetStatus("U"):
				tr, rear = self.IdentifyTrain(obj)
				if tr.IsIdentified():
					obj.SetStatus("O")
					obj.SetEast(tr.IsEast())  # blocks take on the direction of known trains
				else:
					tr.SetEast(obj.IsEast())  # unknown trains take on the block direction
				tr.AddBlock(obj, rear)
				obj.SetTrain(tr)
				obj.SetEast(tr.IsEast())
				self.RailroadEvent(obj.GetEventMessage())
				self.RailroadEvent(tr.GetEventMessage())

			obj.UpdateIndicators()

			# check if this is a stopping section
			if objName.endswith(".E") or objName.endswith(".W"):
				self.CheckStoppingSection(obj, objName)



		# otherwise, this is a detection loss - add it to pending, but only if we are currently occupied
		else:
			logging.debug("detection loss")
			if obj.IsOccupied():
				logging.debug("adding to pending detection loss list")
				self.pendingDetectionLoss.Add(objName, obj)
			else:
				self.DetectionLoss(obj)

	def CheckStoppingSection(self, blk, blkNm):
		# TODO
		# I also need SB logic when a signal changed to red (to activate the sb) or red to non-red (to deactivate the sb)
		blockend = blkNm[-1]
		block = blkNm[:-2]

		occupied = blk.IsOccupied()
		self.Alert("Block %s occupied %s" % (blkNm, occupied))

		east = blockend == "E"
		self.Alert("comparing %s with %s" % (east, blk.IsEast()))
		if east != blk.IsEast():
			self.Alert("Don't need to consider block %s because the block is movong in the opposite direction" % blkNm)
			return

		try:
			sigw, sige = self.sbToSigMap[block]
		except KeyError:
			self.Alert("Block %s not found in map" % block)
			return

		sig = sige if east else sigw
		if sig is None:
			return

		self.Alert("We need to look at aspect of signal %s" % str(sig.Name()))
		srName = block + ".srel"
		if sig.Aspect() == 0:
			self.Alert("We need to %sactivate stopping relay for block %s" % ("" if occupied else "de", block))
			self.SetRelay(srName, 1 if occupied else 0)
		else:
			self.Alert("We need to set/assert that stopping block for block %s is unactive" % block)
			self.SetRelay(srName, 0)

	def CheckShoreTunnelSignals(self, obj, objName):
		exbn = obj.MainBlockName()
		exitBlk = self.blocks[exbn]
		self.Alert("CSTS main block = %s" % exbn)

		if objName == "S11.E" and not obj.IsEast():
			self.Alert("case 1 ")
			sig = self.signals["N10W"]
			osName = self.DetermineSignalOS("N10W")
			osBlk = self.osblocks[osName]
			self.Alert("OS: %s" % osName)
			self.Alert("%s" % sig.Fleeted())
			self.Alert("%d" % sig.Aspect())
			if sig.Aspect() != 0 and sig.Fleeted():
				self.PendingFleetActions[exbn] = [sig, osBlk, None]
				sig.SetAspect(0)
				self.RailroadEvent((sig.GetEventMessage()))

		elif objName == "S21.E" and not obj.IsEast():
			self.Alert("case 2")
			sig = self.signals["N20W"]
			osName = self.DetermineSignalOS("N20W")
			osBlk = self.osblocks[osName]
			self.Alert("OS: %s" % osName)
			if sig.Aspect() != 0 and sig.Fleeted():
				self.PendingFleetActions[exbn] = [sig, osBlk, None]
				sig.SetAspect(0)
				self.RailroadEvent((sig.GetEventMessage()))

		elif objName == "N10.W" and obj.IsEast():
			self.Alert("case 3")
			sig = self.signals["S11E"]
			osName = self.DetermineSignalOS("S11E")
			osBlk = self.osblocks[osName]
			self.Alert("OS: %s" % osName)
			if sig.Aspect() != 0 and sig.Fleeted():
				self.PendingFleetActions[exbn] = [sig, osBlk, None]
				sig.SetAspect(0)
				self.RailroadEvent((sig.GetEventMessage()))

		elif objName == "N20.W" and obj.IsEast():
			self.Alert("case 4")
			sig = self.signals["S21E"]
			osName = self.DetermineSignalOS("S21E")
			osBlk = self.osblocks[osName]
			self.Alert("OS: %s" % osName)
			if sig.Aspect() != 0 and sig.Fleeted():
				self.PendingFleetActions[exbn] = [sig, osBlk, None]
				sig.SetAspect(0)
				self.RailroadEvent((sig.GetEventMessage()))

	def DetectionLoss(self, obj):
		tr = obj.RemoveFromTrain()
		if obj.SetStatus("E"):
			self.RailroadEvent(obj.GetEventMessage())
			if tr is not None:
				self.RailroadEvent(tr.GetEventMessage())

				if len(tr.Blocks()) == 0:
					self.DeleteTrain(tr)

			obj.UpdateIndicators()
			self.CheckFleetTriggers(obj)

		objName = obj.Name()
		if objName.endswith(".E") or objName.endswith(".W"):
			self.CheckStoppingSection(obj, objName)

	def CheckFleetTriggers(self, blk):
		if blk.IsCompletelyEmpty():
			mname = blk.MainBlockName()
			if mname in self.PendingFleetActions:
				sig, osblk, rteNm = self.PendingFleetActions[mname]
				del self.PendingFleetActions[mname]
				if osblk is None or rteNm is None or osblk.ActiveRouteName() == rteNm:
					osName = osblk.Name()
					try:
						a = self.CalculateAspect(sig, osName, False, False, None, True)
					except Exception as e:
						logging.warning("Exception %s in calc aspect %s" % (str(e), sig.Name()))
						return

					msgs = (self.ApplyAspect(a, sig, osName, False))
					msgs.extend(sig.GetEventMessages())
					for m in msgs:
						self.RailroadEvent(m)

	def RailroadEvents(self, elist):
		for e in elist:
			self.cbEvent(e)

	def RailroadEvent(self, event):
		self.cbEvent(event)

	def DeleteTrain(self, tr):
		trid = tr.IName()
		if trid is None:
			return

		try:
			del self.trains[trid]
		except KeyError:
			pass

	def Alert(self, msg, locale=None):
		msg = {"alert": {"msg": msg}}
		if locale is not None:
			msg["alert"]["locale"] = locale
		self.RailroadEvent(msg)

	def Advice(self, msg, locale=None):
		msg = {"advice": {"msg": msg}}
		if locale is not None:
			msg["advice"]["locale"] = locale
		self.RailroadEvent(msg)

	def UpdateRoutesForTurnout(self, turnout):
		tn = turnout.Name()

		try:
			osList = self.to2osMap[tn]
		except KeyError:
			osList = []

		result = []
		for osName in osList:
			result.extend(self.UpdateRoutesForOS(osName, turnout=tn))

		return result

	def UpdateRoutesForOS(self, osName, turnout=None):
		result = []
		try:
			osBlk = self.osblocks[osName]
		except KeyError:
			return result

		if osBlk.DetermineActiveRoute(self.turnouts):
			msgs = osBlk.GetEventMessages()
			if msgs is not None:
				result.extend(msgs)

				blk = self.blocks[osName]
				if blk is not None:
					dist = blk.District()
					if dist is not None:
						changes = dist.CheckTurnoutLocks(self.turnouts)
						for sw, flag in changes:
							result.append({"lockturnout": [{"name": sw, "lock": flag}]})

		return result

	def ProcessSignalLever(self, obj, node):
		objName = obj.Name()
		locale = obj.District().Locale()
		bt = obj.Bits()
		currentBits = self.lastValues.get(objName, [0, 0])
		if len(bt) > 0:
			rbit, cbit, lbit = node.GetInputBits(bt)
			if obj.SetLeverState(rbit, cbit, lbit):
				aspectL = 0
				aspectR = 0

				# possible values here: rbit is 1, lbit is one, or neither is 1.  Both being 1 is impossible
				if lbit != 0:
					left = 1
					right = 0
				elif rbit != 0:
					left = 0
					right = 1
				else:
					left = 0
					right = 0

				msgsL = []
				msgsR = []

				if left != currentBits[0]:
					aspectL, msgsL = self.ProcessSignalLeverSide(obj, left, cbit, "L", locale)
					if aspectL is not None:
						if objName not in self.lastValues:
							self.lastValues[objName] = [left, 0]
						else:
							self.lastValues[objName][0] = left

				if right != currentBits[1]:
					aspectR, msgsR = self.ProcessSignalLeverSide(obj, right, cbit, "R", locale)
					if aspectR is not None:
						if objName not in self.lastValues:
							self.lastValues[objName] = [0, right]
						else:
							self.lastValues[objName][1] = right

				if aspectL is not None and aspectR is not None:
					obj.UpdateLed(aspectR, aspectL)

				for m in msgsL+msgsR:
					self.RailroadEvent(m)

	def ProcessSignalLeverSide(self, lever, bit, callon, LR, locale):
		msgs = []
		leverName = lever.Name()
		locale = lever.District().Locale()
		sigBaseNm = leverName + LR
		osList = self.lvrToOSMap.get(sigBaseNm, None)

		if osList is None:
			logging.error("Unable to determine OS block for signal lever %s" % sigBaseNm)
			return None, []

		sigMatch = None

		for osName in osList:
			osblk = self.osblocks[osName]
			oab = osblk.ActiveRoute()
			if oab is None:
				sigMatch = None
			else:
				sigMatch = oab.HasSignal(sigBaseNm)
				if sigMatch is not None:
					break
		else:
			sigMatch = None

		if sigMatch is None:
			self.Alert("Unable to determine route for lever %s" % sigBaseNm, locale=locale)
			return None, []
		else:
			osblk = self.osblocks[osName]
			rtName = osblk.ActiveRouteName()
			if rtName is None:
				self.Alert("No Route Available for signal %s" % sigBaseNm, locale=locale)
				logging.debug("no active route for os %s - not setting signal %s" % (osName, leverName))
				return None, []

			try:
				sig = self.signals[sigMatch]
			except KeyError:
				sig = None

			if sig is None:
				return None, []

			msgs = []
			try:
				moving = bit == 0  # are we requesting a stop signal?
				aspect = self.CalculateAspect(sig, osName, moving, callon, locale, silent=False)
				if aspect is not None:
					msgs.extend(self.ApplyAspect(aspect, sig, osName, callon))
					logging.debug("calculated aspect for %s = %d" % (sigMatch, aspect))
					msgs.extend(sig.GetEventMessages())

			except Exception as e:
				logging.warning("Exception %s in calc aspect %s" % (str(e), sigMatch))
				return None, []

			lever.district.EvaluateDistrictLocks(sig, None)
			self.EvaluatePreviousSignals(sig)
			return aspect, msgs

	def CalculateAspect(self, sig, osName, moving, callon, locale, silent=False):
		self.Alert("Calculate aspect osname = %s" % osName)
		osblk = self.osblocks[osName]
		blk = osblk.Block()
		rtName = osblk.ActiveRouteName()
		rt = osblk.ActiveRoute()

		if moving:
			return 0

		if callon:
			return restrictedaspect(sig.AspectType())

		if sig is None or rtName is None:
			logging.error("unable to calculate aspect because signal(%s) and/or route(%s) or both is None" % (str(sig), str(rtName)))
			return None

		signame = sig.Name()

		logging.debug(
			"Calculating aspect for os %s/%s signal %s route %s moving %s" % (osblk.Name(), blk.Name(), sig.Name(), rtName, moving))

		if blk.IsOccupied():
			if not silent:
				self.Alert("Block %s is busy" % osblk.RouteDesignator(), locale=sig.District().Locale())
			logging.debug("Unable to calculate aspect: OS Block is busy")
			return None

		currentDirection = sig.East()
		if currentDirection != osblk.IsEast() and osblk.IsCleared():
			if not silent:
				self.Alert("Block %s is cleared in opposite direction" % osblk.RouteDesignator(), locale=sig.District().Locale())
			logging.debug("Unable to calculate aspect: Block %s is cleared in opposite direction" % osblk.Name())
			return None

		exitBlk = rt.ExitBlock(reverse=currentDirection != blk.IsEast())
		rType = rt.RouteType(reverse=currentDirection != blk.IsEast())

		if exitBlk.IsOccupied():
			if not silent:
				self.Alert("Block %s is busy" % exitBlk.RouteDesignator(), locale=sig.District().Locale())
			logging.debug("Unable to calculate aspect: Block %s is busy" % exitBlk.Name())
			return None

		if exitBlk.IsCleared():
			if exitBlk.East() != currentDirection:
				if not silent:
					self.Alert("Block %s is cleared in opposite direction" % exitBlk.RouteDesignator(), locale=sig.District().Locale())
				logging.debug("Unable to calculate aspect: Block %s cleared in opposite direction" % exitBlk.Name())
				return None

		if exitBlk.AreHandSwitchesUnlocked():
			if not silent:
				self.Alert("Block %s has a siding unlocked" % exitBlk.RouteDesignator())
			logging.debug("Unable to calculate aspect: Block %s has a siding unlocked" % exitBlk.Name())
			return None

		if currentDirection != osblk.IsEast():
			osblk.SetEast(currentDirection)

		if CrossingEastWestBoundary(osblk, exitBlk):
			logging.debug("we crossed a EW boundary between %s and %s" % (osblk.Name(), exitBlk.Name()))
			currentDirection = not currentDirection

		logging.debug("exit block, direction = %s, %s <=> %s" % (exitBlk.Name(), exitBlk.East(), currentDirection))
		logging.debug("about to call nextblock for block %s, currentdirection = %s, blk direction = %s" % (exitBlk.Name(), currentDirection, exitBlk.East()))
		nb = exitBlk.NextBlock(reverse=currentDirection != osblk.East())
		logging.debug("Setting EAST of exit block %s to %s" % (exitBlk.Name(), currentDirection))
		exitBlk.SetEast(currentDirection)
		logging.debug("next block returned %s" % ("None" if nb is None else nb.Name()))
		if nb:
			nbName = nb.Name()
			if CrossingEastWestBoundary(nb, exitBlk):
				logging.debug("change of direction to %s" % currentDirection)
				currentDirection = not currentDirection
			# nb.SetEast(currentDirection)
			logging.debug("Changing direction of block %s to %s" % (nbName, currentDirection))
			logging.debug("next block 1 = %s" % nbName)

			nbStatus = nb.GetStatus()
			nbRType = nb.RouteType(reverse=currentDirection != nb.East())
			nbRtName = nb.ActiveRouteName()
			# # try to go one more block, skipping past an OS block

			logging.debug("nbstatus = %s nbRType = %s  nbRtName = %s" % (nbStatus, nbRType, nbRtName))

			nxb = nb.ExitBlock(reverse=currentDirection != nb.East())
			if nxb is None:
				nxbNm = None
				nnb = None
			else:
				nxbNm = nxb.Name()
				logging.debug("next block 2 = %s" % nxbNm)

				if CrossingEastWestBoundary(nb, nxb):
					currentDirection = not currentDirection

				# nxb.SetEast(currentDirection)
				logging.debug("Changing direction of block %s to %s" % (nxbNm, currentDirection))
				nnb = nxb.NextBlock(reverse=currentDirection != nxb.East())
				logging.debug("nnb = %s" % ("None" if nnb is None else nnb.Name()))

			if nnb:
				nnbClear = nnb.IsCleared()
				nnbName = nnb.Name()
			else:
				nnbClear = False
				nnbName = None
		else:
			logging.debug("no bext block identified")
			nxbNm = None
			nbStatus = None
			nbName = None
			nbRType = None
			nbRtName = None
			nnbClear = False
			nnbName = None

		aType = sig.GetAspectType()
		aspect = self.GetAspect(aType, rType, nbStatus, nbRType, nnbClear)

		if self.debug.showaspectcalculation:
			self.Alert("======== New aspect calculation ========")
			self.Alert("OS: %s Route: %s  Sig: %s" % (osblk.Name(), rt.Name(), sig.Name()))
			self.Alert("exit block name = %s   RT: %s" % (exitBlk.Name(), routetype(rType)))
			self.Alert("NB: %s Status: %s  NRT: %s" % (nbName, statusname(nbStatus), routetype(nbRType)))
			self.Alert("Next route = %s" % nbRtName)
			self.Alert("next exit block = %s" % nxbNm)
			self.Alert("NNB: %s  NNBC: %s" % (nnbName, nnbClear))
			self.Alert("Aspect = %s (%x)" % (aspectname(aspect, aType), aspect))

		logging.debug(
			"Calculated aspect = %s   aspect type = %s route type = %s next block status = %s next block route type = %s next next block clear = %s" %
			(aspectname(aspect, aType), aspecttype(aType), routetype(rType), statusname(nbStatus), routetype(nbRType), nnbClear))

		return aspect

	def ApplyAspect(self, aspect, sig, osName, callon):
		signame = sig.Name()
		wasCallon = sig.IsCallon()
		logging.debug("wascallon: %s" % wasCallon)
		osblk = self.osblocks[osName]
		blk = self.blocks[osName]
		exitBlk = osblk.ActiveRoute().ExitBlock(reverse=sig.East() != blk.IsEast())
		ebList = exitBlk.GetAllBlocks()
		logging.debug("setting signal %s to aspect %s %s" % (signame, aspect, callon))
		sig.SetAspect(aspect, callon=callon)
		tlock = []
		if aspect == 0:
			logging.debug("new aspect is 0")
			if not wasCallon:
				logging.debug("not wascallon")
				for eb in ebList:
					logging.debug("set block %s to E" % eb.Name())
					if not eb.IsOccupied():
						logging.debug("yes")
						eb.SetStatus("E")
						# eb.Reset()
				if not osblk.IsOccupied():
					logging.debug("set OS %s to E" % osblk.Name())
					osblk.SetStatus("E")
					# osblk.Reset()
					tlock.extend(osblk.LockRoute(False, sig.Name()))
		else:
			if not callon:
				for eb in ebList:
					eb.SetStatus("C")
				osblk.SetStatus("C")
				tlock.extend(osblk.LockRoute(True, sig.Name()))

		if len(tlock) > 0:
			lockmsg = [{"lockturnout": [{"name": t[0].Name(), "lock": t[1]} for t in tlock]}]
		else:
			lockmsg = []

		self.UpdateSignalLeverLEDs(sig, aspect, callon)

		msgs = osblk.Block().GetEventMessages()
		for eb in ebList:
			self.Alert("Messages for nblock %s" % eb.Name())
			ml = eb.GetEventMessages()
			for m in ml:
				self.Alert(str(m))
			self.Alert("-------------")
			msgs.extend(eb.GetEventMessages())
		msgs.extend(lockmsg)
		return msgs

	@staticmethod
	def GetAspect(atype, rtype, nbstatus, nbrtype, nnbclear):
		# print("Get aspect.  Aspect type = %s, route type %s nextblockstatus %s next block route type %s nextnextclear %s" %
		# (aspecttype(atype), routetype(rtype), statustype(nbstatus), routetype(nbrtype), str(nnbclear)))
		if atype == RegAspects:
			if rtype == MAIN and nbstatus == "C" and nbrtype == MAIN:
				return 0b011  # Clear

			elif rtype == MAIN and nbstatus == "C" and nbrtype == DIVERGING:
				return 0b010  # Approach Medium

			elif rtype == DIVERGING and nbstatus == "C" and nbrtype == MAIN:
				return 0b111  # Medium Clear

			elif rtype in [MAIN, DIVERGING] and nbstatus == "C" and nbrtype == SLOW:
				return 0b110  # Approach Slow

			elif rtype == MAIN and (nbstatus != "C" or nbrtype == RESTRICTING):
				return 0b001  # Approach

			elif rtype == DIVERGING and (nbstatus != "C" or nbrtype != MAIN):
				return 0b101  # Medium Approach

			elif rtype in [RESTRICTING, SLOW]:
				return 0b100  # Restricting

			else:
				return 0  # Stop

		elif atype == RegSloAspects:
			if rtype == MAIN and nbstatus == "C":
				return 0b011  # Clear

			elif rtype == SLOW and nbstatus == "C":
				return 0b111  # Slow clear

			elif rtype == MAIN:
				return 0b001  # Approach

			elif rtype == SLOW:
				return 0b101  # Slow Approach

			elif rtype == RESTRICTING:
				return 0b100  # Restricting

			else:
				return 0  # Stop

		elif atype == AdvAspects:
			if rtype == MAIN and nbstatus == "C" and nbrtype == MAIN and nnbclear:
				return 0b011  # Clear

			elif rtype == MAIN and nbstatus == "C" and nbrtype == DIVERGING:
				return 0b010  # Approach Medium

			elif rtype == DIVERGING and nbstatus == "C" and nbrtype == MAIN:
				return 0b111  # Clear

			elif rtype == MAIN and nbstatus == "C" and nbrtype == MAIN and not nnbclear:
				return 0b110  # Advance Approach

			elif rtype == MAIN and (nbstatus != "C" or nbrtype == RESTRICTING):
				return 0b001  # Approach

			elif rtype == DIVERGING and (nbstatus != "C" or nbrtype != MAIN):
				return 0b101  # Medium Approach

			elif rtype == RESTRICTING:
				return 0b100  # Restricting

			else:
				return 0  # Stop

		elif atype == SloAspects:
			if nbstatus == "C" and rtype in [SLOW, DIVERGING]:
				return 0b01  # Slow Clear

			elif nbstatus != "C" and rtype == SLOW:
				return 0b11  # Slow Approach

			elif rtype == RESTRICTING:
				return 0b10  # Restricting

			else:
				return 0  # Stop

		else:
			return 0

	def EvaluatePreviousSignals(self, sig):
		logging.debug("enter evaluate previous signals for signal %s" % sig.Name())
		if self.debug.showaspectcalculation:
			self.Alert("========================== Evaluating prior signals for signal %s" % sig.Name())
		rt, osblk = self.FindRoute(sig)
		if osblk is None:
			if self.debug.showaspectcalculation:
				self.Alert("No OS block identified")
			return

		osblkNm = osblk.Name()

		# we're going backwards, so look in that same direction
		currentDirection = not sig.East()
		if self.debug.showaspectcalculation:
			self.Alert("Starting in direction %s" % ("east" if currentDirection else "west"))
		exitBlk = rt.ExitBlock(reverse=currentDirection != osblk.East())
		if exitBlk is None:
			if self.debug.showaspectcalculation:
				self.Alert("No exit block identified")
			return

		exitBlkNm = exitBlk.Name()

		if self.debug.showaspectcalculation:
			self.Alert("Now looking at previous block %s" % exitBlkNm)

		if CrossingEastWestBoundary(osblk, exitBlk):
			currentDirection = not currentDirection
			if self.debug.showaspectcalculation:
				self.Alert("Changing direction to %s because of E/W boundary" % ("east" if currentDirection else "west"))

		nb = exitBlk.NextBlock(reverse=currentDirection != exitBlk.East())
		if nb is None:
			if self.debug.showaspectcalculation:
				self.Alert("No next OS block identified")
			return

		nbName = nb.Name()
		if not nb.IsOS():
			if self.debug.showaspectcalculation:
				self.Alert("Next block is not an OS block - returning")
			return

		rt = nb.ActiveRoute()
		if rt is None:
			if self.debug.showaspectcalculation:
				self.Alert("OS block %s does not have a route - returning" % nbName)
			return

		if CrossingEastWestBoundary(nb, exitBlk):
			currentDirection = not currentDirection
			if self.debug.showaspectcalculation:
				self.Alert("Changing direction to %s because of E/W boundary" % ("east" if currentDirection else "west"))

		sigs = rt.Signals()
		ep = [None if e is None else e.Name() for e in rt.EndPoints()]
		if len(sigs) != 2 or len(ep) != 2:
			logging.error("signals and or endpoints for route %s != 2" % rt.GetName())
			return

		if exitBlkNm not in ep:
			if self.debug.showaspectcalculation:
				self.Alert("unknown exit block: %s - returnins" % exitBlkNm)
				self.Alert(str(ep))
			return

		if exitBlkNm == ep[0]:
			sigNm = sigs[1]
		elif exitBlkNm == ep[1]:
			sigNm = sigs[0]
		else:
			self.Alert("Unable to identify signal for block %s" % exitBlkNm)
			return

		if self.debug.showaspectcalculation:
			self.Alert("Considering signal %s" % sigNm)

		try:
			psig = self.signals[sigNm]
		except KeyError:
			return

		# we're not going to change signals that are stopped, so end this here
		currentAspect = psig.Aspect()
		if currentAspect == 0:
			if self.debug.showaspectcalculation:
				self.Alert("Signal %s is Stopped - finished" % sigNm)
			return

		if sigNm.startswith("P"):
			# skip anything to do with Port - we don't control it
			if self.debug.showaspectcalculation:
				self.Alert("Ignoring Port signals")
			return

		# stop if the aspect is unchanged or can't be calculated
		newAspect = self.CalculateAspect(psig, nbName, False, False, None, silent=True)
		if newAspect is None or newAspect == currentAspect:
			if self.debug.showaspectcalculation:
				if self.debug.showaspectcalculation:
					if newAspect is None:
						self.Alert("Unable to calculate a new aspect for signal %s" % sigNm)
					else:
						self.Alert("Aspect for signal %s is unchanged - finished" % sigNm)
			return

		psig.SetAspect(newAspect)
		msgs = psig.GetEventMessages()

		if self.debug.showaspectcalculation:
			self.Alert("Calculated new aspect of %d for signal %s" % (newAspect, sigNm))
			for m in msgs:
				self.Alert("Cmd: (%s)" % str(m))

		for m in msgs:
			self.RailroadEvent(m)

		self.EvaluatePreviousSignals(psig)

	def IdentifyTrain(self, blk):
		"""
		logging.debug("identify train in block %s" % blk.Name())		returns the identified train, or NOne if no traiun identified
		Also return False if this block is to be added to the front of the train, True otherwise
		"""
		if self.debug.identifytrain:
			self.Alert("========New Train Identification========")
			self.Alert("Attempting to identify train in block %s" % blk.Name())
		# =======================================================================
		# uncomment the following code to not identify trains that cross into a block against the signal
		#
		# if self.type == OVERSWITCH:
		# 	if not cleared:
		# 		# should not be entering an OS block without clearance
		# 		return None, False
		# =======================================================================
			
		if blk.IsEast():
			'''
			first look west, then east, then create a new train
			'''
			if self.debug.identifytrain:
				self.Alert("Eastbound block - look west first")
			blkw = blk.NextDetectionSectionWest()
			if blkw is not None:
				if blkw.Name() in ["KOSN10S11", "KOSN20S21"]:
					if self.debug.identifytrain:
						self.Alert("Special case for null blocks KOSN10S11 and KOSN20S21")

					blkw = blkw.NextDetectionSectionWest()
					if blkw:
						if self.debug.identifytrain:
							self.Alert("Using block %s instead of null block" % blkw.Name())
						tr = blkw.Train()
						if tr:
							self.CheckEWCross(tr, blk, blkw)
							if self.debug.identifytrain:
								self.Alert("Returning train %s" % tr.Name())
							# so we found a train coming from the west - so it is moving east
							# so if it is an eastbound train we are adding to the front - else to the rear
							return tr, not tr.IsEast()
						else:
							if self.debug.identifytrain:
								self.Alert("Block %s did not have a train to consider" % blkw.Name())
					else:
						if self.debug.identifytrain:
							self.Alert("No block west to examine")
				else:
					if self.debug.identifytrain:
						self.Alert("Looking at block %s" % blkw.Name())
					tr = blkw.Train()
					if tr:
						self.CheckEWCross(tr, blk, blkw)
						if self.debug.identifytrain:
							self.Alert("Returning train %s" % tr.Name())
						# so we found a train coming from the west - so it is moving east
						# so if it is an eastbound train we are adding to the front - else to the rear
						return tr, not tr.IsEast()
					else:
						if self.debug.identifytrain:
							self.Alert("Block %s did not have a train to consider" % blkw.Name())

			if self.debug.identifytrain:
				self.Alert("Eastbound block - nothing found west - now look east")
			blke = blk.NextDetectionSectionEast()
			if blke is not None:
				if blke.Name() in ["KOSN10S11", "KOSN20S21"]:
					if self.debug.identifytrain:
						self.Alert("Special case for null blocks KOSN10S11 and KOSN20S21")

					blke = blke.NextDetectionSectionEast()
					if blke:
						if self.debug.identifytrain:
							self.Alert("Using block %s instead of null block" % blke.Name())
						tr = blke.Train()
						if tr:
							self.CheckEWCross(tr, blk, blke)
							if self.debug.identifytrain:
								self.Alert("Returning train %s rear" % tr.Name())
							# so we found a train coming from the east - so it is moving west
							# so if it is a westbound train we are adding to the front - else to the rear
							return tr, tr.IsEast()
						else:
							if self.debug.identifytrain:
								self.Alert("Block %s did not have a train to consider" % blke.Name())
					else:
						if self.debug.identifytrain:
							self.Alert("No block east to examine")

				else:
					if self.debug.identifytrain:
						self.Alert("Looking at block %s" % blke.Name())
					tr = blke.Train()
					if tr:
						self.CheckEWCross(tr, blk, blke)
						if self.debug.identifytrain:
							self.Alert("Returning train %s rear" % tr.Name())
						# so we found a train coming from the east - so it is moving west
						# so if it is a westbound train we are adding to the front - else to the rear
						return tr, tr.IsEast()
					else:
						if self.debug.identifytrain:
							self.Alert("Block %s did not have a train to consider" % blke.Name())

		else:
			'''
			first look east, then west, then create a new train
			'''
			if self.debug.identifytrain:
				self.Alert("Westbound block - look east first")
			blke = blk.NextDetectionSectionEast()
			if self.debug.identifytrain:
				self.Alert("Next detection section east from %s is %s" % (blk.Name(), "None" if blke is None else blke.Name()))
			if blke is not None:
				if blke.Name() in ["KOSN10S11", "KOSN20S21"]:
					if self.debug.identifytrain:
						self.Alert("Special case for null blocks KOSN10S11 and KOSN20S21")

					blke = blke.NextDetectionSectionEast()
					if blke is not None:
						if self.debug.identifytrain:
							self.Alert("Using block %s instead of null block" % blke.Name())
						tr = blke.Train()
						if tr:
							self.CheckEWCross(tr, blk, blke)
							if self.debug.identifytrain:
								self.Alert("Returning train %s" % tr.Name())
							# so we found a train coming from the east - so it is moving west
							# so if it is a westbound train we are adding to the front - else to the rear
							return tr, tr.IsEast()
						else:
							if self.debug.identifytrain:
								self.Alert("Block %s did not have a train to consider" % blke.Name())
					else:
						if self.debug.identifytrain:
							self.Alert("No block east to examine")

				else:
					if self.debug.identifytrain:
						self.Alert("Looking at block %s" % blke.Name())
					tr = blke.Train()
					if tr:
						self.CheckEWCross(tr, blk, blke)
						if self.debug.identifytrain:
							self.Alert("Returning train %s" % tr.Name())
						# so we found a train coming from the east - so it is moving west
						# so if it is a westbound train we are adding to the front - else to the rear
						return tr, tr.IsEast()
					else:
						if self.debug.identifytrain:
							self.Alert("Block %s did not have a train to consider" % blke.Name())
					logging.debug("end b")

			if self.debug.identifytrain:
				self.Alert("Westbound block - nothing found east - now look west")
			blkw = blk.NextDetectionSectionWest()
			if self.debug.identifytrain:
				self.Alert("Next detection section west from %s is %s" % (blk.Name(), "None" if blkw is None else blkw.Name()))
			if blkw is not None:
				if blkw.Name() in ["KOSN10S11", "KOSN20S21"]:
					if self.debug.identifytrain:
						self.Alert("Special case for null blocks KOSN10S11 and KOSN20S21")

					blkw = blkw.NextDetectionSectionWest()
					if blkw is not None:
						if self.debug.identifytrain:
							self.Alert("Using block %s instead of null block" % blkw.Name())
						tr = blkw.Train()
						if tr:
							self.CheckEWCross(tr, blk, blkw)
							if self.debug.identifytrain:
								self.Alert("Returning train %s rear" % tr.Name())
							# so we found a train coming from the west - so it is moving east
							# so if it is an eastbound train we are adding to the front - else to the rear
							return tr, not tr.IsEast()
						else:
							if self.debug.identifytrain:
								self.Alert("Block %s did not have a train to consider" % blkw.Name())
					else:
						if self.debug.identifytrain:
							self.Alert("No block west to examine")

				else:
					if self.debug.identifytrain:
						self.Alert("Looking at block %s" % blkw.Name())
					tr = blkw.Train()
					if tr:
						self.CheckEWCross(tr, blk, blkw)
						if self.debug.identifytrain:
							self.Alert("Returning train %s rear" % tr.Name())
						# so we found a train coming from the west - so it is moving east
						# so if it is an eastbound train we are adding to the front - else to the rear
						return tr, not tr.IsEast()
					else:
						if self.debug.identifytrain:
							self.Alert("Block %s did not have a train to consider" % blkw.Name())

		if self.debug.identifytrain:
			self.Alert("Unable to identify a train - generate a new unknown train")

		tr = Train()
		# a new train takes on the direction of the block it's in
		tr.SetEast(blk.IsEast())
		self.trains[tr.IName()] = tr
		return tr, False

	def CheckEWCross(self, tr, blk, blkn):
		if CrossingEastWestBoundary(blk, blkn):
			if self.debug.identifytrain:
				self.Alert("Train %s crossed an E/W boundary - reversing train direction" % tr.Name())
			tr.SetEast(not tr.GetEast())
			# self.frame.Request({"renametrain": {"oldname": tr.GetName(), "newname": tr.GetName(), "east": "1" if tr.GetEast() else "0"}})

class PendingDetectionLoss:
	def __init__(self, railroad):
		self.pendingDetectionLoss = {}
		self.railroad = railroad
		self.pendingDetectionLossCycles = railroad.settings.rrserver.pendingdetectionlosscycles
				
	def Add(self, block, obj):
		self.pendingDetectionLoss[block] = [obj, self.pendingDetectionLossCycles]
		
	def Remove(self, block):
		try:
			del self.pendingDetectionLoss[block]
		except:
			return False
		
		return True
		
	def NextCycle(self):
		removeBlock = []
		for blkName in self.pendingDetectionLoss:
			self.pendingDetectionLoss[blkName][1] -= 1
			if self.pendingDetectionLoss[blkName][1] <= 0:
				# it's time to believe - process the detection loss and remove from this list
				obj = self.pendingDetectionLoss[blkName][0]
				# tr = obj.RemoveFromTrain()
				self.railroad.DetectionLoss(obj)

				removeBlock.append(blkName)
			
		for blkName in removeBlock:
			del(self.pendingDetectionLoss[blkName])


class PulseCounter:
	def __init__(self, vbyte, vbit, pct, plen, node):
		self.vbyte = vbyte
		self.vbit = vbit
		self.count = pct
		self.length = plen
		self.resetLength = plen
		self.node = node
		
	def tally(self):
		if self.length == 0:
			self.count -= 1
			if self.count == 0:
				return False
				
			self.length = self.resetLength
			sendBit = 1
		else:
			self.length -= 1
			sendBit = 0 if self.length == 0 else 1

		self.node.SetOutputBit(self.vbyte, self.vbit, sendBit)
		return True


