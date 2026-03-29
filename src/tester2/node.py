import wx
import os
import json
import logging

from tester2.bus import setBit, getBit
from rrserver.constants import nodeNames

BTNSZ = (100, 40)


class BusException(Exception):
	pass


class Node:
	def __init__(self, bus, addr, nbytes):
		self.bus = bus
		self.addr = addr
		self.nbytes = nbytes
		self.obuf = [0 for _ in range(nbytes)]
		self.ibuf = [0 for _ in range(nbytes)]
		self.lastIBuf = [-1 for _ in range(nbytes)]
		self.lastOBuf = [-1 for _ in range(nbytes)]
		self.grid = None
		self.outRow = 0
		self.inRow = 0
		self.dialog = None
		self.byteDialogs = {}
		self.enabled = True
		self.name = nodeNames[self.addr]

		fn = os.path.join(os.getcwd(), "tester2", "nodes", self.name + ".json")
		self.jdata = None
		try:
			with open(fn, "r") as jfp:
				self.jdata = json.load(jfp)
		except FileNotFoundError:
			dlg = wx.MessageDialog(self, "Unable to open file %s" % fn,
								   "File open error", wx.OK | wx.ICON_EXCLAMATION)
			dlg.ShowModal()
			dlg.Destroy()

		except json.decoder.JSONDecodeError:
			dlg = wx.MessageDialog(self, "Unable to decode JSON file %s" % fn,
								   "JSON parse error", wx.OK | wx.ICON_EXCLAMATION)
			dlg.ShowModal()
			dlg.Destroy()

	def Reset(self):
		self.lastIBuf = [-1 for _ in range(self.nbytes)]
		self.lastOBuf = [-1 for _ in range(self.nbytes)]

	def JsonData(self):
		return self.jdata

	def Enable(self, flag=True):
		self.enabled = flag

	def Dialog(self):
		return self.dialog

	def SetDialog(self, dlg):
		self.dialog = dlg

	def ByteDialog(self, byte):
		return self.byteDialogs.get(byte, None)

	def SetByteDialog(self, dlg, byte):
		self.byteDialogs[byte] = dlg

	def Name(self):
		return self.name

	def Address(self):
		return self.addr

	def NBytes(self):
		return self.nbytes

	def SetGrid(self, grid, outRow, inRow):
		self.grid = grid
		self.outRow = outRow
		self.inRow = inRow

	def getobit(self, byte, bit):
		if byte < 0 or byte >= self.nbytes:
			# invalid byte
			return None

		if bit < 0 or bit > 7:
			# invalid bit
			return None

		ob = self.obuf[byte]
		v = getBit(ob, 7-bit)
		return v

	def getibit(self, byte, bit):
		if byte < 0 or byte >= self.nbytes:
			# invalid byte
			return None

		if bit < 0 or bit > 7:
			# invalid bit
			return None

		ib = self.ibuf[byte]
		v = getBit(ib, 7-bit)
		return v

	def setbit(self, byte, bit, value):
		if byte < 0 or byte >= self.nbytes:
			# invalid byte
			return False

		if bit < 0 or bit > 7:
			# invalid bit
			return False

		ob = self.obuf[byte]
		self.obuf[byte] = setBit(ob, 7-bit, value)
		return True

	def ClearOutputs(self):
		for byx in range(self.nbytes):
			self.ClearOutputByte(byx)

	def ClearOutputByte(self, byx):
		for bix in range(7):
			self.setbit(byx, bix, 0)

	def Render(self, log=False):
		obytes = []
		ibytes = []
		for b in range(self.nbytes):
			if self.lastOBuf[b] != self.obuf[b]:
				self.lastOBuf[b] = self.obuf[b]
				ob = "{:08b}".format(self.obuf[b])[::-1]
				self.grid.SetCellValue(self.outRow, b+1, ob)
				if log:
					obytes.append(ob)
			else:
				if log:
					obytes.append("--------")

			if self.lastIBuf[b] != self.ibuf[b]:
				self.lastIBuf[b] = self.ibuf[b]
				ib = "{:08b}".format(self.ibuf[b])
				self.grid.SetCellValue(self.inRow, b+1, ib)
				if log:
					ibytes.append(ib)
			else:
				if log:
					ibytes.append("--------")

		if log:
			logging.info("%s(%x):" % (self.Name(), self.Address()))
			logging.info("  Out: %s" % " ".join(obytes))
			logging.info("   In: %s" % " ".join(ibytes))

	def OutIn(self, logFlag):
		if not self.enabled:
			return

		changes = self.obuf != self.lastOBuf
		inb = self.bus.sendRecv(self.addr, self.obuf, self.nbytes)

		if inb is None:
			raise BusException
		else:
			if len(inb) != self.nbytes:
				# error - did not receive the expected number of bytes - ignore this message
				raise BusException
			else:
				self.ibuf = [b[0] for b in inb]  # convert byte to integer through subscripting
				if self.ibuf != self.lastIBuf:
					changes = True

		if changes or True:
			self.Render(log=logFlag)


