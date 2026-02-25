import wx
import wx.grid as gridlib
import os

BTNDIM = (100, 40)


class BlockTraversalDlg(wx.Dialog):
	def __init__(self, parent, rpt):
		self.parent = parent
		self.rpt = rpt

		self.csvDir = os.path.join(os.getcwd(), "output")

		wx.Dialog.__init__(self, self.parent, style=wx.DEFAULT_FRAME_STYLE)
		self.SetTitle("Block Traversal Times")
		self.Bind(wx.EVT_CLOSE, self.OnClose)

		labelFont = wx.Font(12, wx.FONTFAMILY_ROMAN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, faceName="Arial")

		headings = ["Block", "Time", "Train", "Engineer"]
		hkeys = ["block", "time", "train", "engineer"]
		colWidth = [70, 70, 70, 300]
		colAlign = [wx.ALIGN_CENTER, wx.ALIGN_CENTER, wx.ALIGN_CENTER, wx.ALIGN_LEFT]
		nRows = len(rpt)
		nCols = len(headings)

		# we want to have at least 5, at most 30 lines on the display
		nr = nRows
		if nr < 5:
			nr = 5
		elif nr > 30:
			nr = 30
		ht = int(33 + nr * 19)

		self.BTgrid = gridlib.Grid(self, size=(sum(colWidth) + 100, ht))
		self.BTgrid.CreateGrid(nRows, nCols)
		self.BTgrid.EnableGridLines(True)
		self.BTgrid.SetGridLineColour(wx.BLACK)

		self.stBTLabel = wx.StaticText(self, wx.ID_ANY, "Raw Data", size=(sum(colWidth ) +100, -1), style=wx.ALIGN_CENTER)
		self.stBTLabel.SetFont(labelFont)

		attrs = []
		for c in range(nCols):
			attr = wx.grid.GridCellAttr()
			attr.SetAlignment(colAlign[c], wx.ALIGN_CENTER)
			attr.SetReadOnly(True)
			attrs.append(attr)

		for i in range(nCols):
			self.BTgrid.SetColLabelValue(i, headings[i])
			self.BTgrid.SetColSize(i, colWidth[i])
			self.BTgrid.SetColAttr(i, attrs[i])

		blockTimes = {}
		row = 0
		for rline in rpt:
			blknm = rline.get("block", None)
			blktm = rline.get("time", None)
			if blknm is None or blktm is None:
				continue

			if blknm.endswith(".E") or blknm.endswith(".W"):
				incr = 0
				bn = blknm[:-2]
			else:
				incr = 1
				bn = blknm

			if bn not in blockTimes:
				blockTimes[bn] = {"seconds": 0, "tally": 0}

			blockTimes[bn]["seconds"] += int(blktm)
			blockTimes[bn]["tally"] += incr

			for col in range(nCols):
				if rline[hkeys[col]] is None or rline[hkeys[col]] == "None":
					self.BTgrid.SetCellValue(row, col, "")
				else:
					self.BTgrid.SetCellValue(row, col, str(rline[hkeys[col]]))
			row += 1

		self.Avggrid = gridlib.Grid(self, size=(240, ht))
		self.Avggrid.CreateGrid(len(blockTimes), 2)
		self.Avggrid.EnableGridLines(True)
		self.Avggrid.SetGridLineColour(wx.BLACK)

		self.stAvgLabel = wx.StaticText(self, wx.ID_ANY, "Block Averages", size=(240, -1), style=wx.ALIGN_CENTER)
		self.stAvgLabel.SetFont(labelFont)

		attrs = []
		for c in range(2):
			attr = wx.grid.GridCellAttr()
			attr.SetAlignment(wx.ALIGN_CENTER, wx.ALIGN_CENTER)
			attr.SetReadOnly(True)
			attrs.append(attr)

		avgHeadings = ["Block", "Average"]
		avgWidth = [70, 70]
		for i in range(2):
			self.Avggrid.SetColLabelValue(i, avgHeadings[i])
			self.Avggrid.SetColSize(i, avgWidth[i])
			self.Avggrid.SetColAttr(i, attrs[i])

		row = 0
		for blk, info in blockTimes.items():
			avg = int(info["seconds" ] /info["tally"])
			self.Avggrid.SetCellValue(row, 0, blk)
			self.Avggrid.SetCellValue(row, 1, "%d" % avg)
			row += 1

		self.bOK = wx.Button(self, wx.ID_ANY, "Generate\nCSV File", size=BTNDIM)
		self.Bind(wx.EVT_BUTTON, self.OnCSV, self.bOK)

		vsz = wx.BoxSizer(wx.VERTICAL)
		vsz.AddSpacer(20)

		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.Add(self.stBTLabel)

		hsz.AddSpacer(20)

		hsz.Add(self.stAvgLabel)

		vsz.Add(hsz)
		vsz.AddSpacer(10)

		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.Add(self.BTgrid, 0, wx.EXPAND)

		hsz.AddSpacer(20)

		hsz.Add(self.Avggrid, 0, wx.EXPAND)

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
