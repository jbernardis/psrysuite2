import wx

import os, sys
cmdFolder = os.getcwd()
if cmdFolder not in sys.path:
	sys.path.insert(0, cmdFolder)

# ofp = open(os.path.join(os.getcwd(), "output", "trafficgen.out"), "w")
# efp = open(os.path.join(os.getcwd(), "output", "trafficgen.err"), "w")
#
# sys.stdout = ofp
# sys.stderr = efp

import logging
logging.basicConfig(filename=os.path.join(os.getcwd(), "logs", "trafficgen.log"), filemode='w', format='%(asctime)s %(message)s', level=logging.DEBUG)

from trafficgen.mainframe import MainFrame


class App(wx.App):
	def OnInit(self):
		self.frame = MainFrame(cmdFolder)
		self.frame.Show()
		return True


app = App(False)
app.MainLoop()