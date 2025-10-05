import wx  
import os
import re


class ChooseItemDlg(wx.Dialog):
    def __init__(self, parent, trains, allowentry, rrserver):
        wx.Dialog.__init__(self, parent, wx.ID_ANY, "")
        self.RRServer = rrserver
        self.Bind(wx.EVT_CLOSE, self.OnCancel)
        self.trains = trains
        self.allowentry = allowentry
        self.files = []
        
        self.suffix = ".trn" if trains else ".loco"
        self.directory = os.path.join("data", "trains" if self.trains else "locos")
        
        if trains:
            if allowentry:
                self.SetTitle("Choose/Enter train IDs file")
            else:
                self.SetTitle("Choose train IDs file")
        else:
            if allowentry:
                self.SetTitle("Choose/Enter loco #s file")
            else:
                self.SetTitle("Choose loco #s file")
        
        self.allowentry = allowentry

        vszr = wx.BoxSizer(wx.VERTICAL)
        vszr.AddSpacer(20)
        
        if allowentry:
            style = wx.CB_DROPDOWN
        else:
            style = wx.CB_DROPDOWN | wx.CB_READONLY    
            
        self.GetFiles()                
        
        cb = wx.ComboBox(self, 500, "", size=(160, -1), choices=self.files, style=style)
        self.cbItems = cb
        vszr.Add(cb, 0, wx.ALIGN_CENTER_HORIZONTAL)
        if not allowentry and len(self.files) > 0:
            self.cbItems.SetSelection(0)
        else:
            self.cbItems.SetSelection(wx.NOT_FOUND)
            
        if not allowentry:
            vszr.AddSpacer(20)

            hszr = wx.BoxSizer(wx.HORIZONTAL)
            hszr.AddSpacer(100)            
            self.cbCliff = wx.CheckBox(self, wx.ID_ANY, "Cliff")
            self.cbCliff.SetValue(True)
            hszr.Add(self.cbCliff)
            vszr.Add(hszr)
            
            hszr = wx.BoxSizer(wx.HORIZONTAL)
            hszr.AddSpacer(100)            
            self.cbNassau = wx.CheckBox(self, wx.ID_ANY, "Nassau")
            self.cbNassau.SetValue(True)
            hszr.Add(self.cbNassau)
            vszr.Add(hszr)
            
            hszr = wx.BoxSizer(wx.HORIZONTAL)
            hszr.AddSpacer(100)            
            self.cbHyde = wx.CheckBox(self, wx.ID_ANY, "Hyde")
            self.cbHyde.SetValue(True)
            hszr.Add(self.cbHyde)
            vszr.Add(hszr)
            
            hszr = wx.BoxSizer(wx.HORIZONTAL)
            hszr.AddSpacer(100)            
            self.cbPort = wx.CheckBox(self, wx.ID_ANY, "Port")
            self.cbPort.SetValue(True)
            hszr.Add(self.cbPort)
            vszr.Add(hszr)
            
            hszr = wx.BoxSizer(wx.HORIZONTAL)
            hszr.AddSpacer(100)            
            self.cbYard = wx.CheckBox(self, wx.ID_ANY, "Yard")
            self.cbYard.SetValue(True)
            hszr.Add(self.cbYard)
            vszr.Add(hszr)
            
            vszr.AddSpacer(5)
            
            hszr = wx.BoxSizer(wx.HORIZONTAL)
            hszr.AddSpacer(100)            
            self.cbOthers = wx.CheckBox(self, wx.ID_ANY, "Other locations")
            self.cbOthers.SetValue(True)
            hszr.Add(self.cbOthers)
            vszr.Add(hszr)
            
            vszr.AddSpacer(5)
            
            bAll = wx.Button(self, wx.ID_ANY, "All")
            self.Bind(wx.EVT_BUTTON, self.OnBAll, bAll)
            bNone = wx.Button(self, wx.ID_ANY, "None")
            self.Bind(wx.EVT_BUTTON, self.OnBNone, bNone)
            
            hsz = wx.BoxSizer(wx.HORIZONTAL)
            hsz.Add(bAll)
            hsz.AddSpacer(30)
            hsz.Add(bNone)
            
            vszr.Add(hsz, 0, wx.ALIGN_CENTER_HORIZONTAL)
        
        vszr.AddSpacer(20)
        
        btnszr = wx.BoxSizer(wx.HORIZONTAL)
        
        bOK = wx.Button(self, wx.ID_ANY, "OK")
        bOK.SetDefault()
        self.Bind(wx.EVT_BUTTON, self.OnBOK, bOK)
        
        bCancel = wx.Button(self, wx.ID_ANY, "Cancel")
        self.Bind(wx.EVT_BUTTON, self.OnCancel, bCancel)
        
        bDelete = wx.Button(self, wx.ID_ANY, "Delete")
        self.Bind(wx.EVT_BUTTON, self.OnDelete, bDelete)
        
        btnszr.Add(bOK)
        btnszr.AddSpacer(20)
        btnszr.Add(bCancel)
        btnszr.AddSpacer(20)
        btnszr.Add(bDelete)
        
        vszr.Add(btnszr, 0, wx.ALIGN_CENTER_HORIZONTAL)
        
        vszr.AddSpacer(20)
                
        hszr = wx.BoxSizer(wx.HORIZONTAL)
        hszr.AddSpacer(20)
        hszr.Add(vszr)
        
        hszr.AddSpacer(20)
        
        self.SetSizer(hszr)
        self.Layout()
        self.Fit()
        
    def OnBAll(self, _):
        self.SetLocations(True)
        
    def OnBNone(self, _):
        self.SetLocations(False)
        
    def SetLocations(self, flag):
        self.cbCliff.SetValue(flag)
        self.cbNassau.SetValue(flag)
        self.cbHyde.SetValue(flag)
        self.cbPort.SetValue(flag)
        self.cbYard.SetValue(flag)
        self.cbOthers.SetValue(flag)
        
    def GetFiles(self):
        fl = self.RRServer.Get("listdir", {"dir": self.directory})
        self.files = sorted([os.path.splitext(f)[0] for f in fl if f.lower().endswith(self.suffix)])
        
    def GetFile(self):
        fn = self.cbItems.GetValue()
        if fn is None or fn == "":
            return None, None
        
        return fn+self.suffix, self.directory
        
    def GetLocations(self):
        if self.allowentry:
            return None
        
        locations = ""
        if self.cbCliff.IsChecked():
            locations += "C"
        if self.cbNassau.IsChecked():
            locations += "N"
        if self.cbHyde.IsChecked():
            locations += "H"
        if self.cbPort.IsChecked():
            locations += "P"
        if self.cbYard.IsChecked():
            locations += "Y"
        if self.cbOthers.IsChecked():
            locations += "*"
            
        return locations, "CNHPY"

    def OnCancel(self, _):
        self.EndModal(wx.ID_CANCEL)
        
    def OnBOK(self, _):
        fn = self.cbItems.GetValue()
        if fn in self.files and self.allowentry:
            dlg = wx.MessageDialog(self, "File '%s' already exists.\n Are you sure you want to over-write it?" % fn,
                "File exists", wx.YES_NO | wx.NO_DEFAULT | wx.ICON_WARNING)
            rv = dlg.ShowModal()
            dlg.Destroy()
            if rv == wx.ID_NO:
                return

        self.EndModal(wx.ID_OK)
        
    def OnDelete(self, _):
        l = None
        dlg = ChooseItemsDlg(self, self.files, self.trains)
        rc = dlg.ShowModal()
        if rc == wx.ID_OK:
            l = dlg.GetFiles()
            
        dlg.Destroy()
        if rc != wx.ID_OK:
            return 

        if len(l) == 0:
            return 
                
        for fn in l:
            self.RRServer.Get("delfile", {"file": fn+self.suffix, "dir": self.directory})
            
        self.GetFiles()
        self.cbItems.SetItems(self.files)
        if not self.allowentry and len(self.files) > 0:
            self.cbItems.SetSelection(0)
        else:
            self.cbItems.SetSelection(wx.NOT_FOUND)


