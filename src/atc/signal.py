class Signal:
	def __init__(self, parent, name, aspect, aspectType):
		self.parent = parent
		self.name = name
		self.aspect = aspect
		self.aspectType = aspectType
		self.locked = False

	def Lock(self, flag=True):
		if self.locked == flag:
			return
		self.locked = flag
		self.parent.SignalLockChange(self.name, self.locked)

	def IsLocked(self):
		return self.locked

	def SetAspect(self, aspect, aspectType):
		if self.aspect == aspect and self.aspectType == aspectType:
			return
		self.aspect = aspect
		self.aspectType = aspectType
		self.parent.SignalAspectChange(self.name, self.aspect, self.aspectType)

	def GetAspect(self):
		return self.aspect, self.aspectType

	def GetName(self):
		return self.name
