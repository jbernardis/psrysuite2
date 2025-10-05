import wx

from traineditor.locomotives.locomotives import Locomotives
from traineditor.locomotives.modifylocodlg import ModifyLocoDlg
from traineditor.locomotives.locoreport import LocosReport

BTNSZ = (120, 46)

defaultProfile = {'acc': 1, 'dec': 1, 'fast': 80, 'medium': 58, 'slow': 10, 'start': 0}


class ManageLocosDlg(wx.Dialog):
	def __init__(self, parent, rrserver, browser):
		wx.Dialog.__init__(self, parent, wx.ID_ANY, "")
		self.Bind(wx.EVT_CLOSE, self.onClose)
		
		self.titleString = "Manage Locomotives"
		self.RRServer = rrserver
		self.browser = browser
		
		self.modified = None
		self.selectedLx = None
		self.selectedLoco = None

		self.SetModified(False)
	
		self.LoadLocos()
			
		textFont = wx.Font(wx.Font(12, wx.FONTFAMILY_ROMAN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, faceName="Arial"))
		
		hsizer=wx.BoxSizer(wx.HORIZONTAL)
		vsizer = wx.BoxSizer(wx.VERTICAL)
		vsizer.AddSpacer(20)
		
		self.locoList = LocoList(self)
		self.locoList.SetFont(textFont)
		self.locoList.setData(self.locos, self.locoOrder)
		self.locoOrder = self.locoList.getLocoOrder()
		vsizer.Add(self.locoList, 0, wx.ALIGN_CENTER_HORIZONTAL)

		vsizer.AddSpacer(20)
		
		btnSizer = wx.BoxSizer(wx.HORIZONTAL)
		btnSizer.AddSpacer(10)
		
		self.bAdd = wx.Button(self, wx.ID_ANY, "Add", size=BTNSZ)
		self.bAdd.SetToolTip("Add a new locomotive to the list")
		self.Bind(wx.EVT_BUTTON, self.bAddPressed, self.bAdd)
		btnSizer.Add(self.bAdd)
		
		btnSizer.AddSpacer(10)
		
		self.bDel = wx.Button(self, wx.ID_ANY, "Delete", size=BTNSZ)
		self.bDel.SetToolTip("Delete the currently selected locomotive from the list")
		self.Bind(wx.EVT_BUTTON, self.bDelPressed, self.bDel)
		btnSizer.Add(self.bDel)
		self.bDel.Enable(False)
		
		btnSizer.AddSpacer(10)
		
		vsizer.Add(btnSizer, 0, wx.ALIGN_CENTER_HORIZONTAL)
		
		vsizer.AddSpacer(20)
		
		btnSizer = wx.BoxSizer(wx.HORIZONTAL)
		btnSizer.AddSpacer(10)
		
		self.bSave = wx.Button(self, wx.ID_ANY, "Save", size=BTNSZ)
		self.bSave.SetToolTip("Save the locomotive list to the currently loaded file")
		self.Bind(wx.EVT_BUTTON, self.bSavePressed, self.bSave)
		btnSizer.Add(self.bSave)
		
		btnSizer.AddSpacer(10)
		
		self.bRevert = wx.Button(self, wx.ID_ANY, "Revert", size=BTNSZ)
		self.bRevert.SetToolTip("Revert to the most recently saved version of the locomotive list")
		self.Bind(wx.EVT_BUTTON, self.bRevertPressed, self.bRevert)
		btnSizer.Add(self.bRevert)
		
		btnSizer.AddSpacer(30)
		
		self.bPrint = wx.Button(self, wx.ID_ANY, "Print", size=BTNSZ)
		self.bPrint.SetToolTip("Print a report of the locomotive information")
		self.Bind(wx.EVT_BUTTON, self.bPrintPressed, self.bPrint)
		self.bPrint.Enable(self.browser is not None)
		btnSizer.Add(self.bPrint)

		
		btnSizer.AddSpacer(30)
		
		self.bExit = wx.Button(self, wx.ID_ANY, "Exit", size=BTNSZ)
		self.bExit.SetToolTip("Dismiss the dialog box")
		self.Bind(wx.EVT_BUTTON, self.bExitPressed, self.bExit)
		btnSizer.Add(self.bExit)

		btnSizer.AddSpacer(10)
		
		vsizer.Add(btnSizer, 0, wx.ALIGN_CENTER_HORIZONTAL)

		vsizer.AddSpacer(20)
		
		hsizer.AddSpacer(20)
		hsizer.Add(vsizer)	   
		hsizer.AddSpacer(20)
		
		self.SetModified(False)
		
		self.SetSizer(hsizer)
		self.Layout()
		self.Fit();

		
	def setTitle(self):
		title = self.titleString
		
		if self.modified:
			title += ' *'
			
		self.SetTitle(title)
		
	def bAddPressed(self, _):
		dlg = wx.TextEntryDialog(self, 'Enter Locomotive ID', 'Loco ID', '')
		rc = dlg.ShowModal()
		if rc == wx.ID_OK:
			locoID = dlg.GetValue()

		dlg.Destroy()
		
		if rc != wx.ID_OK:
			return

		if locoID in self.locoOrder:
			dlg = wx.MessageDialog(self, "Loco ID \"%s\" is already in use" % locoID, 
					"Duplicate Name", wx.OK | wx.ICON_WARNING)
			dlg.ShowModal()
			dlg.Destroy()
			return
		
		self.locoList.add(locoID)
		self.selectedLoco = locoID
		self.locoOrder = self.locoList.getLocoOrder()
		
		self.ModifySelectedLoco()
		
		self.SetModified()
		
	def bDelPressed(self, _):
		if self.selectedLx is None:
			return
		if self.selectedLoco is None:
			return
		
		self.locoList.delete(self.selectedLx)
		self.locoOrder = self.locoList.getLocoOrder()
		self.SetModified()
		
	def bPrintPressed(self, _):
		rpt = LocosReport(self, self.browser)
		rpt.LocosReport(self.locos)
		
	def reportSelection(self, lx, doubleclick=False):
		self.bDel.Enable(lx is not None)
		self.selectedLx = lx
		if lx is None:
			self.selectedLoco = None
			return

		self.locoOrder = self.locoList.getLocoOrder()
		self.selectedLoco = self.locoOrder[lx]
		if doubleclick:
			self.ModifySelectedLoco()
		
	def ModifySelectedLoco(self):
		sl = self.selectedLoco
		dlg = ModifyLocoDlg(self, sl, self.locoList.getLocoInfo(sl))
		rc = dlg.ShowModal()

		if rc == wx.ID_OK:
			loco = dlg.GetResults()
			
		dlg.Destroy()
		if rc != wx.ID_OK:
			return 

		self.locoList.modify(sl, loco)
		self.selectedLoco = sl
		self.SetModified()	
		
	def SetModified(self, flag=True):
		self.modified = flag
		self.setTitle()

	def LoadLocos(self, refresh=False):
		if self.modified:
			dlg = wx.MessageDialog(self, 'Locomotive list has been changed\nPress "Yes" to reload and lose these changes,\nor "No" to return and save them.',
					'Changes will be lost', wx.YES_NO | wx.ICON_WARNING)
			rc = dlg.ShowModal()
			dlg.Destroy()
			if rc != wx.ID_YES:
				return
			
		self.locos = Locomotives(self.RRServer)
		self.extractLocoData(self.locos)

		self.SetModified(False)

		if refresh:
			self.locoList.setData(self.locos, self.locoOrder)
			self.locoOrder = self.locoList.getLocoOrder()

	def extractLocoData(self, locoobj):
		self.locoObj = locoobj
		self.locoOrder = self.locoObj.getLocoList()
		self.locos = {}
		for lId in self.locoOrder:
			self.locos[lId] = self.locoObj.getLoco(lId)

	def bSavePressed(self, _):
		locos = {}
		ll = self.locoList.getLocoOrder()
		for l in ll:
			locos[l] = self.locoList.getLocoInfo(l)
			
		self.RRServer.Post("locos.json", "data", locos)
		self.SetModified(False)
		dlg = wx.MessageDialog(self, 'Locomotive data has been saved', 'Data Saved', wx.OK | wx.ICON_INFORMATION)
		dlg.ShowModal()
		dlg.Destroy()

	def bRevertPressed(self, _):
		self.LoadLocos()
		
	def bExitPressed(self, _):
		self.doExit()
		
	def onClose(self, _):
		self.doExit()
		
	def doExit(self):
		if self.modified:
			dlg = wx.MessageDialog(self, 'Locomotive list has been changed\nPress "Yes" to exit and lose changes,\nor "No" to return and save them.',
					'Changes will be lost', wx.YES_NO | wx.ICON_WARNING)
			rc = dlg.ShowModal()
			dlg.Destroy()
			if rc != wx.ID_YES:
				return

		self.EndModal(wx.ID_CANCEL)

		