class ChooseItemsDlg(wx.Dialog):
    def __init__(self, parent, items, trains):
        wx.Dialog.__init__(self, parent, wx.ID_ANY, "")
        self.Bind(wx.EVT_CLOSE, self.OnCancel)
        if trains:
            self.SetTitle("Choose train file(s) to delete")
        else:
            self.SetTitle("Choose loco file(s) to delete")

        vszr = wx.BoxSizer(wx.VERTICAL)
        vszr.AddSpacer(20)
        
        cb = wx.CheckListBox(self, wx.ID_ANY, size=(160, -1), choices=items)
        self.cbItems = cb
        vszr.Add(cb, 0, wx.ALIGN_CENTER_HORIZONTAL)
        
        vszr.AddSpacer(20)
        
        btnszr = wx.BoxSizer(wx.HORIZONTAL)
        
        bOK = wx.Button(self, wx.ID_ANY, "OK")
        self.Bind(wx.EVT_BUTTON, self.OnBOK, bOK)
        
        bCancel = wx.Button(self, wx.ID_ANY, "Cancel")
        self.Bind(wx.EVT_BUTTON, self.OnCancel, bCancel)
        
        btnszr.Add(bOK)
        btnszr.AddSpacer(20)
        btnszr.Add(bCancel)
        
        vszr.Add(btnszr, 0, wx.ALIGN_CENTER_HORIZONTAL)
        
        vszr.AddSpacer(20)
                
        hszr = wx.BoxSizer(wx.HORIZONTAL)
        hszr.AddSpacer(20)
        hszr.Add(vszr)
        
        hszr.AddSpacer(20)
        
        self.SetSizer(hszr)
        self.Layout()
        self.Fit()
            
    def OnCancel(self, _):
        self.EndModal(wx.ID_CANCEL)
        
    def OnBOK(self, _):
        self.EndModal(wx.ID_OK)
        
    def GetFiles(self):
        return self.cbItems.GetCheckedStrings()


