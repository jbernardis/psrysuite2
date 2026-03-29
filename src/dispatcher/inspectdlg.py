import wx
import wx.grid as gridlib
import os
import sys
import logging
from subprocess import Popen

from c13auto.c13automain import osRoutes

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

        self.dlgAdjacency = None
        self.dlgOSProxy = None
        self.dlgNodeStatus = None
        self.dlgSignalLevers = None
        self.dlgSidingLocks = None
        self.dlgHilite = None
        self.dlgRoutes = None
        self.dlgTrains = None
        self.dlgAuditTrains = None

        self.SetTitle("Inspection Dialog")

        bLogLevel = wx.Button(self, wx.ID_ANY, "Logging Level", size=BSIZE)
        self.Bind(wx.EVT_BUTTON, self.OnBLogLevel, bLogLevel)
        bDebug = wx.Button(self, wx.ID_ANY, "Debugging Flags", size=BSIZE)
        self.Bind(wx.EVT_BUTTON, self.OnBDebug, bDebug)
        bProxies = wx.Button(self, wx.ID_ANY, "OS Proxies", size=BSIZE)
        self.Bind(wx.EVT_BUTTON, self.OnBProxies, bProxies)
        bRoutes = wx.Button(self, wx.ID_ANY, "Active Routes", size=BSIZE)
        self.Bind(wx.EVT_BUTTON, self.OnBRoutes, bRoutes)
        bNodes = wx.Button(self, wx.ID_ANY, "Node Status", size=BSIZE)
        self.Bind(wx.EVT_BUTTON, self.OnBNodes, bNodes)
        bTester = wx.Button(self, wx.ID_ANY, "Tester", size=BSIZE)
        self.Bind(wx.EVT_BUTTON, self.OnBStartTester, bTester)
        bRelays = wx.Button(self, wx.ID_ANY, "Stop Relays", size=BSIZE)
        self.Bind(wx.EVT_BUTTON, self.OnBRelays, bRelays)
        bLevers = wx.Button(self, wx.ID_ANY, "Signal Levers", size=BSIZE)
        self.Bind(wx.EVT_BUTTON, self.OnBLevers, bLevers)
        bToLocks = wx.Button(self, wx.ID_ANY, "Turnout Locks", size=BSIZE)
        self.Bind(wx.EVT_BUTTON, self.OnBTurnoutLocks, bToLocks)
        bAuditTrains = wx.Button(self, wx.ID_ANY, "Audit Trains", size=BSIZE)
        self.Bind(wx.EVT_BUTTON, self.OnBAuditTrains, bAuditTrains)
        bActiveTrains = wx.Button(self, wx.ID_ANY, "Active Trains", size=BSIZE)
        self.Bind(wx.EVT_BUTTON, self.OnBActiveTrains, bActiveTrains)
        bMonitor = wx.Button(self, wx.ID_ANY, "Monitor", size=BSIZE)
        self.Bind(wx.EVT_BUTTON, self.OnBStartMonitor, bMonitor)
        bHandSwitches = wx.Button(self, wx.ID_ANY, "Siding Locks", size=BSIZE)
        self.Bind(wx.EVT_BUTTON, self.OnBHandSwitches, bHandSwitches)
        bResetBlks = wx.Button(self, wx.ID_ANY, "Reset Blocks", size=BSIZE)
        self.Bind(wx.EVT_BUTTON, self.OnBResetBlks, bResetBlks)
        # bIgnoreBlks = wx.Button(self, wx.ID_ANY, "Ignore Blocks", size=BSIZE)
        # self.Bind(wx.EVT_BUTTON, self.OnBIgnoreBlks, bIgnoreBlks)
        bAdjacency = wx.Button(self, wx.ID_ANY, "Block Adjacency", size=BSIZE)
        self.Bind(wx.EVT_BUTTON, self.OnBBlockAdjacency, bAdjacency)
        bHilite = wx.Button(self, wx.ID_ANY, "Hilite\nBlock/Route", size=BSIZE)
        self.Bind(wx.EVT_BUTTON, self.OnBHilite, bHilite)

        bszl = []

        buttonCols = [[bDebug, bLogLevel, bNodes, bRelays],
                    [bAuditTrains, bActiveTrains, bRoutes, bAdjacency, bProxies],
                    [bToLocks, bLevers, bHandSwitches, bResetBlks],
                    [bTester, bMonitor, bHilite]]

        if self.parent.IsDispatcherOrSatellite() and self.settings.scanner.enable:
            bScanner = wx.Button(self, wx.ID_ANY, "Scanner", size=BSIZE)
            self.Bind(wx.EVT_BUTTON, self.OnBScanner, bScanner)
            buttonCols[3].append(bScanner)

        for blist in buttonCols:

            sz = wx.BoxSizer(wx.VERTICAL)
            sz.AddSpacer(20)

            for b in blist:
                sz.Add(b)
                sz.AddSpacer(10)

            sz.AddSpacer(10)

            bszl.append(sz)

        btnszr = wx.BoxSizer(wx.HORIZONTAL)

        for bsz in bszl:
            btnszr.AddSpacer(20)
            btnszr.Add(bsz)

        btnszr.AddSpacer(20)

        self.SetSizer(btnszr)
        self.Layout()
        self.Fit()

    def OnBActiveTrains(self, _):
        tl = self.parent.Get("activetrains", {})
        try:
            self.dlgTrains.Raise()
        except:
            self.dlgTrains = ActiveTrainsDlg(self, tl, self.parent)
            self.dlgTrains.Show()

    def OnBHilite(self, _):
        try:
            self.dlgHilite.Raise()
        except:
            self.dlgHilite = HiliteDlg(self, self.parent)
            self.dlgHilite.Show()

    def OnBStartTester(self, _):
        Exec = os.path.join(os.getcwd(), "tester2", "main.py")
        Proc = Popen([sys.executable, Exec])

        logging.info("Tester2 started as PID %d" % Proc.pid)

    def OnBStartMonitor(self, _):
        Exec = os.path.join(os.getcwd(), "monitor", "main.py")
        Proc = Popen([sys.executable, Exec])

        logging.info("Monitor started as PID %d" % Proc.pid)

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
        try:
            self.dlgOSProxy.Raise()
        except:
            self.dlgOSProxy = OSProxyDlg(self, pi, self.parent.GetOSProxyInfo)
            self.dlgOSProxy.Show()

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

    def OnBBlockAdjacency(self, _):
        ba = self.parent.Get("blockadjacency", {})
        try:
            self.dlgAdjacency.Raise()
        except:
            self.dlgAdjacency = AdjacencyDlg(self, ba, self.parent)
            self.dlgAdjacency.Show()

    def OnBRoutes(self, _):
        rtl = self.parent.Get("getroutes", {})
        try:
            self.dlgRoutes.Raise()
        except:
            self.dlgRoutes = RoutesDlg(self, rtl, self.parent)
            self.dlgRoutes.Show()

    def formatRelayName(self, rn):
        return rn.split(".")[0]

    def OnBLevers(self, _):
        slv = self.GetSignalLeverValues()
        try:
            self.dlgSignalLevers.Raise()
        except:
            self.dlgSignalLevers = ListDlg(self, slv, (200, 200), "Signal Levers", self.GetSignalLeverValues)
            self.dlgSignalLevers.Show()

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
        results = self.parent.Get("audittrains", {})
        try:
            self.dlgAuditTrains.Raise()
        except:
            self.dlgAuditTrains = AuditTrainsDlg(self, results)
            self.dlgAuditTrains.Show()

    def OnBHandSwitches(self, _):
        hsv = self.GetHandswitchValues()
        try:
            self.dlgSidingLocks.Raise()
        except:
            self.dlgSidingLocks = ListDlg(self, hsv, (260, 200), "Siding Locks", self.GetHandswitchValues)
            self.dlgSidingLocks.Show()

    def GetHandswitchValues(self):
        hsinfo = self.parent.GetHandswitchInfo()
        if hsinfo is None:
            return []
        hsList = ["%-9.9s   %s" % (hs, str(hsinfo[hs])) for hs in sorted(hsinfo.keys())]
        return hsList

    def OnBNodes(self, _):
        nodeList = self.parent.GetNodes()
        try:
            self.dlgNodeStatus.Raise()
        except:
            self.dlgNodeStatus = NodeStatusDlg(self, nodeList, self.parent.GetNodes)
            self.dlgNodeStatus.Show()

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

    def OnBScanner(self, _):
        fn = os.path.join(os.getcwd(), "qrcodes", "scanner_battery.png")
        dlg = ScannerDlg(self, fn, self.parent)
        dlg.ShowModal()
        dlg.Destroy()

    def OnCancel(self, _):
        try:
            self.dlgAdjacency.Destroy()
        except:
            pass

        try:
            self.dlgOSProxy.Destroy()
        except:
            pass

        try:
            self.dlgNodeStatus.Destroy()
        except:
            pass

        try:
            self.dlgSignalLevers.Destroy()
        except:
            pass

        try:
            self.dlgSidingLocks.Destroy()
        except:
            pass

        try:
            self.dlgHilite.Destroy()
        except:
            pass

        try:
            self.dlgRoutes.Destroy()
        except:
            pass

        try:
            self.dlgTrains.Destroy()
        except:
            pass

        try:
            self.dlgAuditTrains.Destroy()
        except:
            pass

        self.closer()


