import logging

from rrserver.district import District
from rrserver.constants import  NASSAUW, NASSAUE, NASSAUNX
from rrserver.node import Node

class Nassau(District):
	def __init__(self, rr, name, settings):
		District.__init__(self, rr, name, settings)
		self.rr = rr
		self.name = name
		self.nodeAddresses = [ NASSAUW, NASSAUE, NASSAUNX ]
		
		self.nodes = {
			NASSAUW:   Node(self, rr, NASSAUW,  8, settings),
			NASSAUE:   Node(self, rr, NASSAUE,  4, settings),
			NASSAUNX:  Node(self, rr, NASSAUNX, 3, settings, incount=0)
		}
		self.S11AB = None
		self.entryButton = None
		self.currentCoachRoute = None
		self.fleetPanel = None
		self.fleetDispatch = None
		self.released = False
		self.control = 2

		addr = NASSAUW
		with self.nodes[addr] as n:
			self.rr.AddSignal("N14LC", self, n, addr,[(0, 0)])
			self.rr.AddSignal("N14LB", self, n, addr,[(0, 1)])
			self.rr.AddSignal("N20R",  self, n, addr,[(0, 2)])
			self.rr.AddSignal("N20L",  self, n, addr,[(0, 3)])
			self.rr.AddSignal("N14LA", self, n, addr,[(0, 4), (0, 5)])
			self.rr.AddSignal("N16L",  self, n, addr,[(0, 6), (0, 7)])
			self.rr.AddSignal("N18LB", self, n, addr,[(1, 0), (1, 1)])
			self.rr.AddSignal("N18LA", self, n, addr,[(1, 2), (1, 3)])
			self.rr.AddSignal("N16R",  self, n, addr,[(1, 4), (1, 5)])
			self.rr.AddSignal("N14R",  self, n, addr,[(1, 6), (7, 3)]) # Transferred to byte 7:3: 1:7 bad bit
			self.rr.AddSignal("N18R",  self, n, addr,[(2, 0)])
			self.rr.AddSignal("N11W",  self, n, addr,[(2, 1), (2, 2), (2, 3)])
			self.rr.AddSignal("N21W",  self, n, addr,[(2, 4), (2, 5), (2, 6)])

			self.rr.AddIndicator("S11AB", self, n, addr, [(2, 7)]) # Shore approach indicator
			self.rr.AddBlockInd("R10",    self, n, addr, [(3, 0)]) # Shore approach indicator
			self.rr.AddBlockInd("B20",    self, n, addr, [(3, 1)]) # Bank approach indicator

			self.rr.AddIndicator("NFleet",  self, n, addr, [(3, 2)])
			self.rr.AddIndicator("nNFleet", self, n, addr, [(3, 3)]) # negated nassau fleet

			self.rr.AddSignalLED("N14",  self, n, addr, [(3, 6), (3, 5), (3, 4)])
			self.rr.AddSignalLED("N16",  self, n, addr, [(4, 1), (4, 0), (3, 7)])
			self.rr.AddSignalLED("N18",  self, n, addr, [(4, 4), (4, 3), (4, 2)])
			self.rr.AddSignalLED("N20",  self, n, addr, [(4, 7), (4, 6), (4, 5)])
			
			self.rr.AddTurnout("KSw1", self, n, addr, [(5, 0), (5, 1)])
			self.rr.AddTurnout("KSw3", self, n, addr, [(5, 2), (5, 3)])
			self.rr.AddTurnoutPair("KSw3", "KSw3b")
			self.rr.AddTurnout("KSw5", self, n, addr, [(5, 4), (5, 5)])
			self.rr.AddTurnoutPair("KSw5", "KSw5b")
			self.rr.AddTurnout("KSw7", self, n, addr, [(5, 6), (5, 7)])

			self.rr.AddBreakerInd("CBKrulish", self, n, addr, [(6, 0)])
			self.rr.AddBreakerInd("CBNassauW", self, n, addr, [(6, 1)])
			self.rr.AddBreakerInd("CBNassauE", self, n, addr, [(6, 2)])
			self.rr.AddBreakerInd("CBSouthportJct",  self, n, addr, [(6, 3)])
			self.rr.AddBreakerInd("CBWilson",  self, n, addr, [(6, 4)])
			self.rr.AddBreakerInd("CBThomas",  self, n, addr, [(6, 5)])
			
			self.rr.AddLock("NWSL0", self, n, addr, [(6, 6)]) # switch locks west
			self.rr.AddLock("NWSL1", self, n, addr, [(6, 7)])
			self.rr.AddLock("NWSL2", self, n, addr, [(7, 0)])
			self.rr.AddLock("NWSL3", self, n, addr, [(7, 1)])

			self.rr.AddStopRelay("N21.srel", self, n, addr, [(7, 2)])
			# Bit 7:3 used for signal N14R above
			
			self.rr.AddSignal("N14LD", self, n, addr, [(7, 4)])
			self.rr.AddSignal("N24RD", self, n, addr, [(7, 5)])

			# virtual turnouts - no output bits
			self.rr.AddTurnout("NSw19", self, n, addr, [])
			self.rr.AddTurnoutPair("NSw19", "NSw19b")
			self.rr.AddTurnout("NSw21", self, n, addr, [])	
			self.rr.AddTurnout("NSw23", self, n, addr, [])	
			self.rr.AddTurnout("NSw25", self, n, addr, [])
			self.rr.AddTurnoutPair("NSw25", "NSw25b")
			self.rr.AddTurnout("NSw27", self, n, addr, [])	
			self.rr.AddTurnout("NSw29", self, n, addr, [])	
			self.rr.AddTurnout("NSw31", self, n, addr, [])	
			self.rr.AddTurnout("NSw33", self, n, addr, [])
			self.rr.AddTurnout("NSw35", self, n, addr, [])
			self.rr.AddTurnout("NSw39", self, n, addr, [])
			
			# inputs	
			self.rr.AddTurnoutPosition("NSw19", self, n, addr, [(0, 0), (0, 1)])	
			self.rr.AddTurnoutPosition("NSw21", self, n, addr, [(0, 2), (0, 3)])	
			self.rr.AddTurnoutPosition("NSw23", self, n, addr, [(0, 4), (0, 5)])	
			self.rr.AddTurnoutPosition("NSw25", self, n, addr, [(0, 6), (0, 7)])	
			self.rr.AddTurnoutPosition("NSw27", self, n, addr, [(1, 0), (1, 1)])	
			self.rr.AddTurnoutPosition("NSw29", self, n, addr, [(1, 2), (1, 3)])	
			self.rr.AddTurnoutPosition("NSw31", self, n, addr, [(1, 4), (1, 5)])	
			self.rr.AddTurnoutPosition("NSw33", self, n, addr, [(1, 6), (1, 7)])	
	
			self.rr.AddBlock("N21.W",   self, n, addr, [(2, 0)], True)
			self.rr.AddBlock("N21",     self, n, addr, [(2, 1)], True)
			self.rr.AddBlock("N21.E",   self, n, addr, [(2, 2)], True)
			self.rr.AddBlock("NWOSTY",  self, n, addr, [(2, 3)], False)
			self.rr.AddBlock("NWOSCY",  self, n, addr, [(2, 4)], False)
			self.rr.AddBlock("NWOSW",   self, n, addr, [(2, 5)], False)
			self.rr.AddBlock("NWOSE",   self, n, addr, [(2, 6)], True)
			self.rr.AddBlock("N32",     self, n, addr, [(2, 7)], False)
			self.rr.AddBlock("N31",     self, n, addr, [(3, 0)], False)
			self.rr.AddBlock("N12",     self, n, addr, [(3, 1)], False)
	
			self.rr.AddSignalLever("N14",  self, n, addr, [(3, 4), (3, 5), (3, 6)])
			self.rr.AddSignalLever("N16",  self, n, addr, [(3, 7), (4, 0), (4, 1)])
			self.rr.AddSignalLever("N18",  self, n, addr, [(4, 2), (4, 3), (4, 4)])
			self.rr.AddSignalLever("N20",  self, n, addr, [(4, 5), (4, 6), (4, 7)])
			self.rr.AddSignalLever("N24",  self, n, addr, [(5, 0), (5, 1), (5, 2)])
			self.rr.AddSignalLever("N26",  self, n, addr, [(5, 3), (5, 4), (5, 5)])
			self.rr.AddSignalLever("N28",  self, n, addr, [(5, 6), (5, 7), (6, 0)])

			self.rr.AddBreaker("CBKrulishYd", self, n, addr, [(6, 1)])	
			self.rr.AddBreaker("CBThomas", self, n, addr, [(6, 2)])	
			self.rr.AddBreaker("CBWilson", self, n, addr, [(6, 3)])	
			self.rr.AddBreaker("CBKrulish", self, n, addr, [(6, 4)])	
			self.rr.AddBreaker("CBNassauW", self, n, addr, [(6, 5)])	
			self.rr.AddBreaker("CBNassauE", self, n, addr, [(6, 6)])	
			self.rr.AddBreaker("CBFoss", self, n, addr, [(6, 7)])	
			self.rr.AddBreaker("CBDell", self, n, addr, [(7, 0)])	

			self.rr.AddRouteIn("NSw60A", self, n, addr, [(7, 1)])
			self.rr.AddRouteIn("NSw60B", self, n, addr, [(7, 2)])
			self.rr.AddRouteIn("NSw60C", self, n, addr, [(7, 3)])
			self.rr.AddRouteIn("NSw60D", self, n, addr, [(7, 4)])
				
			self.rr.AddTurnoutPosition("NSw35", self, n, addr, [(7, 5), (7, 6)])	
			
			# virtual blocks - have no detection
			self.rr.AddBlock("T12",     self, n, addr, [], False)
			self.rr.AddBlock("W10",     self, n, addr, [], False)
			self.rr.AddBlock("W11",     self, n, addr, [], False)
			self.rr.AddBlock("W20",     self, n, addr, [], True)
			self.rr.AddBlock("N60",     self, n, addr, [], True)

		addr = NASSAUE
		with self.nodes[addr] as n:
			# outputs
			self.rr.AddSignal("N24RB",  self, n, addr, [(0, 0), (0, 1)])
			self.rr.AddSignal("N24RC",  self, n, addr, [(0, 2), (0, 3)])
			self.rr.AddSignal("N26RC",  self, n, addr, [(0, 4), (0, 5)])
			self.rr.AddSignal("N24RA",  self, n, addr, [(0, 6), (0, 7)])
			self.rr.AddSignal("N26RA",  self, n, addr, [(1, 0)])
			self.rr.AddSignal("N26RB",  self, n, addr, [(1, 1)])
			self.rr.AddSignal("N28R",   self, n, addr, [(1, 2)])
			self.rr.AddSignal("B20E",   self, n, addr, [(1, 3), (1, 4), (1, 5)])
			self.rr.AddSignal("N24L",   self, n, addr, [(1, 6)])
			self.rr.AddSignal("N26L",   self, n, addr, [(1, 7), (2, 0)])
			self.rr.AddSignal("N28L",   self, n, addr, [(2, 1), (2, 2)])
			
			self.rr.AddLock("NESL0", self, n, addr, [(2, 3)]) # switch locks east
			self.rr.AddLock("NESL1", self, n, addr, [(2, 4)])
			self.rr.AddLock("NESL2", self, n, addr, [(2, 5)])
			
			self.rr.AddStopRelay("B10.srel", self, n, addr, [(2, 6)])
			
			self.rr.AddSignalLED("N24",  self, n, addr, [(3, 1), (3, 0), (2, 7)])
			self.rr.AddSignalLED("N26",  self, n, addr, [(3, 4), (3, 3), (3, 2)])
			self.rr.AddSignalLED("N28",  self, n, addr, [(3, 7), (3, 6), (3, 5)])
			
			# virtual turnouts - no output bits
			self.rr.AddTurnout("NSw41", self, n, addr, [])	
			self.rr.AddTurnout("NSw43", self, n, addr, [])	
			self.rr.AddTurnout("NSw45", self, n, addr, [])	
			self.rr.AddTurnout("NSw47", self, n, addr, [])	
			self.rr.AddTurnout("NSw51", self, n, addr, [])	
			self.rr.AddTurnout("NSw53", self, n, addr, [])	
			self.rr.AddTurnout("NSw55", self, n, addr, [])	
			self.rr.AddTurnoutPair("NSw55", "NSw55b")
			self.rr.AddTurnout("NSw57", self, n, addr, [])
			self.rr.AddTurnoutPair("NSw57", "NSw57b")

			# inputs
			self.rr.AddTurnoutPosition("NSw41", self, n, addr, [(0, 0), (3, 2)]) # bit 0,1 is bad
			self.rr.AddTurnoutPosition("NSw43", self, n, addr, [(0, 2), (0, 3)])	
			self.rr.AddTurnoutPosition("NSw45", self, n, addr, [(0, 4), (0, 5)])	
			self.rr.AddTurnoutPosition("NSw47", self, n, addr, [(0, 6), (0, 7)])	
			self.rr.AddTurnoutPosition("NSw51", self, n, addr, [(3, 3), (1, 1)]) # bit 1,0 is bad	
			self.rr.AddTurnoutPosition("NSw53", self, n, addr, [(1, 2), (1, 3)])	
			self.rr.AddTurnoutPosition("NSw55", self, n, addr, [(1, 4), (1, 5)])	
			self.rr.AddTurnoutPosition("NSw57", self, n, addr, [(1, 6), (1, 7)])	
	
			self.rr.AddBlock("N22",     self, n, addr, [(2, 0)], True)
			self.rr.AddBlock("N41",     self, n, addr, [(2, 1)], True)
			self.rr.AddBlock("N42",     self, n, addr, [(2, 2)], True)
			self.rr.AddBlock("NEOSRH",  self, n, addr, [(2, 3)], False)
			self.rr.AddBlock("NEOSW",   self, n, addr, [(2, 4)], False)
			self.rr.AddBlock("NEOSE",   self, n, addr, [(2, 5)], True)
			sbw = self.rr.AddBlock("B10.W",   self, n, addr, [(2, 6)], False)
			b = self.rr.AddBlock("B10",     self, n, addr, [(2, 7)], False)
			b.AddStoppingBlocks([sbw])
	
			self.rr.AddTurnoutPosition("NSw39", self, n, addr, [(3, 0), (3, 1)])	
			
		addr = NASSAUNX
		with self.nodes[addr] as n:
			# outputs
			self.rr.AddOutNXButton("NNXBtnT12",  self, n, addr, [(0, 0)])
			self.rr.AddOutNXButton("NNXBtnN60",  self, n, addr, [(0, 1)])
			self.rr.AddOutNXButton("NNXBtnN11",  self, n, addr, [(0, 2)])
			self.rr.AddOutNXButton("NNXBtnN21",  self, n, addr, [(0, 3)])
			self.rr.AddOutNXButton("NNXBtnW10",  self, n, addr, [(0, 4)])
			self.rr.AddOutNXButton("NNXBtnN32W", self, n, addr, [(0, 5)])
			self.rr.AddOutNXButton("NNXBtnN31W", self, n, addr, [(0, 6)])
			self.rr.AddOutNXButton("NNXBtnN12W", self, n, addr, [(0, 7)])
			
			self.rr.AddOutNXButton("NNXBtnN22W", self, n, addr, [(1, 0)])
			self.rr.AddOutNXButton("NNXBtnN41W", self, n, addr, [(1, 1)])
			self.rr.AddOutNXButton("NNXBtnN42W", self, n, addr, [(1, 2)])
			self.rr.AddOutNXButton("NNXBtnW20W", self, n, addr, [(1, 3)])
			self.rr.AddOutNXButton("NNXBtnW11",  self, n, addr, [(1, 4)])
			self.rr.AddOutNXButton("NNXBtnN32E", self, n, addr, [(1, 5)])
			self.rr.AddOutNXButton("NNXBtnN31E", self, n, addr, [(1, 6)])
			self.rr.AddOutNXButton("NNXBtnN12E", self, n, addr, [(1, 7)])
				
			self.rr.AddOutNXButton("NNXBtnN22E", self, n, addr, [(2, 0)])
			self.rr.AddOutNXButton("NNXBtnN41E", self, n, addr, [(2, 1)])
			self.rr.AddOutNXButton("NNXBtnN42E", self, n, addr, [(2, 2)])
			self.rr.AddOutNXButton("NNXBtnW20E", self, n, addr, [(2, 3)])
			self.rr.AddOutNXButton("NNXBtnR10",  self, n, addr, [(2, 4)])
			self.rr.AddOutNXButton("NNXBtnB10", self, n, addr, [(2, 5)])
			self.rr.AddOutNXButton("NNXBtnB20", self, n, addr, [(2, 6)])
			
			#inputs - none
			
		self.coachRoutes = ["NSw60A", "NSw60B", "NSw60C", "NSw60D"]
		
		'''
		which signals are affected by fleeting, for each of the control options
		This indicates the effect for the dispatcher program.
		
		0 => Nassau, 1 => Dispatcher Main, 2 => Dispatcher All
		'''
		self.fleetedSignals = [
			[],
			["N26L", "N26RB", "N26RC", "N24L", "N24RA", "N24RB", "N14R", "N14LA", "N14LB", "N16R", "N16L", "N18LB"],
			["N26L", "N26RA", "N26RB", "N26RC", "N24L", "N24RA", "N24RB", "N24RC", "N24RD", 
				"N14R", "N14LA", "N14LB", "N14LC", "N14LD", "N16R", "N16L", 
				"N18R", "N18LA", "N18LB", "N20R", "N20L", "N28R", "N28L"]
		]

		self.routeMap = {
			"NSw60A": [["NSw13", "N"], ["NSw15", "R"], ["NSw17", "R"]],
			"NSw60B": [["NSw13", "R"], ["NSw15", "N"], ["NSw17", "R"]],
			"NSw60C": [["NSw13", "N"], ["NSw15", "R"], ["NSw17", "N"]],
			"NSw60D": [["NSw13", "R"], ["NSw15", "N"], ["NSw17", "N"]]
		}

		self.routeOSMap = {
			"NSw60A": "NWOSCY",
			"NSw60B": "NWOSCY",
			"NSw60C": "NWOSCY",
			"NSw60D": "NWOSCY",
		}

		self.NXMap = {
			"NNXBtnT12": {
				"NNXBtnW10":  [ ["NSw25", "N"] ]
			},

			"NNXBtnN60": {
				"NNXBtnW10":  [ ["NSw21", "N"], ["NSw23", "R"], ["NSw25", "R"], ["NSw27", "N"] ],
				"NNXBtnN32W": [ ["NSw21", "N"], ["NSw23", "R"], ["NSw25", "N"], ["NSw27", "N"] ],
				"NNXBtnN31W": [ ["NSw21", "N"], ["NSw23", "N"], ["NSw27", "N"] ],
				"NNXBtnN12W": [ ["NSw21", "N"], ["NSw27", "R"], ["NSw29", "N"] ],
				"NNXBtnN22W": [ ["NSw27", "R"], ["NSw29", "R"], ["NSw31", "N"] ],
				"NNXBtnN41W": [ ["NSw27", "R"], ["NSw29", "R"], ["NSw31", "R"], ["NSw33", "R"] ],
				"NNXBtnN42W": [ ["NSw27", "R"], ["NSw29", "R"], ["NSw31", "R"], ["NSw33", "N"], ["NSw35", "R"] ],
				"NNXBtnW20W": [ ["NSw27", "R"], ["NSw29", "R"], ["NSw31", "R"], ["NSw33", "N"], ["NSw35", "N"] ],
			},

			"NNXBtnN11": {
				"NNXBtnW10":  [ ["NSw19", "N"], ["NSw21", "R"], ["NSw23", "R"], ["NSw25", "R"], ["NSw27", "N"], ["NSw29", "N"] ],
				"NNXBtnN32W": [ ["NSw19", "N"], ["NSw21", "R"], ["NSw23", "R"], ["NSw25", "N"], ["NSw27", "N"], ["NSw29", "N"] ],
				"NNXBtnN31W": [ ["NSw19", "N"], ["NSw21", "R"], ["NSw23", "N"], ["NSw27", "N"], ["NSw29", "N"] ],
				"NNXBtnN12W": [ ["NSw19", "N"], ["NSw21", "N"], ["NSw27", "N"], ["NSw29", "N"] ],
				"NNXBtnN22W": [ ["NSw19", "N"], ["NSw27", "N"], ["NSw29", "R"], ["NSw31", "N"] ],
				"NNXBtnN41W": [ ["NSw19", "N"], ["NSw27", "N"], ["NSw29", "R"], ["NSw31", "R"], ["NSw33", "R"] ],
				"NNXBtnN42W": [ ["NSw19", "N"], ["NSw27", "N"], ["NSw29", "R"], ["NSw31", "R"], ["NSw33", "N"], ["NSw35", "R"] ],
				"NNXBtnW20W": [ ["NSw19", "N"], ["NSw27", "N"], ["NSw29", "R"], ["NSw31", "R"], ["NSw33", "N"], ["NSw35", "N"] ],
			},

			"NNXBtnN21": {
				"NNXBtnW10":  [ ["NSw19", "R"], ["NSw21", "R"], ["NSw23", "R"], ["NSw25", "R"], ["NSw27", "N"], ["NSw29", "N"] ],
				"NNXBtnN32W": [ ["NSw19", "R"], ["NSw21", "R"], ["NSw23", "R"], ["NSw25", "N"], ["NSw27", "N"], ["NSw29", "N"] ],
				"NNXBtnN31W": [ ["NSw19", "R"], ["NSw21", "R"], ["NSw23", "N"], ["NSw27", "N"], ["NSw29", "N"] ],
				"NNXBtnN12W": [ ["NSw19", "R"], ["NSw21", "N"], ["NSw27", "N"], ["NSw29", "N"] ],
				"NNXBtnN22W": [ ["NSw19", "N"], ["NSw29", "N"], ["NSw31", "N"] ],
				"NNXBtnN41W": [ ["NSw19", "N"], ["NSw29", "N"], ["NSw31", "R"], ["NSw33", "R"] ],
				"NNXBtnN42W": [ ["NSw19", "N"], ["NSw29", "N"], ["NSw31", "R"], ["NSw33", "N"], ["NSw35", "R"] ],
				"NNXBtnW20W": [ ["NSw19", "N"], ["NSw29", "N"], ["NSw31", "R"], ["NSw33", "N"], ["NSw35", "N"] ],
			},
			"NNXBtnR10": {
				"NNXBtnW11":  [ ["NSw47", "N"], ["NSw55", "N"] ],
				"NNXBtnN32E": [ ["NSw51", "N"], ["NSw53", "R"], ["NSw55", "N"], ["NSw45", "N"], ["NSw47", "R"] ],
				"NNXBtnN31E": [ ["NSw51", "R"], ["NSw53", "R"], ["NSw55", "N"], ["NSw45", "N"], ["NSw47", "R"] ],
				"NNXBtnN12E": [ ["NSw53", "N"], ["NSw55", "N"], ["NSw45", "N"], ["NSw47", "R"] ],
				"NNXBtnN22E": [ ["NSw43", "N"], ["NSw45", "R"], ["NSw47", "R"] ],
				"NNXBtnN41E": [ ["NSw41", "R"], ["NSw43", "R"], ["NSw45", "R"], ["NSw47", "R"] ],
				"NNXBtnN42E": [ ["NSw39", "R"], ["NSw41", "N"], ["NSw43", "R"], ["NSw45", "R"], ["NSw47", "R"] ],
				"NNXBtnW20E": [ ["NSw39", "N"], ["NSw41", "N"], ["NSw43", "R"], ["NSw45", "R"], ["NSw47", "R"] ]
			}, 
			
			"NNXBtnB10": {
				"NNXBtnW11":  [ ["NSw55", "R"], ["NSw45", "N"], ["NSw47", "N"], ["NSw57", "N"] ],
				"NNXBtnN32E": [ ["NSw51", "N"], ["NSw53", "R"], ["NSw55", "N"], ["NSw45", "N"], ["NSw47", "N"], ["NSw57", "N"] ],
				"NNXBtnN31E": [ ["NSw51", "R"], ["NSw53", "R"], ["NSw55", "N"], ["NSw45", "N"], ["NSw47", "N"], ["NSw57", "N"] ],
				"NNXBtnN12E": [ ["NSw53", "N"], ["NSw55", "N"], ["NSw45", "N"], ["NSw47", "N"], ["NSw57", "N"] ],
				"NNXBtnN22E": [ ["NSw43", "N"], ["NSw45", "R"], ["NSw47", "N"], ["NSw57", "N"] ],
				"NNXBtnN41E": [ ["NSw41", "R"], ["NSw43", "R"], ["NSw45", "R"], ["NSw47", "N"], ["NSw57", "N"]],
				"NNXBtnN42E": [ ["NSw39", "R"], ["NSw41", "N"], ["NSw43", "R"], ["NSw45", "R"], ["NSw47", "N"], ["NSw57", "N"] ],
				"NNXBtnW20E": [ ["NSw39", "N"], ["NSw41", "N"], ["NSw43", "R"], ["NSw45", "R"], ["NSw47", "N"], ["NSw57", "N"] ]
			}, 
			
			"NNXBtnB20": {
				"NNXBtnW11":  [ ["NSw55", "R"], ["NSw45", "N"], ["NSw47", "N"], ["NSw57", "R"] ],
				"NNXBtnN32E": [ ["NSw51", "N"], ["NSw53", "R"], ["NSw55", "N"], ["NSw45", "N"], ["NSw47", "N"], ["NSw57", "R"]],
				"NNXBtnN31E": [ ["NSw51", "R"], ["NSw53", "R"], ["NSw55", "N"], ["NSw45", "N"], ["NSw47", "N"], ["NSw57", "R"]],
				"NNXBtnN12E": [ ["NSw53", "N"], ["NSw55", "N"], ["NSw45", "N"], ["NSw47", "N"], ["NSw57", "R"] ],
				"NNXBtnN22E": [ ["NSw43", "N"], ["NSw45", "N"], ["NSw57", "N"] ],
				"NNXBtnN41E": [ ["NSw41", "R"], ["NSw43", "R"], ["NSw45", "N"], ["NSw57", "N"] ],
				"NNXBtnN42E": [ ["NSw39", "R"], ["NSw41", "N"], ["NSw43", "R"], ["NSw45", "N"], ["NSw57", "N"] ],
				"NNXBtnW20E": [ ["NSw39", "N"], ["NSw41", "N"], ["NSw43", "R"], ["NSw45", "N"], ["NSw57", "N"] ]
			}

		}

		self.leverToSignals = {
			"N14": [["N14LA", "N14LB", "N14LC"], ["N14R"]],
			"N16": [["N16L"], ["N16R"]],
			"N18": [["N18LA", "N18LB"], ["N18R"]],
			"N20": [["N20L"], ["N20R"]],
			"N24": [["N24L"], ["N24RA", "N24RB", "N24RC", "N24RD"]],
			"N26": [["N26L"], ["N26RA", "N26RB", "N26RC"]],
			"N28": [["N28L"], ["N28R"]]
		}

	def MapLeverToSignals(self, lever):
		try:
			return self.leverToSignals[lever][0], self.leverToSignals[lever][1]
		except KeyError:
			return [], []









	def PressButton(self, btn):
		'''
		this is only called when in simulation - it turns the outbount button push
		into a series of turnout position input bits
		'''
		if self.entryButton is None:
			self.entryButton = btn
			return 
		
		tolist = self.EvaluateNXButtons(self.entryButton.Name(), btn.Name())
		for toName, status in tolist:
			tout = self.rr.GetTurnout(toName)
			pos = tout.Position()
			if pos is None:
				logging.warning("Skipping unknown turnout %s in NX button route" % toName)
			else:
				Nval = 0 if status == "R" else 1
				Rval = 1 if status == "R" else 0
				bits, district, node, addr = pos
				node.SetInputBit(bits[0][0], bits[0][1], Nval)
				node.SetInputBit(bits[1][0], bits[1][1], Rval)
			
		self.entryButton = None
		return 

	def EvaluateNXButtons(self, bEntry, bExit):
		try:
			tolist = self.NXMap[bEntry][bExit]
		except KeyError:
			try:
				tolist = self.NXMap[bExit][bEntry]
			except KeyError:
				return []
		
		return tolist
	
	def GetRouteInMsg(self, rt):
		if rt.Name() in self.coachRoutes:		
			return {"turnout": [{"name": x[0], "state": x[1]} for x in self.routeMap[rt.name]] }
		
		return None
	
	def SelectRouteIn(self, rt):
		if rt.Name() in self.coachRoutes:		
			offRtList = [x for x in self.coachRoutes if x != rt.Name()]
			return offRtList
		
		return None
	
	def RouteIn(self, rt, stat, turnouts):
		rt.SetState(stat)
		if stat == 1:
			if rt.name == self.currentCoachRoute:
				return None
			
			self.currentCoachRoute = rt.name

			for tn, state in self.routeMap[rt.name]:
				turnouts[tn].SetNormal(state == 'N')

			self.rr.RailroadEvent({"turnout": [{"name": x[0], "state": x[1]} for x in self.routeMap[rt.name]] })
			
		else:
			if rt.name == self.currentCoachRoute:
				self.currentCoachRoute = None
			return None

		return "NWOSCY"

	def ControlRestricted(self):
		if self.control == 0:
			return "Control is Local"
		elif self.control == 1:
			return "Dispatcher controls main line"
		else:
			return "Dispatcher controls Nassau Tower"

	def UpdateControlOption(self):
		self.lastControl = self.control
		self.control = self.rr.GetControlOption("nassau")  # 0 => Nassau, 1 => Dispatcher Main, 2 => Dispatcher All

	def OutIn(self):
		self.UpdateControlOption()
		if self.control in [0, 1]:
			fleetPanel = self.nodes[NASSAUW].GetInputBit(3, 3) # get the state of the lever on the panel
		else:
			fleetPanel = 0
			
		fleetDispatch = self.rr.GetControlOption("nassau.fleet")  # otherwise get the fleeting state from the check box

		dispatchList = self.fleetedSignals[self.control]
		panelList = [x for x in self.fleetedSignals[2] if x not in dispatchList]
		
		if self.control in [0, 1]: 
			if self.fleetPanel != fleetPanel:
				self.fleetPanel = fleetPanel
				self.nodes[NASSAUW].SetOutputBit(3, 2, fleetPanel)			
				self.nodes[NASSAUW].SetOutputBit(3, 3, 1-fleetPanel)
				for signame in panelList:
					self.rr.RailroadEvent({"fleet": [{"name": signame, "value": fleetPanel}]})

		if self.control in [1, 2]:
			if self.fleetDispatch != fleetDispatch:
				self.fleetDispatch = fleetDispatch
				if self.control == 2: # only update the panel LEDs if the panel has no local control
					self.nodes[NASSAUW].SetOutputBit(3, 2, fleetDispatch)			
					self.nodes[NASSAUW].SetOutputBit(3, 3, 1-fleetDispatch)
				for signame in dispatchList:
					self.rr.RailroadEvent({"fleet": [{"name": signame, "value": fleetDispatch}]})

		rlReq = self.nodes[NASSAUW].GetInputBit(3, 2) == 1
			
		ossLocks = self.rr.GetControlOption("osslocks") == 1

		# release controls if requested by operator or if osslocks are turned off by dispatcher			
		self.released = rlReq or not ossLocks

		NESL = self.rr.GetDistrictLock("NESL")
		NWSL = self.rr.GetDistrictLock("NWSL")
		if self.released:
			# don't set any switch locks if release button is being pressed
			NESL = [0 for _ in range(len(NESL))]
			NWSL = [0 for _ in range(len(NWSL))]
			if self.control == 1:  # Dispatcher Main only
				NESL[0] = 1
				NWSL[0] = 1
				
		for i in range(len(NESL)):
			lnm = "NESL%d" % i
			self.rr.SetLock(lnm, NESL[i])
				
		for i in range(len(NWSL)):
			lnm = "NWSL%d" % i
			self.rr.SetLock(lnm, NWSL[i])
		
		S11AB = self.rr.GetBlock("S11A").IsOccupied() or self.rr.GetBlock("S11B").IsOccupied()
		
		if S11AB != self.S11AB:
			self.S11AB = S11AB
			self.rr.SetIndicator("S11AB", S11AB)

		self.rr.UpdateDistrictTurnoutLocks(self.name, self.released)
		
		District.OutIn(self)
		
	def Released(self, _):
		return self.released
		
	def GetControlOption(self):
		if self.control == 2:  # dispatcher ALL control - ignore all signal levers
			skiplist = ["N14", "N16", "N18", "N24", "N26", "N20", "N28"]
			resumelist = []
			
		elif self.control == 1: # dispatcher MAIN control - ignore signal levers dealing with the main tracks		
			skiplist =  ["N14", "N16", "N18", "N24", "N26"]
			if self.lastControl == 2:
				resumelist = ["N20", "N28"]
			elif self.lastControl == 0:
				resumelist = []
			else:
				resumelist = []
				
		else:  # assume local control - ignore nothing
			skiplist = []
			if self.lastControl == 2:
				resumelist = ["N14", "N16", "N18", "N24", "N26", "N20", "N28"]
			elif self.lastControl == 1:
				resumelist = ["N14", "N16", "N18", "N24", "N26"]
			else:
				resumelist = []
				
		return skiplist, resumelist
