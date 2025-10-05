import wx

class EnterLocoDlg(wx.Dialog):
	def __init__(self, parent, locoList):
		wx.Dialog.__init__(self, parent, wx.ID_ANY, "Enter Locomotive Number")
		
		self.chosenLoco = None

		self.Bind(wx.EVT_CLOSE, self.OnCancel)

		vsz = wx.BoxSizer(wx.VERTICAL)
		vsz.AddSpacer(20)

		font = wx.Font(wx.Font(16, wx.FONTFAMILY_TELETYPE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, faceName="Monospace"))
		lblLoco  = wx.StaticText(self, wx.ID_ANY, "Loco ID:")
		lblLoco.SetFont(font)
		self.cbLocoID = wx.ComboBox(self, wx.ID_ANY, "",
					choices=locoList,
					style=wx.CB_DROPDOWN | wx.TE_PROCESS_ENTER)
		self.cbLocoID.SetFont(font)
		
		self.Bind(wx.EVT_COMBOBOX, self.OnLocoChoice, self.cbLocoID)
		self.Bind(wx.EVT_TEXT, self.OnLocoText, self.cbLocoID)

		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.Add(lblLoco)
		hsz.AddSpacer(10)
		hsz.Add(self.cbLocoID)
		vsz.Add(hsz)
		
		vsz.AddSpacer(20)

		bsz = wx.BoxSizer(wx.HORIZONTAL)

		self.bOK = wx.Button(self, wx.ID_ANY, "OK")
		self.bCancel = wx.Button(self, wx.ID_ANY, "Cancel")

		bsz.Add(self.bOK)
		bsz.AddSpacer(30)
		bsz.Add(self.bCancel)

		self.Bind(wx.EVT_BUTTON, self.OnOK, self.bOK)
		self.Bind(wx.EVT_BUTTON, self.OnCancel, self.bCancel)

		vsz.Add(bsz, 0, wx.ALIGN_CENTER)

		vsz.AddSpacer(20)

		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.AddSpacer(20)
		hsz.Add(vsz)
		hsz.AddSpacer(20)

		self.SetSizer(hsz)
		self.Layout()
		self.Fit()
		
	def BuildSortKey(self, lid):
		return int(lid)
		
	def OnLocoChoice(self, evt):
		self.chosenLoco = evt.GetString()

	def OnLocoText(self, evt):
		self.chosenLoco = evt.GetString()
		evt.Skip()


	def OnCancel(self, _):
		self.EndModal(wx.ID_CANCEL)

	def OnOK(self, _):
		self.EndModal(wx.ID_OK)

	def GetResults(self):
		return self.chosenLoco
