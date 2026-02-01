import wx
import os, sys
import logging

cmdFolder = os.getcwd()
if cmdFolder not in sys.path:
	sys.path.insert(0, cmdFolder)

from dispatcher.settings import Settings

from c13auto.c13automain import MainFrame

ofp = open(os.path.join(os.getcwd(), "output", "c13auto.out"), "w")
efp = open(os.path.join(os.getcwd(), "output", "c13auto.err"), "w")
lfn = os.path.join(os.getcwd(), "logs", "c13auto.log")

sys.stdout = ofp
sys.stderr = efp

settings = Settings()

logLevels = {
	"DEBUG": logging.DEBUG,
	"INFO": logging.INFO,
	"WARNING": logging.WARNING,
	"ERROR": logging.ERROR,
	"CRITICAL": logging.CRITICAL,
}

l = settings.debug.loglevel
if l not in logLevels:
	print("unknown logging level: %s.  Defaulting to DEBUG" % l, file=sys.stderr)
	l = "DEBUG"

loglevel = logLevels[l]
logging.basicConfig(filename=lfn, filemode='w', format='%(asctime)s %(message)s', level=loglevel)


class App(wx.App):
	def OnInit(self):
		self.frame = MainFrame(settings)
		self.frame.Show()
		return True


app = App(False)
app.MainLoop()