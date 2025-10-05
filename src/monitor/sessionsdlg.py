import wx

class SessionsDlg(wx.Dialog):
    def __init__(self, parent, dlgExit, rrServer):
        wx.Dialog.__init__(self, parent, wx.ID_ANY, "Server Sessions")
        self.Bind(wx.EVT_CLOSE, self.OnClose)
 
        self.dlgExit = dlgExit 
        self.rrServer = rrServer

        vsz = wx.BoxSizer(wx.VERTICAL)       
        vsz.AddSpacer(20)
       
        hsz = wx.BoxSizer(wx.HORIZONTAL)
        hsz.AddSpacer(20)

        self.sessCtl = SessionsListCtrl(self, self.rrServer)
        hsz.Add(self.sessCtl)
        
        hsz.AddSpacer(20)
        
        vsz.Add(hsz)
        
        self.bRefresh = wx.Button(self, wx.ID_ANY, "Refresh", size=(100, 46))
        self.Bind(wx.EVT_BUTTON, self.OnRefresh, self.bRefresh)
        
        vsz.AddSpacer(20)
        vsz.Add(self.bRefresh, 0, wx.ALIGN_CENTER_HORIZONTAL)
       
        vsz.AddSpacer(20)
               
        self.SetSizer(vsz)
        self.Layout()
        self.Fit()
        
    def OnRefresh(self, _):
        self.sessCtl.RefreshSessions()
           
    def OnClose(self, _):
        self.dlgExit()
    
        

class SessionsListCtrl(wx.ListCtrl):
    def __init__(self, parent, rrServer):
        self.parent = parent
        self.rrServer = rrServer

        wx.ListCtrl.__init__(
            self, parent, wx.ID_ANY, size=(320, 160),
            style=wx.LC_REPORT|wx.LC_VIRTUAL|wx.LC_VRULES
            )

        self.trains = []
        self.selected = None

        self.InsertColumn(0, "SID")
        self.InsertColumn(1, "Function")
        self.InsertColumn(2, "IP")
        self.InsertColumn(3, "Port")
        self.SetColumnWidth(0, 40)
        self.SetColumnWidth(1, 100)
        self.SetColumnWidth(2, 120)
        self.SetColumnWidth(3, 60)

        self.SetItemCount(0)

        self.normalA = wx.ItemAttr()
        self.normalB = wx.ItemAttr()
        self.normalA.SetBackgroundColour(wx.Colour(225, 255, 240))
        self.normalB.SetBackgroundColour(wx.Colour(138, 255, 197))

        self.sessions = []
        self.SetItemCount(0)
        
        self.RefreshSessions()
        
    def RefreshSessions(self):       
        self.sessions = self.rrServer.Get("sessions", {})
        self.RefreshAll()
 
    def RefreshItemCount(self):
        self.SetItemCount(len(self.sessions))

    def RefreshAll(self):
        self.RefreshItemCount()
        if self.GetItemCount() > 0:
            self.RefreshItems(0, self.GetItemCount()-1)

    def OnGetItemText(self, item, col):
        sess = self.sessions[item]
        return str(sess[col])

    def OnGetItemAttr(self, item):
        if item % 2 == 1:
            return self.normalB
        else:
            return self.normalA
