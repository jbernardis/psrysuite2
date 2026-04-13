import logging


class IgnoredBlocks:
	def __init__(self, blocks):
		self.blocks = blocks
		self.rawList = []
		self.fullList = []

	def GetRawList(self):
		return self.rawList

	def AddRawBlocks(self, rawList):
		newBlocks = [b for b in rawList if b not in self.rawList]
		logging.debug("adding new blocks to raw ignore list: %s" % ", ".join(newBlocks))
		for b in newBlocks:
			self.rawList.append(b)
			self.fullList.extend(self.expandBlock(b))
		logging.debug("Full ignore list: %s" % ", ".join(self.fullList))

	def SetRawBlocks(self, rawList):
		self.rawList = [bn for bn in rawList]
		self.recomputeFullList()

	def AddRawBlock(self, bn):
		logging.debug("adding new block to raw ignore list: %s" % bn)
		self.rawList.append(bn)
		self.fullList.extend(self.expandBlock(bn))

	def RemoveRawBlock(self, bn):
		logging.debug("removing block from raw ignore list: %s" % bn)
		try:
			self.rawList.remove(bn)
		except ValueError:
			# not im list - nothing to do
			return

		self.recomputeFullList()

	def HasBlock(self, bn):
		return bn in self.fullList

	def recomputeFullList(self):
		self.fullList = []
		for bn in self.rawList:
			self.fullList.extend(self.expandBlock(bn))

	def expandBlock(self, bname):
		blk = self.blocks.get(bname, None)
		if blk is None:
			logging.error("Unable to find block %s" % bname)
			return []

		blist = blk.GetAllBlocks()
		result = []
		for b in blist:
			result.append(b.Name())

		logging.debug("Block %s has expanded to %s" % (bname, ", ".join(result)))
		return result
