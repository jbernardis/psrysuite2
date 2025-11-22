import wx
import logging

from dispatcher.constants import aspectname, aspecttype

YardBlocks = [
	"C21", "C31", "C40", "C41", "C42", "C43", "C44", "C50", "C51", "C52", "C53", "C54",
	"H12", "H22", "H30", "H31", "H32", "H33", "H34", "H40", "H41", "H42", "H43",
	"N32", "N42",
	"P1", "P2", "P3", "P4", "P5", "P6", "P7",
	"Y50", "Y51", "Y52", "Y53", "Y81", "Y82", "Y83", "Y84" ]

LadderBlocks = [
	"COSSHE", "COSSHW",
	"HOSEE", "HOSEW", "HOSWE", "HOSWW",
	"YOSWYE", "YOSWYW",
	"YOSKL1", "YOSKL2", "YOSKL3", "YOSKL4",
	"POSSP1", "POSSP2", "POSSP3", "POSSP4", "POSSP5"
]

profileIndex = ["stop", "slow", "medium", "fast"]


# class ActiveTrainList:
# 	def __init__(self):
# 		self.trains = {}
# 		self.dlgTrainList = None
# 		self.locoMap = {}
#
# 	def RegenerateLocoMap(self):
# 		self.locoMap = {tr.GetLoco(): tr for tr in self.trains.values() if tr.GetLoco() != "??"}
#
# 	def AddTrain(self, tr):
# 		self.trains[tr.GetName()] = tr
# 		self.RegenerateLocoMap()
# 		if self.dlgTrainList is not None:
# 			self.dlgTrainList.AddTrain(tr)
#
# 	def GetTrain(self, trid):
# 		try:
# 			return self.trains[trid]
# 		except KeyError:
# 			return None
#
# 	def UpdateTrain(self, trid):
# 		if self.dlgTrainList is not None:
# 			self.dlgTrainList.UpdateTrain(trid)
#
# 	def UpdateForSignal(self, sig):
# 		if sig is None:
# 			return
#
# 		if self.dlgTrainList is None:
# 			return
#
# 		signame = sig.GetName()
# 		for trid, tr in self.trains.items():
# 			s, _, _ = tr.GetSignal()
# 			if s and s.GetName() == signame:
# 				self.dlgTrainList.UpdateTrain(trid)
#
# 	def RenameTrain(self, oldName, newName):
# 		self.trains[newName] = self.trains[oldName]
# 		del(self.trains[oldName])
# 		self.RegenerateLocoMap()
# 		if self.dlgTrainList is not None:
# 			self.dlgTrainList.RenameTrain(oldName, newName)
#
# 	def RemoveTrain(self, trid):
# 		del(self.trains[trid])
# 		self.RegenerateLocoMap()
# 		if self.dlgTrainList is not None:
# 			self.dlgTrainList.RemoveTrain(trid)
#
# 	def RemoveAllTrains(self):
# 		self.trains = {}
# 		self.RegenerateLocoMap()
# 		if self.dlgTrainList is not None:
# 			self.dlgTrainList.RemoveAllTrains()
#
# 	def GetAllTrains(self):
# 		if self.dlgTrainList is None:
# 			dlgTrains= {}
# 		else:
# 			dlgTrains = self.dlgTrainList.GetTrainListControl()
# 		return self.trains, dlgTrains
#
# 	def SetLoco(self, tr, loco):
# 		tr.SetLoco(loco)
# 		self.RegenerateLocoMap()
#
# 	def FindTrainByLoco(self, loco):
# 		try:
# 			return self.locoMap[loco]
# 		except:
# 			return None
#
# 	def ShowTrainList(self, parent):
# 		if self.dlgTrainList is None:
# 			self.dlgTrainList = ActiveTrainsDlg(parent, self.HideTrainList)
# 			for tr in self.trains.values():
# 				self.dlgTrainList.AddTrain(tr)
#
# 			self.dlgTrainList.Show()
# 		else:
# 			self.dlgTrainList.Raise()
#
# 	def HideTrainList(self):
# 		if self.dlgTrainList is not None:
# 			self.dlgTrainList.Destroy()
# 			self.dlgTrainList = None
#
# 	def RefreshTrain(self, trid):
# 		if self.dlgTrainList is not None:
# 			self.dlgTrainList.RefreshTrain(trid)
#
# 	def ticker(self):
# 		refresh = False
# 		for tr in self.trains.values():
# 			if tr.AddTime(1):
# 				refresh = True
# 		if refresh and self.dlgTrainList is not None:
# 			self.dlgTrainList.RefreshAll()
#
# 	def GetTrainTimes(self):
# 		trains = []
# 		times = []
# 		for trid, tr in self.trains.items():
# 			tm = tr.GetTime()
# 			if tm is None:
# 				tm = -1
# 			trains.append(trid)
# 			times.append(tm)
# 		return trains, times
#
# 	def forSnapshot(self):
# 		result = {}
# 		for trid, tr in self.trains.items():
# 			if not trid.startswith("??"):
# 				result[trid] = tr.forSnapshot()
#
# 		return result
#
# 	def dump(self):
# 		for tr in self.trains:
# 			self.trains[tr].dump()
#

