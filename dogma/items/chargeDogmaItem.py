#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\dogma\items\chargeDogmaItem.py
from fittableDogmaItem import FittableDogmaItem
import util

class ChargeDogmaItem(FittableDogmaItem):

    def GetOtherID(self):
        if self.location:
            otherID = self.dogmaLocation.GetSlotOther(self.location.itemID, self.flagID)
            if otherID is None and self.dogmaLocation.IsItemSubLocation(self.itemID):
                otherID = self.location.itemID
            return otherID

    def IsValidFittingLocation(self, location):
        return location.categoryID in (const.categoryShip, const.categoryStarbase, const.categoryStructure)

    def IsOwnerModifiable(self):
        if not self.location:
            return False
        pilotID = self.location.GetPilot()
        if not pilotID:
            return False
        shipID = self.locationID
        if not shipID:
            return False
        if self.dogmaLocation.IsItemSubLocation(self.itemID):
            if shipID == self.dogmaLocation.shipsByPilotID.get(pilotID, None):
                return True
        return False

    def GetStructureID(self):
        pilotID = self.GetPilot()
        shipID = self.dogmaLocation.shipsByPilotID.get(pilotID, None)
        return self.dogmaLocation.GetStructureIdForEnvironment(shipID)

    def GetCharacterID(self):
        return self.GetPilot()
