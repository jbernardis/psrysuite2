import wx
import wx.lib.newevent

import json
import logging

from c13auto.listener import Listener
from c13auto.rrserver import RRServer

entryBlocks = {
	"B11": {"signal": "C18LA", "east": True, "nearos": "BOSE", "nearrte": "BRtB11C13", "farsignal": "C14L", "faros": "COSCLW", "farrte": "CRtC13C12"},
	"B21": {"signal": "C18LB", "east": True, "nearos": "BOSE", "nearrte": "BRtB21C13", "farsignal": "C14L", "faros": "COSCLW", "farrte": "CRtC13C12"},
	"C23": {"signal": "C14RB", "east": False, "nearos": "COSCLW", "nearrte": "CRtC13C23", "farsignal": "C18R", "faros": "BOSE", "farrte": "BRtB11C13"},
	"C12": {"signal": "C14RA", "east": False, "nearos": "COSCLW", "nearrte": "CRtC13C12", "farsignal": "C18R", "faros": "BOSE", "farrte": "BRtB11C13"},
}

osRoutes = {
	"BOSE": {
		"BRtB11C13": ["CSw17", "R"],
		"BRtB21C13": ["CSw17", "N"],
	},
	"COSCLW": {
		"CRtC13C12": ["CSw13", "R"],
		"CRtC13C23": ["CSw13", "N"],
	}
}

(DeliveryEvent, EVT_DELIVERY) = wx.lib.newevent.NewEvent()
(DisconnectEvent, EVT_DISCONNECT) = wx.lib.newevent.NewEvent()


