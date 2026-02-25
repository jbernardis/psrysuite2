import wx
import wx.grid as gridlib
import os
import sys

BTNDIM = (100, 40)


class StoppingBlocksDlg(wx.Dialog):
	def __init__(self, parent, rpt):
		self.parent = parent
		self.rpt = rpt

		sbrpt = []
		for r in self.rpt:
			# only interested in stopping sections
			if not (r["block"].endswith(".E") or r["block"].endswith(".W")):
				continue
			sbrpt.append(r)

		self.csvDir = os.path.join(os.getcwd(), "output")

		wx.Dialog.__init__(self, self.parent, style=wx.DEFAULT_FRAME_STYLE)
		self.SetTitle("Stopping block Times")
		self.Bind(wx.EVT_CLOSE, self.OnClose)

		labelFont = wx.Font(12, wx.FONTFAMILY_ROMAN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, faceName="Arial")

		headings = ["Train", "Block", "Time", "Engineer"]
		hkeys = ["train", "block", "time", "engineer"]
		colWidth = [70, 70, 70, 300]
		colAlign = [wx.ALIGN_CENTER, wx.ALIGN_CENTER, wx.ALIGN_CENTER, wx.ALIGN_LEFT]
		nRows = len(sbrpt)
		nCols = len(headings)

		# we want to have at least 5, at most 30 lines on the display
		nr = nRows
		if nr < 5:
			nr = 5
		elif nr > 30:
			nr = 30
		ht = int(33 + nr * 19)

		self.SBgrid = gridlib.Grid(self, size=(sum(colWidth) + 100, ht))
		self.SBgrid.CreateGrid(nRows, nCols)
		self.SBgrid.EnableGridLines(True)
		self.SBgrid.SetGridLineColour(wx.BLACK)

		self.stSBLabel = wx.StaticText(self, wx.ID_ANY, "Raw Data", size=(sum(colWidth ) +100, -1), style=wx.ALIGN_CENTER)
		self.stSBLabel.SetFont(labelFont)

		attrs = []
		for c in range(nCols):
			attr = wx.grid.GridCellAttr()
			attr.SetAlignment(colAlign[c], wx.ALIGN_CENTER)
			attr.SetReadOnly(True)
			attrs.append(attr)

		for i in range(nCols):
			self.SBgrid.SetColLabelValue(i, headings[i])
			self.SBgrid.SetColSize(i, colWidth[i])
			self.SBgrid.SetColAttr(i, attrs[i])

		row = 0
		engineers = {}
		for r in sbrpt:
			eng = "" if r["engineer"] is None else r["engineer"]
			if eng not in engineers:
				engineers[eng] = {"seconds": 0, "tally": 0}
			engineers[eng]["seconds"] += r["time"]
			engineers[eng]["tally"] += 1

			for col in range(nCols):
				if r[hkeys[col]] is None or r[hkeys[col]] == "None":
					self.SBgrid.SetCellValue(row, col, "")
				else:
					self.SBgrid.SetCellValue(row, col, str(r[hkeys[col]]))
			row += 1

		headings = ["Engineer", "Occurrences", "Total Time"]
		colWidth = [300, 90, 90]
		colAlign = [wx.ALIGN_LEFT, wx.ALIGN_CENTER, wx.ALIGN_CENTER]
		nRows = len(engineers)
		nCols = len(headings)

		self.Enggrid = gridlib.Grid(self, size=(sum(colWidth) + 100, ht))
		self.Enggrid.CreateGrid(nRows, nCols)
		self.Enggrid.EnableGridLines(True)
		self.Enggrid.SetGridLineColour(wx.BLACK)

		self.stEngLabel = wx.StaticText(self, wx.ID_ANY, "By Engineer", size=(sum(colWidth ) +100, -1), style=wx.ALIGN_CENTER)
		self.stEngLabel.SetFont(labelFont)

		attrs = []
		for c in range(nCols):
			attr = wx.grid.GridCellAttr()
			attr.SetAlignment(colAlign[c], wx.ALIGN_CENTER)
			attr.SetReadOnly(True)
			attrs.append(attr)

		for i in range(nCols):
			self.Enggrid.SetColLabelValue(i, headings[i])
			self.Enggrid.SetColSize(i, colWidth[i])
			self.Enggrid.SetColAttr(i, attrs[i])

		row = 0
		for reng in sorted(engineers.keys()):
			rinfo = engineers[reng]
			tally = "%d" % rinfo["tally"]
			seconds = "%d" % rinfo["seconds"]

			for col in range(nCols):
				self.Enggrid.SetCellValue(row, 0, reng)
				self.Enggrid.SetCellValue(row, 1, tally)
				self.Enggrid.SetCellValue(row, 2, seconds)
			row += 1

		self.bOK = wx.Button(self, wx.ID_ANY, "Generate\nCSV File", size=BTNDIM)
		self.Bind(wx.EVT_BUTTON, self.OnCSV, self.bOK)

		vsz = wx.BoxSizer(wx.VERTICAL)
		vsz.AddSpacer(20)

		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.Add(self.stSBLabel)

		hsz.AddSpacer(20)
		hsz.Add(self.stEngLabel)

		vsz.Add(hsz)
		vsz.AddSpacer(10)

		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.Add(self.SBgrid, 0, wx.EXPAND)

		hsz.AddSpacer(20)
		hsz.Add(self.Enggrid, 0, wx.EXPAND)

		vsz.Add(hsz)

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
					if r["engineer"] is None or r["engineer"] == "None":
						r["engineer"] = ""

					rq = {k: ("\"%s\"" % r[k]) for k in keys}
					lines.append("%s" % (",".join([rq[k] for k in keys])))

				csvfp.write("%s\n" % colNames)
				for line in lines:
					csvfp.write("%s\n" % line)
