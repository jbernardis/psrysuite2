import os
import sys
import serial
import time
import logging

cmdFolder = os.getcwd()
if cmdFolder not in sys.path:
	sys.path.insert(0, cmdFolder)

fn = "scanner"
ofp = open(os.path.join(os.getcwd(), "output", "%s.out" % fn), "w")
efp = open(os.path.join(os.getcwd(), "output", "%s.err" % fn), "w")

sys.stdout = ofp
sys.stderr = efp

from dispatcher.settings import Settings
from dispatcher.rrserver import RRServer

settings = Settings()

logLevels = {
	"DEBUG": logging.DEBUG,
	"INFO": logging.INFO,
	"WARNING": logging.WARNING,
	"ERROR": logging.ERROR,
	"CRITICAL": logging.CRITICAL,
}

l = settings.debug.loglevel
if l not in logLevels:
	print("unknown logging level: %s.  Defaulting to DEBUG" % l, file=sys.stderr)
	l = "DEBUG"

loglevel = logLevels[l]

logging.basicConfig(filename=os.path.join(os.getcwd(), "logs", "%s.log" % fn), filemode='w',
					format='%(asctime)s %(message)s', level=loglevel)

scannerPort = serial.Serial(
	port=settings.scanner.tty,
	baudrate=9600,
	bytesize=serial.EIGHTBITS,
	parity=serial.PARITY_NONE,
	stopbits=serial.STOPBITS_ONE,
	timeout=0.5
)

logging.debug(f"Connected to port: {scannerPort.port}")

train = None
loco = None
engineer = None

rrServer = RRServer()
rrServer.SetServerAddress(settings.ipaddr, settings.serverport)
try:
	while True:
		scanDataRaw = scannerPort.readline()

		if scanDataRaw:
			scanData = scanDataRaw.decode('utf-8').strip()
			logging.debug("Scanned data: \"%s\"" % scanData)

			if scanData.startswith("TRAIN: "):
				train = scanData[7:].strip()
				loco = None
				engineer = None

			elif scanData.startswith("LOCOMOTIVE: "):
				loco = scanData[12:].strip()
				if train is not None:
					rrServer.SendRequest({"assigntrain": {"name": train, "loco": loco}})

			elif scanData.startswith("ENGINEER: "):
				engineer = scanData[10:].strip()
				if train is not None:
					rrServer.SendRequest({"assigntrain": {"name": train, "engineer": engineer}})

		time.sleep(0.1)

except Exception as e:
	print("exception occured: %s" % str(e), flush=True)
	logging.debug("Exception==> %s <==" % str(e))
	scannerPort.close()

logging.debug("Scanner process exiting")
