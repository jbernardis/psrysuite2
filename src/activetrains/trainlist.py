import wx
import logging
import time

from dispatcher.constants import aspectname, aspecttype, aspectprofileindex, profileindex

YardBlocks = [
	"C21", "C31", "C40", "C41", "C42", "C43", "C44", "C50", "C51", "C52", "C53", "C54",
	"H12", "H22", "H30", "H31", "H32", "H33", "H34", "H40", "H41", "H42", "H43",
	"N32", "N42",
	"P1", "P2", "P3", "P4", "P5", "P6", "P7",
	"Y50", "Y51", "Y52", "Y53", "Y81", "Y82", "Y83", "Y84"]


class ActiveTrainsPanel(wx.Panel):
	def __init__(self, parent, lines):
		wx.Panel.__init__(self, parent, wx.ID_ANY)
		self.parent = parent
		
		self.settings = parent.settings
		self.suppressYards =   self.settings.activetrains.suppressyards
		self.suppressUnknown = self.settings.activetrains.suppressunknown
		self.suppressNonAssigned =  self.settings.activetrains.onlyassigned
		self.suppressNonAssignedAndKnown = self.settings.activetrains.onlyassignedorunknown

		self.dccSnifferEnabled = self.settings.dccsniffer.enable
		
		self.resized = False
		self.Bind(wx.EVT_SIZE, self.OnResize)
		self.Bind(wx.EVT_IDLE,self.OnIdle)

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

		vsz.Add(hsz)
				
		vsz.AddSpacer(10)
	
		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.AddSpacer(20)

		self.trCtl = TrainListCtrl(self, self.dccSnifferEnabled, lines*32)
		hsz.Add(self.trCtl, 0, wx.EXPAND)
		self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.DoubleClickTrain, self.trCtl)

		hsz.AddSpacer(20)

		vsz.Add(hsz)
		
		vsz.AddSpacer(10)
		
		self.trCtl.SetSuppressYardTracks(self.suppressYards)
		self.trCtl.SetSuppressUnknown(self.suppressUnknown)
		self.trCtl.SetSuppressNonAssigned(self.suppressNonAssigned)
		self.trCtl.SetSuppressNonAssignedAndKnown(self.suppressNonAssignedAndKnown)

		self.SetSizer(vsz)

	def OnResize(self, evt):
		self.resized = True
		evt.Skip()

	def SetLocos(self, locos):
		self.trCtl.SetLocos(locos)
		
	def OnIdle(self, evt):
		if not self.resized:
			return 
		
		self.resized = False
		self.trCtl.ChangeSize(self.GetSize())

	def DoubleClickTrain(self, evt):
		tr = self.trCtl.GetActiveTrain(evt.Index)
		self.parent.TrainSelected(tr)

	def UpdateTimers(self):
		self.trCtl.UpdateTimers()
		
	def GetLocoInfo(self, loco):
		return self.parent.GetLocoInfo(loco)
		
	def OnSuppressYard(self, _):
		flag = self.cbYardTracks.GetValue()
		self.trCtl.SetSuppressYardTracks(flag)

	def OnSuppressNonAssignedAndKnown(self, _):
		flag = self.cbAssignedOrUnknown.GetValue()
		if flag:
			self.cbUnknown.SetValue(False)
			self.cbAssignedOnly.SetValue(False)

		self.trCtl.SetSuppressNonAssignedAndKnown(flag)
		
	def OnSuppressUnknown(self, _):
		flag = self.cbUnknown.GetValue()
		if flag:
			self.cbAssignedOrUnknown.SetValue(False)
			self.cbAssignedOnly.SetValue(False)

		self.trCtl.SetSuppressUnknown(flag)
		
	def OnSuppressNonAssigned(self, _):
		flag = self.cbAssignedOnly.GetValue()
		if flag:
			self.cbAssignedOrUnknown.SetValue(False)
			self.cbUnknown.SetValue(False)

		self.trCtl.SetSuppressNonAssigned(flag)
				
	def AddTrain(self, tr):
		self.trCtl.AddTrain(tr)
		
	def UpdateTrain(self, trid):
		self.trCtl.UpdateTrain(trid)
		
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


