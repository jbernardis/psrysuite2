import utilities.HTML as HTML
from traineditor.reports import Report
BTNSZ = (120, 46)

class LocosReport (Report):
	def __init__(self, parent, browser):
		Report.__init__(self, parent, browser)
					
	def BuildLocoKey(self, lid):
		return int(lid)
	
	def LocosReport(self, locos):
		css = HTML.StyleSheet()
		css.addElement("table", {'width': '650px', 'border-spacing': '15px',  'margin-left': 'auto', 'margin-right': 'auto'})
		css.addElement("table, th, td", { 'border': "1px solid black", 'border-collapse': 'collapse'})
		css.addElement("th", {'text-align': 'center',  'overflow': 'hidden'})
		css.addElement("td.loco", {"text-align": "right", "width": "90px", "padding-right": "40px"})
		css.addElement("td.desc", {"text-align": "left", "width": "500px", "padding-left": "20px"})
		css.addElement("td.step", {"text-align": "right", "width": "40px", "padding-right": "10px"})
		css.addElement("td.speed", {"text-align": "right", "width": "70px", "padding-right": "10px"})
		
		html  = HTML.starthtml()
		html += HTML.head(HTML.style({'type': "text/css", 'media': "screen, print"}, css))
		
		html += HTML.startbody()
		
		html += HTML.h1({'align': 'center'}, "Locomotives")
		
		header = HTML.tr({},
			HTML.th({}, "Loco Number"),
			HTML.th({}, "Description"),
			HTML.th({}, "+"),
			HTML.th({}, "-"),
			HTML.th({}, "start"),
			HTML.th({}, "appr"),
			HTML.th({}, "med"),
			HTML.th({}, "fast"),
			)
		
		rows = []
		locoOrder  = sorted(locos.keys(), key=self.BuildLocoKey)
		for lid in locoOrder:
			desc =   locos[lid]["desc"]
			acc =    locos[lid]["prof"]["acc"]
			dec =    locos[lid]["prof"]["dec"]
			start =  locos[lid]["prof"]["start"]
			slow =   locos[lid]["prof"]["slow"]
			medium = locos[lid]["prof"]["medium"]
			fast =   locos[lid]["prof"]["fast"]
			if desc is None:
				desc = ""
			rows.append(HTML.tr({},
					HTML.td({"class": "loco"}, lid),
					HTML.td({"class": "desc"}, desc),
					HTML.td({"class": "step"}, acc),
					HTML.td({"class": "step"}, dec),
					HTML.td({"class": "speed"}, start),
					HTML.td({"class": "speed"}, slow),
					HTML.td({"class": "speed"}, medium),
					HTML.td({"class": "speed"}, fast)
					)
			)
		html += HTML.table({}, header, "".join(rows))

			
		html += HTML.endbody()
		html += HTML.endhtml()
		
		self.openBrowser("Locomotives Report", html)
	