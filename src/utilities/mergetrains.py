import os
import json

trkfn = os.path.join(os.getcwd(), "data", "trains.json")
seqfn = os.path.join(os.getcwd(), "data", "trainseq.json")

with open(trkfn, "r") as trkfp:
    trkj = json.load(trkfp)
    
with open(seqfn, "r") as seqfp:
    seqj = json.load(seqfp)
    

keyList = sorted([*set(list(trkj.keys()) + list(seqj.keys()))])
ntrains = len(keyList)

trains = {}
for k in keyList:
    if k in trkj:
        tracker = trkj[k]
    else:
        tracker = None
        
    if k in seqj:
        sequence = seqj[k]
    else:
        sequence = None
        
    train = {}
    trackerDir = None
    sequenceDir = None
    if tracker:
        train["tracker"] = tracker["steps"]
        for tk in tracker.keys():
            if tk not in [ "steps", "dir" ]:
                train[tk] = tracker[tk]
            elif tk == "dir":
                trackerDir = tracker[tk]
    else:
        train["tracker"] = []
        train["block"] = None
        train["cutoff"] = False
        train["desc"] = None
        train["loco"] = None
        train["normalloco"] = None
        train["origin"] = {"loc": None, "track": None}
        train["terminus"] = {"loc": None, "track": None}
        
    if sequence:
        train["sequence"] = sequence["steps"]
        for sk in sequence.keys():
            if sk not in [ "steps", "eastbound" ]:
                train[sk] = sequence[sk]
            elif sk == "eastbound":
                sequenceDir = sequence[sk]
    else:
        train["sequence"] = []
        train["startblock"] = None
        train["startsubblock"] = None
        train["time"] = None
        
    if trackerDir is None:
        train["eastbound"] = sequenceDir
    elif sequenceDir is None:
        train["eastbound"] = trackerDir == "East"
    else:
        train["eastbound"] = sequenceDir
        if (sequenceDir and trackerDir != "East") or (not sequenceDir and trackerDir == "East"):
            print("train %s, tracker east: %s  seq east: %s" % (k, str(trackerDir), str(sequenceDir)))
 
    trains[k] = train
 
jfn = os.path.join(os.getcwd(), "data", "newtrains.json")
with open(jfn, "w") as jfp:
    json.dump(trains, jfp, indent=2)
    
print("%d trains saved to output file: %s" % (ntrains, jfn))


    