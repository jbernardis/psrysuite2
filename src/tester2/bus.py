import serial
import time

MAXTRIES = 5


def setBit(dbyte, dbit, val):
	if val != 0:
		return (dbyte | (1 << 7-dbit)) & 0xff
	else:
		return (dbyte & ~(1 << 7-dbit)) & 0xff


def getBit(dbyte, dbit):
	if dbit < 0 or dbit > 7:
		# bit index is out of range
		return 0
	mask = 1 << (7-dbit)
	b = int(bytes([dbyte]).hex(), 16)
	return 1 if b & mask != 0 else 0


class Bus:
	def __init__(self, tty):
		self.initialized = False
		self.tty = tty
		self.byteTally = {}
		self.lastUsed = {}
		self.port = None
		self.error = None

	def Connect(self):
		self.error = None
		try:
			self.port = serial.Serial(port=self.tty,
					baudrate=19200,
					bytesize=serial.EIGHTBITS,
					parity=serial.PARITY_NONE,
					stopbits=serial.STOPBITS_ONE, 
					timeout=0)

		except serial.SerialException as e:
			self.port = None
			self.initialized = True
			self.error = str(e)
			return

		self.initialized = True

	def Error(self):
		return self.error
		
	def isOpen(self):
		return self.port is not None

	def close(self):
		if self.port is None:
			return 
		
		self.port.close()
		self.port = None

	def sendRecv(self, address, outbuf, nbytes):
		if not self.initialized:
			return None
		#
		# try:
		# 	lastused = self.lastUsed[address]
		# except:
		# 	lastused = [None for _ in range(nbytes)]
		# 	self.lastUsed[address] = lastused

		sendBuffer = [address]

		outbuf = list(reversed(outbuf))

		sendBuffer.extend(outbuf)
		
		self.port.write(sendBuffer)

		tries = 0
		inbuf = []
		remaining = nbytes
		while tries < MAXTRIES and remaining > 0:
			b = self.port.read(remaining)
			if len(b) == 0:
				tries += 1
				time.sleep(0.0001)
			else:
				tries = 0
				inbuf.extend([bytes([b[i]]) for i in range(len(b))])
				remaining = nbytes-len(inbuf)
				
		if len(inbuf) != nbytes:
			return None   # [b'\x00'] * nbytes
		else:
			return inbuf