class MainFrame(wx.Frame):
	def __init__(self, settings):
		wx.Frame.__init__(self, None, style=wx.STAY_ON_TOP | wx.CAPTION | wx.RESIZE_BORDER | wx.CLOSE_BOX)
		self.title = "PSRY Block C13 Auto Router"
		self.Bind(wx.EVT_CLOSE, self.OnClose)
		self.settings = settings
		self.clientForever = True
		self.activeRouteRequest = None
		self.activeTrain = None
		self.routeRequestQueue = []

		self.TrainList = Trains()
		self.blockStatus = {}
		self.routes = {}
		self.turnouts = {}
		self.signals = {}
		self.SpikesPeakLocked = True
		self.CliffControl = 0
		self.C13Control = None

		self.sessionid = None
		self.timerInterval = 500
		self.timer = None
		self.subscribed = False

		self.listener = None
		self.rrServer = None

		btnsz = wx.BoxSizer(wx.HORIZONTAL)

		btnsz.AddSpacer(10)

		wx.CallAfter(self.Initialize)

		self.bSubscribe = wx.Button(self, wx.ID_ANY, "Connect")
		self.Bind(wx.EVT_BUTTON, self.OnSubscribe, self.bSubscribe)
		btnsz.Add(self.bSubscribe)

		btnsz.AddSpacer(60)

		self.stStatus = wx.StaticText(self, wx.ID_ANY, "", size=(400, -1))
		textFont = wx.Font(wx.Font(12, wx.FONTFAMILY_ROMAN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, faceName="Arial"))
		self.stStatus.SetFont(textFont)
		btnsz.Add(self.stStatus)
		btnsz.AddSpacer(10)

		occsz = wx.BoxSizer(wx.HORIZONTAL)
		occsz.AddSpacer(60)

		self.stOccupant = wx.StaticText(self, wx.ID_ANY, "Occupant:", size=(100, -1), style=wx.ALIGN_RIGHT)
		self.stOccupant.SetFont(textFont)
		occsz.Add(self.stOccupant)
		occsz.AddSpacer(10)
		self.tcOccupant = wx.TextCtrl(self, wx.ID_ANY, "", style=wx.TE_READONLY)
		self.tcOccupant.SetFont(textFont)
		occsz.Add(self.tcOccupant)

		reasonsz = wx.BoxSizer(wx.HORIZONTAL)
		reasonsz.AddSpacer(60)
		self.stReason = wx.StaticText(self, wx.ID_ANY, "", size=(400, -1))
		self.stReason.SetFont(textFont)
		reasonsz.Add(self.stReason)

		queuesz = wx.BoxSizer(wx.HORIZONTAL)
		queuesz.AddSpacer(60)

		self.stQueue0 = wx.StaticText(self, wx.ID_ANY, "Queue:", size=(100, -1), style=wx.ALIGN_RIGHT)
		self.stQueue0.SetFont(textFont)
		queuesz.Add(self.stQueue0)
		queuesz.AddSpacer(10)
		self.tcQueue0 = wx.TextCtrl(self, wx.ID_ANY, "", style=wx.TE_READONLY)
		self.tcQueue0.SetFont(textFont)
		queuesz.Add(self.tcQueue0)

		queue1sz = wx.BoxSizer(wx.HORIZONTAL)
		queue1sz.AddSpacer(60)

		self.stQueue1 = wx.StaticText(self, wx.ID_ANY, "", size=(100, -1), style=wx.ALIGN_RIGHT)
		self.stQueue1.SetFont(textFont)
		queue1sz.Add(self.stQueue1)
		queue1sz.AddSpacer(10)
		self.tcQueue1 = wx.TextCtrl(self, wx.ID_ANY, "", style=wx.TE_READONLY)
		self.tcQueue1.SetFont(textFont)
		queue1sz.Add(self.tcQueue1)

		queue2sz = wx.BoxSizer(wx.HORIZONTAL)
		queue2sz.AddSpacer(60)

		self.stQueue2 = wx.StaticText(self, wx.ID_ANY, "", size=(100, -1), style=wx.ALIGN_RIGHT)
		self.stQueue2.SetFont(textFont)
		queue2sz.Add(self.stQueue2)
		queue2sz.AddSpacer(10)
		self.tcQueue2 = wx.TextCtrl(self, wx.ID_ANY, "", style=wx.TE_READONLY)
		self.tcQueue2.SetFont(textFont)
		queue2sz.Add(self.tcQueue2)

		self.TcQueue = [self.tcQueue0, self.tcQueue1, self.tcQueue2]

		vsz = wx.BoxSizer(wx.VERTICAL)
		vsz.AddSpacer(20)
		vsz.Add(btnsz)
		vsz.AddSpacer(40)
		vsz.Add(occsz)
		vsz.AddSpacer(10)
		vsz.Add(reasonsz)
		vsz.AddSpacer(20)
		vsz.Add(queuesz)
		vsz.AddSpacer(10)
		vsz.Add(queue1sz)
		vsz.AddSpacer(10)
		vsz.Add(queue2sz)
		vsz.AddSpacer(20)

		self.SetSizer(vsz)
		self.Fit()
		self.Layout()

	def ShowTitle(self):
		titleString = self.title
		if self.subscribed and self.sessionid is not None:
			titleString += ("  -  Session ID %d" % self.sessionid)
		self.SetTitle(titleString)

	def UpdateStatus(self):
		if self.C13Control:
			text = "ENABLED"
			color = wx.Colour(0, 164, 24)
		else:
			text = "DISABLED - "
			color = wx.Colour(255, 0, 0)
			if not self.SpikesPeakLocked:
				text += "Spike's Peak unlocked"
				joiner = ", "
			else:
				joiner = ""
			if self.CliffControl == 0:
				text += joiner + "Cliff Control"

		self.stStatus.SetForegroundColour(color)
		self.stStatus.SetLabel(text)

	def UpdateOccupant(self, clear=False):
		if clear:
			self.tcOccupant.SetValue("")
			self.UpdateReason(clear=True)

		elif self.activeTrain is not None:
			self.tcOccupant.SetValue("%s" % self.activeTrain.Name())
			# self.UpdateReason()

	def UpdateReason(self, clear=False):
		if clear:
			self.stReason.SetLabel("")

		elif self.activeRouteRequest is not None:
			self.stReason.SetLabel("%s" % self.activeRouteRequest.WaitingOn())

		else:
			self.stReason.SetLabel("")

	def UpdateQueue(self):
		for i in range(len(self.TcQueue)):
			if i < len(self.routeRequestQueue):
				req = self.routeRequestQueue[i]
				iname = req.Train()
				tr = self.TrainList.GetTrain(iname)
				self.TcQueue[i].SetValue(tr.Name())
			else:
				self.TcQueue[i].SetValue("")

	def MoveToTop(self):
		st = self.GetWindowStyle()
		st |= wx.STAY_ON_TOP

		self.SetWindowStyle(st)
		self.Show()

	def RouteAvailable(self):
		for bn in ["BOSE", "C13.W", "C13", "C13.E", "COSCLW"]:
			bstat = self.blockStatus.get(bn, "U")  # if we haven't heard about this block yet, assume it's occupied
			if bstat != "E":
				return False

		return True

	def Initialize(self):
		self.timer = wx.Timer(self)
		self.Bind(wx.EVT_TIMER, self.Ticker)
		self.Bind(EVT_DELIVERY, self.onDeliveryEvent)
		self.Bind(EVT_DISCONNECT, self.onDisconnectEvent)

		self.rrServer = RRServer()
		self.rrServer.SetServerAddress(self.settings.ipaddr, self.settings.serverport)

		wx.CallLater(2000, self.ConnectServer)

	def OnSubscribe(self, _):
		if self.subscribed:
			self.DisconnectServer()
		else:
			self.ConnectServer()

	def ConnectServer(self):
		self.listener = Listener(self, self.settings.ipaddr, self.settings.socketport)
		if not self.listener.connect():
			logging.error("Unable to establish connection with server")
			self.listener = None
			return
		self.listener.start()

		self.subscribed = True
		self.bSubscribe.SetLabel("Disconnect")
		self.ShowTitle()

	def DisconnectServer(self):
		self.listener.kill()
		self.listener.join()
		self.listener = None
		self.subscribed = False
		self.sessionid = None
		self.bSubscribe.SetLabel("Connect")
		self.ClearDataStructures()
		self.ShowTitle()

	def ClearDataStructures(self):
		self.routeRequestQueue = []
		self.TrainList.Clear()
		self.blockStatus = {}
		self.routes = {}
		self.turnouts = {}
		self.signals = {}
		self.SpikesPeakLocked = True
		self.CliffControl = 0
		self.C13Control = None

	def Ticker(self, _):
		self.ProcessCommand({"interval": []})

	def onDeliveryEvent(self, evt):
		self.ProcessCommand(evt.data)

	def ProcessCommand(self, msg):
		logging.debug("process command: %s" % str(msg))
		for cmd, parms in msg.items():
			if cmd == "interval":
				if not self.C13Control:
					return

				if self.activeRouteRequest is not None:
					if self.activeRouteRequest.Execute():
						self.activeRouteRequest = None  # route set completed
					self.UpdateReason()

				elif self.RouteAvailable():
					if len(self.routeRequestQueue) > 0:
						self.activeRouteRequest = self.routeRequestQueue.pop(0)
						iname = self.activeRouteRequest.Train()
						self.activeTrain = self.TrainList.GetTrain(iname)
						self.Alert("Train %s setting up on block C13" % self.activeTrain.Name())
						self.UpdateQueue()
						self.UpdateOccupant()
						if self.activeRouteRequest.Execute():
							self.activeRouteRequest = None  # route set completed
						self.UpdateReason()
					else:
						if self.activeTrain is not None:
							self.UpdateOccupant(clear=True)
							self.activeTrain = None

			elif cmd == "block":
				for p in parms:
					name = p.get("name", None)
					state = p.get("state", None)
					if name is None or state is None:
						logging.debug("Ignoring block command eithout either name or state: %s" % str(p))
					else:
						self.blockStatus[name] = state

						if name in ["BOSE", "COSCLW"] and state == "E":
							logging.debug("Block: %s" % str(p))
							logging.debug("Trigger to check for queued trains")

			elif cmd == "turnout":
				for p in parms:
					name = p.get("name", None)
					state = p.get("state", None)
					if name is None or state is None:
						logging.debug("Ignoring turnout command without either name or state: %s" % str(p))
					else:
						self.turnouts[name] = state

			elif cmd == "showaspect":
				for p in parms:
					signal = p.get("signal", None)
					aspect = p.get("aspect", None)
					if signal is None or aspect is None:
						logging.debug("Ignoring showaspect command without either signal or aspect: %s" % str(p))
					else:
						self.signals[signal] = aspect

			elif cmd == "setroute":
				for p in parms:
					osn = p.get("os", None)
					rte = p.get("route", None)
					if osn is None or rte is None:
						logging.debug("Ignoring setroute command without either os or route: %s" % str(p))
					else:
						self.routes[osn] = rte

			elif cmd == "train":
				for p in parms:
					iname = p.get("iname", None)
					rname = p.get("rname", None)
					if iname is None:
						logging.debug("Ignoring Train command without iname")
						continue

					tr = self.TrainList.GetTrain(iname)
					if tr is None:
						tr = Train(p)
						self.TrainList.AddTrain(tr)
						newBlocks = [b for b in p.get("blocks", [])]
						delblocks = []
					else:
						tr = self.TrainList.GetTrain(iname)
						if tr is not None:
							oldRname = tr.RName()
						else:
							oldRname = None
						delblocks, newBlocks = self.TrainList.UpdateTrain(p)
						if rname != oldRname:
							if self.activeTrain is not None and iname == self.activeTrain.IName():
								self.UpdateOccupant()
							else:
								for req in self.routeRequestQueue:
									if iname == req.Train():
										self.UpdateQueue()
										break

					for b in newBlocks:
						if b in entryBlocks:
							eb = entryBlocks[b]
							if tr.Signal() == eb["signal"] and tr.East() == eb["east"]:
								rreq = RouteRequest(self, iname, eb["signal"], eb["nearos"], eb["nearrte"], eb["farsignal"], eb["faros"], eb["farrte"])
								if self.RouteAvailable() and self.activeRouteRequest is None:
									self.activeRouteRequest = rreq
									self.activeTrain = self.TrainList.GetTrain(iname)
									self.Alert("Train %s setting up on block C13" % self.activeTrain.Name())

									if self.C13Control:
										if rreq.Execute():
											self.activeRouteRequest = None  # route set completed
										self.UpdateReason()
									self.UpdateOccupant()

								else:
									self.routeRequestQueue.append(rreq)
									self.UpdateQueue()

			elif cmd == "control":
				for p in parms:
					name = p.get("name", None)
					value = p.get("value", None)
					if name is None or value is None:
						logging.debug("Ignoring control command without either name or value: %s" % str(p))
					elif name == "cliff":
						self.CliffControl = int(value)
						nv = self.SpikesPeakLocked and (self.CliffControl in [1, 2])
						if nv != self.C13Control:
							self.Alert("C13 Automation %s" % ("Enabled" if nv else "Disabled"))
							self.C13Control = nv
						self.UpdateStatus()

			elif cmd == "handswitch":
				for p in parms:
					name = p.get("name", None)
					state = p.get("state", None)
					if name is None or state is None:
						logging.debug("Ignoring handswitch command without name or state: %s" % str(p))
					elif name == "CSw15.hand":
						self.SpikesPeakLocked = int(state) == 0
						nv = self.SpikesPeakLocked and (self.CliffControl in [1, 2])
						if nv != self.C13Control:
							self.Alert("C13 Automation %s" % ("Enabled" if nv else "Disabled"))
							self.C13Control = nv
						self.UpdateStatus()

			elif cmd == "c13ar":
				action = parms["action"][0]
				logging.debug("C13AR Action: (%s)" % action)
				if action == "show":
					if self.IsShown():
						self.Hide()
					else:
						self.MoveToTop()

			elif cmd == "sessionID":
				self.sessionid = int(parms)
				self.Request({"identify": {"SID": self.sessionid, "function": "C13AR"}})
				self.Request({"refresh": {"SID": self.sessionid}})
				self.ShowTitle()

			elif cmd == "end":
				self.timer.Start(self.timerInterval)

	def Alert(self, msg, locale=None):
		msg = {"alert": {"msg": msg}}
		if locale is not None:
			msg["alert"]["locale"] = locale
		self.Request(msg)

	def Request(self, req):
		logging.debug("sending command: %s" % str(req))
		self.rrServer.SendRequest(req)

	def raiseDeliveryEvent(self, data):  # thread context
		try:
			jdata = json.loads(data)
		except json.decoder.JSONDecodeError:
			return

		evt = DeliveryEvent(data=jdata)
		wx.QueueEvent(self, evt)

	def raiseDisconnectEvent(self):  # thread context
		evt = DisconnectEvent()
		wx.PostEvent(self, evt)

	def onDisconnectEvent(self, _):
		self.listener = None
		self.subscribed = False
		self.sessionid = None
		self.bSubscribe.SetLabel("Connect")
		self.ClearDataStructures()
		self.ShowTitle()

	def OnClose(self, evt):
		if self.subscribed:
			self.Hide()
		else:
			self.Kill()

	def Kill(self):
		try:
			self.listener.kill()
			self.listener.join()
		except:
			pass
		self.Destroy()


