import logging

class Fifo:
	def __init__(self):
		self.data = {}
		self.nextin = 0
		self.nextout = 0

	def Append(self, data):
		self.data[self.nextin] = data
		self.nextin += 1
		logging.info("FIFO APPEND: %s" % data.toString())

	def Pop(self):
		if self.nextin == self.nextout:
			return None

		result = self.data[self.nextout]
		del self.data[self.nextout]
		self.nextout += 1
		logging.info("FIFO POP: %s" % result.toString())
		return result

	def Peek(self):
		if self.nextin == self.nextout:
			logging.info("FIFO PEEK EMPTY")
			return None

		result = self.data[self.nextout]
		logging.info("FIFO PEEK: %s" % result.toString())
		return result

	def IsEmpty(self):
		return self.nextin == self.nextout
	
	def DumpQueue(self):
		for qx in sorted(self.data.keys()):
			logging.info("%s: (%s)" % (qx, self.data[qx]))
