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
		
		self.addrList = []

		for dclass, name in self.districtList:
			logging.info("Creating District %s" % name)
			self.districts[name] = dclass(self, name, self.settings)
			self.nodes[name] = self.districts[name].GetNodes()
			self.addrList.extend([[addr, self.districts[name], node] for addr, node, in self.districts[name].GetNodes().items()])

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
		# self.loBlocks = j["blocks"]
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

		self.sigToOSMap = {}
		self.to2osMap = {}
		self.routes = {}
		for rtName, rt in self.loRoutes.items():
			osBlockName = rt["os"]
			if osBlockName in ["KOSN10S11", "KOSN20S21", "N60"]:
				continue
			toList = rt["turnouts"]
			sigList = rt["signals"]

			try:
				osBlock = self.osblocks[osBlockName]
			except KeyError:
				try:
					blk = self.blocks[osBlockName]
				except KeyError:
					blk = None

				osBlock = None if blk is None else OSBlock(osBlockName, blk)

				if osBlock is not None:
					self.osblocks[osBlockName] = osBlock

			if osBlock is None:
				continue

			for sn in sigList:
				z = re.match("([A-Za-z]+[0-9]+[A-Za-z])", sn)
				if z is None or len(z.groups()) < 1:
					continue
				lvr = z.groups()[0]
				if lvr in self.sigToOSMap:
					if osBlockName not in self.sigToOSMap[lvr]:
						self.sigToOSMap[lvr].append(osBlockName)
				else:
					self.sigToOSMap[lvr] = [osBlockName]

			for tn in [tout[0] for tout in toList]:
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

		ioBits = {
			"blocks": blist,
			"turnouts": tlist,
			"breakers": brklist,
			"routesin": rilist,
			"siglevers": sllist
		}
		fn = os.path.join(os.getcwd(), "data", "iobits.json")
		logging.info("Saving IO Bit information to file (%s)" % fn)
		try:
			with open(fn, "w") as jfp:
				json.dump(ioBits, jfp, indent=2)
		except Exception as e:
			logging.info("Error %s saving io bits file" % str(e))

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

		return True
			
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

	def SetOutPulseTo(self, toname, state):
		try:
			turnout = self.turnouts[toname]
		except KeyError:
			logging.warning("Attempt to change state on unknown turnout: %s" % toname)
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

	def SetAspect(self, signame, aspect, frozenaspect=None, callon=False, aspectType=None):
		try:
			sig = self.signals[signame]
		except KeyError:
			logging.warning("Ignoring set aspect - unknown signal name: %s" % signame)
			return

		sig.SetFrozenAspect(frozenaspect)		
		if aspectType is not None:
			sig.SetAspectType(aspectType)
			
		if aspect is not None:
			aspect = sig.district.VerifyAspect(signame, aspect)	
			if not sig.SetAspect(aspect):
				return 
			
			bits = sig.Bits()
			lb = len(bits)
			if lb == 0:	
				sig.district.SetAspect(sig, aspect)
			else:
				if lb == 1:
					vals = [1 if aspect != 0 else 0] 
				elif lb == 2:
					vals = [aspect & 0x02, aspect & 0x01] 
				elif lb == 3:
					vals = [aspect & 0x04, aspect & 0x02, aspect & 0x01] 
				else:
					logging.warning("Unknown bits length for signal %s: %d" % (sig.Name(), len(bits)))
					return
	
				for (vbyte, vbit), val in zip(bits, vals):
					sig.node.SetOutputBit(vbyte, vbit, 1 if val != 0 else 0)
	
			sig.UpdateIndicators() # make sure all indicators reflect this change
			self.UpdateSignalLeverLEDs(sig, aspect, callon)
			self.RailroadEvent(sig.GetEventMessage())
		
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
		sl.UpdateLed()
		
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
		
		if hs.Lock(state == 1):
			self.RailroadEvent(hs.GetEventMessage(lock=True))
			if not hs.UpdateIndicators():
				hs.District().SetHandswitch(hsnameKey, state)

	def SetSignalFleet(self, signame, flag):
		self.fleetedSignals[signame] = flag

	def SetOSRoute(self, blknm, rtname, ends, signals):
		self.osRoutes[blknm] = [rtname, ends, signals]
		print("OS Route: %s: Route %s  Turnouts: %s  Signals: %s" % (blknm, rtname, ends, signals))

	def GetOSRoutes(self):
		return self.osRoutes
		
	def SetControlOption(self, name, value):
		logging.debug("Setting control option for %s to %d" % (name, value))
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
			logging.debug("key error getting control option %s" % name)
			logging.debug("valid keys: %s" % str(list(self.controlOptions.keys())))
			return 0
		
	def SetBlockDirection(self, blknm, direction):
		try:
			blk = self.blocks[blknm]
		except KeyError:
			logging.warning("ignoring block direction - unknown block: %s" % blknm)
			return 
		
		if blk.SetDirection(direction == "E"):
			self.RailroadEvent(blk.GetEventMessage(direction=True))

	def SetBlockClear(self, blknm, clear):
		try:
			blk = self.blocks[blknm]
		except KeyError:
			logging.warning("ignoring block clear - unknown block: %s" % blknm)
			return 
		
		if blk.SetCleared(clear):
			self.RailroadEvent(blk.GetEventMessage(clear=True))
		
	def SetDistrictLock(self, name, value):
		self.districtLock[name] = value

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
	
	def AddHandswitch(self, name, district, node, address, bits):
		try:
			t = self.handswitches[name]
				
		except KeyError:
			# this is the normal scenario
			t = None
			
		if t is None:
			t = Handswitch(name, district, node, address)
		else:
			if t.IsNullHandswitch():
				t.SetHandswitchAddress(district, node, address)
			else:
				logging.warning("Potential duplicate handset: %s" % name)

		self.handswitches[name] = t		
		t.SetBits(bits)
		node.AddInputToMap(bits[0], [t, 'N'])
		node.AddInputToMap(bits[1], [t, 'R'])
		return t
					
	def AddHandswitchInd(self, name, district, node, address, bits, inverted=False):
		try:
			s = self.handswitches[name]
		except KeyError:
			s = Handswitch(name, None, None, None)
			self.handswitches[name] = s
			
		s.AddIndicator(district, node, address, bits, inverted)
		return s
					
	def AddHandswitchReverseInd(self, name, district, node, address, bits):
		try:
			s = self.handswitches[name]
		except KeyError:
			s = Handswitch(name, None, None, None)
			self.handswitches[name] = s
			
		s.AddReverseIndicator(district, node, address, bits)
		return s
					
	def AddHandswitchUnlock(self, name, district, node, address, bits):
		try:
			s = self.handswitches[name]
		except KeyError:
			s = Handswitch(name, None, None, None)
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
		for l in [self.blocks, self.turnouts]: #  #, self.signals, self.signalLevers, self.stopRelays]:
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
		#
		# for signm, flag in self.fleetedSignals.items():
		# 	m = {"fleet": [{ "name": signm, "value": flag}]}
		# 	yield m

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
				logging.debug("changed bit: %s(%s) %x %s %s %s" % (objName, objType, node.Address(), vbyte, vbit, newval))

				if objType == INPUT_BLOCK:
					if objName.split(".")[0] in self.ignoredBlocks:
						logging.info("Ignoring block %s as per ignore list" % objName)
					else:
						# if block has changed to occupied
						if newval != 0:
							# remove any pending detectio loss
							self.pendingDetectionLoss.Remove(objName)
							# and process the detection gain
							if obj.SetStatus("O"):
								self.RailroadEvent(obj.GetEventMessage())
								self.IdentifyTrain(obj)
								obj.UpdateIndicators()

						# otherwise, this is a detection loss - add it to pending, but only if we are currently occupied
						else:
							if obj.IsOccupied():
								self.pendingDetectionLoss.Add(objName, obj)
							else:
								if obj.SetStatus("E"):
									self.RailroadEvent(obj.GetEventMessage())
									obj.UpdateIndicators()

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
									msgs = self.UpdateRoutesForTurnout(obj)
									obj.UpdateLed()
									msgs.extend(obj.GetEventMessages())
									for m in msgs:
										self.RailroadEvent(m)
						else:
							if nflag == 1 and rflag == 0:
								if obj.SetNormal(True):
									msgs = self.UpdateRoutesForTurnout(obj)
									obj.UpdateLed()
									msgs.extend(obj.GetEventMessages())
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
						self.Alert(district.ControlRestricted())

				elif objType == INPUT_HANDSWITCH:
					dataType = objparms[1]
					if dataType == "L":
						objnm = obj.Name()
						if objnm in [ "CSw21ab", "PBSw15ab" ]:
							if objnm not in skiplist:
								if obj.Lock(newval != 0):
									obj.UpdateIndicators()
								unlock = obj.GetUnlock()
								if unlock:
									district, node, addr, bits = unlock
									district.SetHandswitchIn(obj, newval)
						else:
							if objnm not in skiplist:
								unlock = obj.GetUnlock()
								if unlock:
									district, node, addr, bits = unlock
									uflag = node.GetInputBit(bits[0][0], bits[0][1])
									if obj.Lock(uflag != 0):
										self.RailroadEvent(obj.GetEventMessage(lock=True))
										obj.UpdateIndicators()
					
					else:
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
						if osName is not None:
							msgs = self.UpdateRoutesForOS(osName)
							for m in msgs:
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
							if obj.Lock(uflag == 1):
								if olist is None:
									self.RailroadEvent(obj.GetEventMessage(lock=True))
								else:
									for obn in olist:
										obj2 = self.handswitches[obn]
										obj2.Lock(uflag == 1)
										self.RailroadEvent(obj2.GetEventMessage(lock=True))
					
				else:
					bt = obj.Bits()
					if len(bt) > 0:
						rbit, cbit, lbit = obj.node.GetInputBits(bt)
						if obj.SetLeverState(rbit, cbit, lbit):
							self.RailroadEvent(obj.GetEventMessage())
							obj.UpdateLed()

	def RailroadEvents(self, elist):
		for e in elist:
			self.cbEvent(e)

	def RailroadEvent(self, event):
		self.cbEvent(event)

	def Alert(self, msg):
		self.RailroadEvent({"alert": {"msg": msg}})

	def Advice(self, msg):
		self.RailroadEvent({"advice": {"msg": msg}})

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
		locker = osName if turnout is None else turnout
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
							result.append({"lockturnout": [{"name": sw, "lock": flag, "locker": locker}]})

		return result

	def ProcessSignalLever(self, obj, node):
		objName = obj.Name()
		logging.debug("in process sig lever")
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
					aspectL, msgsL = self.ProcessSignalLeverSide(objName, left, cbit, "L")
					if objName not in self.lastValues:
						self.lastValues[objName] = [left, 0]
					else:
						self.lastValues[objName][0] = left

				if right != currentBits[1]:
					aspectR, msgsR = self.ProcessSignalLeverSide(objName, right, cbit, "R")
					if objName not in self.lastValues:
						self.lastValues[objName] = [0, right]
					else:
						self.lastValues[objName][1] = right

				obj.UpdateLed(aspectR, aspectL)

				for m in msgsL+msgsR:
					self.RailroadEvent(m)

	def ProcessSignalLeverSide(self, leverName, bit, callon, LR):
		msgs = []
		sigBaseNm = leverName + LR
		osList = self.sigToOSMap.get(sigBaseNm, None)

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
			self.Alert("Unable to determine signal for lever %s" % sigBaseNm)
			return None
		else:
			osblk = self.osblocks[osName]
			rtName = osblk.ActiveRouteName()
			if rtName is None:
				self.Alert("No Route Available for signal %s" % sigBaseNm)
				logging.debug("no active route for os %s - not setting signal %s" % (osName, leverName))
				return None, []

			sig = self.signals.get(sigMatch, None)

			if sig is not None:
				try:
					if self.CalculateAspect(sig, osName, bit, callon):
						msgs = [m for m in sig.GetEventMessages()]
				except Exception as e:
					logging.warning("Exception %s in calc aspect %s" % (str(e), sigMatch))

				aspect = sig.Aspect()
				logging.debug("calculated aspect for %s = %d" % (sigMatch, aspect))
			else:
				aspect = 0

			return aspect, msgs

	def CalculateAspect(self, sig, osName, bit, callon, silent=False):
		osblk = self.osblocks[osName]
		blk = osblk.Block()
		rtName = osblk.ActiveRouteName()
		rt = osblk.ActiveRoute()

		if sig is None or rtName is None:
			logging.error("unable to calculate aspect because signal(%s) and/or route(%s) or both is None" % (str(sig), str(rtName)))
			return False

		logging.debug(
			"Calculating aspect for os %s/%s signal %s route %s bit %d" % (osblk.Name(), blk.Name(), sig.Name(), rtName, bit))

		if blk.IsOccupied():
			if not silent:
				self.Alert("Block %s is busy" % osblk.RouteDesignator())
			logging.debug("Unable to calculate aspect: OS Block is busy")
			return False

		currentDirection = sig.East()
		if bit != 0 and currentDirection != osblk.IsEast() and osblk.IsCleared():
			if not silent:
				self.Alert("Block %s is cleared in opposite direction" % osblk.RouteDesignator())
			logging.debug("Unable to calculate aspect: Block %s is cleared in opposite direction" % osblk.Name())
			return False

		exitBlk = rt.GetExitBlock(reverse=currentDirection != blk.IsEast())
		rType = rt.GetRouteType(reverse=currentDirection != blk.IsEast())

		if exitBlk.IsOccupied():
			if not silent:
				self.Alert("Block %s is busy" % exitBlk.RouteDesignator())
			logging.debug("Unable to calculate aspect: Block %s is busy" % exitBlk.Name())
			return False

		if CrossingEastWestBoundary(osblk, exitBlk):
			logging.debug("we crossed a EW boundary between %s and %s" % (osblk, exitBlk))
			currentDirection = not currentDirection

		if bit != 0:
			if exitBlk.IsCleared():
				if exitBlk.East() != currentDirection:
					if not silent or True:
						self.Alert("Block %s is cleared in opposite direction" % exitBlk.RouteDesignator())
					logging.debug("Unable to calculate aspect: Block %s cleared in opposite direction" % exitBlk.Name())
					return False

		#
		# if exitBlk.AreHandSwitchesSet() and not self.frame.sidingsUnlocked:
		# 	if not silent:
		# 		self.frame.PopupEvent("Block %s is locked" % exitBlk.GetRouteDesignator())
		# 	logging.debug("Unable to calculate aspect: Block %s is locked" % exitBlkNm)
		# 	return None
		#
		# nb = exitBlk.NextBlock(reverse=currentDirection != exitBlk.GetEast())
		# if nb:
		# 	nbName = nb.GetName()
		# 	if CrossingEastWestBoundary(nb, exitBlk):
		# 		currentDirection = not currentDirection
		#
		# 	nbStatus = nb.GetStatus()
		# 	nbRType = nb.GetRouteType(reverse=currentDirection != nb.GetEast())
		# 	nbRtName = nb.GetRouteName()
		# 	# try to go one more block, skipping past an OS block
		#
		# 	nxbNm = nb.GetExitBlock(reverse=currentDirection != nb.GetEast())
		# 	if nxbNm is None:
		# 		nnb = None
		# 	else:
		# 		try:
		# 			nxb = self.frame.blocks[nxbNm]
		# 		except (KeyError, IndexError):
		# 			nxb = None
		# 		if nxb:
		# 			if CrossingEastWestBoundary(nb, nxb):
		# 				currentDirection = not currentDirection
		# 			nnb = nxb.NextBlock(reverse=currentDirection != nxb.GetEast())
		# 		else:
		# 			nnb = None
		#
		# 	if nnb:
		# 		nnbClear = nnb.GetStatus() == CLEARED
		# 		nnbName = nnb.GetName()
		# 	else:
		# 		nnbClear = False
		# 		nnbName = None
		# else:
		# 	nxbNm = None
		# 	nbStatus = None
		# 	nbName = None
		# 	nbRType = None
		# 	nbRtName = None
		# 	nnbClear = False
		# 	nnbName = None
		#
		# aType = sig.GetAspectType()
		# aspect = self.GetAspect(aType, rType, nbStatus, nbRType, nnbClear)
		#
		# if self.dbg.showaspectcalculation:
		# 	self.frame.DebugMessage("======== New aspect calculation ========")
		# 	self.frame.DebugMessage("OS: %s Route: %s  Sig: %s" % (osblk.GetName(), rt.GetName(), sig.GetName()))
		# 	self.frame.DebugMessage("exit block name = %s   RT: %s" % (exitBlkNm, routetype(rType)))
		# 	self.frame.DebugMessage("NB: %s Status: %s  NRT: %s" % (nbName, statusname(nbStatus), routetype(nbRType)))
		# 	self.frame.DebugMessage("Next route = %s" % nbRtName)
		# 	self.frame.DebugMessage("next exit block = %s" % nxbNm)
		# 	self.frame.DebugMessage("NNB: %s  NNBC: %s" % (nnbName, nnbClear))
		# 	self.frame.DebugMessage("Aspect = %s (%x)" % (aspectname(aspect, aType), aspect))
		#
		# logging.debug(
		# 	"Calculated aspect = %s   aspect type = %s route type = %s next block status = %s next block route type = %s next next block clear = %s" %
		# 	(aspectname(aspect, aType), aspecttype(aType), routetype(rType), statusname(nbStatus), routetype(nbRType),
		# 	 nnbClear))
		#
		# # self.CheckBlockSignals(sig, aspect, exitBlk, doReverseExit, rType, nbStatus, nbRType, nnbClear)
		#
		# return aspect

		sig.SetAspect(bit)
		if bit == 0:
			if not exitBlk.IsOccupied():
				exitBlk.SetStatus("E")
				exitBlk.Reset()
			if not osblk.IsOccupied():
				osblk.SetStatus("E")
				osblk.Reset()
		else:
			exitBlk.SetEast(currentDirection)
			osblk.SetEast(currentDirection)
			exitBlk.SetStatus("C")
			osblk.SetStatus("C")

		self.RailroadEvents(exitBlk.GetEventMessages())
		self.RailroadEvents(osblk.Block().GetEventMessages())

		logging.debug("end of CA =======================================================")

		return True

	def IdentifyTrain(self, blk):
		logging.debug("identify train in block %s" % blk.Name())


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
				if obj.SetStatus("E"):
					self.railroad.RailroadEvent(obj.GetEventMessage())
					obj.UpdateIndicators()

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


