import wx
import wx.grid as gridlib

import os
import json


def swapbyte(b):
    return int("0b"+"{0:08b}".format(b)[::-1], 2)


class GetBitsDlg(wx.Dialog):
    def __init__(self, parent, rrServer, Nodes):
        wx.Dialog.__init__(self, parent, wx.ID_ANY, "Get Bits")
        self.Bind(wx.EVT_CLOSE, self.onCancel)

        self.runContinuous = False
        self.rrServer = rrServer
        self.Nodes = Nodes
        self.dlgBits = None
        self.dlgChx = -1
        self.sendCount = 0
        self.messageCount = 0
        self.ndName = None
        self.ndAddr = None

        vsz = wx.BoxSizer(wx.VERTICAL)       
        vsz.AddSpacer(20)

        font = wx.Font(wx.Font(14, wx.FONTFAMILY_TELETYPE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, faceName="Monospace"))

        hsz = wx.BoxSizer(wx.HORIZONTAL)
        hsz.AddSpacer(20)
        
        self.chNodes = wx.Choice(self, wx.ID_ANY, choices=["%s (0x%x)" % (x[0], x[1]) for x in self.Nodes])
        hsz.Add(self.chNodes, 0, wx.TOP, 10)
        self.chNodes.SetSelection(0)
        
        hsz.AddSpacer(20)
         
        self.bGetBits = wx.Button(self, wx.ID_ANY, "Get Bits", size=wx.Size(100, 46))
        self.Bind(wx.EVT_BUTTON, self.OnGetBits, self.bGetBits)
        hsz.Add(self.bGetBits)

        hsz.AddSpacer(20)

        self.scCount = wx.SpinCtrl(self, wx.ID_ANY, "1")
        self.scCount.SetRange(1, 50)
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

        if chx != self.dlgChx:
            try:
                self.dlgBits.Destroy()
            except (RuntimeError, AttributeError):
                pass

            self.dlgChx = chx
            self.dlgBits = None

        self.ndName, self.ndAddr = self.Nodes[chx]
        try:
            self.dlgBits.Raise()
        except (RuntimeError, AttributeError):
            self.dlgBits = ShowBitsDlg(self, self.ndName, self.ndAddr)
            self.dlgBits.Show()

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
        
        r = self.rrServer.Get("getbits", {"address": "0x%x" % self.ndAddr})

        self.dlgBits.UpdateValues(r["out"], r["in"])

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
        
        try:
            self.dlgBits.Destroy()
        except (RuntimeError, AttributeError):
            pass

        self.Destroy()