class ActiveTrainsDlg(wx.Dialog):
	def __init__(self, parent, trains):
		wx.Dialog.__init__(self, parent, wx.ID_ANY, "Active Trains", size=(1500, 1000), style=wx.RESIZE_BORDER|wx.CAPTION|wx.CLOSE_BOX|wx.STAY_ON_TOP)
		self.parent = parent
		self.trains = trains
		self.signals = None
		self.blocks = None
		self.roster = None
		self.Bind(wx.EVT_CLOSE, self.OnClose)
		self.Bind(wx.EVT_SIZE, self.OnResize)
		self.Bind(wx.EVT_IDLE,self.OnIdle)
		
		self.settings = parent.settings
		self.suppressYards =   self.settings.activetrains.suppressyards
		self.suppressUnknown = self.settings.activetrains.suppressunknown
		self.suppressNonATC =  self.settings.activetrains.onlyatc
		self.suppressNonAssigned =  self.settings.activetrains.onlyassigned
		self.suppressNonAssignedAndKnown = self.settings.activetrains.onlyassignedorunknown

		self.dccSnifferEnabled = self.settings.dccsniffer.enable
		
		self.resized = False
		self.shiftKey = False

		vsz = wx.BoxSizer(wx.VERTICAL)	   
		vsz.AddSpacer(10)
		
		hsz = wx.BoxSizer(wx.HORIZONTAL)

		hsz.AddSpacer(30)
		
		self.cbYardTracks = wx.CheckBox(self, wx.ID_ANY, "Suppress Yard Tracks")
		self.cbYardTracks.SetValue(self.suppressYards)
		self.Bind(wx.EVT_CHECKBOX, self.OnSuppressYard, self.cbYardTracks)
		hsz.Add(self.cbYardTracks)

		hsz.AddSpacer(30)
		
		self.cbAssignedOrUnknown = wx.CheckBox(self, wx.ID_ANY, "Show only Assigned or Unknown Trains")
		self.cbAssignedOrUnknown.SetValue(self.suppressNonAssignedAndKnown)
		self.Bind(wx.EVT_CHECKBOX, self.OnSuppressNonAssignedAndKnown, self.cbAssignedOrUnknown)
		hsz.Add(self.cbAssignedOrUnknown)
		
		hsz.AddSpacer(30)
		
		self.cbUnknown = wx.CheckBox(self, wx.ID_ANY, "Show Only Known Trains")
		self.cbUnknown.SetValue(self.suppressUnknown)
		self.Bind(wx.EVT_CHECKBOX, self.OnSuppressUnknown, self.cbUnknown)
		hsz.Add(self.cbUnknown)

		hsz.AddSpacer(30)
		
		self.cbAssignedOnly = wx.CheckBox(self, wx.ID_ANY, "Show only Assigned Trains")
		self.cbAssignedOnly.SetValue(self.suppressNonAssigned)
		self.Bind(wx.EVT_CHECKBOX, self.OnSuppressNonAssigned, self.cbAssignedOnly)
		hsz.Add(self.cbAssignedOnly)

		hsz.AddSpacer(30)

		self.cbATCOnly = wx.CheckBox(self, wx.ID_ANY, "Show only ATC Trains")
		self.cbATCOnly.SetValue(self.suppressNonATC)
		self.Bind(wx.EVT_CHECKBOX, self.OnSuppressNonATC, self.cbATCOnly)
		hsz.Add(self.cbATCOnly)

		hsz.AddSpacer(60)

		self.bRebuild = wx.Button(self, wx.ID_ANY, "Rebuild")
		self.Bind(wx.EVT_BUTTON, self.onBRebuild, self.bRebuild)
		hsz.Add(self.bRebuild)

		hsz.AddSpacer(30)

		vsz.Add(hsz)

		vsz.AddSpacer(10)

		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.AddSpacer(20)

		self.trCtl = TrainListCtrl(self, self.dccSnifferEnabled)
		hsz.Add(self.trCtl)
		self.trCtl.Bind(wx.EVT_LEFT_DOWN, self.ClickLeft)
		self.trCtl.Bind(wx.EVT_RIGHT_DOWN, self.ClickRight)

		hsz.AddSpacer(20)
		
		vsz.Add(hsz)
		
		vsz.AddSpacer(10)
		
		self.trCtl.SetSuppressYardTracks(self.suppressYards)
		
		self.trCtl.SetSuppressUnknown(self.suppressUnknown)
		self.trCtl.SetSuppressNonATC(self.suppressNonATC)
		self.trCtl.SetSuppressNonAssigned(self.suppressNonAssigned)
		self.trCtl.SetSuppressNonAssignedAndKnown(self.suppressNonAssignedAndKnown)

		self.SetSizer(vsz)
		self.Layout()
		self.Fit()
		self.CenterOnScreen()

	def SetSignals(self, sl):
		self.signals = sl

	def SetBlocks(self, bl):
		self.blocks = bl

	def SetRoster(self, roster):
		self.roster = roster
		self.trCtl.SetRoster(roster)

	def GetTrainListControl(self):
		return self.trCtl.GetTrainListControl()

	def ticker(self):
		pass

	def GetSignalAspect(self, sn):
		sig = self.signals.get(sn, None)
		if sig is None:
			return None, None

		return sig.Aspect(), sig.GetAspectName()

	def GetBlockNames(self, bnl):
		result = []
		for bn in bnl:
			blk = self.blocks.get(bn, None)
			if blk is None:
				result.append(bn)
			else:
				result.append(blk.GetRouteDesignator())

		return ", ".join(result)

	def ClickLeft(self, evt):
		pos = evt.GetPosition()
		idxitem = self.trCtl.HitTest(pos)
		if idxitem == wx.NOT_FOUND:
			evt.Skip()
			return

		idx = idxitem[0]
		tr = self.trCtl.GetActiveTrain(idx)
		self.parent.EditTrain(tr, None)
		evt.Skip()
		
	def ClickRight(self, evt):
		pos = evt.GetPosition()
		idxitem = self.trCtl.HitTest(pos)
		if idxitem == wx.NOT_FOUND:
			evt.Skip()
			return

		idx = idxitem[0]
		tr = self.trCtl.GetActiveTrain(idx)
		self.parent.PopupTrainMenu(self, tr, None, pos)
		evt.Skip()

	def GetLocoInfo(self, loco):
		return self.parent.GetLocoInfo(loco)
		
	def OnSuppressYard(self, _):
		flag = self.cbYardTracks.GetValue()
		self.trCtl.SetSuppressYardTracks(flag)
		
	def OnSuppressNonATC(self, _):
		flag = self.cbATCOnly.GetValue()
		if flag:
			self.cbUnknown.SetValue(False)
			self.cbAssignedOnly.SetValue(False)
			self.cbAssignedOrUnknown.SetValue(False)
		self.trCtl.SetSuppressNonATC(flag)

	def OnSuppressNonAssignedAndKnown(self, _):
		flag = self.cbAssignedOrUnknown.GetValue()
		if flag:
			self.cbUnknown.SetValue(False)
			self.cbAssignedOnly.SetValue(False)
			self.cbATCOnly.SetValue(False)
		self.trCtl.SetSuppressNonAssignedAndKnown(flag)
		
	def OnSuppressUnknown(self, _):
		flag = self.cbUnknown.GetValue()
		if flag:
			self.cbAssignedOrUnknown.SetValue(False)
			self.cbAssignedOnly.SetValue(False)
			self.cbATCOnly.SetValue(False)
		self.trCtl.SetSuppressUnknown(flag)
		
	def OnSuppressNonAssigned(self, _):
		flag = self.cbAssignedOnly.GetValue()
		if flag:
			self.cbAssignedOrUnknown.SetValue(False)
			self.cbUnknown.SetValue(False)
			self.cbATCOnly.SetValue(False)
		self.trCtl.SetSuppressNonAssigned(flag)

	def onBRebuild(self, _):
		self.parent.RebuildActiveTrainList()

	def AddTrain(self, tr):
		self.trCtl.AddTrain(tr)
		
	def UpdateTrain(self, tr):
		self.trCtl.UpdateTrain(tr)
		
	def RefreshTrain(self, trid):
		self.trCtl.UpdateTrain(trid)
		
	def RefreshAll(self):
		self.trCtl.RefreshAll()
		
	def RenameTrain(self, oldName, newName):
		self.trCtl.RenameTrain(oldName, newName)
		
	def RemoveTrain(self, trid):
		self.trCtl.RemoveTrain(trid)
		
	def RemoveAllTrains(self):
		self.trCtl.RemoveAllTrains()
		
	def OnResize(self, evt):
		self.resized = True
		
	def OnIdle(self, evt):
		if not self.resized:
			return 
		
		self.resized = False
		self.trCtl.ChangeSize(self.GetSize())

	def OnClose(self, _):
		self.Hide()


