import wx
import wx.lib.newevent
from wx.lib.gizmos.ledctrl import LEDNumberCtrl

import os
from version import version

from dispatcher.mainframe import MainFrame, ScreenDiagram, BTNDIM
from dispatcher.bitmaps import BitMaps
from dispatcher.trackdiagram import TrackDiagram

from dispatcher.breaker import BreakerDisplay
from dispatcher.nodestatus import NodeStatusDisplay

from cliffdisplay.districts.yard import Yard
from cliffdisplay.districts.hyde import Hyde
from cliffdisplay.districts.latham import Latham
from cliffdisplay.districts.dell import Dell
from cliffdisplay.districts.shore import Shore
from cliffdisplay.districts.krulish import Krulish
from cliffdisplay.districts.nassau import Nassau
from cliffdisplay.districts.bank import Bank
from cliffdisplay.districts.cliveden import Cliveden
from cliffdisplay.districts.cliff import Cliff
from cliffdisplay.districts.port import Port

cliff = "cliff"
c13control = "c13control"


class NassauTrack:
	def __init__(self, name, ebsig, bmp, line):
		self.name = name
		self.ebsig = ebsig
		self.line = line
		self.train = None
		self.east = None
		self.loco = None
		self.signal = bmp

	def SetTrain(self, trid, east):
		self.train = trid
		self.east = east

	def SetLoco(self, lid):
		if lid is None:
			self.loco = None
		else:
			self.loco = str(lid)

	def SetSignal(self, sig):
		self.signal = sig

	def draw(self, dc):
		dc.SetTextForeground(wx.Colour(255, 255, 255))
		xStart = 1540
		dc.DrawText(self.name+":",  xStart, self.line)
		if self.train is None and self.loco is None:
			trloco = ""
		else:
			trloco = "" if self.train is None else self.train
			trloco += "/"
			trloco += "??" if self.loco is None else self.loco
			if self.east is not None:
				dc.DrawBitmap(self.east, xStart + 60, self.line)

		dc.SetTextForeground(wx.Colour(255, 255, 0))
		dc.DrawText(trloco, xStart + 78, self.line)

		dc.DrawBitmap(self.signal, xStart + 200, self.line)

		dc.SetTextForeground(wx.Colour(255, 255, 255))
		dc.DrawText(self.ebsig, xStart + 225, self.line)