class HiliteDlg(wx.Dialog):
    def __init__(self, parent, frame):
        wx.Dialog.__init__(self, parent, wx.ID_ANY, "Block/Route Hilite")
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self.parent = parent
        self.frame = frame

        self.selectedBlock = None
        self.selectedOS = None
        self.selectedRoute = None

        blks = sorted([bn for bn, blk in self.frame.blocks.items() if not blk.IsOS()])
        osblks = sorted([bn for bn, blk in self.frame.blocks.items() if blk.IsOS()])
        rtes = {rn: rte.GetOSName() for rn, rte in self.frame.routes.items()}
 
        self.os2route = {}
        for rtnm, osnm in rtes.items():
            if osnm in self.os2route.keys():
                self.os2route[osnm].append(rtnm)
            else:
                self.os2route[osnm] = [rtnm]

        szBlockChoice = wx.BoxSizer(wx.HORIZONTAL)

        st = wx.StaticText(self, wx.ID_ANY, "Block:")
        szBlockChoice.Add(st)
        szBlockChoice.AddSpacer(10)
        self.chBlk = wx.Choice(self, wx.ID_ANY, choices=blks)
        self.Bind(wx.EVT_CHOICE, self.OnChBlock, self.chBlk)
        szBlockChoice.Add(self.chBlk)

        self.rbBlkOpts = wx.RadioBox(self, wx.ID_ANY, "Options",
            choices=["Main Block Only", "Stop Sections Only", "All"], majorDimension=1, style=wx.RA_SPECIFY_COLS)
        self.rbBlkOpts.SetSelection(2)

        szButtons = wx.BoxSizer(wx.HORIZONTAL)
        szButtons.AddSpacer(20)

        self.bBlock = wx.Button(self, wx.ID_ANY, "Hilite Block", size=BSIZE)
        szButtons.Add(self.bBlock)
        self.Bind(wx.EVT_BUTTON, self.OnBBlock, self.bBlock)
        self.bBlock.Enable(False)

        szButtons.AddSpacer(20)
        self.bClear = wx.Button(self, wx.ID_ANY, "Clear Hilite", size=BSIZE)
        szButtons.Add(self.bClear)
        self.Bind(wx.EVT_BUTTON, self.OnBClear, self.bClear)

        szButtons.AddSpacer(20)
        self.bOS = wx.Button(self, wx.ID_ANY, "Hilite OS Route", size=BSIZE)
        szButtons.Add(self.bOS)
        self.Bind(wx.EVT_BUTTON, self.OnBOS, self.bOS)
        self.bOS.Enable(False)

        vszL = wx.BoxSizer(wx.VERTICAL)
        vszL.AddSpacer(20)
        szButtons.AddSpacer(20)

        vszL.Add(szBlockChoice, 0, wx.ALIGN_CENTER_HORIZONTAL)

        vszL.AddSpacer(20)

        vszL.Add(self.rbBlkOpts, 0, wx.ALIGN_CENTER_HORIZONTAL)

        vszL.AddSpacer(20)

        szOSChoice = wx.BoxSizer(wx.HORIZONTAL)

        st = wx.StaticText(self, wx.ID_ANY, "OS:")
        szOSChoice.Add(st)
        szOSChoice.AddSpacer(10)
        self.chOS = wx.Choice(self, wx.ID_ANY, choices=osblks)
        self.Bind(wx.EVT_CHOICE, self.OnChOS, self.chOS)
        szOSChoice.Add(self.chOS)

        szRouteChoice = wx.BoxSizer(wx.HORIZONTAL)

        st = wx.StaticText(self, wx.ID_ANY, "Route:")
        szRouteChoice.Add(st)
        szRouteChoice.AddSpacer(10)
        self.chRoute = wx.Choice(self, wx.ID_ANY, choices=[])
        self.Bind(wx.EVT_CHOICE, self.OnChRoute, self.chRoute)
        self.chRoute.Enable(False)
        szRouteChoice.Add(self.chRoute)

        vszR = wx.BoxSizer(wx.VERTICAL)
        vszR.AddSpacer(20)

        vszR.Add(szOSChoice, 0, wx.ALIGN_CENTER_HORIZONTAL)
        
        vszR.AddSpacer(10)

        vszR.Add(szRouteChoice, 0, wx.ALIGN_CENTER_HORIZONTAL)

        vszR.AddSpacer(20)

        hsz = wx.BoxSizer(wx.HORIZONTAL)
        hsz.AddSpacer(20)

        hsz.Add(vszL)

        hsz.AddSpacer(20)

        hsz.Add(vszR)

        hsz.AddSpacer(20)

        vsz = wx.BoxSizer(wx.VERTICAL)
        vsz.Add(hsz, 0, wx.ALIGN_CENTER_HORIZONTAL)
        vsz.Add(szButtons, 0, wx.ALIGN_CENTER_HORIZONTAL)
        vsz.AddSpacer(20)

        self.SetSizer(vsz)
        self.Fit()
        self.Layout()

    def OnBBlock(self, _):
        if self.selectedBlock is not None:
            opt = self.rbBlkOpts.GetSelection()
            mainblock = opt in [0, 2]
            stopblocks = opt in [1, 2]
            self.frame.ShowHilitedBlock(self.selectedBlock, mainblock=mainblock, stopblocks=stopblocks)

    def OnBClear(self, _):
        if self.selectedBlock is not None:
            self.frame.ClearHighlitedRoute()

    def OnChBlock(self, _):
        chx = self.chBlk.GetSelection()
        if chx == wx.NOT_FOUND:
            self.selectedBlock = None
            self.bBlock.Enable(False)
        else:
            self.selectedBlock = self.chBlk.GetString(chx)
            self.bBlock.Enable(True)

    def OnChOS(self, _):
        chx = self.chOS.GetSelection()
        if chx == wx.NOT_FOUND:
            self.selectedOS = None
            self.bOS.Enable(False)
            self.chRoute.SetItems([])
            self.chRoute.SetSelection(wx.NOT_FOUND)
            self.chRoute.Enable(False)
        else:
            self.selectedOS = self.chOS.GetString(chx)
            self.bOS.Enable(True)
            self.chRoute.SetItems(self.os2route[self.selectedOS])
            self.chRoute.SetSelection(0)
            self.chRoute.Enable(True)
            self.selectedRoute = self.chRoute.GetString(0)
            
    def OnChRoute(self, _):
        chx = self.chRoute.GetSelection()
        if chx == wx.NOT_FOUND:
            self.selectedRoute = None
            self.bOS.Enable(False)
        else:
            self.selectedRoute = self.chRoute.GetString(chx)
            self.bOS.Enable(True)

    def OnBOS(self, _):
        if self.selectedOS is not None and self.selectedRoute is not None:
            self.frame.ShowHilitedOSRoute(self.selectedOS, self.selectedRoute)

    def OnClose(self, _):
        self.Destroy()


