import wx
import wx.lib.newevent
from subprocess import DEVNULL

import os
import sys
import json
import re
import logging
import time
from subprocess import Popen

from dispatcher.constants import BLOCK

from dispatcher.district import Districts, CrossingEastWestBoundary
from dispatcher.tile import loadTiles
from dispatcher.train import Train
from dispatcher.trainlist import ActiveTrainsDlg, YardBlocks, LadderBlocks
from dispatcher.losttrains import LostTrains, LostTrainsRecoveryDlg
from dispatcher.trainhistory import TrainHistory
from dispatcher.preload import PreLoadedTrains
from dispatcher.routetraindlg import RouteTrainDlg
from dispatcher.inspectdlg import InspectDlg

from dispatcher.breaker import BreakerName
from dispatcher.toaster import Toaster
from dispatcher.listdlg import ListDlg
from dispatcher.delayedrequest import DelayedRequests
from dispatcher.delayedsignal import DelayedSignals
from dispatcher.trainqueue import TrainQueue
from dispatcher.block import formatRouteDesignator
from dispatcher.node import Node

from dispatcher.constants import HyYdPt, LaKr, NaCl, EMPTY, OCCUPIED, \
		OVERSWITCH, SLIPSWITCH, turnoutstate, REPLACE, REAR
from dispatcher.listener import Listener
from dispatcher.rrserver import RRServer

from dispatcher.edittraindlg import EditTrainDlg, SortTrainBlocksDlg
from dispatcher.choicedlgs import ChooseItemDlg, ChooseBlocksDlg, ChooseSnapshotActionDlg, ChooseTrainDlg, ChooseSnapshotDlg
from traineditor.preloaded.managepreloaded import ManagePreloadedDlg

MENU_ATC_REMOVE    = 900
MENU_ATC_STOP      = 901
MENU_ATC_ADD       = 902
MENU_AR_ADD        = 903
MENU_AR_REMOVE     = 904
MENU_TRAIN_EDIT    = 910
MENU_TRAIN_ROUTE   = 911
MENU_TRAIN_SPLIT   = 912
MENU_TRAIN_MERGE   = 913
MENU_TRAIN_SWAP    = 914
MENU_TRAIN_REVERSE = 915
MENU_TRAIN_REORDER = 916
MENU_TRAIN_LOCATE  = 917
MENU_TRAIN_HILITE  = 918

(DeliveryEvent, EVT_DELIVERY) = wx.lib.newevent.NewEvent() 
(DisconnectEvent, EVT_DISCONNECT) = wx.lib.newevent.NewEvent() 

allowedCommands = [ "settrain", "renametrain", "assigntrain", "identify", "refresh", "traintimesrequest", "trainblockorder", "trainsignal", "blockdir", "deletetrain" ]
disallowedSatelliteCommands = [ "relay" ]

wildcardTrain = "train files (*.trn)|*.trn|"	 \
			"All files (*.*)|*.*"
wildcardLoco = "locomotive files (*.loco)|*.loco|"	 \
			"All files (*.*)|*.*"
			
SidingSwitches = [ "LSw11", "LSw13", "DSw9", "SSw1", "CSw3", "CSw11", "CSw15", "CSw19", "CSw21a", "CSw21b" ]

# blocks to consider valid for all routes
ValidBlocks = YardBlocks + LadderBlocks


class ScreenDiagram:
	def __init__(self, screen, bitmapName, offset):
		self.screen = screen
		self.bitmap = bitmapName
		self.offset = offset


BTNDIM = (80, 23) if sys.platform.lower() == "win32" else (100, 23)
WIDTHADJUST = 0 if sys.platform.lower() == "win32" else 56


