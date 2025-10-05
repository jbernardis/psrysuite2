import wx
import os
import sys
import shutil
from glob import glob


class MainFrame(wx.Frame):
	def __init__(self):
		wx.Frame.__init__(self, None, size=(900, 800), style=wx.DEFAULT_FRAME_STYLE)
		self.SetTitle("PSRY Copy Data Files")
		self.Bind(wx.EVT_CLOSE, self.OnClose)

		vszr = wx.BoxSizer(wx.VERTICAL)
		vszr.AddSpacer(20)

		self.cdir = os.path.join(os.getcwd(), "current")
		self.cdirExists = os.path.isdir(self.cdir)
		self.cdirdata = os.path.join(self.cdir, "data")
		self.cdirdataExists = os.path.isdir(self.cdirdata)

		self.files = [x for x in glob(os.path.join(os.getcwd(), "*"))]
		self.choices = []
		for f in self.files:
			if os.path.isdir(f) and os.path.isdir(os.path.join(f, "data")):
				bn = os.path.basename(f)
				if bn not in ["current", "venv"]:
					self.choices.append(bn)

		style = wx.CB_DROPDOWN | wx.CB_READONLY	
		
		self.cbDirs = wx.ComboBox(self, 500, "", size=(160, -1), choices=self.choices, style=wx.CB_DROPDOWN | wx.CB_READONLY)
		if len(self.choices) == 0:
			self.sx = wx.NOT_FOUND
		else:
			self.sx = 0
		self.cbDirs.SetSelection(self.sx)

		vszr.Add(wx.StaticText(self, wx.ID_ANY, "Choose directory to copy from:"), 0, wx.ALIGN_CENTER_HORIZONTAL)
		vszr.AddSpacer(5)			
		vszr.Add(self.cbDirs, 0, wx.ALIGN_CENTER_HORIZONTAL)

		vszr.AddSpacer(20)

		if self.cdirdataExists:

			self.cbRenameData = wx.CheckBox(self, wx.ID_ANY, "Copy current \"data\" directory to \"data-dist\"")
			vszr.Add(self.cbRenameData, 0, wx.ALIGN_CENTER_HORIZONTAL)
			self.cbRenameData.SetValue(True)

			vszr.AddSpacer(20)

		bsz = wx.BoxSizer(wx.HORIZONTAL)
		bsz.AddSpacer(40)

		self.bGo = wx.Button(self, wx.ID_ANY, "Go")
		self.Bind(wx.EVT_BUTTON, self.OnBGo, self.bGo)
		bsz.Add(self.bGo)
		self.bGo.Enable(self.sx != wx.NOT_FOUND and self.cdirExists)

		bsz.AddSpacer(50)

		self.bCancel = wx.Button(self, wx.ID_ANY, "Cancel")
		self.Bind(wx.EVT_BUTTON, self.OnClose, self.bCancel)
		bsz.Add(self.bCancel)

		# TODO: make sure that data exists in source directories
		bsz.AddSpacer(40)

		vszr.Add(bsz)

		vszr.AddSpacer(20)
		
		hszr = wx.BoxSizer(wx.HORIZONTAL)
		hszr.AddSpacer(10)
		hszr.Add(vszr)
		hszr.AddSpacer(10)
		
		self.SetSizer(hszr)
		self.Fit()
		self.Layout()

		if not self.cdirExists:
			wx.CallAfter(self.NoCurrentDirectory)

	def NoCurrentDirectory(self):
		dlg = wx.MessageDialog(self, "Directory \"current\" does not exist.\nDid you extract the zip file?",
				"No \"current\" directory", wx.OK | wx.ICON_ERROR)
		rv = dlg.ShowModal()
		dlg.Destroy()
		self.DoClose()

	def OnBGo(self, _):
		self.sx = self.cbDirs.GetSelection()
		if self.sx == wx.NOT_FOUND:
			return

		curdir = os.path.join(os.getcwd(), self.choices[self.sx])
		newdir = os.path.join(os.getcwd(), "current")

		if self.cdirdataExists:
			if self.cbRenameData.GetValue():
				distdir = os.path.join(newdir, "data-dist")
				if os.path.isdir(distdir):
					dlg = wx.MessageDialog(self, "Directory \"data-dist\" already exists.\nDid you want to destroy the files there?",
						"\"data-dist\" directory already exists", wx.YES_NO | wx.NO_DEFAULT | wx.ICON_ERROR)
					rv = dlg.ShowModal()
					dlg.Destroy()
					if rv == wx.ID_NO:
						self.doClose()
						return

					shutil.rmtree(distdir)

				os.rename(os.path.join(newdir, "data"), os.path.join(newdir, "data-dist"))
			else:
				dlg = wx.MessageDialog(self, "Directory \"data\" already exists.\nDid you want to overwrite the files there?",
					"\"data\" directory already exists", wx.YES_NO | wx.NO_DEFAULT | wx.ICON_ERROR)
				rv = dlg.ShowModal()
				dlg.Destroy()
				if rv == wx.ID_NO:
					self.DoClose()
					return

		shutil.copytree(os.path.join(curdir, "data"), os.path.join(newdir, "data"), dirs_exist_ok=True)

		self.DoClose()


	def OnClose(self, _):
		self.DoClose()

	def DoClose(self):
		self.Destroy()


class App(wx.App):
	def OnInit(self):
		frame = MainFrame()
		frame.Show()
		return True


app = App(False)
app.MainLoop()
