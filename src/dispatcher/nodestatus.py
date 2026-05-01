import wx


class NodeStatusDisplay(wx.StaticText):
	def __init__(self, parent, size=wx.DefaultSize, pos=wx.DefaultPosition):
		wx.StaticText.__init__(self, parent, wx.ID_ANY, "", size=size, pos=pos, style=wx.TE_CENTER)
		self.parent = parent
		self.SetFont(wx.Font(18, wx.FONTFAMILY_ROMAN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, faceName="Arial"))
		self.red   = wx.Colour(255, 0, 0)
		self.green = wx.Colour(0, 160, 24)
		self.black = wx.Colour(100, 100, 100)
		self.SetBackgroundColour(self.parent.GetBackgroundColour())
		self.SetForegroundColour(self.red)

		self.currentPosition = None
		self.interval = None
		self.disabledNodes = {}
		self.keyList = []
		self.UpdateDisplay()

	def UpdateNodeStatus(self, name, addr, status):
		if status == 0:  # node is disabled
			if name not in self.disabledNodes.keys():
				self.disabledNodes[name] = addr

		else:
			try:
				del self.disabledNodes[name]
			except KeyError:
				pass

		self.keyList = sorted(self.disabledNodes.keys())
		self.UpdateDisplay()

	def UpdateDisplay(self):
		if len(self.keyList) == 0:
			self.SetLabel("")
			self.currentPosition = None
			self.interval = None
		else:
			if self.currentPosition is None:
				self.currentPosition = 0
			else:
				self.currentPosition += 1
				if self.currentPosition >= len(self.keyList):
					self.currentPosition = 0
			self.showNodeStatus()

	def showNodeStatus(self):
		name = self.keyList[self.currentPosition]
		try:
			addr = self.disabledNodes[name]
		except IndexError:
			return

		text = "Node"
		if len(self.keyList) > 1:
			text += "s"

		text += " Disabled: %s(0x%x)" % (name, addr)

		if len(self.keyList) > 1:
			text += " (%s/%s)" % (self.currentPosition+1, len(self.keyList))

		self.SetLabel(text)
		self.interval = 2

	def ticker(self):
		if self.interval is None:
			return

		self.interval -= 1
		if self.interval <= 0:
			self.UpdateDisplay()
