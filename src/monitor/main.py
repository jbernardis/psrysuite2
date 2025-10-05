import wx
import os, sys
cmdFolder = os.getcwd()
if cmdFolder not in sys.path:
	sys.path.insert(0, cmdFolder)

fn = "monitor"

ofp = open(os.path.join(os.getcwd(), "output", "%s.out" % fn), "w")
efp = open(os.path.join(os.getcwd(), "output", "%s.err" % fn), "w")

sys.stdout = ofp
sys.stderr = efp

from monitor.mainframe import MainFrame


class App(wx.App):
	def OnInit(self):
		self.frame = MainFrame()
		self.frame.Show()
		return True


app = App(False)
app.MainLoop()