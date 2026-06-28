import wx
import logging

BTNSZ = wx.Size(120, 33)


class CheckTrainsDlg(wx.Dialog):
	def __init__(self, parent, brokenTrains, locosNonUnique, trblocks, trUnknown):
		wx.Dialog.__init__(self, parent, wx.ID_ANY, "Problem Trains")
		self.parent = parent
		self.brokenTrains = brokenTrains

		self.selectedTrain = None
		self.selectedSeg = None

		self.SetTitle("Problem Trains")
		self.Bind(wx.EVT_CLOSE, self.onClose)

		bgGray1 = wx.Colour(192, 192, 192)
		bgGray2 = wx.Colour(224, 224, 224)

		hdgFont = wx.Font(wx.Font(12, wx.FONTFAMILY_ROMAN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, faceName="Arial"))
		btnFont = wx.Font(wx.Font(10, wx.FONTFAMILY_ROMAN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, faceName="Arial"))
		textFont = wx.Font(
			wx.Font(12, wx.FONTFAMILY_ROMAN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, faceName="Arial"))

		vsz = wx.BoxSizer(wx.VERTICAL)
		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.AddSpacer(20)

		grid = wx.GridBagSizer(hgap=5, vgap=5)

		stHeadingTrain = wx.StaticText(self, wx.ID_ANY, "Train", size=wx.Size(100, 23), style=wx.ALIGN_CENTRE_VERTICAL)
		stHeadingTrain.SetFont(hdgFont)
		grid.Add(stHeadingTrain, pos=(0, 0), flag=wx.ALIGN_CENTER_VERTICAL)
		stHeadingSegment = wx.StaticText(self, wx.ID_ANY, "Issue", size=wx.Size(200, 23), style=wx.ALIGN_CENTRE_VERTICAL)
		stHeadingSegment.SetFont(hdgFont)
		grid.Add(stHeadingSegment, pos=(0, 1), flag=wx.ALIGN_CENTER_VERTICAL)

		gline = 1
		self.bMap = {}

		for tr, segs, ooo in brokenTrains:
			trid = tr.Name()
			if ooo:
				stTrid = wx.StaticText(self, wx.ID_ANY, trid, size=wx.Size(100, 23), style=wx.ALIGN_CENTRE_VERTICAL)
				stTrid.SetBackgroundColour(bgGray1 if gline % 2 == 0 else bgGray2)
				stTrid.SetFont(textFont)
				grid.Add(stTrid, pos=(gline, 0), flag=wx.ALIGN_CENTER_VERTICAL)

				stSeg = wx.StaticText(self, wx.ID_ANY, "Blocks Out of Order", size=wx.Size(300, 23), style=wx.ALIGN_CENTRE_VERTICAL)
				stSeg.SetBackgroundColour(bgGray1 if gline % 2 == 0 else bgGray2)
				stSeg.SetFont(textFont)
				grid.Add(stSeg, pos=(gline, 1), flag=wx.ALIGN_CENTER_VERTICAL)

				b = wx.Button(self, wx.ID_ANY, "Re-Order", size=BTNSZ)
				b.user_data = trid
				self.Bind(wx.EVT_BUTTON, self.bBOrderClick, b)
				b.SetFont(btnFont)
				grid.Add(b, pos=(gline, 2))
				gline += 1

			segn = 1
			for seg in segs:
				stTrid = wx.StaticText(self, wx.ID_ANY, trid, size=wx.Size(100, 23), style=wx.ALIGN_CENTRE_VERTICAL)
				stTrid.SetBackgroundColour(bgGray1 if gline % 2 == 0 else bgGray2)
				stTrid.SetFont(textFont)
				grid.Add(stTrid, pos=(gline, 0), flag=wx.ALIGN_CENTER_VERTICAL)

				stSeg = wx.StaticText(self, wx.ID_ANY, "Segment %d: %s" % (segn, ", ".join(seg)), size=wx.Size(300, 23), style=wx.ALIGN_CENTRE_VERTICAL)
				stSeg.SetBackgroundColour(bgGray1 if gline % 2 == 0 else bgGray2)
				stSeg.SetFont(textFont)
				grid.Add(stSeg, pos=(gline, 1), flag=wx.ALIGN_CENTER_VERTICAL)

				b = wx.Button(self, wx.ID_ANY, "Split", size=BTNSZ)
				b.user_data = [trid, seg]
				self.Bind(wx.EVT_BUTTON, self.bBSplitClick, b)
				b.SetFont(btnFont)
				grid.Add(b, pos=(gline, 2))

				self.bMap[gline] = [trid, seg]

				gline += 1

		for trid, trinfo in locosNonUnique.items():
			tr, lid = trinfo
			stTrid = wx.StaticText(self, wx.ID_ANY, tr.Name(), size=wx.Size(100, 23), style=wx.ALIGN_CENTRE_VERTICAL)
			stTrid.SetBackgroundColour(bgGray1 if gline % 2 == 0 else bgGray2)
			stTrid.SetFont(textFont)
			grid.Add(stTrid, pos=(gline, 0), flag=wx.ALIGN_CENTER_VERTICAL)

			stLoco = wx.StaticText(self, wx.ID_ANY, "Non unique loco ID: %s" % lid, size=wx.Size(300, 23), style=wx.ALIGN_CENTRE_VERTICAL)
			stLoco.SetBackgroundColour(bgGray1 if gline % 2 == 0 else bgGray2)
			stLoco.SetFont(textFont)
			grid.Add(stLoco, pos=(gline, 1), flag=wx.ALIGN_CENTER_VERTICAL)

			b = wx.Button(self, wx.ID_ANY, "Edit", size=BTNSZ)
			b.user_data = trid
			self.Bind(wx.EVT_BUTTON, self.bBEditClick, b)
			b.SetFont(btnFont)
			grid.Add(b, pos=(gline, 2))
			gline += 1

		for trid, issue in trblocks.items():
			stTrid = wx.StaticText(self, wx.ID_ANY, trid, size=wx.Size(100, 23), style=wx.ALIGN_CENTRE_VERTICAL)
			stTrid.SetBackgroundColour(bgGray1 if gline % 2 == 0 else bgGray2)
			stTrid.SetFont(textFont)
			grid.Add(stTrid, pos=(gline, 0), flag=wx.ALIGN_CENTER_VERTICAL)

			stLoco = wx.StaticText(self, wx.ID_ANY, issue, size=wx.Size(300, 23), style=wx.ALIGN_CENTRE_VERTICAL)
			stLoco.SetBackgroundColour(bgGray1 if gline % 2 == 0 else bgGray2)
			stLoco.SetFont(textFont)
			grid.Add(stLoco, pos=(gline, 1), flag=wx.ALIGN_CENTER_VERTICAL)
			gline += 1

		for trid in trUnknown:
			stTrid = wx.StaticText(self, wx.ID_ANY, trid, size=wx.Size(100, 23), style=wx.ALIGN_CENTRE_VERTICAL)
			stTrid.SetBackgroundColour(bgGray1 if gline % 2 == 0 else bgGray2)
			stTrid.SetFont(textFont)
			grid.Add(stTrid, pos=(gline, 0), flag=wx.ALIGN_CENTER_VERTICAL)

			stLoco = wx.StaticText(self, wx.ID_ANY, "Unknown Train", size=wx.Size(300, 23), style=wx.ALIGN_CENTRE_VERTICAL)
			stLoco.SetBackgroundColour(bgGray1 if gline % 2 == 0 else bgGray2)
			stLoco.SetFont(textFont)
			grid.Add(stLoco, pos=(gline, 1), flag=wx.ALIGN_CENTER_VERTICAL)
			gline += 1

		hsz.Add(grid, 0, wx.ALIGN_CENTER_VERTICAL)

		hsz.AddSpacer(20)

		vsz.Add(hsz, 0, wx.ALIGN_CENTER_HORIZONTAL)
		vsz.AddSpacer(20)

		sz = wx.BoxSizer(wx.HORIZONTAL)

		sz.AddSpacer(20)

		self.bExit = wx.Button(self, wx.ID_ANY, "Exit", size=BTNSZ)
		self.bExit.SetFont(btnFont)
		sz.Add(self.bExit)
		self.Bind(wx.EVT_BUTTON, self.bExitPressed, self.bExit)

		sz.AddSpacer(20)

		vsz.Add(sz, 0, wx.ALIGN_CENTER_HORIZONTAL)
		vsz.AddSpacer(20)

		self.SetSizer(vsz)
		self.Layout()
		self.Fit()

	def bBSplitClick(self, evt):
		btn = evt.GetEventObject()
		bdata = btn.user_data
		logging.debug("split button data: %s" % str(bdata))
		self.selectedTrain = bdata[0]
		self.selectedSeg = bdata[1]
		self.EndModal(wx.ID_CUT)

	def bBOrderClick(self, evt):
		btn = evt.GetEventObject()
		bdata = btn.user_data
		logging.debug("order button data: %s" % str(bdata))
		self.selectedTrain = bdata
		self.selectedSeg = None
		self.EndModal(wx.ID_FORWARD)

	def bBEditClick(self, evt):
		btn = evt.GetEventObject()
		bdata = btn.user_data
		logging.debug("edit loco for train: %s" % str(bdata))
		self.selectedTrain = bdata
		self.selectedSeg = None
		self.EndModal(wx.ID_EDIT)

	def GetResults(self):
		return self.selectedTrain, self.selectedSeg

	def bExitPressed(self, _):
		self.doCancel()

	def onClose(self, _):
		self.doCancel()

	def doCancel(self):
		self.EndModal(wx.ID_CANCEL)
