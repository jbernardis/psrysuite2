import wx

breakerNames = {
	"CBCliveden":       "Cliveden",
	"CBLatham":         "Latham",
	"CBCornellJct":     "Cornell Junction",
	"CBParsonsJct":     "Parson's Junction",
	"CBSouthJct":       "South Junction",
	"CBCircusJct":      "Circus Junction",
	"CBSouthport":      "Southport",
	"CBLavinYard":      "Lavin Yard",
	"CBReverserP31":    "Reverser P31",
	"CBReverserP41":    "Reverser P41",
	"CBReverserP50":    "Reverser P50",
	"CBReverserC22C23": "Reverser C22/C23",
	"CBKrulish":		"Krulish",
	"CBKrulishYd":		"Krulish Yard",
	"CBNassauW":		"Nassau West",
	"CBNassauE":		"Nassau East",
	"CBWilson":			"Wilson City",
	"CBThomas":			"Thomas Yard",
	"CBFoss":			"Foss",
	"CBDell":			"Dell",
	"CBKale":			"Kale",
	"CBWaterman":		"Waterman Yard",
	"CBEngineYard":		"Engine Yard",
	"CBEastEndJct":		"East End Junction",
	"CBShore":			"Shore",
	"CBRockyHill":		"Rocky Hill",
	"CBHarpersFerry":	"Harpers Ferry",
	"CBBlockY30":		"Block Y30",
	"CBBlockY81":		"Block Y81",
	"CBGreenMtn":		"Green Mountain",
	"CBSheffield":		"Sheffield",
	"CBBank":			"Bank",
	"CBHydeJct":		"Hyde Junction",
	"CBHydeWest":		"Hyde West",
	"CBHydeEast":		"Hyde East",
	"CBSouthportJct":	"Southport Junction",
	"CBCarlton":		"Carlton",
}


def BreakerName(iname):
	try:
		text = breakerNames[iname]
	except KeyError:
		text = iname

	return text


class BreakerDisplay(wx.TextCtrl):
	def __init__(self, parent, size=wx.DefaultSize, pos=wx.DefaultPosition):
		wx.TextCtrl.__init__(self, parent, wx.ID_ANY, "", size=size, pos=pos, style=wx.TE_CENTER)
		self.parent = parent
		self.SetFont(wx.Font(22, wx.FONTFAMILY_ROMAN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, faceName="Arial"))
		self.SetForegroundColour(wx.Colour(255, 255, 255))
		self.red   = wx.Colour(255, 0, 0)
		self.green = wx.Colour(0, 160, 24)
		self.black = wx.Colour(100, 100, 100)

		self.breakers = []
		self.currentPosition = None
		self.interval = None
		self.UpdateDisplay()

	def UpdateDisplay(self):
		if not self.parent.subscribed:
			self.SetBackgroundColour(self.black)
			self.SetValue("Not Connected")
			self.currentPosition = None
			self.interval = None
			return

		if len(self.breakers) == 0:
			self.SetBackgroundColour(self.green)
			self.SetValue("All Clear")
			self.currentPosition = None
			self.interval = None
		else:
			if self.currentPosition is None:
				self.currentPosition = 0
			else:
				self.currentPosition += 1
				if self.currentPosition >= len(self.breakers):
					self.currentPosition = 0
			self.showBreaker()

	def showBreaker(self):
		try:
			brkr = self.breakers[self.currentPosition]
		except IndexError:
			return

		text = BreakerName(brkr)

		if len(self.breakers) > 1:
			text += " (%s/%s)" % (self.currentPosition+1, len(self.breakers))
		self.SetValue(text)
		self.interval = 3

	def AddBreaker(self, brkr):
		if brkr in self.breakers:
			return

		if len(self.breakers) == 0:
			self.SetBackgroundColour(self.red)

		self.breakers.append(brkr)
		self.currentPosition = len(self.breakers)-1
		self.showBreaker()

	def DelBreaker(self, brkr):
		if brkr not in self.breakers:
			return

		ix = self.breakers.index(brkr)

		del self.breakers[ix]
		if ix == self.currentPosition or len(self.breakers) == 0:
			self.UpdateDisplay()
		else:
			self.showBreaker()

	def ticker(self):
		if self.interval is None:
			return

		self.interval -= 1
		if self.interval <= 0:
			self.UpdateDisplay()
