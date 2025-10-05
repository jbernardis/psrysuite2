class Button:
	def __init__(self, district, screen, frame, name, pos, tiles):
		self.district = district
		self.screen = screen
		self.frame = frame
		self.name = name
		self.pos = pos
		self.tiles = tiles
		self.aspect = 0
		self.pressed = False
		self.on = False
		self.off = False
		self.acknowledged = False
		self.invalid = False

	def GetDistrict(self):
		return self.district

	def GetScreen(self):
		return self.screen

	def GetPos(self):
		return self.pos

	def GetName(self):
		return self.name

	def IsPressed(self):
		return self.pressed

	def Draw(self):
		if self.acknowledged:
			bmp = self.tiles.acknowledged
		elif self.invalid:
			bmp = self.tiles.error
		elif self.pressed:
			bmp = self.tiles.dark
		elif self.on:
			bmp = self.tiles.acknowledged
		elif self.off:
			bmp = self.tiles.error
		else:
			bmp = self.tiles.light
		self.frame.DrawTile(self.screen, self.pos, bmp)

	def Press(self, refresh=False):
		if self.pressed:
			return False
		
		self.pressed = True
		if refresh:
			self.Draw()

		return True

	def TurnOn(self, flag=True, refresh=False):
		self.on = flag
		self.off = not flag
		if refresh:
			self.Draw()

	def IsOn(self):
		return self.on

	def Acknowledge(self, refresh=False):
		if self.acknowledged:
			return False
		
		self.acknowledged = True
		if refresh:
			self.Draw()

		return True

	def Invalidate(self, refresh=False):
		if self.invalid:
			return False
		
		self.invalid = True
		if refresh:
			self.Draw()

		return True

	def Release(self, refresh=False):
		self.acknowledged = False
		self.invalid = False
		if not self.pressed:
			return False
		
		self.pressed = False
		if refresh:
			self.Draw()

		return True
