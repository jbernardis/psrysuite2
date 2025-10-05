import configparser
import os
import sys
import getopt

INIFILE = "psry.ini"
GLOBAL = "global"


def parseBoolean(val, defaultVal):
	lval = val.lower()
	
	if lval == 'true' or lval == 't' or lval == 'yes' or lval == 'y':
		return True
	
	if lval == 'false' or lval == 'f' or lval == 'no' or lval == 'n':
		return False
	
	return defaultVal


class SNode:
	def __init__(self):
		pass


class Debug:
	def __init__(self):
		self.showaspectcalculation = False
		self.blockoccupancy = False
		self.identifytrain = False
		self.loglevel = "DEBUG"


class Settings:
	def __init__(self):
		self.datafolder = os.path.join(os.getcwd(), "data")
		self.inifile = os.path.join(self.datafolder, INIFILE)

		self.cfg = configparser.ConfigParser()
		self.cfg.optionxform = str
		if not self.cfg.read(self.inifile):
			print("Settings file %s does not exist.  Using default values" % INIFILE)
		section = "rrserver"
		self.rrserver = SNode()
		self.rrserver.simulation = False
		self.rrserver.rrtty = "COM5"
		self.rrserver.dcctty = "COM6"
		self.rrserver.businterval = 0.4
		self.rrserver.topulselen = 2
		self.rrserver.topulsect = 3
		self.rrserver.nxbpulselen = 4
		self.rrserver.nxbpulsect = 2
		self.rrserver.snapshotlimit = 5
		self.rrserver.ioerrorthreshold = 5
		self.rrserver.pendingdetectionlosscycles = 2
		self.rrserver.ignoredblocks = []
		if self.cfg.has_section(section):
			for opt, value in self.cfg.items(section):
				if opt == 'simulation':
					self.rrserver.simulation = parseBoolean(value, False)

				elif opt == "rrtty":
					self.rrserver.rrtty = value

				elif opt == "dcctty":
					self.rrserver.dcctty = value

				elif opt == "businterval":
					self.rrserver.businterval = float(value)

				elif opt == "topulselen":
					self.rrserver.topulselen = int(value)

				elif opt == "topulsect":
					self.rrserver.topulsect = int(value)

				elif opt == "nxbpulselen":
					self.rrserver.nxbpulselen = int(value)

				elif opt == "nxbpulsect":
					self.rrserver.nxbpulsect = int(value)

				elif opt == "ioerrorthreshold":
					self.rrserver.ioerrorthreshold = int(value)

				elif opt == "snapshotlimit":
					self.rrserver.snapshotlimit = int(value)

				elif opt == "ignoredblocks":
					self.rrserver.ignoredblocks = [x.strip() for x in value.split(",")]

				elif opt == "pendingdetectionlosscycles":
					self.rrserver.pendingdetectionlosscycles = int(value)

		else:
			print("Missing %s section - assuming defaults" % section)

		section = "dccsniffer"
		self.dccsniffer = SNode()
		self.dccsniffer.tty = "COM4"
		self.dccsniffer.enable = True
		self.dccsniffer.interval = 5000
		if self.cfg.has_section(section):
			for opt, value in self.cfg.items(section):
				if opt == 'tty':
					self.dccsniffer.tty = value
				elif opt == 'enable':
					self.dccsniffer.enable = parseBoolean(value, True)
				elif opt == 'interval':
					self.dccsniffer.interval = int(value)

		else:
			print("Missing dccsniffer section - assuming defaults")

		section = "control"
		self.control = SNode()
		self.control.nassau = 2
		self.control.cliff = 0
		self.control.yard = 0
		self.control.c13auto = True

		if self.cfg.has_section(section):
			for opt, value in self.cfg.items(section):
				if opt == 'cliff':
					v = int(value)
					if v < 0 or v > 2:
						print("value for controlcliff out of range - assuming 0")
						v = 0
					self.control.cliff = v

				elif opt == 'nassau':
					v = int(value)
					if v < 0 or v > 2:
						print("value for controlnassau out of range - assuming 0")
						v = 0
					self.control.nassau = v

				elif opt == 'yard':
					v = int(value)
					if v < 0 or v > 1:
						print("value for controlyard out of range - assuming 0")
						v = 0
					self.control.yard = v

				elif opt == 'c13auto':
					self.control.c13auto = parseBoolean(value, True)

		else:
			print("Missing %s section - assuming defaults" % section)

		section = "dispatcher"
		self.dispatcher = SNode()
		self.dispatcher.dispatch = True
		self.dispatcher.satellite = False
		self.dispatcher.precheckshutdownserver = True
		self.dispatcher.prechecksnapshot = True
		self.dispatcher.prechecksavelogs = True
		self.dispatcher.clockstarttime = 355
		self.dispatcher.matrixturnoutdelay = 2
		self.dispatcher.notifyinvalidblocks = True
		self.dispatcher.notifyincorrectroute = True
		self.dispatcher.autoloadsnapshot = True
		if self.cfg.has_section(section):
			for opt, value in self.cfg.items(section):
				if opt == 'dispatch':
					self.dispatcher.dispatch = parseBoolean(value, False)

				elif opt == 'satellite':
					self.dispatcher.satellite = parseBoolean(value, False)

				elif opt == 'precheckshutdownserver':
					self.dispatcher.precheckshutdownserver = parseBoolean(value, True)

				elif opt == 'prechecksnapshot':
					self.dispatcher.prechecksnapshot = parseBoolean(value, True)

				elif opt == 'prechecksavelogs':
					self.dispatcher.prechecksavelogs = parseBoolean(value, True)

				elif opt == 'matrixturnoutdelay':
					try:
						s = int(value)
					except ValueError:
						print("invalid value in ini file for matrix turnout delay: %s" % value)
						s = 2
					self.dispatcher.matrixturnoutdelay = s
					
				elif opt == 'clockstarttime':
					try:
						s = int(value)
					except ValueError:
						print("invalid value in ini file for clock start timer: %s" % value)
						s = 355
					self.dispatcher.clockstarttime = s

				elif opt == 'notifyinvalidblocks':
					self.dispatcher.notifyinvalidblocks = parseBoolean(value, True)

				elif opt == 'notifyincorrectroute':
					self.dispatcher.notifyincorrectroute = parseBoolean(value, True)

				elif opt == 'autoloadsnapshot':
					self.dispatcher.autoloadsnapshot = parseBoolean(value, True)

		else:
			print("Missing %s section - assuming defaults" % section)

		if self.dispatcher.dispatch and self.dispatcher.satellite:
			print("Cannot have bpoth dispatch and satellite enabled at the same time.  Assuming dispatch only")
			self.dispatcher.satellite = False

		section = "display"
		self.display = SNode()
		self.display.name = "Display"
		self.display.pages = 3
		self.display.showcameras = False
		self.display.showevents = False
		self.display.showadvice = False
		self.display.showunknownhistory = True
		if self.cfg.has_section(section):
			for opt, value in self.cfg.items(section):
				if opt == 'pages':
					try:
						s = int(value)
					except ValueError:
						print("invalid value in ini file for pages: (%s)" % value)
						s = 3

					if s not in [1, 3]:
						print("Invalid values for pages: %d" % s)
						s = 3
					self.display.pages = s

				elif opt == 'showcameras':
					self.display.showcameras = parseBoolean(value, False)

				elif opt == 'showevents':
					self.display.showevents = parseBoolean(value, False)

				elif opt == 'showadvice':
					self.display.showadvice = parseBoolean(value, False)

				elif opt == 'showunknownhistory':
					self.display.showunknownhistory = parseBoolean(value, True)

				elif opt == 'name':
					self.display.name = value

		else:
			print("Missing %s section - assuming defaults" % section)

		section = "activetrains" 
		self.activetrains = SNode()
		self.activetrains.lines = 4     
		self.activetrains.suppressyards = True
		self.activetrains.suppressunknown = False
		self.activetrains.onlyatc = False
		self.activetrains.onlyassigned = False
		self.activetrains.onlyassignedorunknown = False
		if self.cfg.has_section(section):
			for opt, value in self.cfg.items(section):
				if opt == 'lines':
					self.activetrains.lines = int(value)
				elif opt == 'suppressyards':
					self.activetrains.suppressyards = parseBoolean(value, True)

				elif opt == 'suppressunknown':
					self.activetrains.suppressunknown = parseBoolean(value, False)

				elif opt == 'onlyassignedorunknown':
					self.activetrains.onlyassignedorunknown = parseBoolean(value, False)

				elif opt == 'onlyassigned':
					self.activetrains.onlyassigned = parseBoolean(value, False)

				elif opt == 'onlyatc':
					self.activetrains.onlyatc = parseBoolean(value, False)
		else:
			print("Missing %s section - assuming defaults" % section)

		"""
		verify mutual exclusion of active train options
		"""
		ct = 0
		ct += 1 if self.activetrains.suppressunknown else 0
		ct += 1 if self.activetrains.onlyassignedorunknown else 0
		ct += 1 if self.activetrains.onlyassigned else 0
		ct += 1 if self.activetrains.onlyatc else 0
		if ct > 1:
			if self.activetrains.onlyassignedorunknown:
				self.activetrains.suppressunknown = False
				self.activetrains.onlyassigned = False
				self.activetrains.onlyatc = False
			elif self.activetrains.onlyassigned:
				self.activetrains.suppressunknown = False
				self.activetrains.onlyatc = False
			elif self.activetrains.suppressunknown:
				self.activetrains.onlyatc = False				
				
		self.debug = Debug()
		if self.cfg.has_section("debug"):
			for opt, value in self.cfg.items("debug"):
				if opt == 'showaspectcalculation':
					self.debug.showaspectcalculation = parseBoolean(value, False)
				elif opt == 'blockoccupancy':
					self.debug.blockoccupancy = parseBoolean(value, False)
				elif opt == 'identifytrain':
					self.debug.identifytrain = parseBoolean(value, False)
				elif opt == 'loglevel':
					self.debug.loglevel = value

		self.ipaddr = "192.168.1.138"
		self.serverport = 9000
		self.socketport = 9001
		self.dccserverport = 9002
		self.backupdir = os.getcwd()
		self.browser = "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe"
		if self.cfg.has_section(GLOBAL):
			for opt, value in self.cfg.items(GLOBAL):
				if opt == 'socketport':
					try:
						s = int(value)
					except ValueError:
						print("invalid value in ini file for socket port: (%s)" % value)
						s = 9001
					self.socketport = s
						
				elif opt == 'serverport':
					try:
						s = int(value)
					except ValueError:
						print("invalid value in ini file for server port: (%s)" % value)
						s = 9000
					self.serverport = s
						
				elif opt == 'dccserverport':
					try:
						s = int(value)
					except ValueError:
						print("invalid value in ini file for DCC server port: (%s)" % value)
						s = 9002
					self.dccserverport = s
						
				elif opt == 'ipaddr':
					self.ipaddr = value
					
				elif opt == 'backupdir':
					self.backupdir = value
					
				elif opt == 'browser':
					self.browser = value

		else:
			print("Missing global section - assuming defaults")

		"""
		process the command line next and override the settings file with the options seen there
		"""
		try:
			opts, _ = getopt.getopt(sys.argv[1:], "", ["dispatch", "display", "simulate", "sim", "nosimulate", "nosim", "satellite"])
		except getopt.GetoptError:
			print('Invalid command line arguments - ignoring')
			return 
		
		for opt, _ in opts:
			print("command line option: %s" % opt, flush=True)
			if opt == "--display":
				self.dispatcher.dispatch = False
				self.dispatcher.satellite = False
				print("Overriding dispatcher mode from command line: display")

			elif opt == "--dispatch":
				self.dispatcher.dispatch = True
				self.dispatcher.satellite = False
				print("Overriding dispatcher mode from command line: dispatch")

			elif opt == "--satellite":
				self.dispatcher.dispatch = False
				self.dispatcher.satellite = True
				print("Overriding dispatcher mode from command line: satellite")

			elif opt in ["--simulate", "--sim"]:
				self.rrserver.simulation = True
				print("Overriding simulation flag from command line: True")
				
			elif opt in ["--nosimulate", "--nosim"]:
				self.rrserver.simulation = False
				print("Overriding simulation flag from command line: False")
		
	def SaveAll(self):
		print("entering saveall", flush=True)
		self.cfg = configparser.ConfigParser()
		self.cfg.optionxform = str
		if not self.cfg.read(self.inifile):
			print("Settings file %s does not exist.  Using default values" % INIFILE)
		
		section = "rrserver"
		try:
			self.cfg.add_section(section)
		except configparser.DuplicateSectionError:
			pass
		
		self.cfg.set(section, "rrtty", self.rrserver.rrtty)
		self.cfg.set(section, "dcctty", self.rrserver.dcctty)
		self.cfg.set(section, "simulation", "True" if self.rrserver.simulation else "False")
		self.cfg.set(section, "businterval", "%0.2f" % self.rrserver.businterval)
		self.cfg.set(section, "topulselen", "%d" % self.rrserver.topulselen)
		self.cfg.set(section, "topulsect", "%d" % self.rrserver.topulsect)
		self.cfg.set(section, "nxbpulselen", "%d" % self.rrserver.nxbpulselen)
		self.cfg.set(section, "nxbpulsect", "%d" % self.rrserver.nxbpulsect)
		self.cfg.set(section, "ioerrorthreshold", "%d" % self.rrserver.ioerrorthreshold)
		self.cfg.set(section, "pendingdetectionlosscycles", "%d" % self.rrserver.pendingdetectionlosscycles)
		self.cfg.set(section, "ignoredblocks", ", ".join(self.rrserver.ignoredblocks))
		self.cfg.set(section, "snapshotlimit", "%d" % self.rrserver.snapshotlimit)

		section = "dccsniffer"
		try:
			self.cfg.add_section(section)
		except configparser.DuplicateSectionError:
			pass
		
		self.cfg.set(section, "tty", self.dccsniffer.tty)
		self.cfg.set(section, "enable", "True" if self.dccsniffer.enable else "False")
		self.cfg.set(section, "interval", "%d" % self.dccsniffer.interval)

		section = "control"
		try:
			self.cfg.add_section(section)
		except configparser.DuplicateSectionError:
			pass

		self.cfg.set(section, "nassau",   "%d" % self.control.nassau)
		self.cfg.set(section, "cliff",    "%d" % self.control.cliff)
		self.cfg.set(section, "yard",     "%d" % self.control.yard)
		self.cfg.set(section, "c13auto", "True" if self.control.c13auto else "False")

		section = "dispatcher"
		try:
			self.cfg.add_section(section)
		except configparser.DuplicateSectionError:
			pass

		print("set dispatch/satellite to %s/%s" % (self.dispatcher.dispatch, self.dispatcher.satellite), flush=True)
		self.cfg.set(section, "dispatch", "True" if self.dispatcher.dispatch else "False")
		self.cfg.set(section, "satellite", "True" if self.dispatcher.satellite else "False")
		self.cfg.set(section, "precheckshutdownserver", "True" if self.dispatcher.precheckshutdownserver else "False")
		self.cfg.set(section, "prechecksnapshot", "True" if self.dispatcher.prechecksnapshot else "False")
		self.cfg.set(section, "prechecksavelogs", "True" if self.dispatcher.prechecksavelogs else "False")
		self.cfg.set(section, "clockstarttime",   "%d" % self.dispatcher.clockstarttime)
		self.cfg.set(section, "matrixturnoutdelay",   "%d" % self.dispatcher.matrixturnoutdelay)
		self.cfg.set(section, "notifyinvalidblocks", "True" if self.dispatcher.notifyinvalidblocks else "False")
		self.cfg.set(section, "notifyincorrectroute", "True" if self.dispatcher.notifyincorrectroute else "False")
		self.cfg.set(section, "autoloadsnapshot", "True" if self.dispatcher.autoloadsnapshot else "False")

		section = "display"
		try:
			self.cfg.add_section(section)
		except configparser.DuplicateSectionError:
			pass

		self.cfg.set(section, "pages",   "%d" % self.display.pages)
		self.cfg.set(section, "showcameras", "True" if self.display.showcameras else "False")
		self.cfg.set(section, "showevents", "True" if self.display.showevents else "False")
		self.cfg.set(section, "showadvice", "True" if self.display.showadvice else "False")
		self.cfg.set(section, "showunknownhistory", "True" if self.display.showunknownhistory else "False")
		self.cfg.set(section, "name", self.display.name)

		section = "activetrains" 
		try:
			self.cfg.add_section(section)
		except configparser.DuplicateSectionError:
			pass
		
		self.cfg.set(section, "lines", "%d" % self.activetrains.lines)
		self.cfg.set(section, "suppressyards", "True" if self.activetrains.suppressyards else "False")
		self.cfg.set(section, "suppressunknown", "True" if self.activetrains.suppressunknown else "False")
		self.cfg.set(section, "onlyatc", "True" if self.activetrains.onlyatc else "False")
		self.cfg.set(section, "onlyassigned", "True" if self.activetrains.onlyassigned else "False")
		self.cfg.set(section, "onlyassignedorunknown", "True" if self.activetrains.onlyassignedorunknown else "False")

		section = "debug"
		try:
			self.cfg.add_section(section)
		except configparser.DuplicateSectionError:
			pass
		self.cfg.set(section, "showaspectcalculation", "True" if self.debug.showaspectcalculation else "False")
		self.cfg.set(section, "blockoccupancy", "True" if self.debug.blockoccupancy else "False")
		self.cfg.set(section, "loglevel", self.debug.loglevel)

		section = GLOBAL
		try:
			self.cfg.add_section(section)
		except configparser.DuplicateSectionError:
			pass
		
		self.cfg.set(section, "ipaddr", self.ipaddr)
		self.cfg.set(section, "serverport", "%d" % self.serverport)
		self.cfg.set(section, "dccserverport", "%d" % self.dccserverport)
		self.cfg.set(section, "socketport", "%d" % self.socketport)
		self.cfg.set(section, "backupdir", self.backupdir)
		self.cfg.set(section, "browser", self.browser)

		try:
			cfp = open(self.inifile, 'w')
		except Exception:
			print("Unable to open settings file %s for writing" % self.inifile)
			return False
		
		self.cfg.write(cfp)
		cfp.close()
		return True
