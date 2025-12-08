import logging

from rrserver.district import District
from rrserver.constants import BANK, CLIFF
from rrserver.node import Node


class Bank(District):
	def __init__(self, rr, name, settings):
		District.__init__(self, rr, name, settings)
		self.rr = rr
		self.name = name
		self.cliffNode = None
		self.released = False
		self.nodeAddresses = [ BANK ]
		self.nodes = {
			BANK:  Node(self, rr, BANK,  4, settings)
		}

		addr = BANK
		with self.nodes[addr] as n:
			# outputs
			self.rr.AddSignal("C22L",  self, n, addr, [(0, 0)])
			self.rr.AddSignal("C24L",  self, n, addr, [(0, 1), (0, 2), (0, 3)])
			self.rr.AddSignal("C24R",  self, n, addr, [(0, 4), (0, 5), (0, 6)])
			self.rr.AddSignal("C22R",  self, n, addr, [(0, 7), (1, 0), (1, 1)])
			self.rr.AddSignal("C18LA", self, n, addr, [(1, 2)])
			self.rr.AddSignal("C18LB", self, n, addr, [(1, 3), (1, 4), (1, 5)])
			self.rr.AddSignal("C18R",  self, n, addr, [(1, 6), (1, 7), (2, 0)])

			self.rr.AddBlockInd("B10", self, n, addr, [(2, 1)])
			self.rr.AddBlockInd("C13", self, n, addr, [(2, 2)])

			self.rr.AddHandswitchInd("CSw21ab", self, n, addr, [(2, 3)], inverted=True)
			self.rr.AddHandswitchInd("CSw19",   self, n, addr, [(2, 4)], inverted=True)

			self.rr.AddTurnout("CSw23", self, n, addr, [(2, 5), (2, 6)])
			self.rr.AddTurnoutPair("CSw23", "CSw23b")
			self.rr.AddTurnout("CSw17", self, n, addr, [(2, 7), (3, 0)])

			self.rr.AddStopRelay("B20.srel", self, n, addr, [(3, 1)])
			self.rr.AddStopRelay("B11.srel", self, n, addr, [(3, 2)])
			self.rr.AddStopRelay("B21.srel", self, n, addr, [(3, 3)])

			self.rr.AddBreakerInd("CBBank", self, n, addr, [(3, 4)])
			
			self.rr.AddSignalInd("C24L", self, n, addr, [(3, 5)])
			
			#inputs
			self.rr.AddTurnoutPosition("CSw23",  self, n, addr, [(0, 0), (0, 1)])
			self.rr.AddHandswitch("CSw21a", self, n, addr, [(0, 2), (0, 3)], "B11")
			self.rr.AddHandswitch("CSw21b", self, n, addr, [(0, 4), (0, 5)], "B11")
			self.rr.AddHandswitch("CSw19",  self, n, addr, [(0, 6), (0, 7)], "B21")
			self.rr.AddTurnoutPosition("CSw17",  self, n, addr, [(1, 0), (1, 1)])
				
			b = self.rr.AddBlock("B20",   self, n, addr, [(1, 2)], True)
			sbe = self.rr.AddBlock("B20.E", self, n, addr, [(1, 3)], True)
			b.AddStoppingBlocks([sbe])

			self.rr.AddBlock("BOSWW", self, n, addr, [(1, 4)], False)
			self.rr.AddBlock("BOSWE", self, n, addr, [(1, 5)], True)

			sbw = self.rr.AddBlock("B11.W", self, n, addr, [(1, 6)], False)
			b = self.rr.AddBlock("B11",   self, n, addr, [(1, 7)], False)
			b.AddStoppingBlocks([sbw])

			sbw = self.rr.AddBlock("B21.W", self, n, addr, [(2, 0)], True)
			b = self.rr.AddBlock("B21",   self, n, addr, [(2, 1)], True)
			sbe = self.rr.AddBlock("B21.E", self, n, addr, [(2, 2)], True)
			b.AddStoppingBlocks([sbe, sbw])

			self.rr.AddBlock("BOSE",  self, n, addr, [(2, 3)], True)

			self.rr.AddBreaker("CBBank",         self, n, addr, [(2, 4)])
			self.rr.AddBreaker("CBKale",         self, n, addr, [(2, 5)])
			self.rr.AddBreaker("CBWaterman",     self, n, addr, [(2, 6)])
			self.rr.AddBreaker("CBEngineYard",   self, n, addr, [(2, 7)])
			self.rr.AddBreaker("CBEastEndJct",   self, n, addr, [(3, 0)])
			self.rr.AddBreaker("CBShore",        self, n, addr, [(3, 1)])		
			self.rr.AddBreaker("CBRockyHill",    self, n, addr, [(3, 2)])
			self.rr.AddBreaker("CBHarpersFerry", self, n, addr, [(3, 3)])
			self.rr.AddBreaker("CBBlockY30",     self, n, addr, [(3, 4)])
			self.rr.AddBreaker("CBBlockY81",     self, n, addr, [(3, 5)])

	def SetHandswitch(self, hsname, state):
		if hsname in ["CSw21a", "CSw21b"]:
			hsa = self.rr.GetHandswitch("CSw21a")
			hsb = self.rr.GetHandswitch("CSw21b")
			if hsname == "CSw21a":
				locked = hsa.IsLocked()
				hsb.Unlock(not locked)
				self.rr.RailroadEvent(hsb.GetEventMessage(lock=True))
			else:
				locked = hsb.IsLocked()
				hsa.Unlock(not locked)
				self.rr.RailroadEvent(hsa.GetEventMessage(lock=True))
			
			hs = self.rr.GetHandswitch("CSw21ab")
			if hs.Unlock(not locked):
				hs.UpdateIndicators()

	def Locale(self):
		return "cliff"

	def BlockOccupancyChange(self, rr, obj, val):
		bname = obj.Name()
		if bname in ["B20", "B21"]:
			self.rr.CheckBlockSignalsAdv("B20", "B21", "B20E", True)

	def SetNodeReference(self, addr, node):
		# the bank node needs information from the cliff panel - the release bit
		if addr == CLIFF:
			self.cliffNode = node

	def OutIn(self):
		rlReq = self.cliffNode.GetInputBit(6, 3)

		ossLocks = self.rr.GetControlOption("osslocks") == 1

		# release controls if requested by operator or if osslocks are turned off by dispatcher
		self.released = rlReq or not ossLocks

		self.rr.UpdateDistrictTurnoutLocks(self.name, self.released)

		District.OutIn(self)