class LocoList(wx.ListCtrl):
	def __init__(self, parent):
		self.parent = parent
		
		wx.ListCtrl.__init__(
			self, parent, wx.ID_ANY, size=(810, 240),
			style=wx.LC_REPORT|wx.LC_VIRTUAL|wx.LC_VRULES|wx.LC_SINGLE_SEL
			)

		self.InsertColumn(0, "Loco")
		self.InsertColumn(1, "Description")
		self.InsertColumn(2, "Start")
		self.InsertColumn(3, "Appr")
		self.InsertColumn(4, "Med")
		self.InsertColumn(5, "Fast")
		self.InsertColumn(6, "Acc")
		self.InsertColumn(7, "Dec")
		self.SetColumnWidth(0, 60)
		self.SetColumnWidth(1, 360)
		self.SetColumnWidth(2, 60)
		self.SetColumnWidth(3, 60)
		self.SetColumnWidth(4, 60)
		self.SetColumnWidth(5, 60)
		self.SetColumnWidth(6, 60)
		self.SetColumnWidth(7, 60)

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
		
	def setData(self, locos, locoOrder):
		self.locos = locos
		self.locoOrder = [l for l in locoOrder]
		lx = len(self.locoOrder)
		self.SetItemCount(lx)
		if lx != 0:
			self.RefreshItems(0, lx)
			
	def getSelection(self):
		if self.selected is None:
			return None
		
		if self.selected < 0 or self.selected >= self.GetItemCount():
			return None
		
		return self.order[self.selected]
	
	def getLocoOrder(self):
		return [l for l in self.locoOrder]
	
	def getLocoInfo(self, lid):
		try:
			return self.locos[lid]
		except KeyError:
			return None
			
	def setSelection(self, tx, doubleclick=False):
		self.selected = tx;
		if tx is not None:
			self.Select(tx)
			
		self.parent.reportSelection(tx, doubleclick=doubleclick)
		
	def buildSortKey(self, lid):
		return int(lid)
		
	def add(self, lid):
		lo = sorted(self.locoOrder + [lid], key=self.buildSortKey)
		lx = lo.index(lid)
		self.locoOrder = lo
		self.locos[lid] = {}
		self.locos[lid]["desc"] = None
		self.locos[lid]["prof"] = {k: defaultProfile[k] for k in defaultProfile.keys()}
		ct = len(self.locoOrder)
		self.SetItemCount(ct)
		if ct > 0:
			self.RefreshItems(0, ct-1)
		self.EnsureVisible(lx)
		return self.locos[lid]
		
	def delete(self, lx):
		lid = self.locoOrder[lx]		
		del (self.locos[lid])
		del (self.locoOrder[lx])
		
		ct = len(self.locoOrder)
		self.SetItemCount(ct)
		if ct == 0:
			self.setSelection(None)
			return

		first = lx
		last = len(self.locoOrder)-1
		
		if last <= first:
			self.RefreshItem(last)
			self.setSelection(last)
		else:
			self.RefreshItems(first, last)
			self.setSelection(first)
			
	def modify(self, loco, locoinfo):
		self.locos[loco].update(locoinfo)
		try:
			lx = self.locoOrder.index(loco)
			self.RefreshItem(lx)
			self.EnsureVisible(lx)
		except ValueError:
			pass
				
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
		if item < 0 or item >= len(self.locoOrder):
			return None
		
		lid = self.locoOrder[item]
		if col == 0:
			return lid
		elif col == 1:
			rv = self.locos[lid]["desc"]
			if rv is None:
				rv = ""
			return rv
		elif col == 2: # start speed
			return "%d" % self.locos[lid]["prof"]["start"]
		elif col == 3: # approach/slow speed
			return "%d" % self.locos[lid]["prof"]["slow"]
		elif col == 4: # medium speed
			return "%d" % self.locos[lid]["prof"]["medium"]
		elif col == 5: # fast/max speed
			return "%d" % self.locos[lid]["prof"]["fast"]
		elif col == 6: # acceleration step
			return "%d" % self.locos[lid]["prof"]["acc"]
		elif col == 7: # deceleration step
			return "%d" % self.locos[lid]["prof"]["dec"]

	def OnGetItemAttr(self, item):
		if item % 2 == 1:
			return self.attr2
		else:
			return self.attr1
