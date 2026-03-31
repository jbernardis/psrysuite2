import wx
import wx.lib.newevent

import os, sys
cmdFolder = os.getcwd()
if cmdFolder not in sys.path:
	sys.path.insert(0, cmdFolder)

ofp = open(os.path.join(os.getcwd(), "output", "atc.out"), "w")
efp = open(os.path.join(os.getcwd(), "output", "atc.err"), "w")

sys.stdout = ofp
sys.stderr = efp

import logging
logging.basicConfig(filename=os.path.join(os.getcwd(), "logs", "atc.log"), filemode='w', format='%(asctime)s %(message)s', level=logging.DEBUG)

import json

from dispatcher.constants import aspectprofileindex
from dispatcher.settings import Settings

from atc.block import Block
from atc.train import Trains
from atc.layoutdata import LayoutData

from atc.atclist import ATCListCtrl
from atc.listener import Listener
from atc.rrserver import RRServer
from atc.dccserver import DCCServer
from atc.blockdelay import BlockDelay, BlockDelayDlg
from atc.dccremote import DCCRemote

(DeliveryEvent, EVT_DELIVERY) = wx.lib.newevent.NewEvent()
(DisconnectEvent, EVT_DISCONNECT) = wx.lib.newevent.NewEvent()

defaultProfile = {
	"start": 0,
	"slow": 10,
	"medium": 58,
	"fast": 80,
	"acc": 1,
	"dec": 1
}

TRAIN_CONTROLLED = 1
TRAIN_SHUTTINGDOWN = 2
TRAIN_ENDOFROUTE = 3


