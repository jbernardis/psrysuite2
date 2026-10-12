import os
import sys
import logging

cmdFolder = os.getcwd()
if cmdFolder not in sys.path:
	sys.path.insert(0, cmdFolder)

from utilities import HTML
from utils import BitSet

REFRESH_DATA_TAG = "#REFDATA#"


class TurnoutControl:
	def __init__(self, parent, rrserver):
		self.parent = parent
		self.rrserver = rrserver
		self.turnouts = Turnouts(self.rrserver)
		self.nxButtons = NXButtons(self.rrserver)
		self.routesin = RoutesIn(self.rrserver)
		self.toNames = self.turnouts.TurnoutNames()
		self.refreshData = {}
		self.buttonGroups = ["WYW", "WYE", "GMW", "GME", "SHW", "SHE", "NWA", "NWB", "NEA", "NEB"]

	def ProcessURL(self, urlinfo):
		path, query, params = urlinfo

		rd = query.get("refdata", None)
		if rd is None:
			self.refreshData = {}
		else:
			self.refreshData = self.decodeRefreshData(rd[0])

		action = None
		buttonGroup = None

		if path in ["menuchoice", "turnoutchoice"]:
			action = "refresh"
			buttonGroup = "single"
			try:
				turnoutName = query['turnoutlist'][0]
				self.refreshData["single"] = turnoutName

			except (KeyError, IndexError):
				pass

		elif path == "sendgroup":
			buttonGroup, button = self.GetGroupAndButtonFromQuery(query)
			if buttonGroup is not None:
				self.refreshData[buttonGroup] = button
				action = "send"

		elif path == "send2group":
			buttonGroup, button = self.GetGroupsAndButtonsFromQuery(query)
			if len(buttonGroup) == 2 and len(button) == 2:
				for grp, btn in zip(buttonGroup, button):
					self.refreshData[grp] = btn
				buttonGroup = buttonGroup[0][0:-1]
				action = "send"

		elif path == "sendnormal":
			action = "Normal"
			buttonGroup = "single"

		elif path == "sendreverse":
			action = "Reverse"
			buttonGroup = "single"

		elif path == "refreshall":
			action = "refresh"

		else:
			return 400, "Invalid tc path: %s" % path

		if action is None:
			return 400, "Invalid request"
		else:
			return self.HTMLTurnoutControl(buttongroup=buttonGroup, action=action)

	def GetTurnoutFromQuery(self, query):
		for k in query.keys():
			if k in self.toNames:
				return k

		return None

	def GetGroupAndButtonFromQuery(self, query):
		for k in query.keys():
			if k in self.buttonGroups:
				try:
					button = query[k][0]
				except IndexError:
					button = None
				return k, button

		return None, None

	def GetGroupsAndButtonsFromQuery(self, query):
		grps = []
		btns = []
		for k in query.keys():
			if k in self.buttonGroups:
				try:
					btns.append(query[k][0])
					grps.append(k)
				except IndexError:
					break

		if len(btns) > 0:
			return grps, btns

		return None, None

	def HTMLTurnoutControl(self, buttongroup=None, action=None):
		html = HTML.h1({}, "Turnout Control")

		html += HTML.startdiv({"class": "grid-container"})

		html += HTML.startdiv({"class": "column"})

		html += self.SingleTurnoutControl(action = action if buttongroup == "single" else "refresh")

		html += self.MatrixStatus("Hyde", {
				"Hyde West 2": ["H30E"],
				"Hyde West West": ["H31W", "H32W", "H33W", "H34W", "H12W"],
				"Hyde East West": ["H31E", "H32E", "H33E", "H34E", "H12E"],
				"Hyde West East": ["H22W", "H43W", "H42W", "H41W"],
				"Hyde East East": ["H22E", "H43E", "H42E", "H41E", "H40E"],
				})

		html += self.TwoButtonGroup("Nassau West",
				["N60", "N11", "N21"],
				["W10", "N32W", "N31W", "N12W", "N22W", "N41W", "N42W", "W20W"],
				["NSw19", "NSw21", "NSw23", "NSw25", "NSw27", "NSw29", "NSw31", "NSw33", "NSw35"],
				"NW", "NNXBtn", action if buttongroup == "NW" else "refresh")

		html += self.TwoButtonGroup("Nassau East",
				["W11", "N32E", "N31E", "N12E", "N22E", "N41E", "N42E", "W20E"],
				["R10", "B10", "B20"],
				["NSw39", "NSw41", "NSw43", "NSw45", "NSw47", "NSw51", "NSw53", "NSw55", "NSw57"],
				"NE", "NNXBtn", action if buttongroup == "NE" else "refresh")

		html += HTML.enddiv()  # column
		html += HTML.startdiv({"class": "column"})

		html += self.ButtonGroup("Waterman West", [["YWWB1", "Y81 West", "Y81W"], ["YWWB2", "Y82 West", "Y82W"], ["YWWB3", "Y83 West", "Y83W"], ["YWWB4", "Y84 West", "Y84W"]], "WYW", action if buttongroup == "WYW" else "refresh")
		html += self.ButtonGroup("Waterman East", [["YWEB1", "Y81 East", "Y81E"], ["YWEB2", "Y82 East", "Y82E"], ["YWEB3", "Y83 East", "Y83E"], ["YWEB4", "Y84 East", "Y84E"]], "WYE", action if buttongroup == "WYE" else "refresh")
		html += self.ButtonGroup("Green Mountain West", [["CC31W", "C31 West", "CC31W"], ["CC30W", "C30 West", "CC30W"], ["CC10W", "C10 West", "CC10W"], ["CG21W", "G21 West", "CG21W"]], "GMW", action if buttongroup == "GMW" else "refresh")
		html += self.ButtonGroup("Green Mountain East", [["CC30E", "C30 East", "CC30E"], ["CC10E", "C10 East", "CC10E"], ["CG10E", "G10 East", "CC10E"], ["CG12E", "G12 East", "CG12E"]], "GME", action if buttongroup == "GME" else "refresh")

		html += HTML.enddiv()  # column
		html += HTML.startdiv({"class": "column"})

		html += self.ButtonGroup("Sheffield West", [
				["CC44W", "C44 West", "CC44W"],
				["CC43W", "C43 West", "CC43W"],
				["CC42W", "C42 West", "CC42W"],
				["CC41W", "C41 West", "CC41W"],
				["CC40W", "C40 West", "CC40W"],
				["CC21W", "C21 West", "CC21W"],
				["CC50W", "C50 West", "CC50W"],
				["CC51W", "C51 West", "CC51W"],
				["CC52W", "C52 West", "CC52W"],
				["CC53W", "C53 West", "CC53W"],
				["CC54W", "C54 West", "CC54W"],
				], "SHW", action if buttongroup == "SHW" else "refresh")

		html += self.ButtonGroup("Sheffield East", [
				["CC44E", "C44 East", "CC44E"],
				["CC43E", "C43 East", "CC43E"],
				["CC42E", "C42 East", "CC42E"],
				["CC41E", "C41 East", "CC41E"],
				["CC40E", "C40 East", "CC40E"],
				["CC21E", "C21 East", "CC21E"],
				["CC50E", "C50 East", "CC50E"],
				["CC51E", "C51 East", "CC51E"],
				["CC52E", "C52 East", "CC52E"],
				["CC53E", "C53 East", "CC53E"],
				["CC54E", "C54 East", "CC54E"],
				], "SHE", action if buttongroup == "SHE" else "refresh")

		html += HTML.enddiv()  # column
		html += HTML.enddiv()  # grid containder

		html += HTML.startdiv({"class": "backbutton"})
		html += "<br>"
		ref = HTML.input({"type": "hidden", "name": "refdata", "value": REFRESH_DATA_TAG})
		rbtn = HTML.button({"type": "submit", "id": "refresh", "name": "refresh"}, "Refresh")
		html += HTML.form({"name": "refresh", "action": "/refreshall", "method": "GET"}, " " + ref + rbtn)

		html += "&nbsp;&nbsp;&nbsp;&nbsp;"

		btn = HTML.button({"type": "submit", "id": "back", "name": "back"}, "Back")
		menu = HTML.form({"name": "turnoutcontrol", "action": "/index", "method": "GET"}, btn)
		html += menu

		html += HTML.enddiv()  # backbutton

		# wrap the HTML into an html body and substitute the refresh data as we do so
		css = self.StyleSheet()

		h = HTML.starthtml()
		h += HTML.head(HTML.style({'type': "text/css"}, css))

		h += HTML.startbody()

		logging.debug("REFRESH DATA: %s" % str(self.refreshData))
		r = self.encodeRefreshData()
		nh = html.replace(REFRESH_DATA_TAG, r)
		h += nh

		h += HTML.endbody()
		h += HTML.endhtml()
		return 200, h

	def encodeRefreshData(self):
		e = ["%s:%s" % (k, v) for k, v in self.refreshData.items()]
		return ",".join(e)

	def decodeRefreshData(self, data):
		if data is None:
			return {}

		rd = {}
		kvlist = data.split(",")
		for kv in kvlist:
			try:
				k, v = kv.split(":")
				rd[k] = v
			except ValueError:
				break

		return rd

	def SingleTurnoutControl(self, action):
		html = HTML.startdiv({"class": "singleturnout"})

		html += HTML.p({}, "Single Turnouts:")

		html += HTML.startdiv({"class": "selectturnout"})
		html += HTML.label({"for": "turnoutlist"}, "Choose a Turnout: ")

		choices = []

		ref = HTML.input({"type": "hidden", "name": "refdata", "value": REFRESH_DATA_TAG})

		turnout = self.refreshData.get("single", self.toNames[0])
		self.refreshData["single"] = turnout

		for tn in self.toNames:
			opts = {"value": tn}
			if tn == turnout:
				opts["selected"] = None
			choices.append(HTML.option(opts, tn))
		selectHtml = HTML.select({"name": "turnoutlist", "id": "turnoutlist", "onchange": "this.form.submit()"}, " ".join(choices))
		turnoutchoice = HTML.form({"name": "turnoutchoice", "action": "/turnoutchoice", "method": "GET"}, ref + selectHtml)

		html += turnoutchoice

		pinfo = self.turnouts.GetNode(turnout, "position")
		if pinfo is not None:
			bits, addr = pinfo
			if addr is not None:
				bitsset = []
				r = self.rrserver.Get("getbits", {"address": "0x%x" % addr})
				for bv in [bits[0], bits[1]]:
					bbyte, bbit = bv
					bitsset.append(BitSet(bbyte, bbit, r["in"]))
				if bitsset[0] == bitsset[1]:
					pos = "Unknown"
				elif bitsset[0]:
					pos = "Normal"
				else:
					pos = "Reverse"

				html += HTML.p({}, "Position for %s: %s" % (turnout, pos))
		else:
			html += HTML.p({}, "Position information not available")

		if action is not None:
			bits, addr = self.turnouts.GetNode(turnout, "control")
			if action == "Normal":
				msg = {"setoutbit": {"address": "0x%x" % addr, "byte": bits[0][0], "bit": bits[0][1], "value": 1, "pulse": True}}
			elif action == "Reverse":
				msg = {"setoutbit": {"address": "0x%x" % addr, "byte": bits[1][0], "bit": bits[1][1], "value": 1, "pulse": True}}
			else:
				msg = None

			if msg is not None:
				r = self.rrserver.Request(msg)
				if not r:
					html += HTML.p({}, "Unable to send request.  Is RRServer running?")
				else:
					html += HTML.p({}, "Request successfully sent")

		html += HTML.enddiv()  # selectturnout

		html += HTML.startdiv({"class": "position"})
		btn = HTML.button({"type": "submit", "name": turnout}, "Normal")
		f1 = HTML.form({"name": "normal", "action": "/sendnormal", "method": "GET"}, ref + btn)

		btn = HTML.button({"type": "submit", "id": "%s:reverse" % turnout, "name": turnout}, "Reverse")
		f2 = HTML.form({"name": "reverse", "action": "/sendreverse", "method": "GET"}, ref + btn)

		html += f1 + "&nbsp;&nbsp;" + f2

		html += HTML.enddiv()  # position

		html += HTML.enddiv()  # single turnout
		return html

	def MatrixStatus(self, heading, matrixinfo):
		html = HTML.startdiv({"class": "matrix"})
		html += HTML.p({}, heading)

		lastAddr = None
		for text, routes in matrixinfo.items():
			rtSet = []
			for rte in routes:
				rinfo = self.routesin.RouteInfo(rte)
				try:
					bits = rinfo["status"][0][0]
					addr = rinfo["status"][1]
				except (KeyError, IndexError):
					pass
				else:
					if addr != lastAddr:
						r = self.rrserver.Get("getbits", {"address": "0x%x" % addr})
						lastAddr = addr
					try:
						rtstat = BitSet(bits[0], bits[1], r["in"])
						if rtstat:
							rtSet.append(rte)
					except (KeyError, IndexError):
						pass
			if len(rtSet) == 0:
				rtString = "Unknown"
			else:
				rtString = ", ".join(rtSet)
			html += HTML.p({"class": "matrixgroup"}, "%s Selected Route: %s" % (text, rtString))

		html += HTML.enddiv()
		return html

	def ButtonGroup(self, heading, rbinfo, rgroup, action):
		html = HTML.startdiv({"class": "buttongroup"})
		html += HTML.p({}, heading)

		lastAddr = None
		rtStatus = {}
		button = self.refreshData.get(rgroup, rbinfo[0][0])
		self.refreshData[rgroup] = button

		if action == 'send' and button is not None:
			bInfo = self.nxButtons.ButtonInfo(button)
			bits = bInfo["position"][0][0]
			addr = bInfo["position"][1]
			msg = {"setoutbit": {"address": "0x%x" % addr, "byte": bits[0], "bit": bits[1], "value": 1, "pulse": True}}
			r = self.rrserver.Request(msg)
			if not r:
				html += HTML.p({}, "Unable to send request.  Is RRServer running?")
			else:
				html += HTML.p({}, "Request successfully sent")

		for bname, _, route in rbinfo:
			rtInfo = self.routesin.RouteInfo(route)
			rtStatus[route] = False
			try:
				bits = rtInfo["status"][0][0]
				addr = rtInfo["status"][1]
			except (KeyError, IndexError):
				pass
			else:
				if addr != lastAddr:
					r = self.rrserver.Get("getbits", {"address": "0x%x" % addr})
					lastAddr = addr
				try:
					rtStatus[route] = BitSet(bits[0], bits[1], r["in"])
				except (KeyError, IndexError):
					pass

		prefix = ""
		rbs = []
		st = [r for r in rtStatus.keys() if rtStatus[r]]
		if len(st) > 0:
			html += HTML.p({}, "Selected Route: %s" % ", ".join(st))
		else:
			html += HTML.p({}, "Selected Route: Unknown")

		for bname, text, route in rbinfo:
			parms = {"type": "radio", "id": bname, "name": rgroup, "value": bname}
			if bname == button:
				parms["checked"] = None

			rbs.append(prefix + HTML.input(parms) + HTML.label({"for": id}, text))
			prefix = "<br>"

		ref = HTML.input({"type": "hidden", "name": "refdata", "value": REFRESH_DATA_TAG})

		btnS = HTML.button({"type": "submit", "id": rgroup, "name": rgroup}, "Send")
		formS = HTML.form({"name": rgroup, "action": "/sendgroup", "method": "GET"}, " ".join(rbs) + "<br><br>" + ref + btnS)
		html += formS

		html += HTML.enddiv()  # buttongroup
		return html

	def TwoButtonGroup(self, heading, buttonsa, buttonsb, turnouts, rgroup, bprefix, action):
		finalMsg = None
		html = HTML.startdiv({"class": "buttongroup"})
		html += HTML.p({}, heading)
		html += HTML.startdiv({"class": "two-button-grid-container"})

		html += HTML.startdiv({"class": "column"})

		html += HTML.startform({"name": rgroup, "action": "/send2group", "method": "GET"})

		buttona = self.refreshData.get(rgroup+"A", buttonsa[0])
		self.refreshData[rgroup+"A"] = buttona
		buttonb = self.refreshData.get(rgroup+"B", buttonsb[0])
		self.refreshData[rgroup+"B"] = buttonb

		if action == 'send':
			vbits = []
			vbytes = []
			vals = []
			for b in [buttona, buttonb]:
				bInfo = self.nxButtons.ButtonInfo(bprefix+b)
				bits = bInfo["position"][0][0]
				addr = bInfo["position"][1]
				vbytes.append(bits[0])
				vbits.append(bits[1])
				vals.append(1)
			msg = {"setoutbit": {"address": "0x%x" % addr, "byte": vbytes, "bit": vbits, "value": vals, "pulse": True}}
			r = self.rrserver.Request(msg)
			if not r:
				finalMsg = HTML.p({}, "Unable to send request.  Is RRServer running?")
			else:
				finalMsg = HTML.p({}, "Request successfully sent")

		rbs = []
		prefix = ""
		group = rgroup + "A"
		for bname in buttonsa:
			parms = {"type": "radio", "id": bname, "name": group, "value": bname}
			if bname == buttona:
				parms["checked"] = None

			rbs.append(prefix + HTML.input(parms) + HTML.label({"for": id}, bname))
			prefix = "<br>"
		html += " ".join(rbs)

		html += HTML.enddiv()  # column 1

		html += HTML.startdiv({"class": "column"})

		rbs = []
		prefix = ""
		group = rgroup + "B"
		for bname in buttonsb:
			parms = {"type": "radio", "id": bname, "name": group, "value": bname}
			if bname == buttonb:
				parms["checked"] = None

			rbs.append(prefix + HTML.input(parms) + HTML.label({"for": id}, bname))
			prefix = "<br>"
		html += " ".join(rbs)

		html += HTML.enddiv()  # column 2

		html += HTML.startdiv({"class": "column"})

		prefix = ""
		html += HTML.startdiv({"class": "position2"})
		for tn in turnouts:
			pinfo = self.turnouts.GetNode(tn, "position")
			if pinfo is not None:
				bits, addr = pinfo
				if addr is not None:
					bitsset = []
					r = self.rrserver.Get("getbits", {"address": "0x%x" % addr})
					for bv in [bits[0], bits[1]]:
						bbyte, bbit = bv
						bitsset.append(BitSet(bbyte, bbit, r["in"]))
					if bitsset[0] == bitsset[1]:
						pos = "Unknown"
					elif bitsset[0]:
						pos = "Normal"
					else:
						pos = "Reverse"
				else:
					pos = "NA"
			else:
				pos = "NA"

			html += prefix + tn + ":" "&nbsp;" + pos
			prefix = "<br>"

		html += HTML.enddiv()  # position
		html += HTML.enddiv()  # column 3
		html += HTML.enddiv()  # 2button-grid-container

		if finalMsg is not None:
			html += finalMsg

		html += HTML.p({},"")

		html += HTML.input({"type": "hidden", "name": "refdata", "value": REFRESH_DATA_TAG})

		html += HTML.button({"type": "submit", "id": rgroup, "name": rgroup}, "Send")
		html += HTML.endform()

		html += HTML.enddiv()  # buttongroup
		return html

	def StyleSheet(self):
		css = self.parent.StyleSheet()
		css.addElement(".grid-container", {"display": "grid", "grid-template-columns": "1fr 1fr 1fr", "gap": "10px", "padding": "5x"})
		css.addElement(".two-button-grid-container", {"display": "grid", "grid-template-columns": "1fr 1fr 1fr", "gap": "10px", "padding": "5x"})
		css.addElement(".column", {"background-color": "#f4f4f4", "padding": "5px", "border": "1px solid #ddd"})
		css.addElement(".buttongroup", {"background-color": "#f8f8f8", "padding": "5px", "border": "2px solid #ddd"})
		css.addElement(".2buttongroup", {"background-color": "#f8f8f8", "padding": "5px", "border": "2px solid #ddd"})
		css.addElement(".matrix", {"background-color": "#f8f8f8", "padding": "5px", "border": "2px solid #ddd"})
		css.addElement(".singleturnout", {"background-color": "#f8f8f8", "padding": "5px", "border": "2px solid #ddd"})
		css.addElement(".matrixgroup", {"padding-left": "15px"})
		css.addElement("div.selectturnout", {"padding-left": "15px"})
		css.addElement("div.position", {"padding-left": "15px"})
		css.addElement("div.position2", {"padding-left": "10px"})
		css.addElement("form", {"display": "inline-block", "margin": "0"})
		return css


