class Train:
	def __init__(self, parent, name, loco):
		self.parent = parent
		self.name = name
		self.loco = loco
		self.blocks = []
		self.east = True

	def AddBlock(self, block):
		if block in self.blocks:
			return

		self.blocks.append(block)
		self.parent.TrainAddBlock(self.name, block)
		
	def SetEast(self, flag):
		self.east = flag
		
	def GetBlocks(self):
		return self.blocks
	
	def GetFirstBlock(self):
		if len(self.blocks) == 0:
			return None
		return self.blocks[0]
			
	def InBlock(self, blknm):
		return blknm in self.blocks

	def DelBlock(self, block):
		if block in self.blocks:
			self.blocks.remove(block)
			self.parent.TrainRemoveBlock(self.name, block, self.blocks)
			
		if len(self.blocks) > 0:
			self.parent.TrainTailInBlock(self.name, self.blocks[0])

		return len(self.blocks)
