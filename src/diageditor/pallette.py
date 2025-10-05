import wx
import os
from PIL import Image as pilimg

files = {
	
	"frame":			["frame.bmp", "Frame for turnout"],
	"empty":			["empty.bmp", "Empty tile"],
	"cross":			["cross.bmp", "Crossover tile"],
	"outline":			["outline.bmp", "Track outline"],
	"button":			["button.bmp", "Routing button/Indicator"],

	"horizontal":		["horizontal.bmp", "Horizontal straight track"],
	"vertical":			["vertical.bmp", "Vertical straight track"],
	"diagl":			["diagl.bmp", "Diagonal left straight track"],
	"diagr":			["diagr.bmp", "Diagonal right straight track"],

	"turnleftdown":		["turnleftdown.bmp", "Turn left down"],
	"turnleftleft": 	["turnleftleft.bmp", "Turn left left"],
	"turnleftright":	["turnleftright.bmp", "Turn left right"],
	"turnleftup": 		["turnleftup.bmp", "Turn left up"],
	"turnrightdown":	["turnrightdown.bmp", "Turn right down"],
	"turnrightleft":	["turnrightleft.bmp", "Turn right left"],
	"turnrightright":	["turnrightright.bmp", "Turn right right"],
	"turnrightup":		["turnrightup.bmp", "Turn right up"],

	"eobdown":			["eobdown.bmp", "End of block down"],
	"eobleft":			["eobleft.bmp", "End of block left"],
	"eobleftdown":		["eobleftdown.bmp", "End of block left down"],
	"eobleftleft":		["eobleftleft.bmp", "End of block left left"],
	"eobleftright":		["eobleftright.bmp", "End of block left right"],
	"eobleftup":		["eobleftup.bmp", "End of block left up"],
	"eobright":			["eobright.bmp", "End of block right"],
	"eobrightdown":		["eobrightdown.bmp", "End of block right down"],
	"eobrightleft":		["eobrightleft.bmp", "End of block right left"],
	"eobrightright":	["eobrightright.bmp", "End of block right right"],
	"eobrightup":		["eobrightup.bmp", "End of block right up"],
	"eobup":			["eobup.bmp", "End of block up"],

	"sigleft":			["sigleft.bmp", "Signal Left"],
	"sigleftlong":		["sigleftlong.bmp", "Signal left - long"],
	"sigright":			["sigright.bmp", "Signal right"],		
	"sigrightlong":		["sigrightlong.bmp", "Signal right - long"],

	"downunlocked":		["downunlocked.bmp", "Handswitch lock - down"],
	"upunlocked":		["upunlocked.bmp", "Handswitch lock - up"]
}

pmap = {
	"misc": ["empty", "frame", "button"],
	"straight": ["horizontal", "vertical", "diagl", "diagr", "cross", "outline"],
	"turns": ["turnleftdown", "turnleftleft", "turnleftright", "turnleftup", "turnrightdown", "turnrightleft", "turnrightright", "turnrightup"],
	"eob": ["eobdown", "eobleft", "eobleftdown", "eobleftleft", "eobleftright", "eobleftup", "eobright", "eobrightdown", "eobrightleft", "eobrightright", "eobrightup", "eobup"],
	"signals": ["sigleft", "sigleftlong", "sigright", "sigrightlong"],
	"locks": ["downunlocked", "upunlocked"]
}

groups = ["misc", "straight", "turns", "eob", "signals", "locks"]

BASEBUTTONID = 1000

class Pallette(wx.Dialog):
	def __init__(self, parent, tileselector, cmdFolder):
		wx.Dialog.__init__(self, parent, wx.ID_ANY, "Tile Pallette", style=wx.CAPTION | wx.STAY_ON_TOP | wx.DIALOG_NO_PARENT)
		self.parent = parent
		self.tileSelector = tileselector
		self.Bind(wx.EVT_CLOSE, self.OnClose)
		self.pallette = []
		vsz = wx.BoxSizer(wx.VERTICAL)
		vsz.AddSpacer(10)
		buttonId = BASEBUTTONID
		self.buttons = []
		self.buttonIds = []
		self.selectedColor = wx.Colour(255, 0, 0)
		self.color = wx.Colour(128, 128, 128)
		for grp in groups:
			hsz = wx.BoxSizer(wx.HORIZONTAL)
			hsz.AddSpacer(10)
			for tname in pmap[grp]:
				tfp = os.path.join(cmdFolder, "tiles", files[tname][0])
				p = wx.Image(tfp, wx.BITMAP_TYPE_BMP).ConvertToBitmap()			
				pil = pilimg.open(tfp).convert("RGB")
				self.pallette.append([p, pil])
				
				b = wx.Button(self, buttonId, "", size=(40, 40))
				b.SetBackgroundColour(self.color)
				b.SetBitmap(p)
				b.SetToolTip(files[tname][1])
				self.Bind(wx.EVT_BUTTON, self.OnTileSelect, b)
				self.buttonIds.append(tname)
				self.buttons.append(b)
				buttonId += 1
				hsz.Add(b)
			hsz.AddSpacer(10)
			vsz.Add(hsz)
			vsz.AddSpacer(10)
				
			
		self.SetSizer(vsz)
		self.Layout()
		self.Fit()
		
		x, y = self.GetSize()
		dx, dy = wx.DisplaySize()
		self.SetPosition((dx-x-100, dy-y-100))
		
		self.SelectPalletteItem(0)
		
	def OnTileSelect(self, evt):
		o = evt.GetEventObject()
		bid = o.GetId()
		idx = bid - BASEBUTTONID
		self.SelectPalletteItem(idx)
		
	def SelectPalletteItem(self, idx):
		for i in range(len(self.buttons)):
			c = self.selectedColor if i == idx else self.color
			self.buttons[i].SetBackgroundColour(c)
			
		self.tileSelector(self.pallette[idx])


	def OnClose(self, evt):
		return