import logging
from dispatcher.constants import RegAspects

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
		self.governingSignal = None
		self.governingAspect = 0
		self.governingAspectType = RegAspects
		self.profiler = None
		self.movedBeyondOrigin = False
		self.headAtTerminus = False
		self.origin = None
		self.terminus = None
		self.completed = False
		self.inBlock = False
		self.forcedStop = False
		self.pendingStop = False
		self.pendingStopCount = 0
		self.pendingStopping = False
		
	def SetOriginTerminus(self, origin, terminus):
		self.origin = origin
		self.terminus = terminus
		
	def SetPendingStop(self, flag):
		if not flag:
			self.pendingStop = False
			self.pendingStopCount = 0
			self.pendingStopping = False
			return 
		
		if self.pendingStopCount == 0 and not self.pendingStopping:
			self.pendingStop = True
			self.pendingStopCount = 7
			return 
		
		if not self.pendingStopping:
			self.pendingStopCount -= 1
			if self.pendingStopCount <= 0:
				self.pendingStop = False
				self.pendingStopCount = 0
				self.pendingStopping = True
			
	def IsWaitingPendingStop(self):
		return self.pendingStop
		
	def SetInBlock(self, flag):
		self.inBlock = flag		
		
	def SetForcedStop(self, flag=True):
		self.forcedStop = flag
		
	def GetForcedStop(self):
		return self.forcedStop
		
	def HasMoved(self, moved=None):
		if moved is not None:
			self.movedBeyondOrigin = moved

		return self.movedBeyondOrigin
	
	def CheckHasMoved(self, blknm):
		if blknm != self.origin:
			self.movedBeyondOrigin = True
			
	def AtTerminus(self, blknm):
		return blknm == self.terminus
	
	def HeadAtTerminus(self, flag=None):
		if flag is not None:
			self.headAtTerminus = flag
			
		return self.headAtTerminus
	
	def MarkCompleted(self):
		self.completed = True
		
	def HasCompleted(self):
		return self.completed
		
	def SetProfiler(self, prof):
		self.profiler = prof
		
	def SetTrain(self, train):
		self.train = train
		
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
	
	def GetSpeedStep(self):		
		# if the train has completed, cut its speed down to zero rapidly
		if self.HasCompleted() and self.speed > 0:
			return -10 if self.speed > 10 else -self.speed

		# if the train is being stopped forcibly, come down to 0 immediately
		if self.forcedStop:
			return -self.speed

		# step == 0 implies we are stopped - so we stay that way		
		if self.step == 0:
			return 0

		# if we are waiting the "pending" interval before stopping, return 0		
		if self.pendingStop:
			return 0

		# jump to the start speed if we are just starting out
		if self.targetSpeed > self.speed and self.speed < self.startSpeed:
			return self.startSpeed - self.speed
		
		# otherwise, we consider the current speed, the target speed, and the step value	
		if self.step > 0:
			if self.speed < self.targetSpeed:
				step = self.targetSpeed - self.speed
				if step > self.step:
					step = self.step
				return step
			elif self.speed > self.targetSpeed:
				return self.speed - self.targetSpeed
			else:
				return 0
			
		if self.step < 0:
			if self.speed > self.targetSpeed:
				step = self.targetSpeed - self.speed
				if step < self.step:
					step = self.step
				return step
			elif self.speed < self.targetSpeed:
				return self.speed - self.targetSpeed
			else:
				return 0
			
		return 0
	
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

	def GetGoverningSignal(self):
		return self.governingSignal, self.governingAspect
	
	def SetGoverningSignal(self, sig):
		self.governingSignal = sig
		
	def SetGoverningAspect(self, aspect, aspectType):
		if self.inBlock:
			# the signal aspect is "frozen" after we pass it so make no change here
			return 
		
		if self.completed:
			# the train has completed - make no aspect change here
			self.targetSpeed = 0
			self.step = 0 
			return
		
		self.governingAspect = aspect
		self.governingAspectType = aspectType	
		if self.profiler is None:
			self.startSpeed = 0
			self.targetSpeed = 0
			self.step = 0
		else:
			self.startSpeed, self.targetSpeed, self.step = self.profiler(self.loco, aspect, aspectType, self.speed)
		
	def GetGoverningAspect(self):
		if self.completed:
			self.governingAspect = 0
			
		return self.governingAspect	
	