import logging

from dispatcher.constants import EMPTY, OCCUPIED, CLEARED, STOP, CLEAR, RegAspects, RegSloAspects, AdvAspects, SloAspects


class Tile:
	def __init__(self, name, bmps):
		self.name = name
		self.bmps = bmps

	def getBmp(self, status, east, revflag):
		if status in ["O", "U"]:
			if status == "O":
				if east:
					k = "red-left" if revflag else "red-right"
				else:
					k = "red-right" if revflag else "red-left"

			else:
				if east:
					k = "yellow-left" if revflag else "yellow-right"
				else:
					k = "yellow-right" if revflag else "yellow-left"

			try:
				bmp = self.bmps[k]
			except KeyError:
				if status == "U":
					try:
						bmp = self.bmps["yellow"]
					except KeyError:
						bmp = self.bmps["red"]
				else:
					bmp = self.bmps["red"]
			return bmp

		if status == "C":
			if east:
				k = "green-left" if revflag else "green-right"
			else:
				k = "green-right" if revflag else "green-left"
			try:
				bmp = self.bmps[k]
			except KeyError:
				bmp = self.bmps["green"]
			return bmp

		return self.bmps["white"]


class MiscTile:
	def __init__(self, name, bmps):
		self.name = name
		self.bmps = bmps

	def getBmp(self, status, tag, unknownTrain=False):
		prefix = ""
		if status == OCCUPIED:
			if unknownTrain:
				prefix = "yellow-"
			else:
				prefix = "red-"
		elif status == CLEARED:
			prefix = "green-"
		elif status == EMPTY:
			prefix = "white-"

		try:
			bmp = self.bmps[prefix+tag]
		except:
			bmp = self.bmps[tag]
		return bmp


class TurnoutTile:
	def __init__(self, name, nbmps, rbmps):
		self.name = name
		self.nbmps = nbmps
		self.rbmps = rbmps

	def getBmp(self, tostat, blkstat, east, disabled):
		if tostat == "N":
			bmps = self.nbmps
		else:
			bmps = self.rbmps

		if blkstat == "O":
			if disabled:
				try:
					return bmps["red-dis"]
				except KeyError:
					pass
			return bmps["red"]

		if blkstat == "U":
			if disabled:
				try:
					return bmps["yellow-dis"]
				except KeyError:
					pass
			try:
				return bmps["yellow"]
			except KeyError:
				pass
			return bmps["red"]

		if blkstat == "C":
			if disabled:
				try:
					return bmps["green-dis"]
				except KeyError:
					pass
				return bmps["green"]
			else:
				return bmps["green"]

		if disabled:
			try:
				return bmps["white-dis"]
			except KeyError:
				pass
		return bmps["white"]


class SlipSwitchTile:
	def __init__(self, name, nnbmps, nrbmps, rnbmps, rrbmps):
		self.name = name
		self.nnbmps = nnbmps
		self.nrbmps = nrbmps
		self.rnbmps = rnbmps
		self.rrbmps = rrbmps

	def getBmp(self, tostat, blkstat, disabled, unknownTrain=False):
		if tostat == ["N", "N"]:
			bmps = self.nnbmps
		elif tostat == ["N", "R"]:
			bmps = self.nrbmps
		elif tostat == ["R", "N"]:
			bmps = self.rnbmps
		else: # tostat == ["R", "R]
			bmps = self.rrbmps

		if blkstat == OCCUPIED:
			if unknownTrain:
				if disabled:
					try:
						return bmps["yellow-dis"]
					except KeyError:
						pass
				try:
					return bmps["yellow"]
				except KeyError:
					pass
				return bmps["red"]
			else:
				if disabled:
					try:
						return bmps["red-dis"]
					except KeyError:
						pass
				return bmps["red"]

		if blkstat == "C":
			if disabled:
				try:
					return bmps["green-dis"]
				except KeyError:
					pass
			return bmps["green"]

		if disabled:
			try:
				return bmps["white-dis"]
			except KeyError:
				pass
		return bmps["white"]


