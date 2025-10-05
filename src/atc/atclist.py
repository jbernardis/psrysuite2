import wx
import os
import logging

ONVAL = "1"
OFFVAL = "0"

class ATCListCtrl(wx.ListCtrl):
	def __init__(self, parent, cmdFolder):
		self.parent = parent
		
		wx.ListCtrl.__init__(
			self, parent, wx.ID_ANY, size=(310, 110),
			style=wx.LC_REPORT|wx.LC_VIRTUAL|wx.LC_VRULES|wx.LC_SINGLE_SEL) #|wx.LC_NO_HEADER)

		self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnItemSelected)
		self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnItemActivated)
		self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.OnItemDeselected)
		self.Bind(wx.EVT_LIST_CACHE_HINT, self.OnItemHint)
		

#		self.Bind(wx.EVT_LIST_ITEM_RIGHT_CLICK, self.onRightClick, self)

		self.InsertColumn(0, "")
		self.InsertColumn(1, "Train")
		self.InsertColumn(2, "Loco")
		self.InsertColumn(3, "Spd")
		self.InsertColumn(4, "Dir")
		self.InsertColumn(5, "L")
		self.InsertColumn(6, "H")
		self.InsertColumn(7, "B")
		self.SetColumnWidth(0, 30)
		self.SetColumnWidth(1, 60)
		self.SetColumnWidth(2, 60)
		self.SetColumnWidth(3, 40)
		self.SetColumnWidth(4, 40)
		self.SetColumnWidth(5, 20)
		self.SetColumnWidth(6, 20)
		self.SetColumnWidth(7, 20)
		
		self.loadImages(os.path.join(cmdFolder, "images"))
		self.il = wx.ImageList(24, 24)
		self.idxRed = self.il.Add(self.pngSigRed)
		self.idxRedRed = self.il.Add(self.pngSigRedRed)
		self.idxRedYel = self.il.Add(self.pngSigRedYel)
		self.idxGrnYel = self.il.Add(self.pngSigGrnYel)
		self.idxGrn = self.il.Add(self.pngSigGrn)
		self.SetImageList(self.il, wx.IMAGE_LIST_SMALL)

		self.SetItemCount(0)
		self.trains = {}
		self.trainNames = []

		self.normalA = wx.ItemAttr()
		self.normalB = wx.ItemAttr()
		self.normalA.SetBackgroundColour(wx.Colour(225, 255, 240))
		self.normalB.SetBackgroundColour(wx.Colour(138, 255, 197))
		
		self.startWidth = self.GetSize()[0]

	def loadImages(self, imgFolder):
		png = wx.Image(os.path.join(imgFolder, "sigred.png"), wx.BITMAP_TYPE_PNG).ConvertToBitmap()
		mask = wx.Mask(png, wx.BLUE)
		png.SetMask(mask)
		self.pngSigRed = png
		
		png = wx.Image(os.path.join(imgFolder, "siggrn.png"), wx.BITMAP_TYPE_PNG).ConvertToBitmap()
		mask = wx.Mask(png, wx.BLUE)
		png.SetMask(mask)
		self.pngSigGrn = png
		
		png = wx.Image(os.path.join(imgFolder, "sigredyel.png"), wx.BITMAP_TYPE_PNG).ConvertToBitmap()
		mask = wx.Mask(png, wx.BLUE)
		png.SetMask(mask)
		self.pngSigRedYel = png
		
		png = wx.Image(os.path.join(imgFolder, "siggrnyel.png"), wx.BITMAP_TYPE_PNG).ConvertToBitmap()
		mask = wx.Mask(png, wx.BLUE)
		png.SetMask(mask)
		self.pngSigGrnYel = png
		
		png = wx.Image(os.path.join(imgFolder, "sigredred.png"), wx.BITMAP_TYPE_PNG).ConvertToBitmap()
		mask = wx.Mask(png, wx.BLUE)
		png.SetMask(mask)
		self.pngSigRedRed = png
		
	def AddTrain(self, tr):
		nm = tr.GetName()
		if nm in self.trainNames:
			return 
		
		self.trainNames.append(nm)
		self.trains[nm] = tr
		ct = len(self.trainNames)
		self.SetItemCount(ct)
		self.RefreshItem(ct-1)
		
	def DelTrain(self, tr):
		nm = tr.GetName()
		return self.DelTrainByName(nm)
	
	def HasTrain(self, trnm):
		return trnm in self.trainNames
	
	def FindTrain(self, trnm):
		try:
			return self.trainNames.index(trnm)
		except ValueError:
			return None
	
	def DelTrainByName(self, nm):
		if nm not in self.trainNames:
			return False
		
		del(self.trains[nm])
		self.trainNames.remove(nm)
		ct = len(self.trainNames)
		self.SetItemCount(ct)
		if ct > 0:
			self.RefreshItems(0, ct-1)
		return True
	
	def UpdateTrainName(self, tr, oldName):
		try:
			idx = self.trainNames.index(oldName)
		except ValueError:
			return 
		
		self.trainNames[idx] = tr.GetName()
		del(self.trains[oldName])
		self.trains[tr.GetName()] = tr
		self.RefreshItem(idx)
		
	def RefreshTrain(self, tr):
		nm = tr.GetName()
		if nm not in self.trainNames:
			return 
		try:
			idx = self.trainNames.index(nm)
		except ValueError:
			return 
		self.RefreshItem(idx)
	
	def ClearAll(self):
		self.SetItemCount = 0
		self.trainNames = []
		self.trains = {}
		self.RefreshItem(0)
			
	def setSelection(self, tx, dclick=False):
		self.selected = tx;
		if tx is not None:
			self.Select(tx)
			
		if dclick:
			pass
			#self.parent.reportDoubleClick(tx)
		else:
			self.parent.ReportSelection(None if tx is None else self.trainNames[tx])
		
	def ChangeSize(self, sz):
		self.SetSize(self.startWidth, sz[1]-60)

	def OnItemSelected(self, event):
		self.setSelection(event.Index)
		
	def OnItemActivated(self, event):
		self.setSelection(event.Index, dclick=True)

	def OnItemDeselected(self, _):
		self.setSelection(None)

	def OnItemHint(self, evt):
		if self.GetFirstSelected() == -1:
			self.setSelection(None)

	def OnGetItemImage(self, item):
		nm = self.trainNames[item]
		dccl = self.trains[nm]
		aspect = dccl.GetGoverningAspect()
		forced = dccl.GetForcedStop()
		
		if forced:
			return self.idxRedRed
		
		if aspect == 0:
			return self.idxRed
		
		if aspect == 0b011: # clear
			return self.idxGrn
		
		if aspect in [ 0b100, 0b110, 0b101 ]: # Restricting, Diverging or Approach Slow
			return self.idxRedYel

		return self.idxGrnYel

	def OnGetItemText(self, item, col):
		nm = self.trainNames[item]
		dccl = self.trains[nm]
		if col == 0:
			return "AA"
		elif col == 1:
			return nm
		elif col == 2:
			return dccl.GetLoco()
		elif col == 3:
			return "%3d" % dccl.GetSpeed()
		elif col == 4:
			return "Rev" if dccl.GetDirection() == "R" else "Fwd"
		elif col == 5:
			return ONVAL if dccl.GetHeadlight() else OFFVAL
		elif col == 6:
			return ONVAL if dccl.GetHorn() else OFFVAL
		elif col == 7:
			return ONVAL if dccl.GetBell() else OFFVAL
		else:
			return "?"

	def OnGetItemAttr(self, item):	
		if item % 2 == 1:
			return self.normalB
		else:
			return self.normalA
