import wx

class InByte(wx.StaticBox):
    def __init__(self, parent, label, byteNumber, bits):
        wx.StaticBox.__init__(self, parent, wx.ID_ANY, label)
        self.parent = parent
 
        self.byteNumber = byteNumber       
        self.value = 0
        
        boxSizer = wx.BoxSizer(wx.VERTICAL)
        topBorder, _ = self.GetBordersForSizer()
        boxSizer.AddSpacer(topBorder)
        boxSizer.Add(wx.StaticText(self, wx.ID_ANY, "", size=(150, -1)), 0, wx.ALL, 1)

        n = 0  
        self.cbs = []      
        for bt in bits:
            cb = wx.CheckBox(self, wx.ID_ANY, bt["label"])
            cb.Enable(bt["used"])
            self.cbs.append(cb)
            self.Bind(wx.EVT_CHECKBOX, self.cbIgnore, cb)
                 
            boxSizer.Add(cb, 0, wx.LEFT, 10)
            boxSizer.AddSpacer(3)
            n += 1
  
        while n <= 7:
            cb = wx.CheckBox(self, wx.ID_ANY, "")
            cb.Enable(False)
            self.cbs.append(cb)
            boxSizer.Add(cb, 0, wx.LEFT, 10)
            boxSizer.AddSpacer(3)
            n += 1
            
        boxSizer.AddSpacer(10)
        
        font = wx.Font(wx.Font(14, wx.FONTFAMILY_TELETYPE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, faceName="Monospace"))
        self.stByteValue = wx.StaticText(self, wx.ID_ANY, "00000000") 
        self.stByteValue.SetFont(font)
        boxSizer.Add(self.stByteValue, 0, wx.ALIGN_CENTER_HORIZONTAL)

        boxSizer.AddSpacer(10)
        self.SetSizer(boxSizer)
        
    def cbIgnore(self, evt):
        cb = evt.GetEventObject()
        cb.SetValue(not cb.GetValue())
        
    def SetValue(self, v):
        self.value = int.from_bytes(v, "little")
        
        for i in range(8):
            mask = 1 << (7-i)
            if self.value & mask != 0:
                self.cbs[i].SetValue(True)
            else:
                self.cbs[i].SetValue(False)
        
        nv = ("{0:08b}".format(self.value))
        self.stByteValue.SetLabel(nv)
 
