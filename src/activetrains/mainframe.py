import wx
import wx.lib.newevent

import os
import sys
import json
import logging
from subprocess import Popen

from dispatcher.train import Train, CopyTrainReferences
from activetrains.trainlist import ActiveTrainList
from dispatcher.listener import Listener
from dispatcher.rrserver import RRServer
from dispatcher.constants import aspectname, aspecttype, aspectprofileindex, RegAspects, REPLACE
from dispatcher.block import formatRouteDesignator

(DeliveryEvent, EVT_DELIVERY) = wx.lib.newevent.NewEvent() 
(DisconnectEvent, EVT_DISCONNECT) = wx.lib.newevent.NewEvent() 

BTNDIM = (80, 23) if sys.platform.lower() == "win32" else (100, 23)
MAXSTEPS = 9

ignoredCommands = ["breaker", "fleet", "control", "siglever", "signallock",
				"blockclear", "blockdir", "turnout", "turnoutlock", "clock"]

class Block:
	def __init__(self, name):
		self.name = name
		self.east = True
		self.train = None
		self.isOS = False
		self.route = None
		
	def GetName(self):
		return self.name
	
	def GetTrain(self):
		return self.train
	
	def SetTrain(self, tr):
		self.train = tr
	
	def SetEast(self, flag=True):
		self.east = flag

	def SetRoute(self, rtname):
		self.route = rtname
		self.isOS = True

	def IsOS(self):
		return self.isOS

	def GetRouteDesignator(self):
		if self.route is None:
			return None
		else:
			return formatRouteDesignator(self.route)

		
class Signal:
	def __init__(self, name):
		self.name = name
		self.aspect = 0
		self.frozenAspect = None
		self.aspectType = RegAspects
		self.train = None
		
	def GetName(self):
		return self.name
	
	def GetAspect(self):
		return self.aspect
	
	def SetAspect(self, aspect):
		self.aspect = aspect
		
	def GetFrozenAspect(self):
		return self.frozenAspect
	
	def SetFrozenAspect(self, fa):
		self.frozenAspect = fa
		
	def SetAspectType(self, atype):
		self.aspectType = atype
		
	def GetAspectProfileIndex(self, aspect=None):
		asp = self.aspect if aspect is None else aspect
		return aspectprofileindex(asp, self.aspectType)
		
	def GetAspectType(self):
		return self.aspectType
	
	def GetAspectName(self, aspect=None):
		if aspect is None:
			aspect = self.aspect
		return "%s (%s)" % (aspectname(aspect, self.aspectType), aspecttype(self.aspectType))
	
	def SetTrain(self, tr):
		self.train = tr
		
	def GetTrain(self):
		return self.train