class TrainListCtrl(wx.ListCtrl):
	def __init__(self, parent, dccsnifferenabled, height=160):
		wx.ListCtrl.__init__(self, parent, wx.ID_ANY, size=(1276, height),
							 style=wx.LC_REPORT + wx.LC_VIRTUAL + wx.LC_SINGLE_SEL)
		self.parent = parent
		self.roster = None
		self.trains = {}
		self.locos = {}
		self.order = []
		self.filtered = []
		self.dccsnifferenabled = dccsnifferenabled
		self.lastTick = int(time.time())

		self.suppressYards = True
		self.suppressUnknown = False
		self.suppressNonAssigned = False
		self.suppressNonAssignedAndKnown = False
		self.SetFont(
			wx.Font(wx.Font(16, wx.FONTFAMILY_ROMAN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, faceName="Arial")))

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
		self.SetColumnWidth(3, 110)
		self.InsertColumn(4, "SB")
		self.SetColumnWidth(4, 50)
		self.InsertColumn(5, "Signal")
		self.SetColumnWidth(5, 300)
		self.InsertColumn(6, "Throttle" if self.dccsnifferenabled else "Limit")
		self.SetColumnWidth(6, 100)
		self.InsertColumn(7, "Blocks")
		self.SetColumnWidth(7, 400)
		self.InsertColumn(8, "Time")
		self.SetColumnWidth(8, 80)
		self.SetItemCount(0)

	def ChangeSize(self, sz):
		self.SetSize(sz[0] - 56, sz[1] - 84)
		self.SetColumnWidth(7, sz[0] - 876 - 56)

	def UpdateTimers(self):
		self.lastTick = int(time.time())
		self.RefreshAll()

	def SetRoster(self, roster):
		self.roster = roster

	def SetLocos(self, locos):
		self.locos = locos

	def AddTrain(self, tr):
		logging.debug("Adding train %s" % str(tr))
		trid = tr["iname"]
		self.order.append(trid)
		self.trains[trid] = tr
		self.filterTrains()
		self.SetItemCount(len(self.filtered))
		if len(self.filtered) > 0:
			self.RefreshItems(0, len(self.filtered) - 1)

	def RenameTrain(self, oldName, newName):
		try:
			tx = self.order.index(oldName)
		except ValueError:
			logging.warning("Attempt to delete a non-existent train: %s" % oldName)
			return

		self.order[tx] = newName

		self.trains[newName] = self.trains[oldName]
		del self.trains[oldName]

		self.filterTrains()
		self.SetItemCount(len(self.filtered))
		if len(self.filtered) > 0:
			self.RefreshItems(0, len(self.filtered) - 1)

	def UpdateTrain(self, tr):
		iname = tr["iname"]
		logging.debug("in update train %s: %s" % (iname, str(tr)))
		if iname not in self.trains:
			self.trains[iname] = tr
			self.order.append(iname)
		else:
			self.trains[iname] = tr

		if len(tr["blocks"]) == 0:
			self.RemoveTrain(iname)
		else:
			self.filterTrains()
			self.SetItemCount(len(self.filtered))
			if len(self.filtered) > 0:
				self.RefreshItems(0, len(self.filtered) - 1)

	def RefreshAll(self):
		self.filterTrains()
		self.SetItemCount(len(self.filtered))
		if len(self.filtered) > 0:
			self.RefreshItems(0, len(self.filtered) - 1)

	def RemoveTrain(self, trid):
		try:
			tx = self.order.index(trid)
		except ValueError:
			logging.warning("Attempt to delete a non-existent train: %s" % trid)
			return
		del self.order[tx]
		del self.trains[trid]

		self.filterTrains()
		self.SetItemCount(len(self.filtered))
		if len(self.filtered) > 0:
			self.RefreshItems(0, len(self.filtered) - 1)

	def RemoveAllTrains(self):
		self.trains = {}
		self.order = []
		self.filtered = []
		self.SetItemCount(0)

	def SetSuppressYardTracks(self, flag):
		self.suppressYards = flag

		self.filterTrains()
		self.SetItemCount(len(self.filtered))
		if len(self.filtered) > 0:
			self.RefreshItems(0, len(self.filtered) - 1)

	def SetSuppressUnknown(self, flag):
		self.suppressUnknown = flag
		if flag:
			self.suppressNonAssigned = False
			self.suppressNonAssignedAndKnown = False

		self.filterTrains()
		self.SetItemCount(len(self.filtered))
		if len(self.filtered) > 0:
			self.RefreshItems(0, len(self.filtered) - 1)

	def SetSuppressNonAssigned(self, flag):
		self.suppressNonAssigned = flag
		if flag:
			self.suppressUnknown = False
			self.suppressNonAssignedAndKnown = False

		self.filterTrains()
		self.SetItemCount(len(self.filtered))
		if len(self.filtered) > 0:
			self.RefreshItems(0, len(self.filtered) - 1)

	def SetSuppressNonAssignedAndKnown(self, flag):
		self.suppressNonAssignedAndKnown = flag
		if flag:
			self.suppressUnknown = False
			self.suppressNonAssigned = False

		self.filterTrains()
		self.SetItemCount(len(self.filtered))
		if len(self.filtered) > 0:
			self.RefreshItems(0, len(self.filtered) - 1)

	def filterTrains(self):
		self.filtered = []
		for trid in sorted(self.order, key=self.BuildTrainKey):
			if not self.suppressed(trid):
				self.filtered.append(trid)

	def BuildTrainKey(self, trid):
		tr = self.trains[trid]
		nm = tr["iname"] if tr["rname"] is None else tr["rname"]
		if nm.startswith("??"):
			return "ZZ%s" % nm
		else:
			return "AA%s" % nm

	def suppressed(self, trid):
		tr = self.trains[trid]
		nm = tr["iname"] if tr["rname"] is None else tr["rname"]
		if self.suppressYards:
			blkNms = tr["blocks"]
			allYard = True  # assume all blocks are yard tracks
			for bn in blkNms:
				if bn not in YardBlocks:
					allYard = False
					break
			if allYard:
				return True

		if self.suppressNonAssignedAndKnown:
			if not nm.startswith("??") and tr["engineer"] is None:
				return True

		if self.suppressUnknown and nm.startswith("??"):
			return True

		if self.suppressNonAssigned and tr["engineer"] is None:
			return True

		return False

	def GetActiveTrain(self, index):
		try:
			trid = self.filtered[index]
		except IndexError:
			return None

		return self.trains[trid]

	def OnGetItemText(self, item, col):
		trid = self.filtered[item]
		tr = self.trains[trid]

		if col == 0:
			name = tr["iname"] if tr["rname"] is None else tr["rname"]
			template = tr["template"]
			if template is None or template == name:
				return name
			else:
				return "%s(%s)" % (name, template)

		elif col == 1:
			return "E" if tr["east"] else "W"

		elif col == 2:
			return "" if tr["loco"] is None else tr["loco"]

		elif col == 3:
			nm = tr["engineer"]
			return "" if nm is None else nm

		elif col == 4:
			return u"\u2713" if tr["stopped"] else " "

		elif col == 5:
			sn = tr["signal"]
			if sn is None:
				return ""

			aspect = tr["aspect"]
			aspectType = tr["aspecttype"]
			pastSignal = tr["pastsignal"]
			an = aspectname(aspect, aspectType)
			atn = aspecttype(aspectType)
			return "%s : %s%s (%s)" % (sn, "*" if pastSignal else "", an, atn)

		elif col == 6:
			throttle = tr["throttle"]
			if throttle is None:
				throttle = ""

			if throttle == "":
				throttle = "<>"

			aspect = tr["aspect"]
			aspectType = tr["aspecttype"]
			pastSignal = tr["pastsignal"]
			px = aspectprofileindex(aspect, aspectType)
			loco = tr["loco"]

			trname = tr["iname"] if tr["rname"] is None else tr["rname"]
			locoinfo = self.locos.get(loco, None)
			if locoinfo is None:
				return throttle
			else:
				try:
					limit = locoinfo["prof"][profileindex[px]]
				except (IndexError, KeyError):
					limit = 0

			return "%s - %d" % (throttle, limit) if self.dccsnifferenabled else "%d" % limit

		elif col == 7:
			bl = ", ".join(reversed(tr["blocks"]))
			return bl

		elif col == 8:
			t = tr.get("assigntime", None)
			if t is None:
				return ""

			elapsed = self.lastTick - t
			mins = int(elapsed / 60)
			return "%3d" % mins

		return ""

	def OnGetItemAttr(self, item):
		if item % 2 == 1:
			return self.normalB
		else:
			return self.normalA