class Turnouts:
	def __init__(self, rrserver):
		self.iodata = rrserver.Get("getiobits", {})
		if self.iodata is None:
			self.turnouts = {}
		else:
			try:
				self.turnouts = {tname: self.iodata["turnouts"][tname] for tname in self.iodata["turnouts"]}  # if len(self.iodata["turnouts"][tname]["control"][0]) > 0}
			except KeyError:
				logging.error("no turnouts in iodata")
				self.turnouts = {}

	def TurnoutNames(self):
		return list(sorted(self.turnouts.keys()))

	def GetNode(self, tnm, function):
		tinfo = self.turnouts.get(tnm, None)
		if tinfo is None:
			return None

		finfo = tinfo.get(function, None)
		if finfo is None:
			return None

		return finfo


class NXButtons:
	def __init__(self, rrserver):
		self.iodata = rrserver.Get("getiobits", {})
		if self.iodata is None:
			self.nxbuttons = {}
		else:
			try:
				self.nxbuttons = {bname: self.iodata["nxbuttons"][bname] for bname in self.iodata["nxbuttons"]}
			except KeyError:
				self.nxbuttons = {}

	def ButtonInfo(self, bn):
		if bn not in self.nxbuttons:
			return None
		else:
			return self.nxbuttons[bn]


class RoutesIn:
	def __init__(self, rrserver):
		self.iodata = rrserver.Get("getiobits", {})
		if self.iodata is None:
			self.routesin = {}
		else:
			try:
				self.routesin = {rname: self.iodata["routesin"][rname] for rname in self.iodata["routesin"]}
			except KeyError:
				self.routesin = {}

	def RouteInfo(self, rn):
		if rn not in self.routesin:
			return None
		else:
			return self.routesin[rn]
