import wx
import os
from glob import glob
import json

class ChooseNodeDlg(wx.Dialog):
    def __init__(self, parent, refOnly):
        wx.Dialog.__init__(self, parent, wx.ID_ANY, "Choose Node")
        self.CenterOnScreen()
        self.Bind(wx.EVT_CLOSE, self.OnCancel)
        
        style = wx.CB_DROPDOWN | wx.CB_READONLY    
            
        self.GetFiles()                
        
        cb = wx.ComboBox(self, 500, "", size=(160, -1), choices=sorted(self.files.keys()), style=style)
        self.cbItems = cb
        
        vszr = wx.BoxSizer(wx.VERTICAL)
        vszr.Add(cb, 0, wx.ALIGN_CENTER_HORIZONTAL)
        if len(self.files) > 0:
            self.cbItems.SetSelection(0)
        else:
            self.cbItems.SetSelection(wx.NOT_FOUND)
        
        vszr.AddSpacer(20)
        
        self.cbReferenceOnly = wx.CheckBox(self, wx.ID_ANY, "Reference Only")
        vszr.Add(self.cbReferenceOnly, 0, wx.ALIGN_CENTER_HORIZONTAL)
        self.cbReferenceOnly.SetValue(refOnly)
        vszr.AddSpacer(20)
        
        btnszr = wx.BoxSizer(wx.HORIZONTAL)
        
        bOK = wx.Button(self, wx.ID_ANY, "OK")
        bOK.SetDefault()
        self.Bind(wx.EVT_BUTTON, self.OnBOK, bOK)
        btnszr.Add(bOK)
        
        vszr.Add(btnszr, 0, wx.ALIGN_CENTER_HORIZONTAL)
        
        vszr.AddSpacer(20)
                
        hszr = wx.BoxSizer(wx.HORIZONTAL)
        hszr.AddSpacer(20)
        hszr.Add(vszr)
        
        hszr.AddSpacer(20)
        
        self.SetSizer(hszr)
        self.Layout()
        self.Fit();

        
    def GetFiles(self):
        fxp = os.path.join(os.getcwd(), "tester", "nodes", "*.json")
        fnames = glob(fxp)
        self.files = {}
        for fn in fnames:
            with open(fn, "r") as jfp:
                j = json.load(jfp)
                self.files["%2x: %s" % (j["address"], j["description"])] = os.path.splitext(os.path.split(fn)[1])[0]                               
                
    def GetValue(self):
        fnk = self.cbItems.GetValue()
        if fnk is None or fnk == "":
            return None
        
        fn = self.files[fnk]
        
        refOnly = self.cbReferenceOnly.IsChecked()
        
        return os.path.join(os.getcwd(), "tester", "nodes", fn+".json"), refOnly
 
    def OnBOK(self, _):
        self.EndModal(wx.ID_OK)
               
    def OnCancel(self, _):
        self.EndModal(wx.ID_CANCEL)

