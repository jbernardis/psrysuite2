import wx


class ModifyPreloadDlg(wx.Dialog):
	def __init__(self, parent, trinfo, locos):
		self.parent = parent
		self.trinfo = trinfo
		self.trid = trinfo["name"]
		self.loco = "" if trinfo["loco"] is None else trinfo["loco"]
		self.notes = "" if trinfo["notes"] is None else trinfo["notes"]

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

		self.chLoco = wx.Choice(self, wx.ID_ANY, choices=locos)
		self.chLoco.SetFont(textFont)
		self.chLoco.SetSelection(0)
		self.Bind(wx.EVT_CHOICE, self.OnLocoChoice, self.chLoco)

		self.teNotes = wx.TextCtrl(self, wx.ID_ANY, self.notes)
		self.teNotes.SetFont(textFont)
		self.Bind(wx.EVT_TEXT, self.OnTextChange, self.teNotes)

		vsz = wx.BoxSizer(wx.VERTICAL)
		vsz.AddSpacer(20)

		st = wx.StaticText(self, wx.ID_ANY, "Loco:")  # , size=(120, -1), style=wx.ALIGN_RIGHT)
		st.SetFont(textFontBold)
		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.AddSpacer(20)
		hsz.Add(st, 0)
		hsz.AddSpacer(5)
		hsz.Add(self.chLoco)
		vsz.Add(hsz, 0, wx.ALIGN_CENTER_HORIZONTAL)
		vsz.AddSpacer(20)

		st = wx.StaticText(self, wx.ID_ANY, "Notes:")  # , size=(120, -1), style=wx.ALIGN_RIGHT)
		st.SetFont(textFontBold)
		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.AddSpacer(20)
		hsz.Add(st, 0)
		hsz.AddSpacer(5)
		hsz.Add(self.teNotes)
		vsz.Add(hsz, 0, wx.ALIGN_CENTER_HORIZONTAL)
		vsz.AddSpacer(20)

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

	def OnLocoChoice(self, _):
		self.SetModified()

	def OnTextChange(self, evt):
		self.SetModified()
		# nm = evt.GetString().upper()
		# obj = evt.GetEventObject()
		# pos = obj.GetInsertionPoint()
		# obj.ChangeValue(nm)
		# obj.SetInsertionPoint(pos)
		# evt.Skip()

	def SetModified(self, flag=True):
		self.modified = flag
		self.ShowTitle()
				
	def GetResults(self):
		loco = self.chLoco.GetStringSelection()

		notes = self.teNotes.GetValue()
		if notes.strip() == "":
			notes = None


		return {
			"name": self.trid,
			"loco": loco,
			"notes": notes
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

