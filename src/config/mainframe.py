import wx
import os
import sys
import winshell
import getopt

from dispatcher.settings import Settings
from config.generatedlg import GenerateDlg
from utilities.backup import saveData, restoreData


def GenShortcut(module, forceStartMenu=False):
	psrypath = os.getcwd()
	python = sys.executable.replace("python.exe", "pythonw.exe")

	paths = [os.path.join(winshell.desktop(), "%s.lnk" % module["name"])]

	if forceStartMenu:
		smdir = os.path.join(winshell.start_menu(), "Programs", "PSRY")
		try:
			os.mkdir(smdir)
		except FileExistsError:
			pass

		paths.append(os.path.join(smdir, "%s.lnk" % module["name"]))

	for link_path in paths:
		if module["dir"] is None:
			pyfile = os.path.join(psrypath, module["main"])
		else:
			pyfile = os.path.join(psrypath, module["dir"], module["main"])

		with winshell.shortcut(link_path) as link:
			link.path = python
			if "parameter" in module:
				link.arguments = "\"%s\" \"%s\"" % (pyfile, module["parameter"])
			else:
				link.arguments = "\"%s\"" % pyfile
			link.working_directory = psrypath
			link.description = module["desc"]
			link.icon_location = (os.path.join(psrypath, "icons", module["icon"]), 0)


