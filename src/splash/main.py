import wx
import os


versiondate = "18-Sep-2025"


class MainFrame(wx.Frame):
	def __init__(self):
		wx.Frame.__init__(self, None, style=wx.DEFAULT_FRAME_STYLE)
		self.SetTitle("PSRY Suite")
		self.Bind(wx.EVT_CLOSE, self.OnClose)
		
		textFont = wx.Font(wx.Font(12, wx.FONTFAMILY_ROMAN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, faceName="Arial"))
		textFontBold = wx.Font(wx.Font(12, wx.FONTFAMILY_ROMAN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, faceName="Arial"))
		largeFontBold = wx.Font(wx.Font(18, wx.FONTFAMILY_ROMAN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, faceName="Arial"))

		self.pngPSRY = wx.Image(os.path.join(os.getcwd(), "images", "PSLogo_large.png"), wx.BITMAP_TYPE_PNG).ConvertToBitmap()
		mask = wx.Mask(self.pngPSRY, wx.BLUE)
		self.pngPSRY.SetMask(mask)
		
		vsizer = wx.BoxSizer(wx.VERTICAL)
		vsizer.AddSpacer(20)
		
		st = wx.StaticText(self, wx.ID_ANY, "PSRY SUITE")
		st.SetFont(largeFontBold)
		vsizer.Add(st, 0, wx.ALIGN_CENTER_HORIZONTAL)
		vsizer.AddSpacer(10)
		
		self.SetSizer(vsizer)
		b = wx.StaticBitmap(self, wx.ID_ANY, self.pngPSRY)
		vsizer.Add(b, 0, wx.ALIGN_CENTER_HORIZONTAL)
		vsizer.AddSpacer(20)
		
		sta = wx.StaticText(self, wx.ID_ANY, "version:", size=(200, -1), style=wx.ALIGN_RIGHT)
		stb = wx.StaticText(self, wx.ID_ANY, versiondate, size=(400, -1))
		sta.SetFont(textFont)
		stb.SetFont(textFontBold)
		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.Add(sta)
		hsz.AddSpacer(10)
		hsz.Add(stb)		
		vsizer.Add(hsz)
		vsizer.AddSpacer(20)
		
		sta = wx.StaticText(self, wx.ID_ANY, "started development:", size=(200, -1), style=wx.ALIGN_RIGHT)
		stb = wx.StaticText(self, wx.ID_ANY, "14-January-2023", size=(400, -1))
		sta.SetFont(textFont)
		stb.SetFont(textFontBold)
		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.Add(sta)
		hsz.AddSpacer(10)
		hsz.Add(stb)		
		vsizer.Add(hsz)
		vsizer.AddSpacer(20)
		
		sta = wx.StaticText(self, wx.ID_ANY, "github:", size=(200, -1), style=wx.ALIGN_RIGHT)
		stb = wx.StaticText(self, wx.ID_ANY, "https://github.com/jbernardis/psrysuite", size=(400, -1))
		sta.SetFont(textFont)
		stb.SetFont(textFontBold)
		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.Add(sta)
		hsz.AddSpacer(10)
		hsz.Add(stb)		
		vsizer.Add(hsz)
		vsizer.AddSpacer(20)
		
		sta = wx.StaticText(self, wx.ID_ANY, "written by:", size=(200, -1), style=wx.ALIGN_RIGHT)
		stb = wx.StaticText(self, wx.ID_ANY, "Jeff Bernardis", size=(400, -1))
		sta.SetFont(textFont)
		stb.SetFont(textFontBold)
		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.Add(sta)
		hsz.AddSpacer(10)
		hsz.Add(stb)		
		vsizer.Add(hsz)
		vsizer.AddSpacer(20)

		sta = wx.StaticText(self, wx.ID_ANY, "based on:", size=(200, -1), style=wx.ALIGN_RIGHT)
		stb = wx.StaticText(self, wx.ID_ANY, "Dispatcher 1 written by Geoff Green", size=(400, -1))
		sta.SetFont(textFont)
		stb.SetFont(textFontBold)
		hsz = wx.BoxSizer(wx.HORIZONTAL)
		hsz.Add(sta)
		hsz.AddSpacer(10)
		hsz.Add(stb)		
		vsizer.Add(hsz)
		vsizer.AddSpacer(20)

		self.Layout()
		self.Fit()
		
		self.Bind(wx.EVT_TIMER, self.OnTicker)
		self.ticker = wx.Timer(self)
		self.ticker.Start(5000)
		
	def OnTicker(self, _):
		self.Destroy()
		
	def OnClose(self, _):
		self.Destroy()
		

class App(wx.App):
	def OnInit(self):
		frame = MainFrame()
		frame.CenterOnScreen()
		frame.Show()
		return True


app = App(False)
app.MainLoop()
