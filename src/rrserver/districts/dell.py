import logging

from rrserver.district import District
from rrserver.constants import  DELL, FOSS
from rrserver.node import Node
from dispatcher.constants import SloAspects


class Dell(District):
	def __init__(self, rr, name, settings):
		District.__init__(self, rr, name, settings)
		
		self.DXO = None
		self.RXO = None
		
		self.rr = rr
		self.name = name
		self.nodeAddresses = [ DELL, FOSS ]
		self.nodes = {
			DELL:  Node(self, rr, DELL,  5, settings, incount=3),
			FOSS:  Node(self, rr, FOSS,  3, settings)
		}

		with self.nodes[DELL] as n:
			# outputs
			self.rr.AddSignal("D4RA", self, n, DELL, [(0, 0), (0, 1), (0, 2)])
			self.rr.AddSignal("D4RB", self, n, DELL, [(0, 3), (0, 4), (0, 5)])
			self.rr.AddSignal("D6RA", self, n, DELL, [(0, 6)])
			self.rr.AddSignal("D6RB", self, n, DELL, [(0, 7)])
	
			self.rr.AddSignal("D4L",  self, n, DELL, [(1, 0), (1, 1), (1, 2)])
			self.rr.AddSignal("D6L",  self, n, DELL, [(1, 3), (1, 4), (1, 5)])
			self.rr.AddOutputDevice("DXO", self, n, DELL, [(1, 6)]) # laport crossing signal/gate
			self.rr.AddBlockInd("H13", self, n, DELL, [(1, 7)])
	
			self.rr.AddBlockInd("D10", self, n, DELL, [(2, 0)])
			self.rr.AddBlockInd("S20", self, n, DELL, [(2, 1)])
			self.rr.AddHandswitchInd("DSw9", self, n, DELL, [(2, 2)])
			self.rr.AddTurnout("DSw1", self, n, DELL, [(2, 3), (2, 4)])
			self.rr.AddTurnout("DSw3", self, n, DELL, [(2, 5), (2, 6)])
			self.rr.AddTurnout("DSw5", self, n, DELL, [(2, 7), (3, 0)])

			self.rr.AddTurnout("DSw7",  self, n, DELL, [(3, 1), (3, 2)])
			self.rr.AddTurnoutPair("DSw7", "DSw7b")
			self.rr.AddTurnout("DSw11", self, n, DELL, [(3, 3), (3, 4)])
			self.rr.AddTurnoutPair("DSw11", "DSw11b")
			self.rr.AddStopRelay("D20.srel", self, n, DELL, [(3, 5)])
			self.rr.AddStopRelay("H23.srel", self, n, DELL, [(3, 6)])
			self.rr.AddStopRelay("D11.srel", self, n, DELL, [(3, 7)])

			# inputs	
			self.rr.AddTurnoutPosition("DSw1", self, n, DELL, [(0, 0), (0, 1)])
			self.rr.AddTurnoutPosition("DSw3", self, n, DELL, [(0, 2), (0, 3)])
			self.rr.AddTurnoutPosition("DSw5", self, n, DELL, [(0, 4), (0, 5)])
			self.rr.AddTurnoutPosition("DSw7", self, n, DELL, [(0, 6), (0, 7)])

			self.rr.AddHandswitch("DSw9", self, n, DELL, [(1, 0), (1, 1)])
			self.rr.AddTurnoutPosition("DSw11", self, n, DELL, [(1, 2), (1, 3)])
			self.rr.AddBlock("D20",      self, n, DELL, [(1, 4)], True) 
			self.rr.AddBlock("D20.E",    self, n, DELL, [(1, 5)], True) 
			b = self.rr.AddBlock("H23",      self, n, DELL, [(1, 6)], True) 
			sbe = self.rr.AddBlock("H23.E",    self, n, DELL, [(1, 7)], True) 
			b.AddStoppingBlocks([sbe])

			self.rr.AddBlock("DOSVJW",   self, n, DELL, [(2, 0)], False) 
			self.rr.AddBlock("DOSVJE",   self, n, DELL, [(2, 1)], True) 
			sbw = self.rr.AddBlock("D11.W",    self, n, DELL, [(2, 2)], False) 
			sba = self.rr.AddBlock("D11A",     self, n, DELL, [(2, 3)], False) 
			sbb = self.rr.AddBlock("D11B",     self, n, DELL, [(2, 4)], False) 
			b = self.rr.AddBlock("D11",      self, n, DELL, [], False)  # virtual definition for D11 
			sbe = self.rr.AddBlock("D11.E",    self, n, DELL, [(2, 5)], False) 
			b.AddStoppingBlocks([sbe, sbw])
			b.AddSubBlocks([sba, sbb])

		with self.nodes[FOSS] as n:
			# outputs
			self.rr.AddSignal("D10R", self, n, FOSS, [(0, 0), (0, 1), (0, 2)])
			self.rr.AddSignal("D12R", self, n, FOSS, [(0, 3), (0, 4), (0, 5)])
	
			self.rr.AddSignal("D10L", self, n, FOSS, [(1, 0), (1, 1), (1, 2)])
			self.rr.AddSignal("D12L", self, n, FOSS, [(1, 3), (1, 4), (1, 5)])
			self.rr.AddStopRelay("D21.srel", self, n, FOSS, [(1, 6)])
			self.rr.AddStopRelay("S10.srel", self, n, FOSS, [(1, 7)])
	
			# bit 2:0 is bad
			self.rr.AddStopRelay("R10.srel", self, n, FOSS, [(2, 1)])
			self.rr.AddOutputDevice("RXO", self, n, FOSS, [(2, 2)]) # rocky hill crossing gate/signal
			s = self.rr.AddSignal("R10W", self, n, FOSS, [(2, 3), (2, 4), (2, 5)])

			#inputs	
			sbw = self.rr.AddBlock("D21.W",     self, n, FOSS, [(0, 0)], True)
			sba = self.rr.AddBlock("D21A",      self, n, FOSS, [(0, 1)], True)
			sbb = self.rr.AddBlock("D21B",      self, n, FOSS, [(0, 2)], True)
			b = self.rr.AddBlock("D21",       self, n, FOSS, [], True) # virtual definition for D21
			sbe = self.rr.AddBlock("D21.E",     self, n, FOSS, [(0, 3)], True)
			b.AddStoppingBlocks([sbe, sbw])
			b.AddSubBlocks([sba, sbb])
			
			self.rr.AddBlock("DOSFOW",    self, n, FOSS, [(0, 4)], False)
			self.rr.AddBlock("DOSFOE",    self, n, FOSS, [(0, 5)], True)
			sbw = self.rr.AddBlock("S10.W",     self, n, FOSS, [(0, 6)], False)
			sba = self.rr.AddBlock("S10A",      self, n, FOSS, [(0, 7)], False)

			sbb = self.rr.AddBlock("S10B",      self, n, FOSS, [(1, 0)], False)
			sbc = self.rr.AddBlock("S10C",      self, n, FOSS, [(1, 1)], False)
			sbe = self.rr.AddBlock("S10.E",     self, n, FOSS, [(1, 2)], False)
			b = self.rr.AddBlock("S10",       self, n, FOSS, [], False) # virtual definition for S10
			b.AddStoppingBlocks([sbe, sbw])
			b.AddSubBlocks([sba, sbb, sbc])
			
			sbw = self.rr.AddBlock("R10.W",     self, n, FOSS, [(1, 3)], False)
			sba = self.rr.AddBlock("R10A",      self, n, FOSS, [(1, 4)], False)
			sbb = self.rr.AddBlock("R10B",      self, n, FOSS, [(1, 5)], False)
			sbc = self.rr.AddBlock("R10C",      self, n, FOSS, [(1, 6)], False)
			b = self.rr.AddBlock("R10",       self, n, FOSS, [], False)
			b.AddStoppingBlocks([sbw])
			b.AddSubBlocks([sba, sbb, sbc])
			
			self.rr.AddBlock("R11",       self, n, FOSS, [(1, 7)], False)
			
			self.rr.AddBlock("R12",       self, n, FOSS, [(2, 0)], False)
			self.rr.AddTurnoutPosition("RSw1", self, n, FOSS, [(2, 1), (2, 2)])

	def CheckTurnoutLocks(self, turnouts):
		changes = []
		s5 = turnouts["DSw5"].IsNormal()
		s7 = turnouts["DSw7"].IsNormal()
		if turnouts["DSw5"].Lock(not s7, "DSw7"):
			changes.append(["DSw5", not s7])
		if turnouts["DSw7"].Lock(not s5, "DSw5"):
			changes.append(["DSw7", not s5])
			changes.append(["DSw7b", not s5])
		return changes


	def OutIn(self):
		# determine the state of the crossing gate at laporte
		dos1 = self.rr.GetBlock("DOSVJW").IsOccupied()
		d11w = self.rr.GetBlock("D11.W").IsOccupied()
		d11a = self.rr.GetBlock("D11A").IsOccupied()
		if dos1 and not self.D1W:
			self.D1E = True
		if (d11w or d11a) and not self.D1E:
			self.D1W = True
		if not dos1 and not (d11w or d11a):
			self.D1E = self.D1W = False
		
		dos2 = self.rr.GetBlock("DOSVJE").IsOccupied()
		d21w = self.rr.GetBlock("D21.W").IsOccupied()
		d21a = self.rr.GetBlock("D21A").IsOccupied()
		if dos2 and not self.D2W:
			self.D2E = True
		if (d21w or d21a) and not self.D2E:
			self.D2W = True
		if not dos2 and not (d21w or d21a):
			self.D2E = self.D2W = False
		
		DXO = (self.D1E and dos1) or (self.D1W and (d11w or d11a)) or (self.D2E and dos2) or (self.D2W and (d21w or d21a))
		if DXO != self.DXO:
			self.DXO = DXO
			self.rr.SetODevice("DXO", self.DXO)
				
		# determine the state of the crossing gate at rocky hill
		r10b = self.rr.GetBlock("R10B")
		r10bo = r10b.IsOccupied()
		r10c = self.rr.GetBlock("R10C")
		r10co = r10c.IsOccupied()
		if r10bo and not self.RXW:
			self.RXE = True
		if r10co and not self.RXE:
			self.RXW = True
		if not r10bo and not r10co:
			self.RXE = self.RXW = False
		
		RXO = (r10bo and self.RXE) or (r10co and self.RXW)
		if RXO != self.RXO:
			self.RXO = RXO
			self.rr.SetODevice("RXO", self.RXO)
			
		# determine the state of signal R10W it should mirror signal N28L
		
		msig = self.rr.GetSignal("N28L")
		aspect = msig.Aspect()

		sig = self.rr.GetSignal("R10W")
		if sig.Aspect() != aspect:
			naspect = 2 if aspect == 3 else aspect
			self.rr.SetAspect("R10W", naspect)

		District.OutIn(self)
