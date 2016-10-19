#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\inventory\invContainers.py
from eve.client.script.ui.inflight.squadrons.fighterInvCont import FighterInvCont
import uiprimitives
import uicontrols
import carbonui.const as uiconst
import uiutil
import invCtrl
import invCont
import crimewatchConst

class _BaseCelestialContainer(invCont._InvContBase):
    __guid__ = 'invCont._BaseCelestialContainer'
    __invControllerClass__ = None

    def ApplyAttributes(self, attributes):
        invCont._InvContBase.ApplyAttributes(self, attributes)
        if self.invController.IsLootable():
            self.CheckCanTakeItems = sm.GetService('crimewatchSvc').CheckCanTakeItems
            self.restrictedFrame = uicontrols.Frame(parent=self, color=crimewatchConst.Colors.Yellow.GetRGBA(), state=uiconst.UI_HIDDEN)
            self.restrictedButtonFill = uiprimitives.Fill(color=crimewatchConst.Colors.Suspect.GetRGBA(), opacity=0.3, name='criminalRestrictionFill', state=uiconst.UI_HIDDEN)
            self.restrictedButton = None
            uicore.event.RegisterForTriuiEvents(uiconst.UI_MOUSEMOVE, self._EnforceLootableContainerRestrictions)

    def RegisterSpecialActionButton(self, button):
        if self.invController.IsLootable():
            if button.func.__name__ == 'LootAll':
                self.restrictedButton = button
                self.restrictedButtonFill.SetParent(button, 0)

    def _EnforceLootableContainerRestrictions(self, *args):
        if not self or self.destroyed:
            return False
        isAccessRestricted = False
        if uicore.uilib.mouseOver in (self, self.restrictedButton) or uiutil.IsUnder(uicore.uilib.mouseOver, self) or uiutil.IsUnder(uicore.uilib.mouseOver, self.restrictedButton):
            if not self.CheckCanTakeItems(self.invController.itemID):
                isAccessRestricted = True
        if isAccessRestricted:
            self.restrictedFrame.Show()
            self.restrictedButtonFill.Show()
        else:
            self.restrictedFrame.Hide()
            self.restrictedButtonFill.Hide()
        return True


class ShipCargo(invCont._InvContBase):
    __guid__ = 'invCont.ShipCargo'
    __invControllerClass__ = invCtrl.ShipCargo


class POSRefinery(_BaseCelestialContainer):
    __guid__ = 'invCont.POSRefinery'
    __invControllerClass__ = invCtrl.POSRefinery


class POSCompression(_BaseCelestialContainer):
    __guid__ = 'invCont.POSCompression'
    __invControllerClass__ = invCtrl.POSCompression


class POSStructureCharges(_BaseCelestialContainer):
    __guid__ = 'invCont.POSStructureCharges'
    __invControllerClass__ = invCtrl.POSStructureCharges


class POSStructureChargeCrystal(POSStructureCharges):
    __guid__ = 'invCont.POSStructureChargeCrystal'
    __invControllerClass__ = invCtrl.POSStructureChargeCrystal


class POSStructureChargesStorage(_BaseCelestialContainer):
    __guid__ = 'invCont.POSStructureChargesStorage'
    __invControllerClass__ = invCtrl.POSStructureChargesStorage


class POSStrontiumBay(_BaseCelestialContainer):
    __guid__ = 'invCont.POSStrontiumBay'
    __invControllerClass__ = invCtrl.POSStrontiumBay


class POSFuelBay(_BaseCelestialContainer):
    __guid__ = 'invCont.POSFuelBay'
    __invControllerClass__ = invCtrl.POSFuelBay


class POSJumpBridge(_BaseCelestialContainer):
    __guid__ = 'invCont.POSJumpBridge'
    __invControllerClass__ = invCtrl.POSJumpBridge


class POSShipMaintenanceArray(_BaseCelestialContainer):
    __guid__ = 'invCont.POSShipMaintenanceArray'
    __invControllerClass__ = invCtrl.POSShipMaintenanceArray


class POSSilo(_BaseCelestialContainer):
    __guid__ = 'invCont.POSSilo'
    __invControllerClass__ = invCtrl.POSSilo


class POSMobileReactor(_BaseCelestialContainer):
    __guid__ = 'invCont.POSMobileReactor'
    __invControllerClass__ = invCtrl.POSMobileReactor


class POSConstructionPlatform(_BaseCelestialContainer):
    __guid__ = 'invCont.POSConstructionPlatform'
    __invControllerClass__ = invCtrl.POSConstructionPlatform


