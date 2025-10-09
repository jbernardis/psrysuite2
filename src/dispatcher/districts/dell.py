from dispatcher.district import District

from dispatcher.block import Block, OverSwitch, Route, OSProxy
from dispatcher.turnout import Turnout, SlipSwitch
from dispatcher.signal import Signal
from dispatcher.handswitch import HandSwitch

from dispatcher.constants import RESTRICTING, MAIN, DIVERGING, SLIPSWITCH, RegAspects


class Dell (District):
	def __init__(self, name, frame, screen):
		District.__init__(self, name, frame, screen)

	def DoTurnoutAction(self, turnout, state, force=False):
		tn = turnout.GetName()
		if turnout.GetType() == SLIPSWITCH:
			if tn == "DSw3":
				bstat = "N" if self.turnouts["DSw5"].IsNormal() else "R"
				turnout.SetStatus([state, bstat])
				turnout.Draw()

		else:
			District.DoTurnoutAction(self, turnout, state, force=force)

		if tn == "DSw5":
			trnout = self.turnouts["DSw3"]
			trnout.UpdateStatus()
			trnout.Draw()

	def DetermineRoute(self, blocks):
		s5 = 'N' if self.turnouts["DSw5"].IsNormal() else 'R'
		s7 = 'N' if self.turnouts["DSw7"].IsNormal() else 'R'
		self.turnouts["DSw5"].SetLock(s7 == 'R', "DSw7", refresh=True)
		self.turnouts["DSw7"].SetLock(s5 == 'R', "DSw5", refresh=True)
		self.turnouts["DSw7b"].SetLock(s5 == 'R', "DSw5", refresh=True)

		# self.FindTurnoutCombinations(blocks, ["DSw1", "DSw3", "DSw5", "DSw7", "DSw11"])

	def DefineBlocks(self):
		self.blocks = {}
		self.osBlocks = {}

		self.blocks["D10"] = Block(self, self.frame, "D10",
			[
				(self.tiles["horiznc"],  self.screen,      (39, 11), False),
				(self.tiles["horiz"],    self.screen,      (40, 11), False),
				(self.tiles["horiznc"],  self.screen,      (41, 11), False),
				(self.tiles["horiz"],    self.screen,      (42, 11), False),
				(self.tiles["horiznc"],  self.screen,      (43, 11), False),
				(self.tiles["horiz"],    self.screen,      (44, 11), False),
				(self.tiles["eobright"], self.screen,      (45, 11), False),
			], False)
		self.blocks["D10"].AddStoppingBlock([
				(self.tiles["eobleft"], self.screen,      (36, 11), False),
				(self.tiles["horiznc"], self.screen,      (37, 11), False),
				(self.tiles["horiz"],   self.screen,      (38, 11), False),
			], False)
		self.blocks["D10"].AddTrainLoc(self.screen, (38, 11))

		self.blocks["D20"] = Block(self, self.frame, "D20",
			[
				(self.tiles["eobleft"], self.screen,      (36, 13), False),
				(self.tiles["horiznc"], self.screen,      (37, 13), False),
				(self.tiles["horiz"],   self.screen,      (38, 13), False),
				(self.tiles["horiznc"], self.screen,      (39, 13), False),
				(self.tiles["horiz"],   self.screen,      (40, 13), False),
				(self.tiles["horiznc"], self.screen,      (41, 13), False),
				(self.tiles["horiz"],   self.screen,      (42, 13), False),
			], True)
		self.blocks["D20"].AddStoppingBlock([
				(self.tiles["horiznc"],  self.screen,      (43, 13), False),
				(self.tiles["horiz"],    self.screen,      (44, 13), False),
				(self.tiles["eobright"], self.screen,      (45, 13), False),
			], True)
		self.blocks["D20"].AddTrainLoc(self.screen, (38, 13))

		self.blocks["D11"] = Block(self, self.frame, "D11",
			[
				(self.tiles["horiz"],   self.screen,      (58, 11), False),
				(self.tiles["horiznc"], self.screen,      (59, 11), False),
				(self.tiles["horiz"],   self.screen,      (60, 11), False),
				(self.tiles["horiznc"], self.screen,      (61, 11), False),
				(self.tiles["horiz"],   self.screen,      (62, 11), False),
				(self.tiles["horiznc"], self.screen,      (63, 11), False),
			], False)
		self.blocks["D11"].AddStoppingBlock([
				(self.tiles["horiz"],    self.screen,      (64, 11), False),
				(self.tiles["eobright"], self.screen,      (65, 11), False),
			], True)
		self.blocks["D11"].AddStoppingBlock([
				(self.tiles["eobleft"], self.screen,      (56, 11), False),
				(self.tiles["horiznc"], self.screen,      (57, 11), False),
			], False)
		self.blocks["D11"].AddTrainLoc(self.screen, (58, 11))

		self.blocks["D21"] = Block(self, self.frame, "D21",
			[
				(self.tiles["horiz"],   self.screen,      (58, 13), False),
				(self.tiles["horiznc"], self.screen,      (59, 13), False),
				(self.tiles["horiz"],   self.screen,      (60, 13), False),
				(self.tiles["horiznc"], self.screen,      (61, 13), False),
				(self.tiles["horiz"],   self.screen,      (62, 13), False),
			], True)
		self.blocks["D21"].AddStoppingBlock([
				(self.tiles["eobleft"], self.screen,      (56, 13), False),
				(self.tiles["horiznc"], self.screen,      (57, 13), False),
			], False)
		self.blocks["D21"].AddStoppingBlock([
				(self.tiles["horiz"],    self.screen,      (64, 13), False),
				(self.tiles["eobright"], self.screen,      (65, 13), False),
			], True)
		self.blocks["D21"].AddTrainLoc(self.screen, (58, 13))

		self.blocks["DOSVJW"] = OverSwitch(self, self.frame, "DOSVJW", 
			[
				(self.tiles["eobleft"],        self.screen, (46, 9), False),
				(self.tiles["turnrightright"], self.screen, (47, 9), False),
				(self.tiles["diagright"],      self.screen, (48, 10), False),
				(self.tiles["eobleft"],        self.screen, (46, 11), False),
				(self.tiles["horiznc"],        self.screen, (47, 11), False),
				(self.tiles["horiz"],          self.screen, (48, 11), False),
				(self.tiles["horiznc"],        self.screen, (50, 11), False),
				(self.tiles["eobleft"],        self.screen, (46, 13), False),
				(self.tiles["horiznc"],        self.screen, (47, 13), False),
				(self.tiles["horiz"],          self.screen, (48, 13), False),
				(self.tiles["eobleft"],        self.screen, (46, 15), False),
				(self.tiles["turnleftright"],  self.screen, (47, 15), False),
				(self.tiles["diagleft"],       self.screen, (48, 14), False),
				(self.tiles["diagleft"],       self.screen, (50, 12), False),
				(self.tiles["horiz"],          self.screen, (53, 11), False),
				(self.tiles["horiznc"],        self.screen, (54, 11), False),
				(self.tiles["eobright"],       self.screen, (55, 11), False),
			],
			False)
		self.blocks["DOSVJW"].AddTrainLoc(self.screen, (49, 18))

		self.blocks["DOSVJE"] = OverSwitch(self, self.frame, "DOSVJE", 
			[
				(self.tiles["eobleft"],        self.screen, (46, 9), False),
				(self.tiles["turnrightright"], self.screen, (47, 9), False),
				(self.tiles["diagright"],      self.screen, (48, 10), False),
				(self.tiles["eobleft"],        self.screen, (46, 11), False),
				(self.tiles["horiznc"],        self.screen, (47, 11), False),
				(self.tiles["horiz"],          self.screen, (48, 11), False),
				(self.tiles["horiznc"],        self.screen, (50, 11), False),
				(self.tiles["eobleft"],        self.screen, (46, 13), False),
				(self.tiles["horiznc"],        self.screen, (47, 13), False),
				(self.tiles["horiz"],          self.screen, (48, 13), False),
				(self.tiles["eobleft"],        self.screen, (46, 15), False),
				(self.tiles["turnleftright"],  self.screen, (47, 15), False),
				(self.tiles["diagleft"],       self.screen, (48, 14), False),
				(self.tiles["diagleft"],       self.screen, (48, 14), False),
				(self.tiles["horiz"],          self.screen, (50, 13), False),
				(self.tiles["horiznc"],        self.screen, (51, 13), False),
				(self.tiles["horiz"],          self.screen, (52, 13), False),
				(self.tiles["horiznc"],        self.screen, (53, 13), False),
				(self.tiles["diagright"],      self.screen, (53, 12), False),
				(self.tiles["eobright"],       self.screen, (55, 13), False),
			],
			True)
		self.blocks["DOSVJE"].AddTrainLoc(self.screen, (49, 20))

		self.blocks["DOSFOE"] = OverSwitch(self, self.frame, "DOSFOE", 
			[
				(self.tiles["eobleft"],        self.screen, (66, 13), False),
				(self.tiles["horiz"],          self.screen, (68, 13), False),
				(self.tiles["horiz"],          self.screen, (69, 13), False),
				(self.tiles["eobright"],       self.screen, (70, 13), False),
				(self.tiles["diagleft"],       self.screen, (68, 12), False),
				(self.tiles["eobright"],       self.screen, (70, 11), False),
			],
			True)
		self.blocks["DOSFOE"].AddTrainLoc(self.screen, (66, 20))

		self.blocks["DOSFOW"] = OverSwitch(self, self.frame, "DOSFOW", 
			[
				(self.tiles["eobleft"],        self.screen, (66, 13), False),
				(self.tiles["diagleft"],       self.screen, (68, 12), False),
				(self.tiles["eobleft"],        self.screen, (66, 11), False),
				(self.tiles["horiz"],          self.screen, (67, 11), False),
				(self.tiles["horiz"],          self.screen, (68, 11), False),
				(self.tiles["eobright"],       self.screen, (70, 11), False),
			],
			False)
		self.blocks["DOSFOW"].AddTrainLoc(self.screen, (66, 18))

		self.osBlocks["DOSVJE"] = ["H13", "H23", "D10", "D20", "D21"]
		self.osBlocks["DOSVJW"] = ["H13", "H23", "D10", "D20", "D11"]
		self.osBlocks["DOSFOE"] = ["D21", "S10", "S20"]
		self.osBlocks["DOSFOW"] = ["S10", "D11", "D21"]

		return self.blocks, self.osBlocks

	def DefineTurnouts(self,  blocks):
		self.turnouts = {}
		
		hsList = [		
			["DSw9",  "toleftleft",   "D21", (63, 13)],
		]

		toList = [
			["DSw1",  "torightleft",  ["DOSVJE", "DOSVJW"], (49, 11)],
			["DSw5",  "toleftleft",   ["DOSVJE", "DOSVJW"], (51, 11)],
			["DSw7",  "torightleft",  ["DOSVJE", "DOSVJW"], (54, 13)],
			["DSw7b", "torightright", ["DOSVJE", "DOSVJW"], (52, 11)],
			["DSw11",  "toleftright", ["DOSFOE", "DOSFOW"], (67, 13)],
			["DSw11b", "toleftleft",  ["DOSFOE", "DOSFOW"], (69, 11)],
		]

		for tonm, tileSet, blks, pos in toList:
			trnout = Turnout(self, self.frame, tonm, self.screen, self.totiles[tileSet], pos)
			for blknm in blks:
				blocks[blknm].AddTurnout(trnout)
				trnout.AddBlock(blknm)
			self.turnouts[tonm] = trnout

		for tonm, tileSet, blknm, pos in hsList:
			trnout = Turnout(self, self.frame, tonm, self.screen, self.totiles[tileSet], pos)
			blk = blocks[blknm]
			blk.AddTurnout(trnout)
			blocks[blknm].AddTurnout(trnout)
			trnout.AddBlock(blknm)
			trnout.SetContainingBlock(blk)
			self.turnouts[tonm] = trnout

		trnout = SlipSwitch(self, self.frame, "DSw3", self.screen, self.totiles["ssright"], (49, 13))
		blocks["DOSVJE"].AddTurnout(trnout)
		blocks["DOSVJW"].AddTurnout(trnout)
		trnout.AddBlock("DOSVJE")
		trnout.AddBlock("DOSVJW")
		trnout.SetControllers(None, self.turnouts["DSw5"])
		self.turnouts["DSw3"] = trnout

		self.turnouts["DSw7"].SetPairedTurnout(self.turnouts["DSw7b"])
		self.turnouts["DSw11"].SetPairedTurnout(self.turnouts["DSw11b"])

		self.turnouts["DSw9"].SetDisabled(True)

		return self.turnouts

	def DefineSignals(self):
		self.signals = {}
		self.osProxies = {}

		sigList = [
			["D6RA",  RegAspects, True,   "right", (46, 10)],
			["D6RB",  RegAspects, True,   "right", (46, 12)],
			["D4RA",  RegAspects, True,   "rightlong", (46, 14)],
			["D4RB",  RegAspects, True,   "rightlong", (46, 16)],

			["D6L",   RegAspects, False,  "leftlong",  (55, 10)],
			["D4L",   RegAspects, False,  "leftlong",  (55, 12)],

			["D12R",  RegAspects, True,   "rightlong", (66, 12)],
			["D10R",  RegAspects, True,   "rightlong", (66, 14)],

			["D12L",  RegAspects, False,  "leftlong",  (70, 10)],
			["D10L",  RegAspects, False,  "leftlong",  (70, 12)]
		]
		for signm, atype, east, tileSet, pos in sigList:
			self.signals[signm]  = Signal(self, self.screen, self.frame, signm, atype, east, pos, self.sigtiles[tileSet])
			
		self.signals["D4RA"].SetMutexSignals(["D4RB"])
		self.signals["D4RB"].SetMutexSignals(["D4RA"])
			
		self.signals["D6RA"].SetMutexSignals(["D6RB"])
		self.signals["D6RB"].SetMutexSignals(["D6RA"])

		blockSbSigs = {
			# which signals govern stopping sections, west and east
			"D10": ("L18L", None),
			"D11": ("D6L",  "D12R"),
			"D20": (None, "D4RA"),
			"D21": ("D4L",  "D10R")
		}

		for blknm, siglist in blockSbSigs.items():
			self.blocks[blknm].SetSBSignals(siglist)

		self.blockSigs = {
			# which signals govern blocks, west and east
			"D10": ("L18L", "D6RB"),
			"D11": ("D6L",  "D12R"),
			"D20": ("L14L", "D4RA"),
			"D21": ("D4L",  "D10R")
		}

		for blknm, siglist in self.blockSigs.items():
			self.blocks[blknm].SetSignals(siglist)

		self.sigLeverMap = {
			"D4.lvr":  ["DOSVJE", "DOSVJW"],
			"D6.lvr":  ["DOSVJE", "DOSVJW"],
			"D10.lvr": ["DOSFOE", "DOSFOW"],
			"D12.lvr": ["DOSFOE", "DOSFOW"],
		}

		for sl in self.sigLeverMap:
			self.frame.AddSignalLever(sl, self)

		self.routes = {}
		self.osSignals = {}

		# FOSS and Valley Junstion interlockings
		block = self.blocks["DOSVJE"]
		self.routes["DRtH13D21"] = Route(self.screen, block, "DRtH13D21", "H13", [(46,  9), (47,  9), (48, 10), (49, 11), (50, 11), (51, 11), (52, 11), (53, 12), (54, 13), (55, 13)], "D21", [RESTRICTING, DIVERGING], ["DSw1:R", "DSw5:N", "DSw7:R"], ["D6RA", "D4L"])
		self.routes["DRtD10D21"] = Route(self.screen, block, "DRtD10D21", "D10", [(46, 11), (47, 11), (48, 11), (49, 11), (50, 11), (51, 11), (52, 11), (53, 12), (54, 13), (55, 13)], "D21", [RESTRICTING, DIVERGING], ["DSw1:N", "DSw5:N", "DSw7:R"], ["D6RB", "D4L"])
		self.routes["DRtD20D21"] = Route(self.screen, block, "DRtD20D21", "D20", [(46, 13), (47, 13), (48, 13), (49, 13), (50, 13), (51, 13), (52, 13), (53, 13), (54, 13), (55, 13)], "D21", [MAIN, RESTRICTING],      ["DSw3:N", "DSw5:N", "DSw7:N"], ["D4RA", "D4L"])
		self.routes["DRtH23D21"] = Route(self.screen, block, "DRtH23D21", "H23", [(46, 15), (47, 15), (48, 14), (49, 13), (50, 13), (51, 13), (52, 13), (53, 13), (54, 13), (55, 13)], "D21", [DIVERGING, RESTRICTING], ["DSw3:R", "DSw5:N", "DSw7:N"], ["D4RB", "D4L"])

		block = self.blocks["DOSVJW"]
		self.routes["DRtH13D11"] = Route(self.screen, block, "DRtH13D11", "D11", [(46,  9), (47,  9), (48, 10), (49, 11), (50, 11), (51, 11), (52, 11), (53, 11), (54, 11), (55, 11)], "H13", [RESTRICTING, DIVERGING], ["DSw1:R", "DSw5:N", "DSw7:N"], ["D6L", "D6RA"])
		self.routes["DRtD10D11"] = Route(self.screen, block, "DRtD10D11", "D11", [(46, 11), (47, 11), (48, 11), (49, 11), (50, 11), (51, 11), (52, 11), (53, 11), (54, 11), (55, 11)], "D10", [RESTRICTING, MAIN],      ["DSw1:N", "DSw5:N", "DSw7:N"], ["D6L", "D6RB"])
		self.routes["DRtD20D11"] = Route(self.screen, block, "DRtD20D11", "D11", [(46, 13), (47, 13), (48, 13), (49, 13), (50, 12), (51, 11), (52, 11), (53, 11), (54, 11), (55, 11)], "D20", [DIVERGING, RESTRICTING], ["DSw3:N", "DSw5:R", "DSw7:N"], ["D6L", "D4RA"])
		self.routes["DRtH23D11"] = Route(self.screen, block, "DRtH23D11", "D11", [(46, 15), (47, 15), (48, 14), (49, 13), (50, 12), (51, 11), (52, 11), (53, 11), (54, 11), (55, 11)], "H23", [DIVERGING, RESTRICTING], ["DSw3:R", "DSw5:R", "DSw7:N"], ["D6L", "D4RB"])

		block = self.blocks["DOSFOE"]
		self.routes["DRtD21S20"] = Route(self.screen, block, "DRtD21S20", "D21", [(66, 13), (67, 13), (68, 13), (69, 13), (70, 13)], "S20", [MAIN, MAIN],             ["DSw11:N"], ["D10R", "D10L"])

		block = self.blocks["DOSFOW"]
		self.routes["DRtD11S10"] = Route(self.screen, block, "DRtD11S10", "S10", [(66, 11), (67, 11), (68, 11), (69, 11), (70, 11)], "D11", [MAIN, MAIN],             ["DSw11:N"], ["D12L", "D12R"])
		self.routes["DRtD21S10"] = Route(self.screen, block, "DRtD21S10", "S10", [(66, 13), (67, 13), (68, 12), (69, 11), (70, 11)], "D21", [DIVERGING, DIVERGING],   ["DSw11:R"], ["D12L", "D10R"])

		self.signals["D4RA"].AddPossibleRoutes("DOSVJE", ["DRtD20D21"])
		self.signals["D4RA"].AddPossibleRoutes("DOSVJW", ["DRtD20D11"])
		self.signals["D4RB"].AddPossibleRoutes("DOSVJE", ["DRtH23D21"])
		self.signals["D4RB"].AddPossibleRoutes("DOSVJW", ["DRtH23D11"])
		
		self.signals["D6RA"].AddPossibleRoutes("DOSVJE", ["DRtH13D21"])
		self.signals["D6RA"].AddPossibleRoutes("DOSVJW", ["DRtH13D11"])
		self.signals["D6RB"].AddPossibleRoutes("DOSVJE", ["DRtD10D21"])
		self.signals["D6RB"].AddPossibleRoutes("DOSVJW", ["DRtD10D11"])

		self.signals["D4L"].AddPossibleRoutes("DOSVJE", ["DRtD20D21", "DRtH23D21", "DRtH13D21", "DRtD10D21"])
		self.signals["D6L"].AddPossibleRoutes("DOSVJW", ["DRtD20D11", "DRtH23D11", "DRtH13D11", "DRtD10D11"])

		self.signals["D10R"].AddPossibleRoutes("DOSFOW", ["DRtD21S10"])
		self.signals["D10R"].AddPossibleRoutes("DOSFOE", ["DRtD21S20"])
		self.signals["D12R"].AddPossibleRoutes("DOSFOW", ["DRtD11S10"])

		self.signals["D10L"].AddPossibleRoutes("DOSFOE", ["DRtD21S20"])
		self.signals["D12L"].AddPossibleRoutes("DOSFOW", ["DRtD11S10", "DRtD21S10"])

		self.osSignals["DOSVJE"] = ["D4RA", "D4RB", "D4L", "D6RA", "D6RB"]
		self.osSignals["DOSVJW"] = ["D4RA", "D4RB", "D6RA", "D6RB", "D6L"]
		self.osSignals["DOSFOE"] = ["D10R", "D10L", "D12L"]
		self.osSignals["DOSFOW"] = ["D10R", "D12R", "D12L"]
			
		p = OSProxy(self, "DOSFOE")
		self.osProxies["DOSFOE"] = p
		p.AddRoute(self.routes["DRtD21S20"])
		p.AddRoute(self.routes["DRtD21S10"])
			
		p = OSProxy(self, "DOSFOW")
		self.osProxies["DOSFOW"] = p
		p.AddRoute(self.routes["DRtD11S10"])
		p.AddRoute(self.routes["DRtD21S10"])
			
		p = OSProxy(self, "DOSVJE")
		self.osProxies["DOSVJE"] = p
		p.AddRoute(self.routes["DRtH13D21"])
		p.AddRoute(self.routes["DRtD10D21"])
		p.AddRoute(self.routes["DRtD20D21"])
		p.AddRoute(self.routes["DRtH23D21"])
		p.AddRoute(self.routes["DRtD20D11"])
		p.AddRoute(self.routes["DRtH23D11"])
			
		p = OSProxy(self, "DOSVJW")
		self.osProxies["DOSVJW"] = p
		p.AddRoute(self.routes["DRtH13D11"])
		p.AddRoute(self.routes["DRtD10D11"])
		p.AddRoute(self.routes["DRtD20D11"])
		p.AddRoute(self.routes["DRtH23D11"])
		p.AddRoute(self.routes["DRtH13D21"])
		p.AddRoute(self.routes["DRtD10D21"])

		return self.signals, self.blockSigs, self.osSignals, self.routes, self.osProxies

	def DefineHandSwitches(self):
		self.handswitches = {}

		hs = HandSwitch(self, self.screen, self.frame, self.blocks["D21"], "DSw9.hand", (63, 14), self.misctiles["handup"])
		self.blocks["D21"].AddHandSwitch(hs)
		self.handswitches["DSw9.hand"] = hs
		return self.handswitches