class MainFrame(wx.Frame):
	def __init__(self, settings):
		wx.Frame.__init__(self, None, size=(900, 800), style=wx.DEFAULT_FRAME_STYLE)
		self.settings = settings

		self.title = None
		self.bitmaps = None
		self.bmpw = self.bmph = None
		self.diagrams = {}
		self.diagramWidth = 0
		self.panels = None
		self.bScreenHyYdPt = self.bScreenLaKr = self.bScreenNaCl = None
		self.centerOffset = 0
		self.widgetMap = None
		self.currentScreen = None
		self.stCliffControl = None
		self.stC13Control = None
		self.showSplash = None
		self.centerh = None
		self.centerw = None
		self.totalh = None
		self.totalw = None
		self.bAdvice = None
		self.bEvents = None
		self.timeDisplay = None
		self.breakerDisplay = None
		self.bResetScreen = None
		self.ypos = None
		self.xpos = None
		self.scrn = None
		self.bLostTrains = None
		self.bActiveTrains = None
		self.bSaveLocos = None
		self.bLoadLocos = None
		self.bClearTrains = None
		self.bSaveTrains = None
		self.bLoadTrains = None
		self.bCheckTrains = None
		self.bEditTrains = None
		self.bThrottle = None
		self.bRefresh = None
		self.bSubscribe = None
		self.bStartClock = None
		self.bResetClock = None
		self.c13Control = 0
		self.stNassauControl = None
		self.stYardControl = None
		self.bSnapshot = None
		self.bPreloaded = None
		self.initializing = True

		self.cbToD = None
		self.cbAutoRouter = None
		self.cbATC = None
		self.cbOSSLocks = None
		self.cbSidingsUnlocked = None
		self.menuTrain = None
		self.menuTrainID = None
		self.menuBlock = None

		self.events = None
		self.advice = None
		self.listener = None
		self.sessionid = None
		self.sessionName = "Name"
		self.subscribed = False
		self.ATCEnabled = False
		self.AREnabled = False
		self.pidATC	= None
		self.procATC = None
		self.OSSLocks = True
		self.sidingsUnlocked = False
		self.CTCManager = None
		self.CTCVisible = False
		
		self.shift = False
		self.shiftXOffset = 0
		self.shiftYOffset = 0
		
		self.ToD = True
		self.timeValue = self.GetToD()
		self.clockRunning = False # only applies to non-TOD clock
		self.clockStatus = 3 # default = ToD

		self.hiliteRouteTicker = 0
		self.hilitedRoute = None

		self.eventsList = []
		self.adviceList = []
		self.dlgEvents = None
		self.dlgAdvice = None
		self.routeTrainDlgs = {}
		self.dlgInspect = None

		self.locoList = []
		self.trainRoster = []
		self.trainNameMap = {}
		self.hilitedTrains = []
		self.trains = []
		self.activeTrainsDlg = ActiveTrainsDlg(self, self.trains)
		self.lostTrains = LostTrains(self)
		self.trainHistory = TrainHistory(self, self.settings)
		self.preloadedTrains = None

		self.nodes = {}

		logging.info("%s process starting" % "dispatcher" if self.IsDispatcher() else "satellite" if self.IsSatellite() else "display")

		icon = wx.Icon()
		icon.CopyFromBitmap(wx.Bitmap(os.path.join(os.getcwd(), "icons", "dispatch.ico"), wx.BITMAP_TYPE_ANY))
		self.SetIcon(icon)

		self.logCount = 6
		
		self.turnoutMap = {}
		self.buttonMap = {}
		self.signalMap = {}
		self.handswitchMap = {}

		self.yardControl = 0
		self.nassauControl = 0
		self.cliffControl = 0
		self.c13auto = self.settings.control.c13auto

		self.delayedRequests = DelayedRequests()
		self.delayedSignals = DelayedSignals()
		self.C13Queue = TrainQueue()
		self.menuFont = wx.Font(wx.Font(14, wx.FONTFAMILY_ROMAN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, faceName="Arial"))

	def OnKeyDown(self, evt):
		kcd = evt.GetKeyCode()
		if kcd == wx.WXK_PAGEUP:
			if self.settings.display.pages == 3:
				if self.currentScreen == LaKr:
					self.SwapToScreen(HyYdPt)
				elif self.currentScreen == NaCl:
					self.SwapToScreen(LaKr)
			else:
				self.shiftXOffset += self.diagramWidth
				if self.shiftXOffset > 0:
					self.shiftXOffset = 0
				self.SetPosition((self.shiftXOffset, self.shiftYOffset))
				
		elif kcd == wx.WXK_PAGEDOWN:
			if self.settings.display.pages == 3:
				if self.currentScreen == HyYdPt:
					self.SwapToScreen(LaKr)
				elif self.currentScreen == LaKr:
					self.SwapToScreen(NaCl)
			else:
				self.shiftXOffset -= self.diagramWidth
				if self.shiftXOffset < -2*self.diagramWidth:
					self.shiftXOffset = -2*self.diagramWidth
				self.SetPosition((self.shiftXOffset, self.shiftYOffset))

		elif kcd == wx.WXK_LEFT:
			self.shiftXOffset -= 10
			if self.shiftXOffset < -2*self.diagramWidth:
				self.shiftXOffset = -2*self.diagramWidth
			self.SetPosition((self.shiftXOffset, self.shiftYOffset))
				
		elif kcd == wx.WXK_RIGHT:
			self.shiftXOffset += 10
			if self.shiftXOffset > 0:
				self.shiftXOffset = 0
			self.SetPosition((self.shiftXOffset, self.shiftYOffset))
					
		elif kcd == wx.WXK_UP:
			self.shiftYOffset -= 10
			self.SetPosition((self.shiftXOffset, self.shiftYOffset))
					
		elif kcd == wx.WXK_DOWN:
			self.shiftYOffset += 10
			if self.shiftYOffset > 0:
				self.shiftYOffset = 0
			self.SetPosition((self.shiftXOffset, self.shiftYOffset))
			
		elif kcd == wx.WXK_HOME:
			self.ResetScreen()
			evt.Skip()
			
		elif kcd == wx.WXK_SHIFT:
			self.SetShift(True)
			for pnl in self.panels.values():
				pnl.SetShift(True)

		elif kcd == wx.WXK_ESCAPE and self.shift:
			self.CloseProgram()
			self.SetShift(False)
			for pnl in self.panels.values():
				pnl.SetShift(False)

		elif kcd == wx.WXK_F1:
			if self.IsDispatcherOrSatellite():
				if not self.subscribed:
					self.PopupEvent("Not connected to server")
				else:
					if self.dlgInspect is None:
						self.dlgInspect = InspectDlg(self, self.CloseInspect, self.settings)
						self.dlgInspect.Show()
					else:
						self.dlgInspect.Raise()

		elif kcd == wx.WXK_F2:
			if self.IsDispatcherOrSatellite():
				if self.CTCManager is not None:
					self.CTCVisible = not self.CTCVisible
					for dp in self.panels.values():
						dp.ShowCTC(self.CTCVisible)
					self.CTCManager.SetVisible(self.CTCVisible)

		elif kcd == wx.WXK_F3:
			if self.IsDispatcherOrSatellite():
				if not self.subscribed:
					self.PopupEvent("Not connected to server")
				else:
					dlg = wx.MultiChoiceDialog(self,
							"Items to reload",
							"Reload Data", ["trains", "preloaded trains", "locomotives", "engineers"])

					rc = dlg.ShowModal()
					if rc == wx.ID_OK:
						selections = dlg.GetSelections()
					else:
						selections = []

					dlg.Destroy()
					if rc != wx.ID_OK:
						return

					dataFlags = [True if i in selections else False for i in range(4)]
					if dataFlags[0] or dataFlags[2] or dataFlags[3]:
						self.RetrieveData(report=True, trains=dataFlags[0], locos=dataFlags[2], engineers=dataFlags[3])

					if dataFlags[1]:
						self.preloadedTrains.Reload()
						self.PopupEvent("Preloaded trains reloaded")

		else:
			#self.PopupEvent("Key Code: %d" % kcd)
			evt.Skip()

	def SendDebugFlags(self):
		if not self.subscribed:
			return

		msg = {"debugflags":
					{
						"showaspectcalculation": 1 if self.settings.debug.showaspectcalculation else 0,
						"blockoccupancy": 1 if self.settings.debug.blockoccupancy else 0,
						"identifytrain": 1 if self.settings.debug.identifytrain else 0
					}
		}
		logging.debug("sending message: %s" % str(msg))
		self.Request(msg)

	def CloseInspect(self):
		self.dlgInspect.Destroy()
		self.dlgInspect = None

	def OnKeyUp(self, evt):
		kcd = evt.GetKeyCode()
		if kcd == wx.WXK_SHIFT:
			self.SetShift(False)
			for pnl in self.panels.values():
				pnl.SetShift(False)

		evt.Skip()
			
	def SetShift(self, flag, propagate=False):
		self.shift = flag
		if propagate:
			for pnl in self.panels.values():
				pnl.SetShift(flag)

	def OnResetScreen(self, _):
		self.ResetScreen()
		
	def ResetScreen(self):
		self.SetMaxSize((self.totalw+16+WIDTHADJUST, self.totalh))
		self.SetSize((self.totalw+16+WIDTHADJUST, self.totalh))
		self.SetPosition((-self.centerOffset, 0))
		
		self.shiftXOffset = -self.centerOffset
		self.shiftYOffset = 0
		
		if self.ATCEnabled:
			self.Request({"atc": { "action": "reset"}})

	def OnBResetClock(self, _):
		self.tickerCount = 0
		self.timeValue = self.settings.dispatcher.clockstarttime
		self.DisplayTimeValue()
		
	def OnBStartClock(self, _):
		self.clockRunning = not self.clockRunning
		self.DetermineClockStatus()			
		self.bStartClock.SetLabel("Stop" if self.clockRunning else "Start")
		self.bResetClock.Enable(not self.clockRunning)
		if self.clockRunning:
			self.tickerCount = 0
		self.DisplayTimeValue()

	def OnCBToD(self, _):
		if self.cbToD.IsChecked():
			self.ToD = True
			self.bStartClock.Enable(False)
			self.bResetClock.Enable(False)
			self.timeValue = self.GetToD()
		else:		
			self.ToD = False
			self.bStartClock.Enable(True)
			self.bResetClock.Enable(True)
			self.timeValue = self.settings.dispatcher.clockstarttime
			
		self.clockRunning = False
		self.bStartClock.SetLabel("Start")

		self.DetermineClockStatus()			
		self.DisplayTimeValue()
		
	def GetToD(self):
		tm = time.localtime()
		return (tm.tm_hour%12) * 60 + tm.tm_min
	
	def DetermineClockStatus(self):
		if self.ToD:
			self.clockStatus = 2
		elif self.clockRunning:
			self.clockStatus = 1
		else:
			self.clockStatus = 0
		self.ShowClockStatus()
		
	def ShowClockStatus(self):
		if self.clockStatus == 0: # clock is stopped
			self.timeDisplay.SetForegroundColour(wx.Colour(255, 0, 0))
		
		elif self.clockStatus == 1: # running in railroad mode
			self.timeDisplay.SetForegroundColour(wx.Colour(0, 255, 0))
		
		elif self.clockStatus == 2: # time of day
			self.timeDisplay.SetForegroundColour(wx.Colour(32, 229, 240))
		self.timeDisplay.Refresh()
		
	def DisplayTimeValue(self):
		hours = int(self.timeValue/60)
		if hours == 0:
			hours = 12
		minutes = self.timeValue % 60
		self.timeDisplay.SetValue("%2d:%02d" % (hours, minutes))
		if self.subscribed and self.IsDispatcher():
			self.Request({"clock": { "value": self.timeValue, "status": self.clockStatus}})
					
	def OnThrottle(self, _):
		throttleExec = os.path.join(os.getcwd(), "throttle", "main.py")
		throttleProc = Popen([sys.executable, throttleExec])
		logging.info("Throttle started as PID %d" % throttleProc.pid)
					
	def OnEditTrains(self, _):
		treditExec = os.path.join(os.getcwd(), "traineditor", "main.py")
		treditProc = Popen([sys.executable, treditExec])
		logging.info("Train Editor started as PID %d" % treditProc.pid)

	def OnBActiveTrains(self, _):
		if self.activeTrainsDlg.IsShown():
			self.activeTrainsDlg.Hide()
		else:
			self.activeTrainsDlg.Show()
		
	def OnBLostTrains(self, _):
		self.RecoverLostTrains()

	def DefineWidgets(self, voffset):
		if not self.IsDispatcher():
			return

		self.rbNassauControl = wx.RadioBox(self, wx.ID_ANY, "Nassau", (150, voffset), wx.DefaultSize,
				["Nassau", "Dispatcher: Main", "Dispatcher: All"], 1, wx.RA_SPECIFY_COLS)
		self.Bind(wx.EVT_RADIOBOX, self.OnRBNassau, self.rbNassauControl)
		self.rbNassauControl.Hide()
		self.widgetMap[NaCl].append([self.rbNassauControl, 0])
		self.rbNassauControl.SetSelection(0)
		self.nassauControl = 0

		self.rbCliffControl = wx.RadioBox(self, wx.ID_ANY, "Cliff", (1550, voffset), wx.DefaultSize,
				["Cliff", "Dispatcher: Bank/C13", "Dispatcher: All"], 1, wx.RA_SPECIFY_COLS)
		self.Bind(wx.EVT_RADIOBOX, self.OnRBCliff, self.rbCliffControl)
		self.rbCliffControl.Hide()
		self.widgetMap[NaCl].append([self.rbCliffControl, 0])
		self.rbCliffControl.SetSelection(0)
		self.cliffControl = 0

		self.rbYardControl = wx.RadioBox(self, wx.ID_ANY, "Yard", (1450, voffset), wx.DefaultSize,
				["Yard", "Dispatcher"], 1, wx.RA_SPECIFY_COLS)
		self.Bind(wx.EVT_RADIOBOX, self.OnRBYard, self.rbYardControl)
		self.rbYardControl.Hide()
		self.widgetMap[HyYdPt].append([self.rbYardControl, 0])

		self.cbLathamFleet = wx.CheckBox(self, -1, "Latham Fleeting", (300, voffset+10))
		self.Bind(wx.EVT_CHECKBOX, self.OnCBLathamFleet, self.cbLathamFleet)
		self.cbLathamFleet.Hide()
		self.widgetMap[LaKr].append([self.cbLathamFleet, 0])
		self.LathamFleetSignals =  ["L8R", "L8L", "L6RA", "L6RB", "L6L", "L4R", "L4L"]

		self.cbCarltonFleet = wx.CheckBox(self, -1, "Carlton Fleeting", (300, voffset+30))
		self.Bind(wx.EVT_CHECKBOX, self.OnCBCarltonFleet, self.cbCarltonFleet)
		self.cbCarltonFleet.Hide()
		self.widgetMap[LaKr].append([self.cbCarltonFleet, 0])
		self.CarltonFleetSignals = ["L18R", "L18L", "L16R", "L14R", "L14L"]

		self.cbValleyJctFleet = wx.CheckBox(self, -1, "Valley Junction Fleeting", (900, voffset+10))
		self.Bind(wx.EVT_CHECKBOX, self.OnCBValleyJctFleet, self.cbValleyJctFleet)
		self.cbValleyJctFleet.Hide()
		self.widgetMap[LaKr].append([self.cbValleyJctFleet, 0])
		self.ValleyJctFleetSignals = ["D6RA", "D6RB", "D6L", "D4RA", "D4RB", "D4L"]

		self.cbFossFleet = wx.CheckBox(self, -1, "Foss Fleeting", (900, voffset+30))
		self.Bind(wx.EVT_CHECKBOX, self.OnCBFossFleet, self.cbFossFleet)
		self.cbFossFleet.Hide()
		self.widgetMap[LaKr].append([self.cbFossFleet, 0])
		self.FossFleetSignals = ["D10R", "D10L", "D12R", "D12L"]

		self.cbShoreFleet = wx.CheckBox(self, -1, "Shore Fleeting", (1500, voffset+10))
		self.Bind(wx.EVT_CHECKBOX, self.OnCBShoreFleet, self.cbShoreFleet)
		self.cbShoreFleet.Hide()
		self.widgetMap[LaKr].append([self.cbShoreFleet, 0])
		self.ShoreFleetSignals = ["S4R", "S12R", "S4LA", "S4LB", "S4LC", "S12LA", "S12LB", "S12LC"]

		self.cbHydeJctFleet = wx.CheckBox(self, -1, "Hyde Junction Fleeting", (1500, voffset+30))
		self.Bind(wx.EVT_CHECKBOX, self.OnCBHydeJctFleet, self.cbHydeJctFleet)
		self.cbHydeJctFleet.Hide()
		self.widgetMap[LaKr].append([self.cbHydeJctFleet, 0])
		self.HydeJctFleetSignals = ["S20R", "S18R", "S16R", "S20L", "S18LA", "S18LB", "S16L"]

		self.cbKrulishFleet = wx.CheckBox(self, -1, "Krulish Fleeting", (2100, voffset+10))
		self.Bind(wx.EVT_CHECKBOX, self.OnCBKrulishFleet, self.cbKrulishFleet)
		self.cbKrulishFleet.Hide()
		self.widgetMap[LaKr].append([self.cbKrulishFleet, 0])
		self.KrulishFleetSignals = ["K8R", "K4R", "K2R", "K8LA", "K8LB", "K2L"]

		self.cbNassauFleet = wx.CheckBox(self, -1, "Nassau Fleeting", (300, voffset+10))
		self.Bind(wx.EVT_CHECKBOX, self.OnCBNassauFleet, self.cbNassauFleet)
		self.cbNassauFleet.Hide()
		self.widgetMap[NaCl].append([self.cbNassauFleet, 0])
		self.NassauFleetSignalsMain = ["N16R", "N14R",
						"N18LB", "N16L", "N14LA", "N14LB",
						"N26RB", "N26RC", "N24RA", "N24RB",
						"N26L", "N24L"]
		self.NassauFleetSignalsAll = ["N18R", "N16R", "N14R",
						"N18LA", "N18LB", "N16L", "N14LA", "N14LB", "N14LC", "N14LD",
						"N28R", "N26RA", "N26RB", "N26RC", "N24RA", "N24RB", "N24RC", "N24RD",
						"N28L", "N26L", "N24L"]
		self.NassauFleetSignals = self.NassauFleetSignalsAll

		self.cbBankFleet = wx.CheckBox(self, -1, "Martinsville Fleeting", (900, voffset+10))
		self.Bind(wx.EVT_CHECKBOX, self.OnCBBankFleet, self.cbBankFleet)
		self.cbBankFleet.Hide()
		self.cbBankFleet.Enable(self.cliffControl != 0)
		self.widgetMap[NaCl].append([self.cbBankFleet, 0])
		self.BankFleetSignals = ["C22L", "C24L", "C22R", "C24R"]

		self.cbClivedenFleet = wx.CheckBox(self, -1, "Cliveden Fleeting", (1400, voffset+10))
		self.Bind(wx.EVT_CHECKBOX, self.OnCBClivedenFleet, self.cbClivedenFleet)
		self.cbClivedenFleet.Hide()
		self.cbClivedenFleet.Enable(self.cliffControl != 0)
		self.widgetMap[NaCl].append([self.cbClivedenFleet, 0])
		self.ClivedenFleetSignals = ["C10L", "C12L", "C10R", "C12R"]

		self.cbC13Auto = wx.CheckBox(self, -1, "Automate block C13", (900, voffset+50))
		self.Bind(wx.EVT_CHECKBOX, self.OnCBC13Auto, self.cbC13Auto)
		self.cbC13Auto.Hide()
		self.cbC13Auto.Enable(self.cliffControl != 0)
		self.widgetMap[NaCl].append([self.cbC13Auto, 0])

		self.cbYardFleet = wx.CheckBox(self, -1, "Yard Fleeting", (1650, voffset+10))
		self.Bind(wx.EVT_CHECKBOX, self.OnCBYardFleet, self.cbYardFleet)
		self.cbYardFleet.Hide()
		self.widgetMap[HyYdPt].append([self.cbYardFleet, 0])
		self.YardFleetSignals = [ "Y2R", "Y2L", "Y4RA", "Y4RB", "Y4L", "Y8R", "Y8LA", "Y8LB", "Y8LC", "Y10R", "Y10L",
					"Y22R", "Y22L", "Y24LA", "Y24LB", "Y26R", "Y26LA", "Y26LB", "Y26LC", "Y34RA", "Y34RB", "Y34L",
					"Y40RA", "Y40RB", "Y40RC", "Y40RD", "Y40L", "Y42R", "Y42LA", "Y42LB", "Y42LC", "Y42LD" ]

		self.cbCliffFleet = wx.CheckBox(self, -1, "Cliff Fleeting", (2100, voffset+10))
		self.Bind(wx.EVT_CHECKBOX, self.OnCBCliffFleet, self.cbCliffFleet)
		self.cbCliffFleet.Hide()
		self.cbCliffFleet.Enable(self.cliffControl == 2)
		self.widgetMap[NaCl].append([self.cbCliffFleet, 0])
		self.CliffFleetSignals = [ "C2LA", "C2LB", "C2LC", "C2LD", "C2R",
					"C4L", "C4RA", "C4RB", "C4RC", "C4RD",
					"C6LA", "C6LB", "C6LC", "C6LD", "C6LE", "C6LF", "C6LG", "C6LH", "C6LJ", "C6LK", "C6LL", "C6R",
					"C8L", "C8RA", "C8RB", "C8RC", "C8RD", "C8RE", "C8RF", "C8RG", "C8RH", "C8RJ", "C8RK", "C8RL" ]

		self.cbHydeFleet = wx.CheckBox(self, -1, "Hyde Fleeting", (250, voffset+10))
		self.Bind(wx.EVT_CHECKBOX, self.OnCBHydeFleet, self.cbHydeFleet)
		self.cbHydeFleet.Hide()
		self.widgetMap[HyYdPt].append([self.cbHydeFleet, 0])
		self.HydeFleetSignals = [ "H4R", "H4LA", "H4LB", "H4LC", "H4LD", "H6R", "H6LA", "H6LB", "H6LC", "H6LD", "H8R", "H8L",
					"H10L", "H10RA", "H10RB", "H10RC", "H10RD", "H10RE", "H12L", "H12RA", "H12RB", "H12RC", "H12RD", "H12RE"  ]

	def GetFleetMap(self, signm):
		siglists = [
			[ self.NassauFleetSignals,    self.cbNassauFleet ],
			[ self.LathamFleetSignals,    self.cbLathamFleet ],
			[ self.CarltonFleetSignals,   self.cbCarltonFleet ],
			[ self.ValleyJctFleetSignals, self.cbValleyJctFleet ],
			[ self.FossFleetSignals,      self.cbFossFleet ],
			[ self.ShoreFleetSignals,     self.cbShoreFleet ],
			[ self.HydeJctFleetSignals,   self.cbHydeJctFleet ],
			[ self.KrulishFleetSignals,   self.cbKrulishFleet ],
			[ self.BankFleetSignals,      self.cbBankFleet ],
			[ self.ClivedenFleetSignals,  self.cbClivedenFleet ],
			[ self.HydeFleetSignals,      self.cbHydeFleet ],
			[ self.YardFleetSignals,      self.cbYardFleet ],
			[ self.CliffFleetSignals,      self.cbCliffFleet ],
		]
		for siglist, checkbox in siglists:
			if signm in siglist:
				return siglist, checkbox
			
		return None, None

	def UpdateControlWidget(self, name, value):
		if not self.IsDispatcher():
			return
		if name == "nassau":
			self.rbNassauControl.SetSelection(value)
			self.nassauControl = value
			self.cbNassauFleet.Enable(value != 0)
			
		elif name == "cliff":
			self.rbCliffControl.SetSelection(value)
			self.cliffControl = value
			
		elif name == "yard":
			logging.debug("setting yard control to %d" % value)
			self.rbYardControl.SetSelection(value)
			self.cbYardFleet.Enable(value != 0)
			self.yardControl = value
			logging.debug("updatecontrolwidget, yard=%d" % value)

		elif name == "cliff.fleet":
			ctl = self.rbCliffControl.GetSelection()
			self.cliffControl = ctl
			if ctl == 0:
				self.cbCliffFleet.SetValue(value != 0)
				self.cbClivedenFleet.SetValue(value != 0)
				self.cbBankFleet.SetValue(value != 0)
				f = 1 if value != 0 else 0
				for signm in self.CliffFleetSignals + self.ClivedenFleetSignals + self.BankFleetSignals:
					self.Request({"fleet": { "name": signm, "value": f}})
			elif ctl == 1:
				self.cbCliffFleet.SetValue(value != 0)
				f = 1 if value != 0 else 0
				for signm in self.CliffFleetSignals + self.ClivedenFleetSignals:
					self.Request({"fleet": { "name": signm, "value": f}})

		elif name == "c13auto":
			self.c13auto = (value != 0)
			self.cbC13Auto.SetValue(self.c13auto)

		elif name == "hyde.fleet":
			self.cbHydeFleet.SetValue(value != 0)			
			f = 1 if value != 0 else 0
			for signm in self.HydeFleetSignals:
				self.Request({"fleet": { "name": signm, "value": f}})
			
		elif name == "yard.fleet":
			self.cbYardFleet.SetValue(value != 0)
			f = 1 if value != 0 else 0
			for signm in self.YardFleetSignals:
				self.Request({"fleet": { "name": signm, "value": f}})			
			
		elif name == "latham.fleet":
			self.cbLathamFleet.SetValue(value != 0)
			
		elif name == "shore.fleet":
			self.cbShoreFleet.SetValue(value != 0)
			
		elif name == "hydejct.fleet":
			self.cbHydeJctFleet.SetValue(value != 0)
			
		elif name == "krulish.fleet":
			self.cbKrulishFleet.SetValue(value != 0)
			
		elif name == "nassau.fleet":
			self.cbNassauFleet.SetValue(value != 0)
			f = 1 if value != 0 else 0
			for signm in self.NassauFleetSignals:
				self.Request({"fleet": { "name": signm, "value": f}})			
			
		elif name == "bank.fleet":
			self.cbBankFleet.SetValue(value != 0)
			
		elif name == "cliveden.fleet":
			self.cbClivedenFleet.SetValue(value != 0)

		elif name == "carlton.fleet":
			self.cbCarltonFleet.SetValue(value != 0)
			
		elif name == "foss.fleet":
			self.cbFossFleet.SetValue(value != 0)
			
		elif name == "valleyjct.fleet":
			self.cbValleyJctFleet.SetValue(value != 0)

	def SendControlValues(self):
		if not self.IsDispatcher():
			return
		
		ctl = self.rbNassauControl.GetSelection()
		self.cbNassauFleet.Enable(ctl != 0)
		self.Request({"": { "name": "nassau", "value": ctl}})
		self.nassauControl = ctl
			
		ctl = self.rbCliffControl.GetSelection()
		self.cbCliffFleet.Enable(ctl == 2)
		self.cbBankFleet.Enable(ctl != 0)
		self.cbClivedenFleet.Enable(ctl == 2)
		self.cbC13Auto.Enable(ctl != 0)
		self.Request({"control": { "name": "cliff", "value": ctl}})
		self.cliffControl = ctl
		
		ctl = self.rbYardControl.GetSelection()
		self.cbYardFleet.Enable(ctl != 0)
		self.Request({"control": { "name": "yard", "value": ctl}})

		f = 1 if self.cbCliffFleet.IsChecked() else 0
		for signm in self.CliffFleetSignals:
			self.Request({"fleet": { "name": signm, "value": f}})
		self.Request({"control": {"name": "cliff.fleet", "value": f}})

		f = 1 if self.cbLathamFleet.IsChecked() else 0
		for signm in self.LathamFleetSignals:
			self.Request({"fleet": { "name": signm, "value": f}})
		self.Request({"control": {"name": "latham.fleet", "value": f}})

		f = 1 if self.cbHydeFleet.IsChecked() else 0
		for signm in self.HydeFleetSignals:
			self.Request({"fleet": { "name": signm, "value": f}})
		self.Request({"control": {"name": "hyde.fleet", "value": f}})

		f = 1 if self.cbYardFleet.IsChecked() else 0
		for signm in self.YardFleetSignals:
			self.Request({"fleet": { "name": signm, "value": f}})
		self.Request({"control": {"name": "yard.fleet", "value": f}})

		f = 1 if self.cbShoreFleet.IsChecked() else 0
		for signm in self.ShoreFleetSignals:
			self.Request({"fleet": { "name": signm, "value": f}})
		self.Request({"control": {"name": "shore.fleet", "value": f}})

		f = 1 if self.cbHydeJctFleet.IsChecked() else 0
		for signm in self.HydeJctFleetSignals:
			self.Request({"fleet": { "name": signm, "value": f}})
		self.Request({"control": {"name": "hydejct.fleet", "value": f}})
			
		f = 1 if self.cbKrulishFleet.IsChecked() else 0
		for signm in self.KrulishFleetSignals:
			self.Request({"fleet": { "name": signm, "value": f}})
		self.Request({"control": {"name": "krulish.fleet", "value": f}})

		f = 1 if self.cbNassauFleet.IsChecked() else 0
		if self.nassauControl == 1:
			self.NassauFleetSignals = self.NassauFleetSignalsMain
		elif self.nassauControl == 2:
			self.NassauFleetSignals = self.NassauFleetSignalsAll

		for signm in self.NassauFleetSignals:
			self.Request({"fleet": { "name": signm, "value": f}})
		self.Request({"control": {"name": "nassau.fleet", "value": f}})
			
		f = 1 if self.cbBankFleet.IsChecked() else 0
		for signm in self.BankFleetSignals:
			self.Request({"fleet": { "name": signm, "value": f}})
		self.Request({"control": {"name": "bank.fleet", "value": f}})

		f = 1 if self.cbClivedenFleet.IsChecked() else 0
		for signm in self.ClivedenFleetSignals:
			self.Request({"fleet": { "name": signm, "value": f}})
		self.Request({"control": {"name": "cliveden.fleet", "value": f}})

		f = 1 if self.cbCarltonFleet.IsChecked() else 0
		for signm in self.CarltonFleetSignals:
			self.Request({"fleet": { "name": signm, "value": f}})
		self.Request({"control": {"name": "carlton.fleet", "value": f}})

		f = 1 if self.cbValleyJctFleet.IsChecked() else 0
		for signm in self.ValleyJctFleetSignals:
			self.Request({"fleet": { "name": signm, "value": f}})
		self.Request({"control": {"name": "valleyjct.fleet", "value": f}})

		f = 1 if self.cbFossFleet.IsChecked() else 0
		for signm in self.FossFleetSignals:
			self.Request({"fleet": { "name": signm, "value": f}})
		self.Request({"control": {"name": "foss.fleet", "value": f}})

		f = 1 if self.cbC13Auto.IsChecked() else 0
		self.Request({"control": {"name": "c13auto", "value": f}})

		self.SendOSSLocks()
		self.SendSidingsUnlocked()

	def OnCBAutoRouter(self, evt):
		self.AREnabled = self.cbAutoRouter.IsChecked()
		if self.AREnabled:
			rqStatus = "on"
		else:
			rqStatus = "off"
		self.Request({"autorouter": { "status": rqStatus}})

	def OnCBATC(self, evt):
		# ATC must run on the same machine as this dispatcher because it has a windowing interface
		self.ATCEnabled = self.cbATC.IsChecked()
		if self.ATCEnabled:
			if self.procATC is None or self.procATC.poll() is not None:
				atcExec = os.path.join(os.getcwd(), "atc", "main.py")
				self.procATC = Popen([sys.executable, atcExec])
				self.pidATC = self.procATC.pid
				logging.debug("atc server started as PID %d" % self.pidATC)
				self.pendingATCShowCmd = {"atc": {"action": ["show"], "x": 1560, "y": 0}}
				wx.CallLater(750, self.sendPendingATCShow)
			else:
				self.Request( {"atc": {"action": ["show"]}})

		else:
			self.Request({"atc": { "action": "hide"}})

	def OnCBOSSLocks(self, evt):
		self.SendOSSLocks()
		
	def SendOSSLocks(self):
		self.OSSLocks = self.cbOSSLocks.IsChecked()		
		self.Request({"control": {"name": "osslocks", "value": 1 if self.OSSLocks else 0}})
		self.districts.EvaluateDistrictLocks(self.OSSLocks)

	def OnCBSidingsUnlocked(self, evt):
		self.SendSidingsUnlocked()
		
	def SendSidingsUnlocked(self):
		self.sidingsUnlocked = self.cbSidingsUnlocked.IsChecked()		
		self.Request({"control": {"name": "sidingsunlocked", "value": 1 if self.sidingsUnlocked else 0}})
		for sw in SidingSwitches:
			if sw.startswith("C"):
				if self.cliffControl == 0:
					# local control - skip to the next switch
					continue
				if self.cliffControl == 1 and sw == "CSw3":
					# cliff operator controls CSw3 only
					continue
				# otherwise, we modify this siding lock
					
			self.Request({'handswitch': {'name': sw+'.hand', 'status': 1 if self.sidingsUnlocked else 0}})
			
	def sendPendingATCShow(self):
		self.Request(self.pendingATCShowCmd)
		
	def OnRBNassau(self, evt):
		ctl = evt.GetInt()
		self.cbNassauFleet.Enable(ctl != 0)
		self.Request({"control": { "name": "nassau", "value": ctl}})
		self.nassauControl = ctl

	def OnRBCliff(self, evt):
		ctl = evt.GetInt()
		self.cbCliffFleet.Enable(ctl == 2)
		self.cbBankFleet.Enable(ctl != 0)
		self.cbClivedenFleet.Enable(ctl == 2)
		self.cbC13Auto.Enable(ctl != 0)
		self.Request({"control": { "name": "cliff", "value": ctl}})
		self.cliffControl = ctl

	def OnRBYard(self, evt):
		ctl = evt.GetInt()
		self.cbYardFleet.Enable(ctl != 0)
		self.Request({"control": { "name": "yard", "value": ctl}})
		self.yardControl = ctl

	def OnCBLathamFleet(self, _):
		f = 1 if self.cbLathamFleet.IsChecked() else 0
		for signm in self.LathamFleetSignals:
			self.Request({"fleet": { "name": signm, "value": f}})
		self.Request({"control": {"name": "latham.fleet", "value": f}})

	def OnCBShoreFleet(self, _):
		f = 1 if self.cbShoreFleet.IsChecked() else 0
		for signm in self.ShoreFleetSignals:
			self.Request({"fleet": { "name": signm, "value": f}})
		self.Request({"control": {"name": "shore.fleet", "value": f}})

	def OnCBHydeJctFleet(self, _):
		f = 1 if self.cbHydeJctFleet.IsChecked() else 0
		for signm in self.HydeJctFleetSignals:
			self.Request({"fleet": { "name": signm, "value": f}})
		self.Request({"control": {"name": "hydejct.fleet", "value": f}})

	def OnCBKrulishFleet(self, _):
		f = 1 if self.cbKrulishFleet.IsChecked() else 0
		for signm in self.KrulishFleetSignals:
			self.Request({"fleet": { "name": signm, "value": f}})
		self.Request({"control": {"name": "krulish.fleet", "value": f}})

	def OnCBNassauFleet(self, _):
		f = 1 if self.cbNassauFleet.IsChecked() else 0
		if self.nassauControl == 1:
			self.NassauFleetSignals = self.NassauFleetSignalsMain
		elif self.nassauControl == 2:
			self.NassauFleetSignals = self.NassauFleetSignalsAll

		for signm in self.NassauFleetSignals:
			self.Request({"fleet": { "name": signm, "value": f}})
		self.Request({"control": {"name": "nassau.fleet", "value": f}})

	def OnCBBankFleet(self, _):
		f = 1 if self.cbBankFleet.IsChecked() else 0
		for signm in self.BankFleetSignals:
			self.Request({"fleet": { "name": signm, "value": f}})
		self.Request({"control": {"name": "bank.fleet", "value": f}})

	def OnCBClivedenFleet(self, _):
		f = 1 if self.cbClivedenFleet.IsChecked() else 0
		for signm in self.ClivedenFleetSignals:
			self.Request({"fleet": { "name": signm, "value": f}})
		self.Request({"control": {"name": "cliveden.fleet", "value": f}})

	def OnCBC13Auto(self, _):
		self.c13auto = self.cbC13Auto.IsChecked()
		self.Request({"control": {"name": "c13auto", "value": 1 if self.c13auto else 0}})

	def OnCBCarltonFleet(self, _):
		f = 1 if self.cbCarltonFleet.IsChecked() else 0
		for signm in self.CarltonFleetSignals:
			self.Request({"fleet": { "name": signm, "value": f}})
		self.Request({"control": {"name": "carlton.fleet", "value": f}})

	def OnCBValleyJctFleet(self, _):
		f = 1 if self.cbValleyJctFleet.IsChecked() else 0
		for signm in self.ValleyJctFleetSignals:
			self.Request({"fleet": { "name": signm, "value": f}})
		self.Request({"control": {"name": "valleyjct.fleet", "value": f}})

	def OnCBFossFleet(self, _):
		f = 1 if self.cbFossFleet.IsChecked() else 0
		for signm in self.FossFleetSignals:
			self.Request({"fleet": { "name": signm, "value": f}})
		self.Request({"control": {"name": "foss.fleet", "value": f}})

	def OnCBCliffFleet(self, _):
		f = 1 if self.cbCliffFleet.IsChecked() else 0
		for signm in self.CliffFleetSignals:
			self.Request({"fleet": { "name": signm, "value": f}})
		self.Request({"control": {"name": "cliff.fleet", "value": f}})

	def OnCBYardFleet(self, _):
		f = 1 if self.cbYardFleet.IsChecked() else 0
		for signm in self.YardFleetSignals:
			self.Request({"fleet": { "name": signm, "value": f}})
		self.Request({"control": {"name": "yard.fleet", "value": f}})

	def OnCBHydeFleet(self, _):
		f = 1 if self.cbHydeFleet.IsChecked() else 0
		for signm in self.HydeFleetSignals:
			self.Request({"fleet": { "name": signm, "value": f}})
		self.Request({"control": {"name": "hyde.fleet", "value": f}})

	def FleetCheckBoxes(self, signm):
		if not self.IsDispatcher():
			return
		siglist, checkbox = self.GetFleetMap(signm)
		if siglist is not None:
			fltct = nfltct = 0
			for sn in siglist:
				sig = self.signals[sn]
				if sig.IsFleeted():
					fltct += 1
				else:
					nfltct += 1
			checkbox.SetValue(nfltct == 0)

	def DrawCameras(self):
		cams = {LaKr: [
			[(242, 32), self.bitmaps.cameras.lakr.cam7],
			[(464, 32), self.bitmaps.cameras.lakr.cam8],
			[(768, 32), self.bitmaps.cameras.lakr.cam9],
			[(890, 32), self.bitmaps.cameras.lakr.cam10],
			[(972, 32), self.bitmaps.cameras.lakr.cam12],
			[(1186, 32), self.bitmaps.cameras.lakr.cam3],
			[(1424, 32), self.bitmaps.cameras.lakr.cam4],
			[(1634, 32), self.bitmaps.cameras.lakr.cam13],
			[(1884, 32), self.bitmaps.cameras.lakr.cam14],
			[(2152, 32), self.bitmaps.cameras.lakr.cam15],
			[(2198, 32), self.bitmaps.cameras.lakr.cam16],
			[(2362, 32), self.bitmaps.cameras.lakr.cam9],
			[(2416, 32), self.bitmaps.cameras.lakr.cam10],
		], HyYdPt: [
			[(282, 72), self.bitmaps.cameras.hyydpt.cam15],
			[(838, 72), self.bitmaps.cameras.hyydpt.cam16],
			[(904, 576), self.bitmaps.cameras.hyydpt.cam1],
			[(1732, 32), self.bitmaps.cameras.hyydpt.cam1],
			[(1830, 32), self.bitmaps.cameras.hyydpt.cam2],
			[(1970, 32), self.bitmaps.cameras.hyydpt.cam3],
			[(2090, 32), self.bitmaps.cameras.hyydpt.cam4],
			[(2272, 236), self.bitmaps.cameras.hyydpt.cam5],
			[(2292, 444), self.bitmaps.cameras.hyydpt.cam6],
		], NaCl: [
			[(364, 28), self.bitmaps.cameras.nacl.cam11],
			[(670, 28), self.bitmaps.cameras.nacl.cam12],
			[(918, 28), self.bitmaps.cameras.nacl.cam1],
			[(998, 28), self.bitmaps.cameras.nacl.cam2],
			[(1074, 28), self.bitmaps.cameras.nacl.cam3],
			[(1248, 28), self.bitmaps.cameras.nacl.cam4],
			[(1442, 28), self.bitmaps.cameras.nacl.cam7],
			[(2492, 502), self.bitmaps.cameras.nacl.cam8],
		]}

		for screen in cams:
			offset = self.diagrams[screen].offset
			for pos, bmp in cams[screen]:
				self.panels[screen].DrawFixedBitmap(pos[0], pos[1], offset, bmp)

	def UpdatePositionDisplay(self, x, y, scr):
		self.xpos.SetValue("%4d" % x)
		self.ypos.SetValue("%4d" % y)
		self.scrn.SetValue("%s" % scr)

	def ShowTitle(self):
		titleString = self.title
		if self.subscribed and self.sessionid is not None:
			titleString += ("  -  Session ID %s" % str(self.sessionid))
		self.SetTitle(titleString)

	def Initialize(self, districtMap):
		self.CreateDispatchTable()
		self.listener = None
		self.ShowTitle()
		self.Bind(EVT_DELIVERY, self.onDeliveryEvent)
		self.Bind(EVT_DISCONNECT, self.onDisconnectEvent)

		self.tiles, self.totiles, self.sstiles, self.sigtiles, self.misctiles = loadTiles(self.bitmaps)
		self.districts = Districts(self)
		self.signalLeverMap = {}
		for dname in ["Yard", "Latham", "Dell", "Shore", "Krulish", "Nassau", "Bank", "Cliveden", "Cliff", "Hyde", "Port"]:
			dobj = districtMap[dname][0]
			dscreen = districtMap[dname][1]
			self.districts.AddDistrict(dobj(dname, self, dscreen))

		self.districts.SetTiles(self.tiles, self.totiles, self.sstiles, self.sigtiles, self.misctiles, self.bitmaps.buttons)

		self.blocks, self.osBlocks = self.districts.DefineBlocks()
		self.turnouts = self.districts.DefineTurnouts(self.blocks)
		self.signals, self.blocksignals, self.ossignals, self.routes, self.osProxies =  self.districts.DefineSignals()
		self.buttons =  self.districts.DefineButtons()
		self.handswitches =  self.districts.DefineHandSwitches()
		self.indicators = self.districts.DefineIndicators()
		self.dlocks = self.districts.DefineDistrictLocks()
		self.sbMap = {}
		for b, blk in self.blocks.items():
			sbw, sbe = blk.GetStoppingSections()
			if sbe:
				self.sbMap[b+".E"] = blk
			if sbw:
				self.sbMap[b+".W"] = blk
		
		self.blockAdjacency = {}
		for osname, blklist in self.osBlocks.items():
			if osname not in self.blockAdjacency:
				self.blockAdjacency[osname] = []
			for b in blklist:
				if b not in self.blockAdjacency[osname]:
					self.blockAdjacency[osname].append(b)
					
				if b not in self.blockAdjacency:
					self.blockAdjacency[b] = []
				self.blockAdjacency[b].append(osname)

		self.pendingFleets = {}

		self.resolveObjects()

		self.rrServer = RRServer()
		self.rrServer.SetServerAddress(self.settings.ipaddr, self.settings.serverport)

		self.trains = {}

		self.activeTrainsDlg.SetSignals(self.signals)
		self.activeTrainsDlg.SetBlocks(self.blocks)

		self.districts.Initialize()

		# only set up hot spots on the diagram
		self.turnoutMap = { (t.GetScreen(), t.GetPos()): t for t in self.turnouts.values() if not t.IsRouteControlled() }
		self.disabledTurnoutMap = { (t.GetScreen(), t.GetPos()): t for t in self.turnouts.values() if t.IsRouteControlled() }
		self.buttonMap = { (b.GetScreen(), b.GetPos()): b for b in self.buttons.values() }
		self.signalMap = { (s.GetScreen(), s.GetPos()): s for s in self.signals.values() }
		self.handswitchMap = { (l.GetScreen(), l.GetPos()): l for l in self.handswitches.values() }
		self.blockMap = self.BuildBlockMap(self.blocks)

		self.buttonsToClear = []

		self.districts.Draw()
		
		self.Bind(wx.EVT_TIMER, self.onTicker)
		self.ticker = wx.Timer(self)
		self.tickerFlag = False
		self.tickerCount = 0
		self.ticker.Start(500)
		
		self.splash()
		
	def splash(self):
		if self.showSplash:
			self.showSplash = False
			splashExec = os.path.join(os.getcwd(), "splash", "main.py")
			pid = Popen([sys.executable, splashExec]).pid
			logging.debug("displaying splash screen as PID %d" % pid)

	def AddSignalLever(self, slname, district):
		self.signalLeverMap[slname] = district

	def GetSignalLeverDistrict(self, slname):
		if slname not in self.signalLeverMap:
			return None

		return self.signalLeverMap[slname]

	def GetTurnoutLocks(self):
		l = self.rrServer.Get("turnoutlocks", {})
		return l

	def ClearLocks(self, toNames):
		self.Request({"clearlocks": {"turnouts": toNames}})

	def IsDispatcher(self):
		return self.settings.dispatcher.dispatch

	def IsSatellite(self):
		return self.settings.dispatcher.satellite

	def IsDispatcherOrSatellite(self):
		return self.settings.dispatcher.dispatch or self.settings.dispatcher.satellite

	def resolveObjects(self):
		for _, bk in self.blocks.items():
			sgWest, sgEast = bk.GetSBSignals()
			if sgWest is not None:
				try:
					self.signals[sgWest].SetGuardBlock(bk)
				except KeyError:
					sgWest = None

			if sgEast is not None:
				try:
					self.signals[sgEast].SetGuardBlock(bk)
				except KeyError:
					sgEast = None
			bk.SetSBSignals((sgWest, sgEast))

		# invert osBlocks so that we can easily map a block into the OS's it interconnects
		self.blockOSMap = {}
		nameMap = {}
		for osblknm, blklist in self.osBlocks.items():
			for blknm in blklist:
				if blknm in self.blockOSMap:
					self.blockOSMap[blknm].append(self.blocks[osblknm])
					nameMap[blknm].append(osblknm)
				else:
					self.blockOSMap[blknm] = [self.blocks[osblknm]]
					nameMap[blknm] = [osblknm]

		# jfn = os.path.join(os.getcwd(), "data", "blockosmap.json")
		# with open(jfn, "w") as jfp:
		# 	json.dump(nameMap, jfp, indent=2)

	def GetOSForBlock(self, blknm):
		if blknm not in self.blockOSMap:
			return []
		else:
			return self.blockOSMap[blknm]
	#
	# def AddPendingFleet(self, block, osblock, route, sig):
	# 	self.pendingFleets[block.GetName()] = [sig, osblock, route]
	#
	# def DelPendingFleet(self, block):
	# 	if block is None:
	# 		return
	#
	# 	bname = block.GetName()
	# 	if bname not in self.pendingFleets:
	# 		return
	#
	# 	del(self.pendingFleets[bname])
	#
	# def DoFleetPending(self, block):
	# 	bname = block.GetName()
	# 	if bname not in self.pendingFleets:
	# 		return
	#
	# 	sig, osblock, rtname = self.pendingFleets[bname]
	# 	del(self.pendingFleets[bname])
	# 	'''
	# 	the signal should be red, so if it's not, do nothing here
	# 	'''
	# 	if sig.GetAspect() != 0:
	# 		return
	# 	'''
	# 	calculate a new aspect for this signal, based on current conditions
	# 	'''
	# 	rt = osblock.GetRoute()
	# 	newAspect = sig.GetDistrict().CalculateAspect(sig, osblock, rt)
	# 	'''
	# 	check if this signal is still in the selected route through this OS block
	# 	'''
	# 	if rt is not None:
	# 		if rt.GetName() == rtname:
	# 			sigs = rt.GetSignals()
	# 			if sig.GetName() in sigs:
	# 				sig.DoFleeting(newAspect)

	def BuildBlockMap(self, bl):
		blkMap = {}
		for b in bl.values():
			tl = b.GetTrainLoc()
			for scrn, pos, _ in tl:
				lkey = (scrn, pos[1])
				if lkey not in blkMap.keys():
					blkMap[lkey] = []
				blkMap[lkey].append((pos[0], b))

		return blkMap

	def AddHilitedTrain(self, tr):
		self.hilitedTrains.append([tr, 8])

	def onTicker(self, _):
		self.tickerFlag = not self.tickerFlag
		if self.tickerFlag:
			# call 1sec every other time to simulate a 1-second timer
			self.onTicker1Sec()
			
		self.tickerCount += 1
		if self.tickerCount == 120:
			self.tickerCount = 0
			self.onTicker1Min()

		nh = []
		for tx in range(len(self.hilitedTrains)):
			tr, ticks = self.hilitedTrains[tx]
			ticks -= 1
			if ticks <= 0:
				tr.SetHilite(False)
			else:
				tr.SetHilite(True if ticks % 2 == 0 else False)
				nh.append([tr, ticks])
		self.hilitedTrains = nh

		if self.hiliteRouteTicker > 0:
			self.hiliteRouteTicker -= 1
			if self.hiliteRouteTicker == 0:
				self.ClearHighlitedRoute(None)

		self.delayedRequests.CheckForExpiry(self.Request)
		self.delayedSignals.CheckForExpiry()

	def onTicker1Sec(self):
		self.ClearExpiredButtons()
		self.breakerDisplay.ticker()
		self.activeTrainsDlg.ticker()
		self.districts.ticker()
		
	def onTicker1Min(self):
		logging.info("ticker 1 minute, timevalue = %d" % self.timeValue )
		if self.IsDispatcher():
			if self.ToD:
				self.timeValue = self.GetToD()
				self.DisplayTimeValue()
			else:
				if self.clockRunning:
					self.timeValue += 1
					self.DisplayTimeValue()

	def ClearExpiredButtons(self):
		collapse = False
		for b in self.buttonsToClear:
			b[0] -= 1
			if b[0] <= 0:
				b[1].Release(refresh=True)
				collapse = True

		if collapse:
			self.buttonsToClear = [x for x in self.buttonsToClear if x[0] > 0]

	def ClearButtonAfter(self, secs, btn):
		self.buttonsToClear.append([secs, btn])

	def ClearButtonNow(self, btn):
		bnm = btn.GetName()
		collapse = False
		for bx in range(len(self.buttonsToClear)):
			if self.buttonsToClear[bx][1].GetName() == bnm:
				self.buttonsToClear[bx][0] = 0
				self.buttonsToClear[bx][1].Release(refresh=True)
				collapse = True

		if collapse:
			self.buttonsToClear = [x for x in self.buttonsToClear if x[0] > 0]

	def ResetButtonExpiry(self, secs, btn):
		bnm = btn.GetName()
		for bx in range(len(self.buttonsToClear)):
			if self.buttonsToClear[bx][1].GetName() == bnm:
				self.buttonsToClear[bx][0] = secs

	def ProcessClick(self, screen, pos, rawpos, shift=False, right=False, screenpos=None):
		self.SetShift(False, propagate=True)
		# ignore screen clicks if not connected
		if not self.subscribed:
			return

		#logging.debug("%s click %s %d, %d %s" % ("right" if right else "left", screen, pos[0], pos[1], "shift" if shift else ""))
		try:
			to = self.turnoutMap[(screen, pos)]
		except KeyError:
			to = None

		if to:
			if right:  # provide turnout status
				self.ShowTurnoutInfo(to)
				return
			
			if to.IsDisabled():
				return

			if self.IsDispatcherOrSatellite():
				to.GetDistrict().TurnoutClick(to, force=shift)
			return

		try:
			to = self.disabledTurnoutMap[(screen, pos)]
		except KeyError:
			to = None

		if to:
			if right:  # provide turnout status
				self.ShowTurnoutInfo(to)
				return
			return

		try:
			btn = self.buttonMap[(screen, pos)]
		except KeyError:
			btn = None

		if btn:
			if right or shift:  # only process left clicks here
				return
			
			if self.IsDispatcherOrSatellite():
				btn.GetDistrict().ButtonClick(btn)
			return

		try:
			sig = self.signalMap[(screen, pos)]
		except KeyError:
			sig = None

		if sig:
			if right:  # provide signal status
				if sig.IsLocked():
					l = sig.GetLockedBy()
					lockers = "Locked" if len(l) == 0 else ("Locked: %s" % ", ".join(l))
				else:
					lockers = ""
					
				signm = sig.GetName()
				lvrNames = re.findall('[A-Z]+[0-9]+', signm)
				lvrState = ""
				if len(lvrNames) == 1:
					sl = self.Get("signallevers", {})
					if lvrNames[0] in sl:
						lvrState = " - Lever: %s" % self.formatSigLvr(sl[lvrNames[0]])

				self.PopupAdvice("%s -  %s   %s%s" % (sig.GetName(), sig.GetAspectName(), lockers, lvrState), force=True)
				return
			
			if sig.IsDisabled():
				return

			if self.IsDispatcherOrSatellite():
				sig.GetDistrict().SignalClick(sig, callon=shift)
			return

		try:
			hs = self.handswitchMap[(screen, pos)]
		except KeyError:
			hs = None

		if hs:
			if right or shift:  # only process left clicks here
				return
			
			if hs.IsDisabled():
				return
			
			if self.IsDispatcherOrSatellite():
				(hs.GetDistrict().HandSwitchClick(hs))
			return

		try:
			ln = self.blockMap[(screen, pos[1])]
		except KeyError:
			ln = None

		if ln:
			for col, blk in ln:
				if col <= pos[0] <= col+3:
					if blk.IsInActiveRoute(col, pos[1]):
						break
			else:
				blk = None

			if blk:
				if blk.IsOccupied():
					tr = blk.GetTrain()
					if tr is None:
						logging.error("Block %s is occupied, but get train returned None" % blk.GetName())
						return

					if not right:
						self.EditTrain(tr, blk)

					else: # pop-up menu
						menuPos = (screenpos[0], screenpos[1] + 90)
						self.PopupTrainMenu(self, tr, blk, menuPos)

				return

		if self.CTCManager is not None:
			self.CTCManager.CheckHotSpots(self.currentScreen, rawpos[0], rawpos[1])

	def PopupTrainMenu(self, owner, tr, blk, menuPos):
		if owner != self:
			dpos = owner.GetPosition()  # this is the position of the dialog box that invoked the menu
			wpos = self.GetPosition()   # this is the position of the main window
			pos = [menuPos[i] + dpos[i] - wpos[i] for i in range(2)]
			pos[1] += 30

		else:
			pos = [x for x in menuPos]

		trid = tr.Name()
		rname = tr.RName()
		sequence = self.GetTrainSequence(rname)

		menu = wx.Menu()
		self.menuTrain = tr
		self.menuTrainID = trid
		self.menuBlock = tr.FrontBlock() if blk is None else blk

		itm = wx.MenuItem(menu, MENU_TRAIN_EDIT, "Edit train name/loco/engineer")
		itm.SetFont(self.menuFont)
		menu.Append(itm)
		self.Bind(wx.EVT_MENU, self.OnTrainEdit, id=MENU_TRAIN_EDIT)

		if sequence is not None:
			itm = wx.MenuItem(menu, MENU_TRAIN_ROUTE, "Route Train")
			itm.SetFont(self.menuFont)
			menu.Append(itm)
			self.Bind(wx.EVT_MENU, self.OnTrainRoute, id=MENU_TRAIN_ROUTE)

		menu.AppendSeparator()

		itm = wx.MenuItem(menu, MENU_TRAIN_SPLIT, "Split train into two trains")
		itm.SetFont(self.menuFont)
		menu.Append(itm)
		self.Bind(wx.EVT_MENU, self.OnTrainSplit, id=MENU_TRAIN_SPLIT)

		itm = wx.MenuItem(menu, MENU_TRAIN_MERGE, "Merge two trains into 1")
		itm.SetFont(self.menuFont)
		menu.Append(itm)
		self.Bind(wx.EVT_MENU, self.OnTrainMerge, id=MENU_TRAIN_MERGE)

		menu.AppendSeparator()

		itm = wx.MenuItem(menu, MENU_TRAIN_SWAP, "Swap train name with another train")
		itm.SetFont(self.menuFont)
		menu.Append(itm)
		self.Bind(wx.EVT_MENU, self.OnTrainSwap, id=MENU_TRAIN_SWAP)

		itm = wx.MenuItem(menu, MENU_TRAIN_REVERSE, "Reverse the train direction")
		itm.SetFont(self.menuFont)
		menu.Append(itm)
		self.Bind(wx.EVT_MENU, self.OnTrainReverse, id=MENU_TRAIN_REVERSE)

		itm = wx.MenuItem(menu, MENU_TRAIN_REORDER, "Reorder train blocks")
		itm.SetFont(self.menuFont)
		menu.Append(itm)
		self.Bind(wx.EVT_MENU, self.OnTrainReorder, id=MENU_TRAIN_REORDER)

		menu.AppendSeparator()

		if sequence is not None:
			itm = wx.MenuItem(menu, MENU_TRAIN_HILITE, "Highlight Train Route")
			itm.SetFont(self.menuFont)
			menu.Append(itm)
			self.Bind(wx.EVT_MENU, self.OnTrainHilite, id=MENU_TRAIN_HILITE)

		itm = wx.MenuItem(menu, MENU_TRAIN_LOCATE, "Locate Train")
		itm.SetFont(self.menuFont)
		menu.Append(itm)
		self.Bind(wx.EVT_MENU, self.OnTrainLocate, id=MENU_TRAIN_LOCATE)

		if self.IsDispatcher():
			if self.ATCEnabled:
				if tr.IsOnATC():
					menu.AppendSeparator()

					itm = wx.MenuItem(menu, MENU_ATC_REMOVE, "Remove from ATC")
					itm.SetFont(self.menuFont)
					menu.Append(itm)
					self.Bind(wx.EVT_MENU, self.OnATCRemove, id=MENU_ATC_REMOVE)
					itm = wx.MenuItem(menu, MENU_ATC_STOP, "ATC Stop/Resume Train")
					itm.SetFont(self.menuFont)
					menu.Append(itm)
					self.Bind(wx.EVT_MENU, self.OnATCStop, id=MENU_ATC_STOP)
				else:
					loco = tr.GetLoco()
					if loco != "??":
						menu.AppendSeparator()

						itm = wx.MenuItem(menu, MENU_ATC_ADD, "Add to ATC")
						itm.SetFont(self.menuFont)
						menu.Append(itm)
						self.Bind(wx.EVT_MENU, self.OnATCAdd, id=MENU_ATC_ADD)

			if self.AREnabled:
				menu.AppendSeparator()

				if tr.IsOnAR():
					itm = wx.MenuItem(menu, MENU_AR_REMOVE, "Remove from Auto Router")
					itm.SetFont(self.menuFont)
					menu.Append(itm)
					self.Bind(wx.EVT_MENU, self.OnARRemove, id=MENU_AR_REMOVE)
				else:
					itm = wx.MenuItem(menu, MENU_AR_ADD, "Add to Auto Router")
					itm.SetFont(self.menuFont)
					menu.Append(itm)
					self.Bind(wx.EVT_MENU, self.OnARAdd, id=MENU_AR_ADD)

		self.PopupMenu(menu, pos)

		menu.Destroy()

	def GetTrainSequence(self, rname):
		if rname is None or rname not in self.trainRoster:
			return None

		roster = self.trainRoster[rname]
		if 'sequence' in roster and len(roster['sequence']) > 0:
			return roster['sequence']

		if 'template' in roster and roster['template'] is not None:
			tname = roster['template']
			if tname not in self.trainRoster:
				logging.error("Template train %s for train %s does not exist" % (tname, rname))
				return None
			roster = self.trainRoster[tname]
			return roster['sequence']

		return None

	def OnTrainEdit(self, _):
		self.EditTrain(self.menuTrain, self.menuBlock)

	def OnTrainRoute(self, _):
		self.RouteTrain(self.menuTrain)

	def OnTrainHilite(self, _):
		self.ShowHilitedRoute(self.menuTrain, self.menuTrainID)

	def OnTrainLocate(self, _):
		if self.menuTrain.SetHilite(True):
			self.AddHilitedTrain(self.menuTrain)

	def OnTrainSplit(self, _):
		pass
		# blockDict = self.menuTrain.GetBlockList()
		# blockOrder = self.menuTrain.GetBlockOrderList()
		# blockList = list(reversed([blockDict[b].GetRouteDesignator() for b in blockOrder]))
		# routeMap = {blockDict[b].GetRouteDesignator(): b for b in blockOrder}
		# if len(blockList) == 1:
		# 	dlg = wx.MessageDialog(self, "Train occupies only 1 block", "Unable to split train",
		# 						   wx.OK | wx.ICON_INFORMATION)
		# 	dlg.ShowModal()
		# 	dlg.Destroy()
		# 	return
		#
		# blist = []
		# dlg = ChooseBlocksDlg(self, self.menuTrainID, blockList)
		# dlg.CenterOnScreen()
		# lrc = dlg.ShowModal()
		# if lrc == wx.ID_OK:
		# 	blist = list(reversed(dlg.GetResults()))
		# dlg.Destroy()
		#
		# if lrc != wx.ID_OK:
		# 	return
		#
		# logging.info("Splitting following blocks from train %s: %s" % (self.menuTrainID, str(blist)))
		#
		# newTr = Train()
		# east = self.menuTrain.GetEast()
		# newTr.SetEast(east)
		# newName = newTr.GetName()
		# newLoco = newTr.GetLoco()
		#
		# newTr.SetBeingEdited(True)
		#
		# for rn in blist:
		# 	bn = routeMap[rn]
		# 	b = blockDict[bn]
		# 	self.menuTrain.RemoveFromBlock(b)
		# 	newTr.AddToBlock(b, 'front')
		# 	b.SetTrain(newTr)
		# 	b.SetEast(east)
		# 	self.CheckTrainsInBlock(b.GetName(), None)
		#
		# self.Request({"settrain": {"blocks": blist}})
		# self.Request(
		# 	{"settrain": {"blocks": blist, "name": newName, "loco": newLoco, "east": "1" if east else "0"}})
		#
		# self.trains[newName] = newTr
		#
		# self.SendTrainBlockOrder(self.menuTrain)
		# self.SendTrainBlockOrder(newTr)

		# self.menuTrain.ValidateStoppingSections()
		# newTr.ValidateStoppingSections()

		# self.activeTrains.AddTrain(newTr)
		# self.activeTrains.UpdateTrain(self.menuTrain)

		# if self.menuTrain.IsInNoBlocks():
		# 	try:
		# 		self.activeTrains.RemoveTrain(self.menuTrainID)
		# 	except:
		# 		logging.warning("can't delete train %s from active train list" % self.menuTrainID)
		# 	try:
		# 		del self.trains[self.menuTrainID]
		# 	except:
		# 		logging.warning("can't delete train %s from train list" % self.menuTrainID)
		#
		# else:
		# 	self.menuTrain.Draw()
		#
		# newTr.Draw()

	def OnTrainMerge(self, _):
		pass
		# trList = [t for t in self.trains.keys() if t != self.menuTrainID]
		# if len(trList) == 0:
		# 	dlg = wx.MessageDialog(self, "No other trains to merge with", "Unable to merge train",
		# 						   wx.OK | wx.ICON_INFORMATION)
		# 	dlg.ShowModal()
		# 	dlg.Destroy()
		# 	return
		#
		# dlg = ChooseTrainDlg(self, self.menuTrainID, trList)
		# dlg.CenterOnScreen()
		# lrc = dlg.ShowModal()
		# if lrc == wx.ID_OK:
		# 	trxid = dlg.GetResults()
		# else:
		# 	trxid = None
		# dlg.Destroy()
		# if lrc != wx.ID_OK:
		# 	return
		#
		# if trxid is None:
		# 	self.PopupEvent("No train chosen for merge operation - ignoring request")
		# 	return
		#
		# trx = self.trains[trxid]
		#
		# east = self.menuTrain.GetEast()  # assume the direction of the surviving train
		#
		# blist = [x for x in trx.GetBlockOrderList()]
		# for blkNm in blist:
		# 	blk = self.blocks[blkNm]
		# 	trx.RemoveFromBlock(blk)
		# 	self.menuTrain.AddToBlock(blk, REAR)
		# 	blk.SetTrain(self.menuTrain)
		# 	blk.SetEast(east)
		# 	self.CheckTrainsInBlock(blk.GetName(), None)
		#
		# # set the block list for the surviving train
		# blist = [x for x in self.menuTrain.GetBlockOrderList()]
		# self.Request(
		# 	{"settrain": {"blocks": blist, "name": self.menuTrainID, "loco": self.menuTrain.GetLoco(), "east": "1" if east else "0"}})
		#
		# self.SendTrainBlockOrder(self.menuTrain)
		# self.menuTrain.ValidateStoppingSections()
		# self.activeTrains.UpdateTrain(self.menuTrainID)
		#
		# self.Request({"deletetrain": {"name": trxid}})
		#
		# self.menuTrain.Draw()

	def OnTrainReverse(self, _):
		self.Request({"trainreverse": {"train": self.menuTrain.IName()}})

	def OnTrainReorder(self, _):
		if self.menuTrain.BlockCount() <= 1:
			dlg = wx.MessageDialog(self, "Train occupies < 2 blocks", "Unable to reorder blocks", wx.OK | wx.ICON_INFORMATION)
			dlg.ShowModal()
			dlg.Destroy()
			return

		bl = [b for b in self.menuTrain.Blocks()]
		self.PopupAdvice("orig ordering: %s" % (", ".join(bl)))

		dlg = SortTrainBlocksDlg(self, self.menuTrain, self.blocks)
		dlg.CenterOnScreen()
		lrc = dlg.ShowModal()
		neworder = []
		if lrc == wx.ID_OK:
			neworder = dlg.GetResults()

		dlg.Destroy()

		self.PopupAdvice("New ordering: %s" % (", ".join(neworder)))
		# if lrc != wx.ID_OK:
		# 	return
		#
		# self.menuTrain.SetBlockOrder(neworder)
		# blk = self.menuTrain.FrontBlock()
		# if blk is not None:
		# 	self.CheckTrainsInBlock(blk.GetName(), None)
		#
		# self.activeTrains.RefreshTrain(self.menuTrainID)
		# self.SendTrainBlockOrder(self.menuTrain)

	@staticmethod
	def BuildTrainKey(trid):
		if trid.startswith("??"):
			return "ZZ%s" % trid
		else:
			return "AA%s" % trid

	def OnTrainSwap(self, _):
		pass
		# trList = sorted([t for t in self.trains.keys() if t != self.menuTrainID], key=self.BuildTrainKey)
		#
		# if len(trList) == 0:
		# 	dlg = wx.MessageDialog(self, "No other trains to swap with", "Unable to swap trains",
		# 						   wx.OK | wx.ICON_INFORMATION)
		# 	dlg.ShowModal()
		# 	dlg.Destroy()
		# 	return
		#
		# dlg = ChooseTrainDlg(self, self.menuTrainID, trList, merge=False)
		# dlg.CenterOnScreen()
		# lrc = dlg.ShowModal()
		# if lrc == wx.ID_OK:
		# 	trxid = dlg.GetResults()
		# else:
		# 	trxid = None
		# dlg.Destroy()
		# if lrc != wx.ID_OK:
		# 	return
		#
		# if trxid is None:
		# 	self.PopupEvent("No train chosen for swap operation - ignoring request")
		# 	return
		#
		# trx = self.trains[trxid]
		# menuRoute = self.menuTrain.GetChosenRoute()
		# trxRoute = trx.GetChosenRoute()
		#
		# tempName = Train.NextName()
		# self.Request({"renametrain": {"oldname": self.menuTrainID, "newname": tempName, "context": "rename"}})
		# self.Request({"renametrain": {"oldname": trxid, "newname": self.menuTrainID, "newroute": menuRoute, "context": "rename"}})
		# self.Request({"renametrain": {"oldname": tempName, "newname": trxid, "newroute": trxRoute, "context": "rename"}})
		#
		# self.menuTrain.Draw()
		# trx.Draw()
		#
		# self.activeTrains.UpdateTrain(self.menuTrainID)
		# self.activeTrains.UpdateTrain(trxid)

	def ShowHilitedRoute(self, tr, trid):
		pass
		# try:
		# 	trinfo = self.trainList[trid]
		# except KeyError:
		# 	rte = tr.GetChosenRoute()
		# 	if rte is None:
		# 		self.PopupEvent("Train %s has no block sequence defined" % trid)
		# 		return
		#
		# 	try:
		# 		trinfo = self.trainList[rte]
		# 	except KeyError:
		# 		self.PopupEvent("Base train %s has no block sequence defined" % rte)
		# 		return
		#
		# routeTiles = self.EnumerateBlockTiles(trinfo["startblock"])
		# for step in trinfo["sequence"]:
		# 	routeTiles.extend(self.EnumerateOSTiles(step["os"], step["route"]))
		# 	routeTiles.extend(self.EnumerateBlockTiles(step["block"]))
		#
		# self.SetHighlitedRoute("MAIN", routeTiles, ticker=14)

	def formatSigLvr(self, data):
		dl = 0 if data[0] is None else data[0]
		dc = 0 if data[1] is None else data[1]
		dr = 0 if data[2] is None else data[2]
		
		callon = " C" if dc != 0 else "  "
		
		if dl != 0 and dr == 0:
			return "L" + callon
		elif dl == 0 and dr != 0:
			return "R" + callon
		elif dl == 0 and dr == 0:
			return "N" + callon
		else:
			return "?" + callon
		
	def OnTrainRouting(self, _):
		self.RouteTrain(self.menuTrain)
		
	def RouteTrain(self, tr):
		trainid, _ = tr.GetNameAndLoco()
		if trainid in self.routeTrainDlgs:
			self.routeTrainDlgs[trainid].Raise()
		else:
			try:
				trinfo = self.trainList[trainid]
				rtName = None
				if "route" in trinfo and trinfo["route"] is not None and trinfo["route"] != "":
					rtName = tr.GetChosenRoute()
					trinfo = self.trainList[rtName]
			except (IndexError, KeyError):
				rtName = tr.GetChosenRoute()
				try:
					trinfo = self.trainList[rtName]
				except KeyError:
					trinfo = None

			# noinspection PyTypeChecker
			if trinfo is None or "sequence" not in trinfo or len(trinfo["sequence"]) == 0:
				dlg = wx.MessageDialog(self, "Train does not have a block sequence defined",
						"No Sequence Defined", wx.OK | wx.ICON_INFORMATION)
				dlg.ShowModal()
				dlg.Destroy()
			else:
				dlg = RouteTrainDlg(self, tr, rtName, trinfo, self.IsDispatcherOrSatellite())
				dlg.Show()
				self.routeTrainDlgs[trainid] = dlg
				dlg.UpdateTrainStatus()
			
	def UpdateRouteDialog(self, tid):
		try:
			dlg = self.routeTrainDlgs[tid]
		except KeyError:
			return
		
		dlg.UpdateTrainStatus()

	def GetTrainObject(self, trid):
		pass
		# return self.activeTrains.GetTrain(trid)

	def EnumerateBlockTiles(self, blkname):
		try:
			blk = self.blocks[blkname]
		except KeyError:
			return []

		tl = blk.GetTiles() + blk.GetSBTiles()
		tol = blk.GetTurnoutLocations()

		tloc = [[t[1], t[2]] for t in tl] + tol

		return tloc

	def EnumerateOSTiles(self, osname, rtname):
		try:
			desiredRoute = self.routes[rtname]
		except KeyError:
			return []

		scr, pos = desiredRoute.GetPositions()
		return [[scr, p] for p in pos]

	def SetHighlitedRoute(self, name, routeTiles, ticker=0):
		for tid in self.routeTrainDlgs:
			if tid != name:
				self.routeTrainDlgs[tid].ClearHiliteFlag()

		self.hilitedRoute = name
		tiles = {}
		for scr, pos in routeTiles:
			offset = self.diagrams[scr].offset
			if scr not in tiles:
				tiles[scr] = []
			tiles[scr].append([pos[0]*16+offset, pos[1]*16])

		for scr in tiles:
			self.panels[scr].SetHighlitedRoute(tiles)
		self.hiliteRouteTicker = ticker

	def ClearHighlitedRoute(self, name=None):
		if name is None:
			name = self.hilitedRoute

		if name is None:
			return

		if name == self.hilitedRoute:
			self.hilitedRoute = None
			for p in self.panels.values():
				p.ClearHighlitedRoute()

	def SetRouteThruOS(self, osname, rtname, blkname, signame):
		osblk = self.blocks[osname]
		OSClear = osblk.IsCleared()	
		currentRoute = osblk.GetRoute()
		desiredRoute = self.routes[rtname]
		
		# determine all route characteristics
		ends = desiredRoute.GetEndPoints()
		if ends[0] == blkname:
			exitBlk = ends[0]
		else:
			exitBlk = ends[1]

		if exitBlk in self.blocks:
			b = self.blocks[exitBlk]
			exitState = b.GetStatus()
			exitClear = b.IsCleared()
			for sbNm in [exitBlk+".E", exitBlk+".W"]:
				if sbNm in self.blocks:
					sb = self.blocks[sbNm]
					exitState += sb.GetStatus()
					exitClear += sb.IsCleared()
					
		else:
			exitState = 0
			exitClear = 0
			
		if currentRoute is not None and currentRoute.GetName() == rtname:
			return True, True, "Already at correct route"
		
		if (currentRoute is None or currentRoute.GetName() != rtname) and OSClear:
			return False, False, "Unable to set route at present"

		if exitState != 0 or exitClear != 0:
			return False, False, "Unable to set route at present"
					
		if currentRoute is not None and currentRoute.GetName() == rtname and not OSClear and exitState != 0:
			return False, False, "Unable to set route at present"
		
		tolist = desiredRoute.GetSetTurnouts()
		for toname, wantedState in tolist:
			trn = self.turnouts[toname]
			wantedNormal = wantedState == "N"
			if trn.IsLocked() and wantedNormal != trn.IsNormal():
				return False, False, "Turnout %s is locked and not in wanted state (%s)" % (toname, wantedState)

		district = osblk.GetDistrict()
		district.SetUpRoute(osblk, desiredRoute)
		return True, False, None
		
	def SetRouteSignal(self, osname, rtname, blkname, signame, silent=False):
		osblk = self.blocks[osname]
		currentRoute = osblk.GetRoute()
		signal = self.signals[signame]
			
		if currentRoute is None or currentRoute.GetName() != rtname:
			return False, "Incorrect route, Set route first"
		
		aspect = signal.GetAspect()
		if aspect != 0:
			return True, "Signal already permits movement"
			
		district = osblk.GetDistrict()
		rc = district.PerformSignalAction(signal, silent=silent)
		return rc, None

	def DelaySignalRequest(self, signm, osnm, rtnm, maxtime):
		self.delayedSignals.Append(signm, osnm, rtnm, maxtime)

	def CloseRouteTrainDlg(self, trainid):
		if trainid in self.routeTrainDlgs:
			self.routeTrainDlgs[trainid].Destroy()
			del(self.routeTrainDlgs[trainid])
		if trainid == self.hilitedRoute:
			self.ClearHighlitedRoute(trainid)
						
	def EditTrain(self, tr, blk):
		oldName = tr.Name()
		oldLoco = tr.Loco()
		oldEngineer = tr.Engineer()
		oldTemplateTrain = tr.TemplateTrain()
		oldATC = tr.ATC() if self.IsDispatcher() else False
		oldAR = tr.AR() if self.IsDispatcher() else False
		oldEast = tr.IsEast()

		blknm = blk.GetName()
		if blknm in ["R10", "F10"] and oldName.startswith("??"):
			bl = self.lostTrains.GetBranchLineTrain(blknm, tr.GetEast())
		else:
			bl = None

		rc = wx.ID_NO
		if bl is not None:
			loc = "Harper's Ferry/James Island" if not bl[3] else "Wilson City"
			dlg = ConfirmBranchLineTrainDlg(self, bl[0], bl[1], bl[2], loc)
			dlg.CenterOnScreen()
			rc = dlg.ShowModal()
			dlg.Destroy()

		if rc == wx.ID_YES:
			trainid, locoid, engineer, east, _, templateTrain = bl
			self.lostTrains.ClearBranchLine(trainid)
			atc = False
			ar = False

		else:
			dlgx = self.centerw - 500 - self.centerOffset
			dlgy = self.totalh - 660
			dlg = EditTrainDlg(self, tr, blk, self.locoList, self.trainRoster, self.engineerList, self.trains,
						self.IsDispatcher() and self.ATCEnabled,
						self.IsDispatcher() and self.AREnabled,
						self.IsDispatcherOrSatellite(),
						self.lostTrains, self.trainHistory, self.preloadedTrains, dlgx, dlgy)
			rc = dlg.ShowModal()
			east = tr.IsEast()
			if rc == wx.ID_OK:
				trainid, locoid, engineer, atc, ar, east, templateTrain = dlg.GetResults()

			dlg.Destroy()

			if rc != wx.ID_OK:
				return

		parms = {"iname": tr.IName(), "name": trainid, "loco": locoid, "template": templateTrain, "east": "1" if east else "0", "engineer": engineer}

		# if self.IsDispatcher() and atc != oldATC:
		# 	if self.VerifyTrainID(trainid) and self.VerifyLocoID(locoid):
		# 		parms.update({"action": "add" if atc else "remove", "train": trainid, "loco": locoid})
		#
		# if self.IsDispatcher() and ar != oldAR:
		# 	if self.VerifyTrainRoute(trainid):
		# 		parms.update({"action": "add" if ar else "remove", "train": trainid})

		self.Request({"modifytrain": parms})

	def SendTrainBlockOrder(self, tr):
		self.Request({"trainblockorder": tr.GetBlockOrder()})

	def StealTrainID(self, trid):
		pass
		# logging.info("Removing train ID %s" % trid)
		# tr = self.trains[trid]
		#
		# newTr = Train()
		# east = tr.GetEast()
		# newTr.SetEast(east)
		# newName = newTr.GetName()
		# newLoco = tr.GetLoco()
		#
		# blockDict = tr.GetBlockList()
		# blockList = [b for b in blockDict.keys()]  # if b != bname
		#
		# for bn in blockList:
		# 	b = blockDict[bn]
		# 	tr.RemoveFromBlock(b)
		# 	newTr.AddToBlock(b, 'front')
		# 	b.SetTrain(newTr)
		# 	b.SetEast(east)
		# 	self.CheckTrainsInBlock(b.GetName(), None)
		#
		# self.Request({"settrain": {"blocks": blockList}})
		# self.Request(
		# 	{"settrain": {"blocks": blockList, "name": newName, "loco": newLoco, "east": "1" if east else "0"}})
		#
		# self.trains[newName] = newTr
		# self.SendTrainBlockOrder(newTr)
		# self.SendTrainBlockOrder(tr)
		#
		# self.activeTrains.AddTrain(newTr)

	def RecoverLostTrains(self):
		pass
		# ltList = self.lostTrains.GetList()
		# recoverable = []
		# for trid, locoid, engineer, east, block, route in ltList:
		# 	if self.blocks[block].HasUnknownTrain():
		# 		recoverable.append([trid, locoid, engineer, east, block, route])
		#
		# if len(recoverable) == 0:
		# 	self.PopupAdvice("No trains to recover")
		# 	return
		#
		# dlg = LostTrainsRecoveryDlg(self, recoverable)
		# rc = dlg.ShowModal()
		# if rc == wx.ID_OK:
		# 	torecover = dlg.GetResult()
		#
		# dlg.Destroy()
		# if rc != wx.ID_OK:
		# 	return
		#
		# for trid, locoid, engineer, east, block, route in torecover:
		# 	if self.blocks[block].HasUnknownTrain():
		# 		tr = self.blocks[block].GetTrain()
		# 		oldName, oldLoco = tr.GetNameAndLoco()
		# 		oldRoute = tr.GetChosenRoute()
		# 		self.PopupAdvice("Recovering train %s/%s in block %s.  Assign to %s" % (trid, locoid, block, engineer))
		# 		self.Request({"renametrain": { "oldname": oldName, "newname": trid, "oldloco": oldLoco, "newloco": locoid, "oldroute": oldRoute, "newroute": route, "east": "1" if east else "0", "context": "recover"}})
		#
		# 		tr.SetEngineer(engineer)
		# 		self.activeTrains.UpdateTrain(trid)
		# 		parms = {"train": trid, "reassign": 0, "engineer": engineer}
		# 		req = {"assigntrain": parms}
		# 		self.Request(req)
		#
		# 		self.lostTrains.Remove(trid)
						
	def ShowTurnoutInfo(self, to):
		if to.GetType() == SLIPSWITCH:
			st = to.GetStatus()
			if len(st) == 2:
				state = "%s/%s" % (turnoutstate(st[0], short=True), turnoutstate(st[1], short=True))
			else:
				state = "??"
		else:
			state = "Normal" if to.IsNormal() else "Reversed"

		top = to.GetPaired()
		parms = {"name": to.GetName()}
		if top is not None:
			parms["pname"] = top.GetName()
		lockinfo = self.Get("turnoutlock", parms)

		try:
			lockers = lockinfo["turnoutlock"]["lockers"]
		except KeyError:
			lockers = []

		lockstate = "Locked" if to.IsLocked() else "Unlocked"

		if len(lockers) > 0:
			lockstate += "  (%s)" % ", ".join(lockers)

		self.PopupAdvice("%s - %s   %s" % (to.GetName(), state, lockstate), force=True)

	def VerifyTrainID(self, trainid):
		if trainid is None or trainid.startswith("??"):
			self.PopupEvent("Train ID is required")
			return False
		return True

	def VerifyTrainRoute(self, trainid):
		if trainid is None:
			self.PopupEvent("Train ID is required")
			return False

		tr = self.trains[trainid]
		hasSequence = ((trainid in self.trainList and len(self.trainList[trainid]["sequence"]) > 0)
					or (tr.GetChosenRoute() is not None))
		if not hasSequence:
			self.PopupEvent("Train does not has a block sequence defined")
		return hasSequence

	def VerifyLocoID(self, locoid):
		if locoid is None or locoid.startswith("??"):
			self.PopupEvent("locomotive ID is required")
			return False
		
		return True
	
	def OnATCAdd(self, _):
		pass
		# trainid, locoid = self.menuTrain.GetNameAndLoco()
		# if self.VerifyTrainID(trainid) and self.VerifyLocoID(locoid):
		# 	self.menuTrain.SetATC(True)
		# 	self.activeTrains.UpdateTrain(trainid)
		# 	self.Request({"atc": {"action": "add", "train": trainid, "loco": locoid}})
		# 	self.menuTrain.Draw()

	def OnATCRemove(self, evt):
		pass
		# trainid, locoid = self.menuTrain.GetNameAndLoco()
		# if self.VerifyTrainID(trainid) and self.VerifyLocoID(locoid):
		# 	self.menuTrain.SetATC(False)
		# 	self.activeTrains.UpdateTrain(trainid)
		# 	self.Request({"atc": {"action": "remove", "train": trainid, "loco": locoid}})
		# 	self.menuTrain.Draw()

	def OnATCStop(self, evt):
		pass
		# trainid, locoid = self.menuTrain.GetNameAndLoco()
		# if self.VerifyTrainID(trainid) and self.VerifyLocoID(locoid):
		# 	self.Request({"atc": {"action": "forcestop", "train": trainid, "loco": locoid}})
		
	def OnARAdd(self, evt):
		pass
		# trainid = self.menuTrain.GetName()
		# if self.VerifyTrainRoute(trainid):
		# 	self.menuTrain.SetAR(True)
		# 	self.activeTrains.UpdateTrain(trainid)
		# 	self.Request({"ar": {"action": "add", "train": trainid}})
		# 	self.menuTrain.Draw()

	def OnARRemove(self, evt):
		pass
		# trainid = self.menuTrain.GetName()
		# if self.VerifyTrainRoute(trainid):
		# 	self.menuTrain.SetAR(False)
		# 	self.activeTrains.UpdateTrain(trainid)
		# 	self.Request({"ar": {"action": "remove", "train": trainid}})
		# 	self.menuTrain.Draw()
							
	def DrawTile(self, screen, pos, bmp):
		offset = self.diagrams[screen].offset
		self.panels[screen].DrawTile(pos[0], pos[1], offset, bmp)

	def DrawText(self, screen, pos, text):
		offset = self.diagrams[screen].offset
		self.panels[screen].DrawText(pos[0], pos[1], offset, text)

	def ClearText(self, screen, pos):
		offset = self.diagrams[screen].offset
		self.panels[screen].ClearText(pos[0], pos[1], offset)

	def DrawTrain(self, tr, delblocks):
		for b in delblocks:
			blk = self.blocks.get(b, None)
			if blk is None:
				blk = self.sbMap.get(b, None)
			if blk is None:
				self.PopupEvent("Unknown block %s in train %s" % (b, tr.Name()))
				self.PopupEvent("%s" % str(list(self.sbMap.keys())))
				continue
			for screen, pos, routes in blk.TrainLoc():
				tx = pos[0]
				ty = pos[1]
				offset = self.diagrams[screen].offset
				self.PopupEvent("Clearing train information in block %s at location %s:(%d, %d)" % (b, screen, tx, ty))
				self.panels[screen].ClearTrain(pos[0], pos[1], offset, tr.Name())

		for b in tr.Blocks():
			blk = self.blocks.get(b, None)
			if blk is None:
				blk = self.sbMap.get(b, None)
			if blk is None:
				self.PopupEvent("Unknown block %s in train %s" % (b, tr.Name()))
				continue

			for screen, pos, routes in blk.TrainLoc():
				tx = pos[0]
				ty = pos[1]
				offset = self.diagrams[screen].offset
				self.panels[screen].DrawTrain(pos[0], pos[1], offset, tr.Name(), tr.Loco(), tr.Stopped(), tr.ATC(), tr.AR(), False, False)  # stopRelay, atc, ar, hilite, mflag)

		if len(tr.Blocks()) == 0:
			self.PopupEvent("Train %s lost detection in block %s" % (tr.Name(), delblocks[0]))

	# self.panels[screen].DrawTrain(pos[0], pos[1], offset, trainID, locoID, stopRelay, atc, ar, hilite, mflag)

	def ClearTrain(self, screen, pos):
		offset = self.diagrams[screen].offset
		self.panels[screen].ClearTrain(pos[0], pos[1], offset)
		
	def CheckTrainsInBlock(self, blkNm, sig):
		# either a train is new in a block or the signal at the end of that block has changed.  See what trains are affected
		blk = self.GetBlockByName(blkNm)
		if blk is None:
			logging.info("Bad block name: %s" % blkNm)
			return 

		btype = blk.GetBlockType()
		if btype == BLOCK:
			if sig is None:
				# identify the signal for this block that matches the block's direction
				sigNm = blk.GetDirectionSignal()
				if sigNm is None:
					# no signal at the end of this block
					return
				sig = self.GetSignalByName(sigNm)
				if sig is None:
					return

		elif btype == OVERSWITCH:
			if sig is None:
				# get the entry signal for this OS block
				sig = blk.GetEntrySignal()
				if sig is None:
					return

		else:
			# for all other block types
			return

		# check for trains in the block.  If it is the front of the train, then this signal change applies to that train.
		for trid, tr in self.trains.items():
			if tr.FrontInBlock(blkNm):
				# we found a train
				ir, cr = self.CheckForIncorrectRoute(tr, sig)
				if cr is not None:
					tr.SetMisrouted(ir is not None)
				tr.SetSignal(sig)
				# self.activeTrains.UpdateTrain(trid)
				req = {"trainsignal": { "train": trid, "block": blkNm, "signal": sig.GetName(), "aspect": sig.GetAspect()}}
				self.Request(req)
				
	def SwapToScreen(self, screen):
		if screen == HyYdPt:
			self.bScreenHyYdPt.Enable(False)
			self.bScreenLaKr.Enable(True)
			self.bScreenNaCl.Enable(True)
		elif screen == LaKr:
			self.bScreenHyYdPt.Enable(True)
			self.bScreenLaKr.Enable(False)
			self.bScreenNaCl.Enable(True) 
		elif screen == NaCl:
			self.bScreenHyYdPt.Enable(True) 
			self.bScreenLaKr.Enable(True)
			self.bScreenNaCl.Enable(False) 
		else:
			return False

		if screen == self.currentScreen:
			return True
		self.panels[screen].Show()
		if self.currentScreen:
			self.panels[self.currentScreen].Hide()
		self.currentScreen = screen

		for scr in self.widgetMap:
			for w, app in self.widgetMap[scr]:
				if (app == 0 and self.IsDispatcher()) or (app == 1 and not self.IsDispatcher()):
					if scr == self.currentScreen:
						w.Show()
					else:
						w.Hide()
				else:
					w.Hide()

		# self.panels[screen].Refresh()
		return True

	def PlaceWidgets(self):
		for scr in self.widgetMap:
			if scr == HyYdPt:
				offset = 0
			elif scr == LaKr:
				offset = self.bmpw
			elif scr == NaCl:
				offset = self.bmpw*2
			else:
				offset = 0

			for w, app in self.widgetMap[scr]:
				if (app == 0 and self.IsDispatcher()) or (app == 1 and not self.IsDispatcher()):
					pos = w.GetPosition()
					pos[0] += offset
					w.SetPosition(pos)
					w.Show()
					
	def GetOSProxyInfo(self):
		counts = {}
		pnames = {}
		osnames = {}
		for pn, p in self.osProxies.items():
			rn, occ, osname = p.Evaluate()
			if rn and occ:
				counts[rn] = counts.get(rn, 0) + 1
				osnames[rn] = osname
				if rn in pnames:
					pnames[rn].append(pn)
				else:
					pnames[rn] = [pn]

		return {rn: {"count": counts[rn], "os": osnames[rn], "segments": pnames[rn]} for rn in counts.keys()}

	def GetHandswitchInfo(self):
		hsinfo = {hsname.split(".")[0]: self.handswitches[hsname].GetValue() for hsname in self.handswitches}
		return hsinfo

	def GetNodes(self):
		nv = [[n.Name(), n.Address(), n.IsEnabled()] for n in self.nodes.values()]
		return nv

	def GetBlockStatus(self, blknm):
		try:
			blk = self.blocks[blknm]
		except KeyError:
			return EMPTY

		return blk.GetStatus()

	def GetBlockByName(self, blknm):
		try:
			return self.blocks[blknm]
		except:
			return None

	def GetSignalByName(self, signm):
		try:
			return self.signals[signm]
		except:
			return None

	def ToasterSetup(self):
		self.events = Toaster()
		self.events.SetOffsets(0, 150)
		self.events.SetFont(wx.Font(wx.Font(20, wx.FONTFAMILY_ROMAN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, faceName="Arial")))
		self.events.SetBackgroundColour(wx.Colour(255, 179, 154))
		self.events.SetTextColour(wx.Colour(0, 0, 0))
		
		self.advice = Toaster()
		self.advice.SetOffsets(0, 150)
		self.advice.SetFont(wx.Font(wx.Font(20, wx.FONTFAMILY_ROMAN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, faceName="Arial")))
		self.advice.SetBackgroundColour(wx.Colour(120, 255, 154))
		self.advice.SetTextColour(wx.Colour(0, 0, 0))

	def DebugMessage(self, message):
		self.PopupEvent(message, force=True)

	def PopupEvent(self, message, force=False):
		if self.IsDispatcherOrSatellite() or self.settings.display.showevents or force:
			self.events.Append(message)
			self.eventsList.append(message)
			if self.dlgEvents is not None:
				self.dlgEvents.AddItem(message)
		
	def OnBEventsLog(self, _):
		if self.dlgEvents is None:
			self.dlgEvents = ListDlg(self, "Events List", self.eventsList, self.DlgEventsExit, self.DlgEventsClear)
			self.dlgEvents.CenterOnScreen()
			self.dlgEvents.Show()
			
	def DlgEventsClear(self):
		self.eventsList = []
			
	def DlgEventsExit(self):
		self.dlgEvents.Destroy()
		self.dlgEvents = None

	def PopupAdvice(self, message, force=False):
		if self.IsDispatcherOrSatellite() or self.settings.display.showadvice or force:
			self.advice.Append(message)
			self.adviceList.append(message)
			if self.dlgAdvice is not None:
				self.dlgAdvice.AddItem(message)
		
	def OnBAdviceLog(self, _):
		if self.dlgAdvice is None:
			self.dlgAdvice = ListDlg(self, "Advice List", self.adviceList, self.DlgAdviceExit, self.DlgAdviceClear)
			self.dlgAdvice.CenterOnScreen()
			self.dlgAdvice.Show()
			
	def DlgAdviceClear(self):
		self.adviceList = []
			
	def DlgAdviceExit(self):
		self.dlgAdvice.Destroy()
		self.dlgAdvice = None

	def OnBPreloaded(self, _):
		dlg = ManagePreloadedDlg(self, self.rrServer)
		rc = dlg.ShowModal()
		dlg.Destroy()
		if rc == wx.ID_OK:
			self.preloadedTrains.Reload()
			self.PopupEvent("Preloaded trains reloaded")

	def OnBSnapshot(self, _):
		dlg = ChooseSnapshotActionDlg(self)	
		rc = dlg.ShowModal()
		dlg.Destroy()
		if rc == wx.ID_SAVE:
			self.TakeSnapshot()
							
		elif rc in [wx.ID_OPEN, wx.ID_SELECTALL]: # restore from snapshot
			self.LoadSnapshot(rc)

	def LoadSnapshot(self, ldType, silent=False):
		snapList = self.Get("snaplist", {})
		if len(snapList) == 0:
			if not silent:
				dlg = wx.MessageDialog(self, "No Snapshots exist", "File Not Found", wx.OK | wx.ICON_WARNING)
				dlg.ShowModal()
				dlg.Destroy()
			return

		blks = [x for x in self.blocks.values() if x.IsOccupied()]
		blkNames = [b.GetName() for b in blks]

		if ldType == wx.ID_SELECTALL:
			dlg = ChooseSnapshotDlg(self, snapList)
			rc = dlg.ShowModal()
			sf = dlg.GetResults()
			dlg.Destroy()
			if rc != wx.ID_OK:
				return
			snapFile = sf
		else:
			snapFile = snapList[-1]

		self.PopupEvent("Using snapshot: %s" % snapFile)

		trjson = self.Get("getsnapshot", {"filename": snapFile})
		if trjson is None:
			dlg = wx.MessageDialog(self, "Snapshot %s does not exist" % snapFile, "File Not Found", wx.OK | wx.ICON_WARNING)
			dlg.ShowModal()
			dlg.Destroy()
			return

		foundTrainBlocks = []
		foundTrains = {}

		for trid, trinfo in trjson.items():
			blist = []
			for b in trinfo["blocks"]:
				if b in blkNames:
					blist.append(b)
					# first remove the block from the old train
					blk = self.blocks[b]
					otr = blk.GetTrain()
					if otr is None:
						self.PopupEvent("Unable to find train %s in block %s" % blk.GetName())
					else:
						otr.RemoveFromBlock(blk)
						self.SendTrainBlockOrder(otr)

						if otr.IsInNoBlocks():
							otrid = otr.GetName()
							try:
								# self.activeTrains.RemoveTrain(otrid)
								del self.trains[otrid]
							except:
								logging.warning("can't delete train %s from train list" % otrid)
						else:
							otr.Draw()
				else:
					self.PopupEvent("Block %s/Train %s in snapshot - not occupied" % (b, trid))

			if len(blist) == 0:
				self.PopupEvent("Train %s does not appear in any blocks - ignoring" % trid)
				continue

			# now if the new train does not yet exist - create it
			if trid not in self.trains:
				# we don't have a train of this name.  create one
				ntr = Train(trid)
				self.trains[trid] = ntr
				# self.activeTrains.AddTrain(ntr)
			else:
				ntr = self.trains[trid]

			try:
				rte = trinfo["route"]
				if rte is not None and rte not in self.trains:
					logging.debug("Route %s for train %s from snapshot %s does not exist" % (rte, trid, snapFile))
					rte = None
			except KeyError:
				rte = None

			ntr.SetChosenRoute(rte)

			# now add the block to the new train
			ntr.SetEast(trinfo["east"])
			for b in blist:
				blk = self.blocks[b]
				ntr.AddToBlock(blk, 'front')
				blk.SetEast(trinfo["east"])
				blk.Draw()

			foundTrainBlocks.extend(blist)
			foundTrains[trid] = 1
			ntr.Draw()

			self.Request({"settrain": { "blocks": blist, "silent": "1"}})
			self.Request({"settrain": { "blocks": blist, "name": trid, "loco": trinfo["loco"], "east": "1" if trinfo["east"] else "0", "route": rte}})

			# ntr = self.trains[trid]
			self.SendTrainBlockOrder(ntr)

		unknownBlocks = [b for b in blkNames if b not in foundTrainBlocks]
		if len(unknownBlocks) > 0:
			self.PopupEvent("Occupied Blocks not in snapshot: %s" % ", ".join(unknownBlocks))

		self.PopupEvent("%d trains restored from Snapshot" % len(foundTrains))

	def TakeSnapshot(self):
		pass
		# trinfo = self.activeTrains.forSnapshot()
		# lenTrInfo = len(trinfo)
		# if lenTrInfo == 0:
		# 	self.PopupEvent("No trains to save")
		# 	return
		#
		# rc, fn = self.rrServer.Post("snapshot.json", "data", trinfo)
		# if rc >= 400:
		# 	self.PopupEvent("Error saving snapshot")
		# else:
		# 	self.PopupEvent("%d trains saved in Snapshot %s" % (lenTrInfo, fn))
		
	def OnSubscribe(self, _):
		if self.subscribed:
			self.listener.kill()
			self.listener.join()
			self.listener = None
			self.subscribed = False
			self.sessionid = None
			self.bSubscribe.SetLabel("Connect")
			self.bRefresh.Enable(False)
			self.bActiveTrains.Enable(False)
			self.bLostTrains.Enable(False)
			self.activeTrainsDlg.Hide()
			self.bCheckTrains.Enable(False)

			if self.IsDispatcherOrSatellite():
				self.bLoadTrains.Enable(False)
				self.bLoadLocos.Enable(False)
				self.bSaveTrains.Enable(False)
				self.bClearTrains.Enable(False)
				self.bSaveLocos.Enable(False)
				self.bSnapshot.Enable(False)
				self.bPreloaded.Enable(False)
				if self.IsDispatcher():
					self.cbAutoRouter.Enable(False)
					self.cbATC.Enable(False)
					self.cbOSSLocks.Enable(False)
					self.cbSidingsUnlocked.Enable(False)
			else:
				self.ClearAllLocks()
				self.AllSignalsNeutral()
				self.AllBlocksNotClear()
			
		else:
			self.listener = Listener(self, self.settings.ipaddr, self.settings.socketport)
			if not self.listener.connect():
				logging.error("Unable to establish connection with server")
				self.listener = None
				return

			self.listener.start()
			self.subscribed = True
			self.bSubscribe.SetLabel("Disconnect")
			self.bRefresh.Enable(True)
			self.bActiveTrains.Enable(True)
			self.bCheckTrains.Enable(True)
			if self.IsDispatcherOrSatellite():
				self.bLoadTrains.Enable(True)
				self.bLoadLocos.Enable(True)
				self.bLostTrains.Enable(True)
				self.bSaveTrains.Enable(True)
				self.bSaveLocos.Enable(True)
				self.bClearTrains.Enable(True)
				self.bSnapshot.Enable(True)
				self.bPreloaded.Enable(True)
				if self.IsDispatcher():
					self.cbAutoRouter.Enable(True)
					self.cbATC.Enable(True)
					self.cbOSSLocks.Enable(True)
					self.cbSidingsUnlocked.Enable(True)

			self.RetrieveData()
			self.preloadedTrains = PreLoadedTrains(self)

			#self.districts.Initialize()
			#if self.IsDispatcher():
				#self.SendControlValues()
				#self.SendSignals()

		self.breakerDisplay.UpdateDisplay()
		self.ShowTitle()

	def RetrieveData(self, report=False, locos=True, trains=True, engineers=True):
		if locos:
			l = self.Get("getlocos", {})
			if l is None:
				logging.error("Unable to retrieve locos")
				l = {}

			self.locoList = l
			if report:
				self.PopupEvent("Locomotives reloaded")

		if trains:
			t = self.Get("gettrains", {})
			if t is None:
				logging.error("Unable to retrieve trains")
				t = {}

			# CopyTrainReferences(t)
			self.trainRoster = t
			if report:
				self.PopupEvent("Train roster reloaded")
			self.activeTrainsDlg.SetRoster(self.trainRoster)

		if engineers:
			e = self.Get("getengineers", {})
			if e is None:
				logging.error("Unable to retrieve engineers")
				e = []

			self.engineerList = e
			if report:
				self.PopupEvent("Engineers reloaded")

	def GetLocoInfo(self, loco):
		try:
			return self.locoList[loco]
		except KeyError:
			return None
	#
	# def SendSignals(self):
	# 	"""
	# 	Tell server about all signal aspect types.  Do not send aspect as this will defeat any initialization done inside rrserver
	# 	"""
	# 	for signm, sig in self.signals.items():
	# 		self.Request({"signal": {"name": signm, "aspect": None, "aspecttype": sig.GetAspectType(), "callon": 0}})

	def OnRefresh(self, _):
		if not self.IsDispatcher():
			self.ClearAllLocks()
			self.AllSignalsNeutral()
			self.AllBlocksNotClear()
			
		self.DoRefresh(False)
		
	def DoRefresh(self, initializing):
		if self.IsDispatcher():
			self.Request({"clock": { "value": self.timeValue, "status": self.clockStatus}})

		self.Request({"refresh": {"SID": self.sessionid}})
		self.initializing = initializing
		
	def ClearAllLocks(self):
		for t in self.turnouts.values():
			t.ClearLocks(forward=False)
			
		for s in self.signals.values():
			s.ClearLocks(forward=False)

	def SetStoppingRelays(self, bn, flag=False, force=False):
		self.Request({"setrelay": {"name": bn, "flag": 1 if flag else 0}})

	def SetIgnoredBlocks(self, igList):
		self.Request({"ignore": {"blocks": igList}})

	def AllSignalsNeutral(self):
		for s in self.signals.values():
			s.ForceNeutral()
			
	def AllBlocksNotClear(self):
		for b in self.blocks.values():
			b.ForceUnCleared()

	def raiseDeliveryEvent(self, data): # thread context
		try:
			jdata = json.loads(data)
		except json.decoder.JSONDecodeError:
			logging.warning("Unable to parse (%s)" % data)
			return
		evt = DeliveryEvent(data=jdata)
		wx.QueueEvent(self, evt)

	def CreateDispatchTable(self):					
		self.dispatch = {
			"showaspect":		self.DoCmdShowAspect,
			"turnout":			self.DoCmdTurnout,
			# "turnoutlever":		self.DoCmdTurnoutLever,
			#  "turnoutlock":		self.DoCmdTurnoutLock,
			"lockturnout":		self.DoCmdLockTurnout,
			"fleet":			self.DoCmdFleet,
			"block":			self.DoCmdBlock,
			# "blockdir":			self.DoCmdBlockDir,
			# "blockclear":		self.DoCmdBlockClear,
			"signal":			self.DoCmdSignal,
			# "siglever":			self.DoCmdSigLever,
			"handswitch":		self.DoCmdHandSwitch,
			# "indicator":		self.DoCmdIndicator,
			"breaker":			self.DoCmdBreaker,
			"districtlock":		self.DoCmdDistrictLock,
			"train":			self.DoCmdTrain,
			# "trainsignal":		self.DoCmdTrainSignal,
			# "settrain":			self.DoCmdSetTrain,
			# "deletetrain":		self.DoCmdDeleteTrain,
			# "assigntrain":		self.DoCmdAssignTrain,
			# "traincomplete":	self.DoCmdTrainComplete,
			"clock":			self.DoCmdClock,
			# "dccspeed":			self.DoCmdDCCSpeed,
			# "dccspeeds":		self.DoCmdDCCSpeeds,
			"control":			self.DoCmdControl,
			"sessionID":		self.DoCmdSessionID,
			"end":				self.DoCmdEnd,
			"advice":			self.DoCmdAdvice,
			"alert":			self.DoCmdAlert,
			# "ar":				self.DoCmdAR,
			# "atc":				self.DoCmdATC,
			# "atcstatus":		self.DoCmdATCStatus,
			# "checktrains":		self.DoCmdCheckTrains,
			# "dumptrains":		self.DoCmdDumpTrains,
			"relay":			self.DoCmdRelay,
			"setroute":			self.DoCmdSetRoute,
			# "signallock":		self.DoCmdSignalLock,
			# "traintimesrequest":	self.DoCmdTrainTimesRequest,
			# "traintimesreport":		self.DoCmdTrainTimesReport,
			# "trainblockorder":	self.DoCmdTrainBlockOrder,
			"nodestatus":		self.DoCmdNodeStatus,
			"ignore":			self.DoCmdIgnore,
		}
		
	def DoCmdNOOP(self, _):
		pass

	def onDeliveryEvent(self, evt):
		for cmd, parms in evt.data.items():
			logging.info("Inbound command: %s: %s" % (cmd, parms))
			
			try:
				handler = self.dispatch[cmd]
			except KeyError:
				logging.error("Unknown command: %s" % cmd)

			else:
				try:
					handler(parms)
				except Exception as e:
					logging.error("Exception %s handling command %s" % (str(e), cmd))
			
	def DoCmdTurnout(self, parms):
		for p in parms:
			try:
				turnout = p["name"]
			except KeyError:
				turnout = None
			try:
				state = p["state"]
			except KeyError:
				state = None
			try:
				force = p["force"]
			except:
				force = False

			if turnout is None or state is None:
				logging.error("Turnout command missing turnout name and/or state")
				return

			try:
				to = self.turnouts[turnout]
			except KeyError:
				to = None
				
			if to is not None and state != to.GetStatus():
				district = to.GetDistrict()
				st = "R" if state == "R" else "N"
				district.DoTurnoutAction(to, st, force=force)

		if self.CTCManager is not None:
			self.CTCManager.DoCmdTurnout(parms)

	def DoCmdRelay(self, parms):
		for p in parms:
			rname = p["name"]
			try:
				direction = p["direction"]
			except KeyError:
				direction = None
			try:
				train = p["train"]
			except KeyError:
				train = "??"
			try:
				state = int(p["state"])
			except (KeyError, ValueError):
				state = 0
			state = True if state != 0 else False
			try:
				silent = int(p["silent"])
			except (KeyError, ValueError):
				silent = 0

			silent = True if silent != 0 else False

			if rname.endswith(".srel"):
				rname = rname[:-5]

			sigmessage = ""
			try:
				blk = self.blocks[rname]
			except KeyError:
				blk = None

			if blk is not None:
				signm = blk.GetDirectionSignal()
				try:
					sig = self.signals[signm]
				except KeyError:
					sig = None
				if sig is not None:
					sigmessage = " Signal %s" % sig.GetName()
				else:
					sigmessage = ""

			if direction is not None and not silent:
				if state:
					self.PopupEvent("Stop Relay: Block %s %s%s Train %s" % (rname, direction, sigmessage, train))
				else:
					self.PopupEvent("Stop Relay: Block %s %s%s cleared" % (rname, direction, sigmessage))

	def DoCmdTurnoutLock(self, parms):
		if self.CTCManager is not None:
			self.CTCManager.DoCmdTurnoutLock(parms)
		for p in parms:
			tonm = p["name"]
			try:
				state = int(p["state"])
			except (KeyError, ValueError):
				state = 0
			state = True if state != 0 else False

			try:
				tout = self.turnouts[tonm]
			except KeyError:
				logging.error("turnoutlock: Unable to find turnout %s" % tonm)
				return

			tout.SetLock(state, refresh=True)

	def DoCmdDistrictLock(self, parms):
		self.PopupEvent("district lock: %s" % str(parms))
		for lname, lvalue in parms.items():
			if lname in self.dlocks:
				self.dlocks[lname].DoDistrictLocks(lname, lvalue)

	def DoCmdLockTurnout(self, parms):
		if self.CTCManager is not None:
			self.CTCManager.DoCmdTurnoutLock(parms)
		for p in parms:
			try:
				tonm = p["name"]
			except KeyError:
				tonm = None

			try:
				lock = int(p["lock"])
			except (KeyError, ValueError):
				lock = False

			if tonm is None:
				logging.debug("lockturnout command missing turnout name")

			try:
				tout = self.turnouts[tonm]
			except KeyError:
				logging.error("lockturnout: Unable to find turnout %s" % tonm)
				return

			tout.SetLock(lock, refresh=True)

	def DoCmdTurnoutLever(self, parms):
		for p in parms:
			try:
				turnout = p["name"]
			except KeyError:
				turnout = None
			try:
				state = p["state"]
			except KeyError:
				state = None
			try:
				force = p["force"]
			except:
				force = False

			if turnout is None or state is None:
				logging.error("Turnout lever command missing turnout name and/or state")
				return

			try:
				tout = self.turnouts[turnout]
			except KeyError:
				tout = None

			try:
				source = p["source"]
			except KeyError:
				source = None

			if tout is not None and state != tout.GetStatus():
				district = tout.GetDistrict()
				district.DoTurnoutLeverAction(tout, state, force=force, source=source)

	def DoCmdFleet(self, parms):
		for p in parms:
			try:
				signm = p["name"]
			except KeyError:
				signm = None
			try:
				value = int(p["value"])
			except:
				value = 0

			if signm is None:
				logging.error("fleet command without signal name parameter")
				return

			try:
				sig = self.signals[signm]
			except KeyError:
				sig = None

			if sig is None:
				logging.error("fleet command with unknown signal name %s" % signm)
				return

			sig.EnableFleeting(value == 1)
			self.FleetCheckBoxes(signm)
			
	def DoCmdBlock(self, parms):
		for p in parms:
			try:
				block = p["name"]
			except KeyError:
				block = None
			try:
				state = p["state"]
			except KeyError:
				state = None
			try:
				east = p["east"]
			except KeyError:
				east = True

			if block is None or state is None:
				logging.error("Block command without block and/or state parameter")
				return
			blk = None
			blockend = None
			try:
				blk = self.blocks[block]
			except KeyError:
				if block.endswith(".E") or block.endswith(".W"):
					blockend = block[-1]
					block = block[:-2]
					try:
						blk = self.blocks[block]
					except KeyError:
						blk = None

			if blk is None:
				logging.info("Ignoring block command for unknown block: %s" % block)
				return

			if blockend is None:
				blk.SetEast(east)
				blk.SetStatus(state)

			else:
				blk.SetStopSectionStatus(state, blockend)


			blk.Draw()

			# if state == "C":
			# 	blk.SetCleared(True)
			# 	return
			# elif blk.IsCleared():
			# 	blk.SetCleared(False)
			#
			# if block in self.osProxies:
			# 	district = self.osProxies[block].GetDistrict()
			# 	block = district.CheckOSProxies(block, state)
			# 	if block is None:
			# 		return
			#
			# if blk.GetBlockType() == OVERSWITCH:
			# 	if blk.GetRoute() is None:
			# 		logging.info("Ignoring block command for OS that does not have a route set")
			# 		msg = "Occupancy for OS %s ignored - no route set" % block
			# 		self.PopupEvent(msg)
			# 		return
			#
			# if self.settings.debug.blockoccupancy:
			# 	msg = "Block %s%s occupancy change: %s" % (block, "" if blockend is None else ".%s" % blockend, state)
			# 	self.PopupEvent(msg)
			#
			# if blk.GetStatus(blockend) != state:
			# 	district = blk.GetDistrict()
			# 	district.DoBlockAction(blk, blockend, state)

	def DoCmdBlockDir(self, parms):
		for p in parms:
			try:
				block = p["block"]
			except:
				logging.error("Blockdir command without block parameter")
				return
			try:
				direction = p["dir"] == 'E'
			except KeyError:
				direction = True  # east
				logging.debug("default path in blockdir")

			logging.debug("Inbound Blockdir %s %s" % (block, direction))
			blk = None
			try:
				blk = self.blocks[block]
				blockend = None
			except KeyError:
				if block.endswith(".E") or block.endswith(".W"):
					blockend = block[-1]
					block = block[:-2]
					try:
						blk = self.blocks[block]
					except KeyError:
						blk = None
			if blk is not None:
				blk.SetEast(direction, broadcast=False)

	def DoCmdSetRoute(self, parms):
		for p in parms:
			try:
				rtName= p["route"]
			except KeyError:
				logging.error("Setroute command without route parameter")
				return

			try:
				osName = p["os"]
			except KeyError:
				logging.error("setroute command without os parameter")
				return

			osBlk = self.blocks[osName]
			rte = self.routes[rtName]

			osBlk.SetRoute(rte)

	def DoCmdBlockClear(self, parms):
		pass

	def DoCmdIgnore(self, parms):
		try:
			iglist = parms["blocks"]
		except KeyError:
			iglist = []
		self.settings.rrserver.ignoredblocks = iglist
		logging.info("setting ignored blocks list to: %s" % str(iglist))

	def DoCmdShowAspect(self, parms):
		for p in parms:
			try:
				sigName = p["signal"]
			except KeyError:
				sigName = None
			try:
				aspect = p["aspect"]
			except KeyError:
				aspect = None

			if sigName is None or aspect is None:
				logging.error("ShowAspect command without signal and/or aspect command")
				return

			try:
				sig = self.signals[sigName]
			except:
				sig = None

			if sig is not None and (aspect != sig.GetAspect()):
				sig.SetAspect(aspect, refresh=True)
				sig.GetDistrict().SetAspect(sig, aspect, refresh=True)

		if self.CTCManager is not None:
			self.CTCManager.DoCmdSignal(parms)

	def DoCmdSignal(self, parms):
		for p in parms:
			try:
				sigName = p["name"]
			except KeyError:
				sigName = None
			try:
				aspect = p["aspect"]
			except KeyError:
				aspect = None

			if sigName is None or aspect is None:
				logging.error("Signal command without signal and/or aspect command")
				return

			try:
				frozenaspect = p["frozenaspect"]
			except:
				frozenaspect = None

			try:
				callon = int(p["callon"]) == 1
			except:
				callon = False

			try:
				sig = self.signals[sigName]
			except:
				sig = None

			if sig is not None and (aspect != sig.GetAspect() or frozenaspect != sig.GetFrozenAspect()):
				district = sig.GetDistrict()
				district.DoSignalAction(sig, aspect, frozenaspect=frozenaspect, callon=callon)
				# self.activeTrains.UpdateForSignal(sig)

		if self.CTCManager is not None:
			self.CTCManager.DoCmdSignal(parms)

	def DoCmdSigLever(self, parms):
		if self.IsDispatcher():
			for p in parms:
				try:
					signame = p["name"]
				except KeyError:
					signame = None
				try:
					state = p["state"]
				except KeyError:
					state = None

				if signame is None or state is None:
					logging.error("Signal lever command without signal and/or state command")
					return

				try:
					callon = int(p["callon"])
				except (KeyError, ValueError):
					callon = 0
				try:
					silent = int(p["silent"])
				except (KeyError, ValueError):
					silent = 1

				try:
					source = p["source"]
				except KeyError:
					source = None

				district = self.GetSignalLeverDistrict(signame)
				if district is None:
					# unable to find district for signal lever
					return
				district.DoSignalLeverAction(signame, state, callon=callon, silent=silent, source=source)
				
	def DoCmdSignalLock(self, parms):
		if self.IsDispatcher():
			return 
		for p in parms:
			try:
				signame = p["name"]
			except KeyError:
				signame = None

			try:
				state = int(p["state"])
			except:
				state = None
			
			try:
				sig = self.signals[signame]
			except:
				sig = None
			if sig is None or state is None:
				logging.error("signal lock command without signal name and/or state parameters")
				return 
			
			sig.SetLock(None, state == 1)

	def DoCmdHandSwitch(self, parms):				
		for p in parms:
			try:
				hsName = p["name"]
			except KeyError:
				hsName = None

			try:
				state = p["state"]
			except KeyError:
				state = None

			if hsName is None or state is None:
				logging.error("Handswitch command without hsname and/or state parameters")
				return
			
			try:
				hs = self.handswitches[hsName]
			except:
				hs = None

			if hs is None:
				logging.error("Unknown handswitch name: %s" % hsName)
				return

			if state != hs.GetValue():
				district = hs.GetDistrict()
				district.DoHandSwitchAction(hs, state)
						
	def DoCmdIndicator(self, parms):
		for p in parms:
			try:
				iName = p["name"]
			except KeyError:
				iName = None
			try:
				value = int(p["value"])
			except KeyError:
				value = None

			if iName is None or value is None:
				logging.error("Indicator command without name and/or value parameters")
				return
			
			try:
				ind = self.indicators[iName]
			except:
				ind = None

			if ind is not None:
				district = ind.GetDistrict()
				district.DoIndicatorAction(ind, value)
			else:
				logging.error("Unknown indicator name: %s" % iName)

	def DoCmdBreaker(self, parms):
		for p in parms:
			try:
				name = p["name"]
			except KeyError:
				name = None
			try:
				val = p["value"]
			except KeyError:
				val = None

			if name is None or val is None:
				logging.error("Breaker command without name and/or value parameter")
				return

			if val == 0:
				self.PopupEvent("Breaker: %s" % BreakerName(name))
				self.breakerDisplay.AddBreaker(name)
			else:
				#self.PopupAdvice("Breaker Cleared: %s" % BreakerName(name))
				self.breakerDisplay.DelBreaker(name)

			if name in self.indicators:
				ind = self.indicators[name]
				if val != ind.GetValue():
					ind.SetValue(val, silent=True)

	def DoCmdTrainSignal(self, parms):							
		try:
			trid = parms["train"]
		except KeyError:
			trid = None
		try:
			signm = parms["signal"]
		except KeyError:
			signm = None
		try:
			blknm = parms["block"]
		except KeyError:
			blknm = None

		if trid is None or signm is None:
			logging.error("Train signal command without train and/or signal command")
			return

		try:
			tr = self.trains[trid]
		except:
			tr = None
			
		try:
			sig = self.signals[signm]
		except:
			sig  = None

		try:
			blk = self.blocks[blknm]
		except:
			blk  = None

		if tr is None:
			logging.error("Unknown train: %s" % trid)
			return

		if sig is None:
			logging.error("Unknown signal %s" % signm)
			return

		curSig = tr.GetSignal()[0]
		if curSig is not None:
			curSigNm = curSig.GetName()
			if curSigNm is not None and curSigNm != signm:
				# we are changing the signal on the train - clear out the stopping sections on the old signal
				blk = curSig.GetGuardBlock()
				if blk is not None:
					blk.ClearStoppingSections()

		ir, cr = self.CheckForIncorrectRoute(tr, sig)
		if cr is not None:
			tr.SetMisrouted(ir is not None)
		tr.SetSignal(sig)
		# self.activeTrains.UpdateTrain(trid)

	def CheckForIncorrectRoute(self, tr, sig, ignoreunchangedsignal=False, silent=False):
		if tr is None or sig is None:
			return None, None

		if not self.settings.dispatcher.notifyincorrectroute:
			return None, None

		if not self.IsDispatcherOrSatellite():
			return None, None

		trid = tr.GetName()
		signm = sig.GetName()

		currentSig, currentAspect, fa = tr.GetSignal()
		if fa is not None:
			currentAspect = fa

		if currentAspect is None:
			return None, None

		if not ignoreunchangedsignal:
			if currentSig is None:
				changedSignal = True
			else:
				changedSignal = currentSig.GetName() != signm or currentAspect != sig.GetAspect()
			if not changedSignal:
				return None, None

		aspect = sig.GetAspect()
		if aspect == 0:
			return None, None

		blk = tr.FrontBlock()
		if blk is not None:
			blknm = blk.GetName()
			if blk.GetEast():
				nb = blk.GetAdjacentBlocks()[0]
			else:
				nb = blk.GetAdjacentBlocks()[1]
		else:
			blknm = None
			nb = None

		if nb is None:
			return None, None

		if nb.GetBlockType() != OVERSWITCH:
			return None, None

		rt = nb.GetRoute()
		if rt is None:
			return None, None

		nextBlk = rt.GetExitBlock()
		if nextBlk is not None and nextBlk in ValidBlocks:
			"""
			possibility here - if we do not want to check for incorrect block entry when we are coming into a yerd
			then we should return None, None here, otherwise pass
			"""
			return None, None

		rtnm = nb.GetRouteName()
		if rtnm is None:
			return None, None

		try:
			seq = self.trainList[trid]["sequence"]
		except (IndexError, KeyError):
			try:
				chrt = tr.GetChosenRoute()
				seq = self.trainList[chrt]["sequence"]
			except (IndexError, KeyError):
				seq = None

		if seq is None:
			return None, None

		blist = [s["block"] for s in seq]
		if blknm not in blist:
			return None, None

		rlist = [s["route"] for s in seq]
		if rtnm not in rlist:
			incorrectRoute = formatRouteDesignator(rtnm)
			correctRoute = None
			for s in seq:
				if signm == s["signal"]:
					correctRoute = formatRouteDesignator(s["route"])
					break

			# if there is no correct route, then most likely we are beyond the end of the train route - do nothing
			if not silent and correctRoute is not None:
				self.PopupAdvice("Train %s: incorrect route beyond signal %s: %s" % (trid, signm, incorrectRoute))
				self.PopupAdvice("The correct route is %s" % correctRoute)

			return incorrectRoute, correctRoute

		return None, rtnm
	#
	# def DoCmdDeleteTrain(self, parms):
	# 	try:
	# 		trid = parms["name"]
	# 	except KeyError:
	# 		trid = None
	#
	# 	if trid is None:
	# 		return
	#
	# 	try:
	# 		del self.trains[trid]
	# 	except:
	# 		logging.warning("can't delete train %s from train list" % trid)
	# 	try:
	# 		self.activeTrains.RemoveTrain(trid)
	# 	except:
	# 		logging.warning("can't delete train %s from active train list" % trid)
	#
	# def DoCmdSetTrain(self, parms):
	# 	try:
	# 		blocks = parms["blocks"]
	# 	except KeyError:
	# 		blocks = []
	#
	# 	try:
	# 		name = parms["name"]
	# 	except KeyError:
	# 		name = None
	#
	# 	try:
	# 		loco = parms["loco"]
	# 	except KeyError:
	# 		loco = None
	#
	# 	try:
	# 		east = parms["east"]
	# 	except KeyError:
	# 		east = None
	# 	try:
	# 		route = parms["route"]
	# 	except KeyError:
	# 		route = None
	#
	# 	try:
	# 		action = parms["action"]
	# 	except KeyError:
	# 		action = REPLACE
	#
	# 	try:
	# 		nameonly = parms["nameonly"]
	# 	except KeyError:
	# 		nameonly = False
	#
	# 	if isinstance(nameonly, str):
	# 		nameonly = False if nameonly == "0" else True
	#
	# 	try:
	# 		silent = parms["silent"]
	# 	except KeyError:
	# 		silent = False
	#
	# 	if isinstance(silent, str):
	# 		silent = True if silent == "1" else False
	#
	# 	blkorderMap = {}
	# 	for block in blocks:
	# 		try:
	# 			blk = self.blocks[block]
	# 		except KeyError:
	# 			blk = None
	#
	# 		if blk is None:
	# 			continue
	#
	# 		tr = blk.GetTrain()
	# 		if name is None: # the block is to be dis-associated with any train
	# 			if tr:
	# 				tr.RemoveFromBlock(blk)
	# 				#  if self.IsDispatcher():
	# 					#  self.SendTrainBlockOrder(tr)
	# 				trid = tr.GetName()
	# 				self.activeTrains.UpdateTrain(trid)
	# 				self.UpdateRouteDialog(trid)
	# 				if tr.IsInNoBlocks():
	# 					if not tr.IsBeingEdited():
	# 						if not silent:
	# 							self.PopupEvent("Train %s - detection1 lost from block %s" % (trid, blk.GetRouteDesignator()))
	# 						self.lostTrains.Add(tr.GetName(), tr.GetLoco(), tr.GetEngineer(), tr.GetEast(), block, tr.GetChosenRoute())
	# 					else:
	# 						tr.SetBeingEdited(False)
	# 					try:
	# 						self.activeTrains.RemoveTrain(trid)
	# 					except:
	# 						logging.warning("can't delete train %s from active train list" % trid)
	# 					try:
	# 						del self.trains[trid]
	# 					except:
	# 						logging.warning("can't delete train %s from train list" % trid)
	#
	# 			delList = []
	# 			for trid, tr in self.trains.items():
	# 				if tr.IsInBlock(blk):
	# 					tr.RemoveFromBlock(blk)
	# 					if self.IsDispatcher():
	# 						blkorderMap[trid] = tr
	# 					self.activeTrains.UpdateTrain(tr.GetName())
	# 					if tr.IsInNoBlocks():
	# 						delList.append([trid, tr])
	#
	# 			for trid, tr in delList:
	# 				if not tr.IsBeingEdited():
	# 					if not silent:
	# 						self.PopupEvent("Train %s - detection2 lost from block %s" % (trid, blk.GetRouteDesignator()))
	# 					self.lostTrains.Add(tr.GetName(), tr.GetLoco(), tr.GetEngineer(), tr.GetEast(), block, tr.GetChosenRoute())
	# 				try:
	# 					self.activeTrains.RemoveTrain(trid)
	# 				except:
	# 					logging.warning("can't delete train %s from active train list" % trid)
	# 				try:
	# 					del self.trains[trid]
	# 				except:
	# 					logging.warning("can't delete train %s from train list" % trid)
	#
	# 			continue
	#
	# 		if not blk.IsOccupied():
	# 			logging.warning("Set train for block %s, but that block is unoccupied" % block)
	# 			continue
	#
	# 		oldName = None
	# 		if tr:
	# 			oldName = tr.GetName()
	# 			if oldName and oldName != name:
	# 				if name in self.trains:
	# 					ntr = self.trains[name]
	# 					# merge the two trains under the new "name"
	# 					try:
	# 						bl = self.trains[oldName].GetBlockList()
	# 					except:
	# 						bl = {}
	# 					for blk in bl.values():
	# 						ntr.AddToBlock(blk, action)
	# 					if self.IsDispatcher():
	# 						blkorderMap[name] = ntr
	# 					self.activeTrains.UpdateTrain(name)
	#
	# 				else:
	# 					tr.SetName(name)
	# 					if name in self.trainList:
	# 						if east is None:
	# 							tr.SetEast(self.trainList[name]["eastbound"])
	# 						else:
	# 							tr.SetEast(east)
	#
	# 					self.trains[name] = tr
	# 					self.activeTrains.RenameTrain(oldName, name)
	# 					# self.Request({"renametrain": { "oldname": oldName, "newname": name, "east": "1" if tr.GetEast() else "0", "context": "settrainmerge"}})
	# 					if self.IsDispatcher():
	# 						blkorderMap[name] = tr
	# 				try:
	# 					self.activeTrains.RemoveTrain(oldName)
	# 				except:
	# 					logging.warning("can't delete train %s from train list" % oldName)
	#
	# 				try:
	# 					del(self.trains[oldName])
	# 				except:
	# 					logging.warning("can't delete train %s from train list" % oldName)
	#
	# 		try:
	# 			# trying to find train in existing list
	# 			tr = self.trains[name]
	# 			if oldName and oldName == name:
	# 				if east is not None:
	# 					tr.SetEast(east)
	# 					blk.SetEast(east)
	# 			else:
	# 				e = tr.GetEast()
	# 				blk.SetEast(e) # block takes on direction of the train if known
	#
	# 		except KeyError:
	# 			# not there - create a new one
	# 			tr = Train(name)
	# 			self.trains[name] = tr
	# 			self.activeTrains.AddTrain(tr)
	# 			# new train takes on direction from the settrain command
	# 			tr.SetEast(east)
	# 			# and block is set to the same thing
	# 			blk.SetEast(east)
	#
	# 		tr.AddToBlock(blk, action)
	# 		tr.SetChosenRoute(route)
	#
	# 		"""
	# 		check to see if the train is in an unexpected block unless:
	# 		- we are not the dispatcher or a satellite
	# 		- the option to do this check is turned off
	# 		- this block is inside a yard or ladder track - to allow the yard operator flexibility
	#
	# 		note that this check is bypassed later if the train does not have a defined block sequence
	# 		"""
	#
	# 		if self.IsDispatcherOrSatellite() and self.settings.dispatcher.notifyinvalidblocks and block not in ValidBlocks:
	# 			try:
	# 				seq = self.trainList[name]["sequence"]
	# 				sb = self.trainList[name]["startblock"]
	# 				if len(seq) == 0:
	# 					seq = None
	# 			except (IndexError, KeyError):
	# 				try:
	# 					rtnm = tr.GetChosenRoute()
	# 					seq = self.trainList[rtnm]["sequence"]
	# 					sb = self.trainList[rtnm]["startblock"]
	# 					if len(seq) == 0:
	# 						seq = None
	# 				except (IndexError, KeyError):
	# 					seq = None
	# 					sb = None
	#
	# 			if seq is not None:
	# 				blist = [sb] + [s["block"] for s in seq] + [formatRouteDesignator(s["route"]) for s in seq]
	# 				bdesig = blk.GetRouteDesignator()
	# 				if bdesig not in blist:
	# 					tr.SetMisrouted(True)
	# 					self.PopupEvent("Train %s not expected in block %s" % (name, bdesig))
	#
	# 		if action == REPLACE:
	# 			tr.SetBlockOrder(blocks)
	#
	# 		blk.SetTrain(tr)
	# 		blkorderMap[name] = tr
	#
	# 		if self.IsDispatcher() and not nameonly:
	# 			self.CheckTrainsInBlock(block, None)
	#
	# 		if loco:
	# 			self.activeTrains.SetLoco(tr, loco)
	#
	# 		tid = tr.GetName()
	# 		self.activeTrains.UpdateTrain(tid)
	# 		self.UpdateRouteDialog(tid)
	# 		self.lostTrains.Remove(tid)
	#
	# 		self.trainHistory.Update(tr)
	#
	# 		#  blk.EvaluateStoppingSections()
	# 		blk.Draw()   # this will redraw the train in this block only
	# 		tr.Draw() # necessary if this train appears in other blocks too
	#
	# 	for trid, tr in blkorderMap.items():
	# 		if trid in self.trains:
	# 			tr.ValidateStoppingSections()
	# 			self.AssertBlockDirections(tr)
	# 			if self.IsDispatcher():
	# 				self.SendTrainBlockOrder(tr)
	# 			self.activeTrains.UpdateTrain(trid)

	def AssertBlockDirections(self, tr):
		order = list(reversed(tr.GetBlockOrderList()))
		if len(order) <= 1:
			return

		lastBlock = order[0]
		lastBlk = self.blocks[lastBlock]
		direction = tr.GetEast()
		for block in order[1:]:
			blk = self.blocks[block]
			if CrossingEastWestBoundary(blk, lastBlk):
				direction = not direction
			blk.SetEast(direction)

			lastBlock = block
			lastBlk = blk
	#
	# def DoCmdTrainComplete(self, parms):
	# 	for p in parms:
	# 		try:
	# 			train = p["train"]
	# 		except KeyError:
	# 			train = None
	#
	# 		if train is None:
	# 			logging.error("TrainComplete command without train parameter")
	# 			return
	#
	# 		try:
	# 			tr = self.trains[train]
	# 		except KeyError:
	# 			logging.error("Unknown train name (%s) in traincomplete message" % train)
	# 			return
	#
	# 		if self.ATCEnabled and tr.IsOnATC():
	# 			locoid = tr.GetLoco()
	# 			self.Request({"atc": {"action": "remove", "train": train, "loco": locoid}})
	# 			tr.SetATC(False)
	# 			self.activeTrains.UpdateTrain(train)
	#
	# 		if self.AREnabled and tr.IsOnAR():
	# 			tr.SetAR(False)
	# 			self.Request({"ar": {"action": "remove", "train": train}})
	# 			self.activeTrains.UpdateTrain(train)
	#
	# 		tr.SetEngineer(None)
	# 		self.activeTrains.UpdateTrain(train)
	# 		self.PopupAdvice("Train %s has completed" % train)
	#
	# 		tr.Draw()
	#
	# def DoCmdAssignTrain(self, parms):
	# 	for p in parms:
	# 		try:
	# 			train = p["train"]
	# 		except KeyError:
	# 			train = None
	#
	# 		try:
	# 			engineer = p["engineer"]
	# 		except KeyError:
	# 			engineer = None
	#
	# 		try:
	# 			reassigned = p["reassign"] != "0"
	# 		except KeyError:
	# 			reassigned = False
	#
	# 		if train is None:
	# 			logging.error("AssignTrain command without train parameter")
	# 			return
	#
	# 		try:
	# 			tr = self.trains[train]
	# 		except:
	# 			logging.error("Unknown train name (%s) in assigntrain message" % train)
	# 			return
	#
	# 		tr.SetEngineer(engineer)
	# 		self.activeTrains.UpdateTrain(train)
	# 		self.trainHistory.UpdateEngineer(train, engineer)
	# 		#
	# 		# if reassigned:
	# 		# 	self.PopupAdvice("Train %s has been reassigned to %s" % (train, engineer))
	# 		# else:
	# 		# 	self.PopupAdvice("Train %s has been assigned to %s" % (train, engineer))
	#
	# 		tr.Draw()

	def DoCmdTrain(self, parms):
		try:
			iname = parms[0]["iname"]
		except KeyError:
			iname = None

		try:
			rname = parms[0]["rname"]
		except KeyError:
			rname = None

		try:
			east = parms[0]["east"]
		except KeyError:
			east = True

		try:
			loco = parms[0]["loco"]
		except KeyError:
			loco = None

		try:
			engineer = parms[0]["engineer"]
		except KeyError:
			engineer = None

		try:
			blocks = parms[0]["blocks"]
		except KeyError:
			blocks = []

		try:
			stopped = parms[0]["stopped"]
		except KeyError:
			stopped = False

		try:
			atc = parms[0]["atc"]
		except KeyError:
			atc = False

		try:
			ar = parms[0]["ar"]
		except KeyError:
			ar = False

		try:
			signal = parms[0]["signal"]
		except KeyError:
			signal = False

		try:
			aspect = parms[0]["aspect"]
		except KeyError:
			aspect = None

		try:
			aspectType = parms[0]["aspecttype"]
		except KeyError:
			aspectType = None

		if iname is None:
			logging.error("Received a train command without an internal name - ignoring")
			return

		if iname not in self.trains:
			tr = Train(iname, rname, east, loco, engineer)
			self.trains[iname] = tr
		else:
			tr = self.trains[iname]
		if rname is not None:
			tr.SetRName(rname)
		tr.SetEast(east)
		tr.SetLoco(loco)
		tr.SetEngineer(engineer)

		if rname is not None:
			self.trainNameMap[rname] = tr
			if rname in self.trainRoster:
				tr.SetRoster(rname, self.trainRoster[rname])
			else:
				tr.SetRoster(rname, None)

		tr.SetStopped(stopped)
		tr.SetATC(atc)
		tr.SetAR(ar)
		tr.SetSignal(signal)
		tr.SetAspect(aspect, aspectType)

		d, n = tr.SetBlocks(blocks)
		for bn in blocks:
			blk = self.blocks.get(bn, None)
			if blk is not None:
				blk.SetTrain(tr)
			else:
				if bn.endswith(".E") or bn.endswith(".W"):
					blockend = bn[-1]
					blkNm = bn[:-2]
					blk = self.blocks.get(blkNm, None)
					if blk is not None:
						state = "O" if tr.IsIdentified() else "U"
						blk.SetStopSectionStatus(state, blockend, refresh=True)
						blk.SetStopSectionTrain(tr, blockend)

		for bn in d:
			blk = self.blocks.get(bn, None)
			if blk is not None:
				blk.SetTrain(None)

		self.DrawTrain(tr, d)
		self.activeTrainsDlg.UpdateTrain(tr)

	def DoCmdClock(self, parms):
		if self.IsDispatcher():
			return

		try:
			tv = parms[0]["value"]
		except KeyError:
			tv = None

		try:
			sv = parms[0]["status"]
		except KeyError:
			sv = None

		error = False
		try:
			self.timeValue = int(tv)
		except:
			error = True

		status = 0
		try:
			status = int(sv)
		except:
			error = True

		if error:
			logging.error("Invbalid parameters in clock command")
			return

		if status != self.clockStatus:
			self.clockStatus = status
			self.ShowClockStatus()
		self.DisplayTimeValue()
	
	def DoCmdDCCSpeed(self, parms):
		pass
		# for p in parms:
		# 	try:
		# 		loco = p["loco"]
		# 	except:
		# 		loco = None
		#
		# 	try:
		# 		speed = p["speed"]
		# 	except:
		# 		speed = "0"
		#
		# 	try:
		# 		speedtype = p["speedtype"]
		# 	except:
		# 		speedtype = None
		#
		# 	if loco is None:
		# 		logging.error("DCCSpeed command without loco parameter")
		# 		return
		#
		# 	tr = self.activeTrains.FindTrainByLoco(loco)
		# 	if tr is not None:
		# 		tr.SetThrottle(speed, speedtype)
		# 		self.activeTrains.UpdateTrain(tr.GetName())

	def DoCmdDCCSpeeds(self, parms):
		pass
		# for loco, spinfo in parms.items():
		# 	tr = self.activeTrains.FindTrainByLoco(loco)
		# 	if tr is not None:
		# 		tr.SetThrottle(spinfo[0], spinfo[1])
		# 		self.activeTrains.UpdateTrain(tr.GetName())

	def DoCmdControl(self, parms):
		for p in parms:
			try:
				name = p["name"]
			except KeyError:
				name = None
			try:
				value = int(p["value"])
			except KeyError:
				value = None

			if name is None or value is None:
				logging.error("Control command without name and/or value parameter")
				return

			if self.IsDispatcher():
				self.UpdateControlWidget(name, value)
			# else:
			# 	self.UpdateControlDisplay(name, value)

	def DoCmdSessionID(self, parms):
		self.sessionid = int(parms)
		if self.IsDispatcher():
			self.sessionName = "Dispatcher"
		elif self.IsSatellite():
			self.sessionName = "Satellite"
		else:
			self.sessionName = self.settings.display.name
		logging.info("connected to railroad server with session ID %d" % self.sessionid)
		self.Request({"identify": {"SID": self.sessionid, "function": "DISPATCH" if self.IsDispatcher() else "SATELLITE" if self.IsSatellite() else "DISPLAY", "name": self.sessionName}})
		self.DoRefresh(True)
		#self.districts.OnConnect()
		self.ShowTitle()

	def DoCmdEnd(self, parms):
		self.BuildLayoutFile()
		self.RefreshComplete()

	def RefreshComplete(self):
		# Done refreshing from  server - now load latest snapshot
		#if self.IsDispatcher() and self.settings.dispatcher.autoloadsnapshot and self.initializing:
			#self.LoadSnapshot(wx.ID_OPEN, silent=True)

		self.SendDebugFlags()

		self.initializing = False

	def DoCmdTrainBlockOrder(self, parms):
		for p in parms:
			try:
				trid = p["name"]
			except KeyError:
				trid = None
			try:
				blocks = p["blocks"]
			except KeyError:
				blocks = []
			try:
				east = p["east"].startswith("T")
			except (IndexError, KeyError):
				east = None

			try:
				tr = self.trains[trid]
			except:
				tr = None

			if tr is not None:
				tr.SetEast(east)
				tr.SetBlockOrder(blocks)
				tr.ValidateStoppingSections()
				# self.activeTrains.UpdateTrain(trid)
	#
	# def DoCmdTrainTimesRequest(self, parms):
	# 	trains, times = self.activeTrains.GetTrainTimes()
	# 	resp = {"traintimesreport": {"trains": trains, "times": times}}
	# 	self.Request(resp)
	#
	# def DoCmdTrainTimesReport(self, parms):
	# 	try:
	# 		trains = parms["trains"]
	# 		times = parms["times"]
	# 	except KeyError:
	# 		logging.error("train times report command without trains and/or times report")
	# 		return
	#
	# 	for trid, tm in zip(trains, times):
	# 		try:
	# 			tr = self.trains[trid]
	# 		except:
	# 			tr = None
	# 		if tr:
	# 			tm = int(tm)
	# 			tr.SetTime(None if tm == -1 else tm)
					
	def DoCmdAdvice(self, parms):
		if "msg" in parms:
			if self.IsDispatcherOrSatellite() or self.settings.display.showadvice:
				self.PopupAdvice(parms["msg"])

	def DoCmdNodeStatus(self, parms):
		logging.debug("nodestatus %s" % str(parms))
		try:
			status = parms["enabled"]
		except KeyError:
			status = 1
		try:
			name = parms["name"]
		except KeyError:
			name = None
		try:
			addr = parms["address"]
		except KeyError:
			addr = None

		if addr is None or name is None:
			return

		if addr in self.nodes:
			self.nodes[addr].SetStatus(status)
		else:
			self.nodes[addr] = Node(name, addr, status)

		if status == 0:
			msg = "Node %s(0x%x) disabled" % (name, addr)
			self.PopupEvent(msg)

	def EnableNode(self, name, addr, flag):
		self.Request({"enablenode": { "name": name, "address": addr, "enable": "1" if flag else "0"}})

	def ReEnableNodes(self, disList):
		for n in disList:
			self.Request({"enablenode": {"name": n[0], "address": n[1], "enable": "1"}})

	def DoCmdAlert(self, parms):
		if "msg" in parms:
			if self.IsDispatcherOrSatellite() or self.settings.display.showevents:
				logging.info("ALERT: %s" % (str(parms)))
				self.PopupEvent(parms["msg"])
				
	def DoCmdAR(self, parms):
		pass
		# try:
		# 	trnm = parms["train"][0]
		# except KeyError:
		# 	logging.warning("AR command without a train name")
		# 	return
		# try:
		# 	tr = self.trains[trnm]
		# except KeyError:
		# 	logging.warning("AR train %s does not exist" % trnm)
		# 	return
		#
		# action = parms["action"][0]
		# tr.SetAR(action == "add")
		# self.activeTrains.UpdateTrain(trnm)
		# tr.Draw()

	def DoCmdATC(self, parms):
		pass
		# try:
		# 	trnm = parms["train"][0]
		# except KeyError:
		# 	logging.warning("Train parameter not found in ATC command: %s" % str(parms))
		# 	return
		#
		# try:
		# 	tr = self.trains[trnm]
		# except KeyError:
		# 	logging.warning("ATC train %s does not exist" % trnm)
		# 	return
		#
		# action = parms["action"][0]
		# tr.SetATC(action == "add")
		# self.activeTrains.UpdateTrain(trnm)
		# tr.Draw()

	def DoCmdATCStatus(self, parms):
		pass
		# try:
		# 	action = parms["action"][0]
		# except KeyError:
		# 	logging.warning("ATC Status command without action")
		# 	return
		#
		# if action == "reject":
		# 	try:
		# 		trnm = parms["train"][0]
		# 	except KeyError:
		# 		logging.warning("ATC Status reject command without train name")
		# 		return
		# 	try:
		# 		tr = self.trains[trnm]
		# 	except KeyError:
		# 		logging.warning("ATC rejected train %s does not exist" % trnm)
		# 		return
		#
		# 	self.PopupEvent("Rejected ATC train %s - no script" % trnm)
		# 	tr.SetATC(False)
		# 	self.activeTrains.UpdateTrain(trnm)
		# 	tr.Draw()
		#
		# elif action in [ "complete", "remove" ]:
		# 	try:
		# 		trnm = parms["train"][0]
		# 	except KeyError:
		# 		logging.warning("ATC Status complete/remove command without train name")
		# 		return
		# 	try:
		# 		tr = self.trains[trnm]
		# 	except KeyError:
		# 		logging.warning("ATC completed train %s does not exist" % trnm)
		# 		return
		#
		# 	if action == "complete":
		# 		self.PopupEvent("ATC train %s has completed" % trnm)
		# 	else:
		# 		self.PopupEvent("Train %s removed from ATC" % trnm)
		#
		# 	tr.SetATC(False)
		# 	if self.AREnabled and tr.IsOnAR():
		# 		tr.SetAR(False)
		# 		self.Request({"ar": {"action": "remove", "train": trnm}})
		#
		# 	self.activeTrains.UpdateTrain(trnm)
		#
		# 	tr.Draw()
					
	def DoCmdCheckTrains(self, parms):
		self.CheckTrains()
					
	def DoCmdDumpTrains(self, parms):
		pass
		# print("===========================dump by trains")
		# self.activeTrains.dump()
		# print("===========================dump by block")
		# for _, blk in self.blocks.items():
		# 	tr = blk.GetTrain()
		# 	if tr is not None:
		# 		print("%s: %s(%s)" % (blk.GetName(), tr.GetName(), tr.GetLoco()))
		# print("===========================end of dump trains", flush=True)

	def raiseDisconnectEvent(self): # thread context
		evt = DisconnectEvent()
		try:
			wx.PostEvent(self, evt)
		except RuntimeError:
			logging.info("Runtime error caught while trying to post disconnect event - not a problem if this is during shutdown")

	def SendAlertRequest(self, msg):
		self.Request({"alert": {"msg": [msg]}})

	def Request(self, req, force=False):
		command = list(req.keys())[0]
		if self.CommandAllowed(command):
			if self.subscribed or force:
				if "delay" in req[command] and req[command]["delay"] > 0:
					self.delayedRequests.Append(req)
				else:
					logging.debug("Sending HTTP Request: %s" % json.dumps(req))
					self.rrServer.SendRequest(req)
		else:
			logging.info("disallowing command %s from non dispatcher" % command)

	def UpdateCTCBitmaps(self, bmps):
		for screen, fg, pos, bmp in bmps:
			offset = self.diagrams[screen].offset
			self.panels[screen].DrawCTCBitmap(fg, pos[0], pos[1], offset, bmp)

	def CheckCTCCompleted(self, ms, cb):
		wx.CallLater(ms, cb)

	def CommandAllowed(self, cmd):
		if self.IsDispatcher():
			return True

		if self.IsSatellite():
			return cmd not in disallowedSatelliteCommands

		return cmd in allowedCommands
					
	def Get(self, cmd, parms):
		return self.rrServer.Get(cmd, parms)

	def SendBlockDirRequests(self):
		bdirs = []
		for b in self.blocks.values():
			bdirs.append({ "block": b.GetName(), "dir": "E" if b.GetEast() else "W"})
			sbw, sbe = b.GetStoppingSections()
			for sb in [sbw, sbe]:
				if sb:
					bdirs.append({ "block": sb.GetName(), "dir": "E" if b.GetEast() else "W"})
			if len(bdirs) >= 10:
				self.Request({"blockdirs": { "data": json.dumps(bdirs)}})
				bdirs = []
		if len(bdirs) > 0:
			self.Request({"blockdirs": { "data": json.dumps(bdirs)}})

	def BuildLayoutFile(self):
		data = {
			"blocks": self.GetBlocks(),
			"routes": self.GetRoutes(),
			"signals": self.GetSignals(),
			"crossover": self.GetCrossoverPoints()
		}
		self.rrServer.Post("layout.json", "data", data)

	def GetBlocks(self):
		blocks = {}
		for b in self.blocks.values():
			blocks.update(b.GetDefinition())
		return blocks

	def GetRoutes(self):
		routes = {}
		for r in self.routes.values():
			routes.update(r.GetDefinition())
		return routes

	def GetSignals(self):
		signals = {}
		for s in self.signals.values():
			signals.update(s.GetDefinition())
		return signals

	def GetCrossoverPoints(self):
		return [[b[0], b[1]] for b in self.districts.GetCrossoverPoints()]

	def onDisconnectEvent(self, _):
		self.listener = None
		self.subscribed = False
		self.bSubscribe.SetLabel("Connect")
		self.bRefresh.Enable(False)
		self.bLoadTrains.Enable(False)
		self.bLoadLocos.Enable(False)
		self.bSaveTrains.Enable(False)
		self.bClearTrains.Enable(False)
		self.bSaveLocos.Enable(False)
		if self.IsDispatcher():
			self.cbAutoRouter.Enable(False)
			self.cbATC.Enable(False)
			self.cbOSSLocks.Enable(False)
			self.cbSidingsUnlocked.Enable(False)
		logging.info("Server socket closed")
		self.breakerDisplay.UpdateDisplay()

		dlg = wx.MessageDialog(self, "The railroad server connection has gone down.",
			"Server Connection Error",
			wx.OK | wx.ICON_ERROR)
		dlg.ShowModal()
		dlg.Destroy()
		
		self.ShowTitle()

	def OnBSaveTrains(self, _):
		self.SaveTrains()
		
	def OnBCheckTrains(self, _):
		self.CheckTrains()

	def RebuildActiveTrainList(self):
		pass
		# self.activeTrains.RemoveAllTrains()
		# for tr in self.trains.values():
		# 	self.activeTrains.AddTrain(tr)

	def OnBClearTrains(self, _):
		pass
		# dlg = wx.MessageDialog(self, 'This clears all train IDs.  Are you sure you want to continue?\nPress "Yes" to confirm,\nor "No" to cancel.',
		# 		'Clear Train IDs', wx.YES_NO | wx.ICON_WARNING)
		# rc = dlg.ShowModal()
		# dlg.Destroy()
		# if rc != wx.ID_YES:
		# 	return
		#
		# newnames = []
		# for trid, tr in self.trains.items():
		# 	oldname = trid
		# 	newname = Train.NextName()
		# 	tr.SetName(newname)
		# 	self.activeTrains.RenameTrain(oldname, newname)
		# 	newnames.append([oldname, newname])
		# 	self.Request({"renametrain": { "oldname": oldname, "newname": newname, "context": "cleartrains"}}) #, "oldloco": oldLoco, "newloco": locoid}})
		#
		# for oname, nname in newnames:
		# 	tr = self.trains[oname]
		# 	del(self.trains[oname])
		# 	self.trains[nname] = tr
		
	def SaveTrains(self):
		if not self.CheckTrainsContiguous(True):
			return 
		
		dlg = ChooseItemDlg(self, True, True, self.rrServer)
		dlg.CenterOnScreen()
		rc = dlg.ShowModal()
		if rc == wx.ID_OK:
			file, directory = dlg.GetFile()
			
		dlg.Destroy()
		if rc != wx.ID_OK:
			return 
		
		if file is None:
			return

		trDict = {}
		for trid, tr in self.trains.items():
			if not trid.startswith("??"):
				trDict[trid] = tr.GetBlockNameList()
		self.rrServer.Post(file, directory, trDict)

		if len(trDict) == 1:
			plural = ""
		else:
			plural = "s"			
		self.PopupEvent("%d train%s saved to file %s" % (len(trDict), plural, file))

	def OnBLoadTrains(self, _):
		dlg = ChooseItemDlg(self, True, False, self.rrServer)
		dlg.CenterOnScreen()
		rc = dlg.ShowModal()
		if rc == wx.ID_OK:
			file, directory = dlg.GetFile()
			locations, allLocations = dlg.GetLocations()
			
		dlg.Destroy()
		if rc != wx.ID_OK:
			return 
		
		if file is None:
			return
		
		trDict = self.rrServer.Get("getfile", {"file": file, "dir": directory})
		if trDict is None:
			return
			
		if len(trDict) == 1:
			plural = ""
		else:
			plural = "s"			
		self.PopupEvent("%d train%s loaded from file %s" % (len(trDict), plural, file))

		for tid, blist in trDict.items():
			for bname in blist:
				blk = self.blocks[bname]
				if blk and self.BlockIncluded(locations, allLocations, bname):
					if blk.IsOccupied():
						tr = blk.GetTrain()
						oldName, _ = tr.GetNameAndLoco()
						self.Request({"renametrain": { "oldname": oldName, "newname": tid, "east": 1 if tr.GetEast() else 0, "context": "loadtrains"}})
					else:
						self.PopupEvent("Block %s not occupied, expecting train %s" % (bname, tid))
						
		self.Request({"checktrains": {}}) # this command will invoke the CheckTrains method after all the renaming has been done
		
	def CheckTrains(self):
		rc1 = self.CheckTrainsContiguous()
		rc2 = self.CheckLocosUnique()
		rc3 = self.CheckBlocksExpected()
		rc4 = self.CheckCorrectRoute()
		if rc1 and rc2 and rc3 and rc4:
			dlg = wx.MessageDialog(self, "All Trains are OK", "All Trains OK", wx.OK | wx.ICON_INFORMATION)
			dlg.ShowModal()
			dlg.Destroy()
		
	def CheckTrainsContiguous(self, query=False):
		t = [tr for tr in self.trains.values() if not tr.IsContiguous()]
		if len(t) == 0:
			return True
		
		if query:
			style = wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION
		else:
			style = wx.OK | wx.ICON_WARNING
		
		msg = "The following trains are in multiple sections:\n\n" + "\n".join([tr.GetName() for tr in t])
		if query:
			msg += "\n\nPress \"YES\" to proceed anyway, or \"NO\" to cancel"
			
		dlg = wx.MessageDialog(self, msg, "Non Contiguous Trains", style)
		rc = dlg.ShowModal()
		dlg.Destroy()
		
		if query and rc == wx.ID_YES:
			return True
		
		return False
	
	def CheckLocosUnique(self, query=False):
		locoMap = {}
		for trid, tr in self.trains.items():
			loco = tr.GetLoco()
			if loco != "??":
				if loco in locoMap:
					locoMap[loco].append(trid)
				else:
					locoMap[loco] = [trid]
					
		locos = list(locoMap.keys())
		for l in locos:
			if len(locoMap[l]) == 1:
				del(locoMap[l])	
		if len(locoMap) == 0:
			return True

		if query:
			style = wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION
		else:
			style = wx.OK | wx.ICON_WARNING
		
		locoList = ["%s: (%s)" % (lid, ", ".join(locoMap[lid])) for lid in locoMap.keys()]				
		msg = "The following locomotive numbers are not unique to a single train:\n\n" + "\n".join(locoList)
		if query:
			msg += "\n\nPress \"YES\" to proceed anyway, or \"NO\" to cancel"
			
		dlg = wx.MessageDialog(self, msg, "Non Unique Locomotive numbers", style)
		rc = dlg.ShowModal()
		dlg.Destroy()
		
		if query and rc == wx.ID_YES:
			return True
		
		return False

	def CheckBlocksExpected(self):
		results = {}
		for trid, tr in self.trains.items():
			if trid in self.trainList:
				try:
					seq = self.trainList[trid]["sequence"]
					sb =  self.trainList[trid]["startblock"]
				except (IndexError, KeyError):
					try:
						rtnm = tr.GetChosenRoute()
						seq = self.trainList[rtnm]["sequence"]
						sb = self.trainList[rtnm]["startblock"]
					except (IndexError, KeyError):
						seq = None
						sb = None

				if seq is not None:
					expectedlist = [sb] + [s["block"] for s in seq] + [formatRouteDesignator(s["route"]) for s in seq] + ValidBlocks
					trList = [blk.GetRouteDesignator() for blk in tr.GetBlockList().values()]
					unexpected = [bn for bn in trList if bn not in expectedlist]
					if len(unexpected) != 0:
						results[trid] = [b for b in unexpected]

		n = len(results)
		if n == 0:
			return True

		if n == 1:
			plural = " is"
		else:
			plural = "s are"

		resList = ["%s: %s" % (trid, ", ".join(results[trid])) for trid in results.keys()]
		msg = ("The following train%s unexpectedly in the indicated block(s):\n\n" % plural) + "\n".join(resList)

		dlg = wx.MessageDialog(self, msg, "Trains in unexpected blocks", style=wx.OK | wx.ICON_WARNING)
		rc = dlg.ShowModal()
		dlg.Destroy()

		return False

	def CheckCorrectRoute(self):
		results = {}
		for trid, tr in self.trains.items():
			if trid not in self.trainList:
				continue

			sig, _, _ = tr.GetSignal()
			if sig is None:
				continue

			incRt, corRt = self.CheckForIncorrectRoute(tr, sig, ignoreunchangedsignal=True, silent=True)
			if incRt is not None:
				results[trid] = [incRt, corRt]

				tr.SetMisrouted(incRt is not None)

		n = len(results)
		if n == 0:
			return True

		if n == 1:
			plural = " is"
		else:
			plural = "s are"

		resList = ["%s: %s should be %s" % (tr, results[tr][0], results[tr][1]) for tr in results]
		msg = ("The following train%s routed incorrectly:\n\n" % plural) + "\n".join(resList)

		dlg = wx.MessageDialog(self, msg, "Trains incorrecrtly routed", style=wx.OK | wx.ICON_WARNING)
		rc = dlg.ShowModal()
		dlg.Destroy()

		return False

	def OnBSaveLocos(self, _):
		self.SaveLocos()
		
	def SaveLocos(self):
		if not self.CheckLocosUnique(True):
			return 
		
		dlg = ChooseItemDlg(self, False, True, self.rrServer)
		dlg.CenterOnScreen()
		rc = dlg.ShowModal()
		if rc == wx.ID_OK:
			file, directory = dlg.GetFile()
			
		dlg.Destroy()
		if rc != wx.ID_OK:
			return 
		
		if file is None:
			return

		locoDict = {}
		for _, tr in self.trains.items():
			loco = tr.GetLoco()
			if loco is not None and not loco.startswith("??"):
				locoDict[loco] = tr.GetBlockNameList()

		self.rrServer.Post(file, directory, locoDict)
			
		if len(locoDict) == 1:
			plural = ""
		else:
			plural = "s"			
		self.PopupEvent("%d locomotive%s saved to file %s" % (len(locoDict), plural, file))

	def OnBLoadLocos(self, _):
		dlg = ChooseItemDlg(self, False, False, self.rrServer)
		dlg.CenterOnScreen()
		rc = dlg.ShowModal()
		if rc == wx.ID_OK:
			file, directory = dlg.GetFile()
			locations, allLocations = dlg.GetLocations()
			
		dlg.Destroy()
		if rc != wx.ID_OK:
			return 
		
		if file is None:
			return

		locoDict = self.rrServer.Get("getfile", {"file": file, "dir": directory})
		if locoDict is None:
			return

		if len(locoDict) == 1:
			plural = ""
		else:
			plural = "s"			
		self.PopupEvent("%d locomotive%s loaded from file %s" % (len(locoDict), plural, file))

		for lid, blist in locoDict.items():
			for bname in blist:
				blk = self.blocks[bname]
				if blk and self.BlockIncluded(locations, allLocations, bname):
					if blk.IsOccupied():
						tr = blk.GetTrain()
						oldName, oldLoco = tr.GetNameAndLoco()
						self.Request({"renametrain": { "oldname": oldName, "newname": oldName, "oldloco": oldLoco, "newloco": lid, "east": 1 if tr.GetEast() else 0, "context": "loadlocos"}})
					else:
						self.PopupEvent("Block %s not occupied, expecting locomotive %s" % (bname, lid))
						
		self.Request({"checktrains": {}}) # this command will invoke the CheckTrains method after all the renaming has been done

	def BlockIncluded(self, locations, allLocations, bname):
		blocation = bname[0]
		if blocation in locations:
			return True
		
		if blocation not in allLocations and "*" in locations:
			return True
		
		return False
	
	def OnClose(self, _):
		self.CloseProgram()
		
	def CloseProgram(self):
		killServer = False
		saveLogs = False
		takeSnapshot = False

		dlg = ExitDlg(self, self.IsDispatcher())
		dlg.CenterOnScreen()
		rc = dlg.ShowModal()
		if rc == wx.ID_OK:
			killServer, takeSnapshot, saveLogs = dlg.GetResults()

		dlg.Destroy()
		if rc != wx.ID_OK:
			return

		if takeSnapshot:
			self.TakeSnapshot()
			
		self.events.Close()
		self.advice.Close()
		try:
			self.listener.kill()
			self.listener.join()
		except:
			pass
		
		if killServer:
			try:
				self.rrServer.SendRequest({"quit": {}})
			except:
				pass
			
		self.Destroy()
		logging.info("%s process ending" % ("Dispatcher" if self.IsDispatcher() else "Satellite" if self.IsSatellite() else "Display"))

		if saveLogs:
			logging.info("Saving log and output files")
			interpreter = sys.executable.replace("python.exe", "pythonw.exe")
			svExec = os.path.join(os.getcwd(), "savelogs", "main.py")
			dispProc = Popen([interpreter, svExec], stdout=DEVNULL, stderr=DEVNULL, close_fds=True)

	def GetDebugFlags(self):
		return self.settings.debug


