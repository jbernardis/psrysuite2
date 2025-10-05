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

from traineditor.layoutdata import LayoutData
from traineditor.generators import GenerateSim

(DeliveryEvent, EVT_DELIVERY) = wx.lib.newevent.NewEvent() 
(DisconnectEvent, EVT_DISCONNECT) = wx.lib.newevent.NewEvent() 


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
		self.pausedScripts = []
		self.listener = None
		self.ticker = None
		self.rrServer = None
		self.selectedScripts = []
		self.startable = []
		self.stoppable = []

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

		wx.CallAfter(self.Initialize)

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
		self.layout = LayoutData(self.rrServer)

		retries = 0
		while not self.layout.IsConnected() and retries < 5:
			retries += 1
			logging.debug("Failed connection with server - retrying after %d second delay" % retries)
			print("Failed connection with server - retrying after %d second delay" % retries)
			time.sleep(retries)
			self.layout = LayoutData(self.rrServer)

		if not self.layout.IsConnected():
			logging.error("Unable to connect with railroad server")
		elif retries > 0:
			logging.debug("Successfully connected with railroad server after %d retries" % retries)

		self.ClearDataStructures()

		self.trains = Trains(self.rrServer)
			
		for tr in self.trains:
			trid, script = GenerateSim(tr, self.layout)

			s = Script(self, script, trid, self.cbComplete)
			self.scripts[trid] = s

		for trid in sorted(self.scripts.keys()):
			self.scriptList.AddScript(self.scripts[trid])

	def reportSelection(self):
		selectedScripts = self.scriptList.GetChecked()
		self.startable = [scr for scr in selectedScripts if not self.scripts[scr].IsRunning()]
		self.stoppable = [scr for scr in selectedScripts if self.scripts[scr].IsRunning()]
		self.enableButtons()

	def enableButtons(self):
		haveStartable = len(self.startable) > 0 and self.subscribed
		self.bStart.Enable(haveStartable)
		self.bClear.Enable(haveStartable)
		self.bStop.Enable(len(self.stoppable) > 0 and self.subscribed)

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
		self.scriptList.ClearChecks()
		self.startable = []
		self.stoppable = []
		self.enableButtons()

	def OnStop(self, _):
		for scr in self.stoppable:
			self.scripts[scr].Stop()
		self.scriptList.ClearChecks()
		self.startable = []
		self.stoppable = []
		self.enableButtons()

	def OnClear(self, _):
		for scr in self.startable:
			self.scripts[scr].RemoveTrain()
		self.scriptList.ClearChecks()
		self.startable = []
		self.stoppable = []
		self.enableButtons()

	def cbComplete(self, scrName):
			self.Request({"traincomplete": {"train": scrName}})
	
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
			logging.debug("Dispatch: %s: %s" % (cmd, parms))
			if cmd == "turnout":
				for p in parms:
					turnout = p["name"]
					state = p["state"]
					self.turnouts[turnout] = state
				self.CheckResumeScripts()

			elif cmd == "block":
				for p in parms:
					block = p["name"]
					state = p["state"]
					if block in self.blocks:
						self.blocks[block][0] = state
					else:
						self.blocks[block] = [ state, 'E']
				self.CheckResumeScripts()

			elif cmd == "blockdir":
				for p in parms:
					block = p["block"]
					direction = p["dir"]
					if block in self.blocks:
						self.blocks[block][1] = direction
					else:
						self.blocks[block] = [ 0, direction]
				self.CheckResumeScripts()
					
			elif cmd == "signal":
				for p in parms:
					sigName = p["name"]
					aspect = p["aspect"]
					self.signals[sigName] = aspect
				self.CheckResumeScripts()

			elif cmd == "setroute":
				for p in parms:
					blknm = p["block"]
					rte = p["route"]
					try:
						ends = [None if e == "-" else e for e in p["ends"]]
					except KeyError:
						ends = None
					self.routes[blknm] = [rte, ends]
				self.CheckResumeScripts()
											
			elif cmd == "handswitch":
				for p in parms:
					hsName = p["name"]
					state = p["state"]
						
			elif cmd == "indicator":
				for p in parms:
					iName = p["name"]
					value = int(p["value"])

			elif cmd == "breaker":
				for p in parms:
					name = p["name"]
					val = p["value"]

			elif cmd == "settrain":
				blocks = parms["blocks"]
				name = parms["name"]
				loco = parms["loco"]
				try:
					east = parms["east"]
				except KeyError:
					east = True

			elif cmd == "sessionID":
				self.sessionid = int(parms)
				self.ShowTitle()
				self.Request({"identify": {"SID": self.sessionid, "function": "TRAFFICGEN"}})
				self.Request({"refresh": {"SID": self.sessionid}})

			elif cmd == "end":
				if parms["type"] == "layout":
					self.Request({"refresh": {"SID": self.sessionid, "type": "trains"}})
				elif parms["type"] == "trains":
					pass

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

