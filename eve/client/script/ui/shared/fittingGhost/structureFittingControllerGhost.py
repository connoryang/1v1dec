#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\fittingGhost\structureFittingControllerGhost.py
import evetypes
from eve.client.script.ui.shared.fitting.fittingController import StructureFittingController
from eve.client.script.ui.shared.fitting.fittingSlotController import StructureFittingServiceSlotController
import inventorycommon.const as invConst
from eve.client.script.ui.shared.fittingGhost.fittingSlotControllerGhost import ShipFittingSlotControllerGhost
from eve.client.script.ui.shared.fittingGhost.ghostControllerMixin import GhostControllerMixin

class StructureFittingSlotControllerGhost(ShipFittingSlotControllerGhost):
    pass


class StructureFittingControllerGhost(GhostControllerMixin, StructureFittingController):
    SLOT_CLASS = ShipFittingSlotControllerGhost
    __notifyevents__ = GhostControllerMixin.__notifyevents__ + StructureFittingController.__notifyevents__

    def __init__(self, itemID, typeID = None):
        StructureFittingController.__init__(self, itemID, typeID)
        GhostControllerMixin.__init__(self, itemID, typeID)

    def SetGhostFittedItem(self, ghostItem = None):
        if not self.IsSimulated():
            StructureFittingController.SetGhostFittedItem(self, ghostItem)
        else:
            GhostControllerMixin.SetGhostFittedItem(self, ghostItem)
