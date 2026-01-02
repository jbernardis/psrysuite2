import os
import utilities.HTML as HTML
from traineditor.reports import Report

BTNSZ = (120, 46)


class EngineerCards (Report):
	def __init__(self, parent, browser):
		Report.__init__(self, parent, browser)

	def CheckQRFiles(self, engList):
		engOrder  = sorted(engList)
		missingFiles = []
		for eng in engOrder:
			fn = os.path.join("qrcodes", "engineer_%s.png" % eng)
			if not os.path.exists(fn):
				missingFiles.append(eng)
		return missingFiles

	def EngineerCards(self, englist):
		css = HTML.StyleSheet()
		css.addElement("table", {'width': '700px', 'border-spacing': '0',  'margin-left': 'auto', 'margin-right': 'auto', "font-family": '"Times New Roman", Times, serif', "font-size": "16px"})
		css.addElement("table, th, td", {'border-collapse': 'collapse'})
		css.addElement("th", {'text-align': 'center',  'overflow': 'hidden'})
		css.addElement("td.eng", {"text-align": "center", "width": "140px", "font-size": "28px", "font-weight": "bold", "border-top": "1px solid black", "border-bottom": "1px solid black", "border-left": "1px solid black"})
		css.addElement("td.qr", {"width": "100px", "text-align": "center",  "vertical-align": "middle", "border-top": "1px solid black", "border-bottom": "1px solid black", "border-right": "1px solid black"})
		css.addElement("td.engmt", {"text-align": "center", "width": "140px", "font-size": "28px", "font-weight": "bold"})
		css.addElement("td.qrmt", {"width": "100px", "text-align": "center",  "vertical-align": "middle"})
		css.addElement("td.spacer", {"width": "80px"})



		html  = HTML.starthtml()
		html += HTML.head(HTML.style({'type': "text/css", 'media': "screen, print"}, css))
		
		html += HTML.startbody()

		rows = []
		engOrder  = sorted(englist)
		for ex in range(0, len(englist), 2):
			eng = englist[ex]
			fn = os.path.join("qrcodes", "engineer_%s.png" % eng)
			if os.path.exists(fn):
				img = HTML.img({"src": fn})
				left = (HTML.td({"class": "eng"}, eng) +
						HTML.td({"class": "qr"}, img))
			else:
				left = (HTML.td({"class": "eng"}, eng) +
						HTML.td({"class": "qr"}, ""))

			if ex == len(englist)-1:
				right = (HTML.td({"class": "engmt"}, "") +
						HTML.td({"class": "qrmt"}, ""))
			else:
				eng = englist[ex+1]
				fn = os.path.join("qrcodes", "engineer_%s.png" % eng)
				if os.path.exists(fn):
					img = HTML.img({"src": fn})
					right = (HTML.td({"class": "eng"}, eng) +
							HTML.td({"class": "qr"}, img))
				else:
					right = (HTML.td({"class": "eng"}, eng) +
							HTML.td({"class": "qr"}, ""))

			html += HTML.table({}, left + HTML.td({"class": "spacer"}, "") + right)

			html += HTML.p({}, "")

		html += HTML.endbody()
		html += HTML.endhtml()

		self.openBrowser("Engineer Cards", html)
