#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\dogma\items\characterFittedDogmaItem.py
from fittableDogmaItem import FittableDogmaItem
import util

class CharacterFittedDogmaItem(FittableDogmaItem):

    def GetShipID(self):
        if self.location is None:
            self.dogmaLocation.LogWarn('CharacterFittedDogmaItem::GetShipID - item not fitted to location', self.itemID)
            return
        return self.location.GetShipID()

    def GetCharacterID(self):
        return self.GetPilot()

    def IsValidFittingLocation(self, location):
        return location.groupID == const.groupCharacter


class GhostCharacterFittedDogmaItem(CharacterFittedDogmaItem):
    __guid__ = 'GhostCharacterFittedDogmaItem'

    def GetShipID(self):
        return self.dogmaLocation.shipID
