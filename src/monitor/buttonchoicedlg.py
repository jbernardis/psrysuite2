import wx

class ButtonChoiceDlg(wx.Dialog):
	def __init__(self, parent, blist1, blist2):
		wx.Dialog.__init__(self, parent, wx.ID_ANY, "Button Choice")
		self.Bind(wx.EVT_CLOSE, self.OnClose)

		vsz = wx.BoxSizer(wx.VERTICAL)	   
		vsz.AddSpacer(20)

		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.AddSpacer(20)
		
		if blist2 is None:
			title1 = "NX Button"
		else:
			title1 = "Entry Button"
			title2 = "Exit Button"
			
		col = 1 if len(blist1) <=8 else 2
		
		self.rb1 = wx.RadioBox(self, wx.ID_ANY, title1, choices=blist1, majorDimension=col, style=wx.RA_SPECIFY_COLS, size=(120, 200))
		
		hsz.Add(self.rb1)
		
		if blist2 is not None:
			col = 1 if len(blist2) <=8 else 2
			self.rb2 = wx.RadioBox(self, wx.ID_ANY, title2, choices=blist2, majorDimension=col, style=wx.RA_SPECIFY_COLS, size=(120, 200))
			
			hsz.AddSpacer(30)
			hsz.Add(self.rb2)
		else:
			self.rb2 = None
		
		hsz.AddSpacer(20)
		
		vsz.Add(hsz, 0, wx.ALIGN_CENTER_HORIZONTAL)
		vsz.AddSpacer(20)

		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.AddSpacer(20)
		
		self.bOK = wx.Button(self, wx.ID_ANY, "OK", size=(100, 40))
		self.Bind(wx.EVT_BUTTON, self.OnOK, self.bOK)
		hsz.Add(self.bOK)
		
		hsz.AddSpacer(30)
		
		self.bCancel = wx.Button(self, wx.ID_ANY, "Cancel", size=(100, 40))
		self.Bind(wx.EVT_BUTTON, self.OnClose, self.bCancel)
		hsz.Add(self.bCancel)
		
		hsz.AddSpacer(20)
		
		vsz.Add(hsz, 0, wx.ALIGN_CENTER_HORIZONTAL)

		vsz.AddSpacer(20)
	
		self.SetSizer(vsz)
		self.Layout()
		self.Fit()
		
	def GetResults(self):
		buttons = []
		buttons.append(self.rb1.GetSelection())
		if self.rb2 is not None:
			buttons.append(self.rb2.GetSelection())
			
		return buttons
	
	def OnOK(self, _):
		self.EndModal(wx.ID_OK)

	def OnClose(self, _):
		self.EndModal(wx.ID_CANCEL)
	