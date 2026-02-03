import wx

from dispatcher.managepreloaded import PreloadedListCtrl

BTNSZ = (120, 46)


class ChoosePreloadedDlg(wx.Dialog):
	def __init__(self, parent, preLoaded):
		wx.Dialog.__init__(self, parent, wx.ID_ANY, "Choose Preloaded Trains")
		self.parent = parent

		self.modified = False
		self.selection = wx.NOT_FOUND
		self.doubleClick = False

		self.SetTitle("Choose Preloaded Train")
		self.Bind(wx.EVT_CLOSE, self.onClose)

		btnFont = wx.Font(wx.Font(10, wx.FONTFAMILY_ROMAN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, faceName="Arial"))
		textFont = wx.Font(
			wx.Font(12, wx.FONTFAMILY_ROMAN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, faceName="Arial"))

		self.preloadedTrains = preLoaded
		if len(self.preloadedTrains) == 0:
			dlg = wx.MessageDialog(self, "No Preloaded Trains have been defined",
				"No Trains Defined", wx.OK | wx.ICON_INFORMATION)
			dlg.ShowModal()
			dlg.Destroy()
			return

		self.trainOrder = sorted([tr["name"] for tr in self.preloadedTrains])
		self.trainMap = {tr["name"]: tr for tr in self.preloadedTrains}

		self.lbTrains = PreloadedListCtrl(self)
		self.lbTrains.SetFont(textFont)

		vsz = wx.BoxSizer(wx.VERTICAL)
		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.AddSpacer(20)
		hsz.Add(self.lbTrains, 0, wx.ALIGN_CENTER_VERTICAL)
		hsz.AddSpacer(20)

		vsz.Add(hsz, 0, wx.ALIGN_CENTER_HORIZONTAL)
		vsz.AddSpacer(20)

		sz = wx.BoxSizer(wx.HORIZONTAL)

		sz.AddSpacer(20)

		self.bOK = wx.Button(self, wx.ID_ANY, "OK", size=BTNSZ)
		self.bOK.SetFont(btnFont)
		self.bOK.SetToolTip("Choose the selected train and exit")
		sz.Add(self.bOK)
		self.Bind(wx.EVT_BUTTON, self.bOKPressed, self.bOK)

		sz.AddSpacer(20)

		self.bCancel = wx.Button(self, wx.ID_ANY, "Cancel", size=BTNSZ)
		self.bCancel.SetFont(btnFont)
		self.bCancel.SetToolTip("Exit the dialog without making a selection")
		sz.Add(self.bCancel)
		self.Bind(wx.EVT_BUTTON, self.bCancelPressed, self.bCancel)

		sz.AddSpacer(20)

		vsz.Add(sz, 0, wx.ALIGN_CENTER_HORIZONTAL)
		vsz.AddSpacer(20)

		self.lbTrains.setData(self.preloadedTrains, self.trainOrder, self.trainMap)
		self.SetSizer(vsz)
		self.Layout()
		self.Fit()

	def reportSelection(self, tx, doubleclick=False):
		self.selection = wx.NOT_FOUND if tx is None else tx
		self.doubleClick = doubleclick

		if self.selection == wx.NOT_FOUND or not doubleclick:
			return

		self.EndModal(wx.ID_OK)

	def bOKPressed(self, _):
		if self.modified:
			self.pl.save()
		self.EndModal(wx.ID_OK)

	def bCancelPressed(self, _):
		self.doCancel()

	def onClose(self, _):
		self.doCancel()

	def doCancel(self):
		self.EndModal(wx.ID_CANCEL)

	def GetResults(self):
		if self.selection is None:
			return None
		trname = self.trainOrder[self.selection]
		return self.trainMap[trname]

