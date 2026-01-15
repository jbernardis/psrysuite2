import logging
'''
DISPATCH = 10
DISPLAY  = 11
ATC      = 30
AR       = 40
'''

functions = [ "DISPATCH", "DISPLAY", "ATC", "AR" ]

class ClientList:
	def __init__(self, parent):
		self.sids = []
		self.skts = []
		self.functions = []
		self.locales = []
		self.clientList = []
		self.functionLists = {}

	def AddClient(self, addr, skt, sid):
		if addr in self.clientList:
			return

		logging.info("Adding new client from %s:%s" % (addr[0], addr[1]))
		self.clientList.append(addr)
		self.sids.append(sid)
		self.skts.append(skt)
		self.functions.append("")
		self.locales.append("")
		self.UpdateFunctionLists()
		
	def GetClients(self):
		return [[self.sids[x], self.functions[x], self.clientList[x][0], self.clientList[x][1], self.locales[x]] for x in range(len(self.sids))]
		
	def SetSessionFunction(self, sid, function, locale):
		try:
			index = self.sids.index(sid)
		except ValueError:
			return
		
		self.functions[index] = function
		self.locales[index] = locale
		self.UpdateFunctionLists()

	def HasFunction(self, function):
		return function in self.functions

	def GetFunctionAddress(self, function, locale=None):
		cl = []
		for i in range(len(self.clientList)):
			if function == self.functions[i] and (locale is None or locale == self.locales[i]):
				cl.append((self.clientList[i], self.skts[i]))
			
		return cl
	
	def UpdateFunctionLists(self):
		self.functionLists = {}
		for f in functions:
			self.functionLists[f] = self.GetFunctionAddress(f)
			
	def GetFunctionClients(self, flist):
		clients = []
		for f in flist:
			try:
				clients.extend(self.functionLists[f])
			except KeyError:
				pass
		return clients

	def GetLocaleClients(self, locale):
		cl = []
		for i in range(len(self.locales)):
			if functions[i] == "DISPLAY":
				if locale == self.locales[i]:
					cl.append((self.clientList[i], self.skts[i]))
			else:
				cl.append((self.clientList[i], self.skts[i]))

		return cl

	def GetFunctionAtAddress(self, address):
		for i in range(len(self.clientList)):
			if self.clientList[i] == address:
				return self.functions[i]
			
		return None
	
	def Count(self):
		return len(self.clientList)

	def DelClient(self, addr):
		logging.info("Removing client with address %s:%s" % (addr[0], addr[1]))
		try:
			index = self.clientList.index(addr)
		except ValueError:
			return

		del(self.clientList[index])
		del(self.sids[index])
		del(self.skts[index])
		del(self.functions[index])
		del(self.locales[index])
		self.UpdateFunctionLists()