class ConfirmBranchLineTrainDlg(wx.Dialog):
	def __init__(self, parent, trid, lid, eng, loc):
		wx.Dialog.__init__(self, parent, wx.ID_ANY, "Confirm Branch Line Train")
		self.Bind(wx.EVT_CLOSE, self.AnswerNo)
		btnsz = (120, 46)
		font = wx.Font(wx.Font(16, wx.FONTFAMILY_ROMAN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, faceName="Arial"))
		fontBold = wx.Font(wx.Font(16, wx.FONTFAMILY_ROMAN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, faceName="Arial"))

		vsz = wx.BoxSizer(wx.VERTICAL)
		vsz.AddSpacer(20)

		st = wx.StaticText(self, wx.ID_ANY, "Confirm Branch Line Train:")
		st.SetFont(font)
		vsz.Add(st, 0, wx.LEFT, 10)
		vsz.AddSpacer(20)

		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.AddSpacer(40)
		st = wx.StaticText(self, wx.ID_ANY, "Train:", size=(140, -1))
		st.SetFont(font)
		hsz.Add(st)
		st = wx.StaticText(self, wx.ID_ANY, trid)
		st.SetFont(fontBold)
		hsz.Add(st)
		vsz.Add(hsz)

		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.AddSpacer(40)
		st = wx.StaticText(self, wx.ID_ANY, "Locomotive:", size=(140, -1))
		st.SetFont(font)
		hsz.Add(st)
		st = wx.StaticText(self, wx.ID_ANY, lid)
		st.SetFont(fontBold)
		hsz.Add(st)
		vsz.Add(hsz)

		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.AddSpacer(40)
		st = wx.StaticText(self, wx.ID_ANY, "Engineer:", size=(140, -1))
		st.SetFont(font)
		hsz.Add(st)
		st = wx.StaticText(self, wx.ID_ANY, "" if eng is None else eng)
		st.SetFont(fontBold)
		hsz.Add(st)
		vsz.Add(hsz)

		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.AddSpacer(40)
		st = wx.StaticText(self, wx.ID_ANY, "From:", size=(140, -1))
		st.SetFont(font)
		hsz.Add(st)
		st = wx.StaticText(self, wx.ID_ANY, loc)
		st.SetFont(fontBold)
		hsz.Add(st)
		vsz.Add(hsz)

		vsz.AddSpacer(30)

		hsz = wx.BoxSizer(wx.HORIZONTAL);
		byes = wx.Button(self, wx.ID_ANY, "Yes", size=btnsz)
		self.Bind(wx.EVT_BUTTON, self.AnswerYes, byes)
		bno = wx.Button(self, wx.ID_ANY, "No", size=btnsz)
		self.Bind(wx.EVT_BUTTON, self.AnswerNo, bno)

		hsz.Add(byes)
		hsz.AddSpacer(30)
		hsz.Add(bno)

		vsz.Add(hsz, 0, wx.ALIGN_CENTER_HORIZONTAL)
		vsz.AddSpacer(20)

		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.AddSpacer(20)
		hsz.Add(vsz)
		hsz.AddSpacer(20)

		self.SetSizer(hsz)
		self.Layout()
		self.Fit()

	def AnswerNo(self, _):
		self.EndModal(wx.ID_NO)

	def AnswerYes(self, _):
		self.EndModal(wx.ID_YES)


