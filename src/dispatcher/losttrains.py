import wx
import os
import logging

BSIZE = (100, 26)


class LostTrains:
	def __init__(self, frame):
		self.frame = frame
		self.trains = {}
		self.branchLineW = None
		self.branchLineE = None
		self.dbg = self.frame.GetDebugFlags()

	def Add(self, train, loco, engineer, east, block, route):
		if train.startswith("??"):
			return False

		if block == "F10":  # and not east:
			self.branchLineW = (train, loco, engineer, east, block, route)
			if self.dbg.identifytrain:
				self.frame.DebugMessage("Recording train %s as branch line west" % train)
		elif block == "R10":  # and east:
			self.branchLineE = (train, loco, engineer, east, block, route)
			if self.dbg.identifytrain:
				self.frame.DebugMessage("Recording train %s as branch line east" % train)
		# elif block == "F10" and self.dbg.identifytrain:
		# 	self.frame.DebugMessage("NOT recording train %s as branch line west because of opposite direction" % train)
		# elif block == "R10" and self.dbg.identifytrain:
		# 	self.frame.DebugMessage("NOT recording train %s as branch line east because of opposite direction" % train)

		self.trains[train] = (loco, engineer, east, block, route)
		return True

	def GetBranchLineTrain(self, blknm, east):
		blt = self.branchLineE if blknm == "F10" else self.branchLineW
		if blt is not None and self.dbg.identifytrain:
			self.frame.DebugMessage("Returning train %s as branch line from block %s" % (blt[0], blknm))

		return blt

	def ClearBranchLine(self, trid):
		if self.branchLineE is not None and self.branchLineE[0] == trid:
			if self.dbg.identifytrain:
				self.frame.DebugMessage("Clearing train %s as branch line east" % trid)
			self.branchLineE = None
			self.Remove(trid)

		elif self.branchLineW is not None and self.branchLineW[0] == trid:
			if self.dbg.identifytrain:
				self.frame.DebugMessage("Clearing train %s as branch line west" % trid)
			self.branchLineW = None
			self.Remove(trid)

	def Remove(self, train):
		if self.branchLineE is not None and self.branchLineE[0] == train:
			if self.dbg.identifytrain:
				self.frame.DebugMessage("Removing train %s as branch line east" % train)
			self.branchLineE = None
		if self.branchLineW is not None and self.branchLineW[0] == train:
			self.branchLineW = None
			if self.dbg.identifytrain:
				self.frame.DebugMessage("Removing train %s as branch line west" % train)

		try:
			del self.trains[train]
		except KeyError:
			return False
			
		return True
	
	def GetTrain(self, tid):
		if tid is None or tid not in self.trains:
			return None
		
		return self.trains[tid]
	
	def GetList(self):
		return [(train, info[0], info[1], info[2], info[3], info[4]) for train, info in self.trains.items()]
	
	def Count(self):
		return len(self.trains)


