class Train:
	def __init__(self, parent, name, loco):
		self.parent = parent
		self.name = name
		self.loco = loco
		self.blocks = []
		self.east = True
		self.chosenRoute = None

	def AddBlock(self, block):
		if block in self.blocks:
			return

		self.blocks.append(block)
		self.parent.TrainAddBlock(self.name, block)
		
	def GetBlocks(self):
		return self.blocks
	
	def GetLatestBlock(self):
		if len(self.blocks) == 0:
			return None
		
		return self.blocks[-1]
	
	def SetEast(self, flag):
		self.east = flag
		
	def GetEast(self):
		return self.east
	
	def IsInBlock(self, block):
		return block in self.blocks

	def DelBlock(self, block):
		if block in self.blocks:
			self.blocks.remove(block)
			self.parent.TrainRemoveBlock(self.name, block, self.blocks)
			
		if len(self.blocks) > 0:
			self.parent.TrainTailInBlock(self.name, self.blocks[0])

		return len(self.blocks)

	def SetChosenRoute(self, rtnm):
		self.chosenRoute = rtnm

	def GetChosenRoute(self):
		return self.chosenRoute
