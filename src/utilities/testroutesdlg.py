import wx

routes = [
    "BRtB10B11", "BRtB10B21", "BRtB11C13", "BRtB20B21", "BRtB21C13",

    "CRtC10C20",
    "CRtC11C10", "CRtC11C30", "CRtC11C31", "CRtC11G21",
    "CRtC12C11",
    "CRtC13C12", "CRtC13C23",
    "CRtC20C21", "CRtC20C40", "CRtC20C41", "CRtC20C42", "CRtC20C43", "CRtC20C44", "CRtC20C50", "CRtC20C51", "CRtC20C52", "CRtC20C53", "CRtC20C54",
    "CRtC21C22",
    "CRtC23C11", "CRtC23C22",
    "CRtC30C20",
    "CRtC40C22", "CRtC41C22", "CRtC42C22", "CRtC43C22", "CRtC44C22", "CRtC50C22", "CRtC51C22", "CRtC52C22", "CRtC53C22", "CRtC54C22",
    "CRtG10C20", "CRtG12C20",

    "DRtD10D11", "DRtD10D21", "DRtD11S10", "DRtD20D11", "DRtD20D21", "DRtD21S10", "DRtD21S20", "DRtH13D11", "DRtH13D21", "DRtH23D11", "DRtH23D21",

    "HRtH11H12", "HRtH11H31", "HRtH11H32", "HRtH11H33", "HRtH11H34",
    "HRtH12H13",
    "HRtH13H31", "HRtH13H32", "HRtH13H33", "HRtH13H34",
    "HRtH21H22", "HRtH21H41", "HRtH21H42", "HRtH21H43",
    "HRtH22H23",
    "HRtH23H40", "HRtH23H41", "HRtH23H42", "HRtH23H43",
    "HRtH30H31",

    "KRtN10K10", "KRtN10N11", "KRtN10N21", "KRtN10S11", "KRtN20N21", "KRtN20S21", "KRtN25K10", "KRtN25N11", "KRtN25N21",

    "LRtL10L11", "LRtL10L21", "LRtL10L31",
    "LRtL11D10",
    "LRtL20L11", "LRtL20L21", "LRtL20L31",
    "LRtL21D10", "LRtL21D20",
    "LRtL31D20",
    "LRtP11L11", "LRtP11L21", "LRtP11L31",
    "LRtP21L11", "LRtP21L21", "LRtP21L31",

    "NRtB10N12", "NRtB10N22", "NRtB10N31", "NRtB10N32", "NRtB10N41", "NRtB10N42", "NRtB10W11", "NRtB10W20",
    "NRtB20N12", "NRtB20N22", "NRtB20N31", "NRtB20N32", "NRtB20N41", "NRtB20N42", "NRtB20W11", "NRtB20W20",
    "NRtN11N12", "NRtN11N22", "NRtN11N31", "NRtN11N32", "NRtN11N41", "NRtN11N42", "NRtN11W10", "NRtN11W20",
    "NRtN21N12", "NRtN21N22", "NRtN21N31", "NRtN21N32", "NRtN21N41", "NRtN21N42", "NRtN21W10", "NRtN21W20",
    "NRtN60N12", "NRtN60N22", "NRtN60N31", "NRtN60N32", "NRtN60N41", "NRtN60N42", "NRtN60W10", "NRtN60W20",
    "NRtR10N12", "NRtR10N22", "NRtR10N31", "NRtR10N32", "NRtR10N41", "NRtR10N42", "NRtR10W11", "NRtR10W20",
    "NRtT12W10",

    "PRtP10P11", "PRtP10P50",
    "PRtP1P10", "PRtP1P20", "PRtP1P40", "PRtP1P62", "PRtP1P63", "PRtP1P64",
    "PRtP20P11", "PRtP20P21", "PRtP20P50", "PRtP2P10", "PRtP2P20", "PRtP2P40", "PRtP2P62", "PRtP2P63", "PRtP2P64",
    "PRtP30P11", "PRtP30P21", "PRtP30P31", "PRtP30P41", "PRtP30P50", "PRtP31P32", "PRtP31P42", "PRtP3P10", "PRtP3P20", "PRtP3P40", "PRtP3P62", "PRtP3P63", "PRtP3P64",
    "PRtP40P31", "PRtP40P41",
    "PRtP41P32", "PRtP41P42",
    "PRtP4P10", "PRtP4P20", "PRtP5P10",
    "PRtP5P20",
    "PRtP60P11", "PRtP60P50",
    "PRtP61P11", "PRtP61P50",
    "PRtP6P10", "PRtP6P20",
    "PRtP7P10", "PRtP7P20", "PRtP7P60", "PRtP7P61", "PRtP7V10",
    "PRtV11P11", "PRtV11P50",

    "SRtF10F11",
    "SRtH10H11",
    "SRtH20H11", "SRtH20H21", "SRtH20H40",
    "SRtP42H11", "SRtP42H21", "SRtP42H40", "SRtP42N25",
    "SRtS10H10", "SRtS10H20", "SRtS10H30", "SRtS10P32", "SRtS10S11", "SRtS10S21",
    "SRtS20H10", "SRtS20H20", "SRtS20H30", "SRtS20P32", "SRtS20S11", "SRtS20S21",

    "YRtY10Y11", "YRtY10Y21", "YRtY10Y50", "YRtY10Y51", "YRtY10Y52", "YRtY10Y53", "YRtY10Y60", "YRtY10Y70",
    "YRtY11L10", "YRtY11L20", "YRtY11P50", "YRtY20Y21",
    "YRtY20Y50", "YRtY20Y51", "YRtY20Y52", "YRtY20Y53", "YRtY20Y60", "YRtY20Y70",
    "YRtY21L20", "YRtY21P50",
    "YRtY30Y11", "YRtY30Y21", "YRtY30Y50", "YRtY30Y51",
    "YRtY70Y81", "YRtY70Y82", "YRtY70Y83", "YRtY70Y84",
    "YRtY87Y11", "YRtY87Y21", "YRtY87Y81", "YRtY87Y82", "YRtY87Y83", "YRtY87Y84"
]

class TestRoutesDlg(wx.Dialog):
	def __init__(self, parent):
		wx.Dialog.__init__(self, parent, wx.ID_ANY, "")
		self.parent = parent
		self.Bind(wx.EVT_CLOSE, self.onClose)
		
		self.SetTitle("Route Tester")
		

		vsz = wx.BoxSizer(wx.VERTICAL)

		
		vsz.AddSpacer(20)
		
		self.ch = wx.Choice(self, wx.ID_ANY, choices = routes)
		vsz.Add(self.ch, 0, wx.ALIGN_CENTER_HORIZONTAL)
		
		vsz.AddSpacer(20)
		
		self.bSelect = wx.Button(self, wx.ID_ANY, "Select")
		self.Bind(wx.EVT_BUTTON, self.OnBSelect, self.bSelect)
		
		vsz.Add(self.bSelect, 0, wx.ALIGN_CENTER_HORIZONTAL)
		
		vsz.AddSpacer(20)

		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.AddSpacer(20)
		hsz.Add(vsz)
		hsz.AddSpacer(20)

		self.SetSizer(hsz)
		self.Layout()
		self.Fit()
		self.CenterOnScreen()
		
	def OnBSelect(self, evt):
		sx = self.ch.GetSelection()
		if sx == wx.NOT_FOUND:
			return 
		
		sv = self.ch.GetString(sx)
		self.parent.TestSetupRoute(sv)

		
	def onClose(self, evt):
		self.EndModal(wx.ID_OK)
		