class LostTrainsDlg(wx.Dialog):
	def __init__(self, parent, lostTrains):
		wx.Dialog.__init__(self, parent, wx.ID_ANY, "")
		self.parent = parent
		self.lt = lostTrains
		self.Bind(wx.EVT_CLOSE, self.OnClose)
		self.pendingDeletions = []
		self.trainOrder = []
		self.trainMap = {}
		self.trainList = self.lt.GetList()
		self.SetArrays()
		self.chosenTrain = None

		self.SetTitle("Lost Trains")

		vsz = wx.BoxSizer(wx.VERTICAL)
		vsz.AddSpacer(20)

		self.ch = LostTrainsCtrl(self)
		self.ch.SetData(self.trainOrder, self.trainList, self.trainMap)
		vsz.Add(self.ch, 0, wx.ALIGN_CENTER_HORIZONTAL)

		vsz.AddSpacer(20)

		hsz = wx.BoxSizer(wx.HORIZONTAL)

		self.bOK = wx.Button(self, wx.ID_ANY, "Select", size=BSIZE)
		self.bOK.SetToolTip("Perform pending removals and return with the checked train as the selection")
		self.Bind(wx.EVT_BUTTON, self.OnBOK, self.bOK)
		hsz.Add(self.bOK)
		self.bOK.Enable(False)

		hsz.AddSpacer(20)

		self.bRemove = wx.Button(self, wx.ID_ANY, "Remove", size=BSIZE)
		self.bRemove.SetToolTip(
			"Mark the checked trains for removal.  Removal is pending until the dialog box is exited")
		self.Bind(wx.EVT_BUTTON, self.OnBRemove, self.bRemove)
		hsz.Add(self.bRemove)
		self.bRemove.Enable(False)

		hsz.AddSpacer(20)

		self.bExit = wx.Button(self, wx.ID_ANY, "Exit", size=BSIZE)
		self.bExit.SetToolTip("Perform pending removals and exit the dialog box without selecting a train")
		self.Bind(wx.EVT_BUTTON, self.OnBExit, self.bExit)
		hsz.Add(self.bExit)

		hsz.AddSpacer(20)

		self.bCancel = wx.Button(self, wx.ID_ANY, "Cancel", size=BSIZE)
		self.bCancel.SetToolTip("Exit the dialog box without doing pending removals and without selecting a train")
		self.Bind(wx.EVT_BUTTON, self.OnBCancel, self.bCancel)
		hsz.Add(self.bCancel)

		vsz.Add(hsz, 0, wx.ALIGN_CENTER_HORIZONTAL)

		vsz.AddSpacer(20)

		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.AddSpacer(20)
		hsz.Add(vsz)
		hsz.AddSpacer(20)

		self.SetSizer(hsz)
		self.Layout()
		self.Fit()
		self.CenterOnScreen()

	def SetArrays(self):
		self.trainOrder = sorted([t[0] for t in self.trainList if t[0] not in self.pendingDeletions])
		self.trainMap = {t[0]: t for t in self.trainList if t[0] not in self.pendingDeletions}

	def DoPendingRemoval(self):
		for tname in self.pendingDeletions:
			self.lt.Remove(tname)
		self.pendingDeletions = []

	def reportSelection(self, tx, doubleclick=False):
		if tx is None or tx == wx.NOT_FOUND:
			return

		checked = self.ch.GetChecked()
		if len(checked) > 1:
			self.bRemove.Enable(True)
			self.bOK.Enable(False)
		elif len(checked) == 1:
			self.bRemove.Enable(True)
			self.bOK.Enable(True)
		else:
			self.bRemove.Enable(False)
			self.bOK.Enable(False)

	def OnBRemove(self, _):
		checked = self.ch.GetChecked()
		self.pendingDeletions.extend([self.trainOrder[i] for i in checked])
		self.SetArrays()
		self.ch.SetData(self.trainOrder, self.trainList, self.trainMap)
		self.bOK.Enable(False)
		self.bRemove.Enable(False)

	def OnBOK(self, _):
		self.DoPendingRemoval()
		checked = self.ch.GetChecked()
		tx = checked[0]
		self.chosenTrain = self.trainOrder[tx]
		self.EndModal(wx.ID_OK)

	def OnBExit(self, _):
		# perform pendingg deletions and exit without selecting a lost train
		self.DoPendingRemoval()
		self.chosenTrain = None
		self.EndModal(wx.ID_CANCEL)

	def OnBCancel(self, _):
		if len(self.pendingDeletions) > 0:
			dlg = wx.MessageDialog(self, "Pending removals will be lost if you continue\nPress Yes to continue or No to return", "Pending Deletions",
				wx.YES_NO | wx.NO_DEFAULT | wx.ICON_WARNING)
			rc = dlg.ShowModal()
			dlg.Destroy()

			if rc != wx.ID_YES:
				return

		self.DoCancel()

	def OnClose(self, _):
		self.DoCancel()

	def DoCancel(self):
		# exit without doing anything
		self.chosenTrain = None
		self.EndModal(wx.ID_CANCEL)

	def GetResult(self):
		return self.chosenTrain


