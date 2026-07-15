
class Signals:
	def __init__(self, rrserver):
		self.iodata = rrserver.Get("getiobits", {})
		if self.iodata is None:
			print("Unable to retrieve iobits from server")
			self.sigs = {}
		else:
			try:
				self.sigs = {sname: self.iodata["signals"][sname] for sname in self.iodata["signals"] if len(self.iodata["signals"][sname]["aspect"][0]) > 0}
			except KeyError:
				print("no signals in iodata")
				self.sigs = {}

		self.layout = rrserver.Get("getlayout", {})
		if self.layout is None:
			print("Unable to retrieve layout information from server")
			self.sigTypes = {}
		else:
			try:
				self.sigTypes = {sname: self.layout["signals"][sname]["aspecttype"] for sname in self.layout["signals"].keys()}
			except KeyError:
				print("Unable to determine signal types")
				self.sigTypes = {}

	def GetAspectBits(self, snm):
		try:
			s = self.sigs[snm]
		except KeyError:
			print("Unknown signal name: %s" % snm)
			return None

		return s["aspect"]

	def GetAspectType(self, snm):
		try:
			s = self.sigTypes[snm]
		except KeyError:
			print("Unknown signal name: %s" % snm)
			return None

		return s

	def SigNames(self):
		return sorted(self.sigs.keys())