class SignalTile:
	def __init__(self, name, bmps):
		self.name = name
		self.bmps = bmps

	def getBmp(self, sig):
		if sig.aspectType == SloAspects:
			if sig.aspect == 0b01:
				tag = "clear"
			elif sig.aspect == 0b11:
				tag = "approach"
			elif sig.aspect == 0b10:
				tag = "restricting"
			else:
				tag = "stop"

		elif sig.aspectType == AdvAspects:
			if sig.aspect == 0b011:
				tag = "clear"
			elif sig.aspect == 0b010:
				tag = "approach-medium"
			elif sig.aspect == 0b111:
				tag = "clear"
			elif sig.aspect == 0b110:
				tag = "advance-approach"
			elif sig.aspect == 0b001:
				tag = "approach"
			elif sig.aspect == 0b101:
				tag = "medium-approach"
			elif sig.aspect == 0b100:
				tag = "restricting"
			else:
				tag = "stop"

		elif sig.aspectType == RegSloAspects:
			if sig.aspect == 0b011:
				tag = "clear"
			elif sig.aspect == 0b111:
				tag = "slow-clear"
			elif sig.aspect == 0b001:
				tag = "approach"
			elif sig.aspect == 0b101:
				tag = "slow-approach"
			elif sig.aspect == 0b100:
				tag = "restricting"
			else:
				tag = "stop"

		else: # assume RegAspects
			if sig.aspect == 0b011:
				tag = "clear"
			elif sig.aspect == 0b010:
				tag = "approach-medium"
			elif sig.aspect == 0b111:
				tag = "medium-clear"
			elif sig.aspect == 0b110:
				tag = "approach-slow"
			elif sig.aspect == 0b001:
				tag = "approach"
			elif sig.aspect == 0b101:
				tag = "medium-approach"
			elif sig.aspect == 0b100:
				tag = "restricting"
			else:
				tag = "stop"
			
		if sig.fleetEnabled:
			tag += "-fleet"

		try:
			return self.bmps[tag]
		except KeyError:
			logging.error("No tile defined for aspect tag %s" % tag)
			if sig.aspect == STOP:
				tag = "stop"
			else:
				tag = "restricting"
			if sig.fleetEnabled:
				tag += "-fleet"
			return self.bmps[tag]