class TrainEntry:
    def __init__(self, name, loco, direction, engineer, blocks, signal, aspect, stopped):
        self.name = name
        self.loco = loco
        self.direction = direction
        self.engineer = engineer
        self.blocks = blocks
        self.signal = signal
        self.aspect = aspect
        self.stopped = stopped

    def NewName(self, name):
        rc = name != self.name
        self.name = name
        return rc

    def NewLoco(self, loco):
        rc = loco != self.loco
        self.loco = loco
        return rc

    def NewDirection(self, direction):
        rc = direction != self.direction
        self.direction = direction
        return rc

    def NewEngineer(self, engineer):
        rc = engineer != self.engineer
        self.engineer = engineer
        return rc

    def NewBlocks(self, blocks):
        rc = blocks != self.blocks
        self.blocks = blocks
        return rc

    def NewSignal(self, signal):
        rc = signal != self.signal
        self.signal = signal
        return rc

    def NewAspect(self, aspect):
        rc = aspect != self.aspect
        self.aspect = aspect
        return rc

    def NewStopped(self, stopped):
        rc = stopped != self.stopped
        self.stopped = stopped
        return rc


class AuditTrainsDlg(wx.Dialog):
    def __init__(self, parent, results):
        wx.Dialog.__init__(self, parent, wx.ID_ANY, "Audit Trains", style=wx.DEFAULT_DIALOG_STYLE | wx.STAY_ON_TOP)
        self.Bind(wx.EVT_CLOSE, self.OnClose)

        font = wx.Font(wx.Font(18, wx.FONTFAMILY_ROMAN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, faceName="Arial"))

        A = results["A"]
        B = results["B"]

        gA = self.TrainsToBlocksGrid(self, A)
        gB = self.BlocksToTrainsGrid(self, B)

        vszl = wx.BoxSizer(wx.VERTICAL)
        tc = wx.StaticText(self, wx.ID_ANY, "Trains => Blocks => Trains")
        tc.SetFont(font)
        vszl.Add(tc, 0, wx.ALIGN_CENTER_HORIZONTAL)
        vszl.AddSpacer(10)
        vszl.Add(gA, 0, wx.ALIGN_CENTER_HORIZONTAL)

        vszr = wx.BoxSizer(wx.VERTICAL)
        tc = wx.StaticText(self, wx.ID_ANY, "Blocks => Trains => Blocks")
        tc.SetFont(font)
        vszr.Add(tc, 0, wx.ALIGN_CENTER_HORIZONTAL)
        vszr.AddSpacer(10)
        vszr.Add(gB, 0, wx.ALIGN_CENTER_HORIZONTAL)

        hszr = wx.BoxSizer(wx.HORIZONTAL)
        hszr.AddSpacer(20)
        hszr.Add(vszl)
        hszr.AddSpacer(10)
        hszr.Add(vszr)
        hszr.AddSpacer(20)

        szr = wx.BoxSizer(wx.VERTICAL)
        szr.AddSpacer(20)
        szr.Add(hszr)
        szr.AddSpacer(20)

        self.SetSizer(szr)
        self.Layout()
        self.Fit();
        self.CenterOnScreen()

    def TrainsToBlocksGrid(self, parent, tdata):
        headings = ["Train", "Train\nBlock", "Block\nTrain"]
        colWidth = [70, 70, 70]
        colAlign = [wx.ALIGN_CENTER, wx.ALIGN_CENTER, wx.ALIGN_CENTER]
        nRows = 0
        for t in tdata.values():
            nRows += len(t)
        nCols = len(headings)

        colorWhite = wx.Colour(255, 255, 255)
        colorRed = wx.Colour(224, 149, 149)

        # we want to have at least 5, at most 30 lines on the display
        nr = nRows
        if nr < 5:
            nr = 5
        elif nr > 30:
            nr = 30
        ht = int(33 + nr * 19)

        g = gridlib.Grid(parent, size=(sum(colWidth) + 20, ht))
        g.CreateGrid(nRows, nCols)
        g.EnableGridLines(True)
        g.SetGridLineColour(wx.BLACK)
        g.SetRowLabelSize(2)

        attrs = []
        for c in range(nCols):
            attr = wx.grid.GridCellAttr()
            attr.SetAlignment(colAlign[c], wx.ALIGN_CENTER)
            attr.SetReadOnly(True)
            attrs.append(attr)

        for i in range(nCols):
            g.SetColLabelValue(i, headings[i])
            g.SetColSize(i, colWidth[i])
            g.SetColAttr(i, attrs[i])

        row = 0
        for trid, tinfo in tdata.items():
            nm = trid
            for b in tinfo:
                g.SetCellValue(row, 0, nm)
                g.SetCellValue(row, 1, b["block"])
                g.SetCellValue(row, 2, b["train"])
                g.SetCellBackgroundColour(row, 0, colorRed if b["train"] != trid else colorWhite)

                nm = ""
                row += 1

        return g

    def BlocksToTrainsGrid(self, parent, bdata):
        headings = ["Block", "Block\nTrain", "Train\nBlocks"]
        colWidth = [70, 70, 300]
        colAlign = [wx.ALIGN_CENTER, wx.ALIGN_CENTER, wx.ALIGN_LEFT]
        nRows = len(bdata)
        nCols = len(headings)

        colorWhite = wx.Colour(255, 255, 255)
        colorRed = wx.Colour(224, 149, 149)

        # we want to have at least 5, at most 30 lines on the display
        nr = nRows
        if nr < 5:
            nr = 5
        elif nr > 30:
            nr = 30
        ht = int(33 + nr * 19)

        g = gridlib.Grid(parent, size=(sum(colWidth) + 20, ht))
        g.CreateGrid(nRows, nCols)
        g.EnableGridLines(True)
        g.SetGridLineColour(wx.BLACK)
        g.SetRowLabelSize(2)

        attrs = []
        for c in range(nCols):
            attr = wx.grid.GridCellAttr()
            attr.SetAlignment(colAlign[c], wx.ALIGN_CENTER)
            attr.SetReadOnly(True)
            attrs.append(attr)

        for i in range(nCols):
            g.SetColLabelValue(i, headings[i])
            g.SetColSize(i, colWidth[i])
            g.SetColAttr(i, attrs[i])

        row = 0
        for blkid, info in bdata.items():
            g.SetCellValue(row, 0, blkid)
            g.SetCellValue(row, 1, info["train"])
            g.SetCellValue(row, 2, ", ".join(info["blocks"]))
            if blkid in info["blocks"]:
                c = colorWhite
            else:
                if "alias" in info:
                    c = colorRed if info["alias"] not in info["blocks"] else colorWhite
                else:
                    c = colorRed
            g.SetCellBackgroundColour(row, 0, c)

            row += 1

        return g

    def OnClose(self, _):
        self.Destroy()