class NodeDlg(wx.Dialog):
	def __init__(self, parent, nd):
		wx.Dialog.__init__(self, parent, wx.ID_ANY, "Details for node %s" % nd.Name())
		self.parent = parent
		self.node = nd
		self.jdata = self.node.JsonData()
		self.Bind(wx.EVT_CLOSE, self.onClose)

		headingFont = wx.Font(16, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
		labelFont = wx.Font(12, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)

		vsizer = wx.BoxSizer(wx.VERTICAL)
		vsizer.AddSpacer(20)

		self.ocbMap = {}

		outSizer = wx.BoxSizer(wx.HORIZONTAL)

		for byx in range(self.node.NBytes()):
			outBSizer = wx.BoxSizer(wx.VERTICAL)
			st = wx.StaticText(self, wx.ID_ANY, "Byte %d" % byx, size=(160, -1))
			st.SetFont(labelFont)
			outBSizer.Add(st)
			for bix in range(8):
				try:
					if self.jdata["obytes"][byx][bix]["used"]:
						st = wx.StaticText(self, wx.ID_ANY, "%s" % self.jdata["obytes"][byx][bix]["label"])
						cb = wx.CheckBox(self, wx.ID_ANY, "")
						v = nd.getobit(byx, bix)
						if v is None:
							v = 0
						cb.SetValue(v != 0)
						self.ocbMap[cb.GetId()] = (byx, bix, cb)
						self.Bind(wx.EVT_CHECKBOX, self.OnOCBClick, cb)
					else:
						st = wx.StaticText(self, wx.ID_ANY, "- %s" % self.jdata["obytes"][byx][bix]["label"])
						cb = None
				except IndexError:
					st = wx.StaticText(self, wx.ID_ANY, "-")
					cb = None

				hz = wx.BoxSizer(wx.HORIZONTAL)
				hz.AddSpacer(20)
				if cb is not None:
					hz.Add(cb)
				hz.Add(st)
				outBSizer.Add(hz)
			outSizer.Add(outBSizer)

		self.icbMap = {}

		inSizer = wx.BoxSizer(wx.HORIZONTAL)

		for byx in range(self.node.NBytes()):
			inBSizer = wx.BoxSizer(wx.VERTICAL)
			st = wx.StaticText(self, wx.ID_ANY, "Byte %d" % byx, size=(160, -1))
			st.SetFont(labelFont)
			inBSizer.Add(st)
			for bix in range(8):
				try:
					if self.jdata["ibytes"][byx][bix]["used"]:
						st = wx.StaticText(self, wx.ID_ANY, "%s" % self.jdata["ibytes"][byx][bix]["label"])
						cb = wx.CheckBox(self, wx.ID_ANY, "")
						cb.Enable(False)
						v = nd.getibit(byx, bix)
						if v is None:
							v = 0
						cb.SetValue(v != 0)
						self.icbMap[cb.GetId()] = (byx, bix, cb)
					else:
						st = wx.StaticText(self, wx.ID_ANY, "- %s" % self.jdata["ibytes"][byx][bix]["label"])
						cb = None
				except IndexError:
					st = wx.StaticText(self, wx.ID_ANY, "-")
					cb = None

				hz = wx.BoxSizer(wx.HORIZONTAL)
				hz.AddSpacer(20)
				if cb is not None:
					hz.Add(cb)
				hz.Add(st)
				inBSizer.Add(hz)
			inSizer.Add(inBSizer)

		st = wx.StaticText(self, wx.ID_ANY, "Node: %s (0x%x)" % (nd.Name(), nd.Address()))
		st.SetFont(headingFont)
		vsizer.Add(st, 0, wx.ALIGN_CENTER_HORIZONTAL)
		vsizer.AddSpacer(10)

		st = wx.StaticText(self, wx.ID_ANY, "Output Bits")
		st.SetFont(headingFont)
		vsizer.Add(st, 0, wx.ALIGN_CENTER_HORIZONTAL)
		vsizer.Add(outSizer)
		vsizer.AddSpacer(20)

		st = wx.StaticText(self, wx.ID_ANY, "Input Bits")
		st.SetFont(headingFont)
		vsizer.Add(st, 0, wx.ALIGN_CENTER_HORIZONTAL)
		vsizer.Add(inSizer)

		vsizer.AddSpacer(20)

		btnsz = wx.BoxSizer(wx.HORIZONTAL)

		self.bClear = wx.Button(self, wx.ID_ANY, "Clear\nOutputs", size=BTNSZ)
		self.Bind(wx.EVT_BUTTON, self.OnBClear, self.bClear)
		btnsz.Add(self.bClear)

		btnsz.AddSpacer(20)

		self.bRefresh = wx.Button(self, wx.ID_ANY, "Refresh", size=BTNSZ)
		self.Bind(wx.EVT_BUTTON, self.OnBRefresh, self.bRefresh)
		btnsz.Add(self.bRefresh)

		vsizer.Add(btnsz, 0, wx.ALIGN_CENTER_HORIZONTAL)

		vsizer.AddSpacer(20)

		hsizer = wx.BoxSizer(wx.HORIZONTAL)
		hsizer.AddSpacer(20)
		hsizer.Add(vsizer)
		hsizer.AddSpacer(20)

		self.SetSizer(hsizer)
		self.Layout()
		self.Fit()

	def OnOCBClick(self, evt):
		byx, bix, cb = self.ocbMap[evt.GetId()]
		self.node.setbit(byx, bix, 1 if cb.IsChecked() else 0)
		self.node.Render()

	def OnBClear(self, _):
		self.node.ClearOutputs()
		self.node.Render()
		for _, _, cb in self.ocbMap.values():
			cb.SetValue(False)

	def OnBRefresh(self, _):
		for byx, bix, cb in self.icbMap.values():
			v = self.node.getibit(byx, bix)
			if v is None:
				v = 0
			cb.SetValue(v != 0)

		for byx, bix, cb in self.ocbMap.values():
			v = self.node.getobit(byx, bix)
			if v is None:
				v = 0
			cb.SetValue(v != 0)

	def onClose(self, _):
		self.node.SetDialog(None)
		self.Destroy()


class NodeByteDlg(wx.Dialog):
	def __init__(self, parent, nd, byx, input):
		wx.Dialog.__init__(self, parent, wx.ID_ANY, "Details for node %s %s byte %d" % (nd.Name(), "Input" if input else "Output", byx))
		self.parent = parent
		self.node = nd
		self.byx = byx
		self.input = input
		jd = self.node.JsonData()
		if input:
			try:
				self.jdata = jd["ibytes"][self.byx]
			except (IndexError, KeyError):
				self.jdata = [{"label": "", "used": False} for _ in range(8)]
			self.byteId = "I%d" % byx
		else:
			try:
				self.jdata = jd["bytes"][self.byx]
			except (IndexError, KeyError):
				self.jdata = [{"label": "", "used": False} for _ in range(8)]
			self.jdata = jd["obytes"][self.byx]
			self.byteId = "O%d" % byx

		self.Bind(wx.EVT_CLOSE, self.onClose)

		headingFont = wx.Font(16, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
		labelFont = wx.Font(12, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)

		self.cbMap = {}

		bSizer = wx.BoxSizer(wx.VERTICAL)

		st = wx.StaticText(self, wx.ID_ANY, "Node: %s (0x%x)" % (nd.Name(), nd.Address()))
		st.SetFont(headingFont)
		bSizer.Add(st, 0, wx.ALIGN_CENTER_HORIZONTAL)
		bSizer.AddSpacer(10)

		st = wx.StaticText(self, wx.ID_ANY, "%s Byte %d" % ("Input" if self.input else "Output", byx))
		st.SetFont(labelFont)
		bSizer.Add(st, 0, wx.ALIGN_CENTER_HORIZONTAL)

		bSizer.AddSpacer(10)

		for bix in range(8):
			try:
				if self.jdata[bix]["used"]:
					st = wx.StaticText(self, wx.ID_ANY, "%s" % self.jdata[bix]["label"])
					cb = wx.CheckBox(self, wx.ID_ANY, "")
					if self.input:
						v = nd.getibit(byx, bix)
					else:
						v = nd.getobit(byx, bix)
					if v is None:
						v = 0
					cb.SetValue(v != 0)
					if self.input:
						cb.Enable(False)
					self.cbMap[cb.GetId()] = (bix, cb)
					self.Bind(wx.EVT_CHECKBOX, self.OnCBClick, cb)
				else:
					st = wx.StaticText(self, wx.ID_ANY, "- %s" % self.jdata[bix]["label"])
					cb = None
			except IndexError:
				st = wx.StaticText(self, wx.ID_ANY, "-")
				cb = None

			hz = wx.BoxSizer(wx.HORIZONTAL)
			hz.AddSpacer(20)
			if cb is not None:
				hz.Add(cb)
			hz.Add(st)
			bSizer.Add(hz)

		bSizer.AddSpacer(20)

		btnsz = wx.BoxSizer(wx.HORIZONTAL)

		if not self.input:
			self.bClear = wx.Button(self, wx.ID_ANY, "Clear\nOutputs", size=BTNSZ)
			self.Bind(wx.EVT_BUTTON, self.OnBClear, self.bClear)
			btnsz.Add(self.bClear)

			btnsz.AddSpacer(20)

		self.bRefresh = wx.Button(self, wx.ID_ANY, "Refresh", size=BTNSZ)
		self.Bind(wx.EVT_BUTTON, self.OnBRefresh, self.bRefresh)
		btnsz.Add(self.bRefresh)

		bSizer.Add(btnsz, 0, wx.ALIGN_CENTER_HORIZONTAL)

		bSizer.AddSpacer(20)

		hsizer = wx.BoxSizer(wx.HORIZONTAL)
		hsizer.AddSpacer(20)
		hsizer.Add(bSizer)
		hsizer.AddSpacer(20)

		self.SetSizer(hsizer)
		self.Layout()
		self.Fit()

	def OnCBClick(self, evt):
		bix, cb = self.cbMap[evt.GetId()]
		self.node.setbit(self.byx, bix, 1 if cb.IsChecked() else 0)
		self.node.Render()

	def OnBClear(self, _):
		self.node.ClearOutputByte(self.byx)
		self.node.Render()
		for _, cb in self.cbMap.values():
			cb.SetValue(False)

	def OnBRefresh(self, _):
		for bix, cb in self.cbMap.values():
			if self.input:
				v = self.node.getibit(self.byx, bix)
			else:
				v = self.node.getobit(self.byx, bix)
			if v is None:
				v = 0
			cb.SetValue(v != 0)

	def onClose(self, _):
		self.node.SetByteDialog(None, self.byteId)
		self.Destroy()

