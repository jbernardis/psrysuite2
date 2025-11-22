import wx

import logging

BSIZE = (100, 26)


class TrainHistory:
	def __init__(self, parent, settings):
		self.parent = parent
		self.settings = settings
		self.history = {}
		self.trainIds = []

	def ShowUnknown(self, flag=None):
		if flag is not None:
			self.settings.display.showunknownhistory = flag
			self.settings.SaveAll()

		return self.settings.display.showunknownhistory

	def Update(self, tr):
		trid = tr.Name()
		if trid not in self.trainIds:
			self.trainIds.append(trid)

		self.history[trid] = {"name": trid, "loco": tr.Loco(), "engineer": tr.Engineer(), "east": tr.East(), "block": tr.Blocks()}

	def UpdateEngineer(self, trid, eng):
		if trid not in self.trainIds:
			logging.error("Trying to update history on non-existant Train %s" % trid)
			return

		self.history[trid]["engineer"] = eng

	def __len__(self):
		return len(self.trainIds)

	def GetTrain(self, trid):
		if trid not in self.history.keys():
			return None

		return self.history[trid]

	def GetTrains(self):
		return self.history


class TrainHistoryDlg(wx.Dialog):
	def __init__(self, parent, trainHistory):
		wx.Dialog.__init__(self, parent, wx.ID_ANY, "")
		self.parent = parent
		self.trainHistory = trainHistory
		self.showUnknown = self.trainHistory.ShowUnknown()

		self.Bind(wx.EVT_CLOSE, self.OnClose)
		self.chosenTrain = None

		self.SetTitle("Train History")

		vsz = wx.BoxSizer(wx.VERTICAL)
		vsz.AddSpacer(10)

		self.ch = TrainHistoryCtrl(self, self.trainHistory, self.showUnknown)
		vsz.Add(self.ch, 0, wx.ALIGN_CENTER_HORIZONTAL)

		self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnClick, self.ch)
		self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnDClick, self.ch)
		self.Bind(wx.EVT_LIST_COL_CLICK, self.ch.OnColClick, self.ch)
		self.Bind(wx.EVT_LIST_COL_RIGHT_CLICK, self.ch.OnColRClick, self.ch)
		vsz.AddSpacer(20)

		hsz = wx.BoxSizer(wx.HORIZONTAL)

		self.cbUnknown = wx.CheckBox(self, wx.ID_ANY, "Include Unknown Trains")
		hsz.Add(self.cbUnknown, 0, wx.TOP, 10)
		self.Bind(wx.EVT_CHECKBOX, self.OnCbUnknown, self.cbUnknown)
		self.cbUnknown.SetValue(self.showUnknown)

		hsz.AddSpacer(20)

		self.bOK = wx.Button(self, wx.ID_ANY, "Select", size=BSIZE)
		self.bOK.SetToolTip("Return with the selected train as the selection")
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

	@staticmethod
	def BuildTrainKey(trid):
		if trid.startswith("??"):
			return "ZZ%s" % trid
		else:
			return "AA%s" % trid

	def OnDClick(self, evt):
		tx = evt.Index
		if tx == wx.NOT_FOUND:
			return

		self.chosenTrain = self.ch.GetTrainName(tx)
		self.EndModal(wx.ID_OK)

	def OnClick(self, evt):
		tx = evt.Index  # GetSelection()
		if tx == wx.NOT_FOUND:
			self.chosenTrain = None
		else:
			self.chosenTrain = self.ch.GetTrainName(tx)

		self.bOK.Enable(self.chosenTrain is not None)

	def OnCbUnknown(self, evt):
		self.showUnknown = self.cbUnknown.GetValue()
		self.trainHistory.ShowUnknown(flag=self.showUnknown)
		self.ch.SetShowUnknown(self.showUnknown)

	def OnBOK(self, _):
		if self.chosenTrain is None:
			self.EndModal(wx.ID_CANCEL)
		else:
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
		return self.chosenTrain


