import logging
from typing import Any

'''
DISPATCH = 10
DISPLAY  = 11
ATC      = 30
AR       = 40
'''

functions = [ "DISPATCH", "DISPLAY", "ATC", "AR", "NODE" ]


class ClientList:
	def __init__(self, parent):
		self.sids = []
		self.skts = []
		self.functions = []
		self.locales = []
		self.clientList = []
		self.functionLists = {}
		self.nodeAddrs = []
		self.nodeClientList = {}
		self.nonNodeClientList = []

	def AddClient(self, addr, skt, sid):
		if addr in self.clientList:
			return

		self.clientList.append(addr)
		self.sids.append(sid)
		self.skts.append(skt)
		self.functions.append("")
		self.locales.append("")
		self.nodeAddrs.append(None)
		self.UpdateFunctionLists()
		
	def GetClients(self):
		cl = []
		for x in range(len(self.sids)):
			if self.functions[x] == "NODE":
				adr = self.nodeAddrs[x]
				f = None if adr is None else "NODE (%s)" % adr
			else:
				f = self.functions[x]
			if f is not None:
				cl.append([self.sids[x], f, self.clientList[x][0], self.clientList[x][1], self.locales[x]])
		return cl
		
	def SetSessionFunction(self, sid, function, locale, nodeaddr):
		try:
			index = self.sids.index(sid)
		except ValueError:
			return
		
		self.functions[index] = function
		self.locales[index] = locale
		self.UpdateFunctionLists()
		self.nodeAddrs[index] = None
		if function == "NODE":
			self.nodeAddrs[index] = nodeaddr
			# make sure that no other session points to this same node address.  This could happen if the
			# node goes down and then comes back up with a new session id
			indices = [i for i, x in enumerate(self.nodeAddrs) if x == nodeaddr]
			for i in indices:
				if i != index:  # no action needed for the new session
					self.DelClient(self.clientList[i])

	def GetNodeSocketAtAddress(self, addr):
		for i in range(len(self.nodeAddrs)):
			if addr == self.nodeAddrs[i]:
				return self.clientList[i], self.skts[i]

		return None, None

	def HasFunction(self, function):
		return function in self.functions

	def GetFunctionAddress(self, function, locale=None):
		cl = []
		for i in range(len(self.clientList)):
			if function == self.functions[i] and (locale is None or locale == self.locales[i]):
				cl.append((self.clientList[i], self.skts[i]))

		return cl

	def GetNodeAddresses(self, invert=False):
		if invert:
			cl = []  # if inverted, this is just a list of addresses for non-Node clients
		else:
			cl = {}  # otherwise, this is a distionary of node sockets indexed by the node address
		for i in range(len(self.clientList)):
			if invert:
				if self.functions[i] != "NODE":
					cl.append((self.clientList[i], self.skts[i]))
			else:
				if self.functions[i] == "NODE":
					cl[self.nodeAddrs[i]] = (self.clientList[i], self.skts[i])

		return cl

	def UpdateFunctionLists(self):
		self.functionLists = {}
		for f in functions:
			if f != "NODE":
				self.functionLists[f] = self.GetFunctionAddress(f)
		self.nodeClientList = self.GetNodeAddresses()
		self.nonNodeClientList = self.GetNodeAddresses(invert=True)

	def NodeClientList(self):
		return self.nodeClientList

	def NonNodeClientList(self):
		return self.nonNodeClientList

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
		del(self.nodeAddrs[index])

		self.UpdateFunctionLists()
