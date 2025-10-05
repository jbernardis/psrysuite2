import logging

from rrserver.district import District
from rrserver.constants import CLIVEDEN
from rrserver.node import Node

class Cliveden(District):
	def __init__(self, rr, name, settings):
		District.__init__(self, rr, name, settings)
		self.rr = rr
		self.name = name
		self.nodeAddresses = [ CLIVEDEN ]
		self.nodes = {
			CLIVEDEN:  Node(self, rr, CLIVEDEN,  4, settings)
		}

		addr = CLIVEDEN
		with self.nodes[addr] as n:
			#outputs
			self.rr.AddSignal("C14L",  self, n, addr, [(0, 0), (0, 1), (0, 2)])
			self.rr.AddSignal("C14RA", self, n, addr, [(0, 3), (0, 4), (0, 5)])
			self.rr.AddSignal("C14RB", self, n, addr, [(0, 6), (0, 7), (1, 0)])		
			self.rr.AddSignal("C12L",  self, n, addr, [(1, 1), (1, 2), (1, 3)])
			self.rr.AddSignal("C10L",  self, n, addr, [(1, 4), (1, 5), (1, 6)])
			# bit 1:7 unused
			self.rr.AddSignal("C12R",  self, n, addr, [(2, 0), (2, 1), (2, 2)])
			self.rr.AddSignal("C10R",  self, n, addr, [(2, 3), (2, 4), (2, 5)])

			self.rr.AddHandswitchInd("CSw11", self, n, addr, [(2, 6)])
			
			self.rr.AddTurnout("CSw13", self, n, addr, [(2, 7), (3, 0)])
			self.rr.AddTurnout("CSw9",  self, n, addr, [(3, 1), (3, 6)]) # bit 3:2 is bad
			self.rr.AddTurnoutPair("CSw9", "CSw9b")
			
			self.rr.AddStopRelay("C13.srel", self, n, addr, [(3, 3)])
			self.rr.AddStopRelay("C23.srel", self, n, addr, [(3, 4)])
			self.rr.AddStopRelay("C12.srel", self, n, addr, [(3, 5)])
			
			# Inputs
			self.rr.AddTurnoutPosition("CSw13", self, n, addr, [(0, 2), (0, 3)])
			
			self.rr.AddHandswitch("CSw11", self, n, addr, [(0, 4), (0, 5)])
			
			self.rr.AddTurnoutPosition("CSw9",  self, n, addr, [(0, 6), (0, 7)])

			sbw = self.rr.AddBlock("C13.W",   self, n, addr, [(1, 0)], False)
			b = self.rr.AddBlock("C13",     self, n, addr, [(1, 1)], False)
			sbe = self.rr.AddBlock("C13.E",   self, n, addr, [(1, 2)], False)
			b.AddStoppingBlocks([sbe, sbw])
			
			self.rr.AddBlock("COSCLW",  self, n, addr, [(1, 3)], False)
			self.rr.AddBlock("C12.W",   self, n, addr, [(1, 4)], True)
			self.rr.AddBlock("C12",     self, n, addr, [(1, 5)], True)
			self.rr.AddBlock("C23.W",   self, n, addr, [(1, 6)], False)
			self.rr.AddBlock("C23",     self, n, addr, [(1, 7)], False)
			self.rr.AddBlock("COSCLEW", self, n, addr, [(2, 0)], False)
			self.rr.AddBlock("COSCLEE", self, n, addr, [(2, 1)], True)
			self.rr.AddBlock("C22",     self, n, addr, [(2, 2)], False)
			
			b = self.rr.AddBreaker("CBGreenMtnStn",  self, n, addr, [(2, 4)])
			b.SetProxy("CBGreenMtn")
			b = self.rr.AddBreaker("CBSheffieldA",   self, n, addr, [(2, 5)])
			b.SetProxy("CBSheffield")
			b = self.rr.AddBreaker("CBGreenMtnYd",   self, n, addr, [(2, 6)])
			b.SetProxy("CBGreenMtn")
			self.rr.AddBreaker("CBHydeJct",      self, n, addr, [(2, 7)])
			self.rr.AddBreaker("CBHydeWest",     self, n, addr, [(3, 0)])
			self.rr.AddBreaker("CBHydeEast",     self, n, addr, [(3, 1)])
			self.rr.AddBreaker("CBSouthportJct", self, n, addr, [(3, 2)])
			self.rr.AddBreaker("CBCarlton",      self, n, addr, [(3, 3)])
			b = self.rr.AddBreaker("CBSheffieldB",   self, n, addr, [(3, 4)])
			b.SetProxy("CBSheffield")
			
			# virtual breakers:
			#    CBSheffield combines the state of SheffieldA and SheffieldB
			#    CBGreenMtn combines the state of GreenMtnStn and GreenMtnYd
			self.rr.AddBreaker("CBSheffield",  self, n, addr, [])
			self.rr.AddBreaker("CBGreenMtn",   self, n, addr, [])

	'''
	special processing for Sheffield and Green Mountain breakers - each of these combines the status of two other breakers
	'''
	def ShowBreakerState(self, brkr):
		for blist, bname in [ [("CBSheffieldA", "CBSheffieldB"), "CBSheffield"], [("CBGreenMtnStn", "CBGreenMtnYd"), "CBGreenMtn"] ]:
			if brkr.Name() in blist:
				# the combined status is only OK if BOTH are OK.  If either has tripped, signal a trip
				stat = self.rr.GetBreaker(blist[0]).IsTripped() or self.rr.GetBreaker(blist[1]).IsTripped()
				cbrkr = self.rr.GetBreaker(bname)
				if cbrkr.SetTripped(stat):
					cbrkr.UpdateIndicators()
					# if we change the state of the breaker, notify everyone
					self.rr.RailroadEvent(cbrkr.GetEventMessage())
			
			
			
			
			
			