class MainFrame(wx.Frame):
	def __init__(self):
		wx.Frame.__init__(self, None, size=(900, 800), style=wx.STAY_ON_TOP | wx.CAPTION | wx.RESIZE_BORDER | wx.CLOSE_BOX)
		self.Bind(wx.EVT_CLOSE, self.OnClose)
		self.Bind(wx.EVT_SIZE, self.OnResize)
		self.Bind(wx.EVT_IDLE,self.OnIdle)

		self.resized = False
		
		self.sessionid = None
		self.settings = Settings()
		self.initialized = False
		self.subscribed = False

		self.blocks = {}
		self.turnouts = {}
		self.signals = {}
		self.routes = {}
		self.roster = None
		self.locos = {}

		self.availableTrains = {}
		self.controlledTrains = {}

		self.listener = None
		self.rrServer = None
		self.dccServer = None
		self.ticker = None
		self.dccRemote = None
		self.blockDelay = None
		self.selectedTrain = None
		
		self.LoadImages(os.path.join(cmdFolder, "images"))
		
		logging.info("psry atc server starting")

		self.title = "PSRY ATC Server"
		
		self.atcList = ATCListCtrl(self, os.getcwd())

		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.AddSpacer(5)

		cszr = wx.BoxSizer(wx.VERTICAL)
		cszr.Add(wx.StaticText(self, wx.ID_ANY, "Available Trains"))

		self.lbAvailable = wx.ListBox(self, wx.ID_ANY, size=(-1, 240), choices=[], style=wx.LB_EXTENDED)
		self.Bind(wx.EVT_LISTBOX, self.OnAvailableChoice, self.lbAvailable)
		cszr.Add(self.lbAvailable)

		hsz.AddSpacer(5)
		hsz.Add(cszr)

		hsz.AddSpacer(5)

		btnsz = wx.BoxSizer(wx.VERTICAL)

		self.bAdd = wx.Button(self, wx.ID_ANY, ">>", size=(25, 33))
		self.Bind(wx.EVT_BUTTON, self.OnBAdd, self.bAdd)
		self.bAdd.Enable(False)
		btnsz.Add(self.bAdd)

		btnsz.AddSpacer(40)

		self.bDel = wx.Button(self, wx.ID_ANY, "<<", size=(25, 33))
		self.Bind(wx.EVT_BUTTON, self.OnBDel, self.bDel)
		self.bDel.Enable(False)
		btnsz.Add(self.bDel)

		hsz.Add(btnsz, 0, wx.ALIGN_CENTER_VERTICAL)
		hsz.AddSpacer(5)

		hsz.Add(self.atcList)
		hsz.AddSpacer(5)
		
		btnszr = wx.BoxSizer(wx.VERTICAL)
		self.bLight = wx.BitmapButton(self, wx.ID_ANY, self.imageLight, size=(32, 32))
		self.bLight.SetToolTip("Headlight On/Off")
		self.Bind(wx.EVT_BUTTON, self.OnBLight, self.bLight)
		btnszr.Add(self.bLight)
		btnszr.AddSpacer(5)
		
		self.bHorn = wx.BitmapButton(self, wx.ID_ANY, self.imageHorn, size=(32, 32))
		self.bHorn.SetToolTip("Horn On/Off")
		self.Bind(wx.EVT_BUTTON, self.OnBHorn, self.bHorn)
		btnszr.Add(self.bHorn)
		btnszr.AddSpacer(5)
		
		self.bBell = wx.BitmapButton(self, wx.ID_ANY, self.imageBell, size=(32, 32))
		self.bBell.SetToolTip("Bell On/Off")
		self.Bind(wx.EVT_BUTTON, self.OnBBell, self.bBell)
		btnszr.Add(self.bBell)
		btnszr.AddSpacer(20)
		
		self.bStop = wx.BitmapButton(self, wx.ID_ANY, self.imageStop, size=(32, 32))
		self.bStop.SetToolTip("Force stop")
		self.Bind(wx.EVT_BUTTON, self.OnBStop, self.bStop)
		btnszr.Add(self.bStop)

		hsz.Add(btnszr)
		hsz.AddSpacer(5)
		
		vsz = wx.BoxSizer(wx.VERTICAL)
		vsz.AddSpacer(5)

		btnszr = wx.BoxSizer(wx.HORIZONTAL)
		btnszr.AddSpacer(10)

		self.bConnect = wx.Button(self, wx.ID_ANY, "Connect",  size=(96, 24))
		self.Bind(wx.EVT_BUTTON, self.OnBConnect, self.bConnect)
		btnszr.Add(self.bConnect)

		btnszr.AddSpacer(30)

		self.bBlockDelay = wx.Button(self, wx.ID_ANY, "Block Delays",  size=(96, 24))
		self.Bind(wx.EVT_BUTTON, self.OnBBlockDelay, self.bBlockDelay)
		btnszr.Add(self.bBlockDelay)

		btnszr.AddSpacer(10)

		vsz.Add(btnszr)
		vsz.AddSpacer(5)

		vsz.Add(hsz)
		vsz.AddSpacer(5)

		self.SetSizer(vsz)
		self.Layout()
		self.Fit()

		self.Show()
		
		wx.CallAfter(self.Initialize)
		self.startingWidth = self.GetSize()[0]
		
	def LoadImages(self, imgFolder):
		png = wx.Image(os.path.join(imgFolder, "headlight.png"), wx.BITMAP_TYPE_PNG).ConvertToBitmap()
		mask = wx.Mask(png, wx.BLUE)
		png.SetMask(mask)
		self.imageLight = png

		png = wx.Image(os.path.join(imgFolder, "headlight_on.png"), wx.BITMAP_TYPE_PNG).ConvertToBitmap()
		mask = wx.Mask(png, wx.BLUE)
		png.SetMask(mask)
		self.imageLightOn = png

		png = wx.Image(os.path.join(imgFolder, "horn.png"), wx.BITMAP_TYPE_PNG).ConvertToBitmap()
		mask = wx.Mask(png, wx.BLUE)
		png.SetMask(mask)
		self.imageHorn = png

		png = wx.Image(os.path.join(imgFolder, "horn_on.png"), wx.BITMAP_TYPE_PNG).ConvertToBitmap()
		mask = wx.Mask(png, wx.BLUE)
		png.SetMask(mask)
		self.imageHornOn = png

		png = wx.Image(os.path.join(imgFolder, "bell.png"), wx.BITMAP_TYPE_PNG).ConvertToBitmap()
		mask = wx.Mask(png, wx.BLUE)
		png.SetMask(mask)
		self.imageBell = png

		png = wx.Image(os.path.join(imgFolder, "bell_on.png"), wx.BITMAP_TYPE_PNG).ConvertToBitmap()
		mask = wx.Mask(png, wx.BLUE)
		png.SetMask(mask)
		self.imageBellOn = png

		png = wx.Image(os.path.join(imgFolder, "atlRed.png"), wx.BITMAP_TYPE_PNG).ConvertToBitmap()
		mask = wx.Mask(png, wx.BLUE)
		png.SetMask(mask)
		self.imageStop = png

		png = wx.Image(os.path.join(imgFolder, "atlGreen.png"), wx.BITMAP_TYPE_PNG).ConvertToBitmap()
		mask = wx.Mask(png, wx.BLUE)
		png.SetMask(mask)
		self.imageResume = png

	def ShowTitle(self):
		titleString = self.title
		if self.subscribed and self.sessionid is not None:
			titleString += ("  -  Session ID %d" % self.sessionid)
		self.SetTitle(titleString)

	def OnBConnect(self, _):
		if self.subscribed:
			self.DisconnectServer()
		else:
			self.ConnectServer()

	def OnBBlockDelay(self, _):
		dlg = BlockDelayDlg(self, self.rrServer, self.blocks)
		rc = dlg.ShowModal()
		dlg.Destroy()

		if rc == wx.ID_OK:
			#  reload the block delay table
			self.blockDelay = BlockDelay(self.rrServer)

	def ConnectServer(self):
		self.dccServer = DCCServer()
		self.dccServer.SetServerAddress(self.settings.ipaddr, self.settings.dccserverport)
		self.dccRemote = DCCRemote(self.dccServer)

		self.listener = Listener(self, self.settings.ipaddr, self.settings.socketport)
		if not self.listener.connect():
			logging.error("Unable to establish connection with railroad server")
			self.listener = None
			return
		self.listener.start()
		self.subscribed = True
		self.bConnect.SetLabel("Disconnect")
		self.ShowTitle()

	def DisconnectServer(self):
		for trid in self.controlledTrains.keys():
			self.RRRequest({"settraincontrol": {"name": trid, "atc": 0}})

		self.subscribed = False
		self.sessionid = None
		self.bConnect.SetLabel("Connect")
		try:
			self.ticker.Stop()
		except:
			pass

		self.atcList.ClearAll()
		self.availableTrains = {}
		self.controlledTrains = {}
		self.lbAvailable.SetItems([])
		self.ShowTitle()

		self.dccServer = None
		self.dccRemote = None
		self.listener.kill()
		self.listener.join()
		self.listener = None


	def Initialize(self):
		self.ShowTitle()
		self.rrServer = RRServer()
		self.rrServer.SetServerAddress(self.settings.ipaddr, self.settings.serverport)

		# load the layout information
		if not self.GetLayoutInformation():
			return

		self.blockDelay = BlockDelay(self.rrServer)

		self.blocks["KOSN10S11"] = Block(self, "KOSN10S11", 0, 'W', True)
		self.blocks["KOSN20S21"] = Block(self, "KOSN20S21", 0, 'E', True)

		self.ticker = wx.Timer(self)

		self.ConnectServer()

		self.initialized = True

		self.ReportSelection(None)
		
		self.Bind(EVT_DELIVERY, self.OnDeliveryEvent)
		self.Bind(EVT_DISCONNECT, self.OnDisconnectEvent)
		self.Bind(wx.EVT_TIMER, self.OnTickerEvent, self.ticker)

		logging.info("exit initialize")

	def GetLayoutInformation(self):
		layout = LayoutData(self.rrServer)
		if layout is None:
			logging.error("Unable to retrieve layout information")
			return False

		subblocks = layout.subblocks

		submap = {}
		for blk, sublist in subblocks.items():
			for sub in sublist:
				submap[sub] = blk

		self.roster = Trains(self.rrServer)
		if self.roster is None:
			logging.error("Unable to retrieve trains information")
			return False

		self.locos = self.rrServer.Get("getlocos", {})
		if self.locos is None:
			logging.error("Unable to retrieve locos")
			self.locos = {}

		return True

	def OnTickerEvent(self, _):
		if len(self.controlledTrains) == 0:
			return

		for trid, tr in self.controlledTrains.items():
			if tr["state"] != TRAIN_ENDOFROUTE:
				if self.EvaluateTrain(trid, tr):
					if tr["step"] is not None:
						self.ApplyStep(trid, tr)

				self.atcList.RefreshTrain(trid)

	def EvaluateTrain(self, trid, tr):
		leadBlock = tr["blocks"][-1]
		if leadBlock.endswith(".E") or leadBlock.endswith(".W"):
			leadBlock = leadBlock[:-2]

		# don't change anything if there is a delay
		if tr["delay"] > 0:
			tr["delay"] -= 1
			tr["status"] = "Delay %d" % tr["delay"]
			return True

		if tr["forcedstop"]:
			if tr["speed"] != 0:
				tr["status"] = "Forced stop"
			tr["state"] = TRAIN_CONTROLLED
			tr["start"] = 0
			tr["target"] = 0
			tr["step"] = -tr["speed"]
			return True

		self.followRoute = True
		if self.followRoute:
			inOs = False
			try:
				idx = tr["script"]["blocks"].index(leadBlock)
			except ValueError:
				try:
					idx = tr["script"]["oses"].index(leadBlock)
					inOs = True
				except ValueError:
					tr["status"] = "Unknown block: %s" % leadBlock
					tr["state"] = TRAIN_SHUTTINGDOWN
					tr["start"] = 0
					tr["target"] = 0
					tr["step"] = -10
					return True

		else:
			inOs = leadBlock in self.routes

		# while in an OS, the governing signal is 0, so do not change the target until we enter the next block
		if not inOs:
			# make sure the OS ahead is set to the right route
			if self.followRoute:
				try:
					osn = tr["script"]["oses"][idx]
				except IndexError:
					tr["status"] = "End of train route"
					tr["state"] = TRAIN_SHUTTINGDOWN
					tr["start"] = 0
					tr["target"] = 0
					tr["step"] = -10
					return True

				osrte = self.routes.get(osn, None)
				if osrte != tr["script"]["routes"][idx]:
					tr["status"] = "OS %s incorrect route" % osn
					tr["start"] = 0
					tr["target"] = 0
					tr["step"] = -10
					return True

			aspect = self.signals.get(tr["signal"], None)
			aspectType = tr["aspecttype"]
			tr["start"], tr["target"], tr["step"] = self.GetSpeedTarget(tr, aspect, aspectType)
			if tr["target"] == 0:
				tr["status"] = "Signal %s" % tr["signal"]
			elif tr["speed"] == tr["target"]:
				tr["status"] = "At target speed"
			elif tr["step"] > 0:
				tr["status"] = "Accelerating"
			elif tr["step"] < 0:
				tr["status"] = "Decelerating"
			else:
				tr["status"] = ""
		return True

	def ApplyStep(self, trid, tr):
		step = tr["step"]
		start = tr["start"]
		target = tr["target"]

		speed = tr["speed"]

		if speed == target:
			return

		if step > 0 and start > speed:
			tr["speed"] = start
			self.dccRemote.SetSpeed(tr["loco"], short=tr["short"], speed=tr["speed"])
		elif step == 0:
			tr["status"] = "At target speed"
		else:
			speed += step
			tr["speed"] = speed
			if (step > 0 and speed >= target) or (step < 0 and speed <= target):
				tr["speed"] = target
				if tr["state"] == TRAIN_SHUTTINGDOWN:
					tr["state"] = TRAIN_ENDOFROUTE
					tr["status"] = "End of train route"
				else:
					tr["status"] = "At target speed"
			self.dccRemote.SetSpeed(tr["loco"], short=tr["short"], speed=tr["speed"])

		# self.atcList.RefreshTrain(trid)

	def GetSpeedTarget(self, tr, aspect, aspectType):
		profile = tr["prof"]
		speed = tr["speed"]

		idx = aspectprofileindex(aspect, aspectType)
		if idx == 0:  # stop
			return 0, 0, 0 if speed == 0 else -10

		if idx == 1:  # restricting
			target = profile["slow"]
		elif idx == 2:  # approach
			target = profile["medium"]
		else:  # clear
			target = profile["fast"]

		start = profile["start"]

		if target > speed:
			return start, target, profile["acc"]
		elif target < speed:
			return start, target, -profile["dec"]
		else:
			return start, target, 0

	def raiseDeliveryEvent(self, data): # thread context
		try:
			jdata = json.loads(data)
		except json.decoder.JSONDecodeError:
			return
		evt = DeliveryEvent(data=jdata)
		wx.QueueEvent(self, evt)

	def OnDeliveryEvent(self, evt):
		for cmd, parms in evt.data.items():
			if cmd == "turnout":
				for p in parms:
					turnout = p["name"]
					state = p["state"]
					locked = p.get("locked", False)
					self.turnouts[turnout] = (state, locked)
			elif cmd == "block":
				for p in parms:
					block = p["name"]
					state = p["state"]
					self.blocks[block] = state

			elif cmd == "showaspect":
				for p in parms:
					sigName = p["signal"]
					aspect = p["aspect"]
					self.signals[sigName] = aspect

			elif cmd == "setroute":
				for p in parms:
					blknm = p["os"]
					rte = p["route"]
					self.routes[blknm] = rte

			elif cmd == "lockturnout":
				for p in parms:
					tonm = p["name"]
					lock = p["lock"]
					pos, x = self.turnouts[tonm]
					self.turnouts[tonm] = (pos, lock)

			elif cmd == "train":
				for p in parms:
					iname = p["iname"]
					rname = p["rname"]
					loco = p['loco']
					logging.debug("iname = %s  rname = %s  loco = %s" % (str(iname), str(rname), str(loco)))
					roster = self.roster.GetTrainById(rname)
					if rname is None or roster is None:
						logging.debug("skipping train %s because it is unknown" % iname)
						continue
					if loco is None or loco == "??":
						logging.debug("skipping train %s because it has no loco address" % iname)
						continue
					if loco not in self.locos.keys():
						logging.debug("Skipping train %s loco %s because loco is not defined" % (iname, loco))
						continue

					if rname in self.controlledTrains:
						tr = self.controlledTrains[rname]
						preBlocks = [b for b in tr["blocks"]]
						self.controlledTrains[rname].update(p)
						if len(p["blocks"]) == 0:
							# remove the train from the controlled list
							self.atcList.DelTrainByName(rname)
							del self.controlledTrains[rname]

						# determine if we've moved into a new block and if it has a delay before
						# we start paying attention to the signal at the other end.  Direction
						# affects delay - a westbound train in a west end stop section should have
						# no delay, but that same train in an east end stop section should be delayed.
						# the delay allows some time for the route to be setup before we start stopping the train
						newBlocks = [b for b in p["blocks"] if b not in preBlocks]
						leadBlock = tr["blocks"][-1]
						# Don't delay processing if:
						#  1) the new blocks list is empty
						#  2) the train is already stopped or (target is 0 and step is negative)
						# otherwise, refer to the block delay table to get the time.  The time is
						# in intervals which is currently 0.5 seconds
						if len(newBlocks) == 0:
							continue
						if tr["speed"] == 0:
							continue
						if tr["target"] == 0 and tr["step"] < 0:
							continue

						tr["delay"] = self.blockDelay.GetBlockDelay(leadBlock, tr["east"])

					elif len(p["blocks"]) > 0:
						if rname not in self.availableTrains:
							self.availableTrains[rname] = p
							choices = sorted(self.availableTrains.keys())
							self.lbAvailable.SetItems(choices)
							self.lbAvailable.SetSelection(0)
							self.bAdd.Enable(True)
						else:
							self.availableTrains[rname].update(p)
					else:
						if rname in self.availableTrains:
							del self.availableTrains[rname]
							choices = sorted(self.availableTrains.keys())
							self.lbAvailable.SetItems(choices)
							if len(choices) > 0:
								self.lbAvailable.SetSelection(0)
								self.bAdd.Enable(True)
							else:
								self.lbAvailable.SetSelection(wx.NOT_FOUND)
								self.bAdd.Enable(False)

			elif cmd == "sessionID":
				self.sessionid = int(parms)
				self.ShowTitle()
				logging.info("session ID %d" % self.sessionid)

				# associate our session id with the ATC function
				self.RRRequest({"identify": {"SID": self.sessionid, "function": "ATC"}})
				# kick off the refresh action
				self.RRRequest({"refresh": {"SID": self.sessionid}})

			elif cmd == "end":
				self.ticker.Start(500)
				pass

			elif cmd in ["disconnect", "exit"]:
				self.running = False
				
			elif cmd == "atc":
				action = parms["action"][0]
				logging.debug("AR Action: %s" % action)
				
				if action == "show":
					if self.IsShown():
						self.Hide()
					else:
						self.MoveToTop()

			else:
				logging.info("unknown command ignored: %s: %s" % (cmd, parms))

	def MoveToTop(self):
		st = self.GetWindowStyle()
		st |= wx.STAY_ON_TOP

		self.SetWindowStyle(st)
		self.Show()

	def OnBAdd(self, _):
		il = self.lbAvailable.GetSelections()
		for i in il:
			trid = self.lbAvailable.GetString(i)
			loco = self.availableTrains[trid]["loco"]
			self.controlledTrains[trid] = self.availableTrains[trid]
			self.controlledTrains[trid]["delay"] = 0
			self.controlledTrains[trid]["forcedstop"] = False
			self.controlledTrains[trid]["state"] = TRAIN_CONTROLLED
			self.controlledTrains[trid]["status"] = ""
			self.controlledTrains[trid]["speed"] = 0
			self.controlledTrains[trid]["target"] = 0
			self.controlledTrains[trid]["step"] = 0
			self.controlledTrains[trid]["headlight"] = False
			self.controlledTrains[trid]["horn"] = False
			self.controlledTrains[trid]["bell"] = False
			self.controlledTrains[trid]["forcedstop"] = False
			self.controlledTrains[trid]["prof"] = self.locos[loco].get("prof", defaultProfile)
			short = self.locos[loco]["short"]
			self.controlledTrains[trid]["short"] = short

			self.RRRequest({"settraincontrol": {"name": trid, "atc": 1}})

			roster = self.roster.GetTrainById(trid)
			steps = roster.GetSteps()

			blockSeq = [roster.GetStartBlock()] + [s["block"] for s in steps]
			signalSeq = [s["signal"] for s in steps]
			osSeq = [s["os"] for s in steps]
			rteSeq = [s["route"] for s in steps]

			currentBlock = self.controlledTrains[trid]["blocks"][-1]
			if currentBlock.endswith(".E") or currentBlock.endswith(".W"):
				currentBlock = currentBlock[:-2]

			try:
				idx = blockSeq.index(currentBlock)
			except ValueError:
				try:
					idx = osSeq.index(currentBlock)
				except ValueError:
					idx = None  # Train is in an unexpected block

			self.controlledTrains[trid]["script"] = {
				"blocks": blockSeq,
				"signals": signalSeq,
				"oses": osSeq,
				"routes": rteSeq
			}
			self.controlledTrains[trid]["index"] = idx
			tr = self.controlledTrains[trid]
			self.dccRemote.SetSpeed(tr["loco"], short=tr["short"], speed=0)

			self.atcList.AddTrain(self.controlledTrains[trid])
			del self.availableTrains[trid]

			self.RRRequest({"assigntrain": {"name": trid, "engineer": "ATC"}})

		choices = sorted(self.availableTrains.keys())
		self.lbAvailable.SetItems(choices)
		if len(choices) == 0:
			self.lbAvailable.SetSelection(wx.NOT_FOUND)
			self.bAdd.Enable(False)
		else:
			self.lbAvailable.SetSelection(0)
			self.bAdd.Enable(True)

	def OnBDel(self, _):
		if self.selectedTrain is None:
			return
		trid = self.selectedTrain

		self.RRRequest({"assigntrain": {"name": trid, "engineer": "-"}})
		self.RRRequest({"settraincontrol": {"name": trid, "atc": 0}})
		self.atcList.DelTrainByName(trid)
		tr = self.controlledTrains[trid]
		self.availableTrains[trid] = tr
		del self.controlledTrains[trid]

		choices = sorted(self.availableTrains.keys())
		self.lbAvailable.SetItems(choices)
		self.lbAvailable.SetSelection(0)
		self.bAdd.Enable(True)
		self.dccRemote.SetSpeed(tr["loco"], short=tr["short"], speed=0)

	def OnAvailableChoice(self, _):
		pass

	def RRRequest(self, req):
		logging.info("Outgoing request: %s" % json.dumps(req))
		self.rrServer.SendRequest(req)

	def raiseDisconnectEvent(self): # thread context
		evt = DisconnectEvent()
		wx.PostEvent(self, evt)

	def OnDisconnectEvent(self, _):
		self.DisconnectServer()

	def ReportSelection(self, trnm):
		flag = trnm is not None
		self.selectedTrain = trnm
		self.EnableButtons(flag)
		if trnm is None:
			self.bLight.SetBitmap(self.imageLight)
			self.bHorn.SetBitmap(self.imageHorn)
			self.bBell.SetBitmap(self.imageBell)
			self.bStop.SetBitmap(self.imageStop)
			self.bStop.SetToolTip("Force stop")
			self.bDel.Enable(False)

		else:
			tr = self.controlledTrains[trnm]
			self.bLight.SetBitmap(self.imageLightOn if tr["headlight"] else self.imageLight)
			self.bHorn.SetBitmap(self.imageHornOn if tr["horn"] else self.imageHorn)
			self.bBell.SetBitmap(self.imageBellOn if tr["bell"] else self.imageBell)
			self.bStop.SetBitmap(self.imageResume if tr["forcedstop"] else self.imageStop)
			self.bStop.SetToolTip("Resume from forced stop" if tr["forcedstop"] else "Force stop")
			self.bDel.Enable(True)

	def EnableButtons(self, flag):
		self.bLight.Enable(flag)
		self.bHorn.Enable(flag)
		self.bBell.Enable(flag)
		self.bStop.Enable(flag)

	def OnBLight(self, _):
		tr = self.controlledTrains.get(self.selectedTrain, None)
		if tr is None:
			return

		light = not tr["headlight"]
		tr["headlight"] = light

		self.dccRemote.SetFunction(tr["loco"], short=tr["short"], headlight=light)
		self.atcList.RefreshTrain(self.selectedTrain)
		self.bLight.SetBitmap(self.imageLightOn if light else self.imageLight)

	def OnBHorn(self, _):
		tr = self.controlledTrains.get(self.selectedTrain, None)
		if tr is None:
			return

		horn = not tr["horn"]
		tr["horn"] = horn

		self.dccRemote.SetFunction(tr["loco"], short=tr["short"], horn=horn)
		self.atcList.RefreshTrain(self.selectedTrain)
		self.bHorn.SetBitmap(self.imageHornOn if horn else self.imageHorn)
		
	def OnBBell(self, _):
		tr = self.controlledTrains.get(self.selectedTrain, None)
		if tr is None:
			return

		bell = not tr["bell"]
		tr["bell"] = bell

		self.dccRemote.SetFunction(tr["loco"], short=tr["short"], bell=bell)
		self.atcList.RefreshTrain(self.selectedTrain)
		self.bBell.SetBitmap(self.imageBellOn if bell else self.imageBell)

	def OnBStop(self, _):
		tr = self.controlledTrains.get(self.selectedTrain, None)
		if tr is None:
			return

		stop = not tr["forcedstop"]
		tr["forcedstop"] = stop

		self.atcList.RefreshTrain(self.selectedTrain)
		self.bStop.SetBitmap(self.imageResume if stop else self.imageStop)
		self.bStop.SetToolTip("Resume from forced stop" if stop else "Force stop")

	def OnResize(self, evt):
		self.resized = True
		
	def OnIdle(self, evt):
		if not self.resized:
			return 
		
		self.resized = False
		sz = self.GetSize()
		sz[0] = self.startingWidth
		self.atcList.ChangeSize(sz)
		self.SetSize(sz)
		
	def OnClose(self, evt):
		if self.subscribed:
			self.Hide()
		else:
			self.kill()
		
	def kill(self):
		try:
			self.listener.kill()
			self.listener.join()
		except:
			pass
		
		try:
			self.ticker.Stop()
		except:
			pass
		
		self.Destroy()


class App(wx.App):
	def __init__(self, redirect=False, filename=None, useBestVisual=False, clearSigInt=True):
		super().__init__(redirect, filename, useBestVisual, clearSigInt)
		self.frame = None

	def OnInit(self):
		self.frame = MainFrame()
		return True


app = App(False)
app.MainLoop()

logging.info("exiting program")