class RouteRequest:
	def __init__(self, parent, trname, nearsignal, nearos, nearroute, farsignal, faros, farroute):
		self.parent = parent
		self.trname = trname
		self.nearsignal = nearsignal
		self.nearos = nearos
		self.nearroute = nearroute
		self.farsignal = farsignal
		self.faros = faros
		self.farroute = farroute

		self.nearRouteRequested = False
		self.nearRouteSet = False
		self.nearRouteIntervals = 0

		self.nearSignalRequested = False
		self.nearSignalSet = False
		self.nearSignalIntervals = 0

		self.farRouteRequested = False
		self.farRouteSet = False
		self.farRouteIntervals = 0

		self.farSignalRequested = False
		self.farSignalSet = False
		self.farSignalIntervals = 0

	def WaitingOn(self):
		reasons = []
		if not self.nearRouteSet:
			reasons.append("Blk %s" % self.nearos)
		if not self.nearSignalSet:
			reasons.append("Sig %s" % self.nearsignal)
		if not self.farRouteSet:
			reasons.append("Blk %s" % self.faros)
		if not self.farSignalSet:
			reasons.append("Sig %s" % self.farsignal)

		if len(reasons) == 0:
			return ""
		else:
			return "Waiting: %s" % ", ".join(reasons)

	def Train(self):
		return self.trname

	def Execute(self):
		if not self.nearRouteRequested:
			self.nearRouteRequested = True
			if self.nearroute != self.parent.routes.get(self.nearos, None):
				# we need to change the route - first clear the signal
				self.parent.Request({"signalclick": {"name": self.nearsignal, "wantedaspect": 0, "callon": 0, "silent": 1}})
				turnout = osRoutes[self.nearos][self.nearroute]
				self.parent.Request({"turnoutclick": {"name": turnout[0], "status": turnout[1]}})
				self.nearRouteIntervals = 8

		if self.nearroute == self.parent.routes.get(self.nearos, None):
			# we got the route we want now set the signal
			self.nearRouteSet = True
			self.parent.Request({"signalclick": {"name": self.nearsignal, "wantedaspect": 1, "callon": 0, "silent": 1}})
			self.nearSignalRequested = True
			self.nearSignalIntervals = 4
		else:
			self.nearRouteIntervals -= 1
			if self.nearRouteIntervals <= 0:
				self.nearRouteRequested = False

		if self.nearSignalRequested and not self.nearSignalSet:
			if self.parent.signals.get(self.nearsignal, 0) != 0:
				self.nearSignalSet = True
			else:
				self.nearSignalIntervals -= 1
				if self.nearSignalIntervals <= 0:
					self.nearSignalRequested = False

		if not self.farRouteRequested:
			self.farRouteRequested = True
			if self.farroute != self.parent.routes.get(self.faros, None):
				# we need to change the route - first clear the signal
				self.parent.Request({"signalclick": {"name": self.farsignal, "wantedaspect": 0, "callon": 0, "silent": 1}})
				turnout = osRoutes[self.faros][self.farroute]
				self.parent.Request({"turnoutclick": {"name": turnout[0], "status": turnout[1]}})
				self.farRouteIntervals = 8

		if self.farroute == self.parent.routes.get(self.faros, None):
			# we got the route we want now set the signal
			self.farRouteSet = True
			self.parent.Request({"signalclick": {"name": self.farsignal, "wantedaspect": 1, "callon": 0, "silent": 1}})
			self.farSignalRequested = True
			self.farSignalIntervals = 4
		else:
			self.farRouteIntervals -= 1
			if self.farRouteIntervals <= 0:
				self.farRouteRequested = False

		if self.farSignalRequested and not self.farSignalSet:
			if self.parent.signals.get(self.farsignal, 0) != 0:
				self.farSignalSet = True
			else:
				self.farSignalIntervals -= 1
				if self.farSignalIntervals <= 0:
					self.farSignalRequested = False

		return self.nearRouteSet and self.nearSignalSet and self.farRouteSet and self.farSignalSet


