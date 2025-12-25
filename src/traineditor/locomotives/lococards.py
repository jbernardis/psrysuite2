import os
import utilities.HTML as HTML
from traineditor.reports import Report

BTNSZ = (120, 46)


class LocoCards (Report):
	def __init__(self, parent, browser):
		Report.__init__(self, parent, browser)

	def CheckQRFiles(self, locos):
		locoOrder  = sorted(locos.keys(), key=lambda x: int(x))
		missingFiles = []
		for lid in locoOrder:
			fn = os.path.join("qrcodes", "locomotive_%s.png" % lid)
			if not os.path.exists(fn):
				missingFiles.append("%s" % lid)
		return missingFiles

	def CheckPictureFiles(self, locos):
		locoOrder  = sorted(locos.keys(), key=lambda x: int(x))
		missingFiles = []
		for lid in locoOrder:
			fn = os.path.join("qrcodes", "picture_%s.png" % lid)
			if not os.path.exists(fn):
				missingFiles.append("%s" % lid)
		return missingFiles

	def LocoCards(self, locos):
		css = HTML.StyleSheet()
		css.addElement("table", {'width': '380px', 'border-spacing': '0',  'margin-left': 'auto', 'margin-right': 'auto', "font-family": '"Times New Roman", Times, serif', "font-size": "16px"})
		css.addElement("table, th, td", {'border-collapse': 'collapse'})
		css.addElement("th", {'text-align': 'center',  'overflow': 'hidden'})
		css.addElement("td.loco", {"text-align": "center", "width": "170px", "font-size": "28px", "font-weight": "bold"})
		css.addElement("td.desc", {"text-align": "center", "width": "170px", "font-size": "16px", "font-weight": "bold"})
		css.addElement("td.qr", {"width": "170px", "text-align": "center",  "vertical-align": "middle"})
		css.addElement("td.picture", {"width": "200px", "text-align": "center",  "vertical-align": "middle"})

		html  = HTML.starthtml()
		html += HTML.head(HTML.style({'type': "text/css", 'media': "screen, print"}, css))
		
		html += HTML.startbody()

		rows = []
		locoOrder  = sorted(locos.keys(), key=lambda x: int(x))
		for lid in locoOrder:
			fn = os.path.join("qrcodes", "locomotive_%s.png" % lid)
			img = HTML.img({"src": fn})
			fn = os.path.join("qrcodes", "picture_%s.png" % lid)
			if os.path.isfile(fn):
				pic = HTML.img({"src": fn})
			else:
				pic = "pic"

			rows.append(HTML.tr({},
					HTML.td({"class": "loco"}, lid),
					HTML.td({"class": "picture", "rowspan": "2"}, pic)
					)
			)
			rows.append(HTML.tr({},
					HTML.td({"class": "qr"}, img)
					)
			)
			rows.append(HTML.tr({},
					HTML.td({"class": "desc", "colspan": 2}, locos[lid]["desc"])
					)
			)
		html += HTML.table({}, "".join(rows))

		html += HTML.endbody()
		html += HTML.endhtml()
		
		self.openBrowser("Locomotive Cards", html)
	