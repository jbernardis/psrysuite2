import os
import sys
import logging

cmdFolder = os.getcwd()
if cmdFolder not in sys.path:
	sys.path.insert(0, cmdFolder)

from utilities import HTML



class TurnoutControl:
	def __init__(self, parent, rrserver):
		self.parent = parent
		self.rrserver = rrserver
		self.turnouts = Turnouts(self.rrserver)
		self.toNames = self.turnouts.TurnoutNames()


	def ProcessURL(self, urlinfo):
		path, query, params = urlinfo

		logging.debug("Process URL: path = %s, query = %s, params = %s" % (path, str(query), str(params)))

		if path in ["menuchoice", "turnoutchoice"]:
			try:
				turnoutName = query['turnoutlist'][0]
			except (KeyError, IndexError):
				turnoutName = None
				logging.info("Unable to determine turnout name from query: %s" % str(query))
			sent = None

		elif path == "sendnormal":
			turnoutName = list(query.keys())[0]
			sent = "Normal"

		elif path == "sendreverse":
			turnoutName = list(query.keys())[0]
			sent = "Reverse"

		elif path == "turnoutrefresh":
			turnoutName = list(query.keys())[0]
			sent = None

		else:
			return 400, "Invalid tc path: %s" % path

		return self.HTMLTurnoutControl(turnout=turnoutName, sent=sent)


	def HTMLTurnoutControl(self, turnout=None, sent=None):
		css = self.StyleSheet()

		html = HTML.starthtml()
		html += HTML.head(HTML.style({'type': "text/css"}, css))

		html += HTML.startbody()
		html += HTML.h1({}, "Turnout Control")

		html += HTML.startdiv({"class": "selectturnout"})
		html += HTML.label({"for": "turnoutlist"}, "Choose a Turnout: ")

		choices = []
		if turnout is None:
			self.selectedTurnout = self.toNames[0]

		else:
			self.selectedTurnout = turnout

		for tn in self.toNames:
			opts = {"value": tn}
			if tn == self.selectedTurnout:
				opts["selected"] = None
			choices.append(HTML.option(opts, tn))
		selectHtml = HTML.select({"name": "turnoutlist", "id": "turnoutlist", "onchange": "this.form.submit()"}, " ".join(choices))
		turnoutchoice = HTML.form({"name": "turnoutchoice", "action": "/turnoutchoice", "method": "GET"}, selectHtml)

		html += turnoutchoice

		pinfo = self.turnouts.GetNode(self.selectedTurnout, "position")
		if pinfo is not None:
			bits, addr = pinfo
			if addr is not None:
				r = self.rrserver.Get("getbits", {"address": "0x%x" % addr})
				for bv, position in [[bits[0], "N"], [bits[1], "R"]]:
					bbyte, bbit = bv
					inbits = r["in"][bbyte]
					bitvals = []
					for b in range(8):
						bitvals.append(inbits % 2)
						inbits = int(inbits/2)
					bitvals = [v for v in bitvals[::-1]]

					html += HTML.p({}, "Position for %s: %s" % ("Normal" if position == "N" else "Reverse", "True" if bitvals[bbit] != 0 else "False"))
		else:
			html += HTML.p({}, "Position information not available")

		if sent is not None:
			bits, addr = self.turnouts.GetNode(self.selectedTurnout, "control")
			if sent == "Normal":
				msg = {"setoutbit": {"address": "0x%x" % addr, "byte": bits[0][0], "bit": bits[0][1], "value": 1, "pulse": True}}
			elif sent == "Reverse":
				msg = {"setoutbit": {"address": "0x%x" % addr, "byte": bits[1][0], "bit": bits[1][1], "value": 1, "pulse": True}}
			else:
				msg = None

			if msg is None:
				logging.debug("Unable to determine bits to use")
			else:
				logging.info("sending to rr server: (%s)" % str(msg))
				r = self.rrserver.Request(msg)
				if not r:
					html += HTML.p({}, "Unable to send request.  Is RRServer running?")
				else:
					html += HTML.p({}, "Request successfully sent")

		html += HTML.startdiv({"class": "position"})
		btn = HTML.button({"type": "submit", "name": self.selectedTurnout}, "Normal")
		f1 = HTML.form({"name": "normal", "action": "/sendnormal", "method": "GET"}, btn)

		btn = HTML.button({"type": "submit", "id": "%s:reverse" % self.selectedTurnout, "name": self.selectedTurnout}, "Reverse")
		f2 = HTML.form({"name": "reverse", "action": "/sendreverse", "method": "GET"}, btn)

		btn = HTML.button({"type": "submit", "id": "%s:refresh" % self.selectedTurnout, "name": self.selectedTurnout}, "Refresh")
		f3 = HTML.form({"name": "refersh", "action": "/turnoutrefresh", "method": "GET"}, btn)

		html += f1 + f2 + f3

		html += HTML.enddiv()

		html += HTML.startdiv({"class": "backbutton"})

		btn = HTML.button({"type": "submit", "id": "back", "name": "back"}, "Back")
		menu = HTML.form({"name": "turnoutcontrol", "action": "/index", "method": "GET"}, btn)
		html += menu

		html += HTML.enddiv()

		html += HTML.endbody()
		html += HTML.endhtml()
		return 200, html

	def StyleSheet(self):
		css = self.parent.StyleSheet()
		css.addElement("div.selectturnout", {"padding-left": "35px"})
		css.addElement("div.position", {"padding-left": "35px"})
		return css


class Turnouts:
	def __init__(self, rrserver):
		self.iodata = rrserver.Get("getiobits", {})
		if self.iodata is None:
			print("Unable to retrieve iobits from server")
			self.turnouts = {}
		else:
			try:
				self.turnouts = {tname: self.iodata["turnouts"][tname] for tname in self.iodata["turnouts"] if len(self.iodata["turnouts"][tname]["control"][0]) > 0}
			except KeyError:
				print("no turnouts in iodata")
				self.turnouts = {}

		logging.debug("Turnout list")
		for tname, tdata in self.turnouts.items():
			logging.debug("   %s: %s" % (tname, str(tdata)))

	def TurnoutNames(self):
		return list(sorted(self.turnouts.keys()))

	def GetNode(self, tnm, function):
		tinfo = self.turnouts.get(tnm, None)
		if tinfo is None:
			return None

		logging.debug("Turnout info: %s" % str(tinfo))

		finfo = tinfo.get(function, None)
		if finfo is None:
			return None

		logging.debug("Function %s info = %s" % (function, str(finfo)))

		return finfo
