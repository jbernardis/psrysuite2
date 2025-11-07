from dispatcher.constants import EMPTY, OCCUPIED, TURNOUT, SLIPSWITCH
import logging


class Turnout:
	def __init__(self, district, frame, name, screen, tiles, pos):
		self.district = district
		self.frame = frame
		self.name = name
		self.screen = screen
		self.tiles = tiles
		self.pos = pos
		self.normal = True
		self.statusFromBlock = "E"
		self.eastFromBlock = True
		self.routeControlled = False
		self.disabled = False
		self.pairedTurnout = None
		self.controllingTurnout = None
		self.opposite = False
		self.ttype = TURNOUT
		self.blockList = []
		self.containingBlock = None
		self.locked = False
		if pos is None:
			self.disabled = True

	def IsLocked(self):
		return self.locked

	def IsDisabled(self):
		return self.disabled
	
	def SetContainingBlock(self, blk):
		self.containingBlock = blk
	
	def GetContainingBlock(self):
		return self.containingBlock

	def SetLock(self, flag, refresh=False):
		if self.locked == flag:
			return False

		self.locked = flag
		if refresh:
			self.Draw()

		if self.pairedTurnout is not None and self.pairedTurnout.IsLocked() != flag:
			self.pairedTurnout.SetLock(flag, refresh=refresh)
		if self.controllingTurnout is not None and self.controllingTurnout.IsLocked() != flag:
			self.controllingTurnout.SetLock(flag, refresh=refresh)

		return True

	def ClearLock(self, refresh=False):
		return self.SetLock(False, refresh)

	def GetType(self):
		return self.ttype

	def GetPaired(self):
		if self.pairedTurnout is not None:
			return self.pairedTurnout
		if self.controllingTurnout is not None:
			return self.controllingTurnout

		return None

	def AddBlock(self, blknm):
		self.blockList.append(self.frame.blocks[blknm])

	# def GetPos(self):
	# 	return self.screen, self.pos

	def Draw(self, blockstat=None, east=None):
		if east is None:
			east = self.eastFromBlock
		if blockstat is None:
			blockstat = self.statusFromBlock

		if self.pos is not None:
			tostat = "N" if self.normal else "R"

			bmp = self.tiles.getBmp(tostat, blockstat, east, self.routeControlled or self.disabled or self.locked)
			self.frame.DrawTile(self.screen, self.pos, bmp)

		self.statusFromBlock = blockstat
		self.eastFromBlock = east

	def SetRouteControl(self, flag=True):
		self.routeControlled = flag

	def SetDisabled(self, flag=True):
		self.disabled = flag

	def IsRouteControlled(self):
		return self.routeControlled

	def SetPairedTurnout(self, turnout, opposite=False):
		self.pairedTurnout = turnout
		turnout.SetControlledBy(self, opposite)

	def SetControlledBy(self, turnout, opposite=False):
		self.controllingTurnout = turnout
		self.opposite = opposite

	def GetControlledBy(self):
		if self.controllingTurnout:
			return self.controllingTurnout
		else:
			return self

	def GetBlockStatus(self):
		return self.statusFromBlock

	def IsNormal(self):
		return self.normal

	def IsReverse(self):
		return not self.normal

	def GetStatus(self):
		return "N" if self.normal else "R"

	def SetReverse(self, refresh=False, force=False):
		if not self.normal:
			return False

		if self.IsLocked() and not force:
			return False

		self.normal = False

		# if self.pairedTurnout is not None:
		# 	if self.opposite:
		# 		self.pairedTurnout.SetNormal(refresh, force)
		# 	else:
		# 		self.pairedTurnout.SetReverse(refresh, force)
		# self.district.DetermineRoute(self.blockList)

		if refresh:
			self.Draw()
		return True

	def SetNormal(self, refresh=False, force=False):
		if self.normal:
			return False

		if self.IsLocked() and not force:
			return False
		
		self.normal = True
		# if self.pairedTurnout is not None:
		# 	if self.opposite:
		# 		self.pairedTurnout.SetReverse(refresh, force)
		# 	else:
		# 		self.pairedTurnout.SetNormal(refresh, force)
		#
		# self.district.DetermineRoute(self.blockList)
		if refresh:
			self.Draw()
		return True

	def GetName(self):
		return self.name

	def GetDistrict(self):
		return self.district

	def GetScreen(self):
		return self.screen

	def GetPos(self):
		return self.pos

	def GetScreenPos(self):
		return self.screen, self.pos


class SlipSwitch(Turnout):
	def __init__(self, district, frame, name, screen, tiles, pos):
		Turnout.__init__(self, district, frame, name, screen, tiles, pos)
		self.ttype = SLIPSWITCH
		self.status = ["N", "N"]
		self.disabled = False
		self.controllers = [None, None]
		self.controller = None

	def SetControllers(self, a, b):
		self.controller = None
		if a is None:
			self.controllers[0] = self
			self.controller = 0
		else:
			self.controllers[0] = a
		if b is None:
			self.controllers[1] = self
			self.controller = 1
		else:
			self.controllers[1] = b

	def IsNormal(self):
		if self.controller is None:
			return False

		return self.status[self.controller] == "N"

	def IsReverse(self):
		if self.controller is None:
			return False

		return self.status[self.controller] != "N"

	def SetReverse(self, refresh=False, force=False):
		if self.controller is None:
			return False

		if not self.IsNormal():
			return False

		if self.IsLocked() and not force:
			return False
		
		self.normal = False
		self.status[self.controller] = "R"
		if self.pairedTurnout is not None:
			if self.opposite:
				self.pairedTurnout.SetNormal(refresh)
			else:
				self.pairedTurnout.SetReverse(refresh)

		self.district.DetermineRoute(self.blockList)

		if refresh:
			self.Draw()
		return True

	def SetNormal(self, refresh=False, force=False):
		if self.controller is None:
			return False

		if self.IsNormal():
			return False

		if self.IsLocked() and not force:
			return False
		
		self.normal = True

		self.status[self.controller] = "N"
		if self.pairedTurnout is not None:
			if self.opposite:
				self.pairedTurnout.SetNormal(refresh)
			else:
				self.pairedTurnout.SetReverse(refresh)

		self.district.DetermineRoute(self.blockList)

		if refresh:
			self.Draw()
		return True

	def SetStatus(self, status):
		self.status = status
		# self.district.DetermineRoute(self.blockList)

	def UpdateStatus(self):
		newstat = [s for s in self.status]
		if self.controller != 0:
			newstat[0] = "N" if self.controllers[0].IsNormal() else "R"
		if self.controller != 1:
			newstat[1] = "N" if self.controllers[1].IsNormal() else "R"
		self.SetStatus(newstat)

	def GetStatus(self):
		return self.status

	def Draw(self, blkStat=None, east=None):
		if blkStat is None:
			blkStat = self.statusFromBlock

		bmp = self.tiles.getBmp(self.status, blkStat, self.routeControlled or self.disabled or self.locked)
		self.frame.DrawTile(self.screen, self.pos, bmp)
		self.statusFromBlock = blkStat
