import json
import re
import os
import logging

from ctcmanager.ctcpanel import CTCPanel


class CTCManager:
	def __init__(self, frame, settings, diagrams):
		self.settings = settings
		self.frame = frame
		self.visible = False

		try:
			with open(os.path.join(os.getcwd(), "data", "ctc.json"), "r") as jfp:
				self.ctcdata = json.load(jfp)
		except FileNotFoundError:
			logging.error("unable to open CTC panel data file ctc.json")
			exit(1)

		self.ctcPanels = {}
		self.sigLeverMap = {}
		self.turnoutLeverMap = {}

		for pname in self.ctcdata["order"]:
			screen = self.ctcdata[pname]["screen"]
			offset = diagrams[screen].offset
			ctc = CTCPanel(frame, pname, self.ctcdata[pname]["signals"], self.ctcdata[pname]["turnouts"], screen, offset, self.ctcdata[pname]["position"])
			self.sigLeverMap.update(ctc.GetSignalLeverMap())
			self.turnoutLeverMap.update(ctc.GetTurnoutLeverMap())
			self.ctcPanels[pname] = ctc

	def SetVisible(self, flag):
		self.visible = flag

	def GetBitmaps(self):
		for ctc in self.ctcPanels.values():
			for bmp in ctc.GetBitmaps():
				yield bmp

	def GetLabels(self):
		for ctc in self.ctcPanels.values():
			for lbl in ctc.GetLabels():
				yield lbl

	def CheckHotSpots(self, scrName, x, y):
		if not self.visible:
			return
		for cn in self.ctcdata["order"]:
			if scrName is None or scrName == self.ctcdata[cn]["screen"]:
				self.ctcPanels[cn].CheckHotSpots(x, y)

	def DoCmdSignal(self, parms):
		for p in parms:
			signm = p["signal"]
			aspect = int(p["aspect"])
			z = re.match("([A-Za-z]+)([0-9]+)([A-Z])", signm)
			if z is None or len(z.groups()) != 3:
				logging.info("Unable to determine lever name from signal name %s" % signm)
				return

			nm, nbr, lr = z.groups()
			lvrID = "%s%d.lvr" % (nm, int(nbr))
			try:
				self.sigLeverMap[lvrID].SetSignalAspect(aspect, lr)
			except KeyError:
				pass

	def DoCmdTurnout(self, parms):
		for p in parms:
			tonm = p["name"]
			state = p["state"]
			try:
				tl = self.turnoutLeverMap[tonm]
			except KeyError:
				tl = None

			if tl:
				tl.SetTurnoutState(state)

	def DoCmdTurnoutLock(self, parms):
		for p in parms:
			tonm = p["name"]
			try:
				state = int(p["state"])
			except (KeyError, ValueError):
				state = 0

			try:
				tl = self.turnoutLeverMap[tonm]
			except KeyError:
				tl = None

			if tl:
				tl.Enable(state == 0)