class ExitDlg (wx.Dialog):
	def __init__(self, parent, isDispatcher):
		wx.Dialog.__init__(self, parent, wx.ID_ANY, "Exit Dialog")
		self.parent = parent
		self.isDispatcher = isDispatcher
		self.Bind(wx.EVT_CLOSE, self.onCancel)

		dw, dh = wx.GetDisplaySize()
		sw, sh = self.GetSize()
		px = (dw-sw)/2
		py = (dh-sh)/2
		self.SetPosition(wx.Point(int(px), int(py)))

		vsz = wx.BoxSizer(wx.VERTICAL)
		vsz.AddSpacer(20)

		self.hasSnapshot = False

		if self.parent.IsDispatcherOrSatellite():
			if self.parent.subscribed:
				self.bTrains = wx.Button(self, wx.ID_ANY, "Save Trains")
				self.bLocos  = wx.Button(self, wx.ID_ANY, "Save Locos")
				self.cbSnapshot  = wx.CheckBox(self, wx.ID_ANY, "Take Snapshot")
				self.cbSnapshot.SetValue(self.parent.settings.dispatcher.prechecksnapshot)
				self.Bind(wx.EVT_BUTTON, self.onSaveTrains, self.bTrains)
				self.Bind(wx.EVT_BUTTON, self.onSaveLocos, self.bLocos)
				self.hasSnapshot = True

				vsz.Add(self.bTrains, 0, wx.ALIGN_CENTER)
				vsz.AddSpacer(10)
				vsz.Add(self.bLocos, 0, wx.ALIGN_CENTER)
				vsz.AddSpacer(20)
				vsz.Add(self.cbSnapshot, 0, wx.ALIGN_CENTER)
				vsz.AddSpacer(10)

			if self.parent.IsDispatcher():
				self.cbKillServer = wx.CheckBox(self, wx.ID_ANY, "Shutdown Server")
				self.cbKillServer.SetValue(self.parent.settings.dispatcher.precheckshutdownserver)

				vsz.Add(self.cbKillServer, 0, wx.ALIGN_CENTER)
				vsz.AddSpacer(10)

			vsz.AddSpacer(10)

		self.cbSaveLogs = wx.CheckBox(self, wx.ID_ANY, "Save log/output files")
		self.cbSaveLogs.SetValue(self.parent.settings.dispatcher.prechecksavelogs)

		vsz.Add(self.cbSaveLogs, 0, wx.ALIGN_CENTER)

		vsz.AddSpacer(20)

		bsz = wx.BoxSizer(wx.HORIZONTAL)

		self.bOK = wx.Button(self, wx.ID_ANY, "OK")
		self.bOK.SetDefault()
		self.bCancel = wx.Button(self, wx.ID_ANY, "Cancel")

		bsz.Add(self.bOK)
		bsz.AddSpacer(10)
		bsz.Add(self.bCancel)

		self.Bind(wx.EVT_BUTTON, self.onCancel, self.bCancel)
		self.Bind(wx.EVT_BUTTON, self.onOK, self.bOK)

		vsz.Add(bsz, 0, wx.ALIGN_CENTER)
		
		vsz.AddSpacer(20)

		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.AddSpacer(10)
		hsz.Add(vsz)
		hsz.AddSpacer(10)

		self.SetSizer(hsz)
		self.Layout()
		self.Fit()
		self.bOK.SetFocus()

	def onSaveTrains(self, _):
		self.parent.SaveTrains()

	def onSaveLocos(self, _):
		self.parent.SaveLocos()

	def GetResults(self):
		rvSnap = self.hasSnapshot and self.cbSnapshot.GetValue()
		if self.isDispatcher:
			return self.cbKillServer.GetValue(), rvSnap, self.cbSaveLogs.GetValue()
		else:
			return False, rvSnap, self.cbSaveLogs.GetValue()

	def onCancel(self, _):
		self.EndModal(wx.ID_CANCEL)

	def onOK(self, _):
		self.EndModal(wx.ID_OK)

