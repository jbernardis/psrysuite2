'''
Created on May 17, 2011

@author: jbernard
'''

class InvalidKeyword(Exception):
	def __init__(self, message):
		self.message = message
		
	def __str__(self):
		return repr(self.message)

class InvalidValue(Exception):
	def __init__(self, message):
		self.message = message
		
	def __str__(self):
		return repr(self.message)

coreopts = ('class', 'dir', 'id', 'lang', 'onclick', 'ondblclick', 'onkeydown', 'onkeypress', 
		   'onkeyup', 'onmousedown', 'onmousemove', 'onmouseout', 'onmouseover', 'onmouseup', 'style', 'title')

# use a lambda to define RGB
rgb = lambda r, g, b: "#%02x%02x%02x" % (r, g, b) 

class StyleElement:
	def __init__(self, selector, props):
		self.sel = selector
		self.props = props.copy()
		
	def __str__(self):
		res = "%s {" % self.sel
		for k in self.props:
			res += " %s : %s;" % (k, self.props[k])
		res += "}\n"
		return res
	
class StyleSheet:
	def __init__(self):
		self.elements = []
		
	def addElement(self, sel, props):
		self.elements.append(StyleElement(sel, props))
		
	def __str__(self):
		res = ""
		for e in self.elements:
			res += str(e)
			
		return res

class Color:
	Red = rgb(255, 0, 0)
	LightRed = rgb(249, 199, 194)
	DarkRed = rgb(237, 113, 122)
	
	Green = rgb(0, 255, 0)
	LightGreen = rgb(190, 223, 196)
	DarkGreen = rgb(0, 173, 99)
	
	Blue = rgb(0, 0, 255)
	LightBlue = rgb(191, 226, 249)
	DarkBlue = rgb(0, 174, 237)
	
	Yellow = rgb(250, 245, 25)	
	LightYellow = rgb(254, 247, 110)
	
	Orange = rgb(241, 166, 41)
	LightOrange = rgb(253, 226, 184)
	DarkOrange = rgb(243, 176, 68)

	@classmethod   
	def RGB(cls, r, g, b):
		if (r < 0 or r > 255): raise InvalidValue("Value for red ("+str(r)+")out of bounds - must be 0-255")
		if (g < 0 or g > 255): raise InvalidValue("Value for green ("+str(g)+")out of bounds - must be 0-255")
		if (b < 0 or b > 255): raise InvalidValue("Value for blue ("+str(b)+")out of bounds - must be 0-255")
		return rgb(r, g, b)

def nbsp(count=1):
	return count * "&nbsp;"	

def element (elname, vals, opts, allowed):
	options = ''
	for k in opts:
		if not k in allowed:
			msg = '"' + k + '" unexpected, must be one of ' + ', '.join(['"' + x + '"' for x in allowed])
			raise InvalidKeyword(msg)
		options = options + ' ' + k + '="' + str(opts[k]) + '"'
	
	values = ''
	for v in vals:
		if (isinstance(v, dict)):
			for k in v:
				if not k in allowed:
					msg = '"' + k + '" unexpected, must be one of ' + ', '.join(['"' + x + '"' for x in allowed])
					raise InvalidKeyword(msg)
				if v[k] == None:
					options = options + ' ' + k
				else:
					options = options + ' ' + k + '="' + str(v[k]) + '"'
		elif (isinstance(v, list)):
			for k in v:
				values = values + ' ' + str(k)
		else:
			values = values + ' ' + str(v)
			
	if (len(values) > 0): values = values[1:]
			
	if (elname.startswith('-')):
		rval = '<' + elname[1:] + options + '>' + values
	else:
		rval = '<' + elname + options + '>' + values + '</' + elname + '>'
		
	return rval

def style(opts, elems):
	allowed = ('media', 'type')
	options = ''
	for k in opts:
		if not k in allowed:
			msg = '"' + k + '" unexpected, must be one of ' + ', '.join(['"' + x + '"' for x in allowed])
			raise InvalidKeyword(msg)
		options = options + ' ' + k + '="' + str(opts[k]) + '"'
	
	return '\n<style' + options + '>\n' + str(elems) + '</style>\n'

def HTTPHeader():
	return ('Content-Type: text/html; charset=ISO-8859-1' + "\n\n" +
			'<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">' + "\n")
	
def table (*vals, **opts):
	return element('table', vals, opts, ('align', 'background', 'bgcolor', 'border', 'bordercolor',
					'bordercolordark', 'bordercolorlight', 'cellpadding', 
					'cellspacing', 'cols', 'frame', 'height', 'hspace', 'nowrap',
					'rules', 'summary', 'valign', 'vspace', 'width')+coreopts)   

def th (*vals, **opts):
	return element('th', vals, opts, ('abbr', 'align', 'axis', 'background', 'bgcolor', 'bordercolor',
					'bordercolordark', 'bordercolorlight', 'char', 'charoff', 'colspan',
					'headers', 'height', 'nowrap', 'rowspan', 'scope', 'valign',
					'width')+coreopts)

