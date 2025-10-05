import wx


class ModifyPreloadDlg(wx.Dialog):
	def __init__(self, parent, trinfo):
		self.parent = parent
		self.trinfo = trinfo
		self.trid = trinfo["name"]
		self.east = trinfo["east"]
		self.loco = "" if trinfo["loco"] is None else trinfo["loco"]
		self.block = "" if trinfo["block"] is None else trinfo["block"]
		self.route = "" if trinfo["route"] is None else trinfo["route"]
		
		wx.Dialog.__init__(self, self.parent, style=wx.DEFAULT_FRAME_STYLE)
		self.modified = False
		
		textFont = wx.Font(wx.Font(12, wx.FONTFAMILY_ROMAN, wx.NORMAL, wx.NORMAL, faceName="Arial"))
		textFontBold = wx.Font(wx.Font(12, wx.FONTFAMILY_ROMAN, wx.NORMAL, wx.BOLD, faceName="Arial"))

		self.title = "Modify Preloaded Train %s" % self.trid
		self.Bind(wx.EVT_CLOSE, self.OnClose)

		self.bOK = wx.Button(self, wx.ID_ANY, "OK", size=(80, 50))
		self.Bind(wx.EVT_BUTTON, self.OnBOK, self.bOK)
		self.bCancel = wx.Button(self, wx.ID_ANY, "Cancel", size=(80, 50))
		self.Bind(wx.EVT_BUTTON, self.OnBCancel, self.bCancel)
		
		self.cbEast = wx.CheckBox(self, wx.ID_ANY, "East")
		self.cbEast.SetValue(self.east)
		self.cbEast.SetFont(textFontBold)
		self.Bind(wx.EVT_CHECKBOX, self.OnChange, self.cbEast)

		self.teLoco = wx.TextCtrl(self, wx.ID_ANY, self.loco)
		self.teLoco.SetFont(textFont)
		self.Bind(wx.EVT_TEXT, self.OnTextChange, self.teLoco)

		self.teBlock = wx.TextCtrl(self, wx.ID_ANY, self.block)
		self.teBlock.SetFont(textFont)
		self.Bind(wx.EVT_TEXT, self.OnTextChange, self.teBlock)

		self.teRoute = wx.TextCtrl(self, wx.ID_ANY, self.route)
		self.teRoute.SetFont(textFont)
		self.Bind(wx.EVT_TEXT, self.OnTextChange, self.teRoute)

		vsz = wx.BoxSizer(wx.VERTICAL)
		vsz.AddSpacer(20)
		
		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.AddSpacer(60)
		hsz.Add(self.cbEast)
		vsz.Add(hsz)
		vsz.AddSpacer(20)
		
		st = wx.StaticText(self, wx.ID_ANY, "Loco:", size=(60, -1), style=wx.ALIGN_RIGHT)
		st.SetFont(textFontBold)
		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.AddSpacer(20)
		hsz.Add(st, 0)
		hsz.AddSpacer(5)
		hsz.Add(self.teLoco)
		vsz.Add(hsz)
		vsz.AddSpacer(20)
		
		st = wx.StaticText(self, wx.ID_ANY, "Block:", size=(60, -1), style=wx.ALIGN_RIGHT)
		st.SetFont(textFontBold)
		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.AddSpacer(20)
		hsz.Add(st, 0)
		hsz.AddSpacer(5)
		hsz.Add(self.teBlock)
		vsz.Add(hsz)
		vsz.AddSpacer(20)
		
		st = wx.StaticText(self, wx.ID_ANY, "Route:", size=(60, -1), style=wx.ALIGN_RIGHT)
		st.SetFont(textFontBold)
		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.AddSpacer(20)
		hsz.Add(st, 0)
		hsz.AddSpacer(5)
		hsz.Add(self.teRoute)
		vsz.Add(hsz)
		vsz.AddSpacer(30)

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
		self.SetModified(False)
		
	def OnChange(self, _):
		self.SetModified()

	def OnTextChange(self, evt):
		self.SetModified()
		nm = evt.GetString().upper()
		obj = evt.GetEventObject()
		pos = obj.GetInsertionPoint()
		obj.ChangeValue(nm)
		obj.SetInsertionPoint(pos)
		evt.Skip()

	def SetModified(self, flag=True):
		self.modified = flag
		self.ShowTitle()
				
	def GetResults(self):
		loco = self.teLoco.GetValue()
		if loco.strip() == "":
			loco = None

		block = self.teBlock.GetValue()
		if block.strip() == "":
			block = None

		route = self.teRoute.GetValue()
		if route.strip() == "":
			route = None

		return {
			"name": self.trid,
			"east": self.cbEast.GetValue(),
			"loco": loco,
			"block": block,
			"route": route
		}

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

