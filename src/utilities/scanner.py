import os
import sys
import serial
import time


scannerPort = serial.Serial(
	port="COM3",
	baudrate=9600,
	bytesize=serial.EIGHTBITS,
	parity=serial.PARITY_NONE,
	stopbits=serial.STOPBITS_ONE,
	timeout=0.5
)

train = None
loco = None
engineer = None
trainScanTime = None

try:
	while True:

		scanDataRaw = scannerPort.readline()

		if scanDataRaw:
			lastScanTime = int(time.time())
			if trainScanTime is None:
				expired = True
			else:
				expired = lastScanTime > trainScanTime + 20
			scanData = scanDataRaw.decode('utf-8').strip()
			print("Scanned data: \"%s\"" % scanData)

			if scanData.startswith("TRAIN: "):
				train = scanData[7:].strip()
				loco = None
				engineer = None
				trainScanTime = int(time.time())
				print("train scan time = %d" % trainScanTime)

			elif scanData.startswith("LOCOMOTIVE: "):
				loco = scanData[12:].strip()
				if train is not None and not expired:
					msg = {"assigntrain": {"name": train, "loco": loco}}
					print("loco message - %s" % str(msg))
					trainScanTime = lastScanTime  # keep the train scan current as long as were scanning other data

			elif scanData.startswith("ENGINEER: "):
				engineer = scanData[10:].strip()
				if train is not None and not expired:
					msg = {"assigntrain": {"name": train, "engineer": engineer}}
					print(" eng message - %s" % str(msg))
					trainScanTime = lastScanTime  # keep the train scan current as long as were scanning other data

		time.sleep(0.1)

except Exception as e:
	scannerPort.close()
