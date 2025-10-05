import wx
import re

sigLeverMap = {
	"C2"   : { "left": [2, 4], "center": [2, 5], "right": [2, 6], "node": "Cliff"},
	"C4"   : { "left": [2, 7], "center": [3, 0], "right": [3, 1], "node": "Cliff"},
	"C6"   : { "left": [3, 2], "center": [3, 3], "right": [3, 4], "node": "Cliff"},
	"C8"   : { "left": [3, 5], "center": [3, 6], "right": [3, 7], "node": "Cliff"},
	"C10"  : { "left": [4, 0], "center": [4, 1], "right": [4, 2], "node": "Cliff"},
	"C12"  : { "left": [4, 3], "center": [4, 4], "right": [4, 5], "node": "Cliff"},
	"C14"  : { "left": [4, 6], "center": [4, 7], "right": [7, 1], "node": "Cliff"},
	"C18"  : { "left": [5, 2], "center": [5, 3], "right": [5, 4], "node": "Cliff"},
	"C22"  : { "left": [5, 5], "center": [5, 6], "right": [5, 7], "node": "Cliff"},
	"C24"  : { "left": [6, 0], "center": [6, 1], "right": [6, 2], "node": "Cliff"},
	
	
	"N14"  : { "left": [3, 6], "center": [3, 5], "right": [3, 4], "node": "Nassau W"},
	"N16"  : { "left": [4, 1], "center": [4, 0], "right": [3, 7], "node": "Nassau W"},
	"N18"  : { "left": [4, 4], "center": [4, 3], "right": [4, 2], "node": "Nassau W"},
	"N20"  : { "left": [4, 7], "center": [4, 6], "right": [4, 5], "node": "Nassau W"},
	"N24"  : { "left": [5, 2], "center": [5, 1], "right": [5, 0], "node": "Nassau W"},
	"N26"  : { "left": [5, 5], "center": [5, 4], "right": [5, 3], "node": "Nassau W"},
	"N28"  : { "left": [6, 0], "center": [5, 7], "right": [5, 6], "node": "Nassau W"},

	
	"PA10" : { "left": [6, 1], "center": [6, 0], "right": [5, 7], "node": "Port A"},
	"PA12" : { "left": [6, 4], "center": [6, 3], "right": [6, 2], "node": "Port A"},
	"PA32" : { "left": [6, 7], "center": [6, 6], "right": [6, 5], "node": "Port A"},
	"PA34" : { "left": [7, 2], "center": [7, 1], "right": [7, 0], "node": "Port A"},
	"PA4"  : { "left": [5, 0], "center": [4, 7], "right": [4, 6], "node": "Port A"},
	"PA6"  : { "left": [5, 3], "center": [5, 2], "right": [5, 1], "node": "Port A"},
	"PA8"  : { "left": [5, 6], "center": [5, 5], "right": [5, 4], "node": "Port A"},
	
	"PB12" : { "left": [4, 4], "center": [4, 5], "right": [4, 6], "node": "Port B"},
	"PB14" : { "left": [4, 7], "center": [5, 0], "right": [5, 1], "node": "Port B"},
	"PB2"  : { "left": [3, 5], "center": [3, 6], "right": [3, 7], "node": "Port B"},
	"PB4"  : { "left": [4, 0], "center": [4, 1], "right": [4, 2], "node": "Port B"},
	
	
	"Y2"   : { "left": [0, 2], "center": [0, 3], "right": [0, 4], "node": "Yard"},
	"Y4"   : { "left": [0, 5], "center": [0, 6], "right": [0, 7], "node": "Yard"},
	"Y8"   : { "left": [1, 0], "center": [1, 1], "right": [1, 2], "node": "Yard"},
	"Y10"  : { "left": [1, 3], "center": [1, 4], "right": [1, 5], "node": "Yard"},
	"Y22"  : { "left": [1, 6], "center": [1, 7], "right": [2, 0], "node": "Yard"},
	"Y24"  : { "left": None,   "center": [2, 2], "right": [2, 1], "node": "Yard"},
	"Y26"  : { "left": [2, 3], "center": [2, 4], "right": [2, 5], "node": "Yard"},
	"Y34"  : { "left": [2, 6], "center": [2, 7], "right": [3, 0], "node": "Yard"},
}


class SigLever:
	def __init__(self, name):
		if name in sigLeverMap:
			self.name = name
			self.map = sigLeverMap[name]
		else:
			self.name = None
			self.map = None
			
	def IsValid(self):
		return self.name is not None
			
	def GetData(self):
		if self.name is None:
			return None
		
		return self.map
		
			
class SigLeverShowDlg(wx.Dialog):
	def __init__(self, parent, closer):
		wx.Dialog.__init__(self, parent, wx.ID_ANY, "Signal Levers")
		self.Bind(wx.EVT_CLOSE, self.OnClose)
		self.closer = closer
		self.parent = parent

		font = wx.Font(wx.Font(12, wx.FONTFAMILY_TELETYPE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, faceName="Monospace"))
		
		vsz = wx.BoxSizer(wx.VERTICAL)	   
		vsz.AddSpacer(20)
		
		self.slList = wx.TextCtrl(self, wx.ID_ANY, "", style=wx.TE_MULTILINE + wx.TE_READONLY, size=(180, 380))	
		self.slList.SetFont(font)	
		vsz.Add(self.slList)
		
		vsz.AddSpacer(20)
		
		self.RefreshLvrs()
	
		self.SetSizer(vsz)
		self.Layout()
		self.Fit()
		
	def formatSigLvr(self, data):
		dl = 0 if data[0] is None else data[0]
		dc = 0 if data[1] is None else data[1]
		dr = 0 if data[2] is None else data[2]
		
		callon = " C" if dc != 0 else "  "
		
		if dl != 0 and dr == 0:
			return "L  " + callon
		elif dl == 0 and dr != 0:
			return "  R" + callon
		elif dl == 0 and dr == 0:
			return " N " + callon
		else:
			return "???" * callon
		
	def BuildLeverKey(self, slnm):
		z = re.match("([A-Za-z]+)([0-9]+)", slnm)
		if z is None or len(z.groups()) != 2:
			return slnm
		
		nm, nbr = z.groups()
		return "%s%03d" % (nm, int(nbr))

	def RefreshLvrs(self):
		sl = self.parent.rrServer.Get("signallevers", {})
		
		slnms = sorted(list(sl.keys()), key=self.BuildLeverKey)
		items = []
		currentNode = slnms[0][0]
		for slnm in slnms:
			sldata = sl[slnm]
			if slnm[0] != currentNode:
				items.append("")
				currentNode = slnm[0]
			items.append("%-10.10s %s" % (slnm, self.formatSigLvr(sldata)))
			
		self.slList.Clear()
		self.slList.AppendText("\n".join(items))
	
	def OnClose(self, _):
		self.closer()


