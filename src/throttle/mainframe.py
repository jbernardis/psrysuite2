import os
import wx
import wx.lib.agw.knobctrl as KC
import wx.lib.gizmos as gizmos

from dispatcher.settings import Settings
from throttle.dccserver import DCCServer
from throttle.rrserver import RRServer
from throttle.dccremote import DCCRemote
from throttle.enterlocodlg import EnterLocoDlg

BTNDIM = (32, 32)
BTNDIM2 = (48, 48)
BTNDIM3 = (144, 48)

class MainFrame(wx.Frame):
	def __init__(self):
		wx.Frame.__init__(self, None, style=wx.DEFAULT_FRAME_STYLE | wx.STAY_ON_TOP)
		self.SetTitle("PSRY Throttle")
		self.Bind(wx.EVT_CLOSE, self.OnClose)
		
		icon = wx.Icon()
		icon.CopyFromBitmap(wx.Bitmap(os.path.join(os.getcwd(), "icons", "throttle.ico"), wx.BITMAP_TYPE_ANY))
		self.SetIcon(icon)
	
		self.selectedLoco = None
		self.selectedLid = 0
		
		self.loadImages(os.path.join(os.getcwd(), "images"))
		self.settings = Settings()

		font = wx.Font(wx.Font(24, wx.FONTFAMILY_TELETYPE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, faceName="Monospace"))
		
		self.stLoco = wx.StaticText(self, wx.ID_ANY, "0000")
		self.stLoco.SetFont(font)
		self.stDirection = wx.StaticText(self, wx.ID_ANY, "FWD")
		self.stDirection.SetFont(font)
		
		self.ledSpeed = gizmos.LEDNumberCtrl(self, wx.ID_ANY, size=(90, 50))
		self.ledSpeed.SetValue("0")
		self.ledSpeed.SetAlignment(gizmos.LED_ALIGN_RIGHT)
		self.ledSpeed.SetDrawFaded(False)
		self.ledSpeed.SetForegroundColour('yellow')
		
		self.bEStop = wx.BitmapButton(self, wx.ID_ANY, self.pngEStop, size=BTNDIM2)
		self.Bind(wx.EVT_BUTTON, self.OnBEStop, self.bEStop)
		
		self.bUp = wx.BitmapButton(self, wx.ID_ANY, self.pngUp, size=BTNDIM)
		self.Bind(wx.EVT_BUTTON, self.OnBUp, self.bUp)
		self.bDown = wx.BitmapButton(self, wx.ID_ANY, self.pngDown, size=BTNDIM)
		self.Bind(wx.EVT_BUTTON, self.OnBDown, self.bDown)
		
		self.bUpFast = wx.BitmapButton(self, wx.ID_ANY, self.pngUpFast, size=BTNDIM)
		self.Bind(wx.EVT_BUTTON, self.OnBUpFast, self.bUpFast)
		self.bDownFast = wx.BitmapButton(self, wx.ID_ANY, self.pngDownFast, size=BTNDIM)
		self.Bind(wx.EVT_BUTTON, self.OnBDownFast, self.bDownFast)
	
		self.knbSpeed = KC.KnobCtrl(self, wx.ID_ANY, size=(150, 150))
		self.knbSpeed.SetTags(range(0, 129, 16))
		self.knbSpeed.SetAngularRange(-45, 225)
		self.knbSpeed.SetValue(0)
		self.Bind(KC.EVT_KC_ANGLE_CHANGED, self.OnKnbSpeedChanged, self.knbSpeed)
		
		self.bDirection = wx.BitmapButton(self, wx.ID_ANY, self.pngDirection, size=BTNDIM3)
		self.Bind(wx.EVT_BUTTON, self.OnBDirection, self.bDirection)
		
		self.bLight = wx.BitmapButton(self, wx.ID_ANY, self.pngLight, size=BTNDIM2)
		self.Bind(wx.EVT_BUTTON, self.OnBLight, self.bLight)
		self.bHorn = wx.BitmapButton(self, wx.ID_ANY, self.pngHorn, size=BTNDIM2)
		self.Bind(wx.EVT_BUTTON, self.OnBHorn, self.bHorn)
		self.bBell = wx.BitmapButton(self, wx.ID_ANY, self.pngBell, size=BTNDIM2)
		self.Bind(wx.EVT_BUTTON, self.OnBBell, self.bBell)
		
		self.bSelect = wx.Button(self, wx.ID_ANY, "SELECT LOCO", size=BTNDIM3)
		self.Bind(wx.EVT_BUTTON, self.OnBSelect, self.bSelect)
		
		self.cbStayOnTop = wx.CheckBox(self, wx.ID_ANY, "Stay on Top")
		self.cbStayOnTop.SetValue(True)
		self.Bind(wx.EVT_CHECKBOX, self.ObCbStayOnTop, self.cbStayOnTop)
	
		vszr = wx.BoxSizer(wx.VERTICAL)
		vszr.AddSpacer(20)
		
		hszr = wx.BoxSizer(wx.HORIZONTAL)
		hszr.Add(self.stLoco)
		hszr.AddSpacer(20)
		hszr.Add(self.stDirection)
		vszr.Add(hszr, 0, wx.ALIGN_CENTER_HORIZONTAL)
		
		vszr.AddSpacer(20)
		hszr = wx.BoxSizer(wx.HORIZONTAL)
		hszr.Add(self.ledSpeed)
		hszr.AddSpacer(20)
		hszr.Add(self.bEStop)
		vszr.Add(hszr, 0, wx.ALIGN_CENTER_HORIZONTAL)
		vszr.AddSpacer(20)
		
		hszr = wx.BoxSizer(wx.HORIZONTAL)
		
		btnszr = wx.BoxSizer(wx.VERTICAL)
		btnszr.Add(self.bUp)
		btnszr.AddSpacer(30)
		btnszr.Add(self.bDown)
		hszr.Add(btnszr, 0, wx.ALIGN_CENTER_VERTICAL)
		
		hszr.AddSpacer(5)		
		hszr.Add(self.knbSpeed)		
		hszr.AddSpacer(5)
		
		btnszr = wx.BoxSizer(wx.VERTICAL)
		btnszr.Add(self.bUpFast)
		btnszr.AddSpacer(30)
		btnszr.Add(self.bDownFast)
		hszr.Add(btnszr, 0, wx.ALIGN_CENTER_VERTICAL)

		vszr.Add(hszr, 0, wx.ALIGN_CENTER_HORIZONTAL)
		vszr.AddSpacer(20)
		
		vszr.Add(self.bDirection, 0, wx.ALIGN_CENTER_HORIZONTAL)
		
		vszr.AddSpacer(20)
		
		btnszr = wx.BoxSizer(wx.HORIZONTAL)
		btnszr.Add(self.bLight)
		btnszr.AddSpacer(30)
		btnszr.Add(self.bHorn)
		btnszr.AddSpacer(30)
		btnszr.Add(self.bBell)
		
		vszr.Add(btnszr, 0, wx.ALIGN_CENTER_HORIZONTAL)

		vszr.AddSpacer(20)
		
		vszr.Add(self.bSelect, 0, wx.ALIGN_CENTER_HORIZONTAL)
		
		vszr.AddSpacer(10)
		
		vszr.Add(self.cbStayOnTop, 0, wx.ALIGN_CENTER_HORIZONTAL)
		
		vszr.AddSpacer(20)

		hszr = wx.BoxSizer(wx.HORIZONTAL)
		hszr.AddSpacer(10)
		hszr.Add(vszr)
		hszr.AddSpacer(10)
		
		self.direction = "F"
		self.bell = False
		self.horn = False
		self.light = False
		
		self.SetSizer(hszr)
		self.Fit()
		self.Layout()
		
		self.EnableControls()
		
		self.dccServer = DCCServer()
		self.dccServer.SetServerAddress(self.settings.ipaddr, self.settings.dccserverport)
		self.dccRemote = DCCRemote(self.dccServer)
		self.rrServer = RRServer()
		self.rrServer.SetServerAddress(self.settings.ipaddr, self.settings.serverport)
		
		# retrieve the loco information from the server
		locos = self.rrServer.Get("getlocos", {})
		if locos is None:
			print("Unable to retrieve locos")
			locos = {}
		self.locoList = sorted(list(locos.keys()), key=self.BuildLocoKey)

	def ObCbStayOnTop(self, _):
		flag = self.cbStayOnTop.GetValue()		

		st = self.GetWindowStyle()
		if flag:
			st |= wx.STAY_ON_TOP
		else:
			st &= ~wx.STAY_ON_TOP
			
		self.SetWindowStyle(st)
		
	def BuildLocoKey(self, lid):
		return int(lid)
		
	def EnableControls(self):
		flag = self.selectedLoco is not None
		
		self.knbSpeed.Enable(flag)
		self.bEStop.Enable(flag)
		self.bUp.Enable(flag)
		self.bUpFast.Enable(flag)
		self.bDown.Enable(flag)
		self.bDownFast.Enable(flag)
		self.bLight.Enable(flag)
		self.bHorn.Enable(flag)
		self.bBell.Enable(flag)
		self.bDirection.Enable(flag)
		
	def loadImages(self, imgFolder):
		png = wx.Image(os.path.join(imgFolder, "up1.png"), wx.BITMAP_TYPE_PNG).ConvertToBitmap()
		mask = wx.Mask(png, wx.BLUE)
		png.SetMask(mask)
		self.pngUp = png

		png = wx.Image(os.path.join(imgFolder, "down1.png"), wx.BITMAP_TYPE_PNG).ConvertToBitmap()
		mask = wx.Mask(png, wx.BLUE)
		png.SetMask(mask)
		self.pngDown = png

		png = wx.Image(os.path.join(imgFolder, "up2.png"), wx.BITMAP_TYPE_PNG).ConvertToBitmap()
		mask = wx.Mask(png, wx.BLUE)
		png.SetMask(mask)
		self.pngUpFast = png

		png = wx.Image(os.path.join(imgFolder, "down2.png"), wx.BITMAP_TYPE_PNG).ConvertToBitmap()
		mask = wx.Mask(png, wx.BLUE)
		png.SetMask(mask)
		self.pngDownFast = png

		png = wx.Image(os.path.join(imgFolder, "headlight.png"), wx.BITMAP_TYPE_PNG).ConvertToBitmap()
		mask = wx.Mask(png, wx.BLUE)
		png.SetMask(mask)
		self.pngLight = png

		png = wx.Image(os.path.join(imgFolder, "headlight_on.png"), wx.BITMAP_TYPE_PNG).ConvertToBitmap()
		mask = wx.Mask(png, wx.BLUE)
		png.SetMask(mask)
		self.pngLightOn = png

		png = wx.Image(os.path.join(imgFolder, "horn.png"), wx.BITMAP_TYPE_PNG).ConvertToBitmap()
		mask = wx.Mask(png, wx.BLUE)
		png.SetMask(mask)
		self.pngHorn = png

		png = wx.Image(os.path.join(imgFolder, "horn_on.png"), wx.BITMAP_TYPE_PNG).ConvertToBitmap()
		mask = wx.Mask(png, wx.BLUE)
		png.SetMask(mask)
		self.pngHornOn = png

		png = wx.Image(os.path.join(imgFolder, "bell.png"), wx.BITMAP_TYPE_PNG).ConvertToBitmap()
		mask = wx.Mask(png, wx.BLUE)
		png.SetMask(mask)
		self.pngBell = png

		png = wx.Image(os.path.join(imgFolder, "bell_on.png"), wx.BITMAP_TYPE_PNG).ConvertToBitmap()
		mask = wx.Mask(png, wx.BLUE)
		png.SetMask(mask)
		self.pngBellOn = png

		png = wx.Image(os.path.join(imgFolder, "direction.png"), wx.BITMAP_TYPE_PNG).ConvertToBitmap()
		mask = wx.Mask(png, wx.BLUE)
		png.SetMask(mask)
		self.pngDirection = png

		png = wx.Image(os.path.join(imgFolder, "stop.png"), wx.BITMAP_TYPE_PNG).ConvertToBitmap()
		mask = wx.Mask(png, wx.BLUE)
		png.SetMask(mask)
		self.pngEStop = png


	def UpdateSpeed(self, speed):
		self.knbSpeed.SetValue(speed)
		self.ledSpeed.SetValue("%d" % speed)
		self.dccRemote.SetSpeed(speed)
		
	def ShowLight(self):
		self.bLight.SetBitmap(self.pngLightOn if self.light else self.pngLight)
		
	def ShowHorn(self):
		self.bHorn.SetBitmap(self.pngHornOn if self.horn else self.pngHorn)
		
	def ShowBell(self):
		self.bBell.SetBitmap(self.pngBellOn if self.bell else self.pngBell)
		
	def ShowDirection(self):
		self.stDirection.SetLabel("FWD" if self.direction == "F" else "REV")
		
	def OnKnbSpeedChanged(self, event):
		speed = event.GetValue()
		self.UpdateSpeed(speed)
		
	def OnBEStop(self, _):
		self.UpdateSpeed(0)
		
	def OnBUp(self, _):
		speed = self.knbSpeed.GetValue() + 1
		if speed > 128:
			speed = 128
		self.UpdateSpeed(speed)
		
	def OnBDown(self, _):
		speed = self.knbSpeed.GetValue() - 1
		if speed < 0:
			speed = 0
		self.UpdateSpeed(speed)
		
	def OnBUpFast(self, _):
		speed = self.knbSpeed.GetValue() + 10
		if speed > 128:
			speed = 128
		self.UpdateSpeed(speed)
		
	def OnBDownFast(self, _):
		speed = self.knbSpeed.GetValue() - 10
		if speed < 0:
			speed = 0
		self.UpdateSpeed(speed)
		
	def OnBLight(self, _):
		self.light = not self.light
		self.ShowLight()
		self.dccRemote.SetFunction(headlight=self.light)
		
	def OnBHorn(self, _):
		self.horn = not self.horn
		self.ShowHorn()
		self.dccRemote.SetFunction(horn=self.horn)
		
	def OnBBell(self, _):
		self.bell = not self.bell
		self.ShowBell()
		self.dccRemote.SetFunction(bell=self.bell)
		
	def OnBDirection(self, _):
		self.direction = "F" if self.direction == "R" else "R"
		self.ShowDirection()
		self.dccRemote.SetDirection(self.direction)
		
	def OnBSelect(self, _):
		dlg = EnterLocoDlg(self, self.locoList)
		rc = dlg.ShowModal()
		if rc == wx.ID_OK:
			nlid = dlg.GetResults()
			
		dlg.Destroy()
		if rc != wx.ID_OK:
			return
		try:
			lid = int(nlid)
		except ValueError:
			return 
		
		if lid == 0:
			self.selectedLid = 0
			self.selectedLoco = None
		else:
			self.selectedLid = lid
			self.selectedLoco = self.dccRemote.SelectLoco(lid, True)
		
		self.EnableControls()
		self.stLoco.SetLabel("%4d" % lid)
		if self.selectedLoco:
			speed = self.selectedLoco.GetSpeed()
			self.knbSpeed.SetValue(speed)
			self.ledSpeed.SetValue("%d" % speed)
			self.light = self.selectedLoco.GetHeadlight()
			self.horn = self.selectedLoco.GetHorn()
			self.bell = self.selectedLoco.GetBell()
			self.direction = self.selectedLoco.GetDirection()
		else:
			self.knbSpeed.SetValue(0)
			self.ledSpeed.SetValue("%0")
			self.light = False
			self.horn = False
			self.bell = False
			self.direction = "F"
			
		self.ShowLight()
		self.ShowHorn()
		self.ShowBell()
		self.ShowDirection()
	
	def OnClose(self, _):
		self.doExit()
		
	def doExit(self):
		self.Destroy()
		
