import wx
import os
import sys

cmdFolder = os.getcwd()
if cmdFolder not in sys.path:
	sys.path.insert(0, cmdFolder)

from config.mainframe import MainFrame

try:
	os.mkdir(os.path.join(os.getcwd(), "logs"))
except FileExistsError:
	pass

try:
	os.mkdir(os.path.join(os.getcwd(), "output"))
except FileExistsError:
	pass


ofp = open(os.path.join(os.getcwd(), "output", "config.out"), "w")
efp = open(os.path.join(os.getcwd(), "output", "config.err"), "w")

sys.stdout = ofp
sys.stderr = efp


class App(wx.App):
	def OnInit(self):
		frame = MainFrame()
		frame.Show()
		return True


app = App(False)
app.MainLoop()
