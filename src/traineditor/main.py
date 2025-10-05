import wx
import os, sys
cmdFolder = os.getcwd()
if cmdFolder not in sys.path:
	sys.path.insert(0, cmdFolder)

ofp = open(os.path.join(os.getcwd(), "output", "trainedit.out"), "w")
efp = open(os.path.join(os.getcwd(), "output", "trainedit.err"), "w")

sys.stdout = ofp
sys.stderr = efp

lockFile = os.path.join(os.getcwd(), "data", "trainedit.lock")

from traineditor.mainframe import MainFrame 

class App(wx.App):
	def OnInit(self):
		if os.path.isfile(lockFile):
			dlg = wx.MessageDialog(None, "There is possibly another copy of train editor running.\n\n\"Yes\" to ignore, or\n\"No\" to exit",
					"Duplicate Process", wx.YES_NO | wx.NO_DEFAULT | wx.ICON_WARNING)
			rc = dlg.ShowModal()
			dlg.Destroy()
			if rc == wx.ID_NO:
				return False
			
		lfp = open(lockFile, "w")
		lfp.close()
		
		self.frame = MainFrame()
		self.frame.Show()
		return True

app = App(False)
rc = app.MainLoop()

os.unlink(lockFile)