import wx
import logging
import time


class Script:
	def __init__(self, frame, tr, layout, timerInterval):
		self.frame = frame
		self.train = tr
		self.layout = layout
		self.timer = None
		self.timerInterval = timerInterval
		self.paused = False
		self.sx = None
		self.loco = ""
		self.tm = 1.0
		self.trainlen = 2  # 2 is the minimum train length
		self.executionCompleted = True
		self.stopped = True
		self.initial = True
		self.occupiedBlocks = []
		self.awaitingOS = None
		self.awaitingRte = None
		self.awaitingSignal = None
		self.blocks = ""

		startBlock = tr.GetStartBlock()
		subblks = self.layout.GetSubBlocks(startBlock)
		self.script = [{"start": subblks, "time": tr.GetStartBlockTime()}]

		blocks = []
		sbe, sbw = self.layout.GetStopBlocks(startBlock)
		if tr.IsEast():
			if sbe is not None:
				blocks.append(sbe)
		else:
			if sbw is not None:
				blocks.append(sbw)

		if len(blocks) > 0:
			self.script.append({"blocks": blocks, "time": tr.GetStartBlockTime()})

		for step in tr.GetSteps():
			self.script.append({"os": step["os"], "route": step["route"], "signal": step["signal"], "time": step["time"]})
			block = step["block"]
			sbe, sbw = self.layout.GetStopBlocks(block)
			subblks = self.layout.GetSubBlocks(block)

			blocks = []
			if tr.IsEast():
				if sbw is not None:
					blocks.append([sbw])
			else:
				if sbe is not None:
					blocks.append([sbe])
			blocks.append(subblks)
			if tr.IsEast():
				if sbe is not None:
					blocks.append([sbe])
			else:
				if sbw is not None:
					blocks.append([sbw])
			for b in blocks:
				self.script.append({"blocks": b, "time": step["time"]})

	def GetName(self):
		return self.train.GetTrainID()
	
	def GetLoco(self):
		return self.loco
	
	def SetLoco(self, loco):
		self.loco = loco
	
	def SetTimeMultiple(self, tm):
		self.tm = tm

	def GetTimeMultiple(self):
		return self.tm
	
	def GetTrainLen(self):
		return self.trainlen
	
	def SetTrainLen(self, tlen):
		self.trainlen = tlen

	def GetStatus(self):
		stat = []
		if self.initial:
			return "ready"

		if self.stopped:
			return "Stopped"

		if self.awaitingSignal is not None:
			stat.append("Waiting for signal " + self.awaitingSignal)

		if self.awaitingOS is not None:
			stat.append("Waiting for Route " + self.awaitingOS + ":" + self.awaitingRte)

		if len(stat) == 0:
			if self.IsRunning():
				return "Running  (" + self.blocks + ")"
			elif self.sx is None:
				return "Completed"
			else:
				return "??"
		else:
			return ", ".join(stat)

	def Execute(self):
		if self.IsRunning():
			print("Script is already running")
			return

		self.sx = -1
		self.timer = 0
		self.executionCompleted = False
		self.stopped = False
		self.initial = False

		self.frame.RefreshStatus(self.GetName())

		self.run()

	def markCompleted(self, withError=False):
		self.error = withError
		self.sx = None

		self.executionCompleted = True
		self.frame.ScriptComplete(self.GetName())

	def Stop(self):
		self.stopped = True
		self.markCompleted()

	def IsRunning(self):
		return self.sx is not None and not self.stopped and not self.executionCompleted

	def run(self):
		if self.executionCompleted:
			return

		if self.paused:
			step = self.script[self.sx]
			self.paused = self.CheckSignalAndRoute(step["os"], step["route"], step["signal"])
			if self.paused:
				return
			self.CompleteOSAction()
			self.BringUpRear()
			return

		if self.timer > 0:
			self.timer -= self.timerInterval

		if self.timer > 0:
			# we haven't reached the next interval yet, just return
			return

		self.sx += 1
		if self.sx >= len(self.script):
			self.BringUpRear(1)  # close up the train to a single block
			self.markCompleted()
			return

		step = self.script[self.sx]
		if "start" in step:
			blk = step["start"][0]
			self.occupiedBlocks.append(step["start"])
			self.frame.MonitorBlock(blk, self)
			self.layout.OccupyBlock(step["start"])
			self.timer = step["time"] * self.tm
		elif "blocks" in step:
			self.occupiedBlocks.append(step["blocks"])
			self.layout.OccupyBlock(step["blocks"])
			self.timer = step["time"] * self.tm
		elif "os" in step:
			# {'os': 'BOSWE', 'route': 'BRtB20B21', 'signal': 'C24L', 'time': 5000}
			self.paused = self.CheckSignalAndRoute(step["os"], step["route"], step["signal"])
			if self.paused:
				return
			self.CompleteOSAction()
		else:
			self.markCompleted(withError=True)

		self.BringUpRear()

	def BringUpRear(self, trlen=None):
		if trlen is None:
			trlen = self.trainlen
		while len(self.occupiedBlocks) > trlen:
			self.layout.OccupyBlock(self.occupiedBlocks[0], occupy=False)
			self.occupiedBlocks = self.occupiedBlocks[1:]

	def CheckSignalAndRoute(self, osblk, rte, signm):
		rv = False
		refresh = osblk != self.awaitingOS or rte != self.awaitingRte or signm != self.awaitingSignal

		if self.frame.GetOSRoute(osblk) != rte:
			self.awaitingOS = osblk
			self.awaitingRte = rte
			rv = True
		else:
			self.awaitingOS = None
			self.awaitingRte = None

		if self.frame.GetSignalAspect(signm) == 0:
			self.awaitingSignal = signm
			rv = True
		else:
			self.awaitingSignal = None

		if refresh:
			self.frame.RefreshStatus(self.GetName())
		return rv

	def CompleteOSAction(self):
		step = self.script[self.sx]
		self.occupiedBlocks.append([step["os"]])
		self.layout.OccupyBlock([step["os"]])
		self.timer = step["time"] * self.tm

	def ReportTrainInBlock(self, trid, parms):

		self.layout.ModifyTrain(trid, self.GetName(), parms["east"], self.loco)
		self.frame.MonitorTrain(trid, self)

	def ReportTrain(self, trid, parms):
		self.blocks = ", ".join(reversed(parms["blocks"]))
		self.frame.RefreshStatus(self.GetName())

	def Ticker(self):
		self.run()
