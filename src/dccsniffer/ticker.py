import threading


class Ticker():
	def __init__(self, parent, interval=5000):
		self.parent = parent
		self.interval = float(interval)/1000.0
		self.forever = False

	def start(self):
		self.forever = True
		self.AtInterval()

	def kill(self):
		self.forever = False

	def AtInterval(self):
		if self.forever:
			threading.Timer(self.interval, self.AtInterval).start()
			self.parent.raiseIntervalEvent()
