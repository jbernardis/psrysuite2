import wx
import os
import sys
cmdFolder = os.getcwd()
if cmdFolder not in sys.path:
	sys.path.insert(0, cmdFolder)

from dispatcher.settings import Settings
from cliffdisplay.cliffframe import CliffFrame

settings = Settings()
fn = "cliffdisplay"

ofp = open(os.path.join(os.getcwd(), "output", "%s.out" % fn), "w")
efp = open(os.path.join(os.getcwd(), "output", "%s.err" % fn), "w")
sys.stdout = ofp
sys.stderr = efp

import logging

logLevels = {
	"DEBUG":	logging.DEBUG,
	"INFO":		logging.INFO,
	"WARNING":	logging.WARNING,
	"ERROR":	logging.ERROR,
	"CRITICAL":	logging.CRITICAL,
}

l = settings.debug.loglevel
if l not in logLevels:
	print("unknown logging level: %s.  Defaulting to DEBUG" % l, file=sys.stderr)
	l = "DEBUG"
	
loglevel = logLevels[l]

logging.basicConfig(filename=os.path.join(os.getcwd(), "logs", "%s.log" % fn), filemode='w', format='%(asctime)s %(message)s', level=loglevel)
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)


class App(wx.App):
	def OnInit(self):
		frame = CliffFrame(settings)
		frame.Show()
		return True


app = App(False)
app.MainLoop()
