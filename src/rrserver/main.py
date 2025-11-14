import os, sys


cmdFolder = os.getcwd()
if cmdFolder not in sys.path:
	sys.path.insert(0, cmdFolder)

lfn = os.path.join(os.getcwd(), "logs", "rrserver.log")

import logging
import logging.handlers
from dispatcher.settings import Settings
from dispatcher.constants import REPLACE
should_roll_over = os.path.isfile(lfn)

settings = Settings()


logLevels = {
	"DEBUG":	logging.DEBUG,
	"INFO":		logging.INFO,
	"WARNING":	logging.WARNING,
	"ERROR":	logging.ERROR,
	"CRITICAL":	logging.CRITICAL,
}

l = settings.debug.loglevel
if l not in logLevels:
	print("unknown logging level: %s.  Defaulting to DEBUG" % l, file=sys.stderr)
	l = "DEBUG"
	
loglevel = logLevels[l]

handler = logging.handlers.RotatingFileHandler(lfn, mode='a', backupCount=5)

logging.basicConfig(format='%(asctime)s %(message)s', level=loglevel, handlers=[handler])
console = logging.StreamHandler()
console.setLevel(loglevel)
formatter = logging.Formatter('%(asctime)s: %(levelname)-8s %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)

if should_roll_over:
	handler.doRollover()

ofp = open(os.path.join(os.getcwd(), "output", "rrserver.out"), "w")
efp = open(os.path.join(os.getcwd(), "output", "rrserver.err"), "w")

sys.stdout = ofp
sys.stderr = efp


import json
import socket
import time
import queue
import threading

from subprocess import Popen

from rrserver.bus import Bus
from rrserver.railroad import Railroad
from rrserver.httpserver import HTTPServer
from rrserver.sktserver import SktServer
from rrserver.routedef import RouteDef

from rrserver.clientlist import ClientList
from rrserver.trainlist import TrainList
from rrserver.dccserver import DCCHTTPServer

# from dispatcher.constants import RegAspects


class ServerMain:
	def __init__(self):
		self.socketServer = None
		self.dispServer = None
		
		logging.info("PSRY Suite - Railroad server starting %s" % ("" if not settings.rrserver.simulation else " - simulation mode"))
		logging.info("Sending logging output  to %s" % lfn)
		
		self.commandsSeen = []
		
		self.pidAR = None
		self.pidADV = None
		self.DCCSniffer = None
		self.timeValue = None
		self.rrBus = None
		self.DCCServer = None
		self.firstInterval = True
		self.clockStatus = 2
		self.busInterval = settings.rrserver.businterval
		self.snapshotLoaded = False
		
		self.cmdQ = queue.Queue()

		self.routeDefs = {}
		self.CrossoverPoints = []

		hostname = socket.gethostname()
		self.ip = socket.gethostbyname(hostname)

		self.clients = {}

		if settings.ipaddr is not None:
			if self.ip != settings.ipaddr:
				logging.info("Using configured IP Address (%s) instead of retrieved IP Address: (%s)" % (settings.ipaddr, self.ip))
				self.ip = settings.ipaddr

		logging.info("Creating railroad object")
		self.rr = Railroad(self, self.rrEventReceipt, settings)
		self.clientList = ClientList(self)
		self.trainList = TrainList(self)
		
		self.Initialize()

	def Initialize(self):
		self.CreateDispatchTable()
		try:
			self.dispServer = HTTPServer(self.ip, settings.serverport, self.dispCommandReceipt, self, self.rr)
		except Exception as e:
			logging.error("Unable to Create HTTP server for IP address %s (%s)" % (self.ip, str(e)))
			self.Shutdown()
			
		logging.info("HTTP Server created")

		logging.info("Starting Socket server at address: %s:%d" % (self.ip, settings.socketport))
		self.socketServer = SktServer(self.ip, settings.socketport, self.socketEventReceipt)
		self.socketServer.start()
		
		logging.info("socket server started - starting DCC HTTP Server")

		if not settings.rrserver.simulation:
			logging.info("Starting DCC Server")		
			continueInit = self.StartDCCServer()		
		else:
			logging.info("DCC HTTP Server not started in simulation mode")
			continueInit = True
			
		if continueInit:
			self.rr.Initialize()
			self.rr.SetSnapshotLimit(settings.rrserver.snapshotlimit)
		else:
			self.queueCmd({"cmd": ["failedstart"]})

	def DelayedStartup(self, _):
		if not settings.rrserver.simulation:
			self.rrBus = Bus(settings.rrserver.rrtty)
			self.rr.setBus(self.rrBus)
			pname = os.path.join(os.getcwd(), "dccsniffer", "main.py")
			if settings.dccsniffer.enable:
				self.DCCSniffer = Popen([sys.executable, pname])
				pid = self.DCCSniffer.pid
				logging.info("started DCC sniffer process as PID %d" % pid)
			else:
				logging.info("start DCC sniffer process skipped")

		self.rr.DelayedStartup()

	def StartDCCServer(self):
		self.DCCServer = DCCHTTPServer(settings.ipaddr, settings.dccserverport, settings.rrserver.dcctty)
		if not self.DCCServer.IsConnected():
			logging.error("Failed to open DCC bus on device %s.  Exiting..." % settings.rrserver.dcctty)
			return False
		else:
			logging.info("DCC HTTP server successfully started")
			return True

	def socketEventReceipt(self, cmd):
		logging.info("received socket connection request: %s" % str(cmd))
		self.cmdQ.put(cmd)

	def queueCmd(self, cmd):
		logging.info("queueing command: %s" % str(cmd))
		self.cmdQ.put(cmd)

	def NewClient(self, cmd):
		if not self.snapshotLoaded:
			if settings.rrserver.autoloadsnapshot:
				self.rr.LoadSnapshot(None)
			self.snapshotLoaded = True

		addr = cmd["addr"]
		skt = cmd["socket"]
		sid = cmd["SID"]
		logging.info("New Client connecting from address: %s:%s" % (addr[0], addr[1]))
		self.socketServer.sendToOne(skt, addr, {"sessionID": sid})
		self.clients[addr] = [skt, sid]
		self.clientList.AddClient(addr, skt, sid, None)

	def DelClient(self, cmd):
		addr = cmd["addr"]
		logging.info("Disconnecting Client from address: %s:%s" % (addr[0], addr[1]))
		try:
			del self.clients[addr]
		except KeyError:
			pass
		
		f = self.clientList.GetFunctionAtAddress(addr)
		self.clientList.DelClient(addr)
		
		if f == "DISPATCH":
			self.deleteClients(["AR", "ADVISOR", "ATC"])
			self.pidAR = None
			self.pidADV = None
					
	def deleteClients(self, clist):
		for cname in clist:
			addrList = self.clientList.GetFunctionAddress(cname)
			for addr, _ in addrList:
				self.socketServer.deleteSocket(addr)
				
	def GetSessions(self):
		return self.clientList.GetClients()

	def refreshClient(self, addr, skt):
		if self.timeValue is not None:
			m = {"clock": [{ "value": self.timeValue, "status": self.clockStatus}]}
			self.socketServer.sendToOne(skt, addr, m)

		for m in self.rr.GetCurrentValues():
			self.socketServer.sendToOne(skt, addr, m)

		for opt, val in self.rr.GetControlOptions().items():
			m = {"control": [{"name": opt, "value": val}]}
			self.socketServer.sendToOne(skt, addr, m)

		nv = self.rr.GetNodeStatuses()
		for addr, name, stat in nv:
			m = {"nodestatus":{"address": addr, "name": name, "enabled": stat}}
			self.socketServer.sendToOne(skt, addr, m)

		self.socketServer.sendToOne(skt, addr, {"end": {}})

	def sendTrainInfo(self, addr, skt):
		for m in self.trainList.GetSetTrainCmds():
			self.socketServer.sendToOne(skt, addr, m)

		self.socketServer.sendToOne(skt, addr, {"end": {"type": "trains"}})

	def rrEventReceipt(self, cmd):
		self.socketServer.sendToAll(cmd)

	def dispCommandReceipt(self, cmd): # thread context
		#logging.info("HTTP Event: %s" % str(cmd))
		self.cmdQ.put(cmd)

	def Alert(self, msg, locale=None):
		msg = {"alert": {"msg": msg}}
		if locale is not None:
			msg["alert"]["locale"] = locale
		self.socketServer.sendToAll(msg)

	def Advice(self, msg, locale=None):
		msg = {"advice": {"msg": msg}}
		if locale is not None:
			msg["advice"]["locale"] = locale
		self.socketServer.sendToAll(msg)

	def CreateDispatchTable(self):					
		self.dispatch = {
			"interval": 	self.DoInterval,
			"clock":    	self.DoClock,
			
			"newclient":	self.NewClient,
			"delclient":	self.DelClient,
			"identify": 	self.DoIdentify,
			"refresh":		self.DoRefresh,

			"fleet":		self.DoFleet,
			"control":		self.DoControl,
			
			# "settrain":		self.DoSetTrain,
			# "deletetrain":	self.DoDeleteTrain,
			"modifytrain":	self.DoModifyTrain,
			"trainreverse":	self.DoTrainReverse,
			"trainreorder":	self.DoTrainReorder,
			"trainsplit":	self.DoTrainSplit,
			"trainmerge":	self.DoTrainMerge,
			"trainswap":	self.DoTrainSwap,
			# "movetrain":	self.DoMoveTrain,
			# "removetrain":	self.DoRemoveTrain,
			# "traincomplete":		self.DoTrainComplete,
			# "trainblockorder":		self.DoTrainBlockOrder,
			# "assigntrain":  self.DoAssignTrain,
			# "checktrains":  self.DoCheckTrains,
			
			"signalclick":   	self.DoSignalClick,
			# "signallock":	self.DoSignalLock,
			"siglever":		self.DoSigLever,
			# "sigleverled":	self.DoSigLeverLED,
			"turnoutclick":  	self.DoTurnoutClick,
			"clearlocks":	self.DoClearLocks,
			# "turnoutlever":	self.DoTurnoutLever,
			# "setroute": 	self.DoSetRoute,
			"nxbutton":		self.DoNXButton,
			# "blockdir":		self.DoBlockDir,
			# "blockdirs":	self.DoBlockDirs,
			# "blockclear":	self.DoBlockClear,
			# "indicator":	self.DoIndicator,
			"setrelay":		self.DoSetRelay,
			"handswitch":	self.DoHandSwitch,
			# "districtlock":	self.DoDistrictLock,
			
			"close":		self.DoClose,			
			"advice":		self.DoAdvice,
			"alert":		self.DoAlert,
			"server":		self.DoServer,
			
			# "autorouter":	self.DoAutorouter,
			# "ar":			self.DoAR,
			# "atc":			self.DoATC,
			# "atcstatus":	self.DoATCStatus,

			"loadsnapshot":	self.DoLoadSnapshot,

			"debug":		self.DoDebug,
			"debugflags":	self.DoDebugFlags,
			"simulate": 	self.DoSimulate,
			"ignore": 		self.DoIgnore,

			"dccspeed":		self.DoDCCSpeed,
			"dccspeeds": 	self.DoDCCSpeeds,

			"quit":			self.DoQuit,
			"delayedstartup":
							self.DelayedStartup,
			"reopen":		self.DoReopen,
			"enablenode":	self.DoEnableNode
		}

	def ProcessCommand(self, cmd):
		try:
			verb = cmd["cmd"][0]
		except KeyError:
			verb = None

		if verb is None:
			logging.error("Command without cmd parameter")
			return

		if verb == "failedstart":
			logging.info("received failed start command")
			self.forever = False
			return 
		
		if not self.forever:
			return
		
		if verb != "interval":
			try:
				jstr = json.dumps(cmd)
			except:
				jstr = str(cmd)
			logging.debug("HTTP Cmd receipt: %s" % jstr)

		try:
			handler = self.dispatch[verb]
		except KeyError:
			logging.error("Unknown command: %s" % verb)
		else:
			handler(cmd)
			# try:
			# 	handler(cmd)
			# except Exception as e:
			# 	logging.error("Exception %s processing command %s" % (str(e), verb))
			# 	logging.error("%s" % str(cmd))

	def DoInterval(self, _):
		if self.pause > 0:
			'''
			no I/O while pause is active
			'''
			self.pause -= 1
			return 
		
		self.rr.OutIn()
		if self.firstInterval:
			self.DelayedStartup(None)
			logging.debug("After first out/in: %s" % self.rr.DumpN20())
			self.firstInterval = False

	def DoSigLever(self, cmd):
		p = {tag: cmd[tag][0] for tag in cmd if tag != "cmd"}
		resp = {"siglever": [p]}
		self.socketServer.sendToAll(resp)

	def DoSigLeverLED(self, cmd):
		try:
			lvrname = cmd["name"][0]
		except KeyError:
			lvrname = None
		try:
			state = cmd["state"][0]
		except KeyError:
			state = None

		if lvrname is None:
			logging.error("SigLeverLED command without lever name - ignoring")
			return

		if lvrname.endswith(".lvr"):
			lvrname = lvrname[:-4]

		if state is None:
			logging.info("SigLeverLED command without state - assuming neutral")
			state = "N"

		logging.debug("Set Signal Lever %s LED to state %s" % (lvrname, state))
		try:
			sl = self.rr.signalLevers[lvrname]
		except KeyError:
			logging.error("Unknown signal lever name: %s" % lvrname)
			logging.debug("Known lever names: %s" % str(list(self.rr.signalLevers.keys())))
			return

		if sl.SetLeverState(1 if state == "R" else 0, 0, 1 if state == 'L' else 0):
			sl.UpdateLed()

	def DoSignalClick(self, cmd):
		try:
			signame = cmd["name"][0]
		except KeyError:
			signame = None
		try:
			callon = int(cmd["callon"][0]) == 1
		except:
			callon = False

		if signame is None:
			logging.error("Signal command without name parameter")
			return
	
		# if aspectType is not None:
		# 	self.rr.SetAspect(signame, aspect, frozenaspect, callon, aspectType=aspectType)
		# else:
		# 	self.rr.SetAspect(signame, aspect, frozenaspect, callon)
		self.rr.SignalClick(signame, callon=callon)

	def DoSignalLock(self, cmd):			
		try:
			signame = cmd["name"][0]
		except KeyError:
			signame = None

		try:
			status = int(cmd["status"][0])
		except KeyError:
			status = None

		if signame is None or status is None:
			logging.error("signal lock command without name and/or status paremeter")
			return
		
		self.rr.SetSignalLock(signame, status)
				
	def DoTurnoutClick(self, cmd):
		try:
			toname = cmd["name"][0]
		except KeyError:
			toname = None

		try:
			status = cmd["status"][0]
		except KeyError:
			status = None

		if toname is None or status is None:
			logging.error("turnout command without name and/or status paremeter")
			return

		self.rr.TurnoutClick(toname, status)

	def DoTurnoutLever(self, cmd):
		p = {tag: cmd[tag][0] for tag in cmd if tag != "cmd"}
		resp = {"turnoutlever": [p]}
		self.socketServer.sendToAll(resp)

	def DoNXButton(self, cmd):
		try:
			bentry = cmd["entry"][0]
		except (IndexError, KeyError):
			bentry = None
		try:
			bexit = cmd["exit"][0]
		except (IndexError, KeyError):
			bexit = None
		try:
			button = cmd["button"][0]
		except (IndexError, KeyError):
			button = None

		if bentry and bexit:
			self.rr.SetOutPulseNXB(bentry)
			self.rr.SetOutPulseNXB(bexit)
		elif button:
			self.rr.SetOutPulseNXB(button)
		else:
			logging.error("NX button without entry&exit/button parameters")
		
	def DoClearLocks(self, cmd):
		logging.debug("clear locks command: %s" % str(cmd))
		self.rr.ClearTurnoutLocks(cmd["turnouts"])

	def DoHandSwitch(self, cmd):
		try:
			hsname = cmd["name"][0]
		except KeyError:
			hsname = None

		try:
			stat = int(cmd["status"][0])
		except KeyError:
			stat = None

		if hsname is None or stat is None:
			logging.error("handswitch without name and/or status paremeter")
			return

		self.rr.SetHandswitch(hsname, stat)

	def DoSetRoute(self, cmd):
		try:
			blknm = cmd["block"][0]
		except (IndexError, KeyError):
			blknm = None

		try:
			route = cmd["route"][0]
		except (IndexError, KeyError):
			route = None

		if blknm is None:
			logging.error("Route command without block parameter")
			return

		if route is None:
			ends = None
			signals = None
		else:
			try:
				ends = [None if e == "-" else e for e in cmd["ends"][0:2]]
			except (IndexError, KeyError):
				ends = None
			try:
				signals = cmd["signals"][0:2]
			except (IndexError, KeyError):
				signals = None

		self.rr.SetOSRoute(blknm, route, ends, signals)
		resp = {"setroute": [{ "block": blknm, "route": route}]}
		if ends is not None:
			resp["setroute"][0]["ends"] = ["-" if e is None else e for e in ends]
		if signals is not None:
			resp["setroute"][0]["signals"] = signals

		self.socketServer.sendToAll(resp)

	def DoIndicator(self, cmd):
		try:
			indname = cmd["name"][0]
		except KeyError:
			indname = None

		try:
			value = int(cmd["value"][0])
		except KeyError:
			value = None

		if indname is None or value is None:
			logging.error("indicator command without name and/or value paremeter")
			return

		self.rr.SetIndicator(indname, value == 1)
		# indicator information is always echoed to all listeners
		resp = {"indicator": [{ "name": indname, "value": value}]}
		self.socketServer.sendToAll(resp)

	def DoSetRelay(self, cmd):
		try:
			name = cmd["name"][0]
		except KeyError:
			name = None

		try:
			flag = int(cmd["flag"][0])
		except KeyError:
			flag = None

		if name is None or flag is None:
			logging.error("set relay command without name and/or flag paremeter")
			return

		logging.debug("set stopping relay %s %d" % (name, flag))
		self.rr.SetRelay(name+".srel", flag)
		
	def DoClock(self, cmd):
		try:
			value = cmd["value"][0]
		except KeyError:
			value = None

		try:
			status = cmd["status"][0]
		except KeyError:
			status = None

		if value is None or status is None:
			logging.error("clock command without value and/or status paremeter")
			return

		resp = {"clock": [{ "value": value, "status": status}]}
		self.timeValue = value
		self.clockStatus = status
		addrList = self.clientList.GetFunctionAddress("DISPLAY") + self.clientList.GetFunctionAddress("SATELLITE")
		for addr, skt in addrList:
			self.socketServer.sendToOne(skt, addr, resp)

	def DoDCCSpeed(self, cmd):
		p = {tag: cmd[tag][0] for tag in cmd if tag != "cmd"}
		resp = {"dccspeed": [p]}
		addrList = self.clientList.GetFunctionAddress("DISPLAY") + self.clientList.GetFunctionAddress(
			"DISPATCH") + self.clientList.GetFunctionAddress("SATELLITE")
		for addr, skt in addrList:
			self.socketServer.sendToOne(skt, addr, resp)

	def DoDCCSpeeds(self, cmd):
		p = {tag: cmd[tag] for tag in cmd if tag != "cmd"}
		resp = {"dccspeeds": p}
		addrList = self.clientList.GetFunctionAddress("DISPLAY") + self.clientList.GetFunctionAddress(
			"DISPATCH") + self.clientList.GetFunctionAddress("SATELLITE")
		for addr, skt in addrList:
			self.socketServer.sendToOne(skt, addr, resp)

	def DoSimulate(self, cmd):
		try:
			action = cmd["action"][0]
		except KeyError:
			action = None

		if action is None:
			logging.error("Sinulate command without action parameter")

		elif action == "occupy":
			try:
				block = cmd["block"][0]
			except KeyError:
				block = None
			try:
				state = int(cmd["state"][0])
			except KeyError:
				state = None

			if block is None or state is None:
				logging.error("simulate occupy command without block and/or state parameter")
			else:
				self.rr.OccupyBlock(block, state)
			
		elif action == "breaker":
			try:
				brkname = cmd["breaker"][0]
			except KeyError:
				brkname = None
			try:
				state = int(cmd["state"][0])
			except KeyError:
				state = None

			if brkname is None or state is None:
				logging.error("simulate breaker command without breaker and/or state parateter")
			else:
				self.rr.SetBreaker(brkname, state)
			
		elif action == "routein":
			try:
				rtname = cmd["name"][0]
			except KeyError:
				rtname = None

			if rtname is None:
				logging.error("simulate routeit command without name parameter")
			else:
				self.rr.SetRouteIn(rtname)
			
		elif action == "turnoutpos":
			try:
				toname = cmd["turnout"][0]
			except KeyError:
				toname = None
			try:
				normal = cmd["normal"][0] == "1"
			except KeyError:
				normal = None

			if toname is None or normal is None:
				logging.error("simulate turnoutpos command without turnout and/or normal parameter")
			else:
				self.rr.SetTurnoutPos(toname, normal)

		else:
			logging.error("Simulate command - unknown action: %s" % action)
			
	def DoIdentify(self, cmd):
		try:
			sid = int(cmd["SID"][0])
		except KeyError:
			sid = None
		try:
			function = cmd["function"][0]
		except KeyError:
			function = None
		try:
			name = cmd["name"][0]
		except KeyError:
			name = None

		if sid is None or function is None:
			logging.error("Identify command without SID and/or function paremeter")
			return

		self.clientList.SetSessionFunction(sid, function, name)
		if function == "DISPATCH":
			self.deleteClients(["AR", "ADVISOR", "ATC"])
			self.pidAR = None
			self.pidADV = None

	def DoFleet(self, cmd):
		try:
			signame = cmd["name"][0]
		except KeyError:
			signame = None
		try:
			value = int(cmd["value"][0])
		except KeyError:
			value = None

		if signame is None or value is None:
			logging.error("Fleet command without signame and/or value parameter")
			return

		self.rr.SetSignalFleet(signame, value != 0)
		resp = {"fleet": [{"name": signame, "value": value}]}
		# fleeting changes are always echoed back to all listeners
		self.socketServer.sendToAll(resp)
		
	def DoDistrictLock(self, cmd):
		try:
			name = cmd["name"][0]
		except KeyError:
			name = None
		try:
			value = cmd["value"]
		except KeyError:
			value = None

		if name is None or value is None:
			logging.error("DistrictLock command without name and/or value parameter")
			return

		self.rr.SetDistrictLock(name, [int(v) for v in value])
			
	def DoControl(self, cmd):
		try:
			name = cmd["name"][0]
		except KeyError:
			name = None
		try:
			value = int(cmd["value"][0])
		except KeyError:
			value = None

		if name is None or value is None:
			logging.error("Control command without name and/or value parameter")
			return

		self.rr.SetControlOption(name, value)
		# p = {tag: cmd[tag][0] for tag in cmd if tag != "cmd"}
		# resp = {"control": [p]}
		# addrList = self.clientList.GetFunctionAddress("DISPLAY") + self.clientList.GetFunctionAddress("DISPATCH") + self.clientList.GetFunctionAddress("SATELLITE")
		# for addr, skt in addrList:
		# 	self.socketServer.sendToOne(skt, addr, resp)
		
	def DoQuit(self, _):
		self.Shutdown()
		
	def DoReopen(self, _):
		self.DoBusReopen()
		
	def DoBusReopen(self):
		if settings.rrserver.simulation:
			return 

		self.pause = 12 # pause I/O for 12 (~5 seconds) cycles while port is re-opened		
		self.rrBus.reopen()

	def DoEnableNode(self, cmd):
		logging.debug("enable node %s" % str(cmd))
		try:
			addr = int(cmd["address"][0])
		except (KeyError, ValueError):
			logging.debug("addr none")
			addr = None
		try:
			name = cmd["name"][0]
		except KeyError:
			logging.debug("name none")
			name = None
		try:
			enable = int(cmd["enable"][0])
		except (KeyError, ValueError):
			logging.debug("enable one")
			enable = 1

		if addr is None or name is None:
			return

		logging.debug("enable %s 0x%x %s" % (name, addr, enable))

		self.rr.EnableNode(name, addr, enable == 1)

	def DoBlockDir(self, cmd):
		try:
			block = cmd["block"][0]
		except KeyError:
			block = None
		try:
			direction = cmd["dir"][0]
		except KeyError:
			direction = None

		if block is None or direction is None:
			logging.error("Blockdir command without block and/or dir parameter")
			return

		self.rr.SetBlockDirection(block, direction)

	def DoBlockDirs(self, cmd):
		try:
			data = json.loads(cmd["data"][0])
		except KeyError:
			data = None

		if data is None:
			logging.error("Blockdirs command without data parameter")
			return

		for b in data:
			try:
				block = b["block"]
			except KeyError:
				block = None
			try:
				direction = b["dir"]
			except KeyError:
				direction = None

			if block is None or direction is None:
				logging.error("Blockdirs command without block and/or dir parameter")
				return

			self.rr.SetBlockDirection(block, direction)

	def DoBlockClear(self, cmd):
		try:
			block = cmd["block"][0]
		except KeyError:
			block = None
		try:
			clear = cmd["clear"][0]
		except KeyError:
			clear = None

		if block is None or clear is None:
			logging.error("Blockclear command without block and/or clear parameter")
			return

		self.rr.SetBlockClear(block, clear == "1")
		
	def DoRefresh(self, cmd):
		try:
			sid = int(cmd["SID"][0])
		except KeyError:
			sid = None

		if sid is None:
			logging.error("Refresh command without SID parameter")
			return

		for addr, data in self.clients.items():
			if data[1] == sid:
				skt = data[0]
				break
		else:
			return

		self.refreshClient(addr, skt)

	def DoTrainBlockOrder(self, cmd):
		try:
			trid = cmd["name"][0]
		except KeyError:
			trid = None

		try:
			blocks = cmd["blocks"]
		except KeyError:
			blocks = []

		try:
			east = cmd["east"][0].startswith("T")
		except (IndexError, KeyError):
			east = None

		if trid is not None and blocks is not None:
			if self.trainList.HasTrain(trid):
				if east is not None:
					self.trainList.SetEast(trid, east)

				self.trainList.UpdateTrainBlockOrder(trid, blocks)

				p = {tag: cmd[tag][0] for tag in cmd if tag != "cmd"}
				p["blocks"] = [b for b in blocks]
				resp = {"trainblockorder": [p]}
				self.socketServer.sendToAll(resp)
			else:
				logging.error("Received trainblock order for non existant train %s" % trid)
		else:
			logging.error("Trainblockorder command without name and/or blocks parameter")

	def DoTrainTimesRequest(self, cmd):
		addrList = self.clientList.GetFunctionAddress("DISPATCH") + self.clientList.GetFunctionAddress("SATELLITE")
		for addr, skt in addrList:
			self.socketServer.sendToOne(skt, addr, {"traintimesrequest": {}})

	def DoTrainTimesReport(self, cmd):
		addrList = self.clientList.GetFunctionAddress("DISPLAY")
		for addr, skt in addrList:
			self.socketServer.sendToOne(skt, addr, {"traintimesreport": cmd})

	def DoDeleteTrain(self, cmd):
		try:
			trn = cmd["name"][0]
		except (IndexError, KeyError):
			trn = None

		if trn is None:
			logging.info("skipping delete train command with no train name")
			return

		p = {tag: cmd[tag][0] for tag in cmd if tag != "cmd"}
		resp = {"deletetrain": p}
		self.socketServer.sendToAll(resp)

		if not self.trainList.HasTrain(trn):
			logging.info("skipping delete of non existant train")
			return

		self.trainList.DeleteTrain(trn)

	def DoSetTrain(self, cmd):
		try:
			blocks = cmd["blocks"]
		except (IndexError, KeyError):
			logging.error("Set train message is missing blocks - ignoring")
			return

		try:
			trn = cmd["name"][0]
		except (IndexError, KeyError):
			trn = None
		try:
			loco = cmd["loco"][0]
		except (IndexError, KeyError):
			loco = None
		try:
			east = True if cmd["east"][0] == "1" else False
		except (IndexError, KeyError):
			east = True
		try:
			action = cmd["action"][0]
		except (IndexError, KeyError):
			action = REPLACE
		try:
			route = cmd["route"][0]
		except (IndexError, KeyError):
			route = None
		try:
			silent = True if cmd["silent"][0] == "1" else False
		except (IndexError, KeyError):
			silent = True

		logging.info("set train: %s" % str(cmd))

		for blknm in blocks:
			ntrn, nloco = self.trainList.FindTrainInBlock(blknm)
			if ntrn and ntrn != trn:
				#remove the block from the old train
				self.trainList.RemoveTrainFromBlock(ntrn, blknm)

		#self.rr.OccupyBlock(block, 0 if trn is None else 1)

		# train information is always echoed back to all listeners
		stParams = {"name": trn, "loco": loco, "blocks": blocks, "east": east, "action": action, "silent": silent}
		if route is not None:
			stParams["route"] = route
		resp = {"settrain": stParams}
		self.socketServer.sendToAll(resp)

		self.trainList.Update(trn, loco, blocks, east, action, route=route)
		
	def DoMoveTrain(self, cmd): #"movetrain":
		try:
			blknm = cmd["block"][0]
		except (IndexError, KeyError):
			return
		self.rr.PlaceTrain(blknm)
		self.rr.OccupyBlock(blknm, 1)

	def DoRemoveTrain(self, cmd): #"removetrain":
		try:
			blknm = cmd["block"][0]
		except (IndexError, KeyError):
			return
		self.rr.RemoveTrain(blknm)
		self.rr.OccupyBlock(blknm, 0)

	def DoTrainComplete(self, cmd):
		p = {tag: cmd[tag][0] for tag in cmd if tag != "cmd"}
		resp = {"traincomplete": [p]}
		self.socketServer.sendToAll(resp)

	def DoAssignTrain(self, cmd):
		p = {tag: cmd[tag][0] for tag in cmd if tag != "cmd"}
		train = p["train"]	
		try:
			engineer = p["engineer"]
		except KeyError:
			engineer = None
			
		self.trainList.UpdateEngineer(train, engineer)
		
		resp = {"assigntrain": [p]}
		self.socketServer.sendToAll(resp)

	def DoModifyTrain(self, cmd):
		try:
			iname = cmd["iname"][0]
		except (IndexError, KeyError):
			iname = None
		try:
			name = cmd["name"][0]
		except (IndexError, KeyError):
			name = None
		try:
			loco = cmd["loco"][0]
		except (IndexError, KeyError):
			loco = None
		try:
			template = cmd["template"][0]
		except (IndexError, KeyError):
			template = None
		try:
			engineer = cmd["engineer"][0]
		except (IndexError, KeyError):
			engineer = None
		try:
			atc = cmd["atc"][0] == 1
		except (IndexError, KeyError):
			atc = None
		try:
			ar = cmd["ar"][0] == 1
		except (IndexError, KeyError):
			ar = None
		try:
			east = cmd["east"][0] == "1"
		except (IndexError, KeyError):
			east = None

		tr = self.rr.GetTrain(iname)
		if tr is None:
			return

		if name is not None:
			roster = self.rr.GetTrainRoster(name)
			tr.SetName(name, roster)

		tr.SetLoco(loco)
		tr.SetTemplateTrain(template)
		tr.SetEngineer(engineer)
		tr.SetATC(atc)
		tr.SetAR(ar)
		tr.SetEast(east)

		# change the status of all blocks to reflect the potentially new train id information
		blkStat = "O" if tr.IsIdentified() else "U"
		for blk in tr.Blocks():
			if blk.IsMasterBlock():
				# the only legitimate transition here is "U" to "O" or "O" to "U"
				changed = False
				for sb in blk.SubBlocks():
					if sb.GetStatus() in ["O", "U"]:
						if sb.SetStatus(blkStat):
							if settings.debug.blockoccupancy:
								self.rr.Alert("changed status of subblock %s to %s" % (sb.Name(), blkStat))
							changed = True
				if changed:
					if settings.debug.blockoccupancy:
						self.rr.Alert("After subblocks, status of main block %s is now %s" % (blk.Name(), blk.GetStatus()))
					self.rr.RailroadEvent(blk.GetEventMessage())

			else:
				if blk.SetStatus(blkStat):
					if settings.debug.blockoccupancy:
						self.rr.Alert("changed status of block %s to %s" % (blk.Name(), blkStat))
					self.rr.RailroadEvent(blk.GetEventMessage())

		self.rr.RailroadEvent(tr.GetEventMessage())

	def DoTrainReverse(self, cmd):
		try:
			iname = cmd["train"][0]
		except (IndexError, KeyError):
			iname = None

		if iname is None:
			logging.debug("Reverse train without a train id")
			return

		self.rr.ReverseTrain(iname)

	def DoTrainReorder(self, cmd):
		try:
			iname = cmd["train"][0]
		except (IndexError, KeyError):
			iname = None

		try:
			blocks = cmd["blocks"]
		except KeyError:
			blocks = None

		if iname is None:
			logging.debug("Reorder train without a train id")
			return

		if blocks is None:
			logging.debug("Reorder train without blocks list")

		self.rr.ReorderTrain(iname, blocks)

	def DoTrainSplit(self, cmd):
		try:
			iname = cmd["train"][0]
		except (IndexError, KeyError):
			iname = None

		try:
			blocks = cmd["blocks"]
		except KeyError:
			blocks = None

		if iname is None:
			logging.debug("Split train without a train id")
			return

		if blocks is None:
			logging.debug("Split train without blocks list")

		self.rr.SplitTrain(iname, blocks)

	def DoTrainMerge(self, cmd):
		try:
			train = cmd["train"][0]
		except (IndexError, KeyError):
			train = None

		try:
			mergetrain = cmd["mergetrain"][0]
		except KeyError:
			mergetrain = None

		if train is None or mergetrain is None:
			logging.debug("Train merge requires 2 trains")
			return

		self.rr.MergeTrains(train, mergetrain)

	def DoTrainSwap(self, cmd):
		try:
			train = cmd["train"][0]
		except (IndexError, KeyError):
			train = None

		try:
			swaptrain = cmd["swaptrain"][0]
		except KeyError:
			swaptrain = None

		if train is None or swaptrain is None:
			logging.debug("Train swap requires 2 trains")
			return

		self.rr.SwapTrains(train, swaptrain)

	def DoCheckTrains(self, cmd):
		addrList = self.clientList.GetFunctionAddress("DISPATCH") + self.clientList.GetFunctionAddress("SATELLITE")
		for addr, skt in addrList:
			self.socketServer.sendToOne(skt, addr, {"checktrains": {}})
		
	def DoTrainSignal(self, cmd):
		try:
			trid = cmd["train"][0]
		except KeyError:
			trid = None
		try:
			signal = cmd["signal"][0]
		except KeyError:
			signal = None
		try:
			aspect = cmd["aspect"][0]
		except KeyError:
			aspect = None

		if trid is None or signal is None or aspect is None:
			logging.error("trainsignal command without train and/or signal and/op aspect parameter")
			return

		self.trainList.UpdateSignal(trid, signal, aspect)
		p = {tag: cmd[tag][0] for tag in cmd if tag != "cmd"}
		resp = {"trainsignal": p}
		self.socketServer.sendToAll(resp)
	
	def DoAdvice(self, cmd):
		addrList = self.clientList.GetFunctionAddress("DISPATCH") + self.clientList.GetFunctionAddress("SATELLITE")
		for addr, skt in addrList:
			self.socketServer.sendToOne(skt, addr, {"advice": cmd})
	
	def DoAlert(self, cmd):
		addrList = self.clientList.GetFunctionAddress("DISPATCH") + self.clientList.GetFunctionAddress("SATELLITE")
		for addr, skt in addrList:
			self.socketServer.sendToOne(skt, addr, {"alert": cmd})

	def DoLoadSnapshot(self, cmd):
		filename = cmd["filename"][0]
		fn = os.path.join(os.getcwd(), "data", "snapshots", filename)
		self.rr.LoadSnapshot(filename)

	def DoServer(self, cmd):
		try:
			action = cmd["action"][0]
		except KeyError:
			action = None

		if action is None:
			logging.error("server command without action parameter")

		elif action == "exit":
			logging.info("HTTP 'server:exit' command received - terminating")
			self.Shutdown()

		else:
			logging.error("server command with unknown action: %s" % action)
				
	def DoDebug(self, cmd):
		try:
			function = cmd["function"][0]
		except KeyError:
			function = None

		if function is None:
			logging.error("debug command without function parameter")
			return

		addrList = self.clientList.GetFunctionAddress(function)
		for addr, skt in addrList:
			self.socketServer.sendToOne(skt, addr, {"debug": cmd})

	def DoDebugFlags(self, cmd):
		logging.debug("Got debugflags command: %s" % str(cmd))
		try:
			showaspectcalculation = int(cmd["showaspectcalculation"][0])
			logging.debug("%s" % showaspectcalculation)
		except (KeyError, IndexError, ValueError):
			showaspectcalculation = 0

		try:
			blockoccupancy = int(cmd["blockoccupancy"][0])
		except (KeyError, IndexError, ValueError):
			blockoccupancy = 0
		try:
			identifytrain = int(cmd["identifytrain"][0])
		except (KeyError, IndexError, ValueError):
			identifytrain = 0

		settings.debug.showaspectcalculation = showaspectcalculation > 0
		settings.debug.blockoccupancy = blockoccupancy > 0
		settings.debug.identifytrain = identifytrain > 0

	def DoDumpTrains(self, cmd):
		self.trainList.Dump()

	def DoIgnore(self, cmd):
		try:
			settings.rrserver.ignoredblocks = cmd["blocks"]
		except KeyError:
			settings.rrserver.ignoredblocks = []

		logging.info("received ignore command: %s" % str(settings.rrserver.ignoredblocks))
		settings.SaveAll()
		self.rr.UpdateIgnoreList()

		p = {tag: cmd[tag] for tag in cmd if tag != "cmd"}
		resp = {"ignore": p}
		addrList = self.clientList.GetFunctionAddress("DISPATCH") + self.clientList.GetFunctionAddress("SATELLITE")
		for addr, skt in addrList:
			self.socketServer.sendToOne(skt, addr, resp)

	def DoClose(self, cmd):
		try:
			function = cmd["function"][0]
		except KeyError:
			function = None

		if function is None:
			logging.error("Close command without function parameter")
			return

		addrList = self.clientList.GetFunctionAddress(function)
		for addr, _ in addrList:
			self.socketServer.deleteSocket(addr)

	def DoAutorouter(self, cmd): # start/kill autorouter process
		try:
			stat = cmd["status"][0]
		except KeyError:
			stat = None

		if stat is None:
			logging.error("autorouter command without status parameter")
			return

		if stat == "on":
			if not self.clientList.HasFunction("AR"):
				arExec = os.path.join(os.getcwd(), "autorouter", "main.py")
				self.pidAR = Popen([sys.executable, arExec]).pid
				logging.debug("autorouter started as PID %d" % self.pidAR)
		else:
			self.deleteClients(["AR"])
			self.pidAR = None
			
	def DoAR(self, cmd): # forward autorouter messages to all AR cliebts
		addrList = self.clientList.GetFunctionAddress("AR") + self.clientList.GetFunctionAddress("DISPLAY") + self.clientList.GetFunctionAddress("SATELLITE")
		for addr, skt in addrList:
			self.socketServer.sendToOne(skt, addr, {"ar": cmd})

	def DoATC(self, cmd):
		addrList = self.clientList.GetFunctionAddress("ATC") + self.clientList.GetFunctionAddress("DISPLAY") + self.clientList.GetFunctionAddress("SATELLITE")
		for addr, skt in addrList:
			self.socketServer.sendToOne(skt, addr, {"atc": cmd})

	def DoATCStatus(self, cmd):
		self.socketServer.sendToAll({"atcstatus": cmd})

	def Shutdown(self):
		logging.info("shutdown requested")
		self.forever = False

	def AtInterval(self):
		if self.forever:
			threading.Timer(self.busInterval, self.AtInterval).start()
			if self.delay is None or self.delay <= 0:
				self.cmdQ.put({"cmd": ["interval"]})
			elif self.delay > 0:
				self.delay -= 1
				if self.delay <= 0:
					self.delay = None
					# self.cmdQ.put({"cmd": ["delayedstartup"]})
					
	def ServeForever(self):
		logging.info("serve forever starting")
		self.forever = True
		self.delay = 5  # wait 5 cycles before delayed startup
		self.pause = 0
		self.AtInterval()
		while self.forever:
			while not self.cmdQ.empty():
				self.ProcessCommand(self.cmdQ.get())
			time.sleep(0.005)
			
		logging.info("terminating server threads")
		try:
			self.dispServer.close()
		except Exception as e:
			logging.error("exception %s terminating http server" % str(e))
		
		try:
			self.socketServer.kill()
		except Exception as e:
			logging.error("exception %s terminating socket server" % str(e))
		
		if not settings.rrserver.simulation:
			if self.DCCSniffer is not None:
				try:
					self.DCCSniffer.kill()
				except Exception as e:
					logging.error("exception %s terminating DCC Sniffer process" % str(e))
				
			try:
				self.DCCServer.close()
			except Exception as e:
				logging.error("exception %s terminating DCC server" % str(e))
		
			try:
				self.rrBus.close()
			except Exception as e:
				logging.error("exception %s closing Railroad Bus port" % str(e))
			
		logging.info("completed - continuing with shutdown")
		

main = ServerMain()
main.ServeForever()


logging.info("Railroad server terminating")
