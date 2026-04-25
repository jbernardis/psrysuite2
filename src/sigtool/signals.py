import os
import json


class Signals:
	def __init__(self):
		fn = os.path.join(os.getcwd(), "data", "iobits.json")
		with open(fn) as iofp:
			self.iodata = json.loads(iofp.read())

		try:
			self.sigs = {sname: self.iodata["signals"][sname] for sname in self.iodata["signals"] if len(self.iodata["signals"][sname]["aspect"][0]) > 0}
		except KeyError:
			print("no signals in iodata")
			self.sigs = {}

		# for snm, sig in self.sigs.items():
		# 	print("%s: %s" % (snm, str(sig)))

		fn = os.path.join(os.getcwd(), "data", "layout.json")
		with open(fn) as lfp:
			self.layout = json.loads(lfp.read())

		self.sigTypes = {sname: self.layout["signals"][sname]["aspecttype"] for sname in self.layout["signals"].keys()}
		#
		# for snm, stp in self.sigTypes.items():
		# 	print("%s: %s" % (snm, stp))

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
