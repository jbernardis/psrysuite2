import os
import wx
import requests
import json
import sys

import re

from monitor.getbitsdlg import GetBitsDlg
from monitor.setinputbitsdlg import SetInputBitsDlg
from dispatcher.settings import Settings
from monitor.sessionsdlg import SessionsDlg
from monitor.trainsdlg import TrainsDlg
from monitor.siglever import SigLever, SigLeverShowDlg
from monitor.buttonchoicedlg import ButtonChoiceDlg
from dispatcher.delayedrequest import DelayedRequests
from traineditor.layoutdata import LayoutData
from monitor.blockosmap import BlockOSMap, CrossingEastWestBoundary
from monitor.snapshotdlg import SnapshotDlg

Nodes = [
	["Yard", 0x11],
	["Kale", 0x12],
	["East Jct", 0x13],
	["Cornell", 0x14],
	["Yard SW", 0x15],
	["Parsons", 0x21],
	["Port A", 0x22],
	["Port B", 0x23],
	["Latham", 0x31],
	["Carlton", 0x32],
	["Dell", 0x41],
	["Foss", 0x42],
	["Hyde Jct", 0x51],
	["Hyde", 0x52],
	["Shore", 0x61],
	["Krulish", 0x71],
	["Nassau W", 0x72],
	["Nassau E", 0x73],
	["Nassau NX", 0x74],
	["Bank", 0x81],
	["Cliveden", 0x91],
	["Green Mtn", 0x92],
	["Cliff", 0x93],
	["Sheffield", 0x95]
]

def getNodeAddress(nm):
	for i in range(len(Nodes)):
		if nm == Nodes[i][0]:
			return Nodes[i][1]
		
	return None
#
# breakerNames = {
# 	"CBBank":           "Bank",
# 	"CBCliveden":       "Cliveden",
# 	"CBLatham":         "Latham",
# 	"CBCornellJct":     "Cornell Junction",
# 	"CBParsonsJct":     "Parson's Junction",
# 	"CBSouthJct":       "South Junction",
# 	"CBCircusJct":      "Circus Junction",
# 	"CBSouthport":      "Southport",
# 	"CBLavinYard":      "Lavin Yard",
# 	"CBReverserP31":    "Reverser P31",
# 	"CBReverserP41":    "Reverser P41",
# 	"CBReverserP50":    "Reverser P50",
# 	"CBReverserC22C23": "Reverser C22/C23",
# 	"CBKrulish":		"Krulish",
# 	"CBKrulishYd":		"Krulish Yard",
# 	"CBNassauW":		"Nassau West",
# 	"CBNassauE":		"Nassau East",
# 	"CBWilson":			"Wilson City",
# 	"CBThomas":			"Thomas Yard",
# 	"CBFoss":			"Foss",
# 	"CBDell":			"Dell",
# 	"CBKale":			"Kale",
# 	"CBWaterman":		"Waterman Yard",
# 	"CBEngineYard":		"Engine Yard",
# 	"CBEastEndJct":		"East End Junction",
# 	"CBShore":			"Shore",
# 	"CBRockyHill":		"Rocky Hill",
# 	"CBHarpersFerry":	"Harpers Ferry",
# 	"CBBlockY30":		"Block Y30",
# 	"CBBlockY81":		"Block Y81",
# 	"CBGreenMtnStn":	"Green Mountain Station",
# 	"CBSheffieldA":		"Sheffield A",
# 	"CBGreenMtnYd":		"Green Mountain Yard",
# 	"CBHydeJct":		"Hyde Junction",
# 	"CBHydeWest":		"Hyde West",
# 	"CBHydeEast":		"Hyde East",
# 	"CBSouthportJct":	"Southport Junction",
# 	"CBCarlton":		"Carlton",
# 	"CBSheffieldB":		"Sheffield B",
# }


