from dispatcher.district import District

from dispatcher.block import Block, OverSwitch, Route, OSProxy
from dispatcher.turnout import Turnout
from dispatcher.signal import Signal
from dispatcher.button import Button
from dispatcher.indicator import Indicator

from dispatcher.constants import LaKr, RESTRICTING, MAIN, DIVERGING, RegAspects


class Hyde (District):
	def __init__(self, name, frame, screen):
		District.__init__(self, name, frame, screen)

	def Initialize(self):
		District.Initialize(self)

		self.buttons["HydeWestPower"].TurnOn(refresh=True)
		self.buttons["HydeEastPower"].TurnOn(refresh=True)
		self.buttons["H30Power"].TurnOn(refresh=True)

	def OnConnect(self):
		District.OnConnect(self)

		for bname in ["HydeEastPower", "HydeWestPower", "H30Power"]:
			onFlag = 1 if self.buttons[bname].IsOn() else 0
			self.indicators[bname].SetValue(onFlag, force=True)

	def DetermineRoute(self, blocks):
		self.FindTurnoutCombinations(blocks, [
			"HSw1", "HSw3", "HSw5", "HSw7", "HSw9", "HSw11", "HSw13", "HSw15",
			"HSw17", "HSw19", "HSw21", "HSw23", "HSw25", "HSw27", "HSw29"])

	def PerformButtonAction(self, btn):
		bname = btn.GetName()
		if bname in ["HydeEastPower", "HydeWestPower", "H30Power"]:
			onFlag = self.buttons[bname].IsOn()
			nv = 0 if onFlag else 1
			self.indicators[bname].SetValue(nv)
			return

		rtname = self.buttonToRoute[bname]
		rte = self.routes[rtname]
		tolist = rte.GetSetTurnouts()
		osBlk = rte.GetOS()
		# osname = osBlk.GetName()
		if osBlk.IsBusy():
			self.ReportBlockBusy(osBlk.GetRouteDesignator())
			return

		btn.Press(refresh=True)
		self.frame.ClearButtonAfter(2, btn)
		self.MatrixTurnoutRequest(tolist)

	def DoIndicatorAction(self, ind, val):
		District.DoIndicatorAction(self, ind, val)

		iName = ind.GetName()
		if iName in self.buttons:
			btn = self.buttons[iName]
			btn.TurnOn(flag=(val == 1), refresh=True)

	def DefineBlocks(self):
		self.blocks = {}
		self.osBlocks = {}

		self.blocks["H11"] = Block(self, self.frame, "H11",
			[
				(self.tiles["horiz"], self.screen, (13, 13), False),
				(self.tiles["horiznc"], self.screen, (14, 13), False),
				(self.tiles["horiz"], self.screen, (15, 13), False),
				(self.tiles["horiznc"], self.screen, (16, 13), False),
				(self.tiles["horiz"], self.screen, (17, 13), False),
				(self.tiles["horiznc"], self.screen, (18, 13), False),
				(self.tiles["horiz"], self.screen, (19, 13), False),
				(self.tiles["horiznc"], self.screen, (20, 13), False),

				(self.tiles["horiz"], LaKr, (126, 11), False),
				(self.tiles["horiznc"], LaKr, (127, 11), False),
			], False)
		self.blocks["H11"].AddStoppingBlock([
				(self.tiles["eobleft"], LaKr, (123, 11), False),
				(self.tiles["horiz"], LaKr, (124, 11), False),
				(self.tiles["horiznc"], LaKr, (125, 11), False),
			], False)
		self.blocks["H11"].AddTrainLoc(self.screen, (14, 13))
		self.blocks["H11"].AddTrainLoc(LaKr, (124, 11))

		self.blocks["H12"] = Block(self, self.frame, "H12",
			[
				(self.tiles["horiz"], self.screen, (33, 13), False),
				(self.tiles["horiznc"], self.screen, (34, 13), False),
				(self.tiles["horiz"], self.screen, (35, 13), False),
				(self.tiles["horiznc"], self.screen, (36, 13), False),
				(self.tiles["horiz"], self.screen, (37, 13), False),
				(self.tiles["horiznc"], self.screen, (38, 13), False),
				(self.tiles["horiz"], self.screen, (39, 13), False),
				(self.tiles["horiznc"], self.screen, (40, 13), False),
			], False)
		self.blocks["H12"].AddTrainLoc(self.screen, (34, 13))

		self.blocks["H30"] = Block(self, self.frame, "H30",
			[
				(self.tiles["horiznc"], self.screen, (13, 11), False),
				(self.tiles["horiz"], self.screen, (14, 11), False),
				(self.tiles["horiznc"], self.screen, (15, 11), False),
				(self.tiles["horiz"], self.screen, (16, 11), False),
				(self.tiles["horiznc"], self.screen, (17, 11), False),
				(self.tiles["horiz"], self.screen, (18, 11), False),
				(self.tiles["turnleftright"], self.screen, (19, 11), False),
				(self.tiles["diagleft"], self.screen, (20, 10), False),
				(self.tiles["diagleft"], self.screen, (21, 9), False),
				(self.tiles["diagleft"], self.screen, (22, 8), False),
				(self.tiles["diagleft"], self.screen, (23, 7), False),
				(self.tiles["diagleft"], self.screen, (24, 6), False),
				(self.tiles["turnleftleft"], self.screen, (25, 5), True),
				(self.tiles["horiz"], self.screen, (26, 5), False),

				(self.tiles["horiznc"], LaKr, (109, 9), False),
				(self.tiles["horiz"], LaKr, (110, 9), False),
				(self.tiles["horiznc"], LaKr, (111, 9), False),
				(self.tiles["horiz"], LaKr, (112, 9), False),
				(self.tiles["horiznc"], LaKr, (113, 9), False),
				(self.tiles["horiz"], LaKr, (114, 9), False),
				(self.tiles["horiznc"], LaKr, (115, 9), False),
				(self.tiles["horiz"], LaKr, (116, 9), False),
				(self.tiles["horiznc"], LaKr, (117, 9), False),
				(self.tiles["horiz"], LaKr, (118, 9), False),
				(self.tiles["horiznc"], LaKr, (119, 9), False),
				(self.tiles["horiz"], LaKr, (120, 9), False),
				(self.tiles["horiznc"], LaKr, (121, 9), False),
				(self.tiles["horiz"], LaKr, (122, 9), False),
				(self.tiles["horiznc"], LaKr, (123, 9), False),
				(self.tiles["horiz"], LaKr, (124, 9), False),
				(self.tiles["horiznc"], LaKr, (125, 9), False),
				(self.tiles["horiz"], LaKr, (126, 9), False),
				(self.tiles["horiznc"], LaKr, (127, 9), False),
			],
			False)
		self.blocks["H30"].AddStoppingBlock([
				(self.tiles["eobleft"], LaKr, (106, 9), False),
				(self.tiles["horiznc"], LaKr, (107, 9), False),
				(self.tiles["horiz"], LaKr, (108, 9), False),
			], False)
		self.blocks["H30"].AddTrainLoc(self.screen, (14, 11))
		self.blocks["H30"].AddTrainLoc(LaKr, (108, 9))

		self.blocks["H31"] = Block(self, self.frame, "H31",
			[
				(self.tiles["horiz"], self.screen, (33, 5), False),
				(self.tiles["horiznc"], self.screen, (34, 5), False),
				(self.tiles["horiz"], self.screen, (35, 5), False),
				(self.tiles["horiznc"], self.screen, (36, 5), False),
				(self.tiles["horiz"], self.screen, (37, 5), False),
				(self.tiles["horiznc"], self.screen, (38, 5), False),
				(self.tiles["horiz"], self.screen, (39, 5), False),
				(self.tiles["horiznc"], self.screen, (40, 5), False),
			], False)
		self.blocks["H31"].AddTrainLoc(self.screen, (34, 5))

		self.blocks["H32"] = Block(self, self.frame, "H32",
			[
				(self.tiles["horiz"], self.screen, (33, 7), False),
				(self.tiles["horiznc"], self.screen, (34, 7), False),
				(self.tiles["horiz"], self.screen, (35, 7), False),
				(self.tiles["horiznc"], self.screen, (36, 7), False),
				(self.tiles["horiz"], self.screen, (37, 7), False),
				(self.tiles["horiznc"], self.screen, (38, 7), False),
				(self.tiles["horiz"], self.screen, (39, 7), False),
				(self.tiles["horiznc"], self.screen, (40, 7), False),
			], False)
		self.blocks["H32"].AddTrainLoc(self.screen, (34, 7))

		self.blocks["H33"] = Block(self, self.frame, "H33",
			[
				(self.tiles["horiz"], self.screen, (33, 9), False),
				(self.tiles["horiznc"], self.screen, (34, 9), False),
				(self.tiles["horiz"], self.screen, (35, 9), False),
				(self.tiles["horiznc"], self.screen, (36, 9), False),
				(self.tiles["horiz"], self.screen, (37, 9), False),
				(self.tiles["horiznc"], self.screen, (38, 9), False),
				(self.tiles["horiz"], self.screen, (39, 9), False),
				(self.tiles["horiznc"], self.screen, (40, 9), False),
			], False)
		self.blocks["H33"].AddTrainLoc(self.screen, (34, 9))

		self.blocks["H34"] = Block(self, self.frame, "H34",
			[
				(self.tiles["horiz"], self.screen, (33, 11), False),
				(self.tiles["horiznc"], self.screen, (34, 11), False),
				(self.tiles["horiz"], self.screen, (35, 11), False),
				(self.tiles["horiznc"], self.screen, (36, 11), False),
				(self.tiles["horiz"], self.screen, (37, 11), False),
				(self.tiles["horiznc"], self.screen, (38, 11), False),
				(self.tiles["horiz"], self.screen, (39, 11), False),
				(self.tiles["horiznc"], self.screen, (40, 11), False),
			], False)
		self.blocks["H34"].AddTrainLoc(self.screen, (34, 11))

		self.blocks["HOSWW"] = OverSwitch(self, self.frame, "HOSWW", 
			[
				(self.tiles["horiznc"], self.screen, (31, 5), False),
				(self.tiles["diagleft"], self.screen, (29, 6), False),
				(self.tiles["diagleft"], self.screen, (27, 8), False),
				(self.tiles["diagleft"], self.screen, (25, 10), False),
				(self.tiles["diagleft"], self.screen, (24, 11), False),
				(self.tiles["diagleft"], self.screen, (23, 12), False),
				(self.tiles["eobleft"], self.screen, (21, 13), False),
				(self.tiles["horiznc"], self.screen, (23, 13), False),
				(self.tiles["horiz"], self.screen, (24, 13), False),

				(self.tiles["horiznc"], self.screen, (29, 7), False),
				(self.tiles["horiz"], self.screen, (30, 7), False),
				(self.tiles["horiznc"], self.screen, (31, 7), False),

				(self.tiles["horiznc"], self.screen, (27, 9), False),
				(self.tiles["horiz"], self.screen, (28, 9), False),
				(self.tiles["horiznc"], self.screen, (29, 9), False),
				(self.tiles["horiz"], self.screen, (30, 9), False),
				(self.tiles["horiznc"], self.screen, (31, 9), False),

				(self.tiles["diagleft"], self.screen, (26, 12), False),
				(self.tiles["turnleftleft"], self.screen, (27, 11), True),
				(self.tiles["horiz"], self.screen, (28, 11), False),
				(self.tiles["horiznc"], self.screen, (29, 11), False),
				(self.tiles["horiz"], self.screen, (30, 11), False),
				(self.tiles["horiznc"], self.screen, (31, 11), False),

				(self.tiles["horiz"], self.screen, (26, 13), False),
				(self.tiles["horiznc"], self.screen, (27, 13), False),
				(self.tiles["horiz"], self.screen, (28, 13), False),
				(self.tiles["horiznc"], self.screen, (29, 13), False),
				(self.tiles["horiz"], self.screen, (30, 13), False),
				(self.tiles["horiznc"], self.screen, (31, 13), False),
			], 
			False)
		self.blocks["HOSWW"].AddTrainLoc(self.screen, (16, 6))

		self.blocks["HOSWW2"] = OverSwitch(self, self.frame, "HOSWW2", 
			[
				(self.tiles["horiznc"], self.screen, (31, 5), False),
				(self.tiles["horiz"], self.screen, (28, 5), False),
				(self.tiles["horiznc"], self.screen, (29, 5), False),
			], 
			False)
		self.blocks["HOSWW2"].AddTrainLoc(self.screen, (16, 4))

		self.osBlocks["HOSWW"] = ["H11", "H12", "H31", "H32", "H33", "H34"]
		self.osBlocks["HOSWW2"] = ["H30", "H31"]

		self.blocks["H21"] = Block(self, self.frame, "H21",
			[
				(self.tiles["eobleft"], LaKr,        (123, 13), False),
				(self.tiles["horiz"],   LaKr,        (124, 13), False),
				(self.tiles["horiznc"], LaKr,        (125, 13), False),
				(self.tiles["horiz"],   self.screen, (13, 15), False),
				(self.tiles["horiznc"], self.screen, (14, 15), False),
				(self.tiles["horiz"],   self.screen, (15, 15), False),
				(self.tiles["horiznc"], self.screen, (16, 15), False),
				(self.tiles["horiz"],   self.screen, (17, 15), False),
				(self.tiles["eobleft"], LaKr,        (123, 13), False),
				(self.tiles["horiz"],   LaKr,        (124, 13), False),
				(self.tiles["horiznc"], LaKr,        (125, 13), False),
				(self.tiles["horiz"],   LaKr,        (126, 13), False),
				(self.tiles["horiznc"], LaKr,        (127, 13), False),
			], True)
		self.blocks["H21"].AddStoppingBlock([
				(self.tiles["horiznc"], self.screen, (18, 15), False),
				(self.tiles["horiz"],   self.screen, (19, 15), False),
				(self.tiles["eobright"], self.screen, (20, 15), False),
			], True)
		self.blocks["H21"].AddTrainLoc(self.screen, (14, 15))
		self.blocks["H21"].AddTrainLoc(LaKr, (124, 13))

		self.blocks["H22"] = Block(self, self.frame, "H22",
			[
				(self.tiles["horiz"],   self.screen, (33, 15), False),
				(self.tiles["horiznc"], self.screen, (34, 15), False),
				(self.tiles["horiz"],   self.screen, (35, 15), False),
				(self.tiles["horiznc"], self.screen, (36, 15), False),
				(self.tiles["horiz"],   self.screen, (37, 15), False),
				(self.tiles["horiznc"], self.screen, (38, 15), False),
				(self.tiles["horiz"],   self.screen, (39, 15), False),
				(self.tiles["horiznc"], self.screen, (40, 15), False),
			], True)
		self.blocks["H22"].AddTrainLoc(self.screen, (34, 15))

		self.blocks["H43"] = Block(self, self.frame, "H43",
			[
				(self.tiles["horiz"],   self.screen, (33, 17), False),
				(self.tiles["horiznc"], self.screen, (34, 17), False),
				(self.tiles["horiz"],   self.screen, (35, 17), False),
				(self.tiles["horiznc"], self.screen, (36, 17), False),
				(self.tiles["horiz"],   self.screen, (37, 17), False),
				(self.tiles["horiznc"], self.screen, (38, 17), False),
				(self.tiles["horiz"],   self.screen, (39, 17), False),
				(self.tiles["horiznc"], self.screen, (40, 17), False),
			], True)
		self.blocks["H43"].AddTrainLoc(self.screen, (34, 17))

		self.blocks["H42"] = Block(self, self.frame, "H42",
			[
				(self.tiles["horiz"],   self.screen, (33, 19), False),
				(self.tiles["horiznc"], self.screen, (34, 19), False),
				(self.tiles["horiz"],   self.screen, (35, 19), False),
				(self.tiles["horiznc"], self.screen, (36, 19), False),
				(self.tiles["horiz"],   self.screen, (37, 19), False),
				(self.tiles["horiznc"], self.screen, (38, 19), False),
				(self.tiles["horiz"],   self.screen, (39, 19), False),
				(self.tiles["horiznc"], self.screen, (40, 19), False),
			], True)
		self.blocks["H42"].AddTrainLoc(self.screen, (34, 19))

		self.blocks["H41"] = Block(self, self.frame, "H41",
			[
				(self.tiles["horiz"],   self.screen, (33, 21), False),
				(self.tiles["horiznc"], self.screen, (34, 21), False),
				(self.tiles["horiz"],   self.screen, (35, 21), False),
				(self.tiles["horiznc"], self.screen, (36, 21), False),
				(self.tiles["horiz"],   self.screen, (37, 21), False),
				(self.tiles["horiznc"], self.screen, (38, 21), False),
				(self.tiles["horiz"],   self.screen, (39, 21), False),
				(self.tiles["horiznc"], self.screen, (40, 21), False),
			], True)
		self.blocks["H41"].AddTrainLoc(self.screen, (34, 21))

		self.blocks["H40"] = Block(self, self.frame, "H40",
			[
				(self.tiles["horiz"],   self.screen, (13, 17), False),
				(self.tiles["horiznc"], self.screen, (14, 17), False),
				(self.tiles["horiz"],   self.screen, (15, 17), False),
				(self.tiles["horiznc"], self.screen, (16, 17), False),
				(self.tiles["horiz"],   self.screen, (17, 17), False),
				(self.tiles["horiznc"], self.screen, (18, 17), False),
				(self.tiles["horiz"],   self.screen, (19, 17), False),
				(self.tiles["horiznc"], self.screen, (20, 17), False),
				(self.tiles["turnrightright"], self.screen, (21, 17), False),
				(self.tiles["diagright"], self.screen, (22, 18), False),
				(self.tiles["diagright"], self.screen, (23, 19), False),
				(self.tiles["diagright"], self.screen, (24, 20), False),
				(self.tiles["diagright"], self.screen, (25, 21), False),
				(self.tiles["diagright"], self.screen, (26, 22), False),
				(self.tiles["turnrightleft"], self.screen, (27, 23), False),
				(self.tiles["horiz"],   self.screen, (28, 23), False),
				(self.tiles["horiznc"], self.screen, (29, 23), False),
				(self.tiles["horiz"],   self.screen, (30, 23), False),
				(self.tiles["horiznc"], self.screen, (31, 23), False),
				(self.tiles["horiz"],   self.screen, (32, 23), False),
				(self.tiles["horiznc"], self.screen, (33, 23), False),
				(self.tiles["horiz"],   self.screen, (34, 23), False),
				(self.tiles["horiznc"], self.screen, (35, 23), False),
				(self.tiles["horiz"],   self.screen, (36, 23), False),
				(self.tiles["horiznc"], self.screen, (37, 23), False),
				(self.tiles["horiz"],   self.screen, (38, 23), False),
				(self.tiles["horiznc"], self.screen, (39, 23), False),
				(self.tiles["horiznc"], self.screen, (40, 23), False),
				(self.tiles["eobleft"], LaKr,        (123, 15), False),
				(self.tiles["horiz"],   LaKr,        (124, 15), False),
				(self.tiles["horiznc"], LaKr,        (125, 15), False),
				(self.tiles["horiz"],   LaKr,        (126, 15), False),
				(self.tiles["horiznc"], LaKr,        (127, 15), False),
			], True)
		self.blocks["H40"].AddTrainLoc(self.screen, (28, 23))
		self.blocks["H40"].AddTrainLoc(LaKr, (124, 15))

		self.blocks["HOSWE"] = OverSwitch(self, self.frame, "HOSWE", 
			[
				(self.tiles["eobleft"], self.screen, (21, 15), False),
				(self.tiles["horiznc"], self.screen, (23, 15), False),
				(self.tiles["horiz"],   self.screen, (24, 15), False),
				(self.tiles["horiznc"], self.screen, (26, 15), False),
				(self.tiles["horiz"],   self.screen, (27, 15), False),
				(self.tiles["horiznc"], self.screen, (28, 15), False),
				(self.tiles["horiz"],   self.screen, (29, 15), False),
				(self.tiles["horiznc"], self.screen, (30, 15), False),
				(self.tiles["horiz"],   self.screen, (31, 15), False),

				(self.tiles["diagright"], self.screen, (26, 16), False),
				(self.tiles["turnrightleft"], self.screen, (27, 17), False),
				(self.tiles["horiznc"], self.screen, (28, 17), False),
				(self.tiles["horiz"],   self.screen, (29, 17), False),
				(self.tiles["horiznc"], self.screen, (30, 17), False),
				(self.tiles["horiz"],   self.screen, (31, 17), False),

				(self.tiles["diagright"], self.screen, (23, 16), False),
				(self.tiles["diagright"], self.screen, (24, 17), False),
				(self.tiles["diagright"], self.screen, (25, 18), False),
				(self.tiles["horiz"],   self.screen, (27, 19), False),
				(self.tiles["horiznc"], self.screen, (28, 19), False),
				(self.tiles["horiz"],   self.screen, (29, 19), False),
				(self.tiles["horiznc"], self.screen, (30, 19), False),
				(self.tiles["horiz"],   self.screen, (31, 19), False),

				(self.tiles["diagright"], self.screen, (27, 20), False),
				(self.tiles["turnrightleft"], self.screen, (28, 21), False),
				(self.tiles["horiz"],   self.screen, (29, 21), False),
				(self.tiles["horiznc"], self.screen, (30, 21), False),
				(self.tiles["horiz"],   self.screen, (31, 21), False),

			], True)
		self.blocks["HOSWE"].AddTrainLoc(self.screen, (16, 22))

		self.osBlocks["HOSWE"] = ["H21", "H22", "H41", "H42", "H43"]

		self.blocks["H13"] = Block(self, self.frame, "H13",
			[
				(self.tiles["horiznc"], self.screen, (60, 13), False),
				(self.tiles["horiz"],   self.screen, (61, 13), False),
				(self.tiles["horiznc"], self.screen, (62, 13), False),
				(self.tiles["horiz"],   self.screen, (63, 13), False),
				(self.tiles["horiznc"], self.screen, (64, 13), False),

				(self.tiles["horiz"],   LaKr,        (40, 9), False),
				(self.tiles["horiznc"], LaKr,        (41, 9), False),
				(self.tiles["horiz"],   LaKr,        (42, 9), False),
				(self.tiles["horiznc"], LaKr,        (43, 9), False),
				(self.tiles["horiz"],   LaKr,        (44, 9), False),
				(self.tiles["eobright"], LaKr,       (45, 9), False),
			], False)
		self.blocks["H13"].AddStoppingBlock([
				(self.tiles["eobleft"], self.screen, (57, 13), False),
				(self.tiles["horiznc"], self.screen, (58, 13), False),
				(self.tiles["horiz"],   self.screen, (59, 13), False),
				], False)
		self.blocks["H13"].AddTrainLoc(self.screen, (58, 13))
		self.blocks["H13"].AddTrainLoc(LaKr, (41, 9))

		self.blocks["HOSEW"] = OverSwitch(self, self.frame, "HOSEW", 
			[
				(self.tiles["horiznc"], self.screen, (42, 5), False),
				(self.tiles["horiz"],   self.screen, (43, 5), False),
				(self.tiles["horiznc"], self.screen, (44, 5), False),
				(self.tiles["horiz"],   self.screen, (45, 5), False),
				(self.tiles["turnrightright"], self.screen, (46, 5), False),
				(self.tiles["diagright"],      self.screen, (47, 6), False),
				(self.tiles["diagright"],      self.screen, (48, 7), False),
				(self.tiles["diagright"],      self.screen, (49, 8), False),
				(self.tiles["diagright"],      self.screen, (50, 9), False),
				(self.tiles["diagright"],      self.screen, (51, 10), False),
				(self.tiles["diagright"],      self.screen, (52, 11), False),
				(self.tiles["diagright"],      self.screen, (53, 12), False),
				(self.tiles["horiznc"],  self.screen, (55, 13), False),
				(self.tiles["eobright"], self.screen, (56, 13), False),

				(self.tiles["horiznc"], self.screen, (42, 7), False),
				(self.tiles["horiz"],   self.screen, (43, 7), False),
				(self.tiles["horiznc"], self.screen, (44, 7), False),
				(self.tiles["turnrightright"], self.screen, (45, 7), False),
				(self.tiles["diagright"],      self.screen, (46, 8), False),
				(self.tiles["diagright"],      self.screen, (47, 9), False),
				(self.tiles["diagright"],      self.screen, (48, 10), False),
				(self.tiles["diagright"],      self.screen, (49, 11), False),
				(self.tiles["diagright"],      self.screen, (50, 12), False),
				(self.tiles["horiznc"], self.screen, (52, 13), False),
				(self.tiles["horiz"],   self.screen, (53, 13), False),

				(self.tiles["horiznc"], self.screen, (42, 9), False),
				(self.tiles["horiz"],   self.screen, (43, 9), False),
				(self.tiles["turnrightright"], self.screen, (44, 9), False),
				(self.tiles["diagright"],      self.screen, (45, 10), False),
				(self.tiles["diagright"],      self.screen, (46, 11), False),
				(self.tiles["diagright"],      self.screen, (47, 12), False),
				(self.tiles["horiznc"], self.screen, (49, 13), False),
				(self.tiles["horiz"],   self.screen, (50, 13), False),

				(self.tiles["horiznc"], self.screen, (42, 11), False),
				(self.tiles["turnrightright"], self.screen, (43, 11), False),
				(self.tiles["diagright"],      self.screen, (44, 12), False),
				(self.tiles["horiznc"], self.screen, (46, 13), False),
				(self.tiles["horiz"],   self.screen, (47, 13), False),

				(self.tiles["horiznc"], self.screen, (42, 13), False),
				(self.tiles["horiz"],   self.screen, (43, 13), False),
				(self.tiles["horiznc"], self.screen, (44, 13), False),

			], 
			False)
		self.blocks["HOSEW"].AddTrainLoc(self.screen, (51, 4))

		self.osBlocks["HOSEW"] = ["H13", "H12", "H31", "H32", "H33", "H34"]

		self.blocks["H23"] = Block(self, self.frame, "H23",
			[
				(self.tiles["eobleft"], self.screen, (57, 15), False),
				(self.tiles["horiznc"], self.screen, (58, 15), False),
				(self.tiles["horiz"],   self.screen, (59, 15), False),
				(self.tiles["horiznc"], self.screen, (60, 15), False),
				(self.tiles["horiz"],   self.screen, (61, 15), False),
				(self.tiles["horiznc"], self.screen, (62, 15), False),
				(self.tiles["horiz"],   self.screen, (63, 15), False),
				(self.tiles["horiznc"], self.screen, (64, 15), False),

				(self.tiles["horiz"],   LaKr,        (40, 15), False),
				(self.tiles["horiznc"], LaKr,        (41, 15), False),
				(self.tiles["horiz"],   LaKr,        (42, 15), False),
			], True)
		self.blocks["H23"].AddTrainLoc(self.screen, (58, 15))
		self.blocks["H23"].AddTrainLoc(LaKr, (41, 15))
		self.blocks["H23"].AddStoppingBlock([
				(self.tiles["horiznc"], LaKr,        (43, 15), False),
				(self.tiles["horiz"],   LaKr,        (44, 15), False),
				(self.tiles["eobright"], LaKr,       (45, 15), False),
				], True)

		self.blocks["HOSEE"] = OverSwitch(self, self.frame, "HOSEE", 
			[
				(self.tiles["horiznc"], self.screen, (42, 15), False),
				(self.tiles["horiz"],   self.screen, (43, 15), False),
				(self.tiles["horiznc"], self.screen, (44, 15), False),
				(self.tiles["horiz"],   self.screen, (45, 15), False),
				(self.tiles["horiznc"], self.screen, (46, 15), False),
				(self.tiles["horiz"],   self.screen, (47, 15), False),
				(self.tiles["horiznc"], self.screen, (48, 15), False),
				(self.tiles["horiz"],   self.screen, (49, 15), False),
				(self.tiles["horiznc"], self.screen, (51, 15), False),
				(self.tiles["horiz"],   self.screen, (52, 15), False),
				(self.tiles["horiznc"], self.screen, (54, 15), False),
				(self.tiles["horiz"],   self.screen, (55, 15), False),
				(self.tiles["eobright"], self.screen, (56, 15), False),

				(self.tiles["horiznc"], self.screen, (42, 17), False),
				(self.tiles["horiz"],   self.screen, (43, 17), False),
				(self.tiles["horiznc"], self.screen, (44, 17), False),
				(self.tiles["horiz"],   self.screen, (45, 17), False),
				(self.tiles["horiznc"], self.screen, (46, 17), False),
				(self.tiles["horiz"],   self.screen, (47, 17), False),
				(self.tiles["diagleft"], self.screen, (49, 16), False),

				(self.tiles["horiznc"], self.screen, (42, 19), False),
				(self.tiles["horiz"],   self.screen, (43, 19), False),
				(self.tiles["horiznc"], self.screen, (44, 19), False),
				(self.tiles["horiz"],   self.screen, (45, 19), False),
				(self.tiles["diagleft"], self.screen, (47, 18), False),

				(self.tiles["horiznc"], self.screen, (42, 21), False),
				(self.tiles["horiz"],   self.screen, (43, 21), False),
				(self.tiles["turnleftright"], self.screen, (44, 21), False),
				(self.tiles["diagleft"], self.screen, (45, 20), False),

				(self.tiles["horiznc"], self.screen, (42, 23), False),
				(self.tiles["horiz"],   self.screen, (43, 23), False),
				(self.tiles["horiznc"], self.screen, (44, 23), False),
				(self.tiles["turnleftright"], self.screen, (45, 23), False),
				(self.tiles["diagleft"], self.screen, (46, 22), False),
				(self.tiles["diagleft"], self.screen, (47, 21), False),
				(self.tiles["diagleft"], self.screen, (48, 20), False),
				(self.tiles["diagleft"], self.screen, (49, 19), False),
				(self.tiles["diagleft"], self.screen, (50, 18), False),
				(self.tiles["diagleft"], self.screen, (51, 17), False),
				(self.tiles["diagleft"], self.screen, (52, 16), False),
			], True)
		self.blocks["HOSEE"].AddTrainLoc(self.screen, (51, 22))

		self.osBlocks["HOSEE"] = ["H23", "H22", "H40", "H41", "H42", "H43"]

		# Blocks H10 and H20 are managed by shore district
		self.blocks["H10"] = Block(self, self.frame, "H10",
			[
				(self.tiles["horiznc"],  LaKr,    (108, 11), False),
				(self.tiles["horiz"],    LaKr,    (109, 11), False),
				(self.tiles["horiznc"],  LaKr,    (110, 11), False),
				(self.tiles["horiz"],    LaKr,    (111, 11), False),
				(self.tiles["horiznc"],  LaKr,    (112, 11), False),
				(self.tiles["eobright"], LaKr,    (113, 11), False),
			], False)
		self.blocks["H10"].AddStoppingBlock([
				(self.tiles["eobleft"],  LaKr,    (106, 11), False),
				(self.tiles["horiz"],    LaKr,    (107, 11), False),
			], False)
		self.blocks["H10"].AddTrainLoc(LaKr, (108, 11))

		self.blocks["H20"] = Block(self, self.frame, "H20",
			[
				(self.tiles["eobleft"],  LaKr,    (106, 13), False),
				(self.tiles["horiz"],    LaKr,    (107, 13), False),
				(self.tiles["horiznc"],  LaKr,    (108, 13), False),
				(self.tiles["horiz"],    LaKr,    (109, 13), False),
				(self.tiles["horiznc"],  LaKr,    (110, 13), False),
				(self.tiles["horiz"],    LaKr,    (111, 13), False),
			], True)
		self.blocks["H20"].AddStoppingBlock([
				(self.tiles["horiznc"],  LaKr,    (112, 13), False),
				(self.tiles["eobright"], LaKr,    (113, 13), False),
			], True)
		self.blocks["H20"].AddTrainLoc(LaKr, (108, 13))

		return self.blocks, self.osBlocks

	def DefineTurnouts(self, blocks):
		self.turnouts = {}

		toList = [
			["HSw7b", "toleftleft",    ["HOSWW", "HOSWW2"], (30, 5)],

			["HSw1",  "toleftright",   ["HOSWW"], (22, 13)],
			["HSw3",  "toleftright",   ["HOSWW"], (25, 13)],
			["HSw5",  "torightupinv",  ["HOSWW"], (26, 9)],
			["HSw7",  "torightupinv",  ["HOSWW"], (28, 7)],

			["HSw9",  "torightright",  ["HOSWE"], (22, 15)],
			["HSw11", "torightright",  ["HOSWE"], (25, 15)],
			["HSw13", "toleftdowninv", ["HOSWE"], (26, 19)],

			["HSw15", "torightleft",   ["HOSEW"], (45, 13)],
			["HSw17", "torightleft",   ["HOSEW"], (48, 13)],
			["HSw19", "torightleft",   ["HOSEW"], (51, 13)],
			["HSw21", "torightleft",   ["HOSEW"], (54, 13)],

			["HSw23", "torightdown",   ["HOSEE"], (46, 19)],
			["HSw25", "torightdown",   ["HOSEE"], (48, 17)],
			["HSw27", "toleftleft",    ["HOSEE"], (50, 15)],
			["HSw29", "toleftleft",    ["HOSEE"], (53, 15)],
		]

		for tonm, tileSet, blklist, pos in toList:
			trnout = Turnout(self, self.frame, tonm, self.screen, self.totiles[tileSet], pos)
			for blknm in blklist:
				blocks[blknm].AddTurnout(trnout)
				trnout.AddBlock(blknm)
			self.turnouts[tonm] = trnout
		
		for tonm in [to[0] for to in toList]:
			self.turnouts[tonm].SetRouteControl(True)

		self.turnouts["HSw7"].SetPairedTurnout(self.turnouts["HSw7b"])
		self.turnouts["HSw3"].SetPairedTurnout(self.turnouts["HSw5"])
		self.turnouts["HSw11"].SetPairedTurnout(self.turnouts["HSw13"])
		
		return self.turnouts

	def DefineSignals(self):
		self.signals = {}
		self.osProxies = {}

		sigList = [
			["H4LA", RegAspects, False, "left",  (32, 14)],
			["H4LB", RegAspects, False, "left",  (32, 16)],
			["H4LC", RegAspects, False, "left",  (32, 18)],
			["H4LD", RegAspects, False, "left",  (32, 20)],
			["H4R",  RegAspects, True,  "rightlong", (21, 16)],
			
			["H6LA", RegAspects, False, "leftlong",  (32, 6)],
			["H6LB", RegAspects, False, "leftlong",  (32, 8)],
			["H6LC", RegAspects, False, "leftlong",  (32, 10)],
			["H6LD", RegAspects, False, "leftlong",  (32, 12)],
			["H6R",  RegAspects, True,  "right", (21, 14)],
			
			["H8L",  RegAspects, False, "leftlong",  (32, 4)],
			["H8R",  RegAspects, True,  "right", (27, 6)],
			
			["H10L", RegAspects, False, "left",  (56, 14)],
			["H10RA", RegAspects, True, "rightlong", (41, 16)],
			["H10RB", RegAspects, True, "rightlong", (41, 18)],
			["H10RC", RegAspects, True, "rightlong", (41, 20)],
			["H10RD", RegAspects, True, "rightlong", (41, 22)],
			["H10RE", RegAspects, True, "rightlong", (41, 24)],
			
			["H12RA", RegAspects, True, "right", (41, 6)],
			["H12RB", RegAspects, True, "right", (41, 8)],
			["H12RC", RegAspects, True, "right", (41, 10)],
			["H12RD", RegAspects, True, "right", (41, 12)],
			["H12RE", RegAspects, True, "right", (41, 14)],
			["H12L", RegAspects, False, "leftlong", (56, 12)],
		]
		for signm, atype, east, tileSet, pos in sigList:
			self.signals[signm]  = Signal(self, self.screen, self.frame, signm, atype, east, pos, self.sigtiles[tileSet])

		sigs = ["H4LA", "H4LB", "H4LC", "H4LD"]
		for s in sigs:
			self.signals[s].SetMutexSignals([x for x in sigs if x != s])

		sigs = ["H6LA", "H6LB", "H6LC", "H6LD"]
		for s in sigs:
			self.signals[s].SetMutexSignals([x for x in sigs if x != s])

		sigs = ["H10RA", "H10RB", "H10RC", "H10RD", "H10RE"]
		for s in sigs:
			self.signals[s].SetMutexSignals([x for x in sigs if x != s])

		sigs = ["H12RA", "H12RB", "H12RC", "H12RD", "H12RE"]
		for s in sigs:
			self.signals[s].SetMutexSignals([x for x in sigs if x != s])

		blockSbSigs = {
			# which signals govern stopping sections, west and east
			"H11": ("S20L", None),
			"H13": ("H12L",  None),
			"H21": (None, "H4R"),
			"H23": (None,  "D4RB"),
			"H30": ("S12LB", None),
			"H10": ("S12LC", None),
			"H20": (None, "S18R"),
		}

		for blknm, siglist in blockSbSigs.items():
			self.blocks[blknm].SetSBSignals(siglist)

		self.blockSigs = {
			# which signals govern blocks, west and east
			"H10": ("S12LC", "S20R"),
			"H11": ("S20L",  "H6R"),
			"H12": ("H6LD",  "H12RE"),
			"H13": ("H12L",  "D6RA"),
			
			"H20": ("S4LA",  "S18R"),
			"H21": ("S18LA", "H4R"),
			"H22": ("H4LA",  "H10RA"),
			"H23": ("H10L",  "D4RB"),
			
			"H30": ("S12LB", "H8R"),
			"H31": ("H8L",   "H12RA"),
			"H32": ("H6LA",  "H12RB"),
			"H33": ("H6LB",  "H12RC"),
			"H34": ("H6LC",  "H12RD"),
			
			"H40": ("S18LB", "H10RE"),
			"H41": ("H4LD",  "H10RD"),
			"H42": ("H4LC",  "H10RC"),
			"H43": ("H4LB",  "H10RB"),
		}

		for blknm, siglist in self.blockSigs.items():
			self.blocks[blknm].SetSignals(siglist)

		self.routes = {}
		self.buttonToRoute = {}

		block = self.blocks["HOSWW"]
		self.routes["HRtH11H12"] = Route(self.screen, block, "HRtH11H12", "H12", [(21, 13), (22, 13), (23, 13), (24, 13), (25, 13), (26, 13), (27, 13), (28, 13), (29, 13), (30, 13), (31, 13)], "H11", [RESTRICTING, RESTRICTING], ["HSw1:N", "HSw3:N"], ["H6LD", "H6R"])
		self.routes["HRtH11H31"] = Route(self.screen, block, "HRtH11H31", "H31", [(21, 13), (22, 13), (23, 12), (24, 11), (25, 10), (26, 9), (27, 8), (28, 7), (29, 6), (30, 5), (31, 5)], "H11", [RESTRICTING, RESTRICTING], ["HSw1:R", "HSw3:R", "HSw7:R"], ["H8L", "H6R"])
		self.routes["HRtH11H32"] = Route(self.screen, block, "HRtH11H32", "H32", [(21, 13), (22, 13), (23, 12), (24, 11), (25, 10), (26, 9), (27, 8), (28, 7), (29, 7), (30, 7), (31, 7)], "H11", [RESTRICTING, RESTRICTING], ["HSw1:R", "HSw3:R", "HSw7:N"], ["H6LA", "H6R"])
		self.routes["HRtH11H33"] = Route(self.screen, block, "HRtH11H33", "H33", [(21, 13), (22, 13), (23, 12), (24, 11), (25, 10), (26, 9), (27, 9), (28, 9), (29, 9), (30, 9), (31, 9)], "H11", [RESTRICTING, RESTRICTING], ["HSw1:R", "HSw3:N"], ["H6LB", "H6R"])
		self.routes["HRtH11H34"] = Route(self.screen, block, "HRtH11H34", "H34", [(21, 13), (22, 13), (23, 13), (24, 13), (25, 13), (26, 12), (27, 11), (28, 11), (29, 11), (30, 11), (31, 11)], "H11", [RESTRICTING, RESTRICTING], ["HSw1:N", "HSw3:R"], ["H6LC", "H6R"])
		self.buttonToRoute["HWWB2"] = "HRtH11H31"
		self.buttonToRoute["HWWB3"] = "HRtH11H32"
		self.buttonToRoute["HWWB4"] = "HRtH11H33"
		self.buttonToRoute["HWWB5"] = "HRtH11H34"
		self.buttonToRoute["HWWB6"] = "HRtH11H12"

		block = self.blocks["HOSWW2"]			
		self.routes["HRtH30H31"] = Route(self.screen, block, "HRtH30H31", "H31", [(28, 5), (29, 5), (30, 5), (31, 5)], "H30", [RESTRICTING, MAIN], ["HSw7:N"], ["H8L", "H8R"])
		self.buttonToRoute["HWWB1"] = "HRtH30H31"

		# ===============================================================================
		# OS Proxies are only needed here because of common track between HOSWW and HOSWW2
		p = OSProxy(self, "HOSWW")
		self.osProxies["HOSWW"] = p
		p.AddRoute(self.routes["HRtH11H12"])
		p.AddRoute(self.routes["HRtH11H31"])
		p.AddRoute(self.routes["HRtH11H32"])
		p.AddRoute(self.routes["HRtH11H33"])
		p.AddRoute(self.routes["HRtH11H34"])

		p = OSProxy(self, "HOSWW2")
		self.osProxies["HOSWW2"] = p
		p.AddRoute(self.routes["HRtH11H31"])
		p.AddRoute(self.routes["HRtH30H31"])
		# ===============================================================================

		block = self.blocks["HOSWE"]
		self.routes["HRtH21H22"] = Route(self.screen, block, "HRtH21H22", "H21", [(21, 15), (22, 15), (23, 15), (24, 15), (25, 15), (26, 15), (27, 15), (28, 15), (29, 15), (30, 15), (31, 15)], "H22", [MAIN, RESTRICTING], ["HSw9:N", "HSw11:N"], ["H4R", "H4LA"])
		self.routes["HRtH21H41"] = Route(self.screen, block, "HRtH21H41", "H21", [(21, 15), (22, 15), (23, 16), (24, 17), (25, 18), (26, 19), (27, 20), (28, 21), (29, 21), (30, 21), (31, 21)], "H41", [DIVERGING, RESTRICTING], ["HSw9:R", "HSw11:R"], ["H4R", "H4LD"])
		self.routes["HRtH21H42"] = Route(self.screen, block, "HRtH21H42", "H21", [(21, 15), (22, 15), (23, 16), (24, 17), (25, 18), (26, 19), (27, 19), (28, 19), (29, 19), (30, 19), (31, 19)], "H42", [DIVERGING, RESTRICTING], ["HSw9:R", "HSw11:N"], ["H4R", "H4LC"])
		self.routes["HRtH21H43"] = Route(self.screen, block, "HRtH21H43", "H21", [(21, 15), (22, 15), (23, 15), (24, 15), (25, 15), (26, 16), (27, 17), (28, 17), (29, 17), (30, 17), (31, 17)], "H43", [DIVERGING, RESTRICTING], ["HSw9:N", "HSw11:R"], ["H4R", "H4LB"])
		self.buttonToRoute["HWEB1"] = "HRtH21H22"
		self.buttonToRoute["HWEB2"] = "HRtH21H43"
		self.buttonToRoute["HWEB3"] = "HRtH21H42"
		self.buttonToRoute["HWEB4"] = "HRtH21H41"

		block = self.blocks["HOSEW"]
		self.routes["HRtH13H31"] = Route(self.screen, block, "HRtH13H31", "H13", [(42, 5), (43, 5), (44, 5), (45, 5), (46, 5), (47, 6), (48, 7), (49, 8), (50, 9), (51, 10), (52, 11), (53, 12), (54, 13), (55, 13), (56, 13)], "H31", [RESTRICTING, DIVERGING], ["HSw21:R"], ["H12L", "H12RA"])
		self.routes["HRtH13H32"] = Route(self.screen, block, "HRtH13H32", "H13", [(42, 7), (43, 7), (44, 7), (45, 7), (46, 8), (47, 9), (48, 10), (49, 11), (50, 12), (51, 13), (52, 13), (53, 13), (54, 13), (55, 13), (56, 13)], "H32", [RESTRICTING, DIVERGING], ["HSw21:N", "HSw19:R"], ["H12L", "H12RB"])
		self.routes["HRtH13H33"] = Route(self.screen, block, "HRtH13H33", "H13", [(42, 9), (43, 9), (44, 9), (45, 10), (46, 11), (47, 12), (48, 13), (49, 13), (50, 13), (51, 13), (52, 13), (53, 13), (54, 13), (55, 13), (56, 13)], "H33", [RESTRICTING, DIVERGING], ["HSw21:N", "HSw19:N", "HSw17:R"], ["H12L", "H12RC"])
		self.routes["HRtH13H34"] = Route(self.screen, block, "HRtH13H34", "H13", [(42, 11), (43, 11), (44, 12), (45, 13), (46, 13), (47, 13), (48, 13), (49, 13), (50, 13), (51, 13), (52, 13), (53, 13), (54, 13), (55, 13), (56, 13)], "H34", [RESTRICTING, DIVERGING], ["HSw21:N", "HSw19:N", "HSw17:N", "HSw15:R"], ["H12L", "H12RD"])
		self.routes["HRtH12H13"] = Route(self.screen, block, "HRtH12H13", "H13", [(42, 13), (43, 13), (44, 13), (45, 13), (46, 13), (47, 13), (48, 13), (49, 13), (50, 13), (51, 13), (52, 13), (53, 13), (54, 13), (55, 13), (56, 13)], "H12", [RESTRICTING, MAIN], ["HSw21:N", "HSw19:N", "HSw17:N", "HSw15:N"], ["H12L", "H12RE"])
		self.buttonToRoute["HEWB1"] = "HRtH13H31"
		self.buttonToRoute["HEWB2"] = "HRtH13H32"
		self.buttonToRoute["HEWB3"] = "HRtH13H33"
		self.buttonToRoute["HEWB4"] = "HRtH13H34"
		self.buttonToRoute["HEWB5"] = "HRtH12H13"

		block = self.blocks["HOSEE"]
		self.routes["HRtH22H23"] = Route(self.screen, block, "HRtH22H23", "H22", [(42, 15), (43, 15), (44, 15), (45, 15), (46, 15), (47, 15), (48, 15), (49, 15), (50, 15), (51, 15), (52, 15), (53, 15), (54, 15), (55, 15), (56, 15)], "H23", [RESTRICTING, RESTRICTING], ["HSw27:N", "HSw29:N"], ["H10RA", "H10L"])
		self.routes["HRtH23H40"] = Route(self.screen, block, "HRtH23H40", "H40", [(42, 23), (43, 23), (44, 23), (45, 23), (46, 22), (47, 21), (48, 20), (49, 19), (50, 18), (51, 17), (52, 16), (53, 15), (54, 15), (55, 15), (56, 15)], "H23", [RESTRICTING, RESTRICTING], ["HSw29:R"], ["H10RE", "H10L"])
		self.routes["HRtH23H43"] = Route(self.screen, block, "HRtH23H43", "H43", [(42, 17), (43, 17), (44, 17), (45, 17), (46, 17), (47, 17), (48, 17), (49, 16), (50, 15), (51, 15), (52, 15), (53, 15), (54, 15), (55, 15), (56, 15)], "H23", [RESTRICTING, RESTRICTING], ["HSw25:R", "HSw27:R", "HSw29:N"], ["H10RB", "H10L"])
		self.routes["HRtH23H42"] = Route(self.screen, block, "HRtH23H42", "H42", [(42, 19), (43, 19), (44, 19), (45, 19), (46, 19), (47, 18), (48, 17), (49, 16), (50, 15), (51, 15), (52, 15), (53, 15), (54, 15), (55, 15), (56, 15)], "H23", [RESTRICTING, RESTRICTING], ["HSw23:R", "HSw25:N", "HSw27:R", "HSw29:N"], ["H10RC", "H10L"])
		self.routes["HRtH23H41"] = Route(self.screen, block, "HRtH23H41", "H41", [(42, 21), (43, 21), (44, 21), (45, 20), (46, 19), (47, 18), (48, 17), (49, 16), (50, 15), (51, 15), (52, 15), (53, 15), (54, 15), (55, 15), (56, 15)], "H23", [RESTRICTING, RESTRICTING], ["HSw23:N", "HSw25:N", "HSw27:R", "HSw29:N"], ["H10RD", "H10L"])
		self.buttonToRoute["HEEB1"] = "HRtH22H23"
		self.buttonToRoute["HEEB2"] = "HRtH23H43"
		self.buttonToRoute["HEEB3"] = "HRtH23H42"
		self.buttonToRoute["HEEB4"] = "HRtH23H41"
		self.buttonToRoute["HEEB5"] = "HRtH23H40"

		self.signals["H4LA"].AddPossibleRoutes("HOSWE", ["HRtH21H22"])
		self.signals["H4LB"].AddPossibleRoutes("HOSWE", ["HRtH21H43"])
		self.signals["H4LC"].AddPossibleRoutes("HOSWE", ["HRtH21H42"])
		self.signals["H4LD"].AddPossibleRoutes("HOSWE", ["HRtH21H41"])
		self.signals["H4R"].AddPossibleRoutes("HOSWE",  ["HRtH21H41", "HRtH21H42", "HRtH21H43", "HRtH21H22"])

		self.signals["H6LA"].AddPossibleRoutes("HOSWW", ["HRtH11H32"])
		self.signals["H6LB"].AddPossibleRoutes("HOSWW", ["HRtH11H33"])
		self.signals["H6LC"].AddPossibleRoutes("HOSWW", ["HRtH11H34"])
		self.signals["H6LD"].AddPossibleRoutes("HOSWW", ["HRtH11H12"])
		self.signals["H6R"].AddPossibleRoutes("HOSWW",  ["HRtH11H31", "HRtH11H32", "HRtH11H33", "HRtH11H34", "HRtH11H12"])

		self.signals["H8L"].AddPossibleRoutes("HOSWW",  ["HRtH11H31"])
		self.signals["H8L"].AddPossibleRoutes("HOSWW2", ["HRtH30H31"])
		self.signals["H8R"].AddPossibleRoutes("HOSWW2", ["HRtH30H31"])

		self.signals["H10L"].AddPossibleRoutes("HOSEE",  ["HRtH22H23", "HRtH23H40", "HRtH23H41", "HRtH23H42", "HRtH23H43"])
		self.signals["H10RA"].AddPossibleRoutes("HOSEE", ["HRtH22H23"])
		self.signals["H10RB"].AddPossibleRoutes("HOSEE", ["HRtH23H43"])
		self.signals["H10RC"].AddPossibleRoutes("HOSEE", ["HRtH23H42"])
		self.signals["H10RD"].AddPossibleRoutes("HOSEE", ["HRtH23H41"])
		self.signals["H10RE"].AddPossibleRoutes("HOSEE", ["HRtH23H40"])

		self.signals["H12L"].AddPossibleRoutes("HOSEW",  ["HRtH13H31", "HRtH13H32", "HRtH13H33", "HRtH13H34", "HRtH12H13"])
		self.signals["H12RA"].AddPossibleRoutes("HOSEW", ["HRtH13H31"])
		self.signals["H12RB"].AddPossibleRoutes("HOSEW", ["HRtH13H32"])
		self.signals["H12RC"].AddPossibleRoutes("HOSEW", ["HRtH13H33"])
		self.signals["H12RD"].AddPossibleRoutes("HOSEW", ["HRtH13H34"])
		self.signals["H12RE"].AddPossibleRoutes("HOSEW", ["HRtH12H13"])

		self.osSignals = {
					"HOSWW": ["H8L", "H6LA", "H6LB", "H6LC", "H6LD", "H6R"],
					"HOSWW2": ["H8L", "H8R"],
					"HOSWE": ["H4LA", "H4LB", "H4LC", "H4LD", "H4R"],
					"HOSEW": ["H12L", "H12RA", "H12RB", "H12RC", "H12RD", "H12RE"],
					"HOSEE": ["H10L", "H10RA", "H10RB", "H10RC", "H10RD", "H10RE"]}
		return self.signals, self.blockSigs, self.osSignals, self.routes, self.osProxies

	def DefineIndicators(self):
		self.indicators = {}
		indNames = ["HydeEastPower", "HydeWestPower", "H30Power"]
		for ind in indNames:
			self.indicators[ind] = Indicator(self.frame, self, ind)

		return self.indicators

	def DefineButtons(self):
		self.buttons = {}
		self.osButtons = {}

		b = Button(self, self.screen, self.frame, "HWWB1", (27, 5), self.btntiles)
		self.buttons["HWWB1"] = b

		b = Button(self, self.screen, self.frame, "HWWB2", (32, 5), self.btntiles)
		self.buttons["HWWB2"] = b

		b = Button(self, self.screen, self.frame, "HWWB3", (32, 7), self.btntiles)
		self.buttons["HWWB3"] = b

		b = Button(self, self.screen, self.frame, "HWWB4", (32, 9), self.btntiles)
		self.buttons["HWWB4"] = b

		b = Button(self, self.screen, self.frame, "HWWB5", (32, 11), self.btntiles)
		self.buttons["HWWB5"] = b

		b = Button(self, self.screen, self.frame, "HWWB6", (32, 13), self.btntiles)
		self.buttons["HWWB6"] = b

		self.osButtons["HOSWW"] = ["HWWB2", "HWWB3", "HWWB4", "HWWB5", "HWWB6"]
		self.osButtons["HOSWW2"] = ["HWWB1"]

		b = Button(self, self.screen, self.frame, "HWEB1", (32, 15), self.btntiles)
		self.buttons["HWEB1"] = b

		b = Button(self, self.screen, self.frame, "HWEB2", (32, 17), self.btntiles)
		self.buttons["HWEB2"] = b

		b = Button(self, self.screen, self.frame, "HWEB3", (32, 19), self.btntiles)
		self.buttons["HWEB3"] = b

		b = Button(self, self.screen, self.frame, "HWEB4", (32, 21), self.btntiles)
		self.buttons["HWEB4"] = b

		self.osButtons["HOSWE"] = ["HWEB1", "HWEB2", "HWEB3", "HWEB4"]

		b = Button(self, self.screen, self.frame, "HEWB1", (41, 5), self.btntiles)
		self.buttons["HEWB1"] = b

		b = Button(self, self.screen, self.frame, "HEWB2", (41, 7), self.btntiles)
		self.buttons["HEWB2"] = b

		b = Button(self, self.screen, self.frame, "HEWB3", (41, 9), self.btntiles)
		self.buttons["HEWB3"] = b

		b = Button(self, self.screen, self.frame, "HEWB4", (41, 11), self.btntiles)
		self.buttons["HEWB4"] = b

		b = Button(self, self.screen, self.frame, "HEWB5", (41, 13), self.btntiles)
		self.buttons["HEWB5"] = b

		self.osButtons["HOSEW"] = ["HEWB1", "HEWB2", "HEWB3", "HEWB4", "HEWB5"]

		b = Button(self, self.screen, self.frame, "HEEB1", (41, 15), self.btntiles)
		self.buttons["HEEB1"] = b

		b = Button(self, self.screen, self.frame, "HEEB2", (41, 17), self.btntiles)
		self.buttons["HEEB2"] = b

		b = Button(self, self.screen, self.frame, "HEEB3", (41, 19), self.btntiles)
		self.buttons["HEEB3"] = b

		b = Button(self, self.screen, self.frame, "HEEB4", (41, 21), self.btntiles)
		self.buttons["HEEB4"] = b

		b = Button(self, self.screen, self.frame, "HEEB5", (41, 23), self.btntiles)
		self.buttons["HEEB5"] = b

		self.osButtons["HOSEE"] = ["HEEB1", "HEEB2", "HEEB3", "HEEB4", "HEEB5"]

		b = Button(self, self.screen, self.frame, "HydeEastPower", (9, 4), self.btntiles)
		self.buttons["HydeEastPower"] = b

		b = Button(self, self.screen, self.frame, "HydeWestPower", (9, 6), self.btntiles)
		self.buttons["HydeWestPower"] = b

		b = Button(self, self.screen, self.frame, "H30Power", (9, 8), self.btntiles)
		self.buttons["H30Power"] = b

		return self.buttons
