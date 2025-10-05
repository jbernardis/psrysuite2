import wx
import os
import winshell
import glob

from config.cleandlg import CleanDlg

GENBTNSZ = (170, 40)


class GenerateDlg(wx.Dialog):
	def __init__(self, parent, generator):
		wx.Dialog.__init__(self, parent, wx.ID_ANY, "Generate Shortcuts/Start Menu")
		self.Bind(wx.EVT_CLOSE, self.OnClose)
		
		self.generator = generator
	
		vszr = wx.BoxSizer(wx.VERTICAL)
		vszr.AddSpacer(20)
		
		genBox = wx.StaticBox(self, wx.ID_ANY, "Generate Shortcuts")
		topBorder = genBox.GetBordersForSizer()[0]
		boxsizer = wx.BoxSizer(wx.VERTICAL)
		boxsizer.AddSpacer(topBorder)
		
		hsz = wx.BoxSizer(wx.HORIZONTAL)
		
		vsz = wx.BoxSizer(wx.VERTICAL)
		
		self.bGenDispatch = wx.Button(genBox, wx.ID_ANY, "Dispatcher", size=GENBTNSZ)
		self.Bind(wx.EVT_BUTTON, self.OnBGenDispatch, self.bGenDispatch)
		vsz.Add(self.bGenDispatch, 0, wx.ALL, 10)
				
		self.bGenRemoteDispatch = wx.Button(genBox, wx.ID_ANY, "Remote Dispatcher", size=GENBTNSZ)
		self.Bind(wx.EVT_BUTTON, self.OnBGenRemoteDispatch, self.bGenRemoteDispatch)
		vsz.Add(self.bGenRemoteDispatch, 0, wx.ALL, 10)
					
		self.bGenSimulation = wx.Button(genBox, wx.ID_ANY, "Simulation", size=GENBTNSZ)
		self.Bind(wx.EVT_BUTTON, self.OnBGenSimulation, self.bGenSimulation)
		vsz.Add(self.bGenSimulation, 0, wx.ALL, 10)

		self.bGenDisplay = wx.Button(genBox, wx.ID_ANY, "Display", size=GENBTNSZ)
		self.Bind(wx.EVT_BUTTON, self.OnBGenDisplay, self.bGenDisplay)
		vsz.Add(self.bGenDisplay, 0, wx.ALL, 10)

		self.bGenCliffDisplay = wx.Button(genBox, wx.ID_ANY, "Cliff Display", size=GENBTNSZ)
		self.Bind(wx.EVT_BUTTON, self.OnBGenCliffDisplay, self.bGenCliffDisplay)
		vsz.Add(self.bGenCliffDisplay, 0, wx.ALL, 10)

		self.bGenSatellite = wx.Button(genBox, wx.ID_ANY, "Satellite", size=GENBTNSZ)
		self.Bind(wx.EVT_BUTTON, self.OnBGenSatellite, self.bGenSatellite)
		vsz.Add(self.bGenSatellite, 0, wx.ALL, 10)

		self.bGenActive = wx.Button(genBox, wx.ID_ANY, "Active Trains", size=GENBTNSZ)
		self.Bind(wx.EVT_BUTTON, self.OnBGenActive, self.bGenActive)
		vsz.Add(self.bGenActive, 0, wx.ALL, 10)

		hsz.Add(vsz)
		
		vsz = wx.BoxSizer(wx.VERTICAL)
					
		self.bGenThrottle = wx.Button(genBox, wx.ID_ANY, "Throttle", size=GENBTNSZ)
		self.Bind(wx.EVT_BUTTON, self.OnBGenThrottle, self.bGenThrottle)
		vsz.Add(self.bGenThrottle, 0, wx.ALL, 10)

		self.bDiagEdit = wx.Button(genBox, wx.ID_ANY, "Diagram Editor", size=GENBTNSZ)
		self.Bind(wx.EVT_BUTTON, self.OnBDiagEdit, self.bDiagEdit)
		vsz.Add(self.bDiagEdit, 0, wx.ALL, 10)

		self.bGenEditor = wx.Button(genBox, wx.ID_ANY, "Database Editor", size=GENBTNSZ)
		self.Bind(wx.EVT_BUTTON, self.OnBGenEditor, self.bGenEditor)
		vsz.Add(self.bGenEditor, 0, wx.ALL, 10)
					
		self.bGenSaveLogs = wx.Button(genBox, wx.ID_ANY, "Save Log Files", size=GENBTNSZ)
		self.Bind(wx.EVT_BUTTON, self.OnBGenSaveLogs, self.bGenSaveLogs)
		vsz.Add(self.bGenSaveLogs, 0, wx.ALL, 10)
		
		hsz.Add(vsz)
		
		vsz = wx.BoxSizer(wx.VERTICAL)
					
		self.bGenServerOnly = wx.Button(genBox, wx.ID_ANY, "Server Only", size=GENBTNSZ)
		self.Bind(wx.EVT_BUTTON, self.OnBGenServerOnly, self.bGenServerOnly)
		vsz.Add(self.bGenServerOnly, 0, wx.ALL, 10)

		self.bGenServerOnlySim = wx.Button(genBox, wx.ID_ANY, "Server Only\n(simulated)", size=GENBTNSZ)
		self.Bind(wx.EVT_BUTTON, self.OnBGenServerOnlySim, self.bGenServerOnlySim)
		vsz.Add(self.bGenServerOnlySim, 0, wx.ALL, 10)

		self.bGenDispatcherOnly = wx.Button(genBox, wx.ID_ANY, "Dispatcher Only", size=GENBTNSZ)
		self.Bind(wx.EVT_BUTTON, self.OnBGenDispatcherOnly, self.bGenDispatcherOnly)
		vsz.Add(self.bGenDispatcherOnly, 0, wx.ALL, 10)
					
		self.bGenTester = wx.Button(genBox, wx.ID_ANY, "Tester", size=GENBTNSZ)
		self.Bind(wx.EVT_BUTTON, self.OnBGenTester, self.bGenTester)
		vsz.Add(self.bGenTester, 0, wx.ALL, 10)
					
		self.bGenConfig = wx.Button(genBox, wx.ID_ANY, "Configuration Utility", size=GENBTNSZ)
		self.Bind(wx.EVT_BUTTON, self.OnBGenConfig, self.bGenConfig)
		vsz.Add(self.bGenConfig, 0, wx.ALL, 10)

		self.bGenMonitor = wx.Button(genBox, wx.ID_ANY, "Server Monitor", size=GENBTNSZ)
		self.Bind(wx.EVT_BUTTON, self.OnBGenMonitor, self.bGenMonitor)
		vsz.Add(self.bGenMonitor, 0, wx.ALL, 10)

		self.bGenMonitorSim = wx.Button(genBox, wx.ID_ANY, "Server Monitor\n(simulated)", size=GENBTNSZ)
		self.Bind(wx.EVT_BUTTON, self.OnBGenMonitorSim, self.bGenMonitorSim)
		vsz.Add(self.bGenMonitorSim, 0, wx.ALL, 10)
		
		hsz.Add(vsz)
		
		boxsizer.Add(hsz)
		
		genBox.SetSizer(boxsizer)
		
		vszr.Add(genBox, 0, wx.ALIGN_CENTER_HORIZONTAL)
		vszr.AddSpacer(10)
		
		self.cbStartMenu = wx.CheckBox(self, wx.ID_ANY, "Also add to Start menu")
		vszr.Add(self.cbStartMenu, 0, wx.ALIGN_CENTER_HORIZONTAL)
		self.cbStartMenu.SetValue(False)
		vszr.AddSpacer(30)
		
		hsz = wx.BoxSizer(wx.HORIZONTAL)
		
		self.bClean = wx.Button(self, wx.ID_ANY, "Clean up Shortcuts", size=GENBTNSZ)
		self.Bind(wx.EVT_BUTTON, self.OnBClean, self.bClean)
		hsz.Add(self.bClean)
		hsz.AddSpacer(50)

		self.bCleanMenu = wx.Button(self, wx.ID_ANY, "Clean up Start Menu", size=GENBTNSZ)
		self.Bind(wx.EVT_BUTTON, self.OnBCleanMenu, self.bCleanMenu)
		hsz.Add(self.bCleanMenu)
		
		vszr.Add(hsz, 0, wx.ALIGN_CENTER_HORIZONTAL)
		vszr.AddSpacer(20)

		hszr = wx.BoxSizer(wx.HORIZONTAL)
		hszr.AddSpacer(10)
		hszr.Add(vszr)
		hszr.AddSpacer(10)
		
		self.SetSizer(hszr)
		self.Fit()
		self.Layout()

	def OnBGenDispatch(self, _):
		module = {
			"name": "PSRY Dispatcher Suite",
			"dir": "launcher",
			"main": "main.py",
			"desc": "Launcher for Local Dispatcher",
			"icon": "launcher.ico",
			"parameter": "dispatcher"
		}
		self.generator(module, self.cbStartMenu.IsChecked())

	def OnBGenSatellite(self, _):
		module = {
			"name": "PSRY Satellite",
			"dir": "launcher",
			"main": "main.py",
			"desc": "Launcher for Dispatcher Satellite",
			"icon": "launcher.ico",
			"parameter": "satellite"
		}
		self.generator(module, self.cbStartMenu.IsChecked())

	def OnBGenRemoteDispatch(self, _):
		module = {
			"name": "PSRY Remote Dispatcher",
			"dir":  "launcher",
			"main": "main.py",
			"desc": "Launcher for Remote Dispatcher",
			"icon": "launcher.ico",
			"parameter": "remotedispatcher"
		}
		self.generator(module, self.cbStartMenu.IsChecked())
		
	def OnBGenSimulation(self, _):
		module = {
			"name": "PSRY Simulator Suite",
			"dir":  "launcher",
			"main": "main.py",
			"desc": "Launcher for Simulation",
			"icon": "launcher.ico",
			"parameter": "simulation"
		}
		self.generator(module, self.cbStartMenu.IsChecked())

	def OnBGenDisplay(self, _):
		module = {
			"name": "PSRY Display",
			"dir": "launcher",
			"main": "main.py",
			"desc": "Launcher for Display",
			"icon": "launcher.ico",
			"parameter": "display"
		}
		self.generator(module, self.cbStartMenu.IsChecked())

	def OnBGenCliffDisplay(self, _):
		module = {
			"name": "PSRY Cliff Display",
			"dir": "launcher",
			"main": "main.py",
			"desc": "Launcher for Cliff Display",
			"icon": "launcher.ico",
			"parameter": "cliffdisplay"
		}
		self.generator(module, self.cbStartMenu.IsChecked())

	def OnBGenServerOnly(self, _):
		module = {
			"name": "PSRY Server Only",
			"dir":  "launcher",
			"main": "main.py",
			"desc": "Railroad Server",
			"icon": "launcher.ico",
			"parameter": "serveronly"
		}	
		self.generator(module, self.cbStartMenu.IsChecked())

	def OnBGenServerOnlySim(self, _):
		module = {
			"name": "PSRY Server Only (simulated)",
			"dir":  "launcher",
			"main": "main.py",
			"desc": "Railroad Server",
			"icon": "launcher.ico",
			"parameter": "serveronlysim"
		}
		self.generator(module, self.cbStartMenu.IsChecked())

	def OnBGenDispatcherOnly(self, _):
		module = {
			"name": "PSRY Dispatcher Only",
			"dir":  "launcher",
			"main": "main.py",
			"desc": "Dispatcher Only",
			"icon": "launcher.ico",
			"parameter": "dispatcheronly"
		}	
		self.generator(module, self.cbStartMenu.IsChecked())

	def OnBGenThrottle(self, _):
		module = {
			"name": "PSRY Throttle",
			"dir": "throttle",
			"main": "main.py",
			"desc": "Throttle",
			"icon": "throttle.ico"
		}
		self.generator(module, self.cbStartMenu.IsChecked())

	def OnBGenEditor(self, _):
		module = {
			"name": "PSRY Database Editor",
			"dir":  "traineditor",
			"main": "main.py",
			"desc": "Train/Locomotive/Engineer Editor",
			"icon": "editor.ico"
		}
		self.generator(module, self.cbStartMenu.IsChecked())

	def OnBDiagEdit(self, _):
		module = {
			"name": "PSRY Diagram Editor",
			"dir":  "diageditor",
			"main": "mainframe.py",
			"desc": "Track Diagram Editor",
			"icon": "diagedit.ico"
		}
		self.generator(module, self.cbStartMenu.IsChecked())

	def OnBGenMonitor(self, _):
		module = {
			"name": "PSRY Monitor for Server",
			"dir":  "monitor",
			"main": "main.py",
			"parameter": "--nosim",
			"desc": "Monitor for Server",
			"icon": "monitor.ico"
		}
		self.generator(module, self.cbStartMenu.IsChecked())
		
	def OnBGenMonitorSim(self, _):
		module = {
			"name": "PSRY Monitor for Simulated Server",
			"dir":  "monitor",
			"main": "main.py",
			"parameter": "--sim",
			"desc": "Monitor for Simulated Server",
			"icon": "monitor.ico"
		}
		self.generator(module, self.cbStartMenu.IsChecked())

	def OnBGenTester(self, _):
		module = {
			"name": "PSRY Tester Utility",
			"dir":  "tester",
			"main": "main.py",
			"desc": "Tester",
			"icon": "tester.ico"
		}
		self.generator(module, self.cbStartMenu.IsChecked())

	def OnBGenActive(self, _):
		module = {
			"name": "PSRY Active Trains",
			"dir":  "activetrains",
			"main": "main.py",
			"desc": "Active Trains",
			"icon": "tracker.ico"
		}
		self.generator(module, self.cbStartMenu.IsChecked())
		
	def OnBGenConfig(self, _):
		module = {
			"name": "PSRY Suite Configuration",
			"dir":  "config",
			"main": "main.py",
			"desc": "Configuration Tool",
			"icon": "config.ico"
		}
		self.generator(module, self.cbStartMenu.IsChecked())
		
	def OnBGenSaveLogs(self, _):
		module = {
			"name": "PSRY Suite - save logs",
			"dir":  "savelogs",
			"main": "main.py",
			"desc": "Save Logs and output for debugging",
			"icon": "savelogs.ico",
		}
		self.generator(module, self.cbStartMenu.IsChecked())
			
	def OnBClean(self, _):
		desktop = winshell.desktop()
		pathname = os.path.join(desktop, "PSRY*.lnk")
		scList = [os.path.splitext(os.path.basename(x))[0] for x in glob.glob(pathname)]
		if len(scList) == 0:
			dlg = wx.MessageDialog(self, "No shortcut files found",
					'No Shortcuts', wx.OK | wx.ICON_INFORMATION)
			dlg.ShowModal()
			dlg.Destroy()
			return 
		
		dlg = CleanDlg(self, scList, "shortcuts")
		rc = dlg.ShowModal()
		rv = []
		if rc == wx.ID_OK:
			rv = dlg.GetResults()

		dlg.Destroy()			
		if rc != wx.ID_OK:
			return 
		
		for p in rv:
			path = os.path.join(desktop, p+".lnk")
			os.unlink(path)
			
	def OnBCleanMenu(self, _):
		pathname = os.path.join(winshell.start_menu(), "Programs", "PSRY", "PSRY*.lnk")
		scList = [os.path.splitext(os.path.basename(x))[0] for x in glob.glob(pathname)]
		if len(scList) == 0:
			dlg = wx.MessageDialog(self, "No start menu items found",
					'No Menu Items', wx.OK | wx.ICON_INFORMATION)
			dlg.ShowModal()
			dlg.Destroy()
			return 
		
		dlg = CleanDlg(self, scList, "start menu")
		rc = dlg.ShowModal()
		rv = []
		if rc == wx.ID_OK:
			rv = dlg.GetResults()

		dlg.Destroy()			
		if rc != wx.ID_OK:
			return 
		
		for p in rv:
			path = os.path.join(winshell.start_menu(), "Programs", "PSRY", p+".lnk")
			os.unlink(path)
		
	def OnClose(self, _):
		self.doExit()
		
	def doExit(self):
		self.Destroy()
