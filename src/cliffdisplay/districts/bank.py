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
				(self.tiles["horiz"], self.screen,        (5, 11), False),
				(self.tiles["horiznc"],   self.screen,    (6, 11), False),
				(self.tiles["horiz"],   self.screen,      (7, 11), False),
				(self.tiles["horiznc"], self.screen,      (8, 11), False),
				(self.tiles["eobright"], self.screen,      (9, 11), False),
			], False)
		self.blocks["B10"].AddStoppingBlock([
				(self.tiles["horiznc"], self.screen,      (2, 11), False),
				(self.tiles["horiz"], self.screen,        (3, 11), False),
				(self.tiles["horiznc"],   self.screen,    (4, 11), False),
			], False)
		self.blocks["B10"].AddTrainLoc(self.screen, (3, 11))

		self.blocks["B20"] = Block(self, self.frame, "B20",
			[
				(self.tiles["horiznc"], self.screen,      (2, 13), False),
				(self.tiles["horiz"],   self.screen,      (3, 13), False),
				(self.tiles["horiznc"], self.screen,      (4, 13), False),
				(self.tiles["horiz"],   self.screen,      (5, 13), False),
				(self.tiles["horiznc"], self.screen, 	  (6, 13), False),
			], True)
		self.blocks["B20"].AddStoppingBlock([
				(self.tiles["horiz"],   self.screen,      (7, 13), False),
				(self.tiles["horiznc"], self.screen,      (8, 13), False),
				(self.tiles["eobright"], self.screen,      (9, 13), False),
			], True)
		self.blocks["B20"].AddTrainLoc(self.screen, (3, 13))

		self.blocks["B11"] = Block(self, self.frame, "B11",
			[
				(self.tiles["horiznc"], self.screen,      (18, 11), False),
				(self.tiles["horiz"],   self.screen,      (19, 11), False),
				(self.tiles["horiz"],   self.screen,      (21, 11), False),
				(self.tiles["horiznc"], self.screen,      (22, 11), False),
				(self.tiles["eobright"], self.screen,      (24, 11), False),
			], False)
		self.blocks["B11"].AddStoppingBlock([
				(self.tiles["eobleft"], self.screen,      (15, 11), False),
				(self.tiles["horiznc"], self.screen,      (16, 11), False),
				(self.tiles["horiz"],   self.screen,      (17, 11), False),
			], False)
		self.blocks["B11"].AddTrainLoc(self.screen, (17, 11))

		self.blocks["B21"] = Block(self, self.frame, "B21",
			[
				(self.tiles["horiz"],   self.screen,      (17, 13), False),
				(self.tiles["horiznc"], self.screen,      (18, 13), False),
				(self.tiles["horiz"],   self.screen,      (19, 13), False),
				(self.tiles["horiz"],   self.screen,      (21, 13), False),
				(self.tiles["horiznc"], self.screen,      (22, 13), False),
			], True)
		self.blocks["B21"].AddStoppingBlock([
				(self.tiles["horiz"],   self.screen,      (23, 13), False),
				(self.tiles["eobright"], self.screen,      (24, 13), False),
			], True)
		self.blocks["B21"].AddStoppingBlock([
				(self.tiles["eobleft"], self.screen,      (15, 13), False),
				(self.tiles["horiznc"], self.screen,      (16, 13), False),
			], False)
		self.blocks["B21"].AddTrainLoc(self.screen, (16, 13))

		self.blocks["BOSWW"] = OverSwitch(self, self.frame, "BOSWW",
			[
				(self.tiles["eobleft"],  self.screen,     (10, 11), False),
				(self.tiles["horiznc"],  self.screen,     (12, 11), False),
				(self.tiles["horiz"],    self.screen,     (13, 11), False),
				(self.tiles["eobright"], self.screen,     (14, 11), False),
				(self.tiles["diagright"], self.screen,     (12, 12), False),
				(self.tiles["eobright"], self.screen,     (14, 13), False),
			], False)
		self.blocks["BOSWW"].AddTrainLoc(self.screen, (10, 19))

		self.blocks["BOSWE"] = OverSwitch(self, self.frame, "BOSWE",
			[
				(self.tiles["eobleft"],  self.screen,     (10, 13), False),
				(self.tiles["horiz"],    self.screen,     (11, 13), False),
				(self.tiles["horiznc"],  self.screen,     (12, 13), False),
				(self.tiles["eobright"], self.screen,     (14, 13), False),
			], False)
		self.blocks["BOSWE"].AddTrainLoc(self.screen, (10, 21))

		self.blocks["BOSE"] = OverSwitch(self, self.frame, "BOSE",
			[
				(self.tiles["eobleft"],  self.screen,     (25, 11), False),
				(self.tiles["turnrightright"], self.screen, (26, 11), False),
				(self.tiles["diagright"], self.screen,     (27, 12), False),
				(self.tiles["eobleft"],  self.screen,     (25, 13), False),
				(self.tiles["horiz"],    self.screen,     (26, 13), False),
				(self.tiles["horiznc"],  self.screen,     (27, 13), False),
				(self.tiles["eobright"], self.screen,     (29, 13), False),
			], True)
		self.blocks["BOSE"].AddTrainLoc(self.screen, (25, 19))

		self.osBlocks["BOSWW"] = ["B10", "B11", "B21"]
		self.osBlocks["BOSWE"] = ["B20", "B21", "B10"]
		self.osBlocks["BOSE"] = ["B11", "B21", "C13"]

		return self.blocks, self.osBlocks

	def DefineTurnouts(self, blocks):
		self.turnouts = {}

		toList = [
			["CSw17",  "torightleft",  ["BOSE"], (28, 13)],
			["CSw23",  "torightright",  ["BOSWW", "BOSWE"], (11, 11)],
			["CSw23b", "torightleft",   ["BOSWW", "BOSWE"], (13, 13)],
		]

		hslist = [
			["CSw19",  "torightright",  "B21", (20, 13)],
			["CSw21a", "torightleft",   "B11", (23, 11)],
			["CSw21b", "torightleft",   "B11", (20, 11)],
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
			["C18LA",  RegAspects, True,    "right", (25, 12)],
			["C18LB",  RegAspects, True,    "rightlong", (25, 14)],
			["C18R",   RegAspects, False,   "leftlong", (29, 12)],

			["C22L",   RegAspects, True,    "right", (10, 12)],
			["C22R",   RegAspects, False,   "leftlong", (14, 10)],

			["C24L",   RegAspects, True,    "rightlong", (10, 14)],
			["C24R",   RegAspects, False,   "leftlong", (14, 12)],
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
		self.routes["BRtB10B11"] = Route(self.screen, block, "BRtB10B11", "B11", [(10, 11), (11, 11), (12, 11), (13, 11), (14, 11)], "B10", [RESTRICTING, MAIN], ["CSw23:N"], ["C22R", "C22L"])
		self.routes["BRtB10B21"] = Route(self.screen, block, "BRtB10B21", "B21", [(10, 11), (11, 11), (12, 12), (13, 13), (14, 13)], "B10", [RESTRICTING, DIVERGING], ["CSw23:R"], ["C24R", "C22L"])

		block = self.blocks["BOSWE"]
		self.routes["BRtB20B21"] = Route(self.screen, block, "BRtB20B21", "B21", [(10, 13), (11, 13), (12, 13), (13, 13), (14, 13)], "B20", [MAIN, RESTRICTING], ["CSw23:N"], ["C24R", "C24L"])

		block = self.blocks["BOSE"]
		self.routes["BRtB11C13"] = Route(self.screen, block, "BRtB11C13", "B11", [(25, 11), (26, 11), (27, 12), (28, 13), (29, 13)], "C13", [RESTRICTING, DIVERGING], ["CSw17:R"], ["C18LA", "C18R"])
		self.routes["BRtB21C13"] = Route(self.screen, block, "BRtB21C13", "B21", [(25, 13), (26, 13), (27, 13), (28, 13), (29, 13)], "C13", [MAIN, MAIN], ["CSw17:N"], ["C18LB", "C18R"])

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

		hs = HandSwitch(self, self.screen, self.frame, self.blocks["B11"], "CSw21b.hand", (20, 10), self.misctiles["handdown"])
		self.blocks["B11"].AddHandSwitch(hs)
		self.handswitches["CSw21b.hand"] = hs

		hs = HandSwitch(self, self.screen, self.frame, self.blocks["B11"], "CSw21a.hand", (23, 10), self.misctiles["handdown"])
		self.blocks["B11"].AddHandSwitch(hs)
		self.handswitches["CSw21a.hand"] = hs

		hs = HandSwitch(self, self.screen, self.frame, self.blocks["B21"], "CSw19.hand", (20, 14), self.misctiles["handup"])
		self.blocks["B21"].AddHandSwitch(hs)
		self.handswitches["CSw19.hand"] = hs

		return self.handswitches

	def DoSignalAction(self, sig, aspect, frozenaspect=None, callon=False):
		District.DoSignalAction(self, sig, aspect, frozenaspect=frozenaspect, callon=callon)
		signame = sig.GetName()
		if signame in ["C18R", "C22R", "C24R", "C22L", "C24L"]:
			self.CheckBlockSignalsAdv("B20", "B21", "B20E", True)
