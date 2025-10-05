from throttle.dccloco import DCCLoco, FORWARD, REVERSE


class DCCRemote:
	def __init__(self, server):
		self.server = server
		self.initialized = False
		self.locos = []
		self.profiles = {}
		
	def LocoCount(self):
		return len(self.locos)
	
	def HasTrain(self, trn):
		for l in self.locos:
			if l.GetTrain() == trn:
				return True
			
		return False
		
	def SelectLoco(self, loco, assertValues=False):
		for l in self.locos:
			if l.GetLoco() == loco:
				self.selectedLoco = l
				break
			
		else:
			l = DCCLoco("", loco)
			self.locos.append(l)
			self.selectedLoco = l

		l = self.selectedLoco
		if assertValues:			
			self.SetSpeedAndDirection(nspeed=l.GetSpeed(), ndir=l.GetDirection(), assertValues=True)
			self.SetFunction(headlight=l.GetHeadlight(), horn=l.GetHorn(), bell=l.GetBell(), assertValues=True)
		return l
		
	def ClearSelection(self):
		self.selectedLoco = None
		
	def DropLoco(self, loco):
		self.locos = [l for l in self.locos if l.GetLoco() != loco]
		
	def SetSpeed(self, nspeed, assertValues=False):
		self.SetSpeedAndDirection(nspeed=nspeed, assertValues=assertValues)
		
	def SetDirection(self, ndir, assertValues = False):
		self.SetSpeedAndDirection(ndir=ndir, assertValues=assertValues)
						
	def SetSpeedAndDirection(self, nspeed=None, ndir=None, assertValues=False):
		if self.selectedLoco is None:
			return 

		ospeed = self.selectedLoco.GetSpeed()		
		if nspeed is not None:
			if nspeed < 0 or nspeed > 128:
				# speed value is out of range - ignore
				return
			
			self.selectedLoco.SetSpeed(nspeed)

		odirection = self.selectedLoco.GetDirection()			
		if ndir is not None:
			if ndir not in [FORWARD, REVERSE]:
				# invalid value for direction - ignore
				return 
			
			self.selectedLoco.SetDirection(ndir)
		
		loco = self.selectedLoco.GetLoco()
		speed = self.selectedLoco.GetSpeed()
		direction = self.selectedLoco.GetDirection()
		
		if (speed != ospeed or direction != odirection) or assertValues:
			self.server.SendRequest({"throttle": {"loco": loco, "speed": speed, "direction": direction}})
		
	def SetFunction(self, headlight=None, horn=None, bell=None, assertValues=False):
		if self.selectedLoco is None:
			return 

		oheadlight = self.selectedLoco.GetHeadlight()
		if headlight is not None:
			self.selectedLoco.SetHeadlight(headlight)
		
		ohorn = self.selectedLoco.GetHorn()
		if horn is not None:
			self.selectedLoco.SetHorn(horn)
			
		obell = self.selectedLoco.GetBell()
		if bell is not None:
			self.selectedLoco.SetBell(bell)
			
		bell = self.selectedLoco.GetBell()
		horn = self.selectedLoco.GetHorn()
		light = self.selectedLoco.GetHeadlight()
		
		loco = self.selectedLoco.GetLoco()

		if (oheadlight != headlight) or (ohorn != horn) or (obell != bell) or assertValues:
			self.server.SendRequest({"function": {"loco": loco, "bell": 1 if bell else 0, "horn": 1 if horn else 0, "light": 1 if light else 0}})
		
	def GetDCCLoco(self, loco):
		for l in self.locos:
			if l.GetLoco() == loco:
				return l
	
		return None
	
	def GetDCCLocoByTrain(self, train):
		for l in self.locos:
			if l.GetTrain() == train:
				return l
			
		return None
		
	def GetDCCLocos(self):
		return self.locos

