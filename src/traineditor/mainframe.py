import os
import wx
from dispatcher.settings import Settings 
from traineditor.rrserver import RRServer
from traineditor.trainsequences.trainblocksequencedlg import TrainBlockSequencesDlg
from traineditor.trntracker.traintrackerdlg import TrainTrackerDlg
from traineditor.locomotives.managelocos import ManageLocosDlg
from traineditor.engineers.manageengineers import ManageEngineersDlg
from traineditor.preloaded.managepreloaded import ManagePreloadedDlg
from utilities.backup import saveData, restoreData


class MainFrame(wx.Frame):
	def __init__(self):
		wx.Frame.__init__(self, None, style=wx.DEFAULT_FRAME_STYLE)
		self.SetTitle("PSRY Train/Locomotive/Engineer Editor")
		self.Bind(wx.EVT_CLOSE, self.OnClose)
		
		icon = wx.Icon()
		icon.CopyFromBitmap(wx.Bitmap(os.path.join(os.getcwd(), "icons", "editor.ico"), wx.BITMAP_TYPE_ANY))
		self.SetIcon(icon)

		self.settings = Settings()
		self.RRServer = RRServer()
		self.RRServer.SetServerAddress(self.settings.ipaddr, self.settings.serverport)

		self.bTrainSeq = wx.Button(self, wx.ID_ANY, "Edit Train Block Sequences", size=(200, 50))
		self.Bind(wx.EVT_BUTTON, self.OnBTrainBlockSequences, self.bTrainSeq)
				
		self.bTrainTracker = wx.Button(self, wx.ID_ANY, "Edit Train Tracker Data", size=(200, 50))
		self.Bind(wx.EVT_BUTTON, self.OnBTrainTrackerData, self.bTrainTracker)

		self.bPreloaded = wx.Button(self, wx.ID_ANY, "Edit Preloaded Trains", size=(200, 50))
		self.Bind(wx.EVT_BUTTON, self.OnBPreLoaded, self.bPreloaded)

		self.bLocos = wx.Button(self, wx.ID_ANY, "Edit Locomotive Data", size=(200, 50))
		self.Bind(wx.EVT_BUTTON, self.OnBLocos, self.bLocos)

		self.bEngineers = wx.Button(self, wx.ID_ANY, "Edit Engineers List", size=(200, 50))
		self.Bind(wx.EVT_BUTTON, self.OnBEngineers, self.bEngineers)
				
		self.bBackup = wx.Button(self, wx.ID_ANY, "Backup\nData Files", size=(100, 50))
		self.Bind(wx.EVT_BUTTON, self.OnBBackup, self.bBackup)
				
		self.bRestore = wx.Button(self, wx.ID_ANY, "Restore\nData Files", size=(100, 50))
		self.Bind(wx.EVT_BUTTON, self.OnBRestore, self.bRestore)
				
		self.bExit = wx.Button(self, wx.ID_ANY, "Exit", size=(80, 50))
		self.Bind(wx.EVT_BUTTON, self.OnBExit, self.bExit)

		vsz = wx.BoxSizer(wx.VERTICAL)
		vsz.AddSpacer(20)
		
		vsz.Add(self.bTrainSeq, 0, wx.ALIGN_CENTER_HORIZONTAL)
		vsz.AddSpacer(20)
		vsz.Add(self.bTrainTracker, 0, wx.ALIGN_CENTER_HORIZONTAL)
		vsz.AddSpacer(20)
		vsz.Add(self.bPreloaded, 0, wx.ALIGN_CENTER_HORIZONTAL)
		vsz.AddSpacer(20)
		vsz.Add(self.bLocos, 0, wx.ALIGN_CENTER_HORIZONTAL)
		vsz.AddSpacer(20)
		vsz.Add(self.bEngineers, 0, wx.ALIGN_CENTER_HORIZONTAL)
		
		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.Add(self.bBackup)
		hsz.AddSpacer(30)
		hsz.Add(self.bRestore)
		vsz.AddSpacer(30)
		vsz.Add(hsz, 0, wx.ALIGN_CENTER_HORIZONTAL)
		
		vsz.AddSpacer(30)
		
		vsz.Add(self.bExit, 0, wx.ALIGN_CENTER_HORIZONTAL)
		vsz.AddSpacer(20)
		
		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.AddSpacer(90)
		hsz.Add(vsz)
		hsz.AddSpacer(90)

		self.SetSizer(hsz)
		self.Fit()
		self.Layout()
		
	def OnBTrainBlockSequences(self, _):
		dlg = TrainBlockSequencesDlg(self, self.RRServer)
		dlg.ShowModal()
		dlg.Destroy()
		
	def OnBTrainTrackerData(self, _):
		dlg = TrainTrackerDlg(self, self.RRServer, self.settings.browser)
		dlg.ShowModal()
		dlg.Destroy()

	def OnBPreLoaded(self, _):
		dlg = ManagePreloadedDlg(self, self.RRServer)
		dlg.ShowModal()
		dlg.Destroy()
		
	def OnBLocos(self, _):
		dlg = ManageLocosDlg(self, self.RRServer, self.settings.browser)
		dlg.ShowModal()
		dlg.Destroy()
		
	def OnBEngineers(self, _):
		dlg = ManageEngineersDlg(self, self.RRServer)
		dlg.ShowModal()
		dlg.Destroy()

	def OnBBackup(self, _):
		saveData(self, self.settings)
				
	def OnBRestore(self, _):
		restoreData(self, self.settings)
				
	def OnBExit(self, _):
		self.doExit()
		
	def OnClose(self, _):
		self.doExit()
		
	def doExit(self):
		self.Destroy()
		
