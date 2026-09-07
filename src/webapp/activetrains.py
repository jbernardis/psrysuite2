import os
import sys

cmdFolder = os.getcwd()
if cmdFolder not in sys.path:
	sys.path.insert(0, cmdFolder)

from utilities import HTML


class ActiveTrains:
	def __init__(self, parent, rrserver):
		self.parent = parent
		self.rrserver = rrserver

	def ProcessURL(self, urlinfo):
		return self.HTMLActiveRoutes()

	def HTMLActiveRoutes(self):
		tl = self.rrserver.Get("activetrains", {})

		css = self.StyleSheet()

		html = HTML.starthtml()
		html += HTML.head(HTML.style({'type': "text/css"}, css))

		html += HTML.startbody()
		html += HTML.h1({}, "Active Trains")

		html += "<br><br>"

		headings = ["Train", "IName", "Loco", "Dir", "Engineer", "Blocks", "Signal", "Aspect", "Stopped"]
		hcols = [HTML.th({}, hdg) for hdg in headings]
		hdgHtml = HTML.tr({}, "".join(hcols))

		rows = []
		for tname in sorted(tl.keys()):
			tn = HTML.td({}, tname)

			itn = HTML.td({}, tl[tname]["iname"])
			l = tl[tname].get("loco", None)
			if l is None:
				l = "None"
			loco = HTML.td({}, l)

			direct = HTML.td({}, "East" if tl[tname]["east"] else "West")

			e = tl[tname].get("engineer", None)
			if e is None:
				e = "None"
			eng = HTML.td({}, e)

			b = tl[tname].get("blocks", [])
			bl = HTML.td({}, ", ".join(b))

			s = tl[tname].get("signal", None)
			if s is None:
				s = ""
			sig = HTML.td({}, s)

			a = tl[tname].get("aspect", None)
			if a is None:
				a = ""
			asp = HTML.td({}, a)

			stop = HTML.td({}, "True" if tl[tname]["stopped"] else "False")

			rows.append(HTML.tr({},tn+itn+loco+direct+eng+bl+sig+asp+stop))

		html += HTML.table({}, hdgHtml + "".join(rows))

		html += str(tl)

		html += "<br><br>"

		html += HTML.startdiv({"class": "atrefresh"})

		btn = HTML.button({"type": "submit", "id": "refresh", "name": "refresh"}, "Refresh")
		refresh = HTML.form({"name": "atrefresh", "action": "/acttrains", "method": "GET"}, "<br><br>" + btn)
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
		css.addElement("div.atrefresh", {"padding-left": "35px"})
		css.addElement("table", {"border-collapse": "collapse", "border-spacing": "0", "width": "auto",
							"font-family": 'Arial, sans-serif', "font-size": "14px", "margin-left": "30mm"})
		css.addElement("th", {'text-align': 'center', 'overflow': 'hidden', "background-color": "#A0A0A0"})
		css.addElement("td", {'text-align': 'center', 'overflow': 'hidden', 'width': '30mm', 'font-weight': 'bold',
							"background-color": "#FFFFFF"})
		css.addElement("table, th, td", {'border': "1px solid black", 'border-collapse': 'collapse'})

		return css
