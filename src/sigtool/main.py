import wx
import os, sys

cmdFolder = os.getcwd()
if cmdFolder not in sys.path:
	sys.path.insert(0, cmdFolder)

from sigtool.mainframe import MainFrame
from dispatcher.settings import Settings

ofp = open(os.path.join(os.getcwd(), "output", "sigtester.out"), "w")
efp = open(os.path.join(os.getcwd(), "output", "sigtester.err"), "w")
sys.stdout = ofp
sys.stderr = efp

settings = Settings()


class App(wx.App):
	def OnInit(self):
		frame = MainFrame(settings)
		frame.Show()
		return True


app = App(False)
rc = app.MainLoop()