class ActiveTrainsDlg(wx.Dialog):
    def __init__(self, parent, tdata, frame):
        wx.Dialog.__init__(self, parent, wx.ID_ANY, "Active Trains")
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self.parent = parent
        self.frame = frame

        headings = ["Train", "Int name", "Loco", "Direction", "Engineer", "Blocks", "Signal", "Aspect", "Stopped"]
        colWidth = [70, 70, 70, 70, 70, 140, 70, 140, 70]
        colAlign = [wx.ALIGN_CENTER, wx.ALIGN_CENTER, wx.ALIGN_CENTER, wx.ALIGN_CENTER, wx.ALIGN_CENTER,
                    wx.ALIGN_CENTER, wx.ALIGN_CENTER, wx.ALIGN_CENTER, wx.ALIGN_CENTER]
        self.nRows = len(tdata)
        nCols = len(headings)

        self.colorWhite = wx.Colour(255, 255, 255)
        self.colorGray = wx.Colour(196, 196, 196)

        # we want to have at least 5, at most 30 lines on the display
        nr = self.nRows
        if nr < 5:
            nr = 5
        elif nr > 30:
            nr = 30
        ht = int(33 + nr * 19)

        self.TRgrid = gridlib.Grid(self, size=(sum(colWidth) + 20, ht))
        self.TRgrid.CreateGrid(self.nRows, nCols)
        self.TRgrid.EnableGridLines(True)
        self.TRgrid.SetGridLineColour(wx.BLACK)
        self.TRgrid.SetRowLabelSize(2)

        attrs = []
        for c in range(nCols):
            attr = wx.grid.GridCellAttr()
            attr.SetAlignment(colAlign[c], wx.ALIGN_CENTER)
            attr.SetReadOnly(True)
            attrs.append(attr)

        for i in range(nCols):
            self.TRgrid.SetColLabelValue(i, headings[i])
            self.TRgrid.SetColSize(i, colWidth[i])
            self.TRgrid.SetColAttr(i, attrs[i])

        row = 0
        self.TRMap = {}
        for trid in sorted(tdata.keys(), key=self.BuildTrainKey):
            name = trid
            iname, loco, direction, engineer, blocks, signal, aspect, stopped = self.ParseTrainEntry(tdata[trid])
            self.TRMap[iname] = TrainEntry(name, loco, direction, engineer, blocks, signal, aspect, stopped)
            self.TRgrid.SetCellValue(row, 0, name)
            self.TRgrid.SetCellValue(row, 1, iname)
            self.TRgrid.SetCellValue(row, 2, loco)
            self.TRgrid.SetCellValue(row, 3, direction)
            self.TRgrid.SetCellValue(row, 4, engineer)
            self.TRgrid.SetCellValue(row, 5, blocks)
            self.TRgrid.SetCellValue(row, 6, signal)
            self.TRgrid.SetCellValue(row, 7, aspect)
            self.TRgrid.SetCellValue(row, 8, stopped)
            row += 1

        vsz = wx.BoxSizer(wx.VERTICAL)
        vsz.AddSpacer(20)

        hsz = wx.BoxSizer(wx.HORIZONTAL)
        hsz.AddSpacer(20)

        hsz.Add(self.TRgrid, 0, wx.EXPAND)

        hsz.AddSpacer(20)
        vsz.Add(hsz)

        vsz.AddSpacer(20)

        bRefresh = wx.Button(self, wx.ID_ANY, "Refresh", size=(100, 30))
        self.Bind(wx.EVT_BUTTON, self.OnBRefresh, bRefresh)
        vsz.Add(bRefresh, 0, wx.ALIGN_CENTER_HORIZONTAL)

        vsz.AddSpacer(20)

        self.SetSizer(vsz)
        self.Fit()
        self.Layout()

    @staticmethod
    def BuildTrainKey(trid):
        if trid.startswith("??"):
            return "ZZ%s" % trid
        else:
            return "AA%s" % trid

    @staticmethod
    def ParseTrainEntry(trinfo):
        iname = trinfo["iname"]
        l = trinfo["loco"]
        loco = "None" if l is None else l
        direction = "East" if trinfo["east"] else "West"
        e = trinfo["engineer"]
        engineer = "None" if e is None else e
        blocks = ", ".join(trinfo["blocks"])
        s = trinfo["signal"]
        signal = "None" if s is None else s
        a = trinfo["aspect"]
        aspect = "None" if a is None else a
        stopped = str(trinfo["stopped"])
        return iname, loco, direction, engineer, blocks, signal, aspect, stopped

    def OnBRefresh(self, _):
        tdata = self.frame.Get("activetrains", {})
        for tid, tinfo in tdata.items():
            logging.debug("%s:  %s" % (tid, str(tinfo)))

        currentKeys = self.TRMap.keys()
        newKeys = [tinfo["iname"] for tinfo in tdata.values()]
        newTrains = [t for t in newKeys if t not in currentKeys]
        delTrains = [t for t in currentKeys if t not in newKeys]

        newRowCount = self.nRows - len(delTrains) + len(newTrains)
        if newRowCount > self.nRows:
            rowsToAdd = newRowCount - self.nRows
            self.TRgrid.AppendRows(rowsToAdd, True)
        elif newRowCount < self.nRows:
            rowsToRemove = self.nRows - newRowCount
            self.TRgrid.DeleteRows(0, rowsToRemove, True)

        self.nRows = newRowCount

        row = 0
        for trid in sorted(tdata.keys(), key=self.BuildTrainKey):
            name = trid
            iname, loco, direction, engineer, blocks, signal, aspect, stopped = self.ParseTrainEntry(tdata[trid])
            currentValues = self.TRMap.get(iname, None)
            if currentValues is None:
                currentValues = TrainEntry(name, loco, direction, engineer, blocks, signal, aspect, stopped)
                self.TRMap[iname] = currentValues

            self.TRgrid.SetCellValue(row, 0, name)
            self.TRgrid.SetCellBackgroundColour(row, 0, self.colorGray if currentValues.NewName(name) else self.colorWhite)
            self.TRgrid.SetCellValue(row, 1, iname)
            self.TRgrid.SetCellValue(row, 2, loco)
            self.TRgrid.SetCellBackgroundColour(row, 2, self.colorGray if currentValues.NewLoco(loco) else self.colorWhite)
            self.TRgrid.SetCellValue(row, 3, direction)
            self.TRgrid.SetCellBackgroundColour(row, 3, self.colorGray if currentValues.NewDirection(direction) else self.colorWhite)
            self.TRgrid.SetCellValue(row, 4, engineer)
            self.TRgrid.SetCellBackgroundColour(row, 4, self.colorGray if currentValues.NewEngineer(engineer) else self.colorWhite)
            self.TRgrid.SetCellValue(row, 5, blocks)
            self.TRgrid.SetCellBackgroundColour(row, 5, self.colorGray if currentValues.NewBlocks(blocks) else self.colorWhite)
            self.TRgrid.SetCellValue(row, 6, signal)
            self.TRgrid.SetCellBackgroundColour(row, 6, self.colorGray if currentValues.NewSignal(signal) else self.colorWhite)
            self.TRgrid.SetCellValue(row, 7, aspect)
            self.TRgrid.SetCellBackgroundColour(row, 7, self.colorGray if currentValues.NewAspect(aspect) else self.colorWhite)
            self.TRgrid.SetCellValue(row, 8, stopped)
            self.TRgrid.SetCellBackgroundColour(row, 8, self.colorGray if currentValues.NewStopped(stopped) else self.colorWhite)
            row += 1

        self.TRgrid.Refresh()

    def OnClose(self, _):
        self.Destroy()


