from dispatcher.district import District

from dispatcher.block import Block, OverSwitch, Route, OSProxy
from dispatcher.turnout import Turnout
from dispatcher.signal import Signal
from dispatcher.handswitch import HandSwitch

from dispatcher.constants import MAIN, DIVERGING, RegAspects


class Cliveden (District):
	def __init__(self, name, frame, screen):
		District.__init__(self, name, frame, screen)
		self.C13Queue = self.frame.C13Queue

	def SetUpRoute(self, osblk, route):
		osname = osblk.GetName()
		controlOpt = self.frame.cliffControl
		if (controlOpt == 1 and osname != "COSCLW") or controlOpt == 0:
			self.frame.PopupEvent("Cliveden control is local")
			return

		District.SetUpRoute(self, osblk, route)

	def DetermineRoute(self, blocks):
		self.FindTurnoutCombinations(blocks, ["CSw9", "CSw13"])

	def DefineBlocks(self):
		self.blocks = {}
		self.osBlocks = {}

		self.blocks["C13"] = Block(self, self.frame, "C13",
			[
				(self.tiles["horiz"],   self.screen,      (32, 13), False),
				(self.tiles["horiznc"], self.screen,      (33, 13), False),
				(self.tiles["horiz"],   self.screen,      (34, 13), False),
				(self.tiles["horiz"],   self.screen,      (36, 13), False),
			], False)
		self.blocks["C13"].AddStoppingBlock([
				(self.tiles["horiznc"], self.screen,      (37, 13), False),
				(self.tiles["eobright"], self.screen,      (38, 13), False),
			], True)
		self.blocks["C13"].AddStoppingBlock([
				(self.tiles["eobleft"], self.screen,      (30, 13), False),
				(self.tiles["horiznc"], self.screen,      (31, 13), False),
			], False)
		self.blocks["C13"].AddTrainLoc(self.screen, (32, 13))

		self.blocks["C23"] = Block(self, self.frame, "C23",
			[
				(self.tiles["horiz"],   self.screen,      (46, 13), False),
				(self.tiles["horiznc"], self.screen,      (47, 13), False),
				(self.tiles["horiz"],   self.screen,      (48, 13), False),
				(self.tiles["horiz"],   self.screen,      (50, 13), False),
				(self.tiles["eobright"], self.screen,      (51, 13), False),
			], False)
		self.blocks["C23"].AddStoppingBlock([
				(self.tiles["eobleft"], self.screen,      (44, 13), False),
				(self.tiles["horiznc"], self.screen,      (45, 13), False),
			], False)
		self.blocks["C23"].AddTrainLoc(self.screen, (47, 13))

		self.blocks["C12"] = Block(self, self.frame, "C12",
			[
				(self.tiles["horiz"],   self.screen,      (46, 15), False),
				(self.tiles["horiznc"], self.screen,      (47, 15), False),
				(self.tiles["horiz"],   self.screen,      (48, 15), False),
				(self.tiles["horiznc"], self.screen,      (49, 15), False),
				(self.tiles["horiz"],   self.screen,      (50, 15), False),
				(self.tiles["eobright"], self.screen,      (51, 15), False),
			], True)
		self.blocks["C12"].AddStoppingBlock([
				(self.tiles["eobleft"], self.screen,      (44, 15), False),
				(self.tiles["horiznc"], self.screen,      (45, 15), False),
			], False)
		self.blocks["C12"].AddTrainLoc(self.screen, (46, 15))

		self.blocks["C22"] = Block(self, self.frame, "C22",
			[
				(self.tiles["eobleft"], self.screen,      (57, 13), False),
				(self.tiles["horiznc"], self.screen,      (58, 13), False),
				(self.tiles["horiz"],   self.screen,      (59, 13), False),
				(self.tiles["horiznc"], self.screen,      (60, 13), False),
				(self.tiles["horiz"],   self.screen,      (61, 13), False),
				(self.tiles["eobright"], self.screen,      (62, 13), False),
			], False)
		self.blocks["C22"].AddTrainLoc(self.screen, (59, 13))

		self.blocks["C11"] = Block(self, self.frame, "C11",
			[
				(self.tiles["eobleft"], self.screen,      (57, 15), False),
				(self.tiles["horiznc"], self.screen,      (58, 15), False),
				(self.tiles["horiz"],   self.screen,      (59, 15), False),
				(self.tiles["horiznc"], self.screen,      (60, 15), False),
				(self.tiles["horiz"],   self.screen,      (61, 15), False),
				(self.tiles["horiznc"], self.screen,      (62, 15), False),
				(self.tiles["horiz"],   self.screen,      (63, 15), False),
				(self.tiles["horiznc"], self.screen,      (64, 15), False),
				(self.tiles["horiz"],   self.screen,      (65, 15), False),
				(self.tiles["horiznc"], self.screen,      (66, 15), False),
				(self.tiles["horiz"],   self.screen,      (67, 15), False),
				(self.tiles["turnrightright"], self.screen, (68, 15), False),
				(self.tiles["diagright"], self.screen,     (69, 16), False),
				(self.tiles["diagright"], self.screen,     (70, 17), False),
				(self.tiles["turnleftup"], self.screen,    (71, 18), False),
				(self.tiles["verticalnc"], self.screen,    (71, 19), True),
				(self.tiles["vertical"], self.screen,     (71, 20), True),
				(self.tiles["verticalnc"], self.screen,    (71, 21), True),
				(self.tiles["vertical"], self.screen,     (71, 22), True),
				(self.tiles["verticalnc"], self.screen,    (71, 23), True),
				(self.tiles["vertical"], self.screen,     (71, 24), True),
				(self.tiles["verticalnc"], self.screen,    (71, 25), True),
				(self.tiles["vertical"], self.screen,     (71, 26), True),
				(self.tiles["turnleftdown"], self.screen,  (71, 27), False),
				(self.tiles["diagright"], self.screen,     (72, 28), False),
				(self.tiles["diagright"], self.screen,     (73, 29), False),
				(self.tiles["turnrightleft"], self.screen, (74, 30), False),
				(self.tiles["eobright"], self.screen,      (75, 30), False),
			], True)
		self.blocks["C11"].AddTrainLoc(self.screen, (59, 15))

		self.blocks["COSCLW"] = OverSwitch(self, self.frame, "COSCLW",
			[
				(self.tiles["eobleft"], self.screen,      (39, 13), False),
				(self.tiles["horiznc"], self.screen,      (41, 13), False),
				(self.tiles["horiz"],   self.screen,      (42, 13), False),
				(self.tiles["eobright"], self.screen,      (43, 13), False),
				(self.tiles["diagright"], self.screen,     (41, 14), False),
				(self.tiles["turnrightleft"], self.screen, (42, 15), False),
				(self.tiles["eobright"], self.screen,      (43, 15), False),
			], False)
		self.blocks["COSCLW"].AddTrainLoc(self.screen, (39, 19))

		self.blocks["COSCLEW"] = OverSwitch(self, self.frame, "COSCLEW",
			[
				(self.tiles["eobleft"], self.screen,      (52, 13), False),
				(self.tiles["horiznc"], self.screen,      (54, 13), False),
				(self.tiles["horiz"],   self.screen,      (55, 13), False),
				(self.tiles["eobright"], self.screen,      (56, 13), False),
			], False)
		self.blocks["COSCLEW"].AddTrainLoc(self.screen, (52, 19))

		self.blocks["COSCLEE"] = OverSwitch(self, self.frame, "COSCLEE",
			[
				(self.tiles["eobleft"], self.screen,      (52, 15), False),
				(self.tiles["horiz"],   self.screen,      (53, 15), False),
				(self.tiles["horiznc"], self.screen,      (54, 15), False),
				(self.tiles["eobright"], self.screen,      (56, 15), False),
				(self.tiles["eobleft"], self.screen,      (52, 13), False),
				(self.tiles["diagright"], self.screen,     (54, 14), False),
			], True)
		self.blocks["COSCLEE"].AddTrainLoc(self.screen, (52, 21))

		self.osBlocks["COSCLW"] = ["C13", "C23", "C12"]
		self.osBlocks["COSCLEW"] = ["C23", "C22"]
		self.osBlocks["COSCLEE"] = ["C12", "C11", "C23"]

		return self.blocks, self.osBlocks

	def DefineTurnouts(self, blocks):
		self.turnouts = {}

		toList = [
			["CSw9",   "torightright",  ["COSCLEW", "COSCLEE"], (53, 13)],
			["CSw9b",  "torightleft",   ["COSCLEW", "COSCLEE"], (55, 15)],
			["CSw13",  "torightright",  ["COSCLW"], (40, 13)],
		]

		hslist = [
			["CSw11",  "toleftright",   "C23", (49, 13)],
			["CSw15",  "torightleft",   "C13", (35, 13)],
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

		self.turnouts["CSw9"].SetPairedTurnout(self.turnouts["CSw9b"])

		self.turnouts["CSw11"].SetDisabled(True)
		self.turnouts["CSw15"].SetDisabled(True)

		return self.turnouts

	def DefineSignals(self):
		self.signals = {}
		self.osProxies = {}

		sigList = [
			["C14L",   RegAspects, True,    "rightlong", (39, 14)],
			["C14RB",  RegAspects, False,   "leftlong", (43, 12)],
			["C14RA",  RegAspects, False,   "leftlong", (43, 14)],

			["C12L",   RegAspects, True,    "rightlong", (52, 16)],
			["C12R",   RegAspects, False,   "leftlong", (56, 14)],

			["C10L",   RegAspects, True,    "rightlong", (52, 14)],
			["C10R",   RegAspects, False,   "leftlong", (56, 12)],
		]
		for signm, atype, east, tileSet, pos in sigList:
			self.signals[signm]  = Signal(self, self.screen, self.frame, signm, atype, east, pos, self.sigtiles[tileSet])

		self.signals["C14RA"].SetMutexSignals(["C14RB"])
		self.signals["C14RB"].SetMutexSignals(["C14RA"])

		self.sigLeverMap = {
			"C10.lvr": ["COSCLEW", "COSCLEE"],
			"C12.lvr": ["COSCLEE"],
			"C14.lvr": ["COSCLW"],
		}

		for sl in self.sigLeverMap:
			self.frame.AddSignalLever(sl, self)

		blockSbSigs = {
			# # which signals govern stopping sections, west and east
			"C13": ("C18R",  "C14L"),
			"C23": ("C14RB", None),
			"C12": ("C14RA", None),
		}

		for blknm, siglist in blockSbSigs.items():
			self.blocks[blknm].SetSBSignals(siglist)

		self.blockSigs = {
			# # which signals govern blocks, west and east
			"C11": ("C12R",  "C4L"),
			"C12": ("C14RA", "C12L"),
			"C13": ("C18R",  "C14L"),
			"C22": ("C10R",  "C8L"),
			"C23": ("C14RB", "C10L"),
		}

		for blknm, siglist in self.blockSigs.items():
			self.blocks[blknm].SetSignals(siglist)

		self.routes = {}
		self.osSignals = {}

		block = self.blocks["COSCLW"]
		self.routes["CRtC13C23"] = Route(self.screen, block, "CRtC13C23", "C23", [(39, 13), (40, 13), (41, 13), (42, 13), (43, 13)], "C13", [MAIN, MAIN], ["CSw13:N"], ["C14RB", "C14L"])
		self.routes["CRtC13C12"] = Route(self.screen, block, "CRtC13C12", "C12", [(39, 13), (40, 13), (41, 14), (42, 15), (43, 15)], "C13", [DIVERGING, DIVERGING], ["CSw13:R"], ["C14RA", "C14L"])

		block = self.blocks["COSCLEW"]
		self.routes["CRtC23C22"] = Route(self.screen, block, "CRtC23C22", "C22", [(52, 13), (53, 13), (54, 13), (55, 13), (56, 13)], "C23", [MAIN, MAIN], ["CSw9:N"], ["C10R", "C10L"])

		block = self.blocks["COSCLEE"]
		self.routes["CRtC12C11"] = Route(self.screen, block, "CRtC12C11", "C12", [(52, 15), (53, 15), (54, 15), (55, 15), (56, 15)], "C11", [MAIN, MAIN], ["CSw9:N"], ["C12L", "C12R"])
		self.routes["CRtC23C11"] = Route(self.screen, block, "CRtC23C11", "C23", [(52, 13), (53, 13), (54, 14), (55, 15), (56, 15)], "C11", [DIVERGING, DIVERGING], ["CSw9:R"], ["C10L", "C12R"])

		self.signals["C14L"].AddPossibleRoutes("COSCLW", ["CRtC13C23", "CRtC13C12"])
		self.signals["C14RA"].AddPossibleRoutes("COSCLW", ["CRtC13C12"])
		self.signals["C14RB"].AddPossibleRoutes("COSCLW", ["CRtC13C23"])

		self.signals["C12L"].AddPossibleRoutes("COSCLEE", ["CRtC12C11"])
		self.signals["C12R"].AddPossibleRoutes("COSCLEE", ["CRtC12C11", "CRtC23C11"])

		self.signals["C10L"].AddPossibleRoutes("COSCLEW", ["CRtC23C22"])
		self.signals["C10L"].AddPossibleRoutes("COSCLEE", ["CRtC23C11"])
		self.signals["C10R"].AddPossibleRoutes("COSCLEW", ["CRtC23C22"])

		self.osSignals["COSCLW"] = ["C14L", "C14RA", "C14RB"]
		self.osSignals["COSCLEW"] = ["C10L", "C10R", "C12R"]
		self.osSignals["COSCLEE"] = ["C12L", "C12R", "C10L"]

		p = OSProxy(self, "COSCLEW")
		self.osProxies["COSCLEW"] = p
		p.AddRoute(self.routes["CRtC23C22"])
		p.AddRoute(self.routes["CRtC23C11"])

		p = OSProxy(self, "COSCLEE")
		self.osProxies["COSCLEE"] = p
		p.AddRoute(self.routes["CRtC12C11"])
		p.AddRoute(self.routes["CRtC23C11"])

		return self.signals, self.blockSigs, self.osSignals, self.routes, self.osProxies

	def DefineHandSwitches(self):
		self.handswitches = {}

		hs = HandSwitch(self, self.screen, self.frame, self.blocks["C23"], "CSw11.hand", (49, 12), self.misctiles["handdown"])
		self.blocks["C23"].AddHandSwitch(hs)
		self.handswitches["CSw11.hand"] = hs

		hs = HandSwitch(self, self.screen, self.frame, self.blocks["C13"], "CSw15.hand", (35, 12), self.misctiles["handdown"])
		self.blocks["C13"].AddHandSwitch(hs)
		self.handswitches["CSw15.hand"] = hs

		return self.handswitches