class MainFrame(wx.Frame):
	def __init__(self, settings):
		wx.Frame.__init__(self, None, size=(1500, 800), style=wx.DEFAULT_FRAME_STYLE)
		self.listener = None
		self.sessionid = None
		self.subscribed = False
		
		# self.activeTrains = ActiveTrainList()
		self.trains = {}
		self.trainList = {}
		self.blocks = {}
		self.signals = {}
			
		self.settings = settings

		self.rrServer = RRServer()
		self.rrServer.SetServerAddress(self.settings.ipaddr, self.settings.serverport)
		self.CreateDispatchTable()
		
		self.SetBackgroundColour(wx.Colour(200, 200, 200))

			
		logging.info("active train list process starting")
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
		
		self.ActiveTrainsPanel = self.activeTrains.CreateTrainListPanel(self, self.settings.activetrains.lines)
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
		self.ticker.Start(1000)
		
		self.splash()
		
	def onTicker(self, _):
		self.activeTrains.ticker()
		
	def TrainSelected(self, tr):
		trid = tr.GetName()
		loco = tr.GetLoco()
		try:
			info = self.trainList[trid]
		except KeyError:
			return 
		
		self.ShowTrainDesc(tr, loco, info)
		
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
		
	def GetLocoInfo(self, loco):
		try:
			return self.locoList[loco]
		except KeyError:
			return None

	def splash(self):
		splashExec = os.path.join(os.getcwd(), "splash", "main.py")
		pid = Popen([sys.executable, splashExec]).pid
		logging.debug("displaying splash screen as PID %d" % pid)
		
	def ShowTitle(self):
		self.SetTitle("Active Train Display - %s" % ("NOT connected" if not self.subscribed else "connected" if self.sessionid is None else ("Session ID %d" % self.sessionid)))

	def NewTrain(self):
		tr = Train(None)
		name, _ = tr.GetNameAndLoco()
		self.trains[name] = tr
		self.activeTrains.AddTrain(tr)
		return tr
	

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
			self.activeTrains.RemoveAllTrains()
			self.trains = {}
			self.activeTrains.EnableTrainListPanel(False)

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
			self.activeTrains.EnableTrainListPanel(True)
		self.ShowTitle()

	def RetrieveData(self):
		locos = self.Get("getlocos", {})
		if locos is None:
			logging.error("Unable to retrieve locos")
			locos = {}
			
		self.locoList = locos

		trains = self.Get("gettrains", {})
		if trains is None:
			logging.error("Unable to retrieve trains")
			trains = {}
			
		CopyTrainReferences(trains)
		self.trainList = trains

		engineers = self.Get("getengineers", {})
		if engineers is None:
			logging.error("Unable to retrieve engineers")
			engineers = []
			
		self.engineerList = engineers

	def OnRefresh(self, _):
		self.DoRefresh()
		
	def DoRefresh(self):
		self.activeTrains.RemoveAllTrains()
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
			"block":			self.DoCmdBlock,
			"signal":			self.DoCmdSignal,
			"trainsignal":		self.DoCmdTrainSignal,
			"settrain":			self.DoCmdSetTrain,
			"deletetrain":		self.DoCmdDeleteTrain,
			"setroute":			self.DoCmdSetRoute,
			"assigntrain":		self.DoCmdAssignTrain,
			"relay":			self.DoCmdRelay,
			"dccspeed":			self.DoCmdDCCSpeed,
			"dccspeeds":		self.DoCmdDCCSpeeds,
			"atc":				self.DoCmdATC,
			"atcstatus":		self.DoCmdATCStatus,
			"ar":				self.DoCmdAR,
			"sessionID":		self.DoCmdSessionID,
			"end":				self.DoCmdEnd,
			"traintimesreport":	self.DoCmdTrainTimesReport,
			"trainblockorder":	self.DoCmdTrainBlockOrder,
		}

	def onDeliveryEvent(self, evt):
		for cmd, parms in evt.data.items():
			if cmd not in ignoredCommands:
				try:
					handler = self.dispatch[cmd]
				except KeyError:
					logging.error("Unknown command: %s" % cmd)
				
				else:
					logging.info("Inbound command: %s: %s" % (cmd, parms))
					handler(parms)
					
	def DoCmdBlock(self, parms):
		for blk in parms:
			blkName = blk["name"]
			if blkName not in self.blocks:
				self.blocks[blkName] = Block(blkName)
					
	def DoCmdSignal(self, parms):
		for sig in parms:
			sigName = sig["name"]
			aspect = sig["aspect"]
			try:
				frozenAspect = sig["frozenaspect"]
			except KeyError:
				frozenAspect = None
			try:
				aspectType = sig["aspecttype"]
			except KeyError:
				aspectType = RegAspects
				
			if sigName not in self.signals:
				s = Signal(sigName)
				self.signals[sigName] = s
			else:
				s = self.signals[sigName]
				
			s.SetAspect(aspect)
			s.SetAspectType(aspectType)
			s.SetFrozenAspect(frozenAspect)
			self.activeTrains.UpdateForSignal(s)

	def DoCmdTrainSignal(self, parms):							
		trid = parms["train"]			
		signm = parms["signal"]
		
		try:
			tr = self.trains[trid]
		except:
			tr = None
			
		try:
			sig = self.signals[signm]
		except:
			sig  = None
			
		if tr is not None and sig is not None:
			tr.SetSignal(sig)
			sig.SetTrain(tr)
			self.activeTrains.UpdateTrain(trid)
		elif tr is None and sig is not None:
			sig.SetTrain(None)
		elif tr is not None and sig is None:
			tr.SetSignal(None)
			self.activeTrains.UpdateTrain(trid)

	def DoCmdTrainBlockOrder(self, parms):
		for p in parms:
			trid = p["name"]
			blocks = p["blocks"]
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
				self.activeTrains.UpdateTrain(trid)


	def DoCmdSetRoute(self, parms):
		for p in parms:
			blknm = p["block"]
			rtnm = p["route"]
			try:
				block = self.blocks[blknm]
			except:
				block = None

			if block is None:
				logging.error("Unable to find block %s from setroute message" % blknm)
			else:
				block.SetRoute(rtnm)

	def DoCmdDeleteTrain(self, parms):
		try:
			trid = parms["name"]
		except KeyError:
			trid = None

		if trid is None:
			return

		try:
			del (self.trains[trid])
		except:
			logging.warning("can't delete train %s from train list" % trid)
		try:
			self.activeTrains.RemoveTrain(trid)
		except:
			logging.warning("can't delete train %s from active train list" % trid)

	def DoCmdSetTrain(self, parms):
		blocks = parms["blocks"]
		name = parms["name"]
		loco = parms["loco"]
		try:
			east = parms["east"]
		except KeyError:
			east = None

		try:
			action = parms["action"]
		except KeyError:
			action = REPLACE

		try:
			nameonly = parms["nameonly"]
		except KeyError:
			nameonly = False

		for block in blocks:
			blk = self.blocks[block]
			tr = blk.GetTrain()
			if name is None:
				if tr:
					tr.RemoveFromBlock(blk)
					self.activeTrains.UpdateTrain(tr.GetName())
					if tr.IsInNoBlocks():
						trid = tr.GetName()
						try:
							self.activeTrains.RemoveTrain(trid)
							del(self.trains[trid])
						except:
							logging.warning("can't delete train %s from train list" % trid)

				delList = []
				for trid, tr in self.trains.items():
					if tr.IsInBlock(blk):
						tr.RemoveFromBlock(blk)
						self.activeTrains.UpdateTrain(tr.GetName())
						if tr.IsInNoBlocks():
							delList.append([trid, tr])

				for trid, tr in delList:
					try:
						self.activeTrains.RemoveTrain(trid)
						del(self.trains[trid])
					except:
						logging.warning("can't delete train %s from train list" % trid)

				continue

			oldName = None
			if tr:
				oldName = tr.GetName()
				if oldName and oldName != name:
					if name in self.trains:
						# merge the two trains under the new "name"
						if not oldName.startswith("??"):
							pass

						try:
							bl = self.trains[oldName].GetBlockList()
						except:
							bl = {}
						for blk in bl.values():
							self.trains[name].AddToBlock(blk, action)
						self.activeTrains.UpdateTrain(name)
					else:
						tr.SetName(name)
						if name in self.trainList:
							tr.SetEast(self.trainList[name]["eastbound"])

						self.trains[name] = tr
						self.activeTrains.RenameTrain(oldName, name)
						#self.Request({"renametrain": { "oldname": oldName, "newname": name, "east": "1" if tr.GetEast() else "0"}})

					try:
						self.activeTrains.RemoveTrain(oldName)
					except:
						logging.warning("can't delete train %s from train list" % oldName)

					try:
						del(self.trains[oldName])
					except:
						logging.warning("can't delete train %s from train list" % oldName)

			try:
				# trying to find train in existing list
				tr = self.trains[name]
				if oldName and oldName == name:
					if east is not None:
						tr.SetEast(east)
						blk.SetEast(east)
				else:
					e = tr.GetEast()
					blk.SetEast(e) # block takes on direction of the train if known
			except KeyError:
				# not there - create a new one")
				tr = Train(name)
				self.trains[name] = tr
				self.activeTrains.AddTrain(tr)
				# new train takes on direction from the settrain command
				tr.SetEast(east)
				# and block is set to the same thing
				blk.SetEast(east)

			tr.AddToBlock(blk, action)
			if action == REPLACE:
				tr.SetBlockOrder(blocks)

			blk.SetTrain(tr)

			if loco:
				self.activeTrains.SetLoco(tr, loco)

			self.activeTrains.UpdateTrain(tr.GetName())
						
	def DoCmdAssignTrain(self, parms):	
		for p in parms:
			train = p["train"]
			try:
				engineer = p["engineer"]
			except KeyError:
				engineer = None
				
			try:
				tr = self.trains[train]
			except:
				logging.error("Unknown train name (%s) in assigntrain message" % train)
				return
				
			tr.SetEngineer(engineer)
			self.activeTrains.UpdateTrain(train)
			
	def DoCmdRelay(self, parms):
		for p in parms:
			relay = p["name"]
			if relay.endswith(".srel"):
				block = relay[:-5]
			else:
				block = relay
				
			status = int(p["state"])
			
			try:
				blk = self.blocks[block]
			except KeyError:
				return 
			
			tr = blk.GetTrain()
			if tr is None:
				return 
			
			tr.SetSBActive(status == 1)
			train = tr.GetName()
			self.activeTrains.UpdateTrain(train)
	
	def DoCmdDCCSpeed(self, parms):		
		for p in parms:
			try:
				loco = p["loco"]
			except:
				loco = None
			
			try:
				speed = p["speed"]
			except:
				speed = "0"
				
			try:
				speedtype = p["speedtype"]
			except:
				speedtype = None
				
			if loco is None:
				return 
			
			tr = self.activeTrains.FindTrainByLoco(loco)
			if tr is not None:
				tr.SetThrottle(speed, speedtype)
				self.activeTrains.UpdateTrain(tr.GetName())

	def DoCmdDCCSpeeds(self, parms):
		for loco, spinfo in parms.items():
			tr = self.activeTrains.FindTrainByLoco(loco)
			if tr is not None:
				tr.SetThrottle(spinfo[0], spinfo[1])
				self.activeTrains.UpdateTrain(tr.GetName())

	def DoCmdATC(self, parms):
		action = parms["action"][0]
		if action not in [ "add", "remove" ]:
			return 
		
		train = parms["train"][0]
		
		try:
			tr = self.trains[train]
		except:
			logging.error("Unknown train name (%s) in atc message" % train)
			return
		
		tr.SetATC(action == "add")
		self.activeTrains.UpdateTrain(train)
		
	def DoCmdATCStatus(self, parms):
		action = parms["action"][0]
		if action != "reject":
			return 
		
		train = parms["train"][0]
		
		try:
			tr = self.trains[train]
		except:
			logging.error("Unknown train name (%s) in atcstatus message" % train)
			return
		
		tr.SetATC(False)
		self.activeTrains.UpdateTrain(train)
				
	def DoCmdAR(self, parms):
		action = parms["action"][0]
		if action not in [ "add", "remove" ]:
			return 

		train = parms["train"][0]
		
		try:
			tr = self.trains[train]
		except:
			logging.error("Unknown train name (%s) in ar message" % train)
			return
		
		tr.SetAR(action == "add")
		self.activeTrains.UpdateTrain(train)

	def DoCmdSessionID(self, parms):
		self.sessionid = int(parms)
		logging.info("connected to railroad server with session ID %d" % self.sessionid)
		self.Request({"identify": {"SID": self.sessionid, "function": "DISPLAY"}})
		self.DoRefresh()
		self.ShowTitle()

	def DoCmdEnd(self, parms):
		if parms["type"] == "layout":
			self.Request({"refresh": {"SID": self.sessionid, "type": "trains"}})

		elif parms["type"] == "trains":
			self.Request({"traintimesrequest": {}})

	def DoCmdTrainTimesReport(self, parms):
		try:
			trains = parms["trains"]
			times = parms["times"]
		except KeyError:
			trains = None

		if trains is None:
			return

		for trid, tm in zip(trains, times):
			try:
				tr = self.trains[trid]
			except:
				tr = None
			if tr:
				tm = int(tm)
				tr.SetTime(None if tm == -1 else tm)
			

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
		
		self.activeTrains.RemoveAllTrains()
		self.trains = {}
		self.activeTrains.EnableTrainListPanel(False)
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
		
