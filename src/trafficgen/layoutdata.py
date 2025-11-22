import json


class LayoutData:
	def __init__(self, rrserver):
		self.rrserver = rrserver
		self.layout = rrserver.Get("getlayout", {})
		self.subblocks = rrserver.Get("getsubblocks", {})
		self.iobits = self.rrserver.Get("getiobits", {})

		if self.layout is None or self.subblocks is None or self.iobits is None:
			self.RRConnected = False
			print("Unable to retrieve layout, subblock and/or iobits information from server")
			return

		self.RRConnected = True

		self.routes = self.layout["routes"]
		self.crossovers = self.layout["crossover"]
		self.blocks = self.layout["blocks"]

	def IsConnected(self):
		return self.RRConnected

	def GetStopBlocks(self, blknm):
		try:
			sbeast = self.blocks[blknm]["sbeast"]
		except KeyError:
			sbeast = None
		try:
			sbwest = self.blocks[blknm]["sbwest"]
		except KeyError:
			sbwest = None

		return sbeast, sbwest

	def GetSubBlocks(self, blknm):
		print("get subblocks for block %s" % blknm)
		try:
			return self.subblocks[blknm]
		except KeyError:
			return [blknm]

	def OccupyBlock(self, blknms, occupy=True):
		reqs = []
		for bname in blknms:
			bi = self.iobits["blocks"][bname]["occupancy"]
			if len(bi[0]) > 0:
				byte = bi[0][0][0]
				bit  = bi[0][0][1]
				nodeaddress = bi[1]

				reqs.append({"setinbit": {"address": "0x%x" % nodeaddress, "byte": [byte], "bit": [bit], "value": [1 if occupy else 0]}})
		for r in reqs:
			self.rrserver.SendRequest(r)

	def ModifyTrain(self, iname, rname, east, loco):
		eastVal = "1" if east else "0"
		req = {"modifytrain": {"iname": iname, "name": rname, "loco": loco, "east": eastVal}}
		print("sending request %s" % str(req))
		self.rrserver.SendRequest(req)

#
	# def IsCrossoverPt(self, osBlk, blk):
	# 	return [osBlk, blk] in self.crossovers
	#
	# def GetRoutesForBlock(self, blknm):
	# 	pass
	# 	# try:
	# 	# 	return self.block2route[blknm]
	# 	# except KeyError:
	# 	# 	return None
	#
	# def GetRouteEnds(self, rname):
	# 	return self.routes[rname]["ends"]
	#
	# def GetRouteSignals(self, rname):
	# 	return self.routes[rname]["signals"]
	#
	# def GetRouteOS(self, rname):
	# 	return self.routes[rname]["os"]
	#
	# def GetBlocks(self):
	# 	return self.blocks
	#
	# def IsBlockEast(self, blknm):
	# 	try:
	# 		return self.blockdir[blknm] == 1
	# 	except KeyError:
	# 		return None
	#
	# def GetSubBlocks(self, blk):
	# 	try:
	# 		return self.subblocks[blk]
	# 	except KeyError:
	# 		return []
	#
	# def GetStopBlocks(self, blk):
	# 	try:
	# 		return self.stopblocks[blk]
	# 	except KeyError:
	# 		return [None, None]
