from dispatcher.constants import STOP, aspectname, aspecttype, aspectprofileindex


class Signal:
	def __init__(self, district, screen, frame, name, aspecttype, east, pos, tiles):
		self.district = district
		self.screen = screen
		self.frame = frame
		self.disabled = False
		self.name = name
		self.tiles = tiles
		self.pos = pos
		self.aspect = STOP
		self.frozenAspect = None
		self.aspectType = aspecttype
		self.east = east
		self.possibleRoutes = {}
		self.lvrName = None
		self.guardBlock = None # block that the signal is guarding exit from
		self.fleetEnabled = False
		self.locked = False
		self.lockedBy = []
		self.mutex = [] # mutually exclusive signals

	def GetDefinition(self):
		return {
			self.name: {
				"aspecttype": self.aspectType
			}
		}

	def SetDisabled(self, flag=True):
		self.disabled = flag

	def IsDisabled(self):
		return self.disabled

	def IsLocked(self):
		return self.locked
	
	def GetLockedBy(self):
		return self.lockedBy

	def EnableFleeting(self, flag=None):
		if flag is None:
			self.fleetEnabled = not self.fleetEnabled
		else:
			self.fleetEnabled = flag
		# self.frame.PopupEvent("Fleet %s for signal %s" % ("enabled" if self.fleetEnabled else "disabled", self.name))
		self.Draw()

	def IsFleeted(self):
		return self.fleetEnabled

	def SetLever(self, lvrName):
		self.lvrName = lvrName

	def GetLever(self):
		return self.lvrName

	def AddPossibleRoutes(self, blk, rtList):
		self.possibleRoutes[blk] = rtList

	def IsPossibleRoute(self, blknm, rname):
		if blknm not in self.possibleRoutes:
			return False

		return rname in self.possibleRoutes[blknm]
		
	def GetDistrict(self):
		return self.district

	def GetScreen(self):
		return self.screen

	def GetName(self):
		return self.name

	def GetAspectType(self):
		return self.aspectType
	
	def GetAspectName(self, aspect=None):
		if aspect is None:
			aspect = self.aspect

		return "%s (%s)" % (aspectname(aspect, self.aspectType), aspecttype(self.aspectType))
	
	def GetAspectProfileIndex(self, aspect=None):
		asp = self.aspect if aspect is None else aspect
		return aspectprofileindex(asp, self.aspectType)

	def GetPos(self):
		return self.pos

	def GetEast(self):
		return self.east

	def Draw(self):
		if self.tiles is None:
			return 
		
		bmp = self.tiles.getBmp(self)
		self.frame.DrawTile(self.screen, self.pos, bmp) 

	def GetAspect(self):
		return self.aspect
	
	def SetMutexSignals(self, mutexList):
		self.mutex = mutexList

	def SetLock(self, lockedby, flag=True):
		# lockedby == NOne means we are in the display process.  Just mark the signal as locked/unlocked and be done
		if flag:
			self.locked = True
			if lockedby is not None:
				if lockedby in self.lockedBy:
				# already locked by this signal
					return
				self.lockedBy.append(lockedby)
				if len(self.lockedBy) == 1:
					self.frame.Request({"signallock": { "name": self.name, "status": 1}})
		else:
			if lockedby is None:
				self.locked = False
			else:
				if lockedby not in self.lockedBy:
					# this signal hasn't locked by this locker, so it can't unlock it
					return
				self.lockedBy.remove(lockedby)
				if len(self.lockedBy) == 0:
					self.locked = False
					self.frame.Request({"signallock": { "name": self.name, "status": 0}})

	def ClearLocks(self, forward=True):
		self.lockedBy = []
		if self.locked:
			self.locked = False
			if forward:
				self.frame.Request({"signallock": { "name": self.name, "status": 0}})

	def SetAspect(self, aspect, refresh=False):
		if self.aspect == aspect:
			return False
		
		self.aspect = aspect

		if refresh:
			self.Draw()

		return True
	
	def ForceNeutral(self):
		self.aspect = 0
		self.Draw()
		
	def SetFrozenAspect(self, fa):
		self.frozenAspect = fa

	def GetFrozenAspect(self):
		return self.frozenAspect

	def SetFleetPending(self, flag, osblk, rtname, blk):
		if not self.fleetEnabled:
			return

		if not flag:
			self.frame.DelPendingFleet(blk)
		else:
			self.frame.AddPendingFleet(blk, osblk, rtname, self)

	def DoFleeting(self, newAspect):
		if self.aspect != 0:
			return # it's already been taken for other purposes - do nothing
	
		self.frame.Request({"signal": { "name": self.GetName(), "aspect": newAspect, "aspecttype": self.aspectType }})

	def SetGuardBlock(self, blk):
		self.guardBlock = blk

	def GetGuardBlock(self):
		return self.guardBlock