class POSPersonalHangar(_BaseCelestialContainer):
    __guid__ = 'invCont.POSPersonalHangar'
    __invControllerClass__ = invCtrl.POSPersonalHangar


class ItemWreck(_BaseCelestialContainer):
    __guid__ = 'invCont.ItemWreck'
    __invControllerClass__ = invCtrl.ItemWreck


class ItemFloatingCargo(_BaseCelestialContainer):
    __guid__ = 'invCont.ItemFloatingCargo'
    __invControllerClass__ = invCtrl.ItemFloatingCargo


class ItemSiphonPseudoSilo(_BaseCelestialContainer):
    __guid__ = 'invCont.ItemSiphonPseudoSilo'
    __invControllerClass__ = invCtrl.ItemSiphonPseudoSilo


class StationContainer(_BaseCelestialContainer):
    __guid__ = 'invCont.StationContainer'
    __invControllerClass__ = invCtrl.StationContainer


class AssetSafetyContainer(_BaseCelestialContainer):
    __guid__ = 'invCont.AssetSafetyContainer'
    __invControllerClass__ = invCtrl.AssetSafetyContainer


class ShipMaintenanceBay(_BaseCelestialContainer):
    __guid__ = 'invCont.ShipMaintenanceBay'
    __invControllerClass__ = invCtrl.ShipMaintenanceBay


class ShipDroneBay(invCont._InvContBase):
    __guid__ = 'invCont.ShipDroneBay'
    __invControllerClass__ = invCtrl.ShipDroneBay


class ShipFighterBay(FighterInvCont):
    __guid__ = 'invCont.ShipFighterBay'
    __invControllerClass__ = invCtrl.ShipFighterBay


class ShipFuelBay(invCont._InvContBase):
    __guid__ = 'invCont.ShipFuelBay'
    __invControllerClass__ = invCtrl.ShipFuelBay


class ShipOreHold(invCont._InvContBase):
    __guid__ = 'invCont.ShipOreHold'
    __invControllerClass__ = invCtrl.ShipOreHold


class ShipGasHold(invCont._InvContBase):
    __guid__ = 'invCont.ShipGasHold'
    __invControllerClass__ = invCtrl.ShipGasHold


class ShipMineralHold(invCont._InvContBase):
    __guid__ = 'invCont.ShipMineralHold'
    __invControllerClass__ = invCtrl.ShipMineralHold


class ShipSalvageHold(invCont._InvContBase):
    __guid__ = 'invCont.ShipSalvageHold'
    __invControllerClass__ = invCtrl.ShipSalvageHold


class ShipShipHold(invCont._InvContBase):
    __guid__ = 'invCont.ShipShipHold'
    __invControllerClass__ = invCtrl.ShipShipHold


class ShipSmallShipHold(invCont._InvContBase):
    __guid__ = 'invCont.ShipSmallShipHold'
    __invControllerClass__ = invCtrl.ShipSmallShipHold


class ShipMediumShipHold(invCont._InvContBase):
    __guid__ = 'invCont.ShipMediumShipHold'
    __invControllerClass__ = invCtrl.ShipMediumShipHold


class ShipLargeShipHold(invCont._InvContBase):
    __guid__ = 'invCont.ShipLargeShipHold'
    __invControllerClass__ = invCtrl.ShipLargeShipHold


class ShipIndustrialShipHold(invCont._InvContBase):
    __guid__ = 'invCont.ShipIndustrialShipHold'
    __invControllerClass__ = invCtrl.ShipIndustrialShipHold


class ShipAmmoHold(invCont._InvContBase):
    __guid__ = 'invCont.ShipAmmoHold'
    __invControllerClass__ = invCtrl.ShipAmmoHold


class ShipCommandCenterHold(invCont._InvContBase):
    __guid__ = 'invCont.ShipCommandCenterHold'
    __invControllerClass__ = invCtrl.ShipCommandCenterHold


class ShipPlanetaryCommoditiesHold(invCont._InvContBase):
    __guid__ = 'invCont.ShipPlanetaryCommoditiesHold'
    __invControllerClass__ = invCtrl.ShipPlanetaryCommoditiesHold


class ShipFleetHangar(_BaseCelestialContainer):
    __guid__ = 'invCont.ShipFleetHangar'
    __invControllerClass__ = invCtrl.ShipFleetHangar


class ShipQuafeHold(invCont._InvContBase):
    __guid__ = 'invCont.ShipQuafeHold'
    __invControllerClass__ = invCtrl.ShipQuafeHold


class StationCorpDeliveries(invCont._InvContBase):
    __guid__ = 'invCont.StationCorpDeliveries'
    __invControllerClass__ = invCtrl.StationCorpDeliveries


