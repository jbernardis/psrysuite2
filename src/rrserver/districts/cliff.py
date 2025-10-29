import logging

from rrserver.district import District
from rrserver.constants import  CLIFF, GREENMTN, SHEFFIELD
from rrserver.node import Node


class Cliff(District):
	def __init__(self, rr, name, settings):
		District.__init__(self, rr, name, settings)
		self.rr = rr
		self.name = name
		self.nodeAddresses = [ GREENMTN, CLIFF, SHEFFIELD ]
		
		self.nodes = {
			GREENMTN:   Node(self, rr, GREENMTN,  3, settings),
			CLIFF:      Node(self, rr, CLIFF,     8, settings),
			SHEFFIELD:  Node(self, rr, SHEFFIELD, 4, settings, incount=2)
		}
		self.entryButton = None
		self.currentCoachRoute = None
		self.optFleet = None
		self.released = False
		self.control = 2
		self.lastControl = 0

		addr = GREENMTN
		with self.nodes[addr] as n:
			# outputs
			self.rr.AddSignal("C2LB", self, n, addr, [(0, 0), (0, 1), (0, 2)])
			self.rr.AddSignal("C2LD", self, n, addr, [(0, 3)])
			self.rr.AddSignal("C2R",  self, n, addr, [(0, 4), (0, 5), (0, 6)])
			self.rr.AddSignal("C2LA", self, n, addr, [(0, 7), (1, 0)])
			self.rr.AddSignal("C2LC", self, n, addr, [(1, 1)])
			self.rr.AddSignal("C4RA", self, n, addr, [(1, 2), (1, 3)])
			self.rr.AddSignal("C4RB", self, n, addr, [(1, 4), (1, 5)])
			self.rr.AddSignal("C4RC", self, n, addr, [(1, 6), (1, 7), (2, 0)])
			self.rr.AddSignal("C4RD", self, n, addr, [(2, 1)])
			self.rr.AddSignal("C4L",  self, n, addr, [(2, 2), (2, 3), (2, 4)])

			self.rr.AddHandswitchInd("CSw3", self, n, addr, [(2, 5)])
			
			# virtual turnouts - these are managed by the CLIFF panel - no output bits
			self.rr.AddTurnout("CSw31", self, n, addr, [])
			self.rr.AddTurnout("CSw33", self, n, addr, [])
			self.rr.AddTurnout("CSw35", self, n, addr, [])
			self.rr.AddTurnout("CSw37", self, n, addr, [])
			self.rr.AddTurnout("CSw39", self, n, addr, [])
			self.rr.AddTurnout("CSw41", self, n, addr, [])

			# inputs
			self.rr.AddRouteIn("CC30E", self, n, addr, [(0, 0)])	
			self.rr.AddRouteIn("CC10E", self, n, addr, [(0, 1)])	
			self.rr.AddRouteIn("CG10E", self, n, addr, [(0, 2)])	
			self.rr.AddRouteIn("CG12E", self, n, addr, [(0, 3)])	
			self.rr.AddRouteIn("CC31W", self, n, addr, [(0, 4)])	
			self.rr.AddRouteIn("CC30W", self, n, addr, [(0, 5)])	
			self.rr.AddRouteIn("CC10W", self, n, addr, [(0, 6)])	
			self.rr.AddRouteIn("CG21W", self, n, addr, [(0, 7)])	
			
			self.rr.AddHandswitch("CSw3", self, n, addr, [(1, 0), (1, 1)], "C30")

			self.rr.AddBlock("C11", self, n, addr, [(1, 2)], True)
			self.rr.AddBlock("COSGMW", self, n, addr, [(1, 3)], True)
			self.rr.AddBlock("C10", self, n, addr, [(1, 4)], True)
			self.rr.AddBlock("C30", self, n, addr, [(1, 5)], True)
			self.rr.AddBlock("C31", self, n, addr, [(1, 6)], True)
			self.rr.AddBlock("COSGME", self, n, addr, [(1, 7)], True)
			self.rr.AddBlock("C20", self, n, addr, [(2, 0)], True)
			
			# virtual blocks with no detection
			self.rr.AddBlock("G10", self, n, addr, [], True)
			self.rr.AddBlock("G12", self, n, addr, [], True)
			self.rr.AddBlock("G21", self, n, addr, [], True)

		addr = CLIFF
		with self.nodes[addr] as n:
			# outputs
			self.rr.AddSignalLED("C2",  self, n, addr, [(0, 0), (0, 1), (0, 2)])
			self.rr.AddSignalLED("C4",  self, n, addr, [(0, 3), (0, 4), (0, 5)])
			self.rr.AddSignalLED("C6",  self, n, addr, [(0, 6), (0, 7), (1, 0)])
			self.rr.AddSignalLED("C8",  self, n, addr, [(1, 1), (1, 2), (1, 3)])
			self.rr.AddSignalLED("C10", self, n, addr, [(1, 4), (1, 5), (1, 6)])
			self.rr.AddSignalLED("C12", self, n, addr, [(1, 7), (2, 0), (2, 1)])
			self.rr.AddSignalLED("C14", self, n, addr, [(2, 2), (2, 3), (2, 4)])
			self.rr.AddSignalLED("C18", self, n, addr, [(2, 7), (3, 0), (3, 1)])
			self.rr.AddSignalLED("C22", self, n, addr, [(3, 2), (3, 3), (3, 4)])
			self.rr.AddSignalLED("C24", self, n, addr, [(3, 5), (3, 6), (3, 7)])

			self.rr.AddHandswitchInd("CSw3",  self, n, addr, [(4, 0), (4, 1)], inverted=True)
			self.rr.AddHandswitchInd("CSw11", self, n, addr, [(4, 2), (4, 3)], inverted=True)
			self.rr.AddHandswitchInd("CSw15", self, n, addr, [(4, 4), (4, 5)], inverted=True)
			self.rr.AddHandswitchInd("CSw19", self, n, addr, [(4, 6), (4, 7)], inverted=True)
			self.rr.AddHandswitchInd("CSw21ab", self, n, addr, [(5, 0), (5, 1)], inverted=True)
			
			self.rr.AddBlockInd("B10", self, n, addr, [(5, 2)])
			
			self.rr.AddBreakerInd("CBGreenMtn",        self, n, addr, [(5, 3)]) # combines GreenMtnStn and GreenMtnYd
			self.rr.AddBreakerInd("CBSheffield",       self, n, addr, [(5, 4)]) # combines SheffieldA and SheffieldB
			self.rr.AddBreakerInd("CBCliveden",        self, n, addr, [(5, 5)])
			self.rr.AddBreakerInd("CBReverserC22C23",  self, n, addr, [(5, 6)])
			self.rr.AddBreakerInd("CBBank",            self, n, addr, [(5, 7)])
			
			self.rr.AddTurnoutLock("CSw31", self, n, addr, [(6, 0)])
			self.rr.AddTurnoutLock("CSw41", self, n, addr, [(6, 1)])
			self.rr.AddTurnoutLock("CSw43", self, n, addr, [(6, 2)])
			self.rr.AddTurnoutLock("CSw61", self, n, addr, [(6, 3)])
			self.rr.AddTurnoutLock("CSw9",  self, n, addr, [(6, 4)])
			self.rr.AddTurnoutLock("CSw13", self, n, addr, [(6, 5)])
			self.rr.AddTurnoutLock("CSw17", self, n, addr, [(6, 6)])
			self.rr.AddTurnoutLock("CSw23", self, n, addr, [(6, 7)])
			
			self.rr.AddHandswitchReverseInd("CSw21a", self, n, addr, [(7, 0)])
			self.rr.AddHandswitchReverseInd("CSw21b", self, n, addr, [(7, 1)])
			self.rr.AddHandswitchReverseInd("CSw19",  self, n, addr, [(7, 2)])
			self.rr.AddHandswitchReverseInd("CSw15",  self, n, addr, [(7, 3)])
			self.rr.AddHandswitchReverseInd("CSw11",  self, n, addr, [(7, 4)])

			# Inputs
			self.rr.AddRouteIn("CC21E",  self, n, addr, [(0, 0)])
			self.rr.AddRouteIn("CC40E",  self, n, addr, [(0, 1)])
			self.rr.AddRouteIn("CC44E",  self, n, addr, [(0, 2)])
			self.rr.AddRouteIn("CC43E",  self, n, addr, [(0, 3)])
			self.rr.AddRouteIn("CC42E",  self, n, addr, [(0, 4)])
			self.rr.AddRouteIn("CC41E",  self, n, addr, [(0, 5)])
			self.rr.AddRouteIn("CC41W",  self, n, addr, [(0, 6)])
			self.rr.AddRouteIn("CC42W",  self, n, addr, [(0, 7)])			
			self.rr.AddRouteIn("CC21W",  self, n, addr, [(1, 0)])
			self.rr.AddRouteIn("CC40W",  self, n, addr, [(1, 1)])
			self.rr.AddRouteIn("CC44W",  self, n, addr, [(1, 2)])
			self.rr.AddRouteIn("CC43W",  self, n, addr, [(1, 3)])
			
			self.rr.AddBlock("COSSHE", self, n, addr, [(1, 4)], False)
			self.rr.AddBlock("C21",    self, n, addr, [(1, 5)], False)
			self.rr.AddBlock("C40",    self, n, addr, [(1, 6)], False)
			self.rr.AddBlock("C41",    self, n, addr, [(1, 7)], False)
			self.rr.AddBlock("C42",    self, n, addr, [(2, 0)], False)
			self.rr.AddBlock("C43",    self, n, addr, [(2, 1)], False)
			self.rr.AddBlock("C44",    self, n, addr, [(2, 2)], False)
			self.rr.AddBlock("COSSHW", self, n, addr, [(2, 3)], False)
			
			self.rr.AddSignalLever("C2",  self, n, addr, [(2, 4), (2, 5), (2, 6)])
			self.rr.AddSignalLever("C4",  self, n, addr, [(2, 7), (3, 0), (3, 1)])
			self.rr.AddSignalLever("C6",  self, n, addr, [(3, 2), (3, 3), (3, 4)])
			self.rr.AddSignalLever("C8",  self, n, addr, [(3, 5), (3, 6), (3, 7)])
			self.rr.AddSignalLever("C10", self, n, addr, [(4, 0), (4, 1), (4, 2)])
			self.rr.AddSignalLever("C12", self, n, addr, [(4, 3), (4, 4), (4, 5)])
			self.rr.AddSignalLever("C14", self, n, addr, [(4, 6), (4, 7), (7, 1)])
			self.rr.AddSignalLever("C18", self, n, addr, [(5, 2), (5, 3), (5, 4)])
			self.rr.AddSignalLever("C22", self, n, addr, [(5, 5), (5, 6), (5, 7)])
			self.rr.AddSignalLever("C24", self, n, addr, [(6, 0), (6, 1), (6, 2)])
			
			#===================================================================
			# self.rr.AddSignalLever("C2",  self, n, addr, [(2, 6), (2, 5), (2, 4)])
			# self.rr.AddSignalLever("C4",  self, n, addr, [(3, 1), (3, 0), (2, 7)])
			# self.rr.AddSignalLever("C6",  self, n, addr, [(3, 4), (3, 3), (3, 2)])
			# self.rr.AddSignalLever("C8",  self, n, addr, [(3, 7), (3, 6), (3, 5)])
			# self.rr.AddSignalLever("C10", self, n, addr, [(4, 2), (4, 1), (4, 0)])
			# self.rr.AddSignalLever("C12", self, n, addr, [(4, 5), (4, 4), (4, 3)])
			# self.rr.AddSignalLever("C14", self, n, addr, [(7, 1), (4, 7), (4, 6)])
			# self.rr.AddSignalLever("C18", self, n, addr, [(5, 4), (5, 3), (5, 2)])
			# self.rr.AddSignalLever("C22", self, n, addr, [(5, 7), (5, 6), (5, 5)])
			# self.rr.AddSignalLever("C24", self, n, addr, [(6, 2), (6, 1), (6, 0)])
			#===================================================================
			
			self.rr.AddHandswitchUnlock("CSw3",    self, n, addr, [(6, 4)])
			self.rr.AddHandswitchUnlock("CSw11",   self, n, addr, [(6, 5)])
			self.rr.AddHandswitchUnlock("CSw15",   self, n, addr, [(6, 6)])
			self.rr.AddHandswitchUnlock("CSw19",   self, n, addr, [(6, 7)])
			self.rr.AddHandswitchUnlock("CSw21ab", self, n, addr, [(7, 0)])

		addr = SHEFFIELD
		with self.nodes[addr] as n:
			# outputs
			self.rr.AddOutNXButton("CC54E", self, n, addr, [(0, 0)])
			self.rr.AddOutNXButton("CC53E", self, n, addr, [(0, 1)])
			self.rr.AddOutNXButton("CC52E", self, n, addr, [(0, 2)])
			self.rr.AddOutNXButton("CC51E", self, n, addr, [(0, 3)])
			self.rr.AddOutNXButton("CC50E", self, n, addr, [(0, 4)])
			self.rr.AddOutNXButton("CC21E", self, n, addr, [(0, 5)])
			self.rr.AddOutNXButton("CC40E", self, n, addr, [(0, 6)])
			self.rr.AddOutNXButton("CC41E", self, n, addr, [(0, 7)])
			self.rr.AddOutNXButton("CC42E", self, n, addr, [(1, 0)])
			self.rr.AddOutNXButton("CC43E", self, n, addr, [(1, 1)])
			self.rr.AddOutNXButton("CC44E", self, n, addr, [(1, 2)])
			self.rr.AddOutNXButton("CC54W", self, n, addr, [(1, 3)])
			self.rr.AddOutNXButton("CC53W", self, n, addr, [(1, 4)])
			self.rr.AddOutNXButton("CC52W", self, n, addr, [(1, 5)])
			self.rr.AddOutNXButton("CC51W", self, n, addr, [(1, 6)])
			self.rr.AddOutNXButton("CC50W", self, n, addr, [(1, 7)])
			self.rr.AddOutNXButton("CC21W", self, n, addr, [(2, 0)])
			self.rr.AddOutNXButton("CC40W", self, n, addr, [(2, 1)])
			self.rr.AddOutNXButton("CC41W", self, n, addr, [(2, 2)])
			self.rr.AddOutNXButton("CC42W", self, n, addr, [(2, 3)])
			self.rr.AddOutNXButton("CC43W", self, n, addr, [(2, 4)])
			self.rr.AddOutNXButton("CC44W", self, n, addr, [(2, 5)])
			self.rr.AddOutNXButton("CC30E", self, n, addr, [(2, 6)])
			self.rr.AddOutNXButton("CC10E", self, n, addr, [(2, 7)])			
			self.rr.AddOutNXButton("CG10E", self, n, addr, [(3, 0)])
			self.rr.AddOutNXButton("CG12E", self, n, addr, [(3, 1)])
			self.rr.AddOutNXButton("CC30W", self, n, addr, [(3, 2)])
			self.rr.AddOutNXButton("CC31W", self, n, addr, [(3, 3)])
			self.rr.AddOutNXButton("CC10W", self, n, addr, [(3, 4)])
			self.rr.AddOutNXButton("CG21W", self, n, addr, [(3, 5)])
			
			# virtual signals - these do not physically exist so no output bits
			self.rr.AddSignal("C6R", self, n, addr, [])
			self.rr.AddSignal("C6LA", self, n, addr, [])
			self.rr.AddSignal("C6LB", self, n, addr, [])
			self.rr.AddSignal("C6LC", self, n, addr, [])
			self.rr.AddSignal("C6LD", self, n, addr, [])
			self.rr.AddSignal("C6LE", self, n, addr, [])
			self.rr.AddSignal("C6LF", self, n, addr, [])
			self.rr.AddSignal("C6LG", self, n, addr, [])
			self.rr.AddSignal("C6LH", self, n, addr, [])
			self.rr.AddSignal("C6LJ", self, n, addr, [])
			self.rr.AddSignal("C6LK", self, n, addr, [])
			self.rr.AddSignal("C6LL", self, n, addr, [])
			self.rr.AddSignal("C8L", self, n, addr, [])
			self.rr.AddSignal("C8RA", self, n, addr, [])
			self.rr.AddSignal("C8RB", self, n, addr, [])
			self.rr.AddSignal("C8RC", self, n, addr, [])
			self.rr.AddSignal("C8RD", self, n, addr, [])
			self.rr.AddSignal("C8RE", self, n, addr, [])
			self.rr.AddSignal("C8RF", self, n, addr, [])
			self.rr.AddSignal("C8RG", self, n, addr, [])
			self.rr.AddSignal("C8RH", self, n, addr, [])
			self.rr.AddSignal("C8RJ", self, n, addr, [])
			self.rr.AddSignal("C8RK", self, n, addr, [])
			self.rr.AddSignal("C8RL", self, n, addr, [])
		
			# virtual turnouts - these are managed by the CLIFF panel - no output bits
			self.rr.AddTurnout("CSw43", self, n, addr, [])
			self.rr.AddTurnout("CSw45", self, n, addr, [])
			self.rr.AddTurnout("CSw47", self, n, addr, [])
			self.rr.AddTurnout("CSw49", self, n, addr, [])
			self.rr.AddTurnout("CSw51", self, n, addr, [])
			self.rr.AddTurnout("CSw53", self, n, addr, [])
			self.rr.AddTurnout("CSw55", self, n, addr, [])
			self.rr.AddTurnout("CSw57", self, n, addr, [])
			self.rr.AddTurnout("CSw59", self, n, addr, [])
			self.rr.AddTurnout("CSw61", self, n, addr, [])
			self.rr.AddTurnout("CSw63", self, n, addr, [])
			self.rr.AddTurnout("CSw65", self, n, addr, [])
			self.rr.AddTurnout("CSw67", self, n, addr, [])
			self.rr.AddTurnout("CSw69", self, n, addr, [])
			self.rr.AddTurnout("CSw71", self, n, addr, [])
			self.rr.AddTurnout("CSw73", self, n, addr, [])
			self.rr.AddTurnout("CSw75", self, n, addr, [])
			self.rr.AddTurnout("CSw77", self, n, addr, [])
			self.rr.AddTurnout("CSw79", self, n, addr, [])
			self.rr.AddTurnout("CSw81", self, n, addr, [])

			# inputs
			self.rr.AddRouteIn("CC50E", self, n, addr, [(0, 0)])
			self.rr.AddRouteIn("CC51E", self, n, addr, [(0, 1)])
			self.rr.AddRouteIn("CC52E", self, n, addr, [(0, 2)])
			self.rr.AddRouteIn("CC53E", self, n, addr, [(0, 3)])
			self.rr.AddRouteIn("CC54E", self, n, addr, [(0, 4)])
			self.rr.AddRouteIn("CC50W", self, n, addr, [(0, 5)])
			self.rr.AddRouteIn("CC51W", self, n, addr, [(0, 6)])
			self.rr.AddRouteIn("CC52W", self, n, addr, [(0, 7)])		
			self.rr.AddRouteIn("CC53W", self, n, addr, [(1, 0)])
			self.rr.AddRouteIn("CC54W", self, n, addr, [(1, 1)])
			
			self.rr.AddBlock("C50", self, n, addr, [(1, 2)], False)
			self.rr.AddBlock("C51", self, n, addr, [(1, 3)], False)
			self.rr.AddBlock("C52", self, n, addr, [(1, 4)], False)
			self.rr.AddBlock("C53", self, n, addr, [(1, 5)], False)
			self.rr.AddBlock("C54", self, n, addr, [(1, 6)], False)

		'''
		which signals are affected by fleeting, for each of the control options
		This indicates the effect for the dispatcher program.
		
		0 => Cliff, 1 => Dispatcher Cliveden/Bank, 2 => Dispatcher All
		'''
		self.fleetedSignals = [
			[],
			["C22L", "C22R", "C24L", "C24R" ],
			["C8L", "C8RA", "C8RB", "C8RC", "C8RD", "C8RE", "C8RF", "C8RG", "C8RH", "C8RJ", "C8RK", "C8RL", 
				"C6R", "C6LA", "C6LB", "C6LC", "C6LD", "C6LE", "C6LF", "C6LG", "C6LH", "C6LJ", "C6LK", "C6LL", 
				"C4L", "C4RA", "C4RB", "C4RC", "C4RD", "C2R", "C2LA", "C2LB", "C2LC", "C2LD"],
				["C10L", "C10R", "C12L", "C12R", "C22L", "C22R", "C24L", "C24R" ]
		]

		self.fleetedSignalsCliff = [
			["C8L", "C8RA", "C8RB", "C8RC", "C8RD", "C8RE", "C8RF", "C8RG", "C8RH", "C8RJ", "C8RK", "C8RL",
				"C6R", "C6LA", "C6LB", "C6LC", "C6LD", "C6LE", "C6LF", "C6LG", "C6LH", "C6LJ", "C6LK", "C6LL",
				"C4L", "C4RA", "C4RB", "C4RC", "C4RD", "C2R", "C2LA", "C2LB", "C2LC", "C2LD",
				"C10L", "C10R", "C12L", "C12R", "C22L", "C22R", "C24L", "C24R"],
			["C8L", "C8RA", "C8RB", "C8RC", "C8RD", "C8RE", "C8RF", "C8RG", "C8RH", "C8RJ", "C8RK", "C8RL",
				"C6R", "C6LA", "C6LB", "C6LC", "C6LD", "C6LE", "C6LF", "C6LG", "C6LH", "C6LJ", "C6LK", "C6LL",
				"C4L", "C4RA", "C4RB", "C4RC", "C4RD", "C2R", "C2LA", "C2LB", "C2LC", "C2LD",
				"C10L", "C10R", "C12L", "C12R"],
				[]
		]

		self.routeMap = {
			"CG21W": [["CSw41", "R"]],
			"CC10W": [["CSw41", "N"], ["CSw39", "N"]],
			"CC30W": [["CSw41", "N"], ["CSw39", "R"], ["CSw37", "R"]],
			"CC31W": [["CSw41", "N"], ["CSw39", "R"], ["CSw37", "N"]],

			"CG12E": [["CSw31", "R"], ["CSw35", "N"]],
			"CG10E": [["CSw31", "R"], ["CSw35", "R"]],
			"CC10E": [["CSw31", "N"], ["CSw33", "N"]],
			"CC30E": [["CSw31", "N"], ["CSw33", "R"]],

			"CC44E": [["CSw43", "N"], ["CSw45", "N"], ["CSw49", "N"]],
			"CC43E": [["CSw43", "N"], ["CSw45", "R"], ["CSw49", "R"]],
			"CC42E": [["CSw43", "R"], ["CSw45", "N"], ["CSw47", "N"], ["CSw51", "N"]],
			"CC41E": [["CSw43", "R"], ["CSw45", "N"], ["CSw47", "R"], ["CSw51", "R"]],
			"CC40E": [["CSw43", "R"], ["CSw45", "R"], ["CSw47", "N"], ["CSw51", "N"]],
			"CC21E": [["CSw43", "R"], ["CSw45", "R"], ["CSw47", "R"], ["CSw51", "R"], ["CSw63", "R"]],
			"CC50E": [["CSw43", "R"], ["CSw45", "R"], ["CSw47", "R"], ["CSw51", "R"], ["CSw63", "N"], ["CSw65", "R"]],
			"CC51E": [["CSw43", "R"], ["CSw45", "R"], ["CSw47", "R"], ["CSw51", "R"], ["CSw63", "N"], ["CSw65", "N"],
						["CSw67", "R"], ["CSw69", "N"]],
			"CC52E": [["CSw43", "R"], ["CSw45", "R"], ["CSw47", "R"], ["CSw51", "R"], ["CSw63", "N"], ["CSw65", "N"],
						["CSw67", "R"], ["CSw69", "R"]],
			"CC53E": [["CSw43", "R"], ["CSw45", "R"], ["CSw47", "R"], ["CSw51", "R"], ["CSw63", "N"], ["CSw65", "N"],
						["CSw67", "N"], ["CSw71", "R"]],
			"CC54E": [["CSw43", "R"], ["CSw45", "R"], ["CSw47", "R"], ["CSw51", "R"], ["CSw63", "N"], ["CSw65", "N"],
						["CSw67", "N"], ["CSw71", "N"]],

			"CC44W": [["CSw57", "N"], ["CSw53", "R"], ["CSw55", "R"], ["CSw59", "N"], ["CSw61", "R"]],
			"CC43W": [["CSw57", "R"], ["CSw53", "N"], ["CSw55", "R"], ["CSw59", "N"], ["CSw61", "R"]],
			"CC42W": [["CSw53", "R"], ["CSw55", "N"], ["CSw59", "R"], ["CSw61", "R"]],
			"CC41W": [["CSw53", "N"], ["CSw55", "N"], ["CSw59", "R"], ["CSw61", "R"]],
			"CC40W": [["CSw55", "R"], ["CSw61", "N"]],
			"CC21W": [["CSw55", "N"], ["CSw61", "N"], ["CSw53", "R"], ["CSw73", "N"]],
			"CC50W": [["CSw55", "N"], ["CSw61", "N"], ["CSw53", "N"], ["CSw73", "R"], ["CSw75", "R"]],
			"CC51W": [["CSw55", "N"], ["CSw61", "N"], ["CSw53", "N"], ["CSw73", "R"], ["CSw75", "N"], ["CSw77", "R"],
						["CSw79", "N"]],
			"CC52W": [["CSw55", "N"], ["CSw61", "N"], ["CSw53", "N"], ["CSw73", "R"], ["CSw75", "N"], ["CSw77", "R"],
						["CSw79", "R"]],
			"CC53W": [["CSw55", "N"], ["CSw61", "N"], ["CSw53", "N"], ["CSw73", "R"], ["CSw75", "N"], ["CSw77", "N"],
						 ["CSw79", "N"], ["CSw81", "R"]],
			"CC54W": [["CSw55", "N"], ["CSw61", "N"], ["CSw53", "N"], ["CSw73", "R"], ["CSw75", "N"], ["CSw77", "N"],
						["CSw79", "R"], ["CSw81", "N"]],
		}

		self.routeOSMap = {
			"CG21W": "COSGWW",
			"CC10W": "COSGMW",
			"CC30W": "COSGMW",
			"CC31W": "COSGMW",

			"CG12E": "COSGME",
			"CG10E": "COSGME",
			"CC10E": "COSGME",
			"CC30E": "COSGME",

			"CC44E": "COSSHE",
			"CC43E": "COSSHE",
			"CC42E": "COSSHE",
			"CC41E": "COSSHE",
			"CC40E": "COSSHE",
			"CC21E": "COSSHE",
			"CC50E": "COSSHE",
			"CC51E": "COSSHE",
			"CC52E": "COSSHE",
			"CC53E": "COSSHE",
			"CC54E": "COSSHE",

			"CC44W": "COSSHW",
			"CC43W": "COSSHW",
			"CC42W": "COSSHW",
			"CC41W": "COSSHW",
			"CC40W": "COSSHW",
			"CC21W": "COSSHW",
			"CC50W": "COSSHW",
			"CC51W": "COSSHW",
			"CC52W": "COSSHW",
			"CC53W": "COSSHW",
			"CC54W": "COSSHW",
		}

		self.routeGroups = [
			["CG21W", "CC10W", "CC30W", "CC31W"],
			["CG12E", "CG10E", "CC10E", "CC30E"],
			["CC44W", "CC43W", "CC42W", "CC41W", "CC40W", "CC21W", "CC50W", "CC51W", "CC52W", "CC53W", "CC54W"],
			["CC44E", "CC43E", "CC42E", "CC41E", "CC40E", "CC21E", "CC50E", "CC51E", "CC52E", "CC53E", "CC54E"]
		]

		nxButtons = [
			"CG21W", "CC10W", "CC30W", "CC31W",
			"CG12E", "CG10E", "CC10E", "CC30E",
			"CC44E", "CC43E", "CC42E", "CC41E", "CC40E", "CC21E", "CC50E", "CC51E", "CC52E", "CC53E", "CC54E",
			"CC44W", "CC43W", "CC42W", "CC41W", "CC40W", "CC21W", "CC50W", "CC51W", "CC52W", "CC53W", "CC54W",
		]

	def Locale(self):
		return "cliff"

	def PressButton(self, btn):
		self.rr.SetRouteIn(btn.Name())
		
	def SelectRouteIn(self, rt):
		rtnm = rt.Name()
		
		for gp in self.routeGroups:
			if rtnm in gp:
				return [x for x in gp if x != rtnm]
			
		return None
	
	def GetRouteInMsg(self, rt):
		rtNm = rt.Name()
		try:
			tolist = self.routeMap[rtNm]
		except KeyError:
			return None
		
		msg = {"turnout": [{"name": x[0], "state": x[1]} for x in tolist] }
		return msg
			
	def RouteIn(self, rt, stat, turnouts):
		rt.SetState(stat)
		rtNm = rt.Name()
		if stat == 0:
			return None

		try:
			tolist = self.routeMap[rtNm]
		except KeyError:
			return	None

		try:
			osName = self.routeOSMap[rtNm]
		except KeyError:
			return None

		# make sure all of the turnouts we need are available
		for toName, _ in tolist:
			tout = self.rr.GetTurnout(toName)
			if not tout:
				return None
			if tout.IsLocked() or tout.IsDisabled():
				self.rr.Alert("Route %s not allowed" % rtNm)
				return None

		for toName, state in tolist:
			tout = self.rr.GetTurnout(toName)
			if tout:
				tout.SetNormal(state == "N")

		msgs = []
		for tn, state in tolist:
			turnouts[tn].SetNormal(state == 'N')
			msgs.extend(turnouts[tn].GetEventMessages())

		for m in msgs:
			self.rr.RailroadEvent(m)

		return osName

	def EvaluateNXButton(self, btn):
		if btn not in self.routeMap:
			return

		tolist = self.routeMap[btn]

		for toName, status in tolist:
			self.rr.GetInput(toName).SetState(status)
			
	def CheckTurnoutPosition(self, tout):
		self.rr.RailroadEvent({"turnout": [{"name": tout.Name(), "state": "N" if tout.IsNormal() else "R"}]})

	def SetHandswitchIn(self, hs, state):
		hsname = hs.Name()
		if hsname == "CSw21ab":
			hsa = self.rr.GetHandswitch("CSw21a")
			if hsa.Unlock(state != 0):
				self.rr.RailroadEvent(hsa.GetEventMessage(lock=True))
				
			hsb = self.rr.GetHandswitch("CSw21b")
			if hsb.Unlock(state != 0):
				self.rr.RailroadEvent(hsb.GetEventMessage(lock=True))

	def UpdateControlOption(self):
		self.lastControl = self.control
		self.control = self.rr.GetControlOption("cliff")  # 0 => Cliff, 1 => Dispatcher bank/cliveden, 2 => Dispatcher All

	def OutIn(self):
		if self.control in [ 0, 1 ]:
			optFleet = self.nodes[CLIFF].GetInputBit(5, 1)
			if self.control == 1:
				optBankFleet = self.rr.GetControlOption("bank.fleet")  # 0 => no fleeting, 1 => fleeting
				optClivedenFleet = self.rr.GetControlOption("bank.fleet")  # 0 => no fleeting, 1 => fleeting
			else:
				optBankFleet = 0
				optClivedenFleet = 0
		else:
			optBankFleet = self.rr.GetControlOption("bank.fleet")  # 0 => no fleeting, 1 => fleeting
			optClivedenFleet = self.rr.GetControlOption("bank.fleet")  # 0 => no fleeting, 1 => fleeting
			optFleet = self.rr.GetControlOption("cliff.fleet")  # 0 => no fleeting, 1 => fleeting
						
		dispatchList = self.fleetedSignalsCliff[self.control]
		if optFleet != self.optFleet:
			self.optFleet = optFleet
			self.nodes[CLIFF].SetOutputBit(2, 5, 1-optFleet)   # fleet indicator
			self.nodes[CLIFF].SetOutputBit(2, 6, optFleet)   # fleet indicator
			if self.control in [0, 1]:  # the only control options that have local fleeting ability
				for signame in dispatchList:
					self.rr.RailroadEvent({"fleet": [{"name": signame, "value": optFleet}]})

		rlReq = self.nodes[CLIFF].GetInputBit(6, 3)
			
		ossLocks = self.rr.GetControlOption("osslocks") == 1

		# release controls if requested by operator or if osslocks are turned off by dispatcher			
		self.released = rlReq or not ossLocks
			
		self.rr.UpdateDistrictTurnoutLocks(self.name, self.released)
		
		District.OutIn(self)
		
	def Released(self, _):
		return self.released

	def GetControlOption(self, reset=True):
		"""
		skiplist is a list of objects that we ignore from the physical control panel beacuse of control settings
		resumelist is a list of things we had been ignoring but which now come into play
		"""
		if self.control == 2: # Dispatcher ALL
			skiplist = ["C2", "C4", "C6", "C8", "C10", "C12", "C14", "C18", "C22", "C24",
					"CSw3", "CSw9", "CSw11", "CSw15", "CSw19", "CSw21a", "CSw21b", "CSw21ab", "CSw23"]
			resumelist = []
			
		elif self.control == 1: # dispatcher runs bank/c13
			skiplist = ["C14", "C18", "C22", "C24", "CSw11", "CSw15", "CSw19", "CSw21a", "CSw21b", "CSw21ab"]
			if self.lastControl == 2:
				resumelist = ["C2", "C4", "C6", "C8", "C10", "C12", "CSw3", "CSw9"]
			elif self.lastControl == 0:
				resumelist = []
			else:
				resumelist = []
				
		else:
			skiplist = []
			if self.lastControl == 2:
				resumelist = ["C2", "C4", "C6", "C8", "C10", "C12", "C14", "C18", "C22", "C24",
					"CSw3", "CSw9", "CSw11", "CSw15", "CSw19", "CSw21a", "CSw21b", "CSw21ab"]
			elif self.lastControl == 1:
				resumelist = ["C10", "C12", "C14", "C18", "C22", "C24", "CSw9", "CSw11", "CSw15", "CSw19", "CSw21a", "CSw21b", "CSw21ab"]
			else:
				resumelist= []

		if reset:
			self.lastControl = self.control
		return skiplist, resumelist

	def ControlRestrictedMessage(self):
		if self.control == 0:
			return "Cliff Control is Local"
		elif self.control == 1:
			return "Dispatcher controls main Bank/Cliveden"
		else:
			return "Dispatcher controls Cliff Tower"
