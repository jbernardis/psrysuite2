import os
import sys
import logging

cmdFolder = os.getcwd()
if cmdFolder not in sys.path:
	sys.path.insert(0, cmdFolder)

from dispatcher.constants import aspectname, aspecttype
from rrserver.constants import nodeNames
from utilities import HTML
from sigtool.signals import Signals

aspectValues = {
	1: [[0], [1]],
	2: [[0, 0], [0, 1], [1, 0], [1, 1]],
	3: [[0, 0, 0], [0, 0, 1], [0, 1, 0], [0, 1, 1], [1, 0, 0], [1, 0, 1], [1, 1, 0], [1, 1, 1]],
}


class SigTester:
	def __init__(self, parent, rrserver):
		self.parent = parent
		self.rrserver = rrserver
		self.signals = Signals(self.rrserver)


	def ProcessURL(self, urlinfo):
		path, query, params = urlinfo

		if path in ["menuchoice", "sigchoice"]:
			try:
				sigName = query['signallist'][0]
			except (KeyError, IndexError):
				sigName = None
				logging.info("Unable to determine signal name from query: %s" % str(query))
			return self.HTMLSignalTester(signal=sigName)

		elif path == "aspectsend":
			try:
				siginfo = query['aspects'][0]
				sigName, sigAspect = siginfo.split(":")
				try:
					sigAspect = int(sigAspect)
				except ValueError:
					sigAspect = None

				if sigAspect is not None and sigName is not None:
					logging.info("Sending aspect %d to signal %s" % (sigAspect, sigName))
					vals = self.signals.GetAspectBits(sigName)
					bits = vals[0]
					nodeAddr = vals[1]

					vbytes = [b[0] for b in bits]
					vbits = [b[1] for b in bits]

					nbits = len(vbytes)
					try:
						vals = aspectValues[nbits][sigAspect]
					except (KeyError, IndexError):
						logging.info("can't decode aspect value: %s %s:%s" % (sigName, nbits, sigAspect))
						vals = None

					if vals is not None:
						msg = {"setoutbit": {"address": "0x%x" % nodeAddr, "byte": vbytes, "bit": vbits, "value": vals}}
						logging.info("sending to rr server: (%s)" % str(msg))
						r = self.rrserver.Request(msg)
						if not r:
							logging.info("Unable to send request.  Is RRServer running?")

				else:
					logging.info("Unable to determine aspect value from %s" % siginfo)

			except (KeyError, IndexError):
				sigaspect = None
				sigName = None
				sigAspect = None
				logging.info("Unable to determine signal name from query: %s" % str(query))

			return self.HTMLSignalTester(signal=sigName, aspect=sigAspect)

		return 400, "Invalid path: %s" % path

	def HTMLSignalTester(self, signal=None, aspect=None):
		sigNames = self.signals.SigNames()
		css = self.StyleSheet()

		html = HTML.starthtml()
		html += HTML.head(HTML.style({'type': "text/css"}, css))

		html += HTML.startbody()
		html += HTML.h1({}, "Signal Tester")

		html += HTML.startdiv({"class": "selectsignal"})
		html += HTML.label({"for": "signallist"}, "Choose a Signal to test: ")

		choices = []
		if signal is None:
			self.selectedSignal = sigNames[0]

		else:
			self.selectedSignal = signal

		for sn in sigNames:
			opts = {"value": sn}
			if sn == self.selectedSignal:
				opts["selected"] = None
			choices.append(HTML.option(opts, sn))
		selectHtml = HTML.select({"name": "signallist", "id": "signallist", "onchange": "this.form.submit()"}, " ".join(choices))
		signalchoice = HTML.form({"name": "signalchoice", "action": "/sigchoice", "method": "GET"}, selectHtml)

		html += signalchoice

		html += HTML.enddiv()

		html += HTML.startdiv({"class": "sigattributes"})

		aspectType = self.signals.GetAspectType(self.selectedSignal)
		sigAttr = HTML.strong({}, "Aspect Type: ") + ("%s<br>" % aspecttype(aspectType))

		vals = self.signals.GetAspectBits(self.selectedSignal)
		bits = vals[0]
		nodeAddr = vals[1]
		bstr = ["(%d, %d)" % (b[0], b[1]) for b in bits]
		sigAttr += HTML.strong({}, "Bits: ") + ("%s<br>" % ", ".join(bstr))
		sigAttr += HTML.strong({}, "Node: ") + ("%s (0x%x)<br>" % (nodeNames[nodeAddr], nodeAddr))

		html += HTML.p(sigAttr)

		html += HTML.enddiv()

		html += HTML.startdiv({"class": "aspectlist"})

		naspects = 2**len(bits)
		rbs = []
		if aspect is None:
			aspect = 0
		for ax in range(naspects):
			id = "%s:%d" % (self.selectedSignal, ax)
			parms = {"type": "radio", "id": id, "name": "aspects", "value": id}
			if ax == aspect:
				parms["checked"] = None

			rbs.append("<br>" + HTML.input(parms) + HTML.label({"for": id}, self.AspectValueString(ax, aspectType, len(bits))))
		btn = HTML.button({"type": "submit", "id": "send", "name": "send"}, "Send")
		aspects = HTML.form({"name": "signalaspect", "action": "/aspectsend", "method": "GET"}, " ".join(rbs) + "<br><br>" + btn)
		html += aspects

		html += HTML.enddiv()

		html += HTML.startdiv({"class": "backbutton"})

		btn = HTML.button({"type": "submit", "id": "back", "name": "back"}, "Back")
		menu = HTML.form({"name": "signaltester", "action": "/index", "method": "GET"}, btn)
		html += menu

		html += HTML.enddiv()

		html += HTML.endbody()
		html += HTML.endhtml()
		return 200, html

	def StyleSheet(self):
		css = self.parent.StyleSheet()
		css.addElement("div.selectsignal", {"padding-left": "35px"})
		css.addElement("div.aspectlist", {"padding-left": "35px"})
		css.addElement("div.sigattributes", {"padding-left": "55px"})
		return css


	def AspectValueString(self, aspect, aspectType, nbits):
		print("aspect value string for aspect %s type %s nbits %d" % (aspect, aspectType, nbits))
		an = aspectname(aspect, aspectType)
		print("result = %s" % an)

		try:
			av = aspectValues[nbits][aspect]
		except (KeyError, IndexError):
			logging.error("Index/Key error trying to retrieve aspect value for %s %s" % (nbits, aspect))
			return an

		pfx = "".join(["%d" % b for b in av])
		return pfx + " " + an
