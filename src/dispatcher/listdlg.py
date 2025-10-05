import wx
import os


class ListDlg(wx.Dialog):
    def __init__(self, parent, title, dataList, dlgexit, dataclear):
        wx.Dialog.__init__(self, parent, style=wx.DEFAULT_FRAME_STYLE)
        
        self.parent = parent
        self.dlgexit = dlgexit
        self.dataclear = dataclear
        
        self.SetTitle(title)
        self.title = title
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        
        font = wx.Font(wx.Font(18, wx.FONTFAMILY_ROMAN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, faceName="Arial"))

        vsz = wx.BoxSizer(wx.VERTICAL)
        vsz.AddSpacer(20)

        data = "\n".join(dataList)
        tcList = wx.TextCtrl(self, wx.ID_ANY, data,
                size=(800, 460), style=wx.TE_MULTILINE)
        tcList.SetFont(font)
        tcList.ShowPosition(len(data))
        vsz.Add(tcList)
        vsz.AddSpacer(10)
        self.tcList = tcList
        
        bsz = wx.BoxSizer(wx.HORIZONTAL)
        
        self.bClear = wx.Button(self, wx.ID_ANY, "Clear")
        self.Bind(wx.EVT_BUTTON, self.OnBClear, self.bClear)
        bsz.Add(self.bClear)

        bsz.AddSpacer(50)

        self.bExit = wx.Button(self, wx.ID_ANY, "Close")
        self.Bind(wx.EVT_BUTTON, self.OnBExit, self.bExit)
        bsz.Add(self.bExit)

        bsz.AddSpacer(50)

        self.bSave = wx.Button(self, wx.ID_ANY, "Save")
        self.Bind(wx.EVT_BUTTON, self.OnBSave, self.bSave)
        bsz.Add(self.bSave)

        vsz.Add(bsz, 0, wx.ALIGN_CENTER_HORIZONTAL)
        
        vsz.AddSpacer(20)
        
        hsz = wx.BoxSizer(wx.HORIZONTAL)
        hsz.AddSpacer(20)
        
        hsz.Add(vsz)
        hsz.AddSpacer(20)
        
        self.SetSizer(hsz)
        
        self.Fit()
        self.Layout()
        
    def AddItem(self, msg):
        self.tcList.AppendText("\n"+msg)
        
    def OnBClear(self, _):
        self.tcList.Clear()
        self.dataclear()

    def OnBSave(self, _):
        wildcard = "All files (*.*)|*.*"

        dlg = wx.FileDialog(
            self, message="Save %s as ..." % self.title, defaultDir=os.path.join(os.getcwd(), "output"),
            defaultFile="", wildcard=wildcard, style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT
            )

        rc = dlg.ShowModal()
        path = None
        if rc == wx.ID_OK:
            path = dlg.GetPath()

        dlg.Destroy()

        if rc != wx.ID_OK:
            return

        with open(path, "w") as ofp:
            ofp.write(self.tcList.GetValue())

        dlg = wx.MessageDialog(self,
                "%s successfully saved to %s" % (self.title, path),
                "%s Saved" % self.title,
                wx.OK | wx.ICON_INFORMATION)

        dlg.ShowModal()
        dlg.Destroy()

    def OnClose(self, _):
        self.DoClose()
        
    def OnBOK(self, _):
        self.DoClose()
        
    def OnBExit(self, _):
        self.DoClose()
        
    def DoClose(self):
        self.dlgexit()
