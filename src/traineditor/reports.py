import wx
import os
import webbrowser

BTNSZ = (120, 46)


class Report:
	def __init__(self, parent, browser, spreadsheet):
		self.initialized = False
		self.parent = parent

		if browser is None or browser.strip() == "":
			self.browser = None
		else:
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

		self.spreadsheet = spreadsheet

		self.initialized = True

	def Initialized(self):
		return self.initialized
	
	def openBrowser(self, title, html):
		if self.browser is None:
			wildcard = "HTML (*.html)|*.html|All files (*.*)|*.*"

			dlg = wx.FileDialog(self.parent, message="Save file as ...", defaultDir=os.getcwd(),
				defaultFile="", wildcard=wildcard, style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
			rc = dlg.ShowModal()
			if rc != wx.ID_OK:
				dlg.Destroy()
				return

			htmlFileName = dlg.GetPath()
			dlg.Destroy()

		else:
			htmlFileName = "report.html"

		with open(htmlFileName, "w") as fp:
			fp.write(html)

		if self.browser is None:
			dlg = wx.MessageDialog(self.parent, "HTML saved to file\n%s" % htmlFileName,
					"File Saved", wx.OK | wx.ICON_INFORMATION)
			dlg.ShowModal()
			dlg.Destroy()

		else:
			path = os.path.join(os.getcwd(), htmlFileName)
			fileURL = 'file:///'+path
			self.browser.open_new(fileURL)
	