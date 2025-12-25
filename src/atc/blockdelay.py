import logging

import wx

DELAYSFILE = "blockdelay.json"


class BlockDelay:
	def __init__(self, rrserver):
		self.blockDelays = rrserver.Get("getfile", {"file": DELAYSFILE})
		if self.blockDelays is None:
			self.blockDelays = {}
		logging.debug("Retrieved block delay file: %s" % str(self.blockDelays))

	def GetBlockDelay(self, bn, east):
		if bn not in self.blockDelays:
			return 0

		return self.blockDelays[bn][1 if east else 0]

	def GetBlockDelays(self, bn):
		if bn not in self.blockDelays:
			return [0, 0]

		return self.blockDelays[bn]


class BlockDelayDlg(wx.Dialog):
	def __init__(self, parent, rrserver, blocks):
		self.parent = parent
		self.rrserver = rrserver
		self.blocks = blocks
		wx.Dialog.__init__(self, self.parent, style=wx.DEFAULT_FRAME_STYLE)
		self.SetFont(wx.Font(wx.Font(12, wx.FONTFAMILY_ROMAN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, faceName="Arial")))

		self.blockorder = sorted([bn for bn in self.blocks.keys() if "OS" not in bn and bn not in ["N25occ"]])

		#  load the block delay table
		self.blockDelay = BlockDelay(self.rrserver)

		self.delays = {}
		for b in self.blockorder:
			self.delays[b] = self.blockDelay.GetBlockDelays(b)

		logging.debug(str(self.delays))

		self.modified = False

		self.title = "ATC: Modify Block Delays"
		self.Bind(wx.EVT_CLOSE, self.OnClose)

		self.delayList = BlockDelayListCtrl(self, self.blockorder, self.delays)

		self.bOK = wx.Button(self, wx.ID_ANY, "OK")
		self.Bind(wx.EVT_BUTTON, self.OnBOK, self.bOK)

		self.bCancel = wx.Button(self, wx.ID_ANY, "Cancel")
		self.Bind(wx.EVT_BUTTON, self.OnBCancel, self.bCancel)

		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.AddSpacer(20)
		hsz.Add(self.delayList)
		hsz.AddSpacer(20)

		vsz = wx.BoxSizer(wx.VERTICAL)
		vsz.AddSpacer(20)
		vsz.Add(hsz, 0, wx.ALIGN_CENTER_HORIZONTAL)
		vsz.AddSpacer(20)

		btnsz = wx.BoxSizer(wx.HORIZONTAL)
		btnsz.AddSpacer(20)
		btnsz.Add(self.bOK)
		btnsz.AddSpacer(20)
		btnsz.Add(self.bCancel)
		btnsz.AddSpacer(20)

		vsz.Add(btnsz, 0, wx.ALIGN_CENTER_HORIZONTAL)
		vsz.AddSpacer(20)

		self.SetSizer(vsz)
		self.Layout()
		self.Fit()

		self.ShowTitle()

	def SetModified(self, flag=True):
		if flag == self.modified:
			return

		self.modified = flag
		self.ShowTitle()

	def ShowTitle(self):
		titleString = "%s" % self.title
		if self.modified:
			titleString += " *"

		self.SetTitle(titleString)

	def ReportSelection(self, bn, dclick=False):
		logging.debug("Reported block %s, dclick=%s" % (bn, dclick))
		if dclick and bn in self.delays:
			dlg = ModifyBlockDelayDlg(self, bn, self.delays[bn][0], self.delays[bn][1])
			rc = dlg.ShowModal()
			neww = newe = 0
			if rc == wx.ID_OK:
				neww, newe = dlg.GetResults()
			dlg.Destroy()
			if rc != wx.ID_OK:
				return
			modified = False
			if self.delays[bn][0] != neww:
				self.delays[bn][0] = neww
				modified = True
			if self.delays[bn][1] != newe:
				self.delays[bn][1] = newe
				modified = True
			if modified:
				self.SetModified(True)
				self.delayList.UpdateBlock(bn, neww, newe)

	def OnClose(self, _):
		self.DoCancel()

	def OnBOK(self, _):
		delays = {blk: self.delays[blk] for blk in self.blockorder if self.delays[blk][0] != 0 or self.delays[blk][1] != 0}
		self.rrserver.Post(DELAYSFILE, "data", delays)

		self.EndModal(wx.ID_OK)

	def OnBCancel(self, _):
		self.DoCancel()

	def DoCancel(self):
		if self.modified:
			dlg = wx.MessageDialog(self,
					'Data has been modified.\nAre you sure you want to cancel?\nPress "Yes" to exit and lose changes,\nor "No" to return and save them.',
					'Changes will be lost', wx.YES_NO | wx.NO_DEFAULT | wx.ICON_WARNING)
			rc = dlg.ShowModal()
			dlg.Destroy()
			if rc != wx.ID_YES:
				return

		self.EndModal(wx.ID_CANCEL)


