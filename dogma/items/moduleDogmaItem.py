#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\dogma\items\moduleDogmaItem.py
from fittableDogmaItem import FittableDogmaItem
from utillib import KeyVal
import dogma.const as dgmconst

class ModuleDogmaItem(FittableDogmaItem):

    def GetCharacterID(self):
        return self.GetPilot()

    def IsOnline(self):
        return dgmconst.effectOnline in self.activeEffects

    def IsValidFittingLocation(self, location):
        return location.categoryID == const.categoryShip


class GhostModuleDogmaItem(ModuleDogmaItem):

    def GetPilot(self):
        return session.charid
