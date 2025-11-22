import logging
import re
import os
import json
from datetime import datetime
from os import listdir
from os.path import isfile, join

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
	INPUT_HANDSWITCH, INPUT_ROUTEIN, nodeNames, CrossingEastWestBoundary

from rrserver.rrobjects import Block, OSBlock, Route, StopRelay, Signal, SignalLever, RouteIn, Turnout, \
			OutNXButton, Handswitch, Breaker, Indicator, ODevice, Lock

from dispatcher.constants import RegAspects, RegSloAspects, AdvAspects, SloAspects, \
	MAIN, SLOW, DIVERGING, RESTRICTING, \
	CLEARED, OCCUPIED, STOP, OVERSWITCH, \
	restrictedaspect, routetype, statusname, aspectname, aspecttype


def GetSnapList():
	folder = os.path.join(os.getcwd(), "data", "snapshots")
	return sorted([f for f in listdir(folder) if isfile(join(folder, f))])


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

		self.breakerCycleDelay = 10  # how many cycles to wait before recording breaker trips

		self.addrList = []

		self.snapshotLimit = 5

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

		self.RecordBreakerTrip(None)  # create a new empty breaker trip report file

		# self.AuditRoutes()

	# def AuditRoutes(self):
	# 	for osblknm, osblk in self.osblocks.items():
	# 		east = osblk.East()
	# 		logging.debug("==========================================")
	# 		logging.debug("determine initial route for OS %s(%s)" % (osblknm, east))
	# 		ar = osblk.ActiveRoute()
	# 		if ar is None:
	# 			logging.debug("  OS %s - NO active route.  Potential routes:")
	# 			for rt in osblk.Routes():
	# 				logging.debug("    %s" % str(rt))
	# 		else:
	# 			logging.debug("  Active Route: %s" % osblk.ActiveRouteName())
	# 			for ep in ar.EndPoints():
	# 				if ep is None:
	# 					logging.debug("    End point is NONE")
	# 				else:
	# 					epeast = ep.East()
	# 					logging.debug("    End point: %s(%s)" % (ep.Name(), epeast))
	# 					nbe = ep.NextBlock(False)
	# 					nben = "None" if nbe is None else nbe.Name()
	# 					nbw = ep.NextBlock(True)
	# 					nbwn = "None" if nbw is None else nbw.Name()
	# 					logging.debug("      nbe: %s" % nben)
	# 					logging.debug("      nbw: %s" % nbwn)
	# 					if osblknm not in [nben, nbwn]:
	# 						logging.debug("Block %s does not point back to the proper OS %s  <==============================" % (ep.Name(), osblknm))
	#
	# def SetDebugFlag(self,	showaspectcalculation = False, blockoccupancy = False, identifytrain = False):
	# 	self.debug.showaspectcalculation = showaspectcalculation
	# 	self.debug.blockoccupancy = blockoccupancy
	# 	self.debug.identifytrain = identifytrain

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

	def SetSnapshotLimit(self, limit):
		self.snapshotLimit = limit

	def LoadSnapshot(self, fn):
		snapList = GetSnapList()
		if len(snapList) == 0:
			logging.info("No snapshot files to load - skipping")
			return

		if fn is None:
			snapFile = snapList[-1]
		elif fn in snapList:
			snapFile = fn
		else:
			logging.error("Unknown snapshot file: %s - skipping" % fn)
			return

		fn = os.path.join(os.getcwd(), "data", "snapshots", snapFile)

		try:
			with open(fn, "r") as jfp:
				j = json.load(jfp)
		except FileNotFoundError:
			logging.info("Snapshot file %s not found" % fn)
			return

		except Exception as e:
			logging.info("Unknown error loading snapshot %s - %s" % (fn, str(e)))
			return

		jstr = json.dumps(j, indent=2)

		trainsFound = {}
		for trid, trinfo in j.items():
			firstBlock = True
			for bn in trinfo["blocks"]:
				blk = self.GetBlock(bn)
				if blk is None:
					self.Alert("Train %s from snapshot, block %s unknown" % (trid, bn))
				elif not blk.IsOccupied():
					self.Alert("Train %s from snapshot, block %s is unoccupied" % (trid, bn))
				else:
					tr = blk.Train()
					# this is OK - found a block with the correct train
					if firstBlock:
						# change the train's name unless it's still using the internal name
						if trid != tr.IName():
							tr.SetName(trid, self.GetTrainRoster(trid))
						else:
							# assert no roster if we are still using internal name
							tr.SetRoster(None)
						tr.SetLoco(trinfo["loco"])
						tr.SetEast(trinfo["east"])
						firstBlock = False

					if tr.Name() != trid:
						self.Alert("Train in block %s is in a different train: %s != %s" % (bn, trid, tr.Name()))
					else:
						if tr.IName() not in trainsFound:
							trainsFound[tr.IName()] = tr

		for tr in trainsFound.values():
			self.RailroadEvent(tr.GetEventMessage())

	def SaveSnapshot(self):
		tlist = self.GetActiveTrainList()
		if len(tlist) == 0:
			return "No trains - snapshot not saved"

		logging.debug("Railroad save snapshot")
		folder = os.path.join(os.getcwd(), "data", "snapshots")
		os.makedirs(folder, exist_ok=True)
		n = datetime.now()
		ts = "%4d%02d%02d-%02d%02d%02d" % (n.year, n.month, n.day, n.hour, n.minute, n.second)
		filename = "snapshot" + ts + ".json"
		fn = os.path.join(folder, filename)

		trains = {}
		for trid, trinfo in tlist.items():
			trains[trid] = {
				"name": trid,
				"loco": trinfo["loco"],
				"east": trinfo["east"],
				"blocks": trinfo["blocks"],
			}
		with open(fn, "w") as jfp:
			json.dump(trains, jfp, indent=2)

		#  get rid of excess versions of the snapshot files
		snapList = sorted([f for f in listdir(folder) if isfile(join(folder, f))])
		if len(snapList) > self.snapshotLimit:
			dellist = snapList[:(len(snapList) - self.snapshotLimit)]
			for fn in dellist:
				fqn = os.path.join(folder, fn)
				os.unlink(fqn)

		return "Snapshot saved to file %s" % filename

	def DelayedStartup(self):
		for d in self.districts.values():
			d.DelayedStartup()

	def DumpN20(self):
		return self.blocks["N20"].GetStatus()
	#
	# def OccupyBlock(self, blknm, state):
	# 	'''
	# 	this method is solely for simulation - to set a block as occupied or not
	# 	'''
	# 	try:
	# 		blist = [ self.blocks[blknm] ]
	# 	except KeyError:
	# 		try:
	# 			blist = [self.GetBlock(x) for x in self.subBlocks[blknm]]
	# 		except KeyError:
	# 			logging.warning("Ignoring occupy command - unknown block name: %s" % blknm)
	# 			return
	#
	# 	newstate = 1 if state != 0 else 0
	# 	for blk in blist:
	# 		if len(blk.Bits()) > 0:
	# 			vbyte, vbit = blk.Bits()[0]
	# 			blk.node.SetInputBit(vbyte, vbit, newstate)
	# 		else:
	# 			'''
	# 			block has sub blocks - occupy all of them as per state
	# 			'''
	# 			sbl = blk.SubBlocks()
	# 			for sb in sbl:
	# 				if len(sb.Bits()) > 0:
	# 					vbyte, vbit = sb.Bits()[0]
	# 					sb.node.SetInputBit(vbyte, vbit, newstate)
	#
	# def SetTurnoutPos(self, tonm, normal):
	# 	'''
	# 	this method is for simulation - to set a turnout to normal or reverse position - this is also used for handswitches
	# 	'''
	# 	try:
	# 		tout = self.turnouts[tonm]
	# 	except KeyError:
	# 		try:
	# 			tout = self.handswitches[tonm]
	#
	# 		except KeyError:
	# 			logging.warning("Ignoring turnoutpos command - unknown turnoutname: %s" % tonm)
	# 			return
	#
	# 	pos = tout.Position()
	# 	if pos is None:
	# 		logging.warning("Turnout definition does not have position - ignoring turnoutpos command")
	# 		return
	#
	# 	bits, district, node, addr = pos
	# 	node.SetInputBit(bits[0][0], bits[0][1], 1 if normal else 0)
	# 	node.SetInputBit(bits[1][0], bits[1][1], 0 if normal else 1)
	#
	# def SetBreaker(self, brkrnm, state):
	# 	'''
	# 	this method is solely for simulation - to set a breaker as on or not
	# 	'''
	# 	try:
	# 		brkr = self.breakers[brkrnm]
	# 	except KeyError:
	# 		logging.warning("Ignoring breaker command - unknown breaker name: %s" % brkrnm)
	# 		return
	#
	# 	try:
	# 		vbyte, vbit = brkr.Bits()[0]
	# 	except IndexError:
	# 		logging.warning("Breaker definition incomplete - ignoring breaker command")
	# 		return
	#
	# 	brkr.node.SetInputBit(vbyte, vbit, 1 if state == 0 else 0)
		
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
			return False

		# rc indicates whether or not the value was changed
		rc = r.IsActivated() != (state != 0)

		bits = r.Bits()
		if len(bits) > 0:		
			vbyte, vbit = bits[0]
			r.node.SetOutputBit(vbyte, vbit, 1 if state != 0 else 0)
			r.Activate(state != 0)

		return rc

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

	def GetTrainRoster(self, trid):
		return self.trainRoster.get(trid, None)
		
	def ClearAllRoutes(self, rtList):
		for rtenm in rtList:
			rte = self.routesIn[rtenm]
			bt = rte.Bits()
			rte.node.SetInputBit(bt[0][0], bt[0][1], 0)

	def SignalClick(self, signm, callon=False):
		try:
			sig = self.signals[signm]
		except KeyError:
			logging.error("Unknown signal: %s" % signm)
			return

		district = sig.District()
		if not district.SignalClick(sig, callon):
			return

		currentAspect = sig.Aspect()

		if sig.District().ControlRestrictedSignal(signm):
			self.Alert(sig.District().ControlRestrictedMessage())
			return

		osName = self.DetermineSignalOS(signm)
		if osName is None:
			return

		msgs = []
		moving = currentAspect != 0  # Are we requesting a stop signal?
		try:
			aspect = self.CalculateAspect(sig, osName, moving, callon, None, silent=False)
			if aspect is None:
				return

		except Exception as e:
			logging.warning("Exception %s in calc aspect %s" % (str(e), signm))
			return

		msgs.extend(self.ApplyAspect(aspect, sig, osName, callon))
		msgs.extend(sig.GetEventMessages())
		for m in msgs:
			self.RailroadEvent(m)

		district.EvaluateDistrictLocks(sig, None)
		self.EvaluatePreviousSignals(sig)

		# find the train that this signal controls and update it with the new aspect
		tr = sig.Train()
		if tr is not None:
			tr.SetAspect(sig.Aspect(), sig.AspectType())
			self.RailroadEvent((tr.GetEventMessage()))

		# finally, check if this signal triggers or clears a stopping relay
		if signm not in self.sigToSbMap:
			logging.info("Signal does not control stopping block")
		else:
			blk, east = self.sigToSbMap[signm]
			sbName = blk.Name() + (".E" if east else ".W")
			sb = self.blocks[sbName]
			relayName = blk.Name() + ".srel"
			tr = sb.Train()
			if sb.IsOccupied() and aspect == 0:
				if tr is not None:
					tr.SetStopped(True)
					self.RailroadEvent((tr.GetEventMessage()))
				self.SetRelay(relayName, 1)
			else:
				self.SetRelay(relayName, 0)
				if tr is not None:
					tr.SetStopped(False)
					self.RailroadEvent((tr.GetEventMessage()))

	def DetermineSignalOS(self, signm):
		osList = (self.sigToOSMap[signm])
		for osblk in osList:
			osName = osblk.Name()

			activeRoute = osblk.ActiveRoute()
			if activeRoute is not None and activeRoute.HasSignal(signm):
				return osName
		else:
			self.Alert("No available route for signal %s" % signm)
			return None

	def TurnoutClick(self, toname, status):
		tout = self.turnouts.get(toname, None)
		if tout is None:
			return

		if tout.IsLocked() or tout.IsDisabled():
			self.Alert("Turnout %s is locked (%s)" % (toname, str(tout.Lockers())))
			return

		self.SetOutPulseTo(toname, status)

	def SetOutPulseTo(self, toname, state):
		try:
			turnout = self.turnouts[toname]
		except KeyError:
			logging.error("Unknown turnout: %s" % toname)
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

	def SetBlockClear(self, blknm, clear):
		try:
			blk = self.blocks[blknm]
		except KeyError:
			logging.warning("ignoring block clear - unknown block: %s" % blknm)
			return

		blk.SetCleared(clear)

	def SetDistrictLock(self, name, value):
		if self.districtLock[name] == value:
			return False

		self.districtLock[name] = value
		msg = {"districtlock": {name: value}}
		self.RailroadEvent(msg)
		return True

	def FindRoute(self, sig):
		signm = sig.Name()
		for osblknm, osblk in self.osblocks.items():
			ar = osblk.ActiveRoute()
			if ar is None:
				continue

			if signm in ar.signals:
				rname = osblk.ActiveRouteName()

				rt = self.routes[rname]
				return rt, osblk

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

		# finally, send the trains
		for tr in self.trains.values():
			m = tr.GetEventMessage()
			if m is not None:
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

	def GetOSBlock(self, osnm):
		try:
			return self.osblocks[osnm]
		except KeyError:
			return None

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

	def GetTurnoutLocks(self):
		result = {}
		for trnm, trn in self.turnouts.items():
			if trn.IsLocked():
				result[trnm] = trn.Lockers()

		return result

	def ClearTurnoutLocks(self, tnlist):
		for tn in tnlist:
			try:
				trn = self.turnouts[tn]
			except KeyError:
				logging.debug("Ignoring request to clear lock on unknown turnlout: %s" % tn)
				trn = None

			if trn is not None:
				trn.ClearLock()
				self.RailroadEvent({"lockturnout": [{"name": tn, "lock": False}]})

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

	def AddPendingFleetAction(self, blknm, sig, osBlk, rte):
		self.PendingFleetActions[blknm] = [sig, osBlk, rte]

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

		if self.breakerCycleDelay > 0:
			self.breakerCycleDelay -= 1

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
					self.RecordBreakerTrip(obj)
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
		if self.settings.debug.blockoccupancy:
			self.Alert("Input block change: %s:%s" % (objName, newval))

		if objName.split(".")[0] in self.ignoredBlocks:
			if self.settings.debug.blockoccupancy:
				self.Alert("Ignoring block %s as per ignore list" % objName)
			return

		if newval != 0:  # if block has changed to occupied
			# remove any pending detection loss
			self.pendingDetectionLoss.Remove(objName)

			passSignal = False
			if obj.IsOS():
				# we've entered an OS block - turn the entry signal back to red and record the signal aspect and exit
				# for future fleeting if fleeting is enabled for the signal
				if self.settings.debug.blockoccupancy:
					self.Alert("This is an OS block - determine any necessary fleet action")
				rte = obj.OS().ActiveRoute()
				if rte is not None:
					sigEnt = rte.EntrySignal()
					sig = self.signals.get(sigEnt, None)
					blkExit = rte.ExitBlock()
					exbn = "None" if blkExit is None else blkExit.Name()

					if sig is not None and blkExit is not None and sig.Aspect() != 0 and sig.Fleeted():
						if self.settings.debug.blockoccupancy:
							self.Alert("Pending fleet action: %s %s %s" % (sigEnt, obj.OS().Name(), obj.OS().ActiveRouteName()))
						self.AddPendingFleetAction(exbn, sig, obj.OS(), obj.OS().ActiveRouteName())

					if sig is not None:
						passSignal = True  # the train has passed the signal - ignore subsequent aspect changes
						sig.SetAspect(0)
						obj.OS().LockRoute(False, sig.Name())
						self.RailroadEvent((sig.GetEventMessage()))

			if self.settings.debug.blockoccupancy:
				self.Alert("Block: %s is subblock: %s main has train: %s" % (objName, obj.IsSubBlock(), obj.MainHasTrain()))

			if obj.IsSubBlock() and obj.MainHasTrain():
				tr = obj.MainBlockTrain()
				obj.SetTrain(tr)
				obj.SetStatus(obj.MainBlockStatus())
				obj.SetEast(tr.IsEast())
				return

			# see if there are any district-specific tasks to do
			district.BlockOccupancyChange(self, obj, 1)

			obj.SetStatus("U")  # Mark the block as occupied unonown and then try to identify the train
			tr, rear = self.IdentifyTrain(obj)
			if self.settings.debug.blockoccupancy:
				self.Alert("Identified train as %s" % tr.Name())

			if tr.IsIdentified():  # if it's a train we know - change status to Occupied
				obj.SetStatus("O")
				if self.settings.debug.blockoccupancy:
					self.Alert("This train is known - status set to occupied")
				obj.SetEast(tr.IsEast())  # blocks take on the direction of known trains
			else:
				tr.SetEast(obj.IsEast())  # unknown trains take on the block direction
			tr.AddBlock(obj, rear)
			if not rear and passSignal:
				tr.PassSignal()  # Mark the train as having passed its signal
			obj.SetTrain(tr)

			if obj.OS() is None:  # this is NOT an OS we moved into - see if there is a new signal
				if not rear:  # if we're movng forward, determine the trains controlling signal
					sig = self.DetermineTrainSignal(tr, obj)
					if sig is not None:
						tr.SetSignal(sig)

			self.RailroadEvent(obj.GetEventMessage())
			self.RailroadEvent(tr.GetEventMessage())

			# now lock the active route's turnouts on behalf of the train
			if obj.OS() is not None:
				locks = obj.OS().LockRoute(True, tr.IName())
				for sw, flag in locks:
					self.RailroadEvent({"lockturnout": [{"name": sw.Name(), "lock": flag}]})

			obj.UpdateIndicators()

			self.CheckStoppingSection(tr)

		# otherwise, this is a detection loss - add it to pending, but only if we are currently occupied
		else:
			if obj.IsOccupied():
				if self.settings.debug.blockoccupancy:
					self.Alert("Recording pending detection loss for block %s" % objName)
				self.pendingDetectionLoss.Add(district, objName, obj)
			else:
				self.DetectionLoss(district, obj)

	def DetermineTrainSignal(self, tr, blk):
		if blk.IsOS():
			ar = blk.OS().ActiveRoute()
			if ar is None:
				logging.debug("OS %s has no active route" % blk.Name())
				return None
			sigNm = ar.EntrySignal()
			sig = self.signals.get(sigNm, None)
			if sig is None:
				logging.debug("Unable to identify signal")
			return sig

		else:
			nb = blk.NextBlock()
			if nb is None:
				logging.info("Moving into a terminal track - no signal here")
				return None
			if not nb.IsOS():
				logging.debug("Block %s should have been an OS" % nb.Name())
				return None
			ar = nb.OS().ActiveRoute()
			if ar is None:
				logging.debug("OS %s has no active route" % nb.Name())
				return None
			sigNm = ar.EntrySignal()
			sig = self.signals.get(sigNm, None)
			if sig is None:
				logging.debug("Unable to identify signal")
			return sig

	def CheckStoppingSection(self, tr):
		if tr.BlockCount() < 1:
			return
		blocks = [b for b in list(reversed(tr.Blocks()))]
		bnList = [b.Name() for b in blocks]
		blkNm = bnList[0]
		blk = blocks[0]

		baseName = None

		if blkNm.endswith(".E") or blkNm.endswith(".W"):
			east = blkNm.endswith(".E")
			if east == blk.IsEast():
				blockend = blkNm[-1]
				block = blkNm[:-2]
				baseName = block
				occupied = blk.IsOccupied()
				try:
					sigw, sige = self.sbToSigMap[block]
				except KeyError:
					sigw = None
					sige = None

				sig = sige if east else sigw
				if sig is not None:
					srName = block + ".srel"
					if sig.Aspect() == 0:
						if tr is not None:
							tr.SetStopped(occupied)
							self.RailroadEvent(tr.GetEventMessage())
						rc = self.SetRelay(srName, 1 if occupied else 0)
						if rc and occupied:
							self.Alert("Stop Relay Activated: %s at signal %s, %s Train %s" %
									(blkNm, sig.Name(), "Eastbound" if tr.IsEast() else "Westbound", tr.Name()))
					else:
						if tr is not None:
							tr.SetStopped(False)
							self.RailroadEvent(tr.GetEventMessage())
						self.SetRelay(srName, 0)
		else:
			tr.SetStopped(False)
			self.RailroadEvent(tr.GetEventMessage())

		# now step through the train, turning off any stopping blocks we encounter
		for blkNm, blk in zip(bnList[1:], blocks[1:]):
			if blkNm.endswith(".E") or blkNm.endswith(".W"):
				block = blkNm[:-2]
				# turn not turn off a stopping section for the same block that we turned it on for above
				if block != baseName:
					srName = block + ".srel"
					self.SetRelay(srName, 0)

	# def CheckShoreTunnelSignals(self, obj, objName):
	# 	exbn = obj.MainBlockName()
	# 	# exitBlk = self.blocks[exbn]
	# 	#
	# 	if objName == "S11.E" and not obj.IsEast():
	# 		sig = self.signals["N10W"]
	# 		osName = self.DetermineSignalOS("N10W")
	# 		osBlk = self.osblocks[osName]
	# 		if sig.Aspect() != 0 and sig.Fleeted():
	# 			self.PendingFleetActions[exbn] = [sig, osBlk, None]
	# 			sig.SetAspect(0)
	# 			self.RailroadEvent((sig.GetEventMessage()))
	#
	# 	elif objName == "S21.E" and not obj.IsEast():
	# 		sig = self.signals["N20W"]
	# 		osName = self.DetermineSignalOS("N20W")
	# 		osBlk = self.osblocks[osName]
	# 		if sig.Aspect() != 0 and sig.Fleeted():
	# 			self.PendingFleetActions[exbn] = [sig, osBlk, None]
	# 			sig.SetAspect(0)
	# 			self.RailroadEvent((sig.GetEventMessage()))
	#
	# 	elif objName == "N10.W" and obj.IsEast():
	# 		sig = self.signals["S11E"]
	# 		osName = self.DetermineSignalOS("S11E")
	# 		osBlk = self.osblocks[osName]
	# 		if sig.Aspect() != 0 and sig.Fleeted():
	# 			self.PendingFleetActions[exbn] = [sig, osBlk, None]
	# 			sig.SetAspect(0)
	# 			self.RailroadEvent((sig.GetEventMessage()))
	#
	# 	elif objName == "N20.W" and obj.IsEast():
	# 		sig = self.signals["S21E"]
	# 		osName = self.DetermineSignalOS("S21E")
	# 		osBlk = self.osblocks[osName]
	# 		if sig.Aspect() != 0 and sig.Fleeted():
	# 			self.PendingFleetActions[exbn] = [sig, osBlk, None]
	# 			sig.SetAspect(0)
	# 			self.RailroadEvent((sig.GetEventMessage()))
	#
	def DetectionLoss(self, district, obj):
		if self.settings.debug.blockoccupancy:
			self.Alert("detection loss: %s" % obj.Name())
		tr = obj.RemoveFromTrain()
		if tr is None: # this only happens on the initial out/in exchange
			return

		district.BlockOccupancyChange(self, obj, 0)

		if obj.SetStatus("E"):
			if self.settings.debug.blockoccupancy:
				self.Alert("Block marked as empty")
			self.RailroadEvent(obj.GetEventMessage())
			if tr is not None:
				self.RailroadEvent(tr.GetEventMessage())

				if len(tr.Blocks()) == 0:
					if self.settings.debug.blockoccupancy:
						self.Alert("Train now has no blocks - deleting")
					self.DeleteTrain(tr)

			obj.UpdateIndicators()
			self.CheckFleetTriggers(obj)

			objName = obj.Name()
			self.CheckStoppingSection(tr)

			# now unlock the active route's turnouts on behalf of the train
			if obj.OS() is not None and tr is not None:
				locks = obj.OS().LockRoute(False, tr.IName())
				for sw, flag in locks:
					self.RailroadEvent({"lockturnout": [{"name": sw.Name(), "lock": flag}]})

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

	def ReverseTrain(self, iname):
		tr = self.trains.get(iname, None)
		if tr is None:
			logging.debug("Attempt to reverse unknown train: %s" % iname)
			return

		if tr.BlockCount() == 0:
			logging.error("Train %s has 0 blocks" % tr.Name())
			return

		# deactivate any stopping relay that this train curfrently has triggerred
		firstBlock = tr.Blocks()[-1]
		bn = firstBlock.Name()
		if bn.endswith(".E") or bn.endswith(".W"):
			srName = bn[:-2] + ".srel"
			self.SetRelay(srName, 0)
			logging.debug("Stopping relay %s deactivated" % srName)

		nd = not tr.East()
		tr.SetEast(nd)

		# now reverse the block ordering, and then reverse each block
		tr.ReverseBlocks()
		bl = tr.Blocks()
		msgs = []
		for b in bl:
			b.SetEast(nd)
			msgs.append(b.GetEventMessage())

		firstBlock = tr.Blocks()[0]
		sig = self.DetermineTrainSignal(tr, firstBlock)
		tr.SetSignal(sig)

		self.CheckStoppingSection(tr)

		msgs.append(tr.GetEventMessage())

		for m in msgs:
			self.RailroadEvent(m)

	def ReorderTrain(self, iname, blocks):
		tr = self.trains.get(iname, None)
		if tr is None:
			logging.error("Attempt to reorder unknown train: %s" % iname)
			return

		if tr.BlockCount() == 0:
			logging.error("Train %s has 0 blocks" % tr.Name())
			return

		# deactivate any stopping relay that this train curfrently has triggerred
		firstBlock = tr.Blocks()[-1]
		bn = firstBlock.Name()
		if bn.endswith(".E") or bn.endswith(".W"):
			srName = bn[:-2] + ".srel"
			self.SetRelay(srName, 0)
			logging.debug("Stopping relay %s deactivated" % srName)

		# build a dictionary of the current blocks
		blockMap = {}
		for blk in tr.Blocks():
			blockMap[blk.Name()] = blk

		tr.ClearBlocks()
		for bn in blocks:
			blk = blockMap.get(bn, None)
			if blk is None:
				self.Alert("Block %s is not currently in the train - ignoring")
			else:
				tr.AddBlock(blockMap[bn], False)

		firstBlock = tr.Blocks()[0]
		sig = self.DetermineTrainSignal(tr, firstBlock)
		tr.SetSignal(sig)

		self.CheckStoppingSection(tr)

		self.RailroadEvent(tr.GetEventMessage())

	def SplitTrain(self, iname, blocks):
		if self.settings.debug.blockoccupancy:
			self.Alert("Got split train %s: %s" % (iname, ", ".join(blocks)))
		tr = self.trains.get(iname, None)
		if tr is None:
			logging.error("attempt to split unknown train: %s" % iname)
			return

		if tr.BlockCount() <= 1:
			logging.error("Train %s has too few blocks (%d) to split" % (tr.Name(), tr.BlockCount()))
			return

		# deactivate any stopping relay that this train curfrently has triggerred
		firstBlock = tr.Blocks()[-1]
		bn = firstBlock.Name()
		if bn.endswith(".E") or bn.endswith(".W"):
			srName = bn[:-2] + ".srel"
			self.SetRelay(srName, 0)
			if self.settings.debug.blockoccupancy:
				self.Alert("Stopping relay %s deactivated" % srName)

		# build a dictionary of the current blocks
		blockMap = {}
		for blk in tr.Blocks():
			blockMap[blk.Name()] = blk

		if self.settings.debug.blockoccupancy:
			self.Alert("Blocks currently in train: %s" % (", ".join(blockMap.keys())))

		remainingBlocks = []
		splitBlocks = []

		for bn, blk in blockMap.items():
			if bn.endswith(".E") or bn.endswith(".W"):
				lbn = bn[:-2]
			else:
				lbn = bn
			if lbn in blocks:
				splitBlocks.append(blk)
			else:
				remainingBlocks.append(blk)

		if self.settings.debug.blockoccupancy:
			self.Alert("Blocks remaining with train: %s" % (", ".join([b.Name() for b in remainingBlocks])))
			self.Alert("Blocks split to  new  train: %s" % (", ".join([b.Name() for b in splitBlocks])))

		# create a new train
		newTr = Train()
		# a new train takes on the direction of the original train
		tr.SetEast(tr.IsEast())
		self.trains[tr.IName()] = tr

		# remove all split blocks from the old train and add them to the new train
		msgs = []
		for blk in splitBlocks:
			if blk.IsMasterBlock():
				blk.RemoveFromTrain()
				for sb in blk.SubBlocks():
					if sb.Train() is not None:
						sb.RemoveFromTrain()
						sb.SetTrain(newTr)
						sb.SetStatus("U")
				newTr.AddBlock(blk, False)
				msgs.append(blk.GetEventMessage())
			else:
				blk.RemoveFromTrain()

				newTr.AddBlock(blk, False)
				blk.SetTrain(newTr)
				blk.SetStatus("U")  # The new train is unidentified
				msgs.append(blk.GetEventMessage())

		# determine each trains current signal, and check if it triggers a stopping section:
		firstBlock = tr.Blocks()[0]
		sig = self.DetermineTrainSignal(tr, firstBlock)
		tr.SetSignal(sig)
		self.CheckStoppingSection(tr)

		firstBlock = newTr.Blocks()[0]
		sig = self.DetermineTrainSignal(newTr, firstBlock)
		newTr.SetSignal(sig)
		self.CheckStoppingSection(newTr)

		self.RailroadEvents(msgs)
		self.RailroadEvent(tr.GetEventMessage())
		self.RailroadEvent(newTr.GetEventMessage())

	def SwapTrains(self, train, swaptrain):
		if self.settings.debug.blockoccupancy:
			self.Alert("Got swap train %s + %s" % (train, swaptrain))
		tr1= self.trains.get(train, None)
		if tr1 is None:
			logging.error("attempt to swap unknown train: %s" % train)
			return

		tr2 = self.trains.get(swaptrain, None)
		if tr2 is None:
			logging.error("attempt to swap unknown train: %s" % swaptrain)
			return

		rname1 = tr1.RName()
		roster1 = tr1.Roster()
		template1 = tr1.TemplateTrain()

		rname2 = tr2.RName()
		roster2 = tr2.Roster()
		template2 = tr2.TemplateTrain()

		tr1.SetName(rname2, roster2)
		tr1.SetTemplateTrain(template2)
		if roster2 is not None:
			tr1.SetEast(roster2["eastbound"])

		tr2.SetName(rname1, roster1)
		tr2.SetTemplateTrain(template1)
		if roster1 is not None:
			tr2.SetEast(roster1["eastbound"])

		self.RailroadEvent(tr1.GetEventMessage())
		self.RailroadEvent(tr2.GetEventMessage())

	def MoveTrain(self, iname, forward, rear, rearonly):
		tr = self.trains.get(iname, None)
		if tr is None:
			logging.error("attempt to move an unknown train")
			return

		if len(tr.Blocks()) == 0:
			logging.error("attempt to move a train in 0 blocks")
			return

		blocks = list(reversed(tr.Blocks()))  # reverse the working blocks so the front of the train is in position 0
		if rearonly:
			xb = blocks[-1]
			self.SendBlockGroupBit(xb, 0)
		else:
			if forward:
				blk = blocks[0]
				nb = blk.NextDetectionSectionEast() if tr.East() else blk.NextDetectionSectionWest()
				if nb.Name() in ["KOSN10S11", "KOSN20S21"]:
					nb = nb.NextDetectionSectionEast() if tr.East() else nb.NextDetectionSectionWest()
				if nb is not None:  # make sure we point to the Block, not the OSBlock
					nb = nb.Block()
				xb = blocks[-1] if rear else None
			else:
				blk = blocks[-1]
				nb = blk.NextDetectionSectionWest() if tr.East() else blk.NextDetectionSectionEast()
				if nb.Name() in ["KOSN10S11", "KOSN20S21"]:
					nb = nb.NextDetectionSectionWest() if tr.East() else nb.NextDetectionSectionEast()
				if nb is not None:  # make sure we point to the Block, not the OSBlock
					nb = nb.Block()
				xb = blocks[0] if rear else None

			if nb is None:
				return

			self.SendBlockGroupBit(nb, 1)
			self.SendBlockGroupBit(xb, 0)

	def SendBlockGroupBit(self, blk, val):
		if blk is None:
			return

		if blk.IsMasterBlock():
			bl = blk.SubBlocks()
		else:
			bl = [blk]
		for bk in bl:
			b = bk.Bits()
			bk.node.SetInputBit(b[0][0], b[0][1], val)

	def MergeTrains(self, train, mergetrain):
		if self.settings.debug.blockoccupancy:
			self.Alert("Got merge train %s + %s" % (train, mergetrain))
		tr = self.trains.get(train, None)
		if tr is None:
			return

		tr2 = self.trains.get(mergetrain, None)
		if tr2 is None:
			return

		# deactivate any stopping relay that the mergetrain curfrently has triggerred
		firstBlock = tr2.Blocks()[-1]
		bn = firstBlock.Name()
		if bn.endswith(".E") or bn.endswith(".W"):
			srName = bn[:-2] + ".srel"
			self.SetRelay(srName, 0)
			if self.settings.debug.blockoccupancy:
				self.Alert("Stopping relay %s deactivated" % srName)

		# remove all blocks from the merge train and add them to the main train
		msgs = []
		blkStat = "O" if tr.IsIdentified() else "U"
		blkDir = tr.IsEast()
		for blk in reversed(tr2.Blocks()):
			if blk.IsMasterBlock():
				blk.RemoveFromTrain()
				for sb in blk.SubBlocks():
					if sb.Train() is not None:
						sb.RemoveFromTrain()
						sb.SetEast(blkDir)  # assert direction is the same as main train
						sb.SetTrain(tr)
						sb.SetStatus(blkStat)
				blk.SetEast(blkDir)  # Assert direction of block
				tr.AddBlock(blk, True)
				msgs.append(blk.GetEventMessage())
			else:
				blk.RemoveFromTrain()

				tr.AddBlock(blk, True)
				blk.SetEast(blkDir)  # Assert direction of block
				blk.SetTrain(tr)
				blk.SetStatus(blkStat)  # The new train is unidentified
				msgs.append(blk.GetEventMessage())

		# the front of the train hasn't changed - so no stopping block calculation need be done

		self.RailroadEvents(msgs)
		self.RailroadEvent(tr.GetEventMessage())
		self.RailroadEvent(tr2.GetEventMessage())

		# train 2 can now be deleted
		del(self.trains[mergetrain])

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
			return None, []
		else:
			osblk = self.osblocks[osName]
			rtName = osblk.ActiveRouteName()
			if rtName is None:
				self.Alert("No Route Available for signal %s" % sigBaseNm, locale=locale)
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
					logging.info("calculated aspect for %s = %d" % (sigMatch, aspect))
					msgs.extend(sig.GetEventMessages())

			except Exception as e:
				logging.warning("Exception %s in calc aspect %s" % (str(e), sigMatch))
				return None, []

			lever.district.EvaluateDistrictLocks(sig, None)
			self.EvaluatePreviousSignals(sig)
			return aspect, msgs

	def CalculateAspect(self, sig, osName, moving, callon, locale, silent=False):
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
			logging.debug("changhing direction of os to %s" % currentDirection)

		if CrossingEastWestBoundary(osblk, exitBlk):
			logging.debug("we crossed a EW boundary between %s and %s" % (osblk.Name(), exitBlk.Name()))
			currentDirection = not currentDirection

		exitBlk.SetEast(currentDirection)
		nb = exitBlk.NextBlock(reverse=currentDirection != osblk.East())
		if nb:
			nbName = nb.Name()
			if CrossingEastWestBoundary(nb, exitBlk):
				currentDirection = not currentDirection

			nbStatus = nb.GetStatus()

			nbRType = nb.RouteType(reverse=currentDirection != nb.East())

			nbRtName = nb.ActiveRouteName()
			# # try to go one more block, skipping past an OS block

			nxb = nb.ExitBlock(reverse=currentDirection != nb.East())
			if nxb is None:
				nxbNm = None
				nnb = None
			else:
				nxbNm = nxb.Name()

				if CrossingEastWestBoundary(nb, nxb):
					currentDirection = not currentDirection

				nnb = nxb.NextBlock(reverse=currentDirection != nxb.East())

			if nnb:
				nnbClear = nnb.IsCleared()
				nnbName = nnb.Name()
			else:
				nnbClear = False
				nnbName = None
		else:
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

		return aspect

	def ApplyAspect(self, aspect, sig, osName, callon):
		signame = sig.Name()
		wasCallon = sig.IsCallon()
		osblk = self.osblocks[osName]
		blk = self.blocks[osName]

		exitBlk = osblk.ActiveRoute().ExitBlock(reverse=sig.East() != blk.IsEast())
		self.Alert("Exit block is %s, sigeast is %s blkeast is %s" % (exitBlk.Name(), sig.East(), blk.IsEast()))
		ebList = exitBlk.GetAllBlocks()
		sig.SetAspect(aspect, callon=callon)
		tlock = []
		if aspect == 0:
			if not wasCallon:
				for eb in ebList:
					if not eb.IsOccupied():
						eb.SetStatus("E")
						# eb.Reset()
				if not osblk.IsOccupied():
					osblk.SetStatus("E")
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
			msgs.extend(eb.GetEventMessages())
		msgs.extend(lockmsg)

		# see if any trains are impacted by changes to this signal
		for trid, tr in self.trains.items():
			tsig = tr.Signal()
			if tsig is not None:
				if signame == tsig.Name():
					msgs.append(tr.GetEventMessage())

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

		# identify the train that this signal controls and update the train with the new aspect
		tr = psig.Train()
		if tr is not None:
			tr.SetAspect(psig.Aspect(), psig.AspectType())
			self.RailroadEvent((tr.GetEventMessage()))

		msgs = psig.GetEventMessages()

		if self.debug.showaspectcalculation:
			self.Alert("Calculated new aspect of %d for signal %s" % (newAspect, sigNm))
			for m in msgs:
				self.Alert("Cmd: (%s)" % str(m))

		for m in msgs:
			self.RailroadEvent(m)

		self.EvaluatePreviousSignals(psig)

	def IdentifyTrain(self, blk):
		if self.debug.identifytrain:
			self.Alert("======= new train identification for block %s" % blk.Name())

		if blk.IsEast():
			if self.debug.identifytrain:
				self.Alert("This is an eastbound block - first look to the west")

			# look to the west
			blkw = blk.NextDetectionSectionWest()
			if self.debug.identifytrain:
				self.Alert("Next west block is %s" % ("None" if blkw is None else blkw.Name()))

			if blkw is not None:
				tr = blkw.Train()
				if self.debug.identifytrain:
					self.Alert("The train found there is %s" % ("None" if tr is None else tr.Name()))

				if tr is not None:
					self.CheckEWCross(tr, blk, blkw)
					if tr.IsEast():
						if self.debug.identifytrain:
							self.Alert("This block is being placed at the front of this train")

						#  then this block goes on the front of the train
						return tr, False
					else:
						if self.debug.identifytrain:
							self.Alert("This block is being placed at the rear of this train")
							self.Alert("and the block direction is being changed to WEST")

						#  this block goes on the rear of the train AND this block is set to a west block
						blk.SetEast(False)
						return tr, True

			# look to the east
			if self.debug.identifytrain:
				self.Alert("Nothing west - now look to the east")

			blke = blk.NextDetectionSectionEast()
			if self.debug.identifytrain:
				self.Alert("Next east block is %s" % ("None" if blke is None else blke.Name()))

			if blke is not None:
				tr = blke.Train()
				if self.debug.identifytrain:
					self.Alert("The train found there is %s" % ("None" if tr is None else tr.Name()))

				if tr is not None:
					self.CheckEWCross(tr, blk, blke)
					if tr.IsEast():
						if self.debug.identifytrain:
							self.Alert("This block is being placed at the rear of this train")

						#  then this block goes on the rear of the train
						return tr, True
					else:
						#  this block goes on the front of the train AND this block is set to a west block
						if self.debug.identifytrain:
							self.Alert("This block is being placed at the front of this train")
							self.Alert("and the block direction is being changed to WEST")

						blk.SetEast(False)
						return tr, False

		else:  # This is a westbound block
			if self.debug.identifytrain:
				self.Alert("This is a westbound block - first look to the east")

			# look to the east
			blke = blk.NextDetectionSectionEast()
			if self.debug.identifytrain:
				self.Alert("Next east block is %s" % ("None" if blke is None else blke.Name()))

			if blke is not None:
				tr = blke.Train()
				if self.debug.identifytrain:
					self.Alert("The train found there is %s" % ("None" if tr is None else tr.Name()))

				if tr is not None:
					self.CheckEWCross(tr, blk, blke)
					if tr.IsEast():
						#  this block goes on the rear of the train AND the block is set to an east block
						if self.debug.identifytrain:
							self.Alert("This block is being placed at the rear of this train")
							self.Alert("and the block direction is being changed to EAST")

						blk.SetEast(True)
						return tr, True
					else:
						#  then this block goes on the front of the train
						if self.debug.identifytrain:
							self.Alert("This block is being placed at the front of this train")

						return tr, False

			# look to the west
			if self.debug.identifytrain:
				self.Alert("Nothing east - now look to the west")

			blkw = blk.NextDetectionSectionWest()
			if self.debug.identifytrain:
				self.Alert("Next west block is %s" % ("None" if blkw is None else blkw.Name()))

			if blkw is not None:
				tr = blkw.Train()
				if self.debug.identifytrain:
					self.Alert("The train found there is %s" % ("None" if tr is None else tr.Name()))

				if tr is not None:
					self.CheckEWCross(tr, blk, blkw)
					if tr.IsEast():
						# this block goes on the front of the train AND the block is set to an east block
						if self.debug.identifytrain:
							self.Alert("This block is being placed at the front of this train")
							self.Alert("and the block direction is being changed to EAST")

						blk.SetEast(True)
						return tr, False
					else:
						# then this block goes on the rear of the train
						if self.debug.identifytrain:
							self.Alert("This block is being placed at the rear of this train")
						return tr, True

		# No trains found in adjoining blocks.
		# this is a new unknown train and it assumes the direction of the underlying block
		if self.debug.identifytrain:
			self.Alert("Unable to identify a train - generate a new unknown train")

		tr = Train()
		# a new train takes on the direction of the block it's in
		tr.SetEast(blk.IsEast())
		self.trains[tr.IName()] = tr
		return tr, False

	def IdentifyTrain2(self, blk):
		"""
		logging.debug("identify train in block %s" % blk.Name())		returns the identified train, or NOne if no traiun identified
		Also return False if this block is to be added to the front of the train, True otherwise

		if this is an eastbound block
			look to the west
				if found train is eastbound,
					then this block goes on the front of the train
					return

				else the train is westbound:
					this block goes on the rear of the trains AND this block is set to a west block
					return

			look to the east
				if found train is eastbound
					then this block goes on the rear of the train
					return

				else the train is westbound
					this block goes on the front of the train AND this block is set to a west block
					return

		else if thsi is a westbound block:
			look to the east
				if found train is westbound
					then this block goes on the front of the train
					return
				else:
					this block goes on the rear of the train AND the block is set to an east block
					return

			look to the west
				if the found train is westbound
					then this block goes on the rear of the train
					return

				else the train is eastbound
					this block goes on the front of the train AND the block is set to an east block

		else:
			this is a new unknown train and it assumes the direction of the underlying block
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
								self.Alert("Train direction is %s, block is East, connect to rear %s" % (tr.IsEast(), not tr.IsEast()))
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
							self.Alert(
								"Train direction is %s, block is East, connect to rear %s" % (tr.IsEast(), not tr.IsEast()))
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
								self.Alert("Train direction is %s, block is East, connect to rear %s" % (tr.IsEast(), tr.IsEast()))
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
							self.Alert(
								"Train direction is %s, block is East, connect to rear %s" % (tr.IsEast(), tr.IsEast()))
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
								self.Alert("Train direction is %s, block is West, connect to rear %s" % (tr.IsEast(), tr.IsEast()))
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
							self.Alert(
								"Train direction is %s, block is West, connect to rear %s" % (tr.IsEast(), tr.IsEast()))
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
								self.Alert("Train direction is %s, block is West, connect to rear %s" % (tr.IsEast(), not tr.IsEast()))
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
							self.Alert(
								"Train direction is %s, block is East, connect to rear %s" % (tr.IsEast(), not tr.IsEast()))
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

	def GetTrain(self, iname):
		return self.trains.get(iname, None)

	def GetActiveTrainList(self):
		result = {}
		for trid, tr in self.trains.items():
			name = tr.Name()
			sig = tr.Signal()
			asp = tr.AspectName()
			if asp is None:
				asp = sig.AspectName()
			result[name] = {
				"iname": tr.IName(),
				"loco": tr.Loco(),
				"east": tr.IsEast(),
				"engineer": tr.Engineer(),
				"blocks": [b.Name() for b in tr.Blocks()],
				"signal": None if sig is None else sig.Name(),
				"aspect": asp,
				"stopped": tr.Stopped(),
				"atc": tr.ATC(),
				"ar": tr.AR(),
			}

		return result

	def CheckEWCross(self, tr, blk, blkn):
		s = blk.StoppedBlock()
		cblk = blk if s is None else s
		s = blkn.StoppedBlock()
		cblkn = blkn if s is None else s

		if CrossingEastWestBoundary(cblk, cblkn):
			if self.debug.identifytrain:
				self.Alert("Train %s crossed an E/W boundary - reversing train direction" % tr.Name())
			tr.SetEast(not tr.East())

	def RecordBreakerTrip(self, brkr):
		ofn = os.path.join(os.getcwd(), "output", "breaker.jtxt")
		if brkr is None:
			with open(ofn, "w") as ofp:
				pass
			return

		if self.breakerCycleDelay > 0:
			return

		with open(ofn, "a") as ofp:
			brkr = {"breaker": brkr.Name()}
			n = datetime.now()
			ts = "%4d%02d%02d-%02d%02d%02d" % (n.year, n.month, n.day, n.hour, n.minute, n.second)
			brkr["timestamp"] = ts
			brkr["trains"] = self.GetActiveTrainList()
			ofp.write("%s\n\n" % json.dumps(brkr, indent=2))


class PendingDetectionLoss:
	def __init__(self, railroad):
		self.pendingDetectionLoss = {}
		self.railroad = railroad
		self.pendingDetectionLossCycles = railroad.settings.rrserver.pendingdetectionlosscycles
				
	def Add(self, district, block, obj):
		self.pendingDetectionLoss[block] = [self.pendingDetectionLossCycles, district, obj]
		
	def Remove(self, block):
		try:
			del self.pendingDetectionLoss[block]
		except:
			return False
		
		return True
		
	def NextCycle(self):
		removeBlock = []
		for blkName in self.pendingDetectionLoss:
			self.pendingDetectionLoss[blkName][0] -= 1
			if self.pendingDetectionLoss[blkName][0] <= 0:
				# it's time to believe - process the detection loss and remove from this list
				district = self.pendingDetectionLoss[blkName][1]
				obj = self.pendingDetectionLoss[blkName][2]
				self.railroad.DetectionLoss(district, obj)

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


