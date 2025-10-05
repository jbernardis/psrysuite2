from PIL import Image

def wx2PIL (bitmap):
	size = tuple(bitmap.GetSize())
	try:
		buf = size[0]*size[1]*3*"\x00"
		bitmap.CopyToBuffer(buf)
	except:
		del buf
		buf = bitmap.ConvertToImage().GetData()
	return Image.frombuffer("RGB", size, buf, "raw", "RGB", 0, 1)

class TileCanvas:
	def __init__(self, fn):
		self.baseImage = Image.open(fn).convert("RGB")
		self.tilew = 16
		self.tileh = 16

		self.tilesw = int(self.baseImage.size[0] / self.tilew)
		self.tilesh = int(self.baseImage.size[1] / self.tileh)

		self.canvh = self.tileh+2
		self.canvw = self.tilew+2

		self.BuildCanvas()
		
	def BuildCanvas(self):
		self.canvas = Image.new('RGB',(self.tilesw*self.canvw,self.tilesh*self.canvh),"#404040FF")

		for row in range(self.tilesh):
			for col in range(self.tilesw):
				t = self.baseImage.crop(self.baseImageBox(col, row))
				self.canvas.paste(t, self.canvasBoxForTile(col, row))
				
	def baseImageBox(self, x, y):
		x1 = x * self.tilew
		x2 = x1 + self.tilew
		y1 = y * self.tileh
		y2 = y1 + self.tileh
		return (x1, y1, x2, y2)

	def canvasBoxForTile(self, x, y):
		x1 = x * self.canvw + 1
		x2 = x1 + self.tilew
		y1 = y * self.canvh + 1
		y2 = y1 + self.tileh
		return (x1, y1, x2, y2)

	def canvasBoxForCursor(self, x, y):
		x1 = x * self.canvw
		x2 = x1 + self.canvw
		y1 = y * self.canvh
		y2 = y1 + self.canvh
		return (x1, y1, x2, y2)
	
	def tileFromCanvas(self, x, y):
		nx = int(x/self.canvw)
		ny = int(y/self.canvh)
		return (nx, ny)
	
	def GetCanvas(self):
		return self.canvas
	
	def ApplyTiles(self, tlist, fn):
		for tx, ty, _, tile in tlist:
			self.baseImage.paste(tile, self.baseImageBox(tx, ty))
		self.BuildCanvas()
		
		self.baseImage.save(fn)
