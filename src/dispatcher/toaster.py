import wx

TB_DEFAULT_STYLE = 0x2008002
TB_CAPTION = 0x22009806

ht = 36
SIZE = 1000


class Toaster(wx.Frame):
	def __init__(self, title="", size=(SIZE, ht), pos=(100,100), style=TB_DEFAULT_STYLE):
		self.size = size
		wx.Frame.__init__(self, None, -1, title, size=size, pos=pos, style=style | wx.CLIP_CHILDREN | wx.STAY_ON_TOP)

		panel = wx.Panel(self, wx.ID_ANY, size=size, pos=(0,0))
		lbsize = self.GetClientSize()
		self.lb = wx.ListBox(panel, wx.ID_ANY, (0, 0), lbsize, [], wx.LB_SINGLE)
		self.showTime = 4000
		self.Timers = []
		self.lct = 0
		self.Hide()

	def SetFont(self, font):
		self.lb.SetFont(font)
	
	def SetBackgroundColour(self, color):
		self.lb.SetBackgroundColour(color)
	
	def SetTextColour(self, color):
		self.lb.SetForegroundColour(color)
		
	def SetOffsets(self, xoffset, yoffset):
		w, h = wx.GetDisplaySize()
		
		px = (w-self.size[0])/2+xoffset
		py = (h-self.size[1])/2+yoffset

		self.SetPosition(wx.Point(int(px), int(py)))
			
	def SetShowTime(self, t):
		self.showTime = t
		
	def checkShow(self):
		if len(self.Timers) >= 1:
			self.Show()
		
	def Append(self, v):
		self.lb.Append(v)
		timer = wx.Timer(self)
		self.Bind(wx.EVT_TIMER, self.onTimer, timer)  
		timer.Start(self.showTime, True) 

		self.Timers.append(timer)
		if len(self.Timers) >= 1:
			self.Show()
		self.ReSize()

	def ReSize(self):
		n = self.lb.GetCount()
		if n >5:
			n = 5
		if n < 1:
			n = 1
		self.SetSize((SIZE, ht*n))
		lbsize = self.GetClientSize()
		self.lb.SetSize(lbsize)

	def onTimer(self, evt):
		delx = []
		for tx in range(len(self.Timers)):
			if not self.Timers[tx].IsRunning():
				delx.append(tx)

		if len(delx) > 0:
			for dx in reversed(delx):
				del self.Timers[dx]
				self.lb.Delete(dx)
			self.ReSize()

		if len(self.Timers) == 0:
			self.Hide()
		
	def Close(self):
		for t in self.Timers:
			try:
				t.Stop()
			except:
				pass
		self.Destroy()
