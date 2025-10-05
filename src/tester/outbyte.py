import wx
import wx.lib.newevent


(OutputChangeEvent, EVT_OUTPUTCHANGE) = wx.lib.newevent.NewEvent() 

class OutByte(wx.StaticBox):
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
        for bt in bits:
            cb = wx.CheckBox(self, wx.ID_ANY, bt["label"])
            if not bt["used"]:
                cb.Enable(False)
            else:
                self.Bind(wx.EVT_CHECKBOX, lambda event, bn=n: self.EvtCB(event, bn), cb)

                
            boxSizer.Add(cb, 0, wx.LEFT, 10)
            boxSizer.AddSpacer(3)
            n += 1
  
        while n <= 7:
            cb = wx.CheckBox(self, wx.ID_ANY, "")
            cb.Enable(False)
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
        
    def GetValue(self):
        return self.value
        
    def EvtCB(self, evt, n):
        checked = evt.IsChecked()
        if checked:
            mask = 1 << n
            self.value |= mask
        else:
            mask = 255 ^ (1 << n)
            self.value &= mask
            
        nv = ("{0:08b}".format(self.value))
        self.stByteValue.SetLabel(nv[::-1])
        
        evt = OutputChangeEvent(index=self.byteNumber)
        wx.QueueEvent(self.parent, evt)


