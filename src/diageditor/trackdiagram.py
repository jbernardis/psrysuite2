import wx
import os

def PIL2wx (image):
	width, height = image.size
	return wx.Bitmap.FromBuffer(width, height, image.tobytes())

wildcard = "Bitmap (*.bmp)|*.bmp"

class TrackDiagram(wx.Panel):
	def __init__(self, parent, bgcanvas, fn, cmdFolder):
		self.bgcanvas = bgcanvas
		self.fn = fn
		self.bgimg = self.bgcanvas.GetCanvas()
		self.bgbmp = PIL2wx(self.bgimg)
		w, h = self.bgimg.size
		wx.Panel.__init__(self, parent, size=(w, h), style=0)
		self.modified = False
		
		self.bmpCursor = wx.Image(os.path.join(cmdFolder, "images", "cursor.bmp"), wx.BITMAP_TYPE_BMP).ConvertToBitmap()
		
		self.tileCurrent = [None, None]
		
		self.parent = parent
		self.SetBackgroundStyle(wx.BG_STYLE_PAINT)
		self.SetCursor(wx.Cursor(wx.CURSOR_ARROW))

		self.Bind(wx.EVT_PAINT, self.OnPaint)
		self.Bind(wx.EVT_MOTION, self.OnMotion)
		self.Bind(wx.EVT_LEFT_UP, self.OnLeftUp)
		self.Bind(wx.EVT_RIGHT_UP, self.OnRightUp)
		self.tx = None
		self.ty = None
		self.cursorx = None
		self.cursory = None
		
		self.tiles = []
		self.undone = []
		
	def ExtractCanvas(self):
		self.bgimg = self.bgcanvas.GetCanvas()
		self.bgbmp = PIL2wx(self.bgimg)
		
	def SetModified(self, flag=True):
		if flag != self.modified:
			self.modified = flag
			self.parent.ReportModified(flag)
		
	def IsModified(self):
		return self.modified
		
	def SetCurrentTile(self, img):
		self.tileCurrent = img

	def OnMotion(self, evt):
		pt = evt.GetPosition()
		ntx, nty = self.bgcanvas.tileFromCanvas(pt.x, pt.y)

		if ntx != self.tx or nty != self.ty:
			self.tx = ntx
			self.ty = nty
			self.parent.UpdatePositionDisplay(ntx, nty)

	def OnRightUp(self, evt):
		self.cursorx = self.tx
		self.cursory = self.ty
		self.Refresh()

	def OnLeftUp(self, evt):
		self.cursorx = self.tx
		self.cursory = self.ty
		if self.tileCurrent[0]:
			self.tiles.append([self.tx, self.ty, self.tileCurrent[0], self.tileCurrent[1]])
			self.SetModified()
			
		self.Refresh()
		
	def UnDo(self):
		try:
			t = self.tiles.pop()
		except IndexError:
			# nothing to undo
			return 

		if len(self.tiles) == 0:
			self.SetModified(False)
				
		self.undone.append(t)
		self.Refresh()
		
	def ReDo(self):
		try:
			t = self.undone.pop()
		except IndexError:
			# nothing to redo
			return 
		
		self.tiles.append(t)
		self.SetModified()
		self.Refresh()
		
	def Revert(self):
		if len(self.tiles) == 0:
			# nothing to revert
			return
		
		dlg = wx.MessageDialog(self,
				'Reverting will lose all changes since the last save\n\nPress "Yes" to confirm, or "No" to cancel',
				'Are you sure you want to revert?',
				wx.YES_NO | wx.NO_DEFAULT | wx.ICON_WARNING)
		rc = dlg.ShowModal()
		dlg.Destroy()
		if rc != wx.ID_YES:
			return 
		
		self.tiles = []
		self.undone = []
		self.Refresh()
		self.SetModified(False)
		
	def Save(self):
		folder, basename = os.path.split(self.fn)
		dlg = wx.FileDialog(
			self, message="Save file as ...", defaultDir=folder,
			defaultFile=basename, wildcard=wildcard, style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
		rc = dlg.ShowModal()
		if rc == wx.ID_OK:
			path = dlg.GetPath()
		dlg.Destroy()
		if rc != wx.ID_OK:
			return
		
		self.fn = path
		self.parent.UpdateFileName(path)

		self.bgcanvas.ApplyTiles(self.tiles, path)
		self.ExtractCanvas()
		self.tiles = []
		self.undone = []
		self.Refresh()
		self.SetModified(False)
		

	def OnPaint(self, evt):
		dc = wx.BufferedPaintDC(self)
		dc.SetTextForeground(wx.Colour(255, 0, 0))
		dc.SetTextBackground(wx.Colour(255, 255, 255))
		dc.SetBackgroundMode(wx.BRUSHSTYLE_SOLID)
		dc.SetFont(wx.Font(wx.Font(10, wx.FONTFAMILY_ROMAN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, faceName="Arial")))
		self.DrawBackground(dc)
		if self.cursorx is not None and self.cursory is not None:
			box = self.bgcanvas.canvasBoxForCursor(self.cursorx, self.cursory)
			dc.DrawBitmap(self.bmpCursor, box[0], box[1])
		for bx, by, bmp, _ in self.tiles:
			box = self.bgcanvas.canvasBoxForTile(bx, by)
			dc.DrawBitmap(bmp, box[0], box[1])

	def DrawBackground(self, dc):
		dc.DrawBitmap(self.bgbmp, 0, 0)
