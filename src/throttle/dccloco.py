FORWARD = 'F'
REVERSE = 'R'

class DCCLoco:
	def __init__(self, train, loco):
		self.loco = loco
		self.train = train
		self.direction = FORWARD;
		self.speed = 0;
		self.light = False;
		self.horn = False
		self.bell = False

	def GetTrain(self):
		return self.train
	
	def GetName(self):
		return self.GetTrain()
		
	def GetLoco(self):
		return self.loco
	
	def SetDirection(self, direction):
		self.direction = direction
		
	def GetDirection(self):
		return self.direction
	
	def SetSpeed(self, speed):
		self.speed = speed
		
	def GetSpeed(self):
		return self.speed

	def SetHeadlight(self, onoff):
		self.light = onoff
		
	def GetHeadlight(self):
		return self.light
	
	def SetHorn(self, onoff):
		self.horn = onoff
		
	def GetHorn(self):
		return self.horn
	
	def SetBell(self, onoff):
		self.bell = onoff
		
	def GetBell(self):
		return self.bell