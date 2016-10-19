#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\fittingGhost\fittingSlotControllerGhost.py
from eve.client.script.ui.shared.fitting.fittingSlotController import ShipFittingSlotController
from signals import Signal

class ShipFittingSlotControllerGhost(ShipFittingSlotController):

    def __init__(self, flagID, parentController):
        ShipFittingSlotController.__init__(self, flagID, parentController)
        self.on_simulation_mode_changed = Signal()

    def GetModule(self):
        if self.IsModulePreviewModule():
            return None
        return self.dogmaModuleItem

    def IsModulePreviewModule(self):
        if not self.dogmaModuleItem:
            return False
        if getattr(self.dogmaModuleItem, 'isPreviewItem', False):
            return True
        return False
