import os
import sys
import logging

cmdFolder = os.getcwd()
if cmdFolder not in sys.path:
	sys.path.insert(0, cmdFolder)

from utilities import HTML
from utils import BitSet


class TurnoutControl:
	def __init__(self, parent, rrserver):
		self.parent = parent
		self.rrserver = rrserver
		self.turnouts = Turnouts(self.rrserver)
		self.nxButtons = NXButtons(self.rrserver)
		self.routesin = RoutesIn(self.rrserver)
		self.toNames = self.turnouts.TurnoutNames()
		self.selectedButton = None
		self.selectedTurnout = None
		self.chosengroup = None
		self.chosenbutton = None

	def ProcessURL(self, urlinfo):
		path, query, params = urlinfo

		logging.debug("Process URL: path = %s, query = %s, params = %s" % (path, str(query), str(params)))

		buttonGroup = None
		turnoutName = None
		sent = None

		if path in ["menuchoice", "turnoutchoice"]:
			try:
				turnoutName = query['turnoutlist'][0]
			except (KeyError, IndexError):
				logging.info("Unable to determine turnout name from query: %s" % str(query))

		elif path == "sendgroup":
			logging.debug("button group, query = %s" % str(query))
			groupName = list(query.keys())[0]
			buttonName = query[groupName][0]
			buttonGroup = "send:%s:%s" % (groupName, buttonName)

		elif path == "refreshgroup":
			logging.debug("button group, query = %s" % str(query))
			groupName = list(query.keys())[0]
			buttonName = query[groupName][0]
			buttonGroup = "refresh:%s:%s" % (groupName, buttonName)
			logging.debug("buttongroup = %s" % buttonGroup)

		elif path == "sendnormal":
			turnoutName = list(query.keys())[0]
			sent = "Normal"

		elif path == "sendreverse":
			turnoutName = list(query.keys())[0]
			sent = "Reverse"

		elif path == "turnoutrefresh":
			turnoutName = list(query.keys())[0]

		else:
			return 400, "Invalid tc path: %s" % path

		return self.HTMLTurnoutControl(turnout=turnoutName, sent=sent, buttongroup=buttonGroup)

	def HTMLTurnoutControl(self, turnout=None, sent=None, buttongroup=None):
		css = self.StyleSheet()

		html = HTML.starthtml()
		html += HTML.head(HTML.style({'type': "text/css"}, css))

		html += HTML.startbody()
		html += HTML.h1({}, "Turnout Control")

		html += HTML.startdiv({"class": "grid-container"})

		html += HTML.startdiv({"class": "column"})

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
					bitset = BitSet(bbyte, bbit, r["in"])

					html += HTML.p({}, "Position for %s: %s" % ("Normal" if position == "N" else "Reverse", str(bitset)))
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

		html += HTML.enddiv()  # selectturnout

		html += HTML.startdiv({"class": "position"})
		btn = HTML.button({"type": "submit", "name": self.selectedTurnout}, "Normal")
		f1 = HTML.form({"name": "normal", "action": "/sendnormal", "method": "GET"}, btn)

		btn = HTML.button({"type": "submit", "id": "%s:reverse" % self.selectedTurnout, "name": self.selectedTurnout}, "Reverse")
		f2 = HTML.form({"name": "reverse", "action": "/sendreverse", "method": "GET"}, btn)

		btn = HTML.button({"type": "submit", "id": "%s:refresh" % self.selectedTurnout, "name": self.selectedTurnout}, "Refresh")
		f3 = HTML.form({"name": "refresh", "action": "/turnoutrefresh", "method": "GET"}, btn)

		html += f1 + f2 + f3

		html += HTML.enddiv()  # position

		html += HTML.enddiv()  # column
		html += HTML.startdiv({"class": "column"})

		if buttongroup is None:
			self.chosengroup = None
			self.chosenbutton = None
			action = None
		else:
			action, self.chosengroup, self.chosenbutton = buttongroup.split(":")

		html += self.ButtonGroup("Waterman West", [["YWEB1", "Y81 West", "Y81E"], ["YWEB2", "Y82 West", "Y82E"], ["YWEB3", "Y83 West", "Y83E"], ["YWEB4", "Y84 West", "Y84E"]], "WYW", action)
		html += self.ButtonGroup("Waterman East", [["YWWB1", "Y81 East", "Y81W"], ["YWWB2", "Y82 East", "Y82W"], ["YWWB3", "Y83 East", "Y83W"], ["YWWB4", "Y84 East", "Y84W"]], "WYE", action)

		html += HTML.p({}, "Sheffield East")
		html += HTML.p({}, "Sheffield West")
		html += HTML.p({}, "Green Mountain East")
		html += HTML.p({}, "Green Mountain West")
		#  nassau - 2 button variant

		html += HTML.enddiv()  # column
		html += HTML.enddiv()  # grid containder

		html += HTML.startdiv({"class": "backbutton"})

		html += "<br><br>"

		btn = HTML.button({"type": "submit", "id": "back", "name": "back"}, "Back")
		menu = HTML.form({"name": "turnoutcontrol", "action": "/index", "method": "GET"}, btn)
		html += menu

		html += HTML.enddiv()  # backbutton

		html += HTML.endbody()
		html += HTML.endhtml()
		return 200, html

	def ButtonGroup(self, heading, rbinfo, rgroup, action):
		html = HTML.startdiv({"class": "buttongroup"})
		html += HTML.p({}, heading)
		logging.info("===================================================================")
		logging.info("button group: %s %s %s %s" % (heading, str(rbinfo), rgroup, action))

		lastAddr = None
		rtStatus = {}
		if self.chosengroup is None or self.chosenbutton is None:
			self.selectedButton = rbinfo[0][0]
		elif rgroup == self.chosengroup:
			self.selectedButton = self.chosenbutton
			if action == 'send':
				bInfo = self.nxButtons.ButtonInfo(self.chosenbutton)
				bits = bInfo["position"][0][0]
				addr = bInfo["position"][1]
				msg = {"setoutbit": {"address": "0x%x" % addr, "byte": bits[0], "bit": bits[1], "value": 1, "pulse": True}}
				logging.info("sending to rr server: (%s)" % str(msg))
				r = self.rrserver.Request(msg)
				if not r:
					html += HTML.p({}, "Unable to send request.  Is RRServer running?")
				else:
					html += HTML.p({}, "Request successfully sent")

			for bname, _, route in rbinfo:
				logging.error("getting route infor for %s" % rgroup)
				rtInfo = self.routesin.RouteInfo(route)
				logging.error("info = (%s)" % str(rtInfo))
				rtStatus[route] = False
				stat = rtInfo["status"]
				try:
					bits = rtInfo["status"][0][0]
					addr = rtInfo["status"][1]
					logging.error("bits = %s, addr = %s" % (str(bits), str(addr)))
				except (KeyError, IndexError):
					logging.info("error 1")
					pass
				else:
					if addr != lastAddr:
						r = self.rrserver.Get("getbits", {"address": "0x%x" % addr})
						lastAddr = addr
					try:
						rtStatus[route] = BitSet(bits[0], bits[1], r["in"])
						logging.info("checking bit %d:%d inside %s = %s" % (bits[0], bits[1], r["in"], rtStatus[route]))
					except (KeyError, IndexError):
						logging.info("error 2")
						pass
		else:
			self.selectedButton = rbinfo[0][0]

		logging.info("========================================================")

		prefix = ""
		rbs = []
		st = ["%s: %s" % (r, s) for r, s in rtStatus.items()]
		html += "<br>%s" % ", ".join(st)
		for bname, text, route in rbinfo:
			parms = {"type": "radio", "id": bname, "name": rgroup, "value": bname}
			if bname == self.selectedButton:
				parms["checked"] = None

			rbs.append(prefix + HTML.input(parms) + HTML.label({"for": id}, text))
			prefix = "<br>"

		btnS = HTML.button({"type": "submit", "id": rgroup, "name": rgroup}, "Send")
		formS = HTML.form({"name": rgroup, "action": "/sendgroup", "method": "GET"}, " ".join(rbs) + "<br><br>" + btnS)
		html += formS
		if self.selectedButton is not None:
			btnR = HTML.button({"type": "submit", "id": rgroup, "name": rgroup, "value": self.selectedButton}, "Refresh")
			formR = HTML.form({"name": rgroup, "action": "/refreshgroup", "method": "GET"}, " " + btnR)
			html += formR

		html += HTML.enddiv()  # buttongroup
		return html

	def StyleSheet(self):
		css = self.parent.StyleSheet()
		css.addElement(".grid-container", {"display": "grid", "grid-template-columns": "1fr 1fr", "gap": "20px", "padding": "20x"})
		css.addElement(".column", {"background-color": "#f4f4f4", "padding": "20px", "border": "1px solid #ddd"})
		css.addElement(".buttongroup", {"background-color": "#f8f8f8", "padding": "20px", "border": "2px solid #ddd"})
		css.addElement("div.selectturnout", {"padding-left": "35px"})
		css.addElement("div.position", {"padding-left": "35px"})
		return css


