
class TrainQueue:
    def __init__(self):
        self.trains = []

    def IsEmpty(self):
        return len(self.trains) == 0
        
    def Append(self, osnm, rtnm, signm, blknm):
        self.trains.append([osnm, rtnm, signm, blknm])

    def Pushx(self, osnm, rtnm, signm, blknm):
        self.trains = [[osnm, rtnm, signm, blknm]] + self.trains

    def Peek(self):
        if len(self.trains) == 0:
            return None

        rv = self.trains[0]
        return rv

    def Pop(self):
        if len(self.trains) == 0:
            return None

        rv = self.trains[0]
        self.trains = self.trains[1:]
        return rv