class CliffFrame(MainFrame):
	def __init__(self, settings):
		MainFrame.__init__(self, settings)

		self.settings.dispatcher.dispatch = False
		self.SetupScreen()
		self.districtMap = {
			"Yard": [Yard, cliff],
			"Latham": [Latham, cliff],
			"Dell": [Dell, cliff],
			"Shore": [Shore, cliff],
			"Krulish": [Krulish, cliff],
			"Nassau": [Nassau, cliff],
			"Bank": [Bank, cliff],
			"Cliveden": [Cliveden, cliff],
			"Cliff": [Cliff, cliff],
			"Hyde": [Hyde, cliff],
			"Port": [Port, cliff]
		}
		wx.CallAfter(self.CliffInitialize)

		startLine = 140
		self.nassauTracks = {
			"W11": NassauTrack("W11", "N28R",  self.bitmaps.misc.indicatorr, startLine),
			"N32": NassauTrack("N32", "N26RA", self.bitmaps.misc.indicatorr, startLine + 30),
			"N31": NassauTrack("N31", "N26RB", self.bitmaps.misc.indicatorr, startLine + 60),
			"N12": NassauTrack("N12", "N26RC", self.bitmaps.misc.indicatorr, startLine + 90),
			"N22": NassauTrack("N22", "N24RA", self.bitmaps.misc.indicatorr, startLine + 120),
			"N41": NassauTrack("N41", "N24RB", self.bitmaps.misc.indicatorr, startLine + 150),
			"N42": NassauTrack("N42", "N24RC", self.bitmaps.misc.indicatorr, startLine + 180),
			"W20": NassauTrack("W20", "N24RD", self.bitmaps.misc.indicatorr, startLine + 210)
		}

		self.nassauTracksBySignal = {
			"N28R":  self.nassauTracks["W11"],
			"N26RA": self.nassauTracks["N32"],
			"N26RB": self.nassauTracks["N31"],
			"N26RC": self.nassauTracks["N12"],
			"N24RA": self.nassauTracks["N22"],
			"N24RB": self.nassauTracks["N41"],
			"N24RC": self.nassauTracks["N42"],
			"N24RD": self.nassauTracks["W20"]
		}

		self.trackRoutedToBank = {
			"B10": None,
			"B20": None
		}

	def CliffInitialize(self):
		self.Initialize(self.districtMap)

		bmpHilite = self.misctiles["hilite"]
		bmpOOS = self.misctiles["oos"]
		for p in self.panels.values():
			p.SetBmps(bmpHilite, bmpOOS)

	def DrawCustom(self):
		self.panels[self.diagrams[cliff].screen].DrawCustom()

	def drawCustom(self, dc):
		dc.SetTextBackground(wx.Colour(0, 0, 0))
		dc.SetFont(wx.Font(wx.Font(12, wx.FONTFAMILY_ROMAN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, faceName="Arial")))
		for nt in self.nassauTracks.values():
			nt.draw(dc)

	def SetupScreen(self):
		self.title = "Cliff Monitor"
		self.title += " v2 (" + version["date"] + ") "
		self.Bind(wx.EVT_CLOSE, self.OnClose)
		self.bitmaps = BitMaps(os.path.join(os.getcwd(), "images", "bitmaps"))
		self.bmpw, self.bmph = self.bitmaps.diagrams.Cliff.GetSize()
		self.diagrams = {
			cliff: ScreenDiagram(cliff, self.bitmaps.diagrams.Cliff, 0)
		}
		topSpace = 120

		ht = None  # diagram height.  None => use bitmap size.  use a number < 800 to trim bottom off of diagram bitmaps
		self.diagramWidth = 1904

		dp = TrackDiagram(self, [self.diagrams[cliff]], self.settings, ht)
		dp.SetPosition((8, 120))
		_, diagramh = dp.GetSize()
		self.panels = {self.diagrams[cliff].screen: dp}
		totalw = self.diagramWidth
		self.centerOffset = 0

		self.ToasterSetup()

		voffset = topSpace + diagramh + 10
		self.widgetMap = {cliff: []}
		self.DefineControlDisplay(voffset)

		self.currentScreen = None
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

		self.bActiveTrains = wx.Button(self, wx.ID_ANY, "Active Trains", pos=(self.centerOffset + 250, 45), size=BTNDIM)
		self.Bind(wx.EVT_BUTTON, self.OnBActiveTrains, self.bActiveTrains)
		self.bActiveTrains.SetToolTip("Show the active train window")
		self.bActiveTrains.Enable(False)

		self.bLostTrains = wx.Button(self, wx.ID_ANY, "Lost Trains", pos=(self.centerOffset + 250, 75), size=BTNDIM)
		self.Bind(wx.EVT_BUTTON, self.OnBLostTrains, self.bLostTrains)
		self.bLostTrains.SetToolTip("Recover lost trains")
		self.bLostTrains.Enable(False)

		if not self.IsDispatcherOrSatellite():
			self.bEditTrains.Hide()
			self.bLostTrains.Hide()

		self.scrn = wx.TextCtrl(self, wx.ID_ANY, "", size=(80, -1), pos=(self.centerOffset + 1610, 25),
								style=wx.TE_READONLY)
		self.xpos = wx.TextCtrl(self, wx.ID_ANY, "", size=(60, -1), pos=(self.centerOffset + 1710, 25),
								style=wx.TE_READONLY)
		self.ypos = wx.TextCtrl(self, wx.ID_ANY, "", size=(60, -1), pos=(self.centerOffset + 1790, 25),
								style=wx.TE_READONLY)

		self.bResetScreen = wx.Button(self, wx.ID_ANY, "Reset Screen", pos=(int(totalw / 2 + 100), 80), size=BTNDIM)
		self.Bind(wx.EVT_BUTTON, self.OnResetScreen, self.bResetScreen)
		self.bResetScreen.SetToolTip("Move the screen back to its home location")

		self.breakerDisplay = BreakerDisplay(self, pos=(int(totalw / 2 - 400 / 2), 30), size=(400, 40))
		self.nodeStatusDisplay = NodeStatusDisplay(self, pos=(int(totalw / 2 - 400 / 2), 1), size=(400, 29))

		self.timeDisplay = LEDNumberCtrl(self, wx.ID_ANY, pos=(self.centerOffset + 480, 10), size=(150, 50))
		self.timeDisplay.SetBackgroundColour(wx.Colour(0, 0, 0))

		self.bEvents = wx.Button(self, wx.ID_ANY, "Events Log", pos=(self.centerOffset + 1400, 25), size=BTNDIM)
		self.Bind(wx.EVT_BUTTON, self.OnBEventsLog, self.bEvents)

		self.bAdvice = wx.Button(self, wx.ID_ANY, "Advice Log", pos=(self.centerOffset + 1400, 65), size=BTNDIM)
		self.Bind(wx.EVT_BUTTON, self.OnBAdviceLog, self.bAdvice)

		self.totalw = totalw
		self.totalh = diagramh + 280  # 1080 if diagram is full 800 height
		self.centerw = int(self.totalw / 2)
		self.centerh = int(self.totalh / 2)
		self.showSplash = True
		self.ResetScreen()
		self.Bind(wx.EVT_CHAR_HOOK, self.OnKeyDown)

	def DefineControlDisplay(self, voffset):
		f = wx.Font(16, wx.FONTFAMILY_ROMAN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, faceName="Arial")

		self.stCliffControl = wx.StaticText(self, wx.ID_ANY, "CLIFF: Dispatch All", pos=(800, voffset + 10))
		self.stCliffControl.SetFont(f)
		self.widgetMap[cliff].append([self.stCliffControl, 1])

	def UpdateControlDisplay(self, name, value):
		if name == "cliff":
			self.cliffControl = value
			if value == 0:
				self.stCliffControl.SetLabel("CLIFF: Local")
			elif value == 1:
				self.stCliffControl.SetLabel("CLIFF: Dispatch Bank/Cliveden")
			elif value == 2:
				self.stCliffControl.SetLabel("CLIFF: Dispatch All")

	def DoCmdTrain(self, parms):
		MainFrame.DoCmdTrain(self, parms)
		try:
			iname = parms[0]["iname"]
		except KeyError:
			iname = None

		try:
			rname = parms[0]["rname"]
		except KeyError:
			rname = None

		try:
			blocks = parms[0]["blocks"]
		except KeyError:
			blocks = []

		try:
			east = parms[0]["east"]
		except KeyError:
			east = None

		try:
			loco = parms[0]["loco"]
		except KeyError:
			loco = None

		tr = self.trains[iname]
		name = tr.Name()
		delBlocks = tr.GetDelBlocks()

		for nm, trk in self.nassauTracks.items():
			if nm in blocks:
				trk.SetTrain(name, self.bitmaps.misc.arroweast if east else self.bitmaps.misc.arrowwest)
				trk.SetLoco(loco)
				break

			if nm in delBlocks:
				trk.SetTrain(None, None)
				trk.SetLoco(None)
				break

		self.DrawCustom()

	def DoCmdSet1Route(self, bn, route):
		if bn not in ["NEOSE", "NEOSW", "NEOSRH"]:
			MainFrame.DoCmdSet1Route(self, bn, route)
			return

		if route is None:
			if bn == "NEOSE":
				self.trackRoutedToBank["B20"] = None
			elif bn == "NEOSW":
				self.trackRoutedToBank["B10"] = None
		else:
			ends = [route[-6:-3], route[-3:]]
			if "B10" in ends:
				self.trackRoutedToBank["B10"] = ends[0] if ends[1] == "B10" else ends[1]

			elif "B20" in ends:
				self.trackRoutedToBank["B20"] = ends[0] if ends[1] == "B20" else ends[1]

	def DoCmdShowAspect(self, parms):
		MainFrame.DoCmdShowAspect(self, parms)
		changes = False
		for p in parms:
			try:
				sigName = p["signal"]
			except KeyError:
				sigName = None
			try:
				aspect = p["aspect"]
			except KeyError:
				aspect = 0

			if sigName is None:
				continue

			if sigName not in self.nassauTracksBySignal.keys():
				continue

			nassauTrack = self.nassauTracksBySignal[sigName]

			if nassauTrack.name in self.trackRoutedToBank.values():
				if aspect == 0:
					bmp = self.bitmaps.misc.indicatorr
				else:
					bmp = self.bitmaps.misc.indicatorg
			else:
				bmp = self.bitmaps.misc.indicatorr

			nassauTrack.SetSignal(bmp)
			changes = True

		if changes:
			self.DrawCustom()