def tr (*vals, **opts):
	return element('tr', vals, opts, ('align', 'background', 'bgcolor', 'bordercolor', 
					'bordercolordark', 'bordercolorlight', 'char', 'charoff',
					'nowrap', 'valign')+coreopts)

def td (*vals, **opts):
	return element('td', vals, opts, ('abbr', 'align', 'axis', 'background', 'bgcolor', 'bordercolor',
					'bordercolordark', 'bordercolorlight', 'char', 'charoff', 'colspan',
					'color', 'headers', 'height', 'nowrap', 'rowspan', 'scope', 'valign',
					'width')+coreopts)

def thead (*vals, **opts):
	return element('thead', vals, opts, ('align', 'char', 'charoff', 'valign')+coreopts)

def tbody (*vals, **opts):
	return element('tbody', vals, opts, ('align', 'char', 'charoff', 'valign')+coreopts)

def tfoot (*vals, **opts):
	return element('tfoot', vals, opts, ('align', 'char', 'charoff', 'valign')+coreopts)

def caption (*vals, **opts):
	return element('caption', vals, opts, ('align', 'valign')+coreopts)

def colgroup (*vals, **opts):
	return element('-colgroup', vals, opts, ('align', 'char', 'charoff', 'span', 'valign', 'width')+coreopts)

def col (*vals, **opts):
	return element('-col', vals, opts, ('align', 'char', 'charoff', 'span', 'valign', 'width')+coreopts)

def comment (*vals, **opts):
	return element('comment', vals, opts, ())

def frameset (*vals, **opts):
	return element('frameset', vals, opts,
					('border', 'bordercolor', 'cols', 'frameborder', 'framespacing',
					'onblur', 'onfocus', 'onload', 'onunload', 'rows'))

def frame (*vals, **opts):
	return element('frame', vals, opts,
					('bordercolor', 'frameborder', 'longdesc', 'marginheight'
					'marginwidth', 'noresize', 'scrolling', 'src'))

def noframes (*vals, **opts):
	return element('noframes', vals, opts, ())

def startbody(*vals, **opts):
	return element('-body', vals, opts,
					('alink', 'background', 'bgcolor', 'bgproperties', 'leftmargin', 'link',
					'onblur', 'onfocus', 'onload', 'onunload', 'text', 'topmargin', 'vlink') + coreopts)

def endbody():
	return "</body>"

def starthtml(*vals, **opts):
	return element('-html', vals, opts, ('version', 'xmlns'))

def endhtml():
	return "</html>"

def head(*vals, **opts):
	return element('head', vals, opts, ('profile', ))
	pass

def base(*vals, **opts):
	return element('-base', vals, opts, ('href', 'target'))

def basefont(*vals, **opts):
	return element('-basefont', vals, opts, ('color', 'face', 'size'))

def isindex(*vals, **opts):
	return element('-isindex', vals, opts, ('action', 'prompt'))

def link(*vals, **opts):
	return element('-link', vals, opts, ('charset', 'href', 'hreflang', 'media', 'rel', 'rev', 'type'))

def meta(*vals, **opts):
	return element('-nextid', vals, opts, ('charset', 'content', 'http-equiv', 'scheme'))

def nextid(*vals, **opts):
	return element('-meta', vals, opts, ('n', ))



def title(*vals, **opts):
	return element('title', vals, opts, ())

def h1(*vals, **opts):
	return element('h1', vals, opts, ('align', )+coreopts)
def h2(*vals, **opts):
	return element('h2', vals, opts, ('align', )+coreopts)
def h3(*vals, **opts):
	return element('h3', vals, opts, ('align', )+coreopts)
def h4(*vals, **opts):
	return element('h4', vals, opts, ('align', )+coreopts)
def h5(*vals, **opts):
	return element('h5', vals, opts, ('align', )+coreopts)
def h6(*vals, **opts):
	return element('h6', vals, opts, ('align', )+coreopts)

def a(*vals, **opts):
	return element('a', vals, opts, ('accesskey', 'charset', 'coords', 'href', 'hreflang',
							'rel', 'rev', 'shape', 'tabindex', 'target', 'type')+coreopts)

def dir(*vals, **opts):
	return element('dir', vals, opts, ('type', )+coreopts)

def menu(*vals, **opts):
	return element('menu', vals, opts, ('type', )+coreopts)

def ul(*vals, **opts):
	return element('ul', vals, opts, ('compact', 'type')+coreopts)

def ol(*vals, **opts):
	return element('ol', vals, opts, ('compact', 'start', 'type')+coreopts)

def dl(*vals, **opts):
	return element('dl', vals, opts, ('compact', )+coreopts)

def dd(*vals, **opts):
	return element('dd', vals, opts, ()+coreopts)

def dt(*vals, **opts):
	return element('dt', vals, opts, ()+coreopts)

def li(*vals, **opts):
	return element('li', vals, opts, ('type', 'value')+coreopts)

def em(*vals, **opts):
	return element('em', vals, opts,()+coreopts)

def blockquote(*vals, **opts):
	return element('blockquote', vals, opts, ()+coreopts)

