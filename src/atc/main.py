import wx
import wx.lib.newevent

import os, sys
cmdFolder = os.getcwd()
if cmdFolder not in sys.path:
	sys.path.insert(0, cmdFolder)

# ofp = open(os.path.join(os.getcwd(), "output", "atc.out"), "w")
# efp = open(os.path.join(os.getcwd(), "output", "atc.err"), "w")
#
# sys.stdout = ofp
# sys.stderr = efp

import logging
logging.basicConfig(filename=os.path.join(os.getcwd(), "logs", "atc.log"), filemode='w', format='%(asctime)s %(message)s', level=logging.DEBUG)

import json

from dispatcher.constants import RegAspects
from dispatcher.settings import Settings

from atc.turnout import Turnout
from atc.signal import Signal
from atc.block import Block
from atc.overswitch import OverSwitch
from atc.train import Trains
from atc.route import Route
from atc.generatescripts import GenerateScripts
from atc.layoutdata import LayoutData

#from atc.dccremote import DCCRemote
from atc.atclist import ATCListCtrl
from atc.listener import Listener
from atc.rrserver import RRServer
from atc.dccserver import DCCServer

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
		# self.dccRemote = None

		self.selectedTrain = None
		
		self.LoadImages(os.path.join(cmdFolder, "images"))
		
		logging.info("psry atc server starting")

		self.SetTitle("PSRY ATC Server")
		
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

		self.bAdd = wx.Button(self, wx.ID_ANY, ">>")
		self.Bind(wx.EVT_BUTTON, self.OnBAdd, self.bAdd)
		self.bAdd.Enable(False)
		btnsz.Add(self.bAdd)

		btnsz.AddSpacer(40)

		self.bDel = wx.Button(self, wx.ID_ANY, "<<")
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
		
		hsz.Add(btnszr)
		hsz.AddSpacer(5)
		
		btnszr = wx.BoxSizer(wx.VERTICAL)
		self.bStop = wx.BitmapButton(self, wx.ID_ANY, self.imageStop, size=(32, 32))
		self.bStop.SetToolTip("Force stop")
		self.Bind(wx.EVT_BUTTON, self.OnBStop, self.bStop)
		btnszr.Add(self.bStop)
		btnszr.AddSpacer(5)
		
		self.bAtcOff = wx.BitmapButton(self, wx.ID_ANY, self.imageAtcOff, size=(32, 32))
		self.bAtcOff.SetToolTip("Remove From ATC")
		self.Bind(wx.EVT_BUTTON, self.OnBAtcOff, self.bAtcOff)
		btnszr.Add(self.bAtcOff)
		
		hsz.Add(btnszr)
		hsz.AddSpacer(5)
		
		vsz = wx.BoxSizer(wx.VERTICAL)
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
		
		png = wx.Image(os.path.join(imgFolder, "horn.png"), wx.BITMAP_TYPE_PNG).ConvertToBitmap()
		mask = wx.Mask(png, wx.BLUE)
		png.SetMask(mask)
		self.imageHorn = png
		
		png = wx.Image(os.path.join(imgFolder, "bell.png"), wx.BITMAP_TYPE_PNG).ConvertToBitmap()
		mask = wx.Mask(png, wx.BLUE)
		png.SetMask(mask)
		self.imageBell = png
		
		png = wx.Image(os.path.join(imgFolder, "stop.png"), wx.BITMAP_TYPE_PNG).ConvertToBitmap()
		mask = wx.Mask(png, wx.BLUE)
		png.SetMask(mask)
		self.imageStop = png
		
		png = wx.Image(os.path.join(imgFolder, "atcoff.png"), wx.BITMAP_TYPE_PNG).ConvertToBitmap()
		mask = wx.Mask(png, wx.BLUE)
		png.SetMask(mask)
		self.imageAtcOff = png

	def Initialize(self):
		logging.info("enter initialize")

		self.rrServer = RRServer()
		self.rrServer.SetServerAddress(self.settings.ipaddr, self.settings.serverport)

		# load the layout information
		if not self.GetLayoutInformation():
			return

		self.blocks["KOSN10S11"] = Block(self, "KOSN10S11", 0, 'W', True)
		self.blocks["KOSN20S21"] = Block(self, "KOSN20S21", 0, 'E', True)

		self.ticker = wx.Timer(self)

		self.dccServer = DCCServer()
		self.dccServer.SetServerAddress(self.settings.ipaddr, self.settings.dccserverport)
		# self.dccRemote = DCCRemote(self.dccServer, self.blocks, self.turnouts, self.signals, self.routes, self.roster)

		self.listener = Listener(self, self.settings.ipaddr, self.settings.socketport)
		if not self.listener.connect():
			logging.error("Unable to establish connection with railroad server")
			self.listener = None
			return
		self.listener.start()

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

		# self.dccRemote.Initialize(self.locos)

		return True

	def OnTickerEvent(self, _):
		if len(self.controlledTrains) == 0:
			return

		for trid, tr in self.controlledTrains.items():
			target = self.CalculateTarget(trid, tr)
			if target is not None:
				tr["target"] = target

	def CalculateTarget(self, trid, tr):
		print("looking at train %s" % trid)
		print("Signal %s, aspect=%d" % (tr["signal"], self.signals[tr["signal"]]))
		leadBlock = tr["blocks"][-1]
		print("lead block = %s" % leadBlock)
		inOs = False
		try:
			idx = tr["script"]["blocks"].index(leadBlock)
		except ValueError:
			try:
				idx = tr["script"]["oses"].index(leadBlock)
				inOs = True
			except ValueError:
				# Alert train is in unknown block - but only do it once
				return 0  # we can't identify the block - stop the train

		# while in an OS, the governing signal is 0, so do not change the target until we enter the next block
		if not inOs:
			aspect = self.signals.get(tr["signal"], None)
			aspectType = tr["aspecttype"]
			print("Signals: %s <=> %s" % (tr["signal"], tr["script"]["signals"][idx]))


	# 	gs, _ = dccl.GetGoverningSignal()
		# 	aspect = 0  # assume STOP
		# 	aspectType = RegAspects
		#
		# 	if dccl.HasCompleted():
		# 		logging.info("Train %s has completed" % dccl.GetTrain())
		# 		aspect = 0 # we've reached the terminus - we should stop
		#
		# 	elif gs is None:
		# 		logging.info("governing signal is None")
		# 		# we are moving into terminus block - move slowly
		# 		aspect = 4 # restricting
		#
		# 	elif "signal" in gs:
		# 		signame = gs["signal"]
		# 		logging.info("Governing signal is %s" % signame)
		# 		if signame in self.signals:
		# 			aspect, aspectType = self.signals[signame].GetAspect()
		# 			logging.info("Retrieved aspect = %s" % str(aspect))
		#
		# 		if "os" in gs and "route" in gs and aspect != 0:
		# 			overswitch = gs["os"]
		# 			route = gs["route"]
		# 			logging.info("Wanted os/route is %s/%s, active route is %s" % (overswitch, route, self.osList[overswitch].GetActiveRouteName()))
		# 			if overswitch in self.osList and self.osList[overswitch].GetActiveRouteName() != route:
		# 				# either we don't know that OS or its not set to the needed route
		# 				logging.info("setting aspect to 0")
		# 				aspect = 0
		# 				aspectType = RegAspects
		#
		# 	else:
		# 		logging.error("Unable to interpret governing signal %s" % str(gs))
		#
		# 	logging.info("Using aspect %d/%d" % (aspect, aspectType))
		# 	dccl.SetGoverningAspect(aspect, aspectType)
		# 	dccl.SetPendingStop(dccl.GetGoverningAspect() == 0)
		#
		# 	self.dccRemote.SelectLoco(dccl.GetLoco())
		#
		# 	speed = self.dccRemote.ApplySpeedStep() #step)
		# 	if speed == 0 and dccl.HasCompleted():
		# 		self.atcList.DelTrain(dccl)
		# 		loco = dccl.GetLoco()
		# 		train = dccl.GetTrain()
		# 		self.dccRemote.DropLoco(loco)
		# 		self.RRRequest({"atcstatus": {"action": "complete", "train": train}})
		# 	else:
		# 		self.atcList.RefreshTrain(dccl)

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

					if rname in self.controlledTrains:
						print("Updating train %s:%s" % (rname, str(self.controlledTrains[rname])), file=sys.stderr)
						print("with %s" % str(p), file=sys.stderr)
						print("           Result:%s" % str(self.controlledTrains[rname]), file=sys.stderr)
						self.controlledTrains[rname].update(p)
						if len(p["blocks"]) == 0:
							# remove the train from the controlled list
							self.atcList.DelTrainByName(rname)
							del self.controlledTrains[rname]

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





					# iname = p["iname"]
					# rname = p["rname"]
					# logging.debug("p = %s" % str(p))
					# name = iname if rname is None or rname.strip() == "" else rname
					# if name in self.controlledTrains:
					# 	self.updateTrain(name, p)
					# elif name not in self.availableTrains:
					# 	self.availableTrains.append(name)
					# 	self.lbAvailable.SetItems(self.availableTrains)
					# roster = self.roster.GetTrainById(rname)
					# if rname is None or roster is None:
					# 	logging.debug("skipping train %s because it is unknown" % iname)
					# 	continue
					#
					# if rname in self.controlledTrains:
					# 	self.controlledTrains[rname].update(p)
					# 	if len(p["blocks"]) == 0:
					# 		# remove the train from the controlled list
					# 		self.controlledList.RemoveTrain(rname)
					# 		del self.controlledTrains[rname]
					# 	else:
					# 		# see if we need to change anything for this train
					# 		self.AnalyzeTrain(rname)
					#
					# elif len(p["blocks"]) > 0:
					# 	if rname not in self.availableTrains:
					# 		self.availableTrains[rname] = p
					# 		choices = sorted(self.availableTrains.keys())
					# 		self.lbAvailable.SetItems(choices)
					# 		self.lbAvailable.SetSelection(0)
					# 		self.bAdd.Enable(True)
					# 	else:
					# 		self.availableTrains[rname].update(p)
					# else:
					# 	if rname in self.availableTrains:
					# 		del self.availableTrains[rname]
					# 		choices = sorted(self.availableTrains.keys())
					# 		self.lbAvailable.SetItems(choices)
					# 		if len(choices) > 0:
					# 			self.lbAvailable.SetSelection(0)
					# 			self.bAdd.Enable(True)
					# 		else:
					# 			self.lbAvailable.SetSelection(wx.NOT_FOUND)
					# 			self.bAdd.Enable(False)

			elif cmd == "sessionID":
				self.sessionid = int(parms)
				logging.info("session ID %d" % self.sessionid)

				# associate our session id with the ATC function
				self.RRRequest({"identify": {"SID": self.sessionid, "function": "ATC"}})
				# kick off the refresh action
				self.RRRequest({"refresh": {"SID": self.sessionid}})

			elif cmd == "end":
				print("starting timer", file=sys.stderr)
				self.ticker.Start(2000)  # 500)
				pass

			elif cmd in ["disconnect", "exit"]:
				self.running = False
				
			elif cmd == "atc":
				action = parms["action"][0]
				
				if action == "hide":
					self.Hide()

				elif action == "show":
					self.Show()

			else:
				logging.info("unknown command ignored: %s: %s" % (cmd, parms))

	def OnBAdd(self, _):
		il = self.lbAvailable.GetSelections()
		for i in il:
			trid = self.lbAvailable.GetString(i)
			loco = self.availableTrains[trid]["loco"]
			self.controlledTrains[trid] = self.availableTrains[trid]
			self.controlledTrains[trid]["forcedstop"] = False
			self.controlledTrains[trid]["speed"] = 0
			self.controlledTrains[trid]["target"] = 0
			self.controlledTrains[trid]["headlight"] = False
			self.controlledTrains[trid]["horn"] = False
			self.controlledTrains[trid]["bell"] = False
			self.controlledTrains[trid]["prof"] = self.locos[loco].get("prof", defaultProfile)

			roster = self.roster.GetTrainById(trid)
			print("%s" % str(roster))
			print("start block = %s" % roster.GetStartBlock())
			steps = roster.GetSteps()
			for s in steps:
				print("Step: %s" % str(s))

			blockSeq = [roster.GetStartBlock()] + [s["block"] for s in roster.GetSteps()]
			signalSeq = [s["signal"] for s in roster.GetSteps()]
			osSeq = [s["os"] for s in roster.GetSteps()]
			rteSeq = [s["route"] for s in roster.GetSteps()]

			print("Arrays:")
			for j in range(len(rteSeq)):
				print("%d:  %s  %s  %s  %s" % (j, blockSeq[j], signalSeq[j], osSeq[j], rteSeq[j]))
			print("after loop", flush=True)

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

			self.atcList.AddTrain(self.controlledTrains[trid])
			print("train %s: %s" % (trid, self.controlledTrains[trid]))
			print("loco %s: %s" % (loco, str(self.locos[loco])), file=sys.stderr)
			del self.availableTrains[trid]

		choices = sorted(self.availableTrains.keys())
		self.lbAvailable.SetItems(choices)
		if len(choices) == 0:
			self.lbAvailable.SetSelection(wx.NOT_FOUND)
			self.bAdd.Enable(False)
		else:
			self.lbAvailable.SetSelection(0)
			self.bAdd.Enable(True)

	def OnBDel(self, _):
		pass

	def OnAvailableChoice(self, _):
		pass

	def RRRequest(self, req):
		logging.info("Outgoing request: %s" % json.dumps(req))
		self.rrServer.SendRequest(req)

	def raiseDisconnectEvent(self): # thread context
		evt = DisconnectEvent()
		wx.PostEvent(self, evt)

	def OnDisconnectEvent(self, _):
		try:
			self.StopAllLocos()
		except:
			pass
		
		self.kill()
		
	def ReportSelection(self, trnm):
		flag = trnm is not None
		self.selectedTrain = trnm
		self.EnableButtons(flag)			

	def EnableButtons(self, flag):
		self.bLight.Enable(flag)
		self.bHorn.Enable(flag)
		self.bBell.Enable(flag)
		self.bStop.Enable(flag)
		self.bAtcOff.Enable(flag)
		
	def OnBLight(self, _):
		pass
		# dccl = self.selectedDCCL
		# if dccl is None:
		# 	return
		#
		# light = dccl.GetHeadlight()
		#
		# self.dccRemote.SelectLoco(dccl.GetLoco())
		# self.dccRemote.SetFunction(headlight=not light)
		# self.atcList.RefreshTrain(dccl)
		
	def OnBHorn(self, _):
		pass
		# dccl = self.selectedDCCL
		# if dccl is None:
		# 	return
		#
		# horn = dccl.GetHorn()
		#
		# self.dccRemote.SelectLoco(dccl.GetLoco())
		# self.dccRemote.SetFunction(horn=not horn)
		# self.atcList.RefreshTrain(dccl)
		
	def OnBBell(self, _):
		pass
		# dccl = self.selectedDCCL
		# if dccl is None:
		# 	return
		#
		# bell = dccl.GetBell()
		#
		# self.dccRemote.SelectLoco(dccl.GetLoco())
		# self.dccRemote.SetFunction(bell=not bell)
		# self.atcList.RefreshTrain(dccl)
		
	def OnBStop(self, _):
		pass
		# dccl = self.selectedDCCL
		# if dccl is None:
		# 	return
		#
		# self.dccRemote.SelectLoco(dccl.GetLoco())
		# dccl.SetForcedStop(not dccl.GetForcedStop())
		# self.atcList.RefreshTrain(dccl)
		
	def OnBAtcOff(self, _):
		pass
		# dccl = self.selectedDCCL
		# if dccl is None:
		# 	return
		#
		# train = dccl.GetTrain()
		#
		# dlg = wx.MessageDialog(None, "Are you sure you want to remove Train %s from ATC?" % train,
		# 					'Remove Train from ATC?',
		# 					wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)
		# dlg.Centre()
		# rc = dlg.ShowModal()
		# dlg.Destroy()
		#
		# if rc == wx.ID_NO:
		# 	return
		#
		# self.atcList.DelTrain(dccl)
		# loco = dccl.GetLoco()
		# self.dccRemote.DropLoco(loco)
		# if self.dccRemote.LocoCount() == 0:
		# 	self.EnableButtons(False)
		#
		# self.RRRequest({"atcstatus": {"action": "remove", "train": train}})
		
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
		self.kill()
		return
		
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