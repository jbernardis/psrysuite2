HyYdPt = "HyYdPt"
LaKr   = "LaKr"
NaCl   = "NaCl"

screensList = [HyYdPt, LaKr, NaCl]

# block statuses
EMPTY = 0
OCCUPIED = 1
CLEARED = 2

# block types
BLOCK = 10
OVERSWITCH = 11
STOPPINGBLOCK = 12

# turnout status
NORMAL = 20
REVERSE = 21

# turnout types
TURNOUT = 30
SLIPSWITCH = 31

# basic signal aspects
STOP = 0b000
CLEAR = 0b011

# where to add a list of blocks onto a train
FRONT = "f"
REAR = "r"
REPLACE = "p"

# route types
MAIN = 40
SLOW = 41
DIVERGING = 42
RESTRICTING = 43

# aspect types
RegAspects = 50
RegSloAspects = 51
AdvAspects = 52
SloAspects = 53


def turnoutstate(st, short=False):
	if st == NORMAL:
		return "Nml" if short else "Normal"
	if st == REVERSE:
		return "Rev" if short else "Reverse"
	
	return "??"


def statusname(status):
	if status == EMPTY:
		return "EMPTY"
	
	elif status == "OCCUPIED":
		return "OCCUPIED"
	
	elif status == CLEARED:
		return "CLEARED"
	
	else:
		return "None"


def aspectname(aspect, atype):
	if atype == RegAspects:
		if aspect == 0b011:
			return "Clear"

		elif aspect == 0b010:
			return "Approach Medium"

		elif aspect == 0b111:
			return "Medium Clear"

		elif aspect == 0b110:
			return "Approach Slow"

		elif aspect == 0b001:
			return "Approach"

		elif aspect == 0b101:
			return "Medium Approach"

		elif aspect == 0b100:
			return "Restricting"

		else:
			return "Stop"

	elif atype == RegSloAspects:
		if aspect == 0b011:
			return "Clear"

		elif aspect == 0b111:
			return "Slow clear"

		elif aspect == 0b001:
			return "Approach"

		elif aspect == 0b101:
			return "Slow Approach"

		elif aspect == 0b100:
			return "Restricting"

		else:
			return "Stop"

	elif atype == AdvAspects:
		if aspect == 0b011:
			return "Clear"

		elif aspect == 0b010:
			return "Approach Medium"

		elif aspect == 0b111:
			return "Clear"

		elif aspect == 0b110:
			return "Advance Approach"

		elif aspect == 0b001:
			return "Approach"

		elif aspect == 0b101:
			return "Medium Approach"

		elif aspect == 0b100:
			return "Restricting"

		else:
			return "Stop"

	elif atype == SloAspects:
		if aspect == 0b01:
			return "Slow Clear"

		elif aspect == 0b11:
			return "Slow Approach"

		elif aspect == 0b10:
			return "Restricting"

		else:
			return "Stop"

	else:
		return "Stop"


def aspectprofileindex(aspect, atype):
	""" 
	return the index used to determine maximum speed from a locomotive's profile
	the return value ranges from 0 - the least permissive (stop)
	to 3 for the most permissive (clear)
	"""
	if atype == RegAspects:
		if aspect == 0b011:
			return 3  # Clear
		
		elif aspect == 0b010:
			return 2  # Approach Medium
		
		elif aspect == 0b111:
			return 2  # Medium Clear
		
		elif aspect == 0b110:
			return 1  # Approach Slow
		
		elif aspect == 0b001:
			return 2  # Approach
		
		elif aspect == 0b101:
			return 2  # Medium Approach
		
		elif aspect == 0b100:
			return 1  # Restricting
		
		else:
			return 0  # Stop
	
	elif atype == RegSloAspects:
		if aspect == 0b011:
			return 3  # Clear
		
		elif aspect == 0b111:
			return 2  # Slow clear
		
		elif aspect == 0b001:
			return 2  # Approach
		
		elif aspect == 0b101:
			return 1  # Slow Approach
		
		elif aspect == 0b100:
			return 1  # Restricting
		
		else:
			return 0  # Stop
	
	elif atype == AdvAspects:
		if aspect == 0b011:
			return 3  # Clear
		
		elif aspect == 0b010:
			return 2  # Approach Medium
		
		elif aspect == 0b111:
			return 3  # Clear
		
		elif aspect == 0b110:
			return 2  # Advance Approach
		
		elif aspect == 0b001:
			return 2  # Approach
		
		elif aspect == 0b101:
			return 2  # Medium Approach
		
		elif aspect == 0b100:
			return 1  # Restricting
		
		else:
			return 0  # Stop
	
	elif atype == SloAspects:
		if aspect == 0b01:
			return 2  # Slow Clear
		
		elif aspect == 0b11:
			return 1  # Slow Approach
		
		elif aspect == 0b10:
			return 1  # Restricting
		
		else:
			return 0  # Stop
	
	else:
		return 0  # Stop


