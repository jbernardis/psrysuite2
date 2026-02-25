import wx
import os

from loganalyzer.rrserverlog import RRServerLog
from loganalyzer.blocktraversaldlg import BlockTraversalDlg
from loganalyzer.stoppingblocksdlg import StoppingBlocksDlg
from loganalyzer.breakersdlg import BreakersDlg

BTNDIM = (100, 40)


class MainFrame(wx.Frame):
	def __init__(self, settings):
		wx.Frame.__init__(self, None, style=wx.CAPTION | wx.RESIZE_BORDER | wx.CLOSE_BOX)
		self.SetTitle("PSRY Log File Analyzer")
		self.Bind(wx.EVT_CLOSE, self.OnClose)
		self.settings = settings

		self.logDir = os.path.join(os.getcwd(), "logs")
		self.fileName = os.path.join(self.logDir, "rrserver.log")

		self.RRServerLog = RRServerLog()
		self.RRServerLog.ProcessLogFile(self.fileName)

		vsz = wx.BoxSizer(wx.VERTICAL)
		vsz.AddSpacer(20)

		self.teFileName = wx.TextCtrl(self, wx.ID_ANY, self.fileName, size=(450, -1), style=wx.TE_READONLY)
		self.bFileName = wx.Button(self, wx.ID_ANY, "...", size=(40, -1))
		self.Bind(wx.EVT_BUTTON, self.OnBFileName, self.bFileName)

		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.AddSpacer(20)
		hsz.Add(self.teFileName)
		hsz.AddSpacer(10)
		hsz.Add(self.bFileName)
		hsz.AddSpacer(20)

		vsz.Add(hsz)

		vsz.AddSpacer(20)

		self.bBlockTraversal = wx.Button(self, wx.ID_ANY, "Block Traversal\nTimes", size=BTNDIM)
		self.Bind(wx.EVT_BUTTON, self.OnBBlockTraversal, self.bBlockTraversal)

		self.bStoppingSection = wx.Button(self, wx.ID_ANY, "Stopping Section\nTimes", size=BTNDIM)
		self.Bind(wx.EVT_BUTTON, self.OnBStoppingSection, self.bStoppingSection)

		self.bBreakers = wx.Button(self, wx.ID_ANY, "Breakers", size=BTNDIM)
		self.Bind(wx.EVT_BUTTON, self.OnBBreakers, self.bBreakers)

		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.AddSpacer(20)
		hsz.Add(self.bBlockTraversal)

		hsz.AddSpacer(20)

		hsz.Add(self.bStoppingSection)

		hsz.AddSpacer(20)

		hsz.Add(self.bBreakers)
		hsz.AddSpacer(20)

		vsz.Add(hsz, 0, wx.ALIGN_CENTER_HORIZONTAL)

		vsz.AddSpacer(20)

		self.SetSizer(vsz)
		self.Fit()
		self.Layout()

	def OnBFileName(self, _):
		wildcard = "Log files (*.log)|*.log|All files (*.*)|*.*"
		dlg = wx.FileDialog(
			self, message="Choose log file",
			defaultDir=self.logDir,
			defaultFile=self.fileName,
			wildcard=wildcard,
			style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST | wx.FD_PREVIEW)

		rc = dlg.ShowModal()
		if rc != wx.ID_OK:
			dlg.Destroy()
			return

		self.fileName = dlg.GetPath()
		dlg.Destroy()

		self.logDir = os.path.split(self.fileName)[0]
		self.teFileName.SetValue(self.fileName)

		self.RRServerLog.ProcessLogFile(self.fileName)

	def OnBBlockTraversal(self, _):
		rpt = self.RRServerLog.ReportBlockTraversal()
		dlg = BlockTraversalDlg(self, rpt)
		rc = dlg.ShowModal()
		dlg.Destroy()

	def OnBStoppingSection(self, _):
		rpt = self.RRServerLog.ReportStoppageTimes()
		dlg = StoppingBlocksDlg(self, rpt)
		rc = dlg.ShowModal()
		dlg.Destroy()

	def OnBBreakers(self, _):
		rpt = self.RRServerLog.ReportBreakers()
		dlg = BreakersDlg(self, rpt)
		rc = dlg.ShowModal()
		dlg.Destroy()

	def OnClose(self, evt):
		self.Destroy()
