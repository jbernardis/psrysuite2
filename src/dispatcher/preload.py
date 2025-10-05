import wx
import os
import json
import logging

PRELOADFILE = "preloads.json"
BSIZE = (100, 26)


class PreLoadedTrains:
	def __init__(self, parent):
		self.parent = parent
		self.preloadedTrains = []
		self.Reload()

	def Reload(self):
		pt = self.parent.Get("getfile", {"file": PRELOADFILE})
		if pt is None:
			logging.error("Unable to retrieve preloaded trains")
			pt = []
		self.preloadedTrains = pt

	def __len__(self):
		return len(self.preloadedTrains)

	def GetPreloadedTrains(self):
		return self.preloadedTrains


class PreloadedTrainsDlg(wx.Dialog):
	def __init__(self, parent, preloadedTrains):
		wx.Dialog.__init__(self, parent, wx.ID_ANY, "")
		self.parent = parent
		self.preloadedTrains = preloadedTrains
		self.Bind(wx.EVT_CLOSE, self.OnClose)
		self.chosenTrain = None

		self.preloadedTrainList = self.preloadedTrains.GetPreloadedTrains()
		self.trainNames = sorted([t["name"] for t in self.preloadedTrainList])
		self.trainMap = {}
		for tr in self.preloadedTrainList:
			self.trainMap[tr["name"]] = tr

		self.choices = []
		for trid in self.trainNames:
			tr = self.trainMap[trid]
			ew = "E" if tr["east"] else "W"
			rte = "" if tr["route"] is None else tr["route"]
			self.choices.append("%s / %s / %s / %s / %s" % (trid, ew, tr["loco"], tr["block"], rte))

		self.SetTitle("Preloaded Trains")

		vsz = wx.BoxSizer(wx.VERTICAL)
		vsz.AddSpacer(20)

		chFont = wx.Font(wx.Font(12, wx.FONTFAMILY_ROMAN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, faceName="Arial"))

		self.ch = PreloadedListCtrl(self)
		self.ch.SetFont(chFont)
		self.ch.setData(self.preloadedTrainList, self.trainNames, self.trainMap)
		vsz.Add(self.ch, 0, wx.ALIGN_CENTER_HORIZONTAL)

		vsz.AddSpacer(20)

		hsz = wx.BoxSizer(wx.HORIZONTAL)

		self.bOK = wx.Button(self, wx.ID_ANY, "Select", size=BSIZE)
		self.bOK.SetToolTip("Return with the chosen train as the selection")
		self.Bind(wx.EVT_BUTTON, self.OnBOK, self.bOK)
		hsz.Add(self.bOK)
		self.bOK.Enable(False)

		hsz.AddSpacer(20)

		self.bCancel = wx.Button(self, wx.ID_ANY, "Cancel", size=BSIZE)
		self.bCancel.SetToolTip("Exit the dialog box without selecting a train")
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

	def reportSelection(self, sx, doubleclick=False):
		if sx == wx.NOT_FOUND or sx is None:
			self.chosenTrain = None
			self.bOK.Enable(False)
			return

		self.chosenTrain = self.trainNames[sx]
		if doubleclick:
			self.EndModal(wx.ID_OK)
		else:
			self.bOK.Enable(True)

	def OnBOK(self, _):
		self.EndModal(wx.ID_OK)

	def OnBCancel(self, _):
		self.DoCancel()

	def OnClose(self, _):
		self.DoCancel()

	def DoCancel(self):
		# exit without doing anything
		self.chosenTrain = None
		self.EndModal(wx.ID_CANCEL)

	def GetResult(self):
		return self.trainMap[self.chosenTrain]


class PreloadedListCtrl(wx.ListCtrl):
	def __init__(self, parent):
		self.parent = parent
		self.trains = []
		self.trainOrder = []
		self.trainMap = {}

		wx.ListCtrl.__init__(
			self, parent, wx.ID_ANY, size=(420, 240),
			style=wx.LC_REPORT | wx.LC_VIRTUAL | wx.LC_VRULES | wx.LC_SINGLE_SEL
		)

		self.InsertColumn(0, "Train")
		self.InsertColumn(1, "Dir")
		self.InsertColumn(2, "Loco")
		self.InsertColumn(3, "Block")
		self.InsertColumn(4, "Route")
		self.SetColumnWidth(0, 80)
		self.SetColumnWidth(1, 80)
		self.SetColumnWidth(2, 80)
		self.SetColumnWidth(3, 80)
		self.SetColumnWidth(4, 80)

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

	def setData(self, preloadList, preloadOrder, trainMap):
		self.trains = preloadList
		self.trainOrder = preloadOrder
		lx = len(self.trainOrder)
		self.SetItemCount(lx)
		if lx != 0:
			self.RefreshItems(0, lx)

		self.trainMap = trainMap

	def getSelection(self):
		if self.selected is None:
			return None

		if self.selected < 0 or self.selected >= self.GetItemCount():
			return None

		return self.trainOrder[self.selected]

	def getTrainOrder(self):
		return [l for l in self.trainOrder]

	def getTrainInfo(self, trid):
		try:
			return self.trainMap[trid]
		except KeyError:
			return None

	def setSelection(self, tx, doubleclick=False):
		self.selected = tx
		if tx is not None:
			self.Select(tx)

		self.parent.reportSelection(tx, doubleclick=doubleclick)

	def OnItemSelected(self, event):
		self.setSelection(event.Index)

	def OnItemActivated(self, event):
		self.setSelection(event.Index, doubleclick=True)

	def OnItemDeselected(self, evt):
		self.setSelection(None)

	def OnItemHint(self, evt):
		if self.GetFirstSelected() == -1:
			self.setSelection(None)

	def OnGetItemText(self, item, col):
		if item < 0 or item >= len(self.trainOrder):
			return None

		tr = self.trainMap[self.trainOrder[item]]
		if col == 0:
			return tr["name"]

		elif col == 1:
			return "E" if tr["east"] else "W"

		elif col == 2:
			return "" if tr["loco"] is None else tr["loco"]

		elif col == 3:
			return "" if tr["block"] is None else tr["block"]

		elif col == 4:
			return "" if tr["route"] is None else tr["route"]

	def OnGetItemAttr(self, item):
		if item % 2 == 1:
			return self.attr2
		else:
			return self.attr1
