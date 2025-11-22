# district node addresses
YARD      = 0x11
KALE      = 0x12
EASTJCT   = 0x13
CORNELL   = 0x14
YARDSW    = 0x15
PARSONS   = 0x21
PORTA     = 0x22
PORTB     = 0x23
LATHAM    = 0x31
CARLTON   = 0x32
DELL      = 0x41
FOSS      = 0x42
HYDEJCT   = 0x51
HYDE      = 0x52
SHORE     = 0x61
KRULISH   = 0x71
NASSAUW   = 0x72
NASSAUE   = 0x73
NASSAUNX  = 0x74
BANK      = 0x81
CLIVEDEN  = 0x91
GREENMTN  = 0x92
CLIFF     = 0x93
SHEFFIELD = 0x95


nodeNames = {
    YARD:       "Yard",
    KALE:       "Kale",
    EASTJCT:    "East Jct",
    CORNELL:    "Cornell",
    YARDSW:     "Yard SW",
    PARSONS:    "Parsons Jct",
    PORTA:      "Port A",
    PORTB:      "Port B",
    LATHAM:     "Latham",
    CARLTON:    "Carlton",
    DELL:       "Dell",
    FOSS:       "Foss",
    HYDEJCT:    "Hyde Jct",
    HYDE:       "Hyde",
    SHORE:      "Shore",
    KRULISH:    "Krulish",
    NASSAUW:    "Nassau W",
    NASSAUE:    "Nassau E",
    NASSAUNX:   "Nassau NX",
    BANK:       "Bank",
    CLIVEDEN:   "Cliveden",
    GREENMTN:   "Green Mtn",
    CLIFF:      "Cliff",
    SHEFFIELD:  "Sheffield"
}
    
# input bit types
INPUT_BLOCK = 1
INPUT_TURNOUTPOS = 2
INPUT_HANDSWITCH = 3
INPUT_SIGNALLEVER = 4
INPUT_ROUTEIN = 5
INPUT_BREAKER = 6


EWCrossoverPoints = [
    ["COSSHE", "C20"],
    ["YOSCJE", "P50"],
    ["YOSCJW", "P50"],
    ["POSSJ1", "P30"],
    ["SOSE",   "P32"],
    ["SOSW",   "P32"],
    ["YOSKL4", "Y30"],
    ["YOSWYW", "Y87"],
]


def CrossingEastWestBoundary(osblk, blk):
    if osblk is None or blk is None:
        return False
    blkNm = blk.Name()
    osNm = osblk.Name()
    return [osNm, blkNm] in EWCrossoverPoints or [blkNm, osNm] in EWCrossoverPoints
