import os
import sys
import logging
import json

cmdFolder = os.getcwd()
if cmdFolder not in sys.path:
	sys.path.insert(0, cmdFolder)

from rrserver.constants import nodeNames
from utilities import HTML


class GetBits:
	def __init__(self, parent, rrserver):
		self.parent = parent
		self.rrserver = rrserver
		self.nodeNames = sorted(nodeNames.values())
		self.nodeMap = {nm: addr for addr, nm in nodeNames.items()}

	def ProcessURL(self, urlinfo):
		path, query, params = urlinfo

		if path in ["menuchoice", "nodechoice"]:
			try:
				nodeName = query['nodelist'][0]
			except (KeyError, IndexError):
				try:
					nodeName = query['refreshnode'][0]
				except (KeyError, IndexError):
					nodeName = None
					logging.info("Unable to determine node name from query: %s" % str(query))
			return self.HTMLGetBits(nodename=nodeName)

		return 400, "Invalid path: %s" % path

	def HTMLGetBits(self, nodename=None):
		css = self.StyleSheet()

		html = HTML.starthtml()
		html += HTML.head(HTML.style({'type': "text/css"}, css))

		html += HTML.startbody()
		html += HTML.h1({}, "Node O/I Bits")

		html += HTML.startdiv({"class": "selectnode"})
		html += HTML.label({"for": "nodelist"}, "Choose a Node: ")

		choices = []
		if nodename is None:
			self.selectedNode = self.nodeNames[0]

		else:
			self.selectedNode = nodename

		for nn in self.nodeNames:
			opts = {"value": nn}
			if nn == self.selectedNode:
				opts["selected"] = None
			choices.append(HTML.option(opts, nn))
		selectHtml = HTML.select({"name": "nodelist", "id": "nodelist", "onchange": "this.form.submit()"}, " ".join(choices))
		nodechoice = HTML.form({"name": "nodechoice", "action": "/nodechoice", "method": "GET"}, selectHtml)

		html += nodechoice
		html += "Chosen node: " + HTML.strong({}, "%s" % self.selectedNode) + "<br><br>"

		html += HTML.enddiv()

		ndAddr = self.nodeMap.get(self.selectedNode, None)
		if ndAddr is not None:
			r = self.rrserver.Get("getbits", {"address": "0x%x" % ndAddr})

			fn = os.path.join(os.getcwd(), "tester", "nodes", self.selectedNode + ".json")
			ndData = {}
			with open(fn) as jfp:
				try:
					ndData = json.load(jfp)
				except:
					ndData = {}

			html += self.BuildTable(r["out"], r["in"], ndData)
		else:
			html += "can't determine address for node %s" % self.selectedNode

		html += HTML.startdiv({"class": "bitsrefresh"})

		btn = HTML.button({"type": "submit", "id": "refresh", "name": "refresh"}, "Refresh")
		inp = HTML.input({"type": "hidden", "name": "refreshnode", "value": self.selectedNode})
		refresh = HTML.form({"name": "bitsrefresh", "action": "/nodechoice", "method": "GET"}, inp + "<br><br>" + btn)
		html += refresh

		html += HTML.enddiv()

		html += HTML.startdiv({"class": "backbutton"})

		btn = HTML.button({"type": "submit", "id": "back", "name": "back"}, "Back")
		menu = HTML.form({"name": "betbits", "action": "/index", "method": "GET"}, btn)
		html += menu

		html += HTML.enddiv()

		html += HTML.endbody()
		html += HTML.endhtml()
		return 200, html

	def BuildTable(self, obytes, ibytes, nddata):
		html = "<br><br>"
		orows = []

		olen = len(nddata["obytes"])
		ilen = len(nddata["ibytes"])

		html += HTML.h1("Output Bytes<br>")
		headings = ["Byte %d" % i for i in range(olen)]
		hcols = [HTML.th({}, hdg) for hdg in headings]
		hdgHtml = HTML.tr({}, "".join(hcols))

		for bitx in range(8):
			orow = []
			for obx in range(olen):
				oby = obytes[obx]
				if (oby & (1 << bitx)) != 0:
					bitclass = "biton"
				else:
					bitclass = "bitoff"

				try:
					orow.append(HTML.td({"class": bitclass}, nddata["obytes"][obx][bitx]["label"]))
				except:
					print("error indexing nddata: %d %d" % (obx, bitx))

			orows.append(HTML.tr({}, "".join(orow)))

		html += HTML.table({}, hdgHtml + "".join(orows))
		html += "<br><br>"
		html += HTML.h1("Input Bytes<br>")

		headings = ["Byte %d" % i for i in range(ilen)]
		hcols = [HTML.th({}, hdg) for hdg in headings]
		hdgHtml = HTML.tr({}, "".join(hcols))

		irows = []
		for bitx in range(8):
			irow = []
			for ibx in range(ilen):
				iby = ibytes[ibx]

				bx = 7 - bitx
				if (iby & (1 << bx)) != 0:
					bitclass = "biton"
				else:
					bitclass = "bitoff"

				try:
					irow.append(HTML.td({"class": bitclass}, nddata["ibytes"][ibx][bitx]["label"]))
				except (KeyError, IndexError):
					irow.append(HTML.td({}, ""))
			irows.append(HTML.tr({}, "".join(irow)))

		html += HTML.table({}, hdgHtml + "".join(irows))

		return html

	def StyleSheet(self):
		css = self.parent.StyleSheet()
		css.addElement("div.selectnode", {"padding-left": "35px"})
		css.addElement("div.bitsrefresh", {"padding-left": "35px"})
		css.addElement("table", {"border-collapse": "collapse", "border-spacing": "0", "width": "auto",
								 "font-family": 'Arial, sans-serif', "font-size": "14px", "margin-left": "30mm"})
		css.addElement("th", {'text-align': 'center', 'overflow': 'hidden'})
		css.addElement("td", {'text-align': 'center', 'overflow': 'hidden', 'width': '60mm', 'font-weight': 'bold'})
		css.addElement("table, th, td", {'border': "1px solid black", 'border-collapse': 'collapse'})
		css.addElement("td.biton", {"background-color": "#FFFFFF"})
		css.addElement("td.bitoff", {"background-color": "#808080"})

		return css
