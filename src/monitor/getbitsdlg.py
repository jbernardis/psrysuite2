import wx

def swapbyte(b):
    return int("0b"+"{0:08b}".format(b)[::-1], 2)

class GetBitsDlg(wx.Dialog):
    def __init__(self, parent, rrServer, Nodes):
        wx.Dialog.__init__(self, parent, wx.ID_ANY, "Get Bits")
        self.Bind(wx.EVT_CLOSE, self.onCancel)
  
        self.rrServer = rrServer
        self.Nodes = Nodes

        vsz = wx.BoxSizer(wx.VERTICAL)       
        vsz.AddSpacer(20)
       
        hsz = wx.BoxSizer(wx.HORIZONTAL)
        
        font = wx.Font(wx.Font(14, wx.FONTFAMILY_TELETYPE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, faceName="Monospace"))

        stO = wx.StaticText(self, wx.ID_ANY, "OUTPUTS:", size=(100, -1))
        stO.SetFont(font)
        self.stBitsO = wx.StaticText(self, wx.ID_ANY, "", size=(1000, -1)) 
        self.stBitsO.SetFont(font)
        stI = wx.StaticText(self, wx.ID_ANY, "INPUTS:", size=(100, -1))
        stI.SetFont(font)
        self.stBitsI = wx.StaticText(self, wx.ID_ANY, "", size=(1000, -1)) 
        self.stBitsI.SetFont(font)
        
        hsz.AddSpacer(20)
        hsz.Add(stO)
        hsz.AddSpacer(10)
        hsz.Add(self.stBitsO)
        vsz.Add(hsz)
         
        vsz.AddSpacer(10)

        hsz = wx.BoxSizer(wx.HORIZONTAL)
        hsz.AddSpacer(20)
        hsz.Add(stI)
        hsz.AddSpacer(10)
        hsz.Add(self.stBitsI)
        vsz.Add(hsz)
         
        vsz.AddSpacer(20)
        
       
        
        hsz = wx.BoxSizer(wx.HORIZONTAL)
        hsz.AddSpacer(20)
        
        self.chNodes = wx.Choice(self, wx.ID_ANY, choices=["%s (0x%x)" % (x[0], x[1]) for x in self.Nodes])
        hsz.Add(self.chNodes, 0, wx.TOP, 10)
        self.chNodes.SetSelection(0)
        
        hsz.AddSpacer(20)
         
        self.bGetBits = wx.Button(self, wx.ID_ANY, "Get Bits", size=(100, 46))
        self.Bind(wx.EVT_BUTTON, self.OnGetBits, self.bGetBits)
        hsz.Add(self.bGetBits)

        hsz.AddSpacer(20)

        self.scCount = wx.SpinCtrl(self, wx.ID_ANY, "1")
        self.scCount.SetRange(1,50)
        self.scCount.SetValue(1)
        
        hsz.Add(self.scCount, 0, wx.ALIGN_CENTRE_VERTICAL, 0)
        
        st = wx.StaticText(self, wx.ID_ANY, "Count")
        st.SetFont(font)
        hsz.AddSpacer(10)
        hsz.Add(st, 0, wx.ALIGN_CENTRE_VERTICAL, 0)
        
        hsz.AddSpacer(20)

        self.cbContinuous = wx.CheckBox(self, wx.ID_ANY, "Continuous")
        self.cbContinuous.SetFont(font)
        hsz.Add(self.cbContinuous, 0, wx.ALIGN_CENTRE_VERTICAL, 0)
        
        hsz.AddSpacer(20)
        
        self.stCounter = wx.StaticText(self, wx.ID_ANY, "    ")
        self.stCounter.SetFont(font)
        hsz.Add(self.stCounter,  0, wx.ALIGN_CENTRE_VERTICAL, 0)
             
        hsz.AddSpacer(20)
        
        vsz.AddSpacer(20)
        vsz.Add(hsz)
       
        vsz.AddSpacer(20)
               
        self.SetSizer(vsz)
        self.Layout()
        self.Fit()
        
        self.Bind(wx.EVT_TIMER, self.onTicker)
        self.ticker = wx.Timer(self)

    def OnGetBits(self, _):
        chx = self.chNodes.GetSelection()
        if chx == wx.NOT_FOUND:
            return 
        
        self.node = self.Nodes[chx][1]
        self.runContinuous = self.cbContinuous.IsChecked()
        self.sendCount = self.scCount.GetValue()
        
        if self.sendCount > 1 or self.runContinuous:
            self.ticker.Start(400)
            self.bGetBits.Enable(False)
            self.chNodes.Enable(False)
        
        self.messageCount = 0
            
        self.SendOnce()
        
    def onTicker(self, _):
        self.SendOnce()
        
    def SendOnce(self):
        self.messageCount += 1
        
        self.stCounter.SetLabel("%3d" % self.messageCount)
        
        r = self.rrServer.Get("getbits", {"address": "0x%x" % self.node})
        oStr = ""
        iStr = ""
        for oval, ival in zip(r["out"], r["in"]):
            oStr += "{0:08b}  ".format(swapbyte(oval))
            iStr += "{0:08b}  ".format(ival)
            
        self.stBitsI.SetLabel(iStr)
        self.stBitsO.SetLabel(oStr)
                
        if self.runContinuous:
            if not self.cbContinuous.IsChecked():
                self.ticker.Stop()
                self.bGetBits.Enable(True)
                self.chNodes.Enable(True)
        else:
            self.sendCount -= 1
            if self.sendCount <= 0:
                self.ticker.Stop()
                self.bGetBits.Enable(True)
                self.chNodes.Enable(True)
         
    def onCancel(self, _):
        try:
            self.ticker.Stop()
        except:
            pass
        
        self.runContinuous = False
        self.Destroy()
    
        
