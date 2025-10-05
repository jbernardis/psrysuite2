import wx
import logging
import time


class Script (wx.Frame):
	def __init__(self, parent, script, scriptName, cbCompletion):
		wx.Frame.__init__(self, parent, style=wx.DEFAULT_FRAME_STYLE)
		self.timer = None
		self.sx = None
		self.parent = parent
		self.script = script
		self.scriptName = scriptName
		self.cbCompletion = cbCompletion
		self.executionCompleted = False
		self.stopped = False
		self.error = False
		self.waitingFor = ""
		self.tm = 1 # time multiple

		self.pauseSignal = None
		self.pauseBlock = None
		self.pauseRoute = None
		self.pauseOSBlk = None

		self.occupiedBlocks = []
		self.trainlen = None
		
		self.loco = self.GetLoco()

		self.Bind(wx.EVT_TIMER, self.onTicker)
		self.ticker = wx.Timer(self)

	def GetName(self):
		return self.scriptName
	
	def GetLoco(self):
		for step in self.script:
			cmd, params = list(step.items())[0]
			if cmd == "placetrain":
				try:
					loco = params["loco"]
					return loco
				except:
					return None
		return None
	
	def SetLoco(self, loco):
		for step in self.script:
			cmd, params = list(step.items())[0]
			if cmd == "placetrain":
				try:
					params["loco"] = loco
					self.loco = loco
					return True
				except:
					return False
		return False
	
	def SetTimeMultiple(self, tm):
		self.tm = tm

	def GetTimeMultiple(self):
		return self.tm
	
	def GetTrainLen(self):
		return self.trainlen
	
	def SetTrainLen(self, tlen):
		self.trainlen = tlen

	def GetStatus(self):
		stat = "Loco %s  " % self.loco
		if self.stopped:
			return stat + "Stopped"
		elif self.executionCompleted:
			return stat + "Completed"
		elif self.sx is None:
			return "Ready"
		else:
			sx = self.sx - 1
			if sx < 0:
				sx = 0
			step = self.script[sx]
			cmd, params = list(step.items())[0]
			if cmd in ["placetrain", "movetrain"]:
				return stat + ("Block: %s" % params["block"])
			elif cmd == "waitfor":
				return stat + ("Waiting for: %s" % self.waitingFor)
			else:
				return stat + ("Step %d" % sx)

	def Execute(self):
		if self.script is None:
			self.markCompleted(withError=True)
			return

		self.sx = 0
		self.timer = 0
		self.executionCompleted = False
		self.stopped = False
		self.error = False

		self.run()

	def markCompleted(self, withError=False):
		self.error = withError
		self.sx = None
		self.tm = 1
		self.executionCompleted = True
		self.cbCompletion(self.scriptName)

	def Stop(self):
		self.stopped = True
		self.markCompleted()

	def IsRunning(self):
		return self.sx is not None and not self.stopped and not self.executionCompleted

	def run(self):
		while not self.stopped:
			try:
				step = self.script[self.sx]
			except IndexError:
				self.markCompleted()
				while len(self.occupiedBlocks) > 1:
					self.parent.Request({"removetrain": {"block": self.occupiedBlocks[0]}})
					del(self.occupiedBlocks[0])
				return

			self.sx += 1
			cmd, params = list(step.items())[0]
			if cmd == "placetrain":
				try:
					block = params["block"]
					name = params["name"]
					loco = params["loco"]
				except KeyError:
					self.markCompleted(withError=True)
					return

				try:
					subblock = params["subblock"]
				except KeyError:
					subblock = block

				try:
					direction = params["dir"] == "E"
				except KeyError:
					direction = True

				if self.trainlen is None:
					try:
						self.trainlen = int(params["length"])
					except KeyError:
						self.trainlen = 3

				try:
					duration = int(params["time"])
				except KeyError:
					duration = 1000

				#if direction is not None:
					#self.parent.Request({"blockdir": { "block": block, "dir": direction}})
				req = {"movetrain": {"block": subblock}}
				self.parent.Request(req)

				time.sleep(0.500)
				
				req = {"settrain": {"blocks": [block], "name": name, "loco": loco, "east": "1" if direction else "0"}}
				self.parent.Request(req)
				self.ticker.StartOnce(duration * self.tm)

				self.AddToOccupiedBlocks(subblock)
				return

			elif cmd == "movetrain":
				try:
					block = params["block"]
				except KeyError:
					self.markCompleted(withError=True)
					return

				try:
					duration = int(params["time"])
				except KeyError:
					duration = 1000

				self.parent.Request({"movetrain": {"block": block}})
				self.ticker.StartOnce(duration * self.tm)
				self.AddToOccupiedBlocks(block)
				return

			elif cmd == "wait":
				self.ticker.StartOnce(params["duration"]*self.tm)
				return

			elif cmd == "waitfor":
				self.pauseSignal = self.pauseBlock = self.pauseRoute = self.pauseOSBlk = None
				if "signal" in params:
					self.pauseSignal = params["signal"]
				if "block" in params:
					self.pauseBlock = params["block"]
				if "route" in params:
					self.pauseRoute = params["route"]
					self.pauseOSBlk = params["os"]
				if self.CheckPause():  # a return of True indicates we are blocked
					self.parent.PauseScript(self)
					return
			
			else:
				logging.error("Unknown command in trafficgen script: (%s) - ignoring" % cmd)

	def AddToOccupiedBlocks(self, bn):
		self.occupiedBlocks.append(bn)
		while len(self.occupiedBlocks) > self.trainlen:
			self.parent.Request({"removetrain": {"block": self.occupiedBlocks[0]}})
			del(self.occupiedBlocks[0])

	def RemoveTrain(self):
		for b in self.occupiedBlocks:
			self.parent.Request({"removetrain": {"block": b}})
		self.occupiedBlocks = []
		self.sx = None
		self.stopped = False
		self.executionCompleted = False


	def Resume(self):
		logging.debug("resumption of script %s" % self.GetName())
		self.run()

	def onTicker(self, _):
		self.run()

	def CheckPause(self):
		rv = False
		w = []
		if self.pauseSignal:
			if self.parent.SignalAspect(self.pauseSignal) == 0:
				w.append("Signal %s" % self.pauseSignal)
				rv = True  # paused because signal is red

		if self.pauseBlock:
			if self.parent.BlockOccupied(self.pauseBlock):
				rv = True   # paused because block is occupied
				w.append("Block(s) occupied %s" % str(self.pauseBlock))

		if self.pauseRoute and self.pauseOSBlk:
			if self.parent.NotOSRoute(self.pauseOSBlk, self.pauseRoute):
				rv = True  # paused because wrong route is selected
				w.append("OS/Route %s/%s" % (self.pauseOSBlk, self.pauseRoute))

		self.waitingFor = ", ".join(w)
		return rv
