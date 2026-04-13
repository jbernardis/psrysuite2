from dispatcher.district import District

from dispatcher.block import Block, OverSwitch, Route
from dispatcher.turnout import Turnout
from dispatcher.signal import Signal
from dispatcher.button import Button
from dispatcher.handswitch import HandSwitch

from dispatcher.constants import RESTRICTING, MAIN, DIVERGING, SLOW, RegAspects, RegSloAspects, SloAspects


class Cliff (District):
	def __init__(self, name, frame, screen):
		District.__init__(self, name, frame, screen)

	def SetUpRoute(self, osblk, route):
		controlOpt = self.frame.cliffControl
		if controlOpt == 0:  # Cliff local control
			self.frame.PopupEvent("Cliff control is local")
			return

		if controlOpt == 1:  # Cliff local control
			self.frame.PopupEvent("Dispatcher control is Bank/Cliveden only")
			return

		rtname = route.GetName()

		if rtname not in self.routeButtons:
			self.frame.PopupEvent("Unknown route: %s" % rtname)
			return

		bname = self.routeButtons[rtname]
		btn = self.frame.buttons[bname]
		self.ButtonClick(btn)

	def DetermineRoute(self, blocks):
		self.FindTurnoutCombinations(blocks, [
			"CSw31", "CSw33", "CSw35", "CSw37", "CSw39", "CSw41", "CSw43", "CSw45", "CSw47", "CSw49",
			"CSw51", "CSw53", "CSw55", "CSw57", "CSw59", "CSw61", "CSw63", "CSw65", "CSw67", "CSw69",
			"CSw71", "CSw73", "CSw75", "CSw77", "CSw79", "CSw81"])

	def DefineBlocks(self):
		self.blocks = {}
		self.osBlocks = {}

		self.blocks["G21"] = Block(self, self.frame, "G21",
			[
				(self.tiles["houtline"], self.screen,  (33, 21), False),
				(self.tiles["houtline"], self.screen,  (34, 21), False),
				(self.tiles["houtline"], self.screen,  (35, 21), False),
			], True)
		self.blocks["G21"].AddOOSLoc(self.screen, (35, 21))

		self.blocks["C10"] = Block(self, self.frame, "C10",
			[
				(self.tiles["horiznc"], self.screen,  (18, 19), False),
				(self.tiles["horiz"],   self.screen,  (19, 19), True),
				(self.tiles["horiznc"], self.screen,  (20, 19), False),
				(self.tiles["horiz"],   self.screen,  (21, 19), True),
				(self.tiles["horiznc"], self.screen,  (22, 19), False),
				(self.tiles["horiz"],   self.screen,  (23, 19), True),
				(self.tiles["horiznc"], self.screen,  (24, 19), False),
				(self.tiles["horiz"],   self.screen,  (25, 19), True),
				(self.tiles["horiznc"], self.screen,  (26, 19), False),
				(self.tiles["horiz"],   self.screen,  (27, 19), True),
				(self.tiles["horiznc"], self.screen,  (28, 19), False),
				(self.tiles["horiz"],   self.screen,  (29, 19), True),
				(self.tiles["horiznc"], self.screen,  (30, 19), False),
				(self.tiles["horiz"],   self.screen,  (31, 19), True),
				(self.tiles["horiznc"], self.screen,  (32, 19), False),
				(self.tiles["horiz"],   self.screen,  (33, 19), True),
				(self.tiles["horiznc"], self.screen,  (34, 19), False),
				(self.tiles["horiz"],   self.screen,  (35, 19), True),
			], True)
		self.blocks["C10"].AddTrainLoc(self.screen, (25, 19))
		self.blocks["C10"].AddOOSLoc(self.screen, (18, 19))
		self.blocks["C10"].AddOOSLoc(self.screen, (35, 19))

		self.blocks["C30"] = Block(self, self.frame, "C30",
			[
				(self.tiles["horiznc"], self.screen,  (18, 17), False),
				(self.tiles["horiz"],   self.screen,  (19, 17), True),
				(self.tiles["horiznc"], self.screen,  (21, 17), False),
				(self.tiles["horiz"],   self.screen,  (22, 17), True),
				(self.tiles["horiznc"], self.screen,  (23, 17), False),
				(self.tiles["horiz"],   self.screen,  (24, 17), True),
				(self.tiles["horiznc"], self.screen,  (25, 17), False),
				(self.tiles["horiz"],   self.screen,  (26, 17), True),
				(self.tiles["horiznc"], self.screen,  (27, 17), False),
				(self.tiles["horiz"],   self.screen,  (28, 17), True),
				(self.tiles["horiznc"], self.screen,  (29, 17), False),
				(self.tiles["horiz"],   self.screen,  (30, 17), True),
				(self.tiles["horiznc"], self.screen,  (31, 17), False),
				(self.tiles["horiz"],   self.screen,  (32, 17), True),
				(self.tiles["horiznc"], self.screen,  (33, 17), False),
				(self.tiles["horiznc"], self.screen,  (34, 17), False),
				(self.tiles["horiz"],   self.screen,  (35, 17), True),
			], True)
		self.blocks["C30"].AddTrainLoc(self.screen, (25, 17))
		self.blocks["C30"].AddOOSLoc(self.screen, (18, 17))
		self.blocks["C30"].AddOOSLoc(self.screen, (35, 17))

		self.blocks["C31"] = Block(self, self.frame, "C31",
			[
				(self.tiles["horiznc"], self.screen,  (35, 15), False),
				(self.tiles["horiznc"], self.screen,  (34, 15), False),
				(self.tiles["horiznc"], self.screen,  (33, 15), False),
				(self.tiles["horiznc"], self.screen,  (32, 15), False),
				(self.tiles["eobleft"], self.screen,  (31, 15), False),
			], True)
		self.blocks["C31"].AddTrainLoc(self.screen, (32, 15))
		self.blocks["C31"].AddOOSLoc(self.screen, (35, 15))

		self.blocks["COSGMW"] = OverSwitch(self, self.frame, "COSGMW",
			[
				(self.tiles["eobright"], self.screen,  (43, 19), False),

				(self.tiles["diagleft"], self.screen, (41, 20), False),
				(self.tiles["turnleftright"], self.screen, (40, 21), False),
				(self.tiles["horiznc"],  self.screen, (39, 21), False),
				(self.tiles["horiz"],    self.screen, (38, 21), True),
				(self.tiles["horiznc"],  self.screen, (37, 21), False),

				(self.tiles["horiz"],    self.screen, (40, 19), True),
				(self.tiles["horiznc"],  self.screen, (39, 19), False),
				(self.tiles["horiz"],    self.screen, (38, 19), True),
				(self.tiles["horiznc"],  self.screen, (37, 19), False),

				(self.tiles["diagright"], self.screen, (40, 18), False),

				(self.tiles["horiz"],    self.screen, (38, 17), True),
				(self.tiles["horiznc"],  self.screen, (37, 17), False),

				(self.tiles["diagright"], self.screen, (38, 16), False),
				(self.tiles["turnrightright"], self.screen, (37, 15), False),
			], True)
		self.blocks["COSGMW"].AddTrainLoc(self.screen, (38, 12))

		self.osBlocks["COSGMW"] = ["C11", "G21", "C10", "C30", "C31"]

		self.blocks["G12"] = Block(self, self.frame, "G12",
			[
				(self.tiles["houtline"], self.screen,  (18, 23), False),
				(self.tiles["houtline"], self.screen,  (19, 23), False),
				(self.tiles["houtline"], self.screen,  (20, 23), False),
			], True)
		self.blocks["G12"].AddOOSLoc(self.screen, (18, 23))

		self.blocks["G10"] = Block(self, self.frame, "G10",
			[
				(self.tiles["houtline"], self.screen, (18, 21), False),
				(self.tiles["houtline"], self.screen, (19, 21), False),
				(self.tiles["houtline"], self.screen, (20, 21), False),
			], True)
		self.blocks["G10"].AddOOSLoc(self.screen, (18, 21))

		self.blocks["C20"] = Block(self, self.frame, "C20",
			[
				(self.tiles["eobright"],  self.screen, (10, 19), False),
				(self.tiles["horiznc"],  self.screen, (9, 19), False),
				(self.tiles["horiz"],    self.screen, (8, 19), True),
				(self.tiles["horiznc"],  self.screen, (7, 19), False),
				(self.tiles["horiz"],    self.screen, (6, 19), True),

				(self.tiles["turnleftleft"], self.screen, (5, 19), False),
				(self.tiles["turnrightup"], self.screen, (4, 20), False),

				(self.tiles["verticalnc"], self.screen, (4, 21), False),
				(self.tiles["vertical"],   self.screen, (4, 22), True),
				(self.tiles["verticalnc"], self.screen, (4, 23), False),
				(self.tiles["vertical"],   self.screen, (4, 24), True),
				(self.tiles["verticalnc"], self.screen, (4, 25), False),
				(self.tiles["vertical"],   self.screen, (4, 26), True),
				(self.tiles["verticalnc"], self.screen, (4, 27), False),
				(self.tiles["vertical"],   self.screen, (4, 28), True),
				(self.tiles["verticalnc"], self.screen, (4, 29), False),
				(self.tiles["vertical"],   self.screen, (4, 30), True),
				(self.tiles["verticalnc"], self.screen, (4, 31), False),
				(self.tiles["vertical"],   self.screen, (4, 32), True),
				(self.tiles["verticalnc"], self.screen, (4, 33), False),
				(self.tiles["vertical"],   self.screen, (4, 34), True),
				(self.tiles["verticalnc"], self.screen, (4, 35), False),
				(self.tiles["vertical"],   self.screen, (4, 36), True),
				(self.tiles["verticalnc"], self.screen, (4, 37), False),
				(self.tiles["vertical"],   self.screen, (4, 38), True),
				(self.tiles["verticalnc"], self.screen, (4, 39), False),
				(self.tiles["vertical"],   self.screen, (4, 40), True),
				(self.tiles["verticalnc"], self.screen, (4, 41), False),
				(self.tiles["vertical"],   self.screen, (4, 42), True),
				(self.tiles["verticalnc"], self.screen, (4, 43), False),
				(self.tiles["vertical"],   self.screen, (4, 44), True),

				(self.tiles["turnleftdown"], self.screen, (4, 45), False),
				(self.tiles["turnrightleft"], self.screen, (5, 46), False),

				(self.tiles["horiz"],      self.screen, (6, 46), False),
				(self.tiles["eobright"],    self.screen, (7, 46), False),
			], True)
		self.blocks["C20"].AddTrainLoc(self.screen, (2, 30))
		self.blocks["C20"].AddOOSLoc(self.screen, (10, 19))
		self.blocks["C20"].AddOOSLoc(self.screen, (7, 46))

		self.blocks["COSGME"] = OverSwitch(self, self.frame, "COSGME",
			[
				(self.tiles["turnrightleft"],  self.screen, (16, 23), False),
				(self.tiles["diagright"],      self.screen, (15, 22), False),
				(self.tiles["diagright"],      self.screen, (13, 20), False),

				(self.tiles["eobright"],       self.screen, (11, 19), False),

				(self.tiles["horiznc"],        self.screen, (16, 21), False),
				(self.tiles["horiz"],          self.screen, (15, 21), True),

				(self.tiles["horiznc"],        self.screen, (16, 19), False),
				(self.tiles["horiz"],          self.screen, (15, 19), True),
				(self.tiles["horiznc"],        self.screen, (14, 19), False),

				(self.tiles["horiznc"],        self.screen, (16, 17), False),
				(self.tiles["turnleftleft"],  self.screen, (15, 17), False),
				(self.tiles["diagleft"],       self.screen, (14, 18), False),
			], True)
		self.blocks["COSGME"].AddTrainLoc(self.screen, (12, 12))

		self.osBlocks["COSGME"] = ["C10", "C30", "G12", "G10", "C20"]

	# 	# Sheffield yard and west OS
		self.blocks["C44"] = Block(self, self.frame, "C44",
			[
				(self.tiles["horiznc"],        self.screen, (20, 46), False),
				(self.tiles["horiz"],          self.screen, (21, 46), True),
				(self.tiles["horiznc"],        self.screen, (22, 46), False),
				(self.tiles["horiz"],          self.screen, (23, 46), True),
				(self.tiles["horiznc"],        self.screen, (24, 46), False),
				(self.tiles["horiz"],          self.screen, (25, 46), True),
				(self.tiles["horiznc"],        self.screen, (26, 46), False),
				(self.tiles["horiz"],          self.screen, (27, 46), True),
				(self.tiles["horiznc"],        self.screen, (28, 46), False),
				(self.tiles["horiz"],          self.screen, (29, 46), True),
				(self.tiles["horiznc"],        self.screen, (30, 46), False),
				(self.tiles["horiz"],          self.screen, (31, 46), True),
				(self.tiles["horiznc"],        self.screen, (32, 46), False),
				(self.tiles["horiz"],          self.screen, (33, 46), True),
				(self.tiles["horiznc"],        self.screen, (34, 46), False),
				(self.tiles["horiz"],          self.screen, (35, 46), True),
				(self.tiles["horiznc"],        self.screen, (36, 46), False),
				(self.tiles["horiz"],          self.screen, (37, 46), True),
				(self.tiles["horiznc"],        self.screen, (38, 46), False),
				(self.tiles["horiz"],          self.screen, (39, 46), True),
				(self.tiles["horiznc"],        self.screen, (40, 46), False),
				(self.tiles["horiz"],          self.screen, (41, 46), True),
				(self.tiles["horiznc"],        self.screen, (42, 46), False),
				(self.tiles["horiz"],          self.screen, (43, 46), True),
			], False)
		self.blocks["C44"].AddTrainLoc(self.screen, (28, 46))
		self.blocks["C44"].AddOOSLoc(self.screen, (20, 46))
		self.blocks["C44"].AddOOSLoc(self.screen, (43, 46))

		self.blocks["C43"] = Block(self, self.frame, "C43",
			[
				(self.tiles["horiznc"],        self.screen, (20, 44), False),
				(self.tiles["horiz"],          self.screen, (21, 44), True),
				(self.tiles["horiznc"],        self.screen, (22, 44), False),
				(self.tiles["horiz"],          self.screen, (23, 44), True),
				(self.tiles["horiznc"],        self.screen, (24, 44), False),
				(self.tiles["horiz"],          self.screen, (25, 44), True),
				(self.tiles["horiznc"],        self.screen, (26, 44), False),
				(self.tiles["horiz"],          self.screen, (27, 44), True),
				(self.tiles["horiznc"],        self.screen, (28, 44), False),
				(self.tiles["horiz"],          self.screen, (29, 44), True),
				(self.tiles["horiznc"],        self.screen, (30, 44), False),
				(self.tiles["horiz"],          self.screen, (31, 44), True),
				(self.tiles["horiznc"],        self.screen, (32, 44), False),
				(self.tiles["horiz"],          self.screen, (33, 44), True),
				(self.tiles["horiznc"],        self.screen, (34, 44), False),
				(self.tiles["horiz"],          self.screen, (35, 44), True),
				(self.tiles["horiznc"],        self.screen, (36, 44), False),
				(self.tiles["horiz"],          self.screen, (37, 44), True),
				(self.tiles["horiznc"],        self.screen, (38, 44), False),
				(self.tiles["horiz"],          self.screen, (39, 44), True),
				(self.tiles["horiznc"],        self.screen, (40, 44), False),
				(self.tiles["horiz"],          self.screen, (41, 44), True),
				(self.tiles["horiznc"],        self.screen, (42, 44), False),
				(self.tiles["horiz"],          self.screen, (43, 44), True),
			], False)
		self.blocks["C43"].AddTrainLoc(self.screen, (28, 44))
		self.blocks["C43"].AddOOSLoc(self.screen, (20, 44))
		self.blocks["C43"].AddOOSLoc(self.screen, (43, 44))

		self.blocks["C42"] = Block(self, self.frame, "C42",
			[
				(self.tiles["horiznc"],        self.screen, (20, 42), False),
				(self.tiles["horiz"],          self.screen, (21, 42), True),
				(self.tiles["horiznc"],        self.screen, (22, 42), False),
				(self.tiles["horiz"],          self.screen, (23, 42), True),
				(self.tiles["horiznc"],        self.screen, (24, 42), False),
				(self.tiles["horiz"],          self.screen, (25, 42), True),
				(self.tiles["horiznc"],        self.screen, (26, 42), False),
				(self.tiles["horiz"],          self.screen, (27, 42), True),
				(self.tiles["horiznc"],        self.screen, (28, 42), False),
				(self.tiles["horiz"],          self.screen, (29, 42), True),
				(self.tiles["horiznc"],        self.screen, (30, 42), False),
				(self.tiles["horiz"],          self.screen, (31, 42), True),
				(self.tiles["horiznc"],        self.screen, (32, 42), False),
				(self.tiles["horiz"],          self.screen, (33, 42), True),
				(self.tiles["horiznc"],        self.screen, (34, 42), False),
				(self.tiles["horiz"],          self.screen, (35, 42), True),
				(self.tiles["horiznc"],        self.screen, (36, 42), False),
				(self.tiles["horiz"],          self.screen, (37, 42), True),
				(self.tiles["horiznc"],        self.screen, (38, 42), False),
				(self.tiles["horiz"],          self.screen, (39, 42), True),
				(self.tiles["horiznc"],        self.screen, (40, 42), False),
				(self.tiles["horiz"],          self.screen, (41, 42), True),
				(self.tiles["horiznc"],        self.screen, (42, 42), False),
				(self.tiles["horiz"],          self.screen, (43, 42), True),
			], False)
		self.blocks["C42"].AddTrainLoc(self.screen, (28, 42))
		self.blocks["C42"].AddOOSLoc(self.screen, (20, 42))
		self.blocks["C42"].AddOOSLoc(self.screen, (43, 42))

		self.blocks["C41"] = Block(self, self.frame, "C41",
			[
				(self.tiles["horiznc"],        self.screen, (20, 40), False),
				(self.tiles["horiz"],          self.screen, (21, 40), True),
				(self.tiles["horiznc"],        self.screen, (22, 40), False),
				(self.tiles["horiz"],          self.screen, (23, 40), True),
				(self.tiles["horiznc"],        self.screen, (24, 40), False),
				(self.tiles["horiz"],          self.screen, (25, 40), True),
				(self.tiles["horiznc"],        self.screen, (26, 40), False),
				(self.tiles["horiz"],          self.screen, (27, 40), True),
				(self.tiles["horiznc"],        self.screen, (28, 40), False),
				(self.tiles["horiz"],          self.screen, (29, 40), True),
				(self.tiles["horiznc"],        self.screen, (30, 40), False),
				(self.tiles["horiz"],          self.screen, (31, 40), True),
				(self.tiles["horiznc"],        self.screen, (32, 40), False),
				(self.tiles["horiz"],          self.screen, (33, 40), True),
				(self.tiles["horiznc"],        self.screen, (34, 40), False),
				(self.tiles["horiz"],          self.screen, (35, 40), True),
				(self.tiles["horiznc"],        self.screen, (36, 40), False),
				(self.tiles["horiz"],          self.screen, (37, 40), True),
				(self.tiles["horiznc"],        self.screen, (38, 40), False),
				(self.tiles["horiz"],          self.screen, (39, 40), True),
				(self.tiles["horiznc"],        self.screen, (40, 40), False),
				(self.tiles["horiz"],          self.screen, (41, 40), True),
				(self.tiles["horiznc"],        self.screen, (42, 40), False),
				(self.tiles["horiz"],          self.screen, (43, 40), True),
			], False)
		self.blocks["C41"].AddTrainLoc(self.screen, (28, 40))
		self.blocks["C41"].AddOOSLoc(self.screen, (20, 40))
		self.blocks["C41"].AddOOSLoc(self.screen, (43, 40))

		self.blocks["C40"] = Block(self, self.frame, "C40",
			[
				(self.tiles["horiznc"],        self.screen, (25, 38), False),
				(self.tiles["horiz"],          self.screen, (26, 38), True),
				(self.tiles["horiznc"],        self.screen, (27, 38), False),
				(self.tiles["horiz"],          self.screen, (28, 38), True),
				(self.tiles["horiznc"],        self.screen, (29, 38), False),
				(self.tiles["horiz"],          self.screen, (30, 38), True),
				(self.tiles["horiznc"],        self.screen, (31, 38), False),
				(self.tiles["horiz"],          self.screen, (32, 38), True),
				(self.tiles["horiznc"],        self.screen, (33, 38), False),
				(self.tiles["horiz"],          self.screen, (34, 38), True),
				(self.tiles["horiznc"],        self.screen, (35, 38), False),
				(self.tiles["horiz"],          self.screen, (36, 38), True),
				(self.tiles["horiznc"],        self.screen, (37, 38), False),
				(self.tiles["horiz"],          self.screen, (38, 38), True),
				(self.tiles["horiznc"],        self.screen, (39, 38), False),
				(self.tiles["horiz"],          self.screen, (40, 38), True),
				(self.tiles["horiznc"],        self.screen, (41, 38), False),
				(self.tiles["horiz"],          self.screen, (42, 38), True),
				(self.tiles["horiznc"],        self.screen, (43, 38), False),
			], False)
		self.blocks["C40"].AddTrainLoc(self.screen, (28, 38))
		self.blocks["C40"].AddOOSLoc(self.screen, (25, 38))
		self.blocks["C40"].AddOOSLoc(self.screen, (43, 38))

		self.blocks["C21"] = Block(self, self.frame, "C21",
			[
				(self.tiles["horiznc"],        self.screen, (25, 36), False),
				(self.tiles["horiz"],          self.screen, (26, 36), True),
				(self.tiles["horiznc"],        self.screen, (27, 36), False),
				(self.tiles["horiz"],          self.screen, (28, 36), True),
				(self.tiles["horiznc"],        self.screen, (29, 36), False),
				(self.tiles["horiz"],          self.screen, (30, 36), True),
				(self.tiles["horiznc"],        self.screen, (31, 36), False),
				(self.tiles["horiz"],          self.screen, (32, 36), True),
				(self.tiles["horiznc"],        self.screen, (33, 36), False),
				(self.tiles["horiz"],          self.screen, (34, 36), True),
				(self.tiles["horiznc"],        self.screen, (35, 36), False),
				(self.tiles["horiz"],          self.screen, (36, 36), True),
				(self.tiles["horiznc"],        self.screen, (37, 36), False),
				(self.tiles["horiz"],          self.screen, (38, 36), True),
				(self.tiles["horiznc"],        self.screen, (39, 36), False),
				(self.tiles["horiz"],          self.screen, (40, 36), True),
				(self.tiles["horiznc"],        self.screen, (41, 36), False),
				(self.tiles["horiz"],          self.screen, (42, 36), True),
				(self.tiles["horiznc"],        self.screen, (43, 36), False),
			], False)
		self.blocks["C21"].AddTrainLoc(self.screen, (28, 36))
		self.blocks["C21"].AddOOSLoc(self.screen, (25, 36))
		self.blocks["C21"].AddOOSLoc(self.screen, (43, 36))

		self.blocks["C50"] = Block(self, self.frame, "C50",
			[
				(self.tiles["horiznc"],        self.screen, (25, 34), False),
				(self.tiles["horiz"],          self.screen, (26, 34), True),
				(self.tiles["horiznc"],        self.screen, (27, 34), False),
				(self.tiles["horiz"],          self.screen, (28, 34), True),
				(self.tiles["horiznc"],        self.screen, (29, 34), False),
				(self.tiles["horiz"],          self.screen, (30, 34), True),
				(self.tiles["horiznc"],        self.screen, (31, 34), False),
				(self.tiles["horiz"],          self.screen, (32, 34), True),
				(self.tiles["horiznc"],        self.screen, (33, 34), False),
				(self.tiles["horiz"],          self.screen, (34, 34), True),
				(self.tiles["horiznc"],        self.screen, (35, 34), False),
				(self.tiles["horiz"],          self.screen, (36, 34), True),
				(self.tiles["horiznc"],        self.screen, (37, 34), False),
				(self.tiles["horiz"],          self.screen, (38, 34), True),
				(self.tiles["horiznc"],        self.screen, (39, 34), False),
				(self.tiles["horiz"],          self.screen, (40, 34), True),
				(self.tiles["horiznc"],        self.screen, (41, 34), False),
				(self.tiles["horiz"],          self.screen, (42, 34), True),
				(self.tiles["horiznc"],        self.screen, (43, 34), False),
			], False)
		self.blocks["C50"].AddTrainLoc(self.screen, (28, 34))
		self.blocks["C50"].AddOOSLoc(self.screen, (25, 34))
		self.blocks["C50"].AddOOSLoc(self.screen, (43, 34))

		self.blocks["C51"] = Block(self, self.frame, "C51",
			[
				(self.tiles["horiznc"],        self.screen, (31, 32), False),
				(self.tiles["horiz"],          self.screen, (32, 32), True),
				(self.tiles["horiznc"],        self.screen, (33, 32), False),
				(self.tiles["horiz"],          self.screen, (34, 32), True),
				(self.tiles["horiznc"],        self.screen, (35, 32), False),
				(self.tiles["horiz"],          self.screen, (36, 32), True),
				(self.tiles["horiznc"],        self.screen, (37, 32), False),
			], False)
		self.blocks["C51"].AddTrainLoc(self.screen, (32, 32))
		self.blocks["C51"].AddOOSLoc(self.screen, (31, 32))
		self.blocks["C51"].AddOOSLoc(self.screen, (37, 32))

		self.blocks["C52"] = Block(self, self.frame, "C52",
			[
				(self.tiles["horiznc"],        self.screen, (31, 30), False),
				(self.tiles["horiz"],          self.screen, (32, 30), True),
				(self.tiles["horiznc"],        self.screen, (33, 30), False),
				(self.tiles["horiz"],          self.screen, (34, 30), True),
				(self.tiles["horiznc"],        self.screen, (35, 30), False),
				(self.tiles["horiz"],          self.screen, (36, 30), True),
				(self.tiles["horiznc"],        self.screen, (37, 30), False),
			], False)
		self.blocks["C52"].AddTrainLoc(self.screen, (32, 30))
		self.blocks["C52"].AddOOSLoc(self.screen, (31, 30))
		self.blocks["C52"].AddOOSLoc(self.screen, (37, 30))

		self.blocks["C53"] = Block(self, self.frame, "C53",
			[
				(self.tiles["horiznc"],        self.screen, (31, 28), False),
				(self.tiles["horiz"],          self.screen, (32, 28), True),
				(self.tiles["horiznc"],        self.screen, (33, 28), False),
				(self.tiles["horiz"],          self.screen, (34, 28), True),
				(self.tiles["horiznc"],        self.screen, (35, 28), False),
				(self.tiles["horiz"],          self.screen, (36, 28), True),
				(self.tiles["horiznc"],        self.screen, (37, 28), False),
			], False)
		self.blocks["C53"].AddTrainLoc(self.screen, (32, 28))
		self.blocks["C53"].AddOOSLoc(self.screen, (31, 28))
		self.blocks["C53"].AddOOSLoc(self.screen, (37, 28))

		self.blocks["C54"] = Block(self, self.frame, "C54",
			[
				(self.tiles["horiznc"],        self.screen, (31, 26), False),
				(self.tiles["horiz"],          self.screen, (32, 26), True),
				(self.tiles["horiznc"],        self.screen, (33, 26), False),
				(self.tiles["horiz"],          self.screen, (34, 26), True),
				(self.tiles["horiznc"],        self.screen, (35, 26), False),
				(self.tiles["horiz"],          self.screen, (36, 26), True),
				(self.tiles["horiznc"],        self.screen, (37, 26), False),
			], False)
		self.blocks["C54"].AddTrainLoc(self.screen, (32, 26))
		self.blocks["C54"].AddOOSLoc(self.screen, (31, 26))
		self.blocks["C54"].AddOOSLoc(self.screen, (37, 26))

		self.blocks["COSSHE"] = OverSwitch(self, self.frame, "COSSHE",
			[
				(self.tiles["horiznc"],        self.screen, (18, 46), False),
				(self.tiles["horiz"],          self.screen, (17, 46), True),
				(self.tiles["horiznc"],        self.screen, (16, 46), False),
				(self.tiles["horiz"],          self.screen, (15, 46), True),
				(self.tiles["horiznc"],        self.screen, (14, 46), False),
				(self.tiles["horiz"],          self.screen, (13, 46), True),
				(self.tiles["horiz"],          self.screen, (11, 46), True),
				(self.tiles["horiznc"],        self.screen, (10, 46), False),
				(self.tiles["eobleft"],        self.screen, (8, 46), False),

				(self.tiles["horiznc"],        self.screen, (18, 44), False),
				(self.tiles["horiz"],          self.screen, (17, 44), False),
				(self.tiles["horiznc"],        self.screen, (16, 44), False),
				(self.tiles["horiz"],          self.screen, (15, 44), False),
				(self.tiles["turnleftleft"],   self.screen, (14, 44), False),
				(self.tiles["diagleft"],       self.screen, (13, 44), False),

				(self.tiles["horiznc"],        self.screen, (18, 42), False),
				(self.tiles["horiz"],          self.screen, (17, 42), True),
				(self.tiles["horiz"],          self.screen, (15, 42), True),
				(self.tiles["horiznc"],        self.screen, (14, 42), False),
				(self.tiles["diagleft"],       self.screen, (12, 43), False),
				(self.tiles["diagleft"],       self.screen, (11, 44), False),
				(self.tiles["diagleft"],       self.screen, (10, 45), False),

				(self.tiles["turnleftleft"],   self.screen, (18, 40), False),
				(self.tiles["diagleft"],       self.screen, (17, 41), False),

				(self.tiles["horiz"],          self.screen, (23, 38), True),
				(self.tiles["horiznc"],        self.screen, (22, 38), False),
				(self.tiles["horiz"],          self.screen, (21, 38), True),
				(self.tiles["horiznc"],        self.screen, (20, 38), False),
				(self.tiles["horiz"],          self.screen, (19, 38), True),
				(self.tiles["horiznc"],        self.screen, (18, 38), False),
				(self.tiles["diagleft"],       self.screen, (16, 39), False),
				(self.tiles["diagleft"],       self.screen, (15, 40), False),
				(self.tiles["diagleft"],       self.screen, (14, 41), False),

				(self.tiles["horiz"],          self.screen, (23, 36), False),
				(self.tiles["horiznc"],        self.screen, (22, 36), False),
				(self.tiles["horiz"],          self.screen, (21, 36), True),
				(self.tiles["horiznc"],        self.screen, (20, 36), False),
				(self.tiles["diagleft"],       self.screen, (18, 37), False),

				(self.tiles["horiz"],          self.screen, (23, 34), False),
				(self.tiles["horiznc"],        self.screen, (22, 34), False),
				(self.tiles["diagleft"],       self.screen, (20, 35), False),

				(self.tiles["horiz"],          self.screen, (29, 32), True),
				(self.tiles["horiznc"],        self.screen, (28, 32), False),
				(self.tiles["horiz"],          self.screen, (27, 32), True),
				(self.tiles["horiz"],          self.screen, (25, 32), True),
				(self.tiles["horiznc"],        self.screen, (24, 32), False),
				(self.tiles["diagleft"],       self.screen, (22, 33), False),

				(self.tiles["horiz"],          self.screen, (29, 30), True),
				(self.tiles["turnleftleft"],   self.screen, (28, 30), False),
				(self.tiles["diagleft"],       self.screen, (27, 31), False),

				(self.tiles["horiz"],          self.screen, (29, 28), True),
				(self.tiles["horiznc"],        self.screen, (28, 28), False),
				(self.tiles["diagleft"],       self.screen, (26, 29), False),
				(self.tiles["diagleft"],       self.screen, (25, 30), False),
				(self.tiles["diagleft"],       self.screen, (24, 31), False),

				(self.tiles["turnleftleft"],   self.screen, (29, 26), False),
				(self.tiles["diagleft"],       self.screen, (28, 27), False),
			], False)
		self.blocks["COSSHE"].AddTrainLoc(self.screen, (12, 33))

		self.osBlocks["COSSHE"] = ["C44", "C43", "C42", "C41", "C40", "C21", "C50", "C51", "C52", "C53", "C54", "C20"]

		self.blocks["COSSHW"] = OverSwitch(self, self.frame, "COSSHW",
			[
				(self.tiles["eobright"],        self.screen, (56, 36), False),
				(self.tiles["diagleft"],       self.screen, (54, 37), False),
				(self.tiles["diagleft"],       self.screen, (53, 38), False),
				(self.tiles["diagleft"],       self.screen, (52, 39), False),
				(self.tiles["diagleft"],       self.screen, (50, 41), False),
				(self.tiles["diagleft"],       self.screen, (49, 42), False),
				(self.tiles["diagleft"],       self.screen, (48, 43), False),
				(self.tiles["diagleft"],       self.screen, (46, 45), False),
				(self.tiles["turnleftright"],  self.screen, (45, 46), False),

				(self.tiles["horiznc"],        self.screen, (46, 44), False),
				(self.tiles["horiz"],          self.screen, (45, 44), True),

				(self.tiles["horiznc"],        self.screen, (50, 40), False),
				(self.tiles["horiz"],          self.screen, (49, 40), True),
				(self.tiles["diagleft"],       self.screen, (47, 41), False),
				(self.tiles["turnleftright"],  self.screen, (46, 42), False),
				(self.tiles["horiz"],          self.screen, (45, 42), True),

				(self.tiles["horiz"],          self.screen, (47, 40), True),
				(self.tiles["horiznc"],        self.screen, (46, 40), False),
				(self.tiles["horiz"],          self.screen, (45, 40), True),

				(self.tiles["horiznc"],        self.screen, (54, 36), False),
				(self.tiles["horiz"],          self.screen, (53, 36), True),
				(self.tiles["diagleft"],       self.screen, (51, 37), False),
				(self.tiles["turnleftright"],  self.screen, (50, 38), False),
				(self.tiles["horiz"],          self.screen, (49, 38), True),
				(self.tiles["horiznc"],        self.screen, (48, 38), False),
				(self.tiles["horiz"],          self.screen, (47, 38), True),
				(self.tiles["horiznc"],        self.screen, (46, 38), False),
				(self.tiles["horiz"],          self.screen, (45, 38), True),

				(self.tiles["horiz"],          self.screen, (51, 36), True),
				(self.tiles["horiznc"],        self.screen, (50, 36), False),
				(self.tiles["horiznc"],        self.screen, (48, 36), False),
				(self.tiles["horiz"],          self.screen, (47, 36), True),
				(self.tiles["horiznc"],        self.screen, (46, 36), False),
				(self.tiles["horiz"],          self.screen, (45, 36), True),

				(self.tiles["diagright"],      self.screen, (48, 35), False),
				(self.tiles["horiznc"],        self.screen, (46, 34), False),
				(self.tiles["horiz"],          self.screen, (45, 34), True),

				(self.tiles["diagright"],      self.screen, (46, 33), False),
				(self.tiles["horiznc"],        self.screen, (44, 32), False),
				(self.tiles["horiz"],          self.screen, (43, 32), True),
				(self.tiles["horiz"],          self.screen, (41, 32), True),
				(self.tiles["horiznc"],        self.screen, (40, 32), False),
				(self.tiles["horiz"],          self.screen, (39, 32), True),

				(self.tiles["diagright"],      self.screen, (41, 31), False),
				(self.tiles["turnrightright"], self.screen, (40, 30), False),
				(self.tiles["horiz"],          self.screen, (39, 30), True),

				(self.tiles["diagright"],      self.screen, (44, 31), False),
				(self.tiles["diagright"],      self.screen, (43, 30), False),
				(self.tiles["diagright"],      self.screen, (42, 29), False),
				(self.tiles["horiznc"],        self.screen, (40, 28), False),
				(self.tiles["horiz"],          self.screen, (39, 28), True),

				(self.tiles["diagright"],      self.screen, (40, 27), False),
				(self.tiles["turnrightright"], self.screen, (39, 26), False),
			], False)
		self.blocks["COSSHW"].AddTrainLoc(self.screen, (52, 44))

		self.osBlocks["COSSHW"] = ["C22", "C44", "C43", "C42", "C41", "C40", "C21", "C50", "C51", "C52", "C53", "C54"]

		return self.blocks, self.osBlocks

	def DefineTurnouts(self, blocks):
		self.turnouts = {}

		hsList = [
			["CSw3",   "toleftright",   "C30", (20, 17)],
		]
		toList = [
			["CSw31",  "torightright",  ["COSGME"], (12, 19)],
			["CSw33",  "toleftright",   ["COSGME"], (13, 19)],
			["CSw35",  "toleftdown",    ["COSGME"], (14, 21)],
			["CSw37",  "toleftup",     ["COSGMW"], (39, 17)],
			["CSw39",  "torightleft",  ["COSGMW"], (41, 19)],
			["CSw41",  "toleftleft",   ["COSGMW"], (42, 19)],

			["CSw43",  "toleftright",   ["COSSHE"], (9, 46)],
			["CSw45",  "torightupinv",  ["COSSHE"], (13, 42)],
			["CSw47",  "torightupinv",  ["COSSHE"], (17, 38)],
			["CSw49",  "toleftright",   ["COSSHE"], (12, 46)],
			["CSw51",  "toleftright",   ["COSSHE"], (16, 42)],

			["CSw53",  "toleftleft",  ["COSSHW"], (48, 40)],
			["CSw55",  "toleftleft",  ["COSSHW"], (52, 36)],
			["CSw57",  "torightdown", ["COSSHW"], (47, 44)],
			["CSw59",  "torightdown", ["COSSHW"], (51, 40)],
			["CSw61",  "toleftleft",  ["COSSHW"], (55, 36)]
			,
			["CSw63",  "torightup",    ["COSSHE"], (19, 36)],
			["CSw65",  "torightup",    ["COSSHE"], (21, 34)],
			["CSw67",  "torightup",    ["COSSHE"], (23, 32)],
			["CSw69",  "toleftright",  ["COSSHE"], (26, 32)],
			["CSw71",  "torightup",    ["COSSHE"], (27, 28)],

			["CSw73",  "torightleft", ["COSSHW"], (49, 36)],
			["CSw75",  "toleftup",    ["COSSHW"], (47, 34)],
			["CSw77",  "toleftup",    ["COSSHW"], (45, 32)],
			["CSw79",  "torightleft", ["COSSHW"], (42, 32)],
			["CSw81",  "toleftup",    ["COSSHW"], (41, 28)],
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

		self.turnouts["CSw3"].SetDisabled(True)

		for tonm in [x[0] for x in toList]:
			self.turnouts[tonm].SetRouteControl(True)

		return self.turnouts

	def DefineButtons(self):
		self.buttons = {}
		self.osButtons = {}

		btnList = [
			["CG21W", (36, 21)],
			["CC10W", (36, 19)],
			["CC30W", (36, 17)],
			["CC31W", (36, 15)],
			["CG12E", (17, 23)],
			["CG10E", (17, 21)],
			["CC10E", (17, 19)],
			["CC30E", (17, 17)],

			["CC44E", (19, 46)],
			["CC43E", (19, 44)],
			["CC42E", (19, 42)],
			["CC41E", (19, 40)],
			["CC40E", (24, 38)],
			["CC21E", (24, 36)],
			["CC50E", (24, 34)],
			["CC51E", (30, 32)],
			["CC52E", (30, 30)],
			["CC53E", (30, 28)],
			["CC54E", (30, 26)],

			["CC44W", (44, 46)],
			["CC43W", (44, 44)],
			["CC42W", (44, 42)],
			["CC41W", (44, 40)],
			["CC40W", (44, 38)],
			["CC21W", (44, 36)],
			["CC50W", (44, 34)],
			["CC51W", (38, 32)],
			["CC52W", (38, 30)],
			["CC53W", (38, 28)],
			["CC54W", (38, 26)],
		]

		for btnnm, btnpos in btnList:
			self.buttons[btnnm] = Button(self, self.screen, self.frame, btnnm, btnpos, self.btntiles)

		self.osButtons["COSGMW"] = ["CG21W", "CC10W", "CC30W", "CC31W"]
		self.osButtons["COSGME"] = ["CG12E", "CG10E", "CC10E", "CC30E"]
		self.osButtons["COSSHE"] = [
			"CC44E", "CC43E", "CC42E", "CC41E", "CC40E", "CC21E", "CC50E", "CC51E", "CC52E", "CC53E", "CC54E"]
		self.osButtons["COSSHW"] = [
			"CC44W", "CC43W", "CC42W", "CC41W", "CC40W", "CC21W", "CC50W", "CC51W", "CC52W", "CC53W", "CC54W"]

		return self.buttons

	def DefineSignals(self):
		self.signals = {}
		self.osProxies = {}

		sigList = [
			["C2LD", RegAspects,    True,  "left",     (17, 22)],
			["C2LC", RegAspects,    True,  "left",     (17, 20)],
			["C2LB", RegAspects,    True,  "leftlong", (17, 18)],
			["C2LA", SloAspects,    True,  "left",     (17, 16)],

			["C2R",  RegSloAspects, False, "rightlong", (11, 20)],

			["C4L",  RegSloAspects, True,  "leftlong",  (43, 18)],

			["C4RD", RegAspects,    False, "right",     (36, 22)],
			["C4RC", RegAspects,    False, "rightlong", (36, 20)],
			["C4RB", SloAspects,    False, "right",     (36, 18)],
			["C4RA", SloAspects,    False, "right",     (36, 16)],

			["C6LF", RegAspects,    True,  "left",     (19, 45)],
			["C6LE", RegAspects,    True,  "left",     (19, 43)],
			["C6LD", RegAspects,    True,  "left",     (19, 41)],
			["C6LC", RegAspects,    True,  "left",     (19, 39)],
			["C6LB", RegAspects,    True,  "left",     (24, 37)],
			["C6LA", RegAspects,    True,  "left",     (24, 35)],
			["C6LG", RegAspects,    True,  "left",     (24, 33)],
			["C6LH", RegAspects,    True,  "left",     (30, 31)],
			["C6LJ", RegAspects,    True,  "left",     (30, 29)],
			["C6LK", RegAspects,    True,  "left",     (30, 27)],
			["C6LL", RegAspects,    True,  "left",     (30, 25)],

			["C6R",  RegAspects,    False, "rightlong",  (8, 47)],

			["C8L",  RegAspects,    True,  "leftlong", (56, 35)],

			["C8RF", RegAspects,    False, "right",      (44, 47)],
			["C8RE", RegAspects,    False, "right",      (44, 45)],
			["C8RD", RegAspects,    False, "right",      (44, 43)],
			["C8RC", RegAspects,    False, "right",      (44, 41)],
			["C8RB", RegAspects,    False, "right",      (44, 39)],
			["C8RA", RegAspects,    False, "right",      (44, 37)],
			["C8RG", RegAspects,    False, "right",      (44, 35)],
			["C8RH", RegAspects,    False, "right",      (38, 33)],
			["C8RJ", RegAspects,    False, "right",      (38, 31)],
			["C8RK", RegAspects,    False, "right",      (38, 29)],
			["C8RL", RegAspects,    False, "right",      (38, 27)],
		]

		self.sigLeverMap = {
			"C2.lvr": ["COSGME"],
			"C4.lvr": ["COSGMW"],
			"C6.lvr": ["COSSHE"],
			"C8.lvr": ["COSSHW"]
		}

		for sl in self.sigLeverMap:
			self.frame.AddSignalLever(sl, self)

		for signm, atype, east, tileSet, pos in sigList:
			self.signals[signm]  = Signal(self, self.screen, self.frame, signm, atype, east, pos, self.sigtiles[tileSet])

		self.signals["C2LA"].SetMutexSignals(["C2LB", "C2LC", "C2LD"])
		self.signals["C2LB"].SetMutexSignals(["C2LA", "C2LC", "C2LD"])
		self.signals["C2LC"].SetMutexSignals(["C2LA", "C2LB", "C2LD"])
		self.signals["C2LD"].SetMutexSignals(["C2LA", "C2LB", "C2LC"])

		self.signals["C4RA"].SetMutexSignals(["C4RB", "C4RC", "C4RD"])
		self.signals["C4RB"].SetMutexSignals(["C4RA", "C4RC", "C4RD"])
		self.signals["C4RC"].SetMutexSignals(["C4RA", "C4RB", "C4RD"])
		self.signals["C4RD"].SetMutexSignals(["C4RA", "C4RB", "C4RC"])

		sigs = ["C6LA", "C6LB", "C6LC", "C6LD", "C6LE", "C6LF", "C6LG", "C6LH", "C6LJ", "C6LK", "C6LL"]
		for s in sigs:
			self.signals[s].SetMutexSignals([x for x in sigs if x != s])

		sigs = ["C8RA", "C8RB", "C8RC", "C8RD", "C8RE", "C8RF", "C8RG", "C8RH", "C8RJ", "C8RK", "C8RL"]
		for s in sigs:
			self.signals[s].SetMutexSignals([x for x in sigs if x != s])

		self.blockSigs = {
			# # which signals govern blocks, west and east
			"C10": ("C4RC",  "C2LB"),
			"C20": ("C2R",   "C6R"),
			"C21": ("C8RA",  "C6LA"),
			"C30": ("C4RB",  "C2LA"),
			"C31": ("C4RA",  None),
			"C40": ("C8RB",  "C6LB"),
			"C41": ("C8RC",  "C6LC"),
			"C42": ("C8RD",  "C6LD"),
			"C43": ("C8RE",  "C6LE"),
			"C44": ("C8RF",  "C6LF"),
			"C50": ("C8RG",  "C6LG"),
			"C51": ("C8RH",  "C6LH"),
			"C52": ("C8RJ",  "C6LJ"),
			"C53": ("C8RK",  "C6LK"),
			"C54": ("C8RL",  "C6LL"),
			"G10": (None,    "C2LC"),
			"G12": (None,    "C2LD"),
			"G21": ("C4RD",  None),
		}

		for blknm, siglist in self.blockSigs.items():
			self.blocks[blknm].SetSignals(siglist)

		self.routes = {}
		self.osSignals = {}
		self.routeButtons = {}

		# Green Mountain West
		block = self.blocks["COSGMW"]
		self.routes["CRtC11G21"] = Route(self.screen, block, "CRtC11G21", "C11", [(43, 19), (42, 19), (41, 20), (40, 21), (39, 21), (38, 21), (37, 21)], "G21", [RESTRICTING, RESTRICTING], ["CSw41:R"], ["C4L", "C4RD"])
		self.routes["CRtC11C10"] = Route(self.screen, block, "CRtC11C10", "C11", [(43, 19), (42, 19), (41, 19), (40, 19), (39, 19), (38, 19), (37, 19)], "C10", [MAIN, MAIN], ["CSw39:N", "CSw41:N"], ["C4L", "C4RC"])
		self.routes["CRtC11C30"] = Route(self.screen, block, "CRtC11C30", "C11", [(43, 19), (42, 19), (41, 19), (40, 18), (39, 17), (38, 17), (37, 17)], "C30", [SLOW, SLOW], ["CSw37:R", "CSw39:R", "CSw41:N"], ["C4L", "C4RB"])
		self.routes["CRtC11C31"] = Route(self.screen, block, "CRtC11C31", "C11", [(43, 19), (42, 19), (41, 19), (40, 18), (39, 17), (38, 16), (37, 15)], "C31", [RESTRICTING, SLOW], ["CSw37:N", "CSw39:R", "CSw41:N"], ["C4L", "C4RA"])

		self.routeButtons["CRtC11G21"] = "CG21W"
		self.routeButtons["CRtC11C10"] = "CC10W"
		self.routeButtons["CRtC11C30"] = "CC30W"
		self.routeButtons["CRtC11C31"] = "CC31W"

		self.signals["C4L"].AddPossibleRoutes("COSGMW", ["CRtC11G21", "CRtC11C10", "CRtC11C30", "CRtC11C31"])
		self.signals["C4RD"].AddPossibleRoutes("COSGMW", ["CRtC11G21"])
		self.signals["C4RC"].AddPossibleRoutes("COSGMW", ["CRtC11C10"])
		self.signals["C4RB"].AddPossibleRoutes("COSGMW", ["CRtC11C30"])
		self.signals["C4RA"].AddPossibleRoutes("COSGMW", ["CRtC11C31"])

		self.osSignals["COSGMW"] = ["C4L", "C4RA", "C4RB", "C4RC", "C4RD"]

		# Green Mountain East
		block = self.blocks["COSGME"]
		self.routes["CRtG12C20"] = Route(self.screen, block, "CRtG12C20", "G12", [(11, 19), (12, 19), (13, 20), (14, 21), (15, 22), (16, 23)], "C20", [RESTRICTING, RESTRICTING], ["CSw31:R", "CSw35:N"], ["C2LD", "C2R"])
		self.routes["CRtG10C20"] = Route(self.screen, block, "CRtG10C20", "G10", [(11, 28), (12, 19), (13, 20), (14, 21), (15, 21), (16, 21)], "C20", [RESTRICTING, RESTRICTING], ["CSw31:R", "CSw35:R"], ["C2LC", "C2R"])
		self.routes["CRtC10C20"] = Route(self.screen, block, "CRtC10C20", "C10", [(11, 30), (12, 19), (13, 19), (14, 19), (15, 19), (16, 19)], "C20", [MAIN, MAIN], ["CSw31:N", "CSw33:N"], ["C2LB", "C2R"])
		self.routes["CRtC30C20"] = Route(self.screen, block, "CRtC30C20", "C30", [(11, 32), (12, 19), (13, 19), (14, 18), (15, 17), (16, 17)], "C20", [SLOW, SLOW], ["CSw31:N", "CSw33:R"], ["C2LA", "C2R"])

		self.routeButtons["CRtG12C20"] = "CG12E"
		self.routeButtons["CRtG10C20"] = "CG10E"
		self.routeButtons["CRtC10C20"] = "CC10E"
		self.routeButtons["CRtC30C20"] = "CC30E"

		self.signals["C2LD"].AddPossibleRoutes("COSGME", ["CRtG12C20"])
		self.signals["C2LC"].AddPossibleRoutes("COSGME", ["CRtG10C20"])
		self.signals["C2LB"].AddPossibleRoutes("COSGME", ["CRtC10C20"])
		self.signals["C2LA"].AddPossibleRoutes("COSGME", ["CRtC30C20"])
		self.signals["C2R"].AddPossibleRoutes("COSGME", ["CRtG12C20", "CRtG10C20", "CRtC10C20", "CRtC30C20"])

		self.osSignals["COSGME"] = ["C2LA", "C2LB", "C2LC", "C2LD", "C2R"]

		# Sheffield Yard East
		block = self.blocks["COSSHE"]
		self.routes["CRtC20C44"] = Route(self.screen, block, "CRtC20C44", "C20", [(8, 46), (9, 46), (10, 46), (11, 46), (12, 46), (13, 46), (14, 46), (15, 46), (16, 46), (17, 46), (18, 46)], "C44", [SLOW, SLOW], ["CSw43:N", "CSw49:N"], ["C6R", "C6LF"])
		self.routes["CRtC20C43"] = Route(self.screen, block, "CRtC20C43", "C20", [(8, 46), (9, 46), (10, 46), (11, 46), (12, 46), (13, 45), (14, 44), (15, 44), (16, 44), (17, 44), (18, 44)], "C43", [SLOW, SLOW], ["CSw43:N", "CSw49:R"], ["C6R", "C6LE"])
		self.routes["CRtC20C42"] = Route(self.screen, block, "CRtC20C42", "C20", [(8, 46), (9, 46), (10, 45), (11, 44), (12, 43), (13, 42), (14, 42), (15, 42), (16, 42), (17, 42), (18, 42)], "C42", [SLOW, SLOW], ["CSw43:R", "CSw45:N", "CSw51:N", "CSw47:N"], ["C6R", "C6LD"])
		self.routes["CRtC20C41"] = Route(self.screen, block, "CRtC20C41", "C20", [(8, 46), (9, 46), (10, 45), (11, 44), (12, 43), (13, 42), (14, 42), (15, 42), (16, 42), (17, 41), (18, 40)], "C41", [SLOW, SLOW], ["CSw43:R", "CSw45:N", "CSw51:R", "CSw47:R"], ["C6R", "C6LC"])
		self.routes["CRtC20C40"] = Route(self.screen, block, "CRtC20C40", "C20", [(8, 46), (9, 46), (10, 45), (11, 44), (12, 43), (13, 42), (14, 41), (15, 40), (16, 39), (17, 38), (18, 38), (19, 38), (20, 38), (21, 38), (22, 38), (23, 38)], "C40", [SLOW, SLOW], ["CSw43:R", "CSw45:R", "CSw47:N", "CSw51:N"], ["C6R", "C6LB"])
		self.routes["CRtC20C21"] = Route(self.screen, block, "CRtC20C21", "C20", [(8, 46), (9, 46), (10, 45), (11, 44), (12, 43), (13, 42), (14, 41), (15, 40), (16, 39), (17, 38), (18, 37), (19, 36), (20, 36), (21, 36), (22, 36), (23, 36)], "C21", [MAIN, MAIN], ["CSw43:R", "CSw45:R", "CSw47:R", "CSw51:R", "CSw63:R"], ["C6R", "C6LA"])
		self.routes["CRtC20C50"] = Route(self.screen, block, "CRtC20C50", "C20", [(8, 46), (9, 46), (10, 45), (11, 44), (12, 43), (13, 42), (14, 41), (15, 40), (16, 39), (17, 38), (18, 37), (19, 36), (20, 35), (21, 34), (22, 34), (23, 34)], "C50", [SLOW, SLOW], ["CSw43:R", "CSw45:R", "CSw47:R", "CSw51:R", "CSw63:N", "CSw65:R"], ["C6R", "C6LG"])

		self.routes["CRtC20C51"] = Route(self.screen, block, "CRtC20C51", "C20",
				[(90, 17), (8, 46), (9, 46), (10, 45), (11, 44), (12, 43), (13, 42), (14, 41), (15, 40), (16, 39), (17, 38), (18, 37), (19, 36), (20, 35), (21, 34), (22, 33), (23, 32), (24, 32), (25, 32), (26, 32), (27, 32), (28, 32), (29, 32)], "C51", [SLOW, SLOW], ["CSw43:R", "CSw45:R", "CSw47:R", "CSw51:R", "CSw63:N", "CSw65:N", "CSw67:R", "CSw69:N"], ["C6R", "C6LH"])
		self.routes["CRtC20C52"] = Route(self.screen, block, "CRtC20C52", "C20",
				[(90, 19), (8, 46), (9, 46), (10, 45), (11, 44), (12, 43), (13, 42), (14, 41), (15, 40), (16, 39), (17, 38), (18, 37), (19, 36), (20, 35), (21, 34), (22, 33), (23, 32), (24, 32), (25, 32), (26, 32), (27, 31), (28, 30), (29, 30)], "C52", [SLOW, SLOW], ["CSw43:R", "CSw45:R", "CSw47:R", "CSw51:R", "CSw63:N", "CSw65:N", "CSw67:R", "CSw69:R"], ["C6R", "C6LJ"])
		self.routes["CRtC20C53"] = Route(self.screen, block, "CRtC20C53", "C20",
				[(90, 21), (8, 46), (9, 46), (10, 45), (11, 44), (12, 43), (13, 42), (14, 41), (15, 40), (16, 39), (17, 38), (18, 37), (19, 36), (20, 35), (21, 34), (22, 33), (23, 32), (24, 31), (25, 30), (26, 29), (27, 28), (28, 28), (29, 28)], "C53", [SLOW, SLOW], ["CSw43:R", "CSw45:R", "CSw47:R", "CSw51:R", "CSw63:N", "CSw65:N", "CSw67:N", "CSw71:R"], ["C6R", "C6LK"])
		self.routes["CRtC20C54"] = Route(self.screen, block, "CRtC20C54", "C20",
				[(90, 23),  (8, 46), (9, 46), (10, 45), (11, 44), (12, 43), (13, 42), (14, 41), (15, 40), (16, 39), (17, 38), (18, 37), (19, 36), (20, 35), (21, 34), (22, 33), (23, 32), (24, 31), (25, 30), (26, 29), (27, 28), (28, 27), (29, 26)], "C54", [SLOW, SLOW], ["CSw43:R", "CSw45:R", "CSw47:R", "CSw51:R", "CSw63:N", "CSw65:N", "CSw67:N", "CSw71:N"], ["C6R", "C6LL"])

		self.routeButtons["CRtC20C44"] = "CC44E"
		self.routeButtons["CRtC20C43"] = "CC43E"
		self.routeButtons["CRtC20C42"] = "CC42E"
		self.routeButtons["CRtC20C41"] = "CC41E"
		self.routeButtons["CRtC20C40"] = "CC40E"
		self.routeButtons["CRtC20C21"] = "CC21E"
		self.routeButtons["CRtC20C50"] = "CC50E"
		self.routeButtons["CRtC20C51"] = "CC51E"
		self.routeButtons["CRtC20C52"] = "CC52E"
		self.routeButtons["CRtC20C53"] = "CC53E"
		self.routeButtons["CRtC20C54"] = "CC54E"

		self.signals["C6R"].AddPossibleRoutes("COSSHE", ["CRtC20C44", "CRtC20C43", "CRtC20C42", "CRtC20C41", "CRtC20C40", "CRtC20C21", "CRtC20C50", "CRtC20C51", "CRtC20C52", "CRtC20C53", "CRtC20C54"])
		self.signals["C6LA"].AddPossibleRoutes("COSSHE", ["CRtC20C21"])
		self.signals["C6LB"].AddPossibleRoutes("COSSHE", ["CRtC20C40"])
		self.signals["C6LC"].AddPossibleRoutes("COSSHE", ["CRtC20C41"])
		self.signals["C6LD"].AddPossibleRoutes("COSSHE", ["CRtC20C42"])
		self.signals["C6LE"].AddPossibleRoutes("COSSHE", ["CRtC20C43"])
		self.signals["C6LF"].AddPossibleRoutes("COSSHE", ["CRtC20C44"])
		self.signals["C6LG"].AddPossibleRoutes("COSSHE", ["CRtC20C50"])
		self.signals["C6LH"].AddPossibleRoutes("COSSHE", ["CRtC20C51"])
		self.signals["C6LJ"].AddPossibleRoutes("COSSHE", ["CRtC20C52"])
		self.signals["C6LK"].AddPossibleRoutes("COSSHE", ["CRtC20C53"])
		self.signals["C6LL"].AddPossibleRoutes("COSSHE", ["CRtC20C54"])

		self.osSignals["COSSHE"] = ["C6LA", "C6LB", "C6LC", "C6LD", "C6LE", "C6LF", "C6LG", "C6LH", "C6LJ", "C6LK", "C6LL", "C6R"]

		# Sheffield Yard West
		block = self.blocks["COSSHW"]
		self.routes["CRtC44C22"] = Route(self.screen, block, "CRtC44C22", "C44", [(56, 36), (55, 36), (54, 37), (53, 38), (52, 39), (51, 40), (50, 41), (49, 42), (48, 43), (47, 44), (46, 45), (45, 46)], "C22", [SLOW, SLOW], ["CSw57:N", "CSw59:N", "CSw61:R"], ["C8RF", "C8L"])
		self.routes["CRtC43C22"] = Route(self.screen, block, "CRtC43C22", "C43", [(56, 36), (55, 36), (54, 37), (53, 38), (52, 39), (51, 40), (50, 41), (49, 42), (48, 43), (47, 44), (46, 44), (45, 44)], "C22", [SLOW, SLOW], ["CSw57:R", "CSw59:N", "CSw61:R"], ["C8RE", "C8L"])
		self.routes["CRtC42C22"] = Route(self.screen, block, "CRtC42C22", "C42", [(56, 36), (55, 36), (54, 37), (53, 38), (52, 39), (51, 40), (50, 40), (49, 40), (48, 40), (47, 41), (46, 42), (45, 42)], "C22", [SLOW, SLOW], ["CSw53:R", "CSw59:R", "CSw61:R"], ["C8RD", "C8L"])
		self.routes["CRtC41C22"] = Route(self.screen, block, "CRtC41C22", "C41", [(56, 36), (55, 36), (54, 37), (53, 38), (52, 39), (51, 40), (50, 40), (49, 40), (48, 40), (47, 40), (46, 40), (45, 40)], "C22", [SLOW, SLOW], ["CSw53:N", "CSw59:R", "CSw61:R"], ["C8RC", "C8L"])
		self.routes["CRtC40C22"] = Route(self.screen, block, "CRtC40C22", "C40", [(56, 36), (55, 36), (54, 36), (53, 36), (52, 36), (51, 37), (50, 38), (49, 38), (48, 38), (47, 38), (46, 38), (45, 38)], "C22", [SLOW, SLOW], ["CSw55:R", "CSw61:N"], ["C8RB", "C8L"])
		self.routes["CRtC21C22"] = Route(self.screen, block, "CRtC21C22", "C21", [(56, 36), (55, 36), (54, 36), (53, 36), (52, 36), (51, 36), (50, 36), (49, 36), (48, 36), (47, 36), (46, 36), (45, 36)], "C22", [MAIN, DIVERGING], ["CSw55:N", "CSw61:N", "CSw73:N"], ["C8RA", "C8L"])
		self.routes["CRtC50C22"] = Route(self.screen, block, "CRtC50C22", "C50", [(56, 36), (55, 36), (54, 36), (53, 36), (52, 36), (51, 36), (50, 36), (49, 36), (48, 35), (47, 34), (46, 34), (45, 34) ], "C22", [SLOW, SLOW], ["CSw55:N", "CSw61:N", "CSw73:R", "CSw75:R"], ["C8RG", "C8L"])

		self.routes["CRtC51C22"] = Route(self.screen, block, "CRtC51C22", "C51", [
				(56, 36), (55, 36), (54, 36), (53, 36), (52, 36), (51, 36), (50, 36), (49, 36), (48, 35), (47, 34), (46, 33), (45, 32), (44, 32), (43, 32), (42, 32), (41, 32), (40, 32), (39, 32)], "C22", [SLOW, SLOW], ["CSw55:N", "CSw61:N", "CSw73:R", "CSw75:N", "CSw77:R", "CSw79:N"], ["C8RH", "C8L"])
		self.routes["CRtC52C22"] = Route(self.screen, block, "CRtC52C22", "C52", [
				(56, 36), (55, 36), (54, 36), (53, 36), (52, 36), (51, 36), (50, 36), (49, 36), (48, 35), (47, 34), (46, 33), (45, 32), (44, 32), (43, 32), (42, 32), (41, 31), (40, 30), (39, 30)], "C22", [SLOW, SLOW], ["CSw55:N", "CSw61:N", "CSw73:R", "CSw75:N", "CSw77:R", "CSw79:R"], ["C8RJ", "C8L"])
		self.routes["CRtC53C22"] = Route(self.screen, block, "CRtC53C22", "C53", [
				(56, 36), (55, 36), (54, 36), (53, 36), (52, 36), (51, 36), (50, 36), (49, 36), (48, 35), (47, 34), (46, 33), (45, 32), (44, 31), (43, 30), (42, 29), (41, 28), (40, 28), (39, 28)], "C22", [SLOW, SLOW], ["CSw55:N", "CSw61:N", "CSw73:R", "CSw75:N", "CSw77:N", "CSw81:R"], ["C8RK", "C8L"])
		self.routes["CRtC54C22"] = Route(self.screen, block, "CRtC54C22", "C54", [
				(56, 36), (55, 36), (54, 36), (53, 36), (52, 36), (51, 36), (50, 36), (49, 36), (48, 35), (47, 34), (46, 33), (45, 32), (44, 31), (43, 30), (42, 29), (41, 28), (40, 27), (39, 26)], "C22", [SLOW, SLOW], ["CSw55:N", "CSw61:N", "CSw73:R", "CSw75:N", "CSw77:N", "CSw81:N"], ["C8RL", "C8L"])

		self.routeButtons["CRtC44C22"] = "CC44W"
		self.routeButtons["CRtC43C22"] = "CC43W"
		self.routeButtons["CRtC42C22"] = "CC42W"
		self.routeButtons["CRtC41C22"] = "CC41W"
		self.routeButtons["CRtC40C22"] = "CC40W"
		self.routeButtons["CRtC21C22"] = "CC21W"
		self.routeButtons["CRtC50C22"] = "CC50W"
		self.routeButtons["CRtC51C22"] = "CC51W"
		self.routeButtons["CRtC52C22"] = "CC52W"
		self.routeButtons["CRtC53C22"] = "CC53W"
		self.routeButtons["CRtC54C22"] = "CC54W"

		self.signals["C8L"].AddPossibleRoutes("COSSHW", ["CRtC44C22", "CRtC43C22", "CRtC42C22", "CRtC41C22", "CRtC40C22", "CRtC21C22", "CRtC50C22", "CRtC51C22", "CRtC52C22", "CRtC53C22", "CRtC54C22"])
		self.signals["C8RA"].AddPossibleRoutes("COSSHW", ["CRtC21C22"])
		self.signals["C8RB"].AddPossibleRoutes("COSSHW", ["CRtC40C22"])
		self.signals["C8RC"].AddPossibleRoutes("COSSHW", ["CRtC41C22"])
		self.signals["C8RD"].AddPossibleRoutes("COSSHW", ["CRtC42C22"])
		self.signals["C8RE"].AddPossibleRoutes("COSSHW", ["CRtC43C22"])
		self.signals["C8RF"].AddPossibleRoutes("COSSHW", ["CRtC44C22"])
		self.signals["C8RG"].AddPossibleRoutes("COSSHW", ["CRtC50C22"])
		self.signals["C8RH"].AddPossibleRoutes("COSSHW", ["CRtC51C22"])
		self.signals["C8RJ"].AddPossibleRoutes("COSSHW", ["CRtC52C22"])
		self.signals["C8RK"].AddPossibleRoutes("COSSHW", ["CRtC53C22"])
		self.signals["C8RL"].AddPossibleRoutes("COSSHW", ["CRtC54C22"])

		self.osSignals["COSSHW"] = ["C8L", "C8RA", "C8RB", "C8RC", "C8RD", "C8RE", "C8RF", "C8RG", "C8RH", "C8RJ", "C8RK", "C8RL"]

		return self.signals, self.blockSigs, self.osSignals, self.routes, self.osProxies

	def DefineHandSwitches(self):
		self.handswitches = {}

		hs = HandSwitch(self, self.screen, self.frame, self.blocks["C30"], "CSw3.hand", (20, 16), self.misctiles["handdown"])
		self.blocks["C30"].AddHandSwitch(hs)
		self.handswitches["CSw3.hand"] = hs

		return self.handswitches