class ChooseBlocksDlg(wx.Dialog):
    def __init__(self, parent, tid, blocklist):
        wx.Dialog.__init__(self, parent, wx.ID_ANY, "")
        self.Bind(wx.EVT_CLOSE, self.OnCancel)
        self.SetTitle("Split block(s) from train %s" % tid)

        vszr = wx.BoxSizer(wx.VERTICAL)
        vszr.AddSpacer(20)
        
        st = wx.StaticText(self, wx.ID_ANY, "Choose block(s) to split to a new train")
        vszr.Add(st, 0, wx.ALIGN_CENTER_HORIZONTAL)
        vszr.AddSpacer(10)
        
        cb = wx.CheckListBox(self, wx.ID_ANY, size=(160, -1), choices=blocklist)
        self.cbItems = cb
        vszr.Add(cb, 0, wx.ALIGN_CENTER_HORIZONTAL)
        
        vszr.AddSpacer(20)
        
        btnszr = wx.BoxSizer(wx.HORIZONTAL)
        
        bOK = wx.Button(self, wx.ID_ANY, "OK")
        self.Bind(wx.EVT_BUTTON, self.OnBOK, bOK)
        
        bCancel = wx.Button(self, wx.ID_ANY, "Cancel")
        self.Bind(wx.EVT_BUTTON, self.OnCancel, bCancel)
        
        btnszr.Add(bOK)
        btnszr.AddSpacer(20)
        btnszr.Add(bCancel)
        
        vszr.Add(btnszr, 0, wx.ALIGN_CENTER_HORIZONTAL)
        
        vszr.AddSpacer(20)
                
        hszr = wx.BoxSizer(wx.HORIZONTAL)
        hszr.AddSpacer(20)
        hszr.Add(vszr)
        
        hszr.AddSpacer(20)
        
        self.SetSizer(hszr)
        self.Layout()
        self.Fit()
        
    def GetResults(self):
        return list(self.cbItems.GetCheckedStrings())
        
    def OnCancel(self, _):
        self.EndModal(wx.ID_CANCEL)
        
    def OnBOK(self, _):
        self.EndModal(wx.ID_OK)
        