class MainFrame(wx.Frame):
	def __init__(self):
		wx.Frame.__init__(self, None, size=(900, 800), style=wx.DEFAULT_FRAME_STYLE)
		self.SetTitle("PSRY Configuration Utility")
		self.Bind(wx.EVT_CLOSE, self.OnClose)

		try:
			opts, _ = getopt.getopt(sys.argv[1:], "",
									["install"])
		except getopt.GetoptError:
			print('Invalid command line arguments - ignoring')
			return

		install = False
		for opt, _ in opts:
			print("command line option: %s" % opt, flush=True)
			if opt == "--install":
				install = True

		print("install = %s" % str(install))

		self.settings = Settings()
		
		icon = wx.Icon()
		icon.CopyFromBitmap(wx.Bitmap(os.path.join(os.getcwd(), "icons", "config.ico"), wx.BITMAP_TYPE_ANY))
		self.SetIcon(icon)
		
		vszrl = wx.BoxSizer(wx.VERTICAL)
		vszrl.AddSpacer(20)
		
		commBox = wx.StaticBox(self, wx.ID_ANY, "Communications")
		topBorder = commBox.GetBordersForSizer()[0]
		boxsizer = wx.BoxSizer(wx.VERTICAL)
		boxsizer.AddSpacer(topBorder+10)
		
		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.AddSpacer(20)
		hsz.Add(wx.StaticText(commBox, wx.ID_ANY, "IP Address: ", size=(130, -1)))		
		self.teIpAddr = wx.TextCtrl(commBox, wx.ID_ANY, "", size=(100, -1))
		self.teIpAddr.SetValue(self.settings.ipaddr)
		hsz.Add(self.teIpAddr)
		hsz.AddSpacer(20)
		boxsizer.Add(hsz)
		
		boxsizer.AddSpacer(10)
		
		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.AddSpacer(20)
		hsz.Add(wx.StaticText(commBox, wx.ID_ANY, "RR Server Port: ", size=(130, -1)))		
		self.teRRPort = wx.TextCtrl(commBox, wx.ID_ANY, "", size=(100, -1))
		self.teRRPort.SetValue("%d" % self.settings.serverport)
		hsz.Add(self.teRRPort)
		hsz.AddSpacer(20)
		boxsizer.Add(hsz)
		
		boxsizer.AddSpacer(10)
		
		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.AddSpacer(20)
		hsz.Add(wx.StaticText(commBox, wx.ID_ANY, "DCC Server Port: ", size=(130, -1)))		
		self.teDCCPort = wx.TextCtrl(commBox, wx.ID_ANY, "", size=(100, -1))
		self.teDCCPort.SetValue("%d" % self.settings.dccserverport)
		hsz.Add(self.teDCCPort)
		hsz.AddSpacer(20)
		boxsizer.Add(hsz)

		boxsizer.AddSpacer(10)

		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.AddSpacer(20)
		hsz.Add(wx.StaticText(commBox, wx.ID_ANY, "WEB App port: ", size=(130, -1)))
		self.teWebPort = wx.TextCtrl(commBox, wx.ID_ANY, "", size=(100, -1))
		self.teWebPort.SetValue("%d" % self.settings.webappport)
		hsz.Add(self.teWebPort)
		hsz.AddSpacer(20)
		boxsizer.Add(hsz)

		boxsizer.AddSpacer(10)

		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.AddSpacer(20)
		hsz.Add(wx.StaticText(commBox, wx.ID_ANY, "Broadcast port: ", size=(130, -1)))
		self.teBroadcastPort = wx.TextCtrl(commBox, wx.ID_ANY, "", size=(100, -1))
		self.teBroadcastPort.SetValue("%d" % self.settings.socketport)
		hsz.Add(self.teBroadcastPort)
		hsz.AddSpacer(20)
		boxsizer.Add(hsz)

		boxsizer.AddSpacer(10)

		commBox.SetSizer(boxsizer)
		
		vszrl.Add(commBox, 0, wx.EXPAND)
		
		vszrl.AddSpacer(20)

		commBox = wx.StaticBox(self, wx.ID_ANY, "Server")
		topBorder = commBox.GetBordersForSizer()[0]
		boxsizer = wx.BoxSizer(wx.VERTICAL)
		boxsizer.AddSpacer(topBorder+10)

		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.AddSpacer(20)
		hsz.Add(wx.StaticText(commBox, wx.ID_ANY, "Railroad COM Port: ", size=(130, -1)))		
		self.teRRComPort = wx.TextCtrl(commBox, wx.ID_ANY, "", size=(100, -1))
		self.teRRComPort.SetValue(self.settings.rrserver.rrtty)
		hsz.Add(self.teRRComPort)
		hsz.AddSpacer(20)
		boxsizer.Add(hsz)
		
		boxsizer.AddSpacer(10)

		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.AddSpacer(20)
		hsz.Add(wx.StaticText(commBox, wx.ID_ANY, "Cmd Station COM port: ", size=(130, -1)))		
		self.teDCCComPort = wx.TextCtrl(commBox, wx.ID_ANY, "", size=(100, -1))
		self.teDCCComPort.SetValue(self.settings.rrserver.dcctty)
		hsz.Add(self.teDCCComPort)
		hsz.AddSpacer(20)
		boxsizer.Add(hsz)

		boxsizer.AddSpacer(10)

		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.AddSpacer(20)
		hsz.Add(wx.StaticText(commBox, wx.ID_ANY, "Snapshot version limit: ", size=(130, -1)))
		self.teSnapshotLimit = wx.TextCtrl(commBox, wx.ID_ANY, "", size=(100, -1))
		self.teSnapshotLimit.SetValue("%d" % self.settings.rrserver.snapshotlimit)
		hsz.Add(self.teSnapshotLimit)
		hsz.AddSpacer(20)
		boxsizer.Add(hsz)

		boxsizer.AddSpacer(10)

		self.cbAutoLoadSnap = wx.CheckBox(commBox, wx.ID_ANY, "Autoload latest snapshot")
		boxsizer.Add(self.cbAutoLoadSnap, 0, wx.LEFT, 40)
		self.cbAutoLoadSnap.SetValue(self.settings.rrserver.autoloadsnapshot)

		boxsizer.AddSpacer(10)

		commBox.SetSizer(boxsizer)
		
		vszrl.Add(commBox, 0, wx.EXPAND)
		
		vszrl.AddSpacer(20)

		dispBox = wx.StaticBox(self, wx.ID_ANY, "Dispatcher/Display/Satellite")
		topBorder = dispBox.GetBordersForSizer()[0]
		boxsizer = wx.BoxSizer(wx.VERTICAL)
		boxsizer.AddSpacer(topBorder+10)

		self.rbMode = wx.RadioBox(dispBox, wx.ID_ANY, "Function", choices=["Dispatch", "Satellite", "Display"])
		boxsizer.Add(self.rbMode, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)
		rbv = 0 if self.settings.dispatcher.dispatch else 1 if self.settings.dispatcher.satellite else 2
		self.rbMode.SetSelection(rbv)

		boxsizer.AddSpacer(10)

		self.rbPages = wx.RadioBox(dispBox, wx.ID_ANY, "Pages", choices=["1", "3"])
		boxsizer.Add(self.rbPages, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)
		self.rbPages.SetSelection(0 if self.settings.display.pages == 1 else 1)

		boxsizer.AddSpacer(10)

		self.cbNotifyIncorrectRoute = wx.CheckBox(dispBox, wx.ID_ANY, "Notify signal cleared for incorrect route")
		boxsizer.Add(self.cbNotifyIncorrectRoute, 0, wx.LEFT, 40)
		self.cbNotifyIncorrectRoute.SetValue(self.settings.dispatcher.notifyincorrectroute)

		boxsizer.AddSpacer(10)

		self.cbNotifyInvalidBlocks = wx.CheckBox(dispBox, wx.ID_ANY, "Notify if train is in incorrect block(s)")
		boxsizer.Add(self.cbNotifyInvalidBlocks, 0, wx.LEFT, 40)
		self.cbNotifyInvalidBlocks.SetValue(self.settings.dispatcher.notifyinvalidblocks)

		boxsizer.AddSpacer(10)

		self.cbPrecheckShutdownServer = wx.CheckBox(dispBox, wx.ID_ANY, "Precheck \"Shutdown Server\" on exit")
		boxsizer.Add(self.cbPrecheckShutdownServer, 0, wx.LEFT, 40)
		self.cbPrecheckShutdownServer.SetValue(self.settings.dispatcher.precheckshutdownserver)

		boxsizer.AddSpacer(10)

		self.cbPrecheckSaveLogs = wx.CheckBox(dispBox, wx.ID_ANY, "Precheck \"Save Logs\" on exit")
		boxsizer.Add(self.cbPrecheckSaveLogs, 0, wx.LEFT, 40)
		self.cbPrecheckSaveLogs.SetValue(self.settings.dispatcher.prechecksavelogs)

		boxsizer.AddSpacer(10)

		self.cbPrecheckSnapshot = wx.CheckBox(dispBox, wx.ID_ANY, "Precheck \"Take Snapshot\" on exit")
		boxsizer.Add(self.cbPrecheckSnapshot, 0, wx.LEFT, 40)
		self.cbPrecheckSnapshot.SetValue(self.settings.dispatcher.prechecksnapshot)

		boxsizer.AddSpacer(10)

		dispBox.SetSizer(boxsizer)
		
		vszrl.Add(dispBox, 0, wx.EXPAND)
		
		vszrl.AddSpacer(20)

		vszrm = wx.BoxSizer(wx.VERTICAL)
		vszrm.AddSpacer(20)

		clrBox = wx.StaticBox(self, wx.ID_ANY, "Train Tag Colors")
		topBorder = clrBox.GetBordersForSizer()[0]
		boxsizer = wx.BoxSizer(wx.VERTICAL)
		boxsizer.AddSpacer(topBorder+10)

		stHdr = wx.StaticText(clrBox, wx.ID_ANY, "FG                   BG")
		boxsizer.Add(stHdr, 0, wx.LEFT, 94)
		boxsizer.AddSpacer(4)

		clrsz = wx.BoxSizer(wx.HORIZONTAL)
		clrsz.AddSpacer(20)

		self.stTag = wx.StaticText(clrBox, wx.ID_ANY, "Prefix:", size=(50, -1))
		clrsz.Add(self.stTag, 0, wx.TOP, 12)

		f = self.settings.display.colortagfg
		self.bTagFG = wx.Button(clrBox, wx.ID_ANY, "", size=(40, 40))
		self.bTagFG.SetBackgroundColour(wx.Colour(f[0], f[1], f[2]))
		self.Bind(wx.EVT_BUTTON, self.OnBTagFG, self.bTagFG)
		clrsz.Add(self.bTagFG)

		clrsz.AddSpacer(30)

		b = self.settings.display.colortagbg
		self.bTagBG = wx.Button(clrBox, wx.ID_ANY, "", size=(40, 40))
		self.bTagBG.SetBackgroundColour(wx.Colour(b[0], b[1], b[2]))
		self.Bind(wx.EVT_BUTTON, self.OnBTagBG, self.bTagBG)
		clrsz.Add(self.bTagBG)

		clrsz.AddSpacer(20)

		self.stTagEx = wx.StaticText(clrBox, wx.ID_ANY, " Example ")
		self.stTagEx.SetForegroundColour(wx.Colour(f[0], f[1], f[2]))
		self.stTagEx.SetBackgroundColour(wx.Colour(b[0], b[1], b[2]))
		clrsz.Add(self.stTagEx, 0, wx.TOP, 12)

		boxsizer.Add(clrsz)
		boxsizer.AddSpacer(10)

		clrsz = wx.BoxSizer(wx.HORIZONTAL)
		clrsz.AddSpacer(20)

		self.stTrain = wx.StaticText(clrBox, wx.ID_ANY, "Train:", size=(50, -1))
		clrsz.Add(self.stTrain, 0, wx.TOP, 12)

		f = self.settings.display.colortrainfg
		self.bTrainFG = wx.Button(clrBox, wx.ID_ANY, "", size=(40, 40))
		self.bTrainFG.SetBackgroundColour(wx.Colour(f[0], f[1], f[2]))
		self.Bind(wx.EVT_BUTTON, self.OnBTrainFG, self.bTrainFG)
		clrsz.Add(self.bTrainFG)

		clrsz.AddSpacer(30)

		b = self.settings.display.colortrainbg
		self.bTrainBG = wx.Button(clrBox, wx.ID_ANY, "", size=(40, 40))
		self.bTrainBG.SetBackgroundColour(wx.Colour(b[0], b[1], b[2]))
		self.Bind(wx.EVT_BUTTON, self.OnBTrainBG, self.bTrainBG)
		clrsz.Add(self.bTrainBG)

		clrsz.AddSpacer(20)

		self.stTrainEx = wx.StaticText(clrBox, wx.ID_ANY, " Example ")
		self.stTrainEx.SetForegroundColour(wx.Colour(f[0], f[1], f[2]))
		self.stTrainEx.SetBackgroundColour(wx.Colour(b[0], b[1], b[2]))
		clrsz.Add(self.stTrainEx, 0, wx.TOP, 12)

		boxsizer.Add(clrsz)
		boxsizer.AddSpacer(10)

		clrsz = wx.BoxSizer(wx.HORIZONTAL)
		clrsz.AddSpacer(20)

		self.stLoco = wx.StaticText(clrBox, wx.ID_ANY, "Loco:", size=(50, -1))
		clrsz.Add(self.stLoco, 0, wx.TOP, 12)

		f = self.settings.display.colorlocofg
		self.bLocoFG = wx.Button(clrBox, wx.ID_ANY, "", size=(40, 40))
		self.bLocoFG.SetBackgroundColour(wx.Colour(f[0], f[1], f[2]))
		self.Bind(wx.EVT_BUTTON, self.OnBLocoFG, self.bLocoFG)
		clrsz.Add(self.bLocoFG)

		clrsz.AddSpacer(30)

		b = self.settings.display.colorlocobg
		self.bLocoBG = wx.Button(clrBox, wx.ID_ANY, "", size=(40, 40))
		self.bLocoBG.SetBackgroundColour(wx.Colour(b[0], b[1], b[2]))
		self.Bind(wx.EVT_BUTTON, self.OnBLocoBG, self.bLocoBG)
		clrsz.Add(self.bLocoBG)

		clrsz.AddSpacer(20)

		self.stLocoEx = wx.StaticText(clrBox, wx.ID_ANY, " Example ")
		self.stLocoEx.SetForegroundColour(wx.Colour(f[0], f[1], f[2]))
		self.stLocoEx.SetBackgroundColour(wx.Colour(b[0], b[1], b[2]))
		clrsz.Add(self.stLocoEx, 0, wx.TOP, 12)

		boxsizer.Add(clrsz)

		boxsizer.AddSpacer(10)

		clrBox.SetSizer(boxsizer)

		vszrm.Add(clrBox, 0, wx.EXPAND)

		vszrm.AddSpacer(20)

		dispBox = wx.StaticBox(self, wx.ID_ANY, "Display")
		topBorder = dispBox.GetBordersForSizer()[0]
		boxsizer = wx.BoxSizer(wx.VERTICAL)
		boxsizer.AddSpacer(topBorder+10)

		self.cbShowEvents = wx.CheckBox(dispBox, wx.ID_ANY, "Show Events")
		boxsizer.Add(self.cbShowEvents, 0, wx.LEFT, 40)
		self.cbShowEvents.SetValue(self.settings.display.showevents)

		boxsizer.AddSpacer(10)

		self.cbShowAdvice = wx.CheckBox(dispBox, wx.ID_ANY, "Show Advice")
		boxsizer.Add(self.cbShowAdvice, 0, wx.LEFT, 40)
		self.cbShowAdvice.SetValue(self.settings.display.showadvice)

		boxsizer.AddSpacer(10)

		self.cbShowUnknown = wx.CheckBox(dispBox, wx.ID_ANY, "Show Unknown Train History")
		boxsizer.Add(self.cbShowUnknown, 0, wx.LEFT, 40)
		self.cbShowUnknown.SetValue(self.settings.display.showunknownhistory)

		boxsizer.AddSpacer(10)

		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.AddSpacer(40)
		hsz.Add(wx.StaticText(dispBox, wx.ID_ANY, "Locale:"))
		hsz.AddSpacer(10)

		self.locales = ["<none>", "cliff", "port", "yard"]
		self.chLocale = wx.Choice(dispBox, wx.ID_ANY, choices=self.locales)
		hsz.Add(self.chLocale)
		try:
			lx = self.locales.index(self.settings.display.locale)
		except ValueError:
			lx = 0
		self.chLocale.SetSelection(lx)
		boxsizer.Add(hsz)

		boxsizer.AddSpacer(10)

		dispBox.SetSizer(boxsizer)
		
		vszrm.Add(dispBox, 0, wx.EXPAND)
		vszrm.AddSpacer(20)

		scannerBox = wx.StaticBox(self, wx.ID_ANY, "QR Code Scanner")
		topBorder = scannerBox.GetBordersForSizer()[0]
		boxsizer = wx.BoxSizer(wx.VERTICAL)
		boxsizer.AddSpacer(topBorder + 10)

		boxsizer.AddSpacer(10)

		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.AddSpacer(20)
		hsz.Add(wx.StaticText(scannerBox, wx.ID_ANY, "Scanner COM port: ", size=(130, -1)))
		self.teScannerComPort = wx.TextCtrl(scannerBox, wx.ID_ANY, "", size=(100, -1))
		self.teScannerComPort.SetValue(self.settings.scanner.tty)
		hsz.Add(self.teScannerComPort)
		hsz.AddSpacer(20)
		boxsizer.Add(hsz)

		self.cbScannerEnable = wx.CheckBox(scannerBox, wx.ID_ANY, "Enable")
		boxsizer.Add(self.cbScannerEnable, 0, wx.LEFT, 40)
		self.cbScannerEnable.SetValue(self.settings.scanner.enable)

		boxsizer.AddSpacer(10)

		scannerBox.SetSizer(boxsizer)

		vszrm.Add(scannerBox, 0, wx.EXPAND)

		vszrm.AddSpacer(20)

		snifferBox = wx.StaticBox(self, wx.ID_ANY, "DCC Sniffer")
		topBorder = snifferBox.GetBordersForSizer()[0]
		boxsizer = wx.BoxSizer(wx.VERTICAL)
		boxsizer.AddSpacer(topBorder + 10)

		boxsizer.AddSpacer(10)

		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.AddSpacer(20)
		hsz.Add(wx.StaticText(snifferBox, wx.ID_ANY, "DCC Sniffer COM port: ", size=(130, -1)))
		self.teSnifferComPort = wx.TextCtrl(snifferBox, wx.ID_ANY, "", size=(100, -1))
		self.teSnifferComPort.SetValue(self.settings.dccsniffer.tty)
		hsz.Add(self.teSnifferComPort)
		hsz.AddSpacer(20)
		boxsizer.Add(hsz)

		self.cbSnifferEnable = wx.CheckBox(snifferBox, wx.ID_ANY, "Enable")
		boxsizer.Add(self.cbSnifferEnable, 0, wx.LEFT, 40)
		self.cbSnifferEnable.SetValue(self.settings.dccsniffer.enable)

		boxsizer.AddSpacer(10)

		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.AddSpacer(20)
		hsz.Add(wx.StaticText(snifferBox, wx.ID_ANY, "Interval (usec): ", size=(130, -1)))
		self.teInterval = wx.TextCtrl(snifferBox, wx.ID_ANY, "", size=(100, -1))
		self.teInterval.SetValue("%d" % self.settings.dccsniffer.interval)
		hsz.Add(self.teInterval)
		hsz.AddSpacer(20)
		boxsizer.Add(hsz)

		boxsizer.AddSpacer(10)

		snifferBox.SetSizer(boxsizer)

		vszrm.Add(snifferBox, 0, wx.EXPAND)

		vszrm.AddSpacer(20)

		vszrr = wx.BoxSizer(wx.VERTICAL)
		vszrr.AddSpacer(20)

		atBox = wx.StaticBox(self, wx.ID_ANY, "Active Trains")
		topBorder = atBox.GetBordersForSizer()[0]
		boxsizer = wx.BoxSizer(wx.VERTICAL)
		boxsizer.AddSpacer(topBorder + 10)

		self.cbSuppressYards = wx.CheckBox(atBox, wx.ID_ANY, "Suppress Yards")
		boxsizer.Add(self.cbSuppressYards, 0, wx.LEFT, 40)
		self.cbSuppressYards.SetValue(self.settings.activetrains.suppressyards)

		boxsizer.AddSpacer(10)

		self.showonly = ["All", "Known", "Assigned", "Assigned or Unknown"]
		self.rbShowOnly = wx.RadioBox(atBox, wx.ID_ANY, "Show Only", choices=self.showonly,
									  majorDimension=1, style=wx.RA_SPECIFY_COLS)
		boxsizer.Add(self.rbShowOnly, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)
		ix = 0
		if self.settings.activetrains.suppressunknown:
			ix = 1
		elif self.settings.activetrains.onlyassigned:
			ix = 2
		elif self.settings.activetrains.onlyassignedorunknown:
			ix = 3
		self.rbShowOnly.SetSelection(ix)

		boxsizer.AddSpacer(10)

		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.AddSpacer(20)
		hsz.Add(wx.StaticText(atBox, wx.ID_ANY, "Lines: ", size=(130, -1)))
		self.teLines = wx.TextCtrl(atBox, wx.ID_ANY, "", size=(100, -1))
		self.teLines.SetValue("%d" % self.settings.activetrains.lines)
		hsz.Add(self.teLines)
		hsz.AddSpacer(20)
		boxsizer.Add(hsz)

		boxsizer.AddSpacer(10)

		atBox.SetSizer(boxsizer)

		vszrr.Add(atBox, 0, wx.EXPAND)
		vszrr.AddSpacer(20)

		controlBox = wx.StaticBox(self, wx.ID_ANY, "Control")
		topBorder = controlBox.GetBordersForSizer()[0]
		boxsizer = wx.BoxSizer(wx.VERTICAL)
		boxsizer.AddSpacer(topBorder+10)

		boxsizer.AddSpacer(10)
		
		self.ctlCliff = ["Cliff", "Dispatcher Bank/Cliveden", "Dispatcher All"]	
		self.rbCtlCliff = wx.RadioBox(controlBox, wx.ID_ANY, "Cliff", choices=self.ctlCliff,
					majorDimension=1, style=wx.RA_SPECIFY_COLS)
		boxsizer.Add(self.rbCtlCliff, 2, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)
		self.rbCtlCliff.SetSelection(self.settings.control.cliff)

		boxsizer.AddSpacer(10)
		
		self.ctlNassau = ["Nassau", "Dispatcher Main", "Dispatcher All"]	
		self.rbCtlNassau = wx.RadioBox(controlBox, wx.ID_ANY, "Nassau", choices=self.ctlNassau,
					majorDimension=1, style=wx.RA_SPECIFY_COLS)
		boxsizer.Add(self.rbCtlNassau, 2, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)
		self.rbCtlNassau.SetSelection(self.settings.control.nassau)
		
		boxsizer.AddSpacer(10)
	
		self.ctlYard = ["Yard", "Dispatcher"]	
		self.rbCtlYard = wx.RadioBox(controlBox, wx.ID_ANY, "Yard", choices=self.ctlYard,
					majorDimension=1, style=wx.RA_SPECIFY_COLS)
		boxsizer.Add(self.rbCtlYard, 2, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)
		self.rbCtlYard.SetSelection(self.settings.control.yard)

		boxsizer.AddSpacer(10)

		controlBox.SetSizer(boxsizer)
		
		vszrr.Add(controlBox, 0, wx.EXPAND)

		vszr = wx.BoxSizer(wx.VERTICAL)
		hszr = wx.BoxSizer(wx.HORIZONTAL)
		hszr.Add(vszrl, 1, wx.EXPAND)
		hszr.AddSpacer(30)
		hszr.Add(vszrm, 1, wx.EXPAND)
		hszr.AddSpacer(30)
		hszr.Add(vszrr, 1, wx.EXPAND)

		vszr.Add(hszr)
		
		vszrfile = wx.BoxSizer(wx.VERTICAL)
				
		vszrfile.Add(wx.StaticText(self, wx.ID_ANY, "Backup Directory:"))
		
		self.teBackupDir = wx.TextCtrl(self, wx.ID_ANY, self.settings.backupdir, size=(450, -1), style=wx.TE_READONLY)
		self.bBackupDir = wx.Button(self, wx.ID_ANY, "...", size=(40, -1))
		self.Bind(wx.EVT_BUTTON, self.OnBBackupDir, self.bBackupDir)
		
		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.Add(self.teBackupDir)
		hsz.AddSpacer(10)
		hsz.Add(self.bBackupDir)
		
		vszrfile.AddSpacer(5)
		vszrfile.Add(hsz)

		vszrfile.Add(wx.StaticText(self, wx.ID_ANY, "Browser Location:"))

		browser = "" if self.settings.browser is None else self.settings.browser
		self.teBrowser = wx.TextCtrl(self, wx.ID_ANY, browser, size=(450, -1), style=wx.TE_READONLY)
		self.bBrowser = wx.Button(self, wx.ID_ANY, "...", size=(40, -1))
		self.Bind(wx.EVT_BUTTON, self.OnBBrowser, self.bBrowser)

		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.Add(self.teBrowser)
		hsz.AddSpacer(10)
		hsz.Add(self.bBrowser)

		vszrfile.AddSpacer(5)
		vszrfile.Add(hsz)

		vszrfile.Add(wx.StaticText(self, wx.ID_ANY, "Spreadsheet Location:"))

		spreadsheet = "" if self.settings.spreadsheet is None else self.settings.spreadsheet
		self.teCalc = wx.TextCtrl(self, wx.ID_ANY, spreadsheet, size=(450, -1), style=wx.TE_READONLY)
		self.bCalc = wx.Button(self, wx.ID_ANY, "...", size=(40, -1))
		self.Bind(wx.EVT_BUTTON, self.OnBCalc, self.bCalc)

		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.Add(self.teCalc)
		hsz.AddSpacer(10)
		hsz.Add(self.bCalc)

		vszrfile.AddSpacer(5)
		vszrfile.Add(hsz)

		vszr.AddSpacer(10)
		vszr.Add(vszrfile, 9, wx.ALIGN_CENTER_HORIZONTAL)

		vszr.AddSpacer(20)

		btnszr = wx.BoxSizer(wx.HORIZONTAL)
		btnszr2 = wx.BoxSizer(wx.HORIZONTAL)

		self.bSave = wx.Button(self, wx.ID_ANY, "Save", size=(200, 60))
		btnszr.Add(self.bSave)
		self.Bind(wx.EVT_BUTTON, self.OnBSave, self.bSave)
		btnszr.AddSpacer(20)
		
		self.bGenerate = wx.Button(self, wx.ID_ANY, "Generate Shortcuts/Start Menu", size=(200, 60))
		btnszr.Add(self.bGenerate)
		self.Bind(wx.EVT_BUTTON, self.OnBGenerate, self.bGenerate)

		self.bBackup = wx.Button(self, wx.ID_ANY, "Backup Data Files", size=(200, 60))
		btnszr2.Add(self.bBackup)
		btnszr2.AddSpacer(20)
		self.Bind(wx.EVT_BUTTON, self.OnBBackup, self.bBackup)
		self.bRestore = wx.Button(self, wx.ID_ANY, "Restore Data Files", size=(200, 60))
		btnszr2.Add(self.bRestore)
		self.Bind(wx.EVT_BUTTON, self.OnBRestore, self.bRestore)
		
		vszr.Add(btnszr2, 0, wx.ALIGN_CENTER_HORIZONTAL)
		vszr.AddSpacer(30)
		vszr.Add(btnszr, 0, wx.ALIGN_CENTER_HORIZONTAL)
		vszr.AddSpacer(30)

		hszr = wx.BoxSizer(wx.HORIZONTAL)
		hszr.AddSpacer(10)
		hszr.Add(vszr)
		hszr.AddSpacer(10)
		
		self.SetSizer(hszr)
		self.Fit()
		self.Layout()
		
		if install:
			self.GenConfigShortcut()
		
	@staticmethod
	def GenConfigShortcut():
		module = {
			"name": "PSRY Suite Configuration",
			"dir":  "config",
			"main": "main.py",
			"desc": "Configuration Tool",
			"icon": "config.ico",
		}
		GenShortcut(module, True)
		module = {
			"name": "PSRY Suite - save logs",
			"dir":  "savelogs",
			"main": "main.py",
			"desc": "Save Logs and output for debugging",
			"icon": "savelogs.ico",
		}
		GenShortcut(module, True)

	def OnBBackupDir(self, _):
		startDir = self.teBackupDir.GetValue()
		dlg = wx.DirDialog(self, "Choose a backup directory:", defaultPath=startDir, style=wx.DD_DEFAULT_STYLE)
		rc = dlg.ShowModal()
		path = None
		if rc == wx.ID_OK:
			path = dlg.GetPath()

		dlg.Destroy()
		if rc != wx.ID_OK:
			return 
		
		self.teBackupDir.SetValue(path)

	def OnBTagFG(self, _):
		c = self.settings.display.colortagfg
		nc = self.ChooseColor(c[0], c[1], c[2], "Prefix Foreground")
		if nc is not None:
			self.settings.display.colortagfg = nc
			nclr = wx.Colour(nc[0], nc[1], nc[2])
			self.bTagFG.SetBackgroundColour(nclr)
			self.stTagEx.SetForegroundColour(nclr)
			self.stTagEx.Refresh()

	def OnBTagBG(self, _):
		c = self.settings.display.colortagbg
		nc = self.ChooseColor(c[0], c[1], c[2], "Prefix Background")
		if nc is not None:
			self.settings.display.colortagbg = nc
			nclr = wx.Colour(nc[0], nc[1], nc[2])
			self.bTagBG.SetBackgroundColour(nclr)
			self.stTagEx.SetBackgroundColour(nclr)
			self.stTagEx.Refresh()

	def OnBTrainFG(self, _):
		c = self.settings.display.colortrainfg
		nc = self.ChooseColor(c[0], c[1], c[2], "Train Foreground")
		if nc is not None:
			self.settings.display.colortrainfg = nc
			nclr = wx.Colour(nc[0], nc[1], nc[2])
			self.bTrainFG.SetBackgroundColour(nclr)
			self.stTrainEx.SetForegroundColour(nclr)
			self.stTrainEx.Refresh()

	def OnBTrainBG(self, _):
		c = self.settings.display.colortrainbg
		nc = self.ChooseColor(c[0], c[1], c[2], "Train Background")
		if nc is not None:
			self.settings.display.colortrainbg = nc
			nclr = wx.Colour(nc[0], nc[1], nc[2])
			self.bTrainBG.SetBackgroundColour(nclr)
			self.stTrainEx.SetBackgroundColour(nclr)
			self.stTrainEx.Refresh()

	def OnBLocoFG(self, _):
		c = self.settings.display.colorlocofg
		nc = self.ChooseColor(c[0], c[1], c[2], "Loco Foreground")
		if nc is not None:
			self.settings.display.colorlocofg = nc
			nclr = wx.Colour(nc[0], nc[1], nc[2])
			self.bLocoFG.SetBackgroundColour(nclr)
			self.stLocoEx.SetForegroundColour(nclr)
			self.stLocoEx.Refresh()

	def OnBLocoBG(self, _):
		c = self.settings.display.colorlocobg
		nc = self.ChooseColor(c[0], c[1], c[2], "Loco Background")
		if nc is not None:
			self.settings.display.colorlocobg = nc
			nclr = wx.Colour(nc[0], nc[1], nc[2])
			self.bLocoBG.SetBackgroundColour(nclr)
			self.stLocoEx.SetBackgroundColour(nclr)
			self.stLocoEx.Refresh()

	def ChooseColor(self, r, g, b, dlgTitle):
		dlg = wx.ColourDialog(self)
		dlg.SetTitle("Choose color for %s" % dlgTitle)
		data = dlg.GetColourData()
		data.SetChooseFull(True)
		data.SetColour(wx.Colour(r, g, b, 255))
		rc = dlg.ShowModal()
		if rc != wx.ID_OK:
			dlg.Destroy()
			return None

		data = dlg.GetColourData()

		color = data.GetColour().Get()
		dlg.Destroy()

		if len(color) < 3:
			return None   # don't know how to deal with this
		return color[0:3]

	def OnBBrowser(self, _):
		wildcard = "All files (*.*)|*.*"
		startPath = self.teBrowser.GetValue()
		spath = os.path.split(startPath)
		sdir = spath[0]
		if len(spath) == 1:
			sfile = ""
		else:
			sfile = spath[1]

		dlg = wx.FileDialog(
			self, message="Choose browser executable",
			defaultDir=sdir,
			defaultFile=sfile,
			wildcard=wildcard,
			style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST | wx.FD_PREVIEW)

		rc = dlg.ShowModal()
		path = None
		if rc == wx.ID_OK:
			path = dlg.GetPath()

		dlg.Destroy()
		if rc != wx.ID_OK:
			return

		self.teBrowser.SetValue(path)

	def OnBCalc(self, _):
		wildcard = "All files (*.*)|*.*"
		startPath = self.teCalc.GetValue()
		spath = os.path.split(startPath)
		sdir = spath[0]
		if len(spath) == 1:
			sfile = ""
		else:
			sfile = spath[1]

		dlg = wx.FileDialog(
			self, message="Choose spreadsheet executable",
			defaultDir=sdir,
			defaultFile=sfile,
			wildcard=wildcard,
			style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST | wx.FD_PREVIEW)

		rc = dlg.ShowModal()
		path = None
		if rc == wx.ID_OK:
			path = dlg.GetPath()

		dlg.Destroy()
		if rc != wx.ID_OK:
			return

		self.teCalc.SetValue(path)

	def OnBGenerate(self, _):
		dlg = GenerateDlg(self, GenShortcut)
		dlg.ShowModal()
		dlg.Destroy()

	def OnBBackup(self, _):
		saveData(self, self.settings)
				
	def OnBRestore(self, _):
		restoreData(self, self.settings)
		
	def OnBSave(self, _):
		self.settings.ipaddr = self.teIpAddr.GetValue()
		self.settings.serverport = int(self.teRRPort.GetValue())
		self.settings.dccserverport = int(self.teDCCPort.GetValue())
		self.settings.socketport = int(self.teBroadcastPort.GetValue())
		self.settings.webappport = int(self.teWebPort.GetValue())
		self.settings.backupdir = self.teBackupDir.GetValue()
		self.settings.browser = self.teBrowser.GetValue()
		self.settings.spreadsheet = self.teCalc.GetValue()
		if self.settings.spreadsheet.strip() == "":
			self.settings.spreadsheet = None

		rbv = self.rbMode.GetSelection()
		self.settings.dispatcher.dispatch = rbv == 0
		self.settings.dispatcher.satellite = rbv == 1
		self.settings.dispatcher.notifyincorrectroute = self.cbNotifyIncorrectRoute.IsChecked()
		self.settings.dispatcher.notifyinvalidblocks = self.cbNotifyInvalidBlocks.IsChecked()
		self.settings.dispatcher.precheckshutdownserver = self.cbPrecheckShutdownServer.IsChecked()
		self.settings.dispatcher.prechecksnapshot = self.cbPrecheckSnapshot.IsChecked()
		self.settings.dispatcher.prechecksavelogs = self.cbPrecheckSaveLogs.IsChecked()

		self.settings.rrserver.rrtty = self.teRRComPort.GetValue()
		self.settings.rrserver.dcctty = self.teDCCComPort.GetValue()
		self.settings.rrserver.snapshotlimit = int(self.teSnapshotLimit.GetValue())
		self.settings.rrserver.autoloadsnapshot = self.cbAutoLoadSnap.IsChecked()

		self.settings.scanner.tty = self.teScannerComPort.GetValue()
		self.settings.scanner.enable = self.cbScannerEnable.IsChecked()

		self.settings.dccsniffer.tty = self.teSnifferComPort.GetValue()
		self.settings.dccsniffer.enable = self.cbSnifferEnable.IsChecked()
		self.settings.dccsniffer.interval = int(self.teInterval.GetValue())

		self.settings.display.pages = 1 if self.rbPages.GetSelection() == 0 else 3
		self.settings.display.showevents = self.cbShowEvents.IsChecked()
		self.settings.display.showadvice = self.cbShowAdvice.IsChecked()
		self.settings.display.showunknownhistory = self.cbShowUnknown.IsChecked()
		self.settings.display.locale = self.chLocale.GetStringSelection()
		if self.settings.display.locale == self.locales[0]:
			self.settings.display.locale = ""

		print("In save, color = %s" % str(self.settings.display.colortrainfg))

		self.settings.activetrains.suppressyards = self.cbSuppressYards.IsChecked()		
		ix = self.rbShowOnly.GetSelection()
		self.settings.activetrains.suppressunknown = False
		self.settings.activetrains.onlyassigned = False
		self.settings.activetrains.onlyassignedorunknown = False
		if ix == 1:
			self.settings.activetrains.suppressunknown = True
		elif ix == 2:
			self.settings.activetrains.onlyassigned = True
		elif ix == 3:
			self.settings.activetrains.onlyassignedorunknown = True
		cv = self.settings.activetrains.lines
		try:
			self.settings.activetrains.lines = int(self.teLines.GetValue())
		except ValueError:
			self.settings.activetrains.lines = cv
		
		self.settings.control.cliff = self.rbCtlCliff.GetSelection()
		self.settings.control.nassau = self.rbCtlNassau.GetSelection()
		self.settings.control.yard = self.rbCtlYard.GetSelection()

		if self.settings.SaveAll():
			dlg = wx.MessageDialog(self, "Configuration Data has been saved", "Data Saved", wx.OK | wx.ICON_INFORMATION)
		else:
			dlg = wx.MessageDialog(self, "Unable to save configuration data", "Save Failed", wx.OK | wx.ICON_ERROR)
			
		dlg.ShowModal()
		dlg.Destroy()

	def OnClose(self, _):
		self.Destroy()
