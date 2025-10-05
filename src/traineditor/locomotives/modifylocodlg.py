import wx
		
class ModifyLocoDlg(wx.Dialog):
	def __init__(self, parent, locoid, locoinfo):
		self.parent = parent
		self.locoid = locoid
		self.locoinfo = locoinfo
		
		wx.Dialog.__init__(self, self.parent, style=wx.DEFAULT_FRAME_STYLE)
		self.modified = False
		
		textFont = wx.Font(wx.Font(12, wx.FONTFAMILY_ROMAN, wx.NORMAL, wx.NORMAL, faceName="Arial"))
		textFontBold = wx.Font(wx.Font(12, wx.FONTFAMILY_ROMAN, wx.NORMAL, wx.BOLD, faceName="Arial"))

		self.title = "Modify Locomotive %s" % self.locoid
		self.Bind(wx.EVT_CLOSE, self.OnClose)

		self.teDesc = wx.TextCtrl(self, wx.ID_ANY, "", size=(300, -1))
		self.Bind(wx.EVT_TEXT, self.OnDescText, self.teDesc)
		self.teDesc.SetFont(textFont)

		self.bOK = wx.Button(self, wx.ID_ANY, "OK", size=(80, 50))
		self.Bind(wx.EVT_BUTTON, self.OnBOK, self.bOK)
		self.bCancel = wx.Button(self, wx.ID_ANY, "Cancel", size=(80, 50))
		self.Bind(wx.EVT_BUTTON, self.OnBCancel, self.bCancel)
		
		self.scStart = wx.SpinCtrl(self, wx.ID_ANY, "")
		self.scStart.SetRange(0,64)
		self.scStart.SetValue(0)
		self.Bind(wx.EVT_SPINCTRL, self.OnSpin, self.scStart)
		
		self.scApproach = wx.SpinCtrl(self, wx.ID_ANY, "")
		self.scApproach.SetRange(0,125)
		self.scApproach.SetValue(0)
		self.Bind(wx.EVT_SPINCTRL, self.OnSpin, self.scApproach)
		
		self.scMedium = wx.SpinCtrl(self, wx.ID_ANY, "")
		self.scMedium.SetRange(0,125)
		self.scMedium.SetValue(0)
		self.Bind(wx.EVT_SPINCTRL, self.OnSpin, self.scMedium)
		
		self.scFast = wx.SpinCtrl(self, wx.ID_ANY, "")
		self.scFast.SetRange(0,125)
		self.scFast.SetValue(0)
		self.Bind(wx.EVT_SPINCTRL, self.OnSpin, self.scFast)
		
		self.scAcc = wx.SpinCtrl(self, wx.ID_ANY, "")
		self.scAcc.SetRange(1, 10)
		self.scAcc.SetValue(1)
		self.Bind(wx.EVT_SPINCTRL, self.OnSpin, self.scAcc)
		
		self.scDec = wx.SpinCtrl(self, wx.ID_ANY, "")
		self.scDec.SetRange(1, 10)
		self.scDec.SetValue(1)
		self.Bind(wx.EVT_SPINCTRL, self.OnSpin, self.scDec)

		vsz = wx.BoxSizer(wx.VERTICAL)
		vsz.AddSpacer(20)
		
		st = wx.StaticText(self, wx.ID_ANY, "Description:", size=(150, -1), style=wx.ALIGN_RIGHT)
		st.SetFont(textFontBold)
		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.AddSpacer(20)
		hsz.Add(st, 0, wx.TOP, 5)
		hsz.AddSpacer(5)
		hsz.Add(self.teDesc)
		vsz.Add(hsz)
		vsz.AddSpacer(20)
		
		st = wx.StaticText(self, wx.ID_ANY, "Start:", size=(150, -1), style=wx.ALIGN_RIGHT)
		st.SetFont(textFontBold)
		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.AddSpacer(20)
		hsz.Add(st, 0)
		hsz.AddSpacer(5)
		hsz.Add(self.scStart)
		vsz.Add(hsz)
		vsz.AddSpacer(10)
		
		st = wx.StaticText(self, wx.ID_ANY, "Approach:", size=(150, -1), style=wx.ALIGN_RIGHT)
		st.SetFont(textFontBold)
		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.AddSpacer(20)
		hsz.Add(st, 0)
		hsz.AddSpacer(5)
		hsz.Add(self.scApproach)
		vsz.Add(hsz)
		vsz.AddSpacer(10)
		
		st = wx.StaticText(self, wx.ID_ANY, "Medium:", size=(150, -1), style=wx.ALIGN_RIGHT)
		st.SetFont(textFontBold)
		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.AddSpacer(20)
		hsz.Add(st, 0)
		hsz.AddSpacer(5)
		hsz.Add(self.scMedium)
		vsz.Add(hsz)
		vsz.AddSpacer(10)
		
		st = wx.StaticText(self, wx.ID_ANY, "Fast:", size=(150, -1), style=wx.ALIGN_RIGHT)
		st.SetFont(textFontBold)
		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.AddSpacer(20)
		hsz.Add(st, 0)
		hsz.AddSpacer(5)
		hsz.Add(self.scFast)
		vsz.Add(hsz)
		vsz.AddSpacer(10)
		
		st = wx.StaticText(self, wx.ID_ANY, "Acceleration:", size=(150, -1), style=wx.ALIGN_RIGHT)
		st.SetFont(textFontBold)
		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.AddSpacer(20)
		hsz.Add(st, 0)
		hsz.AddSpacer(5)
		hsz.Add(self.scAcc)
		vsz.Add(hsz)
		vsz.AddSpacer(10)
		
		st = wx.StaticText(self, wx.ID_ANY, "Deceleration:", size=(150, -1), style=wx.ALIGN_RIGHT)
		st.SetFont(textFontBold)
		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.AddSpacer(20)
		hsz.Add(st, 0)
		hsz.AddSpacer(5)
		hsz.Add(self.scDec)
		vsz.Add(hsz)
		
		vsz.AddSpacer(40)

		bsz = wx.BoxSizer(wx.HORIZONTAL)
		bsz.Add(self.bOK)
		bsz.AddSpacer(20)
		bsz.Add(self.bCancel)
		
		vsz.Add(bsz, 0, wx.ALIGN_CENTER_HORIZONTAL)
		vsz.AddSpacer(20)
				
		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.AddSpacer(20)
		hsz.Add(vsz)
		hsz.AddSpacer(20)

		self.SetSizer(hsz)
		self.Fit()
		self.Layout()

		wx.CallAfter(self.Initialize)

	def ShowTitle(self):
		titleString = "%s" % self.title
		if self.modified:
			titleString += " *"

		self.SetTitle(titleString)

	def Initialize(self):
		self.ShowTitle()
		dvalue = self.locoinfo["desc"]
		if dvalue is None:
			dvalue = ""
		self.teDesc.SetValue(dvalue)
		
		self.scStart.SetValue(self.locoinfo["prof"]["start"])
		self.scApproach.SetValue(self.locoinfo["prof"]["slow"])
		self.scMedium.SetValue(self.locoinfo["prof"]["medium"])
		self.scFast.SetValue(self.locoinfo["prof"]["fast"])
		self.scAcc.SetValue(self.locoinfo["prof"]["acc"])
		self.scDec.SetValue(self.locoinfo["prof"]["dec"])
		
		self.SetModified(False)
		
	def OnDescText(self, _):
		self.SetModified()
		
	def OnSpin(self, _):
		self.SetModified()
				
	def SetModified(self, flag=True):
		self.modified = flag
		self.ShowTitle()
				
	def GetResults(self):
		loco = {}
		loco["desc"] = self.teDesc.GetValue()
		loco["prof"] = {}
		loco["prof"]["start"] = self.scStart.GetValue()
		loco["prof"]["slow"] = self.scApproach.GetValue()
		loco["prof"]["medium"] = self.scMedium.GetValue()
		loco["prof"]["fast"] = self.scFast.GetValue()
		loco["prof"]["acc"] = self.scAcc.GetValue()
		loco["prof"]["dec"] = self.scDec.GetValue()	
		return loco

	def OnClose(self, _):
		self.DoCancel()
		
	def OnBOK(self, _):
		self.EndModal(wx.ID_OK)
		
	def OnBCancel(self, _):
		self.DoCancel()
		
	def DoCancel(self):
		if self.modified:
			dlg = wx.MessageDialog(self, 'Data has been modified.\nAre you sure you want to cancel?\nPress "Yes" to exit and lose changes,\nor "No" to return and save them.',
					'Changes will be lost', wx.YES_NO | wx.ICON_WARNING)
			rc = dlg.ShowModal()
			dlg.Destroy()
			if rc != wx.ID_YES:
				return
			
		self.EndModal(wx.ID_CANCEL)