class Train:
	def __init__(self, tr):
		self.iname = tr["iname"]
		self.rname = tr["rname"]
		self.blocks = [b for b in tr["blocks"]]
		self.signal = tr["signal"]
		self.aspect = tr["aspect"]
		self.stopped = tr["stopped"]
		self.dblocks = []
		self.nblocks = []
		self.east = tr["east"]

	def Name(self):
		return self.iname if self.rname is None else self.rname

	def IName(self):
		return self.iname

	def SetIName(self, iname):
		self.iname = iname

	def RName(self):
		return self.rname

	def SetRName(self, rname):
		self.rname = rname

	def East(self):
		return self.east

	def SetEast(self, east):
		self.east = east

	def Blocks(self):
		return self.blocks

	def SetBlocks(self, blocks):
		self.dblocks = [bn for bn in self.blocks if bn not in blocks]  # deleted blocks
		self.nblocks = [bn for bn in blocks if bn not in self.blocks]  # new blocks
		self.blocks = [b for b in blocks]
		return self.dblocks, self.nblocks

	def Signal(self):
		return self.signal

	def SetSignal(self, signal):
		self.signal = signal

	def Aspect(self):
		return self.aspect

	def SetAspect(self, aspect):
		self.aspect = aspect

	def Stopped(self):
		return self.stopped

	def SetStopped(self, stopped):
		self.stopped = stopped

	def Dump(self):
		return "i:%s r:%s b:%s Sig: %s/%s/%s" % (self.iname, self.rname, ", ".join(self.blocks), self.signal, self.aspect, self.stopped)


class Trains:
	def __init__(self):
		self.trains = {}

	def Clear(self):
		self.trains = {}

	def AddTrain(self, tr):
		self.trains[tr.IName()] = tr
		# logging.debug("added train %s" % tr.Dump())

	def GetTrain(self, iname):
		return self.trains.get(iname, None)

	def UpdateTrain(self, tr):
		iname = tr["iname"]
		if iname not in self.trains:
			logging.debug("Trying to upodate a non-existant train: %s" % iname)
			return [], []

		blen = len(tr["blocks"])
		if blen == 0:
			del self.trains[iname]
			logging.debug("deleting train %s because blocks = []" % iname)
			return [], []
		else:
			itr = self.trains[iname]
			logging.debug("updating train %s from %s" % (iname, itr.Dump()))
			itr.SetRName(tr.get("rname", None))
			itr.SetEast(tr["east"])
			dblks, nblks = itr.SetBlocks(tr["blocks"])
			itr.SetSignal(tr["signal"])
			itr.SetAspect(tr["aspect"])
			itr.SetStopped(tr["stopped"])
			logging.debug("to %s" % itr.Dump())
			logging.debug("dblks = %s, nblks = %s" % (dblks, nblks))
			return dblks, nblks
