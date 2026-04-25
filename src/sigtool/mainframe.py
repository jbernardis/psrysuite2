import os
import wx

from sigtool.signals import Signals
from sigtool.railroadserver import RRServer
from dispatcher.constants import aspectname, aspecttype
from rrserver.constants import nodeNames

aspectValues = {
	1: [[0], [1]],
	2: [[0, 0], [0, 1], [1, 0], [1, 1]],
	3: [[0, 0, 0], [0, 0, 1], [0, 1, 0], [0, 1, 1], [1, 0, 0], [1, 0, 1], [1, 1, 0], [1, 1, 1]],
}


class MainFrame(wx.Frame):
	def __init__(self, settings):
		wx.Frame.__init__(self, None, style=wx.DEFAULT_FRAME_STYLE, size=(410, 330))
		self.SetTitle("PSRY Signal Testing Tool")
		self.Bind(wx.EVT_CLOSE, self.OnClose)

		self.settings = settings

		self.aspectType = None
		self.nodeAddr = None
		self.bits = []
		self.chosenBits = 0
		self.chosenAspect = 0

		self.signals = Signals()

		self.rrServer = RRServer()
		self.rrServer.SetServerAddress(self.settings.ipaddr, self.settings.serverport)

		stSignal = wx.StaticText(self, wx.ID_ANY, "Signal:", pos=wx.Point(20, 24))

		self.sigList = self.signals.SigNames()
		self.chSigName = wx.Choice(self, wx.ID_ANY, choices=self.sigList, pos=wx.Point(70, 20))
		self.Bind(wx.EVT_CHOICE, self.OnSignalChoice, self.chSigName)
		self.chSigName.SetSelection(0)
		self.selectedSignal = self.sigList[0]

		self.selectedSignal = self.sigList[0]

		self.stType = wx.StaticText(self, wx.ID_ANY, "", pos=wx.Point(20, 60))

		self.stBits = wx.StaticText(self, wx.ID_ANY, "", pos=wx.Point(20, 90))

		self.stNode = wx.StaticText(self, wx.ID_ANY, "", pos=wx.Point(20, 120))

		self.aspectType = self.signals.GetAspectType(self.selectedSignal)
		vals = self.signals.GetAspectBits(self.selectedSignal)
		bits = vals[0]
		addr = vals[1]

		choices = []
		for az in range(2):
			choices.append(self.AspectString(az, 1)+"   ")
		self.rg1bit = wx.RadioBox(self, wx.ID_ANY, choices=choices, majorDimension=0, style=wx.RA_SPECIFY_ROWS,
								pos=wx.Point(200, 20), size=wx.Size(170, 198))
		self.rg1bit.Show(len(bits) == 1)
		self.Bind(wx.EVT_RADIOBOX, self.OnAspect1, self.rg1bit)

		choices = []
		for az in range(4):
			choices.append(self.AspectString(az, 2)+"   ")
		self.rg2bit = wx.RadioBox(self, wx.ID_ANY, choices=choices, majorDimension=0, style=wx.RA_SPECIFY_ROWS,
								pos=wx.Point(200, 20), size=wx.Size(170, 198))
		self.rg2bit.Show(len(bits) == 2)
		self.Bind(wx.EVT_RADIOBOX, self.OnAspect2, self.rg2bit)

		choices = []
		for az in range(8):
			choices.append(self.AspectString(az, 3)+"   ")
		self.rg3bit = wx.RadioBox(self, wx.ID_ANY, choices=choices, majorDimension=0, style=wx.RA_SPECIFY_ROWS,
								pos=wx.Point(200, 20), size=wx.Size(170, 198))
		self.rg3bit.Show(len(bits) == 3)
		self.Bind(wx.EVT_RADIOBOX, self.OnAspect3, self.rg3bit)

		self.bSend = wx.Button(self, wx.ID_ANY, "Send")
		width = self.GetSize()[0]
		bwidth = self.bSend.GetSize()[0]
		bcenter = int(width/2 - bwidth/2)
		self.bSend.SetPosition(wx.Point(bcenter, 250))
		self.Bind(wx.EVT_BUTTON, self.OnBSend, self.bSend)

		self.PopulateFields()

	def AspectString(self, aspect, nbits):
		an = aspectname(aspect, self.aspectType)

		try:
			av = aspectValues[nbits][aspect]
		except (KeyError, IndexError):
			self.Message("Index/Key error trying to retrieve aspect value for %s %s" % (nbits, aspect))
			return an

		pfx = "".join(["%d" % b for b in av])
		return pfx + " " + an

	def OnSignalChoice(self, _):
		chx = self.chSigName.GetSelection()
		self.selectedSignal = None if chx == wx.NOT_FOUND else self.chSigName.GetString(chx)
		self.PopulateFields()

	def OnAspect1(self, _):
		ax = self.rg1bit.GetSelection()
		self.SetChosenAspect(1, ax)

	def OnAspect2(self, _):
		ax = self.rg2bit.GetSelection()
		self.SetChosenAspect(2, ax)

	def OnAspect3(self, _):
		ax = self.rg3bit.GetSelection()
		self.SetChosenAspect(3, ax)

	def SetChosenAspect(self, bits, aspect):
		self.chosenBits = bits
		self.chosenAspect = aspect

	def PopulateFields(self):
		if self.selectedSignal is None:
			self.aspectType = None
			self.nodeAddr = None
			self.bits = []

			self.stType.SetLabel("")
			self.stBits.SetLabel("")
			self.stNode.SetLabel("")
			self.rg1bit.Enable(False)
			self.rg2bit.Enable(False)
			self.rg3bit.Enable(False)
		else:
			self.aspectType = self.signals.GetAspectType(self.selectedSignal)
			atName = aspecttype(self.aspectType)
			self.stType.SetLabel("Aspect Type: %s" % atName)

			vals = self.signals.GetAspectBits(self.selectedSignal)
			self.bits = vals[0]
			self.nodeAddr = vals[1]
			bstr = ["(%d, %d)" % (b[0], b[1]) for b in self.bits]
			self.stBits.SetLabel("Bits: %s" % ", ".join(bstr))
			self.stNode.SetLabel("Node: %s (0x%x)" % (nodeNames[self.nodeAddr], self.nodeAddr))

			for az in range(2):
				self.rg1bit.SetItemLabel(az, self.AspectString(az, 1))
			if len(self.bits) == 1:
				self.rg1bit.Show(True)
				self.SetChosenAspect(1, self.rg1bit.GetSelection())
			else:
				self.rg1bit.Show(False)

			for az in range(4):
				self.rg2bit.SetItemLabel(az, self.AspectString(az, 2))
			if len(self.bits) == 2:
				self.rg2bit.Show(True)
				self.SetChosenAspect(2, self.rg2bit.GetSelection())
			else:
				self.rg2bit.Show(False)

			for az in range(8):
				self.rg3bit.SetItemLabel(az, self.AspectString(az, 3))
			if len(self.bits) == 3:
				self.rg3bit.Show(True)
				self.SetChosenAspect(3, self.rg3bit.GetSelection())
			else:
				self.rg3bit.Show(False)

	def OnBSend(self, _):
		if self.selectedSignal is None or self.chosenBits is None or self.chosenAspect is None:
			self.Message("Please choose a signal first")
			return

		vbytes = [b[0] for b in self.bits]
		vbits = [b[1] for b in self.bits]
		addr = self.nodeAddr
		nbits = len(vbytes)
		try:
			vals = aspectValues[nbits][self.chosenAspect]
		except (KeyError, IndexError):
			self.Message("can't decode aspect value: %s %s:%s" % (self.selectedSignal, nbits, self.chosenAspect))
			return

		msg = {"setoutbit": {"address": "0x%x" % addr, "byte": vbytes, "bit": vbits, "value": vals}}
		if not self.rrServer.Request(msg):
			self.Message("Unable to send request.  Is RRServer running?")

	def Message(self, txt):
		dlg = wx.MessageDialog(self, txt, "Alert", wx.OK | wx.ICON_WARNING)
		dlg.ShowModal()
		dlg.Destroy()

	def OnBExit(self, _):
		self.doExit()
		
	def OnClose(self, _):
		self.doExit()
		
	def doExit(self):
		self.Destroy()
		
