def GenerateAR(tr, blks):		
	trainid = tr.GetTrainID()
	lastBlock = tr.GetStartBlock()
	blkSeq = tr.GetSteps()
	script = {}
	for b in blkSeq:
		if len(script) == 0:
			script["origin"] = lastBlock
			
		if blks is None or b["block"] in blks:
			trigger = 'F' if b["trigger"] == "Front" else 'R'			
			script[lastBlock] = {"route": b["route"], "trigger": trigger}
		lastBlock = b["block"]
		
	script["terminus"] = lastBlock

	return trainid, script

		
def GenerateSim(tr, layout):
	locoid = 0
	trainid = tr.GetTrainID()
	east = tr.IsEast()
	segTimes, segString = determineSegmentsAndTimes(tr.GetStartBlock(), None, east, tr.GetStartBlockTime(), layout)
	sBlk = tr.GetStartBlock()
	subBlk = tr.GetStartSubBlock()
	#if subBlk is not None:
		#sBlk = subBlk
		
	# determine which segment is our starting position and ignore the seqments before it in the list
	for idx in range(len(segTimes)):
		if sBlk == segTimes[idx][0]:
			break
	else:
		idx = 0
		
	script = []
	placeTrainCmd = {"block": sBlk, "name": trainid, "loco": locoid, "time": segTimes[idx][1], "length": 3, "dir": "E" if east else "W"}
	if subBlk is not None:
		placeTrainCmd["subblock"] = segTimes[idx][0]
		
	script.append({"placetrain": placeTrainCmd})

	idx += 1
	while idx < len(segTimes):
		script.append({"movetrain": {"block": segTimes[idx][0], "time": segTimes[idx][1]}})
		idx += 1

	blkSeq = tr.GetSteps()
	nblocks = len(blkSeq)
	bx = 0
	lastBlock = sBlk
	for b in blkSeq:
		bx += 1
		terminus = bx == nblocks
		if checkChangeDirection(lastBlock, b["os"], b["block"], layout):
			east = not east
			
		segTimes, segString = determineSegmentsAndTimes(b["block"], b["os"], east, b["time"], layout, terminus=terminus)

		script.append({"waitfor": {"signal": b["signal"], "route": b["route"], "os": segTimes[0][0], "block": segString}})
		
		script.append({"movetrain": {"block": segTimes[0][0], "time": segTimes[0][1]}})
		for seg, tm in segTimes[1:]:
			script.append({"movetrain": {"block": seg, "time": tm}})
			
		lastBlock = b["block"]

	return trainid, script

def StoppingSection(blk):
	return blk.endswith(".W") or blk.endswith(".E")

def checkChangeDirection(b1, os, b2, layout):
	if layout.IsCrossoverPt(os, b1):
		return True
	
	return layout.IsCrossoverPt(os, b2)		
	
def determineSegmentsAndTimes(block, os, east, blockTime, layout, terminus=False):
	subBlocks = layout.GetSubBlocks(block)
	if len(subBlocks) == 0:
		subBlocks = [block]  # no sub-blocks - just use the block name itself
	stopBlocks = layout.GetStopBlocks(block)
	
	blks = []
	waitblks = []
	subCt = len(subBlocks)
	stopCt = 0
	if east:
		if stopBlocks[1]:
			stopCt += 1
			blks.append(stopBlocks[1])
			waitblks.append(stopBlocks[1])
		blks.extend(subBlocks)
		waitblks.append(block)
		if stopBlocks[0] and not terminus: # Don't include stop block in terminus'
			stopCt += 1
			blks.append(stopBlocks[0])
			waitblks.append(stopBlocks[0])
	else:
		if stopBlocks[0]:
			stopCt += 1
			blks.append(stopBlocks[0])
			waitblks.append(stopBlocks[0])
		# when traveling westbound, subblocks are visited in the reverse order
		blks.extend(list(reversed(subBlocks)))
		waitblks.append(block)
		if stopBlocks[1] and not terminus: # Don't include stop block in terminus:
			stopCt += 1
			blks.append(stopBlocks[1])
			waitblks.append(stopBlocks[1])

	waitString = ",".join(waitblks) # segment string should NOT include the os
	if os is not None:
		blks.insert(0, os)
		subCt += 1
	stopTime = int(blockTime * 0.1)
	subTime = int((blockTime - stopTime * stopCt) / subCt)
	segTimes = [[blk, stopTime if StoppingSection(blk) else subTime] for blk in blks]
	
	return segTimes,waitString
