import wx
import wx.lib.newevent
from wx.lib.gizmos.ledctrl import LEDNumberCtrl

import os
from dispatcher.mainframe import MainFrame, ScreenDiagram, BTNDIM
from dispatcher.bitmaps import BitMaps
from dispatcher.trackdiagram import TrackDiagram

from dispatcher.breaker import BreakerDisplay
from dispatcher.districts.yard import Yard
from dispatcher.districts.hyde import Hyde
from dispatcher.districts.latham import Latham
from dispatcher.districts.dell import Dell
from dispatcher.districts.shore import Shore
from dispatcher.districts.krulish import Krulish
from dispatcher.districts.nassau import Nassau
from dispatcher.districts.bank import Bank
from dispatcher.districts.cliveden import Cliveden
from dispatcher.districts.cliff import Cliff
from dispatcher.districts.port import Port

from dispatcher.constants import HyYdPt, LaKr, NaCl, screensList

from ctcmanager.ctcmanager import CTCManager
import logging

class PSRYFrame(MainFrame):
	def __init__(self, settings):
		MainFrame.__init__(self, settings)
		self.SetupScreen()
		self.districtMap = {
			"Yard": [Yard, HyYdPt],
			"Latham": [Latham, LaKr],
			"Dell": [Dell, LaKr],
			"Shore": [Shore, LaKr],
			"Krulish": [Krulish, LaKr],
			"Nassau": [Nassau, NaCl],
			"Bank": [Bank, NaCl],
			"Cliveden": [Cliveden, NaCl],
			"Cliff": [Cliff, NaCl],
			"Hyde": [Hyde, HyYdPt],
			"Port": [Port, HyYdPt]
		}
		wx.CallAfter(self.PSRYInitialize)

	def PSRYInitialize(self):
		self.Initialize(self.districtMap)

		bmpHilite = self.misctiles["hilite"]
		for p in self.panels.values():
			p.SetHiliteBmp(bmpHilite)

	def drawCustom(self, dc):
		pass

	def SetupScreen(self):
		self.title = "PSRY Dispatcher" if self.IsDispatcher() else "Satellite" if self.IsSatellite() else "PSRY Monitor"
		self.Bind(wx.EVT_CLOSE, self.OnClose)
		self.bitmaps = BitMaps(os.path.join(os.getcwd(), "images", "bitmaps"))
		singlePage = self.settings.display.pages == 1
		self.bmpw, self.bmph = self.bitmaps.diagrams.HydeYardPort.GetSize()
		self.diagrams = {
			HyYdPt: ScreenDiagram(HyYdPt, self.bitmaps.diagrams.HydeYardPort, 0),
			LaKr: ScreenDiagram(LaKr, self.bitmaps.diagrams.LathamKrulish, self.bmpw if singlePage else 0),
			NaCl: ScreenDiagram(NaCl, self.bitmaps.diagrams.NassauCliff, self.bmpw * 2 if singlePage else 0)
		}
		topSpace = 120

		ht = None  # diagram height.  None => use bitmap size.  use a number < 800 to trim bottom off of diagram bitmaps
		self.diagramWidth = 2544

		if self.settings.display.pages == 1:  # set up a single ultra-wide display accross 3 monitors
			dp = TrackDiagram(self, [self.diagrams[sn] for sn in screensList], ht)
			dp.SetPosition((0, 120))
			_, diagramh = dp.GetSize()
			self.panels = {self.diagrams[sn].screen: dp for sn in screensList}  # all 3 screens just point to the same diagram
			totalw = self.diagramWidth * 3
			self.centerOffset = self.diagramWidth

		else:  # set up three separate screens for a single monitor
			self.panels = {}
			diagramh = 0
			for d in [self.diagrams[sn] for sn in screensList]:
				dp = TrackDiagram(self, [d], ht)
				_, diagramh = dp.GetSize()
				dp.Hide()
				dp.SetPosition((0, 120))
				self.panels[d.screen] = dp

			# add buttons to switch from screen to screen
			voffset = topSpace + diagramh + 20
			b = wx.Button(self, wx.ID_ANY, "Hyde/Yard/Port", pos=(500, voffset), size=(200, 50))
			self.Bind(wx.EVT_BUTTON, lambda event: self.SwapToScreen(HyYdPt), b)
			self.bScreenHyYdPt = b
			b = wx.Button(self, wx.ID_ANY, "Latham/Dell/Shore/Krulish", pos=(1145, voffset), size=(200, 50))
			self.Bind(wx.EVT_BUTTON, lambda event: self.SwapToScreen(LaKr), b)
			self.bScreenLaKr = b
			b = wx.Button(self, wx.ID_ANY, "Nassau/Bank/Cliff", pos=(1790, voffset), size=(200, 50))
			self.Bind(wx.EVT_BUTTON, lambda event: self.SwapToScreen(NaCl), b)
			self.bScreenNaCl = b
			totalw = self.diagramWidth
			self.centerOffset = 0

		if self.IsDispatcherOrSatellite():
			self.CTCManager = CTCManager(self, self.settings, self.diagrams)
			for screen, fg, pos, bmp in self.CTCManager.GetBitmaps():
				offset = self.diagrams[screen].offset
				self.panels[screen].DrawCTCBitmap(fg, pos[0], pos[1], offset, bmp)
			for label, font, screen, lblx, lbly in self.CTCManager.GetLabels():
				offset = self.diagrams[screen].offset
				self.panels[screen].DrawCTCLabel(lblx, lbly, offset, font, label)

		self.ToasterSetup()

		if self.settings.display.showcameras:
			self.DrawCameras()

		voffset = topSpace + diagramh + 10
		self.widgetMap = {HyYdPt: [], LaKr: [], NaCl: []}
		self.DefineWidgets(voffset)
		self.DefineControlDisplay(voffset)

		self.currentScreen = None
		if self.settings.display.pages == 3:
			self.SwapToScreen(LaKr)
		else:
			self.PlaceWidgets()

		self.bSubscribe = wx.Button(self, wx.ID_ANY, "Connect", pos=(int(totalw / 2 - 185), 80), size=BTNDIM)
		self.Bind(wx.EVT_BUTTON, self.OnSubscribe, self.bSubscribe)
		self.bSubscribe.SetToolTip("Connect to/Disconnect from the Railroad server")

		self.bRefresh = wx.Button(self, wx.ID_ANY, "Refresh", pos=(self.centerOffset + 50, 15), size=BTNDIM)
		self.Bind(wx.EVT_BUTTON, self.OnRefresh, self.bRefresh)
		self.bRefresh.SetToolTip("Refresh all railroad information from the railroad server")
		self.bRefresh.Enable(False)

		self.bThrottle = wx.Button(self, wx.ID_ANY, "Throttle", pos=(self.centerOffset + 150, 15), size=BTNDIM)
		self.Bind(wx.EVT_BUTTON, self.OnThrottle, self.bThrottle)
		self.bThrottle.SetToolTip("Open up a new throttle window - multiple allowed")

		self.bEditTrains = wx.Button(self, wx.ID_ANY, "Edit Data", pos=(self.centerOffset + 150, 45), size=BTNDIM)
		self.Bind(wx.EVT_BUTTON, self.OnEditTrains, self.bEditTrains)
		self.bEditTrains.SetToolTip("Open up the train editor window")

		self.bCheckTrains = wx.Button(self, wx.ID_ANY, "Check Trains", pos=(self.centerOffset + 250, 15), size=BTNDIM)
		self.Bind(wx.EVT_BUTTON, self.OnBCheckTrains, self.bCheckTrains)
		self.bCheckTrains.SetToolTip("Check trains for continuity and for locomotive number uniqueness")
		self.bCheckTrains.Enable(False)

		self.bLoadTrains = wx.Button(self, wx.ID_ANY, "Load Train IDs", pos=(self.centerOffset + 1950, 15), size=BTNDIM)
		self.bLoadTrains.Enable(False)
		self.Bind(wx.EVT_BUTTON, self.OnBLoadTrains, self.bLoadTrains)
		self.bLoadTrains.SetToolTip("Load train IDs from a file")

		self.bSaveTrains = wx.Button(self, wx.ID_ANY, "Save Train IDs", pos=(self.centerOffset + 1950, 45), size=BTNDIM)
		self.bSaveTrains.Enable(False)
		self.Bind(wx.EVT_BUTTON, self.OnBSaveTrains, self.bSaveTrains)
		self.bSaveTrains.SetToolTip("Save train IDs to a file")

		self.bClearTrains = wx.Button(self, wx.ID_ANY, "Clear Train IDs", pos=(self.centerOffset + 1950, 75), size=BTNDIM)
		self.bClearTrains.Enable(False)
		self.Bind(wx.EVT_BUTTON, self.OnBClearTrains, self.bClearTrains)
		self.bClearTrains.SetToolTip("Repolace train IDs from active trains with temporary names")

		self.bLoadLocos = wx.Button(self, wx.ID_ANY, "Load Loco #s", pos=(self.centerOffset + 2050, 15), size=BTNDIM)
		self.Bind(wx.EVT_BUTTON, self.OnBLoadLocos, self.bLoadLocos)
		self.bLoadLocos.Enable(False)
		self.bLoadLocos.SetToolTip("Load locomotive IDs from a file")

		self.bSaveLocos = wx.Button(self, wx.ID_ANY, "Save Loco #s", pos=(self.centerOffset + 2050, 45), size=BTNDIM)
		self.Bind(wx.EVT_BUTTON, self.OnBSaveLocos, self.bSaveLocos)
		self.bSaveLocos.Enable(False)
		self.bSaveLocos.SetToolTip("Save locomotive IDs to a file")

		self.bActiveTrains = wx.Button(self, wx.ID_ANY, "Active Trains", pos=(self.centerOffset + 250, 45), size=BTNDIM)
		self.Bind(wx.EVT_BUTTON, self.OnBActiveTrains, self.bActiveTrains)
		self.bActiveTrains.SetToolTip("Show the active train window")
		self.bActiveTrains.Enable(False)

		self.bLostTrains = wx.Button(self, wx.ID_ANY, "Lost Trains", pos=(self.centerOffset + 250, 75), size=BTNDIM)
		self.Bind(wx.EVT_BUTTON, self.OnBLostTrains, self.bLostTrains)
		self.bLostTrains.SetToolTip("Recover lost trains")
		self.bLostTrains.Enable(False)

		if not self.IsDispatcherOrSatellite():
			self.bLoadTrains.Hide()
			self.bLoadLocos.Hide()
			self.bSaveTrains.Hide()
			self.bSaveLocos.Hide()
			self.bClearTrains.Hide()
			self.bEditTrains.Hide()
			self.bLostTrains.Hide()

		self.scrn = wx.TextCtrl(self, wx.ID_ANY, "", size=(80, -1), pos=(self.centerOffset + 2260, 25),
								style=wx.TE_READONLY)
		self.xpos = wx.TextCtrl(self, wx.ID_ANY, "", size=(60, -1), pos=(self.centerOffset + 2360, 25),
								style=wx.TE_READONLY)
		self.ypos = wx.TextCtrl(self, wx.ID_ANY, "", size=(60, -1), pos=(self.centerOffset + 2440, 25),
								style=wx.TE_READONLY)

		self.bResetScreen = wx.Button(self, wx.ID_ANY, "Reset Screen", pos=(int(totalw / 2 + 100), 80), size=BTNDIM)
		self.Bind(wx.EVT_BUTTON, self.OnResetScreen, self.bResetScreen)
		self.bResetScreen.SetToolTip("Move the screen back to its home location")

		self.breakerDisplay = BreakerDisplay(self, pos=(int(totalw / 2 - 400 / 2), 30), size=(400, 40))

		self.timeDisplay = LEDNumberCtrl(self, wx.ID_ANY, pos=(self.centerOffset + 480, 10), size=(150, 50))
		self.timeDisplay.SetBackgroundColour(wx.Colour(0, 0, 0))

		if self.IsDispatcher():
			self.DetermineClockStatus()
			self.ShowClockStatus()
			self.DisplayTimeValue()
			self.cbToD = wx.CheckBox(self, wx.ID_ANY, "Time of Day", pos=(self.centerOffset + 515, 65))
			self.cbToD.SetValue(True)
			self.Bind(wx.EVT_CHECKBOX, self.OnCBToD, self.cbToD)

			self.bStartClock = wx.Button(self, wx.ID_ANY, "Start", pos=(self.centerOffset + 485, 90), size=(60, 23))
			self.Bind(wx.EVT_BUTTON, self.OnBStartClock, self.bStartClock)
			self.bStartClock.Enable(False)

			self.bResetClock = wx.Button(self, wx.ID_ANY, "Reset", pos=(self.centerOffset + 565, 90), size=(60, 23))
			self.Bind(wx.EVT_BUTTON, self.OnBResetClock, self.bResetClock)
			self.bResetClock.Enable(False)

			self.cbOSSLocks = wx.CheckBox(self, -1, "OSS Locks", (int(totalw / 2 - 100 / 2), 75))
			self.Bind(wx.EVT_CHECKBOX, self.OnCBOSSLocks, self.cbOSSLocks)
			self.cbOSSLocks.SetValue(self.OSSLocks)
			self.cbOSSLocks.Enable(False)

			self.cbSidingsUnlocked = wx.CheckBox(self, -1, "Unlock Sidings", (int(totalw / 2 - 100 / 2), 95))
			self.Bind(wx.EVT_CHECKBOX, self.OnCBSidingsUnlocked, self.cbSidingsUnlocked)
			self.cbSidingsUnlocked.SetValue(self.sidingsUnlocked)
			self.cbSidingsUnlocked.Enable(False)

			self.cbAutoRouter = wx.CheckBox(self, wx.ID_ANY, "Auto-Router", pos=(self.centerOffset + 670, 25))
			self.Bind(wx.EVT_CHECKBOX, self.OnCBAutoRouter, self.cbAutoRouter)
			self.cbAutoRouter.Enable(False)
			self.cbATC = wx.CheckBox(self, wx.ID_ANY, "Automatic Train Control", pos=(self.centerOffset + 670, 50))
			self.Bind(wx.EVT_CHECKBOX, self.OnCBATC, self.cbATC)
			self.cbATC.Enable(False)

		if self.IsDispatcherOrSatellite():
			self.bSnapshot = wx.Button(self, wx.ID_ANY, "Snapshot", pos=(self.centerOffset + 2050, 75), size=BTNDIM)
			self.bSnapshot.Enable(False)
			self.Bind(wx.EVT_BUTTON, self.OnBSnapshot, self.bSnapshot)

			self.bPreloaded = wx.Button(self, wx.ID_ANY, "Preloaded", pos=(self.centerOffset + 2150, 15), size=BTNDIM)
			self.bPreloaded.Enable(False)
			self.Bind(wx.EVT_BUTTON, self.OnBPreloaded, self.bPreloaded)

		if self.IsDispatcherOrSatellite() or self.settings.display.showevents:
			self.bEvents = wx.Button(self, wx.ID_ANY, "Events Log", pos=(self.centerOffset + 840, 25), size=BTNDIM)
			self.Bind(wx.EVT_BUTTON, self.OnBEventsLog, self.bEvents)

		if self.IsDispatcherOrSatellite() or self.settings.display.showadvice:
			self.bAdvice = wx.Button(self, wx.ID_ANY, "Advice Log", pos=(self.centerOffset + 840, 65), size=BTNDIM)
			self.Bind(wx.EVT_BUTTON, self.OnBAdviceLog, self.bAdvice)

		self.totalw = totalw
		self.totalh = diagramh + 280  # 1080 if diagram is full 800 height
		self.centerw = int(self.totalw / 2)
		self.centerh = int(self.totalh / 2)
		self.showSplash = True
		self.ResetScreen()
		self.Bind(wx.EVT_CHAR_HOOK, self.OnKeyDown)

	def DefineControlDisplay(self, voffset):
		if self.IsDispatcher():
			return

		f = wx.Font(16, wx.FONTFAMILY_ROMAN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, faceName="Arial")

		self.stCliffControl = wx.StaticText(self, wx.ID_ANY, "CLIFF: Dispatch All", pos=(2100, voffset + 10))
		self.stCliffControl.Hide()
		self.stCliffControl.SetFont(f)
		self.widgetMap[NaCl].append([self.stCliffControl, 1])

		self.stYardControl = wx.StaticText(self, wx.ID_ANY, "YARD: Local", pos=(1550, voffset + 10))
		self.stYardControl.Hide()
		self.stYardControl.SetFont(f)
		self.widgetMap[HyYdPt].append([self.stYardControl, 1])

		self.stNassauControl = wx.StaticText(self, wx.ID_ANY, "NASSAU: Dispatch All", pos=(170, voffset + 10))
		self.stNassauControl.Hide()
		self.stNassauControl.SetFont(f)
		self.widgetMap[NaCl].append([self.stNassauControl, 1])

	def UpdateControlDisplay(self, name, value):
		if self.IsDispatcher():
			return

		if name == "yard":
			self.yardControl = value
			logging.debug("update control display, yard=%d" % value)
			if value == 0:
				self.stYardControl.SetLabel("YARD: Local")
			elif value == 1:
				self.stYardControl.SetLabel("YARD: Dispatch")

		elif name == "nassau":
			self.nassauControl = value
			if value == 0:
				self.stNassauControl.SetLabel("NASSAU: Local")
			elif value == 1:
				self.stNassauControl.SetLabel("NASSAU: Dispatch Main")
			elif value == 2:
				self.stNassauControl.SetLabel("NASSAU: Dispatch All")

		elif name == "cliff":
			self.cliffControl = value
			if value == 0:
				self.stCliffControl.SetLabel("CLIFF: Local")
			elif value == 1:
				self.stCliffControl.SetLabel("CLIFF: Dispatch Bank/Cliveden")
			elif value == 2:
				self.stCliffControl.SetLabel("CLIFF: Dispatch All")

		elif name == "osslocks":
			self.districts.EvaluateDistrictLocks(ossLocks=value == 1)
