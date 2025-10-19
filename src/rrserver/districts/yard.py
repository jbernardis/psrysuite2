import logging

from rrserver.district import District
from rrserver.constants import YARD, KALE, EASTJCT, CORNELL, YARDSW
from rrserver.node import Node


class Yard(District):
	def __init__(self, rr, name, settings):
		District.__init__(self, rr, name, settings)
		self.rr = rr
		self.name = name
		self.released = False
		self.control = 0
		self.lastControl = 0
		
		self.Y20D = None
		self.Y20H = None
		
		self.nodeAddresses = [ CORNELL, EASTJCT, KALE, YARD, YARDSW ]
		self.nodes = {
			CORNELL: Node(self, rr, CORNELL, 2, settings),
			EASTJCT: Node(self, rr, EASTJCT, 2, settings),
			KALE:    Node(self, rr, KALE,    4, settings),
			YARD:    Node(self, rr, YARD,    6, settings),
			YARDSW:  Node(self, rr, YARDSW,  5, settings, incount=0)
		}
		
		# cornell node
		addr = CORNELL
		with self.nodes[addr] as n:
			# outputs
			self.rr.AddSignal("Y4L",  self, n, addr, [(0, 0), (0, 1), (0, 2)])
			self.rr.AddSignal("Y2L",  self, n, addr, [(0, 3)])
			self.rr.AddSignal("Y2R",  self, n, addr, [(0, 4), (0, 5), (0, 6)])
			self.rr.AddSignal("Y4RA", self, n, addr, [(0, 7), (1, 0), (1, 1)])
			self.rr.AddSignal("Y4RB", self, n, addr, [(1, 2)])
			
			self.rr.AddStopRelay("Y21.srel", self, n, addr, [(1, 3)])
			self.rr.AddStopRelay("L10.srel", self, n, addr, [(1, 4)])
		
			# inputs
			self.rr.AddTurnoutPosition("YSw1", self, n, addr, [(0, 0), (0, 1)])
			self.rr.AddTurnoutPosition("YSw3", self, n, addr, [(0, 2), (0, 3)])
			
			self.rr.AddBlock("Y21.W",   self, n, addr, [(0, 4)], True)
			self.rr.AddBlock("Y21",     self, n, addr, [(0, 5)], True)
			self.rr.AddBlock("Y21.E",   self, n, addr, [(0, 6)], True)
			self.rr.AddBlock("YOSCJW",  self, n, addr, [(0, 7)], False) #  CJOS1	
			self.rr.AddBlock("YOSCJE",  self, n, addr, [(1, 0)], True) #  CJOS2
			sbw = self.rr.AddBlock("L10.W",   self, n, addr, [(1, 1)], False)
			b = self.rr.AddBlock("L10",     self, n, addr, [(1, 2)], False)
			b.AddStoppingBlocks([sbw])
		
		
		# eastend jct node
		addr = EASTJCT
		with self.nodes[addr] as n:
			# outputs
			self.rr.AddSignal("Y10L", self, n, addr, [(0, 0), (0, 1), (0, 2)])
			self.rr.AddSignal("Y8LA", self, n, addr, [(0, 3)])
			self.rr.AddSignal("Y8LB", self, n, addr, [(0, 4)])
			self.rr.AddSignal("Y8LC", self, n, addr, [(0, 5)])
			self.rr.AddSignal("Y8R",  self, n, addr, [(0, 6), (0, 7), (1, 0)])
			self.rr.AddSignal("Y10R", self, n, addr, [(1, 1)])
			
			self.rr.AddStopRelay("Y20.srel", self, n, addr, [(1, 2)])
			self.rr.AddStopRelay("Y11.srel", self, n, addr, [(1, 3)])
		
		
			# inputs
			self.rr.AddTurnoutPosition("YSw7",  self, n, addr, [(0, 0), (0, 1)])
			self.rr.AddTurnoutPosition("YSw9",  self, n, addr, [(0, 2), (0, 3)])
			self.rr.AddTurnoutPosition("YSw11", self, n, addr, [(0, 4), (0, 5)])

			self.rr.AddBlock("Y20",    self, n, addr, [(0, 6)], True)
			self.rr.AddBlock("Y20.E",  self, n, addr, [(0, 7)], True)
			self.rr.AddBlock("YOSEJW", self, n, addr, [(1, 0)], False) #  KJOS1
			self.rr.AddBlock("YOSEJE", self, n, addr, [(1, 1)], True) #  KJOS2
			self.rr.AddBlock("Y11.W" , self, n, addr, [(1, 2)], False)
			self.rr.AddBlock("Y11",    self, n, addr, [(1, 3)], False)

		# kale node
		addr = KALE
		with self.nodes[addr] as n:
			# outputs
			self.rr.AddSignal("Y22L",  self, n, addr, [(0, 0)])
			self.rr.AddSignal("Y26LA", self, n, addr, [(0, 1)])
			self.rr.AddSignal("Y26LB", self, n, addr, [(0, 2)])
			self.rr.AddSignal("Y26LC", self, n, addr, [(0, 3)])
			self.rr.AddSignal("Y24LA", self, n, addr, [(0, 4)])
			self.rr.AddSignal("Y24LB", self, n, addr, [(0, 5)])
			
			self.rr.AddSignal("Y20H",  self, n, addr, [(0, 6)])  # these are the 2 bits to be used for roger's new signal bridge
			self.rr.AddSignal("Y20D",  self, n, addr, [(0, 7)])

			self.rr.AddSignal("Y26R", self, n, addr, [(1, 0)])
			self.rr.AddSignal("Y22R", self, n, addr, [(1, 1), (1, 2)]) # 

			# inputs
			self.rr.AddTurnoutPosition("YSw17", self, n, addr, [(0, 0), (0, 1)])
			self.rr.AddTurnoutPosition("YSw19", self, n, addr, [(0, 2), (0, 3)])
			self.rr.AddTurnoutPosition("YSw21", self, n, addr, [(0, 4), (0, 5)])
			self.rr.AddTurnoutPosition("YSw23", self, n, addr, [(0, 6), (0, 7)])
			self.rr.AddTurnoutPosition("YSw25", self, n, addr, [(1, 0), (1, 1)])
			self.rr.AddTurnoutPosition("YSw27", self, n, addr, [(1, 2), (1, 3)])
			self.rr.AddTurnoutPosition("YSw29", self, n, addr, [(1, 4), (1, 5)])
						
			self.rr.AddBlock("Y30",    self, n, addr, [(1, 6)], False)
			self.rr.AddBlock("YOSKL4", self, n, addr, [(1, 7)], True) #KAOS1
			self.rr.AddBlock("Y53",    self, n, addr, [(2, 0)], True)
			self.rr.AddBlock("Y52",    self, n, addr, [(2, 1)], True)
			self.rr.AddBlock("Y51",    self, n, addr, [(2, 2)], True)
			self.rr.AddBlock("Y50",    self, n, addr, [(2, 3)], True)
			self.rr.AddBlock("YOSKL2", self, n, addr, [(2, 4)], False) #KAOS3
			self.rr.AddBlock("YOSKL1", self, n, addr, [(2, 5)], True) #KAOS4
			self.rr.AddBlock("YOSKL3", self, n, addr, [(2, 6)], False) #KAOS2
			self.rr.AddBlock("Y10",    self, n, addr, [(2, 7)], False)
		
		# engine yard	
		addr = YARD
		with self.nodes[addr] as n:
			# outputs
			self.rr.AddSignalLED("Y2",  self, n, addr, [(0, 2), (0, 1), (0, 0)])
			self.rr.AddSignalLED("Y4",  self, n, addr, [(0, 5), (0, 4), (0, 3)])
			self.rr.AddSignalLED("Y8",  self, n, addr, [(1, 0), (0, 7), (0, 6)])
			self.rr.AddSignalLED("Y10", self, n, addr, [(1, 3), (1, 2), (1, 1)])
			self.rr.AddSignalLED("Y22", self, n, addr, [(1, 6), (1, 5), (1, 4)])
			self.rr.AddSignalLED("Y24", self, n, addr, [None, (2, 0), (1, 7)])
			self.rr.AddSignalLED("Y26", self, n, addr, [(2, 3), (2, 2), (2, 1)])
			self.rr.AddSignalLED("Y34", self, n, addr, [(2, 6), (2, 5), (2, 4)])
			
			self.rr.AddSignal("Y34RA", self, n, addr, [(2, 7)])
			self.rr.AddSignal("Y34RB", self, n, addr, [(3, 0)])
			self.rr.AddSignal("Y34L",  self, n, addr, [(3, 1), (3, 2), (3, 3)])
						
			self.rr.AddBreakerInd("CBKale",       self, n, addr, [(3, 4)])
			self.rr.AddBreakerInd("CBEastEndJct", self, n, addr, [(3, 5)])
			self.rr.AddBreakerInd("CBCornellJct", self, n, addr, [(3, 6)])
			self.rr.AddBreakerInd("CBEngineYard", self, n, addr, [(3, 7)])
			self.rr.AddBreakerInd("CBWaterman",   self, n, addr, [(4, 0)])
			
			self.rr.AddBlockInd("L20", self, n, addr, [(4, 1)])
			self.rr.AddBlockInd("P50", self, n, addr, [(4, 2)])
						
			self.rr.AddTurnoutLock("YSw1",  self, n, addr, [(4, 3)])
			self.rr.AddTurnoutLock("YSw3",  self, n, addr, [(4, 4)])
			self.rr.AddTurnoutLock("YSw7",  self, n, addr, [(4, 5)])
			self.rr.AddTurnoutLock("YSw9",  self, n, addr, [(4, 6)])
			self.rr.AddTurnoutLock("YSw17", self, n, addr, [(4, 7)])			
			self.rr.AddTurnoutLock("YSw19", self, n, addr, [(5, 0)])
			self.rr.AddTurnoutLock("YSw21", self, n, addr, [(5, 1)])
			self.rr.AddTurnoutLock("YSw23", self, n, addr, [(5, 2)])
			self.rr.AddTurnoutLock("YSw25", self, n, addr, [(5, 3)])
			self.rr.AddTurnoutLock("YSw29", self, n, addr, [(5, 4)])
			self.rr.AddTurnoutLock("YSw33", self, n, addr, [(5, 5)])
			
			# inputs	
			self.rr.AddTurnoutPosition("YSw33", self, n, addr, [(0, 0), (0, 1)])		
			self.rr.AddSignalLever("Y2",  self, n, addr, [(0, 2), (0, 3), (0, 4)])
			self.rr.AddSignalLever("Y4",  self, n, addr, [(0, 5), (0, 6), (0, 7)])
			self.rr.AddSignalLever("Y8",  self, n, addr, [(1, 0), (1, 1), (1, 2)])
			self.rr.AddSignalLever("Y10", self, n, addr, [(1, 3), (1, 4), (1, 5)])
			self.rr.AddSignalLever("Y22", self, n, addr, [(1, 6), (1, 7), (2, 0)])
			self.rr.AddSignalLever("Y24", self, n, addr, [None, (2, 1), (2, 2)])
			self.rr.AddSignalLever("Y26", self, n, addr, [(2, 3), (2, 4), (2, 5)])
			self.rr.AddSignalLever("Y34", self, n, addr, [(2, 6), (2, 7), (3, 0)])
			
			self.rr.AddRouteIn("Y81W",  self, n, addr, [(3, 3)])
			self.rr.AddRouteIn("Y82W",  self, n, addr, [(3, 4)])
			self.rr.AddRouteIn("Y83W",  self, n, addr, [(3, 5)])
			self.rr.AddRouteIn("Y84W",  self, n, addr, [(3, 6)])
			self.rr.AddRouteIn("Y81E",  self, n, addr, [(3, 7)])
			self.rr.AddRouteIn("Y82E",  self, n, addr, [(4, 0)])
			self.rr.AddRouteIn("Y83E",  self, n, addr, [(4, 1)])
			self.rr.AddRouteIn("Y84E",  self, n, addr, [(4, 2)])
			
			self.rr.AddBlock("Y70",    self, n, addr, [(4, 3)], True)  # waterman detectiuon
			self.rr.AddBlock("YOSWYE", self, n, addr, [(4, 4)], True) #  WOS1
			# bit 5 is bad
			self.rr.AddBlock("Y82",    self, n, addr, [(4, 6)], True)
			self.rr.AddBlock("Y83",    self, n, addr, [(4, 7)], True)
			self.rr.AddBlock("Y84",    self, n, addr, [(5, 0)], True)
			self.rr.AddBlock("YOSWYW", self, n, addr, [(5, 1)], True) #  WOS2
			self.rr.AddBlock("Y87",    self, n, addr, [(5, 2)], False)
			self.rr.AddBlock("Y81",    self, n, addr, [(5, 3)], True)
			
			# virtual signals - these do not physically exist and are given no bit positione
			self.rr.AddSignal("Y40L",  self, n, addr, [])
			self.rr.AddSignal("Y40RA", self, n, addr, [])
			self.rr.AddSignal("Y40RB", self, n, addr, [])
			self.rr.AddSignal("Y40RC", self, n, addr, [])
			self.rr.AddSignal("Y40RD", self, n, addr, [])
			self.rr.AddSignal("Y42R",  self, n, addr, [])
			self.rr.AddSignal("Y42LA", self, n, addr, [])
			self.rr.AddSignal("Y42LB", self, n, addr, [])
			self.rr.AddSignal("Y42LC", self, n, addr, [])
			self.rr.AddSignal("Y42LD", self, n, addr, [])

			# virtual block - has no detection
			self.rr.AddBlock("Y60",    self, n, addr, [], True)

		addr = YARDSW			
		with self.nodes[addr] as n:
			#outputs
			self.rr.AddTurnout("YSw1",  self, n, addr, [(0, 0), (0, 1)])
			self.rr.AddTurnout("YSw3",  self, n, addr, [(0, 2), (0, 3)])
			self.rr.AddTurnoutPair("YSw3", "YSw3b")
			self.rr.AddTurnout("YSw7",  self, n, addr, [(0, 4), (0, 5)])
			self.rr.AddTurnoutPair("YSw7", "YSw7b")
			self.rr.AddTurnout("YSw9",  self, n, addr, [(0, 6), (0, 7)])
			self.rr.AddTurnout("YSw11", self, n, addr, [(1, 0), (1, 1)])
			self.rr.AddTurnout("YSw17", self, n, addr, [(1, 2), (1, 3)])
			self.rr.AddTurnout("YSw19", self, n, addr, [(1, 4), (1, 5)])
			self.rr.AddTurnout("YSw21", self, n, addr, [(1, 6), (1, 7)])		
			self.rr.AddTurnoutPair("YSw21", "YSw21b")
			self.rr.AddTurnout("YSw23", self, n, addr, [(2, 0), (2, 1)])
			self.rr.AddTurnoutPair("YSw23", "YSw23b")
			self.rr.AddTurnout("YSw25", self, n, addr, [(2, 2), (2, 3)])
			self.rr.AddTurnout("YSw27", self, n, addr, [(2, 4), (2, 5)])
			self.rr.AddTurnout("YSw29", self, n, addr, [(2, 6), (2, 7)])			
			self.rr.AddTurnout("YSw33", self, n, addr, [(3, 0), (3, 1)])
			
			self.rr.AddOutNXButton("YWWB1", self, n, addr, [(4, 0)])
			self.rr.AddOutNXButton("YWWB2", self, n, addr, [(4, 1)])
			self.rr.AddOutNXButton("YWWB3", self, n, addr, [(4, 2)])
			self.rr.AddOutNXButton("YWWB4", self, n, addr, [(4, 3)])
			self.rr.AddOutNXButton("YWEB1", self, n, addr, [(4, 4)])
			self.rr.AddOutNXButton("YWEB2", self, n, addr, [(4, 5)])
			self.rr.AddOutNXButton("YWEB3", self, n, addr, [(4, 6)])
			self.rr.AddOutNXButton("YWEB4", self, n, addr, [(4, 7)])
			# no inputs
			# virtual turnouts - no bits - for waterman
			self.rr.AddTurnoutPosition("YSw113", self, n, addr, [])
			self.rr.AddTurnoutPosition("YSw115", self, n, addr, [])
			self.rr.AddTurnoutPosition("YSw116", self, n, addr, [])
			self.rr.AddTurnoutPosition("YSw131", self, n, addr, [])
			self.rr.AddTurnoutPosition("YSw132", self, n, addr, [])
			self.rr.AddTurnoutPosition("YSw134", self, n, addr, [])

		self.buttonMap = {
			"YWEB1": "Y81E", "YWEB2": "Y82E", "YWEB3": "Y83E", "YWEB4": "Y84E",
			"YWWB1": "Y81W", "YWWB2": 'Y82W', "YWWB3": 'Y83W', "YWWB4": "Y84W"
		}
		self.routes = {
			"east": ["Y81E", "Y82E", "Y83E", "Y84E"],
			"west": ["Y81W", "Y82W", "Y83W", "Y84W"]
		}
		self.currentRoute = {"east": None, "west": None}

		self.routeMap = {
				"Y81W": [ ["YSw113", "N"], ["YSw115","N"], ["YSw116", "N"] ], 
				"Y82W": [ ["YSw113", "N"], ["YSw115","R"], ["YSw116", "R"] ],
				"Y83W": [ ["YSw113", "N"], ["YSw115","R"], ["YSw116", "N"] ],
				"Y84W": [ ["YSw113", "R"], ["YSw115","N"], ["YSw116", "N"] ],
				"Y81E": [ ["YSw131", "N"], ["YSw132","N"], ["YSw134", "N"] ], 
				"Y82E": [ ["YSw131", "R"], ["YSw132","R"], ["YSw134", "N"] ],
				"Y83E": [ ["YSw131", "N"], ["YSw132","R"], ["YSw134", "N"] ],
				"Y84E": [ ["YSw131", "N"], ["YSw132","N"], ["YSw134", "R"] ],
		}
	
	def PressButton(self, btn):
		try:
			rtnm = self.buttonMap[btn.name]
		except KeyError:
			logging.warning("Unknown button pressed: %s" % btn.name)
			return None
		
		rtl = self.routes["east"] if rtnm in self.routes["east"] else self.routes["west"] if rtnm in self.routes["west"] else None
		if rtl is None:
			return None

		for rnm in rtl:		
			rt = self.rr.GetRouteIn(rnm)
			if rt is None:
				continue
			
			bt = rt.Bits()
			rt.node.SetInputBit(bt[0][0], bt[0][1], 0)
		
		rt = self.rr.GetRouteIn(rtnm)
		if rt is None:
			return None
		
		bt = rt.Bits()
		rt.node.SetInputBit(bt[0][0], bt[0][1], 1)
		
	
	def SelectRouteIn(self, rt):
		rtl = self.routes["east"] if rt.name in self.routes["east"] else self.routes["west"] if rt.name in self.routes["west"] else None
		if rtl is None:
			return None
		
		offRtList = [x for x in rtl if x != rt.name]
		return offRtList
	
	def GetRouteInMsg(self, rt):
		rtNm = rt.Name()
		
		return {"turnout": [{"name": x[0], "state": x[1]} for x in self.routeMap[rtNm]] }
		
	def RouteIn(self, rt, stat, turnouts):
		rt.SetState(stat)
		group = "east" if rt.name in self.routes["east"] else "west" if rt.name in self.routes["west"] else None
		if group is None:
			return None

		if stat == 1:
			if rt.name == self.currentRoute[group]:
				return None
			
			self.currentRoute[group] = rt.name

			msgs = []
			for tn, state in self.routeMap[rt.name]:
				turnouts[tn].SetNormal(state == 'N')
				msgs.extend(turnouts[tn].GetEventMessages())

			for m in msgs:
				self.rr.RailroadEvent(m)

			return "YOSWYW" if group == "east" else "YOSWYE"

		else:
			if rt.name == self.currentRoute[group]:
				self.currentRoute[group] = None
			return None

	def Released(self, _):
		return self.released

	def UpdateControlOption(self):
		self.lastControl = self.control
		self.control = self.rr.GetControlOption("yard")  # 0 => Yard, 1 => Dispatcher

	def OutIn(self):
		if self.control == 0: #yard local control allows the panel release button
			rlReq = self.nodes[YARD].GetInputBit(3, 1)
			if rlReq is None:
				rlReq = 0
		else:
			rlReq = 0
			
		ossLocks = self.rr.GetControlOption("osslocks") == 1

		# release controls if requested by operator or if osslocks are turned off by dispatcher			
		self.released = rlReq or not ossLocks
		self.rr.UpdateDistrictTurnoutLocks(self.name, self.released)

		optFleet = self.rr.GetControlOption("yard.fleet")  # 0 => no fleeting, 1 => fleeting

		District.OutIn(self)
		
		Y20 = self.rr.GetBlock("Y20")
		Y10L = self.rr.GetSignal("Y10L")
		Y20D = Y20.IsCleared() and (not Y20.IsOccupied()) and Y20.IsEast()
		Y20H = Y20D and Y10L.Aspect() != 0
		if Y20H:
			Y20D = False 
		if Y20D != self.Y20D or Y20H != self.Y20H:
			self.Y20D = Y20D
			self.Y20H = Y20H
			self.rr.SetAspect("Y20H", 1 if Y20H else 0)
			self.rr.SetAspect("Y20D", 1 if Y20D else 0)
		
	def GetControlOption(self):
		if self.control == 1:  # dispatcher control
			skiplist = ["Y2", "Y4", "Y8", "Y10", "Y22", "Y24", "Y26", "Y34"]
			resumelist = []
						
		else:  # assume local control
			skiplist = []
			if self.lastControl == 1:
				resumelist = ["Y2", "Y4", "Y8", "Y10", "Y22", "Y24", "Y26", "Y34"]
			else:
				resumelist = []

		self.lastControl = self.control
		return skiplist, resumelist

	def ControlRestrictedMessage(self):
		if self.control == 0:
			return "Control is Local"
		else:
			return "Dispatcher controls Yard Tower"
