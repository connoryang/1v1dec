#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\dogma\items\dblessDogmaItem.py
from chargeDogmaItem import ChargeDogmaItem
from ccpProfile import TimedFunction
import dogma.const as dogmaConst
import sys

class DBLessDogmaItem(ChargeDogmaItem):

    @TimedFunction('DBLessDogmaItem::__init__')
    def __init__(self, dogmaLocation, item, eveCfg, clientIDFunc):
        ChargeDogmaItem.__init__(self, dogmaLocation, item, eveCfg, clientIDFunc)
        self.fittedItems = {}
        self.subLocations = {}

    def Load(self, _, __):
        pass

    def Unload(self):
        ChargeDogmaItem.Unload(self)
        self.dogmaLocation.RemoveSubLocationFromLocation(self.itemID)

    def SetLocation(self, locationID, locationDogmaItem, flagID):
        ChargeDogmaItem.SetLocation(self, locationID, locationDogmaItem, flagID)
        locationDogmaItem.SetSubLocation(self.itemID)
        locationDogmaItem.MarkDirty()

    def UnsetLocation(self, locationDogmaItem):
        ChargeDogmaItem.UnsetLocation(self, locationDogmaItem)
        locationDogmaItem.RemoveSubLocation(self.itemID)

    def OnItemLoaded(self):
        locationID, flagID, typeID = self.itemID
        try:
            quantity = self.dogmaLocation.GetQuantityFromCache(locationID, flagID)
            self.attributes[dogmaConst.attributeQuantity].SetBaseValue(quantity)
        except KeyError:
            sys.exc_clear()
        finally:
            ChargeDogmaItem.OnItemLoaded(self)
