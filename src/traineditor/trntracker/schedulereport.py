import wx
import os
import sys
import qrcode
import utilities.HTML as HTML
from traineditor.reports import Report
from traineditor.trntracker.choosetrains import ChooseScheduleDlg
from traineditor.trntracker.schedule import Schedule

BTNSZ = (120, 46)


class ScheduleReport (Report):
	def __init__(self, parent, browser):
		Report.__init__(self, parent, browser)
		self.parent = parent
		self.RRServer = None
		self.roster = None
		self.locos = None
					
	def getSchedFiles(self):
		schedList = self.RRServer.Get("schedlist", {})
		if len(schedList) == 0:
			dlg = wx.MessageDialog(self, "No Schedules exist", "File Not Found", wx.OK | wx.ICON_WARNING)
			dlg.ShowModal()
			dlg.Destroy()
			return []

		return [s[:-5] for s in schedList]  # strip off the .json suffix

	def ScheduleReport(self, roster, locos, rrserver):
		self.roster = roster
		self.locos = locos
		self.RRServer = rrserver
		dlg = ChooseScheduleDlg(self.parent, self.getSchedFiles(), False)
		rc = dlg.ShowModal()
		if rc != wx.ID_OK:
			dlg.Destroy()
			return

		schedNm = dlg.GetValue()
		dlg.Destroy()

		sched = Schedule()
		if not sched.load(schedNm, self.RRServer):
			return

		css = HTML.StyleSheet()
		css.addElement("table", {"border-collapse": "collapse", "border-spacing": "0", "width": "170mm", "font-family": 'Arial, sans-serif', "font-size": "20px", "margin-left": "auto", "margin-right": "auto"})
		css.addElement("th", {'text-align': 'center',  'overflow': 'hidden'})
		css.addElement("td", {'text-align': 'center',  'overflow': 'hidden'})
		css.addElement("table, th, td", { 'border': "1px solid black", 'border-collapse': 'collapse'})
		css.addElement("td.index", {"width": "10mm", "font-weight": "bold"})
		css.addElement("td.trainid", {"width": "20mm", "font-weight": "bold"})
		css.addElement("td.loco", {"width": "20mm", "font-weight": "bold"})
		css.addElement("td.dir", {"width": "10mm", "font-weight": "bold"})
		css.addElement("td.engineer", {"width": "60mm"})
		css.addElement("td.origin", {"width": "25mm", "font-weight": "bold"})
		css.addElement("td.terminus", {"width": "25mm", "font-weight": "bold"})
		css.addElement("td.freight", {"background-color": "#FFB6B2"})
		css.addElement("td.passenger", {"background-color": "#8AFFBB"})
		css.addElement("p.header", {"font-family": 'Arial, sans-serif', "font-size": "30px", "font-weight": "bold"})

		html  = HTML.starthtml()
		html += HTML.head(HTML.style({'type': "text/css", 'media': "screen, print"}, css))

		html += HTML.startbody()

		header = HTML.tr({},
			HTML.th({}, ""),
			HTML.th({}, "Train"),
			HTML.th({}, "Loco"),
			HTML.th({}, "Dir"),
			HTML.th({}, "Engineer"),
			HTML.th({}, "Origin"),
			HTML.th({}, "Terminus"),
			)

		activetrains = self.RRServer.Get("activetrains", {})
		print("active trains = %s" % str(activetrains), file=sys.stderr)

		rows = []
		rowx = 1
		for tid in sched.getSchedule():
			tinfo = activetrains.get(tid, None)
			rows.append(self.formatTableRow(tid, tinfo, rowx))
			rowx += 1

		if len(rows) > 0:
			html += HTML.div({"style": "height: 50px"})
			html += HTML.p({'align': 'center', 'class': 'header'}, "Main Schedule")
			html += HTML.table({}, header, "".join(rows))

		rows = []
		rowx = 1
		for tid in sched.getExtras():
			tinfo = activetrains.get(tid, None)
			rows.append(self.formatTableRow(tid, tinfo, rowx))
			rowx += 1

		if len(rows) > 0:
			html += HTML.div({"style": "height: 50px"})
			html += HTML.p({'align': 'center', 'class': 'header'}, "Extra Trains")
			html += HTML.table({}, header, "".join(rows))

		html += HTML.endbody()
		html += HTML.endhtml()

		self.openBrowser("Schedule", html)

	def formatTableRow(self, tid, tinfo, rowx):
		r = self.roster.get(tid, None)
		if r is None:
			east = True
			origin = ""
			terminus = ""
			loco = None
		else:
			east = r["eastbound"]
			origin = "%s" % r["origin"]["loc"]
			trk = r["origin"]["track"]
			if trk is not None:
				origin += "(%s)" % trk
			terminus = "%s" % r["terminus"]["loc"]
			trk = r["terminus"]["track"]
			if trk is not None:
				terminus += "(%s)" % trk
			loco = r.get("normalloco", None)

		if tinfo is not None:
			aloco = tinfo.get("loco", None)
			if loco is None:
				loco = aloco

		if loco is None:
			loco = ""
		else:
			linfo = self.locos.getLoco(loco)
			if linfo is not None and linfo["short"]:
				loco += "(s)"

		passenger = tid[0].isdigit()

		engineer = ""

		colorClass = "passenger" if passenger else "freight"

		return HTML.tr({},
			HTML.td({"class": "index"}, "%-2d" % rowx),
			HTML.td({"class": "trainid %s" % colorClass}, tid),
			HTML.td({"class": "loco"}, loco),
			HTML.td({"class": "dir"}, "E" if east else "W"),
			HTML.td({"class": "engineer"}, engineer),
			HTML.td({"class": "origin"}, origin),
			HTML.td({"class": "terminus"}, terminus)
		)
