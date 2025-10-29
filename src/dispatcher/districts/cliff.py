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
		
	def HandSwitchClick(self, hs, nv=None):
		controlOpt = self.frame.cliffControl
		if controlOpt != 2:  # cliff local control or limited to bank/cliveden (handled in those districts)
			if controlOpt == 0:
				msg = "Cliff control is local"
			else:
				msg = "Dispatcher control is Bank/Cliveden only"
			self.frame.PopupEvent(msg)
			return

		District.HandSwitchClick(self, hs, nv)

	def PerformSignalAction(self, sig, callon=False, silent=True):
		controlOpt = self.frame.cliffControl
		if controlOpt != 2:  # cliff local control or limited to bank/cliveden (handled in those districts)
			if controlOpt == 0:
				msg = "Cliff control is local"
			else:
				msg = "Dispatcher control is Bank/Cliveden only"
			self.frame.PopupEvent(msg)
			return False

		return District.PerformSignalAction(self, sig, callon=callon)

	def DoSignalLeverAction(self, signame, state, callon, silent=1, source=None):
		controlOpt = self.frame.cliffControl
		if source == "ctc":
			if controlOpt != 2:  # cliff local control or limited to bank/cliveden (handled in those districts)
				if controlOpt == 0:
					msg = "Cliff control is local"
				else:
					msg = "Dispatcher control is Bank/Cliveden only"
				self.frame.PopupEvent(msg)
				return False

		return District.DoSignalLeverAction(self, signame, state, callon, silent, source)

	def DoTurnoutLeverAction(self, turnout, state, force=False, source=None):
		controlOpt = self.frame.cliffControl
		if source == "ctc":
			if controlOpt != 2:  # cliff local control or limited to bank/cliveden (handled in those districts)
				if controlOpt == 0:
					msg = "Cliff control is local"
				else:
					msg = "Dispatcher control is Bank/Cliveden only"
				self.frame.PopupEvent(msg)
				return False

		return District.DoTurnoutLeverAction(self, turnout, state, force, source)

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

	def SignalClick(self, sig, callon=False, silent=False):
		controlOpt = self.frame.cliffControl
		if controlOpt != 2:  # either cliff local for everything or cliff for cliff and dispatcher for bank/cliveden
			if controlOpt == 0:
				msg = "Cliff control is local"
			else:
				msg = "Dispatcher control is Bank/Cliveden only"
			self.frame.PopupEvent(msg)
			return

		# otherwise, allow everything
		District.SignalClick(self, sig, callon, silent)

	def ButtonClick(self, btn):
		controlOpt = self.frame.cliffControl
		if controlOpt != 2:  # cliff local control or limited to bank/cliveden (handled in those districts)
			btn.Press(refresh=False)
			btn.Invalidate(refresh=True)
			self.frame.ClearButtonAfter(2, btn)
			if controlOpt == 0:
				msg = "Cliff control is local"
			else:
				msg = "Dispatcher control is Bank/Cliveden only"
			self.frame.PopupEvent(msg)
			return

		bname = btn.GetName()
		for osBlkNm in ["COSGMW", "COSGME", "COSSHE", "COSSHW"]:
			if bname in self.osButtons[osBlkNm]:
				break
		else:
			osBlkNm = None

		if osBlkNm:
			osBlk = self.blocks[osBlkNm]
			if osBlk.IsBusy():
				self.ReportBlockBusy(osBlk.GetRouteDesignator())
				return

			btn.Press(refresh=True)
			self.frame.ClearButtonAfter(2, btn)
			self.frame.Request({"nxbutton": {"button": btn.GetName()}})

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
				(self.tiles["houtline"], self.screen,  (127, 28), False),
				(self.tiles["houtline"], self.screen,  (128, 28), False),
				(self.tiles["houtline"], self.screen,  (129, 28), False),
			], True)

		self.blocks["C10"] = Block(self, self.frame, "C10",
			[
				(self.tiles["horiznc"], self.screen,  (127, 30), False),
				(self.tiles["horiz"],   self.screen,  (128, 30), False),
				(self.tiles["horiznc"], self.screen,  (129, 30), False),
				(self.tiles["horiz"],   self.screen,  (130, 30), False),
				(self.tiles["horiznc"], self.screen,  (131, 30), False),
				(self.tiles["horiz"],   self.screen,  (132, 30), False),
				(self.tiles["horiznc"], self.screen,  (133, 30), False),
				(self.tiles["horiz"],   self.screen,  (134, 30), False),
				(self.tiles["horiznc"], self.screen,  (135, 30), False),
				(self.tiles["horiz"],   self.screen,  (136, 30), False),
				(self.tiles["horiznc"], self.screen,  (137, 30), False),
				(self.tiles["horiz"],   self.screen,  (138, 30), False),
				(self.tiles["horiznc"], self.screen,  (139, 30), False),
				(self.tiles["horiz"],   self.screen,  (140, 30), False),
				(self.tiles["horiznc"], self.screen,  (141, 30), False),
				(self.tiles["horiz"],   self.screen,  (142, 30), False),
				(self.tiles["horiznc"], self.screen,  (143, 30), False),
				(self.tiles["horiz"],   self.screen,  (144, 30), False),
			], True)
		self.blocks["C10"].AddTrainLoc(self.screen, (130, 30))

		self.blocks["C30"] = Block(self, self.frame, "C30",
			[
				(self.tiles["horiznc"], self.screen,  (127, 32), False),
				(self.tiles["horiz"],   self.screen,  (128, 32), False),
				(self.tiles["horiznc"], self.screen,  (129, 32), False),
				(self.tiles["horiz"],   self.screen,  (130, 32), False),
				(self.tiles["horiznc"], self.screen,  (131, 32), False),
				(self.tiles["horiz"],   self.screen,  (132, 32), False),
				(self.tiles["horiznc"], self.screen,  (133, 32), False),
				(self.tiles["horiz"],   self.screen,  (134, 32), False),
				(self.tiles["horiznc"], self.screen,  (135, 32), False),
				(self.tiles["horiz"],   self.screen,  (136, 32), False),
				(self.tiles["horiznc"], self.screen,  (137, 32), False),
				(self.tiles["horiz"],   self.screen,  (138, 32), False),
				(self.tiles["horiznc"], self.screen,  (139, 32), False),
				(self.tiles["horiz"],   self.screen,  (140, 32), False),
				(self.tiles["horiznc"], self.screen,  (141, 32), False),
				(self.tiles["horiznc"], self.screen,  (143, 32), False),
				(self.tiles["horiz"],   self.screen,  (144, 32), False),
			], True)
		self.blocks["C30"].AddTrainLoc(self.screen, (130, 32))

		self.blocks["C31"] = Block(self, self.frame, "C31",
			[
				(self.tiles["horiznc"], self.screen,  (127, 34), False),
				(self.tiles["horiznc"], self.screen,  (128, 34), False),
				(self.tiles["horiznc"], self.screen,  (129, 34), False),
				(self.tiles["horiznc"], self.screen,  (130, 34), False),
				(self.tiles["eobright"], self.screen,  (131, 34), False),
			], True)
		self.blocks["C31"].AddTrainLoc(self.screen, (128, 34))

		self.blocks["COSGMW"] = OverSwitch(self, self.frame, "COSGMW",
			[
				(self.tiles["eobleft"], self.screen,  (119, 30), False),

				(self.tiles["diagleft"], self.screen, (121, 29), False),
				(self.tiles["turnleftleft"], self.screen, (122, 28), False),
				(self.tiles["horiznc"],  self.screen, (123, 28), False),
				(self.tiles["horiz"],    self.screen, (124, 28), False),
				(self.tiles["horiznc"],  self.screen, (125, 28), False),

				(self.tiles["horiz"],    self.screen, (122, 30), False),
				(self.tiles["horiznc"],  self.screen, (123, 30), False),
				(self.tiles["horiz"],    self.screen, (124, 30), False),
				(self.tiles["horiznc"],  self.screen, (125, 30), False),

				(self.tiles["diagright"], self.screen, (122, 31), False),

				(self.tiles["horiz"],    self.screen, (124, 32), False),
				(self.tiles["horiznc"],  self.screen, (125, 32), False),

				(self.tiles["diagright"], self.screen, (124, 33), False),
				(self.tiles["turnrightleft"], self.screen, (125, 34), False),
			], True)
		self.blocks["COSGMW"].AddTrainLoc(self.screen, (119, 37))

		self.osBlocks["COSGMW"] = ["C11", "G21", "C10", "C30", "C31"]

		self.blocks["G12"] = Block(self, self.frame, "G12",
			[
				(self.tiles["houtline"], self.screen,  (142, 26), False),
				(self.tiles["houtline"], self.screen,  (143, 26), False),
				(self.tiles["houtline"], self.screen,  (144, 26), False),
			], True)

		self.blocks["G10"] = Block(self, self.frame, "G10",
			[
				(self.tiles["houtline"], self.screen, (142, 28), False),
				(self.tiles["houtline"], self.screen, (143, 28), False),
				(self.tiles["houtline"], self.screen, (144, 28), False),
			], True)

		self.blocks["C20"] = Block(self, self.frame, "C20",
			[
				(self.tiles["eobleft"],  self.screen, (152, 30), False),
				(self.tiles["horiznc"],  self.screen, (153, 30), False),
				(self.tiles["horiz"],    self.screen, (154, 30), False),
				(self.tiles["horiznc"],  self.screen, (155, 30), False),
				(self.tiles["turnleftright"], self.screen, (156, 30), False),
				(self.tiles["turnrightdown"], self.screen, (157, 29), False),
				(self.tiles["verticalnc"], self.screen, (157, 28), False),
				(self.tiles["vertical"],   self.screen, (157, 27), False),
				(self.tiles["verticalnc"], self.screen, (157, 26), False),
				(self.tiles["vertical"],   self.screen, (157, 25), False),
				(self.tiles["verticalnc"], self.screen, (157, 24), False),
				(self.tiles["vertical"],   self.screen, (157, 23), False),
				(self.tiles["verticalnc"], self.screen, (157, 22), False),
				(self.tiles["vertical"],   self.screen, (157, 21), False),
				(self.tiles["verticalnc"], self.screen, (157, 20), False),
				(self.tiles["vertical"],   self.screen, (157, 19), False),
				(self.tiles["verticalnc"], self.screen, (157, 18), False),
				(self.tiles["vertical"],   self.screen, (157, 17), False),
				(self.tiles["verticalnc"], self.screen, (157, 16), False),
				(self.tiles["vertical"],   self.screen, (157, 15), False),
				(self.tiles["verticalnc"], self.screen, (157, 14), False),
				(self.tiles["vertical"],   self.screen, (157, 13), False),
				(self.tiles["verticalnc"], self.screen, (157, 12), False),
				(self.tiles["vertical"],   self.screen, (157, 11), False),
				(self.tiles["verticalnc"], self.screen, (157, 10), False),
				(self.tiles["vertical"],   self.screen, (157, 9), False),
				(self.tiles["verticalnc"], self.screen, (157, 8), False),
				(self.tiles["vertical"],   self.screen, (157, 7), False),
				(self.tiles["verticalnc"], self.screen, (157, 6), False),
				(self.tiles["vertical"],   self.screen, (157, 5), False),
				(self.tiles["turnleftup"], self.screen, (157, 4), False),
				(self.tiles["turnrightright"], self.screen, (156, 3), False),
				(self.tiles["eobleft"],    self.screen, (155, 3), False),
			], True)
		self.blocks["C20"].AddTrainLoc(self.screen, (153, 30))

		self.blocks["COSGME"] = OverSwitch(self, self.frame, "COSGME",
			[
				(self.tiles["turnrightright"], self.screen,  (146, 26), False),
				(self.tiles["diagright"],      self.screen, (147, 27), False),
				(self.tiles["diagright"],      self.screen, (149, 29), False),
				(self.tiles["eobright"],       self.screen, (151, 30), False),
				(self.tiles["horiznc"],        self.screen, (146, 28), False),
				(self.tiles["horiz"],          self.screen, (147, 28), False),
				(self.tiles["horiznc"],        self.screen, (146, 30), False),
				(self.tiles["horiz"],          self.screen, (147, 30), False),
				(self.tiles["horiznc"],        self.screen, (148, 30), False),
				(self.tiles["horiznc"],        self.screen, (146, 32), False),
				(self.tiles["turnleftright"],  self.screen, (147, 32), False),
				(self.tiles["diagleft"],       self.screen, (148, 31), False),
			], True)
		self.blocks["COSGME"].AddTrainLoc(self.screen, (145, 37))

		self.osBlocks["COSGME"] = ["C10", "C30", "G12", "G10", "C20"]

		# Sheffield yard and west OS
		self.blocks["C44"] = Block(self, self.frame, "C44",
			[
				(self.tiles["horiznc"],        self.screen, (119, 3), False),
				(self.tiles["horiz"],          self.screen, (120, 3), False),
				(self.tiles["horiznc"],        self.screen, (121, 3), False),
				(self.tiles["horiz"],          self.screen, (122, 3), False),
				(self.tiles["horiznc"],        self.screen, (123, 3), False),
				(self.tiles["horiz"],          self.screen, (124, 3), False),
				(self.tiles["horiznc"],        self.screen, (125, 3), False),
				(self.tiles["horiz"],          self.screen, (126, 3), False),
				(self.tiles["horiznc"],        self.screen, (127, 3), False),
				(self.tiles["horiz"],          self.screen, (128, 3), False),
				(self.tiles["horiznc"],        self.screen, (129, 3), False),
				(self.tiles["horiz"],          self.screen, (130, 3), False),
				(self.tiles["horiznc"],        self.screen, (131, 3), False),
				(self.tiles["horiz"],          self.screen, (132, 3), False),
				(self.tiles["horiznc"],        self.screen, (133, 3), False),
				(self.tiles["horiz"],          self.screen, (134, 3), False),
				(self.tiles["horiznc"],        self.screen, (135, 3), False),
				(self.tiles["horiz"],          self.screen, (136, 3), False),
				(self.tiles["horiznc"],        self.screen, (137, 3), False),
				(self.tiles["horiz"],          self.screen, (138, 3), False),
				(self.tiles["horiznc"],        self.screen, (139, 3), False),
				(self.tiles["horiz"],          self.screen, (140, 3), False),
				(self.tiles["horiznc"],        self.screen, (141, 3), False),
				(self.tiles["horiz"],          self.screen, (142, 3), False),
			], False)
		self.blocks["C44"].AddTrainLoc(self.screen, (122, 3))

		self.blocks["C43"] = Block(self, self.frame, "C43",
			[
				(self.tiles["horiznc"],        self.screen, (119, 5), False),
				(self.tiles["horiz"],          self.screen, (120, 5), False),
				(self.tiles["horiznc"],        self.screen, (121, 5), False),
				(self.tiles["horiz"],          self.screen, (122, 5), False),
				(self.tiles["horiznc"],        self.screen, (123, 5), False),
				(self.tiles["horiz"],          self.screen, (124, 5), False),
				(self.tiles["horiznc"],        self.screen, (125, 5), False),
				(self.tiles["horiz"],          self.screen, (126, 5), False),
				(self.tiles["horiznc"],        self.screen, (127, 5), False),
				(self.tiles["horiz"],          self.screen, (128, 5), False),
				(self.tiles["horiznc"],        self.screen, (129, 5), False),
				(self.tiles["horiz"],          self.screen, (130, 5), False),
				(self.tiles["horiznc"],        self.screen, (131, 5), False),
				(self.tiles["horiz"],          self.screen, (132, 5), False),
				(self.tiles["horiznc"],        self.screen, (133, 5), False),
				(self.tiles["horiz"],          self.screen, (134, 5), False),
				(self.tiles["horiznc"],        self.screen, (135, 5), False),
				(self.tiles["horiz"],          self.screen, (136, 5), False),
				(self.tiles["horiznc"],        self.screen, (137, 5), False),
				(self.tiles["horiz"],          self.screen, (138, 5), False),
				(self.tiles["horiznc"],        self.screen, (139, 5), False),
				(self.tiles["horiz"],          self.screen, (140, 5), False),
				(self.tiles["horiznc"],        self.screen, (141, 5), False),
				(self.tiles["horiz"],          self.screen, (142, 5), False),
			], False)
		self.blocks["C43"].AddTrainLoc(self.screen, (122, 5))

		self.blocks["C42"] = Block(self, self.frame, "C42",
			[
				(self.tiles["horiznc"],        self.screen, (119, 7), False),
				(self.tiles["horiz"],          self.screen, (120, 7), False),
				(self.tiles["horiznc"],        self.screen, (121, 7), False),
				(self.tiles["horiz"],          self.screen, (122, 7), False),
				(self.tiles["horiznc"],        self.screen, (123, 7), False),
				(self.tiles["horiz"],          self.screen, (124, 7), False),
				(self.tiles["horiznc"],        self.screen, (125, 7), False),
				(self.tiles["horiz"],          self.screen, (126, 7), False),
				(self.tiles["horiznc"],        self.screen, (127, 7), False),
				(self.tiles["horiz"],          self.screen, (128, 7), False),
				(self.tiles["horiznc"],        self.screen, (129, 7), False),
				(self.tiles["horiz"],          self.screen, (130, 7), False),
				(self.tiles["horiznc"],        self.screen, (131, 7), False),
				(self.tiles["horiz"],          self.screen, (132, 7), False),
				(self.tiles["horiznc"],        self.screen, (133, 7), False),
				(self.tiles["horiz"],          self.screen, (134, 7), False),
				(self.tiles["horiznc"],        self.screen, (135, 7), False),
				(self.tiles["horiz"],          self.screen, (136, 7), False),
				(self.tiles["horiznc"],        self.screen, (137, 7), False),
				(self.tiles["horiz"],          self.screen, (138, 7), False),
				(self.tiles["horiznc"],        self.screen, (139, 7), False),
				(self.tiles["horiz"],          self.screen, (140, 7), False),
				(self.tiles["horiznc"],        self.screen, (141, 7), False),
				(self.tiles["horiz"],          self.screen, (142, 7), False),
			], False)
		self.blocks["C42"].AddTrainLoc(self.screen, (122, 7))

		self.blocks["C41"] = Block(self, self.frame, "C41",
			[
				(self.tiles["horiznc"],        self.screen, (119, 9), False),
				(self.tiles["horiz"],          self.screen, (120, 9), False),
				(self.tiles["horiznc"],        self.screen, (121, 9), False),
				(self.tiles["horiz"],          self.screen, (122, 9), False),
				(self.tiles["horiznc"],        self.screen, (123, 9), False),
				(self.tiles["horiz"],          self.screen, (124, 9), False),
				(self.tiles["horiznc"],        self.screen, (125, 9), False),
				(self.tiles["horiz"],          self.screen, (126, 9), False),
				(self.tiles["horiznc"],        self.screen, (127, 9), False),
				(self.tiles["horiz"],          self.screen, (128, 9), False),
				(self.tiles["horiznc"],        self.screen, (129, 9), False),
				(self.tiles["horiz"],          self.screen, (130, 9), False),
				(self.tiles["horiznc"],        self.screen, (131, 9), False),
				(self.tiles["horiz"],          self.screen, (132, 9), False),
				(self.tiles["horiznc"],        self.screen, (133, 9), False),
				(self.tiles["horiz"],          self.screen, (134, 9), False),
				(self.tiles["horiznc"],        self.screen, (135, 9), False),
				(self.tiles["horiz"],          self.screen, (136, 9), False),
				(self.tiles["horiznc"],        self.screen, (137, 9), False),
				(self.tiles["horiz"],          self.screen, (138, 9), False),
				(self.tiles["horiznc"],        self.screen, (139, 9), False),
				(self.tiles["horiz"],          self.screen, (140, 9), False),
				(self.tiles["horiznc"],        self.screen, (141, 9), False),
				(self.tiles["horiz"],          self.screen, (142, 9), False),
			], False)
		self.blocks["C41"].AddTrainLoc(self.screen, (122, 9))

		self.blocks["C40"] = Block(self, self.frame, "C40",
			[
				(self.tiles["horiznc"],        self.screen, (119, 11), False),
				(self.tiles["horiz"],          self.screen, (120, 11), False),
				(self.tiles["horiznc"],        self.screen, (121, 11), False),
				(self.tiles["horiz"],          self.screen, (122, 11), False),
				(self.tiles["horiznc"],        self.screen, (123, 11), False),
				(self.tiles["horiz"],          self.screen, (124, 11), False),
				(self.tiles["horiznc"],        self.screen, (125, 11), False),
				(self.tiles["horiz"],          self.screen, (126, 11), False),
				(self.tiles["horiznc"],        self.screen, (127, 11), False),
				(self.tiles["horiz"],          self.screen, (128, 11), False),
				(self.tiles["horiznc"],        self.screen, (129, 11), False),
				(self.tiles["horiz"],          self.screen, (130, 11), False),
				(self.tiles["horiznc"],        self.screen, (131, 11), False),
				(self.tiles["horiz"],          self.screen, (132, 11), False),
				(self.tiles["horiznc"],        self.screen, (133, 11), False),
				(self.tiles["horiz"],          self.screen, (134, 11), False),
				(self.tiles["horiznc"],        self.screen, (135, 11), False),
				(self.tiles["horiz"],          self.screen, (136, 11), False),
				(self.tiles["horiznc"],        self.screen, (137, 11), False),
			], False)
		self.blocks["C40"].AddTrainLoc(self.screen, (122, 11))

		self.blocks["C21"] = Block(self, self.frame, "C21",
			[
				(self.tiles["horiznc"],        self.screen, (119, 13), False),
				(self.tiles["horiz"],          self.screen, (120, 13), False),
				(self.tiles["horiznc"],        self.screen, (121, 13), False),
				(self.tiles["horiz"],          self.screen, (122, 13), False),
				(self.tiles["horiznc"],        self.screen, (123, 13), False),
				(self.tiles["horiz"],          self.screen, (124, 13), False),
				(self.tiles["horiznc"],        self.screen, (125, 13), False),
				(self.tiles["horiz"],          self.screen, (126, 13), False),
				(self.tiles["horiznc"],        self.screen, (127, 13), False),
				(self.tiles["horiz"],          self.screen, (128, 13), False),
				(self.tiles["horiznc"],        self.screen, (129, 13), False),
				(self.tiles["horiz"],          self.screen, (130, 13), False),
				(self.tiles["horiznc"],        self.screen, (131, 13), False),
				(self.tiles["horiz"],          self.screen, (132, 13), False),
				(self.tiles["horiznc"],        self.screen, (133, 13), False),
				(self.tiles["horiz"],          self.screen, (134, 13), False),
				(self.tiles["horiznc"],        self.screen, (135, 13), False),
				(self.tiles["horiz"],          self.screen, (136, 13), False),
				(self.tiles["horiznc"],        self.screen, (137, 13), False),
			], False)
		self.blocks["C21"].AddTrainLoc(self.screen, (122, 13))

		self.blocks["C50"] = Block(self, self.frame, "C50",
			[
				(self.tiles["horiznc"],        self.screen, (119, 15), False),
				(self.tiles["horiz"],          self.screen, (120, 15), False),
				(self.tiles["horiznc"],        self.screen, (121, 15), False),
				(self.tiles["horiz"],          self.screen, (122, 15), False),
				(self.tiles["horiznc"],        self.screen, (123, 15), False),
				(self.tiles["horiz"],          self.screen, (124, 15), False),
				(self.tiles["horiznc"],        self.screen, (125, 15), False),
				(self.tiles["horiz"],          self.screen, (126, 15), False),
				(self.tiles["horiznc"],        self.screen, (127, 15), False),
				(self.tiles["horiz"],          self.screen, (128, 15), False),
				(self.tiles["horiznc"],        self.screen, (129, 15), False),
				(self.tiles["horiz"],          self.screen, (130, 15), False),
				(self.tiles["horiznc"],        self.screen, (131, 15), False),
				(self.tiles["horiz"],          self.screen, (132, 15), False),
				(self.tiles["horiznc"],        self.screen, (133, 15), False),
				(self.tiles["horiz"],          self.screen, (134, 15), False),
				(self.tiles["horiznc"],        self.screen, (135, 15), False),
				(self.tiles["horiz"],          self.screen, (136, 15), False),
				(self.tiles["horiznc"],        self.screen, (137, 15), False),
			], False)
		self.blocks["C50"].AddTrainLoc(self.screen, (122, 15))

		self.blocks["C51"] = Block(self, self.frame, "C51",
			[
				(self.tiles["horiznc"],        self.screen, (125, 17), False),
				(self.tiles["horiz"],          self.screen, (126, 17), False),
				(self.tiles["horiznc"],        self.screen, (127, 17), False),
				(self.tiles["horiz"],          self.screen, (128, 17), False),
				(self.tiles["horiznc"],        self.screen, (129, 17), False),
				(self.tiles["horiz"],          self.screen, (130, 17), False),
				(self.tiles["horiznc"],        self.screen, (131, 17), False),
			], False)
		self.blocks["C51"].AddTrainLoc(self.screen, (126, 17))

		self.blocks["C52"] = Block(self, self.frame, "C52",
			[
				(self.tiles["horiznc"],        self.screen, (125, 19), False),
				(self.tiles["horiz"],          self.screen, (126, 19), False),
				(self.tiles["horiznc"],        self.screen, (127, 19), False),
				(self.tiles["horiz"],          self.screen, (128, 19), False),
				(self.tiles["horiznc"],        self.screen, (129, 19), False),
				(self.tiles["horiz"],          self.screen, (130, 19), False),
				(self.tiles["horiznc"],        self.screen, (131, 19), False),
			], False)
		self.blocks["C52"].AddTrainLoc(self.screen, (126, 19))

		self.blocks["C53"] = Block(self, self.frame, "C53",
			[
				(self.tiles["horiznc"],        self.screen, (125, 21), False),
				(self.tiles["horiz"],          self.screen, (126, 21), False),
				(self.tiles["horiznc"],        self.screen, (127, 21), False),
				(self.tiles["horiz"],          self.screen, (128, 21), False),
				(self.tiles["horiznc"],        self.screen, (129, 21), False),
				(self.tiles["horiz"],          self.screen, (130, 21), False),
				(self.tiles["horiznc"],        self.screen, (131, 21), False),
			], False)
		self.blocks["C53"].AddTrainLoc(self.screen, (126, 21))

		self.blocks["C54"] = Block(self, self.frame, "C54",
			[
				(self.tiles["horiznc"],        self.screen, (125, 23), False),
				(self.tiles["horiz"],          self.screen, (126, 23), False),
				(self.tiles["horiznc"],        self.screen, (127, 23), False),
				(self.tiles["horiz"],          self.screen, (128, 23), False),
				(self.tiles["horiznc"],        self.screen, (129, 23), False),
				(self.tiles["horiz"],          self.screen, (130, 23), False),
				(self.tiles["horiznc"],        self.screen, (131, 23), False),
			], False)
		self.blocks["C54"].AddTrainLoc(self.screen, (126, 23))

		self.blocks["COSSHE"] = OverSwitch(self, self.frame, "COSSHE",
			[
				(self.tiles["horiznc"],        self.screen, (144, 3), False),
				(self.tiles["horiz"],          self.screen, (145, 3), False),
				(self.tiles["horiznc"],        self.screen, (146, 3), False),
				(self.tiles["horiz"],          self.screen, (147, 3), False),
				(self.tiles["horiznc"],        self.screen, (148, 3), False),
				(self.tiles["horiz"],          self.screen, (149, 3), False),
				(self.tiles["horiz"],          self.screen, (151, 3), False),
				(self.tiles["horiznc"],        self.screen, (152, 3), False),
				(self.tiles["eobright"],       self.screen, (154, 3), False),

				(self.tiles["horiznc"],        self.screen, (144, 5), False),
				(self.tiles["horiz"],          self.screen, (145, 5), False),
				(self.tiles["horiznc"],        self.screen, (146, 5), False),
				(self.tiles["horiz"],          self.screen, (147, 5), False),
				(self.tiles["turnleftright"],  self.screen, (148, 5), False),
				(self.tiles["diagleft"],       self.screen, (149, 4), False),

				(self.tiles["horiznc"],        self.screen, (144, 7), False),
				(self.tiles["horiz"],          self.screen, (145, 7), False),
				(self.tiles["horiz"],          self.screen, (147, 7), False),
				(self.tiles["horiznc"],        self.screen, (148, 7), False),
				(self.tiles["diagleft"],       self.screen, (150, 6), False),
				(self.tiles["diagleft"],       self.screen, (151, 5), False),
				(self.tiles["diagleft"],       self.screen, (152, 4), False),

				(self.tiles["turnleftright"],  self.screen, (144, 9), False),
				(self.tiles["diagleft"],       self.screen, (145, 8), False),

				(self.tiles["horiz"],          self.screen, (139, 11), False),
				(self.tiles["horiznc"],        self.screen, (140, 11), False),
				(self.tiles["horiz"],          self.screen, (141, 11), False),
				(self.tiles["horiznc"],        self.screen, (142, 11), False),
				(self.tiles["horiz"],          self.screen, (143, 11), False),
				(self.tiles["horiznc"],        self.screen, (144, 11), False),
				(self.tiles["diagleft"],       self.screen, (146, 10), False),
				(self.tiles["diagleft"],       self.screen, (147, 9), False),
				(self.tiles["diagleft"],       self.screen, (148, 8), False),

				(self.tiles["horiz"],          self.screen, (139, 13), False),
				(self.tiles["horiznc"],        self.screen, (140, 13), False),
				(self.tiles["horiz"],          self.screen, (141, 13), False),
				(self.tiles["horiznc"],        self.screen, (142, 13), False),
				(self.tiles["diagleft"],       self.screen, (144, 12), False),

				(self.tiles["horiz"],          self.screen, (139, 15), False),
				(self.tiles["horiznc"],        self.screen, (140, 15), False),
				(self.tiles["diagleft"],       self.screen, (142, 14), False),

				(self.tiles["horiz"],          self.screen, (133, 17), False),
				(self.tiles["horiznc"],        self.screen, (134, 17), False),
				(self.tiles["horiz"],          self.screen, (135, 17), False),
				(self.tiles["horiz"],          self.screen, (137, 17), False),
				(self.tiles["horiznc"],        self.screen, (138, 17), False),
				(self.tiles["diagleft"],       self.screen, (140, 16), False),

				(self.tiles["horiz"],          self.screen, (133, 19), False),
				(self.tiles["turnleftright"],  self.screen, (134, 19), False),
				(self.tiles["diagleft"],       self.screen, (135, 18), False),

				(self.tiles["horiz"],          self.screen, (133, 21), False),
				(self.tiles["horiznc"],        self.screen, (134, 21), False),
				(self.tiles["diagleft"],       self.screen, (136, 20), False),
				(self.tiles["diagleft"],       self.screen, (137, 19), False),
				(self.tiles["diagleft"],       self.screen, (138, 18), False),

				(self.tiles["turnleftright"],  self.screen, (133, 23), False),
				(self.tiles["diagleft"],       self.screen, (134, 22), False),
			], False)
		self.blocks["COSSHE"].AddTrainLoc(self.screen, (146, 15))

		self.osBlocks["COSSHE"] = ["C44", "C43", "C42", "C41", "C40", "C21", "C50", "C51", "C52", "C53", "C54", "C20"]

		self.blocks["COSSHW"] = OverSwitch(self, self.frame, "COSSHW",
			[
				(self.tiles["eobleft"],        self.screen, (106, 13), False),
				(self.tiles["diagleft"],       self.screen, (108, 12), False),
				(self.tiles["diagleft"],       self.screen, (109, 11), False),
				(self.tiles["diagleft"],       self.screen, (110, 10), False),
				(self.tiles["diagleft"],       self.screen, (112, 8), False),
				(self.tiles["diagleft"],       self.screen, (113, 7), False),
				(self.tiles["diagleft"],       self.screen, (114, 6), False),
				(self.tiles["diagleft"],       self.screen, (116, 4), False),
				(self.tiles["turnleftleft"],   self.screen, (117, 3), False),

				(self.tiles["horiznc"],        self.screen, (116, 5), False),
				(self.tiles["horiz"],          self.screen, (117, 5), False),

				(self.tiles["horiznc"],        self.screen, (112, 9), False),
				(self.tiles["horiz"],          self.screen, (113, 9), False),
				(self.tiles["diagleft"],       self.screen, (115, 8), False),
				(self.tiles["turnleftleft"],   self.screen, (116, 7), False),
				(self.tiles["horiz"],          self.screen, (117, 7), False),

				(self.tiles["horiz"],          self.screen, (115, 9), False),
				(self.tiles["horiznc"],        self.screen, (116, 9), False),
				(self.tiles["horiz"],          self.screen, (117, 9), False),

				(self.tiles["horiznc"],        self.screen, (108, 13), False),
				(self.tiles["horiz"],          self.screen, (109, 13), False),

				(self.tiles["diagleft"],       self.screen, (111, 12), False),
				(self.tiles["turnleftleft"],   self.screen, (112, 11), False),
				(self.tiles["horiz"],          self.screen, (113, 11), False),
				(self.tiles["horiznc"],        self.screen, (114, 11), False),
				(self.tiles["horiz"],          self.screen, (115, 11), False),
				(self.tiles["horiznc"],        self.screen, (116, 11), False),
				(self.tiles["horiz"],          self.screen, (117, 11), False),

				(self.tiles["horiz"],          self.screen, (111, 13), False),
				(self.tiles["horiznc"],        self.screen, (112, 13), False),
				(self.tiles["horiznc"],        self.screen, (114, 13), False),
				(self.tiles["horiz"],          self.screen, (115, 13), False),
				(self.tiles["horiznc"],        self.screen, (116, 13), False),
				(self.tiles["horiz"],          self.screen, (117, 13), False),

				(self.tiles["diagright"],      self.screen, (114, 14), False),
				(self.tiles["horiznc"],        self.screen, (116, 15), False),
				(self.tiles["horiz"],          self.screen, (117, 15), False),
				(self.tiles["diagright"],      self.screen, (116, 16), False),

				(self.tiles["horiznc"],        self.screen, (118, 17), False),
				(self.tiles["horiz"],          self.screen, (119, 17), False),
				(self.tiles["horiz"],          self.screen, (121, 17), False),
				(self.tiles["horiznc"],        self.screen, (122, 17), False),
				(self.tiles["horiz"],          self.screen, (123, 17), False),

				(self.tiles["diagright"],      self.screen, (121, 18), False),
				(self.tiles["turnrightleft"],  self.screen, (122, 19), False),
				(self.tiles["horiz"],          self.screen, (123, 19), False),

				(self.tiles["diagright"],      self.screen, (118, 18), False),
				(self.tiles["diagright"],      self.screen, (119, 19), False),
				(self.tiles["diagright"],      self.screen, (120, 20), False),

				(self.tiles["horiznc"],        self.screen, (122, 21), False),
				(self.tiles["horiz"],          self.screen, (123, 21), False),

				(self.tiles["diagright"],      self.screen, (122, 22), False),
				(self.tiles["turnrightleft"],  self.screen, (123, 23), False),
			], False)
		self.blocks["COSSHW"].AddTrainLoc(self.screen, (107, 4))

		self.osBlocks["COSSHW"] = ["C22", "C44", "C43", "C42", "C41", "C40", "C21", "C50", "C51", "C52", "C53", "C54"]

		return self.blocks, self.osBlocks

	def DefineTurnouts(self, blocks):
		self.turnouts = {}

		hsList = [
			["CSw3",   "toleftleft",   "C30", (142, 32)],
		]
		toList = [
			["CSw31",  "torightleft",  ["COSGME"], (150, 30)],
			["CSw33",  "toleftleft",   ["COSGME"], (149, 30)],
			["CSw35",  "toleftup",     ["COSGME"], (148, 28)],
			["CSw37",  "toleftdown",   ["COSGMW"], (123, 32)],
			["CSw39",  "torightright", ["COSGMW"], (121, 30)],
			["CSw41",  "toleftright",  ["COSGMW"], (120, 30)],
			["CSw43",  "toleftleft",   ["COSSHE"], (153, 3)],
			["CSw45",  "torightdowninv",  ["COSSHE"], (149, 7)],
			["CSw47",  "torightdowninv",  ["COSSHE"], (145, 11)],
			["CSw49",  "toleftleft",   ["COSSHE"], (150, 3)],
			["CSw51",  "toleftleft",   ["COSSHE"], (146, 7)],
			["CSw53",  "toleftright",  ["COSSHW"], (114, 9)],
			["CSw55",  "toleftright",  ["COSSHW"], (110, 13)],
			["CSw57",  "torightup",    ["COSSHW"], (115, 5)],
			["CSw59",  "torightup",    ["COSSHW"], (111, 9)],
			["CSw61",  "toleftright",  ["COSSHW"], (107, 13)],
			["CSw63",  "torightdown",  ["COSSHE"], (143, 13)],
			["CSw65",  "torightdown",  ["COSSHE"], (141, 15)],
			["CSw67",  "torightdown",  ["COSSHE"], (139, 17)],
			["CSw69",  "toleftleft",   ["COSSHE"], (136, 17)],
			["CSw71",  "torightdown",  ["COSSHE"], (135, 21)],
			["CSw73",  "torightright", ["COSSHW"], (113, 13)],
			["CSw75",  "toleftdown",   ["COSSHW"], (115, 15)],
			["CSw77",  "toleftdown",   ["COSSHW"], (117, 17)],
			["CSw79",  "torightright", ["COSSHW"], (120, 17)],
			["CSw81",  "toleftdown",   ["COSSHW"], (121, 21)],
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
			["CG21W", (126, 28)],
			["CC10W", (126, 30)],
			["CC30W", (126, 32)],
			["CC31W", (126, 34)],
			["CG12E", (145, 26)],
			["CG10E", (145, 28)],
			["CC10E", (145, 30)],
			["CC30E", (145, 32)],

			["CC44E", (143, 3)],
			["CC43E", (143, 5)],
			["CC42E", (143, 7)],
			["CC41E", (143, 9)],
			["CC40E", (138, 11)],
			["CC21E", (138, 13)],
			["CC50E", (138, 15)],
			["CC51E", (132, 17)],
			["CC52E", (132, 19)],
			["CC53E", (132, 21)],
			["CC54E", (132, 23)],

			["CC44W", (118, 3)],
			["CC43W", (118, 5)],
			["CC42W", (118, 7)],
			["CC41W", (118, 9)],
			["CC40W", (118, 11)],
			["CC21W", (118, 13)],
			["CC50W", (118, 15)],
			["CC51W", (124, 17)],
			["CC52W", (124, 19)],
			["CC53W", (124, 21)],
			["CC54W", (124, 23)],
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
			["C2LD", RegAspects,    True,  "right",     (145, 27)],
			["C2LC", RegAspects,    True,  "right",     (145, 29)],
			["C2LB", RegAspects,    True,  "rightlong", (145, 31)],
			["C2LA", SloAspects,    True,  "right",     (145, 33)],

			["C2R",  RegSloAspects, False, "leftlong",  (151, 29)],

			["C4L",  RegSloAspects, True,  "rightlong", (119, 31)],

			["C4RD", RegAspects,    False, "left",      (126, 27)],
			["C4RC", RegAspects,    False, "leftlong",  (126, 29)],
			["C4RB", SloAspects,    False, "left",      (126, 31)],
			["C4RA", SloAspects,    False, "left",      (126, 33)],

			["C6LF", RegAspects,    True,  "right",     (143, 4)],
			["C6LE", RegAspects,    True,  "right",     (143, 6)],
			["C6LD", RegAspects,    True,  "right",     (143, 8)],
			["C6LC", RegAspects,    True,  "right",     (143, 10)],
			["C6LB", RegAspects,    True,  "right",     (138, 12)],
			["C6LA", RegAspects,    True,  "right",     (138, 14)],
			["C6LG", RegAspects,    True,  "right",     (138, 16)],
			["C6LH", RegAspects,    True,  "right",     (132, 18)],
			["C6LJ", RegAspects,    True,  "right",     (132, 20)],
			["C6LK", RegAspects,    True,  "right",     (132, 22)],
			["C6LL", RegAspects,    True,  "right",     (132, 24)],

			["C6R",  RegAspects,    False, "leftlong",  (154, 2)],

			["C8L",  RegAspects,    True,  "rightlong", (106, 14)],

			["C8RF", RegAspects,    False, "left",      (118, 2)],
			["C8RE", RegAspects,    False, "left",      (118, 4)],
			["C8RD", RegAspects,    False, "left",      (118, 6)],
			["C8RC", RegAspects,    False, "left",      (118, 8)],
			["C8RB", RegAspects,    False, "left",      (118, 10)],
			["C8RA", RegAspects,    False, "left",      (118, 12)],
			["C8RG", RegAspects,    False, "left",      (118, 14)],
			["C8RH", RegAspects,    False, "left",      (124, 16)],
			["C8RJ", RegAspects,    False, "left",      (124, 18)],
			["C8RK", RegAspects,    False, "left",      (124, 20)],
			["C8RL", RegAspects,    False, "left",      (124, 22)],
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
		self.routes["CRtC11G21"] = Route(self.screen, block, "CRtC11G21", "C11", [(119, 30), (120, 30), (121, 29), (122, 28), (123, 28), (124, 28), (125, 28)], "G21", [RESTRICTING, RESTRICTING], ["CSw41:R"], ["C4L", "C4RD"])
		self.routes["CRtC11C10"] = Route(self.screen, block, "CRtC11C10", "C11", [(119, 30), (120, 30), (121, 30), (122, 30), (123, 30), (124, 30), (125, 30)], "C10", [MAIN, MAIN], ["CSw39:N", "CSw41:N"], ["C4L", "C4RC"])
		self.routes["CRtC11C30"] = Route(self.screen, block, "CRtC11C30", "C11", [(119, 30), (120, 30), (121, 30), (122, 31), (123, 32), (124, 32), (125, 32)], "C30", [SLOW, SLOW], ["CSw37:R", "CSw39:R", "CSw41:N"], ["C4L", "C4RB"])
		self.routes["CRtC11C31"] = Route(self.screen, block, "CRtC11C31", "C11", [(119, 30), (120, 30), (121, 30), (122, 31), (123, 32), (124, 33), (125, 34)], "C31", [RESTRICTING, SLOW], ["CSw37:N", "CSw39:R", "CSw41:N"], ["C4L", "C4RA"])

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
		self.routes["CRtG12C20"] = Route(self.screen, block, "CRtG12C20", "G12", [(146, 26), (147, 27), (148, 28), (149, 29), (150, 30), (151, 30)], "C20", [RESTRICTING, RESTRICTING], ["CSw31:R", "CSw35:N"], ["C2LD", "C2R"])
		self.routes["CRtG10C20"] = Route(self.screen, block, "CRtG10C20", "G10", [(146, 28), (147, 28), (148, 28), (149, 29), (150, 30), (151, 30)], "C20", [RESTRICTING, RESTRICTING], ["CSw31:R", "CSw35:R"], ["C2LC", "C2R"])
		self.routes["CRtC10C20"] = Route(self.screen, block, "CRtC10C20", "C10", [(146, 30), (147, 30), (148, 30), (149, 30), (150, 30), (151, 30)], "C20", [MAIN, MAIN], ["CSw31:N", "CSw33:N"], ["C2LB", "C2R"])
		self.routes["CRtC30C20"] = Route(self.screen, block, "CRtC30C20", "C30", [(146, 32), (147, 32), (148, 31), (149, 30), (150, 30), (151, 30)], "C20", [SLOW, SLOW], ["CSw31:N", "CSw33:R"], ["C2LA", "C2R"])

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
		self.routes["CRtC20C44"] = Route(self.screen, block, "CRtC20C44", "C20", [(144, 3), (145, 3), (146, 3), (147, 3), (148, 3), (149, 3), (150, 3), (151, 3), (152, 3), (153, 3), (154, 3)], "C44", [SLOW, SLOW], ["CSw43:N", "CSw49:N"], ["C6R", "C6LF"])
		self.routes["CRtC20C43"] = Route(self.screen, block, "CRtC20C43", "C20", [(144, 5), (145, 5), (146, 5), (147, 5), (148, 5), (149, 4), (150, 3), (151, 3), (152, 3), (153, 3), (154, 3)], "C43", [SLOW, SLOW], ["CSw43:N", "CSw49:R"], ["C6R", "C6LE"])
		self.routes["CRtC20C42"] = Route(self.screen, block, "CRtC20C42", "C20", [(144, 7), (145, 7), (146, 7), (147, 7), (148, 7), (149, 7), (150, 6), (151, 5), (152, 4), (153, 3), (154, 3)], "C42", [SLOW, SLOW], ["CSw43:R", "CSw45:N", "CSw51:N", "CSw47:N"], ["C6R", "C6LD"])
		self.routes["CRtC20C41"] = Route(self.screen, block, "CRtC20C41", "C20", [(144, 9), (145, 8), (146, 7), (147, 7), (148, 7), (149, 7), (150, 6), (151, 5), (152, 4), (153, 3), (154, 3)], "C41", [SLOW, SLOW], ["CSw43:R", "CSw45:N", "CSw51:R", "CSw47:R"], ["C6R", "C6LC"])
		self.routes["CRtC20C40"] = Route(self.screen, block, "CRtC20C40", "C20", [(139, 11), (140, 11), (141, 11), (142, 11), (143, 11), (144, 11), (145, 11), (146, 10), (147, 9), (148, 8), (149, 7), (150, 6), (151, 5), (152, 4), (153, 3), (154, 3)], "C40", [SLOW, SLOW], ["CSw43:R", "CSw45:R", "CSw47:N", "CSw51:N"], ["C6R", "C6LB"])
		self.routes["CRtC20C21"] = Route(self.screen, block, "CRtC20C21", "C20", [(139, 13), (140, 13), (141, 13), (142, 13), (143, 13), (144, 12), (145, 11), (146, 10), (147, 9), (148, 8), (149, 7), (150, 6), (151, 5), (152, 4), (153, 3), (154, 3)], "C21", [MAIN, MAIN], ["CSw43:R", "CSw45:R", "CSw47:R", "CSw51:R", "CSw63:R"], ["C6R", "C6LA"])
		self.routes["CRtC20C50"] = Route(self.screen, block, "CRtC20C50", "C20", [(139, 15), (140, 15), (141, 15), (142, 14), (143, 13), (144, 12), (145, 11), (146, 10), (147, 9), (148, 8), (149, 7), (150, 6), (151, 5), (152, 4), (153, 3), (154, 3)], "C50", [SLOW, SLOW], ["CSw43:R", "CSw45:R", "CSw47:R", "CSw51:R", "CSw63:N", "CSw65:R"], ["C6R", "C6LG"])
		self.routes["CRtC20C51"] = Route(self.screen, block, "CRtC20C51", "C20",
				[(133, 17), (134, 17), (135, 17), (136, 17), (137, 17), (138, 17), (139, 17), (140, 16), (141, 15), (142, 14), (143, 13), (144, 12), (145, 11), (146, 10), (147, 9), (148, 8), (149, 7), (150, 6), (151, 5), (152, 4), (153, 3), (154, 3)], "C51", [SLOW, SLOW], ["CSw43:R", "CSw45:R", "CSw47:R", "CSw51:R", "CSw63:N", "CSw65:N", "CSw67:R", "CSw69:N"], ["C6R", "C6LH"])
		self.routes["CRtC20C52"] = Route(self.screen, block, "CRtC20C52", "C20",
				[(133, 19), (134, 19), (135, 18), (136, 17), (137, 17), (138, 17), (139, 17), (140, 16), (141, 15), (142, 14), (143, 13), (144, 12), (145, 11), (146, 10), (147, 9), (148, 8), (149, 7), (150, 6), (151, 5), (152, 4), (153, 3), (154, 3)], "C52", [SLOW, SLOW], ["CSw43:R", "CSw45:R", "CSw47:R", "CSw51:R", "CSw63:N", "CSw65:N", "CSw67:R", "CSw69:R"], ["C6R", "C6LJ"])
		self.routes["CRtC20C53"] = Route(self.screen, block, "CRtC20C53", "C20",
				[(133, 21), (134, 21), (135, 21), (136, 20), (137, 19), (138, 18), (139, 17), (140, 16), (141, 15), (142, 14), (143, 13), (144, 12), (145, 11), (146, 10), (147, 9), (148, 8), (149, 7), (150, 6), (151, 5), (152, 4), (153, 3), (154, 3)], "C53", [SLOW, SLOW], ["CSw43:R", "CSw45:R", "CSw47:R", "CSw51:R", "CSw63:N", "CSw65:N", "CSw67:N", "CSw71:R"], ["C6R", "C6LK"])
		self.routes["CRtC20C54"] = Route(self.screen, block, "CRtC20C54", "C20",
				[(133, 23), (134, 22), (135, 21), (136, 20), (137, 19), (138, 18), (139, 17), (140, 16), (141, 15), (142, 14), (143, 13), (144, 12), (145, 11), (146, 10), (147, 9), (148, 8), (149, 7), (150, 6), (151, 5), (152, 4), (153, 3), (154, 3)], "C54", [SLOW, SLOW], ["CSw43:R", "CSw45:R", "CSw47:R", "CSw51:R", "CSw63:N", "CSw65:N", "CSw67:N", "CSw71:N"], ["C6R", "C6LL"])

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
		self.routes["CRtC44C22"] = Route(self.screen, block, "CRtC44C22", "C44", [(106, 13), (107, 13), (108, 12), (109, 11), (110, 10), (111, 9), (112, 8), (113, 7), (114, 6), (115, 5), (116, 4), (117, 3)], "C22", [SLOW, SLOW], ["CSw57:N", "CSw59:N", "CSw61:R"], ["C8RF", "C8L"])
		self.routes["CRtC43C22"] = Route(self.screen, block, "CRtC43C22", "C43", [(106, 13), (107, 13), (108, 12), (109, 11), (110, 10), (111, 9), (112, 8), (113, 7), (114, 6), (115, 5), (116, 5), (117, 5)], "C22", [SLOW, SLOW], ["CSw57:R", "CSw59:N", "CSw61:R"], ["C8RE", "C8L"])
		self.routes["CRtC42C22"] = Route(self.screen, block, "CRtC42C22", "C42", [(106, 13), (107, 13), (108, 12), (109, 11), (110, 10), (111, 9), (112, 9), (113, 9), (114, 9), (115, 8), (116, 7), (117, 7)], "C22", [SLOW, SLOW], ["CSw53:R", "CSw59:R", "CSw61:R"], ["C8RD", "C8L"])
		self.routes["CRtC41C22"] = Route(self.screen, block, "CRtC41C22", "C41", [(106, 13), (107, 13), (108, 12), (109, 11), (110, 10), (111, 9), (112, 9), (113, 9), (114, 9), (115, 9), (116, 9), (117, 9)], "C22", [SLOW, SLOW], ["CSw53:N", "CSw59:R", "CSw61:R"], ["C8RC", "C8L"])
		self.routes["CRtC40C22"] = Route(self.screen, block, "CRtC40C22", "C40", [(106, 13), (107, 13), (108, 13), (109, 13), (110, 13), (111, 12), (112, 11), (113, 11), (114, 11), (115, 11), (116, 11), (117, 11)], "C22", [SLOW, SLOW], ["CSw55:R", "CSw61:N"], ["C8RB", "C8L"])
		self.routes["CRtC21C22"] = Route(self.screen, block, "CRtC21C22", "C21", [(106, 13), (107, 13), (108, 13), (109, 13), (110, 13), (111, 13), (112, 13), (113, 13), (114, 13), (115, 13), (116, 13), (117, 13)], "C22", [MAIN, DIVERGING], ["CSw55:N", "CSw61:N", "CSw73:N"], ["C8RA", "C8L"])
		self.routes["CRtC50C22"] = Route(self.screen, block, "CRtC50C22", "C50", [(106, 13), (107, 13), (108, 13), (109, 13), (110, 13), (111, 13), (112, 13), (113, 13), (114, 14), (115, 15), (116, 15), (117, 15)], "C22", [SLOW, SLOW], ["CSw55:N", "CSw61:N", "CSw73:R", "CSw75:R"], ["C8RG", "C8L"])
		self.routes["CRtC51C22"] = Route(self.screen, block, "CRtC51C22", "C51", [
				(106, 13), (107, 13), (108, 13), (109, 13), (110, 13), (111, 13), (112, 13), (113, 13), (114, 14), (115, 15), (116, 16), (117, 17), (118, 17), (119, 17), (120, 17), (121, 17), (122, 17), (123, 17)], "C22", [SLOW, SLOW], ["CSw55:N", "CSw61:N", "CSw73:R", "CSw75:N", "CSw77:R", "CSw79:N"], ["C8RH", "C8L"])
		self.routes["CRtC52C22"] = Route(self.screen, block, "CRtC52C22", "C52", [
				(106, 13), (107, 13), (108, 13), (109, 13), (110, 13), (111, 13), (112, 13), (113, 13), (114, 14), (115, 15), (116, 16), (117, 17), (118, 17), (119, 17), (120, 17), (121, 18), (122, 19), (123, 19)], "C22", [SLOW, SLOW], ["CSw55:N", "CSw61:N", "CSw73:R", "CSw75:N", "CSw77:R", "CSw79:R"], ["C8RJ", "C8L"])
		self.routes["CRtC53C22"] = Route(self.screen, block, "CRtC53C22", "C53", [
				(106, 13), (107, 13), (108, 13), (109, 13), (110, 13), (111, 13), (112, 13), (113, 13), (114, 14), (115, 15), (116, 16), (117, 17), (118, 18), (119, 19), (120, 20), (121, 21), (122, 21), (123, 21)], "C22", [SLOW, SLOW], ["CSw55:N", "CSw61:N", "CSw73:R", "CSw75:N", "CSw77:N", "CSw81:R"], ["C8RK", "C8L"])
		self.routes["CRtC54C22"] = Route(self.screen, block, "CRtC54C22", "C54", [
				(106, 13), (107, 13), (108, 13), (109, 13), (110, 13), (111, 13), (112, 13), (113, 13), (114, 14), (115, 15), (116, 16), (117, 17), (118, 18), (119, 19), (120, 20), (121, 21), (122, 22), (123, 23)], "C22", [SLOW, SLOW], ["CSw55:N", "CSw61:N", "CSw73:R", "CSw75:N", "CSw77:N", "CSw81:N"], ["C8RL", "C8L"])

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

		hs = HandSwitch(self, self.screen, self.frame, self.blocks["C30"], "CSw3.hand", (142, 33), self.misctiles["handup"])
		self.blocks["C30"].AddHandSwitch(hs)
		self.handswitches["CSw3.hand"] = hs

		return self.handswitches
