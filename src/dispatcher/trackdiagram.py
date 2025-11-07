import wx


class TrackDiagram(wx.Panel):
	def __init__(self, frame, dlist, ht=None): # dlist = screen, id, diagramBmp, offset):
		wx.Panel.__init__(self, frame, size=(100, 100), pos=(0,0), style=0)
		self.frame = frame
		self.screens = [d.screen for d in dlist]
		self.bgbmps  = [d.bitmap for d in dlist]
		self.offsets = [d.offset for d in dlist]
		self.xoffset = [int(o/16) for o in self.offsets]
		self.xoffset.append(9999)
		self.offsetMap = {d.screen: d.offset for d in dlist}
		self.SetBackgroundStyle(wx.BG_STYLE_PAINT)

		self.showPosition = True
		self.showCTC = False

		self.tiles = {}
		self.text = {}
		self.trains = {}
		self.bitmaps = {}
		self.ctcfgbitmaps = {}
		self.ctcbgbitmaps = {}
		self.ctclabels = {}
		self.tx = 0
		self.ty = 0
		self.scr = -1
		self.shift_down = False
		self.highlitedRoute = []
		self.hilitebmp = None

		self.SetCursor(wx.Cursor(wx.CURSOR_ARROW))

		w = 0
			
		for b in self.bgbmps:
			w += b.GetWidth()
		
		if ht is None:
			h = self.bgbmps[0].GetHeight()  # assume all the same height
		else:
			h = ht

		self.SetSize((w, h))
		self.SetBackgroundStyle(wx.BG_STYLE_PAINT)

		self.Bind(wx.EVT_PAINT, self.OnPaint)
		self.Bind(wx.EVT_MOTION, self.OnMotion)
		self.Bind(wx.EVT_LEFT_UP, self.OnLeftUp)
		self.Bind(wx.EVT_RIGHT_UP, self.OnRightUp)
		self.Bind(wx.EVT_CHAR_HOOK, self.OnKeyDown)
		self.Bind(wx.EVT_KEY_UP, self.OnKeyUp)
		self.Bind(wx.EVT_ENTER_WINDOW, lambda event: self.SetFocus())

	def SetHiliteBmp(self, bmp):
		self.hilitebmp = bmp

	def ShowCTC(self, flag=True):
		if flag == self.showCTC:
			return

		self.showCTC = flag
		self.Refresh()

	def DrawBackground(self, dc):
		for i in range(len(self.bgbmps)):
			dc.DrawBitmap(self.bgbmps[i], self.offsets[i], 0)

	def OnMotion(self, evt):
		pt = evt.GetPosition()
		ntx = int(pt.x/16)
		nty = int(pt.y/16)
		ox = self.DetermineScreen(ntx)
		if ox is None:
			# ignore if we can't determine position
			return

		ntx -= self.xoffset[ox]
		scr = self.screens[ox]

		if ntx != self.tx or nty != self.ty or self.scr != scr:
			self.tx = ntx
			self.ty = nty
			self.scr = scr
			if self.showPosition:
				self.frame.UpdatePositionDisplay(self.tx, self.ty, self.scr)

	def DetermineScreen(self, x):
		for ox in range(len(self.xoffset)-1):
			if self.xoffset[ox] <= x < self.xoffset[ox+1]:
				return ox

		return None 

	def OnKeyDown(self, event):
		keycode = event.GetKeyCode()
		if keycode == wx.WXK_SHIFT:
			self.shift_down = True
			self.frame.SetShift(True)

		event.Skip()

	def OnKeyUp(self, event):
		keycode = event.GetKeyCode()
		if keycode == wx.WXK_SHIFT:
			self.shift_down = False
			self.frame.SetShift(False)

		event.Skip()
		
	def SetShift(self, flag):
		self.shift_down = flag		

	def OnLeftUp(self, evt):
		pt = evt.GetPosition()
		self.frame.ProcessClick(self.scr, (self.tx, self.ty), (pt.x, pt.y), shift=self.shift_down, screenpos=evt.GetPosition())

	def OnRightUp(self, evt):
		pt = evt.GetPosition()
		self.frame.ProcessClick(self.scr, (self.tx, self.ty), (pt.x, pt.y), shift=self.shift_down, right=True, screenpos=evt.GetPosition())

	def DrawTile(self, x, y, offset, bmp):
		self.tiles[(x*16+offset, y*16)] = bmp;
		self.Refresh()

	def DrawText(self, x, y, offset, text):
		self.text[(x*16+offset, y*16)] = text;
		self.Refresh()

	def DrawCustom(self):
		self.Refresh()

	def DrawFixedBitmap(self, x, y, offset, bmp):
		self.bitmaps[x+offset, y] = bmp
		self.Refresh()

	def DrawCTCBitmap(self, fg, x, y, offset, bmp):
		if fg:
			self.ctcfgbitmaps[x+offset, y] = bmp
		else:
			self.ctcbgbitmaps[x+offset, y] = bmp
		self.Refresh()

	def DrawCTCLabel(self, x, y, offset, font, lbl):
		self.ctclabels[x+offset, y] = (lbl, font)
		self.Refresh()

	def ClearText(self, x, y, offset):
		textKey = (x*16+offset, y*16)
		if textKey not in self.text:
			return
		del(self.text[textKey])
		self.Refresh()

	def DrawTrain(self, x, y, offset, trainID, locoID, stopRelay, atc, ar, pinpoint, misrouted):
		self.trains[(x*16+offset, y*16)] = [trainID, locoID, stopRelay, atc, ar, pinpoint, misrouted]
		self.Refresh()

	def ClearTrain(self, x, y, offset, trainID):
		try:
			del self.trains[(x*16+offset, y*16)]
		except KeyError:
			pass
		self.Refresh()

	def SetHighlitedRoute(self, tiles):
		self.highlitedRoute = []
		for s in self.screens:
			if s in tiles:
				self.highlitedRoute.extend(tiles[s])
		self.Refresh()

	def ClearHighlitedRoute(self):
		self.highlitedRoute = []
		self.Refresh()

	def OnPaint(self, evt):
		dc = wx.BufferedPaintDC(self)
		dc.SetTextForeground(wx.Colour(255, 0, 0))
		dc.SetTextBackground(wx.Colour(255, 255, 255))
		dc.SetBackgroundMode(wx.BRUSHSTYLE_SOLID)
		dc.SetFont(wx.Font(wx.Font(10, wx.FONTFAMILY_ROMAN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, faceName="Arial")))
		self.DrawBackground(dc)
		for bx, bmp in self.tiles.items():
			dc.DrawBitmap(bmp, bx[0], bx[1])
		for bx, bmp in self.bitmaps.items():
			dc.DrawBitmap(bmp, bx[0], bx[1])
		for bx, txt in self.text.items():
			dc.DrawText(txt, bx[0], bx[1])
		for bx, tinfo in self.trains.items():
			x = bx[0]
			y = bx[1]
			hilite = tinfo[5]
			misrouted = tinfo[6]
			ht = int(dc.GetTextExtent("0")[1]/2.0)

			if misrouted:
				dc.SetTextForeground(wx.Colour(236, 56, 255))
				dc.SetTextBackground(wx.Colour(236, 56, 255))
				txt = "  "
				dc.DrawText(txt, x, y)
				x += dc.GetTextExtent(txt)[0]

			if tinfo[2]:
				dc.SetTextForeground(wx.Colour(255, 255, 255))
				dc.SetTextBackground(wx.Colour(255, 0, 0))
				txt = "* "
				dc.DrawText(txt, x, y)
				x += dc.GetTextExtent(txt)[0]

			if tinfo[3] or tinfo[4]:
				dc.SetTextForeground(wx.Colour(255, 255, 0))
				dc.SetTextBackground(wx.Colour(0, 0, 0))
				if tinfo[3] and tinfo[4]:
					txt = "AR "
				elif tinfo[3]:
					txt = "A "
				else:
					txt=" R"
				dc.DrawText(txt, x, y)
				x += dc.GetTextExtent(txt)[0]

			dc.SetTextForeground(wx.Colour(255, 0, 0))
			dc.SetTextBackground(wx.Colour(255, 255, 255))
			dc.DrawText(tinfo[0]+" ", x, y)
			x += dc.GetTextExtent(tinfo[0])[0]+2

			dc.SetTextForeground(wx.Colour(255, 255, 255))
			dc.SetTextBackground(wx.Colour(255, 0, 0))
			dc.DrawText(tinfo[1], x, y)
			x += dc.GetTextExtent(tinfo[1])[0]

			if misrouted:
				dc.SetTextForeground(wx.Colour(236, 56, 255))
				dc.SetTextBackground(wx.Colour(236, 56, 255))
				txt = "  "
				dc.DrawText(txt, x, y)
				x += dc.GetTextExtent(txt)[0]

			if hilite:
				dc.SetPen(wx.Pen(wx.GREEN, width=10, style=wx.PENSTYLE_SOLID))
				dc.SetBrush(wx.Brush(wx.GREEN, wx.TRANSPARENT))
				dc.DrawCircle(bx[0] + int((x - bx[0]) / 2.0), y + ht, 50)

		if len(self.highlitedRoute) > 0 and self.hilitebmp is not None:
			for hx, hy in self.highlitedRoute:
				dc.DrawBitmap(self.hilitebmp, hx, hy)

		if self.showCTC:
			for bx, bmp in self.ctcbgbitmaps.items():
				dc.DrawBitmap(bmp, bx[0], bx[1])
			for bx, bmp in self.ctcfgbitmaps.items():
				dc.DrawBitmap(bmp, bx[0], bx[1])
			dc.SetTextForeground(wx.Colour(255, 255, 0))
			dc.SetTextBackground(wx.Colour(0, 0, 0))
			for bx, lblinfo  in self.ctclabels.items():
				txt, fnt = lblinfo
				dc.SetFont(fnt)
				dc.DrawText(txt, bx[0], bx[1])

		self.frame.drawCustom(dc)

