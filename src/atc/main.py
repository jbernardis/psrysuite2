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

from dispatcher.constants import RegAspects
from dispatcher.settings import Settings
from dispatcher.train import CopyTrainReferences

from atc.turnout import Turnout
from atc.signal import Signal
from atc.block import Block
from atc.overswitch import OverSwitch
from atc.train import Train
from atc.route import Route
from atc.generatescripts import GenerateScripts

from atc.dccremote import DCCRemote
from atc.atclist import ATCListCtrl
from atc.listener import Listener
from atc.rrserver import RRServer
from atc.dccserver import DCCServer
from atc.ticker import Ticker


(DeliveryEvent, EVT_DELIVERY) = wx.lib.newevent.NewEvent() 
(DisconnectEvent, EVT_DISCONNECT) = wx.lib.newevent.NewEvent() 
(TickerEvent, EVT_TICKER) = wx.lib.newevent.NewEvent() 

class MainFrame(wx.Frame):
	def __init__(self):
		wx.Frame.__init__(self, None, size=(900, 800), style=wx.STAY_ON_TOP | wx.CAPTION | wx.RESIZE_BORDER)
		self.Bind(wx.EVT_CLOSE, self.OnClose)
		self.Bind(wx.EVT_SIZE, self.OnResize)
		self.Bind(wx.EVT_IDLE,self.OnIdle)
		self.resized = False
		
		self.sessionid = None
		self.settings = Settings()
		self.initialized = False
		
		self.posx = 0
		self.posy = 0
		self.resetx = 0
		self.resety = 0

		self.blocks = {}
		self.turnouts = {}
		self.signals = {}
		self.routes = {}
		self.osList = {}
		self.trains = {}
		self.listener = None
		self.rrServer = None
		
		self.selectedTrain = None
		
		self.LoadImages(os.path.join(cmdFolder, "images"))
		
		logging.info("psry atc server starting")

		self.SetTitle("PSRY ATC Server")
		
		self.atcList = ATCListCtrl(self, os.getcwd())

		hsz = wx.BoxSizer(wx.HORIZONTAL)
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
		
	def SetPos(self):
		self.SetPosition((self.posx, self.posy))

	def GetPos(self):
		self.posx, self.posy = self.GetPosition()

	def Initialize(self):
		logging.info("enter initialize")
		self.Bind(EVT_DELIVERY, self.OnDeliveryEvent)
		self.Bind(EVT_DISCONNECT, self.OnDisconnectEvent)
		self.Bind(EVT_TICKER, self.OnTickerEvent)

		self.dccServer = DCCServer()
		self.dccServer.SetServerAddress(self.settings.ipaddr, self.settings.dccserverport)
		self.dccRemote = DCCRemote(self.dccServer)
				
		self.rrServer = RRServer()
		self.rrServer.SetServerAddress(self.settings.ipaddr, self.settings.serverport)
		
		self.listener = Listener(self, self.settings.ipaddr, self.settings.socketport)
		if not self.listener.connect():
			logging.error("Unable to establish connection with railroad server")
			self.listener = None
			return
		self.listener.start()
		
		logging.info("socket connection created")
		
		# load the scripts and layout information	
		if not self.ProcessScripts():
			return
		
		
		self.ticker = Ticker(0.4, self.raiseTickerEvent)

		self.initialized = True
		self.SetPos()
		
		self.ReportSelection(None)
		
		self.blocks["KOSN10S11"] = Block(self, "KOSN10S11", 0, 'W', True)
		self.blocks["KOSN20S21"] = Block(self, "KOSN20S21", 0, 'E', True)

		logging.info("exit initialize")
		
	def BuildLocoKey(self, lid):
		return int(lid)

	def ProcessScripts(self):
		layout = self.rrServer.Get("getlayout", {})
		if layout is None:
			logging.error("Unable to retrieve layout information")
			return False

		subblocks = layout["subblocks"]

		submap = {}
		for blk, sublist in subblocks.items():
			for sub in sublist:
				submap[sub] = blk
				
		trains = self.rrServer.Get("gettrains", {})
		if trains is None:
			logging.error("Unable to retrieve trains information")
			return False

		CopyTrainReferences(trains)
		
		logging.info("Trains: %s" % json.dumps(trains))

		scripts = GenerateScripts(layout, trains)
		
		self.scripts = {}
		
		for train, script in scripts.items():
			lastblk = None
			sigList = []
			for step in script:
				cmd = list(step.keys())[0]
				blk = step[cmd]["block"]
				if blk in submap:
					blk = submap[blk]
				if cmd == "waitfor":
					sig = step[cmd]["signal"]
					osb = step[cmd]["os"]
					rte = step[cmd]["route"]
					sigList.append([sig, osb, rte])
				elif cmd == "placetrain":
					origin = blk
					lastblk = blk
				elif cmd == "movetrain":
					lastblk = blk
					
			terminus = lastblk
			sigList.append([None, None, None])					
			sigx = 0

			steps = {}	
			steps["origin"] = origin
			steps["terminus"] = terminus
			for step in script:
				cmd = list(step.keys())[0]
				if cmd in ["placetrain", "movetrain"]:
					blk = step[cmd]["block"]
					if blk in submap:
						blk = submap[blk]
						
					if blk in steps and origin == terminus and blk == terminus:
						pass
					else:
						steps[blk] = {
					   "signal": str(sigList[sigx][0]),
					   "os": str(sigList[sigx][1]),
					   "route": str(sigList[sigx][2])
					}
					lastblk = blk

				elif cmd == "waitfor":
					sigx += 1
				
			self.scripts[train] = steps

		return True
	
	def HaveScript(self, train):
		return train in self.scripts
	
	def SetOriginTerminus(self, dccl):
		trnm = dccl.GetTrain()
		origin = self.scripts[trnm]["origin"]
		terminus = self.scripts[trnm]["terminus"]
		dccl.SetOriginTerminus(origin, terminus)		
	
	def GetSignal(self, train, block):
		if not self.HaveScript(train):
			return None
		
		if block not in self.scripts[train]:
			return None
		
		return self.scripts[train][block]

	def tickerEvent(self):  # thread context
		if self.dccRemote.LocoCount() > 0:
			self.commandQ.put("{\"ticker\": []}")
			
	def raiseTickerEvent(self):
		evt = TickerEvent()
		wx.QueueEvent(self, evt)
		
	def OnTickerEvent(self, _):
		for dccl in self.dccRemote.GetDCCLocos():
			logging.info("in ticker loop for loco %s" % dccl.GetLoco())
			gs, _ = dccl.GetGoverningSignal()
			aspect = 0  # assume STOP
			aspectType = RegAspects

			if dccl.HasCompleted():
				logging.info("Train %s has completed" % dccl.GetTrain())
				aspect = 0 # we've reached the terminus - we should stop
				
			elif gs is None:
				logging.info("governing signal is None")
				# we are moving into terminus block - move slowly
				aspect = 4 # restricting

			elif "signal" in gs:
				signame = gs["signal"]
				logging.info("Governing signal is %s" % signame)
				if signame in self.signals:
					aspect, aspectType = self.signals[signame].GetAspect()
					logging.info("Retrieved aspect = %s" % str(aspect))
					
				if "os" in gs and "route" in gs and aspect != 0:
					overswitch = gs["os"]
					route = gs["route"]
					logging.info("Wanted os/route is %s/%s, active route is %s" % (overswitch, route, self.osList[overswitch].GetActiveRouteName()))
					if overswitch in self.osList and self.osList[overswitch].GetActiveRouteName() != route:
						# either we don't know that OS or its not set to the needed route
						logging.info("setting aspect to 0")
						aspect = 0
						aspectType = RegAspects
						
			else:
				logging.error("Unable to interpret governing signal %s" % str(gs))
	
			logging.info("Using aspect %d/%d" % (aspect, aspectType))
			dccl.SetGoverningAspect(aspect, aspectType)
			dccl.SetPendingStop(dccl.GetGoverningAspect() == 0)	
			
			self.dccRemote.SelectLoco(dccl.GetLoco())
			
			speed = self.dccRemote.ApplySpeedStep() #step)
			if speed == 0 and dccl.HasCompleted():
				self.atcList.DelTrain(dccl)
				loco = dccl.GetLoco()
				train = dccl.GetTrain()
				self.dccRemote.DropLoco(loco)
				self.RRRequest({"atcstatus": {"action": "complete", "train": train}})
			else:
				self.atcList.RefreshTrain(dccl)

	def raiseDeliveryEvent(self, data): # thread context
		try:
			jdata = json.loads(data)
		except json.decoder.JSONDecodeError:
			return
		evt = DeliveryEvent(data=jdata)
		wx.QueueEvent(self, evt)
			
	def OnDeliveryEvent(self, evt):  # thread context
		for cmd, parms in evt.data.items():
			if cmd == "turnout":
				for p in parms:
					turnout = p["name"]
					state = p["state"]
					if turnout not in self.turnouts:
						self.turnouts[turnout] = Turnout(self, turnout, state)
					else:
						self.turnouts[turnout].SetState(state)

			elif cmd == "turnoutlock":
				for p in parms:
					toName = p["name"]
					lock = int(p["state"])
					locker = int(p["locker"])
					if toName in self.turnouts:
						self.turnouts[toName].Lock(lock != 0, locker)

			elif cmd == "block":
				for p in parms:
					block = p["name"]
					state = p["state"]
					if block not in self.blocks:
						self.blocks[block] = Block(self, block, state, 'E', False)
					else:
						b = self.blocks[block]
						b.SetState(state)

			elif cmd == "blockdir":
				for p in parms:
					block = p["block"]
					direction = p["dir"]
					if block not in self.blocks:
						self.blocks[block] = Block(self, block, 0, direction, False)
					else:
						b = self.blocks[block]
						b.SetDirection(direction)

			elif cmd == "blockclear":
				for p in parms:
					block = p["block"]
					clear = p["clear"]
					if block not in self.blocks:
						self.blocks[block] = Block(self, block, 0, 'E', clear != 0)
					else:
						b = self.blocks[block]
						b.SetClear(clear)

			elif cmd == "signal":
				print("ATC Signal command: %s" % str(parms), flush=True)
				for p in parms:
					sigName = p["name"]
					try:
						aspect = int(p["aspect"])
					except:
						aspect = 0  # stop if uncertain
						
					try:
						aspectType = int(p["aspecttype"])
					except:
						aspectType = RegAspects
						
					if sigName not in self.signals:
						self.signals[sigName] = Signal(self, sigName, aspect, aspectType)
					else:
						self.signals[sigName].SetAspect(aspect, aspectType)

			elif cmd == "signallock":
				for p in parms:
					sigName = p["name"]
					lock = int(p["state"])
					if sigName in self.signals:
						self.signals[sigName].Lock(lock != 0)

			elif cmd == "routedef":
				name = parms["name"]
				os = parms["os"]
				ends = [None if e == "-" else e for e in parms["ends"]]
				signals = parms["signals"]
				turnouts = parms["turnouts"]
				if os not in self.osList:
					self.osList[os] = OverSwitch(os)

				rte = Route(self, name, os, ends, signals, turnouts)
				self.routes[name] = rte
				self.osList[os].AddRoute(rte)

			elif cmd == "setroute":
				for p in parms:
					blknm = p["block"]
					rtnm = p["route"]
					if blknm not in self.osList:
						self.osList[blknm] = OverSwitch(blknm)

					self.osList[blknm].SetActiveRoute(rtnm)

			elif cmd == "settrain":
				blocks = parms["blocks"]
				name = parms["name"]
				loco = parms["loco"]
				try:
					east = parms["east"]
				except KeyError:
					east = True

				if name is None:
					for b in blocks:
						self.blocks[b].SetTrain(None, None)
				else:
					if name not in self.trains:
						self.trains[name] = Train(self, name, loco)

					self.trains[name].SetEast(east)
					for b in blocks:
						self.trains[name].AddBlock(b)
						self.blocks[b].SetDirection(east)
						self.blocks[b].SetTrain(name, loco)
						
			elif cmd == "trainsignal":
				print("ATC TrainSignal command: %s" % str(parms), flush=True)
				train = parms["train"][0]
				dccl = self.dccRemote.GetDCCLocoByTrain(train)
				if dccl is None:
					# ignore non-ATC trains
					return

				sig = parms["signal"][0]
				asp = parms["aspect"][0]
				blk = parms["block"][0]
				
				gs, _ = dccl.GetGoverningSignal()
				logging.info("trainsignal: train %s, sig/aspect/block = %s/%s/%s  gs = (%s)" % (train, sig, asp, block, str(gs)))

			elif cmd == "sessionID":
				self.sessionid = int(parms)
				logging.info("session ID %d" % self.sessionid)
				# retrieve the loco information from the server
				locos = self.rrServer.Get("getlocos", {})
				if locos is None:
					logging.error("Unable to retrieve locos")
					locos = {}
				if not self.dccRemote.Initialize(locos):
					logging.error("Unable to initialize DCC remote")
					return
				# associate our session id with the ATC function
				self.RRRequest({"identify": {"SID": self.sessionid, "function": "ATC"}})
				# kick off the refresh action
				self.RRRequest({"refresh": {"SID": self.sessionid}})

			elif cmd == "end":
				if parms["type"] == "layout":
					self.requestRoutes()
				elif parms["type"] == "routes":
					self.requestTrains()
					
			elif cmd in ["disconnect", "exit"]:
				self.running = False
				
			elif cmd == "atc":
				action = parms["action"][0]
				
				if action == "add":
					trnm = parms["train"][0]
					if not self.HaveScript(trnm):
						# we do not have a script for this train - reject the request
						self.RRRequest({"atcstatus": {"action": "reject", "train": trnm}})
						return
					
					tr = self.atcList.FindTrain(trnm)
					if tr is not None:
						return #ignore if we already have the train
					
					loco = parms["loco"][0]
					dccl = self.dccRemote.SelectLoco(loco)
					dccl.SetTrain(trnm)
					self.SetOriginTerminus(dccl)
					self.atcList.AddTrain(dccl)
					
					tr = self.trains[trnm]
					blk = tr.GetFirstBlock()
					dccl.SetGoverningSignal(self.GetSignal(trnm, blk))
						
				elif action == "remove":
					train = parms["train"][0]
					loco = parms["loco"][0]
					dccl = self.dccRemote.GetDCCLocoByTrain(train)
					if dccl is not None:
						self.atcList.DelTrain(dccl)
						self.dccRemote.DropLoco(loco)
						
				elif action == "forcestop":
					train = parms["train"][0]
					loco = parms["loco"][0]
					dccl = self.dccRemote.GetDCCLocoByTrain(train)
					if dccl is None:
						return
					
					self.dccRemote.SelectLoco(loco)
					dccl.SetForcedStop(not dccl.GetForcedStop())
					self.atcList.RefreshTrain(dccl)
					
				elif action == "hide":
					self.GetPos()
					self.Hide()
				
				elif action == "reset":
					self.posx = self.resetx
					self.posy = self.resety
					self.SetPos()
					self.Show()
				
				elif action == "show":
					if "x" in parms or "y" in parms:
						if "x" in parms:
							self.posx = int(parms["x"][0])
							self.resetx = self.posx
						if "y" in parms:
							self.posy = int(parms["y"][0])
							self.resety = self.posy
						self.SetPos()

					self.Show()

			else:
				if cmd not in ["control", "relay", "handswitch", "siglever", "breaker", "fleet"]:
					logging.info("unknown command ignored: %s: %s" % (cmd, parms))


	def requestRoutes(self):
		if self.sessionid is not None:
			self.RRRequest({"refresh": {"SID": self.sessionid, "type": "routes"}})

	def requestTrains(self):
		if self.sessionid is not None:
			self.RRRequest({"refresh": {"SID": self.sessionid, "type": "trains"}})

	def SignalLockChange(self, sigName, nLock):
		logging.info("signal %s lock has changed %s" % (sigName, str(nLock)))

	def SignalAspectChange(self, sigName, nAspect, nAspectType):
		logging.info("signal %s aspect has changed %d/%d" % (sigName, nAspect, nAspectType))

	def TurnoutLockChange(self, toName, nLock):
		logging.info("turnout %s lock has changed %s" % (toName, str(nLock)))

	def TurnoutStateChange(self, toName, nState):
		logging.info("turnout %s state has changed %s" % (toName, nState))

	def BlockDirectionChange(self, blkName, nDirection):
		logging.info("block %s has changed direction: %s" % (blkName, nDirection))

	def BlockStateChange(self, blkName, nState):
		logging.info("block %s has changed state: %d" % (blkName, nState))

	def BlockClearChange(self, blkName, nClear):
		logging.info("block %s has changed clear: %s" % (blkName, str(nClear)))

	def BlockTrainChange(self, blkName, oldTrain, oldLoco, newTrain, newLoco):
		if oldTrain is not None and oldTrain != newTrain:
			try:
				if self.trains[oldTrain].DelBlock(blkName) == 0:
					del(self.trains[oldTrain])
			except KeyError:
				pass

	def TrainAddBlock(self, train, block):
		dccl = self.dccRemote.GetDCCLocoByTrain(train)
		if dccl is None:
			# ignore non-ATC trains
			return
		
		logging.info("Train %s has moved into block %s" % (train, block))
		gs, _ = dccl.GetGoverningSignal()
		logging.info("gs = (%s)" % str(gs))
		if gs is not None and gs["os"] == block:
			#keep with current signal in this instance
			logging.info("Maintaining current signal = (%s)" % str(gs))
			pass
		else:
			gs = self.GetSignal(train, block)
			logging.info("Changing to new governing signal = (%s)" % str(gs))
			dccl.SetGoverningSignal(gs)
		
		dccl.CheckHasMoved(block)
		
		if dccl.AtTerminus(block):
			dccl.HeadAtTerminus(True)
			dccl.SetGoverningSignal(None)
		else:
			sig = self.GetSignal(train, block)
			# see if we've passed our signal.  If so, we need to freeze our aspect
			# until the tail of the train also passes the signal
			dccl.SetInBlock(gs != sig)
			
	def TrainTailInBlock(self, train, block):
		dccl = self.dccRemote.GetDCCLocoByTrain(train)
		if dccl is None:
			# ignore non-ATC trains
			return
		
		logging.info("Train %s tail in block %s" % (train, block))
		
		if dccl.AtTerminus(block):
			dccl.MarkCompleted()

	def TrainRemoveBlock(self, train, block, blocks):
		logging.info("Train %s has left block %s and is now in %s" % (train, block, ",".join(blocks)))

	def RRRequest(self, req):
		logging.info("Outgoing request: %s" % json.dumps(req))
		self.rrServer.SendRequest(req)

	def raiseDisconnectEvent(self): # thread context
		evt = DisconnectEvent()
		wx.PostEvent(self, evt)

	def OnDisconnectEvent(self, _):
		try:
			self.dccRemote.StopAll()
		except:
			pass
		
		self.kill()
		
	def ReportSelection(self, trnm):
		flag = trnm is not None
		self.selectedTrain = trnm
		self.EnableButtons(flag)			
		if trnm is None:
			self.selectedDCCL = None
		else:
			self.selectedDCCL = self.dccRemote.GetDCCLocoByTrain(trnm)
			
	def EnableButtons(self, flag):
		self.bLight.Enable(flag)
		self.bHorn.Enable(flag)
		self.bBell.Enable(flag)
		self.bStop.Enable(flag)
		self.bAtcOff.Enable(flag)
		
	def OnBLight(self, _):
		dccl = self.selectedDCCL
		if dccl is None:
			return
		
		light = dccl.GetHeadlight()
		
		self.dccRemote.SelectLoco(dccl.GetLoco())
		self.dccRemote.SetFunction(headlight=not light)
		self.atcList.RefreshTrain(dccl)
		
	def OnBHorn(self, _):
		dccl = self.selectedDCCL
		if dccl is None:
			return
		
		horn = dccl.GetHorn()
		
		self.dccRemote.SelectLoco(dccl.GetLoco())
		self.dccRemote.SetFunction(horn=not horn)
		self.atcList.RefreshTrain(dccl)
		
	def OnBBell(self, _):
		dccl = self.selectedDCCL
		if dccl is None:
			return
		
		bell = dccl.GetBell()
		
		self.dccRemote.SelectLoco(dccl.GetLoco())
		self.dccRemote.SetFunction(bell=not bell)
		self.atcList.RefreshTrain(dccl)
		
	def OnBStop(self, _):
		dccl = self.selectedDCCL
		if dccl is None:
			return
		
		self.dccRemote.SelectLoco(dccl.GetLoco())
		dccl.SetForcedStop(not dccl.GetForcedStop())
		self.atcList.RefreshTrain(dccl)
		
	def OnBAtcOff(self, _):
		dccl = self.selectedDCCL
		if dccl is None:
			return
		
		train = dccl.GetTrain()
				
		dlg = wx.MessageDialog(None, "Are you sure you want to remove Train %s from ATC?" % train,
							   'Remove Train from ATC?',
							   wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)
		dlg.Centre()
		rc = dlg.ShowModal()
		dlg.Destroy()
		
		if rc == wx.ID_NO:
			return
		
		self.atcList.DelTrain(dccl)
		loco = dccl.GetLoco()
		self.dccRemote.DropLoco(loco)
		if self.dccRemote.LocoCount() == 0:
			self.EnableButtons(False)
			
		self.RRRequest({"atcstatus": {"action": "remove", "train": train}})
		
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
		#self.kill()
		return
		
	def kill(self):
		try:
			self.listener.kill()
			self.listener.join()
		except:
			pass
		
		try:
			self.ticker.stop()
		except:
			pass
		
		self.Destroy()

class App(wx.App):
	def __init__(self, redirect=False, filename=None, useBestVisual=False, clearSigInt=True):
		super().__init__(redirect, filename, useBestVisual, clearSigInt)
		self.frame = None

	def OnInit(self):
		self.frame = MainFrame()
		self.frame.Hide()
		return True


app = App(False)
app.MainLoop()

logging.info("exiting program")