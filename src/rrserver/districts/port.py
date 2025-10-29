import logging

from rrserver.district import District
from rrserver.constants import PORTA, PORTB, PARSONS
from rrserver.node import Node

class Port(District):
	def __init__(self, rr, name, settings):
		District.__init__(self, rr, name, settings)
		self.rr = rr
		self.name = name
		self.releasedA = False
		self.releasedB = False
		self.n25occ = None
		self.nodeAddresses = [ PORTA, PORTB, PARSONS]
		self.nodes = {
			PORTA:    Node(self, rr, PORTA,   9, settings, incount=8),
			PORTB:    Node(self, rr, PORTB,   7, settings, incount=6),
			PARSONS:  Node(self, rr, PARSONS, 4, settings)
		}

		self.PBE = False
		self.PBW = False
		self.PBXO = None
		self.clr10w = None
		self.clr50w = None
		self.clr11e = None
		self.clr21e = None
		self.clr40w = None
		self.clr32w = None
		self.clr42e = None

		# Port A - Southport
		addr = PORTA
		with self.nodes[PORTA] as n:
			self.rr.AddSignal("PA12R",  self, n, addr, [(0, 0), (0, 1)])
			self.rr.AddSignal("PA10RA", self, n, addr, [(0, 2), (0, 3)])
			self.rr.AddSignal("PA12LA", self, n, addr, [(0, 4)])
			self.rr.AddSignal("PA10RB", self, n, addr, [(0, 5), (0, 6)])
			self.rr.AddSignal("PA8R",   self, n, addr, [(0, 7), (1, 0)])
			self.rr.AddSignal("PA12LB", self, n, addr, [(1, 1)])
			self.rr.AddSignal("PA6R",   self, n, addr, [(1, 2), (1, 3)])
			self.rr.AddSignal("PA4RA",  self, n, addr, [(1, 4), (1, 5)])
			self.rr.AddSignal("PA12LC", self, n, addr, [(1, 6)])
			self.rr.AddSignal("PA4RB",  self, n, addr, [(1, 7), (2, 0)])
			self.rr.AddSignal("PA8L",   self, n, addr, [(2, 1)])
			self.rr.AddSignal("PA6LA",  self, n, addr, [(2, 2)])
			self.rr.AddSignal("PA6LB",  self, n, addr, [(2, 3)])
			self.rr.AddSignal("PA6LC",  self, n, addr, [(2, 4)])
			self.rr.AddOutputDevice("P10.clrw",  self, n, addr, [2, 5]) # semaphore for P10
			self.rr.AddOutputDevice("P10.rstw",  self, n, addr, [2, 6])
			self.rr.AddSignal("PA4L",   self, n, addr, [])  # virtual signals for semaphores
			self.rr.AddSignal("PA10L",  self, n, addr, [])
		
			self.rr.AddSignalLED("PA4",  self, n, addr, [(3, 1), (3, 0), (2, 7)])
			self.rr.AddSignalLED("PA6",  self, n, addr, [(3, 4), (3, 3), (3, 2)])
			self.rr.AddSignalLED("PA8",  self, n, addr, [(3, 7), (3, 6), (3, 5)])
			self.rr.AddSignalLED("PA10", self, n, addr, [(4, 2), (4, 1), (4, 0)])
			self.rr.AddSignalLED("PA12", self, n, addr, [(4, 5), (4, 4), (4, 3)])
			self.rr.AddSignalLED("PA32", self, n, addr, [(5, 0), (4, 7), (4, 6)])
			self.rr.AddSignalLED("PA34", self, n, addr, [(5, 3), (5, 2), (5, 1)])
		
			self.rr.AddBlockInd("P21", self, n, addr, [(5, 4)])
			self.rr.AddBlockInd("P40", self, n, addr, [(5, 5)])
			
			
			
			'''
			don't know what these 3are - they may be related to semaphores
			
			self.rr.AddBlockInd("P50", self, n, addr, [(5, 6)])
			self.rr.AddBlockInd("P11", self, n, addr, [(5, 7)])
			self.rr.AddBlockInd("P21", self, n, addr, [(6, 0)])
			
			'''
			
			
			
			self.rr.AddBreakerInd("CBParsonsJct", self, n, addr, [(6, 1)])
			self.rr.AddBreakerInd("CBSouthport",  self, n, addr, [(6, 2)])
			self.rr.AddBreakerInd("CBLavinYard",  self, n, addr, [(6, 3)])
		
			# virtual turnouts - we do not control these, so no output bits
			self.rr.AddTurnout("PASw1",  self, n, addr, [])
			self.rr.AddTurnout("PASw3",  self, n, addr, [])
			self.rr.AddTurnout("PASw5",  self, n, addr, [])
			self.rr.AddTurnout("PASw7",  self, n, addr, [])
			self.rr.AddTurnout("PASw9",  self, n, addr, [])
			self.rr.AddTurnoutPair("PASw9", "PASw9b")
			self.rr.AddTurnout("PASw11", self, n, addr, [])
			self.rr.AddTurnout("PASw13", self, n, addr, [])
			self.rr.AddTurnout("PASw15", self, n, addr, [])
			self.rr.AddTurnout("PASw17", self, n, addr, [])
			self.rr.AddTurnout("PASw19", self, n, addr, [])
			self.rr.AddTurnoutPair("PASw19", "PASw19b")
			self.rr.AddTurnout("PASw21", self, n, addr, [])
			self.rr.AddTurnout("PASw23", self, n, addr, [])
			
			self.rr.AddTurnoutLock("PASw1", self, n, addr, [(6, 4)])
			self.rr.AddTurnoutLock("PASw3", self, n, addr, [(6, 5)])
			self.rr.AddTurnoutLock("PASw5", self, n, addr, [(6, 6)])
			self.rr.AddTurnoutLock("PASw7", self, n, addr, [(6, 7)])
			self.rr.AddTurnoutLock("PASw9", self, n, addr, [(7, 0)])
			self.rr.AddTurnoutLock("PASw11", self, n, addr, [(7, 1)])
			self.rr.AddTurnoutLock("PASw15", self, n, addr, [(7, 2)])
			self.rr.AddTurnoutLock("PASw19", self, n, addr, [(7, 3)])
			self.rr.AddTurnoutLock("PASw21", self, n, addr, [(7, 4)])
			self.rr.AddTurnoutLock("PASw23", self, n, addr, [(7, 5)])
			self.rr.AddTurnoutLock("PASw31", self, n, addr, [(7, 6)])
			self.rr.AddTurnoutLock("PASw33", self, n, addr, [(7, 7)])
			self.rr.AddTurnoutLock("PASw35", self, n, addr, [(8, 0)])
			self.rr.AddTurnoutLock("PASw37", self, n, addr, [(8, 1)])
			
			self.rr.AddStopRelay("P10.srel", self, n, addr, [(8, 2)])
			self.rr.AddStopRelay("P40.srel", self, n, addr, [(8, 3)])
			self.rr.AddStopRelay("P31.srel", self, n, addr, [(8, 4)])
			self.rr.AddOutputDevice("P40.clrw",  self, n, addr, [8, 5]) # semaphore for P40
			self.rr.AddOutputDevice("P40.rstw",  self, n, addr, [8, 6])

			# inputs
			self.rr.AddTurnoutPosition("PASw1",  self, n, addr, [(0, 0), (0, 1)])
			self.rr.AddTurnoutPosition("PASw3",  self, n, addr, [(0, 2), (0, 3)])
			self.rr.AddTurnoutPosition("PASw5",  self, n, addr, [(0, 4), (0, 5)])
			self.rr.AddTurnoutPosition("PASw7",  self, n, addr, [(0, 6), (0, 7)])
			self.rr.AddTurnoutPosition("PASw9",  self, n, addr, [(1, 0), (1, 1)])
			self.rr.AddTurnoutPosition("PASw11", self, n, addr, [(1, 2), (1, 3)])
			self.rr.AddTurnoutPosition("PASw13", self, n, addr, [(1, 4), (1, 5)])
			self.rr.AddTurnoutPosition("PASw15", self, n, addr, [(1, 6), (1, 7)])
			self.rr.AddTurnoutPosition("PASw17", self, n, addr, [(2, 0), (2, 1)])
			self.rr.AddTurnoutPosition("PASw19", self, n, addr, [(2, 2), (2, 3)])
			self.rr.AddTurnoutPosition("PASw21", self, n, addr, [(2, 4), (2, 5)])
			self.rr.AddTurnoutPosition("PASw23", self, n, addr, [(2, 6), (2, 7)])

			self.rr.AddBlock("P1",     self, n, addr, [(3, 0)], True)
			self.rr.AddBlock("P2",     self, n, addr, [(3, 1)], True)
			self.rr.AddBlock("P3",     self, n, addr, [(3, 2)], True)
			self.rr.AddBlock("P4",     self, n, addr, [(3, 3)], True)
			self.rr.AddBlock("P5",     self, n, addr, [(3, 4)], False)
			self.rr.AddBlock("P6",     self, n, addr, [(3, 5)], False)
			self.rr.AddBlock("P7",     self, n, addr, [(3, 6)], False)
			self.rr.AddBlock("POSSP1", self, n, addr, [(3, 7)], True)
			self.rr.AddBlock("POSSP2", self, n, addr, [(4, 0)], True)
			self.rr.AddBlock("POSSP3", self, n, addr, [(4, 1)], True)
			self.rr.AddBlock("POSSP4", self, n, addr, [(4, 2)], True)
			self.rr.AddBlock("POSSP5", self, n, addr, [(4, 3)], True)

			b = self.rr.AddBlock("P10",    self, n, addr, [(4, 4)], False)
			sbe = self.rr.AddBlock("P10.E",  self, n, addr, [(4, 5)], False)
			b.AddStoppingBlocks([sbe])

			self.rr.AddSignalLever("PA4",  self, n, addr, [(4, 6), (4, 7), (5, 0)])
			self.rr.AddSignalLever("PA6",  self, n, addr, [(5, 1), (5, 2), (5, 3)])
			self.rr.AddSignalLever("PA8",  self, n, addr, [(5, 4), (5, 5), (5, 6)])			
			self.rr.AddSignalLever("PA10", self, n, addr, [(5, 7), (6, 0), (6, 1)])
			self.rr.AddSignalLever("PA12", self, n, addr, [(6, 2), (6, 3), (6, 4)])
			self.rr.AddSignalLever("PA32", self, n, addr, [(6, 5), (6, 6), (6, 7)])
			self.rr.AddSignalLever("PA34", self, n, addr, [(7, 0), (7, 1), (7, 2)])

			# virtual blocks - they have no detection
			self.rr.AddBlock("P60",     self, n, addr, [], False)
			self.rr.AddBlock("P61",     self, n, addr, [], False)
			self.rr.AddBlock("P62",     self, n, addr, [], True)
			self.rr.AddBlock("P63",     self, n, addr, [], True)
			self.rr.AddBlock("P64",     self, n, addr, [], True)
			self.rr.AddBlock("V10",     self, n, addr, [], True)
			self.rr.AddBlock("V11",     self, n, addr, [], False)

		addr = PARSONS	
		with self.nodes[PARSONS] as n:
			#outputs
			self.rr.AddSignal("PA34LB", self, n, addr, [(0, 0), (0, 1), (0, 2)])
			self.rr.AddSignal("PA32L",  self, n, addr, [(0, 3)])
			self.rr.AddSignal("PA34LA", self, n, addr, [(0, 4), (0, 5), (0, 6)])
			self.rr.AddSignal("PA34RD", self, n, addr, [(0, 7), (1, 0), (1, 1)])
			self.rr.AddSignal("PA34RC", self, n, addr, [(1, 2)])
			self.rr.AddSignal("PA32RA", self, n, addr, [(1, 3), (1, 4), (1, 5)])
			self.rr.AddSignal("PA34RB", self, n, addr, [(1, 6)])
			self.rr.AddSignal("PA32RB", self, n, addr, [(1, 7), (2, 0), (2, 1)])
			self.rr.AddSignal("PA34RA", self, n, addr, [(2, 2)])

			self.rr.AddStopRelay("P20.srel", self, n, addr, [(2, 3)])
			self.rr.AddStopRelay("P30.srel", self, n, addr, [(2, 4)])
			self.rr.AddStopRelay("P50.srel", self, n, addr, [(2, 5)])
			self.rr.AddStopRelay("P11.srel", self, n, addr, [(2, 6)])

			# virtual turnouts - we do not control these, so no output bits
			self.rr.AddTurnout("PASw27", self, n, addr, [])
			self.rr.AddTurnout("PASw29", self, n, addr, [])
			self.rr.AddTurnout("PASw31", self, n, addr, [])
			self.rr.AddTurnout("PASw33", self, n, addr, [])
			self.rr.AddTurnout("PASw35", self, n, addr, [])
			self.rr.AddTurnout("PASw37", self, n, addr, [])

			# Inputs
			self.rr.AddTurnoutPosition("PASw27", self, n, addr, [(0, 0), (0, 1)])
			self.rr.AddTurnoutPosition("PASw29", self, n, addr, [(0, 2), (0, 3)])
			self.rr.AddTurnoutPosition("PASw31", self, n, addr, [(0, 4), (0, 5)])
			self.rr.AddTurnoutPosition("PASw33", self, n, addr, [(0, 6), (0, 7)])
			self.rr.AddTurnoutPosition("PASw35", self, n, addr, [(1, 0), (1, 1)])
			self.rr.AddTurnoutPosition("PASw37", self, n, addr, [(1, 2), (1, 3)])
			
			b = self.rr.AddBlock("P20",    self, n, addr, [(1, 4)], True)
			sbe = self.rr.AddBlock("P20.E",  self, n, addr, [(1, 5)], True)
			b.AddStoppingBlocks([sbe])

			sbw = self.rr.AddBlock("P30.W",  self, n, addr, [(1, 6)], False)
			b = self.rr.AddBlock("P30",    self, n, addr, [(1, 7)], False)
			sbe = self.rr.AddBlock("P30.E",  self, n, addr, [(2, 0)], False)
			b.AddStoppingBlocks([sbe, sbw])

			self.rr.AddBlock("POSPJ1", self, n, addr, [(2, 1)], False)
			self.rr.AddBlock("POSPJ2", self, n, addr, [(2, 2)], False)

			sbw = self.rr.AddBlock("P50.W",  self, n, addr, [(2, 5)], False)
			b = self.rr.AddBlock("P50",    self, n, addr, [(2, 4)], False)
			sbe = self.rr.AddBlock("P50.E",  self, n, addr, [(2, 3)], False)
			b.AddStoppingBlocks([sbe, sbw])
			
			sbw = self.rr.AddBlock("P11.W",  self, n, addr, [(2, 6)], False)
			b = self.rr.AddBlock("P11",    self, n, addr, [(2, 7)], False)
			sbe = self.rr.AddBlock("P11.E",  self, n, addr, [(3, 0)], False)
			b.AddStoppingBlocks([sbe, sbw])

		addr = PORTB
		with self.nodes[PORTB] as n:
			#outputs
			self.rr.AddSignal("PB2L",  self, n, addr, [(0, 0), (0, 1), (0, 2)])
			self.rr.AddSignal("PB4L",  self, n, addr, [(0, 3), (0, 4), (0, 5)])
			self.rr.AddSignal("PB2R",  self, n, addr, [(0, 6), (0, 7), (1, 0)])
			self.rr.AddSignal("PB4R",  self, n, addr, [(1, 1), (1, 2), (1, 3)])
			self.rr.AddSignal("PB12R", self, n, addr, [(1, 4), (1, 5), (1, 6)])
			self.rr.AddSignal("PB14R", self, n, addr, [(1, 7), (2, 0), (2, 1)])
			self.rr.AddSignal("PB12L", self, n, addr, [(2, 2), (2, 3), (2, 4)])
			self.rr.AddSignal("PB14L", self, n, addr, [(2, 5), (2, 6), (2, 7)])

			self.rr.AddSignalLED("PB2",  self, n, addr, [(3, 0), (3, 1), (3, 2)])
			self.rr.AddSignalLED("PB4",  self, n, addr, [(3, 3), (3, 4), (3, 5)])

			self.rr.AddHandswitchInd("PBSw5",  self, n, addr, [(3, 6), (3, 7)], inverted=True)

			self.rr.AddSignalLED("PB12",  self, n, addr, [(4, 0), (4, 1), (4, 2)])
			self.rr.AddSignalLED("PB14",  self, n, addr, [(4, 3), (4, 4), (4, 5)])

			self.rr.AddHandswitchInd("PBSw15ab",  self, n, addr, [(4, 6), (4, 7)], inverted=True)
			
			self.rr.AddBlockInd("P30", self, n, addr, [(5, 0)])
			self.rr.AddBlockInd("P42", self, n, addr, [(5, 1)])
			
			self.rr.AddBreakerInd("CBSouthJct",  self, n, addr, [(5, 4)])
			self.rr.AddBreakerInd("CBCircusJct", self, n, addr, [(5, 5)])

			self.rr.AddTurnoutLock("PBSw1", self, n, addr, [(5, 6)])
			self.rr.AddTurnoutLock("PBSw3", self, n, addr, [(5, 7)])

			self.rr.AddHandswitchInd("PBSw5", self, n, addr, [(6, 0)], inverted=True)
			
			self.rr.AddTurnoutLock("PBSw11", self, n, addr, [(6, 1)])
			self.rr.AddTurnoutLock("PBSw13", self, n, addr, [(6, 2)])
	
			self.rr.AddHandswitchInd("PBSw15ab",  self, n, addr, [(6, 3)], inverted=True)
			
			self.rr.AddStopRelay("P32.srel", self, n, addr, [(6, 4)])
			self.rr.AddStopRelay("P41.srel", self, n, addr, [(6, 5)])
	
			# virtual turnouts - we do not control these, so no output bits
			self.rr.AddTurnout("PBSw1",  self, n, addr, [])
			self.rr.AddTurnoutPair("PBSw1", "PBSw1b")
			self.rr.AddTurnout("PBSw3",  self, n, addr, [])
			self.rr.AddTurnoutPair("PBSw3", "PBSw3b")
			self.rr.AddTurnout("PBSw11", self, n, addr, [])
			self.rr.AddTurnoutPair("PBSw11", "PBSw11b")
			self.rr.AddTurnout("PBSw13", self, n, addr, [])
			self.rr.AddTurnoutPair("PBSw13", "PBSw13b")

			# Inputs
			self.rr.AddTurnoutPosition("PBSw1",  self, n, addr, [(0, 0), (0, 1)])
			self.rr.AddTurnoutPosition("PBSw3",  self, n, addr, [(0, 2), (0, 3)])
			self.rr.AddTurnoutPosition("PBSw11", self, n, addr, [(0, 4), (0, 5)])
			self.rr.AddTurnoutPosition("PBSw13", self, n, addr, [(0, 6), (0, 7)])
	
			self.rr.AddHandswitch("PBSw5",   self, n, addr, [(1, 0), (1, 1)], "P41")
			self.rr.AddHandswitch("PBSw15a", self, n, addr, [(1, 2), (1, 3)], "P42")
			self.rr.AddHandswitch("PBSw15b", self, n, addr, [(1, 4), (1, 5)], "P42")

			b = self.rr.AddBlock("P40",    self, n, addr, [(1, 6)], False)	
			sbe = self.rr.AddBlock("P40.E",  self, n, addr, [(1, 7)], False)	
			b.AddStoppingBlocks([sbe])

			self.rr.AddBlock("POSSJ2", self, n, addr, [(2, 0)], False)	
			self.rr.AddBlock("POSSJ1", self, n, addr, [(2, 1)], False)

			sbe = self.rr.AddBlock("P31.E",  self, n, addr, [(2, 2)], False)
			b = self.rr.AddBlock("P31",    self, n, addr, [(2, 3)], False)
			sbw = self.rr.AddBlock("P31.W",  self, n, addr, [(2, 4)], False)
			b.AddStoppingBlocks([sbe, sbw])

			sbw = self.rr.AddBlock("P32.W",  self, n, addr, [(2, 5)], False)	
			b = self.rr.AddBlock("P32",    self, n, addr, [(2, 6)], False)	
			sbe = self.rr.AddBlock("P32.E",  self, n, addr, [(2, 7)], False)	
			b.AddStoppingBlocks([sbe, sbw])

			self.rr.AddBlock("POSCJ2", self, n, addr, [(3, 0)], False)	
			self.rr.AddBlock("POSCJ1", self, n, addr, [(3, 1)], False)

			sbe = self.rr.AddBlock("P41.E",  self, n, addr, [(3, 2)], True)
			b = self.rr.AddBlock("P41",    self, n, addr, [(3, 3)], True)
			sbw = self.rr.AddBlock("P41.W",  self, n, addr, [(3, 4)], True)
			b.AddStoppingBlocks([sbe, sbw])
				
			self.rr.AddSignalLever("PB2",  self, n, addr, [(3, 7), (3, 6), (3, 5)])
			self.rr.AddSignalLever("PB4",  self, n, addr, [(4, 2), (4, 1), (4, 0)])
				
			self.rr.AddHandswitchUnlock("PBSw5",    self, n, addr, [(4, 3)])
				
			self.rr.AddSignalLever("PB12",  self, n, addr, [(4, 6), (4, 5), (4, 4)])
			self.rr.AddSignalLever("PB14",  self, n, addr, [(5, 1), (5, 0), (4, 7)])
				
			self.rr.AddHandswitchUnlock("PBSw15ab",    self, n, addr, [(5, 2)])
			
			self.rr.AddTurnoutPosition("PBSw17", self, n, addr, [(5, 4), (5, 5)])
			self.rr.AddBlock("P33",    self, n, addr, [(5, 6)], False)	

	def SetAspect(self, sig, aspect):
		if sig.Name() == "PA4L":
			pb4La = aspect != 0 # clear
			pb4Lb = aspect == 4 # restricting
			for od, flag in [(self.rr.GetOutputDevice("P40.clrw"), pb4La), (self.rr.GetOutputDevice("P40.rstw"), pb4Lb)]:
				if od.SetOn(flag):
					bt = od.Bits()
					self.nodes[PORTA].SetOutputBit(bt[0], bt[1], 1 if flag else 0)
			return True
		elif sig.Name() == "PA10L":
			pb10La = aspect != 0 # clear
			pb10Lb = aspect == 4 # restricting
			for od, flag in [(self.rr.GetOutputDevice("P10.clrw"), pb10La), (self.rr.GetOutputDevice("P10.rstw"), pb10Lb)]:
				if od.SetOn(flag):
					bt = od.Bits()
					self.nodes[PORTA].SetOutputBit(bt[0], bt[1], 1 if flag else 0)
			return True
		
		return False
	
	def VerifyAspect(self, signame, aspect):
		if signame in [ "PA4RA", "PA4RB", "PA6R", "PA8R", "PA10RA", "PA10RB", "PA12R" ]:
			if aspect > 4:
				return aspect-4
			elif aspect == 4:
				return 0b10
			else:
				return aspect
			
		return aspect


	def OutIn(self):
		rlReqA = self.nodes[PORTA].GetInputBit(7, 3) == 1
		rlReqB = self.nodes[PORTB].GetInputBit(5, 3) == 1
		ossLocks = self.rr.GetControlOption("osslocks") == 1

		# release controls if requested by operator or if osslocks are turned off by dispatcher			
		self.releasedA = rlReqA or not ossLocks
		self.releasedB = rlReqB or not ossLocks

		P40M = self.rr.GetBlock("P40").IsOccupied()
		P40E = self.rr.GetBlock("P40.E").IsOccupied()
		if P40M and not self.PBE:
			self.PBW = True
		if P40E and not self.PBW:
			self.PBE = True
		if not P40M and not P40E:
			self.PBE = self.PBW = False
		PBXO = (P40E and self.PBE) or (P40M and self.PBW)
		if PBXO != self.PBXO:
			self.PBXO = PBXO
			self.nodes[PORTB].SetOutputBit(6, 6, 1 if PBXO else 0)
		
		blk = self.rr.GetBlock("P50")
		clr50w = blk.IsCleared() and not blk.IsEast()
		if clr50w != self.clr50w:
			self.clr50w = clr50w
			self.nodes[PORTA].SetOutputBit(5, 6, 1 if clr50w else 0) # yard signal
		
		blk = self.rr.GetBlock("P11")
		clr11e = blk.IsCleared() and blk.IsEast()
		if clr11e != self.clr11e:
			self.clr11e = clr11e
			self.nodes[PORTA].SetOutputBit(5, 7, 1 if clr11e else 0) # latham signals
		
		blk = self.rr.GetBlock("P21")
		clr21e = blk.IsCleared() and blk.IsEast()
		if clr21e != self.clr21e:
			self.clr21e = clr21e
			self.nodes[PORTA].SetOutputBit(6, 0, 1 if clr21e else 0) 
			
		blk = self.rr.GetBlock("P32")
		clr32w = blk.IsCleared() and not blk.IsEast()
		if clr32w != self.clr32w:
			self.clr32w = clr32w
			self.nodes[PORTB].SetOutputBit(5, 2, 1 if clr32w else 0)
		
		blk = self.rr.GetBlock("P42")
		clr42e = blk.IsCleared() and blk.IsEast()
		if clr42e != self.clr42e:
			self.clr42e = clr42e
			self.nodes[PORTB].SetOutputBit(5, 3, 1 if clr42e else 0)
		
		self.rr.UpdateDistrictTurnoutLocksByNode(self.name, self.releasedA, [PORTA, PARSONS])
		self.rr.UpdateDistrictTurnoutLocksByNode(self.name, self.releasedB, [PORTB])
		
		District.OutIn(self)
		
	def Released(self, tout):
		addr = tout.address
		if addr in [PORTA, PARSONS]:
			return self.releasedA
		else:
			return self.releasedB

	def SetHandswitchIn(self, hs, state):
		hsname = hs.Name()
		if hsname == "PBSw15ab":
			hsa = self.rr.GetHandswitch("PBSw15a")
			if hsa.Unlock(state != 0):
				self.rr.RailroadEvent(hsa.GetEventMessage(lock=True))
				
			hsb = self.rr.GetHandswitch("PBSw15b")
			if hsb.Unlock(state != 0):
				self.rr.RailroadEvent(hsb.GetEventMessage(lock=True))

	def SetHandswitch(self, hsname, state):
		if hsname in ["PBSw15a", "PBSw15b"]:
			hsa = self.rr.GetHandswitch("PBSw15a")
			hsb = self.rr.GetHandswitch("PSw15b")
			unlocked = hsa.IsUnlocked() or hsb.IsUnlocked()
			
			hs = self.rr.GetHandswitch("PBSw15ab")
			if hs.Unlock(unlocked):
				hs.UpdateIndicators()