class ChooseTrainDlg(wx.Dialog):
    def __init__(self, parent, tid, trainlist, merge=True):
        wx.Dialog.__init__(self, parent, wx.ID_ANY, "")
        self.Bind(wx.EVT_CLOSE, self.OnCancel)
        self.SetTitle("Choose train")

        vszr = wx.BoxSizer(wx.VERTICAL)
        vszr.AddSpacer(20)
        
        action = "merge" if merge else "swap"
        st = wx.StaticText(self, wx.ID_ANY, "Choose train to %s with %s" % (action, tid))
        vszr.Add(st, 0, wx.ALIGN_CENTER_HORIZONTAL)
        vszr.AddSpacer(10)

        cb = wx.ListBox(self, wx.ID_ANY, size=(160, -1), choices=trainlist, style=wx.LB_SINGLE)
        self.cbItems = cb
        vszr.Add(cb, 0, wx.ALIGN_CENTER_HORIZONTAL)
        
        vszr.AddSpacer(20)
        
        btnszr = wx.BoxSizer(wx.HORIZONTAL)
        
        bOK = wx.Button(self, wx.ID_ANY, "OK")
        self.Bind(wx.EVT_BUTTON, self.OnBOK, bOK)
        
        bCancel = wx.Button(self, wx.ID_ANY, "Cancel")
        self.Bind(wx.EVT_BUTTON, self.OnCancel, bCancel)
        
        btnszr.Add(bOK)
        btnszr.AddSpacer(20)
        btnszr.Add(bCancel)
        
        vszr.Add(btnszr, 0, wx.ALIGN_CENTER_HORIZONTAL)
        
        vszr.AddSpacer(20)
                
        hszr = wx.BoxSizer(wx.HORIZONTAL)
        hszr.AddSpacer(20)
        hszr.Add(vszr)
        
        hszr.AddSpacer(20)
        
        self.SetSizer(hszr)
        self.Layout()
        self.Fit()
        
    def GetResults(self):
        idx = self.cbItems.GetSelection()
        if idx == wx.NOT_FOUND:
            return None
        
        return self.cbItems.GetString(idx)
        
    def OnCancel(self, _):
        self.EndModal(wx.ID_CANCEL)
        
    def OnBOK(self, _):
        self.EndModal(wx.ID_OK)


BTNDIM = (120, 40)


class ChooseSnapshotActionDlg(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, wx.ID_ANY, "Choose snapshot sction")
        self.Bind(wx.EVT_CLOSE, self.OnCancel)
        
        vszr = wx.BoxSizer(wx.VERTICAL)

        vszr.AddSpacer(20)
        
        bSave = wx.Button(self, wx.ID_ANY, "Save", size=BTNDIM)
        self.Bind(wx.EVT_BUTTON, self.OnBSave, bSave)
        vszr.Add(bSave, 0, wx.ALIGN_CENTER_HORIZONTAL)

        vszr.AddSpacer(20)

        bRestore = wx.Button(self, wx.ID_ANY, "Restore Latest", size=BTNDIM)
        self.Bind(wx.EVT_BUTTON, self.OnBRestore, bRestore)
        vszr.Add(bRestore, 0, wx.ALIGN_CENTER_HORIZONTAL)

        vszr.AddSpacer(20)

        bSelect = wx.Button(self, wx.ID_ANY, "Restore Selected", size=BTNDIM)
        self.Bind(wx.EVT_BUTTON, self.OnBSelect, bSelect)
        vszr.Add(bSelect, 0, wx.ALIGN_CENTER_HORIZONTAL)

        vszr.AddSpacer(30)

        hszr = wx.BoxSizer(wx.HORIZONTAL)
        hszr.AddSpacer(30)
        
        bCancel = wx.Button(self, wx.ID_ANY, "Cancel", size=BTNDIM)
        self.Bind(wx.EVT_BUTTON, self.OnCancel, bCancel)
        hszr.Add(bCancel, 0)

        hszr.AddSpacer(30)

        vszr.Add(hszr)
        
        vszr.AddSpacer(20)
       
        self.SetSizer(vszr)
        self.Layout()
        self.Fit()
        self.CenterOnScreen()
        
    def OnBSave(self, _):
        self.EndModal(wx.ID_SAVE)

    def OnBRestore(self, _):
        self.EndModal(wx.ID_OPEN)

    def OnBSelect(self, _):
        self.EndModal(wx.ID_SELECTALL)

    def OnCancel(self, _):
        self.EndModal(wx.ID_CANCEL)


