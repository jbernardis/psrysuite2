import os
import wx

from traineditor.preloaded.preloadedtrains import PreLoadedTrains
from traineditor.preloaded.modifypreloaddlg import ModifyPreloadDlg

BTNSZ = (120, 46)


class ManagePreloadedDlg(wx.Dialog):
	def __init__(self, parent, rrserver):
		wx.Dialog.__init__(self, parent, wx.ID_ANY, "Manage Preloaded Trains")
		self.parent = parent
		self.rrserver = rrserver

		self.modified = False
		self.selection = wx.NOT_FOUND
		self.doubleClick = False

		self.titleString = "Manage Preloaded Trains"
		self.Bind(wx.EVT_CLOSE, self.onClose)

		btnFont = wx.Font(wx.Font(10, wx.FONTFAMILY_ROMAN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, faceName="Arial"))
		textFont = wx.Font(wx.Font(12, wx.FONTFAMILY_ROMAN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, faceName="Arial"))
		
		self.pl = PreLoadedTrains(rrserver)
		self.preloadedTrains = self.pl.getPreloadedTrainsList()
		self.trainOrder = sorted([tr["name"] for tr in self.preloadedTrains])
		self.trainMap = {tr["name"]: tr for tr in self.preloadedTrains}

		self.lbTrains = PreloadedListCtrl(self)
		self.lbTrains.SetFont(textFont)

		vsz = wx.BoxSizer(wx.VERTICAL)
		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.AddSpacer(20)
		hsz.Add(self.lbTrains, 0, wx.ALIGN_CENTER_VERTICAL)
		hsz.AddSpacer(20)
		
		sz = wx.BoxSizer(wx.VERTICAL)
		sz.AddSpacer(20)
				
		self.bAddTr = wx.Button(self, wx.ID_ANY, "Add", size=BTNSZ)
		self.bAddTr.SetFont(btnFont)
		self.bAddTr.SetToolTip("Add a new Train")
		sz.Add(self.bAddTr, 0, wx.ALIGN_CENTER_HORIZONTAL)
		self.Bind(wx.EVT_BUTTON, self.bAddTrPressed, self.bAddTr)
		
		sz.AddSpacer(20)
		
		self.bDelTr = wx.Button(self, wx.ID_ANY, "Delete", size=BTNSZ)
		self.bDelTr.SetFont(btnFont)
		self.bDelTr.SetToolTip("Delete the selected Train")
		sz.Add(self.bDelTr)
		self.Bind(wx.EVT_BUTTON, self.bDelTrPressed, self.bDelTr)
		self.bDelTr.Enable(False)

		sz.AddSpacer(20)
		hsz.Add(sz, 0, wx.ALIGN_CENTER_VERTICAL)
		hsz.AddSpacer(20)
		
		vsz.Add(hsz, 0, wx.ALIGN_CENTER_HORIZONTAL)		
		vsz.AddSpacer(20)

		sz = wx.BoxSizer(wx.HORIZONTAL)
		
		sz.AddSpacer(20)
		
		self.bSave = wx.Button(self, wx.ID_ANY, "Save", size=BTNSZ)
		self.bSave.SetFont(btnFont)
		self.bSave.SetToolTip("Save the list of preloaded trains and remain on the dialog box")
		sz.Add(self.bSave)
		self.Bind(wx.EVT_BUTTON, self.bSavePressed, self.bSave)
				
		sz.AddSpacer(20)
		
		self.bOK = wx.Button(self, wx.ID_ANY, "OK", size=BTNSZ)
		self.bOK.SetFont(btnFont)
		self.bOK.SetToolTip("Save the preloaded trains (if needed) and exit the dialog box")
		sz.Add(self.bOK)
		self.Bind(wx.EVT_BUTTON, self.bOKPressed, self.bOK)
		
		sz.AddSpacer(20)
		
		self.bCancel = wx.Button(self, wx.ID_ANY, "Cancel", size=BTNSZ)
		self.bCancel.SetFont(btnFont)
		self.bCancel.SetToolTip("Exit the dialog box discarding any pending changes")
		sz.Add(self.bCancel)
		self.Bind(wx.EVT_BUTTON, self.bCancelPressed, self.bCancel)

		sz.AddSpacer(20)
		
		vsz.Add(sz, 0, wx.ALIGN_CENTER_HORIZONTAL)		
		vsz.AddSpacer(20)
		
		self.setModified(False)
		self.lbTrains.setData(self.preloadedTrains, self.trainOrder, self.trainMap)
		self.SetSizer(vsz)
		self.Layout()
		self.Fit()

		self.setTitle()

	def setTitle(self):
		title = self.titleString
		if self.modified:
			title += " *"

		self.SetTitle(title)
		
	def setModified(self, flag=True):
		self.modified = flag
		self.setTitle()

	def reportSelection(self, tx, doubleclick=False):
		self.bDelTr.Enable(tx is not None)
		self.selection = wx.NOT_FOUND if tx is None else tx
		self.doubleClick = doubleclick

		if self.selection == wx.NOT_FOUND or not doubleclick:
			return

		trname = self.trainOrder[tx]
		trinfo = self.trainMap[trname]
		dlg = ModifyPreloadDlg(self, trinfo)
		rc = dlg.ShowModal()
		newTr = None
		if rc == wx.ID_OK:
			newTr = dlg.GetResults()

		dlg.Destroy()
		if rc != wx.ID_OK or newTr is None:
			return

		self.pl.modify(trname, newTr)

		self.preloadedTrains = self.pl.getPreloadedTrainsList()
		self.trainOrder = sorted([tr["name"] for tr in self.preloadedTrains])
		self.trainMap = {tr["name"]: tr for tr in self.preloadedTrains}

		self.lbTrains.setData(self.preloadedTrains, self.trainOrder, self.trainMap)
		self.setModified()

		self.lbTrains.Select(self.selection)

	def bAddTrPressed(self, _):
		dlg = wx.TextEntryDialog(
				self, 'Enter Name of new train',
				'Add Train', '')

		rc = dlg.ShowModal()

		trname = None
		if rc == wx.ID_OK:
			trname = dlg.GetValue()

		dlg.Destroy()
		
		if rc != wx.ID_OK or trname is None:
			return
		
		if trname in self.trainOrder:
			dlg = wx.MessageDialog(self, "Train \"%s\" is already in the list" % trname,
					"Duplicate Name", wx.OK | wx.ICON_WARNING)
			dlg.ShowModal()
			dlg.Destroy()
			return

		tr = {
			"name": trname,
			"loco": "",
			"east": True,
			"block": ""
		}
		self.pl.add(tr)

		self.preloadedTrains = self.pl.getPreloadedTrainsList()
		self.trainOrder = sorted([tr["name"] for tr in self.preloadedTrains])
		self.trainMap = {tr["name"]: tr for tr in self.preloadedTrains}

		self.lbTrains.setData(self.preloadedTrains, self.trainOrder, self.trainMap)
		self.setModified()

		try:
			self.selection = self.trainOrder.index(tr["name"])
		except:
			self.selection = wx.NOT_FOUND

		self.lbTrains.Select(self.selection)

	def bDelTrPressed(self, _):
		if self.selection == wx.NOT_FOUND:
			return

		trid = self.trainOrder[self.selection]
		self.pl.delete(trid)

		self.preloadedTrains = self.pl.getPreloadedTrainsList()
		self.trainOrder = sorted([tr["name"] for tr in self.preloadedTrains])
		self.trainMap = {tr["name"]: tr for tr in self.preloadedTrains}

		self.lbTrains.setData(self.preloadedTrains, self.trainOrder, self.trainMap)
		self.setModified()

		if self.selection >= len(self.trainOrder):
			self.selection = len(self.trainOrder) - 1
			if self.selection < 0:
				self.selection = wx.NOT_FOUND

		self.lbTrains.Select(self.selection)

	def bSavePressed(self, _):
		self.pl.save()
		self.setModified(False)
		dlg = wx.MessageDialog(self, 'Preloaded Train list has been saved', 'Data Saved', wx.OK | wx.ICON_INFORMATION)
		dlg.ShowModal()
		dlg.Destroy()

	def bOKPressed(self, _):
		if self.modified:
			self.pl.save()
		self.EndModal(wx.ID_OK)
		
	def bCancelPressed(self, _):
		self.doCancel()
		
	def onClose(self, _):
		self.doCancel()
		
	def doCancel(self):
		if self.modified:
			dlg = wx.MessageDialog(self, 'Preloaded Train list has been changed\nPress "Yes" to exit and lose changes,\nor "No" to return and save them.',
					'Changes will be lost', wx.YES_NO | wx.ICON_WARNING)
			rc = dlg.ShowModal()
			dlg.Destroy()
			if rc != wx.ID_YES:
				return

		self.EndModal(wx.ID_CANCEL)


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
		self.SetColumnWidth(0, 80)
		self.SetColumnWidth(1, 80)
		self.SetColumnWidth(2, 80)
		self.SetColumnWidth(3, 80)

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

	def modify(self, trid, trinfo):
		pass
		# self.locos[loco].update(locoinfo)
		# try:
		# 	lx = self.locoOrder.index(loco)
		# 	self.RefreshItem(lx)
		# 	self.EnsureVisible(lx)
		# except ValueError:
		# 	pass

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

	def OnGetItemAttr(self, item):
		if item % 2 == 1:
			return self.attr2
		else:
			return self.attr1
