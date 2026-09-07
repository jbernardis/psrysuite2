import os
import sys

cmdFolder = os.getcwd()
if cmdFolder not in sys.path:
	sys.path.insert(0, cmdFolder)

from utilities import HTML


class ActiveRoutes:
	def __init__(self, parent, rrserver):
		self.parent = parent
		self.rrserver = rrserver

	def ProcessURL(self, urlinfo):
		return self.HTMLActiveRoutes()

	def HTMLActiveRoutes(self):
		rte = self.rrserver.Get("getroutes", {})

		css = self.StyleSheet()

		html = HTML.starthtml()
		html += HTML.head(HTML.style({'type': "text/css"}, css))

		html += HTML.startbody()
		html += HTML.h1({}, "Active Routes")

		html += "<br><br>"

		headings = ["OS", "Route"]
		hcols = [HTML.th({}, hdg) for hdg in headings]
		hdgHtml = HTML.tr({}, "".join(hcols))

		rows = []
		for osn in sorted(rte.keys()):
			os = HTML.td({}, osn)
			rt = HTML.td({}, rte[osn])
			rows.append(HTML.tr({},os+rt))

		html += HTML.table({}, hdgHtml + "".join(rows))

		html += "<br><br>"

		html += HTML.startdiv({"class": "rterefresh"})

		btn = HTML.button({"type": "submit", "id": "refresh", "name": "refresh"}, "Refresh")
		refresh = HTML.form({"name": "rterefresh", "action": "/actroutes", "method": "GET"}, "<br><br>" + btn)
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

	def StyleSheet(self):
		css = self.parent.StyleSheet()
		css.addElement("div.rterefresh", {"padding-left": "35px"})
		css.addElement("table", {"border-collapse": "collapse", "border-spacing": "0", "width": "auto",
							"font-family": 'Arial, sans-serif', "font-size": "14px", "margin-left": "30mm"})
		css.addElement("th", {'text-align': 'center', 'overflow': 'hidden', "background-color": "#A0A0A0"})
		css.addElement("td", {'text-align': 'center', 'overflow': 'hidden', 'width': '30mm', 'font-weight': 'bold',
							"background-color": "#FFFFFF"})
		css.addElement("table, th, td", {'border': "1px solid black", 'border-collapse': 'collapse'})

		return css
