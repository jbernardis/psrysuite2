from dispatcher.district import EWCrossoverPoints


def CrossingEastWestBoundary(osblk, blk):
	return [osblk, blk] in EWCrossoverPoints or [blk, osblk] in EWCrossoverPoints


class BlockOSMap:
	def __init__(self, rrserver):
		self.blockosmap = rrserver.Get("blockosmap", {})
		self.osblockmap = {}

		for blk, oslists in self.blockosmap.items():
			wos = oslists[0]
			eos = oslists[1]
			for o in wos:
				if o not in self.osblockmap:
					self.osblockmap[o] = [[], []]
				if CrossingEastWestBoundary(o, blk):
					self.osblockmap[o][0].append(blk)
				else:
					self.osblockmap[o][1].append(blk)
			for o in eos:
				if o not in self.osblockmap:
					self.osblockmap[o] = [[], []]

				if CrossingEastWestBoundary(o, blk):
					self.osblockmap[o][1].append(blk)
				else:
					self.osblockmap[o][0].append(blk)

	def GetEastOSList(self, bname):
		try:
			return self.blockosmap[bname][1]
		except (KeyError, IndexError):
			return []

	def GetWestOSList(self, bname):
		try:
			return self.blockosmap[bname][0]
		except (KeyError, IndexError):
			return []

	def GetOSList(self, bname, east):
		if east:
			return self.GetEastOSList(bname)
		else:
			return self.GetWestOSList(bname)

	def GetEastBlockList(self, osname):
		try:
			return self.osblockmap[osname][1]
		except (KeyError, IndexError):
			return []

	def GetWestBlockList(self, osname):
		try:
			return self.osblockmap[osname][0]
		except (KeyError, IndexError):
			return []

	def GetBlockList(self, osname, east):
		if east:
			return self.GetEastBlockList(osname)
		else:
			return self.GetWestBlockList(osname)



