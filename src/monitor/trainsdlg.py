import wx

class TrainsDlg(wx.Dialog):
    def __init__(self, parent, dlgExit, rrServer):
        wx.Dialog.__init__(self, parent, wx.ID_ANY, "Active Trains")
        self.Bind(wx.EVT_CLOSE, self.OnClose)
  
        self.dlgExit = dlgExit
        self.rrServer = rrServer

        vsz = wx.BoxSizer(wx.VERTICAL)       
        vsz.AddSpacer(20)
       
        hsz = wx.BoxSizer(wx.HORIZONTAL)
        hsz.AddSpacer(20)

        self.trCtl = TrainsListCtrl(self, self.rrServer)
        hsz.Add(self.trCtl)
        
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
        self.trCtl.RefreshTrains()
           
    def OnClose(self, _):
        self.dlgExit()
    

class TrainsListCtrl(wx.ListCtrl):
    def __init__(self, parent, rrServer):
        self.parent = parent
        self.rrServer = rrServer

        wx.ListCtrl.__init__(
            self, parent, wx.ID_ANY, size=(460, 160),
            style=wx.LC_REPORT|wx.LC_VIRTUAL|wx.LC_VRULES
            )

        self.trains = []
        self.selected = None

        self.InsertColumn(0, "Train")
        self.InsertColumn(1, "Loco")
        self.InsertColumn(2, "ATC")
        self.InsertColumn(3, "Signal")
        self.InsertColumn(4, "Aspect")
        self.InsertColumn(5, "Blocks")
        self.SetColumnWidth(0, 50)
        self.SetColumnWidth(1, 50)
        self.SetColumnWidth(2, 40)
        self.SetColumnWidth(3, 60)
        self.SetColumnWidth(4, 60)
        self.SetColumnWidth(5, 200)

        self.SetItemCount(0)

        self.normalA = wx.ItemAttr()
        self.normalB = wx.ItemAttr()
        self.normalA.SetBackgroundColour(wx.Colour(225, 255, 240))
        self.normalB.SetBackgroundColour(wx.Colour(138, 255, 197))

        self.sessions = []
        self.SetItemCount(0)
        
        self.RefreshTrains()
        
    def RefreshTrains(self):       
        self.trains = self.rrServer.Get("activetrains", {})
        self.trainNames = sorted(self.trains.keys())
        self.RefreshAll()
 
    def RefreshItemCount(self):
        self.SetItemCount(len(self.trains))

    def RefreshAll(self):
        self.RefreshItemCount()
        if self.GetItemCount() > 0:
            self.RefreshItems(0, self.GetItemCount()-1)

    def OnGetItemText(self, item, col):
        tr = self.trains[self.trainNames[item]]
        if col == 0:
            return self.trainNames[item]
        elif col == 1:
            try:
                loco = str(tr["loco"])
            except KeyError:
                loco = ""
            return "" if loco is None else loco
        
        elif col == 2:
            try:
                atc = str(tr["atc"])
            except KeyError:
                atc = ""
            return "" if atc is None else atc
        
        elif col == 3:
            try:
                signal = tr["signal"]
            except KeyError:
                signal = ""
            return "" if signal is None else signal
       
        elif col == 4:
            try:
                aspect = tr["aspect"]
            except KeyError:
                aspect = ""
            return "" if aspect is None else ("0x%x" % aspect)
        
        else:
            try:
                blks = tr["blocks"]
            except KeyError:
                blks = None
            return "" if blks is None else ", ".join(tr["blocks"])

    def OnGetItemAttr(self, item):
        if item % 2 == 1:
            return self.normalB
        else:
            return self.normalA