mname = {
    "01": "Jan",
    "02": "Feb",
    "03": "Mar",
    "04": "Apr",
    "05": "May",
    "06": "Jun",
    "07": "Jul",
    "08": "Aug",
    "09": "Sep",
    "10": "Oct",
    "11": "Nov",
    "12": "Dec"
}


class ChooseSnapshotDlg(wx.Dialog):
    def __init__(self, parent, snaplist):
        wx.Dialog.__init__(self, parent, wx.ID_ANY, "")
        self.Bind(wx.EVT_CLOSE, self.OnCancel)
        self.SetTitle("Choose Snapshot to load")

        self.font = wx.Font(wx.Font(14, wx.FONTFAMILY_ROMAN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, faceName="Arial"))

        self.rexp = r"snapshot(\d\d\d\d)(\d\d)(\d\d)-(\d\d)(\d\d)(\d\d)"

        self.snapList = [s for s in snaplist]
        timeList = [self.IsolateTimeStamp(x) for x in snaplist]

        vszr = wx.BoxSizer(wx.VERTICAL)
        vszr.AddSpacer(20)

        rbStyle = wx.RB_GROUP
        self.radios = []
        for t in timeList:
            rb = wx.RadioButton(self, wx.ID_ANY, t, style=rbStyle)
            rb.SetFont(self.font)
            self.radios.append(rb)
            rbStyle = 0
            vszr.Add(rb)
            vszr.AddSpacer(10)

        vszr.AddSpacer(20)
        self.radios[-1].SetValue(True)

        btnszr = wx.BoxSizer(wx.HORIZONTAL)

        bOK = wx.Button(self, wx.ID_ANY, "OK")
        self.Bind(wx.EVT_BUTTON, self.OnBOK, bOK)

        bCancel = wx.Button(self, wx.ID_ANY, "Cancel")
        self.Bind(wx.EVT_BUTTON, self.OnCancel, bCancel)

        btnszr.Add(bOK)
        btnszr.AddSpacer(20)
        btnszr.Add(bCancel)

        vszr.Add(btnszr, 0, wx.ALIGN_CENTER_HORIZONTAL)

        vszr.AddSpacer(20)

        hszr = wx.BoxSizer(wx.HORIZONTAL)
        hszr.AddSpacer(20)
        hszr.Add(vszr)

        hszr.AddSpacer(20)

        self.SetSizer(hszr)
        self.Layout()
        self.Fit()

    def IsolateTimeStamp(self, fn):
        m = re.match(self.rexp, fn)
        year, month, day, hour, minute, second = m.group(1, 2, 3, 4, 5, 6)
        return year + "/" + mname[month] + "/" + ("%2d" % int(day)) + "-" + ("%02d" % int(hour)) + ":" + minute + ":" + second

    def GetResults(self):
        for i in range(len(self.radios)):
            if self.radios[i].GetValue():
                return self.snapList[i]
        return self.snapList[0]

    def OnCancel(self, _):
        self.EndModal(wx.ID_CANCEL)

    def OnBOK(self, _):
        self.EndModal(wx.ID_OK)