class Turnouts:
	def __init__(self, rrserver):
		self.iodata = rrserver.Get("getiobits", {})
		if self.iodata is None:
			logging.error("Unable to retrieve iobits from server")
			self.turnouts = {}
		else:
			try:
				self.turnouts = {tname: self.iodata["turnouts"][tname] for tname in self.iodata["turnouts"] if len(self.iodata["turnouts"][tname]["control"][0]) > 0}
			except KeyError:
				logging.error("no turnouts in iodata")
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


class NXButtons:
	def __init__(self, rrserver):
		self.iodata = rrserver.Get("getiobits", {})
		if self.iodata is None:
			logging.error("Unable to retrieve iobits from server")
			self.nxbuttons = {}
		else:
			try:
				self.nxbuttons = {bname: self.iodata["nxbuttons"][bname] for bname in self.iodata["nxbuttons"]}
			except KeyError:
				logging.error("no nxbuttons in iodata")
				self.nxbuttons = {}

		logging.debug("NX Button List")
		for bname, bdata in self.nxbuttons.items():
			logging.debug("   %s: %s" % (bname, str(bdata)))

	def ButtonInfo(self, bn):
		if bn not in self.nxbuttons:
			return None
		else:
			return self.nxbuttons[bn]


class RoutesIn:
	def __init__(self, rrserver):
		self.iodata = rrserver.Get("getiobits", {})
		if self.iodata is None:
			logging.error("Unable to retrieve iobits from server")
			self.routesin = {}
		else:
			try:
				self.routesin = {rname: self.iodata["routesin"][rname] for rname in self.iodata["routesin"]}
			except KeyError:
				logging.error("no routes in in iodata")
				self.routesin = {}

		logging.debug("Routes In List")
		for rname, rdata in self.routesin.items():
			logging.debug("   %s: %s" % (rname, str(rdata)))

	def RouteInfo(self, rn):
		if rn not in self.routesin:
			return None
		else:
			return self.routesin[rn]