def loadTiles(bitmaps):
	b = bitmaps.track

	tiles = {}
	tiles["horiz"] = Tile("horiz", {
		"white": b.straight.normal,
		"green": b.straight.routed,
		"green-right": b.straight.rightrouted,
		"green-left": b.straight.leftrouted,
		"red-right": b.straight.rightoccupied,
		"red-left": b.straight.leftoccupied,
		"yellow-right": b.straight.rightunknown,
		"yellow-left": b.straight.leftunknown,
		"red": b.straight.occupied,
		"yellow": b.straight.unknown})
	tiles["horiznc"] = Tile("horiz", {
		"white": b.straight.normal,
		"green": b.straight.routed,
		"yellow": b.straight.unknown,
		"red": b.straight.occupied})
	tiles["houtline"] = Tile("houtline", {
		"white": b.straightoutline.normal,
		"green": b.straightoutline.routed,
		"yellow": b.straightoutline.unknown,
		"red": b.straightoutline.occupied})
	tiles["vertical"] = Tile("vertical", {
		"white": b.vertical.normal,
		"green": b.vertical.routed,
		"green-right": b.vertical.uprouted,
		"green-left": b.vertical.downrouted,
		"red-right": b.vertical.upoccupied,
		"red-left": b.vertical.downoccupied,
		"red": b.vertical.occupied,
		"yellow-right": b.vertical.upunknown,
		"yellow-left": b.vertical.downunknown,
		"yellow": b.vertical.unknown})
	tiles["verticalnc"] = Tile("vertical", {
		"white": b.vertical.normal,
		"green": b.vertical.routed,
		"red": b.vertical.occupied,
		"yellow": b.vertical.unknown})
	tiles["eobleft"] = Tile("eobleft", {
		"white": b.eobleft.normal,
		"green": b.eobleft.routed,
		"red": b.eobleft.occupied,
		"yellow": b.eobleft.unknown})
	tiles["eobright"] = Tile("eobright", {
		"white": b.eobright.normal,
		"green": b.eobright.routed,
		"red": b.eobright.occupied,
		"yellow": b.eobright.unknown})
	tiles["eobdown"] = Tile("eobdown", {
		"white": b.eobdown.normal,
		"green": b.eobdown.routed,
		"red": b.eobdown.occupied,
		"yellow": b.eobdown.unknown})
	tiles["eobleftup"] = Tile("eobleftup", {
		"white": b.eobleftup.normal,
		"green": b.eobleftup.routed,
		"red": b.eobleftup.occupied,
		"yellow": b.eobleftup.unknown})
	tiles["diagleft"] = Tile("diagleft", {
		"white": b.diagleft.normal,
		"green": b.diagleft.routed,
		"red": b.diagleft.occupied,
		"yellow": b.diagleft.unknown})
	tiles["diagright"] = Tile("diagright", {
		"white": b.diagright.normal,
		"green": b.diagright.routed,
		"red": b.diagright.occupied,
		"yellow": b.diagright.unknown})
	tiles["turnleftright"] = Tile("turnleftright", {
		"white": b.turnleftright.normal,
		"green": b.turnleftright.routed,
		"red": b.turnleftright.occupied,
		"yellow": b.turnleftright.unknown})
	tiles["turnleftleft"] = Tile("turnleftleft", {
		"white": b.turnleftleft.normal,
		"green": b.turnleftleft.routed,
		"red": b.turnleftleft.occupied,
		"yellow": b.turnleftleft.unknown})
	tiles["turnrightleft"] = Tile("turnrightleft", {
		"white": b.turnrightleft.normal,
		"green": b.turnrightleft.routed,
		"red": b.turnrightleft.occupied,
		"yellow": b.turnrightleft.unknown})
	tiles["turnrightright"] = Tile("turnrightright", {
		"white": b.turnrightright.normal,
		"green": b.turnrightright.routed,
		"red": b.turnrightright.occupied,
		"yellow": b.turnrightright.unknown})

	tiles["turnrightup"] = Tile("turnrightup", {
		"white": b.turnrightup.normal,
		"green": b.turnrightup.routed,
		"red": b.turnrightup.occupied,
		"yellow": b.turnrightup.unknown})

	tiles["turnrightdown"] = Tile("turnrightdown", {
		"white": b.turnrightdown.normal,
		"green": b.turnrightdown.routed,
		"red": b.turnrightdown.occupied,
		"yellow": b.turnrightdown.unknown})

	tiles["turnleftdown"] = Tile("turnleftdown", {
		"white": b.turnleftdown.normal,
		"green": b.turnleftdown.routed,
		"red": b.turnleftdown.occupied,
		"yellow": b.turnleftdown.unknown})

	tiles["turnleftup"] = Tile("turnleftup", {
		"white": b.turnleftup.normal,
		"green": b.turnleftup.routed,
		"red": b.turnleftup.occupied,
		"yellow": b.turnleftup.unknown})

	turnouts = {}
	turnouts["torightleft"] = TurnoutTile("torightleft", 
		{
			"white": b.torightleft.normal.normal,
			"green": b.torightleft.normal.routed,
			"red": b.torightleft.normal.occupied,
			"white-dis": b.torightleft.normal.normaldis,
			"green-dis": b.torightleft.normal.routeddis,
			"red-dis": b.torightleft.normal.occupieddis,
			"yellow": b.torightleft.normal.unknown,
			"yellow-dis": b.torightleft.normal.unknowndis
		},
		{
			"white": b.torightleft.reversed.normal,
			"green": b.torightleft.reversed.routed,
			"red": b.torightleft.reversed.occupied,
			"white-dis": b.torightleft.reversed.normaldis,
			"green-dis": b.torightleft.reversed.routeddis,
			"red-dis": b.torightleft.reversed.occupieddis,
			"yellow": b.torightleft.reversed.unknown,
			"yellow-dis": b.torightleft.reversed.unknowndis
		}
	)

	turnouts["torightright"] = TurnoutTile("torightright", 
		{
			"white": b.torightright.normal.normal,
			"green": b.torightright.normal.routed,
			"red": b.torightright.normal.occupied,
			"white-dis": b.torightright.normal.normaldis,
			"green-dis": b.torightright.normal.routeddis,
			"red-dis": b.torightright.normal.occupieddis,
			"yellow": b.torightright.normal.unknown,
			"yellow-dis": b.torightright.normal.unknowndis
		},
		{
			"white": b.torightright.reversed.normal,
			"green": b.torightright.reversed.routed,
			"red": b.torightright.reversed.occupied,
			"white-dis": b.torightright.reversed.normaldis,
			"green-dis": b.torightright.reversed.routeddis,
			"red-dis": b.torightright.reversed.occupieddis,
			"yellow": b.torightright.reversed.unknown,
			"yellow-dis": b.torightright.reversed.unknowndis
		}
	)

	turnouts["torightrightinv"] = TurnoutTile("torightrightinv", 
		{
			"white": b.torightright.reversed.normal,
			"green": b.torightright.reversed.routed,
			"red": b.torightright.reversed.occupied,
			"white-dis": b.torightright.reversed.normaldis,
			"green-dis": b.torightright.reversed.routeddis,
			"red-dis": b.torightright.reversed.occupieddis,
			"yellow": b.torightright.reversed.unknown,
			"yellow-dis": b.torightright.reversed.unknowndis
		},
		{
			"white": b.torightright.normal.normal,
			"green": b.torightright.normal.routed,
			"red": b.torightright.normal.occupied,
			"white-dis": b.torightright.normal.normaldis,
			"green-dis": b.torightright.normal.routeddis,
			"red-dis": b.torightright.normal.occupieddis,
			"yellow": b.torightright.normal.unknown,
			"yellow-dis": b.torightright.normal.unknowndis
		}
	)

	turnouts["torightup"] = TurnoutTile("torightup", 
		{
			"white": b.torightup.normal.normal,
			"green": b.torightup.normal.routed,
			"red": b.torightup.normal.occupied,
			"white-dis": b.torightup.normal.normaldis,
			"green-dis": b.torightup.normal.routeddis,
			"red-dis": b.torightup.normal.occupieddis,
			"yellow": b.torightup.normal.unknown,
			"yellow-dis": b.torightup.normal.unknowndis
		},
		{
			"white": b.torightup.reversed.normal,
			"green": b.torightup.reversed.routed,
			"red": b.torightup.reversed.occupied,
			"white-dis": b.torightup.reversed.normaldis,
			"green-dis": b.torightup.reversed.routeddis,
			"red-dis": b.torightup.reversed.occupieddis,
			"yellow": b.torightup.reversed.unknown,
			"yellow-dis": b.torightup.reversed.unknowndis
		}
	)

	turnouts["toleftup"] = TurnoutTile("toleftup", 
		{
			"white": b.toleftup.normal.normal,
			"green": b.toleftup.normal.routed,
			"red": b.toleftup.normal.occupied,
			"white-dis": b.toleftup.normal.normaldis,
			"green-dis": b.toleftup.normal.routeddis,
			"red-dis": b.toleftup.normal.occupieddis,
			"yellow": b.toleftup.normal.unknown,
			"yellow-dis": b.toleftup.normal.unknowndis
		},
		{
			"white": b.toleftup.reversed.normal,
			"green": b.toleftup.reversed.routed,
			"red": b.toleftup.reversed.occupied,
			"white-dis": b.toleftup.reversed.normaldis,
			"green-dis": b.toleftup.reversed.routeddis,
			"red-dis": b.toleftup.reversed.occupieddis,
			"yellow": b.toleftup.reversed.unknown,
			"yellow-dis": b.toleftup.reversed.unknowndis
		}
	)

	turnouts["toleftupinv"] = TurnoutTile("toleftup", 
		{
			"white": b.toleftup.reversed.normal,
			"green": b.toleftup.reversed.routed,
			"red": b.toleftup.reversed.occupied,
			"white-dis": b.toleftup.reversed.normaldis,
			"green-dis": b.toleftup.reversed.routeddis,
			"red-dis": b.toleftup.reversed.occupieddis,
			"yellow": b.toleftup.reversed.unknown,
			"yellow-dis": b.toleftup.reversed.unknowndis
		},
		{
			"white": b.toleftup.normal.normal,
			"green": b.toleftup.normal.routed,
			"red": b.toleftup.normal.occupied,
			"white-dis": b.toleftup.normal.normaldis,
			"green-dis": b.toleftup.normal.routeddis,
			"red-dis": b.toleftup.normal.occupieddis,
			"yellow": b.toleftup.normal.unknown,
			"yellow-dis": b.toleftup.normal.unknowndis
		}
	)

	turnouts["torightupinv"] = TurnoutTile("torightupinv", 
		{
			"white": b.torightup.reversed.normal,
			"green": b.torightup.reversed.routed,
			"red": b.torightup.reversed.occupied,
			"white-dis": b.torightup.reversed.normaldis,
			"green-dis": b.torightup.reversed.routeddis,
			"red-dis": b.torightup.reversed.occupieddis,
			"yellow": b.torightup.reversed.unknown,
			"yellow-dis": b.torightup.reversed.unknowndis
		},
		{
			"white": b.torightup.normal.normal,
			"green": b.torightup.normal.routed,
			"red": b.torightup.normal.occupied,
			"white-dis": b.torightup.normal.normaldis,
			"green-dis": b.torightup.normal.routeddis,
			"red-dis": b.torightup.normal.occupieddis,
			"yellow": b.torightup.normal.unknown,
			"yellow-dis": b.torightup.normal.unknowndis
		}
	)

	turnouts["torightdown"] = TurnoutTile("torightdown", 
		{
			"white": b.torightdown.normal.normal,
			"green": b.torightdown.normal.routed,
			"red": b.torightdown.normal.occupied,
			"white-dis": b.torightdown.normal.normaldis,
			"green-dis": b.torightdown.normal.routeddis,
			"red-dis": b.torightdown.normal.occupieddis,
			"yellow": b.torightdown.normal.unknown,
			"yellow-dis": b.torightdown.normal.unknowndis
		},
		{
			"white": b.torightdown.reversed.normal,
			"green": b.torightdown.reversed.routed,
			"red": b.torightdown.reversed.occupied,
			"white-dis": b.torightdown.reversed.normaldis,
			"green-dis": b.torightdown.reversed.routeddis,
			"red-dis": b.torightdown.reversed.occupieddis,
			"yellow": b.torightdown.reversed.unknown,
			"yellow-dis": b.torightdown.reversed.unknowndis
		}
	)

	turnouts["torightdowninv"] = TurnoutTile("torightdowninv", 
		{
			"white": b.torightdown.reversed.normal,
			"green": b.torightdown.reversed.routed,
			"red": b.torightdown.reversed.occupied,
			"white-dis": b.torightdown.reversed.normaldis,
			"green-dis": b.torightdown.reversed.routeddis,
			"red-dis": b.torightdown.reversed.occupieddis,
			"yellow": b.torightdown.reversed.unknown,
			"yellow-dis": b.torightdown.reversed.unknowndis
		},
		{
			"white": b.torightdown.normal.normal,
			"green": b.torightdown.normal.routed,
			"red": b.torightdown.normal.occupied,
			"white-dis": b.torightdown.normal.normaldis,
			"green-dis": b.torightdown.normal.routeddis,
			"red-dis": b.torightdown.normal.occupieddis,
			"yellow": b.torightdown.normal.unknown,
			"yellow-dis": b.torightdown.normal.unknowndis
		}
	)

	turnouts["toleftleft"] = TurnoutTile("toleftleft", 
		{
			"white": b.toleftleft.normal.normal,
			"green": b.toleftleft.normal.routed,
			"red": b.toleftleft.normal.occupied,
			"white-dis": b.toleftleft.normal.normaldis,
			"green-dis": b.toleftleft.normal.routeddis,
			"red-dis": b.toleftleft.normal.occupieddis,
			"yellow": b.toleftleft.normal.unknown,
			"yellow-dis": b.toleftleft.normal.unknowndis
		},
		{
			"white": b.toleftleft.reversed.normal,
			"green": b.toleftleft.reversed.routed,
			"red": b.toleftleft.reversed.occupied,
			"white-dis": b.toleftleft.reversed.normaldis,
			"green-dis": b.toleftleft.reversed.routeddis,
			"red-dis": b.toleftleft.reversed.occupieddis,
			"yellow": b.toleftleft.reversed.unknown,
			"yellow-dis": b.toleftleft.reversed.unknowndis
		}
	)

	turnouts["toleftleftinv"] = TurnoutTile("toleftleftinv", 
		{
			"white": b.toleftleft.reversed.normal,
			"green": b.toleftleft.reversed.routed,
			"red": b.toleftleft.reversed.occupied,
			"white-dis": b.toleftleft.reversed.normaldis,
			"green-dis": b.toleftleft.reversed.routeddis,
			"red-dis": b.toleftleft.reversed.occupieddis,
			"yellow": b.toleftleft.reversed.unknown,
			"yellow-dis": b.toleftleft.reversed.unknowndis
		},
		{
			"white": b.toleftleft.normal.normal,
			"green": b.toleftleft.normal.routed,
			"red": b.toleftleft.normal.occupied,
			"white-dis": b.toleftleft.normal.normaldis,
			"green-dis": b.toleftleft.normal.routeddis,
			"red-dis": b.toleftleft.normal.occupieddis,
			"yellow": b.toleftleft.normal.unknown,
			"yellow-dis": b.toleftleft.normal.unknowndis
		}
	)
	
	turnouts["toleftright"] = TurnoutTile("toleftright", 
		{
			"white": b.toleftright.normal.normal,
			"green": b.toleftright.normal.routed,
			"red": b.toleftright.normal.occupied,
			"white-dis": b.toleftright.normal.normaldis,
			"green-dis": b.toleftright.normal.routeddis,
			"red-dis": b.toleftright.normal.occupieddis,
			"yellow": b.toleftright.normal.unknown,
			"yellow-dis": b.toleftright.normal.unknowndis
		},
		{
			"white": b.toleftright.reversed.normal,
			"green": b.toleftright.reversed.routed,
			"red": b.toleftright.reversed.occupied,
			"white-dis": b.toleftright.reversed.normaldis,
			"green-dis": b.toleftright.reversed.routeddis,
			"red-dis": b.toleftright.reversed.occupieddis,
			"yellow": b.toleftright.reversed.unknown,
			"yellow-dis": b.toleftright.reversed.unknowndis
		}
	)
	
	turnouts["toleftrightinv"] = TurnoutTile("toleftrightinv", 
		{
			"white": b.toleftright.reversed.normal,
			"green": b.toleftright.reversed.routed,
			"red": b.toleftright.reversed.occupied,
			"white-dis": b.toleftright.reversed.normaldis,
			"green-dis": b.toleftright.reversed.routeddis,
			"red-dis": b.toleftright.reversed.occupieddis,
			"yellow": b.toleftright.reversed.unknown,
			"yellow-dis": b.toleftright.reversed.unknowndis
		},
		{
			"white": b.toleftright.normal.normal,
			"green": b.toleftright.normal.routed,
			"red": b.toleftright.normal.occupied,
			"white-dis": b.toleftright.normal.normaldis,
			"green-dis": b.toleftright.normal.routeddis,
			"red-dis": b.toleftright.normal.occupieddis,
			"yellow": b.toleftright.normal.unknown,
			"yellow-dis": b.toleftright.normal.unknowndis
		}
	)
	
	turnouts["toleftdown"] = TurnoutTile("toleftdown", 
		{
			"white": b.toleftdown.normal.normal,
			"green": b.toleftdown.normal.routed,
			"red": b.toleftdown.normal.occupied,
			"white-dis": b.toleftdown.normal.normaldis,
			"green-dis": b.toleftdown.normal.routeddis,
			"red-dis": b.toleftdown.normal.occupieddis,
			"yellow": b.toleftdown.normal.unknown,
			"yellow-dis": b.toleftdown.normal.unknowndis
		},
		{
			"white": b.toleftdown.reversed.normal,
			"green": b.toleftdown.reversed.routed,
			"red": b.toleftdown.reversed.occupied,
			"white-dis": b.toleftdown.reversed.normaldis,
			"green-dis": b.toleftdown.reversed.routeddis,
			"red-dis": b.toleftdown.reversed.occupieddis,
			"yellow": b.toleftdown.reversed.unknown,
			"yellow-dis": b.toleftdown.reversed.unknowndis
		}
	)
	
	turnouts["toleftdowninv"] = TurnoutTile("toleftdowninv", 
		{
			"white": b.toleftdown.reversed.normal,
			"green": b.toleftdown.reversed.routed,
			"red": b.toleftdown.reversed.occupied,
			"white-dis": b.toleftdown.reversed.normaldis,
			"green-dis": b.toleftdown.reversed.routeddis,
			"red-dis": b.toleftdown.reversed.occupieddis,
			"yellow": b.toleftdown.reversed.unknown,
			"yellow-dis": b.toleftdown.reversed.unknowndis
		},
		{
			"white": b.toleftdown.normal.normal,
			"green": b.toleftdown.normal.routed,
			"red": b.toleftdown.normal.occupied,
			"white-dis": b.toleftdown.normal.normaldis,
			"green-dis": b.toleftdown.normal.routeddis,
			"red-dis": b.toleftdown.normal.occupieddis,
			"yellow": b.toleftdown.normal.unknown,
			"yellow-dis": b.toleftdown.normal.unknowndis
		}
	)

	slipswitches = {}
	turnouts["ssleft"] = SlipSwitchTile("ssleft",
		{ # NN
			"white": b.slipleft.nn.normal,
			"green": b.slipleft.nn.routed,
			"red":   b.slipleft.nn.occupied,
			"yellow":   b.slipleft.nn.unknown,
			"white-dis": b.slipleft.nn.normaldis,
			"green-dis": b.slipleft.nn.routeddis,
			"red-dis":   b.slipleft.nn.occupieddis,
			"yellow-dis":   b.slipleft.nn.unknowndis
		},
		{ # NR
			"white": b.slipleft.nr.normal,
			"green": b.slipleft.nr.routed,
			"red":   b.slipleft.nr.occupied,
			"yellow":   b.slipleft.nr.unknown,
			"white-dis": b.slipleft.nr.normaldis,
			"green-dis": b.slipleft.nr.routeddis,
			"red-dis":   b.slipleft.nr.occupieddis,
			"yellow-dis":   b.slipleft.nr.unknowndis
		},
		{ # RN
			"white": b.slipleft.rn.normal,
			"green": b.slipleft.rn.routed,
			"red":   b.slipleft.rn.occupied,
			"yellow":   b.slipleft.rn.unknown,
			"white-dis": b.slipleft.rn.normaldis,
			"green-dis": b.slipleft.rn.routeddis,
			"red-dis":   b.slipleft.rn.occupieddis,
			"yellow-dis":   b.slipleft.rn.unknowndis
		},
		{ # RR
			"white": b.slipleft.rr.normal,
			"green": b.slipleft.rr.routed,
			"red":   b.slipleft.rr.occupied,
			"yellow":   b.slipleft.rr.unknown,
			"white-dis": b.slipleft.rr.normaldis,
			"green-dis": b.slipleft.rr.routeddis,
			"red-dis":   b.slipleft.rr.occupieddis,
			"yellow-dis":   b.slipleft.rr.unknowndis
		}

	)
	turnouts["ssright"] = SlipSwitchTile("ssright",
		{ # NN
			"white": b.slipright.nn.normal,
			"green": b.slipright.nn.routed,
			"red":   b.slipright.nn.occupied,
			"yellow":   b.slipright.nn.unknown,
			"white-dis": b.slipright.nn.normaldis,
			"green-dis": b.slipright.nn.routeddis,
			"red-dis":   b.slipright.nn.occupieddis,
			"yellow-dis":   b.slipright.nn.unknowndis
		},
		{ # NR
			"white": b.slipright.nr.normal,
			"green": b.slipright.nr.routed,
			"red":   b.slipright.nr.occupied,
			"yellow":   b.slipright.nr.unknown,
			"white-dis": b.slipright.nr.normaldis,
			"green-dis": b.slipright.nr.routeddis,
			"red-dis":   b.slipright.nr.occupieddis,
			"yellow-dis":   b.slipright.nr.unknowndis
		},
		{ # RN
			"white": b.slipright.rn.normal,
			"green": b.slipright.rn.routed,
			"red":   b.slipright.rn.occupied,
			"yellow":   b.slipright.rn.unknown,
			"white-dis": b.slipright.rn.normaldis,
			"green-dis": b.slipright.rn.routeddis,
			"red-dis":   b.slipright.rn.occupieddis,
			"yellow-dis":   b.slipright.rn.unknowndis
		},
		{ # RR
			"white": b.slipright.rr.normal,
			"green": b.slipright.rr.routed,
			"red":   b.slipright.rr.occupied,
			"yellow":   b.slipright.rr.unknown,
			"white-dis": b.slipright.rr.normaldis,
			"green-dis": b.slipright.rr.routeddis,
			"red-dis":   b.slipright.rr.occupieddis,
			"yellow-dis":   b.slipright.rr.unknowndis
		}

	)

	bmisc = bitmaps.misc
	misctiles = {}
	misctiles["crossover"] = MiscTile("crossover",
		{
			"white-diagright": b.diagright.normal,
			"green-diagright": b.diagright.routed,
			"red-diagright": b.diagright.occupied,
			"yellow-diagright": b.diagright.unknown,
			"white-diagleft": b.diagleft.normal,
			"green-diagleft": b.diagleft.routed,
			"red-diagleft": b.diagleft.occupied,
			"yellow-diagleft": b.diagleft.unknown,
			"cross": bmisc.cross
		})
	misctiles["handdown"] = MiscTile("handdown",
		{
			"locked" : bmisc.downlocked,
			"unlocked" : bmisc.downunlocked
		})
	misctiles["handup"] = MiscTile("handup",
		{
			"locked" : bmisc.uplocked,
			"unlocked" : bmisc.upunlocked,
		})
	misctiles["crossing"] = MiscTile("crossing",
		{
			"white-main": b.straight.normal,
			"green-main": b.straight.routed,
			"red-main": b.straight.occupied,
			"yellow-main": b.straight.unknown,
			"white-cross": b.diagright.normal,
			"green-cross": b.diagright.routed,
			"red-cross": b.diagright.occupied,
			"yellow-cross": b.diagright.unknown,
		})
	misctiles["indicator"] = MiscTile("indicator",
		{
			"green": bmisc.indicatorg,
			"red": bmisc.indicatorr,
			"out": bmisc.indicatorout,
		})
	misctiles["hilite"] = bmisc.hilite

	b = bitmaps.signals
	signals = {}
	signals["left"] = SignalTile("left", 
		{
			"clear": b.left.green,
			"clear-fleet": b.left.greenfleet,
			"slow-clear": b.left.green,
			"slow-clear-fleet": b.left.greenfleet,
			"medium-clear": b.left.green,
			"medium-clear-fleet": b.left.greenfleet,

			"stop": b.left.red,
			"stop-fleet": b.left.redfleet,

			"approach": b.left.flashyellow,
			"approach-fleet": b.left.flashyellowfleet,
			"approach-slow": b.left.flashyellow,
			"approach-slow-fleet": b.left.flashyellowfleet,
			"approach-medium": b.left.flashyellow,
			"approach-medium-fleet": b.left.flashyellowfleet,
			"advance-approach": b.left.flashyellow,
			"advance-approach-fleet": b.left.flashyellowfleet,
			"medium-approach": b.left.flashyellow,
			"medium-approach-fleet": b.left.flashyellowfleet,
			"slow-approach": b.left.flashyellow,
			"slow-approach-fleet": b.left.flashyellowfleet,

			"restricting": b.left.yellow,
			"restricting-fleet": b.left.yellowfleet,
		})
	signals["leftlong"] = SignalTile("leftlong", 
		{
			"clear": b.leftlong.greenred,
			"clear-fleet": b.leftlong.greenredfleet,
			"slow-clear": b.leftlong.redgreen,
			"slow-clear-fleet": b.leftlong.redgreenfleet,
			"medium-clear": b.leftlong.redgreen,
			"medium-clear-fleet": b.leftlong.redgreenfleet,

			"stop": b.leftlong.red,
			"stop-fleet": b.leftlong.redfleet,

			"approach": b.leftlong.yellowred,
			"approach-fleet": b.leftlong.yellowredfleet,
			"approach-slow": b.leftlong.yellowyellow,
			"approach-slow-fleet": b.leftlong.yellowyellowfleet,
			"approach-medium": b.leftlong.yellowgreen,
			"approach-medium-fleet": b.leftlong.yellowgreenfleet,
			"advance-approach": b.leftlong.yellowred,
			"advance-approach-fleet": b.leftlong.yellowredfleet,
			"medium-approach": b.leftlong.redflashyellow,
			"medium-approach-fleet": b.leftlong.redflashyellowfleet,
			"slow-approach": b.leftlong.redflashyellow,
			"slow-approach-fleet": b.leftlong.redflashyellowfleet,

			"restricting": b.leftlong.redyellow,
			"restricting-fleet": b.leftlong.redyellowfleet,
		})
	signals["right"] = SignalTile("right", 
		{
			"clear": b.right.green,
			"clear-fleet": b.right.greenfleet,
			"slow-clear": b.right.green,
			"slow-clear-fleet": b.right.greenfleet,
			"medium-clear": b.right.green,
			"medium-clear-fleet": b.right.greenfleet,

			"stop": b.right.red,
			"stop-fleet": b.right.redfleet,

			"approach": b.right.flashyellow,
			"approach-fleet": b.right.flashyellowfleet,
			"approach-slow": b.right.flashyellow,
			"approach-slow-fleet": b.right.flashyellowfleet,
			"approach-medium": b.right.flashyellow,
			"approach-medium-fleet": b.right.flashyellowfleet,
			"advance-approach": b.right.flashyellow,
			"advance-approach-fleet": b.right.flashyellowfleet,
			"medium-approach": b.right.flashyellow,
			"medium-approach-fleet": b.right.flashyellowfleet,
			"slow-approach": b.right.flashyellow,
			"slow-approach-fleet": b.right.flashyellowfleet,

			"restricting": b.right.yellow,
			"restricting-fleet": b.right.yellowfleet,
		})
	signals["rightlong"] = SignalTile("rightlong", 
		{
			"clear": b.rightlong.greenred,
			"clear-fleet": b.rightlong.greenredfleet,
			"slow-clear": b.rightlong.redgreen,
			"slow-clear-fleet": b.rightlong.redgreenfleet,
			"medium-clear": b.rightlong.redgreen,
			"medium-clear-fleet": b.rightlong.redgreenfleet,

			"stop": b.rightlong.red,
			"stop-fleet": b.rightlong.redfleet,

			"approach": b.rightlong.yellowred,
			"approach-fleet": b.rightlong.yellowredfleet,
			"approach-slow": b.rightlong.yellowyellow,
			"approach-slow-fleet": b.rightlong.yellowyellowfleet,
			"approach-medium": b.rightlong.yellowgreen,
			"approach-medium-fleet": b.rightlong.yellowgreenfleet,
			"advance-approach": b.rightlong.yellowred,
			"advance-approach-fleet": b.rightlong.yellowredfleet,
			"medium-approach": b.rightlong.redflashyellow,
			"medium-approach-fleet": b.rightlong.redflashyellowfleet,
			"slow-approach": b.rightlong.redflashyellow,
			"slow-approach-fleet": b.rightlong.redflashyellowfleet,

			"restricting": b.rightlong.redyellow,
			"restricting-fleet": b.rightlong.redyellowfleet,
		})

	return tiles, turnouts, slipswitches, signals, misctiles
