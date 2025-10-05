import wx


class SnapshotDlg(wx.Dialog):
	def __init__(self, parent):
		wx.Dialog.__init__(self, parent, wx.ID_ANY, "Snapshot Options")
		self.Bind(wx.EVT_CLOSE, self.OnCancel)

		vsz = wx.BoxSizer(wx.VERTICAL)
		vsz.AddSpacer(20)

		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.AddSpacer(20)

		self.cbTurnouts = wx.CheckBox(self, wx.ID_ANY, "Turnouts")
		self.cbTurnouts.SetValue(True)
		hsz.Add(self.cbTurnouts)

		vsz.Add(hsz)
		vsz.AddSpacer(20)

		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.AddSpacer(20)

		self.cbSignals = wx.CheckBox(self, wx.ID_ANY, "Signals")
		self.cbSignals.SetValue(True)
		self.Bind(wx.EVT_CHECKBOX, self.OnCBSignal, self.cbSignals)
		hsz.Add(self.cbSignals)

		hsz.AddSpacer(20)

		self.cbSkipNeutral = wx.CheckBox(self, wx.ID_ANY, "Exclude neutral signals")
		self.cbSkipNeutral.SetValue(False)
		hsz.Add(self.cbSkipNeutral)

		vsz.Add(hsz)
		vsz.AddSpacer(20)

		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.AddSpacer(20)
		self.cbTrains = wx.CheckBox(self, wx.ID_ANY, "Trains")
		self.cbTrains.SetValue(True)
		hsz.Add(self.cbTrains)

		vsz.Add(hsz)
		vsz.AddSpacer(20)

		self.bOK = wx.Button(self, wx.ID_ANY, "OK", size=(100, 46))
		self.Bind(wx.EVT_BUTTON, self.OnOK, self.bOK)

		self.bCancel = wx.Button(self, wx.ID_ANY, "Cancel", size=(100, 46))
		self.Bind(wx.EVT_BUTTON, self.OnCancel, self.bCancel)

		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.AddSpacer(20)
		hsz.Add(self.bOK)
		hsz.AddSpacer(20)
		hsz.Add(self.bCancel)
		hsz.AddSpacer(20)

		vsz.AddSpacer(20)
		vsz.Add(hsz, 0, wx.ALIGN_CENTER_HORIZONTAL)

		vsz.AddSpacer(20)

		self.SetSizer(vsz)
		self.Layout()
		self.Fit()

	def OnCBSignal(self, _):
		self.cbSkipNeutral.Enable(self.cbSignals.IsChecked())

	def OnOK(self, _):
		self.EndModal(wx.ID_OK)

	def OnCancel(self, _):
		self.EndModal(wx.ID_CANCEL)

	def GetResults(self):
		return self.cbTurnouts.IsChecked(), self.cbSignals.IsChecked(), self.cbSkipNeutral.IsChecked(), self.cbTrains.IsChecked()
