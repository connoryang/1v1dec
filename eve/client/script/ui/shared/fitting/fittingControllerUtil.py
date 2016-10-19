#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\fitting\fittingControllerUtil.py
import evetypes
from eve.client.script.ui.shared.fitting.fittingController import StructureFittingController, ShipFittingController
from eve.client.script.ui.shared.fitting.fittingUtil import GetTypeIDForController
from eve.client.script.ui.shared.fittingGhost.shipFittingControllerGhost import ShipFittingControllerGhost
from eve.client.script.ui.shared.fittingGhost.structureFittingControllerGhost import StructureFittingControllerGhost

def GetFittingController(itemID, ghost = False):
    typeID = GetTypeIDForController(itemID)
    if ghost:
        if IsInStructureCategory(typeID):
            return StructureFittingControllerGhost(itemID, typeID)
        else:
            return ShipFittingControllerGhost(itemID)
    else:
        if IsInStructureCategory(typeID):
            return StructureFittingController(itemID, typeID)
        return ShipFittingController(itemID)


def IsInStructureCategory(typeID):
    return evetypes.GetCategoryID(typeID) == const.categoryStructure
