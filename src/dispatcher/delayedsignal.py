
class DelayedSignals:
    def __init__(self):
        self.signals = {}
        
    def Append(self, signm, osnm, rtnm, maxtime):
        self.signals[rtnm] = [osnm, signm, maxtime]

    def CheckForExpiry(self):
        delList = []
        for rtnm in self.signals:
            self.signals[rtnm][2] -= 1
            if self.signals[rtnm][2] <= 0:
                delList.append(rtnm)

        for rtnm in delList:
            del self.signals[rtnm]

    def GetSignal(self, rtnm):
        try:
            signm = self.signals[rtnm][1]
            osnm = self.signals[rtnm][0]
        except KeyError:
            return None, None

        del self.signals[rtnm]
        return osnm, signm
