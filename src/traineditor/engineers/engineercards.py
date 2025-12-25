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
		css.addElement("table", {'width': '300px', 'border-spacing': '0',  'margin-left': 'auto', 'margin-right': 'auto', "font-family": '"Times New Roman", Times, serif', "font-size": "16px"})
		css.addElement("table, th, td", {'border-collapse': 'collapse'})
		css.addElement("th", {'text-align': 'center',  'overflow': 'hidden'})
		css.addElement("td.eng", {"text-align": "center", "width": "170px", "font-size": "28px", "font-weight": "bold"})
		css.addElement("td.qr", {"width": "170px", "text-align": "center",  "vertical-align": "middle"})

		html  = HTML.starthtml()
		html += HTML.head(HTML.style({'type': "text/css", 'media': "screen, print"}, css))
		
		html += HTML.startbody()

		rows = []
		engOrder  = sorted(englist)
		for eng in engOrder:
			fn = os.path.join("qrcodes", "engineer_%s.png" % eng)
			if os.path.exists(fn):
				img = HTML.img({"src": fn})
				rows.append(HTML.tr({},
						HTML.td({"class": "eng"}, eng),
						HTML.td({"class": "qr"}, img)
						)
				)
		html += HTML.table({}, "".join(rows))

		html += HTML.endbody()
		html += HTML.endhtml()

		self.openBrowser("Engineer Cards", html)