class AdjacencyDlg(wx.Dialog):
    def __init__(self, parent, adata, frame):
        wx.Dialog.__init__(self, parent, wx.ID_ANY, "Block Adjacency")
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self.frame = frame

        headings = ["West", "Block", "East"]
        colWidth = [70, 70, 70]
        colAlign = [wx.ALIGN_CENTER, wx.ALIGN_CENTER, wx.ALIGN_CENTER]
        nRows = len(adata)
        nCols = len(headings)

        self.colorWhite = wx.Colour(255, 255, 255)
        self.colorGray = wx.Colour(196, 196, 196)

        # we want to have at least 5, at most 30 lines on the display
        nr = nRows
        if nr < 5:
            nr = 5
        elif nr > 30:
            nr = 30
        ht = int(33 + nr * 19)

        self.BAgrid = gridlib.Grid(self, size=(sum(colWidth) + 20, ht))
        self.BAgrid.CreateGrid(nRows, nCols)
        self.BAgrid.EnableGridLines(True)
        self.BAgrid.SetGridLineColour(wx.BLACK)
        self.BAgrid.SetRowLabelSize(2)

        attrs = []
        for c in range(nCols):
            attr = wx.grid.GridCellAttr()
            attr.SetAlignment(colAlign[c], wx.ALIGN_CENTER)
            attr.SetReadOnly(True)
            attrs.append(attr)

        for i in range(nCols):
            self.BAgrid.SetColLabelValue(i, headings[i])
            self.BAgrid.SetColSize(i, colWidth[i])
            self.BAgrid.SetColAttr(i, attrs[i])

        self.BAMap = {}
        row = 0
        for bn in sorted(adata.keys()):
            self.BAMap[bn] = row
            self.BAgrid.SetCellValue(row, 0, adata[bn][0])
            self.BAgrid.SetCellValue(row, 1, bn)
            self.BAgrid.SetCellValue(row, 2, adata[bn][1])
            row += 1

        vsz = wx.BoxSizer(wx.VERTICAL)
        vsz.AddSpacer(20)

        hsz = wx.BoxSizer(wx.HORIZONTAL)
        hsz.AddSpacer(20)

        hsz.Add(self.BAgrid, 0, wx.EXPAND)

        hsz.AddSpacer(20)
        vsz.Add(hsz)

        vsz.AddSpacer(20)

        bRefresh = wx.Button(self, wx.ID_ANY, "Refresh", size=(100, 30))
        self.Bind(wx.EVT_BUTTON, self.OnBRefresh, bRefresh)
        vsz.Add(bRefresh, 0, wx.ALIGN_CENTER_HORIZONTAL)

        vsz.AddSpacer(20)

        self.SetSizer(vsz)
        self.Fit()
        self.Layout()

    def OnBRefresh(self, _):
        ba = self.frame.Get("blockadjacency", {})
        for bn in ba.keys():
            row = self.BAMap.get(bn, None)
            if row is not None:
                vwest = self.BAgrid.GetCellValue(row, 0)
                veast = self.BAgrid.GetCellValue(row, 2)

                self.BAgrid.SetCellBackgroundColour(row, 0, self.colorGray if vwest != ba[bn][0] else self.colorWhite)
                self.BAgrid.SetCellBackgroundColour(row, 2, self.colorGray if veast != ba[bn][1] else self.colorWhite)

                self.BAgrid.SetCellValue(row, 0, ba[bn][0])
                self.BAgrid.SetCellValue(row, 2, ba[bn][1])
            else:
                logging.debug("Refresh block adjacency - unknown block: %s" % bn)

        self.BAgrid.Refresh()

    def OnClose(self, _):
        self.Destroy()


