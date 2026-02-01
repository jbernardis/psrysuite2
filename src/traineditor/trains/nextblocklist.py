import wx


class NextBlockListCtrl(wx.ListCtrl):
	def __init__(self, parent):
		self.parent = parent

		wx.ListCtrl.__init__(
			self, parent, wx.ID_ANY, size=(340, 140),
			style=wx.LC_REPORT|wx.LC_VIRTUAL|wx.LC_VRULES
			)

		self.blocks = []
		self.selected = None

		self.InsertColumn(0, "Block")
		self.InsertColumn(1, "Signal")
		self.InsertColumn(2, "OS")
		self.InsertColumn(3, "Route")
		self.SetColumnWidth(0, 80)
		self.SetColumnWidth(1, 80)
		self.SetColumnWidth(2, 80)
		self.SetColumnWidth(3, 80)

		self.SetItemCount(0)

		self.normalA = wx.ItemAttr()
		self.normalB = wx.ItemAttr()
		self.normalA.SetBackgroundColour(wx.Colour(225, 255, 240))
		self.normalB.SetBackgroundColour(wx.Colour(138, 255, 197))

		self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnItemSelected)
		self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnItemActivated)

	def SetBlocks(self, blocks):
		self.SetItemCount(0)
		self.blocks = [x for x in blocks]
		self.refreshItemCount()
		if len(self.blocks) > 0:
			self.setSelection(0)
		else:
			self.setSelection(None)

	def refreshItemCount(self):
		self.SetItemCount(len(self.blocks))

	def setSelection(self, tx, activate=False):
		self.selected = tx;
		if tx is not None:
			self.Select(tx)

		self.parent.reportSelection(tx, activate)

	def GetSelection(self):
		return self.selected

	def OnItemSelected(self, event):
		self.setSelection(event.Index)

	def OnItemActivated(self, event):
		self.setSelection(event.Index, activate=True)

	def OnGetItemText(self, item, col):
		return "" if self.blocks[item][col] is None else self.blocks[item][col]

	def OnGetItemAttr(self, item):
		if item % 2 == 1:
			return self.normalB
		else:
			return self.normalA
