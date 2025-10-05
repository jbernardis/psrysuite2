
import logging
from rrserver.constants import nodeNames

MAX_ERRORCOUNT = 10

def setBit(obyte, obit, val):
	if val != 0:
		return (obyte | (1 << obit)) & 0xff
	else:
		return (obyte & ~(1 << obit)) & 0xff


def getBit(ibyte, ibit):
	if ibit < 0 or ibit > 7:
		# bit index is out of range
		return 0
	mask = 1 << (7-ibit)
	b = int(bytes([ibyte]).hex(), 16)
	return 1 if b & mask != 0 else 0


class Node:
	def __init__(self, district, rr, address, bcount, settings, incount=None):
		self.district = district
		self.rr = rr
		self.address = address
		self.bcount = bcount
		'''
		We assume there are as many input bytes as there are output bytes, and indeed, we do pulse in the same
		number of bytes.  Some nodes, though, have less bytes with actual data.  Since the subsequent bytes
		might be garbage, we use incount to tell us how many of these input bytes should be processed.  The rest
		are ignored
		'''
		self.incount = bcount if incount is None else incount
		self.outb = [0 for _ in range(bcount)]
		self.inb = [0 for _ in range(bcount)]
		self.lastinb = [0 for _ in range(bcount)]
		self.topulselen = settings.rrserver.topulselen
		self.topulsect = settings.rrserver.topulsect
		self.nxbpulselen = settings.rrserver.nxbpulselen
		self.nxbpulsect = settings.rrserver.nxbpulsect
		self.ioerrorthreshold = settings.rrserver.ioerrorthreshold
		self.first = True
		
		self.errorCount = 0
		self.goodCount = 0
		self.disabled = False
		
		self.inputMap = {}
		
		self.rrBus = None

	def GetAllBits(self):
		return self.bcount, self.outb, self.inb

	def GetInputBit(self, vbyte, vbit):
		return getBit(self.inb[vbyte], vbit)
	
	def AddInputToMap(self, bytebit, o):
		self.inputMap[bytebit] = o

	def GetInputMap(self):
		return self.inputMap
	
	def GetInputBits(self, bits):
		rv = []
		for bt in bits:
			if bt is None:
				rv.append(None)
			else:
				rv.append(getBit(self.inb[bt[0]], bt[1]))
		return rv
	
	def SetInputBit(self, vbyte, vbit, state):
		old = self.inb[vbyte]
		self.inb[vbyte] = setBit(self.inb[vbyte], 7-vbit, state)

	def SetOutputBit(self, vbyte, vbit, state):
		self.outb[vbyte] = setBit(self.outb[vbyte], vbit, state)	   
		
	def setBus(self, bus):
		self.rrBus = bus

	def GetAddress(self):
		return self.Address()

	def Address(self):
		return self.address

	def OutIn(self):
		if self.disabled:
			return 
		
		if self.rrBus is None: 
			return # simulation mode
			
		inb = self.rrBus.sendRecv(self.address, self.outb, self.bcount)
		if inb is not None:
			for i in range(self.bcount):
				self.inb[i] = int.from_bytes(inb[i], "big")
			self.goodCount += 1
			if self.goodCount >= 5:
				self.goodCount = 0
				if self.errorCount > 0:
					self.errorCount -= 1
		else:
			self.errorCount += 1
			self.goodCount = 0
			msg = "Railroad IO error at node %s(0x%2x) (%dx)" % (nodeNames[self.address], self.address, self.errorCount)
			logging.error(msg)
			if self.errorCount >= self.ioerrorthreshold:
				self.rr.RailroadEvent({"alert": { "msg": [msg] }})
				
			if self.errorCount >= MAX_ERRORCOUNT:
				self.disabled = True
				self.rr.RailroadEvent({"nodestatus": {"name":  nodeNames[self.address], "address": self.address, "enabled": 0 } })

	def ReEnable(self):
		msg = "Re-Enabling node %s(0x%2x)" % (nodeNames[self.address], self.address)
		logging.info(msg)
		self.goodCount = 0
		self.errorCount = 0
		self.disabled = False

	def IsEnabled(self):
		return not self.disabled

	def Enable(self, flag=True):
		msg = "Node %s(0x%2x) set enable to %s" % (nodeNames[self.address], self.address, flag)
		logging.debug(msg)
		if self.disabled != flag:
			return

		self.disabled = not flag
		self.rr.RailroadEvent({"nodestatus": {"name": nodeNames[self.address], "address": self.address, "enabled": 1 if flag else 0}})

	def GetChangedInputs(self):
		results = []
		for b in range(self.incount):
			new = self.inb[b]
			old = self.lastinb[b]
			if self.first:
				mask = 0b11111111
			else:
				mask = new ^ old
			if mask != 0:
				for i in range(8):
					if mask & (1 << (7-i)) != 0:
						v = getBit(new, i)
						try:
							o = self.inputMap[(b, i)]
						except KeyError:
							if not self.first:
								logging.warning("input for location %x:%d:%d not found" % (self.address, b, i))
							o = None
						if o:
							results.append([self, b, i, o, v])
						
		self.lastinb = [x for x in self.inb]
		self.first = False
	
		return results

	def __enter__(self):
		return self
	
	def __exit__(self, exc_type, exc_val, exc_tb):
		pass
