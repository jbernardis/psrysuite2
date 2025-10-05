import json
import os


class Schedule():
	def __init__(self):
		self.schedule = []
		self.extras = []

		self.ox = 0

	def getSchedule(self):
		return self.schedule

	def getExtras(self):
		return self.extras

	def isExtraTrain(self, tid):
		return tid in self.extras

	def getTid(self, tx):
		if tx < 0 or tx >= len(self.schedule):
			return None

		return self.schedule[tx]

	def __len__(self):
		return len(self.schedule)

	def __iter__(self):
		self.ox = 0
		return self

	def __next__(self):
		if self.ox >= len(self.schedule):
			raise StopIteration

		rv = self.schedule[self.ox]
		self.ox += 1
		return rv

	def setNewSchedule(self, no):
		self.schedule = [t for t in no]

	def setNewExtras(self, nex):
		self.extras = [t for t in nex]

	def save(self, fn, rrserver):
		j = {"schedule": self.schedule, "extras": self.extras}
		rc = rrserver.Post(fn, os.path.join("data", "schedules"), j)
		return rc < 400

	def load(self, fn, rrserver):
		j = rrserver.Get("getfile", {"dir": os.path.join("data", "schedules"), "file": fn})
		if j is None:
			self.schedule = []
			self.extras = []
			return False

		self.schedule = [t for t in j["schedule"]]
		self.extras = [t for t in j["extras"]]
		return True