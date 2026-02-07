from dispatcher.district import District

from dispatcher.block import Block, OverSwitch, Route, OSProxy
from dispatcher.turnout import Turnout
from dispatcher.signal import Signal
from dispatcher.handswitch import HandSwitch

from dispatcher.constants import RESTRICTING, MAIN, DIVERGING, RegAspects


class Bank (District):
	def __init__(self, name, frame, screen):
		District.__init__(self, name, frame, screen)
		self.C13Queue = self.frame.C13Queue

	def SetUpRoute(self, osblk, route):
		controlOpt = self.frame.cliffControl
		if controlOpt == 0:  # bank local control
			self.frame.PopupEvent("Bank control is local")
			return

		District.SetUpRoute(self, osblk, route)

	def DetermineRoute(self, blocks):
		self.FindTurnoutCombinations(blocks, ["CSw17", "CSw23"])

	def DefineBlocks(self):
		self.blocks = {}
		self.osBlocks = {}

		self.blocks["B10"] = Block(self, self.frame, "B10",
			[
				(self.tiles["eobleft"], self.screen,      (110, 38), False),
				(self.tiles["horiznc"],   self.screen,    (111, 38), False),
				(self.tiles["horiz"],   self.screen,      (112, 38), True),
				(self.tiles["horiznc"], self.screen,      (113, 38), False),
				(self.tiles["horiz"], self.screen,        (114, 38), True),
				(self.tiles["horiznc"], self.screen,      (115, 38), False),
			], False)
		self.blocks["B10"].AddStoppingBlock([
				(self.tiles["ssleft"], self.screen,       (116, 38), True),
				(self.tiles["horiznc"],   self.screen,    (117, 38), False),
			], False)
		self.blocks["B10"].AddTrainLoc(self.screen, (112, 38))

		self.blocks["B20"] = Block(self, self.frame, "B20",
			[
				(self.tiles["horiznc"], self.screen,      (117, 36), False),
				(self.tiles["horiz"],   self.screen,      (116, 36), True),
				(self.tiles["horiznc"], self.screen,      (115, 36), False),
				(self.tiles["horiz"],   self.screen,      (114, 36), True),
				(self.tiles["horiznc"], self.screen, 	  (113, 36), False),
				(self.tiles["horiz"],   self.screen,      (112, 36), True),
			], True)
		self.blocks["B20"].AddStoppingBlock([
				(self.tiles["ssright"], self.screen,      (111, 36), False),
				(self.tiles["eobleft"], self.screen,      (110, 36), True),
			], True)
		self.blocks["B20"].AddTrainLoc(self.screen, (114, 36))

		self.blocks["B11"] = Block(self, self.frame, "B11",
			[
				(self.tiles["horiz"],   self.screen,      (102, 38), False),
				(self.tiles["horiznc"], self.screen,      (101, 38), False),
				(self.tiles["horiz"],   self.screen,      (100, 38), True),
				(self.tiles["horiz"],   self.screen,      (98, 38), True),
				(self.tiles["horiznc"], self.screen,      (97, 38), False),
				(self.tiles["eobleft"], self.screen,      (95, 38), False),
			], False)
		self.blocks["B11"].AddStoppingBlock([
				(self.tiles["eobright"], self.screen,      (104, 38), False),
				(self.tiles["ssleft"],  self.screen,      (103, 38), False),
			], False)
		self.blocks["B11"].AddTrainLoc(self.screen, (100, 38))

		self.blocks["B21"] = Block(self, self.frame, "B21",
			[
				(self.tiles["horiz"],   self.screen,      (102, 36), True),
				(self.tiles["horiznc"], self.screen,      (101, 36), False),
				(self.tiles["horiz"],   self.screen,      (100, 36), True),
				(self.tiles["horiz"],   self.screen,      (98, 36), True),
				(self.tiles["horiznc"], self.screen,      (97, 36), False),
			], True)
		self.blocks["B21"].AddStoppingBlock([
				(self.tiles["ssright"], self.screen,      (96, 36), True),
				(self.tiles["eobleft"], self.screen,      (95, 36), False),
			], True)
		self.blocks["B21"].AddStoppingBlock([
				(self.tiles["eobright"], self.screen,      (104, 36), False),
				(self.tiles["ssleft"],  self.screen,      (103, 36), False),
			], False)
		self.blocks["B21"].AddTrainLoc(self.screen, (100, 36))

		self.blocks["BOSWW"] = OverSwitch(self, self.frame, "BOSWW",
			[
				(self.tiles["eobright"],  self.screen,     (109, 38), False),
				(self.tiles["horiznc"],   self.screen,     (107, 38), True),
				(self.tiles["horiz"],     self.screen,     (106, 38), False),
				(self.tiles["eobleft"],   self.screen,     (105, 38), False),
				(self.tiles["diagright"], self.screen,     (107, 37), False),
				(self.tiles["eobleft"],   self.screen,     (105, 36), False),
			], False)
		self.blocks["BOSWW"].AddTrainLoc(self.screen, (105, 29))

		self.blocks["BOSWE"] = OverSwitch(self, self.frame, "BOSWE",
			[
				(self.tiles["eobright"], self.screen,     (109, 36), False),
				(self.tiles["horiz"],    self.screen,     (108, 36), False),
				(self.tiles["horiznc"],  self.screen,     (107, 36), True),
				(self.tiles["eobleft"],  self.screen,     (105, 36), False),
			], False)
		self.blocks["BOSWE"].AddTrainLoc(self.screen, (105, 27))

		self.blocks["BOSE"] = OverSwitch(self, self.frame, "BOSE",
			[
				(self.tiles["eobright"],  self.screen,     (94, 38), False),
				(self.tiles["turnrightleft"], self.screen, (93, 38), False),
				(self.tiles["diagright"], self.screen,     (92, 37), False),
				(self.tiles["eobright"],  self.screen,     (94, 36), False),
				(self.tiles["horiz"],    self.screen,      (93, 36), True),
				(self.tiles["horiznc"],  self.screen,      (92, 36), False),
				(self.tiles["eobleft"], self.screen,       (90, 36), False),
			], True)
		self.blocks["BOSE"].AddTrainLoc(self.screen, (90, 29))

		self.osBlocks["BOSWW"] = ["B10", "B11", "B21"]
		self.osBlocks["BOSWE"] = ["B20", "B21", "B10"]
		self.osBlocks["BOSE"] = ["B11", "B21", "C13"]

		return self.blocks, self.osBlocks

	def DefineTurnouts(self, blocks):
		self.turnouts = {}

		toList = [
			["CSw17",  "torightright",  ["BOSE"], (91, 36)],
			["CSw23",  "torightleft",  ["BOSWW", "BOSWE"], (108, 38)],
			["CSw23b", "torightright",   ["BOSWW", "BOSWE"], (106, 36)],
		]

		hslist = [
			["CSw19",  "toleftright",  "B21", (99, 36)],
			["CSw21a", "torightright", "B11", (96, 38)],
			["CSw21b", "torightright", "B11", (99, 38)],
		]

		for tonm, tileSet, blks, pos in toList:
			trnout = Turnout(self, self.frame, tonm, self.screen, self.totiles[tileSet], pos)
			for blknm in blks:
				blocks[blknm].AddTurnout(trnout)
				trnout.AddBlock(blknm)
			self.turnouts[tonm] = trnout

		for tonm, tileSet, blknm, pos in hslist:
			trnout = Turnout(self, self.frame, tonm, self.screen, self.totiles[tileSet], pos)
			blk = blocks[blknm]
			blk.AddTurnout(trnout)
			trnout.AddBlock(blknm)
			trnout.SetContainingBlock(blk)
			self.turnouts[tonm] = trnout

		self.turnouts["CSw23"].SetPairedTurnout(self.turnouts["CSw23b"])

		self.turnouts["CSw19"].SetDisabled(True)
		self.turnouts["CSw21a"].SetDisabled(True)
		self.turnouts["CSw21b"].SetDisabled(True)

		return self.turnouts

	def DefineSignals(self):
		self.signals = {}
		self.osProxies = {}

		sigList = [
			["C18LA",  RegAspects, True,    "left", (94, 37)],
			["C18LB",  RegAspects, True,    "leftlong", (94, 35)],
			["C18R",   RegAspects, False,   "rightlong", (90, 37)],

			["C22L",   RegAspects, True,    "left", (109, 37)],
			["C22R",   RegAspects, False,   "rightlong", (105, 39)],

			["C24L",   RegAspects, True,    "leftlong", (109, 35)],
			["C24R",   RegAspects, False,   "rightlong", (105, 37)],
		]
		for signm, atype, east, tileSet, pos in sigList:
			self.signals[signm]  = Signal(self, self.screen, self.frame, signm, atype, east, pos, self.sigtiles[tileSet])

		self.signals["C18LA"].SetMutexSignals(["C18LB"])
		self.signals["C18LB"].SetMutexSignals(["C18LA"])

		self.sigLeverMap = {
			"C18.lvr": ["BOSE"],
			"C22.lvr": ["BOSWW"],
			"C24.lvr": ["BOSWW", "BOSWE"],
		}

		for sl in self.sigLeverMap:
			self.frame.AddSignalLever(sl, self)

		blockSbSigs = {
			# # which signals govern stopping sections, west and east
			"B11": ("C22R",  None),
			"B20": (None,    "C24L"),
			"B21": ("C24R",  "C18LB"),
		}

		for blknm, siglist in blockSbSigs.items():
			self.blocks[blknm].SetSBSignals(siglist)

		self.blockSigs = {
			# # which signals govern blocks, west and east - not needed for OS and stopping blocks
			"B11": ("C22R",  "C18LA"),
			"B20": ("N24L",  "C24L"),
			"B21": ("C24R",  "C18LB"),
		}

		for blknm, siglist in self.blockSigs.items():
			self.blocks[blknm].SetSignals(siglist)

		self.routes = {}
		self.osSignals = {}

		block = self.blocks["BOSWW"]
		self.routes["BRtB10B11"] = Route(self.screen, block, "BRtB10B11", "B11", [(109, 38), (108, 38), (107, 38), (106, 38), (105, 38)], "B10", [RESTRICTING, MAIN], ["CSw23:N"], ["C22R", "C22L"])
		self.routes["BRtB10B21"] = Route(self.screen, block, "BRtB10B21", "B21", [(109, 38), (108, 38), (107, 37), (106, 36), (105, 36)], "B10", [RESTRICTING, DIVERGING], ["CSw23:R"], ["C24R", "C22L"])

		block = self.blocks["BOSWE"]
		self.routes["BRtB20B21"] = Route(self.screen, block, "BRtB20B21", "B21", [(109, 36), (108, 36), (107, 36), (106, 36), (105, 36)], "B20", [MAIN, RESTRICTING], ["CSw23:N"], ["C24R", "C24L"])

		block = self.blocks["BOSE"]
		self.routes["BRtB11C13"] = Route(self.screen, block, "BRtB11C13", "B11", [(94, 38), (93, 38), (92, 37), (91, 36), (90, 36)], "C13", [RESTRICTING, DIVERGING], ["CSw17:R"], ["C18LA", "C18R"])
		self.routes["BRtB21C13"] = Route(self.screen, block, "BRtB21C13", "B21", [(94, 36), (93, 36), (92, 36), (91, 36), (90, 36)], "C13", [MAIN, MAIN], ["CSw17:N"], ["C18LB", "C18R"])

		self.signals["C22L"].AddPossibleRoutes("BOSWW", ["BRtB10B11", "BRtB10B21"])
		self.signals["C22R"].AddPossibleRoutes("BOSWW", ["BRtB10B11"])

		self.signals["C24L"].AddPossibleRoutes("BOSWE", ["BRtB20B21"])
		self.signals["C24R"].AddPossibleRoutes("BOSWE", ["BRtB20B21"])
		self.signals["C24R"].AddPossibleRoutes("BOSWW", ["BRtB10B21"])

		self.signals["C18LA"].AddPossibleRoutes("BOSE", ["BRtB11C13"])
		self.signals["C18LB"].AddPossibleRoutes("BOSE", ["BRtB21C13"])
		self.signals["C18R"].AddPossibleRoutes("BOSE", ["BRtB11C13", "BRtB21C13"])

		self.osSignals["BOSWW"] = ["C22L", "C22R", "C24R"]
		self.osSignals["BOSWE"] = ["C24L", "C24R"]
		self.osSignals["BOSE"] = ["C18LB", "C18LA", "C18R"]

		p = OSProxy(self, "BOSWW")
		self.osProxies["BOSWW"] = p
		p.AddRoute(self.routes["BRtB10B21"])
		p.AddRoute(self.routes["BRtB10B11"])

		p = OSProxy(self, "BOSWE")
		self.osProxies["BOSWE"] = p
		p.AddRoute(self.routes["BRtB10B21"])
		p.AddRoute(self.routes["BRtB20B21"])

		return self.signals, self.blockSigs, self.osSignals, self.routes, self.osProxies

	def DefineHandSwitches(self):
		self.handswitches = {}

		hs = HandSwitch(self, self.screen, self.frame, self.blocks["B11"], "CSw21b.hand", (99, 39), self.misctiles["handup"])
		self.blocks["B11"].AddHandSwitch(hs)
		self.handswitches["CSw21b.hand"] = hs

		hs = HandSwitch(self, self.screen, self.frame, self.blocks["B11"], "CSw21a.hand", (96, 39), self.misctiles["handup"])
		self.blocks["B11"].AddHandSwitch(hs)
		self.handswitches["CSw21a.hand"] = hs

		hs = HandSwitch(self, self.screen, self.frame, self.blocks["B21"], "CSw19.hand", (99, 35), self.misctiles["handdown"])
		self.blocks["B21"].AddHandSwitch(hs)
		self.handswitches["CSw19.hand"] = hs

		return self.handswitches

	def DoSignalAction(self, sig, aspect, frozenaspect=None, callon=False):
		District.DoSignalAction(self, sig, aspect, frozenaspect=frozenaspect, callon=callon)
		signame = sig.GetName()
		if signame in ["C18R", "C22R", "C24R", "C22L", "C24L"]:
			self.CheckBlockSignalsAdv("B20", "B21", "B20E", True)
