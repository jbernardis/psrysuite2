import wx

class TrainParmDlg(wx.Dialog):
	def __init__(self, parent, trainlist):
		self.parent = parent
		
		wx.Dialog.__init__(self, self.parent, style=wx.DEFAULT_FRAME_STYLE)
		self.SetTitle("Edit Starting Trains Parameters")
		self.Bind(wx.EVT_CLOSE, self.OnClose)

		vsz = wx.BoxSizer(wx.VERTICAL)
		vsz.AddSpacer(20)

		self.lcParms = ParmListCtrl(self)
		
		for tr in sorted(trainlist.keys()):
			self.lcParms.AddTrain(trainlist[tr])
			
		vsz.Add(self.lcParms, 0, wx.EXPAND)

		vsz.AddSpacer(10)
		
		bsz = wx.BoxSizer(wx.HORIZONTAL)
		
		self.bOK = wx.Button(self, wx.ID_ANY, "OK")
		self.Bind(wx.EVT_BUTTON, self.OnBOK, self.bOK)
		bsz.Add(self.bOK)
		bsz.AddSpacer(20)
		
		self.bCancel = wx.Button(self, wx.ID_ANY, "Cancel")
		self.Bind(wx.EVT_BUTTON, self.OnBCancel, self.bCancel)
		bsz.Add(self.bCancel)
		
		vsz.Add(bsz, 0, wx.ALIGN_CENTER_HORIZONTAL)
		
		vsz.AddSpacer(20)
		
		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.AddSpacer(20)
		
		hsz.Add(vsz)
		hsz.AddSpacer(20)
		
		self.SetSizer(hsz)
		
		self.Fit()
		self.Layout()
		
	def TrainSelected(self, tx, tr):
		dlg = SingleTrainDlg(self, tr)
		rc = dlg.ShowModal()
		if rc == wx.ID_OK:
			lid, tm, tlen = dlg.GetResults()
		dlg.Destroy()
		if rc != wx.ID_OK:
			return 

		self.lcParms.SetParams(tx, lid, tm, tlen)
		
	def GetResults(self):
		return {}

	def OnClose(self, _):
		self.DoClose()
		
	def OnBOK(self, _):
		self.EndModal(wx.ID_OK)
		
	def OnBCancel(self, _):
		self.DoClose()
		
	def DoClose(self):
		self.EndModal(wx.ID_CANCEL)

class ParmListCtrl(wx.ListCtrl):
	def __init__(self, parent):
		self.parent = parent

		wx.ListCtrl.__init__(
			self, parent, wx.ID_ANY, size=(380, 160),
			style=wx.LC_REPORT|wx.LC_VIRTUAL|wx.LC_VRULES
			)

		self.trains = []
		self.selected = None

		self.InsertColumn(0, "Train")
		self.InsertColumn(1, "Loco")
		self.InsertColumn(2, "Time Mult")
		self.InsertColumn(3, "Length")
		self.SetColumnWidth(0, 80)
		self.SetColumnWidth(1, 80)
		self.SetColumnWidth(2, 80)
		self.SetColumnWidth(3, 80)

		self.SetItemCount(0)

		self.normalA = wx.ItemAttr()
		self.normalB = wx.ItemAttr()
		self.normalA.SetBackgroundColour(wx.Colour(225, 255, 240))
		self.normalB.SetBackgroundColour(wx.Colour(138, 255, 197))

		self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnItemActivated)

	def AddTrain(self, trarray):
		self.trains.append(trarray) # (trainid, loco, timemultiple, length)
		self.refreshItemCount()

	def refreshItemCount(self):
		self.SetItemCount(len(self.trains))

	def refreshAll(self):
		self.refreshItemCount()
		if self.GetItemCount() > 0:
			self.RefreshItems(0, self.GetItemCount()-1)

	def setSelection(self, tx):
		self.selected = tx;
		if tx is not None:
			self.Select(tx)
			self.parent.TrainSelected(tx, self.trains[tx])

	def OnItemActivated(self, event):
		idx = event.Index
		self.RefreshItem(idx)
		self.setSelection(event.Index)
		
	def SetParams(self, tx, lid, tm, tlen):
		self.trains[tx][1] = lid
		self.trains[tx][2] = tm
		self.trains[tx][3] = tlen
		self.RefreshItem(tx)

	def OnGetItemText(self, item, col):
		tr = self.trains[item]
		return str(tr[col])

	def OnGetItemAttr(self, item):
		if item % 2 == 1:
			return self.normalB
		else:
			return self.normalA