class RoutesDlg(wx.Dialog):
    def __init__(self, parent, rtl, frame):
        wx.Dialog.__init__(self, parent, wx.ID_ANY, "Active Routes")
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self.frame = frame

        headings = ["OS", "Active Route"]
        colWidth = [100, 100]
        colAlign = [wx.ALIGN_CENTER, wx.ALIGN_CENTER]
        nRows = len(rtl)
        nCols = len(headings)

        self.colorWhite = wx.Colour(255, 255, 255)
        self.colorGray = wx.Colour(196, 196, 196)

        # we want to have at least 5, at most 30 lines on the display
        nr = nRows
        if nr < 5:
            nr = 5
        elif nr > 30:
            nr = 30
        ht = int(33 + nr * 19)

        self.RTgrid = gridlib.Grid(self, size=(sum(colWidth) + 20, ht))
        self.RTgrid.CreateGrid(nRows, nCols)
        self.RTgrid.EnableGridLines(True)
        self.RTgrid.SetGridLineColour(wx.BLACK)
        self.RTgrid.SetRowLabelSize(2)

        attrs = []
        for c in range(nCols):
            attr = wx.grid.GridCellAttr()
            attr.SetAlignment(colAlign[c], wx.ALIGN_CENTER)
            attr.SetReadOnly(True)
            attrs.append(attr)

        for i in range(nCols):
            self.RTgrid.SetColLabelValue(i, headings[i])
            self.RTgrid.SetColSize(i, colWidth[i])
            self.RTgrid.SetColAttr(i, attrs[i])

        self.RTMap = {}
        row = 0
        for rtn in sorted(rtl.keys()):
            self.RTMap[rtn] = row
            self.RTgrid.SetCellValue(row, 0, rtn)
            self.RTgrid.SetCellValue(row, 1, "None" if rtl[rtn] is None else rtl[rtn])
            row += 1

        vsz = wx.BoxSizer(wx.VERTICAL)
        vsz.AddSpacer(20)

        hsz = wx.BoxSizer(wx.HORIZONTAL)
        hsz.AddSpacer(20)

        hsz.Add(self.RTgrid, 0, wx.EXPAND)

        hsz.AddSpacer(20)
        vsz.Add(hsz)

        vsz.AddSpacer(20)

        bRefresh = wx.Button(self, wx.ID_ANY, "Refresh", size=(100, 30))
        self.Bind(wx.EVT_BUTTON, self.OnBRefresh, bRefresh)
        vsz.Add(bRefresh, 0, wx.ALIGN_CENTER_HORIZONTAL)

        vsz.AddSpacer(20)

        self.SetSizer(vsz)
        self.Fit()
        self.Layout()

    def OnBRefresh(self, _):
        rtl = self.frame.Get("getroutes", {})
        for rtn in rtl.keys():
            row = self.RTMap.get(rtn, None)
            if row is not None:
                vold = self.RTgrid.GetCellValue(row, 1)
                vnew = "None" if rtl[rtn] is None else rtl[rtn]

                self.RTgrid.SetCellBackgroundColour(row, 1, self.colorGray if vold != vnew else self.colorWhite)

                self.RTgrid.SetCellValue(row, 1, vnew)
            else:
                logging.debug("Refresh active routes - unknown OS: %s" % rtn)

        self.RTgrid.Refresh()

    def OnClose(self, _):
        self.Destroy()


