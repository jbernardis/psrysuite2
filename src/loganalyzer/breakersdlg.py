import wx
import wx.grid as gridlib
import os
import sys

BTNDIM = (100, 40)


class BreakersDlg(wx.Dialog):
	def __init__(self, parent, rpt):
		self.parent = parent
		self.rpt = rpt

		self.csvDir = os.path.join(os.getcwd(), "output")

		wx.Dialog.__init__(self, self.parent, style=wx.DEFAULT_FRAME_STYLE)
		self.SetTitle("Breaker Report")
		self.Bind(wx.EVT_CLOSE, self.OnClose)

		labelFont = wx.Font(12, wx.FONTFAMILY_ROMAN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, faceName="Arial")

		headings = ["Breaker", "Time", "Duration"]
		hkeys = ["breaker", "time", "duration"]
		colWidth = [90, 180, 70]
		colAlign = [wx.ALIGN_LEFT, wx.ALIGN_CENTER, wx.ALIGN_CENTER]
		nRows = len(self.rpt)
		nCols = len(headings)

		# we want to have at least 5, at most 30 lines on the display
		nr = nRows
		if nr < 5:
			nr = 5
		elif nr > 30:
			nr = 30
		ht = int(33 + nr * 19)

		self.Brkgrid = gridlib.Grid(self, size=(sum(colWidth) + 100, ht))
		self.Brkgrid.CreateGrid(nRows, nCols)
		self.Brkgrid.EnableGridLines(True)
		self.Brkgrid.SetGridLineColour(wx.BLACK)

		attrs = []
		for c in range(nCols):
			attr = wx.grid.GridCellAttr()
			attr.SetAlignment(colAlign[c], wx.ALIGN_CENTER)
			attr.SetReadOnly(True)
			attrs.append(attr)

		for i in range(nCols):
			self.Brkgrid.SetColLabelValue(i, headings[i])
			self.Brkgrid.SetColSize(i, colWidth[i])
			self.Brkgrid.SetColAttr(i, attrs[i])

		row = 0
		print("%s" % str(self.rpt))
		for r in self.rpt:
			for col in range(nCols):
				self.Brkgrid.SetCellValue(row, col, str(r[hkeys[col]]))
			row += 1

		self.bOK = wx.Button(self, wx.ID_ANY, "Generate\nCSV File", size=BTNDIM)
		self.Bind(wx.EVT_BUTTON, self.OnCSV, self.bOK)

		vsz = wx.BoxSizer(wx.VERTICAL)
		vsz.AddSpacer(20)

		vsz.Add(self.Brkgrid, 0, wx.EXPAND)

		vsz.AddSpacer(20)

		vsz.Add(self.bOK, 0, wx.ALIGN_CENTER_HORIZONTAL)

		vsz.AddSpacer(20)

		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.AddSpacer(20)
		hsz.Add(vsz)
		hsz.AddSpacer(20)

		self.SetSizer(hsz)
		self.Fit()
		self.Layout()

	def OnCSV(self, evt):
		self.GenerateCSV(self.rpt)

	def OnClose(self, _):
		self.EndModal(wx.ID_CANCEL)

	def GenerateCSV(self, rpt):
		wildcard = "CSV files (*.csv)|*.csv"
		dlg = wx.FileDialog(
			self, message="Save file as ...", defaultDir=self.csvDir,
			defaultFile="", wildcard=wildcard, style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT
		)
		if dlg.ShowModal() == wx.ID_OK:
			path = dlg.GetPath()
			self.csvDir = os.path.split(path)[0]
			dlg.Destroy()
		else:
			dlg.Destroy()
			return

		with open(path, "w") as csvfp:
			if len(rpt) > 0:
				keys = list(rpt[0].keys())
				colNames = "%s" % ",".join(["\"%s\"" % k for k in keys])
				lines = []
				for r in rpt:
					rq = {k: ("\"%s\"" % r[k]) for k in keys}
					lines.append("%s" % (",".join([rq[k] for k in keys])))

				csvfp.write("%s\n" % colNames)
				for line in lines:
					csvfp.write("%s\n" % line)

