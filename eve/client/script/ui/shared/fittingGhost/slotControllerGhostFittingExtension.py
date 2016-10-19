#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\fittingGhost\slotControllerGhostFittingExtension.py
import weakref

class ShipFittingSlotControllerGhostFittingExtension(object):

    def __init__(self, controller):
        self.controller = weakref.ref(controller)

    def FitCharges(self, flagID, chargeItems):
        chargeTypeID = chargeItems[0].typeID
        ghostFittingSvc = sm.GetService('ghostFittingSvc')
        ghostFittingSvc.FitAmmoToLocation(flagID, chargeTypeID)
        ghostFittingSvc.SendFittingSlotsChangedEvent()
        if self.controller:
            self.controller().on_item_fitted()

    def UnfitFromSlot(self, charge, module):
        itemID = None
        if charge:
            itemID = charge.itemID
        elif module:
            itemID = module.itemID
        if itemID:
            self._UnfitModuleOrAmmo(itemID)

    def _UnfitModuleOrAmmo(self, itemID):
        ghostFittingSvc = sm.GetService('ghostFittingSvc')
        ghostFittingSvc.UnfitModule(itemID)
