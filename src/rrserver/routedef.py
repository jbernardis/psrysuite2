class RouteDef:
	def __init__(self, name, os, ends, signals, turnouts):
		self.name = name
		self.os = os
		self.ends = [x for x in ends]
		self.signals = [x for x in signals]
		self.turnouts = [t for t in turnouts]
		self.FormatRoute()

	def FormatRoute(self):
		return {"routedef": {"name": self.name, "os": self.os, "ends": self.ends, "signals": self.signals, "turnouts": self.turnouts}}
