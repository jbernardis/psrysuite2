import wx


class CleanDlg(wx.Dialog):
    def __init__(self, parent, choices, label):
        wx.Dialog.__init__(self, parent, wx.ID_ANY, "Clean up %s" % label)
        self.Bind(wx.EVT_CLOSE, self.onCancel)
        
        vsz = wx.BoxSizer(wx.VERTICAL)
        vsz.AddSpacer(20)
        self.choices = [l for l in choices]

        self.lbLinks = wx.CheckListBox(self, wx.ID_ANY, choices=self.choices)
        vsz.Add(self.lbLinks, 0, wx.ALIGN_CENTER_HORIZONTAL)
        vsz.AddSpacer(20)
        
        bsz = wx.BoxSizer(wx.HORIZONTAL)

        self.bOK = wx.Button(self, wx.ID_ANY, "OK")
        self.bOK.SetDefault()
        self.bCancel = wx.Button(self, wx.ID_ANY, "Cancel")

        bsz.Add(self.bOK)
        bsz.AddSpacer(30)
        bsz.Add(self.bCancel)

        self.Bind(wx.EVT_BUTTON, self.onOK, self.bOK)
        self.Bind(wx.EVT_BUTTON, self.onCancel, self.bCancel)

        vsz.Add(bsz, 0, wx.ALIGN_CENTER)
        vsz.AddSpacer(20)
        
        hsz = wx.BoxSizer(wx.HORIZONTAL)
        hsz.AddSpacer(20)
        hsz.Add(vsz)
        hsz.AddSpacer(20)
        
        self.SetSizer(hsz)
        self.Layout()
        self.Fit()
        
    def onCancel(self, _):
        self.EndModal(wx.ID_CANCEL)

    def onOK(self, _):
        self.EndModal(wx.ID_OK)
        
    def GetResults(self):
        return [self.choices[i] for i in self.lbLinks.GetCheckedItems()]
