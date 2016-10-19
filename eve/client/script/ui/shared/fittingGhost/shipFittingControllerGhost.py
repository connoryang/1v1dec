#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\fittingGhost\shipFittingControllerGhost.py
from eve.client.script.ui.shared.fitting.fittingController import ShipFittingController
from eve.client.script.ui.shared.fittingGhost.fittingSlotControllerGhost import ShipFittingSlotControllerGhost
from eve.client.script.ui.shared.fittingGhost.ghostControllerMixin import GhostControllerMixin

class ShipFittingControllerGhost(GhostControllerMixin, ShipFittingController):
    SLOT_CLASS = ShipFittingSlotControllerGhost
    __notifyevents__ = GhostControllerMixin.__notifyevents__ + ShipFittingController.__notifyevents__

    def __init__(self, itemID, typeID = None):
        ShipFittingController.__init__(self, itemID, typeID)
        GhostControllerMixin.__init__(self, itemID, typeID)

    def SetGhostFittedItem(self, ghostItem = None):
        if not self.IsSimulated():
            ShipFittingController.SetGhostFittedItem(self, ghostItem)
        else:
            GhostControllerMixin.SetGhostFittedItem(self, ghostItem)