class MainFrame(wx.Frame):
	def __init__(self):
		wx.Frame.__init__(self, None, style=wx.DEFAULT_FRAME_STYLE)
		
		self.connected = False
		
		self.dlgSessions = None
		self.dlgTrains = None
		self.dlgSigLvrs = None

		self.blockList = []
		self.iobits = []
		self.blockOccupied = {}
		self.routes = {}
		self.layout = None
		self.trains = {}
		self.trainNames = []
		self.blockOsMap = None
		self.matrixMap = {}
		self.gmMap = {}
		self.hydeMap = {}
		self.turnoutList = {}
		self.breakerList = {}
		self.routesInList = []
		self.riFamilies = {}
		self.sigLvrList = []
		self.hsUnlock = []

		self.rrServer = None
		self.delayedRequests = None
		self.ticker = None
		self.tickerCounter = 0

		self.script = []
		self.scriptLines = 0
		self.scriptLine = -1
		self.scriptPause = -1

		self.recording = False
		self.recordedCommands = []

		self.settings = Settings()
		if self.settings.rrserver.simulation:		
			self.SetTitle("PSRY Monitor for Railroad Server in simulation mode")
		else:
			self.SetTitle("PSRY Monitor for Railroad Server")

		icon = wx.Icon()
		icon.CopyFromBitmap(wx.Bitmap(os.path.join(os.getcwd(), "icons", "monitor.ico"), wx.BITMAP_TYPE_ANY))
		self.SetIcon(icon)

		self.Bind(wx.EVT_CLOSE, self.OnClose)
		vsz = wx.BoxSizer(wx.VERTICAL)
		vsz.AddSpacer(20)
		
		bsz = wx.BoxSizer(wx.HORIZONTAL)
		bsz.AddSpacer(20)
		
		self.bConnect = wx.Button(self, wx.ID_ANY, "Connect", size=(100, 46))
		self.Bind(wx.EVT_BUTTON, self.OnConnect, self.bConnect)
		bsz.Add(self.bConnect)

		bsz.AddSpacer(20)
		
		self.bQuit = wx.Button(self, wx.ID_ANY, "Shutdown\nServer", size=(100, 46))
		self.Bind(wx.EVT_BUTTON, self.OnQuit, self.bQuit)
		bsz.Add(self.bQuit)
		
		bsz.AddSpacer(20)
		
		self.bSessions = wx.Button(self, wx.ID_ANY, "Sessions", size=(100, 46))
		self.Bind(wx.EVT_BUTTON, self.OnSessions, self.bSessions)
		bsz.Add(self.bSessions)
		
		bsz.AddSpacer(20)
		
		self.bTrains = wx.Button(self, wx.ID_ANY, "Trains", size=(100, 46))
		self.Bind(wx.EVT_BUTTON, self.OnTrains, self.bTrains)
		bsz.Add(self.bTrains)
		
		bsz.AddSpacer(20)
		
		vsz.Add(bsz)
		vsz.AddSpacer(20)

		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.AddSpacer(20)
		
		self.bGetBits = wx.Button(self, wx.ID_ANY, "Get O/I Bits", size=(100, 46))
		self.Bind(wx.EVT_BUTTON, self.OnGetBits, self.bGetBits)
		hsz.Add(self.bGetBits)
		
		hsz.AddSpacer(10)
		vsz.Add(hsz)
		
		vsz.AddSpacer(20)
		
		if self.settings.rrserver.simulation:		
			hsz = wx.BoxSizer(wx.HORIZONTAL)
			hsz.AddSpacer(20)
	
			self.bSetInputBit = wx.Button(self, wx.ID_ANY, "Set Input Bits", size=(100, 46))
			self.Bind(wx.EVT_BUTTON, self.OnSetInputBit, self.bSetInputBit)
			hsz.Add(self.bSetInputBit)
					
			vsz.Add(hsz)
			
			vsz.AddSpacer(20)

		if self.settings.rrserver.simulation:
			hsz = wx.BoxSizer(wx.HORIZONTAL)
			hsz.AddSpacer(20)

			self.bOccupy = wx.Button(self, wx.ID_ANY, "Occupy\nBlock", size=(100, 46))
			self.Bind(wx.EVT_BUTTON, self.OnOccupy, self.bOccupy)
			hsz.Add(self.bOccupy)

			hsz.AddSpacer(20)
			self.chBlock = wx.Choice(self, wx.ID_ANY, choices=[])
			self.chBlock.SetSelection(0)
			hsz.Add(self.chBlock, 0, wx.TOP, 10)

			hsz.AddSpacer(20)

			self.cbOccupy = wx.CheckBox(self, wx.ID_ANY, "Occupy")
			self.cbOccupy.SetValue(True)
			hsz.Add(self.cbOccupy, 0, wx.TOP, 15)

			hsz.AddSpacer(20)

			self.bOccupyNone = wx.Button(self, wx.ID_ANY, "Clear All", size=(100, 46))
			self.Bind(wx.EVT_BUTTON, self.OnOccupyNone, self.bOccupyNone)
			hsz.Add(self.bOccupyNone)

			hsz.AddSpacer(20)
			vsz.Add(hsz)

			vsz.AddSpacer(20)

		if self.settings.rrserver.simulation:
			hsz = wx.BoxSizer(wx.HORIZONTAL)
			hsz.AddSpacer(20)

			self.bMove = wx.Button(self, wx.ID_ANY, "Move\nTrain", size=(100, 46))
			self.Bind(wx.EVT_BUTTON, self.OnMove, self.bMove)
			hsz.Add(self.bMove)

			hsz.AddSpacer(20)
			self.chTrain = wx.Choice(self, wx.ID_ANY, choices=[])
			self.chTrain.SetSelection(wx.NOT_FOUND)
			hsz.Add(self.chTrain, 0, wx.TOP, 10)

			hsz.AddSpacer(5)
			self.bRefreshTrains = wx.Button(self, wx.ID_ANY, "...", size=(20, 20))
			self.Bind(wx.EVT_BUTTON, self.OnRefreshTrains, self.bRefreshTrains)
			hsz.Add(self.bRefreshTrains, 0, wx.TOP, 12)

			hsz.AddSpacer(20)

			self.cbForward = wx.CheckBox(self, wx.ID_ANY, "Forward")
			self.cbForward.SetValue(True)
			hsz.Add(self.cbForward, 0, wx.TOP, 15)
			hsz.AddSpacer(20)
			hsz.AddSpacer(20)

			self.cbRear = wx.CheckBox(self, wx.ID_ANY, "Bring up rear")
			self.cbRear.SetValue(True)
			hsz.Add(self.cbRear, 0, wx.TOP, 15)
			hsz.AddSpacer(20)

			self.bRear = wx.Button(self, wx.ID_ANY, "Rear Only", size=(100, 46))
			self.Bind(wx.EVT_BUTTON, self.OnRear, self.bRear)
			hsz.Add(self.bRear)

			hsz.AddSpacer(20)
			vsz.Add(hsz)

			vsz.AddSpacer(20)

		if self.settings.rrserver.simulation:		
			hsz = wx.BoxSizer(wx.HORIZONTAL)
			hsz.AddSpacer(20)
	
			self.bBreaker = wx.Button(self, wx.ID_ANY, "Breaker", size=(100, 46))
			self.Bind(wx.EVT_BUTTON, self.OnBreaker, self.bBreaker)
			hsz.Add(self.bBreaker)
			
			hsz.AddSpacer(20)
			self.chBreaker = wx.Choice(self, wx.ID_ANY, choices=[])
			hsz.Add(self.chBreaker, 0, wx.TOP, 10)
			self.chBreaker.SetSelection(0)
			
			hsz.AddSpacer(20)
			self.cbBreaker = wx.CheckBox(self, wx.ID_ANY, "OK")
			self.cbBreaker.SetValue(True)
			hsz.Add(self.cbBreaker, 0, wx.TOP, 15)
			
			hsz.AddSpacer(20)
			self.bClearAll = wx.Button(self, wx.ID_ANY, "Clear All", size=(100, 46))
			self.Bind(wx.EVT_BUTTON, self.OnClearBreakers, self.bClearAll)
			hsz.Add(self.bClearAll)
			
			hsz.AddSpacer(20)
			
			vsz.Add(hsz)
			
			vsz.AddSpacer(20)

		if self.settings.rrserver.simulation:
			hsz = wx.BoxSizer(wx.HORIZONTAL)
			hsz.AddSpacer(20)

			self.bTurnoutPos = wx.Button(self, wx.ID_ANY, "TurnoutPos", size=(100, 46))
			self.Bind(wx.EVT_BUTTON, self.OnTurnoutPos, self.bTurnoutPos)
			hsz.Add(self.bTurnoutPos)

			hsz.AddSpacer(20)
			self.chTurnout = wx.Choice(self, wx.ID_ANY, choices=[])
			hsz.Add(self.chTurnout, 0, wx.TOP, 10)
			self.chTurnout.SetSelection(wx.NOT_FOUND)

			hsz.AddSpacer(20)
			self.cbNormal = wx.CheckBox(self, wx.ID_ANY, "Normal")
			hsz.Add(self.cbNormal, 0, wx.TOP, 15)

			hsz.AddSpacer(20)

			vsz.Add(hsz)

			vsz.AddSpacer(20)

		if self.settings.rrserver.simulation:
			hsz = wx.BoxSizer(wx.HORIZONTAL)
			hsz.AddSpacer(20)

			self.bHSUnlock = wx.Button(self, wx.ID_ANY, "Hand Switch\nUnlock", size=(100, 46))
			self.Bind(wx.EVT_BUTTON, self.OnHSUnlock, self.bHSUnlock)
			hsz.Add(self.bHSUnlock)

			hsz.AddSpacer(20)
			self.chHSUnlock = wx.Choice(self, wx.ID_ANY, choices=[])
			hsz.Add(self.chHSUnlock, 0, wx.TOP, 10)
			self.chHSUnlock.SetSelection(wx.NOT_FOUND)

			hsz.AddSpacer(20)
			self.cbHSUnlock = wx.CheckBox(self, wx.ID_ANY, "Unlock")
			hsz.Add(self.cbHSUnlock, 0, wx.TOP, 15)

			hsz.AddSpacer(20)

			vsz.Add(hsz)

			vsz.AddSpacer(20)

		if self.settings.rrserver.simulation:
			self.BuildMatrixMap()
			hsz = wx.BoxSizer(wx.HORIZONTAL)
			hsz.AddSpacer(20)

			self.bRoutesIn = wx.Button(self, wx.ID_ANY, "Routes In", size=(100, 46))
			self.Bind(wx.EVT_BUTTON, self.OnRoutesIn, self.bRoutesIn)
			hsz.Add(self.bRoutesIn)

			hsz.AddSpacer(20)
			self.chRoutesIn = wx.Choice(self, wx.ID_ANY, choices=[])
			hsz.Add(self.chRoutesIn, 0, wx.TOP, 10)
			self.chRoutesIn.SetSelection(0)

			hsz.AddSpacer(20)

			vsz.Add(hsz)

			vsz.AddSpacer(20)

		if self.settings.rrserver.simulation:
			self.BuildMatrixMap()
			hsz = wx.BoxSizer(wx.HORIZONTAL)
			hsz.AddSpacer(20)

			self.bMatrix = wx.Button(self, wx.ID_ANY, "NX Buttons", size=(100, 46))
			self.Bind(wx.EVT_BUTTON, self.OnMatrix, self.bMatrix)
			hsz.Add(self.bMatrix)

			hsz.AddSpacer(20)
			self.chMatrixArea = wx.Choice(self, wx.ID_ANY, choices=list(self.matrixMap.keys()))
			hsz.Add(self.chMatrixArea, 0, wx.TOP, 10)
			self.chMatrixArea.SetSelection(0)

			hsz.AddSpacer(20)

			vsz.Add(hsz)

			vsz.AddSpacer(20)

		if self.settings.rrserver.simulation:			
			hsz = wx.BoxSizer(wx.HORIZONTAL)
			hsz.AddSpacer(20)
			
			self.bSigLvr = wx.Button(self, wx.ID_ANY, "Signal Lever", size=(100, 46))
			self.Bind(wx.EVT_BUTTON, self.OnSigLvr, self.bSigLvr)
			hsz.Add(self.bSigLvr, 0, wx.ALIGN_CENTER_VERTICAL)
			
			hsz.AddSpacer(20)
			self.chSigLvr = wx.Choice(self, wx.ID_ANY, choices=[])
			hsz.Add(self.chSigLvr, 0, wx.ALIGN_CENTER_VERTICAL)
			self.chSigLvr.SetSelection(wx.NOT_FOUND)
			
			hsz.AddSpacer(20)
			self.rbSigLever = wx.RadioBox(self, wx.ID_ANY,choices=["Left", "Center", "Right"], majorDimension=1, style=wx.RA_SPECIFY_COLS,)
			self.rbSigLever.SetSelection(1)
			hsz.Add(self.rbSigLever)

			hsz.AddSpacer(10)
			self.cbCallOn = wx.CheckBox(self, wx.ID_ANY, "Call On")
			hsz.Add(self.cbCallOn, 0, wx.ALIGN_CENTER_VERTICAL)

			hsz.AddSpacer(20)

			self.bSigLvrShow = wx.Button(self, wx.ID_ANY, "Show", size=(100, 46))
			self.Bind(wx.EVT_BUTTON, self.OnSigLvrShow, self.bSigLvrShow)
			hsz.Add(self.bSigLvrShow, 0, wx.ALIGN_CENTER_VERTICAL)

			hsz.AddSpacer(20)

			self.bSigNeutral = wx.Button(self, wx.ID_ANY, "Neutralize\nAll Signals", size=(100, 46))
			self.Bind(wx.EVT_BUTTON, self.OnSigNeutral, self.bSigNeutral)
			hsz.Add(self.bSigNeutral, 0, wx.ALIGN_CENTER_VERTICAL)

			hsz.AddSpacer(20)

			vsz.Add(hsz)
			
			vsz.AddSpacer(20)
		else:
			hsz = wx.BoxSizer(wx.HORIZONTAL)
			hsz.AddSpacer(20)
			
			self.bSigLvrShow = wx.Button(self, wx.ID_ANY, "Show\nSignal Levers", size=(100, 46))
			self.Bind(wx.EVT_BUTTON, self.OnSigLvrShow, self.bSigLvrShow)
			hsz.Add(self.bSigLvrShow)
			
			hsz.AddSpacer(20)
			
			vsz.Add(hsz)
			
			vsz.AddSpacer(20)
			
		if self.settings.rrserver.simulation:
			hsz = wx.BoxSizer(wx.HORIZONTAL)
			hsz.AddSpacer(20)
			self.bScript = wx.Button(self, wx.ID_ANY, "Script", size=(100, 46))
			self.Bind(wx.EVT_BUTTON, self.OnScript, self.bScript)
			hsz.Add(self.bScript)
			hsz.AddSpacer(20)

			self.bSnapshot = wx.Button(self, wx.ID_ANY, "Snapshot", size=(100, 46))
			self.Bind(wx.EVT_BUTTON, self.OnSnapshot, self.bSnapshot)
			hsz.Add(self.bSnapshot)

			hsz.AddSpacer(20)

			self.bRecord = wx.Button(self, wx.ID_ANY, "Record", size=(100, 46))
			self.Bind(wx.EVT_BUTTON, self.OnRecord, self.bRecord)
			hsz.Add(self.bRecord)

			hsz.AddSpacer(20)

			self.lStatus = wx.StaticText(self, wx.ID_ANY, "", size=(200, -1))
			self.lStatus.SetFont(wx.Font(16, wx.FONTFAMILY_ROMAN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, faceName="Arial"))
			hsz.Add(self.lStatus, 0, wx.TOP, 15)

			vsz.Add(hsz)
			
			vsz.AddSpacer(20)

		self.SetSizer(vsz)
		self.Fit()
		self.Layout()

		wx.CallAfter(self.Initialize)
		
	def BuildMatrixMap(self):
		self.riFamilies = {
			"CC10E": "GME",
			"CC10W": "GMW",
			"CC21E": "SHE",
			"CC21W": "SHW",
			"CC30E": "GME",
			"CC30W": "GMW",
			"CC31W": "GMW",
			"CC40E": "SHE",
			"CC40W": "SHW",
			"CC41E": "SHE",
			"CC41W": "SHW",
			"CC42E": "SHE",
			"CC42W": "SHW",
			"CC43E": "SHE",
			"CC43W": "SHW",
			"CC44E": "SHE",
			"CC44W": "SHW",
			"CC50E": "SHE",
			"CC50W": "SHW",
			"CC51E": "SHE",
			"CC51W": "SHW",
			"CC52E": "SHE",
			"CC52W": "SHW",
			"CC53E": "SHE",
			"CC53W": "SHW",
			"CC54E": "SHE",
			"CC54W": "SHW",
			"CG10E": "GME",
			"CG12E": "GME",
			"CG21W": "GMW",
			"H12E": "HWE",
			"H12W": "HWW",
			"H22E": "HEE",
			"H22W": "HEW",
			"H30E": "HWE",
			"H31E": "HWE",
			"H31W": "HWW",
			"H32E": "HWE",
			"H32W": "HWW",
			"H33E": "HWE",
			"H33W": "HWW",
			"H34E": "HWE",
			"H34W": "HWW",
			"H40E": "HEE",
			"H41E": "HEE",
			"H41W": "HEW",
			"H42E": "HEE",
			"H42W": "HEW",
			"H43E": "HEE",
			"H43W": "HEW",
			"NSw60A": "N60",
			"NSw60B": "N60",
			"NSw60C": "N60",
			"NSw60D": "N60",
			"Y81E": "YE",
			"Y81W": "YW",
			"Y82E": "YE",
			"Y82W": "YW",
			"Y83E": "YE",
			"Y83W": "YW",
			"Y84E": "YE",
			"Y84W": "YW"
		}

		self.matrixMap = {
			"Waterman Yard": {
				"node": "Yard",
				"buttons": ["YWWB1", "YWWB2", "YWWB3", "YWWB4", "YWEB1", "YWEB2", "YWEB3", "YWEB4"],
				"bits"   : [[3, 3],  [3, 4],  [3, 5],  [3, 6],  [3, 7],  [4, 0],  [4, 1],  [4, 2]]
			},
			"Cliff A": {
				"node"   : "Sheffield",
				"buttons": ["C50E", "C51E", "C52E", "C53E", "C54E", "C50W", "C51W", "C52W", "C53W", "C54W"],
				"bits"   : [[0, 0], [0, 1], [0, 2], [0, 3], [0, 4], [0, 5], [0, 6], [0, 7], [1, 0], [1, 1]]
			},
			"Cliff B": {
				"node"   : "Cliff",
				"buttons": ["C21E", "C40E", "C41E", "C42E", "C43E", "C44E", "C21W", "C40W", "C41W", "C42W", "C43W", "C44W"],
				"bits"   : [[0, 0], [0, 1], [0, 5], [0, 4], [0, 3], [0, 2], [1, 0], [1, 1], [0, 6], [0, 7], [1, 3], [1, 2]]
			}
		}

		self.sheffieldRoutesMap = {
			"CRtC20C44": ["C44E", "Cliff"],
			"CRtC20C43": ["C43E", "Cliff"],
			"CRtC20C42": ["C42E", "Cliff"],
			"CRtC20C41": ["C41E", "Cliff"],
			"CRtC20C40": ["C40E", "Cliff"],
			"CRtC20C21": ["C21E", "Cliff"],

			"CRtC44C22": ["C44W", "Cliff"],
			"CRtC43C22": ["C43W", "Cliff"],
			"CRtC42C22": ["C42W", "Cliff"],
			"CRtC41C22": ["C41W", "Cliff"],
			"CRtC40C22": ["C40W", "Cliff"],
			"CRtC21C22": ["C21W", "Cliff"],

			"CRtC50C22": ["C50W", "Sheffield"],
			"CRtC51C22": ["C51W", "Sheffield"],
			"CRtC52C22": ["C52W", "Sheffield"],
			"CRtC53C22": ["C53W", "Sheffield"],
			"CRtC54C22": ["C54W", "Sheffield"],

			"CRtC20C50": ["C50E", "Sheffield"],
			"CRtC20C51": ["C51E", "Sheffield"],
			"CRtC20C52": ["C52E", "Sheffield"],
			"CRtC20C53": ["C53E", "Sheffield"],
			"CRtC20C54": ["C54E", "Sheffield"],
		}

		self.gmMap = {
			"CRtC11G21": [0, 7],
			"CRtC11C10": [0, 6],
			"CRtC11C30": [0, 5],
			"CRtC11C31": [0, 4],

			"CRtG12C20": [0, 3],
			"CRtG10C20": [0, 2],
			"CRtC10C20": [0, 1],
			"CRtC30C20": [0, 0]
		}

		self.hydeMap = {
			"HRtH11H12": [0, 0],
			"HRtH11H31": [0, 4],
			"HRtH11H32": [0, 5],
			"HRtH11H33": [0, 2],
			"HRtH11H34": [0, 1],

			"HRtH30H31": [0, 3],

			"HRtH21H22": [0, 6],
			"HRtH21H41": [1, 1],
			"HRtH21H42": [1, 0],
			"HRtH21H43": [0, 7],

			"HRtH13H31": [2, 3],
			"HRtH13H32": [2, 2],
			"HRtH13H33": [2, 1],
			"HRtH13H34": [2, 0],
			"HRtH12H13": [1, 7],

			"HRtH22H23": [1, 5],
			"HRtH23H40": [1, 6],
			"HRtH23H43": [1, 4],
			"HRtH23H42": [1, 3],
			"HRtH23H41": [1, 2]
		}

		self.hydeGroups = {
			"HOSWW":  ["HRtH22H12", "HRtH11H31", "HRtH11H32", "HRtH11H33", "HRtH11H34"],
			"HOSWW2": ["HRtH30H31"],
			"HOSWE":  ["HRtH21H22", "HRtH21H41", "HRtH21H42", "HRtH21H43"],
			"HOSEW":  ["HRtH13H31", "HRtH13H32", "HRtH13H33", "HRtH13H34", "HRtH12H13"],
			"HOSEE":  ["HRtH22H23", "HRtH23H40", "HRtH23H43", "HRtH23H42", "HRtH23H41"]
		}

	def EnableButtons(self, flag=True):
		self.bSessions.Enable(flag)
		self.bTrains.Enable(flag)
		self.bGetBits.Enable(flag)
		self.bSigLvrShow.Enable(flag)	
		if self.settings.rrserver.simulation:
			self.bOccupy.Enable(flag)
			self.bOccupyNone.Enable(flag)
			self.bMove.Enable(flag)
			self.bRear.Enable(flag)
			self.bRefreshTrains.Enable(flag)
			self.bBreaker.Enable(flag)
			self.bClearAll.Enable(flag)
			self.bQuit.Enable(flag)
			self.bTurnoutPos.Enable(flag)
			self.bHSUnlock.Enable(flag)
			self.bSetInputBit.Enable(flag)
			self.bMatrix.Enable(flag)
			self.bRoutesIn.Enable(flag)
			self.bSigLvr.Enable(flag)
			self.bSigNeutral.Enable(flag)
			self.bScript.Enable(flag)
			self.bSnapshot.Enable(flag)
			self.bRecord.Enable(flag)

	def OnConnect(self, _):
		self.ConnectToServer()
			
	def OnOccupy(self, _):
		chx = self.chBlock.GetSelection()
		if chx == wx.NOT_FOUND:
			return
		bname = self.chBlock.GetString(chx)
		state = 1 if self.cbOccupy.IsChecked() else 0

		bi = self.iobits["blocks"][bname]["occupancy"]
		if len(bi[0]) > 0:
			byte = bi[0][0][0]
			bit  = bi[0][0][1]
			nodeaddress = bi[1]

			req = {"setinbit": {"address": "0x%x" % nodeaddress, "byte": [byte], "bit": [bit], "value": [state]}}

			self.Request(req)

	def OnOccupyNone(self, _):
		script = []
		for bname in self.blockList:
			bi = self.iobits["blocks"][bname]["occupancy"]
			if len(bi[0]) == 0:
				continue
			print("Block %s" % str(bi), file=sys.stderr)
			byte = bi[0][0][0]
			bit = bi[0][0][1]
			nodeaddress = bi[1]

			script.append({"setinbit": {"address": "0x%x" % nodeaddress, "byte": [byte], "bit": [bit], "value": [0]}})

		if len(script) > 0:
			self.ExecuteScript(script)

	def OnMove(self, _):
		tx = self.chTrain.GetSelection()
		if tx == wx.NOT_FOUND:
			dlg = wx.MessageDialog(self, "Choose a train",
				"choose a train to move", wx.OK | wx.ICON_INFORMATION)
			dlg.ShowModal()
			dlg.Destroy()
			return

		self.trains = self.rrServer.Get("activetrains", {})
		self.UpdateBlocks()
		nb, eb, msg = self.IdentifyNextBlock(self.trains[self.trainNames[tx]])
		rear = self.cbRear.IsChecked()

		if nb is None:
			dlg = wx.MessageDialog(self, "Unable to determine next block",
				msg, wx.OK | wx.ICON_INFORMATION)
			dlg.ShowModal()
			dlg.Destroy()
			return
		else:
			self.Request({"simulate": {"action": "occupy", "block": nb, "state": 1}})
			self.blockOccupied[nb] = True

			if rear:
				self.Request({"simulate": {"action": "occupy", "block": eb, "state": 0}})
				self.blockOccupied[eb] = False

	def UpdateBlocks(self):
		blocks = self.rrServer.Get("getblocks", {})
		for bname, binfo in blocks.items():
			self.blockOccupied[bname] = binfo.get("occupied", 0) == 1

	def OnRear(self, _):
		tx = self.chTrain.GetSelection()
		if tx == wx.NOT_FOUND:
			dlg = wx.MessageDialog(self, "Choose a train",
				"choose a train to move", wx.OK | wx.ICON_INFORMATION)
			dlg.ShowModal()
			dlg.Destroy()
			return

		self.trains = self.rrServer.Get("activetrains", {})
		tr = self.trains[self.trainNames[tx]]
		order = self.ExpandTrainBlockList(tr)
		if order is None:
			dlg = wx.MessageDialog(self,
					"Train %s does not occupy any blocks" % self.trainNames[tx],
					"Train occupies no blocks", wx.OK | wx.ICON_INFORMATION)
			dlg.ShowModal()
			dlg.Destroy()
			return

		east = tr["east"]
		moveEast = east	if self.cbForward.IsChecked() else not east

		if moveEast:
			endBlock = order[-1 if east else 0]
		else:
			endBlock = order[0 if east else -1]

		self.Request({"simulate": {"action": "occupy", "block": endBlock, "state": 0}})
		self.blockOccupied[endBlock] = False

	def OnRefreshTrains(self, _):
		self.trains = self.rrServer.Get("activetrains", {})
		self.trainNames = sorted(self.trains.keys())
		self.chTrain.SetItems(self.trainNames)
		self.chTrain.SetSelection(wx.NOT_FOUND if len(self.trainNames) == 0 else 0)

	def IdentifyNextBlock(self, tr):
		self.layout = LayoutData(self.rrServer)
		print("identify next block for train %s east %s" % (str(tr), tr["east"]))
		blocks = list(reversed(tr["blockorder"]))
		print("initial list of blocks: %s" % str(blocks))
		if len(blocks) == 0:
			return None, None, "Train does not occupy any blocks"

		east = tr["east"]
		moveEast = east	if self.cbForward.IsChecked() else not east
		print("moving east: %s" % str(moveEast))

		order = self.ExpandTrainBlockList(tr)
		if order is None:
			return None, None, "Train does not occupy any blocks"

		print("expanded list of blocks: %s" % str(order))

		if moveEast:
			startBlock = order[0 if east else -1]
			endBlock = order[-1 if east else 0]
		else:
			startBlock = order[-1 if east else 0]
			endBlock = order[0 if east else -1]

		print("start block %s end block %s" % (startBlock, endBlock))

		if startBlock.endswith(".W") and moveEast:
			return startBlock[:-2], endBlock, ""

		elif startBlock.endswith(".E") and not moveEast:
			return startBlock[:-2], endBlock, ""

		elif startBlock.endswith(".W") or startBlock.endswith(".E"):
			startBlock = startBlock[:-2]

		else:
			sbe, sbw = self.layout.GetStopBlocks(startBlock)
			if moveEast:
				if sbe and not self.BlockOccupied(sbe):
					return sbe, endBlock, ""
			else:
				if sbw and not self.BlockOccupied(sbw):
					return sbw, endBlock, ""

		availableBlocks = self.GetAvailableBlocks(startBlock, moveEast)
		print("available blocks returned: %s" % str(availableBlocks))
		routes = self.rrServer.Get("getroutes", {})
		print("routes: %s" % str(routes))
		if len(availableBlocks) == 0:  # This is an OS we are looking at
			print("we are inside an OS looking for the next block")
			try:
				rt = routes[startBlock]
			except KeyError:
				rt = None

			print("current route through OS = %s" % rt)

			# this is the list of blocks in the direction we are headed
			dirBlocks = self.blockOsMap.GetBlockList(startBlock, moveEast)
			print("dirblocks from %s = %s" % (startBlock, str(dirBlocks)))
			if rt:
				discarded = []
				ends = rt[1]
				for end in ends:
					print("look to see if %s is in (%s)" % (end, str(dirBlocks)))
					if end not in dirBlocks:
						print("discarding %s" % end)
						discarded.append(end)
				nends = [e for e in ends if e not in discarded]
				if len(nends) == 0:
					return None, None, "All possible endpoints eliminated for block %s: %s" % (startBlock, str(ends))
				if len(nends) > 1:
					return None, None, "Multiple endpoints remain for block %s: %s" % (startBlock, str(nends))

				nb = nends[0]
				if CrossingEastWestBoundary(startBlock, nb):
					moveEast = not moveEast
					tr["east"] = not tr["east"]

				sbe, sbw = self.layout.GetStopBlocks(nb)
				if moveEast and sbw:
					nb = sbw
				elif not moveEast and sbe:
					nb = sbe
				print("returning blocks start: %s   end: %s" % (nb, endBlock))
				return nb, endBlock, ""

		print("we are past all of the OS logic")
		bl = []
		for ab, sig, osb, rte in availableBlocks:
			r = routes[osb][0]
			print("looking for a match for os %s route %s <=> %s" % (osb, rte, r))
			if r == rte:
				if osb == "KOSN10S11":
					if moveEast:
						osb = "N10.W"
					else:
						osb = "S11.E"
				elif osb == "KOSN20S21":
					if moveEast:
						osb = "N20.W"
					else:
						osb = "S21.E"

				print("adding %s to prospects" % osb)
				bl.append(osb)
			else:
				print("skipping os %s because of route %s != %s" % (osb, r, rte))

		print("final list of blocks: %s" % str(bl))
		if len(bl) == 0:
			return None, None, "Unable to identify next block"

		if len(bl) > 1:
			return None, None, "Multiple next blocks to choose from: %s" % ", ".join(bl)

		print("returning blocks start: %s  end: %s" % (bl[0], endBlock))
		return bl[0], endBlock, ""

	def ExpandTrainBlockList(self, tr):
		blocks = list(reversed(tr["blockorder"]))
		if len(blocks) == 0:
			return None

		order = []
		east = tr["east"]

		print("starting expansion, east = %s" % str(east))

		for b in blocks:
			print("in loop for block %s" % b)
			sbe, sbw = self.layout.GetStopBlocks(b)
			if east:
				print("East, sbe sbw %s %s" % (str(sbe), str(sbw)))
				if sbe and self.BlockOccupied(sbe):
					order.append(sbe)
				if self.BlockOccupied(b):
					order.append(b)
				else:
					print("block %s is not occupied" % b)
				if sbw and self.BlockOccupied(sbw):
					order.append(sbw)
			else:
				print("West, sbe sbw %s %s" % (str(sbe), str(sbw)))
				if sbw and self.BlockOccupied(sbw):
					order.append(sbw)
				if self.BlockOccupied(b):
					order.append(b)
				else:
					print("block %s is not occupied" % b)
				if sbe and self.BlockOccupied(sbe):
					order.append(sbe)

		if len(order) <= 0:
			return None

		return order

	def GetAvailableBlocks(self, blk, moveEast):
		result = []
		if blk is None:
			return result

		rteList = self.layout.GetRoutesForBlock(blk)
		oslist = self.blockOsMap.GetOSList(blk, moveEast)
		for r in rteList:
			e = self.layout.GetRouteEnds(r)
			s = self.layout.GetRouteSignals(r)
			os = self.layout.GetRouteOS(r)

			if os in oslist:
				if e[0] == blk:
					result.append([e[1], s[0], os, r])
				elif e[1] == blk:
					result.append([e[0], s[1], os, r])
		return result

	def BlockOccupied(self, bname):
		try:
			return self.blockOccupied[bname]
		except KeyError:
			return False

	def OnGetBits(self, _):
		dlg = GetBitsDlg(self, self.rrServer, Nodes)
		dlg.Show()
		
	def OnBreaker(self, _):
		chx = self.chBreaker.GetSelection()
		if chx == wx.NOT_FOUND:
			return

		bname = self.chBreaker.GetString(chx)
		bi = self.iobits["breakers"][bname]["status"]
		byte = bi[0][0][0]
		bit  = bi[0][0][1]
		nodeaddress = bi[1]

		val = 1 if self.cbBreaker.IsChecked() else 0

		req = {"setinbit": {"address": "0x%x" % nodeaddress, "byte": [byte], "bit": [bit], "value": [val]}}
		self.Request(req)

	def OnClearBreakers(self, _):
		self.ClearAllBreakers()

	def ClearAllBreakers(self):
		script = []
		for bname in self.iobits["breakers"].keys():
			bi = self.iobits["breakers"][bname]["status"]
			if len(bi[0]) == 0:
				continue

			byte = bi[0][0][0]
			bit = bi[0][0][1]
			nodeaddress = bi[1]
			script.append({"setinbit": {"address": "0x%x" % nodeaddress, "byte": [byte], "bit": [bit], "value": [1]}})

		for s in script:
			self.Request(s)

	def OnHSUnlock(self, _):
		hsx = self.chHSUnlock.GetSelection()
		if hsx == wx.NOT_FOUND:
			return

		hsName = self.chHSUnlock.GetString(hsx)
		try:
			hsi = self.iobits["handswitches"][hsName]["unlock"]
		except KeyError:
			hsi = None
		unlock = self.cbHSUnlock.IsChecked()

		if hsi is not None:
			byte = hsi[0][0][0]
			bit = hsi[0][0][1]
			nodeaddress = hsi[1]

			req = {"setinbit": {"address": "0x%x" % nodeaddress, "byte": [byte], "bit": [bit],
								"value": [1 if unlock else 0]}}

			self.Request(req)

	def OnTurnoutPos(self, _):
		chx = self.chTurnout.GetSelection()
		if chx == wx.NOT_FOUND:
			return

		tname = self.chTurnout.GetString(chx)
		if self.cbNormal.IsChecked():
			valN = 1
			valR = 0
		else:
			valN = 0
			valR = 1

		try:
			ti = self.iobits["turnouts"][tname]["position"]
		except KeyError:
			try:
				ti = self.iobits["handswitches"][tname]["position"]
			except KeyError:
					ti = None

		if ti is not None:
			byteN = ti[0][0][0]
			bitN  = ti[0][0][1]
			byteR = ti[0][1][0]
			bitR  = ti[0][1][1]
			nodeaddress = ti[1]

			req = {"setinbit": {"address": "0x%x" % nodeaddress, "byte": [byteN, byteR], "bit": [bitN, bitR], "value": [valN, valR]}}

			self.Request(req)

	def OnRoutesIn(self, _):
		chx = self.chRoutesIn.GetSelection()
		if chx == wx.NOT_FOUND:
			return

		rname = self.chRoutesIn.GetString(chx)
		try:
			family = self.riFamilies[rname]
		except KeyError:
			family = None

		if family is None:
			return

		family = [r for r in self.riFamilies if self.riFamilies[r] == family and r != rname]

		for r in family:
			ri = self.iobits["routesin"][r]["status"]
			byte = ri[0][0][0]
			bit = ri[0][0][1]
			nodeaddress = ri[1]
			req = {"setinbit": {"address": "0x%x" % nodeaddress, "byte": [byte], "bit": [bit], "value": [0]}}
			self.Request(req)

		ri = self.iobits["routesin"][rname]["status"]
		byte = ri[0][0][0]
		bit  = ri[0][0][1]
		nodeaddress = ri[1]
		req = {"setinbit": {"address": "0x%x" % nodeaddress, "byte": [byte], "bit": [bit], "value": [1]}}
		self.Request(req)

	def OnMatrix(self, _):
		chx = self.chMatrixArea.GetSelection()
		if chx == wx.NOT_FOUND:
			return 

		area = self.chMatrixArea.GetString(chx)
		if area not in self.matrixMap:
			return 
		
		try:
			blist1 = self.matrixMap[area]["entry"]
			blist2 = self.matrixMap[area]["exit"]
		except KeyError:
			try:
				blist1 = self.matrixMap[area]["buttons"]
				blist2 = None
			except KeyError:
				# error
				return
			
		dlg = ButtonChoiceDlg(self, blist1, blist2)
		rc = dlg.ShowModal()
		if rc == wx.ID_OK:
			buttons = dlg.GetResults()
			
		dlg.Destroy()
		if rc != wx.ID_OK:
			return

		reqList = self.SendButtons(area, buttons)
		self.ExecuteScript(reqList)

	def SendButtons(self, area, buttons):
		try:
			bits1  = self.matrixMap[area]["entrybits"]
			bits2  = self.matrixMap[area]["exitbits"]
		except KeyError:
			try:
				bits1  = self.matrixMap[area]["bits"]
				bits2  = None
			except KeyError:
				# error
				return []

		vbytes = []
		vbits = []
		vals1 = []
		vals0 = []
		
		vbytes.append(bits1[buttons[0]][0])
		vbits.append(bits1[buttons[0]][1])
		vals1.append(1)
		vals0.append(0)
		if len(buttons) > 1:
			vbytes.append(bits2[buttons[1]][0])
			vbits.append(bits2[buttons[1]][1])
			vals1.append(1)
			vals0.append(0)

		addr = getNodeAddress(self.matrixMap[area]["node"])
		reqlist = []
		if addr is not None:		
			reqlist.append({"setinbit": {"address": "0x%x" % addr, "byte": vbytes, "bit": vbits, "value": vals1}})
			reqlist.append({"delay": {"ms": 500}}) # we must pause here to let button press register before release
			reqlist.append({"setinbit": {"address": "0x%x" % addr, "byte": vbytes, "bit": vbits, "value": vals0}})
		return reqlist
		
	def OnSigLvr(self, _):
		chx = self.chSigLvr.GetSelection()
		if chx == wx.NOT_FOUND:
			return

		lvr = self.chSigLvr.GetString(chx)
		sli = self.iobits["siglevers"][lvr]["position"]

		right = sli[0][0]
		callon = sli[0][1]
		left = sli[0][2]

		swPos = self.rbSigLever.GetSelection()
		vRight = 1 if swPos == 2 else 0
		vLeft = 1 if swPos == 0 else 0

		# vRight = 1 if self.cbRight.IsChecked() else 0
		# vLeft = 1 if self.cbLeft.IsChecked() else 0
		vCallOn = 1 if self.cbCallOn.IsChecked() else 0

		bytes = []
		bits = []
		vals = []

		if right is not None:
			bytes.append(right[0])
			bits.append(right[1])
			vals.append(vRight)

		if callon is not None:
			bytes.append(callon[0])
			bits.append(callon[1])
			vals.append(vCallOn)

		if left is not None:
			bytes.append(left[0])
			bits.append(left[1])
			vals.append(vLeft)

		addr = sli[1]

		req = {"setinbit": {"address": "0x%x" % addr, "byte": bytes, "bit": bits, "value": vals}}
		self.Request(req)

	def RetrieveSigLevers(self):
		siglvrs = self.rrServer.Get("getsiglevers", {})
		print(json.dumps(siglvrs, indent=2), flush=True)
		return siglvrs

	def OnSigLvrShow(self, _):
		if self.dlgSigLvrs is None:
			self.dlgSigLvrs = SigLeverShowDlg(self, self.CloseSigLvrShow)
			self.dlgSigLvrs.Show()
		else:
			self.dlgSigLvrs.Refresh()
			
	def CloseSigLvrShow(self):
		if self.dlgSigLvrs is None:
			return 
		
		self.dlgSigLvrs.Destroy()
		self.dlgSigLvrs = None
		
	def OnScript(self, _):
		fdir = os.path.join(os.getcwd(), "data", "scripts")
		if not os.path.exists(fdir):
			os.makedirs(fdir)

		dlg = wx.FileDialog(
			self, message="Select script file",
			defaultDir=fdir,
			defaultFile="",
			wildcard="Monitor Script File (*.scr)|*.scr",
			style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST | wx.FD_PREVIEW)

		rc = dlg.ShowModal()
		if rc == wx.ID_OK:
			path = dlg.GetPath()
			
		dlg.Destroy()
		if rc != wx.ID_OK:
			return

		with open(path, "r") as jfp:
			sl = jfp.readlines()
		script = [json.loads(s) for s in sl]
		self.ExecuteScript(script)

	def ExecuteScript(self, script):
		self.script = [c for c in script]
		self.scriptLines = len(self.script)
		if self.scriptLines == 0:
			return

		self.scriptLine = 0
		self.EnableScriptingButtons(False)
		self.EnableButtons(False)

	def EnableScriptingButtons(self, flag=True):
		self.bScript.Enable(flag)
		self.bSnapshot.Enable(flag)
		self.bRecord.Enable(flag or self.recording)
		if self.recording:
			self.bRecord.SetLabel("Stop")
		else:
			self.bRecord.SetLabel("Record")

	def ExecuteScriptLine(self):
		self.lStatus.SetLabel("%d/%d" % (self.scriptLine+1, self.scriptLines))
		c = self.script[self.scriptLine]
		self.scriptLine += 1
		if self.scriptLine >= self.scriptLines:
			self.scriptLine = -1
			self.EnableScriptingButtons(True)
			self.EnableButtons(True)
			dlg = wx.MessageDialog(self, "Script execution completed", "Script execution completed",
					wx.OK | wx.ICON_INFORMATION)

			dlg.ShowModal()
			dlg.Destroy()

		cmd = list(c.keys())[0]
		if self.scriptLine == -1:
			self.lStatus.SetLabel("")

		parms = c[cmd]
		if cmd == "delay":
			try:
				secs = parms["sec"]
			except KeyError:
				secs = None
			try:
				msecs = parms["ms"]
			except KeyError:
				msecs = None

			if secs is None:
				if msecs is None:
					secs = 1
				else:
					secs = msecs / 1000.0

			# pause the ticker from starting the next line until the timer has expired
			# time.sleep(secs)
			print("delay for %f seconds" % secs)
			self.scriptPause = int(secs * 10.0)
			print("setting scriptPause to %d" % self.scriptPause)
		else:
			self.Request(c)
			if cmd == "movetrain":
				try:
					bname = parms["block"][0]
					self.blockOccupied[bname] = True
				except KeyError:
					pass
			elif cmd == "simulate":
				try:
					action = parms["action"][0]
				except KeyError:
					action = None

				if action in ["occupy"]:
					try:
						bname = parms["block"][0]
					except KeyError:
						bname = None
					try:
						bstate = parms["state"][0]
					except KeyError:
						bstate = 1
					if bname is not None:
						self.blockOccupied[bname] = bstate == 1

	def OnRecord(self, _):
		if self.recording:
			self.recording = False
			self.EnableScriptingButtons(True)
			self.SaveScript(self.recordedCommands)
		else:
			self.recording = True
			self.recordedCommands = []
			self.EnableScriptingButtons(False)

	def OnSnapshot(self, _):
		dlg = SnapshotDlg(self)
		rc = dlg.ShowModal()

		if rc != wx.ID_OK:
			dlg.Destroy()
			return

		rTurnouts, rSignals, rSkipNeutral, rTrains = dlg.GetResults()
		dlg.Destroy()

		self.layout = LayoutData(self.rrServer)

		script = []

		#script.extend(self.SnapshotSignals(clearall=True))

		if rTurnouts:
			script.extend(self.SnapshotTurnouts())

		if rSignals:
			script.extend(self.SnapshotSignals(skipred=rSkipNeutral))

		if rTrains:
			script.extend(self.SnapshotTrains())

		if len(script) > 0:
			self.SaveScript(script)
		else:
			dlg = wx.MessageDialog(self, "No script was generated", "No script generated", wx.OK | wx.ICON_INFORMATION)
			dlg.ShowModal()
			dlg.Destroy()

	def SaveScript(self, script):
		fdir = os.path.join(os.getcwd(), "data", "scripts")
		if not os.path.exists(fdir):
			os.makedirs(fdir)

		wildcard = "script files (*.scr)|*.scr"

		jfn = None
		dlg = wx.FileDialog(
			self, message="Save snapshot script as ...", defaultDir=fdir,
			defaultFile="", wildcard=wildcard, style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT
		)
		rc = dlg.ShowModal()
		if rc == wx.ID_OK:
			jfn = dlg.GetPath().lower()
			if not jfn.endswith(".scr"):
				jfn += ".scr"

		dlg.Destroy()
		if rc != wx.ID_OK:
			return

		with open(jfn, "w") as jfp:
			for s in script:
				jfp.write("%s\n" % json.dumps(s))

	def SnapshotTrains(self):
		result = []
		trainlist = self.rrServer.Get("activetrains", {})

		for tname, trn in trainlist.items():
			fullorder = self.ExpandTrainBlockList(trn)

			print("%s: %s" % (tname, str(trn)))

			first = not tname.startswith("??")
			for bname in reversed(fullorder):
				result.append({"simulate": {"action": "occupy", "block": bname, "state": 1}})

				if first:
					first = False
					east = 1 if trn["east"] else 0
					result.append({"delay": {"ms": 1000}})
					result.append({"settrain": {"blocks": [bname], "name": tname, "loco": trn["loco"], "east": east}})
				else:
					result.append({"delay": {"ms": 400}})

		return result

	def OnSigNeutral(self, _):
		script = self.SnapshotSignals(clearall=True, skipred=True)

		slState = self.rrServer.Get("signallevers", {})

		for lvr in self.sigLevers:
			info = self.sigLevers[lvr].GetData()
			if info is None:
				continue

			print(str(info))
			if lvr in slState:
				print("Lever %s state = %s" % (lvr, slState[lvr]))
				state = slState[lvr]
				if state[0] == 0 and state[2] == 0:  # if the lever is not thrown either way, skip
					continue

			if info["left"] is None:
				vbytes = [info["right"][0]]
				vbits = [info["right"][1]]
				vals = [0]
			elif info["right"] is None:
				vbytes = [info["left"][0]]
				vbits = [info["left"][1]]
				vals = [0]
			else:
				vbytes = [info["left"][0], info["right"][0]]
				vbits = [info["left"][1], info["right"][1]]
				vals = [0, 0]

			addr = getNodeAddress(info["node"])
			if addr is not None:
				req = {"setinbit": {"address": "0x%x" % addr, "byte": vbytes, "bit": vbits, "value": vals}}
				script.append(req)

		self.ExecuteScript(script)

	def SnapshotSignals(self, clearall=False, skipred=False):
		# {"signal": {"name": ["PB2L"], "aspect": ["1"], "aspecttype": ["50"], "callon": ["0"]}}
		sigs = self.rrServer.Get("getsignals", {})

		result = []
		for s, sv in sigs.items():
			if clearall:
				aspect = "%d" % sv["aspect"]
				if aspect != "0" or not skipred:
					result.append({"signal": {"name": [s], "aspect": ["0"], "aspecttype": ["%d" % sv["aspecttype"]], "callon": ["0"]}})
			else:
				aspect = "%d" % sv["aspect"]
				if aspect != "0" or not skipred:
					result.append({"signal": {"name": [s], "aspect": [aspect], "aspecttype": ["%d" % sv["aspecttype"]], "callon": ["0"]}})

		return result

	def SnapshotTurnouts(self):
		r = self.rrServer.Get("getturnouts", {})
		tnMap = {}
		for t in r:
			tnMap.update(t)

		tnlist = [tn for tn in tnMap.keys() if tnMap[tn]["position"] == "1"]

		script = []
		for tn in tnlist:
			script.append({"simulate": {"action": "turnoutpos", "turnout": tn, "normal": tnMap[tn]["state"]}})

		routes = self.rrServer.Get("getroutes", {})

		# Handle Waterman Yard
		rtw = routes["YOSWYW"][0]
		rte = routes["YOSWYE"][0]
		script.extend(self.sendRteButton(rte, "Waterman Yard", 0))
		script.extend(self.sendRteButton(rtw, "Waterman Yard", 4))

		# Hyde
		sbits = [[bt, 0] for bt in self.hydeMap.values()]
		for osn in self.hydeGroups.keys():
			try:
				rn = routes[osn][0]
			except (KeyError, IndexError):
				rn = None

			if rn is not None:
				sbits.append([self.hydeMap[rn], 1])

		addr = getNodeAddress("Hyde")
		vbytes = []
		vbits = []
		vals = []
		for bb, v in sbits:
			vbytes.append(bb[0])
			vbits.append(bb[1])
			vals.append(v)

		if addr is not None:
			script.append({"setinbit": {"address": "0x%x" % addr, "byte": vbytes, "bit": vbits, "value": vals}})

		# Green Mountain
		sbits = [[bt, 0] for bt in self.gmMap.values()]
		try:
			rte = routes["COSGME"][0]
		except (KeyError, IndexError):
			rte = None
		if rte is not None:
			sbits.append([self.gmMap[rte], 1])
		try:
			rtw = routes["COSGMW"][0]
		except (KeyError, IndexError):
			rtw = None
		if rtw is not None:
			sbits.append([self.gmMap[rtw], 1])

		addr = getNodeAddress("Green Mtn")
		vbytes = []
		vbits = []
		vals = []
		for bb, v in sbits:
			vbytes.append(bb[0])
			vbits.append(bb[1])
			vals.append(v)

		if addr is not None:
			script.append({"setinbit": {"address": "0x%x" % addr, "byte": vbytes, "bit": vbits, "value": vals}})

		# Sheffield
		sbits = [[bt, 0] for bt in self.matrixMap["Cliff A"]["bits"]]
		try:
			rte = routes["COSSHE"][0]
		except (KeyError, IndexError):
			rte = None
		try:
			rtw = routes["COSSHW"][0]
		except (KeyError, IndexError):
			rtw = None

		for rt in [rte, rtw]:
			if rt is not None:
				try:
					btn, node = self.sheffieldRoutesMap[rt]
				except KeyError:
					btn = None
				if btn is not None:
					try:
						bx = self.matrixMap["Cliff A"]["buttons"].index(btn)
					except ValueError:
						bx = None
					if bx is not None:
						sbits.append([self.matrixMap["Cliff A"]["bits"][bx], 1])

		addr = getNodeAddress("Sheffield")
		vbytes = []
		vbits = []
		vals = []
		for bb, v in sbits:
			vbytes.append(bb[0])
			vbits.append(bb[1])
			vals.append(v)

		if addr is not None:
			script.append({"setinbit": {"address": "0x%x" % addr, "byte": vbytes, "bit": vbits, "value": vals}})

		# Cliff
		sbits = [[bt, 0] for bt in self.matrixMap["Cliff B"]["bits"]]
		try:
			rte = routes["COSSHE"][0]
		except (KeyError, IndexError):
			rte = None
		try:
			rtw = routes["COSSHW"][0]
		except (KeyError, IndexError):
			rtw = None

		for rt in [rte, rtw]:
			if rt is not None:
				try:
					btn, node = self.sheffieldRoutesMap[rt]
				except KeyError:
					btn = None
				if btn is not None:
					try:
						bx = self.matrixMap["Cliff B"]["buttons"].index(btn)
					except ValueError:
						bx = None
					if bx is not None:
						sbits.append([self.matrixMap["Cliff B"]["bits"][bx], 1])

		addr = getNodeAddress("Cliff")
		vbytes = []
		vbits = []
		vals = []
		for bb, v in sbits:
			vbytes.append(bb[0])
			vbits.append(bb[1])
			vals.append(v)

		if addr is not None:
			script.append({"setinbit": {"address": "0x%x" % addr, "byte": vbytes, "bit": vbits, "value": vals}})

		return script

	def sendRteButton(self, route, area, offset):
		bx = 0
		if "Y84" in route:
			bx = 3
		elif "Y83" in route:
			bx = 2
		elif "Y82" in route:
			bx = 1

		return self.SendButtons(area, [bx+offset])

	def OnSetInputBit(self, _):
		dlg = SetInputBitsDlg(self, Nodes)
		dlg.Show()
			
	def OnTrains(self, _):
		if self.dlgTrains is None:
			self.dlgTrains = TrainsDlg(self, self.DlgTrainsExit, self.rrServer)
			self.dlgTrains.Show()

	def DlgTrainsExit(self):
		self.dlgTrains.Destroy()
		self.dlgTrains = None
				
	def OnSessions(self, _):
		if self.dlgSessions is None:
			self.dlgSessions = SessionsDlg(self, self.DlgSessionsExit, self.rrServer)
			self.dlgSessions.Show()

	def DlgSessionsExit(self):
		self.dlgSessions.Destroy()
		self.dlgSessions = None

	def OnQuit(self, _):
		self.rrServer.SendRequest({"quit": {}})
		self.connected = False
		self.EnableButtons(False)

	def Initialize(self):
		self.rrServer = RRServer()
		self.rrServer.SetServerAddress(self.settings.ipaddr, self.settings.serverport)
		self.EnableButtons(False)	

		self.delayedRequests = DelayedRequests()				
		self.Bind(wx.EVT_TIMER, self.OnTicker)
		self.ticker = wx.Timer(self)
		self.tickerCounter = 0
		self.ticker.Start(100)
		
	def OnTicker(self, _):
		self.tickerCounter = (self.tickerCounter + 1) % 4
		if self.tickerCounter == 0:
			self.delayedRequests.CheckForExpiry(self.Request)

		if self.scriptLine >= 0:
			if self.scriptPause > 0:
				self.scriptPause -= 1
			else:
				self.ExecuteScriptLine()

	def ConnectToServer(self):
		layout = self.rrServer.Get("getlayout", {})
		if layout is None:
			self.connected = False
			dlg = wx.MessageDialog(self, "Unable to establish a connection with server",
					"Not Connected", wx.OK | wx.ICON_WARNING)
			dlg.ShowModal()
			dlg.Destroy()
			return self.connected
		else:
			self.connected = True

		self.iobits = self.rrServer.Get("getiobits", {})
		if self.iobits is None:
			self.connected = False
			dlg = wx.MessageDialog(self, "Unable to establish a connection with server",
					"Not Connected", wx.OK | wx.ICON_WARNING)
			dlg.ShowModal()
			dlg.Destroy()
			return self.connected
		else:
			self.connected = True

		if self.connected:
			self.blockOsMap = BlockOSMap(self.rrServer)

		if self.settings.rrserver.simulation:
			bl = []
			for bn, binfo in self.iobits["blocks"].items():
				bits = binfo['occupancy'][0]
				if len(bits) > 0:
					bl.append(bn)

			self.blockList = sorted(bl, key=self.BuildBlockKey)
			self.chBlock.SetItems(self.blockList)
			self.chBlock.SetSelection(0)
	
			t = self.iobits["turnouts"]
			tl = [tn for tn in t.keys() if t[tn]["position"] is not None]

			hs = self.iobits["handswitches"]
			hsl = [hsn for hsn in hs.keys() if hsn not in ["CSw21ab", "PBSw15ab"]]
			tl = tl + hsl

			self.turnoutList = sorted(tl, key=self.BuildTurnoutKey)
			self.chTurnout.SetItems(self.turnoutList)
			self.chTurnout.SetSelection(0)

			b = self.iobits["breakers"]

			bl = [bn for bn in b.keys() if (b[bn]["status"] is not None and len(b[bn]["status"]) > 0)]

			self.breakerList = sorted(bl)
			self.chBreaker.SetItems(self.breakerList)
			self.chBreaker.SetSelection(0)

			ri = self.iobits["routesin"]
			self.routesInList = sorted(list(ri.keys()))
			self.chRoutesIn.SetItems(self.routesInList)
			self.chRoutesIn.SetSelection(0)

			sl = self.iobits["siglevers"]
			self.sigLvrList = sorted(list(sl.keys()))
			self.chSigLvr.SetItems(self.sigLvrList)
			self.chSigLvr.SetSelection(0)

			hs = self.iobits["handswitches"]
			hsl = [hsn for hsn in hs.keys() if len(self.iobits["handswitches"][hsn]["unlock"]) > 0]
			self.hsUnlock = sorted(hsl, key=self.BuildTurnoutKey)
			self.chHSUnlock.SetItems(self.hsUnlock)
			self.chHSUnlock.SetSelection(0)

			if self.connected:
				self.ClearAllBreakers()

		self.EnableButtons(self.connected)			
		return self.connected

	@staticmethod
	def FormatFamilyName(rname):
		first = rname[0]
		last = rname[-1]
		if last not in ["W", "E"]:
			return first
		else:
			return first+last

	def BuildBlockKey(self, blk):
		z = re.match("([A-Za-z]+)([0-9]*)(\\.[EW])?", blk)
		if z is None:
			return blk

		if len(z.groups()) != 3:
			return blk

		base, nbr, suffix = z.groups()
		if nbr != "":
			nbr = "%03d" % int(nbr)

		if suffix is None:
			suffix = ".M"

		return base+nbr+suffix

	def BuildSignalLeverKey(self, slnm):
		z = re.match("([A-Za-z]+)([0-9]+)", slnm)
		if z is None or len(z.groups()) != 2:
			return slnm

		nm, nbr = z.groups()
		return "%s%03d" % (nm, int(nbr))

	@staticmethod
	def BuildTurnoutKey(tonm):
		z = re.match("([A-Za-z]+)([0-9]+)(.*)", tonm)
		if z is None:
			return tonm

		if len(z.groups()) == 2:
			nm, nbr = z.groups()
			return "%s%03d" % (nm, int(nbr))

		elif len(z.groups()) == 3:
			nm, nbr, sfx = z.groups()
			return "%s%03d%s" % (nm, int(nbr), sfx)

		return None

	def Request(self, req):
		if self.connected:
			command = list(req.keys())[0]			
			if "delay" in req[command] and req[command]["delay"] > 0:
				self.delayedRequests.Append(req)
			else:
				if self.recording:
					self.recordedCommands.append(req)
					d = self.GetNeededDelay(req)
					if d > 0:
						self.recordedCommands.append({"delay": {"ms": d}})
				self.rrServer.SendRequest(req)
		else:
			dlg = wx.MessageDialog(self, "No connection with server",
					"Not Connected", wx.OK | wx.ICON_WARNING)
			dlg.ShowModal()
			dlg.Destroy()

	def GetNeededDelay(self, req):
		try:
			action = req["simulate"]["action"]
		except KeyError:
			action = None
		if action is not None:
			return 400

		try:
			s = req["setinbit"]
		except KeyError:
			s = None
		if s is not None:
			return 500

		return 0

	def OnClose(self, evt):
		try:
			self.ticker.Stop()
		except:
			pass
		
		self.Destroy()


class RRServer(object):
	def __init__(self):
		self.ipAddr = None
	
	def SetServerAddress(self, ip, port):
		self.ipAddr = "http://%s:%s" % (ip, port)

	def SendRequest(self, req):
		for cmd, parms in req.items():
			#print("send Request: %s: %s" % (cmd, str(parms)))
			try:
				requests.get(self.ipAddr + "/" + cmd, params=parms, timeout=0.5)
			except requests.exceptions.ConnectionError as e:
				return None
			
		return True
				
	def Get(self, cmd, parms):
		try:
			r = requests.get(self.ipAddr + "/" + cmd, params=parms, timeout=4.0)
		except requests.exceptions.ConnectionError:
			return None
		
		if r.status_code >= 400:
			return None
		
		return r.json()

