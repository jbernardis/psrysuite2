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
				(self.tiles["horiz"],   self.screen,      (87, 36), True),
				(self.tiles["horiznc"], self.screen,      (86, 36), False),
				(self.tiles["horiz"],   self.screen,      (85, 36), True),
				(self.tiles["horiz"],   self.screen,      (83, 36), True),
			], False)
		self.blocks["C13"].AddStoppingBlock([
				(self.tiles["ssright"], self.screen,      (82, 36), False),
				(self.tiles["eobleft"], self.screen,      (81, 36), False),
			], True)
		self.blocks["C13"].AddStoppingBlock([
				(self.tiles["eobright"], self.screen,      (89, 36), False),
				(self.tiles["ssleft"], self.screen,      (88, 36), False),
			], False)
		self.blocks["C13"].AddTrainLoc(self.screen, (82, 36))

		self.blocks["C23"] = Block(self, self.frame, "C23",
			[
				(self.tiles["horiz"],   self.screen,      (73, 36), True),
				(self.tiles["horiznc"], self.screen,      (72, 36), False),
				(self.tiles["horiz"],   self.screen,      (71, 36), True),
				(self.tiles["horiz"],   self.screen,      (69, 36), True),
				(self.tiles["eobleft"], self.screen,      (68, 36), False),
			], False)
		self.blocks["C23"].AddStoppingBlock([
				(self.tiles["eobright"], self.screen,      (75, 36), False),
				(self.tiles["ssleft"], self.screen,      (74, 36), False),
			], False)
		self.blocks["C23"].AddTrainLoc(self.screen, (70, 36))

		self.blocks["C12"] = Block(self, self.frame, "C12",
			[
				(self.tiles["horiz"],   self.screen,      (73, 34), True),
				(self.tiles["horiznc"], self.screen,      (72, 34), False),
				(self.tiles["horiz"],   self.screen,      (71, 34), True),
				(self.tiles["horiznc"], self.screen,      (70, 34), False),
				(self.tiles["horiz"],   self.screen,      (69, 34), True),
				(self.tiles["eobleft"], self.screen,      (68, 34), False),
			], True)
		self.blocks["C12"].AddStoppingBlock([
				(self.tiles["eobright"], self.screen,      (75, 34), False),
				(self.tiles["ssleft"], self.screen,      (74, 34), False),
			], False)
		self.blocks["C12"].AddTrainLoc(self.screen, (70, 34))

		self.blocks["C22"] = Block(self, self.frame, "C22",
			[
				(self.tiles["eobleft"], self.screen,      (57, 36), False),
				(self.tiles["horiznc"], self.screen,      (58, 36), False),
				(self.tiles["horiz"],   self.screen,      (59, 36), True),
				(self.tiles["horiznc"], self.screen,      (60, 36), False),
				(self.tiles["horiz"],   self.screen,      (61, 36), True),
				(self.tiles["eobright"], self.screen,     (62, 36), False),
			], False)
		self.blocks["C22"].AddTrainLoc(self.screen, (59, 36))

		self.blocks["C11"] = Block(self, self.frame, "C11",
			[
				(self.tiles["eobright"], self.screen,    (62, 34), False),
				(self.tiles["horiznc"], self.screen,      (61, 34), False),
				(self.tiles["horiz"],   self.screen,      (60, 34), True),
				(self.tiles["horiznc"], self.screen,      (59, 34), False),
				(self.tiles["horiz"],   self.screen,      (58, 34), True),
				(self.tiles["horiznc"], self.screen,      (57, 34), False),
				(self.tiles["horiz"],   self.screen,      (56, 34), True),
				(self.tiles["horiznc"], self.screen,      (55, 34), False),
				(self.tiles["horiz"],   self.screen,      (54, 34), True),
				(self.tiles["horiznc"], self.screen,      (53, 34), False),
				(self.tiles["horiz"],   self.screen,      (52, 34), True),
				(self.tiles["turnrightleft"], self.screen, (51, 34), False),
				(self.tiles["diagright"], self.screen,     (50, 33), False),
				(self.tiles["diagright"], self.screen,     (49, 32), False),
				(self.tiles["turnleftdown"], self.screen,  (48, 31), False),

				(self.tiles["verticalnc"], self.screen,   (48, 30), False),
				(self.tiles["vertical"], self.screen,     (48, 29), False),
				(self.tiles["verticalnc"], self.screen,   (48, 28), False),
				(self.tiles["vertical"], self.screen,     (48, 27), False),
				(self.tiles["verticalnc"], self.screen,   (48, 26), False),
				(self.tiles["vertical"], self.screen,     (48, 25), False),
				(self.tiles["verticalnc"], self.screen,   (48, 24), False),
				(self.tiles["vertical"], self.screen,     (48, 23), False),

				(self.tiles["turnleftup"], self.screen,    (48, 22), False),
				(self.tiles["diagright"], self.screen,     (47, 21), False),
				(self.tiles["diagright"], self.screen,     (46, 20), False),
				(self.tiles["turnrightright"], self.screen, (45, 19), False),
				(self.tiles["eobleft"], self.screen,       (44, 19), False),
			], True)
		self.blocks["C11"].AddTrainLoc(self.screen, (54, 34))

		self.blocks["COSCLW"] = OverSwitch(self, self.frame, "COSCLW",
			[
				(self.tiles["eobright"], self.screen,      (80, 36), False),
				(self.tiles["horiznc"], self.screen,      (78, 36), False),
				(self.tiles["horiz"],   self.screen,      (77, 36), True),
				(self.tiles["eobleft"], self.screen,      (76, 36), False),
				(self.tiles["diagright"], self.screen,     (78, 35), False),
				(self.tiles["turnrightright"], self.screen, (77, 34), False),
				(self.tiles["eobleft"], self.screen,      (76, 34), False),
			], False)
		self.blocks["COSCLW"].AddTrainLoc(self.screen, (76, 29))

		self.blocks["COSCLEW"] = OverSwitch(self, self.frame, "COSCLEW",
			[
				(self.tiles["eobright"], self.screen,      (67, 36), False),
				(self.tiles["horiznc"], self.screen,      (65, 36), False),
				(self.tiles["horiz"],   self.screen,      (64, 36), True),
				(self.tiles["eobleft"], self.screen,      (63, 36), False),
			], False)
		self.blocks["COSCLEW"].AddTrainLoc(self.screen, (63, 29))

		self.blocks["COSCLEE"] = OverSwitch(self, self.frame, "COSCLEE",
			[
				(self.tiles["eobright"], self.screen,      (67, 34), False),
				(self.tiles["horiz"],   self.screen,      (66, 34), True),
				(self.tiles["horiznc"], self.screen,      (65, 34), False),
				(self.tiles["eobleft"], self.screen,      (63, 34), False),
				(self.tiles["eobright"], self.screen,      (67, 36), False),
				(self.tiles["diagright"], self.screen,     (65, 35), False),
			], True)
		self.blocks["COSCLEE"].AddTrainLoc(self.screen, (63, 28))

		self.osBlocks["COSCLW"] = ["C13", "C23", "C12"]
		self.osBlocks["COSCLEW"] = ["C23", "C22"]
		self.osBlocks["COSCLEE"] = ["C12", "C11", "C23"]

		return self.blocks, self.osBlocks

	def DefineTurnouts(self, blocks):
		self.turnouts = {}

		toList = [
			["CSw9",   "torightleft",  ["COSCLEW", "COSCLEE"], (66, 36)],
			["CSw9b",  "torightright",   ["COSCLEW", "COSCLEE"], (64, 34)],
			["CSw13",  "torightleft",  ["COSCLW"], (79, 36)],
		]

		hslist = [
			["CSw11",  "toleftleft",   "C23", (70, 36)],
			["CSw15",  "torightright",   "C13", (84, 36)],
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
			["C14L",   RegAspects, True,    "leftlong", (80, 35)],
			["C14RB",  RegAspects, False,   "rightlong", (76, 37)],
			["C14RA",  RegAspects, False,   "rightlong", (76, 35)],

			["C12L",   RegAspects, True,    "leftlong", (67, 33)],
			["C12R",   RegAspects, False,   "rightlong", (63, 35)],

			["C10L",   RegAspects, True,    "leftlong", (67, 35)],
			["C10R",   RegAspects, False,   "rightlong", (63, 37)],
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
		self.routes["CRtC13C23"] = Route(self.screen, block, "CRtC13C23", "C23", [(80, 36), (79, 36), (78, 36), (77, 36), (76, 36)], "C13", [MAIN, MAIN], ["CSw13:N"], ["C14RB", "C14L"])
		self.routes["CRtC13C12"] = Route(self.screen, block, "CRtC13C12", "C12", [(80, 36), (79, 36), (78, 35), (77, 34), (76, 34)], "C13", [DIVERGING, DIVERGING], ["CSw13:R"], ["C14RA", "C14L"])

		block = self.blocks["COSCLEW"]
		self.routes["CRtC23C22"] = Route(self.screen, block, "CRtC23C22", "C22", [(67, 36), (66, 36), (65, 36), (64, 36), (63, 36)], "C23", [MAIN, MAIN], ["CSw9:N"], ["C10R", "C10L"])

		block = self.blocks["COSCLEE"]
		self.routes["CRtC12C11"] = Route(self.screen, block, "CRtC12C11", "C12", [(67, 34), (66, 34), (65, 34), (64, 34), (63, 34)], "C11", [MAIN, MAIN], ["CSw9:N"], ["C12L", "C12R"])
		self.routes["CRtC23C11"] = Route(self.screen, block, "CRtC23C11", "C23", [(67, 36), (66, 36), (65, 35), (64, 34), (63, 34)], "C11", [DIVERGING, DIVERGING], ["CSw9:R"], ["C10L", "C12R"])

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

		hs = HandSwitch(self, self.screen, self.frame, self.blocks["C23"], "CSw11.hand", (70, 37), self.misctiles["handup"])
		self.blocks["C23"].AddHandSwitch(hs)
		self.handswitches["CSw11.hand"] = hs

		hs = HandSwitch(self, self.screen, self.frame, self.blocks["C13"], "CSw15.hand", (84, 37), self.misctiles["handup"])
		self.blocks["C13"].AddHandSwitch(hs)
		self.handswitches["CSw15.hand"] = hs

		return self.handswitches
