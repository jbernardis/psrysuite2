import wx
import os, sys
import traceback
cmdFolder = os.getcwd()
if cmdFolder not in sys.path:
	sys.path.insert(0, cmdFolder)

from dispatcher.settings import Settings
from dispatcher.psryframe import PSRYFrame
from dispatcher.constants import logLevels

settings = Settings()

if settings.dispatcher.dispatch:
	fn = "dispatch"
elif settings.dispatcher.satellite:
	fn = "satellite"
else:
	fn = "display"

ofp = open(os.path.join(os.getcwd(), "output", "%s.out" % fn), "w")
efp = open(os.path.join(os.getcwd(), "output", "%s.err" % fn), "w")

sys.stdout = ofp
sys.stderr = efp


def global_exception_handler(exctype, value, tb):
	"""
	Catches any unhandled exception globally and prints the full stack trace.
	"""
	print("--- GLOBAL EXCEPTION CAUGHT ---", file=sys.stderr)

	# Print the entire stack trace exactly like Python normally does
	traceback.print_exception(exctype, value, tb, file=sys.stderr)
	sys.stderr.flush()


# Register the global exception handler
sys.excepthook = global_exception_handler

import logging

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
		self.frame = PSRYFrame(settings)
		self.frame.Show()
		return True


app = App(False)
app.MainLoop()