class SingleTrainDlg(wx.Dialog):
	def __init__(self, parent, trinfo):
		self.parent = parent
		
		self.tid = trinfo[0]
		self.lid = trinfo[1]
		self.tm = trinfo[2]
		self.tlen = trinfo[3]
		
		wx.Dialog.__init__(self, self.parent, style=wx.DEFAULT_FRAME_STYLE)
		self.SetTitle("Edit Single Train Parameters")
		self.Bind(wx.EVT_CLOSE, self.OnClose)

		vsz = wx.BoxSizer(wx.VERTICAL)
		vsz.AddSpacer(20)

		self.tcLocoID = wx.TextCtrl(self, wx.ID_ANY, self.lid, size=(100, -1))	
		hsz = wx.BoxSizer(wx.HORIZONTAL)
		st = wx.StaticText(self, wx.ID_ANY, "Loco ID:", size=(100, -1))
		hsz.Add(st)
		hsz.AddSpacer(10)	
		hsz.Add(self.tcLocoID)
		
		vsz.Add(hsz)

		vsz.AddSpacer(10)
		
		hsz = wx.BoxSizer(wx.HORIZONTAL)
		st = wx.StaticText(self, wx.ID_ANY, "Time Multiple:", size=(100, -1))
		hsz.Add(st)
		hsz.AddSpacer(10)	
		self.scTime = wx.SpinCtrl(self, -1, "%d" % self.tm)
		self.scTime.SetRange(1,10)
		self.scTime.SetValue(self.tm)
		hsz.Add(self.scTime)
		vsz.Add(hsz)
		vsz.AddSpacer(10)
		
		hsz = wx.BoxSizer(wx.HORIZONTAL)
		st = wx.StaticText(self, wx.ID_ANY, "Train Length:", size=(100, -1))
		hsz.Add(st)
		hsz.AddSpacer(10)	
		self.scLen = wx.SpinCtrl(self, -1, "%d" % self.tm)
		self.scLen.SetRange(2, 5)
		self.scLen.SetValue(self.tlen)
		hsz.Add(self.scLen)
		
		vsz.Add(hsz)
		vsz.AddSpacer(30)
		
		bsz = wx.BoxSizer(wx.HORIZONTAL)
		
		self.bOK = wx.Button(self, wx.ID_ANY, "OK")
		self.Bind(wx.EVT_BUTTON, self.OnBOK, self.bOK)
		bsz.Add(self.bOK)
		bsz.AddSpacer(20)
		
		self.bCancel = wx.Button(self, wx.ID_ANY, "Cancel")
		self.Bind(wx.EVT_BUTTON, self.OnBCancel, self.bCancel)
		bsz.Add(self.bCancel)
		
		vsz.Add(bsz, 0, wx.ALIGN_CENTER_HORIZONTAL)
		
		vsz.AddSpacer(20)
		
		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.AddSpacer(20)
		
		hsz.Add(vsz)
		hsz.AddSpacer(20)
		
		self.SetSizer(hsz)
		
		self.Fit()
		self.Layout()
		
	def GetResults(self):
		loco = self.tcLocoID.GetValue()
		tm = self.scTime.GetValue()
		tlen = self.scLen.GetValue()
		return loco, tm, tlen

	def OnClose(self, _):
		self.DoClose()
		
	def OnBOK(self, _):
		self.EndModal(wx.ID_OK)
		
	def OnBCancel(self, _):
		self.DoClose()
		
	def DoClose(self):
		self.EndModal(wx.ID_CANCEL)