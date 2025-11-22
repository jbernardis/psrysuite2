import wx
import os


def makeBlank():
	empty = wx.Bitmap(24, 24, 32)
	dc = wx.MemoryDC(empty)
	dc.SetBackground(wx.Brush((0,0,0,0)))
	dc.Clear()
	del dc
	empty.SetMaskColour((0,0,0))
	return empty


class ScriptListCtrl(wx.ListCtrl):
	def __init__(self, parent, imgFolder):
		self.parent = parent

		wx.ListCtrl.__init__(
			self, parent, wx.ID_ANY, size=(490, 280),
			style=wx.LC_REPORT|wx.LC_VIRTUAL|wx.LC_VRULES
			)

		self.scripts = []
		self.imgIndex = []
		self.selected = None

		self.InsertColumn(0, "Train")
		self.InsertColumn(1, "Status")
		self.SetColumnWidth(0, 80)
		self.SetColumnWidth(1, 400)

		self.SetItemCount(0)

		self.normalA = wx.ItemAttr()
		self.normalB = wx.ItemAttr()
		self.normalA.SetBackgroundColour(wx.Colour(225, 255, 240))
		self.normalB.SetBackgroundColour(wx.Colour(138, 255, 197))

		self.loadImages(imgFolder)
		self.il = wx.ImageList(24, 24)
		empty = makeBlank()
		self.idxEmpty = self.il.Add(empty)
		self.idxSelected = self.il.Add(self.selected)
		self.SetImageList(self.il, wx.IMAGE_LIST_SMALL)

		self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnItemSelected)

		self.ticker = wx.Timer(self)
		self.Bind(wx.EVT_TIMER, self.onTicker)
		self.ticker.Start(1000)

	def loadImages(self, imgFolder):
		png = wx.Image(os.path.join(imgFolder, "selected.png"), wx.BITMAP_TYPE_PNG).ConvertToBitmap()
		mask = wx.Mask(png, wx.BLUE)
		png.SetMask(mask)
		self.selected = png

	def onTicker(self, _):
		self.refreshAll()

	def ClearChecks(self):
		self.imgIndex = [self.idxEmpty for _ in range(len(self.scripts))]
		self.refreshAll()

	def AddScript(self, script):
		self.scripts.append(script)
		self.imgIndex.append(self.idxEmpty)
		self.refreshItemCount()

	def refreshItemCount(self):
		self.SetItemCount(len(self.scripts))

	def refreshAll(self):
		self.refreshItemCount()
		if self.GetItemCount() > 0:
			self.RefreshItems(0, self.GetItemCount()-1)

	def refreshScript(self, scrName):
		for i in range(len(self.scripts)):
			scr = self.scripts[i]
			if scr.GetName() == scrName:
				self.RefreshItem(i)

	def setSelection(self, tx):
		self.selected = tx;
		if tx is not None:
			self.Select(tx, on=0)
			self.parent.reportSelection()

	def SelectAll(self):
		self.imgIndex = [self.idxSelected for _ in range(len(self.scripts))]
		self.refreshAll()
		self.parent.reportSelection()

	def SelectNone(self):
		self.ClearChecks()
		self.parent.reportSelection()

	def GetChecked(self):
		return [self.scripts[i].GetName() for i in range(len(self.scripts)) if self.imgIndex[i] == self.idxSelected]

	def OnItemSelected(self, event):
		idx = event.Index
		if self.imgIndex[idx] == self.idxEmpty:
			self.imgIndex[idx] = self.idxSelected
		else:
			self.imgIndex[idx] = self.idxEmpty

		self.RefreshItem(idx)
		self.setSelection(event.Index)

	def OnGetItemImage(self, item):
		return self.imgIndex[item]

	def OnGetItemText(self, item, col):
		scr = self.scripts[item]
		if col == 0:
			return scr.GetName()
		elif col == 1:
			return scr.GetStatus()

		return ""

	def OnGetItemAttr(self, item):
		if item % 2 == 1:
			return self.normalB
		else:
			return self.normalA
