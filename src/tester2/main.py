import wx
import wx.grid as gridlib

import os
import sys

cmdFolder = os.getcwd()
if cmdFolder not in sys.path:
    sys.path.insert(0, cmdFolder)

from tester2.bus import Bus
from tester2.node import Node, NodeDlg, NodeByteDlg
from dispatcher.settings import Settings
from rrserver.constants import (YARD, KALE, EASTJCT, CORNELL, YARDSW, PARSONS, PORTA, PORTB, LATHAM, CARLTON, DELL,
        FOSS, HYDEJCT, HYDE, SHORE, KRULISH, NASSAUW, NASSAUE, NASSAUNX, BANK, CLIVEDEN, GREENMTN, CLIFF, SHEFFIELD)

fn = "tester2"
ofp = open(os.path.join(os.getcwd(), "output", "tester2.out"), "w")
efp = open(os.path.join(os.getcwd(), "output", "tester2.err"), "w")
sys.stdout = ofp
sys.stderr = efp

import logging

logging.basicConfig(filename=os.path.join(os.getcwd(), "logs", "%s.log" % fn), filemode='w',
                    format='%(asctime)s %(message)s', level=logging.INFO)

BTNSZ = (100, 40)


nodeInfo = [
    [YARD, 6],
    [KALE, 3],
    [EASTJCT, 2],
    [CORNELL, 2],
    [YARDSW, 5],
    [PARSONS, 4],
    [PORTA, 9],
    [PORTB, 7],
    [LATHAM, 5],
    [CARLTON, 5],
    [DELL, 4],
    [FOSS, 3],
    [HYDEJCT, 3],
    [HYDE, 5],
    [SHORE, 7],
    [KRULISH, 3],
    [NASSAUW, 8],
    [NASSAUE, 4],
    [NASSAUNX, 3],
    [BANK, 4],
    [CLIVEDEN, 4],
    [GREENMTN, 3],
    [CLIFF, 8],
    [SHEFFIELD, 4]
]


class MyRenderer(wx.grid.GridCellStringRenderer):
    def __init__(self, parent):
        super().__init__()

    def Draw(self, grid, attr, dc, rect, row, col, isSelected):
        super().Draw(grid, attr, dc, rect, row, col, isSelected)
        x, y, width, height = rect
        dc.SetPen(wx.Pen(wx.BLACK, width=1, style=wx.PENSTYLE_SOLID))
        dc.DrawLine(x, y + height - 1, x + width, y + height - 1)


