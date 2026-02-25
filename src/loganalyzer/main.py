import wx
import os, sys

cmdFolder = os.getcwd()
if cmdFolder not in sys.path:
	sys.path.insert(0, cmdFolder)

from dispatcher.settings import Settings

from loganalyzer.mainframe import MainFrame

ofp = open(os.path.join(os.getcwd(), "output", "loganalyzer.out"), "w")
efp = open(os.path.join(os.getcwd(), "output", "loganalyzer.err"), "w")

sys.stdout = ofp
sys.stderr = efp

settings = Settings()


class App(wx.App):
	def OnInit(self):
		frame = MainFrame(settings)
		frame.Show()
		return True


app = App(False)
app.MainLoop()