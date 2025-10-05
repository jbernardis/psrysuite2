import logging

from rrserver.district import District
from rrserver.constants import HYDE
from rrserver.node import Node

class Hyde(District):
	def __init__(self, rr, name, settings):
		District.__init__(self, rr, name, settings)
		self.rr = rr
		self.name = name
		self.released = False
		self.n25occ = None
		self.nodeAddresses = [ HYDE ]
		self.nodes = {
			HYDE:  Node(self, rr, HYDE,  5, settings)
		}

		# INPUTS
		routeNames = [ "H30E",
				"H31E", "H32E", "H33E", "H34E", "H12E", "H22E", "H43E", "H42E", "H41E", "H40E",
				"H31W", "H32W", "H33W", "H34W", "H12W", "H22W", "H43W", "H42W", "H41W"	]
		
		self.toPos = { # keep track of turnout positions - initially assume all normal
			"HSw1":  True,
			"HSw3":  True,
			"HSw5":  True, 
			"HSw7":  True, 
			"HSw9":  True,
			"HSw11": True,
			"HSw13": True, 
			"HSw15": True,
			"HSw17": True, 
			"HSw19": True,
			"HSw21": True, 
			"HSw23": True,
			"HSw25": True,
			"HSw27": True,
			"HSw29": True, 
		}

		self.routeMap = {
			"H12W": [["HSw1", "N"], ["HSw3", "N"], ["HSw5", "N"]],
			"H34W": [["HSw1", "N"], ["HSw3", "R"], ["HSw5", "R"]],
			"H33W": [["HSw1", "R"], ["HSw3", "N"], ["HSw5", "N"]],
			"H32W": [["HSw1", "R"], ["HSw3", "R"], ["HSw5", "R"], ["HSw7", "N"]],
			"H31W": [["HSw1", "R"], ["HSw3", "R"], ["HSw5", "R"], ["HSw7", "R"]],

			"H12E": [["HSw15", "N"], ["HSw17", "N"], ["HSw19", "N"], ["HSw21", "N"]],
			"H34E": [["HSw15", "R"], ["HSw17", "N"], ["HSw19", "N"], ["HSw21", "N"]],
			"H33E": [["HSw15", "N"], ["HSw17", "R"], ["HSw19", "N"], ["HSw21", "N"]],
			"H32E": [["HSw15", "N"], ["HSw17", "N"], ["HSw19", "R"], ["HSw21", "N"]],
			"H31E": [["HSw15", "N"], ["HSw17", "N"], ["HSw19", "N"], ["HSw21", "R"]],
			"H30E": [["HSw7", "N"]],

			"H22W": [["HSw9", "N"], ["HSw11", "N"], ["HSw13", "N"]],
			"H43W": [["HSw9", "N"], ["HSw11", "R"], ["HSw13", "R"]],
			"H42W": [["HSw9", "R"], ["HSw11", "N"], ["HSw13", "N"]],
			"H41W": [["HSw9", "R"], ["HSw11", "R"], ["HSw13", "R"]],

			"H22E": [["HSw23", "N"], ["HSw25", "N"], ["HSw27", "N"], ["HSw29", "N"]],
			"H43E": [["HSw23", "N"], ["HSw25", "R"], ["HSw27", "R"], ["HSw29", "N"]],
			"H42E": [["HSw23", "R"], ["HSw25", "N"], ["HSw27", "R"], ["HSw29", "N"]],
			"H41E": [["HSw23", "N"], ["HSw25", "N"], ["HSw27", "R"], ["HSw29", "N"]],
			"H40E": [["HSw23", "N"], ["HSw25", "N"], ["HSw27", "N"], ["HSw29", "R"]],
		}

		self.routeOSMap = {
			"H12W": "HOSWW",
			"H34W": "HOSWW",
			"H33W": "HOSWW",
			"H32W": "HOSWW",
			"H31W": "HOSWW",

			"H12E": "HOSEW",
			"H34E": "HOSEW",
			"H33E": "HOSEW",
			"H32E": "HOSEW",
			"H31E": "HOSEW",

			"H30E": "HOSWW2",

			"H22W": "HOSWE",
			"H43W": "HOSWE",
			"H42W": "HOSWE",
			"H41W": "HOSWE",

			"H22E": "HOSEE",
			"H43E": "HOSEE",
			"H42E": "HOSEE",
			"H41E": "HOSEE",
			"H40E": "HOSEE",
		}

		self.routeNeeded = {
				"H12W": [ ["HSw1", "N"], ["HSw3","N"] ], 
				"H34W": [ ["HSw1", "N"], ["HSw3", "R"] ],
				"H33W": [ ["HSw1", "R"], ["HSw5", "N"] ], 
				"H32W": [ ["HSw1", "R"], ["HSw5", "R"], ["HSw7","N"] ], 
				"H31W": [ ["HSw1", "R"], ["HSw5", "R"], ["HSw7","R"] ], 

				"H12E": [ ["HSw15", "N"], ["HSw17", "N"], ["HSw19", "N"], ["HSw21", "N"] ], 
				"H34E": [ ["HSw15", "R"], ["HSw17", "N"], ["HSw19", "N"], ["HSw21", "N"] ], 
				"H33E": [ ["HSw17", "R"], ["HSw19", "N"], ["HSw21", "N"] ], 
				"H32E": [ ["HSw19", "R"], ["HSw21", "N"] ], 
				"H31E": [ ["HSw21", "R"] ], 
				
				"H30E": [ ["HSw7", "N"] ],

				"H22W": [ ["HSw9", "N"], ["HSw11", "N"] ], 
				"H43W": [ ["HSw9", "N"], ["HSw11", "R"] ], 
				"H42W": [ ["HSw9", "R"], ["HSw13", "N"] ], 
				"H41W": [ ["HSw9", "R"], ["HSw13", "R"] ], 

				"H22E": [ ["HSw27", "N"], ["HSw29", "N"] ], 
				"H43E": [ ["HSw25", "R"], ["HSw27", "R"], ["HSw29", "N"] ], 
				"H42E": [ ["HSw23", "R"], ["HSw25", "N"], ["HSw27", "R"], ["HSw29", "N"] ], 
				"H41E": [ ["HSw23", "N"], ["HSw25", "N"], ["HSw27", "R"], ["HSw29", "N"] ], 
				"H40E": [ ["HSw29", "R"] ], 
		}
		
		self.routeGroups = [
			["H30E"],
			["H12W", "H34W", "H33W", "H32W", "H31W"],
			["H12E", "H34E", "H33E", "H32E", "H31E"],
			["H22W", "H43W", "H42W", "H41W"],
			["H22E", "H43E", "H42E", "H41E", "H40E"]
		]

		
		addr = HYDE
		with self.nodes[addr] as n:
			# outputs
			self.rr.AddTurnout("HSw1",  self, n, addr, [(0, 0), (0, 1)])
			self.rr.AddTurnout("HSw3",  self, n, addr, [(0, 2), (0, 3)])
			self.rr.AddTurnoutPair("HSw3", "HSw5")
			self.rr.AddTurnout("HSw7",  self, n, addr, [(0, 4), (0, 5)])
			self.rr.AddTurnoutPair("HSw7", "HSw7b")
			self.rr.AddTurnout("HSw9",  self, n, addr, [(0, 6), (0, 7)])
			self.rr.AddTurnout("HSw11", self, n, addr, [(1, 0), (1, 1)])
			self.rr.AddTurnoutPair("HSw11", "HSw13")
			self.rr.AddTurnout("HSw23", self, n, addr, [(1, 2), (1, 3)])
			self.rr.AddTurnout("HSw25", self, n, addr, [(1, 4), (1, 5)])
			self.rr.AddTurnout("HSw27", self, n, addr, [(1, 6), (1, 7)])
			self.rr.AddTurnout("HSw29", self, n, addr, [(2, 0), (2, 1)])
			self.rr.AddTurnout("HSw15", self, n, addr, [(2, 2), (2, 3)])
			self.rr.AddTurnout("HSw17", self, n, addr, [(2, 4), (2, 5)])
			self.rr.AddTurnout("HSw19", self, n, addr, [(2, 6), (2, 7)])
			self.rr.AddTurnout("HSw21", self, n, addr, [(3, 0), (3, 1)])
			
			# virtual turnouts - these are physically controlled by other turnouts
			# and so have no output bits
			self.rr.AddTurnout("HSw5", self, n, addr, [])
			self.rr.AddTurnout("HSw13", self, n, addr, [])

			self.rr.AddBlockInd("H30",    self, n, addr, [(3, 2)])
			self.rr.AddBlockInd("H10",    self, n, addr, [(3, 3)])
			self.rr.AddBlockInd("H23",    self, n, addr, [(3, 4)])
			self.rr.AddBlockInd("N25occ", self, n, addr, [(3, 5)])

			self.rr.AddStopRelay("H21.srel", self, n, addr, [(3, 6)])
			self.rr.AddStopRelay("H13.srel", self, n, addr, [(3, 7)])

			self.rr.AddBreakerInd("CBHydeJct",  self, n, addr, [(4, 0)])
			self.rr.AddBreakerInd("CBHydeWest", self, n, addr, [(4, 1)])
			self.rr.AddBreakerInd("CBHydeEast", self, n, addr, [(4, 2)])
			self.rr.AddIndicator("HydeWestPower", self, n, addr, [(4, 3)])
			self.rr.AddIndicator("HydeEastPower", self, n, addr, [(4, 4)])
			
			# virtual signals - these do not physically exist and are given no output bits
			self.rr.AddSignal("H4R",   self, n, addr, [])
			self.rr.AddSignal("H4LA",  self, n, addr, [])
			self.rr.AddSignal("H4LB",  self, n, addr, [])
			self.rr.AddSignal("H4LC",  self, n, addr, [])
			self.rr.AddSignal("H4LD",  self, n, addr, [])
			self.rr.AddSignal("H6R",   self, n, addr, [])
			self.rr.AddSignal("H6LA",  self, n, addr, [])
			self.rr.AddSignal("H6LB",  self, n, addr, [])
			self.rr.AddSignal("H6LC",  self, n, addr, [])
			self.rr.AddSignal("H6LD",  self, n, addr, [])
			self.rr.AddSignal("H8R",   self, n, addr, [])
			self.rr.AddSignal("H8L",   self, n, addr, [])
			self.rr.AddSignal("H10L",  self, n, addr, [])
			self.rr.AddSignal("H10RA", self, n, addr, [])
			self.rr.AddSignal("H10RB", self, n, addr, [])
			self.rr.AddSignal("H10RC", self, n, addr, [])
			self.rr.AddSignal("H10RD", self, n, addr, [])
			self.rr.AddSignal("H10RE", self, n, addr, [])
			self.rr.AddSignal("H12L",  self, n, addr, [])
			self.rr.AddSignal("H12RA", self, n, addr, [])
			self.rr.AddSignal("H12RB", self, n, addr, [])
			self.rr.AddSignal("H12RC", self, n, addr, [])
			self.rr.AddSignal("H12RD", self, n, addr, [])
			self.rr.AddSignal("H12RE", self, n, addr, [])

			# Inputs
			self.rr.AddRouteIn("H12W", self, n, addr, [(0, 0)])
			self.rr.AddRouteIn("H34W", self, n, addr, [(0, 1)])
			self.rr.AddRouteIn("H33W", self, n, addr, [(0, 2)])
			self.rr.AddRouteIn("H30E", self, n, addr, [(0, 3)])
			self.rr.AddRouteIn("H31W", self, n, addr, [(0, 4)])
			self.rr.AddRouteIn("H32W", self, n, addr, [(0, 5)])
			self.rr.AddRouteIn("H22W", self, n, addr, [(0, 6)])
			self.rr.AddRouteIn("H43W", self, n, addr, [(0, 7)])
			self.rr.AddRouteIn("H42W", self, n, addr, [(1, 0)])
			self.rr.AddRouteIn("H41W", self, n, addr, [(1, 1)])
			self.rr.AddRouteIn("H41E", self, n, addr, [(1, 2)])
			self.rr.AddRouteIn("H42E", self, n, addr, [(1, 3)])
			self.rr.AddRouteIn("H43E", self, n, addr, [(1, 4)])
			self.rr.AddRouteIn("H22E", self, n, addr, [(1, 5)])
			self.rr.AddRouteIn("H40E", self, n, addr, [(1, 6)])
			self.rr.AddRouteIn("H12E", self, n, addr, [(1, 7)])
			self.rr.AddRouteIn("H34E", self, n, addr, [(2, 0)])
			self.rr.AddRouteIn("H33E", self, n, addr, [(2, 1)])
			self.rr.AddRouteIn("H32E", self, n, addr, [(2, 2)])
			self.rr.AddRouteIn("H31E", self, n, addr, [(2, 3)])
			
			self.rr.AddBlock("H21", self, n, addr, [(2, 4)], True)
			self.rr.AddBlock("H21.E", self, n, addr, [(2, 5)], True)
			self.rr.AddBlock("HOSWW2", self, n, addr, [(2, 6)], False)
			self.rr.AddBlock("HOSWW", self, n, addr, [(2, 7)], False)
			self.rr.AddBlock("HOSWE", self, n, addr, [(3, 0)], True)
			self.rr.AddBlock("H31", self, n, addr, [(3, 1)], False)
			self.rr.AddBlock("H32", self, n, addr, [(3, 2)], False)
			self.rr.AddBlock("H33", self, n, addr, [(3, 3)], False)
			self.rr.AddBlock("H34", self, n, addr, [(3, 4)], False)
			self.rr.AddBlock("H12", self, n, addr, [(3, 5)], False)
			self.rr.AddBlock("H22", self, n, addr, [(3, 6)], True)
			self.rr.AddBlock("H43", self, n, addr, [(3, 7)], True)
			self.rr.AddBlock("H42", self, n, addr, [(4, 0)], True)
			self.rr.AddBlock("H41", self, n, addr, [(4, 1)], True)
			self.rr.AddBlock("H40", self, n, addr, [(4, 2)], True)
			self.rr.AddBlock("HOSEW", self, n, addr, [(4, 3)], False)
			self.rr.AddBlock("HOSEE", self, n, addr, [(4, 4)], True)
			self.rr.AddBlock("H13.W", self, n, addr, [(4, 5)], False)
			self.rr.AddBlock("H13", self, n, addr, [(4, 6)], False)

	def OutIn(self):
		n25occ = self.rr.GetBlock("N25.W").IsOccupied() or self.rr.GetBlock("N25").IsOccupied() or self.rr.GetBlock("N25.E").IsOccupied()
		if n25occ != self.n25occ:
			self.n25occ = n25occ
			self.nodes[HYDE].SetOutputBit(3, 5, 1 if n25occ else 0)
			
		ossLocks = self.rr.GetControlOption("osslocks") == 1

		# release controls if requested by operator or if osslocks are turned off by dispatcher			
		self.released = not ossLocks

		optFleet = self.rr.GetControlOption("hyde.fleet")  # 0 => no fleeting, 1 => fleeting

		District.OutIn(self)
		
	def CheckTurnoutPosition(self, tout):
		'''
		for simulation only - if a turnut without position bits is selected, see if there should be a 
		route selected instead
		'''
		tonm = tout.Name()
		if tonm not in self.toPos:
			return 
		
		self.toPos[tonm] = tout.IsNormal()
		
		if tonm == "HSw3":
			self.toPos["HSw5"] = self.toPos["HSw3"]
			self.rr.turnouts["HSw5"].SetNormal(tout.IsNormal())
		elif tonm == "HSw5":
			self.toPos["HSw3"] = self.toPos["HSw5"]
			self.rr.turnouts["HSw3"].SetNormal(tout.IsNormal())
		elif tonm == "HSw11":
			self.toPos["HSw13"] = self.toPos["HSw11"]
			self.rr.turnouts["HSw13"].SetNormal(tout.IsNormal())
		elif tonm == "HSw13":
			self.toPos["HSw11"] = self.toPos["HSw13"]
			self.rr.turnouts["HSw11"].SetNormal(tout.IsNormal())

		for g in self.routeGroups:
			routeForGroup = False			
			for r in g:
				match = True
				for to, status in self.routeNeeded[r]:
					st = True if status == "N" else False
					if self.toPos[to] != st:
						match = False
						break
					
				if match:
					self.rr.SetRouteIn(r)
					routeForGroup = True
					break

			if not routeForGroup:
				self.rr.ClearAllRoutes(g)
		
		
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
		
		return {"turnout": [{"name": x[0], "state": x[1]} for x in tolist] }
			
	def RouteIn(self, rt, stat, turnouts):
		rt.SetState(stat)
		rtNm = rt.Name()
		if stat == 0:
			return None

		try:
			tolist = self.routeMap[rtNm]
		except KeyError:
			return None

		try:
			osName = self.routeOSMap[rtNm]
		except KeyError:
			return None

		for tonm, state in tolist:
			self.toPos[tonm] = state == "N" 
			try:
				self.rr.turnouts[tonm].SetNormal(state == "N")
			except KeyError:
				logging.warning("turnout %s unknown" % tonm)

		msgs = []
		for tn, state in tolist:
			turnouts[tn].SetNormal(state == 'N')
			msgs.extend(turnouts[tn].GetEventMessages())

		for m in msgs:
			self.rr.RailroadEvent(m)

		return osName



