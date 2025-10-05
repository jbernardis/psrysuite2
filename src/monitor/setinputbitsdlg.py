import wx

class SetInputBitsDlg(wx.Dialog):
    def __init__(self, parent, Nodes):
        wx.Dialog.__init__(self, parent, wx.ID_ANY, "Set Input Bits")
        self.Bind(wx.EVT_CLOSE, self.onCancel)
 
        self.Nodes = Nodes

        vsz = wx.BoxSizer(wx.VERTICAL)   
        self.parent = parent    
        vsz.AddSpacer(20)
        
        font = wx.Font(wx.Font(14, wx.FONTFAMILY_TELETYPE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, faceName="Monospace"))

        hsz = wx.BoxSizer(wx.HORIZONTAL)
        hsz.AddSpacer(20)
        
        self.chNodes = wx.Choice(self, wx.ID_ANY, choices=["%s (0x%x)" % (x[0], x[1]) for x in self.Nodes])
        hsz.Add(self.chNodes, 0, wx.TOP, 10)
        self.chNodes.SetSelection(0)
        
        hsz.AddSpacer(20)
         
        self.bSetBits = wx.Button(self, wx.ID_ANY, "Set Bits", size=(100, 46))
        self.Bind(wx.EVT_BUTTON, self.OnSetBits, self.bSetBits)
        hsz.Add(self.bSetBits)
             
        hsz.AddSpacer(20)
        
        vsz.Add(hsz)
       
        vsz.AddSpacer(20)
        
        self.nbits = 4
        
        self.vbytes = [None for _ in range(self.nbits)]
        self.vbits =  [None for _ in range(self.nbits)]
        self.values = [None for _ in range(self.nbits)]
        self.include = [None for _ in range(self.nbits)]

        st = wx.StaticText(self, wx.ID_ANY, "Include:   Byte:    Bit:    Value:")
        st.SetFont(font)
        vsz.Add(st, 0, wx.LEFT | wx.RIGHT, 20)
        vsz.AddSpacer(5)
                
        for i in range(self.nbits): 
            hsz = wx.BoxSizer(wx.HORIZONTAL)      
            hsz.AddSpacer(50)
            
            cb = wx.CheckBox(self, wx.ID_ANY, "")
            cb.SetValue(True if i == 0 else False)
            hsz.Add(cb, 0, wx.TOP, 15)
            self.include[i] = cb
            
            hsz.AddSpacer(80)
                     
            sc = wx.SpinCtrl(self, wx.ID_ANY, "0")
            sc.SetRange(0, 10)
            sc.SetValue(0)
            hsz.Add(sc, 0, wx.TOP, 10)
            self.vbytes[i] = sc
                                    
            hsz.AddSpacer(54)
            
            sc = wx.SpinCtrl(self, wx.ID_ANY, "0")
            sc.SetRange(0, 7)
            sc.SetValue(0)
            hsz.Add(sc, 0, wx.TOP, 10)
            self.vbits[i] = sc
            
            hsz.AddSpacer(74)
            
            cb = wx.CheckBox(self, wx.ID_ANY, "")
            cb.SetValue(True)
            hsz.Add(cb, 0, wx.TOP, 15)
            self.values[i] = cb
            
            hsz.AddSpacer(20)
            vsz.Add(hsz)
            vsz.AddSpacer(4)
               
        vsz.AddSpacer(16)
        self.SetSizer(vsz)
        self.Layout()
        self.Fit()

    def OnSetBits(self, _):
        chx = self.chNodes.GetSelection()
        if chx == wx.NOT_FOUND:
            return 
        
        node = self.Nodes[chx][1]
        
        vbytes = []
        vbits = []
        vals = []
        for i in range(self.nbits):
            if self.include[i].IsChecked():
                vbytes.append(self.vbytes[i].GetValue())
                vbits.append(self.vbits[i].GetValue())
                vals.append(1 if self.values[i].IsChecked() else 0)
                
        req = {"setinbit": {"address": "0x%x" % node, "byte": vbytes, "bit": vbits, "value": vals}}
        self.parent.Request(req)

         
    def onCancel(self, _):
        self.Destroy()
    
        
