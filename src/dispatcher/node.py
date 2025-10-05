class Node:
	def __init__(self, name, address, status):
		self.name = name
		self.address = address
		self.status = status

	def IsEnabled(self):
		return self.status == 1

	def Name(self):
		return self.name

	def Address(self):
		return self.address

	def SetStatus(self, status):
		self.status = status