class LostTrainsCtrl(wx.ListCtrl):
	def __init__(self, parent):
		self.parent = parent
		self.trains = []
		self.trainOrder = []
		self.trainMap = {}
		self.checked = []

		wx.ListCtrl.__init__(
			self, parent, wx.ID_ANY, size=(520, 240),
			style=wx.LC_REPORT | wx.LC_VIRTUAL | wx.LC_VRULES | wx.LC_SINGLE_SEL
		)
		self.SetFont(wx.Font(wx.Font(14, wx.FONTFAMILY_ROMAN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, faceName="Arial")))

		bmpCheck, bmpEmpty = self.makeBmps()
		self.il = wx.ImageList(16, 16)
		self.idxCheck = self.il.Add(bmpCheck)
		self.idxEmpty = self.il.Add(bmpEmpty)
		self.SetImageList(self.il, wx.IMAGE_LIST_SMALL)

		self.InsertColumn(0, "Train")
		self.InsertColumn(1, "Dir")
		self.InsertColumn(2, "Loco")
		self.InsertColumn(3, "Engineer")
		self.InsertColumn(4, "Block")
		self.InsertColumn(5, "Route")
		self.SetColumnWidth(0, 100)
		self.SetColumnWidth(1, 80)
		self.SetColumnWidth(2, 80)
		self.SetColumnWidth(3, 80)
		self.SetColumnWidth(4, 80)
		self.SetColumnWidth(5, 80)

		self.SetItemCount(0)
		self.selected = None

		self.attr1 = wx.ItemAttr()
		self.attr2 = wx.ItemAttr()
		self.attr1.SetBackgroundColour(wx.Colour(225, 255, 240))
		self.attr2.SetBackgroundColour(wx.Colour(138, 255, 197))

		self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnItemSelected)
		self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnItemActivated)
		self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.OnItemDeselected)
		self.Bind(wx.EVT_LIST_CACHE_HINT, self.OnItemHint)

	@staticmethod
	def makeBmps():
		bmpEmpty = wx.Bitmap(16, 16, 32)
		dc = wx.MemoryDC(bmpEmpty)
		dc.SetBackground(wx.Brush((0, 0, 0, 0)))
		dc.Clear()
		del dc
		bmpEmpty.SetMaskColour((0, 0, 0))

		fp = os.path.join(os.getcwd(), "images", "check.png")
		bmpCheck = wx.Image(fp, wx.BITMAP_TYPE_PNG).ConvertToBitmap()

		return bmpCheck, bmpEmpty

	def SetData(self, trainOrder, trainList, trainMap):
		self.trains = trainList
		self.trainMap = trainMap

		self.trainOrder = trainOrder

		self.checked = []
		lx = len(self.trainOrder)
		self.SetItemCount(lx)
		if lx != 0:
			self.RefreshItems(0, lx)

	def getSelection(self):
		if self.selected is None:
			return None

		if self.selected < 0 or self.selected >= self.GetItemCount():
			return None

		return self.trainOrder[self.selected]

	def GetChecked(self):
		return self.checked

	def getTrainOrder(self):
		return [l for l in self.trainOrder]

	def getTrainInfo(self, trid):
		try:
			return self.trains[trid]
		except KeyError:
			return None

	def setSelection(self, tx, doubleclick=False):
		self.selected = tx
		if tx is not None:
			if tx in self.checked:
				self.checked.remove(tx)
			else:
				self.checked.append(tx)
			self.Select(tx)
			self.RefreshItem(tx)

		self.parent.reportSelection(tx, doubleclick=doubleclick)

	def OnItemSelected(self, event):
		self.setSelection(event.Index)
		event.Skip()

	def OnItemActivated(self, event):
		self.setSelection(event.Index, doubleclick=True)
		event.Skip()

	def OnItemDeselected(self, event):
		self.setSelection(None)
		event.Skip()

	def OnItemHint(self, evt):
		if self.GetFirstSelected() == -1:
			self.setSelection(None)

	def OnGetItemImage(self, item):
		if item in self.checked:
			return self.idxCheck
		else:
			return self.idxEmpty

	def OnGetItemText(self, item, col):
		if item < 0 or item >= len(self.trainOrder):
			return None

		trid = self.trainOrder[item]
		tr = self.trainMap[trid]
		if col == 0:
			return trid

		elif col == 1:
			return "E" if tr[3] else "W"

		elif col == 2:
			return "" if tr[1] is None else tr[1]

		elif col == 3:
			return "" if tr[2] is None else tr[2]

		elif col == 4:
			return "" if tr[4] is None else tr[4]

		elif col == 5:
			return "" if tr[5] is None else tr[5]

	def OnGetItemAttr(self, item):
		if item % 2 == 1:
			return self.attr2
		else:
			return self.attr1


