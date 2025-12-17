import wx  
import json
import logging

BSIZE = (120, 40)
skipBlocks = ["KOSN10S11", "KOSN20S21"]


class InspectDlg(wx.Dialog):
    def __init__(self, parent, closer, settings):
        wx.Dialog.__init__(self, parent, wx.ID_ANY, "")
        self.CenterOnScreen()
        self.parent = parent
        self.closer = closer
        self.settings = settings
        self.Bind(wx.EVT_CLOSE, self.OnCancel)

        self.SetTitle("Inspection Dialog")

        btnszr1 = wx.BoxSizer(wx.VERTICAL)
        btnszr1.AddSpacer(20)

        bLogLevel = wx.Button(self, wx.ID_ANY, "Logging Level", size=BSIZE)
        self.Bind(wx.EVT_BUTTON, self.OnBLogLevel, bLogLevel)
        btnszr1.Add(bLogLevel)

        btnszr1.AddSpacer(10)

        bDebug = wx.Button(self, wx.ID_ANY, "Debugging Flags", size=BSIZE)
        self.Bind(wx.EVT_BUTTON, self.OnBDebug, bDebug)
        btnszr1.Add(bDebug)

        btnszr1.AddSpacer(10)

        bProxies = wx.Button(self, wx.ID_ANY, "OS Proxies", size=BSIZE)
        self.Bind(wx.EVT_BUTTON, self.OnBProxies, bProxies)
        btnszr1.Add(bProxies)

        btnszr1.AddSpacer(10)

        bNodes = wx.Button(self, wx.ID_ANY, "Node Status", size=BSIZE)
        self.Bind(wx.EVT_BUTTON, self.OnBNodes, bNodes)
        btnszr1.Add(bNodes)

        btnszr1.AddSpacer(20)

        btnszr2 = wx.BoxSizer(wx.VERTICAL)
        btnszr2.AddSpacer(20)

        bRelays = wx.Button(self, wx.ID_ANY, "Stop Relays", size=BSIZE)
        self.Bind(wx.EVT_BUTTON, self.OnBRelays, bRelays)
        btnszr2.Add(bRelays)

        btnszr2.AddSpacer(10)

        bLevers = wx.Button(self, wx.ID_ANY, "Signal Levers", size=BSIZE)
        self.Bind(wx.EVT_BUTTON, self.OnBLevers, bLevers)
        btnszr2.Add(bLevers)

        btnszr2.AddSpacer(10)

        bToLocks = wx.Button(self, wx.ID_ANY, "Turnout Locks", size=BSIZE)
        self.Bind(wx.EVT_BUTTON, self.OnBTurnoutLocks, bToLocks)
        btnszr2.Add(bToLocks)

        btnszr2.AddSpacer(10)

        bAuditTrains = wx.Button(self, wx.ID_ANY, "Audit Trains", size=BSIZE)
        self.Bind(wx.EVT_BUTTON, self.OnBAuditTrains, bAuditTrains)
        btnszr2.Add(bAuditTrains)

        btnszr2.AddSpacer(20)

        btnszr3 = wx.BoxSizer(wx.VERTICAL)
        btnszr3.AddSpacer(20)

        bHandSwitches = wx.Button(self, wx.ID_ANY, "Siding Locks", size=BSIZE)
        self.Bind(wx.EVT_BUTTON, self.OnBHandSwitches, bHandSwitches)
        btnszr3.Add(bHandSwitches)

        btnszr3.AddSpacer(10)

        bResetBlks = wx.Button(self, wx.ID_ANY, "Reset Blocks", size=BSIZE)
        self.Bind(wx.EVT_BUTTON, self.OnBResetBlks, bResetBlks)
        btnszr3.Add(bResetBlks)

        btnszr3.AddSpacer(10)

        bIgnoreBlks = wx.Button(self, wx.ID_ANY, "Ignore Blocks", size=BSIZE)
        self.Bind(wx.EVT_BUTTON, self.OnBIgnoreBlks, bIgnoreBlks)
        btnszr3.Add(bIgnoreBlks)

        btnszr3.AddSpacer(20)

        btnszr = wx.BoxSizer(wx.HORIZONTAL)

        btnszr.AddSpacer(20)
        btnszr.Add(btnszr1)
        btnszr.AddSpacer(10)
        btnszr.Add(btnszr2)
        btnszr.AddSpacer(10)
        btnszr.Add(btnszr3)
        btnszr.AddSpacer(20)

        self.SetSizer(btnszr)
        self.Layout()
        self.Fit()

    def OnBLogLevel(self, _):
        dlg = LogLevelDlg(self)
        rc = dlg.ShowModal()
        if rc == wx.ID_OK:
            lvl = dlg.GetResults()
            self.parent.SendLogLevel(lvl)

        dlg.Destroy()

    def OnBDebug(self, _):
        dlg = DebugFlagsDlg(self, self.settings)
        rc = dlg.ShowModal()
        if rc == wx.ID_OK:
            dlg.ApplyResults()
            self.parent.SendDebugFlags()
        dlg.Destroy()

    def OnBProxies(self, _):
        pi = self.parent.GetOSProxyInfo()
        if pi is None:
            pi = []
        dlg = OSProxyDlg(self, pi, self.parent.GetOSProxyInfo)
        dlg.ShowModal()
        dlg.Destroy()

    def OnBRelays(self, _):
        rlAct, rlInact = self.GetRelayList()

        dlg = RelayDlg(self, rlAct, rlInact)
        rc = dlg.ShowModal()
        if rc == wx.ID_OK:
            newRlAct, newRlInact = dlg.GetRelays()

        dlg.Destroy()
        if rc != wx.ID_OK:
            return

        tobeActivated = [r for r in newRlAct if r not in rlAct]
        tobeDeactivated = [r for r in newRlInact if r not in rlInact]

        if len(tobeActivated) == 0 and len(tobeDeactivated) == 0:
            return

        for bn in tobeActivated:
            self.parent.SetStoppingRelays(bn, True, force=True)
        for bn in tobeDeactivated:
            self.parent.SetStoppingRelays(bn, False, force=True)

        msg = []
        if len(tobeActivated) != 0:
            msg.append("  Activated: %s" % ", ".join(tobeActivated))
        if len(tobeDeactivated) != 0:
            msg.append("Deactivated: %s" % ", ".join(tobeDeactivated))
        dlg = wx.MessageDialog(self, "\n".join(msg),
            "Stopping Relays",
            wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()

    def GetRelayList(self):
        rl = self.parent.Get("stoprelays", {})

        if rl is None:
            return []
        relaysActive = [self.formatRelayName(rly) for rly in sorted(rl.keys()) if rl[rly]]
        relaysInactive = [self.formatRelayName(rly) for rly in sorted(rl.keys()) if not rl[rly]]
        return relaysActive, relaysInactive

    def formatRelayName(self, rn):
        return rn.split(".")[0]

    def OnBLevers(self, _):
        slv = self.GetSignalLeverValues()
        dlg = ListDlg(self, slv, (200, 200), "Signal Levers", self.GetSignalLeverValues)
        dlg.ShowModal()
        dlg.Destroy()

    def OnBTurnoutLocks(self, _):
        lks = self.parent.GetTurnoutLocks()
        toList = ["%s: %s" % (x, ", ".join(lks[x])) for x in sorted(lks.keys())]
        if len(toList) == 0:
            dlg = wx.MessageDialog(self, "No turnouts are presently locked",
                "Turnout Locks",
                wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return

        dlg = wx.MultiChoiceDialog( self,
            "Choose turnout(s) to unlock",
            "Turnout Locks", toList)

        rc = dlg.ShowModal()
        if rc == wx.ID_OK:
            selections = dlg.GetSelections()
            toNames = [toList[x] for x in selections]
        else:
            toNames = []

        dlg.Destroy()
        if rc != wx.ID_OK:
            return

        if len(toNames) == 0:
            return

        tl = []
        for t in toNames:
            try:
                tx = t.index(":")
            except ValueError:
                tx = None
            if tx is not None:
                tl.append(t[:tx])

        self.parent.ClearLocks(tl)

        dlg = wx.MessageDialog(self, "Requested Turnout(s) Unlock:\n%s" % ", ".join(tl),
            "Turnout Locks",
            wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()

    def GetSignalLeverValues(self):
        sl = self.parent.Get("signallevers", {})
        if sl is None:
            return []

        leverList = ["%-6.6s   %s" % (lvr, self.formatSigLvr(sl[lvr])) for lvr in sorted(sl.keys())]
        return leverList

    def formatSigLvr(self, data):
        dl = 0 if data[0] is None else data[0]
        dc = 0 if data[1] is None else data[1]
        dr = 0 if data[2] is None else data[2]

        callon = " C" if dc != 0 else "  "

        if dl != 0 and dr == 0:
            return "L  " + callon
        elif dl == 0 and dr != 0:
            return "  R" + callon
        elif dl == 0 and dr == 0:
            return " N " + callon
        else:
            return " ? " + callon

    def OnBAuditTrains(self, _):
        messages = self.parent.Get("audittrains", {})

        logging.debug("********** Train/Block Audit Start **********")
        for ml in messages:
            logging.debug(ml)

        logging.debug("********** Train/Block Audit End ************")

        dlg = wx.MessageDialog(self, "\n".join(messages),
                               "Train/Block Audit",
                               wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()

    def OnBHandSwitches(self, _):
        hsv = self.GetHandswitchValues()
        dlg = ListDlg(self, hsv, (260, 200), "Siding Locks", self.GetHandswitchValues)
        dlg.ShowModal()
        dlg.Destroy()

    def GetHandswitchValues(self):
        hsinfo = self.parent.GetHandswitchInfo()
        if hsinfo is None:
            return []
        hsList = ["%-9.9s   %s" % (hs, str(hsinfo[hs])) for hs in sorted(hsinfo.keys())]
        return hsList

    def OnBNodes(self, _):
        nodeList = self.parent.GetNodes()
        dlg = NodeStatusDlg(self, nodeList, self.parent.GetNodes)
        dlg.ShowModal()
        dlg.Destroy()

    def ReEnableNodes(self, dislist):
        self.parent.ReEnableNodes(dislist)

    def OnBResetBlks(self, _):
        resetList = []
        blks = sorted([bn for bn, blk in self.parent.blocks.items() if (blk.IsCleared() and bn not in skipBlocks)])
        dlg = CheckListDlg(self, blks, "Choose Block(s) to reset")
        rc = dlg.ShowModal()
        if rc == wx.ID_OK:
            resetList = dlg.GetCheckedItems()

        dlg.Destroy()
        if rc != wx.ID_OK:
            return

        self.parent.Request({"resetblocks": {"blocks": resetList}})

    def OnBIgnoreBlks(self, _):
        ignoreIndices = []
        blks = sorted(list(self.parent.blocks.keys()))
        dlg = CheckListDlg(self, blks, "Choose Block(s) to ignore", prechecked=self.settings.rrserver.ignoredblocks)
        rc = dlg.ShowModal()
        if rc == wx.ID_OK:
            ignoreList = dlg.GetCheckedItems()

        dlg.Destroy()
        if rc != wx.ID_OK:
            return

        logging.info("New ignore list: %s" % str(ignoreList))
        self.parent.SetIgnoredBlocks(ignoreList)
        self.settings.rrserver.ignoredblocks = ignoreList

    def OnCancel(self, _):
        self.closer()


class RelayDlg(wx.Dialog):
    def __init__(self, parent, rlAct, rlInact):
        wx.Dialog.__init__(self, parent, wx.ID_ANY, "Choose Relays")
        self.Bind(wx.EVT_CLOSE, self.OnCancel)

        vsz = wx.BoxSizer(wx.VERTICAL)
        vsz.AddSpacer(20)

        st = wx.StaticText(self, wx.ID_ANY, "Check/Uncheck to Activate/Deactivate")
        vsz.Add(st)
        vsz.AddSpacer(10)

        self.AllRelays = sorted(rlAct+rlInact)

        self.cblRelays = wx.CheckListBox(self, wx.ID_ANY, choices=self.AllRelays, size=(100, 200))
        self.cblRelays.SetCheckedStrings(rlAct)
        vsz.Add(self.cblRelays, 0, wx.ALIGN_CENTER_HORIZONTAL)

        vsz.AddSpacer(20)

        h = wx.BoxSizer(wx.HORIZONTAL)

        self.bOK = wx.Button(self, wx.ID_ANY, "OK")
        self.Bind(wx.EVT_BUTTON, self.OnBOk, self.bOK)
        h.Add(self.bOK)

        h.AddSpacer(20)

        self.bCancel = wx.Button(self, wx.ID_ANY, "Cancel")
        self.Bind(wx.EVT_BUTTON, self.OnCancel, self.bCancel)
        h.Add(self.bCancel)

        vsz.Add(h, 0, wx.ALIGN_CENTER_HORIZONTAL)

        vsz.AddSpacer(20)

        hsz = wx.BoxSizer(wx.HORIZONTAL)
        hsz.AddSpacer(20)
        hsz.Add(vsz)
        hsz.AddSpacer(20)

        self.SetSizer(hsz)
        self.Layout()
        self.Fit()

    def GetRelays(self):
        rlAct = self.cblRelays.GetCheckedStrings()
        rlInact = [r for r in self.AllRelays if r not in rlAct]
        return rlAct, rlInact

    def OnCancel(self, evt):
        self.EndModal(wx.ID_CANCEL)

    def OnBOk(self, evt):
        self.EndModal(wx.ID_OK)


class DebugFlagsDlg(wx.Dialog):
    def __init__(self, parent, settings):
        wx.Dialog.__init__(self, parent, wx.ID_ANY, "Debugging Flags")
        self.Bind(wx.EVT_CLOSE, self.OnCancel)
        self.parent = parent
        self.settings = settings

        vszr = wx.BoxSizer(wx.VERTICAL)
        vszr.AddSpacer(20)

        self.cbEvalAspect = wx.CheckBox(self, wx.ID_ANY, "Show aspect calculation")
        vszr.Add(self.cbEvalAspect)
        self.cbEvalAspect.SetValue(self.settings.debug.showaspectcalculation)

        vszr.AddSpacer(10)

        self.cbBlockOccupancy = wx.CheckBox(self, wx.ID_ANY, "Block Occupancy")
        vszr.Add(self.cbBlockOccupancy)
        self.cbBlockOccupancy.SetValue(self.settings.debug.blockoccupancy)

        vszr.AddSpacer(10)

        self.cbTrainID = wx.CheckBox(self, wx.ID_ANY, "Train Identification")
        vszr.Add(self.cbTrainID)
        self.cbTrainID.SetValue(self.settings.debug.identifytrain)

        btnszr = wx.BoxSizer(wx.HORIZONTAL)

        self.bOK = wx.Button(self, wx.ID_ANY, "OK", size=BSIZE)
        self.Bind(wx.EVT_BUTTON, self.OnOK, self.bOK)
        btnszr.Add(self.bOK)

        btnszr.AddSpacer(20)

        self.bCancel = wx.Button(self, wx.ID_ANY, "Cancel", size=BSIZE)
        self.Bind(wx.EVT_BUTTON, self.OnCancel, self.bCancel)
        btnszr.Add(self.bCancel)

        vszr.AddSpacer(20)
        vszr.Add(btnszr, 0, wx.ALIGN_CENTER_HORIZONTAL)

        vszr.AddSpacer(20)

        hszr = wx.BoxSizer(wx.HORIZONTAL)
        hszr.AddSpacer(20)
        hszr.Add(vszr)
        hszr.AddSpacer(20)

        self.SetSizer(hszr)
        self.Layout()
        self.Fit()
        self.CenterOnScreen()

    def OnCancel(self, _):
        self.EndModal(wx.ID_CANCEL)

    def OnOK(self, _):
        self.EndModal(wx.ID_OK)

    def ApplyResults(self):
        messages = []
        nv = self.cbEvalAspect.GetValue()
        if nv != self.settings.debug.showaspectcalculation:
            self.settings.debug.showaspectcalculation = nv
            messages.append("Show Aspect Calculation => %s" % nv)

        nv = self.cbBlockOccupancy.GetValue()
        if nv != self.settings.debug.blockoccupancy:
            self.settings.debug.blockoccupancy = nv
            messages.append("Block Occupancy => %s" % nv)

        nv = self.cbTrainID.GetValue()
        if nv != self.settings.debug.identifytrain:
            self.settings.debug.identifytrain = nv
            messages.append("Train Identification => %s" % nv)

        if len(messages) == 0:
            dlg = wx.MessageDialog(self, "No Flags Changed",
                                   "No Changes",
                                   wx.OK | wx.ICON_INFORMATION
                                   )
        else:
            dlg = wx.MessageDialog(self, "\n".join(messages),
                                   "Flags Modified",
                                   wx.OK | wx.ICON_INFORMATION
                                   )
        dlg.ShowModal()
        dlg.Destroy()


class LogLevelDlg(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, wx.ID_ANY, "Set Log Level")
        self.Bind(wx.EVT_CLOSE, self.OnCancel)
        self.CenterOnScreen()

        vszr = wx.BoxSizer(wx.VERTICAL)

        font = wx.Font(wx.Font(14, wx.FONTFAMILY_TELETYPE, wx.NORMAL, wx.BOLD, faceName="Monospace"))

        self.logLevels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        self.logLevelValues = [logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR, logging.CRITICAL]

        self.rbMode = wx.RadioBox(self, wx.ID_ANY, "Log Level", choices=self.logLevels,
                                  majorDimension=1, style=wx.RA_SPECIFY_COLS)
        vszr.AddSpacer(20)
        vszr.Add(self.rbMode, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)
        l = logging.getLogger().getEffectiveLevel()
        try:
            lvl = self.logLevelValues.index(l)
        except ValueError:
            lvl = 4
        self.rbMode.SetSelection(lvl)

        btnszr = wx.BoxSizer(wx.HORIZONTAL)

        self.bOK = wx.Button(self, wx.ID_ANY, "OK", size=BSIZE)
        self.Bind(wx.EVT_BUTTON, self.OnOK, self.bOK)
        btnszr.Add(self.bOK)

        btnszr.AddSpacer(20)

        self.bCancel = wx.Button(self, wx.ID_ANY, "Cancel", size=BSIZE)
        self.Bind(wx.EVT_BUTTON, self.OnCancel, self.bCancel)
        btnszr.Add(self.bCancel)

        vszr.AddSpacer(20)
        vszr.Add(btnszr, 0, wx.ALIGN_CENTER_HORIZONTAL)

        vszr.AddSpacer(20)

        hszr = wx.BoxSizer(wx.HORIZONTAL)
        hszr.AddSpacer(20)
        hszr.Add(vszr)
        hszr.AddSpacer(20)

        self.SetSizer(hszr)
        self.Layout()
        self.Fit();

    def OnOK(self, _):
        self.EndModal(wx.ID_OK)

    def OnCancel(self, _):
        self.EndModal(wx.ID_CANCEL)

    def GetResults(self):
        lvl = self.rbMode.GetSelection()
        return self.logLevelValues[lvl]


class ListDlg(wx.Dialog):
    def __init__(self, parent, data, sz, title, cbRefresh=None):
        wx.Dialog.__init__(self, parent, wx.ID_ANY, title)
        self.Bind(wx.EVT_CLOSE, self.OnCancel)
        self.parent = parent
        self.cbRefresh = cbRefresh

        vszr = wx.BoxSizer(wx.VERTICAL)

        font = wx.Font(wx.Font(14, wx.FONTFAMILY_TELETYPE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, faceName="Monospace"))

        lb = wx.ListBox(self, wx.ID_ANY, choices=data, size=sz, style=wx.LC_REPORT)
        lb.SetFont(font)
        vszr.Add(lb, 1, wx.ALL, 20)
        self.lb = lb

        if callable(cbRefresh):
            vszr.AddSpacer(20)
            b = wx.Button(self, wx.ID_ANY, "Refresh")
            self.Bind(wx.EVT_BUTTON, self.onBRefresh, b)
            vszr.Add(b, 0, wx.ALIGN_CENTER_HORIZONTAL)
            vszr.AddSpacer(20)

        self.SetSizer(vszr)
        self.Layout()
        self.Fit();
        self.CenterOnScreen()

    def onBRefresh(self, _):
        top = self.lb.GetTopItem()
        r = self.cbRefresh()
        if r is None:
            return

        self.lb.Clear()
        self.lb.SetItems(r)
        self.lb.SetFirstItem(top)

    def OnCancel(self, _):
        self.EndModal(wx.ID_CANCEL)


class OSProxyDlg(wx.Dialog):
    def __init__(self, parent, data, cbRefresh=None):
        wx.Dialog.__init__(self, parent, wx.ID_ANY, "OS Proxies")
        self.Bind(wx.EVT_CLOSE, self.OnCancel)
        self.parent = parent
        self.cbRefresh = cbRefresh

        vszr = wx.BoxSizer(wx.VERTICAL)

        lb = OSProxyListCtrl(self, data)
        vszr.Add(lb, 1, wx.ALL, 20)
        self.lb = lb

        if callable(self.cbRefresh):
            vszr.AddSpacer(20)
            b = wx.Button(self, wx.ID_ANY, "Refresh")
            self.Bind(wx.EVT_BUTTON, self.onBRefresh, b)
            vszr.Add(b, 0, wx.ALIGN_CENTER_HORIZONTAL)
            vszr.AddSpacer(20)

        self.SetSizer(vszr)
        self.Layout()
        self.Fit();
        self.CenterOnScreen()

    def onBRefresh(self, _):
        ospdict = self.cbRefresh()
        self.lb.SetData(ospdict)

    def OnCancel(self, _):
        self.EndModal(wx.ID_CANCEL)


class OSProxyListCtrl(wx.ListCtrl):
    def __init__(self, parent, ospdict, cbRefresh=None):
        wx.ListCtrl.__init__(self, parent, wx.ID_ANY, size=(700, 160), style=wx.LC_REPORT + wx.LC_VIRTUAL)
        self.parent = parent
        self.cbRefresh=cbRefresh
        self.order = [rname for rname in sorted(ospdict.keys())]
        self.osp = ospdict

        font = wx.Font(wx.Font(14, wx.FONTFAMILY_TELETYPE, wx.NORMAL, wx.BOLD, faceName="Monospace"))
        self.SetFont(font)

        self.normalA = wx.ItemAttr()
        self.normalB = wx.ItemAttr()
        self.normalA.SetBackgroundColour(wx.Colour(225, 255, 240))
        self.normalB.SetBackgroundColour(wx.Colour(138, 255, 197))

        self.InsertColumn(0, "Route")
        self.SetColumnWidth(0, 160)
        self.InsertColumn(1, "OS")
        self.SetColumnWidth(1, 160)
        self.InsertColumn(2, "Count")
        self.SetColumnWidth(2, 80)
        self.InsertColumn(3, "Segments")
        self.SetColumnWidth(3, 300)

        self.SetItemCount(len(self.order))

    def SetData(self, ospdict):
        self.order = [rname for rname in sorted(ospdict.keys())]
        self.osp = ospdict
        self.SetItemCount(0)
        self.SetItemCount(len(self.order))

    def OnGetItemText(self, item, col):
        rte = self.order[item]

        if col == 0:
            return rte

        elif col == 1:
            return self.osp[rte]["os"]

        elif col == 2:
            return "%d" % self.osp[rte]["count"]

        elif col == 3:
            return ", ".join(self.osp[rte]["segments"])

    def OnGetItemAttr(self, item):
        if item % 2 == 1:
            return self.normalB
        else:
            return self.normalA


class NodeStatusDlg(wx.Dialog):
    def __init__(self, parent, data, cbRefresh=None):
        wx.Dialog.__init__(self, parent, wx.ID_ANY, "Node Status")
        self.Bind(wx.EVT_CLOSE, self.OnCancel)
        self.parent = parent
        self.cbRefresh = cbRefresh

        vszr = wx.BoxSizer(wx.VERTICAL)

        lb = NodeStatusListCtrl(self, data)
        vszr.Add(lb, 1, wx.ALL, 20)
        self.lb = lb

        hszr = wx.BoxSizer(wx.HORIZONTAL)

        if callable(self.cbRefresh):
            hszr.AddSpacer(20)
            b = wx.Button(self, wx.ID_ANY, "Refresh")
            self.Bind(wx.EVT_BUTTON, self.onBRefresh, b)
            hszr.Add(b)

        hszr.AddSpacer(20)
        b = wx.Button(self, wx.ID_ANY, "Re-Enable")
        self.Bind(wx.EVT_BUTTON, self.onBReEnable, b)
        hszr.Add(b)
        self.bReEnable = b
        hszr.AddSpacer(20)

        vszr.AddSpacer(20)
        vszr.Add(hszr, 0, wx.ALIGN_CENTER_HORIZONTAL)
        vszr.AddSpacer(20)

        self.SetSizer(vszr)
        self.Layout()
        self.Fit();
        self.CenterOnScreen()

        dislist = self.lb.GetDisabled()
        self.bReEnable.Enable(len(dislist) > 0)

    def onBReEnable(self, _):
        disList = self.lb.GetDisabled()
        self.parent.ReEnableNodes(disList)

    def onBRefresh(self, _):
        nlist = self.cbRefresh()
        self.lb.SetData(nlist)
        dislist = self.lb.GetDisabled()
        self.bReEnable.Enable(len(dislist) > 0)

    def OnCancel(self, _):
        self.EndModal(wx.ID_CANCEL)


class NodeStatusListCtrl(wx.ListCtrl):
    def __init__(self, parent, nlist, cbRefresh=None):
        wx.ListCtrl.__init__(self, parent, wx.ID_ANY, size=(420, 680), style=wx.LC_REPORT + wx.LC_VIRTUAL)
        self.parent = parent
        self.cbRefresh=cbRefresh
        self.nodeinfo = sorted(nlist, key=lambda x: x[1])

        font = wx.Font(wx.Font(14, wx.FONTFAMILY_TELETYPE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, faceName="Monospace"))
        self.SetFont(font)

        self.normalA = wx.ItemAttr()
        self.normalB = wx.ItemAttr()
        self.normalA.SetBackgroundColour(wx.Colour(225, 255, 240))
        self.normalB.SetBackgroundColour(wx.Colour(138, 255, 197))

        self.InsertColumn(0, "Name")
        self.SetColumnWidth(0, 160)
        self.InsertColumn(1, "Address")
        self.SetColumnWidth(1, 160)
        self.InsertColumn(2, "Enabled")
        self.SetColumnWidth(2, 100)

        self.SetItemCount(len(self.nodeinfo))

    def SetData(self, nlist):
        self.nodeinfo = sorted(nlist, key=lambda x: x[1])
        self.SetItemCount(0)
        self.SetItemCount(len(self.nodeinfo))

    def GetDisabled(self):
        rv = []
        for ni in self.nodeinfo:
            if not ni[2]:
                rv.append([ni[0], ni[1]])

        return rv

    def OnGetItemText(self, item, col):
        ni = self.nodeinfo[item]

        if col == 0:
            return ni[0]

        elif col == 1:
            return "0x%02x" % ni[1]

        elif col == 2:
            return "%s" % ni[2]

    def OnGetItemAttr(self, item):
        if item % 2 == 1:
            return self.normalB
        else:
            return self.normalA


class CheckListDlg(wx.Dialog):
    def __init__(self, parent, items, title, prechecked=[]):
        self.choices = items
        wx.Dialog.__init__(self, parent, wx.ID_ANY, title)
        self.Bind(wx.EVT_CLOSE, self.OnCancel)

        vszr = wx.BoxSizer(wx.VERTICAL)
        vszr.AddSpacer(20)

        cb = wx.CheckListBox(self, wx.ID_ANY, size=(160, -1), choices=items)
        self.cbItems = cb
        pcxl = []
        for pc in prechecked:
            try:
                n = items.index(pc)
            except ValueError:
                n = None
            if n is not None:
                pcxl.append(n)

        if len(pcxl) > 0:
            self.cbItems.SetCheckedItems(pcxl)
        vszr.Add(cb, 0, wx.ALIGN_CENTER_HORIZONTAL)

        vszr.AddSpacer(20)

        btnszr = wx.BoxSizer(wx.HORIZONTAL)

        bAll = wx.Button(self, wx.ID_ANY, "All")
        self.Bind(wx.EVT_BUTTON, self.OnBAll, bAll)

        bNone = wx.Button(self, wx.ID_ANY, "None")
        self.Bind(wx.EVT_BUTTON, self.OnBNone, bNone)

        btnszr.Add(bAll)
        btnszr.AddSpacer(20)
        btnszr.Add(bNone)

        vszr.Add(btnszr, 0, wx.ALIGN_CENTER_HORIZONTAL)

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

    def OnBAll(self, evt):
        self.cbItems.SetCheckedItems(range(len(self.choices)))

    def OnBNone(self, evt):
        self.cbItems.SetCheckedItems([])

    def OnCancel(self, _):
        self.EndModal(wx.ID_CANCEL)

    def OnBOK(self, _):
        self.EndModal(wx.ID_OK)

    def GetCheckedItems(self):
        return self.cbItems.GetCheckedStrings()
