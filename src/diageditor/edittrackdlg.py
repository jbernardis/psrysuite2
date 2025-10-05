import wx

from tilecanvas import TileCanvas
from trackdiagram import TrackDiagram

class EditTrackDlg(wx.Dialog):
	def __init__(self, parent, fn, closer, cmdFolder):
		wx.Dialog.__init__(self, parent, wx.ID_ANY, "Track Editor: %s" % fn, style=wx.CAPTION | wx.CLOSE_BOX | wx.DIALOG_NO_PARENT)
		self.parent = parent
		self.fn = fn
		self.modified = False
		self.closer = closer
		self.currentPalletteTile = [None, None]
		self.Bind(wx.EVT_CLOSE, self.DoCancel)
		self.parent = parent
		self.canvas = TileCanvas(fn)
		self.dp = TrackDiagram(self, self.canvas, self.fn, cmdFolder)
		self.dp.SetCurrentTile(self.currentPalletteTile)
		
		vsz = wx.BoxSizer(wx.VERTICAL)
		vsz.AddSpacer(10)
		
		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.AddSpacer(10)
		hsz.Add(self.dp)
		hsz.AddSpacer(10)
		vsz.Add(hsz)
		
		hsz = wx.BoxSizer(wx.HORIZONTAL)
		
		self.bUnDo = wx.Button(self, wx.ID_ANY, "UnDo")
		self.Bind(wx.EVT_BUTTON, self.DoUnDo, self.bUnDo)
		hsz.Add(self.bUnDo)
		
		self.bReDo = wx.Button(self, wx.ID_ANY, "ReDo")
		self.Bind(wx.EVT_BUTTON, self.DoReDo, self.bReDo)
		hsz.Add(self.bReDo)
		
		hsz.AddSpacer(50)
		
		self.bRevert = wx.Button(self, wx.ID_ANY, "Revert")
		self.Bind(wx.EVT_BUTTON, self.DoRevert, self.bRevert)
		hsz.Add(self.bRevert)
		
		hsz.AddSpacer(100)
		
		self.bSave = wx.Button(self, wx.ID_ANY, "Save")
		self.Bind(wx.EVT_BUTTON, self.DoSave, self.bSave)
		hsz.Add(self.bSave)
		
		hsz.AddSpacer(10)
		
		self.bCancel = wx.Button(self, wx.ID_ANY, "Cancel")
		self.Bind(wx.EVT_BUTTON, self.DoCancel, self.bCancel)
		hsz.Add(self.bCancel)
		
		hsz.AddSpacer(500)
		
		self.xpos = wx.TextCtrl(self, wx.ID_ANY, "", size=(60, -1), style=wx.TE_READONLY)
		self.ypos = wx.TextCtrl(self, wx.ID_ANY, "", size=(60, -1), style=wx.TE_READONLY)
		hsz.Add(self.xpos)
		hsz.AddSpacer(10)
		hsz.Add(self.ypos)
		hsz.AddSpacer(20)
		vsz.Add(hsz, 0, wx.ALIGN_RIGHT)
		
		self.UpdateTitle()
		
		self.SetSizer(vsz)
		self.Layout()
		self.Fit()
		
		self.CenterOnScreen()
		
	def UpdateTitle(self):
		tstring = "Track Diagram Editor: %s" % self.fn
		if self.modified:
			tstring += " - MODIFIED"
			
		self.SetTitle(tstring)
		self.dp.SetFocus()
		
	def ReportModified(self, flag):
		self.modified = flag
		self.UpdateTitle()
		
	def UpdateFileName(self, newfn):
		self.fn = newfn
		self.UpdateTitle()
		self.parent.UpdateDirectory(newfn)
	
	def UpdatePositionDisplay(self, x, y):
		self.xpos.SetValue("%4d" % x)
		self.ypos.SetValue("%4d" % y)
		self.dp.SetFocus()

	def SetCurrentTile(self, img):
		self.currentPalletteTile = img
		self.dp.SetCurrentTile(img)
		
	def DoUnDo(self, _):
		self.dp.UnDo()
		
	def DoReDo(self, _):
		self.dp.ReDo()
		
	def DoRevert(self, _):
		self.dp.Revert()
		
	def DoSave(self, _):
		self.dp.Save()
		
	def DoCancel(self, evt):
		if self.modified:
			dlg = wx.MessageDialog(self,
					'Cancelling will lose all changes since the last save\n\nPress "Yes" to confirm, or "No" to cancel',
					'Are you sure you want to cancel?',
					wx.YES_NO | wx.NO_DEFAULT | wx.ICON_WARNING)
			rc = dlg.ShowModal()
			dlg.Destroy()
			if rc != wx.ID_YES:
				return 
		self.closer()
