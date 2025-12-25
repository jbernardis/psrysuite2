import wx
import wx.lib.newevent

import os
import json
import logging
import time

from dispatcher.settings import Settings


from autorouter.listener import Listener
from autorouter.rrserver import RRServer
# from autorouter.script import Script
from autorouter.trainlist import TrainListCtrl

from autorouter.train import Trains
from autorouter.layoutdata import LayoutData

# from traineditor.generators import GenerateSim

(DeliveryEvent, EVT_DELIVERY) = wx.lib.newevent.NewEvent() 
(DisconnectEvent, EVT_DISCONNECT) = wx.lib.newevent.NewEvent()

ignoredCommands = ["alert", "clock", "nodestatus", "control", "fleet", "breaker"]

osButtons = {
	"COSGMW": {
		"CRtC11G21": "CG21W",
		"CRtC11C10": "CC10W",
		"CRtC11C30": "CC30W",
		"CRtC11C31": "CC31W"
	},
	"COSGME": {
		"CRtG12C20": "CG12E",
		"CRtG10C20": "CG10E",
		"CRtC10C20": "CC10E",
		"CRtC30C20": "CC30E"
	},
	"COSSHE": {
		"CRtC20C44": "CC44E",
		"CRtC20C43": "CC43E",
		"CRtC20C42": "CC42E",
		"CRtC20C41": "CC41E",
		"CRtC20C40": "CC40E",
		"CRtC20C21": "CC21E",
		"CRtC20C50": "CC50E",
		"CRtC20C51": "CC51E",
		"CRtC20C52": "CC52E",
		"CRtC20C53": "CC53E",
		"CRtC20C54": "CC54E"
	},
	"COSSHW": {
		"CRtC44C22": "CC44W",
		"CRtC43C22": "CC43W",
		"CRtC42C22": "CC42W",
		"CRtC41C22": "CC41W",
		"CRtC40C22": "CC40W",
		"CRtC21C22": "CC21W",
		"CRtC50C22": "CC50W",
		"CRtC51C22": "CC51W",
		"CRtC52C22": "CC52W",
		"CRtC53C22": "CC53W",
		"CRtC54C22": "CC54W"
	}
}