class TrainHistoryCtrl(wx.ListCtrl):
	def __init__(self, parent, trainHistory, showUnknown):
		#  calculate control height by the size of history
		n = len(trainHistory)
		if n < 6:
			n = 6
		elif n > 20:
			n = 20
		ht = n * 24 + 50
		wx.ListCtrl.__init__(self, parent, wx.ID_ANY, size=(800, ht), style=wx.LC_REPORT + wx.LC_VIRTUAL)
		self.parent = parent
		self.trainHistory = trainHistory
		self.trains = self.trainHistory.GetTrains()
		self.sortColumn = 0
		self.sortReverse = False
		self.showUnknown = showUnknown
		self.trainOrder = []
		self.sortTrainOrder()

		self.SetFont(wx.Font(wx.Font(14, wx.FONTFAMILY_ROMAN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, faceName="Arial")))

		self.normalA = wx.ItemAttr()
		self.normalB = wx.ItemAttr()
		self.normalA.SetBackgroundColour(wx.Colour(225, 255, 240))
		self.normalB.SetBackgroundColour(wx.Colour(138, 255, 197))

		self.InsertColumn(0, "Train")
		self.SetColumnWidth(0, 100)
		self.InsertColumn(1, "E/W")
		self.SetColumnWidth(1, 56)
		self.InsertColumn(2, "Loco")
		self.SetColumnWidth(2, 80)
		self.InsertColumn(3, "Engineer")
		self.SetColumnWidth(3, 160)
		self.InsertColumn(4, "Blocks")
		self.SetColumnWidth(4, 400)
		self.SetItemCount(len(self.trains))

	def GetTrainName(self, tx):
		try:
			return self.trainOrder[tx]
		except (KeyError, IndexError):
			return None

	def SetShowUnknown(self, flag):
		self.showUnknown = flag
		self.sortTrainOrder()
		self.SetItemCount(0)
		n = len(self.trainOrder)
		self.SetItemCount(n)
		if n > 0:
			self.RefreshItems(0, n-1)

	def sortTrainOrder(self):
		if self.showUnknown:
			k = self.trains.keys()
		else:
			k = [kk for kk in self.trains.keys() if not kk.startswith("??")]
		self.trainOrder = sorted(k, key=self.BuildTrainKey, reverse=self.sortReverse)

	def BuildTrainKey(self, trid):
		if self.sortColumn == 0:
			if trid.startswith("??"):
				return "ZZ%s" % trid
			else:
				return "AA%s" % trid
		else:
			tr = self.trains[trid]
			if self.sortColumn == 1:  # east
				if tr["east"]:
					return "E"
				else:
					return "W"

			elif self.sortColumn == 2:  # loco
				l = tr["loco"]
				if l.startswith("??"):
					return "ZZ%s" % l
				else:
					k = ("00000"+l)[-5:]
					return "AA%s" % k

			elif self.sortColumn == 3:  # engineer
				if tr["engineer"] is None:
					return "ZZZZZZZZ"
				else:
					return tr["engineer"]

			elif self.sortColumn == 4:  # blocks
				if len(tr["block"]) == 0:
					return ""
				else:
					return tr["block"][-1]

	def OnColClick(self, evt):
		self.sortColumn = evt.GetColumn()
		self.sortReverse = False
		self.sortTrainOrder()
		self.RefreshItems(0, len(self.trainOrder)-1)

	def OnColRClick(self, evt):
		self.sortColumn = evt.GetColumn()
		self.sortReverse = True
		self.sortTrainOrder()
		self.RefreshItems(0, len(self.trainOrder)-1)

	def OnGetItemText(self, item, col):
		trid = self.trainOrder[item]
		tr = self.trains[trid]

		if col == 0:
			return trid

		elif col == 1:
			return "E" if tr["east"] else "W"

		elif col == 2:
			return "" if tr["loco"] is None else tr["loco"]

		elif col == 3:
			return "" if tr["engineer"] is None else tr["engineer"]

		elif col == 4:
			return ", ".join(reversed(tr["block"]))

		return "unknown column: %d" % item

	def OnGetItemAttr(self, item):
		if item % 2 == 1:
			return self.normalB
		else:
			return self.normalA