class LostTrainsRecoveryDlg(wx.Dialog):
	def __init__(self, parent, lostTrains):
		wx.Dialog.__init__(self, parent, wx.ID_ANY, "")
		self.parent = parent
		self.lostTrains = lostTrains
		self.Bind(wx.EVT_CLOSE, self.OnClose)
		self.pendingDeletions = []
		self.chosenTrain = None
		self.trainNames = []

		self.choices = self.DetermineChoices()
		
		self.SetTitle("Recover Lost Trains")
		
		vsz = wx.BoxSizer(wx.VERTICAL)
		vsz.AddSpacer(20)
		st = wx.StaticText(self, wx.ID_ANY, "Select train(s) to recover")
		vsz.Add(st, 0, wx.ALIGN_CENTER_HORIZONTAL)
		vsz.AddSpacer(20)
		
		vszl = wx.BoxSizer(wx.VERTICAL)
		st = wx.StaticText(self, wx.ID_ANY, 'Train / Dir / Loco / Engineer / Block / Route')
		vszl.Add(st, 0, wx.ALIGN_CENTER_HORIZONTAL)
		
		vszl.AddSpacer(10)

		self.ch = wx.CheckListBox(self, wx.ID_ANY, choices=self.choices, size=(-1, 220))
		vszl.Add(self.ch, 0, wx.ALIGN_CENTER_HORIZONTAL)
		self.Bind(wx.EVT_CHECKLISTBOX, self.OnCheck, self.ch)
		self.ch.SetCheckedItems(range(len(self.choices)))
	
		vszl.AddSpacer(20)
		
		vszr = wx.BoxSizer(wx.VERTICAL)
		
		self.bAll = wx.Button(self, wx.ID_ANY, "Select All", size=BSIZE)
		self.bAll.SetToolTip("Select All trains")
		self.Bind(wx.EVT_BUTTON, self.OnBAll, self.bAll)		
		vszr.Add(self.bAll)
		
		vszr.AddSpacer(10)
		
		self.bSheffield = wx.Button(self, wx.ID_ANY, "Sheffield", size=BSIZE)
		self.bSheffield.SetToolTip("Select trains in Sheffield yard")
		self.Bind(wx.EVT_BUTTON, self.OnBSheffield, self.bSheffield)		
		vszr.Add(self.bSheffield)
		
		vszr.AddSpacer(10)
		
		self.bNassau = wx.Button(self, wx.ID_ANY, "Nassau", size=BSIZE)
		self.bNassau.SetToolTip("Select trains in Wilson City")
		self.Bind(wx.EVT_BUTTON, self.OnBNassau, self.bNassau)		
		vszr.Add(self.bNassau)
		
		vszr.AddSpacer(10)
		
		self.bHyde = wx.Button(self, wx.ID_ANY, "Hyde", size=BSIZE)
		self.bHyde.SetToolTip("Select trains in Hyde yard")
		self.Bind(wx.EVT_BUTTON, self.OnBHyde, self.bHyde)		
		vszr.Add(self.bHyde)
		
		vszr.AddSpacer(10)
		
		self.bPort = wx.Button(self, wx.ID_ANY, "Port", size=BSIZE)
		self.bPort.SetToolTip("Select trains in Southport")
		self.Bind(wx.EVT_BUTTON, self.OnBPort, self.bPort)		
		vszr.Add(self.bPort)
		
		vszr.AddSpacer(10)
		
		self.bWaterman = wx.Button(self, wx.ID_ANY, "Waterman", size=BSIZE)
		self.bWaterman.SetToolTip("Select trains in Waterman yard")
		self.Bind(wx.EVT_BUTTON, self.OnBWaterman, self.bWaterman)		
		vszr.Add(self.bWaterman)
		
		vszr.AddSpacer(10)
		
		self.bYard = wx.Button(self, wx.ID_ANY, "Koehlstadt", size=BSIZE)
		self.bYard.SetToolTip("Select trains in Koehlstadt")
		self.Bind(wx.EVT_BUTTON, self.OnBYard, self.bYard)		
		vszr.Add(self.bYard)
		
		vszr.AddSpacer(10)
		
		self.bNone = wx.Button(self, wx.ID_ANY, "Select None", size=BSIZE)
		self.bNone.SetToolTip("Deselect All trains")
		self.Bind(wx.EVT_BUTTON, self.OnBNone, self.bNone)		
		vszr.Add(self.bNone)
		
		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.Add(vszl, 2)
		hsz.AddSpacer(20)
		hsz.Add(vszr, 1)
		
		vsz.Add(hsz, 0, wx.ALIGN_CENTER_HORIZONTAL)
		
		vsz.AddSpacer(30)
		
		hsz = wx.BoxSizer(wx.HORIZONTAL)
		
		self.bOK = wx.Button(self, wx.ID_ANY, "OK", size=BSIZE)
		self.bOK.SetToolTip("Recover the selected trains")
		self.Bind(wx.EVT_BUTTON, self.OnBOK, self.bOK)		
		hsz.Add(self.bOK)
		
		hsz.AddSpacer(20)
		
		self.bCancel = wx.Button(self, wx.ID_ANY, "Cancel", size=BSIZE)
		self.bCancel.SetToolTip("Exit the dialog box without making any changes")
		self.Bind(wx.EVT_BUTTON, self.OnBCancel, self.bCancel)		
		hsz.Add(self.bCancel)
		
		vsz.Add(hsz, 0, wx.ALIGN_CENTER_HORIZONTAL)
		
		vsz.AddSpacer(20)

		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.AddSpacer(20)
		hsz.Add(vsz)
		hsz.AddSpacer(20)

		self.SetSizer(hsz)
		self.Layout()
		self.Fit()
		self.CenterOnScreen()
		
	def DetermineChoices(self):
		self.trainNames = [t[0] for t in self.lostTrains]
		return ["%s / %s / %s / %s / %s / %s" % (t[0], "E" if t[3] else "W", t[1], t[2], t[4], t[5]) for t in self.lostTrains]
	
	def ApplyBlockFilter(self, blocks):
		for idx in range(len(self.lostTrains)):
			lt = self.lostTrains[idx]
			self.ch.Check(idx, check=lt[4] in blocks)
		self.SetOKButton()

	def OnCheck(self, _):
		self.SetOKButton()
		
	def SetOKButton(self):
		checkedItems = self.ch.GetCheckedItems()
		n = len(checkedItems)
		if n == 0:
			self.bOK.Enable(False)
		else:
			self.bOK.Enable(True)
			
	def OnBAll(self, _):
		self.ch.SetCheckedItems(range(len(self.choices)))
		self.bOK.Enable(True)
			
	def OnBNone(self, _):
		self.ch.SetCheckedItems([])
		self.bOK.Enable(False)
		
	def OnBSheffield(self, _):
		self.ApplyBlockFilter(["C21", "C40", "C41", "C42", "C43", "C44", "C50", "C51", "C52", "C53", "C54"])
		
	def OnBNassau(self, _):
		self.ApplyBlockFilter(["N12", "N22", "N31", "N32", "N41", "N42"])
		
	def OnBHyde(self, _):
		self.ApplyBlockFilter(["H12", "H22", "H30", "H31", "H32", "H33", "H34", "H40", "H41", "H42", "H43"])
		
	def OnBPort(self, _):
		self.ApplyBlockFilter(["P1", "P2", "P3", "P4", "P5", "P6", "P7"])
		
	def OnBYard(self, _):
		self.ApplyBlockFilter(["Y50", "Y51", "Y52", "Y53"])
		
	def OnBWaterman(self, _):
		self.ApplyBlockFilter(["Y81", "Y82", "Y83", "Y84"])
		
	def OnBOK(self, _):
		self.EndModal(wx.ID_OK)
		
	def OnBCancel(self, _):
		self.DoCancel()
		
	def OnClose(self, _):
		self.DoCancel()
		
	def DoCancel(self):
		self.EndModal(wx.ID_CANCEL)
		
	def GetResult(self):
		checkedItems = self.ch.GetCheckedItems()
		results = [self.lostTrains[i] for i in checkedItems]

		return results