class ScannerDlg(wx.Dialog):
    def __init__(self, parent, pngfile, frame):
        wx.Dialog.__init__(self, parent, wx.ID_ANY, "Scanner", style=wx.DEFAULT_DIALOG_STYLE | wx.STAY_ON_TOP)
        self.Bind(wx.EVT_CLOSE, self.OnClose)

        self.frame = frame

        vsz = wx.BoxSizer(wx.VERTICAL)
        vsz.AddSpacer(20)

        self.pngPSRY = wx.Image(pngfile, wx.BITMAP_TYPE_PNG).ConvertToBitmap()
        mask = wx.Mask(self.pngPSRY, wx.BLUE)
        self.pngPSRY.SetMask(mask)
        b = wx.StaticBitmap(self, wx.ID_ANY, self.pngPSRY)
        vsz.Add(b)
        vsz.AddSpacer(10)

        vsz.Add(wx.StaticText(self, wx.ID_ANY, "Battery Check"), 0, wx.ALIGN_CENTER_HORIZONTAL)

        vsz.AddSpacer(20)

        bReset = wx.Button(self, wx.ID_ANY, "Reset", size=BSIZE)
        vsz.Add(bReset, 0, wx.ALIGN_CENTER_HORIZONTAL)
        self.Bind(wx.EVT_BUTTON, self.OnBReset, bReset)

        vsz.AddSpacer(20)

        hsz = wx.BoxSizer(wx.HORIZONTAL)
        hsz.AddSpacer(20)
        hsz.Add(vsz)
        hsz.AddSpacer(20)

        self.SetSizer(hsz)
        self.Layout()
        self.Fit()

    def OnBReset(self, _):
        logging.debug("re/starting scanner process")
        self.frame.StartScanner()
        logging.debug("back from startscanner")

    def OnClose(self, evt):
        self.EndModal(wx.ID_OK)


