import wx
import wx.lib.newevent

import os
import sys
import json
import logging
import time

from dispatcher.train import formatThrottle
from activetrains.trainlist import ActiveTrainsPanel
from dispatcher.listener import Listener
from dispatcher.rrserver import RRServer
from dispatcher.constants import aspectname, aspecttype, aspectprofileindex, RegAspects, REPLACE

(DeliveryEvent, EVT_DELIVERY) = wx.lib.newevent.NewEvent() 
(DisconnectEvent, EVT_DISCONNECT) = wx.lib.newevent.NewEvent() 

BTNDIM = (80, 23) if sys.platform.lower() == "win32" else (100, 23)
MAXSTEPS = 9

ignoredCommands = ["breaker", "fleet", "control", "siglever", "signallock",
				"blockclear", "blockdir", "turnout", "turnoutlock", "clock"]


class MainFrame(wx.Frame):
	def __init__(self, settings):
		wx.Frame.__init__(self, None, size=(1500, 800), style=wx.DEFAULT_FRAME_STYLE)
		self.settings = settings

		self.listener = None
		self.sessionid = None
		self.subscribed = False
		
		self.trains = {}
		self.locoMap = {}
		self.routes = {}
		self.locos = {}

		self.rrServer = RRServer()
		self.rrServer.SetServerAddress(self.settings.ipaddr, self.settings.serverport)
		self.CreateDispatchTable()
		
		self.SetBackgroundColour(wx.Colour(200, 200, 200))

		icon = wx.Icon()
		icon.CopyFromBitmap(wx.Bitmap(os.path.join(os.getcwd(), "icons", "dispatch.ico"), wx.BITMAP_TYPE_ANY))
		self.SetIcon(icon)
		
		self.pngPSRY = wx.Image(os.path.join(os.getcwd(), "images", "PSLogo_mid.png"), wx.BITMAP_TYPE_PNG).ConvertToBitmap()
		mask = wx.Mask(self.pngPSRY, wx.BLUE)
		self.pngPSRY.SetMask(mask)

		self.Bind(wx.EVT_CLOSE, self.OnClose)
		self.trains = {}
		self.bSubscribe = wx.Button(self, wx.ID_ANY, "Connect", size=BTNDIM)
		self.Bind(wx.EVT_BUTTON, self.OnSubscribe, self.bSubscribe)
		self.bSubscribe.SetToolTip("Connect to/Disconnect from the Railroad server")

		self.bRefresh = wx.Button(self, wx.ID_ANY, "Refresh", size=BTNDIM)
		self.Bind(wx.EVT_BUTTON, self.OnRefresh, self.bRefresh)
		self.bRefresh.SetToolTip("Refresh all railroad information from the railroad server")
		self.bRefresh.Enable(False)
		
		vsz = wx.BoxSizer(wx.VERTICAL)	
		vsz.AddSpacer(20)
		
		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.AddSpacer(20) 
		hsz.Add(self.bSubscribe, 0, wx.ALIGN_CENTER_VERTICAL)
		hsz.AddSpacer(30)
		
		b = wx.StaticBitmap(self, wx.ID_ANY, self.pngPSRY)
		hsz.Add(b, 0, wx.ALIGN_CENTER_VERTICAL)
		
		hsz.AddSpacer(30)

		hsz.Add(self.bRefresh, 0, wx.ALIGN_CENTER_VERTICAL) 
		hsz.AddSpacer(20)
		
		vsz.Add(hsz, 0, wx.ALIGN_CENTER_HORIZONTAL)
		vsz.AddSpacer(10)
		
		self.ActiveTrainsPanel = ActiveTrainsPanel(self, self.settings.activetrains.lines)
		vsz.Add(self.ActiveTrainsPanel, 1, wx.EXPAND)
		
		vsz.AddSpacer(20)
		
		self.ShowTitle()
				
		self.SetSizer(vsz)
		self.Layout()
		self.Fit()
		
		self.Bind(EVT_DELIVERY, self.onDeliveryEvent)
		self.Bind(EVT_DISCONNECT, self.onDisconnectEvent)
		
		self.Bind(wx.EVT_TIMER, self.onTicker)
		self.ticker = wx.Timer(self)
		self.ticker.Start(60000)

	def onTicker(self, _):
		self.ActiveTrainsPanel.UpdateTimers()
		
	def TrainSelected(self, tr):
		logging.debug("train selected %s" % str(tr))
		pass
		# trid = tr.GetName()
		# loco = tr.GetLoco()
		# try:
		# 	info = self.trainList[trid]
		# except KeyError:
		# 	return
		#
		# self.ShowTrainDesc(tr, loco, info)
		
	def ShowTrainDesc(self, tr, loco, info):
		desc = []
		try:
			d = " - " + info["desc"]
		except KeyError:
			d = ""
		desc.append("Train: %s%s" % (tr.GetName(), d))
		desc.append("")
				
		details = "Eastbound" if info["eastbound"] else "Westbound"
		if info["cutoff"]:
			details += " via cutoff"
		desc.append(details)
		desc.append("")
		
		try:
			linfo = self.locoList[loco]
		except KeyError:
			linfo = None
		if linfo:
			try:
				d = " - " + linfo["desc"]
			except:
				d = ""
			desc.append("Locomotive: %s%s" % (loco, d))
		else:
			desc.append("Locomotive unknown")
		desc.append("")
			
		track = info["tracker"]
		for lx in range(MAXSTEPS):
			if lx >= len(track):
				desc.append("")
			else:
				desc.append("%-12.12s  %-4.4s  %s" % (track[lx][0], "(%d)" % track[lx][2], track[lx][1]))
		
		dlg = DescriptionDlg(self, tr.GetName(), desc)
		dlg.ShowModal()
		dlg.Destroy()

	def ShowTitle(self):
		self.SetTitle("Active Train Display - %s" % ("NOT connected" if not self.subscribed else "connected" if self.sessionid is None else ("Session ID %d" % self.sessionid)))

	def Request(self, req, force=False):
		self.rrServer.SendRequest(req)
					
	def Get(self, cmd, parms):
		return self.rrServer.Get(cmd, parms)

	def OnSubscribe(self, _):
		if self.subscribed:
			self.listener.kill()
			self.listener.join()
			self.listener = None
			self.subscribed = False
			self.sessionid = None
			self.bSubscribe.SetLabel("Connect")
			self.bRefresh.Enable(False)
			# self.activeTrains.RemoveAllTrains()
			self.trains = {}
			self.locoMap = {}
			self.routes = {}
			self.EnableActiveTrainsPanel(False)

		else:
			self.listener = Listener(self, self.settings.ipaddr, self.settings.socketport)
			if not self.listener.connect():
				logging.error("Unable to establish connection with server")
				print("Unable to establish connection with server")
				self.listener = None
				
				dlg = wx.MessageDialog(self, 'Unable to connect to server', 'Unable to Connect', wx.OK | wx.ICON_ERROR)
				dlg.ShowModal()
				dlg.Destroy()
				return

			self.listener.start()
			self.subscribed = True
			self.bSubscribe.SetLabel("Disconnect")
			self.bRefresh.Enable(True)
				
			self.RetrieveData()
			self.EnableActiveTrainsPanel(True)

		self.ShowTitle()

	def EnableActiveTrainsPanel(self, flag=True):
		self.ActiveTrainsPanel.Enable(flag)
		if flag:
			self.ActiveTrainsPanel.SetLocos(self.locos)

	def RetrieveData(self):
		logging.debug("retrieve data")
		locos = self.Get("getlocos", {})
		if locos is None:
			logging.error("Unable to retrieve locos")
			locos = {}

		self.locos = locos
		#
		# trains = self.Get("gettrains", {})
		# if trains is None:
		# 	logging.error("Unable to retrieve trains")
		# 	trains = {}
		#
		# self.trainList = trains
		#
		# engineers = self.Get("getengineers", {})
		# if engineers is None:
		# 	logging.error("Unable to retrieve engineers")
		# 	engineers = []
		#
		# self.engineerList = engineers

	def OnRefresh(self, _):
		self.DoRefresh()
		
	def DoRefresh(self):
		self.ActiveTrainsPanel.RemoveAllTrains()
		self.trains = {}
		self.Request({"refresh": {"SID": self.sessionid}})

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
			"train":			self.DoCmdTrain,
			"setroute":			self.DoCmdSetRoute,
			# "dccspeed":			self.DoCmdDCCSpeed,
			"dccspeeds":		self.DoCmdDCCSpeeds,
			"sessionID":		self.DoCmdSessionID,
			"end":				self.DoCmdEnd,
		}

	def onDeliveryEvent(self, evt):
		for cmd, parms in evt.data.items():
			try:
				handler = self.dispatch[cmd]
			except KeyError:
				pass
				# logging.error("Unknown command: %s" % cmd)

			else:
				logging.info("Inbound command: %s: %s" % (cmd, parms))
				handler(parms)
					
	def DoCmdTrain(self, parms):
		for p in parms:
			trid = p["iname"]
			if trid in self.trains:  # an existing train
				if len(p["blocks"]) < 1:  # no blocks - delete the train
					del self.trains[trid]
					self.ActiveTrainsPanel.RemoveTrain(trid)

				else:  # update the existing train with new information
					self.ReplaceRouteNames(p)
					if p["engineer"] != self.trains[trid]["engineer"] and p["engineer"] is None:
						p["assigntime"] = None
					self.trains[trid].update(p)
					self.ActiveTrainsPanel.RefreshAll()

			else:  # a new train
				if "throttle" not in p:
					p["throttle"] = None
				if "assigntime" not in p:
					p["assigntime"] = None
				self.trains[trid] = p
				self.ReplaceRouteNames(p)
				self.ActiveTrainsPanel.AddTrain(p)

		self.GenerateLocoMap()

	def DoCmdSetRoute(self, parms):
		for p in parms:
			try:
				osbn = p["os"]
			except KeyError:
				osbn = None

			try:
				rtn = p["route"]
			except KeyError:
				rtn = None

			if osbn is None or rtn is None:
				return

			self.routes[osbn] = "{%s}" % rtn[3:]

	def GenerateLocoMap(self):
		self.locoMap = {tr["loco"]: tr for tr in self.trains.values() if tr["loco"] != "??"}

	def ReplaceRouteNames(self, tr):
		tr["blocks"] = [self.routes.get(bn, bn) for bn in tr["blocks"]]

	def FindTrainByLoco(self, loco):
		try:
			return self.locoMap[loco]
		except:
			return None

	# def DoCmdDCCSpeed(self, parms):
	# 	for p in parms:
	# 		try:
	# 			loco = p["loco"]
	# 		except:
	# 			loco = None
	#
	# 		try:
	# 			speed = p["speed"]
	# 		except:
	# 			speed = "0"
	#
	# 		try:
	# 			speedtype = p["speedtype"]
	# 		except:
	# 			speedtype = None
	#
	# 		if loco is None:
	# 			logging.error("DCCSpeed command without loco parameter")
	# 			return
	#
	# 		tr = self.FindTrainByLoco(loco)
	# 		if tr is not None:
	# 			tr["throttle"] = (speed, speedtype)
	# 			self.ActiveTrainsPanel.UpdateTrain(tr)
	#
	def DoCmdDCCSpeeds(self, parms):
		for loco, spinfo in parms.items():
			tr = self.FindTrainByLoco(loco)
			if tr is not None:
				tr["throttle"] = formatThrottle(spinfo[0], spinfo[1])
				self.ActiveTrainsPanel.UpdateTrain(tr)

	def DoCmdSessionID(self, parms):
		self.sessionid = int(parms)
		logging.info("connected to railroad server with session ID %d" % self.sessionid)
		self.Request({"identify": {"SID": self.sessionid, "function": "ACTIVETRAINS"}})
		self.DoRefresh()
		self.ShowTitle()

	def DoCmdEnd(self, parms):
		pass

	def raiseDisconnectEvent(self): # thread context
		evt = DisconnectEvent()
		try:
			wx.PostEvent(self, evt)
		except RuntimeError:
			logging.info("Runtime error caught while trying to post disconnect event - not a problem if this is during shutdown")

	def onDisconnectEvent(self, _):
		self.listener = None
		self.subscribed = False
		self.bSubscribe.SetLabel("Connect")
		self.bRefresh.Enable(False)
		logging.info("Server socket closed")
		
		self.ActiveTrainsPanel.RemoveAllTrains()
		self.trains = {}
		self.EnableActiveTrainsPanel(False)
		self.ShowTitle()

		dlg = wx.MessageDialog(self, "The railroad server connection has gone down.",
			"Server Connection Error",
			wx.OK | wx.ICON_ERROR)
		dlg.ShowModal()
		dlg.Destroy()
	
	def OnClose(self, _):
		self.CloseProgram()
		
	def CloseProgram(self):
		try:
			self.listener.kill()
			self.listener.join()
		except:
			pass
			
		self.Destroy()
		logging.info("Active Train List process ending")


class DescriptionDlg(wx.Dialog):
	def __init__(self, parent, trid, desc):
		wx.Dialog.__init__(self, parent, wx.ID_ANY, "Train %s Description" % trid)
		self.parent = parent
		self.Bind(wx.EVT_CLOSE, self.OnClose)
		
		font = wx.Font(wx.Font(14, wx.FONTFAMILY_TELETYPE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, faceName="Monospace"))
		
		vsz = wx.BoxSizer(wx.VERTICAL)
		vsz.AddSpacer(20)
		
		for ln in desc:
			st = wx.StaticText(self, wx.ID_ANY, ln)
			st.SetFont(font)
			vsz.Add(st)

		vsz.AddSpacer(20)
			
		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.AddSpacer(20)
		hsz.Add(vsz)
		hsz.AddSpacer(20)

		self.SetSizer(hsz)
		self.Layout()
		self.Fit()
		
	def OnClose(self, _):
		self.EndModal(0)
		
