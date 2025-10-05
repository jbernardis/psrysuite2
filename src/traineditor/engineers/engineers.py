class Engineers:
	def __init__(self, rrserver):
		self.RRServer = rrserver
		self.engineers = rrserver.Get("getengineers", {})
		
	def save(self):
		self.RRServer.Post("engineers.txt", "data", self.engineers)	
	
	def getEngineerList(self):
		return sorted(self.engineers)
	
	def add(self, eng):
		if eng in self.engineers:
			return False
		
		self.engineers.append(eng)
		self.engineers = sorted(self.engineers)
		return True
	
	def delete(self, eng):
		try:
			self.engineers.remove(eng)
			return True
		except ValueError:
			return False
