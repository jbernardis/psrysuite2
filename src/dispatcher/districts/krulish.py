from dispatcher.district import District

from dispatcher.block import Block, OverSwitch, Route, OSProxy
from dispatcher.turnout import Turnout
from dispatcher.signal import Signal

from dispatcher.constants import NaCl, RegAspects, RESTRICTING, DIVERGING, MAIN


class Krulish (District):
	def __init__(self, name, frame, screen):
		District.__init__(self, name, frame, screen)

	def SetAspect(self, sig, aspect, refresh=False):
		District.SetAspect(self, sig, aspect, refresh)
		signm = sig.GetName()
		self.frame.PopupAlert("In krulish set aspect")

		if signm == "N10W":
			if aspect == 0:
				bmp = self.misctiles["indicator"].getBmp(None, "out")
			else:
				bmp = self.misctiles["indicator"].getBmp(None, "green")
			self.frame.DrawTile(self.screen, (119, 5), bmp)
		if signm == "N20W":
			if aspect == 0:
				bmp = self.misctiles["indicator"].getBmp(None, "out")
			else:
				bmp = self.misctiles["indicator"].getBmp(None, "green")
			self.frame.DrawTile(self.screen, (119, 24), bmp)
		if signm == "S11E":
			if aspect == 0:
				bmp = self.misctiles["indicator"].getBmp(None, "out")
			else:
				bmp = self.misctiles["indicator"].getBmp(None, "green")
			self.frame.DrawTile(self.screen, (124, 5), bmp)
		if signm == "S21E":
			if aspect == 0:
				bmp = self.misctiles["indicator"].getBmp(None, "out")
			else:
				bmp = self.misctiles["indicator"].getBmp(None, "green")
			self.frame.DrawTile(self.screen, (124, 24), bmp)
			
		if signm in ["K2R", "K4R", "K8R"]:
			self.frame.PopupAlert("its one of those signals")
		# 	self.CheckBlockSignals("N11", "N11W", False)
		# 	self.CheckBlockSignals("N21", "N21W", False)
	
	def DoBlockAction(self, blk, blockend, state):
		blknm = blk.GetName()
		if blknm == "N20" and blockend == "W" and self.blocks["KOSN20S21"].GetEast():
			District.DoBlockAction(self, self.blocks["KOSN20S21"], None, state)
		elif blknm == "N10" and blockend == "W" and self.blocks["KOSN10S11"].GetEast():
			District.DoBlockAction(self, self.blocks["KOSN10S11"], None, state)

		District.DoBlockAction(self, blk, blockend, state)

		if blknm == "N11":
			self.CheckBlockSignals("N11", "N11W", False)

	def DetermineRoute(self, blocks):
		s3 = 'N' if self.turnouts["KSw3"].IsNormal() else 'R'
		s5 = 'N' if self.turnouts["KSw5"].IsNormal() else 'R'
		self.turnouts["KSw3"].SetLock(s5 == 'R', refresh=True)
		self.turnouts["KSw3b"].SetLock(s5 == 'R', refresh=True)
		self.turnouts["KSw5"].SetLock(s3 == 'R', refresh=True)
		self.turnouts["KSw5b"].SetLock(s3 == 'R', refresh=True)

		self.FindTurnoutCombinations(blocks, ["KSw1", "KSw3", "KSw5", "KSw7"])

	def DefineBlocks(self):
		self.blocks = {}
		self.osBlocks = {}

		self.blocks["N10"] = Block(self, self.frame, "N10",
			[
				(self.tiles["horiznc"], self.screen, (125, 7), False),
				(self.tiles["horiz"],   self.screen, (126, 7), False),
				(self.tiles["horiznc"], self.screen, (127, 7), False),
				(self.tiles["horiz"],   self.screen, (128, 7), False),
				(self.tiles["horiznc"], self.screen, (129, 7), False),
				(self.tiles["horiz"],   self.screen, (130, 7), False),
				(self.tiles["horiznc"], self.screen, (131, 7), False),
				(self.tiles["horiz"],   self.screen, (132, 7), False),
				(self.tiles["turnrightright"], self.screen, (133, 7), False),
				(self.tiles["diagright"], self.screen, (134, 8), False),
				(self.tiles["diagright"], self.screen, (135, 9), False),
				(self.tiles["diagright"], self.screen, (136, 10), False),
				(self.tiles["turnrightleft"], self.screen, (137, 11), False),
			], False)
		self.blocks["N10"].AddStoppingBlock([
				(self.tiles["eobleft"], self.screen, (122, 7), False),
				(self.tiles["horiznc"], self.screen, (123, 7), False),
				(self.tiles["horiz"],   self.screen, (124, 7), False),
			], False)
		self.blocks["N10"].AddStoppingBlock([
				(self.tiles["horiz"],   self.screen, (138, 11), False),
				(self.tiles["horiznc"], self.screen, (139, 11), False),
				(self.tiles["eobright"], self.screen, (140, 11), False),
			], True)
		self.blocks["N10"].AddTrainLoc(self.screen, (125, 7))

		self.blocks["N25"] = Block(self, self.frame, "N25",
			[
				(self.tiles["horiz"],   self.screen, (124, 17), False),
				(self.tiles["horiznc"], self.screen, (125, 17), False),
				(self.tiles["horiz"],   self.screen, (126, 17), False),
				(self.tiles["horiznc"], self.screen, (127, 17), False),
				(self.tiles["horiz"],   self.screen, (128, 17), False),
				(self.tiles["horiznc"], self.screen, (129, 17), False),
				(self.tiles["horiz"],   self.screen, (130, 17), False),
				(self.tiles["horiznc"], self.screen, (131, 17), False),
				(self.tiles["turnleftright"], self.screen, (132, 17), False),
				(self.tiles["diagleft"], self.screen, (133, 16), False),
				(self.tiles["diagleft"], self.screen, (134, 15), False),
				(self.tiles["diagleft"], self.screen, (135, 14), False),
				(self.tiles["turnleftleft"], self.screen, (136, 13), False),
				(self.tiles["horiznc"], self.screen, (137, 13), False),
			], False)
		self.blocks["N25"].AddStoppingBlock([
				(self.tiles["eobleft"], self.screen, (121, 17), False),
				(self.tiles["horiz"],   self.screen, (122, 17), False),
				(self.tiles["horiznc"], self.screen, (123, 17), False),
			], False)
		self.blocks["N25"].AddStoppingBlock([
				(self.tiles["horiz"],   self.screen, (138, 13), False),
				(self.tiles["horiznc"], self.screen, (139, 13), False),
				(self.tiles["eobright"], self.screen, (140, 13), False),
			], True)
		self.blocks["N25"].AddTrainLoc(self.screen, (126, 17))

		self.blocks["N20"] = Block(self, self.frame, "N20",
			[
				(self.tiles["horiznc"], self.screen, (125, 19), False),
				(self.tiles["horiz"],   self.screen, (126, 19), False),
				(self.tiles["horiznc"], self.screen, (127, 19), False),
				(self.tiles["horiz"],   self.screen, (128, 19), False),
				(self.tiles["horiznc"], self.screen, (129, 19), False),
				(self.tiles["horiz"],   self.screen, (130, 19), False),
				(self.tiles["horiznc"], self.screen, (131, 19), False),
				(self.tiles["horiz"],   self.screen, (132, 19), False),
				(self.tiles["turnleftright"], self.screen, (133, 19), False),
				(self.tiles["diagleft"], self.screen, (134, 18), False),
				(self.tiles["diagleft"], self.screen, (135, 17), False),
				(self.tiles["diagleft"], self.screen, (136, 16), False),
				(self.tiles["turnleftleft"], self.screen, (137, 15), False),
			], True)
		self.blocks["N20"].AddStoppingBlock([
				(self.tiles["eobleft"], self.screen, (122, 19), False),
				(self.tiles["horiznc"], self.screen, (123, 19), False),
				(self.tiles["horiz"],   self.screen, (124, 19), False),
			], False)
		self.blocks["N20"].AddStoppingBlock([
				(self.tiles["horiz"],   self.screen, (138, 15), False),
				(self.tiles["horiznc"], self.screen, (139, 15), False),
				(self.tiles["eobright"], self.screen, (140, 15), False),
			], True)
		self.blocks["N20"].AddTrainLoc(self.screen, (124, 19))

		self.blocks["N11"] = Block(self, self.frame, "N11",
			[
				(self.tiles["horiznc"], self.screen, (153, 11), False),
				(self.tiles["horiz"],   self.screen, (154, 11), False),
				(self.tiles["horiznc"], self.screen, (155, 11), False),
				(self.tiles["horiz"],   self.screen, (156, 11), False),
				(self.tiles["horiznc"], self.screen, (157, 11), False),
				(self.tiles["horiz"],   self.screen, (158, 11), False),
				(self.tiles["horiznc"], NaCl,        (0, 11), False),
				(self.tiles["horiz"],   NaCl,        (1, 11), False),
				(self.tiles["horiznc"], NaCl,        (2, 11), False),
				(self.tiles["horiz"],   NaCl,        (3, 11), False),
				(self.tiles["horiznc"], NaCl,        (4, 11), False),
			], False)
		self.blocks["N11"].AddStoppingBlock([
				(self.tiles["eobleft"], self.screen, (150, 11), False),
				(self.tiles["horiznc"], self.screen, (151, 11), False),
				(self.tiles["horiz"],   self.screen, (152, 11), False),
			], False)
		self.blocks["N11"].AddStoppingBlock([
				(self.tiles["horiz"],   NaCl,        (5, 11), False),
				(self.tiles["horiznc"], NaCl,        (6, 11), False),
				(self.tiles["horiz"],   NaCl,        (7, 11), False),
			], True)
		self.blocks["N11"].AddTrainLoc(self.screen, (154, 11))
		self.blocks["N11"].AddTrainLoc(NaCl, (2, 11))

		self.blocks["K10"] = Block(self, self.frame, "K10",
			[
				(self.tiles["houtline"],  self.screen, (150, 9), False),
				(self.tiles["houtline"],  self.screen, (151, 9), False),
				(self.tiles["houtline"],  self.screen, (152, 9), False),
			], False)

		self.blocks["KOSW"] = OverSwitch(self, self.frame, "KOSW", 
			[
				(self.tiles["eobleft"],      self.screen, (141, 11), False),
				(self.tiles["horiznc"],      self.screen, (142, 11), False),
				(self.tiles["horiz"],        self.screen, (143, 11), False),
				(self.tiles["diagleft"],     self.screen, (147, 10), False),
				(self.tiles["turnleftleft"], self.screen, (148, 9), False),
				(self.tiles["eobright"],     self.screen, (149, 9), False),
				(self.tiles["horiznc"],      self.screen, (147, 11), False),
				(self.tiles["horiz"],        self.screen, (148, 11), False),
				(self.tiles["eobright"],     self.screen, (149, 11), False),
				(self.tiles["diagright"],    self.screen, (146, 12), False),
				(self.tiles["horiz"],        self.screen, (148, 13), False),
				(self.tiles["eobright"],     self.screen, (149, 13), False),
			], 
			False)
		self.blocks["KOSW"].AddTrainLoc(self.screen, (143, 18))

		self.blocks["KOSM"] = OverSwitch(self, self.frame, "KOSM", 
			[
				(self.tiles["eobleft"],      self.screen, (141, 13), False),
				(self.tiles["horiznc"],      self.screen, (143, 13), False),
				(self.tiles["horiz"],        self.screen, (144, 13), False),
				(self.tiles["horiznc"],      self.screen, (146, 13), False),
				(self.tiles["horiz"],        self.screen, (148, 13), False),
				(self.tiles["eobright"],     self.screen, (149, 13), False),
				(self.tiles["diagleft"],     self.screen, (143, 12), False),
				(self.tiles["horiznc"],      self.screen, (147, 11), False),
				(self.tiles["horiz"],        self.screen, (148, 11), False),
				(self.tiles["eobright"],     self.screen, (149, 11), False),
				(self.tiles["diagleft"],     self.screen, (147, 10), False),
				(self.tiles["turnleftleft"], self.screen, (148, 9), False),
				(self.tiles["eobright"],     self.screen, (149, 9), False),
			], 
			False)
		self.blocks["KOSM"].AddTrainLoc(self.screen, (143, 20))

		self.blocks["KOSE"] = OverSwitch(self, self.frame, "KOSE", 
			[
				(self.tiles["eobleft"],       self.screen, (141, 15), False),
				(self.tiles["horiz"],         self.screen, (142, 15), False),
				(self.tiles["turnleftright"], self.screen, (143, 15), False),
				(self.tiles["diagleft"],      self.screen, (144, 14), False),
				(self.tiles["horiznc"],       self.screen, (146, 13), False),
				(self.tiles["horiz"],         self.screen, (148, 13), False),
				(self.tiles["eobright"],      self.screen, (149, 13), False),
			],
			True)
		self.blocks["KOSE"].AddTrainLoc(self.screen, (143, 22))

		self.blocks["KOSN10S11"] = OverSwitch(self, self.frame, "KOSN10S11", [], False)
		self.blocks["KOSN20S21"] = OverSwitch(self, self.frame, "KOSN20S21", [], True)

		self.osBlocks["KOSW"] = ["N10", "N11", "N21", "N25", "K10"]
		self.osBlocks["KOSM"] = ["N11", "N21", "N25", "K10"]
		self.osBlocks["KOSE"] = ["N10", "N11", "N20", "N21", "N25"]
		self.osBlocks["KOSN10S11"] = ["N10", "S11"]
		self.osBlocks["KOSN20S21"] = ["N20", "S21"]

		return self.blocks, self.osBlocks

	def DefineTurnouts(self, blocks):
		self.turnouts = {}
		toList = [
			["KSw1",  "toleftleftinv", ["KOSE", "KOSM"], (145, 13)],
			["KSw3",  "toleftright",   ["KOSW", "KOSM"], (142, 13)],
			["KSw3b", "toleftleft",    ["KOSW", "KOSM"], (144, 11)],
			["KSw5",  "torightleft",   ["KOSW", "KOSM", "KOSE"], (147, 13)],
			["KSw5b", "torightright",  ["KOSW", "KOSM", "KOSE"], (145, 11)],
			["KSw7",  "toleftright",   ["KOSW", "KOSM"], (146, 11)],
		]
		for tonm, tileSet, blks, pos in toList:
			trnout = Turnout(self, self.frame, tonm, self.screen, self.totiles[tileSet], pos)
			for blknm in blks:
				blocks[blknm].AddTurnout(trnout)
				trnout.AddBlock(blknm)
			self.turnouts[tonm] = trnout

		self.turnouts["KSw3"].SetPairedTurnout(self.turnouts["KSw3b"])
		self.turnouts["KSw5"].SetPairedTurnout(self.turnouts["KSw5b"])

		return self.turnouts
	
	def DefineSignals(self):
		self.signals = {}
		self.routes = {}
		self.osSignals = {}
		self.osProxies = {}
		
		sigList = [
			["K8R",  RegAspects, True,    "rightlong", (141, 12)],
			["K4R",  RegAspects, True,    "rightlong", (141, 14)],
			["K2R",  RegAspects, True,    "rightlong", (141, 16)],

			["K8LA", RegAspects, False,   "left",  (149, 8)],
			["K8LB", RegAspects, False,   "leftlong", (149, 10)],
			["K2L",  RegAspects, False,   "leftlong", (149, 12)],

			["N20W", RegAspects, False,   "leftlong", (121, 18)],
			["S21E", RegAspects, True,    "rightlong", (122, 20)],

			["N10W", RegAspects, False,   "leftlong", (121, 6)],
			["S11E", RegAspects, True,    "rightlong", (122, 8)],
		]

		for signm, atype, east, tileSet, pos in sigList:
			self.signals[signm]  = Signal(self, self.screen, self.frame, signm, atype, east, pos, self.sigtiles[tileSet])

		for signm in ["N20W", "N10W", "S21E", "S11E"]:
			self.signals[signm].EnableFleeting(True)
			
		self.signals["K8LA"].SetMutexSignals(["K8LB"])
		self.signals["K8LB"].SetMutexSignals(["K8LA"])
			
		self.blockSigs = {
			# # which signals govern stopping sections, west and east
			"N10": ("N10W",  "K8R"),
			"N11": ("K8LB",  "N16R"),
			"N20": ("N20W",  "K2R"),
			"N25": ("S16L",  "K4R")
		}

		self.sigLeverMap = {
			"K2.lvr":  ["KOSW", "KOSM", "KOSE"],
			"K4.lvr":  ["KOSM"],
			"K8.lvr":  ["KOSW", "KOSM"]
		}

		for sl in self.sigLeverMap:
			self.frame.AddSignalLever(sl, self)

		for blknm, siglist in self.blockSigs.items():
			self.blocks[blknm].SetSBSignals(siglist)
			self.blocks[blknm].SetSignals(siglist)
		self.blocks["K10"].SetSignals(("K8LA", None))

		block = self.blocks["KOSW"]
		self.routes["KRtN10K10"] = Route(self.screen, block, "KRtN10K10", "K10", [(141, 11), (142, 11), (143, 11), (144, 11), (145, 11), (146, 11), (147, 10), (148, 9), (149, 9)], "N10", [RESTRICTING, RESTRICTING], ["KSw3:N", "KSw5:N", "KSw7:R"], ["K8LA", "K8R"])
		self.routes["KRtN10N11"] = Route(self.screen, block, "KRtN10N11", "N11", [(141, 11), (142, 11), (143, 11), (144, 11), (145, 11), (146, 11), (147, 11), (148, 11), (149, 11)], "N10", [MAIN, MAIN], ["KSw3:N", "KSw5:N", "KSw7:N"], ["K8LB", "K8R"])
		self.routes["KRtN10N21"] = Route(self.screen, block, "KRtN10N21", "N21", [(141, 11), (142, 11), (143, 11), (144, 11), (145, 11), (146, 12), (147, 13), (148, 13), (149, 13)], "N10", [DIVERGING, DIVERGING], ["KSw3:N", "KSw5:R"], ["K2L", "K8R"])

		block = self.blocks["KOSM"]
		self.routes["KRtN25K10"] = Route(self.screen, block, "KRtN25K10", "K10", [(141, 13), (142, 13), (143, 12), (144, 11), (145, 11), (146, 11), (147, 10), (148, 9), (149, 9)], "N25", [RESTRICTING, RESTRICTING], ["KSw3:R", "KSw5:N", "KSw7:R"], ["K8LA", "K4R"])
		self.routes["KRtN25N11"] = Route(self.screen, block, "KRtN25N11", "N11", [(141, 13), (142, 13), (143, 12), (144, 11), (145, 11), (146, 11), (147, 11), (148, 11), (149, 11)], "N25", [DIVERGING, DIVERGING], ["KSw3:R", "KSw5:N", "KSw7:N"], ["K8LB", "K4R"])
		self.routes["KRtN25N21"] = Route(self.screen, block, "KRtN25N21", "N21", [(141, 13), (142, 13), (143, 13), (144, 13), (145, 13), (146, 13), (147, 13), (148, 13), (149, 13)], "N25", [MAIN, MAIN], ["KSw1:R", "KSw3:N", "KSw5:N"], ["K2L", "K4R"])

		block = self.blocks["KOSE"]
		self.routes["KRtN20N21"] = Route(self.screen, block, "KRtN20N21", "N20", [(141, 15), (142, 15), (143, 15), (144, 14), (145, 13), (146, 13), (147, 13), (148, 13), (149, 13)], "N21", [DIVERGING, DIVERGING], ["KSw1:N", "KSw5:N"], ["K2R", "K2L"])

		block = self.blocks["KOSN10S11"]
		self.routes["KRtN10S11"] = Route(self.screen, block, "KRtN10S11", "N10", [], "S11", [MAIN, MAIN], [], ["N10W", "S11E"])
		block.SetRoute(self.routes["KRtN10S11"])

		block = self.blocks["KOSN20S21"]
		self.routes["KRtN20S21"] = Route(self.screen, block, "KRtN20S21", "S21", [], "N20", [MAIN, MAIN], [], ["S21E", "N20W"])
		block.SetRoute(self.routes["KRtN20S21"])

		self.signals["K8R"].AddPossibleRoutes("KOSW", ["KRtN10K10", "KRtN10N11", "KRtN10N21"])
		self.signals["K4R"].AddPossibleRoutes("KOSM", ["KRtN25K10", "KRtN25N11", "KRtN25N21"])
		self.signals["K2R"].AddPossibleRoutes("KOSE", ["KRtN20N21"])
		self.signals["K8LA"].AddPossibleRoutes("KOSW", ["KRtN10K10"])
		self.signals["K8LA"].AddPossibleRoutes("KOSM", ["KRtN25K10"])
		self.signals["K8LB"].AddPossibleRoutes("KOSW", ["KRtN10N11"])
		self.signals["K8LB"].AddPossibleRoutes("KOSM", ["KRtN25N11"])
		self.signals["K2L"].AddPossibleRoutes("KOSW", ["KRtN10N21"])
		self.signals["K2L"].AddPossibleRoutes("KOSM", ["KRtN25N21"])
		self.signals["K2L"].AddPossibleRoutes("KOSE", ["KRtN20N21"])

		self.signals["N10W"].AddPossibleRoutes("KOSN10S11", ["KRtN10S11"])
		self.signals["S11E"].AddPossibleRoutes("KOSN10S11", ["KRtN10S11"])

		self.signals["N20W"].AddPossibleRoutes("KOSN20S21", ["KRtN20S21"])
		self.signals["S21E"].AddPossibleRoutes("KOSN20S21", ["KRtN20S21"])

		self.osSignals["KOSW"] = ["K8R", "K8LA", "K8LB", "K2L"]
		self.osSignals["KOSM"] = ["K4R", "K8LA", "K8LB", "K2L"]
		self.osSignals["KOSE"] = ["K2R", "K2L"]
		self.osSignals["KOSN10S11"] = ["N10W", "S11E"]
		self.osSignals["KOSN20S21"] = ["N20W", "S21E"]
		
		p = OSProxy(self, "KOSW")
		self.osProxies["KOSW"] = p
		p.AddRoute(self.routes["KRtN10K10"])
		p.AddRoute(self.routes["KRtN10N11"])
		p.AddRoute(self.routes["KRtN10N21"])
		p.AddRoute(self.routes["KRtN25K10"])
		p.AddRoute(self.routes["KRtN25N11"])
		
		p = OSProxy(self, "KOSM")
		self.osProxies["KOSM"] = p
		#p.AddRoute(self.routes["KRtN10K10"])
		#p.AddRoute(self.routes["KRtN10N11"])
		p.AddRoute(self.routes["KRtN25K10"])
		p.AddRoute(self.routes["KRtN25N21"])
		p.AddRoute(self.routes["KRtN25N11"])
		p.AddRoute(self.routes["KRtN10N21"])
		
		p = OSProxy(self, "KOSE")
		self.osProxies["KOSE"] = p
		p.AddRoute(self.routes["KRtN10N21"])
		p.AddRoute(self.routes["KRtN20N21"])
		p.AddRoute(self.routes["KRtN25N21"])

		return self.signals, self.blockSigs, self.osSignals, self.routes, self.osProxies
