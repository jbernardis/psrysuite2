import wx
import os
import webbrowser

BTNSZ = (120, 46)

class Report:
	def __init__(self, parent, browser):
		self.initialized = False
		self.parent = parent
		
		browserCmd = browser.replace("\\", "/")  + " --app=%s"

		try:
			self.browser = webbrowser.get(browserCmd)
		except webbrowser.Error:
			dlg = wx.MessageDialog(self.parent, "Unable to find an available browser at\n%s" % browserCmd,
					"Report Initialization failed",
					wx.OK | wx.ICON_ERROR)
			dlg.ShowModal()
			dlg.Destroy()
			return

		self.initialized = True
		
	def Initialized(self):
		return self.initialized
	
	def openBrowser(self, title, html):
		htmlFileName = "report.html"
		with open(htmlFileName, "w") as fp:
			fp.write(html)
		
		path = os.path.join(os.getcwd(), htmlFileName)
		
		fileURL = 'file:///'+path

		self.browser.open_new(fileURL)
	