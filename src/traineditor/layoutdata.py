import json

class LayoutData:
	def __init__(self, rrserver):
		self.layout = rrserver.Get("getlayout", {})
		if self.layout is None:
			self.RRConnected = False
			return

		self.RRConnected = True

		self.routes = self.layout["routes"]
		self.subblocks = self.layout["subblocks"]
		self.crossovers = self.layout["crossover"]

		self.block2route = {}
		self.osblocks = []
		self.blocks = []

		self.blockdir = {b: d["east"] for b, d in self.layout["blocks"].items()}
		self.stopblocks = {b: [d["sbeast"], d["sbwest"]] for b, d in self.layout["blocks"].items()}
		for r in self.routes:
			for b in self.routes[r]["ends"]:
				if b not in self.blocks and b is not None:
					self.blocks.append(b)
				if b in self.block2route:
					self.block2route[b].append(r)
				else:
					self.block2route[b] = [r]
			oswitch = self.routes[r]["os"]
			if oswitch not in self.osblocks and oswitch is not None:
				self.osblocks.append(oswitch)
			if oswitch in self.block2route:
				self.block2route[oswitch].append(r)
			else:
				self.block2route[oswitch] = [r]

		self.osblocks = sorted(self.osblocks)
		self.blocks = sorted([x for x in self.blocks if x not in self.osblocks])

	def IsConnected(self):
		return self.RRConnected
		
	def IsCrossoverPt(self, osBlk, blk):
		return [osBlk, blk] in self.crossovers

	def GetRoutesForBlock(self, blknm):
		try:
			return self.block2route[blknm]
		except KeyError:
			return None

	def GetRouteEnds(self, rname):
		return self.routes[rname]["ends"]

	def GetRouteSignals(self, rname):
		return self.routes[rname]["signals"]

	def GetRouteOS(self, rname):
		return self.routes[rname]["os"]

	def GetBlocks(self):
		return self.blocks

	def IsBlockEast(self, blknm):
		try:
			return self.blockdir[blknm] == 1
		except KeyError:
			return None

	def GetSubBlocks(self, blk):
		try:
			return self.subblocks[blk]
		except KeyError:
			return []

	def GetStopBlocks(self, blk):
		try:
			return self.stopblocks[blk]
		except KeyError:
			return [None, None]
