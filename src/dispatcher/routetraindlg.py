import wx
import logging

from dispatcher.constants import BlockName
from dispatcher.block import formatRouteDesignator
from dispatcher.trainlist import YardBlocks

BUTTONSIZE = (90, 30)
COLSIG = 100
COLOS = 350
COLBLK = 60

HILITEON = "Hilite ON"
HILITEOFF = "Hilite OFF"


class RouteTrainDlg(wx.Dialog):
	def __init__(self, parent, train, trinfo, template, isDispatcher, blocks):
		wx.Dialog.__init__(self, parent, wx.ID_ANY, "")
		self.parent = parent
		self.train = train
		self.template = template
		# loco = train.Loco()
		self.trainName = train.Name()
		self.trinfo = trinfo
		self.isDispatcher = isDispatcher
		self.blocks = blocks
		self.sequence = trinfo["sequence"]
		self.Bind(wx.EVT_CLOSE, self.onClose)
		self.hilited = False

		self.colors = [wx.Colour(225, 255, 240), wx.Colour(138, 255, 197)]
		self.line = 0
		
		self.SetTitle("Route Status")
		
		self.font = wx.Font(wx.Font(14, wx.FONTFAMILY_ROMAN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, faceName="Arial"))
		self.fontTrainID = wx.Font(wx.Font(22, wx.FONTFAMILY_ROMAN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, faceName="Arial"))
		self.bmpArrow = self.parent.bitmaps.arrow
		self.bmpClear = self.parent.bitmaps.clear
		self.lastStepx = None

		self.goodBlocks = [step["block"] for step in self.sequence]
		self.goodOSs = [formatRouteDesignator(step["route"]) for step in self.sequence]
		self.startingBlock = trinfo["startblock"]

		logging.debug("template train = (%s)" % self.template)

		vsz = wx.BoxSizer(wx.VERTICAL)

		hsz = wx.BoxSizer(wx.HORIZONTAL)
		st = wx.StaticText(self, wx.ID_ANY, "Train:")
		st.SetFont(self.font)
		hsz.Add(st, 0, wx.ALIGN_CENTER_VERTICAL)
		hsz.AddSpacer(10)
		trstr = self.trainName
		if self.template is not None:
			trstr += " (%s)" % str(self.template)
		st = wx.StaticText(self, wx.ID_ANY, trstr)
		st.SetFont(self.fontTrainID)
		hsz.Add(st)
		vsz.Add(hsz, 0, wx.ALIGN_CENTER_HORIZONTAL)

		hsz = wx.BoxSizer(wx.HORIZONTAL)
		st = wx.StaticText(self, wx.ID_ANY, "Engineer:")
		st.SetFont(self.font)
		hsz.Add(st, 0, wx.ALIGN_CENTER_VERTICAL)
		hsz.AddSpacer(10)
		engineer = train.Engineer()
		if engineer is None:
			engineer = "(None)"
		st = wx.StaticText(self, wx.ID_ANY, engineer)
		st.SetFont(self.font)
		hsz.Add(st)
		vsz.Add(hsz, 0, wx.ALIGN_CENTER_HORIZONTAL)

		vsz.AddSpacer(20)
		vsz.Add(self.AddHeaders())
		vsz.AddSpacer(10)
		
		self.bmps = []		
		vsz.Add(self.AddLine(None, None, None, trinfo["startblock"]))
		
		for step in trinfo["sequence"]:
			vsz.Add(self.AddLine(step["signal"], step["os"], step["route"], step["block"]))
			
		vsz.AddSpacer(20)

		hsz = wx.BoxSizer(wx.HORIZONTAL)

		if self.isDispatcher:
			self.bRoute = wx.Button(self, wx.ID_ANY, "Set Route", size=BUTTONSIZE)
			self.Bind(wx.EVT_BUTTON, self.OnBRoute, self.bRoute)
			hsz.Add(self.bRoute)
			
			hsz.AddSpacer(30)
			
			self.bSignal = wx.Button(self, wx.ID_ANY, "Set Signal", size=BUTTONSIZE)
			self.Bind(wx.EVT_BUTTON, self.OnBSignal, self.bSignal)
			hsz.Add(self.bSignal)

			hsz.AddSpacer(30)

		self.bRefresh = wx.Button(self, wx.ID_ANY, "Refresh", size=BUTTONSIZE)
		self.Bind(wx.EVT_BUTTON, self.OnBRefresh, self.bRefresh)
		hsz.Add(self.bRefresh)

		hsz.AddSpacer(30)

		self.bHilite = wx.Button(self, wx.ID_ANY, HILITEON, size=BUTTONSIZE)
		self.Bind(wx.EVT_BUTTON, self.OnBHiLite, self.bHilite)
		hsz.Add(self.bHilite)

		vsz.Add(hsz, 0, wx.ALIGN_CENTER_HORIZONTAL)

		vsz.AddSpacer(10)

		self.msg = wx.StaticText(self, wx.ID_ANY, "                                      ")
		self.msg.SetFont(self.font)
			
		vsz.Add(self.msg)
		
		vsz.AddSpacer(20)

		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.AddSpacer(20)
		hsz.Add(vsz)
		hsz.AddSpacer(20)

		self.SetSizer(hsz)
		self.Layout()
		self.Fit()
		self.CenterOnScreen()

	def OnBRoute(self, _):
		if self.lastStepx is None:
			return
		
		if self.lastStepx >= len(self.sequence):
			if self.trinfo["startblock"] == self.sequence[-1]["block"]:
				self.ClearArrow(self.lastStepx)
				self.lastStepx = 0
				self.SetArrow(self.lastStepx)
				
		if self.lastStepx >= len(self.sequence):
			return

		sx = self.lastStepx
		if self.sequence[sx]["os"] is None or self.sequence[sx]["os"] == "":
			return

		rc, alreadyset, msg = self.parent.SetRouteThruOS(self.sequence[sx]["os"], self.sequence[sx]["route"], self.sequence[sx]["block"], self.sequence[sx]["signal"])
		logging.debug("back from setroute: %s %s %s" % (rc, alreadyset, msg))
		
		if not rc or (rc and msg is not None):
			self.parent.PopupAdvice(msg)
		#
		# if rc:
		# 	if alreadyset:
		# 		self.parent.SetRouteSignal(self.sequence[sx]["os"], self.sequence[sx]["route"], "", self.sequence[sx]["signal"])
		# 	else:
		# 		self.parent.DelaySignalRequest(self.sequence[sx]["signal"], self.sequence[sx]["os"], self.sequence[sx]["route"], 5)

	def OnBSignal(self, _):
		if self.lastStepx is None:
			return

		sx = self.lastStepx				
		if self.sequence[sx]["signal"] is None or self.sequence[sx]["signal"] == "":
			return

		rc, msg = self.parent.SetRouteSignal(self.sequence[sx]["os"], self.sequence[sx]["route"], self.sequence[sx]["block"], self.sequence[sx]["signal"])
		
		if not rc or (rc and msg is not None):
			self.parent.PopupEvent(msg)

	def OnBHiLite(self, _):
		if self.hilited:
			self.parent.ClearHighlitedRoute(self.trainName)
			self.hilited = False
			self.bHilite.SetLabel(HILITEON)
		else:
			routeTiles = self.parent.EnumerateBlockTiles(self.startingBlock)
			for step in self.sequence:
				routeTiles.extend(self.parent.EnumerateOSTiles(step["os"], step["route"]))
				routeTiles.extend(self.parent.EnumerateBlockTiles(step["block"]))

			self.hilited = True
			self.bHilite.SetLabel(HILITEOFF)
			self.parent.SetHighlitedRoute(self.trainName, routeTiles)

	def ClearHiliteFlag(self):
		self.hilited = False
		self.bHilite.SetLabel(HILITEON)

	def OnBRefresh(self, _):
		self.DetermineTrainPosition()
		
	def UpdateTrainStatus(self):
		self.DetermineTrainPosition()
		
	def DetermineTrainPosition(self):
		fbn = self.train.FrontBlock()
		if fbn.endswith(".E") or fbn.endswith(".W"):
			fbn = fbn[:-2]
		fb = self.blocks.get(fbn, None)

		if fb is None:
			self.ClearArrow(self.lastStepx)
			self.msg.SetLabel("Train is in an unknown block: %s" % fbn)
			return

		fbn = fb.GetRouteDesignator()
		try:
			stepx = self.goodBlocks.index(fbn)+1
		except ValueError:
			try:
				stepx = self.goodOSs.index(fbn)+1
			except ValueError:
				if fbn == self.startingBlock:
					stepx = 0
				else:
					stepx = None

		if self.lastStepx is not None:
			self.ClearArrow(self.lastStepx)

		if stepx is None:
			if fb.GetName() not in YardBlocks:
				self.msg.SetLabel("Train is in unexpected block: %s" % fbn)

			if self.isDispatcher:
				self.bRoute.Enable(False)
				self.bSignal.Enable(False)

		elif stepx == 0:  # train is in starting block
			self.msg.SetLabel("")
			self.SetArrow(stepx)
			if self.isDispatcher:
				self.bRoute.Enable(True)
				self.bSignal.Enable(True)

		else:
			self.msg.SetLabel("")
			self.SetArrow(stepx)
			if self.isDispatcher:
				self.bRoute.Enable(True)
				self.bSignal.Enable(True)

		self.lastStepx = stepx

	def SetArrow(self, sx):
		if sx is None:
			return
		self.bmps[sx].SetBitmap(self.bmpArrow)
		
	def ClearArrow(self, sx):
		if sx is None:
			return
		self.bmps[sx].SetBitmap(self.bmpClear)
		
	def onClose(self, _):
		self.parent.CloseRouteTrainDlg(self.trainName)
		
	def AddHeaders(self):
		sigst = wx.StaticText(self, wx.ID_ANY, "Signal", size=(COLSIG, -1))
		sigst.SetFont(self.font)
			
		rtest = wx.StaticText(self, wx.ID_ANY, "OS(Route)", size=(COLOS, -1))
		rtest.SetFont(self.font)
			
		blkst = wx.StaticText(self, wx.ID_ANY, "Block", size=(COLBLK, -1))
		blkst.SetFont(self.font)
		
		bmp = wx.StaticBitmap(self, wx.ID_ANY, self.bmpClear)
		
		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.Add(bmp)
		hsz.AddSpacer(10)
		hsz.Add(sigst)
		hsz.Add(rtest)
		hsz.Add(blkst)
		
		return hsz
		
	def AddLine(self, signame, osname, rtname, blkname):
		color = self.colors[self.line % 2]
		if signame is None:
			sigst = wx.StaticText(self, wx.ID_ANY, "", size=(COLSIG, -1))
		else:
			sigst = wx.StaticText(self, wx.ID_ANY, signame, size=(COLSIG, -1))
		sigst.SetFont(self.font)
		sigst.SetBackgroundColour(color)

		if osname is None or rtname is None:
			rtest = wx.StaticText(self, wx.ID_ANY, "", size=(COLOS, -1))
		else:
			try:
				rn = rtname.split("Rt")[1]
			except IndexError:
				rn = rtname
			rtest = wx.StaticText(self, wx.ID_ANY, "%s(%s)" % (BlockName(osname), rn), size=(COLOS, -1))
		rtest.SetFont(self.font)
		rtest.SetBackgroundColour(color)
			
		blkst = wx.StaticText(self, wx.ID_ANY, blkname, size=(COLBLK, -1))
		blkst.SetFont(self.font)
		blkst.SetBackgroundColour(color)

		bmp = wx.StaticBitmap(self, wx.ID_ANY, self.bmpClear)
		self.bmps.append(bmp)
		
		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.Add(bmp)
		hsz.AddSpacer(10)
		hsz.Add(sigst)
		hsz.Add(rtest)
		hsz.Add(blkst)

		self.line += 1
		
		return hsz
