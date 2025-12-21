import logging


class BlockDelay:
	def __init__(self, rrserver):
		self.blockDelays = rrserver.Get("getfile", {"file": "blockdelay.json"})
		if self.blockDelays is None:
			self.blockDelays = {}
		logging.debug("Retrieved block delay file: %s" % str(self.blockDelays))

	def GetBlockDelay(self, bn, east):
		if bn not in self.blockDelays:
			return 0

		return self.blockDelays[bn][1 if east else 0]
