class Node:
	def __init__(self, name, address, status, ecount):
		self.name = name
		self.address = address
		self.status = status
		self.ecount = ecount

	def IsEnabled(self):
		return self.status == 1

	def Name(self):
		return self.name

	def Address(self):
		return self.address

	def ErrorCount(self):
		return self.ecount

	def Status(self):
		return self.status

	def SetStatus(self, status, ecount):
		self.status = status
		self.ecount = ecount
