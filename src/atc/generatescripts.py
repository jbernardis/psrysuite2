import json

from traineditor.generators import GenerateSim

def GenerateScripts(layoutJson, trainsJson):
    trains = Trains(trainsJson)
    layout = LayoutData(layoutJson)
  
    scripts = {}  
    for tr in trains:
        trid, script = GenerateSim(tr, layout)
        scripts[trid] = script
        
    return scripts

# these data structures represent the data as read from the various database files - not the running system.  Thius, these are local here
class Train:
    def __init__(self, tid):
        self.tid = tid
        self.east = True
        self.steps = []
        self.startblock = None
        self.startsubblock = None
        self.startblocktime = 5000
        self.normalLoco = None
        
    def SetDirection(self, direction):
        self.east = direction
        
    def GetTrainID(self):
        return self.tid
    
    def IsEast(self):
        return self.east

    def SetSteps(self, steps):
        self.steps = [x for x in steps]
        
    def GetNSteps(self):
        return len(self.steps)
        
    def GetSteps(self):
        return [x for x in self.steps]
    
    def SetStartBlockTime(self, time):
        self.startblocktime = time
        
    def GetStartBlockTime(self):
        return self.startblocktime
    
    def SetStartBlock(self, blk):
        self.startblock = blk
        
    def GetStartBlock(self):
        return self.startblock
    
    def SetStartSubBlock(self, blk):
        self.startsubblock = blk
        
    def GetStartSubBlock(self):
        return self.startsubblock
    
    def SetNormalLoco(self, loco):
        self.normalLoco = loco
        
    def GetNormalLoco(self):
        return self.normalLoco
    
    def ToJSON(self):
        return {"eastbound": self.east, "startblock": self.startblock, "startsubblock": self.startsubblock, "time": self.startblocktime, "sequence": self.steps}
    
class Trains:
    def __init__(self, trainsJson):
        self.trainlist = []
        self.trainmap = {}
        for tid, trData in trainsJson.items():
            if len(trData["sequence"]) > 0:
                tr = self.AddTrain(tid, trData["eastbound"])
                tr.SetStartBlock(trData["startblock"])
                tr.SetStartSubBlock(trData["startsubblock"])
                tr.SetStartBlockTime(trData["time"])
                tr.SetSteps(trData["sequence"])
                
                tr.SetNormalLoco(trData["normalloco"])
                self.trainmap[tid] = tr
            
    def __iter__(self):
        self._nx_ = 0
        return self
    
    def __next__(self):
        if self._nx_ >= len(self.trainlist):
            raise StopIteration
        
        nx = self._nx_
        self._nx_ += 1
        return self.trainlist[nx]
        
    def GetTrainList(self):
        return [tr.GetTrainID() for tr in self.trainlist]
    
    def AddTrain(self, tid, east):
        tr = Train(tid)
        tr.SetDirection(east)
        self.trainlist.append(tr)
        self.trainmap[tid] = tr
        return tr
    
    def DelTrainByTID(self, tid):
        if tid not in self.trainmap:
            return False
        
        del self.trainmap[tid]
        
        newtr = [tr for tr in self.trainlist if tr.GetTrainID() != tid]
        self.trainlist = newtr
        
    def GetTrainById(self, tid):
        if tid not in self.trainmap:
            return None
        
        return self.trainmap[tid]
   

class LayoutData:
    def __init__(self, layoutJson):
        self.layout = layoutJson

        self.routes = self.layout["routes"]
        self.subblocks = self.layout["subblocks"]
        self.crossovers = self.layout["crossover"]

        self.block2route = {}
        self.osblocks = []
        self.blocks = []

        self.blockdir = {b: d["east"] for b, d in self.layout["blocks"].items()}
        self.stopblocks = {b: [d["sbeast"], d["sbwest"]] for b, d in self.layout["blocks"].items()}
        for r in self.routes:
            for b in self.routes[r]["ends"]:
                if b not in self.blocks and b is not None:
                    self.blocks.append(b)
                if b in self.block2route:
                    self.block2route[b].append(r)
                else:
                    self.block2route[b] = [r]
            oswitch = self.routes[r]["os"]
            if oswitch not in self.osblocks and oswitch is not None:
                self.osblocks.append(oswitch)
            if oswitch in self.block2route:
                self.block2route[oswitch].append(r)
            else:
                self.block2route[oswitch] = [r]

        self.osblocks = sorted(self.osblocks)
        self.blocks = sorted([x for x in self.blocks if x not in self.osblocks])
        
    def IsCrossoverPt(self, osBlk, blk):
        return [osBlk, blk] in self.crossovers

    def GetRoutesForBlock(self, blknm):
        try:
            return self.block2route[blknm]
        except KeyError:
            return None

    def GetRouteEnds(self, rname):
        return self.routes[rname]["ends"]

    def GetRouteSignals(self, rname):
        return self.routes[rname]["signals"]

    def GetRouteOS(self, rname):
        return self.routes[rname]["os"]

    def GetBlocks(self):
        return self.blocks

    def IsBlockEast(self, blknm):
        try:
            return self.blockdir[blknm] == 1
        except KeyError:
            return None

    def GetSubBlocks(self, blk):
        try:
            return self.subblocks[blk]
        except KeyError:
            return []

    def GetStopBlocks(self, blk):
        try:
            return self.stopblocks[blk]
        except KeyError:
            return [None, None]