def big(*vals, **opts):
	return element('big', vals, opts, ()+coreopts)

def b(*vals, **opts):
	return element('b', vals, opts, ()+coreopts)

def blink(*vals, **opts):
	return element('blink', vals, opts, ()+coreopts)

def i(*vals, **opts):
	return element('i', vals, opts, ()+coreopts)

def s(*vals, **opts):
	return element('s', vals, opts, ()+coreopts)

def small(*vals, **opts):
	return element('small', vals, opts, ()+coreopts)

def strike(*vals, **opts):
	return element('strike', vals, opts, ()+coreopts)

def sub(*vals, **opts):
	return element('sub', vals, opts, ()+coreopts)

def sup(*vals, **opts):
	return element('sup', vals, opts, ()+coreopts)

def tt(*vals, **opts):
	return element('tt', vals, opts, ()+coreopts)

def u(*vals, **opts):
	return element('u', vals, opts, ()+coreopts)

def abbr(*vals, **opts):
	return element('abbr', vals, opts, ()+coreopts)

def acronym(*vals, **opts):
	return element('acronym', vals, opts, ()+coreopts)

def cite(*vals, **opts):
	return element('cite', vals, opts, ()+coreopts)

def Del(*vals, **opts):
	return element('del', vals, opts, ('cite', 'datetime')+coreopts)

def dfn(*vals, **opts):
	return element('dfn', vals, opts, ()+coreopts)

def ins(*vals, **opts):
	return element('ins', vals, opts, ('cite', 'datetime')+coreopts)

def kbd(*vals, **opts):
	return element('kbd', vals, opts, ()+coreopts)

def samp(*vals, **opts):
	return element('samp', vals, opts, ()+coreopts)

def var(*vals, **opts):
	return element('var', vals, opts, ()+coreopts)

def address(*vals, **opts):
	return element('address', vals, opts, ()+coreopts)

def bdo(*vals, **opts):
	return element('bdo', vals, opts, ()+coreopts)

def center(*vals, **opts):
	return element('center', vals, opts, ()+coreopts)

def div(*vals, **opts):
	return element('div', vals, opts, ('align', 'nowrap')+coreopts)

def startdiv(*vals, **opts):
	return element('-div', vals, opts, ('align', 'nowrap')+coreopts)

def enddiv(*vals, **opts):
	return "</div>"

def font(*vals, **opts):
	return element('font', vals, opts, ('color', 'face', 'size')+coreopts)

def map(*vals, **opts):
	return element('map', vals, opts, ('name', )+coreopts)

def area(*vals, **opts):
	return element('-area', vals, opts, ('accesskey', 'alt', 'coords', 'href', 'nohref', 'notab',
							'inblur', 'onfocus', 'shape', 'tabindex', 'taborder', 'target'))

def marquee(*vals, **opts):
	return element('marquee', vals, opts, ('align', 'behavior', 'bgcolor', 'direction', 'height' 'hspace',
							'loop', 'scrollamount', 'scrolldelay', 'vspace', 'width')+coreopts)

def hr(*vals, **opts):
	return element('-hr', vals, opts, ('align', 'color', 'noshade', 'size', 'width'))

def iframe(*vals, **opts):
	return element('iframe', vals, opts, ('align', 'frameborder', 'height', 'longdesc', 'marginheight',
							'marginwidth', 'scrolling', 'src', 'width'))

def listing(*vals, **opts):
	return element('listing', vals, opts, ()+coreopts)

def p(*vals, **opts):
	return element('p', vals, opts, ('align', )+coreopts)

def pre(*vals, **opts):
	return element('pre', vals, opts, ()+coreopts)

def q(*vals, **opts):
	return element('q', vals, opts, ('cite', )+coreopts)

def span(*vals, **opts):
	return element('span', vals, opts, ()+coreopts)

def xmp(*vals, **opts):
	return element('xmp', vals, opts, ()+coreopts)

def nobr(*vals, **opts):
	return element('nobr', vals, opts, ()+coreopts)

def img(*vals, **opts):
	return element('-img', vals, opts, ('align', 'alt', 'border', 'controls', 'dynsrc', 'height',
										'hspace', 'ismap', 'longdesc', 'loop', 'lowsrc', 'name',
										'onabort', 'onerror', 'onload', 'src', 'start', 
										'usemap', 'vspace', 'width')+coreopts)

def figure(*vals, **opts):
	return element('figure', vals, opts, ()+coreopts)
	
def figcaption(*vals, **opts):
	return element('figcaption', vals, opts, ()+coreopts)
	
def strong(*vals, **opts):
	return element('strong', vals, opts, ()+coreopts)

def form(*vals, **opts):
	return element('form', vals, opts, ('name', )+coreopts)

def select(*vals, **opts):
	return element('select', vals, opts, ('name', )+coreopts)

def option(*vals, **opts):
	return element('option', vals, opts, ('value', )+coreopts)

def input(*vals, **opts):
	return element('input', vals, opts, ('value', 'type', 'name', 'size')+coreopts)