class MainFrame(wx.Frame):
	def __init__(self, cmdFolder):
		wx.Frame.__init__(self, None, style=wx.STAY_ON_TOP | wx.CAPTION | wx.RESIZE_BORDER | wx.CLOSE_BOX)
		self.sessionid = None
		self.subscribed = False
		self.settings = Settings()
		self.blocks = {}
		self.turnouts = {}
		self.signals = {}
		self.routes = {}
		self.layout = None
		self.roster = None
		self.listener = None
		self.rrServer = None
		self.timerMultiplier = 1

		self.availableTrains = {}
		self.controlledTrains = {}

		self.requestQueue = []

		# icon = wx.Icon()
		# icon.CopyFromBitmap(wx.Bitmap(os.path.join(os.getcwd(), "icons", "trafficgen.ico"), wx.BITMAP_TYPE_ANY))
		# self.SetIcon(icon)

		self.title = "PSRY Auto Router"
		self.Bind(wx.EVT_CLOSE, self.OnClose)
		vsz = wx.BoxSizer(wx.VERTICAL)
		hsz = wx.BoxSizer(wx.HORIZONTAL)

		self.bSubscribe = wx.Button(self, wx.ID_ANY, "Connect")
		self.Bind(wx.EVT_BUTTON, self.OnSubscribe, self.bSubscribe)

		vsz.AddSpacer(20)

		hsz.AddSpacer(20)
		hsz.Add(self.bSubscribe)
		hsz.AddSpacer(20)

		vsz.Add(hsz)
		vsz.AddSpacer(20)

		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.AddSpacer(20)

		cszr = wx.BoxSizer(wx.VERTICAL)
		cszr.Add(wx.StaticText(self, wx.ID_ANY, "Available Trains"))

		self.lbAvailable = wx.ListBox(self, wx.ID_ANY, size=(-1, 280), choices=[], style=wx.LB_EXTENDED)
		self.Bind(wx.EVT_LISTBOX, self.OnAvailableChoice, self.lbAvailable)
		cszr.Add(self.lbAvailable)

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

		cszr = wx.BoxSizer(wx.VERTICAL)
		cszr.Add(wx.StaticText(self, wx.ID_ANY, "Controlled Trains"))

		self.controlledList = TrainListCtrl(self, os.path.join(cmdFolder, "trafficgen"))
		cszr.Add(self.controlledList)

		hsz.Add(cszr)
		hsz.AddSpacer(20)

		vsz.Add(hsz)
		vsz.AddSpacer(20)

		self.SetSizer(vsz)
		self.Fit()
		self.Layout()

		self.timerInterval = 500

		self.timer = wx.Timer(self)
		self.Bind(wx.EVT_TIMER, self.Ticker)

		wx.CallAfter(self.Initialize)

	def MoveToTop(self):
		st = self.GetWindowStyle()

		st |= wx.STAY_ON_TOP

		# st &= ~wx.STAY_ON_TOP

		self.SetWindowStyle(st)
		self.Show()

	def Ticker(self, _):
		self.CheckQueuedRequests()

	def CheckQueuedRequests(self):
		newList = []
		for req in self.requestQueue:
			if not self.ProcessRouteRequest(req):
				newList.append(req)
		self.requestQueue = newList

	def ShowTitle(self):
		titleString = self.title
		if self.subscribed and self.sessionid is not None:
			titleString += ("  -  Session ID %d" % self.sessionid)
		self.SetTitle(titleString)

	def Initialize(self):
		self.listener = None
		self.ShowTitle()
		self.Bind(EVT_DELIVERY, self.onDeliveryEvent)
		self.Bind(EVT_DISCONNECT, self.onDisconnectEvent)

		self.rrServer = RRServer()
		self.rrServer.SetServerAddress(self.settings.ipaddr, self.settings.serverport)

		wx.CallLater(2000, self.ConnectServer)

	def reportSelection(self):
		selectedTrains = self.controlledList.GetChecked()
		self.bDel.Enable(len(selectedTrains) > 0)

	def ClearDataStructures(self):
		self.blocks = {}
		self.turnouts = {}
		self.signals = {}
		self.routes = {}
		self.availableTrains = {}
		self.controlledTrains = {}
		self.controlledList.ClearAll()

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

	def OnAvailableChoice(self, _):
		il = self.lbAvailable.GetSelections()
		if len(il) == 0:
			self.bAdd.Enable(False)

		else:
			self.bAdd.Enable(True)

	def OnBAdd(self, _):
		il = self.lbAvailable.GetSelections()
		for i in il:
			trid = self.lbAvailable.GetString(i)
			self.controlledTrains[trid] = self.availableTrains[trid]
			self.controlledTrains[trid]["status"] = ""
			self.controlledList.AddTrain(self.controlledTrains[trid])
			del self.availableTrains[trid]
			self.AnalyzeTrain(trid)

		choices = sorted(self.availableTrains.keys())
		self.lbAvailable.SetItems(choices)
		if len(choices) == 0:
			self.lbAvailable.SetSelection(wx.NOT_FOUND)
			self.bAdd.Enable(False)
		else:
			self.lbAvailable.SetSelection(0)
			self.bAdd.Enable(True)

	def OnBDel(self, _):
		selectedTrains = self.controlledList.GetChecked()
		for trid in selectedTrains:
			tr = self.controlledTrains[trid]
			del self.controlledTrains[trid]
			self.controlledList.RemoveTrain(trid)
			self.availableTrains[trid] = tr

		choices = sorted(self.availableTrains.keys())
		self.lbAvailable.SetItems(choices)
		self.lbAvailable.SetSelection(0)
		self.bAdd.Enable(True)
		self.bDel.Enable(False)

	def SignalAspect(self, signal):
		try:
			return self.signals[signal]
		except KeyError:
			# signal %s unknown
			return False

	def BlockOccupied(self, block):
		blist = block.split(",")
		for b in blist:
			if self.blocks[b][0] != 0:
				return True
		return False

	def NotOSRoute(self, OS, rte):
		route = self.routes[OS][0]
		if rte != route:
			return True
		return False

	def raiseDeliveryEvent(self, data):  # thread context
		try:
			jdata = json.loads(data)
		except json.decoder.JSONDecodeError:
			return
		evt = DeliveryEvent(data=jdata)
		wx.QueueEvent(self, evt)

	def onDeliveryEvent(self, evt):
		for cmd, parms in evt.data.items():
			if cmd in ignoredCommands:
				logging.debug("Ignoring: %s: %s" % (cmd, parms))
				continue

			logging.debug("Dispatch: %s: %s" % (cmd, parms))
			if cmd == "autorouter":
				action = parms["action"][0]
				logging.debug("AR Action: (%s)" % action)
				if action == "show":
					if self.IsShown():
						self.Hide()
					else:
						self.MoveToTop()

			elif cmd == "turnout":
				for p in parms:
					turnout = p["name"]
					state = p["state"]
					locked = p.get("locked", False)
					self.turnouts[turnout] = (state, locked)
				self.CheckQueuedRequests()

			elif cmd == "block":
				for p in parms:
					block = p["name"]
					state = p["state"]
					self.blocks[block] = state
				self.CheckQueuedRequests()

			elif cmd == "showaspect":
				for p in parms:
					sigName = p["signal"]
					aspect = p["aspect"]
					self.signals[sigName] = aspect
				self.CheckQueuedRequests()

			elif cmd == "setroute":
				for p in parms:
					blknm = p["os"]
					rte = p["route"]
					self.routes[blknm] = rte
				self.CheckQueuedRequests()

			elif cmd == "lockturnout":
				for p in parms:
					tonm = p["name"]
					lock = p["lock"]
					pos, x = self.turnouts[tonm]
					self.turnouts[tonm] = (pos, lock)
				self.CheckQueuedRequests()

			elif cmd == "train":
				for p in parms:
					iname = p["iname"]
					rname = p["rname"]
					roster = self.roster.GetTrainById(rname)
					if rname is None or roster is None:
						logging.debug("skipping train %s because it is unknown" % iname)
						continue

					if rname in self.controlledTrains:
						self.controlledTrains[rname].update(p)
						if len(p["blocks"]) == 0:
							# remove the train from the controlled list
							self.controlledList.RemoveTrain(rname)
							del self.controlledTrains[rname]
						else:
							# see if we need to change anything for this train
							self.AnalyzeTrain(rname)

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
				self.roster = Trains(self.rrServer)
				self.layout = LayoutData(self.rrServer)
				self.Request({"identify": {"SID": self.sessionid, "function": "AUTOROUTER"}})
				self.Request({"refresh": {"SID": self.sessionid}})

			elif cmd == "end":
				self.timer.Start(self.timerInterval)

			else:
				logging.debug("Ignoring unknown command: %s %s" % (cmd, str(parms)))

	def AnalyzeTrain(self, trid):
		print("checking train %s for needed action" % trid)
		try:
			tr = self.controlledTrains[trid]
		except KeyError:
			logging.debug("Train %s not in controlled list" % trid)
			return

		print("%s" % str(tr))
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

		currentBlock = tr["blocks"][-1]
		if currentBlock.endswith(".E") or currentBlock.endswith(".W"):
			currentBlock = currentBlock[:-2]

		try:
			idx = blockSeq.index(currentBlock)
		except ValueError:
			# it could be in an OS in which case nothing needs to be done
			if currentBlock in osSeq:
				tr["status"] = ""
				self.controlledList.refreshTrain(trid)
				return

			tr["status"] = "Train % is in unexpected block: %s" % (trid, currentBlock)
			self.controlledList.refreshTrain(trid)
			return

		if idx >= len(signalSeq):
			tr["status"] = "Completed"
			self.controlledList.refreshTrain(trid)
			return

		wantedOS = osSeq[idx]
		wantedRoute = rteSeq[idx]
		wantedSignal = signalSeq[idx]
		print("Train %s is in block %s and needs route %s/%s and signal %s to move forward" % (trid, currentBlock, wantedOS, wantedRoute, wantedSignal))

		rte = self.routes.get(wantedOS, None)
		wrongRoute = rte is None or rte != wantedRoute
		if not wrongRoute and wantedOS in ["SOSE", "SOSW"]:
			# check for interference from harpers ferry crossing
			al = self.signals["S8L"]
			ar = self.signals["S8R"]
			if al + ar != 0:
				wrongRoute = True
		print("wrong route: %s active route %s" % (str(wrongRoute), str(rte)))

		# if the signal is permissive but the route is wrong, set the signal to 0 aspect and just continue
		aspect = self.signals[wantedSignal]
		if wrongRoute and aspect != 0:
			self.Request({"signalclick": {"name": wantedSignal, "wantedaspect": 0, "callon": 0}})

		# if the route is correct, but the signal is stopped, ask for a permissive signal

		if not wrongRoute:
			if aspect == 0:
				# request the signal and proceed
				self.Request({"signalclick": {"name": wantedSignal, "wantedaspect": 1, "callon": 0}})
			# otherwise we have the correct route and a permissive signal - just proceed
			tr["status"] = ""
			self.controlledList.refreshTrain(trid)
			return

		# otherwise the route is wrong.  Since this takes time to set up, we need to enqueue the request
		rt = self.layout.GetOSActiveRoute(wantedRoute)
		print("%s" % str(rt))
		if rt is None:
			logging.error("Unable to find route %s" % wantedRoute)
			tr["status"] = "Unable to find route %s/%s" % (wantedOS, wantedRoute)
			self.controlledList.refreshTrain(trid)
			return

		toList = rt["turnouts"]
		tr["status"] = "Waiting for route %s/%s" % (wantedOS, wantedRoute)
		self.requestQueue.append(RouteRequest(wantedOS, wantedRoute, toList, wantedSignal))
		self.controlledList.refreshTrain(trid)

	def ProcessRouteRequest(self, req):
		# see if we need to set the route
		osName = req.OSName()
		route = req.Route()
		if osName in ["SOSE", "SOSW"]:
			# check for interference from harpers ferry crossing
			al = self.signals["S8L"]
			ar = self.signals["S8R"]
			if al + ar != 0:
				return False

		currentRoute = self.routes.get(osName, None)
		if currentRoute != route:
			try:
				nxb = osButtons[osName][route]
			except KeyError:
				nxb = None
			if nxb is None:  # set route with individual turnout commands
				toCmd = []
				for tnm, pos in req.ToList():
					st, lock = self.turnouts[tnm]
					if st != pos:
						# it's not in the position we want, so make sure it's unlocked
						if lock:
							return False
						toCmd.append([tnm, pos])

				if len(toCmd) > 0:
					for tnm, pos in toCmd:
						self.Request({"turnoutclick": {"name": tnm, "status": pos}})
					return False
			else:
				self.Request({"nxbutton": {"button": [nxb], "cmd": ["nxbutton"]}})
			return False

		# once the route is correct, request a permissive signal
		self.Request({"signalclick": {"name": req.Signal(), "wantedaspect": 1, "callon": 0}})
		return True

	def GetSignalAspect(self, signm):
		try:
			return self.signals[signm]
		except KeyError:
			return 0

	def GetOSRoute(self, osnm):
		try:
			return self.routes[osnm]
		except KeyError:
			return None

	def raiseDisconnectEvent(self): # thread context
		evt = DisconnectEvent()
		wx.PostEvent(self, evt)

	def Request(self, req):
		if self.subscribed:
			logging.debug("sending command: %s" % str(req))
			self.rrServer.SendRequest(req)

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
	def __init__(self, osName, route, tolist, signal):
		self.osName = osName
		self.route = route
		self.tolist = tolist
		self.signal = signal

	def OSName(self):
		return self.osName

	def Route(self):
		return self.route

	def ToList(self):
		return self.tolist

	def Signal(self):
		return self.signal