class AssetSafetyDeliveries(invCont._InvContBase):
    __guid__ = 'invCont.AssetSafetyDeliveries'
    __invControllerClass__ = invCtrl.AssetSafetyDeliveries


class StationOwnerView(invCont._InvContBase):
    __guid__ = 'invCont.StationOwnerView'
    __invControllerClass__ = invCtrl.StationOwnerView

    def _GetInvController(self, attributes):
        return self.__invControllerClass__(itemID=attributes.itemID, ownerID=attributes.ownerID)


class StationItems(invCont._InvContBase):
    __guid__ = 'invCont.StationItems'
    __invControllerClass__ = invCtrl.StationItems
    __notifyevents__ = invCont._InvContBase.__notifyevents__ + ['OnItemNameChange']

    def OnItemNameChange(self, *args):
        self.Refresh()


class StationShips(invCont._InvContBase):
    __guid__ = 'invCont.StationShips'
    __invControllerClass__ = invCtrl.StationShips
    __notifyevents__ = invCont._InvContBase.__notifyevents__ + ['OnItemNameChange', 'ProcessActiveShipChanged']

    def OnItemNameChange(self, *args):
        self.Refresh()

    def ProcessActiveShipChanged(self, shipID, oldShipID):
        self.Refresh()


class StationCorpMember(invCont._InvContBase):
    __guid__ = 'invCont.StationCorpMember'
    __invControllerClass__ = invCtrl.StationCorpMember

    def ApplyAttributes(self, attributes):
        invCont._InvContBase.ApplyAttributes(self, attributes)
        sm.GetService('invCache').InvalidateLocationCache((const.containerHangar, self.invController.ownerID))

    def _GetInvController(self, attributes):
        return self.__invControllerClass__(itemID=attributes.itemID, ownerID=attributes.ownerID)

    def Refresh(self):
        sm.GetService('invCache').InvalidateLocationCache((const.containerHangar, self.invController.ownerID))
        invCont._InvContBase.Refresh(self)


class StationCorpHangar(invCont._InvContBase):
    __guid__ = 'invCont.StationCorpHangar'
    __invControllerClass__ = invCtrl.StationCorpHangar

    def _GetInvController(self, attributes):
        return self.__invControllerClass__(itemID=attributes.itemID, divisionID=attributes.divisionID)


class POSCorpHangar(invCont._InvContBase):
    __guid__ = 'invCont.POSCorpHangar'
    __invControllerClass__ = invCtrl.POSCorpHangar

    def _GetInvController(self, attributes):
        return self.__invControllerClass__(itemID=attributes.itemID, divisionID=attributes.divisionID)


class SpaceComponentInventory(_BaseCelestialContainer):
    __guid__ = 'invCont.SpaceComponentInventory'
    __invControllerClass__ = invCtrl.SpaceComponentInventory


class Structure(invCont._InvContBase):
    __guid__ = 'invCont.Structure'
    __invControllerClass__ = invCtrl.Structure


class StructureAmmoBay(invCont._InvContBase):
    __guid__ = 'invCont.StructureAmmoBay'
    __invControllerClass__ = invCtrl.StructureAmmoBay


class StructureFuelBay(invCont._InvContBase):
    __guid__ = 'invCont.StructureFuelBay'
    __invControllerClass__ = invCtrl.StructureFuelBay


class StructureFighterBay(FighterInvCont):
    __guid__ = 'invCont.StructureFighterBay'
    __invControllerClass__ = invCtrl.StructureFighterBay


class StructureItemHangar(invCont._InvContBase):
    __guid__ = 'invCont.StructureItemHangar'
    __invControllerClass__ = invCtrl.StructureItemHangar


class StructureShipHangar(invCont._InvContBase):
    __guid__ = 'invCont.StructureShipHangar'
    __invControllerClass__ = invCtrl.StructureShipHangar


class StructureDeliveriesHangar(invCont._InvContBase):
    __guid__ = 'invCont.StructureDeliveriesHangar'
    __invControllerClass__ = invCtrl.StructureDeliveriesHangar


class StructureCorpHangar(invCont._InvContBase):
    __guid__ = 'invCont.StructureCorpHangar'
    __invControllerClass__ = invCtrl.StructureCorpHangar

    def _GetInvController(self, attributes):
        return self.__invControllerClass__(itemID=attributes.itemID, divisionID=attributes.divisionID)


class AssetSafetyCorpContainer(StructureCorpHangar):
    __guid__ = 'invCont.AssetSafetyCorpContainer'
    __invControllerClass__ = invCtrl.AssetSafetyCorpContainer
