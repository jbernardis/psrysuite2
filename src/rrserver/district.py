import sys


class District:
	def __init__(self, parent, name, settings):
		self.parent = parent
		self.name = name
		self.address = None
		self.settings = settings

		self.routeMap = {}
		self.rrBus = None
		
	def Name(self):
		return self.name

	def Locale(self):
		return None
				
	def OutIn(self):
		for nd in self.nodes.values():
			nd.OutIn()

	def BlockOccupancyChange(self, rr, obj, val):
		pass

	def CheckTurnoutLocks(self, turnouts):
		print("in default checkswitchlocks")
		return []

	def EvaluateDistrictLocks(self, sig, ossLocks=None):
		pass

	def ControlRestrictedMessage(self):
		return "Control is Restricted"

	def ControlRestrictedSignal(self, sig):
		return False

	def MapLeverToSignals(self, lever):
		return [], []

	def Initialize(self):
		pass

	def DelayedStartup(self):
		pass
			
	def GetControlOption(self, reset=True):
		return [], []

	def UpdateControlOption(self):
		pass
		
	def GetNodes(self):
		return self.nodes
	
	def Released(self, _):
		return False
	
	def PressButton(self, bname):
		pass
			
	def TurnoutLeverChange(self, _):
		pass

	def SetHandswitch(self, nm, st):
		pass
	
	def SetHandswitchIn(self, obj, newval):
		pass
	
	def CheckTurnoutPosition(self, turnout):
		pass
		
	def RouteIn(self, rt, stat, turnouts):
		return None
	
	def GetRouteInMsg(self, r):
		return None
	
	def ShowBreakerState(self, _):
		pass
	
	def SelectRouteIn(self, _):
		return None
	
	def SetAspect(self, snm, asp):
		return False
	
	def VerifyAspect(self, signame, aspect):
		return aspect

	def SignalClick(self, sig, callon):
		return True
			
	def setBus(self, bus):
		self.rrBus = bus
		for nd in self.nodes.values():
			nd.setBus(bus)
