import wx
import wx.lib.newevent

import os
import json
import logging
import time

from dispatcher.settings import Settings


from trafficgen.listener import Listener
from trafficgen.rrserver import RRServer
from trafficgen.script import Script
from trafficgen.scrlist import ScriptListCtrl
from trafficgen.trainparmdlg import TrainParmDlg

from trafficgen.train import Trains
from trafficgen.layoutdata import LayoutData

from traineditor.generators import GenerateSim

(DeliveryEvent, EVT_DELIVERY) = wx.lib.newevent.NewEvent() 
(DisconnectEvent, EVT_DISCONNECT) = wx.lib.newevent.NewEvent()

ignoredCommands = ["alert", "clock", "lockturnout", "nodestatus", "control", "fleet", "breaker"]


class MainFrame(wx.Frame):
	def __init__(self, cmdFolder):
		wx.Frame.__init__(self, None, style=wx.DEFAULT_FRAME_STYLE)
		self.sessionid = None
		self.subscribed = False
		self.settings = Settings()
		self.scripts = {}
		self.blocks = {}
		self.turnouts = {}
		self.signals = {}
		self.routes = {}
		self.layout = None
		self.pausedScripts = []
		self.trains = {}
		self.listener = None
		self.rrServer = None
		self.selectedScripts = []
		self.startable = []
		self.running = []
		self.timerMultiplier = 1
		self.monitoredBlocks = {}
		self.monitoredTrains = {}

		icon = wx.Icon()
		icon.CopyFromBitmap(wx.Bitmap(os.path.join(os.getcwd(), "icons", "trafficgen.ico"), wx.BITMAP_TYPE_ANY))
		self.SetIcon(icon)

		self.title = "PSRY Traffic Generator"
		self.Bind(wx.EVT_CLOSE, self.OnClose)
		vsz = wx.BoxSizer(wx.VERTICAL)
		hsz = wx.BoxSizer(wx.HORIZONTAL)

		self.bSubscribe = wx.Button(self, wx.ID_ANY, "Connect")
		self.Bind(wx.EVT_BUTTON, self.OnSubscribe, self.bSubscribe)

		self.bRefresh = wx.Button(self, wx.ID_ANY, "Refresh")
		self.Bind(wx.EVT_BUTTON, self.OnRefresh, self.bRefresh)
		self.bRefresh.Enable(False)

		self.bStart = wx.Button(self, wx.ID_ANY, "Start")
		self.Bind(wx.EVT_BUTTON, self.OnStart, self.bStart)
		self.bStart.Enable(False)

		self.bStop = wx.Button(self, wx.ID_ANY, "Stop")
		self.Bind(wx.EVT_BUTTON, self.OnStop, self.bStop)
		self.bStop.Enable(False)

		self.bClear = wx.Button(self, wx.ID_ANY, "Clear")
		self.Bind(wx.EVT_BUTTON, self.OnClear, self.bClear)
		self.bClear.Enable(False)

		self.bSelectAll = wx.Button(self, wx.ID_ANY, "All")
		self.Bind(wx.EVT_BUTTON, self.OnSelectAll, self.bSelectAll)

		self.bSelectNone = wx.Button(self, wx.ID_ANY, "None")
		self.Bind(wx.EVT_BUTTON, self.OnSelectNone, self.bSelectNone)

		vsz.AddSpacer(20)

		hsz.AddSpacer(20)
		hsz.Add(self.bSubscribe)
		hsz.AddSpacer(20)
		hsz.Add(self.bRefresh)
		hsz.AddSpacer(20)

		vsz.Add(hsz)
		vsz.AddSpacer(20)

		self.scriptList = ScriptListCtrl(self, os.path.join(cmdFolder, "trafficgen"))
		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.AddSpacer(20)
		btnsz = wx.BoxSizer(wx.VERTICAL)
		btnsz.AddSpacer(20)
		btnsz.Add(self.bSelectAll)
		btnsz.AddSpacer(10)
		btnsz.Add(self.bSelectNone)
		btnsz.AddSpacer(50)
		btnsz.Add(self.bStart)
		btnsz.AddSpacer(10)
		btnsz.Add(self.bStop)
		btnsz.AddSpacer(10)
		btnsz.Add(self.bClear)
		btnsz.AddSpacer(20)
		hsz.Add(btnsz)
		hsz.AddSpacer(10)
		hsz.Add(self.scriptList)
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

	def Ticker(self, _):
		for scr in self.running:
			script = self.scripts[scr]
			script.Ticker()

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

	def reportSelection(self):
		selectedScripts = self.scriptList.GetChecked()
		self.startable = [scr for scr in selectedScripts if not self.scripts[scr].IsRunning()]
		self.stoppable = [scr for scr in selectedScripts if self.scripts[scr].IsRunning()]
		self.enableButtons()

	def enableButtons(self):
		haveStartable = len(self.startable) > 0 and self.subscribed
		self.bStart.Enable(haveStartable)
		self.bClear.Enable(haveStartable)
		self.bStop.Enable(len(self.running) > 0 and self.subscribed)

	def ClearDataStructures(self):
		self.blocks = {}
		self.turnouts = {}
		self.signals = {}
		self.routes = {}
		self.pausedScripts = []

	def OnSubscribe(self, _):
		if self.subscribed:
			self.listener.kill()
			self.listener.join()
			self.listener = None
			self.subscribed = False
			self.sessionid = None
			self.bSubscribe.SetLabel("Connect")
			self.bRefresh.Enable(False)
			self.enableButtons()
			self.ClearDataStructures()
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
			self.enableButtons()

		self.ShowTitle()

	def OnRefresh(self, _):
		self.Request({"refresh": {"SID": self.sessionid}})

	def OnSelectAll(self, _):
		self.scriptList.SelectAll()

	def OnSelectNone(self, _):
		self.scriptList.SelectNone()

	def OnStart(self, _):
		trainParams = {}
		for scr in self.startable:
			tr = self.trains.GetTrainById(scr)
			loco = tr.GetNormalLoco()
			if loco is None:
				loco = "??"
			script = self.scripts[scr]
			tm = script.GetTimeMultiple()
			tlen = script.GetTrainLen()
			if tlen is None:
				tlen = 3
			trainParams[scr] = [scr, loco, tm, tlen]
			
		dlg = TrainParmDlg(self, trainParams)
		rc = dlg.ShowModal()
		dlg.Destroy()
		if rc != wx.ID_OK:
			return 
			
		for scr in self.startable:
			p = trainParams[scr]
			script = self.scripts[scr]
			script.SetLoco(p[1])
			script.SetTimeMultiple(p[2])
			script.SetTrainLen(p[3])
			script.Execute()
			self.running.append(scr)

		self.scriptList.ClearChecks()
		self.startable = []
		self.enableButtons()

	def OnStop(self, _):
		for scr in self.running:
			self.scripts[scr].Stop()
		self.scriptList.ClearChecks()
		self.startable = []
		self.running = []
		self.enableButtons()

	def OnClear(self, _):
		for scr in self.startable:
			self.scripts[scr].RemoveTrain()
		self.scriptList.ClearChecks()
		self.startable = []
		self.stoppable = []
		self.enableButtons()

	def ScriptComplete(self, scrName):
		try:
			del(self.running[scrName])
		except:
			pass

	def PauseScript(self, script):
		self.pausedScripts.append(script)

	def CheckResumeScripts(self):
		delList = []
		resumeList = []
		logging.debug("check for which scripts to resume.  %d paused" % len(self.pausedScripts))
		for i in range(len(self.pausedScripts)):
			logging.debug("Script at index %d" % i)
			scr = self.pausedScripts[i]
			if not scr.CheckPause():
				logging.debug("deleting from paused list and adding to resume list")
				delList.append(i)
				resumeList.append(scr)

		for i in delList:
			logging.debug("actually deleting script %d from paused list" % i)
			del(self.pausedScripts[i])

		for scr in resumeList:
			logging.debug("resuming script %s" % str(scr.GetName()))
			scr.Resume()

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
				continue

			logging.debug("Dispatch: %s: %s" % (cmd, parms))
			if cmd == "turnout":
				for p in parms:
					turnout = p["name"]
					state = p["state"]
					self.turnouts[turnout] = state

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

			elif cmd == "train":
				for p in parms:
					iname = p["iname"]
					rname = p["rname"]
					east = p["east"]
					loco = p["loco"]
					blocks = p["blocks"]
					signal = p["signal"]
					aspect = p["aspect"]
					for bn in blocks:
						if bn in self.monitoredBlocks:
							self.monitoredBlocks[bn].ReportTrainInBlock(iname, p)
							del(self.monitoredBlocks[bn])
					if iname in self.monitoredTrains:
						self.monitoredTrains[iname].ReportTrain(iname, p)

			elif cmd == "sessionID":
				self.sessionid = int(parms)
				self.ShowTitle()
				self.Request({"identify": {"SID": self.sessionid, "function": "TRAFFICGEN"}})
				self.Request({"refresh": {"SID": self.sessionid}})

			elif cmd == "end":
				self.trains = Trains(self.rrServer)
				self.layout = LayoutData(self.rrServer)

				for tr in self.trains:
					scr = Script(self, tr, self.layout, self.timerInterval)
					self.scriptList.AddScript(scr)
					self.scripts[scr.GetName()] = scr

				self.timer.Start(self.timerInterval)

			else:
				logging.debug("Ignoring unknown command: %s %s" % (cmd, str(parms)))

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

	def MonitorBlock(self, blknm, script):
		self.monitoredBlocks[blknm] = script

	def MonitorTrain(self, iname, script):
		self.monitoredTrains[iname] = script

	def RefreshStatus(self, scrName):
		self.scriptList.refreshScript(scrName)

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
		self.bRefresh.Enable(False)
		self.ClearDataStructures()
		self.ShowTitle()

	def OnClose(self, evt):
		try:
			self.listener.kill()
			self.listener.join()
		except:
			pass
		self.Destroy()

