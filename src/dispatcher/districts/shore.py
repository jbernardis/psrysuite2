from dispatcher.district import District

from dispatcher.block import Block, OverSwitch, OSProxy, Route
from dispatcher.turnout import Turnout
from dispatcher.signal import Signal
from dispatcher.handswitch import HandSwitch

from dispatcher.constants import RESTRICTING, MAIN, DIVERGING,  OCCUPIED, CLEARED, STOP, RegAspects, restrictedaspect


class Shore (District):
	def __init__(self, name, frame, screen):
		District.__init__(self, name, frame, screen)

	def PerformSignalAction(self, sig, callon=False, silent=False):
		signm = sig.GetName()
		osblk = self.blocks["SOSHF"]
		if signm not in ["S8L", "S8R"]:
			if not callon:
				if signm in ["S12R", "S12LA", "S12LB", "S12LC", "S4R", "S4LA", "S4LB", "S4LC"]:
					if osblk.IsBusy():
						self.ReportOSBusy(osblk.GetRouteDesignator())
						return False
			return District.PerformSignalAction(self, sig, callon=callon)

		aspect = sig.GetAspect()
		signm = sig.GetName()
		movement = aspect == 0  # do we want the signal to allow movement
		if movement:
			if osblk.IsBusy() or self.blocks["SOSW"].IsBusy() or self.blocks["SOSE"].IsBusy():
				self.ReportOSBusy(osblk.GetRouteDesignator())
				return False
			aspect = restrictedaspect(sig.GetAspectType())
		else:  # stopping
			esig = osblk.GetEntrySignal()	
			if esig is not None and esig.GetName() != signm:
				self.frame.PopupEvent("Incorrect signal")
				return False
			aspect = STOP

		self.frame.Request({"signal": {"name": signm, "aspect": aspect, "aspecttype": sig.GetAspectType()}})
		sig.SetLock(osblk.GetName(), 0 if aspect == 0 else 1)
		return True

	def DoSignalAction(self, sig, aspect, frozenaspect=None, callon=False):
		if not callon:
			signm = sig.GetName()
			if signm in ["S8L", "S8R"]:
				osblk = self.blocks["SOSHF"]
				east = signm == "S8R"
				osblk.SetEast(east)
				osblk.SetRoute(self.routes["SRtF10F11"])
				sig.SetAspect(aspect, refresh=True)
				if aspect == STOP:
					osblk.SetEntrySignal(None)
				else:
					osblk.SetEntrySignal(sig)
				osblk.SetCleared(aspect != STOP, refresh=True)
		
				if osblk.IsBusy() and aspect == STOP:
					return
		
				exitBlk = self.frame.GetBlockByName("F11" if east else "F10")
				entryBlk = self.frame.GetBlockByName("F10" if east else "F11")
				if exitBlk.IsOccupied():
					return
		
				exitBlk.SetEast(east)
				entryBlk.SetEast(east)
				exitBlk.SetCleared(aspect != STOP, refresh=True)
				return
					
			elif signm in ["S12R", "S12LA", "S12LB", "S12LC", "S4R", "S4LA", "S4LB", "S4LC"]:
				if self.blocks["SOSHF"].IsBusy():
					return
			
		District.DoSignalAction(self, sig, aspect, frozenaspect=frozenaspect, callon=callon)
		self.drawCrossing()

	def DoSignalLeverAction(self, signame, state, callon, silent=1, source=None):
		if source == "ctc":
			if signame == "S8.lvr":
				for osname in ["SOSE", "SOSW"]:
					osblk = self.blocks[osname]
					if osblk.IsBusy():
						self.ReportOSBusy(osblk.GetRouteDesignator())
						return False

			elif signame in ["S12.lvr", "S4.lvr"]:
				osblk = self.blocks["SOSHF"]
				if osblk.IsBusy():
					self.ReportOSBusy(osblk.GetRouteDesignator())
					return False

		return District.DoSignalLeverAction(self, signame, state, callon, silent, source)
		
	def DoBlockAction(self, blk, blockend, state):
		blknm = blk.GetName()
		if blknm == "S21" and blockend == "E" and not self.frame.GetBlockByName("KOSN20S21").GetEast():
			District.DoBlockAction(self, self.frame.GetBlockByName("KOSN20S21"), None, state)
		elif blknm == "S11" and blockend == "E" and not self.frame.GetBlockByName("KOSN10S11").GetEast():
			District.DoBlockAction(self, self.frame.GetBlockByName("KOSN10S11"), None, state)
		
		if blknm == "SOSHF" and state == "E":
			for sig in [self.signals["S8L"], self.signals["S8R"]]:
				sig.SetLock("SOSHF", 0)
		District.DoBlockAction(self, blk, blockend, state)

	def DrawOthers(self, block):
		if block.GetName() in ["SOSHF", "SOSW", "SOSE"]:
			self.drawCrossing()

	def drawCrossing(self):
		osstat = self.blocks["SOSHF"].GetStatus()
		bwstat = self.blocks["SOSW"].GetStatus()
		bestat = self.blocks["SOSE"].GetStatus()

		if self.turnouts["SSw3"].IsReverse() or self.turnouts["SSw5"].IsReverse():
			bwstat, bestat = bestat, bwstat

		if osstat == "O":
			bmpw = bmpe = "red-cross"
		elif osstat == "U":
			bmpw = bmpe = "yellow-cross"
		elif osstat == "C":
			bmpw = bmpe = "green-cross"
		else:
			if bwstat == "O":
				bmpw = "red-main"
			elif bwstat == "U":
				bmpw = "yellow-main"
			elif bwstat == "C":
				bmpw = "green-main"
			else:
				bmpw = "white-main"

			if bestat == "O":
				bmpe = "red-main"
			elif bestat == "U":
				bmpe = "yellow-main"
			elif bestat == "C":
				bmpe = "green-main"
			else:
				bmpe = "white-main"

		bmp = self.misctiles["crossing"].getBmp("", bmpw)
		self.frame.DrawTile(self.screen, (90, 11), bmp)

		bmp = self.misctiles["crossing"].getBmp("", bmpe)
		self.frame.DrawTile(self.screen, (92, 13), bmp)

	def DetermineRoute(self, blocks):
		s3 = 'N' if self.turnouts["SSw3"].IsNormal() else 'R'
		s5 = 'N' if self.turnouts["SSw5"].IsNormal() else 'R'
		self.turnouts["SSw3"].SetLock(s5 == 'R', refresh=True)
		self.turnouts["SSw3b"].SetLock(s5 == 'R', refresh=True)
		self.turnouts["SSw5"].SetLock(s3 == 'R', refresh=True)
		self.turnouts["SSw5b"].SetLock(s3 == 'R', refresh=True)

		self.FindTurnoutCombinations(blocks, ["SSw3", "SSw5", "SSw7", "SSw9", "SSw11", "SSw13", "SSw15", "SSw17", "SSw19"])

	def DefineBlocks(self):
		self.blocks = {}
		self.osBlocks = {}

		self.blocks["S10"] = Block(self, self.frame, "S10",
			[
				(self.tiles["horiz"],    self.screen, (74, 11), False),
				(self.tiles["horiznc"],  self.screen, (75, 11), False),
				(self.tiles["horiz"],    self.screen, (76, 11), False),
				(self.tiles["horiz"],    self.screen, (78, 11), False),
				(self.tiles["horiznc"],  self.screen, (79, 11), False),
			], False)
		self.blocks["S10"].AddStoppingBlock([
				(self.tiles["eobleft"],  self.screen, (71, 11), False),
				(self.tiles["horiz"],    self.screen, (72, 11), False),
				(self.tiles["horiznc"],  self.screen, (73, 11), False),
			], False)
		self.blocks["S10"].AddStoppingBlock([
				(self.tiles["horiz"],    self.screen, (80, 11), False),
				(self.tiles["horiznc"],  self.screen, (81, 11), False),
				(self.tiles["eobright"], self.screen, (82, 11), False),
			], True)
		self.blocks["S10"].AddTrainLoc(self.screen, (73, 11))

		self.blocks["S11"] = Block(self, self.frame, "S11",
			[
				(self.tiles["horiz"],    self.screen, (109, 7), False),
				(self.tiles["horiznc"],  self.screen, (110, 7), False),
				(self.tiles["horiz"],    self.screen, (111, 7), False),
				(self.tiles["horiznc"],  self.screen, (112, 7), False),
				(self.tiles["horiz"],    self.screen, (113, 7), False),
				(self.tiles["horiznc"],  self.screen, (114, 7), False),
				(self.tiles["horiz"],    self.screen, (115, 7), False),
				(self.tiles["horiznc"],  self.screen, (116, 7), False),
				(self.tiles["horiz"],    self.screen, (117, 7), False),
				(self.tiles["horiznc"],  self.screen, (118, 7), False),
			], False)
		self.blocks["S11"].AddStoppingBlock([
				(self.tiles["eobleft"],  self.screen, (106, 7), False),
				(self.tiles["horiz"],    self.screen, (107, 7), False),
				(self.tiles["horiznc"],  self.screen, (108, 7), False),
			], False)
		self.blocks["S11"].AddStoppingBlock([
				(self.tiles["horiz"],    self.screen, (119, 7), False),
				(self.tiles["horiznc"],  self.screen, (120, 7), False),
				(self.tiles["eobright"], self.screen, (121, 7), False),
			], True)
		self.blocks["S11"].AddTrainLoc(self.screen, (112, 7))

		self.blocks["S20"] = Block(self, self.frame, "S20",
			[
				(self.tiles["horiz"],    self.screen, (74, 13), False),
				(self.tiles["horiznc"],  self.screen, (75, 13), False),
				(self.tiles["horiz"],    self.screen, (76, 13), False),
				(self.tiles["horiznc"],  self.screen, (77, 13), False),
				(self.tiles["horiz"],    self.screen, (78, 13), False),
				(self.tiles["horiznc"],  self.screen, (79, 13), False),
			], True)
		self.blocks["S20"].AddStoppingBlock([
				(self.tiles["eobleft"],  self.screen, (71, 13), False),
				(self.tiles["horiz"],    self.screen, (72, 13), False),
				(self.tiles["horiznc"],  self.screen, (73, 13), False),
			], False)
		self.blocks["S20"].AddStoppingBlock([
				(self.tiles["horiz"],    self.screen, (80, 13), False),
				(self.tiles["horiznc"],  self.screen, (81, 13), False),
				(self.tiles["eobright"], self.screen, (82, 13), False),
			], True)
		self.blocks["S20"].AddTrainLoc(self.screen, (73, 13))

		self.blocks["S21"] = Block(self, self.frame, "S21",
			[
				(self.tiles["horiz"],    self.screen, (113, 19), False),
				(self.tiles["horiznc"],  self.screen, (114, 19), False),
				(self.tiles["horiz"],    self.screen, (115, 19), False),
				(self.tiles["horiznc"],  self.screen, (116, 19), False),
				(self.tiles["horiz"],    self.screen, (117, 19), False),
				(self.tiles["horiznc"],  self.screen, (118, 19), False),
			], True)		
		self.blocks["S21"].AddStoppingBlock([
				(self.tiles["eobleft"],  self.screen, (110, 19), False),
				(self.tiles["horiz"],    self.screen, (111, 19), False),
				(self.tiles["horiznc"],  self.screen, (112, 19), False),
			], False)
		self.blocks["S21"].AddStoppingBlock([
				(self.tiles["horiz"],    self.screen, (119, 19), False),
				(self.tiles["horiznc"],  self.screen, (120, 19), False),
				(self.tiles["eobright"], self.screen, (121, 19), False),
			], True)
		
		self.blocks["S21"].AddTrainLoc(self.screen, (112, 19))

		self.blocks["SOSW"] = OverSwitch(self, self.frame, "SOSW", 
			[
				(self.tiles["eobleft"],   self.screen, (83, 11), False),
				(self.tiles["horiznc"],   self.screen, (85, 11), False),
				(self.tiles["horiz"],     self.screen, (86, 11), False),
				(self.tiles["horiznc"],   self.screen, (87, 11), False),
				(self.tiles["horiz"],     self.screen, (88, 11), False),
				(self.tiles["horiznc"],   self.screen, (91, 11), False),
				(self.tiles["horiz"],     self.screen, (92, 11), False),
				(self.tiles["horiznc"],   self.screen, (93, 11), False),
				(self.tiles["horiz"],     self.screen, (94, 11), False),
				(self.tiles["horiznc"],   self.screen, (95, 11), False),
				(self.tiles["horiz"],     self.screen, (96, 11), False),
				(self.tiles["horiznc"],   self.screen, (97, 11), False),
				(self.tiles["horiz"],     self.screen, (98, 11), False),
				(self.tiles["horiz"],     self.screen, (100, 11), False),
				(self.tiles["horiznc"],   self.screen, (101, 11), False),
				(self.tiles["horiz"],     self.screen, (102, 11), False),
				(self.tiles["horiznc"],   self.screen, (103, 11), False),
				(self.tiles["horiz"],     self.screen, (104, 11), False),
				(self.tiles["eobright"],  self.screen, (105, 11), False),
				(self.tiles["diagleft"],  self.screen, (100, 10), False),
				(self.tiles["diagleft"],  self.screen, (101, 9), False),
				(self.tiles["diagleft"],  self.screen, (102, 8), False),
				(self.tiles["turnleftleft"], self.screen, (103, 7), False),
				(self.tiles["horiz"],     self.screen, (104, 7), False),
				(self.tiles["eobright"],  self.screen, (105, 7), False),
				(self.tiles["diagleft"],  self.screen, (103, 10), False),
				(self.tiles["turnleftleft"], self.screen, (104, 9), False),
				(self.tiles["eobright"],  self.screen, (105, 9), False),
				(self.tiles["diagright"], self.screen, (85, 12), False),
				(self.tiles["horiz"],     self.screen, (88, 13), False),
				(self.tiles["horiznc"],   self.screen, (89, 13), False),
				(self.tiles["horiz"],     self.screen, (90, 13), False),
				(self.tiles["horiznc"],   self.screen, (91, 13), False),
				(self.tiles["horiznc"],   self.screen, (93, 13), False),
				(self.tiles["horiz"],     self.screen, (94, 13), False),
				(self.tiles["horiznc"],   self.screen, (95, 13), False),
				(self.tiles["horiz"],     self.screen, (96, 13), False),
				(self.tiles["horiznc"],   self.screen, (97, 13), False),
				(self.tiles["horiz"],     self.screen, (98, 13), False),
				(self.tiles["horiz"],     self.screen, (100, 13), False),
				(self.tiles["horiznc"],   self.screen, (101, 13), False),
				(self.tiles["horiznc"],   self.screen, (103, 13), False),
				(self.tiles["horiz"],     self.screen, (104, 13), False),
				(self.tiles["eobright"],  self.screen, (105, 13), False),
				(self.tiles["diagright"], self.screen, (100, 14), False),
				(self.tiles["diagright"], self.screen, (101, 15), False),
				(self.tiles["diagright"], self.screen, (102, 16), False),
				(self.tiles["diagright"], self.screen, (103, 17), False),
				(self.tiles["diagright"], self.screen, (104, 18), False),
				(self.tiles["diagright"], self.screen, (105, 19), False),
				(self.tiles["diagright"], self.screen, (106, 20), False),
				(self.tiles["turnrightleft"], self.screen, (107, 21), False),
				(self.tiles["horiz"],     self.screen, (108, 21), False),
				(self.tiles["eobright"],  self.screen, (109, 21), False),
				(self.tiles["diagright"], self.screen, (103, 14), False),
				(self.tiles["diagright"], self.screen, (104, 15), False),
				(self.tiles["diagright"], self.screen, (105, 16), False),
				(self.tiles["diagright"], self.screen, (106, 17), False),
				(self.tiles["diagright"], self.screen, (107, 18), False),
				(self.tiles["turnrightleft"], self.screen, (108, 19), False),
				(self.tiles["eobright"],  self.screen, (109, 19), False),
			],
			False)
		# self.blocks["SOSW"].AddTrainLoc(self.screen, (94, 11), ["SRtS10S11", "SRtS10H30", "SRtS10H10"])
		# self.blocks["SOSW"].AddTrainLoc(self.screen, (94, 13), ["SRtS10H20", "SRtS10S21", "SRtS10P32"])
		self.blocks["SOSW"].AddTrainLoc(self.screen, (84, 18))

		self.blocks["SOSE"] = OverSwitch(self, self.frame, "SOSE", 
			[
				(self.tiles["eobleft"],   self.screen, (83, 13), False),
				(self.tiles["horiz"],     self.screen, (84, 13), False),
				(self.tiles["horiznc"],   self.screen, (85, 13), False),
				(self.tiles["diagleft"],  self.screen, (88, 12), False),
				(self.tiles["horiznc"],   self.screen, (85, 11), False),
				(self.tiles["horiz"],     self.screen, (86, 11), False),
				(self.tiles["horiznc"],   self.screen, (87, 11), False),
				(self.tiles["horiz"],     self.screen, (88, 11), False),
				(self.tiles["horiznc"],   self.screen, (91, 11), False),
				(self.tiles["horiz"],     self.screen, (92, 11), False),
				(self.tiles["horiznc"],   self.screen, (93, 11), False),
				(self.tiles["horiz"],     self.screen, (94, 11), False),
				(self.tiles["horiznc"],   self.screen, (95, 11), False),
				(self.tiles["horiz"],     self.screen, (96, 11), False),
				(self.tiles["horiznc"],   self.screen, (97, 11), False),
				(self.tiles["horiz"],     self.screen, (98, 11), False),
				(self.tiles["horiz"],     self.screen, (100, 11), False),
				(self.tiles["horiznc"],   self.screen, (101, 11), False),
				(self.tiles["horiz"],     self.screen, (102, 11), False),
				(self.tiles["horiznc"],   self.screen, (103, 11), False),
				(self.tiles["horiz"],     self.screen, (104, 11), False),
				(self.tiles["eobright"],  self.screen, (105, 11), False),
				(self.tiles["diagleft"],  self.screen, (100, 10), False),
				(self.tiles["diagleft"],  self.screen, (101, 9), False),
				(self.tiles["diagleft"],  self.screen, (102, 8), False),
				(self.tiles["turnleftleft"], self.screen, (103, 7), False),
				(self.tiles["horiz"],     self.screen, (104, 7), False),
				(self.tiles["eobright"],  self.screen, (105, 7), False),
				(self.tiles["diagleft"],  self.screen, (103, 10), False),
				(self.tiles["turnleftleft"], self.screen, (104, 9), False),
				(self.tiles["eobright"],  self.screen, (105, 9), False),
				(self.tiles["horiz"],     self.screen, (88, 13), False),
				(self.tiles["horiznc"],   self.screen, (89, 13), False),
				(self.tiles["horiz"],     self.screen, (90, 13), False),
				(self.tiles["horiznc"],   self.screen, (91, 13), False),
				(self.tiles["horiznc"],   self.screen, (93, 13), False),
				(self.tiles["horiz"],     self.screen, (94, 13), False),
				(self.tiles["horiznc"],   self.screen, (95, 13), False),
				(self.tiles["horiz"],     self.screen, (96, 13), False),
				(self.tiles["horiznc"],   self.screen, (97, 13), False),
				(self.tiles["horiz"],     self.screen, (98, 13), False),
				(self.tiles["horiz"],     self.screen, (100, 13), False),
				(self.tiles["horiznc"],   self.screen, (101, 13), False),
				(self.tiles["horiznc"],   self.screen, (103, 13), False),
				(self.tiles["horiz"],     self.screen, (104, 13), False),
				(self.tiles["eobright"],  self.screen, (105, 13), False),
				(self.tiles["diagright"], self.screen, (100, 14), False),
				(self.tiles["diagright"], self.screen, (101, 15), False),
				(self.tiles["diagright"], self.screen, (102, 16), False),
				(self.tiles["diagright"], self.screen, (103, 17), False),
				(self.tiles["diagright"], self.screen, (104, 18), False),
				(self.tiles["diagright"], self.screen, (105, 19), False),
				(self.tiles["diagright"], self.screen, (106, 20), False),
				(self.tiles["turnrightleft"], self.screen, (107, 21), False),
				(self.tiles["horiz"],     self.screen, (108, 21), False),
				(self.tiles["eobright"],  self.screen, (109, 21), False),
				(self.tiles["diagright"], self.screen, (103, 14), False),
				(self.tiles["diagright"], self.screen, (104, 15), False),
				(self.tiles["diagright"], self.screen, (105, 16), False),
				(self.tiles["diagright"], self.screen, (106, 17), False),
				(self.tiles["diagright"], self.screen, (107, 18), False),
				(self.tiles["turnrightleft"], self.screen, (108, 19), False),
				(self.tiles["eobright"],  self.screen, (109, 19), False),
			],
			True)
		# self.blocks["SOSE"].AddTrainLoc(self.screen, (94, 11), ["SRtS20S11", "SRtS20H30", "SRtS20H10"])
		# self.blocks["SOSE"].AddTrainLoc(self.screen, (94, 13), ["SRtS20H20", "SRtS20S21", "SRtS20P32"])
		self.blocks["SOSE"].AddTrainLoc(self.screen, (84, 20))

		self.blocks["F10"] = Block(self, self.frame, "F10",
			[
				(self.tiles["horiz"],    self.screen, (83, 9), False),
				(self.tiles["horiznc"],  self.screen, (84, 9), False),
			], True)
		self.blocks["F10"].AddStoppingBlock([
				(self.tiles["horiz"],    self.screen, (85, 9), False),
				(self.tiles["eobright"], self.screen, (86, 9), False),
			], True)
		self.blocks["F10"].AddTrainLoc(self.screen, (83, 9))

		self.blocks["F11"] = Block(self, self.frame, "F11",
			[
				(self.tiles["diagright"],      self.screen, (98, 16), False),
				(self.tiles["diagright"],      self.screen, (99, 17), False),
				(self.tiles["diagright"],      self.screen, (100, 18), False),
				(self.tiles["diagright"],      self.screen, (101, 19), False),
				(self.tiles["diagright"],      self.screen, (102, 20), False),
				(self.tiles["turnleftup"],     self.screen, (103, 21), False),
				(self.tiles["eobdown"],        self.screen, (103, 22), False),
			], False)
		self.blocks["F11"].AddStoppingBlock([
				(self.tiles["eobleft"],        self.screen, (96, 15), False),
				(self.tiles["turnrightright"], self.screen, (97, 15), False),
		], False)
		self.blocks["F11"].AddTrainLoc(self.screen, (99, 17))

		self.blocks["SOSHF"] = OverSwitch(self, self.frame, "SOSHF", 
			[
				(self.tiles["eobleft"],        self.screen, (87, 9), False),
				(self.tiles["turnrightright"], self.screen, (88, 9), False),
				(self.tiles["diagright"],      self.screen, (89, 10), False),
				(self.tiles["diagright"],      self.screen, (91, 12), False),
				(self.tiles["diagright"],      self.screen, (93, 14), False),
				(self.tiles["turnrightleft"],  self.screen, (94, 15), False),
				(self.tiles["eobright"],       self.screen, (95, 15), False),
			],
			True)
		self.blocks["SOSHF"].AddTrainLoc(self.screen, (89, 7))

		self.blocks["SOSHJW"] = OverSwitch(self, self.frame, "SOSHJW",
			[
				(self.tiles["eobleft"],   self.screen, (114, 11), False),
				(self.tiles["horiznc"],   self.screen, (115, 11), False),
				(self.tiles["horiz"],     self.screen, (116, 11), False),
				(self.tiles["horiznc"],   self.screen, (117, 11), False),
				(self.tiles["horiz"],     self.screen, (118, 11), False),
				(self.tiles["horiznc"],   self.screen, (119, 11), False),
				(self.tiles["horiz"],     self.screen, (120, 11), False),
				(self.tiles["eobright"],  self.screen, (122, 11), False),
			], False)
		self.blocks["SOSHJW"].AddTrainLoc(self.screen, (116, 27))

		self.blocks["SOSHJM"] = OverSwitch(self, self.frame, "SOSHJM",
			[
				(self.tiles["eobright"],      self.screen, (122, 11), False),
				(self.tiles["diagleft"],      self.screen, (120, 12), False),
				(self.tiles["eobleft"],       self.screen, (114, 13), False),
				(self.tiles["horiznc"],       self.screen, (115, 13), False),
				(self.tiles["horiz"],         self.screen, (116, 13), False),
				(self.tiles["horiz"],         self.screen, (120, 13), False),
				(self.tiles["horiznc"],       self.screen, (121, 13), False),
				(self.tiles["eobright"],      self.screen, (122, 13), False),
				(self.tiles["diagright"],     self.screen, (119, 14), False),
				(self.tiles["turnrightleft"], self.screen, (120, 15), False),
				(self.tiles["horiznc"],       self.screen, (121, 15), False),
				(self.tiles["eobright"],      self.screen, (122, 15), False),
			], True)
		self.blocks["SOSHJM"].AddTrainLoc(self.screen, (116, 29))

		self.blocks["SOSHJE"] = OverSwitch(self, self.frame, "SOSHJE",
			[
				(self.tiles["eobright"],  self.screen, (122, 11), False),
				(self.tiles["diagleft"],  self.screen, (120, 12), False),
				(self.tiles["horiz"],     self.screen, (120, 13), False),
				(self.tiles["horiznc"],   self.screen, (121, 13), False),
				(self.tiles["eobright"],  self.screen, (122, 13), False),
				(self.tiles["diagright"], self.screen, (119, 14), False),
				(self.tiles["turnrightleft"], self.screen, (120, 15), False),
				(self.tiles["horiznc"],   self.screen, (121, 15), False),
				(self.tiles["eobright"],  self.screen, (122, 15), False),
				(self.tiles["diagleft"],  self.screen, (116, 14), False),
				(self.tiles["eobleft"],   self.screen, (114, 15), False),
				(self.tiles["horiz"],     self.screen, (116, 15), False),
				(self.tiles["turnrightright"], self.screen, (117, 15), False),
				(self.tiles["diagright"], self.screen, (118, 16), False),
				(self.tiles["turnrightleft"], self.screen, (119, 17), False),
				(self.tiles["eobright"],  self.screen, (120, 17), False),
			], True)
		self.blocks["SOSHJE"].AddTrainLoc(self.screen, (116, 31))

		self.osBlocks["SOSW"] = ["S10", "S11", "H30", "H10", "H20", "S21", "P32"]
		self.osBlocks["SOSE"] = ["S20", "S11", "H30", "H10", "H20", "S21", "P32"]
		self.osBlocks["SOSHF"] = ["F10", "F11"]
		self.osBlocks["SOSHJW"] = ["H10", "H11"]
		self.osBlocks["SOSHJM"] = ["H11", "H20", "H21", "H40"]
		self.osBlocks["SOSHJE"] = ["H11", "H21", "H40", "P42", "N25"]

		return self.blocks, self.osBlocks

	def DefineTurnouts(self, blocks):
		self.turnouts = {}

		hsList = [
			["SSw1",  "torightleft",  "S10", (77, 11)],
		]
			
		toList = [
			["SSw3",  "torightright",     ["SOSW", "SOSE"], (84, 11)],
			["SSw3b",  "torightleft",     ["SOSW", "SOSE"], (86, 13)],
			["SSw5",   "toleftleft",      ["SOSW", "SOSE"], (89, 11)],
			["SSw5b",  "toleftright",     ["SOSW", "SOSE"], (87, 13)],
			["SSw7",   "torightright",    ["SOSW", "SOSE"], (99, 13)],
			["SSw9",   "torightrightinv", ["SOSW", "SOSE"], (102, 13)],
			["SSw11",  "toleftrightinv",  ["SOSW", "SOSE"], (99, 11)],
			["SSw13",  "toleftright",     ["SOSW", "SOSE"], (102, 11)],

			["SSw15",  "toleftleft",   ["SOSHJM", "SOSHJE"], (117, 13)],
			["SSw15b", "toleftright",  ["SOSHJM", "SOSHJE"], (115, 15)],
			["SSw17",  "torightright", ["SOSHJM", "SOSHJE"], (118, 13)],
			["SSw19",  "toleftright",  ["SOSHJW", "SOSHJM", "SOSHJE"], (119, 13)],
			["SSw19b", "toleftleft",   ["SOSHJW", "SOSHJM", "SOSHJE"], (121, 11)],
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

		self.turnouts["SSw3"].SetPairedTurnout(self.turnouts["SSw3b"])
		self.turnouts["SSw5"].SetPairedTurnout(self.turnouts["SSw5b"])
		self.turnouts["SSw15"].SetPairedTurnout(self.turnouts["SSw15b"])
		self.turnouts["SSw19"].SetPairedTurnout(self.turnouts["SSw19b"])

		self.turnouts["SSw1"].SetDisabled(True)

		return self.turnouts

	def DefineSignals(self):
		self.signals = {}
		self.osProxies = {}

		sigList = [
			["S12R", RegAspects, True,    "rightlong", (83, 12)],
			["S4R",  RegAspects, True,    "rightlong", (83, 14)],

			["S12LA", RegAspects, False,   "leftlong",  (105, 6)],
			["S12LB", RegAspects, False,   "left",  (105, 8)],
			["S12LC", RegAspects, False,   "leftlong",  (105, 10)],

			["S4LA", RegAspects, False,    "left", (105, 12)],
			["S4LB", RegAspects, False,    "leftlong", (109, 18)],
			["S4LC", RegAspects, False,    "leftlong", (109, 20)],

			["S8R",  RegAspects, True,    "rightlong",  (87, 10)],
			["S8L",  RegAspects, False,   "leftlong",  (95, 14)],

			["S16R", RegAspects, True,    "rightlong", (114, 16)],
			["S16L", RegAspects, False,   "leftlong",  (120, 16)],

			["S18R",  RegAspects, True,    "rightlong", (114, 14)],
			["S18LA", RegAspects, False,   "left",  (122, 12)],
			["S18LB", RegAspects, False,   "left",  (122, 14)],

			["S20R", RegAspects, True,    "right", (114, 12)],
			["S20L", RegAspects, False,   "leftlong",  (122, 10)]

		]
		for signm, atype, east, tileSet, pos in sigList:
			self.signals[signm]  = Signal(self, self.screen, self.frame, signm, atype, east, pos, self.sigtiles[tileSet])

		self.signals["S18LA"].SetMutexSignals(["S18LB"])
		self.signals["S18LB"].SetMutexSignals(["S18LA"])
		
		self.signals["S4LA"].SetMutexSignals(["S4LB", "S4LC"])
		self.signals["S4LB"].SetMutexSignals(["S4LA", "S4LC"])
		self.signals["S4LC"].SetMutexSignals(["S4LA", "S4LB"])

		blockSbSigs = {
			# which signals govern stopping sections, west and east
			"S10": ("D12L", "S12R"),
			"S20": ("D10L", "S4R"),
			"S11": ("S12LA", "S11E"),
			"F10": (None, "S8R"),
			"F11": ("S8L", None),
			"S21": ("S4LB", "S21E"),
		}

		self.blockSigs = {
			"S10": ("D12L", "S12R"),
			"S20": ("D10L", "S4R"),
			"S11": ("S12LA", "S11E"),
			"F10": (None, "S8R"),
			"F11": ("S8L", None),
			"S21": ("S4LB", "S21E"),
		}

		for blknm, siglist in blockSbSigs.items():
			self.blocks[blknm].SetSBSignals(siglist)
			self.blocks[blknm].SetSignals(siglist)

		self.sigLeverMap = {
			"S4.lvr":  ["SOSE", "SOSW"],
			"S8.lvr":  ["SOSHF"],
			"S12.lvr": ["SOSE", "SOSW"],
			"S16.lvr": ["SOSHJE"],
			"S18.lvr": ["SOSHJE", "SOSHJM"],
			"S20.lvr": ["SOSHJE", "SOSHJM", "SOSHJW"],
		}

		for sl in self.sigLeverMap:
			self.frame.AddSignalLever(sl, self)

		self.routes = {}
		self.osSignals = {}

		block = self.blocks["SOSW"]
		self.routes["SRtS10S11"] = Route(self.screen, block, "SRtS10S11", "S11", [(83, 11), (84, 11), (85, 11), (86, 11), (87, 11), (88, 11), (89, 11),
																				(90, 11), (91, 11), (92, 11), (93, 11), (94, 11), (95, 11), (96, 11), (97, 11), (98, 11), (99, 11),
																				(100, 10), (101, 9), (102, 8), (103, 7), (104, 7), (105, 7)], "S10", [MAIN, MAIN], ["SSw3:N", "SSw5:N", "SSw11:N"], ["S12LA", "S12R"])
		self.routes["SRtS10H30"] = Route(self.screen, block, "SRtS10H30", "H30", [(83, 11), (84, 11), (85, 11), (86, 11), (87, 11), (88, 11), (89, 11),
																				(90, 11), (91, 11), (92, 11), (93, 11), (94, 11), (95, 11), (96, 11), (97, 11), (98, 11), (99, 11),
																				(100, 11), (101, 11), (102, 11), (103, 10), (104, 9), (105, 9)], "S10", [RESTRICTING, RESTRICTING], ["SSw3:N", "SSw5:N", "SSw11:R", "SSw13:R"], ["S12LB", "S12R"])
		self.routes["SRtS10H10"] = Route(self.screen, block, "SRtS10H10", "H10", [(83, 11), (84, 11), (85, 11), (86, 11), (87, 11), (88, 11), (89, 11),
																				(90, 11), (91, 11), (92, 11), (93, 11), (94, 11), (95, 11), (96, 11), (97, 11), (98, 11), (99, 11),
																				(100, 11), (101, 11), (102, 11), (103, 11), (104, 11), (105, 11)], "S10", [RESTRICTING, DIVERGING], ["SSw3:N", "SSw5:N", "SSw11:R", "SSw13:N"], ["S12LC", "S12R"])
		self.routes["SRtS10H20"] = Route(self.screen, block, "SRtS10H20", "H20", [(83, 11), (84, 11), (85, 12), (86, 13), (87, 13), (88, 13), (89, 13),
																				(90, 13), (91, 13), (92, 13), (93, 13), (94, 13), (95, 13), (96, 13), (97, 13), (98, 13), (99, 13),
																				(100, 13), (101, 13), (102, 13), (103, 13), (104, 13), (105, 13)], "S10", [DIVERGING, RESTRICTING], ["SSw3:R", "SSw5:N", "SSw7:N", "SSw9:R"], ["S4LA", "S12R"])
		self.routes["SRtS10S21"] = Route(self.screen, block, "SRtS10S21", "S21", [(83, 11), (84, 11), (85, 12), (86, 13), (87, 13), (88, 13), (89, 13),
																				(90, 13), (91, 13), (92, 13), (93, 13), (94, 13), (95, 13), (96, 13), (97, 13), (98, 13), (99, 13),
																				(100, 13), (101, 13), (102, 13), (103, 14), (104, 15), (105, 16), (106, 17), (107, 18), (108, 19), (109, 19)], "S10", [DIVERGING, RESTRICTING], ["SSw3:R", "SSw5:N", "SSw7:N", "SSw9:N"], ["S4LB", "S12R"])
		self.routes["SRtS10P32"] = Route(self.screen, block, "SRtS10P32", "P32", [(83, 11), (84, 11), (85, 12), (86, 13), (87, 13), (88, 13), (89, 13),
																				(90, 13), (91, 13), (92, 13), (93, 13), (94, 13), (95, 13), (96, 13), (97, 13), (98, 13), (99, 13),
																				(100, 14), (101, 15), (102, 16), (103, 17), (104, 18), (105, 19), (106, 20), (107, 21), (108, 21), (109, 21)], "S10", [DIVERGING, DIVERGING], ["SSw3:R", "SSw5:N", "SSw7:R"], ["S4LC", "S12R"])
		
		block = self.blocks["SOSE"]
		self.routes["SRtS20S21"] = Route(self.screen, block, "SRtS20S21", "S20", [(83, 13), (84, 13), (85, 13), (86, 13), (87, 13), (88, 13), (89, 13),
																				(90, 13), (91, 13), (92, 13), (93, 13), (94, 13), (95, 13), (96, 13), (97, 13), (98, 13), (99, 13),
																				(100, 13), (101, 13), (102, 13), (103, 14), (104, 15), (105, 16), (106, 17), (107, 18), (108, 19), (109, 19)], "S21", [MAIN, MAIN], ["SSw3:N", "SSw5:N", "SSw7:N", "SSw9:N"], ["S4R", "S4LB"])
		self.routes["SRtS20S11"] = Route(self.screen, block, "SRtS20S11", "S20", [(83, 13), (84, 13), (85, 13), (86, 13), (87, 13), (88, 12), (89, 11),
																				(90, 11), (91, 11), (92, 11), (93, 11), (94, 11), (95, 11), (96, 11), (97, 11), (98, 11), (99, 11),
																				(100, 10), (101, 9), (102, 8), (103, 7), (104, 7), (105, 7)], "S11", [DIVERGING, DIVERGING], ["SSw3:N", "SSw5:R", "SSw11:N"], ["S4R", "S12LA"])
		self.routes["SRtS20H30"] = Route(self.screen, block, "SRtS20H30", "S20", [(83, 13), (84, 13), (85, 13), (86, 13), (87, 13), (88, 12), (89, 11),
																				(90, 11), (91, 11), (92, 11), (93, 11), (94, 11), (95, 11), (96, 11), (97, 11), (98, 11), (99, 11),
																				(100, 11), (101, 11), (102, 11), (103, 10), (104, 9), (105, 9)], "H30", [RESTRICTING, RESTRICTING], ["SSw3:N", "SSw5:R", "SSw11:R", "SSw13:R"], ["S4R", "S12LB"])
		self.routes["SRtS20H10"] = Route(self.screen, block, "SRtS20H10", "S20", [(83, 13), (84, 13), (85, 13), (86, 13), (87, 13), (88, 12), (89, 11),
																				(90, 11), (91, 11), (92, 11), (93, 11), (94, 11), (95, 11), (96, 11), (97, 11), (98, 11), (99, 11),
																				(100, 11), (101, 11), (102, 11), (103, 11), (104, 11), (105, 11)], "H10", [RESTRICTING, DIVERGING], ["SSw3:N", "SSw5:R", "SSw11:R", "SSw13:N"], ["S4R", "S12LC"])
		self.routes["SRtS20H20"] = Route(self.screen, block, "SRtS20H20", "S20", [(83, 13), (84, 13), (85, 13), (86, 13), (87, 13), (88, 13), (89, 13),
																				(90, 13), (91, 13), (92, 13), (93, 13), (94, 13), (95, 13), (96, 13), (97, 13), (98, 13), (99, 13),
																				(100, 13), (101, 13), (102, 13), (103, 13), (104, 13), (105, 13)], "H20", [DIVERGING, RESTRICTING], ["SSw3:N", "SSw5:N", "SSw7:N", "SSw9:R"], ["S4R", "S4LA"])
		self.routes["SRtS20P32"] = Route(self.screen, block, "SRtS20P32", "S20", [(83, 13), (84, 13), (85, 13), (86, 13), (87, 13), (88, 13), (89, 13),
																				(90, 13), (91, 13), (92, 13), (93, 13), (94, 13), (95, 13), (96, 13), (97, 13), (98, 13), (99, 13),
																				(100, 14), (101, 15), (102, 16), (103, 17), (104, 18), (105, 19), (106, 20), (107, 21), (108, 21), (109, 21)], "P32", [DIVERGING, DIVERGING], ["SSw3:N", "SSw5:N", "SSw7:R"], ["S4R", "S4LC"])

		block = self.blocks["SOSHF"]
		self.routes["SRtF10F11"] = Route(self.screen, block, "SRtF10F11", "F10", [(87, 9), (88, 9), (89, 10), (90, 11), (91, 12), (92, 13), (93, 14), (94, 15), (95, 15)], "F11", [RESTRICTING, RESTRICTING], [], ["S8R", "S8L"])

		self.signals["S12R"].AddPossibleRoutes("SOSW", ["SRtS10S11", "SRtS10H30", "SRtS10H10", "SRtS10H20", "SRtS10S21", "SRtS10P32"])
		self.signals["S4R"].AddPossibleRoutes("SOSE",  ["SRtS20S11", "SRtS20H30", "SRtS20H10", "SRtS20H20", "SRtS20S21", "SRtS20P32"])
		self.signals["S12LA"].AddPossibleRoutes("SOSW", ["SRtS10S11"])
		self.signals["S12LA"].AddPossibleRoutes("SOSE", ["SRtS20S11"])
		self.signals["S12LB"].AddPossibleRoutes("SOSW", ["SRtS10H30"])
		self.signals["S12LB"].AddPossibleRoutes("SOSE", ["SRtS20H30"])
		self.signals["S12LC"].AddPossibleRoutes("SOSW", ["SRtS10H10"])
		self.signals["S12LC"].AddPossibleRoutes("SOSE", ["SRtS20H10"])
		self.signals["S4LA"].AddPossibleRoutes("SOSW", ["SRtS10H20"])
		self.signals["S4LA"].AddPossibleRoutes("SOSE", ["SRtS20H20"])
		self.signals["S4LB"].AddPossibleRoutes("SOSW", ["SRtS10S21"])
		self.signals["S4LB"].AddPossibleRoutes("SOSE", ["SRtS20S21"])
		self.signals["S4LC"].AddPossibleRoutes("SOSW", ["SRtS10P32"])
		self.signals["S4LC"].AddPossibleRoutes("SOSE", ["SRtS20P32"])
		self.signals["S8R"].AddPossibleRoutes("SOSHF", ["SRtF10F11"])
		self.signals["S8L"].AddPossibleRoutes("SOSHF", ["SRtF10F11"])

		self.osSignals["SOSW"] = ["S12LA", "S12LB", "S12LC", "S12R", "S4LA", "S4LB", "S4LC", "S4R", "S8L", "S8R"]
		self.osSignals["SOSE"] = ["S12LA", "S12LB", "S12LC", "S12R", "S4LA", "S4LB", "S4LC", "S4R", "S8L", "S8R"]
		self.osSignals["SOSHF"] = ["S12LA", "S12LB", "S12LC", "S12R", "S4LA", "S4LB", "S4LC", "S4R", "S8L", "S8R"]

		block = self.blocks["SOSHJW"]
		self.routes["SRtH10H11"] = Route(self.screen, block, "SRtH10H11", "H11", [(114, 11), (115, 11), (116, 11), (117, 11), (118, 11), (119, 11), (120, 11), (121, 11), (122, 11)], "H10", [RESTRICTING, MAIN], ["SSw19:N"], ["S20L", "S20R"])

		block = self.blocks["SOSHJM"]
		self.routes["SRtH20H11"] = Route(self.screen, block, "SRtH20H11", "H20", [(114, 13), (115, 13), (116, 13), (117, 13), (118, 13), (119, 13), (120, 12), (121, 11), (122, 11)], "H11", [RESTRICTING, RESTRICTING], ["SSw15:N", "SSw17:N", "SSw19:R"], ["S18R", "S20L"])
		self.routes["SRtH20H21"] = Route(self.screen, block, "SRtH20H21", "H20", [(114, 13), (115, 13), (116, 13), (117, 13), (118, 13), (119, 13), (120, 13), (121, 13), (122, 13)], "H21", [MAIN, RESTRICTING], ["SSw15:N", "SSw17:N", "SSw19:N"], ["S18R", "S18LA"])
		self.routes["SRtH20H40"] = Route(self.screen, block, "SRtH20H40", "H20", [(114, 13), (115, 13), (116, 13), (117, 13), (118, 13), (119, 14), (120, 15), (121, 15), (122, 15)], "H40", [DIVERGING, RESTRICTING], ["SSw15:N", "SSw17:R"], ["S18R", "S18LB"])

		block = self.blocks["SOSHJE"]
		self.routes["SRtP42H11"] = Route(self.screen, block, "SRtP42H11", "P42", [(114, 15), (115, 15), (116, 14), (117, 13), (118, 13), (119, 13), (120, 12), (121, 11), (122, 11)], "H11", [RESTRICTING, DIVERGING], ["SSw15:R", "SSw17:N", "SSw19:R"], ["S16R", "S20L"])
		self.routes["SRtP42H21"] = Route(self.screen, block, "SRtP42H21", "P42", [(114, 15), (115, 15), (116, 14), (117, 13), (118, 13), (119, 13), (120, 13), (121, 13), (122, 13)], "H21", [RESTRICTING, DIVERGING], ["SSw15:R", "SSw17:N", "SSw19:N"], ["S16R", "S18LA"])
		self.routes["SRtP42H40"] = Route(self.screen, block, "SRtP42H40", "P42", [(114, 15), (115, 15), (116, 14), (117, 13), (118, 13), (119, 14), (120, 15), (121, 15), (122, 15)], "H40", [RESTRICTING, RESTRICTING], ["SSw15:R", "SSw17:R"], ["S16R", "S18LB"])
		self.routes["SRtP42N25"] = Route(self.screen, block, "SRtP42N25", "P42", [(114, 15), (115, 15), (116, 15), (117, 15), (118, 16), (119, 17), (120, 17)], "N25", [MAIN, MAIN], ["SSw15:N"], ["S16R", "S16L"])

		self.signals["S20R"].AddPossibleRoutes("SOSHJW", ["SRtH10H11"])
		self.signals["S18R"].AddPossibleRoutes("SOSHJM", ["SRtH20H11", "SRtH20H21", "SRtH20H40"])
		self.signals["S16R"].AddPossibleRoutes("SOSHJE", ["SRtP42H11", "SRtP42H21", "SRtP42H40", "SRtP42N25"])
		self.signals["S20L"].AddPossibleRoutes("SOSHJW", ["SRtH10H11"])
		self.signals["S20L"].AddPossibleRoutes("SOSHJM", ["SRtH20H11"])
		self.signals["S20L"].AddPossibleRoutes("SOSHJE", ["SRtP42H11"])
		self.signals["S18LA"].AddPossibleRoutes("SOSHJM", ["SRtH20H21"])
		self.signals["S18LA"].AddPossibleRoutes("SOSHJE", ["SRtP42H21"])
		self.signals["S18LB"].AddPossibleRoutes("SOSHJM", ["SRtH20H40"])
		self.signals["S18LB"].AddPossibleRoutes("SOSHJE", ["SRtP42H40"])
		self.signals["S16L"].AddPossibleRoutes("SOSHJE", ["SRtP42N25"])

		self.osSignals["SOSHJW"] = ["S20R", "S20L"]
		self.osSignals["SOSHJM"] = ["S18R", "S20L", "S18LA", "S18LB"]
		self.osSignals["SOSHJE"] = ["S16R", "S20L", "S18LA", "S18LB", "S16L"]

		p = OSProxy(self, "SOSE")
		self.osProxies["SOSE"] = p
		p.AddRoute(self.routes["SRtS20S21"])
		p.AddRoute(self.routes["SRtS20S11"])
		p.AddRoute(self.routes["SRtS20H30"])
		p.AddRoute(self.routes["SRtS20H10"])
		p.AddRoute(self.routes["SRtS20H20"])
		p.AddRoute(self.routes["SRtS20P32"])
		p.AddRoute(self.routes["SRtS10S21"])
		p.AddRoute(self.routes["SRtS10H20"])
		p.AddRoute(self.routes["SRtS10P32"])

		p = OSProxy(self, "SOSW")
		self.osProxies["SOSW"] = p
		p.AddRoute(self.routes["SRtS10S21"])
		p.AddRoute(self.routes["SRtS10S11"])
		p.AddRoute(self.routes["SRtS10H30"])
		p.AddRoute(self.routes["SRtS10H10"])
		p.AddRoute(self.routes["SRtS10H20"])
		p.AddRoute(self.routes["SRtS10P32"])
		p.AddRoute(self.routes["SRtS20S11"])
		p.AddRoute(self.routes["SRtS20H30"])
		p.AddRoute(self.routes["SRtS20H10"])
		
		p = OSProxy(self, "SOSHJE")
		self.osProxies["SOSHJE"] = p
		p.AddRoute(self.routes["SRtP42H11"])
		p.AddRoute(self.routes["SRtP42H21"])
		p.AddRoute(self.routes["SRtP42H40"])
		p.AddRoute(self.routes["SRtP42N25"])
		
		p = OSProxy(self, "SOSHJM")
		self.osProxies["SOSHJM"] = p
		p.AddRoute(self.routes["SRtH20H11"])
		p.AddRoute(self.routes["SRtH20H21"])
		p.AddRoute(self.routes["SRtH20H40"])
		p.AddRoute(self.routes["SRtP42H21"])
		p.AddRoute(self.routes["SRtP42H40"])
		p.AddRoute(self.routes["SRtP42H11"])
		
		p = OSProxy(self, "SOSHJW")
		self.osProxies["SOSHJW"] = p
		p.AddRoute(self.routes["SRtH10H11"])
		p.AddRoute(self.routes["SRtH20H11"])
		p.AddRoute(self.routes["SRtP42H11"])
		
		self.blocks["SOSHF"].SetRoute(self.routes["SRtF10F11"])

		return self.signals, self.blockSigs, self.osSignals, self.routes, self.osProxies

	def DefineHandSwitches(self):
		self.handswitches = {}

		hs = HandSwitch(self, self.screen, self.frame, self.blocks["S10"], "SSw1.hand", (77, 10), self.misctiles["handdown"])
		self.blocks["S10"].AddHandSwitch(hs)
		self.handswitches["SSw1.hand"] = hs

		return self.handswitches

		
