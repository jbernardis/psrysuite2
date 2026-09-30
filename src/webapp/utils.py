

def BitSet(bbyte, bbit, bvals):
	bval = bvals[bbyte]
	bitvals = []
	for b in range(8):
		bitvals.append(bval % 2)
		bval = int(bval / 2)
	bitvals = [v for v in bitvals[::-1]]
	return bitvals[bbit] != 0