def restrictedaspect(atype):
	return 0b10 if atype == SloAspects else 0b100


def aspecttype(atype):
	if atype == RegAspects:
		return "Regular"
	if atype == RegSloAspects:
		return "Reg Slow"
	if atype == AdvAspects:
		return "Advance"
	if atype == SloAspects:
		return "Slow"
	return "unknown"
		
		
def routetype(rtype):
	if rtype == MAIN:
		return "MAIN"
	if rtype == DIVERGING:
		return "DIVERGING"
	if rtype == SLOW:
		return "SLOW"
	if rtype == RESTRICTING:
		return "RESTRICTING"


def statustype(stat):
	if stat == CLEARED:
		return "CLEARED"
	else:
		return "NOT CLEARED"


osBlockNames = {
	'BOSE': 'Bank East',
	'BOSWE': 'Bank West EB',
	'BOSWW': 'Bank West WB',
	'COSCLEE': 'Cliveden East EB',
	'COSCLEW': 'Cliveden East WB',
	'COSCLW': 'Cliveden West', 
	'COSGME': 'Green Mountain East', 
	'COSGMW': 'Green Mountain West',
	'COSSHE': 'Sheffield East', 
	'COSSHW': 'Sheffield West', 
	'DOSFOE': 'Foss East', 
	'DOSFOW': 'Foss West', 
	'DOSVJE': 'Valley Junction East', 
	'DOSVJW': 'Valley Junction West', 
	'HOSEE': 'Hyde East EB', 
	'HOSEW': 'Hyde East WB', 
	'HOSWE': 'Hyde West EB', 
	'HOSWW': 'Hyde West WB', 
	'HOSWW2': 'Hyde West H30', 
	'KOSE': 'Krulish EB',
	'KOSM': 'Krulish Mid', 
	'KOSN10S11': 'Krulish Virtual WB',
	'KOSN20S21': 'Krulish Virtual EB', 
	'KOSW': 'Krulish WB', 
	'LOSCAE': 'Carlton EB', 
	'LOSCAM': 'Carlton Mid', 
	'LOSCAW': 'Carlton WB', 
	'LOSLAE': 'Latham EB', 
	'LOSLAM': 'Latham Mid', 
	'LOSLAW': 'Latham WB', 
	'NEOSE': 'Nassau East EB', 
	'NEOSRH': 'Nassau East Rocky Hill', 
	'NEOSW': 'Nassau East WB', 
	'NWOSCY': 'Nassau West Coach Yard', 
	'NWOSE': 'Nassau West EB', 
	'NWOSTY': 'Nassau West Thomas Yard', 
	'NWOSW': 'Nassau West WB', 
	'POSCJ1': 'Circus Jct 1', 
	'POSCJ2': 'Circus Jct 2', 
	'POSPJ1': 'Parsons Jct 1', 
	'POSPJ2': 'Parsons Jct 2', 
	'POSSJ1': 'South Jct 1', 
	'POSSJ2': 'South Jct 2', 
	'POSSP1': 'Southport 1', 
	'POSSP2': 'Southport 2', 
	'POSSP3': 'Southport 3', 
	'POSSP4': 'Southport 4', 
	'POSSP5': 'Southport 5', 
	'SOSE': 'Shore EB', 
	'SOSHF': 'Shore Harpers Ferry', 
	'SOSHJE': 'Hyde Jct EB', 
	'SOSHJM': 'Hyde Jct Mid', 
	'SOSHJW': 'Hyde Jct WB', 
	'SOSW': 'Shore WB', 
	'YOSCJE': 'Cornell Junction EB', 
	'YOSCJW': 'Cornell Jct WB', 
	'YOSEJE': 'East Jct EB', 
	'YOSEJW': 'East Jct WB', 
	'YOSKL1': 'Kale 1', 
	'YOSKL2': 'Kale 2', 
	'YOSKL3': 'Kale 3', 
	'YOSKL4': 'Kale 4', 
	'YOSWYE': 'Waterman E', 
	'YOSWYW': 'Waterman W'
}


def BlockName(bn):
	return osBlockNames.get(bn, bn)

	
