import wx
import os
import sys 
import inspect

cmdFolder = os.path.realpath(os.path.abspath(os.path.split(inspect.getfile( inspect.currentframe() ))[0]))
if cmdFolder not in sys.path:
	sys.path.insert(0, cmdFolder)
	
from edittrackdlg import EditTrackDlg
from pallette import Pallette

wildcard = "Bitmap (*.bmp)|*.bmp"

class MainFrame(wx.Frame):
	def __init__(self):
		wx.Frame.__init__(self, None, size=(900, 800), style=wx.DEFAULT_FRAME_STYLE)
		self.currentPalletteTile = None
		self.Bind(wx.EVT_CLOSE, self.OnClose)
		self.editor = None
		
		icon = wx.Icon()
		icon.CopyFromBitmap(wx.Bitmap(os.path.join(os.getcwd(), "icons", "diagedit.ico"), wx.BITMAP_TYPE_ANY))
		self.SetIcon(icon)
		
		self.startDirectory = os.path.join(os.getcwd(), "images", "bitmaps", "diagrams")
		
		self.pallette = Pallette(self, self.ReportTileSelection, cmdFolder)
		self.pallette.Show()
		
		vsz = wx.BoxSizer(wx.VERTICAL)
		vsz.AddSpacer(60)
		
		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.AddSpacer(60)
		
		self.bOpen = wx.Button(self, wx.ID_ANY, "Open Track\nDiagram File", size=(100, 60))
		hsz.Add(self.bOpen)
		self.Bind(wx.EVT_BUTTON, self.OnOpen, self.bOpen)

		hsz.AddSpacer(60)
		vsz.Add(hsz)
		
		vsz.AddSpacer(60)
		
		self.SetSizer(vsz)
		self.Layout()
		self.Fit()
		
		self.CenterOnScreen()
		
	def OnOpen(self, evt):	
		dlg = wx.FileDialog(
			self, message="Choose a bitmap file",
			defaultDir=self.startDirectory,
			defaultFile="",
			wildcard=wildcard,
			style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST | wx.FD_PREVIEW)

		rc = dlg.ShowModal()
		path = None
		if rc == wx.ID_OK:
			path = dlg.GetPath()
			
		if rc != wx.ID_OK:
			return

		self.UpdateDirectory(path)
		self.editor = EditTrackDlg(self, path, self.closeEditor, cmdFolder)
		self.editor.SetCurrentTile(self.currentPalletteTile)
		self.editor.Show()
		self.bOpen.Enable(False)
		
	def closeEditor(self):
		self.editor.Destroy()
		self.editor = None
		self.bOpen.Enable(True)
		
	def UpdateDirectory(self, path):
		self.startDirectory = os.path.split(path)[0]
		
	def ReportTileSelection(self, img):
		self.currentPalletteTile = img
		if self.editor is not None:
			self.editor.SetCurrentTile(img)
	
	def OnClose(self, _):
		if self.editor:
			dlg = wx.MessageDialog(self, 'Please close the Track Diagram Editor before exiting',
					   'Editor Active', wx.OK | wx.ICON_ERROR)
			dlg.ShowModal()
			dlg.Destroy()
			return

			
		self.pallette.Destroy()
		self.Destroy()

class App(wx.App):
	def OnInit(self):
		self.frame = MainFrame()
		self.frame.Show()
		return True

app = App(False)
app.MainLoop()