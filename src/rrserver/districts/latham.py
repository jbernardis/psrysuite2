import logging

from rrserver.district import District
from rrserver.constants import  LATHAM, CARLTON
from rrserver.node import Node

class Latham(District):
	def __init__(self, rr, name, settings):
		District.__init__(self, rr, name, settings)
		self.rr = rr
		self.name = name
		self.nodeAddresses = [ LATHAM, CARLTON ]
		self.nodes = {
			LATHAM:   Node(self, rr, LATHAM,   5, settings),
			CARLTON:  Node(self, rr, CARLTON,  5, settings, incount=3)
		}

		addr = LATHAM		
		with self.nodes[addr] as n:
			# outputs
			self.rr.AddTurnout("LSw1", self, n, addr, [(0, 0), (0, 1)])
			self.rr.AddTurnout("LSw3", self, n, addr, [(2, 2), (0, 3)]) #output bit 0:2 is bad - using 2:2
			self.rr.AddTurnoutPair("LSw3", "LSw3b")
			self.rr.AddTurnout("LSw5", self, n, addr, [(0, 4), (0, 5)])
			self.rr.AddTurnoutPair("LSw5", "LSw5b")
			self.rr.AddTurnout("LSw7", self, n, addr, [(0, 7), (0, 6)]) #yes - these bits are intentionally reversed
			self.rr.AddTurnoutPair("LSw7", "LSw7b")
			self.rr.AddTurnout("LSw9", self, n, addr, [(1, 0), (1, 1)])
			self.rr.AddTurnoutPair("LSw9", "LSw9b")

			self.rr.AddSignal("L4R",  self, n, addr, [(1, 2), (1, 3), (1, 4)])
			self.rr.AddSignal("L6RB", self, n, addr, [(1, 5)])
			self.rr.AddSignal("L6RA", self, n, addr, [(1, 6), (1, 7), (2, 0)])
			self.rr.AddSignal("L8R",  self, n, addr, [(2, 1)])
			# bit 2:2 is used above for LSw3
			# bit 2:3 is unused
			self.rr.AddSignal("L4L",  self, n, addr, [(2, 4)])
			self.rr.AddSignal("L6L",  self, n, addr, [(2, 5), (2, 6), (2, 7)])
			self.rr.AddSignal("L8L",  self, n, addr, [(3, 0), (3, 1), (3, 2)])
			
			self.rr.AddBlockInd("L10", self, n, addr, [(3, 3)])
			self.rr.AddBlockInd("L31", self, n, addr, [(3, 4)])
			self.rr.AddBlockInd("P11", self, n, addr, [(3, 5)])

			self.rr.AddStopRelay("L20.srel", self, n, addr, [(3, 6)])
			self.rr.AddStopRelay("P21.srel", self, n, addr, [(3, 7)])
			self.rr.AddStopRelay("L11.srel", self, n, addr, [(4, 0)])
			self.rr.AddStopRelay("L21.srel", self, n, addr, [(4, 1)])
			#self.rr.AddStopRelay("P50.srel", self, n, addr, [(4, 2)])
			
			# inputs
			self.rr.AddTurnoutPosition("LSw1", self, n, addr, [(0, 0), (0, 1)])
			self.rr.AddTurnoutPosition("LSw3", self, n, addr, [(0, 2), (0, 3)])
			self.rr.AddTurnoutPosition("LSw5", self, n, addr, [(0, 4), (0, 5)])
			self.rr.AddTurnoutPosition("LSw7", self, n, addr, [(0, 6), (0, 7)])
			self.rr.AddTurnoutPosition("LSw9", self, n, addr, [(1, 0), (1, 1)])
			
			b = self.rr.AddBlock("L20",      self, n, addr, [(1, 2)], True)
			sbe = self.rr.AddBlock("L20.E",    self, n, addr, [(1, 3)], True)
			b.AddStoppingBlocks([sbe])
			
			b = self.rr.AddBlock("P21",      self, n, addr, [(1, 4)], True)
			sbe = self.rr.AddBlock("P21.E",    self, n, addr, [(1, 5)], True)
			b.AddStoppingBlocks([sbe])
			
			self.rr.AddBlock("LOSLAW",   self, n, addr, [(1, 6)], False) #LOS1
			self.rr.AddBlock("LOSLAM",   self, n, addr, [(1, 7)], True) #LOS2
			self.rr.AddBlock("LOSLAE",   self, n, addr, [(2, 0)], True) #LOS3
			self.rr.AddBlock("L11.W",    self, n, addr, [(2, 1)], False)
			self.rr.AddBlock("L11",      self, n, addr, [(2, 2)], False)
			self.rr.AddBlock("L21.W",    self, n, addr, [(2, 3)], True)
			self.rr.AddBlock("L21",      self, n, addr, [(2, 4)], True)
			self.rr.AddBlock("L21.E",    self, n, addr, [(2, 5)], True)
			
			self.rr.AddBreaker("CBCliveden",       self, n, addr, [(2, 6)])
			self.rr.AddBreaker("CBLatham",         self, n, addr, [(2, 7)])
			self.rr.AddBreaker("CBCornellJct",     self, n, addr, [(3, 0)])
			self.rr.AddBreaker("CBParsonsJct",     self, n, addr, [(3, 1)])
			self.rr.AddBreaker("CBSouthJct",       self, n, addr, [(3, 2)])
			self.rr.AddBreaker("CBCircusJct",      self, n, addr, [(3, 3)])
			self.rr.AddBreaker("CBSouthport",      self, n, addr, [(3, 4)])
			self.rr.AddBreaker("CBLavinYard",      self, n, addr, [(3, 5)])
			self.rr.AddBreaker("CBReverserP31",    self, n, addr, [(3, 6)])
			self.rr.AddBreaker("CBReverserP41",    self, n, addr, [(3, 7)])
			self.rr.AddBreaker("CBReverserP50",    self, n, addr, [(4, 0)])
			self.rr.AddBreaker("CBReverserC22C23", self, n, addr, [(4, 1)])

		addr = CARLTON	
		with self.nodes[addr] as n:
			# outputs
			self.rr.AddSignal("L16R", self, n, addr, [(0, 0), (0, 1), (0, 2)])
			self.rr.AddSignal("L18R", self, n, addr, [(0, 3)])
			self.rr.AddSignal("L14R", self, n, addr, [(0, 4), (0, 5), (0, 6)])
			self.rr.AddSignal("L14L", self, n, addr, [(0, 7)])
			self.rr.AddSignal("L18L", self, n, addr, [(1, 0), (1, 1), (1, 2)])

			self.rr.AddHandswitchInd("LSw11", self, n, addr, [(1, 3)])
			self.rr.AddHandswitchInd("LSw13", self, n, addr, [(1, 4)])

			self.rr.AddTurnout("LSw15", self, n, addr, [(1, 5), (1, 6)])
			self.rr.AddTurnoutPair("LSw15", "LSw15b")
			self.rr.AddTurnout("LSw17", self, n, addr, [(1, 7), (2, 0)])
			
			self.rr.AddStopRelay("L31.srel", self, n, addr, [(2, 1)])
			self.rr.AddStopRelay("D10.srel", self, n, addr, [(2, 2)])

			self.rr.AddSignal("S21E", self, n, addr, [(2, 3), (2, 4), (2, 5)])
			self.rr.AddSignal("N20W", self, n, addr, [(2, 6), (2, 7), (3, 0)])
			# bits 1, 2, 3 unused
			self.rr.AddSignal("S11E", self, n, addr, [(3, 4), (3, 5), (3, 6)])
			self.rr.AddSignal("N10W", self, n, addr, [(3, 7), (4, 0), (4, 1)])
			
			self.rr.AddStopRelay("S21.srel", self, n, addr, [(4, 2)])
			self.rr.AddStopRelay("N25.srel", self, n, addr, [(4, 3)])
			
			# inputs
			self.rr.AddHandswitch("LSw11", self, n, addr, [(0, 0), (0, 1)])
			self.rr.AddHandswitch("LSw13", self, n, addr, [(0, 2), (0, 3)])
			
			self.rr.AddTurnoutPosition("LSw15", self, n, addr, [(0, 4), (0, 5)])
			self.rr.AddTurnoutPosition("LSw17", self, n, addr, [(0, 6), (0, 7)])

			b = self.rr.AddBlock("L31",      self, n, addr, [(1, 0)], True) 
			sbe = self.rr.AddBlock("L31.E",    self, n, addr, [(1, 1)], True) 
			b.AddStoppingBlocks([sbe])

			self.rr.AddBlock("LOSCAW",   self, n, addr, [(1, 2)], False) 
			self.rr.AddBlock("LOSCAM",   self, n, addr, [(1, 3)], True) 
			self.rr.AddBlock("LOSCAE",   self, n, addr, [(1, 4)], True) 
			self.rr.AddBlock("D10.W",    self, n, addr, [(1, 5)], False) 
			self.rr.AddBlock("D10",      self, n, addr, [(1, 6)], False) 
	
			sbw = self.rr.AddBlock("S21.W",    self, n, addr, [(2, 0)], True) 
			b = self.rr.AddBlock("S21",      self, n, addr, [(2, 1)], True) 
			sbe = self.rr.AddBlock("S21.E",    self, n, addr, [(2, 2)], True) 
			b.AddStoppingBlocks([sbe, sbw])
			
			self.rr.AddBlock("N25.W",    self, n, addr, [(2, 3)], False) 
			self.rr.AddBlock("N25",      self, n, addr, [(2, 4)], False) 
			self.rr.AddBlock("N25.E",    self, n, addr, [(2, 5)], False) 

	def Initialize(self):
		District.Initialize(self)
		
		self.rr.SetAspect("S21E", 1)
		self.rr.SetAspect("N10W", 1)
		self.rr.SetBlockDirection("N20", "E")
		self.rr.SetBlockDirection("S11", "W")
