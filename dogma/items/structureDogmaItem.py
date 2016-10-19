#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\dogma\items\structureDogmaItem.py
import weakref
from inventorycommon.util import IsStructureFittingFlag
import utillib
from locationDogmaItem import LocationDogmaItem
import dogma.const
import inventorycommon.const as invconst

class StructureDogmaItem(LocationDogmaItem):

    def __init__(self, *args, **kwargs):
        self.drones = set()
        LocationDogmaItem.__init__(self, *args, **kwargs)

    def OnItemLoaded(self):
        self.dogmaLocation.FitItemToLocation(self.itemID, self.itemID, 0)
        LocationDogmaItem.OnItemLoaded(self)

    def PostLoadAction(self):
        self.dogmaLocation.UpdateStructureServices(self.itemID)

    def ValidFittingFlag(self, flagID):
        return IsStructureFittingFlag(flagID) or flagID == invconst.flagDroneBay

    def CanFitItem(self, dogmaItem, flagID):
        if dogmaItem.categoryID in (const.categoryStructureModule, const.categoryCharge) and self.ValidFittingFlag(flagID):
            return True
        elif dogmaItem.groupID == const.groupCharacter and flagID == const.flagPilot:
            return True
        elif dogmaItem.itemID == self.itemID:
            return True
        else:
            return False

    def SetLocation(self, locationID, locationDogmaItem, flagID):
        if locationID != self.itemID:
            raise RuntimeError('ShipDogmaItem.SetLocation::locationID is not ship (%s, %s)' % (locationID, self.itemID))
        self.fittedItems[locationID] = weakref.proxy(self)
        self.flagID = flagID

    def IsOnline(self):
        return True

    def IsActive(self):
        return False

    def RegisterPilot(self, item):
        self.fittedItems[item.itemID] = weakref.proxy(item)

    def UnregisterPilot(self, item):
        self.fittedItems.pop(item.itemID, None)

    def GetCharacterID(self):
        return None

    def GetPilot(self):
        return self.dogmaLocation.pilotsByShipID.get(self.itemID, None)

    def GetHeatStates(self):
        return {attribute:self.attributes[attribute].GetHeatMessage() for attribute in dogma.heatAttributes}

    def GetHeatValues(self):
        return {attribute:0 for attribute in dogma.heatAttributes}

    def GetDrones(self):
        return {}

    def GetDronesInBay(self):
        return {}

    def GetDronesInSpace(self):
        return {}

    @property
    def overloadedModules(self):
        return set()

    def GetStructureID(self):
        return self.itemID
