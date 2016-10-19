#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\fittingGhost\ghostFittingUtil.py
import dogma.const as dogmaConst
import evetypes
OFFLINE = 0
ONLINE = 1
ACTIVE = 2
OVERHEATED = 3

class GhostFittingDataObject(object):

    def __init__(self, locationID, flagID, typeID, ownerID = None, number = None):
        self.locationID = locationID
        self.flagID = flagID
        self.typeID = typeID
        self.number = number
        self.itemID = self.GetItemKey()
        self.categoryID = evetypes.GetCategoryID(typeID)
        self.groupID = evetypes.GetGroupID(typeID)
        self.ownerID = session.charid

    def GetItemKey(self):
        if self.number is None:
            return '%s_%s' % (self.flagID, self.typeID)
        else:
            return '%s_%s_%s' % (self.flagID, self.typeID, self.number)

    def SetNumber(self, number):
        self.number = number
        self.itemID = self.GetItemKey()


class DBLessGhostFittingDataObject(GhostFittingDataObject):

    def GetItemKey(self):
        return (self.locationID, self.flagID, self.typeID)

    def SetQty(self, qty):
        self.attributes[dogmaConst.attributeQuantity].SetBaseValue(qty)
