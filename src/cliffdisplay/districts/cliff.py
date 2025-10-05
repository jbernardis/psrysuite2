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
		self.PerformButtonAction(btn)

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
				(self.tiles["houtline"], self.screen,  (84, 28), False),
				(self.tiles["houtline"], self.screen,  (85, 28), False),
				(self.tiles["houtline"], self.screen,  (86, 28), False),
			], True)

		self.blocks["C10"] = Block(self, self.frame, "C10",
			[
				(self.tiles["horiznc"], self.screen,  (84, 30), False),
				(self.tiles["horiz"],   self.screen,  (85, 30), False),
				(self.tiles["horiznc"], self.screen,  (86, 30), False),
				(self.tiles["horiz"],   self.screen,  (87, 30), False),
				(self.tiles["horiznc"], self.screen,  (88, 30), False),
				(self.tiles["horiz"],   self.screen,  (89, 30), False),
				(self.tiles["horiznc"], self.screen,  (90, 30), False),
				(self.tiles["horiz"],   self.screen,  (91, 30), False),
				(self.tiles["horiznc"], self.screen,  (92, 30), False),
				(self.tiles["horiz"],   self.screen,  (93, 30), False),
				(self.tiles["horiznc"], self.screen,  (94, 30), False),
				(self.tiles["horiz"],   self.screen,  (95, 30), False),
				(self.tiles["horiznc"], self.screen,  (96, 30), False),
				(self.tiles["horiz"],   self.screen,  (97, 30), False),
				(self.tiles["horiznc"], self.screen,  (98, 30), False),
				(self.tiles["horiz"],   self.screen,  (99, 30), False),
				(self.tiles["horiznc"], self.screen,  (100, 30), False),
				(self.tiles["horiz"],   self.screen,  (101, 30), False),
			], True)
		self.blocks["C10"].AddTrainLoc(self.screen, (87, 30))

		self.blocks["C30"] = Block(self, self.frame, "C30",
			[
				(self.tiles["horiznc"], self.screen,  (84, 32), False),
				(self.tiles["horiz"],   self.screen,  (85, 32), False),
				(self.tiles["horiznc"], self.screen,  (86, 32), False),
				(self.tiles["horiz"],   self.screen,  (87, 32), False),
				(self.tiles["horiznc"], self.screen,  (88, 32), False),
				(self.tiles["horiz"],   self.screen,  (89, 32), False),
				(self.tiles["horiznc"], self.screen,  (90, 32), False),
				(self.tiles["horiz"],   self.screen,  (91, 32), False),
				(self.tiles["horiznc"], self.screen,  (92, 32), False),
				(self.tiles["horiz"],   self.screen,  (93, 32), False),
				(self.tiles["horiznc"], self.screen,  (94, 32), False),
				(self.tiles["horiz"],   self.screen,  (95, 32), False),
				(self.tiles["horiznc"], self.screen,  (96, 32), False),
				(self.tiles["horiz"],   self.screen,  (97, 32), False),
				(self.tiles["horiznc"], self.screen,  (98, 32), False),
				(self.tiles["horiznc"], self.screen,  (100, 32), False),
				(self.tiles["horiz"],   self.screen,  (101, 32), False),
			], True)
		self.blocks["C30"].AddTrainLoc(self.screen, (87, 32))

		self.blocks["C31"] = Block(self, self.frame, "C31",
			[
				(self.tiles["horiznc"], self.screen,  (84, 34), False),
				(self.tiles["horiznc"], self.screen,  (85, 34), False),
				(self.tiles["horiznc"], self.screen,  (86, 34), False),
				(self.tiles["horiznc"], self.screen,  (87, 34), False),
				(self.tiles["eobright"], self.screen,  (88, 34), False),
			], True)
		self.blocks["C31"].AddTrainLoc(self.screen, (85, 34))

		self.blocks["COSGMW"] = OverSwitch(self, self.frame, "COSGMW",
			[
				(self.tiles["eobleft"], self.screen,  (76, 30), False),

				(self.tiles["diagleft"], self.screen, (78, 29), False),
				(self.tiles["turnleftleft"], self.screen, (79, 28), False),
				(self.tiles["horiznc"],  self.screen, (80, 28), False),
				(self.tiles["horiz"],    self.screen, (81, 28), False),
				(self.tiles["horiznc"],  self.screen, (82, 28), False),

				(self.tiles["horiz"],    self.screen, (79, 30), False),
				(self.tiles["horiznc"],  self.screen, (80, 30), False),
				(self.tiles["horiz"],    self.screen, (81, 30), False),
				(self.tiles["horiznc"],  self.screen, (82, 30), False),

				(self.tiles["diagright"], self.screen, (79, 31), False),

				(self.tiles["horiz"],    self.screen, (81, 32), False),
				(self.tiles["horiznc"],  self.screen, (82, 32), False),

				(self.tiles["diagright"], self.screen, (81, 33), False),
				(self.tiles["turnrightleft"], self.screen, (82, 34), False),
			], True)
		self.blocks["COSGMW"].AddTrainLoc(self.screen, (77, 36))

		self.osBlocks["COSGMW"] = ["C11", "G21", "C10", "C30", "C31"]

		self.blocks["G12"] = Block(self, self.frame, "G12",
			[
				(self.tiles["houtline"], self.screen,  (99, 26), False),
				(self.tiles["houtline"], self.screen,  (100, 26), False),
				(self.tiles["houtline"], self.screen,  (101, 26), False),
			], True)

		self.blocks["G10"] = Block(self, self.frame, "G10",
			[
				(self.tiles["houtline"], self.screen, (99, 28), False),
				(self.tiles["houtline"], self.screen, (100, 28), False),
				(self.tiles["houtline"], self.screen, (101, 28), False),
			], True)

		self.blocks["C20"] = Block(self, self.frame, "C20",
			[
				(self.tiles["eobleft"],  self.screen, (109, 30), False),
				(self.tiles["horiznc"],  self.screen, (110, 30), False),
				(self.tiles["horiz"],    self.screen, (111, 30), False),
				(self.tiles["horiznc"],  self.screen, (112, 30), False),
				(self.tiles["horiz"],    self.screen, (113, 30), False),
				(self.tiles["turnleftright"], self.screen, (114, 30), False),
				(self.tiles["turnrightdown"], self.screen, (115, 29), False),
				(self.tiles["verticalnc"], self.screen, (115, 28), False),
				(self.tiles["vertical"],   self.screen, (115, 27), False),
				(self.tiles["verticalnc"], self.screen, (115, 26), False),
				(self.tiles["vertical"],   self.screen, (115, 25), False),
				(self.tiles["verticalnc"], self.screen, (115, 24), False),
				(self.tiles["vertical"],   self.screen, (115, 23), False),
				(self.tiles["verticalnc"], self.screen, (115, 22), False),
				(self.tiles["vertical"],   self.screen, (115, 21), False),
				(self.tiles["verticalnc"], self.screen, (115, 20), False),
				(self.tiles["vertical"],   self.screen, (115, 19), False),
				(self.tiles["verticalnc"], self.screen, (115, 18), False),
				(self.tiles["vertical"],   self.screen, (115, 17), False),
				(self.tiles["verticalnc"], self.screen, (115, 16), False),
				(self.tiles["vertical"],   self.screen, (115, 15), False),
				(self.tiles["verticalnc"], self.screen, (115, 14), False),
				(self.tiles["vertical"],   self.screen, (115, 13), False),
				(self.tiles["verticalnc"], self.screen, (115, 12), False),
				(self.tiles["vertical"],   self.screen, (115, 11), False),
				(self.tiles["verticalnc"], self.screen, (115, 10), False),
				(self.tiles["vertical"],   self.screen, (115, 9), False),
				(self.tiles["verticalnc"], self.screen, (115, 8), False),
				(self.tiles["vertical"],   self.screen, (115, 7), False),
				(self.tiles["verticalnc"], self.screen, (115, 6), False),
				(self.tiles["vertical"],   self.screen, (115, 5), False),
				(self.tiles["turnleftup"], self.screen, (115, 4), False),
				(self.tiles["turnrightright"], self.screen, (114, 3), False),
				(self.tiles["horiz"],      self.screen, (113, 3), True),
				(self.tiles["eobleft"],    self.screen, (112, 3), False),
			], True)
		self.blocks["C20"].AddTrainLoc(self.screen, (119, 30))

		self.blocks["COSGME"] = OverSwitch(self, self.frame, "COSGME",
			[
				(self.tiles["turnrightright"], self.screen,  (103, 26), False),
				(self.tiles["diagright"],      self.screen, (104, 27), False),
				(self.tiles["diagright"],      self.screen, (106, 29), False),
				(self.tiles["eobright"],       self.screen, (108, 30), False),
				(self.tiles["horiznc"],        self.screen, (103, 28), False),
				(self.tiles["horiz"],          self.screen, (104, 28), False),
				(self.tiles["horiznc"],        self.screen, (103, 30), False),
				(self.tiles["horiz"],          self.screen, (104, 30), False),
				(self.tiles["horiznc"],        self.screen, (105, 30), False),
				(self.tiles["horiznc"],        self.screen, (103, 32), False),
				(self.tiles["turnleftright"],  self.screen, (104, 32), False),
				(self.tiles["diagleft"],       self.screen, (105, 31), False),
			], True)
		self.blocks["COSGME"].AddTrainLoc(self.screen, (102, 36))

		self.osBlocks["COSGME"] = ["C10", "C30", "G12", "G10", "C20"]

	# 	# Sheffield yard and west OS
		self.blocks["C44"] = Block(self, self.frame, "C44",
			[
				(self.tiles["horiznc"],        self.screen, (76, 3), False),
				(self.tiles["horiz"],          self.screen, (77, 3), False),
				(self.tiles["horiznc"],        self.screen, (78, 3), False),
				(self.tiles["horiz"],          self.screen, (79, 3), False),
				(self.tiles["horiznc"],        self.screen, (80, 3), False),
				(self.tiles["horiz"],          self.screen, (81, 3), False),
				(self.tiles["horiznc"],        self.screen, (82, 3), False),
				(self.tiles["horiz"],          self.screen, (83, 3), False),
				(self.tiles["horiznc"],        self.screen, (84, 3), False),
				(self.tiles["horiz"],          self.screen, (85, 3), False),
				(self.tiles["horiznc"],        self.screen, (86, 3), False),
				(self.tiles["horiz"],          self.screen, (87, 3), False),
				(self.tiles["horiznc"],        self.screen, (88, 3), False),
				(self.tiles["horiz"],          self.screen, (89, 3), False),
				(self.tiles["horiznc"],        self.screen, (90, 3), False),
				(self.tiles["horiz"],          self.screen, (91, 3), False),
				(self.tiles["horiznc"],        self.screen, (92, 3), False),
				(self.tiles["horiz"],          self.screen, (93, 3), False),
				(self.tiles["horiznc"],        self.screen, (94, 3), False),
				(self.tiles["horiz"],          self.screen, (95, 3), False),
				(self.tiles["horiznc"],        self.screen, (96, 3), False),
				(self.tiles["horiz"],          self.screen, (97, 3), False),
				(self.tiles["horiznc"],        self.screen, (98, 3), False),
				(self.tiles["horiz"],          self.screen, (99, 3), False),
			], False)
		self.blocks["C44"].AddTrainLoc(self.screen, (79, 3))

		self.blocks["C43"] = Block(self, self.frame, "C43",
			[
				(self.tiles["horiznc"],        self.screen, (76, 5), False),
				(self.tiles["horiz"],          self.screen, (77, 5), False),
				(self.tiles["horiznc"],        self.screen, (78, 5), False),
				(self.tiles["horiz"],          self.screen, (79, 5), False),
				(self.tiles["horiznc"],        self.screen, (80, 5), False),
				(self.tiles["horiz"],          self.screen, (81, 5), False),
				(self.tiles["horiznc"],        self.screen, (82, 5), False),
				(self.tiles["horiz"],          self.screen, (83, 5), False),
				(self.tiles["horiznc"],        self.screen, (84, 5), False),
				(self.tiles["horiz"],          self.screen, (85, 5), False),
				(self.tiles["horiznc"],        self.screen, (86, 5), False),
				(self.tiles["horiz"],          self.screen, (87, 5), False),
				(self.tiles["horiznc"],        self.screen, (88, 5), False),
				(self.tiles["horiz"],          self.screen, (89, 5), False),
				(self.tiles["horiznc"],        self.screen, (90, 5), False),
				(self.tiles["horiz"],          self.screen, (91, 5), False),
				(self.tiles["horiznc"],        self.screen, (92, 5), False),
				(self.tiles["horiz"],          self.screen, (93, 5), False),
				(self.tiles["horiznc"],        self.screen, (94, 5), False),
				(self.tiles["horiz"],          self.screen, (95, 5), False),
				(self.tiles["horiznc"],        self.screen, (96, 5), False),
				(self.tiles["horiz"],          self.screen, (97, 5), False),
				(self.tiles["horiznc"],        self.screen, (98, 5), False),
				(self.tiles["horiz"],          self.screen, (99, 5), False),
			], False)
		self.blocks["C43"].AddTrainLoc(self.screen, (79, 5))

		self.blocks["C42"] = Block(self, self.frame, "C42",
			[
				(self.tiles["horiznc"],        self.screen, (76, 7), False),
				(self.tiles["horiz"],          self.screen, (77, 7), False),
				(self.tiles["horiznc"],        self.screen, (78, 7), False),
				(self.tiles["horiz"],          self.screen, (79, 7), False),
				(self.tiles["horiznc"],        self.screen, (80, 7), False),
				(self.tiles["horiz"],          self.screen, (81, 7), False),
				(self.tiles["horiznc"],        self.screen, (82, 7), False),
				(self.tiles["horiz"],          self.screen, (83, 7), False),
				(self.tiles["horiznc"],        self.screen, (84, 7), False),
				(self.tiles["horiz"],          self.screen, (85, 7), False),
				(self.tiles["horiznc"],        self.screen, (86, 7), False),
				(self.tiles["horiz"],          self.screen, (87, 7), False),
				(self.tiles["horiznc"],        self.screen, (88, 7), False),
				(self.tiles["horiz"],          self.screen, (89, 7), False),
				(self.tiles["horiznc"],        self.screen, (90, 7), False),
				(self.tiles["horiz"],          self.screen, (91, 7), False),
				(self.tiles["horiznc"],        self.screen, (92, 7), False),
				(self.tiles["horiz"],          self.screen, (93, 7), False),
				(self.tiles["horiznc"],        self.screen, (94, 7), False),
				(self.tiles["horiz"],          self.screen, (95, 7), False),
				(self.tiles["horiznc"],        self.screen, (96, 7), False),
				(self.tiles["horiz"],          self.screen, (97, 7), False),
				(self.tiles["horiznc"],        self.screen, (98, 7), False),
				(self.tiles["horiz"],          self.screen, (99, 7), False),
			], False)
		self.blocks["C42"].AddTrainLoc(self.screen, (79, 7))

		self.blocks["C41"] = Block(self, self.frame, "C41",
			[
				(self.tiles["horiznc"],        self.screen, (76, 9), False),
				(self.tiles["horiz"],          self.screen, (77, 9), False),
				(self.tiles["horiznc"],        self.screen, (78, 9), False),
				(self.tiles["horiz"],          self.screen, (79, 9), False),
				(self.tiles["horiznc"],        self.screen, (80, 9), False),
				(self.tiles["horiz"],          self.screen, (81, 9), False),
				(self.tiles["horiznc"],        self.screen, (82, 9), False),
				(self.tiles["horiz"],          self.screen, (83, 9), False),
				(self.tiles["horiznc"],        self.screen, (84, 9), False),
				(self.tiles["horiz"],          self.screen, (85, 9), False),
				(self.tiles["horiznc"],        self.screen, (86, 9), False),
				(self.tiles["horiz"],          self.screen, (87, 9), False),
				(self.tiles["horiznc"],        self.screen, (88, 9), False),
				(self.tiles["horiz"],          self.screen, (89, 9), False),
				(self.tiles["horiznc"],        self.screen, (90, 9), False),
				(self.tiles["horiz"],          self.screen, (91, 9), False),
				(self.tiles["horiznc"],        self.screen, (92, 9), False),
				(self.tiles["horiz"],          self.screen, (93, 9), False),
				(self.tiles["horiznc"],        self.screen, (94, 9), False),
				(self.tiles["horiz"],          self.screen, (95, 9), False),
				(self.tiles["horiznc"],        self.screen, (96, 9), False),
				(self.tiles["horiz"],          self.screen, (97, 9), False),
				(self.tiles["horiznc"],        self.screen, (98, 9), False),
				(self.tiles["horiz"],          self.screen, (99, 9), False),
			], False)
		self.blocks["C41"].AddTrainLoc(self.screen, (79, 9))

		self.blocks["C40"] = Block(self, self.frame, "C40",
			[
				(self.tiles["horiznc"],        self.screen, (76, 11), False),
				(self.tiles["horiz"],          self.screen, (77, 11), False),
				(self.tiles["horiznc"],        self.screen, (78, 11), False),
				(self.tiles["horiz"],          self.screen, (79, 11), False),
				(self.tiles["horiznc"],        self.screen, (80, 11), False),
				(self.tiles["horiz"],          self.screen, (81, 11), False),
				(self.tiles["horiznc"],        self.screen, (82, 11), False),
				(self.tiles["horiz"],          self.screen, (83, 11), False),
				(self.tiles["horiznc"],        self.screen, (84, 11), False),
				(self.tiles["horiz"],          self.screen, (85, 11), False),
				(self.tiles["horiznc"],        self.screen, (86, 11), False),
				(self.tiles["horiz"],          self.screen, (87, 11), False),
				(self.tiles["horiznc"],        self.screen, (88, 11), False),
				(self.tiles["horiz"],          self.screen, (89, 11), False),
				(self.tiles["horiznc"],        self.screen, (90, 11), False),
				(self.tiles["horiz"],          self.screen, (91, 11), False),
				(self.tiles["horiznc"],        self.screen, (92, 11), False),
				(self.tiles["horiz"],          self.screen, (93, 11), False),
				(self.tiles["horiznc"],        self.screen, (94, 11), False),
			], False)
		self.blocks["C40"].AddTrainLoc(self.screen, (79, 11))

		self.blocks["C21"] = Block(self, self.frame, "C21",
			[
				(self.tiles["horiznc"],        self.screen, (76, 13), False),
				(self.tiles["horiz"],          self.screen, (77, 13), False),
				(self.tiles["horiznc"],        self.screen, (78, 13), False),
				(self.tiles["horiz"],          self.screen, (79, 13), False),
				(self.tiles["horiznc"],        self.screen, (80, 13), False),
				(self.tiles["horiz"],          self.screen, (81, 13), False),
				(self.tiles["horiznc"],        self.screen, (82, 13), False),
				(self.tiles["horiz"],          self.screen, (83, 13), False),
				(self.tiles["horiznc"],        self.screen, (84, 13), False),
				(self.tiles["horiz"],          self.screen, (85, 13), False),
				(self.tiles["horiznc"],        self.screen, (86, 13), False),
				(self.tiles["horiz"],          self.screen, (87, 13), False),
				(self.tiles["horiznc"],        self.screen, (88, 13), False),
				(self.tiles["horiz"],          self.screen, (89, 13), False),
				(self.tiles["horiznc"],        self.screen, (90, 13), False),
				(self.tiles["horiz"],          self.screen, (91, 13), False),
				(self.tiles["horiznc"],        self.screen, (92, 13), False),
				(self.tiles["horiz"],          self.screen, (93, 13), False),
				(self.tiles["horiznc"],        self.screen, (94, 13), False),
			], False)
		self.blocks["C21"].AddTrainLoc(self.screen, (79, 13))

		self.blocks["C50"] = Block(self, self.frame, "C50",
			[
				(self.tiles["horiznc"],        self.screen, (76, 15), False),
				(self.tiles["horiz"],          self.screen, (77, 15), False),
				(self.tiles["horiznc"],        self.screen, (78, 15), False),
				(self.tiles["horiz"],          self.screen, (79, 15), False),
				(self.tiles["horiznc"],        self.screen, (80, 15), False),
				(self.tiles["horiz"],          self.screen, (81, 15), False),
				(self.tiles["horiznc"],        self.screen, (82, 15), False),
				(self.tiles["horiz"],          self.screen, (83, 15), False),
				(self.tiles["horiznc"],        self.screen, (84, 15), False),
				(self.tiles["horiz"],          self.screen, (85, 15), False),
				(self.tiles["horiznc"],        self.screen, (86, 15), False),
				(self.tiles["horiz"],          self.screen, (87, 15), False),
				(self.tiles["horiznc"],        self.screen, (88, 15), False),
				(self.tiles["horiz"],          self.screen, (89, 15), False),
				(self.tiles["horiznc"],        self.screen, (90, 15), False),
				(self.tiles["horiz"],          self.screen, (91, 15), False),
				(self.tiles["horiznc"],        self.screen, (92, 15), False),
				(self.tiles["horiz"],          self.screen, (93, 15), False),
				(self.tiles["horiznc"],        self.screen, (94, 15), False),
			], False)
		self.blocks["C50"].AddTrainLoc(self.screen, (79, 15))

		self.blocks["C51"] = Block(self, self.frame, "C51",
			[
				(self.tiles["horiznc"],        self.screen, (82, 17), False),
				(self.tiles["horiz"],          self.screen, (83, 17), False),
				(self.tiles["horiznc"],        self.screen, (84, 17), False),
				(self.tiles["horiz"],          self.screen, (85, 17), False),
				(self.tiles["horiznc"],        self.screen, (86, 17), False),
				(self.tiles["horiz"],          self.screen, (87, 17), False),
				(self.tiles["horiznc"],        self.screen, (88, 17), False),
			], False)
		self.blocks["C51"].AddTrainLoc(self.screen, (83, 17))

		self.blocks["C52"] = Block(self, self.frame, "C52",
			[
				(self.tiles["horiznc"],        self.screen, (82, 19), False),
				(self.tiles["horiz"],          self.screen, (83, 19), False),
				(self.tiles["horiznc"],        self.screen, (84, 19), False),
				(self.tiles["horiz"],          self.screen, (85, 19), False),
				(self.tiles["horiznc"],        self.screen, (86, 19), False),
				(self.tiles["horiz"],          self.screen, (87, 19), False),
				(self.tiles["horiznc"],        self.screen, (88, 19), False),
			], False)
		self.blocks["C52"].AddTrainLoc(self.screen, (83, 19))

		self.blocks["C53"] = Block(self, self.frame, "C53",
			[
				(self.tiles["horiznc"],        self.screen, (82, 21), False),
				(self.tiles["horiz"],          self.screen, (83, 21), False),
				(self.tiles["horiznc"],        self.screen, (84, 21), False),
				(self.tiles["horiz"],          self.screen, (85, 21), False),
				(self.tiles["horiznc"],        self.screen, (86, 21), False),
				(self.tiles["horiz"],          self.screen, (87, 21), False),
				(self.tiles["horiznc"],        self.screen, (88, 21), False),
			], False)
		self.blocks["C53"].AddTrainLoc(self.screen, (83, 21))

		self.blocks["C54"] = Block(self, self.frame, "C54",
			[
				(self.tiles["horiznc"],        self.screen, (82, 23), False),
				(self.tiles["horiz"],          self.screen, (83, 23), False),
				(self.tiles["horiznc"],        self.screen, (84, 23), False),
				(self.tiles["horiz"],          self.screen, (85, 23), False),
				(self.tiles["horiznc"],        self.screen, (86, 23), False),
				(self.tiles["horiz"],          self.screen, (87, 23), False),
				(self.tiles["horiznc"],        self.screen, (88, 23), False),
			], False)
		self.blocks["C54"].AddTrainLoc(self.screen, (83, 23))

		self.blocks["COSSHE"] = OverSwitch(self, self.frame, "COSSHE",
			[
				(self.tiles["horiznc"],        self.screen, (101, 3), False),
				(self.tiles["horiz"],          self.screen, (102, 3), False),
				(self.tiles["horiznc"],        self.screen, (103, 3), False),
				(self.tiles["horiz"],          self.screen, (104, 3), False),
				(self.tiles["horiznc"],        self.screen, (105, 3), False),
				(self.tiles["horiz"],          self.screen, (106, 3), False),
				(self.tiles["horiz"],          self.screen, (108, 3), False),
				(self.tiles["horiznc"],        self.screen, (109, 3), False),
				(self.tiles["eobright"],       self.screen, (111, 3), False),

				(self.tiles["horiznc"],        self.screen, (101, 5), False),
				(self.tiles["horiz"],          self.screen, (102, 5), False),
				(self.tiles["horiznc"],        self.screen, (103, 5), False),
				(self.tiles["horiz"],          self.screen, (104, 5), False),
				(self.tiles["turnleftright"],  self.screen, (105, 5), False),
				(self.tiles["diagleft"],       self.screen, (106, 4), False),

				(self.tiles["horiznc"],        self.screen, (101, 7), False),
				(self.tiles["horiz"],          self.screen, (102, 7), False),
				(self.tiles["horiz"],          self.screen, (104, 7), False),
				(self.tiles["horiznc"],        self.screen, (105, 7), False),
				(self.tiles["diagleft"],       self.screen, (107, 6), False),
				(self.tiles["diagleft"],       self.screen, (108, 5), False),
				(self.tiles["diagleft"],       self.screen, (109, 4), False),

				(self.tiles["turnleftright"],  self.screen, (101, 9), False),
				(self.tiles["diagleft"],       self.screen, (102, 8), False),

				(self.tiles["horiz"],          self.screen, (96, 11), False),
				(self.tiles["horiznc"],        self.screen, (97, 11), False),
				(self.tiles["horiz"],          self.screen, (98, 11), False),
				(self.tiles["horiznc"],        self.screen, (99, 11), False),
				(self.tiles["horiz"],          self.screen, (100, 11), False),
				(self.tiles["horiznc"],        self.screen, (101, 11), False),
				(self.tiles["diagleft"],       self.screen, (103, 10), False),
				(self.tiles["diagleft"],       self.screen, (104, 9), False),
				(self.tiles["diagleft"],       self.screen, (105, 8), False),

				(self.tiles["horiz"],          self.screen, (96, 13), False),
				(self.tiles["horiznc"],        self.screen, (97, 13), False),
				(self.tiles["horiz"],          self.screen, (98, 13), False),
				(self.tiles["horiznc"],        self.screen, (99, 13), False),
				(self.tiles["diagleft"],       self.screen, (101, 12), False),

				(self.tiles["horiz"],          self.screen, (96, 15), False),
				(self.tiles["horiznc"],        self.screen, (97, 15), False),
				(self.tiles["diagleft"],       self.screen, (99, 14), False),

				(self.tiles["horiz"],          self.screen, (90, 17), False),
				(self.tiles["horiznc"],        self.screen, (91, 17), False),
				(self.tiles["horiz"],          self.screen, (92, 17), False),
				(self.tiles["horiz"],          self.screen, (94, 17), False),
				(self.tiles["horiznc"],        self.screen, (95, 17), False),
				(self.tiles["diagleft"],       self.screen, (97, 16), False),

				(self.tiles["horiz"],          self.screen, (90, 19), False),
				(self.tiles["turnleftright"],  self.screen, (91, 19), False),
				(self.tiles["diagleft"],       self.screen, (92, 18), False),

				(self.tiles["horiz"],          self.screen, (90, 21), False),
				(self.tiles["horiznc"],        self.screen, (91, 21), False),
				(self.tiles["diagleft"],       self.screen, (93, 20), False),
				(self.tiles["diagleft"],       self.screen, (94, 19), False),
				(self.tiles["diagleft"],       self.screen, (95, 18), False),

				(self.tiles["turnleftright"],  self.screen, (90, 23), False),
				(self.tiles["diagleft"],       self.screen, (91, 22), False),
			], False)
		self.blocks["COSSHE"].AddTrainLoc(self.screen, (103, 15))

		self.osBlocks["COSSHE"] = ["C44", "C43", "C42", "C41", "C40", "C21", "C50", "C51", "C52", "C53", "C54", "C20"]

		self.blocks["COSSHW"] = OverSwitch(self, self.frame, "COSSHW",
			[
				(self.tiles["eobleft"],        self.screen, (63, 13), False),
				(self.tiles["diagleft"],       self.screen, (65, 12), False),
				(self.tiles["diagleft"],       self.screen, (66, 11), False),
				(self.tiles["diagleft"],       self.screen, (67, 10), False),
				(self.tiles["diagleft"],       self.screen, (69, 8), False),
				(self.tiles["diagleft"],       self.screen, (70, 7), False),
				(self.tiles["diagleft"],       self.screen, (71, 6), False),
				(self.tiles["diagleft"],       self.screen, (73, 4), False),
				(self.tiles["turnleftleft"],   self.screen, (74, 3), False),

				(self.tiles["horiznc"],        self.screen, (73, 5), False),
				(self.tiles["horiz"],          self.screen, (74, 5), False),

				(self.tiles["horiznc"],        self.screen, (69, 9), False),
				(self.tiles["horiz"],          self.screen, (70, 9), False),
				(self.tiles["diagleft"],       self.screen, (72, 8), False),
				(self.tiles["turnleftleft"],   self.screen, (73, 7), False),
				(self.tiles["horiz"],          self.screen, (74, 7), False),

				(self.tiles["horiz"],          self.screen, (72, 9), False),
				(self.tiles["horiznc"],        self.screen, (73, 9), False),
				(self.tiles["horiz"],          self.screen, (74, 9), False),

				(self.tiles["horiznc"],        self.screen, (65, 13), False),
				(self.tiles["horiz"],          self.screen, (66, 13), False),

				(self.tiles["diagleft"],       self.screen, (68, 12), False),
				(self.tiles["turnleftleft"],   self.screen, (69, 11), False),
				(self.tiles["horiz"],          self.screen, (70, 11), False),
				(self.tiles["horiznc"],        self.screen, (71, 11), False),
				(self.tiles["horiz"],          self.screen, (72, 11), False),
				(self.tiles["horiznc"],        self.screen, (73, 11), False),
				(self.tiles["horiz"],          self.screen, (74, 11), False),

				(self.tiles["horiz"],          self.screen, (68, 13), False),
				(self.tiles["horiznc"],        self.screen, (69, 13), False),
				(self.tiles["horiznc"],        self.screen, (71, 13), False),
				(self.tiles["horiz"],          self.screen, (72, 13), False),
				(self.tiles["horiznc"],        self.screen, (73, 13), False),
				(self.tiles["horiz"],          self.screen, (74, 13), False),

				(self.tiles["diagright"],      self.screen, (71, 14), False),
				(self.tiles["horiznc"],        self.screen, (73, 15), False),
				(self.tiles["horiz"],          self.screen, (74, 15), False),
				(self.tiles["diagright"],      self.screen, (73, 16), False),

				(self.tiles["horiznc"],        self.screen, (75, 17), False),
				(self.tiles["horiz"],          self.screen, (76, 17), False),
				(self.tiles["horiz"],          self.screen, (78, 17), False),
				(self.tiles["horiznc"],        self.screen, (79, 17), False),
				(self.tiles["horiz"],          self.screen, (80, 17), False),

				(self.tiles["diagright"],      self.screen, (78, 18), False),
				(self.tiles["turnrightleft"],  self.screen, (79, 19), False),
				(self.tiles["horiz"],          self.screen, (80, 19), False),

				(self.tiles["diagright"],      self.screen, (75, 18), False),
				(self.tiles["diagright"],      self.screen, (76, 19), False),
				(self.tiles["diagright"],      self.screen, (77, 20), False),

				(self.tiles["horiznc"],        self.screen, (79, 21), False),
				(self.tiles["horiz"],          self.screen, (80, 21), False),

				(self.tiles["diagright"],      self.screen, (79, 22), False),
				(self.tiles["turnrightleft"],  self.screen, (80, 23), False),
			], False)
		self.blocks["COSSHW"].AddTrainLoc(self.screen, (63, 4))

		self.osBlocks["COSSHW"] = ["C22", "C44", "C43", "C42", "C41", "C40", "C21", "C50", "C51", "C52", "C53", "C54"]

		return self.blocks, self.osBlocks

	def DefineTurnouts(self, blocks):
		self.turnouts = {}

		hsList = [
			["CSw3",   "toleftleft",   "C30", (99, 32)],
		]
		toList = [
			["CSw31",  "torightleft",  ["COSGME"], (107, 30)],
			["CSw33",  "toleftleft",   ["COSGME"], (106, 30)],
			["CSw35",  "toleftup",     ["COSGME"], (105, 28)],
			["CSw37",  "toleftdown",   ["COSGMW"], (80, 32)],
			["CSw39",  "torightright", ["COSGMW"], (78, 30)],
			["CSw41",  "toleftright",  ["COSGMW"], (77, 30)],
			["CSw43",  "toleftleft",   ["COSSHE"], (110, 3)],
			["CSw45",  "torightdowninv",  ["COSSHE"], (106, 7)],
			["CSw47",  "torightdowninv",  ["COSSHE"], (102, 11)],
			["CSw49",  "toleftleft",   ["COSSHE"], (107, 3)],
			["CSw51",  "toleftleft",   ["COSSHE"], (103, 7)],
			["CSw53",  "toleftright",  ["COSSHW"], (71, 9)],
			["CSw55",  "toleftright",  ["COSSHW"], (67, 13)],
			["CSw57",  "torightup",    ["COSSHW"], (72, 5)],
			["CSw59",  "torightup",    ["COSSHW"], (68, 9)],
			["CSw61",  "toleftright",  ["COSSHW"], (64, 13)],
			["CSw63",  "torightdown",  ["COSSHE"], (100, 13)],
			["CSw65",  "torightdown",  ["COSSHE"], (98, 15)],
			["CSw67",  "torightdown",  ["COSSHE"], (96, 17)],
			["CSw69",  "toleftleft",   ["COSSHE"], (93, 17)],
			["CSw71",  "torightdown",  ["COSSHE"], (92, 21)],
			["CSw73",  "torightright", ["COSSHW"], (70, 13)],
			["CSw75",  "toleftdown",   ["COSSHW"], (72, 15)],
			["CSw77",  "toleftdown",   ["COSSHW"], (74, 17)],
			["CSw79",  "torightright", ["COSSHW"], (77, 17)],
			["CSw81",  "toleftdown",   ["COSSHW"], (78, 21)],
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
			["CG21W", (83, 28)],
			["CC10W", (83, 30)],
			["CC30W", (83, 32)],
			["CC31W", (83, 34)],
			["CG12E", (102, 26)],
			["CG10E", (102, 28)],
			["CC10E", (102, 30)],
			["CC30E", (102, 32)],

			["CC44E", (100, 3)],
			["CC43E", (100, 5)],
			["CC42E", (100, 7)],
			["CC41E", (100, 9)],
			["CC40E", (95, 11)],
			["CC21E", (95, 13)],
			["CC50E", (95, 15)],
			["CC51E", (89, 17)],
			["CC52E", (89, 19)],
			["CC53E", (89, 21)],
			["CC54E", (89, 23)],

			["CC44W", (75, 3)],
			["CC43W", (75, 5)],
			["CC42W", (75, 7)],
			["CC41W", (75, 9)],
			["CC40W", (75, 11)],
			["CC21W", (75, 13)],
			["CC50W", (75, 15)],
			["CC51W", (81, 17)],
			["CC52W", (81, 19)],
			["CC53W", (81, 21)],
			["CC54W", (81, 23)],
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
			["C2LD", RegAspects,    True,  "right",     (102, 27)],
			["C2LC", RegAspects,    True,  "right",     (102, 29)],
			["C2LB", RegAspects,    True,  "rightlong", (102, 31)],
			["C2LA", SloAspects,    True,  "right",     (102, 33)],

			["C2R",  RegSloAspects, False, "leftlong",  (108, 29)],

			["C4L",  RegSloAspects, True,  "rightlong", (76, 31)],

			["C4RD", RegAspects,    False, "left",      (83, 27)],
			["C4RC", RegAspects,    False, "leftlong",  (83, 29)],
			["C4RB", SloAspects,    False, "left",      (83, 31)],
			["C4RA", SloAspects,    False, "left",      (83, 33)],

			["C6LF", RegAspects,    True,  "right",     (100, 4)],
			["C6LE", RegAspects,    True,  "right",     (100, 6)],
			["C6LD", RegAspects,    True,  "right",     (100, 8)],
			["C6LC", RegAspects,    True,  "right",     (100, 100)],
			["C6LB", RegAspects,    True,  "right",     (95, 12)],
			["C6LA", RegAspects,    True,  "right",     (95, 14)],
			["C6LG", RegAspects,    True,  "right",     (95, 16)],
			["C6LH", RegAspects,    True,  "right",     (89, 18)],
			["C6LJ", RegAspects,    True,  "right",     (89, 20)],
			["C6LK", RegAspects,    True,  "right",     (89, 22)],
			["C6LL", RegAspects,    True,  "right",     (89, 24)],

			["C6R",  RegAspects,    False, "leftlong",  (111, 2)],

			["C8L",  RegAspects,    True,  "rightlong", (63, 14)],

			["C8RF", RegAspects,    False, "left",      (75, 2)],
			["C8RE", RegAspects,    False, "left",      (75, 4)],
			["C8RD", RegAspects,    False, "left",      (75, 6)],
			["C8RC", RegAspects,    False, "left",      (75, 8)],
			["C8RB", RegAspects,    False, "left",      (75, 10)],
			["C8RA", RegAspects,    False, "left",      (75, 12)],
			["C8RG", RegAspects,    False, "left",      (75, 14)],
			["C8RH", RegAspects,    False, "left",      (81, 16)],
			["C8RJ", RegAspects,    False, "left",      (81, 18)],
			["C8RK", RegAspects,    False, "left",      (81, 20)],
			["C8RL", RegAspects,    False, "left",      (81, 22)],
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
		self.routes["CRtC11G21"] = Route(self.screen, block, "CRtC11G21", "C11", [(76, 30), (77, 30), (78, 29), (79, 28), (80, 28), (81, 28), (82, 28)], "G21", [RESTRICTING, RESTRICTING], ["CSw41:R"], ["C4L", "C4RD"])
		self.routes["CRtC11C10"] = Route(self.screen, block, "CRtC11C10", "C11", [(76, 30), (77, 30), (78, 30), (79, 30), (80, 30), (81, 30), (82, 30)], "C10", [MAIN, MAIN], ["CSw39:N", "CSw41:N"], ["C4L", "C4RC"])
		self.routes["CRtC11C30"] = Route(self.screen, block, "CRtC11C30", "C11", [(76, 30), (77, 30), (78, 30), (79, 31), (80, 32), (81, 32), (82, 32)], "C30", [SLOW, SLOW], ["CSw37:R", "CSw39:R", "CSw41:N"], ["C4L", "C4RB"])
		self.routes["CRtC11C31"] = Route(self.screen, block, "CRtC11C31", "C11", [(76, 30), (77, 30), (78, 30), (79, 31), (80, 32), (81, 33), (82, 34)], "C31", [RESTRICTING, SLOW], ["CSw37:N", "CSw39:R", "CSw41:N"], ["C4L", "C4RA"])

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
		self.routes["CRtG12C20"] = Route(self.screen, block, "CRtG12C20", "G12", [(103, 26), (104, 27), (105, 28), (106, 29), (107, 30), (108, 30)], "C20", [RESTRICTING, RESTRICTING], ["CSw31:R", "CSw35:N"], ["C2LD", "C2R"])
		self.routes["CRtG10C20"] = Route(self.screen, block, "CRtG10C20", "G10", [(103, 28), (104, 28), (105, 28), (106, 29), (107, 30), (108, 30)], "C20", [RESTRICTING, RESTRICTING], ["CSw31:R", "CSw35:R"], ["C2LC", "C2R"])
		self.routes["CRtC10C20"] = Route(self.screen, block, "CRtC10C20", "C10", [(103, 30), (104, 30), (105, 30), (106, 30), (107, 30), (108, 30)], "C20", [MAIN, MAIN], ["CSw31:N", "CSw33:N"], ["C2LB", "C2R"])
		self.routes["CRtC30C20"] = Route(self.screen, block, "CRtC30C20", "C30", [(103, 32), (104, 32), (105, 31), (106, 30), (107, 30), (108, 30)], "C20", [SLOW, SLOW], ["CSw31:N", "CSw33:R"], ["C2LA", "C2R"])

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
		self.routes["CRtC20C44"] = Route(self.screen, block, "CRtC20C44", "C20", [(101, 3), (102, 3), (103, 3), (104, 3), (105, 3), (106, 3), (107, 3), (108, 3), (109, 3), (110, 3), (111, 3)], "C44", [SLOW, SLOW], ["CSw43:N", "CSw49:N"], ["C6R", "C6LF"])
		self.routes["CRtC20C43"] = Route(self.screen, block, "CRtC20C43", "C20", [(101, 5), (102, 5), (103, 5), (104, 5), (105, 5), (106, 4), (107, 3), (108, 3), (109, 3), (110, 3), (111, 3)], "C43", [SLOW, SLOW], ["CSw43:N", "CSw49:R"], ["C6R", "C6LE"])
		self.routes["CRtC20C42"] = Route(self.screen, block, "CRtC20C42", "C20", [(101, 7), (102, 7), (103, 7), (104, 7), (105, 7), (106, 7), (107, 6), (108, 5), (109, 4), (110, 3), (111, 3)], "C42", [SLOW, SLOW], ["CSw43:R", "CSw45:N", "CSw51:N", "CSw47:N"], ["C6R", "C6LD"])
		self.routes["CRtC20C41"] = Route(self.screen, block, "CRtC20C41", "C20", [(101, 9), (102, 8), (103, 7), (104, 7), (105, 7), (106, 7), (107, 6), (108, 5), (109, 4), (110, 3), (111, 3)], "C41", [SLOW, SLOW], ["CSw43:R", "CSw45:N", "CSw51:R", "CSw47:R"], ["C6R", "C6LC"])
		self.routes["CRtC20C40"] = Route(self.screen, block, "CRtC20C40", "C20", [(96, 11), (97, 11), (98, 11), (99, 11), (100, 11), (101, 11), (102, 11), (103, 10), (104, 9), (105, 8), (106, 7), (107, 6), (108, 5), (109, 4), (110, 3), (111, 3)], "C40", [SLOW, SLOW], ["CSw43:R", "CSw45:R", "CSw47:N", "CSw51:N"], ["C6R", "C6LB"])
		self.routes["CRtC20C21"] = Route(self.screen, block, "CRtC20C21", "C20", [(96, 13), (97, 13), (98, 13), (99, 13), (100, 13), (101, 12), (102, 11), (103, 10), (104, 9), (105, 8), (106, 7), (107, 6), (108, 5), (109, 4), (110, 3), (111, 3)], "C21", [MAIN, MAIN], ["CSw43:R", "CSw45:R", "CSw47:R", "CSw51:R", "CSw63:R"], ["C6R", "C6LA"])
		self.routes["CRtC20C50"] = Route(self.screen, block, "CRtC20C50", "C20", [(96, 15), (97, 15), (98, 15), (99, 14), (100, 13), (101, 12), (102, 11), (103, 10), (104, 9), (105, 8), (106, 7), (107, 6), (108, 5), (109, 4), (110, 3), (111, 3)], "C50", [SLOW, SLOW], ["CSw43:R", "CSw45:R", "CSw47:R", "CSw51:R", "CSw63:N", "CSw65:R"], ["C6R", "C6LG"])

		self.routes["CRtC20C51"] = Route(self.screen, block, "CRtC20C51", "C20",
				[(90, 17), (91, 17), (92, 17), (93, 17), (94, 17), (95, 17), (96, 17), (97, 16), (98, 15), (99, 14), (100, 13), (101, 12), (102, 11), (103, 10), (104, 9), (105, 8), (106, 7), (107, 6), (108, 5), (109, 4), (110, 3), (111, 3)], "C51", [SLOW, SLOW], ["CSw43:R", "CSw45:R", "CSw47:R", "CSw51:R", "CSw63:N", "CSw65:N", "CSw67:R", "CSw69:N"], ["C6R", "C6LH"])
		self.routes["CRtC20C52"] = Route(self.screen, block, "CRtC20C52", "C20",
				[(90, 19), (91, 19), (92, 18), (93, 17), (94, 17), (95, 17), (96, 17), (97, 16), (98, 15), (99, 14), (100, 13), (101, 12), (102, 11), (103, 10), (104, 9), (105, 8), (106, 7), (107, 6), (108, 5), (109, 4), (110, 3), (111, 3)], "C52", [SLOW, SLOW], ["CSw43:R", "CSw45:R", "CSw47:R", "CSw51:R", "CSw63:N", "CSw65:N", "CSw67:R", "CSw69:R"], ["C6R", "C6LJ"])
		self.routes["CRtC20C53"] = Route(self.screen, block, "CRtC20C53", "C20",
				[(90, 21), (91, 21), (92, 21), (93, 20), (94, 19), (95, 18), (96, 17), (97, 16), (98, 15), (99, 14), (100, 13), (101, 12), (102, 11), (103, 10), (104, 9), (105, 8), (106, 7), (107, 6), (108, 5), (109, 4), (110, 3), (111, 3)], "C53", [SLOW, SLOW], ["CSw43:R", "CSw45:R", "CSw47:R", "CSw51:R", "CSw63:N", "CSw65:N", "CSw67:N", "CSw71:R"], ["C6R", "C6LK"])
		self.routes["CRtC20C54"] = Route(self.screen, block, "CRtC20C54", "C20",
				[(90, 23), (91, 22), (92, 21), (93, 20), (94, 19), (95, 18), (96, 17), (97, 16), (98, 15), (99, 14), (100, 13), (101, 12), (102, 11), (103, 10), (104, 9), (105, 8), (106, 7), (107, 6), (108, 5), (109, 4), (110, 3), (111, 3)], "C54", [SLOW, SLOW], ["CSw43:R", "CSw45:R", "CSw47:R", "CSw51:R", "CSw63:N", "CSw65:N", "CSw67:N", "CSw71:N"], ["C6R", "C6LL"])

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
		self.routes["CRtC44C22"] = Route(self.screen, block, "CRtC44C22", "C44", [(63, 13), (64, 13), (65, 12), (66, 11), (67, 10), (68, 9), (69, 8), (70, 7), (71, 6), (72, 5), (73, 4), (74, 3)], "C22", [SLOW, SLOW], ["CSw57:N", "CSw59:N", "CSw61:R"], ["C8RF", "C8L"])
		self.routes["CRtC43C22"] = Route(self.screen, block, "CRtC43C22", "C43", [(63, 13), (64, 13), (65, 12), (66, 11), (67, 10), (68, 9), (69, 8), (70, 7), (71, 6), (72, 5), (73, 5), (74, 5)], "C22", [SLOW, SLOW], ["CSw57:R", "CSw59:N", "CSw61:R"], ["C8RE", "C8L"])
		self.routes["CRtC42C22"] = Route(self.screen, block, "CRtC42C22", "C42", [(63, 13), (64, 13), (65, 12), (66, 11), (67, 10), (68, 9), (69, 9), (70, 9), (71, 9), (72, 8), (73, 7), (74, 7)], "C22", [SLOW, SLOW], ["CSw53:R", "CSw59:R", "CSw61:R"], ["C8RD", "C8L"])
		self.routes["CRtC41C22"] = Route(self.screen, block, "CRtC41C22", "C41", [(63, 13), (64, 13), (65, 12), (66, 11), (67, 10), (68, 9), (69, 9), (70, 9), (71, 9), (72, 9), (73, 9), (74, 9)], "C22", [SLOW, SLOW], ["CSw53:N", "CSw59:R", "CSw61:R"], ["C8RC", "C8L"])
		self.routes["CRtC40C22"] = Route(self.screen, block, "CRtC40C22", "C40", [(63, 13), (64, 13), (65, 13), (66, 13), (67, 13), (68, 12), (69, 11), (70, 11), (71, 11), (72, 11), (73, 11), (74, 11)], "C22", [SLOW, SLOW], ["CSw55:R", "CSw61:N"], ["C8RB", "C8L"])
		self.routes["CRtC21C22"] = Route(self.screen, block, "CRtC21C22", "C21", [(63, 13), (64, 13), (65, 13), (66, 13), (67, 13), (68, 13), (69, 13), (70, 13), (71, 13), (72, 13), (73, 13), (74, 13)], "C22", [MAIN, DIVERGING], ["CSw55:N", "CSw61:N", "CSw73:N"], ["C8RA", "C8L"])
		self.routes["CRtC50C22"] = Route(self.screen, block, "CRtC50C22", "C50", [(63, 13), (64, 13), (65, 13), (66, 13), (67, 13), (68, 13), (69, 13), (70, 13), (71, 14), (72, 15), (73, 15), (74, 15)], "C22", [SLOW, SLOW], ["CSw55:N", "CSw61:N", "CSw73:R", "CSw75:R"], ["C8RG", "C8L"])

		self.routes["CRtC51C22"] = Route(self.screen, block, "CRtC51C22", "C51", [
				(63, 13), (64, 13), (65, 13), (66, 13), (67, 13), (68, 13), (69, 13), (70, 13), (71, 14), (72, 15), (73, 16), (74, 17), (75, 17), (76, 17), (77, 17), (78, 17), (79, 17), (80, 17)], "C22", [SLOW, SLOW], ["CSw55:N", "CSw61:N", "CSw73:R", "CSw75:N", "CSw77:R", "CSw79:N"], ["C8RH", "C8L"])
		self.routes["CRtC52C22"] = Route(self.screen, block, "CRtC52C22", "C52", [
				(63, 13), (64, 13), (65, 13), (66, 13), (67, 13), (68, 13), (69, 13), (70, 13), (71, 14), (72, 15), (73, 16), (74, 17), (75, 17), (76, 17), (77, 17), (78, 18), (79, 19), (80, 19)], "C22", [SLOW, SLOW], ["CSw55:N", "CSw61:N", "CSw73:R", "CSw75:N", "CSw77:R", "CSw79:R"], ["C8RJ", "C8L"])
		self.routes["CRtC53C22"] = Route(self.screen, block, "CRtC53C22", "C53", [
				(63, 13), (64, 13), (65, 13), (66, 13), (67, 13), (68, 13), (69, 13), (70, 13), (71, 14), (72, 15), (73, 16), (74, 17), (75, 18), (76, 19), (77, 20), (78, 21), (79, 21), (80, 21)], "C22", [SLOW, SLOW], ["CSw55:N", "CSw61:N", "CSw73:R", "CSw75:N", "CSw77:N", "CSw81:R"], ["C8RK", "C8L"])
		self.routes["CRtC54C22"] = Route(self.screen, block, "CRtC54C22", "C54", [
				(63, 13), (64, 13), (65, 13), (66, 13), (67, 13), (68, 13), (69, 13), (70, 13), (71, 14), (72, 15), (73, 16), (74, 17), (75, 18), (76, 19), (77, 20), (78, 21), (79, 22), (80, 23)], "C22", [SLOW, SLOW], ["CSw55:N", "CSw61:N", "CSw73:R", "CSw75:N", "CSw77:N", "CSw81:N"], ["C8RL", "C8L"])

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

		hs = HandSwitch(self, self.screen, self.frame, self.blocks["C30"], "CSw3.hand", (99, 33), self.misctiles["handup"])
		self.blocks["C30"].AddHandSwitch(hs)
		self.handswitches["CSw3.hand"] = hs

		return self.handswitches
