import wx
import os

SWNORMAL= "SwNormal"
SWREVERSE = "SwReverse"
SWNEUTRAL = "SwNeutral"
SWNORMALDISABLED = "SwNormalDis"
SWREVERSEDISABLED = "SwReverseDis"
SWNEUTRALDISABLED = "SwNeutralDis"
LAMPOFF = "LampOff"
LAMPRED = "LampRed"
LAMPGREEN = "LampGreen"


class TurnoutLever:
	images = None

	def __init__(self, frame, label, name, screen, pos):
		self.frame = frame
		self.label = label
		self.name = name
		self.screen = screen
		self.pos = [x for x in pos]
		self.buffer = None

		if TurnoutLever.images is None:
			TurnoutLever.loadBitmaps()

		self.bmpN = TurnoutLever.images[LAMPGREEN]
		self.bmpR = TurnoutLever.images[LAMPOFF]
		self.bmpPlate = TurnoutLever.images[SWNEUTRAL]

		self.enabled = True

		self.state = "N"
		self.requestedState = None

		if len(self.label) == 1:
			ox = 26
		elif len(self.label) == 2:
			ox = 23
		else:
			ox = 20
		self.labelx = self.pos[0]+ox
		self.labely = self.pos[1]+19
		self.labelFont = wx.Font(wx.Font(10, wx.FONTFAMILY_ROMAN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, faceName="Arial"))

	def Refresh(self):
		self.frame.UpdateCTCBitmaps(self.GetBitmaps())

	def Enable(self, flag=True):
		self.enabled = flag
		self.bmpPlate = TurnoutLever.images[SWNEUTRAL] if self.enabled else TurnoutLever.images[SWNEUTRALDISABLED]
		if self.state == "N":
			self.bmpN = TurnoutLever.images[LAMPGREEN]
			self.bmpR = TurnoutLever.images[LAMPOFF]
		elif self.state == "R":
			self.bmpN = TurnoutLever.images[LAMPOFF]
			self.bmpR = TurnoutLever.images[LAMPRED]
		else:
			self.bmpN = TurnoutLever.images[LAMPOFF]
			self.bmpR = TurnoutLever.images[LAMPOFF]

		self.Refresh()

	def SetTurnoutState(self, state):
		self.requestedState = None

		if state == "N":
			self.bmpR = TurnoutLever.images[LAMPOFF]
			self.bmpN = TurnoutLever.images[LAMPGREEN]
			self.bmpPlate = TurnoutLever.images[SWNEUTRAL] if self.enabled else TurnoutLever.images[SWNEUTRALDISABLED]
			self.state = "N"

		elif state == "R":
			self.bmpR = TurnoutLever.images[LAMPRED]
			self.bmpN = TurnoutLever.images[LAMPOFF]
			self.bmpPlate = TurnoutLever.images[SWNEUTRAL] if self.enabled else TurnoutLever.images[
				SWNEUTRALDISABLED]
			self.state = "R"

		self.Refresh()

	def GetBitmaps(self):
		return [
			[self.screen, True, (self.pos[0], self.pos[1]+17), self.bmpPlate],
			[self.screen, False, (self.pos[0], self.pos[1]), self.bmpN],
			[self.screen, False, (self.pos[0]+40, self.pos[1]), self.bmpR]
		]

	def GetLabel(self):
		return self.label, self.labelFont, self.screen, self.labelx, self.labely

	@classmethod
	def loadBitmaps(self):
		TurnoutLever.images = {}
		for f in [ SWNEUTRAL, SWNORMAL, SWREVERSE,
				   SWNEUTRALDISABLED, SWNORMALDISABLED, SWREVERSEDISABLED,
				   LAMPOFF, LAMPGREEN, LAMPRED ]:
			fp = os.path.join("images", "bitmaps", "CTC", f + ".png")
			png = wx.Image(fp, wx.BITMAP_TYPE_PNG).ConvertToBitmap()
			mask = wx.Mask(png, wx.BLUE)
			png.SetMask(mask)
			TurnoutLever.images[f] = png

	def LeverClick(self, direction):
		if not self.enabled:
			return False

		if self.requestedState is not None:
			return False

		revt = None
		if direction == "N":
			if self.state == "R":
				self.frame.Request(
					{'turnoutlever': {'name': self.name, 'state': direction, 'force': 0, 'source': 'ctc'}})
				self.bmpPlate = TurnoutLever.images[SWNORMAL] if self.enabled else TurnoutLever.images[SWNORMALDISABLED]
				self.requestedState = "N"
			else:
				return False
		else:
			if self.state == "N":
				self.frame.Request(
					{'turnoutlever': {'name': self.name, 'state': direction, 'force': 0, 'source': 'ctc'}})
				self.bmpPlate = TurnoutLever.images[SWREVERSE] if self.enabled else TurnoutLever.images[SWREVERSEDISABLED]
				self.requestedState = "R"
			else:
				return False

		self.Refresh()
		self.frame.CheckCTCCompleted(3000, self.checkIfCompleted)
		return True

	def checkIfCompleted(self):
		if self.requestedState is None:
			return

		self.bmpPlate = self.images[SWNEUTRAL]
		self.requestedState = None
		self.Refresh()
