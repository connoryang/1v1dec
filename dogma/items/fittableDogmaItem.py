#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\dogma\items\fittableDogmaItem.py
from dogma.dogmaLogging import *
from baseDogmaItem import BaseDogmaItem
from ccpProfile import TimedFunction
import weakref

class FittableDogmaItem(BaseDogmaItem):

    def __init__(self, *args, **kwargs):
        self._location = None
        self.lastStopTime = None
        BaseDogmaItem.__init__(self, *args, **kwargs)

    @property
    def location(self):
        if self._location:
            return self._location()

    @location.setter
    def location(self, location):
        if location is None:
            self._location = None
        else:
            self._location = weakref.ref(location)

    @property
    def ownerID(self):
        if self.location:
            return self.location.ownerID

    @ownerID.setter
    def ownerID(self, ownerID):
        if self.location and self.location.ownerID != ownerID:
            self.dogmaLocation.LogError('Setting ownerID on a FittableDogmaItem to something that disagrees with its location!', self.location.ownerID, ownerID)

    @TimedFunction('FittableDogmaItem::Unload')
    def Unload(self):
        BaseDogmaItem.Unload(self)
        if self.location:
            try:
                locationFittedItems = self.location.fittedItems
            except AttributeError:
                return

            if self.itemID in locationFittedItems:
                del locationFittedItems[self.itemID]
        elif self.itemID in self.dogmaLocation.itemsMissingLocation:
            del self.dogmaLocation.itemsMissingLocation[self.itemID]

    def SetLastStopTime(self, lastStopTime):
        self.lastStopTime = lastStopTime

    def IsActive(self):
        for effectID in self.activeEffects:
            if effectID == const.effectOnline:
                continue
            effect = self.dogmaLocation.GetEffect(effectID)
            if effect.effectCategory in (const.dgmEffActivation, const.dgmEffTarget):
                return True

        return False

    @TimedFunction('FittableDogmaItem::SetLocation')
    def SetLocation(self, locationID, location, flagID):
        if location is None:
            self.dogmaLocation.LogError('FittableDogmaItem.SetLocation :: Location dogma item is None')
            return
        if not self.IsValidFittingLocation(location):
            self.dogmaLocation.LogError('FittableDogmaItem.SetLocation :: Invalid fitting location')
            return
        oldData = self.GetLocationInfo()
        self.location = location
        self.flagID = flagID
        location.RegisterFittedItem(self, flagID)
        return oldData

    def IsValidFittingLocation(self, location):
        return False

    def UnsetLocation(self, locationDogmaItem):
        locationDogmaItem.UnregisterFittedItem(self)

    def GetShipID(self):
        if self.location:
            return self.location.itemID

    def GetPilot(self):
        if self.location:
            return self.location.GetPilot()

    def GetOtherID(self):
        otherID = None
        if self.location:
            otherID = self.location.subLocations.get(self.flagID, None)
            if otherID is None:
                other = self.dogmaLocation.GetChargeNonDB(self.location.itemID, self.flagID)
                if other is not None:
                    otherID = other.itemID
        return otherID

    def SerializeForPropagation(self):
        retVal = BaseDogmaItem.SerializeForPropagation(self)
        retVal.lastStopTime = self.lastStopTime
        return retVal

    def UnpackPropagationData(self, propData, charID, shipID):
        BaseDogmaItem.UnpackPropagationData(self, propData, charID, shipID)
        self.SetLastStopTime(propData.lastStopTime)