class TrainListCtrl(wx.ListCtrl):
	def __init__(self, parent, dccsnifferenabled, height=160):
		wx.ListCtrl.__init__(self, parent, wx.ID_ANY, size=(1366, height), style=wx.LC_REPORT + wx.LC_VIRTUAL + wx.LC_SINGLE_SEL)
		self.parent = parent
		self.roster = None
		self.trains = {}
		self.order = []
		self.filtered = []
		self.dccsnifferenabled = dccsnifferenabled
		
		self.suppressYards = True
		self.suppressUnknown = False
		self.suppressNonATC = False
		self.suppressNonAssigned = False		
		self.suppressNonAssignedAndKnown = False
		self.SetFont(wx.Font(wx.Font(16, wx.FONTFAMILY_ROMAN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, faceName="Arial")))
		
		self.normalA = wx.ItemAttr()
		self.normalB = wx.ItemAttr()
		self.normalA.SetBackgroundColour(wx.Colour(225, 255, 240))
		self.normalB.SetBackgroundColour(wx.Colour(138, 255, 197))

		self.InsertColumn(0, "Train")
		self.SetColumnWidth(0, 100)
		self.InsertColumn(1, "E/W")
		self.SetColumnWidth(1, 56)
		self.InsertColumn(2, "Loco")
		self.SetColumnWidth(2, 80)
		self.InsertColumn(3, "Engineer")
		self.SetColumnWidth(3, 100)
		self.InsertColumn(4, "ATC")
		self.SetColumnWidth(4, 50)
		self.InsertColumn(5, "AR")
		self.SetColumnWidth(5, 50)
		self.InsertColumn(6, "SB")
		self.SetColumnWidth(6, 50)
		self.InsertColumn(7, "Signal")
		self.SetColumnWidth(7, 300)
		self.InsertColumn(8, "Throttle" if self.dccsnifferenabled else "Limit")
		self.SetColumnWidth(8, 100)
		self.InsertColumn(9, "Blocks")
		self.SetColumnWidth(9, 400)
		self.InsertColumn(10, "Time")
		self.SetColumnWidth(10, 80)
		self.SetItemCount(0)
		
	def ChangeSize(self, sz):
		self.SetSize(sz[0]-56, sz[1]-84)
		self.SetColumnWidth(9, sz[0]-966-56)

	def SetRoster(self, roster):
		self.roster = roster
		
	def AddTrain(self, tr):
		nm = tr.GetName()
		if nm in self.order:
			logging.warning("Attempt to add a duplicate train: %s" % nm)
			return 
		
		self.trains[nm] = tr
		self.order.append(nm)

		self.filterTrains()	
		self.SetItemCount(len(self.filtered))	
		if len(self.filtered) > 0:
			self.RefreshItems(0, len(self.filtered)-1)

	def GetTrainListControl(self):
		return {
			"trains": list(self.trains.keys()),
			"trainct": len(self.trains),

			"order": self.order.copy(),
			"orderct": len(self.order),

			"filter": self.filtered.copy(),
			"filterct": len(self.filtered)
		}
		
	def RenameTrain(self, oldName, newName):
		try:
			tx = self.order.index(oldName)
		except ValueError:
			logging.warning("Attempt to delete a non-existent train: %s" % oldName)
			return 
		
		self.order[tx] = newName
		
		self.trains[newName] = self.trains[oldName]
		del(self.trains[oldName])
		
		self.filterTrains()	
		self.SetItemCount(len(self.filtered))	
		if len(self.filtered) > 0:
			self.RefreshItems(0, len(self.filtered)-1)
		
	def UpdateTrain(self, tr):
		iname = tr.IName()
		if iname not in self.trains:
			self.trains[iname] = tr
			self.order.append(iname)

		if tr.BlockCount() == 0:
			self.RemoveTrain(iname)
		else:
			self.filterTrains()
			self.SetItemCount(len(self.filtered))
			if len(self.filtered) > 0:
				self.RefreshItems(0, len(self.filtered)-1)
			
	def RefreshAll(self):
		self.filterTrains()	
		self.SetItemCount(len(self.filtered))	
		if len(self.filtered) > 0:
			self.RefreshItems(0, len(self.filtered)-1)
		
	def RemoveTrain(self, trid):
		try:
			tx = self.order.index(trid)
		except ValueError:
			logging.warning("Attempt to delete a non-existent train: %s" % trid)
			return 
		del(self.order[tx])
		del(self.trains[trid])

		self.filterTrains()	
		self.SetItemCount(len(self.filtered))	
		if len(self.filtered) > 0:
			self.RefreshItems(0, len(self.filtered)-1)
		
	def RemoveAllTrains(self):
		self.trains = {}
		self.order = []
		self.filtered = []
		self.SetItemCount(len(self.filtered))	
		
	def SetSuppressYardTracks(self, flag):
		self.suppressYards = flag

		self.filterTrains()	
		self.SetItemCount(len(self.filtered))
		if len(self.filtered) > 0:
			self.RefreshItems(0, len(self.filtered)-1)
		
	def SetSuppressUnknown(self, flag):
		self.suppressUnknown = flag
		if flag:
			self.suppressNonATC = False
			self.suppressNonAssigned = False
			self.suppressNonAssignedAndKnown = False

		self.filterTrains()
		self.SetItemCount(len(self.filtered))
		if len(self.filtered) > 0:
			self.RefreshItems(0, len(self.filtered)-1)
		
	def SetSuppressNonATC(self, flag):
		self.suppressNonATC = flag
		if flag:
			self.suppressUnknown = False
			self.suppressNonAssigned = False
			self.suppressNonAssignedAndKnown = False

		self.filterTrains()	
		self.SetItemCount(len(self.filtered))	
		if len(self.filtered) > 0:
			self.RefreshItems(0, len(self.filtered)-1)
		
	def SetSuppressNonAssigned(self, flag):
		self.suppressNonAssigned = flag
		if flag:
			self.suppressUnknown = False
			self.suppressNonATC = False
			self.suppressNonAssignedAndKnown = False

		self.filterTrains()	
		self.SetItemCount(len(self.filtered))
		if len(self.filtered) > 0:
			self.RefreshItems(0, len(self.filtered)-1)

	def SetSuppressNonAssignedAndKnown(self, flag):
		self.suppressNonAssignedAndKnown = flag
		if flag:
			self.suppressUnknown = False
			self.suppressNonATC = False
			self.suppressNonAssigned = False

		self.filterTrains()	
		self.SetItemCount(len(self.filtered))	
		if len(self.filtered) > 0:
			self.RefreshItems(0, len(self.filtered)-1)
			
	def filterTrains(self):
		self.filtered = []
		for trid in sorted(self.order, key=self.BuildTrainKey):
			if not self.suppressed(trid):
				self.filtered.append(trid)

	def BuildTrainKey(self, trid):
		tr = self.trains[trid]
		nm = tr.Name()
		if nm.startswith("??"):
			return "ZZ%s" % nm
		else:
			return "AA%s" % nm

	def suppressed(self, trid):
		tr = self.trains[trid]
		nm = tr.Name()
		if self.suppressYards:
			blkNms = tr.Blocks()
			allYard = True # assume all blocks are yard tracks
			for bn in blkNms:
				if bn not in YardBlocks:
					allYard = False
					break
			if allYard:
				return True
			
		if self.suppressNonAssignedAndKnown:
			if not nm.startswith("??") and tr.Engineer() is None:
				return True
			
		if self.suppressUnknown and nm.startswith("??"):
			return True
		
		if self.suppressNonAssigned and tr.Engineer() is None:
			return True

		if self.suppressNonATC and not tr.ATC():
			return True
					
		return False
	
	def GetActiveTrain(self, index):
		try:
			trid = self.filtered[index]
		except:
			return None
		
		return self.trains[trid]

	def OnGetItemText(self, item, col):
		trid = self.filtered[item]
		tr = self.trains[trid]
		
		if col == 0:
			return tr.Name()
		
		elif col == 1:
			return "E" if tr.IsEast() else "W"
		
		elif col == 2:
			return tr.Loco()
		
		elif col == 3:
			nm = "ATC" if tr.ATC() else tr.Engineer()
			return "" if nm is None else nm
		
		elif col == 4:
			return u"\u2713" if tr.ATC() else " "
		
		elif col == 5:
			return u"\u2713" if tr.AR() else " "
		
		elif col == 6:
			return u"\u2713" if tr.Stopped() else " "
		
		elif col == 7:
			sn = tr.Signal()
			if sn is None:
				return ""

			aspect, aspectType, pastSignal = tr.Aspect()
			if aspect is None:
				aspect, aspectName = self.parent.GetSignalAspect(sn)
				if aspect is None:
					return ""

				return "%s : %s" % (sn, aspectName)
			else:
				an = aspectname(aspect, aspectType)
				atn = aspecttype(aspectType)
				return "%s : %s%s (%s)" % (sn, "*" if pastSignal else "", an, atn)

		elif col == 8:
			return "Thr"

		elif col == 88:
			throttle = tr.GetThrottle()
			if throttle is None:
				throttle = ""
				
			if throttle == "":
				throttle = "<>"
			
			sig, asp, fasp = tr.GetSignal()
			aspect = fasp if fasp is not None else asp
			if sig is None or aspect is None:
				throttlelimit = 0
			else:
				throttlelimit = sig.GetAspectProfileIndex(aspect)
			loco = tr.GetLoco()
			locoinfo = self.parent.GetLocoInfo(loco)
			if locoinfo is None:
				limit = 0
			else:
				try:
					limit = locoinfo["prof"][profileIndex[throttlelimit]]
				except (IndexError, KeyError):
					limit = 0

			return "%s - %d" % (throttle, limit) if self.dccsnifferenabled else "%d" % limit
		
		elif col == 9:
			bl = self.parent.GetBlockNames(reversed(tr.Blocks()))
			return bl
		
		elif col == 10:
			return "time"

		elif col == 1010:
			t = tr.GetTime()
			if t is None:
				return ""
			
			mins = int(t / 60)
			secs = t % 60
			return "%2d:%02d" % (mins, secs)

		return ""

	def OnGetItemAttr(self, item):	
		if item % 2 == 1:
			return self.normalB
		else:
			return self.normalA
