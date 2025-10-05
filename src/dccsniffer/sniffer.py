import threading
import serial
import logging
import time


class Sniffer(threading.Thread):
	def __init__(self, parent):
		threading.Thread.__init__(self)
		self.tty = None
		self.baud = None
		self.port = None
		self._isRunning = False
		self.parent = parent

	def connect(self, tty):
		self.tty = tty
		try:
			self.port = serial.Serial(port=self.tty, baudrate=115200, bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_TWO, timeout=1)
		except serial.SerialException:
			self.port = None
			raise
		
	def isConnected(self):
		return self.port is not None
	
	def kill(self):
		self._isRunning = False

	def isRunning(self):
		return self._isRunning

	def run(self):
		self._isRunning = True
		while self._isRunning:
			if self.port is None or not self.port.is_open:
				self._isRunning = False
			else:
				try:
					c = self.port.read_until()
				except serial.SerialException:
					self.port = None
					self._isRunning = True
				
				if len(c) != 0:
					try:
						s = str(c, 'UTF-8')
					except:
						logging.info("unable to convert DCC message to string: (" + s + ")")
					else:
						p = s.split()
						if len(p) < 3:
							logging.warning("received unexpected DCC message: %s" % s)
						else:
							req = {
								"cmd": "dccspeed",
								"loco": "%d" % int(p[1]), # strip off any leading zeroes
								"speed": p[2],
								"stype": p[0]
							}

							self.parent.raiseDCCEvent(req)
				else:
					time.sleep(0.0001)

		try:
			self.port.close()
		except:
			pass
				
		logging.info("DCC sniffer ended execution")