class MyFrame(wx.Frame):
    def __init__(self):
        self.settings = Settings()
        
        wx.Frame.__init__(self, None, wx.ID_ANY, "I/O Tester", size=(1, 1))
        self.Bind(wx.EVT_CLOSE, self.onClose)

        self.bus = Bus(self.settings.rrserver.rrtty)
        self.running = False
        self.logMessages = False

        self.nodes = []
        maxBytes = 0
        for addr, nbytes in nodeInfo:
            if nbytes > maxBytes:
                maxBytes = nbytes
            self.nodes.append(Node(self.bus, addr, nbytes))

        self.bmGreen = wx.Image(os.path.join(os.getcwd(), "images", "atlGreen.png"), wx.BITMAP_TYPE_PNG).ConvertToBitmap()
        mask = wx.Mask(self.bmGreen, wx.BLUE)
        self.bmGreen.SetMask(mask)

        self.bmRed = wx.Image(os.path.join(os.getcwd(), "images", "atlRed.png"), wx.BITMAP_TYPE_PNG).ConvertToBitmap()
        mask = wx.Mask(self.bmRed, wx.BLUE)
        self.bmRed.SetMask(mask)

        self.bmGray = wx.Image(os.path.join(os.getcwd(), "images", "atlGray.png"), wx.BITMAP_TYPE_PNG).ConvertToBitmap()
        mask = wx.Mask(self.bmGray, wx.BLUE)
        self.bmGray.SetMask(mask)

        nNodes = len(self.nodes)
        nRows = nNodes * 2
        nCols = maxBytes +1
        colWidth = [100] + [140]*maxBytes
        ht = int(33 + nRows * 19)

        bitFont = wx.Font(12, wx.FONTFAMILY_TELETYPE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, faceName="Monospace")

        self.grid = gridlib.Grid(self, size=(sum(colWidth) + 20, ht))
        self.grid.CreateGrid(nRows, nCols)
        self.grid.EnableGridLines(False)
        self.grid.EnableEditing(False)
        self.grid.SetRowLabelSize(0)

        self.grid.GetGridWindow().Bind(wx.EVT_MOTION, self.OnGridMotion)

        self.Bind(gridlib.EVT_GRID_CELL_LEFT_CLICK, self.OnGridClick, self.grid)

        attrs = []
        for c in range(nCols):
            attr = wx.grid.GridCellAttr()
            attr.SetAlignment(wx.ALIGN_LEFT if c == 0 else wx.ALIGN_CENTER, wx.ALIGN_CENTER)
            attr.SetReadOnly(True)
            attrs.append(attr)

        for i in range(nCols):
            if i == 0:
                self.grid.SetColLabelValue(i, "Node (Address)")
            else:
                self.grid.SetColLabelValue(i, "Byte %d" % (i-1))
            self.grid.SetColSize(i, colWidth[i])
            self.grid.SetColAttr(i, attrs[i])

        for r in range(nRows):
            for c in range(0, maxBytes):
                self.grid.SetCellFont(r, c + 1, bitFont)

        self.myRenderer = MyRenderer(self)

        cIn = wx.Colour(255, 182, 178)
        cOut = wx.Colour(138, 255, 187)

        for n in range(len(self.nodes)):
            row = n * 2
            nd = self.nodes[n]
            nd.SetGrid(self.grid, row, row+1)
            self.grid.SetCellValue(row, 0, "%s (%x)" % (nd.Name(), nd.Address()))
            self.grid.SetCellRenderer(row + 1, 0, self.myRenderer)
            for c in range(nd.NBytes()):
                self.grid.SetCellRenderer(row+1, c+1, self.myRenderer)
                self.grid.SetCellBackgroundColour(row, c+1, cOut)
                self.grid.SetCellBackgroundColour(row+1, c+1, cIn)

            nd.Render()

        enasz = wx.BoxSizer(wx.VERTICAL)
        self.cbMap = {}
        enasz.AddSpacer(36)
        for n in range(nNodes):
            cb = wx.CheckBox(self, wx.ID_ANY, "")
            self.Bind(wx.EVT_CHECKBOX, self.OnEnableClick, cb)
            cb.SetValue(True)
            enasz.Add(cb)
            enasz.AddSpacer(23)
            self.cbMap[cb.GetId()] = (self.nodes[n], cb)

        sz = wx.BoxSizer(wx.VERTICAL)
        sz.AddSpacer(20)

        hz = wx.BoxSizer(wx.HORIZONTAL)
        hz.AddSpacer(10)

        hz.Add(enasz)
        hz.AddSpacer(10)

        hz.Add(self.grid, 0, wx.EXPAND)

        hz.AddSpacer(10)

        btnsz = wx.BoxSizer(wx.VERTICAL)

        btnsz.AddSpacer(20)

        self.bConnect = wx.Button(self, wx.ID_ANY, "Connect", size=BTNSZ)
        self.Bind(wx.EVT_BUTTON, self.OnBConnect, self.bConnect)
        btnsz.Add(self.bConnect, 0, wx.ALIGN_CENTER_HORIZONTAL)

        btnsz.AddSpacer(40)

        sendBox = wx.StaticBox(self, -1, "Send")
        topBorder, otherBorder = sendBox.GetBordersForSizer()
        boxsizer = wx.BoxSizer(wx.VERTICAL)
        boxsizer.AddSpacer(topBorder+20)

        self.bOnce = wx.Button(sendBox, wx.ID_ANY, "Once", size=BTNSZ)
        self.Bind(wx.EVT_BUTTON, self.OnBOnce, self.bOnce)
        boxsizer.Add(self.bOnce)
        self.bOnce.Enable(False)

        boxsizer.AddSpacer(60)

        self.bmSignal = wx.StaticBitmap(sendBox, wx.ID_ANY, self.bmGray)
        boxsizer.Add(self.bmSignal, 0, wx.ALIGN_CENTER_HORIZONTAL)

        boxsizer.AddSpacer(10)

        st = wx.StaticText(sendBox, wx.ID_ANY, "Interval (usec)")
        boxsizer.Add(st, 0, wx.ALIGN_CENTER_HORIZONTAL)
        boxsizer.AddSpacer(10)
        self.scInterval = wx.SpinCtrl(sendBox, wx.ID_ANY, "")
        self.scInterval.SetRange(100, 2000)
        self.scInterval.SetValue(400)
        self.scInterval.SetIncrement(100)
        boxsizer.Add(self.scInterval, 0, wx.ALIGN_CENTER_HORIZONTAL)

        boxsizer.AddSpacer(20)

        self.bStart = wx.Button(sendBox, wx.ID_ANY, "Continuous", size=BTNSZ)
        self.Bind(wx.EVT_BUTTON, self.OnBStart, self.bStart)
        boxsizer.Add(self.bStart)
        self.bStart.Enable(False)

        boxsizer.AddSpacer(20)

        self.bStop = wx.Button(sendBox, wx.ID_ANY, "Stop", size=BTNSZ)
        self.Bind(wx.EVT_BUTTON, self.OnBStop, self.bStop)
        boxsizer.Add(self.bStop)
        self.bStop.Enable(False)

        boxsizer.AddSpacer(20)

        hboxsizer = wx.BoxSizer(wx.HORIZONTAL)
        hboxsizer.AddSpacer(20)
        hboxsizer.Add(boxsizer)
        hboxsizer.AddSpacer(20)

        sendBox.SetSizer(hboxsizer)

        btnsz.Add(sendBox)

        btnsz.AddSpacer(100)

        self.cbLog = wx.CheckBox(self, wx.ID_ANY, "Log Messages", size=BTNSZ)
        self.Bind(wx.EVT_CHECKBOX, self.OnCBLog, self.cbLog)
        btnsz.Add(self.cbLog, 0, wx.ALIGN_CENTER_HORIZONTAL)

        btnsz.AddSpacer(90)

        self.bSelectNone = wx.Button(self, wx.ID_ANY, "Select None", size=BTNSZ)
        self.Bind(wx.EVT_BUTTON, self.OnBSelectNone, self.bSelectNone)
        btnsz.Add(self.bSelectNone, 0, wx.ALIGN_CENTER_HORIZONTAL)

        btnsz.AddSpacer(20)

        self.bSelectAll = wx.Button(self, wx.ID_ANY, "Select All", size=BTNSZ)
        self.Bind(wx.EVT_BUTTON, self.OnBSelectAll, self.bSelectAll)
        btnsz.Add(self.bSelectAll, 0, wx.ALIGN_CENTER_HORIZONTAL)

        btnsz.AddSpacer(80)

        self.bRefresh = wx.Button(self, wx.ID_ANY, "Refresh", size=BTNSZ)
        self.Bind(wx.EVT_BUTTON, self.OnBRefresh, self.bRefresh)
        btnsz.Add(self.bRefresh, 0, wx.ALIGN_CENTER_HORIZONTAL)

        btnsz.AddSpacer(20)

        hz.Add(btnsz)

        hz.AddSpacer(10)

        sz.Add(hz)
        sz.AddSpacer(20)

        hsz = wx.BoxSizer(wx.HORIZONTAL)
        hsz.AddSpacer(20)
        hsz.Add(sz)
        hsz.AddSpacer(20)
        
        self.SetSizer(hsz)
        self.Fit()

        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.OnTimer, self.timer)

        self.CenterOnScreen()

        wx.CallAfter(self.refresh)

    def OnBConnect(self, _):
        if self.bus.isOpen():
            self.bus.close()
            self.bStart.Enable(False)
            self.bStop.Enable(False)
            self.bOnce.Enable(False)
            self.bConnect.SetLabel("Connect")
            self.bmSignal.SetBitmap(self.bmRed)

        else:
            self.bus.Connect()
            if not self.bus.isOpen():
                msg = self.bus.Error()
                if msg is None:
                    msg = "Unknwon error"
                dlg = wx.MessageDialog(self, msg, "Bus Connect Error", wx.OK | wx.ICON_INFORMATION)
                dlg.ShowModal()
                dlg.Destroy()
                self.bmSignal.SetBitmap(self.bmGray)

            else:
                self.bStart.Enable(True)
                self.bStop.Enable(False)
                self.bOnce.Enable(True)
                self.bConnect.SetLabel("Disconnect")
                self.bmSignal.SetBitmap(self.bmRed)

    def refresh(self):
        self.grid.ClearSelection()
        self.grid.Refresh()
        if not self.bus.isOpen():
            self.bmSignal.SetBitmap(self.bmGray)
        elif self.running:
            self.bmSignal.SetBitmap(self.bmGreen)
        else:
            self.bmSignal.SetBitmap(self.bmRed)

    def OnBRefresh(self, _):
        self.refresh()

    def OnCBLog(self, _):
        self.logMessages = self.cbLog.IsChecked()

    def StartTimer(self):
        self.timer.Start(self.scInterval.GetValue())

    def StopTimer(self):
        self.timer.Stop()

    def OnTimer(self, _):
        self.SendOne()

    def SendOne(self):
        try:
            for nd in self.nodes:
                nd.OutIn(self.logMessages)
        except Exception as e:
            print("Exception %s" % str(e))

    def ResetNodes(self):
        for n in self.nodes:
            n.Reset()

    def OnBOnce(self, _):
        self.ResetNodes()
        self.SendOne()

    def OnBStart(self, _):
        self.ResetNodes()
        self.bOnce.Enable(False)
        self.bStart.Enable(False)
        self.bStop.Enable(True)
        self.StartTimer()
        self.running = True
        self.bmSignal.SetBitmap(self.bmGreen)

    def OnBStop(self, _):
        self.bOnce.Enable(True)
        self.bStart.Enable(True)
        self.bStop.Enable(False)
        self.StopTimer()
        self.running = False
        self.bmSignal.SetBitmap(self.bmRed)

    def OnGridMotion(self, evt):
        pass

    def OnBSelectAll(self, _):
        for nd, cb in self.cbMap.values():
            cb.SetValue(True)
            nd.Enable(True)

    def OnBSelectNone(self, _):
        for nd, cb in self.cbMap.values():
            cb.SetValue(False)
            nd.Enable(False)

    def OnEnableClick(self, evt):
        id = evt.GetId()
        try:
            nd, cb = self.cbMap[id]
            nd.Enable(cb.IsChecked())
        except KeyError:
            # skip this message if we can't identify the node
            pass

    def OnGridClick(self, evt):
        r = evt.GetRow()
        c = evt.GetCol()
        if c == 0:
            nr = int(r / 2)
            nd = self.nodes[nr]
            dlg = nd.Dialog()
            if dlg is None:
                dlg = NodeDlg(self, nd)
                nd.SetDialog(dlg)
                dlg.Show()
            else:
                dlg.Raise()
        else:  # c != 0
            dbyte = c - 1
            if dbyte < 0:
                return

            input = r%2 != 0

            nx = int(r/2)
            nd = self.nodes[nx]

            byteId = "%s%d" % ("I" if input else "O", dbyte)
            dlg = nd.ByteDialog(byteId)
            if dlg is None:
                dlg = NodeByteDlg(self, nd, dbyte, input)
                nd.SetByteDialog(dlg, byteId)
                dlg.Show()
            else:
                dlg.Raise()

    def onClose(self, evt):
        self.shutdown()
        
    def shutdown(self):
        try:
            self.bus.close()
        except:
            pass

        try:
            self.Destroy()
        except:
            pass


app = wx.App()
frame = MyFrame()
frame.Show(True)
try:
    app.MainLoop()
except Exception as e:
    pass
