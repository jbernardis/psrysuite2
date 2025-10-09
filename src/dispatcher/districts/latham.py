from dispatcher.district import District

from dispatcher.block import Block, OverSwitch, Route, OSProxy
from dispatcher.turnout import Turnout
from dispatcher.signal import Signal
from dispatcher.handswitch import HandSwitch

from dispatcher.constants import HyYdPt, RESTRICTING, MAIN, DIVERGING, RegAspects, AdvAspects


class Latham (District):
	def __init__(self, name, frame, screen):
		District.__init__(self, name, frame, screen)

	def DetermineRoute(self, blocks):
		s3 = 'N' if self.turnouts["LSw3"].IsNormal() else 'R'
		s5 = 'N' if self.turnouts["LSw5"].IsNormal() else 'R'
		s7 = 'N' if self.turnouts["LSw7"].IsNormal() else 'R'
		s9 = 'N' if self.turnouts["LSw9"].IsNormal() else 'R'
		self.turnouts["LSw3"].SetLock(s9 == 'R', "LSw9", refresh=True)
		self.turnouts["LSw3b"].SetLock(s9 == 'R', "LSw9", refresh=True)
		self.turnouts["LSw9"].SetLock(s3 == 'R', "LSw3", refresh=True)
		self.turnouts["LSw9b"].SetLock(s3 == 'R', "LSw3", refresh=True)
		self.turnouts["LSw5"].SetLock(s7 == 'R', "LSw7", refresh=True)
		self.turnouts["LSw5b"].SetLock(s7 == 'R', "LSw7", refresh=True)
		self.turnouts["LSw7"].SetLock(s5 == 'R', "LSw5", refresh=True)
		self.turnouts["LSw7b"].SetLock(s5 == 'R', "LSw5", refresh=True)

		self.FindTurnoutCombinations(blocks, ["LSw1", "LSw3", "LSw5", "LSw7", "LSw9", "LSw15", "LSw17"])

	def DefineBlocks(self):
		self.blocks = {}
		self.osBlocks = {}

		self.blocks["L10"] = Block(self, self.frame, "L10",
			[
				(self.tiles["horiznc"], HyYdPt,      (140, 11), False),
				(self.tiles["horiz"],   HyYdPt,      (141, 11), False),
				(self.tiles["horiznc"], HyYdPt,      (142, 11), False),
				(self.tiles["horiz"],   HyYdPt,      (143, 11), False),
				(self.tiles["horiznc"], HyYdPt,      (144, 11), False),
				(self.tiles["horiz"],   HyYdPt,      (145, 11), False),
				(self.tiles["horiznc"], HyYdPt,      (146, 11), False),
				(self.tiles["horiz"],   HyYdPt,      (147, 11), False),
				(self.tiles["horiznc"], HyYdPt,      (148, 11), False),
				(self.tiles["horiz"],   HyYdPt,      (149, 11), False),
				(self.tiles["horiznc"], HyYdPt,      (150, 11), False),
				(self.tiles["horiz"],   HyYdPt,      (151, 11), False),
				(self.tiles["horiznc"], HyYdPt,      (152, 11), False),
				(self.tiles["horiz"],   HyYdPt,      (153, 11), False),
				(self.tiles["horiznc"], HyYdPt,      (154, 11), False),
				(self.tiles["horiz"],   HyYdPt,      (155, 11), False),
				(self.tiles["horiznc"], HyYdPt,      (156, 11), False),
				(self.tiles["horiz"],   HyYdPt,      (157, 11), False),
				(self.tiles["horiznc"], HyYdPt,      (158, 11), False),
				(self.tiles["horiznc"],  self.screen, (0, 11), False),
				(self.tiles["horiz"],    self.screen, (1, 11), False),
				(self.tiles["horiznc"],  self.screen, (2, 11), False),
				(self.tiles["horiz"],    self.screen, (3, 11), False),
				(self.tiles["horiznc"],  self.screen, (4, 11), False),
				(self.tiles["horiz"],    self.screen, (5, 11), False),
				(self.tiles["horiznc"],  self.screen, (6, 11), False),
				(self.tiles["eobright"], self.screen, (7, 11), False),
			], False)
		self.blocks["L10"].AddStoppingBlock([
				(self.tiles["horiz"],   HyYdPt,      (137, 11), False),
				(self.tiles["horiznc"], HyYdPt,      (138, 11), False),
				(self.tiles["horiz"],   HyYdPt,      (139, 11), False),
			], False)
		self.blocks["L10"].AddTrainLoc(self.screen, (1, 11))
		self.blocks["L10"].AddTrainLoc(HyYdPt, (141, 11))

		self.blocks["L20"] = Block(self, self.frame, "L20",
			[
				(self.tiles["horiz"],   HyYdPt,      (137, 13), False),
				(self.tiles["horiznc"], HyYdPt,      (138, 13), False),
				(self.tiles["horiz"],   HyYdPt,      (139, 13), False),
				(self.tiles["horiznc"], HyYdPt,      (140, 13), False),
				(self.tiles["horiz"],   HyYdPt,      (141, 13), False),
				(self.tiles["horiznc"], HyYdPt,      (142, 13), False),
				(self.tiles["horiz"],   HyYdPt,      (143, 13), False),
				(self.tiles["horiznc"], HyYdPt,      (144, 13), False),
				(self.tiles["horiz"],   HyYdPt,      (145, 13), False),
				(self.tiles["horiznc"], HyYdPt,      (146, 13), False),
				(self.tiles["horiz"],   HyYdPt,      (147, 13), False),
				(self.tiles["horiznc"], HyYdPt,      (148, 13), False),
				(self.tiles["horiz"],   HyYdPt,      (149, 13), False),
				(self.tiles["horiznc"], HyYdPt,      (150, 13), False),
				(self.tiles["horiz"],   HyYdPt,      (151, 13), False),
				(self.tiles["horiznc"], HyYdPt,      (152, 13), False),
				(self.tiles["horiz"],   HyYdPt,      (153, 13), False),
				(self.tiles["horiznc"], HyYdPt,      (154, 13), False),
				(self.tiles["horiz"],   HyYdPt,      (155, 13), False),
				(self.tiles["horiznc"], HyYdPt,      (156, 13), False),
				(self.tiles["horiz"],   HyYdPt,      (157, 13), False),
				(self.tiles["horiznc"], HyYdPt,      (158, 13), False),
				(self.tiles["horiznc"], self.screen, (0, 13), False),
				(self.tiles["horiz"],   self.screen, (1, 13), False),
				(self.tiles["horiznc"], self.screen, (2, 13), False),
				(self.tiles["horiz"],   self.screen, (3, 13), False),
				(self.tiles["horiznc"], self.screen, (4, 13), False),
			], True)
		self.blocks["L20"].AddStoppingBlock([
				(self.tiles["horiz"],    self.screen, (5, 13), False),
				(self.tiles["horiznc"],  self.screen, (6, 13), False),
				(self.tiles["eobright"], self.screen, (7, 13), False),
			], True)
		self.blocks["L20"].AddTrainLoc(self.screen, (1, 13))
		self.blocks["L20"].AddTrainLoc(HyYdPt, (141, 13))

		self.blocks["L11"] = Block(self, self.frame, "L11",
			[
				(self.tiles["horiznc"],   self.screen, (24, 11), False),
				(self.tiles["horiz"],     self.screen, (25, 11), False),
				(self.tiles["horiznc"],   self.screen, (26, 11), False),
				(self.tiles["horiz"],     self.screen, (27, 11), False),
				(self.tiles["horiznc"],   self.screen, (28, 11), False),
				(self.tiles["eobright"],  self.screen, (29, 11), False),
			], False)
		self.blocks["L11"].AddStoppingBlock([
				(self.tiles["eobleft"],   self.screen, (21, 11), False),
				(self.tiles["horiznc"],   self.screen, (22, 11), False),
			], False)
		self.blocks["L11"].AddTrainLoc(self.screen, (24, 11))

		self.blocks["L21"] = Block(self, self.frame, "L21",
			[
				(self.tiles["horiznc"],   self.screen, (24, 13), False),
				(self.tiles["horiz"],     self.screen, (25, 13), False),
				(self.tiles["horiznc"],   self.screen, (26, 13), False),
			], True)
		self.blocks["L21"].AddStoppingBlock([
				(self.tiles["eobleft"],   self.screen, (21, 13), False),
				(self.tiles["horiznc"],   self.screen, (22, 13), False),
				(self.tiles["horiz"],     self.screen, (23, 13), False),
			], False)
		self.blocks["L21"].AddStoppingBlock([
				(self.tiles["horiz"],     self.screen, (27, 13), False),
				(self.tiles["horiznc"],   self.screen, (28, 13), False),
				(self.tiles["eobright"],  self.screen, (29, 13), False),
			], True)
		self.blocks["L21"].AddTrainLoc(self.screen, (24, 13))

		self.blocks["L31"] = Block(self, self.frame, "L31",
			[
				(self.tiles["eobleft"],   self.screen, (21, 15), False),
				(self.tiles["horiznc"],   self.screen, (22, 15), False),
				(self.tiles["horiz"],     self.screen, (23, 15), False),
				(self.tiles["horiznc"],   self.screen, (24, 15), False),
				(self.tiles["horiz"],     self.screen, (25, 15), False),
				(self.tiles["horiznc"],   self.screen, (26, 15), False),
			], True)
		self.blocks["L31"].AddStoppingBlock([
				(self.tiles["horiznc"],   self.screen, (28, 15), False),
				(self.tiles["eobright"],  self.screen, (29, 15), False),
			], True)
		self.blocks["L31"].AddTrainLoc(self.screen, (22, 15))

		self.blocks["LOSLAW"] = OverSwitch(self, self.frame, "LOSLAW", 
			[
				(self.tiles["eobleft"],   self.screen, (8, 11), False),
				(self.tiles["horiznc"],   self.screen, (9, 11), False),
				(self.tiles["horiz"],     self.screen, (10, 11), False),
				(self.tiles["horiznc"],   self.screen, (11, 11), False),
				(self.tiles["horiz"],     self.screen, (12, 11), False),
				(self.tiles["horiz"],     self.screen, (14, 11), False),
				(self.tiles["horiznc"],   self.screen, (15, 11), False),
				(self.tiles["horiz"],     self.screen, (16, 11), False),
				(self.tiles["horiznc"],   self.screen, (17, 11), False),
				(self.tiles["horiznc"],   self.screen, (19, 11), False),
				(self.tiles["eobright"],  self.screen, (20, 11), False),
				(self.tiles["diagright"], self.screen, (14, 12), False),
				(self.tiles["diagleft"],  self.screen, (17, 12), False),
				(self.tiles["horiz"],     self.screen, (18, 13), False),
				(self.tiles["horiznc"],   self.screen, (19, 13), False),
				(self.tiles["eobright"],  self.screen, (20, 13), False),
				(self.tiles["diagright"], self.screen, (18, 14), False),
				(self.tiles["eobright"],  self.screen, (20, 15), False),
			],
			False)
		self.blocks["LOSLAW"].AddTrainLoc(self.screen, (13, 18))

		self.blocks["LOSLAM"] = OverSwitch(self, self.frame, "LOSLAM", 
			[
				(self.tiles["eobleft"],   self.screen, (8, 13), False),
				(self.tiles["horiznc"],   self.screen, (9, 13), False),
				(self.tiles["horiz"],     self.screen, (10, 13), False),
				(self.tiles["horiz"],     self.screen, (12, 13), False),
				(self.tiles["horiznc"],   self.screen, (13, 13), False),
				(self.tiles["horiz"],     self.screen, (18, 13), False),
				(self.tiles["horiznc"],   self.screen, (19, 13), False),
				(self.tiles["eobright"],  self.screen, (20, 13), False),
				(self.tiles["diagleft"],  self.screen, (17, 12), False),
				(self.tiles["horiznc"],   self.screen, (19, 11), False),
				(self.tiles["eobright"],  self.screen, (20, 11), False),
				(self.tiles["diagright"], self.screen, (18, 14), False),
				(self.tiles["eobright"],  self.screen, (20, 15), False),
				(self.tiles["eobleft"],   self.screen, (8, 15), False),
				(self.tiles["turnleftright"], self.screen, (9, 15), False),
				(self.tiles["diagleft"],   self.screen, (10, 14), False),
			],
			True)
		self.blocks["LOSLAM"].AddTrainLoc(self.screen, (13, 20))

		self.blocks["LOSLAE"] = OverSwitch(self, self.frame, "LOSLAE", 
			[
				(self.tiles["eobleft"],   self.screen, (8, 17), False),
				(self.tiles["horiznc"],   self.screen, (9, 17), False),
				(self.tiles["turnleftright"], self.screen, (10, 17), False),
				(self.tiles["diagleft"],   self.screen, (11, 16), False),
				(self.tiles["horiznc"],   self.screen, (13, 15), False),
				(self.tiles["horiz"],     self.screen, (14, 15), False),
				(self.tiles["horiznc"],   self.screen, (15, 15), False),
				(self.tiles["horiz"],     self.screen, (16, 15), False),
				(self.tiles["horiznc"],   self.screen, (17, 15), False),
				(self.tiles["horiz"],     self.screen, (18, 15), False),
				(self.tiles["eobright"],  self.screen, (20, 15), False),
				(self.tiles["diagleft"],  self.screen, (13, 14), False),
				(self.tiles["horiz"],     self.screen, (18, 13), False),
				(self.tiles["horiznc"],   self.screen, (19, 13), False),
				(self.tiles["eobright"],  self.screen, (20, 13), False),
				(self.tiles["diagleft"],  self.screen, (17, 12), False),
				(self.tiles["horiznc"],   self.screen, (19, 11), False),
				(self.tiles["eobright"],  self.screen, (20, 11), False),
				(self.tiles["diagright"], self.screen, (18, 14), False),
				(self.tiles["eobright"],  self.screen, (20, 15), False),
			],
			True)
		self.blocks["LOSLAE"].AddTrainLoc(self.screen, (13, 22))

		self.blocks["LOSCAW"] = OverSwitch(self, self.frame, "LOSCAW", 
			[
				(self.tiles["eobleft"],   self.screen, (30, 11), False),
				(self.tiles["horiznc"],   self.screen, (31, 11), False),
				(self.tiles["horiz"],     self.screen, (32, 11), False),
				(self.tiles["horiz"],     self.screen, (34, 11), False),
				(self.tiles["eobright"],  self.screen, (35, 11), False),
			], 
			False)
		self.blocks["LOSCAW"].AddTrainLoc(self.screen, (31, 18))

		self.blocks["LOSCAM"] = OverSwitch(self, self.frame, "LOSCAM", 
			[
				(self.tiles["eobleft"],   self.screen, (30, 13), False),
				(self.tiles["horiz"],     self.screen, (32, 13), False),
				(self.tiles["horiznc"],   self.screen, (33, 13), False),
				(self.tiles["eobright"],  self.screen, (35, 13), False),
				(self.tiles["diagleft"],  self.screen, (32, 12), False),
				(self.tiles["horiz"],     self.screen, (34, 11), False),
				(self.tiles["eobright"],  self.screen, (35, 11), False),
			], 
			True)
		self.blocks["LOSCAM"].AddTrainLoc(self.screen, (31, 20))

		self.blocks["LOSCAE"] = OverSwitch(self, self.frame, "LOSCAE", 
			[
				(self.tiles["eobleft"],   self.screen, (30, 15), False),
				(self.tiles["horiznc"],   self.screen, (31, 15), False),
				(self.tiles["turnleftright"], self.screen, (32, 15), False),
				(self.tiles["diagleft"],  self.screen, (33, 14), False),
				(self.tiles["eobright"],  self.screen, (35, 13), False),
			], 
			True)
		self.blocks["LOSCAE"].AddTrainLoc(self.screen, (31, 22))

		self.osBlocks["LOSLAW"] = ["L10", "L11", "L21", "L31"]
		self.osBlocks["LOSLAM"] = ["L20", "P11", "L11", "L21", "L31"]
		self.osBlocks["LOSLAE"] = ["P21", "L11", "L21", "L31"]

		self.osBlocks["LOSCAW"] = ["L11", "D10"]
		self.osBlocks["LOSCAM"] = ["L21", "D10", "D20"]
		self.osBlocks["LOSCAE"] = ["L31", "D20"]

		return self.blocks, self.osBlocks

	def DefineTurnouts(self, blocks):
		self.turnouts = {}

		toList = [
			["LSw1",  "toleftleft",   ["LOSLAM"], (11, 13)],
			["LSw3",  "toleftleft",   ["LOSLAM", "LOSLAE"], (14, 13)],
			["LSw3b", "torightupinv", ["LOSLAM", "LOSLAE"], (12, 15)],
			["LSw5",  "torightright", ["LOSLAW"], (13, 11)],
			["LSw5b", "torightleft",  ["LOSLAW", "LOSLAM", "LOSLAE"], (15, 13)],
			["LSw7",  "toleftleft",   ["LOSLAW", "LOSLAM", "LOSLAE"], (18, 11)],
			["LSw7b", "toleftright",  ["LOSLAW", "LOSLAM", "LOSLAE"], (16, 13)],
			["LSw9",  "torightright", ["LOSLAW", "LOSLAM", "LOSLAE"], (17, 13)],
			["LSw9b", "torightleft",  ["LOSLAW", "LOSLAM", "LOSLAE"], (19, 15)],

			["LSw15",  "toleftleft",  ["LOSCAW", "LOSCAM"], (33, 11)],
			["LSw15b", "toleftright", ["LOSCAM"], (31, 13)],
			["LSw17",  "toleftleft",  ["LOSCAM", "LOSCAE"], (34, 13)],
		]
		
		hsList = [
			["LSw11", "toleftright",  "L11", (23, 11)],
			["LSw13", "toleftleft",   "L31", (27, 15)],
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
			trnout.AddBlock(blknm)
			trnout.SetContainingBlock(blk)
			self.turnouts[tonm] = trnout

		self.turnouts["LSw3"].SetPairedTurnout(self.turnouts["LSw3b"])
		self.turnouts["LSw5"].SetPairedTurnout(self.turnouts["LSw5b"])
		self.turnouts["LSw7"].SetPairedTurnout(self.turnouts["LSw7b"])
		self.turnouts["LSw9"].SetPairedTurnout(self.turnouts["LSw9b"])
		self.turnouts["LSw15"].SetPairedTurnout(self.turnouts["LSw15b"])

		self.turnouts["LSw11"].SetDisabled(True)
		self.turnouts["LSw13"].SetDisabled(True)

		return self.turnouts

	def DefineSignals(self):
		self.signals = {}
		self.osProxies = {}

		sigList = [
			["L8R",  RegAspects, True,    "right", (8, 12)],
			["L6RA", RegAspects, True,    "rightlong", (8, 14)],
			["L6RB", RegAspects, True,    "right", (8, 16)],
			["L4R",  RegAspects, True,    "rightlong", (8, 18)],

			["L8L",  RegAspects, False,   "leftlong",  (20, 10)],
			["L6L",  RegAspects, False,   "leftlong",  (20, 12)],
			["L4L",  RegAspects, False,   "left",  (20, 14)],

			["L18R", RegAspects, True,    "right", (30, 12)],
			["L16R", RegAspects, True,    "rightlong", (30, 14)],
			["L14R", RegAspects, True,    "rightlong", (30, 16)],

			["L18L", AdvAspects, False,   "leftlong",  (35, 10)],
			["L14L", RegAspects, False,   "left",  (35, 12)]
		]
		for signm, atype, east, tileSet, pos in sigList:
			self.signals[signm]  = Signal(self, self.screen, self.frame, signm, atype, east, pos, self.sigtiles[tileSet])

		self.sigLeverMap = {
			"L4.lvr":  ["LOSLAW", "LOSLAM", "LOSLAE"],
			"L6.lvr":  ["LOSLAW", "LOSLAM", "LOSLAE"],
			"L8.lvr":  ["LOSLAW", "LOSLAM", "LOSLAE"],
			"L14.lvr": ["LOSCAE", "LOSCAM"],
			"L16.lvr": ["LOSCAM"],
			"L18.lvr": ["LOSCAM", "LOSCAW"],
		}

		for sl in self.sigLeverMap:
			self.frame.AddSignalLever(sl, self)

		self.signals["L6RA"].SetMutexSignals(["L6RB"])
		self.signals["L6RB"].SetMutexSignals(["L6RA"])

		blockSbSigs = {
			# which signals govern stopping sections, west and east
			"L10": ("Y2R",  None),
			"L11": ("L8L",  None),
			"L20": (None, "L6RA"),
			"L21": ("L6L",  "L16R"),
			"L31": (None,  "L14R")
		}

		for blknm, siglist in blockSbSigs.items():
			self.blocks[blknm].SetSBSignals(siglist)

		self.blockSigs = {
			# which signals govern blocks, west and east
			"L10": ("Y2R",  "L8R"),
			"L11": ("L8L",  "L18R"),
			"L20": ("Y4RB", "L6RA"),
			"L21": ("L6L",  "L16R"),
			"L31": ("L4L",  "L14R")
		}

		for blknm, siglist in self.blockSigs.items():
			self.blocks[blknm].SetSignals(siglist)

		self.routes = {}
		self.osSignals = {}

		# latham OS
		block = self.blocks["LOSLAW"]
		self.routes["LRtL10L11"] = Route(self.screen, block, "LRtL10L11", "L11", [(8, 11), (9, 11), (10, 11), (11, 11), (12, 11), (13, 11), (14, 11), (15, 11), (16, 11), (17, 11), (18, 11), (19, 11), (20, 11)], "L10", [RESTRICTING, MAIN], ["LSw5:N", "LSw7:N"], ["L8L", "L8R"])
		self.routes["LRtL10L21"] = Route(self.screen, block, "LRtL10L21", "L21",   [(8, 11), (9, 11), (10, 11), (11, 11), (12, 11), (13, 11), (14, 12), (15, 13), (16, 13), (17, 13), (18, 13), (19, 13), (20, 13)], "L10", [RESTRICTING, DIVERGING], ["LSw5:R", "LSw7:N", "LSw9:N"], ["L6L", "L8R"])
		self.routes["LRtL10L31"] = Route(self.screen, block, "LRtL10L31", "L31",   [(8, 11), (9, 11), (10, 11), (11, 11), (12, 11), (13, 11), (14, 12), (15, 13), (16, 13), (17, 13), (18, 14), (19, 15), (20, 15)], "L10", [RESTRICTING, DIVERGING], ["LSw5:R", "LSw7:N", "LSw9:R"], ["L4L", "L8R"])

		block = self.blocks["LOSLAM"]
		self.routes["LRtL20L11"] = Route(self.screen, block, "LRtL20L11", "L20", [(8, 13), (9, 13), (10, 13), (11, 13), (12, 13), (13, 13), (14, 13), (15, 13), (16, 13), (17, 12), (18, 11), (19, 11), (20, 11)], "L11", [RESTRICTING, RESTRICTING], ["LSw1:N", "LSw3:N", "LSw5:N", "LSw7:R"], ["L6RA", "L8L"])
		self.routes["LRtP11L11"] = Route(self.screen, block, "LRtP11L11", "P11", [(8, 15), (9, 15), (10, 14), (11, 13), (12, 13), (13, 13), (14, 13), (15, 13), (16, 13), (17, 12), (18, 11), (19, 11), (20, 11)], "L11", [RESTRICTING, DIVERGING], ["LSw1:R", "LSw3:N", "LSw5:N", "LSw7:R"], ["L6RB", "L8L"])
		self.routes["LRtL20L21"] = Route(self.screen, block, "LRtL20L21", "L20", [(8, 13), (9, 13), (10, 13), (11, 13), (12, 13), (13, 13), (14, 13), (15, 13), (16, 13), (17, 13), (18, 13), (19, 13), (20, 13)], "L21", [MAIN, RESTRICTING], ["LSw1:N", "LSw3:N", "LSw5:N", "LSw7:N", "LSw9:N"], ["L6RA", "L6L"])
		self.routes["LRtP11L21"] = Route(self.screen, block, "LRtP11L21", "P11", [(8, 15), (9, 15), (10, 14), (11, 13), (12, 13), (13, 13), (14, 13), (15, 13), (16, 13), (17, 13), (18, 13), (19, 13), (20, 13)], "L21", [RESTRICTING, DIVERGING], ["LSw1:R", "LSw3:N", "LSw5:N", "LSw7:N", "LSw9:N"], ["L6RB", "L6L"])
		self.routes["LRtL20L31"] = Route(self.screen, block, "LRtL20L31", "L20", [(8, 13), (9, 13), (10, 13), (11, 13), (12, 13), (13, 13), (14, 13), (15, 13), (16, 13), (17, 13), (18, 14), (19, 15), (20, 15)], "L31", [DIVERGING, RESTRICTING], ["LSw1:N", "LSw3:N", "LSw5:N", "LSw7:N", "LSw9:R"], ["L6RA", "L4L"])
		self.routes["LRtP11L31"] = Route(self.screen, block, "LRtP11L31", "P11", [(8, 15), (9, 15), (10, 14), (11, 13), (12, 13), (13, 13), (14, 13), (15, 13), (16, 13), (17, 13), (18, 14), (19, 15), (20, 15)], "L31", [RESTRICTING, RESTRICTING], ["LSw1:R", "LSw3:N", "LSw5:N", "LSw7:N", "LSw9:R"], ["L6RB", "L4L"])

		block = self.blocks["LOSLAE"]
		self.routes["LRtP21L11"] = Route(self.screen, block, "LRtP21L11", "P21", [(8, 17), (9, 17), (10, 17), (11, 16), (12, 15), (13, 14), (14, 13), (15, 13), (16, 13), (17, 12), (18, 11), (19, 11), (20, 11)], "L11", [RESTRICTING, RESTRICTING], ["LSw3:R", "LSw5:N", "LSw7:R"], ["L4R", "L8L"])
		self.routes["LRtP21L21"] = Route(self.screen, block, "LRtP21L21", "P21", [(8, 17), (9, 17), (10, 17), (11, 16), (12, 15), (13, 14), (14, 13), (15, 13), (16, 13), (17, 13), (18, 13), (19, 13), (20, 13)], "L21", [RESTRICTING, RESTRICTING], ["LSw3:R", "LSw5:N", "LSw7:N", "LSw9:N"], ["L4R", "L6L"])
		self.routes["LRtP21L31"] = Route(self.screen, block, "LRtP21L31", "P21", [(8, 17), (9, 17), (10, 17), (11, 16), (12, 15), (13, 15), (14, 15), (15, 15), (16, 15), (17, 15), (18, 15), (19, 15), (20, 15)], "L31", [MAIN, RESTRICTING], ["LSw3:N", "LSw9:N"], ["L4R", "L4L"])

		self.signals["L8R"].AddPossibleRoutes("LOSLAW", ["LRtL10L11", "LRtL10L21", "LRtL10L31"])
		self.signals["L8L"].AddPossibleRoutes("LOSLAW", ["LRtL10L11"])
		self.signals["L8L"].AddPossibleRoutes("LOSLAM", ["LRtL20L11", "LRtP11L11"])
		self.signals["L8L"].AddPossibleRoutes("LOSLAE", ["LRtP21L11"])

		self.signals["L6RA"].AddPossibleRoutes("LOSLAM", ["LRtL20L11", "LRtL20L21", "LRtL20L31"])
		self.signals["L6RB"].AddPossibleRoutes("LOSLAM", ["LRtP11L11", "LRtP11L21", "LRtP11L31"])
		self.signals["L6L"].AddPossibleRoutes("LOSLAW", ["LRtL10L21"])
		self.signals["L6L"].AddPossibleRoutes("LOSLAM", ["LRtL20L21", "LRtP11L21"])
		self.signals["L6L"].AddPossibleRoutes("LOSLAE", ["LRtP21L21"])

		self.signals["L4R"].AddPossibleRoutes("LOSLAE", ["LRtP21L11", "LRtP21L21", "LRtP21L31"])
		self.signals["L4L"].AddPossibleRoutes("LOSLAW", ["LRtL10L31"])
		self.signals["L4L"].AddPossibleRoutes("LOSLAM", ["LRtL20L31", "LRtP11L31"])
		self.signals["L4L"].AddPossibleRoutes("LOSLAE", ["LRtP21L31"])

		self.osSignals["LOSLAW"] = ["L8R", "L8L", "L6L", "L4L"]
		self.osSignals["LOSLAM"] = ["L6RA", "L6RB", "L8L", "L6L", "L4L"]
		self.osSignals["LOSLAE"] = ["L4R", "L8L", "L6L", "L4L"]
		
		p = OSProxy(self, "LOSLAW")
		self.osProxies["LOSLAW"] = p
		p.AddRoute(self.routes["LRtL10L11"])
		p.AddRoute(self.routes["LRtL20L11"])
		p.AddRoute(self.routes["LRtP11L11"])
		p.AddRoute(self.routes["LRtP21L11"])
		p.AddRoute(self.routes["LRtL10L21"])
		p.AddRoute(self.routes["LRtL10L31"])

		p = OSProxy(self, "LOSLAM")
		self.osProxies["LOSLAM"] = p
		p.AddRoute(self.routes["LRtL10L21"])
		p.AddRoute(self.routes["LRtL20L21"])
		p.AddRoute(self.routes["LRtP11L21"])
		p.AddRoute(self.routes["LRtP21L21"])
		p.AddRoute(self.routes["LRtP11L11"])
		p.AddRoute(self.routes["LRtP11L31"])
		p.AddRoute(self.routes["LRtL20L11"])
		p.AddRoute(self.routes["LRtL20L31"])
		p.AddRoute(self.routes["LRtL10L31"])
		p.AddRoute(self.routes["LRtP21L11"])

		p = OSProxy(self, "LOSLAE")
		self.osProxies["LOSLAE"] = p
		p.AddRoute(self.routes["LRtL10L31"])
		p.AddRoute(self.routes["LRtL20L31"])
		p.AddRoute(self.routes["LRtP11L31"])
		p.AddRoute(self.routes["LRtP21L31"])
		p.AddRoute(self.routes["LRtP21L21"])
		p.AddRoute(self.routes["LRtP21L11"])

		# Carlton OS
		block = self.blocks["LOSCAW"]
		self.routes["LRtL11D10"] = Route(self.screen, block, "LRtL11D10", "D10", [(30, 11), (31, 11), (32, 11), (33, 11), (34, 11), (35, 11)], "L11", [RESTRICTING, MAIN], ["LSw15:N"], ["L18L", "L18R"])

		block = self.blocks["LOSCAM"]
		self.routes["LRtL21D10"] = Route(self.screen, block, "LRtL21D10", "L21", [(30, 13), (31, 13), (32, 12), (33, 11), (34, 11), (35, 11)], "D10", [RESTRICTING, DIVERGING], ["LSw15:R"], ["L16R", "L18L"])
		self.routes["LRtL21D20"] = Route(self.screen, block, "LRtL21D20", "L21", [(30, 13), (31, 13), (32, 13), (33, 13), (34, 13), (35, 13)], "D20", [MAIN, RESTRICTING], ["LSw15:N", "LSw17:N"], ["L16R", "L14L"])

		block = self.blocks["LOSCAE"]
		self.routes["LRtL31D20"] = Route(self.screen, block, "LRtL31D20", "L31", [(30, 15), (31, 15), (32, 15), (33, 14), (34, 13), (35, 13)], "D20", [DIVERGING, RESTRICTING], ["LSw17:R"], ["L14R", "L14L"])

		self.signals["L18R"].AddPossibleRoutes("LOSCAW", ["LRtL11D10"])
		self.signals["L18L"].AddPossibleRoutes("LOSCAW", ["LRtL11D10"])
		self.signals["L18L"].AddPossibleRoutes("LOSCAM", ["LRtL21D10"])

		self.signals["L16R"].AddPossibleRoutes("LOSCAM", ["LRtL21D10", "LRtL21D20"])

		self.signals["L14R"].AddPossibleRoutes("LOSCAE", ["LRtL31D20"])
		self.signals["L14L"].AddPossibleRoutes("LOSCAE", ["LRtL31D20"])
		self.signals["L14L"].AddPossibleRoutes("LOSCAM", ["LRtL21D20"])

		self.osSignals["LOSCAW"] = ["L18R", "L18L"]
		self.osSignals["LOSCAM"] = ["L16R", "L18L", "L14L"]
		self.osSignals["LOSCAE"] = ["L14R", "L14L"]
		
		p = OSProxy(self, "LOSCAW")
		self.osProxies["LOSCAW"] = p
		p.AddRoute(self.routes["LRtL11D10"])
		p.AddRoute(self.routes["LRtL21D10"])

		p = OSProxy(self, "LOSCAM")
		self.osProxies["LOSCAM"] = p
		p.AddRoute(self.routes["LRtL21D10"])
		p.AddRoute(self.routes["LRtL21D20"])

		p = OSProxy(self, "LOSCAE")
		self.osProxies["LOSCAE"] = p
		p.AddRoute(self.routes["LRtL21D20"])
		p.AddRoute(self.routes["LRtL31D20"])

		return self.signals, self.blockSigs, self.osSignals, self.routes, self.osProxies

	def DefineHandSwitches(self):
		self.handswitches = {}

		hs = HandSwitch(self, self.screen, self.frame, self.blocks["L11"], "LSw11.hand", (23, 10), self.misctiles["handdown"])
		self.blocks["L11"].AddHandSwitch(hs)
		self.handswitches["LSw11.hand"] = hs

		hs = HandSwitch(self, self.screen, self.frame, self.blocks["L31"], "LSw13.hand", (27, 16), self.misctiles["handup"])
		self.blocks["L31"].AddHandSwitch(hs)
		self.handswitches["LSw13.hand"] = hs
		return self.handswitches
