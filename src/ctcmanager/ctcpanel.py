import wx

from ctcmanager.siglever import SigLever, LEFT, RIGHT
from ctcmanager.turnoutlever import TurnoutLever


class CTCPanel:
	def __init__(self, frame, name, signals, turnouts, screen, offset, position):
		self.frame = frame
		self.position = [x for x in position]
		self.panelName = name
		self.screen = screen
		self.signals = signals
		self.turnouts = turnouts
		self.sigLeverMap = {}
		self.sigHS = {}
		self.trnLeverMap = {}
		self.trnHS = {}

		self.labelFont = wx.Font(wx.Font(14, wx.FONTFAMILY_ROMAN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, faceName="Arial"))

		hsStart = self.position[0]
		hsWidth = 65
		totalWidthsig = 0
		for sig in self.signals:
			sl = SigLever(frame, sig["label"], sig["name"], screen, [hsStart, position[1]])
			self.sigLeverMap[sig["name"]] = sl
			hs = hsStart+offset
			self.sigHS[sig["name"]] = (hs+3, hs+29, hs+31, hs+57)
			hsStart += hsWidth
			totalWidthsig += hsWidth

		hsStart = self.position[0]

		totalWidthtrn = 0
		for sw in self.turnouts:
			tl = TurnoutLever(frame, sw["label"], sw["name"], screen, [hsStart, position[1]+90])
			self.trnLeverMap[sw["name"]] = tl
			hs = hsStart+offset
			self.trnHS[sw["name"]] = (hs+3, hs+29, hs+31, hs+57)
			hsStart += hsWidth
			totalWidthtrn += hsWidth

		width = totalWidthsig if totalWidthsig > totalWidthtrn else totalWidthtrn
		self.center = int(width/2)

		# print("Maps for %s" %  name)
		# print("Signals:")
		# for s, hs in self.sigHS.items():
		# 	print("   %s: %d-%d  %d-%d" % (s, hs[0], hs[1], hs[2], hs[3]))
		# print("")
		# print("Turnouts:")
		# for t, hs in self.trnHS.items():
		# 	print("   %s: %d-%d  %d-%d" % (t, hs[0], hs[1], hs[2], hs[3]))
		# print("==============================================================", flush=True)

	def GetBitmaps(self):
		for sig in self.signals:
			for bmp in self.sigLeverMap[sig["name"]].GetBitmaps():
				yield bmp
		for sw in self.turnouts:
			for bmp in self.trnLeverMap[sw["name"]].GetBitmaps():
				yield bmp

	def GetLabels(self):
		yield self.panelName, self.labelFont, self.screen, self.position[0]+self.center-(len(self.panelName)*6), self.position[1]-30
		for sig in self.signals:
			yield self.sigLeverMap[sig["name"]].GetLabel()

		for sw in self.turnouts:
			yield self.trnLeverMap[sw["name"]].GetLabel()

	def CheckHotSpots(self, x, y):
		if 550 <= y <= 610:
			for sig in self.signals:
				lxmin, lxmax, rxmin, rxmax = self.sigHS[sig["name"]]
				if lxmin <= x <= lxmax:
					self.sigLeverMap[sig["name"]].LeverClick(LEFT)
					return

				if rxmin <= x <= rxmax:
					self.sigLeverMap[sig["name"]].LeverClick(RIGHT)
					return

		elif 630 <= y <= 690:
			for sw in self.turnouts:
				nxmin, nxmax, rxmin, rxmax = self.trnHS[sw["name"]]
				if nxmin <= x <= nxmax:
					self.trnLeverMap[sw["name"]].LeverClick("N")
					return

				if rxmin <= x <= rxmax:
					self.trnLeverMap[sw["name"]].LeverClick("R")
					return

	def GetSignalLeverMap(self):
		return self.sigLeverMap

	def GetTurnoutLeverMap(self):
		return self.trnLeverMap