class RelayDlg(wx.Dialog):
    def __init__(self, parent, rlAct, rlInact):
        wx.Dialog.__init__(self, parent, wx.ID_ANY, "Choose Relays", style=wx.DEFAULT_DIALOG_STYLE | wx.STAY_ON_TOP)
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
        wx.Dialog.__init__(self, parent, wx.ID_ANY, "Debugging Flags", style=wx.DEFAULT_DIALOG_STYLE | wx.STAY_ON_TOP)
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

        vszr.AddSpacer(10)

        self.cbBlockAdj = wx.CheckBox(self, wx.ID_ANY, "Block Adjacency")
        vszr.Add(self.cbBlockAdj)
        self.cbBlockAdj.SetValue(self.settings.debug.blockadjacency)

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

        nv = self.cbBlockAdj.GetValue()
        if nv != self.settings.debug.blockadjacency:
            self.settings.debug.blockadjacency = nv
            messages.append("Block Adjacency => %s" % nv)

        # if len(messages) == 0:
        #     dlg = wx.MessageDialog(self, "No Flags Changed",
        #                            "No Changes",
        #                            wx.OK | wx.ICON_INFORMATION
        #                            )
        # else:
        #     dlg = wx.MessageDialog(self, "\n".join(messages),
        #                            "Flags Modified",
        #                            wx.OK | wx.ICON_INFORMATION
        #                            )
        # dlg.ShowModal()
        # dlg.Destroy()


class LogLevelDlg(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, wx.ID_ANY, "Set Log Level", style=wx.DEFAULT_DIALOG_STYLE | wx.STAY_ON_TOP)
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
        self.Destroy()


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
        self.Destroy()


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
        self.Destroy()


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
        wx.Dialog.__init__(self, parent, wx.ID_ANY, title, style=wx.DEFAULT_DIALOG_STYLE | wx.STAY_ON_TOP)
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
