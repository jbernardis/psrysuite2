
class DelayedRequests:
    def __init__(self):
        self.events = []
        
    def Append(self, evt):
        cmd = list(evt.keys())[0]
        delay = evt[cmd]["delay"]
        del evt[cmd]["delay"]
        self.events.append([delay, evt])
        
    def CheckForExpiry(self, cb):
        if len(self.events) == 0:
            return 
        
        for evt in self.events:
            evt[0] -= 1
            
        readyList = [evt[1] for evt in self.events if evt[0] <= 0]
        
        self.events = [evt for evt in self.events if evt[0] > 0]
        
        for evt in readyList:
            cb(evt)
