import wx

colMap = ["block", "signal", "os", "route", "time", "trigger"]

class BlockSequenceListCtrl(wx.ListCtrl):
	def __init__(self, parent, height=300, readonly=False):
		self.parent = parent

		wx.ListCtrl.__init__(
			self, parent, wx.ID_ANY, size=(440, height),
			style=wx.LC_REPORT|wx.LC_VIRTUAL|wx.LC_VRULES
			)

		self.blocks = []
		self.selected = None

		self.InsertColumn(0, "Block")
		self.InsertColumn(1, "Signal")
		self.InsertColumn(2, "OS")
		self.InsertColumn(3, "Route")
		self.InsertColumn(4, "Time")
		self.InsertColumn(5, "Trigger")
		self.SetColumnWidth(0, 50)
		self.SetColumnWidth(1, 80)
		self.SetColumnWidth(2, 80)
		self.SetColumnWidth(3, 80)
		self.SetColumnWidth(4, 50)
		self.SetColumnWidth(5, 80)

		self.SetItemCount(0)

		self.normalA = wx.ItemAttr()
		self.normalB = wx.ItemAttr()
		self.normalA.SetBackgroundColour(wx.Colour(225, 255, 240))
		self.normalB.SetBackgroundColour(wx.Colour(138, 255, 197))

		if not readonly:
			self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnItemSelected)
			self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnItemActivated)

	def AddBlock(self, step):
		self.blocks.append(step)
		self.refreshItemCount()
		
	def SetItems(self, blocks):
		self.blocks = blocks
		self.refreshItemCount()

	def DelBlock(self):
		self.blocks.pop()
		self.refreshItemCount()
		if len(self.blocks) == 0:
			return None

		return self.blocks[-1]
			
	def GetBlocks(self):
		return self.blocks
	
	def GetBlock(self, idx):
		if idx < 0 or idx >= len(self.blocks):
			return None
		
		return {k:v for k,v in self.blocks[idx].items()}
	
	def SetBlock(self, idx, nv):
		if idx < 0 or idx >= len(self.blocks):
			return False
		
		self.blocks[idx] = {k:v for k,v in nv.items()}
		self.RefreshItem(idx)
		return True

	def refreshItemCount(self):
		try:
			self.parent.reportNonEmpty(len(self.blocks) != 0)
		except AttributeError:
			pass

		self.SetItemCount(0)		
		self.SetItemCount(len(self.blocks))

	def setSelection(self, tx):
		self.selected = tx;
		if tx is not None:
			self.Select(tx)

	def GetSelection(self):
		return self.selected

	def OnItemSelected(self, event):
		self.setSelection(event.Index)

	def OnItemActivated(self, event):
		item = event.Index
		try:
			self.parent.reportItemActivated(item)
		except AttributeError:
			pass

	def OnGetItemText(self, item, col):
		return str(self.blocks[item][colMap[col]])

	def OnGetItemAttr(self, item):
		if item % 2 == 1:
			return self.normalB
		else:
			return self.normalA