class BlockDelayListCtrl(wx.ListCtrl):
	def __init__(self, parent, blockorder, delays):
		self.parent = parent
		self.selected = None
		self.blockorder = blockorder
		self.delays = delays

		wx.ListCtrl.__init__(
			self, parent, wx.ID_ANY, size=(340, 380),
			style=wx.LC_REPORT | wx.LC_VIRTUAL | wx.LC_VRULES | wx.LC_SINGLE_SEL)

		self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnItemSelected)
		self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnItemActivated)
		self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.OnItemDeselected)
		self.Bind(wx.EVT_LIST_CACHE_HINT, self.OnItemHint)

		self.InsertColumn(0, "Block")
		self.InsertColumn(1, "Westbound")
		self.InsertColumn(2, "Eastbound")
		self.SetColumnWidth(0, 80)
		self.SetColumnWidth(1, 120)
		self.SetColumnWidth(2, 120)

		self.normalA = wx.ItemAttr()
		self.normalB = wx.ItemAttr()
		self.normalA.SetBackgroundColour(wx.Colour(225, 255, 240))
		self.normalB.SetBackgroundColour(wx.Colour(138, 255, 197))

		self.SetItemCount(len(self.blockorder))

	def setSelection(self, bx, dclick=False):
		self.selected = bx
		if bx is not None:
			self.Select(bx)

		self.parent.ReportSelection(None if bx is None else self.blockorder[bx], dclick=dclick)

	def OnItemSelected(self, event):
		self.setSelection(event.Index)

	def OnItemActivated(self, event):
		self.setSelection(event.Index, dclick=True)

	def OnItemDeselected(self, _):
		self.setSelection(None)

	def OnItemHint(self, evt):
		if self.GetFirstSelected() == -1:
			self.setSelection(None)

	def UpdateBlock(self, bname, neww, newe):
		try:
			idx = self.blockorder.index(bname)
		except ValueError:
			idx = None
		if idx is None:
			return

		self.delays[bname][0] = neww
		self.delays[bname][1] = newe
		self.RefreshItem(idx)

	def OnGetItemText(self, item, col):
		bname = self.blockorder[item]

		if col == 0:
			return bname
		elif col == 1:
			return "%3d" % self.delays[bname][0]
		elif col == 2:
			return "%3d" % self.delays[bname][1]

		return "?"

	def OnGetItemAttr(self, item):
		if item % 2 == 1:
			return self.normalB
		else:
			return self.normalA


class ModifyBlockDelayDlg(wx.Dialog):
	def __init__(self, parent, block, west, east):
		self.parent = parent
		self.block = block
		self.west = west
		self.east = east

		self.modified = False

		wx.Dialog.__init__(self, self.parent, style=wx.DEFAULT_FRAME_STYLE)
		self.SetFont(wx.Font(wx.Font(12, wx.FONTFAMILY_ROMAN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, faceName="Arial")))

		self.title = "Modify Block %s Delays" % block
		self.Bind(wx.EVT_CLOSE, self.OnClose)

		self.scWest = wx.SpinCtrl(self, wx.ID_ANY, "")
		self.scWest.SetRange(0, 100)
		self.scWest.SetValue(self.west)
		self.Bind(wx.EVT_SPINCTRL, self.OnSpin, self.scWest)
		self.Bind(wx.EVT_TEXT, self.OnSpin, self.scWest)

		self.stWest = wx.StaticText(self, wx.ID_ANY, "Westbound: ")

		self.scEast = wx.SpinCtrl(self, wx.ID_ANY, "")
		self.scEast.SetRange(0, 100)
		self.scEast.SetValue(self.east)
		self.Bind(wx.EVT_SPINCTRL, self.OnSpin, self.scEast)
		self.Bind(wx.EVT_TEXT, self.OnSpin, self.scEast)

		self.stEast = wx.StaticText(self, wx.ID_ANY, "Eastbound: ")

		self.bOK = wx.Button(self, wx.ID_ANY, "OK")
		self.Bind(wx.EVT_BUTTON, self.OnBOK, self.bOK)

		self.bCancel = wx.Button(self, wx.ID_ANY, "Cancel")
		self.Bind(wx.EVT_BUTTON, self.OnBCancel, self.bCancel)

		vsz = wx.BoxSizer(wx.VERTICAL)
		vsz.AddSpacer(20)

		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.Add(self.stWest)
		hsz.AddSpacer(10)
		hsz.Add(self.scWest)
		vsz.Add(hsz, 0, wx.ALIGN_CENTER_HORIZONTAL)

		vsz.AddSpacer(30)

		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.Add(self.stEast)
		hsz.AddSpacer(10)
		hsz.Add(self.scEast)
		vsz.Add(hsz, 0, wx.ALIGN_CENTER_HORIZONTAL)

		vsz.AddSpacer(20)

		btnsz = wx.BoxSizer(wx.HORIZONTAL)
		btnsz.AddSpacer(80)
		btnsz.Add(self.bOK)
		btnsz.AddSpacer(20)
		btnsz.Add(self.bCancel)
		btnsz.AddSpacer(80)

		vsz.Add(btnsz, 0, wx.ALIGN_CENTER_HORIZONTAL)
		vsz.AddSpacer(20)

		self.SetSizer(vsz)
		self.Layout()
		self.Fit()

		self.ShowTitle()

	def SetModified(self, flag=True):
		if flag == self.modified:
			return

		self.modified = flag
		self.ShowTitle()

	def ShowTitle(self):
		titleString = "%s" % self.title
		if self.modified:
			titleString += " *"

		self.SetTitle(titleString)

	def OnSpin(self, evt):
		self.SetModified(True)

	def GetResults(self):
		return self.scWest.GetValue(), self.scEast.GetValue()

	def OnClose(self, _):
		self.DoCancel()

	def OnBOK(self, _):
		# TODO - save the data
		self.EndModal(wx.ID_OK)

	def OnBCancel(self, _):
		self.DoCancel()

	def DoCancel(self):
		if self.modified:
			dlg = wx.MessageDialog(self,
					'Data has been modified.\nAre you sure you want to cancel?\nPress "Yes" to exit and lose changes,\nor "No" to return and save them.',
					'Changes will be lost', wx.YES_NO | wx.NO_DEFAULT | wx.ICON_WARNING)
			rc = dlg.ShowModal()
			dlg.Destroy()
			if rc != wx.ID_YES:
				return

		self.EndModal(wx.ID_CANCEL)