class ShowBitsDlg(wx.Dialog):
    def __init__(self, parent, ndname, ndaddr):
        title = "Node %s (0x%x) Output Input bytes" % (ndname, ndaddr)
        wx.Dialog.__init__(self, parent, wx.ID_ANY, title)
        self.Bind(wx.EVT_CLOSE, self.OnClose)

        fn = os.path.join(os.getcwd(), "tester", "nodes", ndname+".json")
        self.ndData = {}
        with open(fn) as jfp:
            try:
                self.ndData = json.load(jfp)
            except:
                self.ndData = {}

        nbytes = len(self.ndData["obytes"])
        headings = ["Byte %d" % x for x in range(nbytes)]
        colWidth = [160] * nbytes
        colAlign = [wx.ALIGN_LEFT] * nbytes
        nRows = 8
        nCols = nbytes

        self.colorWhite = wx.Colour(255, 255, 255)
        self.colorGray = wx.Colour(196, 196, 196)

        ht = int(33 + nRows * 19)

        self.BOgrid = gridlib.Grid(self, size=wx.Size(sum(colWidth) + 20, ht))
        self.BOgrid.CreateGrid(nRows, nCols)
        self.BOgrid.EnableGridLines(True)
        self.BOgrid.SetGridLineColour(wx.BLACK)
        self.BOgrid.SetRowLabelSize(2)

        attrs = []
        for c in range(nCols):
            attr = wx.grid.GridCellAttr()
            attr.SetAlignment(colAlign[c], wx.ALIGN_CENTER)
            attr.SetReadOnly(True)
            attrs.append(attr)

        for i in range(nCols):
            self.BOgrid.SetColLabelValue(i, headings[i])
            self.BOgrid.SetColSize(i, colWidth[i])
            self.BOgrid.SetColAttr(i, attrs[i])

        col = 0
        obytes = len(self.ndData["obytes"])
        for vbyte in self.ndData["obytes"]:
            row = 0
            for vbit in vbyte:
                self.BOgrid.SetCellBackgroundColour(row, col, self.colorGray)
                self.BOgrid.SetCellValue(row, col, vbit["label"])

                row += 1
            col += 1

        vsz = wx.BoxSizer(wx.VERTICAL)
        vsz.AddSpacer(10)

        self.outBitValues = [[0, 0, 0, 0, 0, 0, 0, 0] for _ in range(obytes)]
        self.outValues = [0] * obytes

        if obytes > 0:
            st = wx.StaticText(self, wx.ID_ANY, "Output Bytes")
            vsz.Add(st, 0, wx.ALIGN_CENTER)
            vsz.AddSpacer(10)

        hsz = wx.BoxSizer(wx.HORIZONTAL)
        hsz.AddSpacer(20)

        hsz.Add(self.BOgrid, 0, wx.EXPAND)
        vsz.Add(hsz, 0, wx.EXPAND)

        vsz.AddSpacer(10)

        # Now the input bytes

        nbytes = len(self.ndData["ibytes"])
        headings = ["Byte %d" % x for x in range(nbytes)]
        colWidth = [160] * nbytes
        colAlign = [wx.ALIGN_LEFT] * nbytes
        nRows = 8
        nCols = nbytes

        self.colorWhite = wx.Colour(255, 255, 255)
        self.colorGray = wx.Colour(196, 196, 196)

        ht = int(33 + nRows * 19)

        self.BIgrid = gridlib.Grid(self, size=wx.Size(sum(colWidth) + 20, ht))
        self.BIgrid.CreateGrid(nRows, nCols)
        self.BIgrid.EnableGridLines(True)
        self.BIgrid.SetGridLineColour(wx.BLACK)
        self.BIgrid.SetRowLabelSize(2)

        attrs = []
        for c in range(nCols):
            attr = wx.grid.GridCellAttr()
            attr.SetAlignment(colAlign[c], wx.ALIGN_CENTER)
            attr.SetReadOnly(True)
            attrs.append(attr)

        for i in range(nCols):
            self.BIgrid.SetColLabelValue(i, headings[i])
            self.BIgrid.SetColSize(i, colWidth[i])
            self.BIgrid.SetColAttr(i, attrs[i])

        col = 0
        ibytes = len(self.ndData["ibytes"])
        for vbyte in self.ndData["ibytes"]:
            row = 0
            for vbit in vbyte:
                self.BIgrid.SetCellBackgroundColour(row, col, self.colorGray)
                self.BIgrid.SetCellValue(row, col, vbit["label"])

                row += 1
            col += 1

        self.inBitValues = [[0, 0, 0, 0, 0, 0, 0, 0] for _ in range(ibytes)]
        self.inValues = [0] * ibytes

        if ibytes > 0:
            st = wx.StaticText(self, wx.ID_ANY, "Input Bytes")
            vsz.Add(st, 0, wx.ALIGN_CENTER)
            vsz.AddSpacer(10)

        hsz = wx.BoxSizer(wx.HORIZONTAL)
        hsz.AddSpacer(20)

        hsz.Add(self.BIgrid, 0, wx.EXPAND)

        vsz.Add(hsz)

        vsz.AddSpacer(20)

        self.SetSizer(vsz)
        self.Fit()
        self.Layout()

    def OnClose(self, _):
        self.Destroy()

    def UpdateValues(self, obytes, ibytes):
        for obx in range(len(obytes)):
            if obx >= len(self.outValues):
                continue

            oby = obytes[obx]
            if oby != self.outValues[obx]:
                self.outValues[obx] = oby
                bits = []
                for bit in range(8):
                    if (oby & (1 << bit)) != 0:
                        bits.append(1)
                    else:
                        bits.append(0)

                for bit in range(8):
                    if bits[bit] != self.outBitValues[obx][bit]:
                        self.outBitValues[obx][bit] = bits[bit]
                        self.BOgrid.SetCellBackgroundColour(bit, obx, self.colorGray if bits[bit] == 0 else self.colorWhite)

        self.BOgrid.Refresh()

        for ibx in range(len(ibytes)):
            if ibx >= len(self.inValues):
                continue

            iby = ibytes[ibx]
            if iby != self.inValues[ibx]:
                self.inValues[ibx] = iby
                bits = []
                for bit in range(8):
                    if (iby & (1 << bit)) != 0:
                        bits.append(1)
                    else:
                        bits.append(0)
                bits.reverse()

                for bit in range(8):
                    if bits[bit] != self.inBitValues[ibx][bit]:
                        self.inBitValues[ibx][bit] = bits[bit]
                        self.BIgrid.SetCellBackgroundColour(bit, ibx, self.colorGray if bits[bit] == 0 else self.colorWhite)

        self.BIgrid.Refresh()
