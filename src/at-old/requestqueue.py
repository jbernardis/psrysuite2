
class RequestQueue:
	def __init__(self, parent):
		self.parent = parent
		self.queue = []
		
		self.waitingForTurnout = None
		
	def Append(self, msg):
		if self.waitingForTurnout is None:
			if list(msg.keys())[0] == "turnout":
				self.waitingForTurnout = msg["turnout"]["name"]
			self.parent.Request(msg)
		else:  # cant send anything until we get a response for outstanding turnout
			self.queue.append(msg)
			
	def Resume(self, toName):
		if self.waitingForTurnout is not None:
			if self.waitingForTurnout == toName:
				self.waitingForTurnout = None
			else:
				return
			
		while len(self.queue) > 0 and self.waitingForTurnout is None:
			msg = self.queue[0]
			self.parent.Request(msg)
			
			if list(msg.keys())[0] == "turnout":
				self.waitingForTurnout = msg["turnout"]["name"]
				
			del(self.queue[0])
		
			