#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\tacticalNavigation\navigationPoint.py
import navigationBracket
import tacticalNavigation.ui as tacticalui
from ballparkFunctions import AddClientBall, RemoveClientBall

class NavigationPoint:

    def __init__(self, globalPosition):
        self.globalPosition = globalPosition
        self.clientBall = AddClientBall(globalPosition)
        self.bracket = navigationBracket.NavigationPointBracket.Create(self.clientBall)
        self.refCount = 0

    def GetNavBall(self):
        return self.clientBall

    def AddReferrer(self):
        self.refCount += 1

    def RemoveReferrer(self):
        self.refCount -= 1

    def HasReferrers(self):
        return self.refCount > 0

    def Destroy(self):
        self.bracket.Close()
        RemoveClientBall(self.clientBall)
