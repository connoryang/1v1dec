#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\fittingGhost\ghostControllerMixin.py
import signals
from dogma import const as dogmaConst
from eve.client.script.ui.shared.fitting.fittingController import ShipFittingController
from eve.client.script.ui.shared.fitting.fittingUtil import GHOST_FITTABLE_GROUPS, ModifiedAttribute, GetEffectiveHp
import evetypes
from eve.client.script.ui.shared.fittingGhost.fittingStanceButtons import GhostShipStanceButtonController
from shipfitting.fittingDogmaLocationUtil import GetAlignTime, CapacitorSimulator, GetFuelUsage
import inventorycommon.const as invConst
from shipfitting.fittingStuff import GetSlotTypeForType
EFFECTIVE_HP = 'effectiveHp'
ALIGN_TIME = 'alignTime'
FUEL_USAGE = 'fuelUsage'
CAP_DELTA = 'delta'
CAP_DELTA_PERCENTAGE = 'deltaPercentage'
LOAD_BALANCE = 'loadBalance'
TTL = 'TTL'

class GhostControllerMixin(object):
    __notifyevents__ = []

    def __init__(self, itemID, typeID = None):
        self.actuallyFittedModuleInfo = None
        self.on_slots_changed = signals.Signal()
        self.on_simulation_mode_changed = signals.Signal()
        self.on_simulation_state_changed = signals.Signal()
        self.attributesBeforeGhostfitting = {}

    def OnFittingSlotsChanged(self, *args):
        self.on_slots_changed()
        self._UpdateSlots()

    def OnSubSystemsChanged(self, *args):
        self.on_subsystem_fitted(animate=False)

    def OnSimulatedShipLoaded(self, itemID, typeID = None):
        self.SetDogmaLocation()
        self.UpdateItem(itemID, typeID)

    def IsSimulated(self):
        return sm.GetService('fittingSvc').IsShipSimulated()

    def GetSimulationMode(self):
        return sm.GetService('ghostFittingSvc').GetSimulationMode()

    def SetGhostFittedItem(self, ghostItem = None):
        self.ResetFakeItemInfo()
        if ghostItem and evetypes.GetCategoryID(ghostItem.typeID) not in GHOST_FITTABLE_GROUPS:
            return
        dogmaItem = None
        if ghostItem:
            self.attributesBeforeGhostfitting = self.GetCurrentAttributeValues()
            desiredFlag = int(self.dogmaLocation.dogmaStaticMgr.GetTypeAttribute2(ghostItem.typeID, dogmaConst.attributeSubSystemSlot))
            if desiredFlag in invConst.subSystemSlotFlags:
                self.RemoveModuleAndRememberIt(desiredFlag)
            dogmaItem = self.ghostFittingExtension.GhostFitItem(ghostItem)
        else:
            self.TryFitPreviouslyFittedType()
        self.ghostFittedItem = dogmaItem
        self.on_item_ghost_fitted()
        self.on_stats_changed()

    def RemoveModuleAndRememberIt(self, desiredFlag, *args):
        dogmaItem = self.dogmaLocation.GetSubSystemInFlag(None, desiredFlag)
        if dogmaItem and not getattr(dogmaItem, 'isPreviewItem', False):
            self.actuallyFittedModuleInfo = (desiredFlag, dogmaItem.typeID)
            self.ghostFittingExtension.UnFitItem(dogmaItem)

    def ResetFakeItemInfo(self):
        self.attributesBeforeGhostfitting = {}
        self.RemoveFakeItem()

    def RemoveFakeItem(self):
        if self.ghostFittedItem:
            dogmaItem = self.dogmaLocation.SafeGetDogmaItem(self.ghostFittedItem.itemID)
            if dogmaItem and getattr(dogmaItem, 'isPreviewItem', False):
                self.ghostFittingExtension.UnFitItem(dogmaItem)

    def TryFitPreviouslyFittedType(self):
        if self.actuallyFittedModuleInfo:
            flagID, moduleTypeID = self.actuallyFittedModuleInfo
            shipID = self.dogmaLocation.GetCurrentShipID()
            dogmaItem = sm.GetService('ghostFittingSvc').FitModuleToShipAndChangeState(shipID, flagID, moduleTypeID)
            self.actuallyFittedModuleInfo = None

    def AcceptPossibleRemovalTax(self, nodes):
        return True

    def OnSimulationStateChanged(self, newState):
        self.on_simulation_state_changed(newState)

    def OnSimulationModeChanged(self, newMode):
        for flagID, slot in self.slotsByFlagID.iteritems():
            slot.on_simulation_mode_changed(newMode)

        self.on_simulation_mode_changed(newMode)

    def GetStanceBtnControllerClass(self):
        if self.IsSimulated():
            return GhostShipStanceButtonController
        return ShipFittingController.GetStanceBtnControllerClass(self)

    def GetCurrentAttributeValues(self):
        delta, deltaPercentage, loadBalance, TTL_value = self._GetCapSimulatorValues()
        attributeValueDict = {dogmaConst.attributeScanResolution: self.GetScanResolution().value,
         dogmaConst.attributeMaxTargetRange: self.GetMaxTargetRange().value,
         dogmaConst.attributeMaxLockedTargets: self.GetMaxTargets().value,
         dogmaConst.attributeSignatureRadius: self.GetSignatureRadius().value,
         dogmaConst.attributeScanRadarStrength: self.GetScanRadarStrength().value,
         dogmaConst.attributeScanMagnetometricStrength: self.GetScanMagnetometricStrength().value,
         dogmaConst.attributeScanGravimetricStrength: self.GetScanGravimetricStrength().value,
         dogmaConst.attributeScanLadarStrength: self.GetScanLadarStrength().value,
         dogmaConst.attributeMass: self.GetMass().value,
         dogmaConst.attributeAgility: self.GetAgility().value,
         dogmaConst.attributeBaseWarpSpeed: self.GetBaseWarpSpeed().value,
         dogmaConst.attributeWarpSpeedMultiplier: self.GetWarpSpeedMultiplier().value,
         dogmaConst.attributeMaxVelocity: self.GetMaxVelocity().value,
         dogmaConst.attributeCpuLoad: self.GetCPULoad().value,
         dogmaConst.attributeCpuOutput: self.GetCPUOutput().value,
         dogmaConst.attributePowerLoad: self.GetPowerLoad().value,
         dogmaConst.attributePowerOutput: self.GetPowerOutput().value,
         dogmaConst.attributeUpgradeLoad: self.GetCalibrationLoad().value,
         dogmaConst.attributeUpgradeCapacity: self.GetCalibrationOutput().value,
         dogmaConst.attributeShieldCapacity: self.GetShieldHp().value,
         dogmaConst.attributeArmorHP: self.GetArmorHp().value,
         dogmaConst.attributeHp: self.GetStructureHp().value,
         dogmaConst.attributeShieldRechargeRate: self.GetRechargeRate().value,
         dogmaConst.attributeShieldEmDamageResonance: self.GetShieldEmDamageResonance().value,
         dogmaConst.attributeShieldExplosiveDamageResonance: self.GetShieldExplosiveDamageResonance().value,
         dogmaConst.attributeShieldKineticDamageResonance: self.GetShieldKineticDamageResonance().value,
         dogmaConst.attributeShieldThermalDamageResonance: self.GetShieldThermalDamageResonance().value,
         dogmaConst.attributeArmorEmDamageResonance: self.GetArmorEmDamageResonance().value,
         dogmaConst.attributeArmorExplosiveDamageResonance: self.GetArmorExplosiveDamageResonance().value,
         dogmaConst.attributeArmorKineticDamageResonance: self.GetArmorKineticDamageResonance().value,
         dogmaConst.attributeArmorThermalDamageResonance: self.GetArmorThermalDamageResonance().value,
         dogmaConst.attributeEmDamageResonance: self.GetStructureEmDamageResonance().value,
         dogmaConst.attributeExplosiveDamageResonance: self.GetStructureExplosiveDamageResonance().value,
         dogmaConst.attributeKineticDamageResonance: self.GetStructureKineticDamageResonance().value,
         dogmaConst.attributeThermalDamageResonance: self.GetStructureThermalDamageResonance().value,
         dogmaConst.attributeCapacity: self.GetCargoCapacity().value,
         dogmaConst.attributeDroneCapacity: self.GetDroneCapacity().value,
         dogmaConst.attributeCapacitorCapacity: self.GetCapacitorCapacity().value,
         dogmaConst.attributeRechargeRate: self.GetCapRechargeRate().value,
         CAP_DELTA: delta,
         CAP_DELTA_PERCENTAGE: deltaPercentage,
         LOAD_BALANCE: loadBalance,
         TTL: TTL_value,
         EFFECTIVE_HP: self.GetEffectiveHp().value,
         ALIGN_TIME: self.GetAlignTime().value,
         FUEL_USAGE: self.GetFuelUsage().value}
        return attributeValueDict

    def GetScanResolution(self):
        return self.GetStatsInfo(dogmaConst.attributeScanResolution, higherIsBetter=False)

    def GetMaxTargetRange(self):
        return self.GetStatsInfo(dogmaConst.attributeMaxTargetRange)

    def GetMaxTargets(self):
        return self.GetStatsInfo(dogmaConst.attributeMaxLockedTargets)

    def GetSignatureRadius(self):
        return self.GetStatsInfo(dogmaConst.attributeSignatureRadius, higherIsBetter=False)

    def GetScanRadarStrength(self):
        return self.GetStatsInfo(dogmaConst.attributeScanRadarStrength)

    def GetScanMagnetometricStrength(self):
        return self.GetStatsInfo(dogmaConst.attributeScanMagnetometricStrength)

    def GetScanGravimetricStrength(self):
        return self.GetStatsInfo(dogmaConst.attributeScanGravimetricStrength)

    def GetScanLadarStrength(self):
        return self.GetStatsInfo(dogmaConst.attributeScanLadarStrength)

    def GetMass(self):
        return self.GetStatsInfo(dogmaConst.attributeMass, higherIsBetter=False)

    def GetAgility(self):
        return self.GetStatsInfo(dogmaConst.attributeAgility, higherIsBetter=False)

    def GetBaseWarpSpeed(self):
        return self.GetStatsInfo(dogmaConst.attributeBaseWarpSpeed)

    def GetWarpSpeedMultiplier(self):
        return self.GetStatsInfo(dogmaConst.attributeWarpSpeedMultiplier)

    def GetMaxVelocity(self):
        return self.GetStatsInfo(dogmaConst.attributeMaxVelocity)

    def GetCPULoad(self):
        return self.GetStatsInfo(dogmaConst.attributeCpuLoad, higherIsBetter=False)

    def GetCPUOutput(self):
        return self.GetStatsInfo(dogmaConst.attributeCpuOutput)

    def GetPowerLoad(self):
        return self.GetStatsInfo(dogmaConst.attributePowerLoad, higherIsBetter=False)

    def GetPowerOutput(self):
        return self.GetStatsInfo(dogmaConst.attributePowerOutput)

    def GetCalibrationLoad(self):
        return self.GetStatsInfo(dogmaConst.attributeUpgradeLoad, higherIsBetter=False)

    def GetCalibrationOutput(self):
        return self.GetStatsInfo(dogmaConst.attributeUpgradeCapacity)

    def GetShieldHp(self):
        return self.GetStatsInfo(dogmaConst.attributeShieldCapacity)

    def GetArmorHp(self):
        return self.GetStatsInfo(dogmaConst.attributeArmorHP)

    def GetStructureHp(self):
        return self.GetStatsInfo(dogmaConst.attributeHp)

    def GetRechargeRate(self):
        return self.GetStatsInfo(dogmaConst.attributeShieldRechargeRate)

    def GetShieldEmDamageResonance(self):
        return self.GetStatsInfo(dogmaConst.attributeShieldEmDamageResonance, higherIsBetter=False)

    def GetShieldExplosiveDamageResonance(self):
        return self.GetStatsInfo(dogmaConst.attributeShieldExplosiveDamageResonance, higherIsBetter=False)

    def GetShieldKineticDamageResonance(self):
        return self.GetStatsInfo(dogmaConst.attributeShieldKineticDamageResonance, higherIsBetter=False)

    def GetShieldThermalDamageResonance(self):
        return self.GetStatsInfo(dogmaConst.attributeShieldThermalDamageResonance, higherIsBetter=False)

    def GetArmorEmDamageResonance(self):
        return self.GetStatsInfo(dogmaConst.attributeArmorEmDamageResonance, higherIsBetter=False)

    def GetArmorExplosiveDamageResonance(self):
        return self.GetStatsInfo(dogmaConst.attributeArmorExplosiveDamageResonance, higherIsBetter=False)

    def GetArmorKineticDamageResonance(self):
        return self.GetStatsInfo(dogmaConst.attributeArmorKineticDamageResonance, higherIsBetter=False)

    def GetArmorThermalDamageResonance(self):
        return self.GetStatsInfo(dogmaConst.attributeArmorThermalDamageResonance, higherIsBetter=False)

    def GetStructureEmDamageResonance(self):
        return self.GetStatsInfo(dogmaConst.attributeEmDamageResonance, higherIsBetter=False)

    def GetStructureExplosiveDamageResonance(self):
        return self.GetStatsInfo(dogmaConst.attributeExplosiveDamageResonance, higherIsBetter=False)

    def GetStructureKineticDamageResonance(self):
        return self.GetStatsInfo(dogmaConst.attributeKineticDamageResonance, higherIsBetter=False)

    def GetStructureThermalDamageResonance(self):
        return self.GetStatsInfo(dogmaConst.attributeThermalDamageResonance, higherIsBetter=False)

    def GetCargoCapacity(self):
        return self.GetStatsInfo(dogmaConst.attributeCapacity)

    def GetDroneCapacity(self):
        return self.GetStatsInfo(dogmaConst.attributeDroneCapacity)

    def GetCapacitorCapacity(self):
        return self.GetStatsInfo(dogmaConst.attributeCapacitorCapacity)

    def GetCapRechargeRate(self):
        return self.GetStatsInfo(dogmaConst.attributeRechargeRate, higherIsBetter=False)

    def GetFighterCapacity(self):
        return self.GetStatsInfo(dogmaConst.attributeFighterCapacity)

    def GetStatsInfo(self, attributeID, higherIsBetter = True):
        oldValue = self.attributesBeforeGhostfitting.get(attributeID, None)
        currentValue = self.GetAttribute(attributeID)
        return ModifiedAttribute(value=currentValue, oldValue=oldValue, higherIsBetter=higherIsBetter, attributeID=attributeID)

    def GetEffectiveHp(self):
        oldValue = self.attributesBeforeGhostfitting.get(EFFECTIVE_HP, None)
        currentValue = GetEffectiveHp(self)
        return ModifiedAttribute(value=currentValue, oldValue=oldValue)

    def GetAlignTime(self):
        oldValue = self.attributesBeforeGhostfitting.get(ALIGN_TIME, None)
        currentValue = GetAlignTime(self.dogmaLocation)
        return ModifiedAttribute(value=currentValue, oldValue=oldValue, higherIsBetter=False)

    def GetFuelUsage(self):
        oldValue = self.attributesBeforeGhostfitting.get(FUEL_USAGE, None)
        currentValue = GetFuelUsage(self.dogmaLocation)
        return ModifiedAttribute(value=currentValue, oldValue=oldValue, higherIsBetter=False)

    def _GetCapSimulatorValues(self):
        dogmaLocation = self.dogmaLocation
        peakRechargeRate, totalCapNeed, loadBalance, TTL_value = CapacitorSimulator(dogmaLocation, dogmaLocation.GetCurrentShipID())
        delta = round((peakRechargeRate - totalCapNeed) * 1000, 2)
        deltaPercentage = round((peakRechargeRate - totalCapNeed) / peakRechargeRate * 100, 1)
        return (delta,
         deltaPercentage,
         loadBalance,
         TTL_value)

    def GetCapSimulatorInfos(self):
        delta, deltaPercentage, loadBalance, TTL_value = self._GetCapSimulatorValues()
        oldValue = self.attributesBeforeGhostfitting.get(CAP_DELTA, None)
        deltaInfo = ModifiedAttribute(value=delta, oldValue=oldValue)
        oldValue = self.attributesBeforeGhostfitting.get(CAP_DELTA_PERCENTAGE, None)
        deltaPercentageInfo = ModifiedAttribute(value=deltaPercentage, oldValue=oldValue)
        oldValue = self.attributesBeforeGhostfitting.get(LOAD_BALANCE, None)
        loadBalanceInfo = ModifiedAttribute(value=loadBalance, oldValue=oldValue)
        oldValue = self.attributesBeforeGhostfitting.get(TTL, None)
        ttlInfo = ModifiedAttribute(value=TTL_value or 0, oldValue=oldValue)
        return [deltaInfo,
         deltaPercentageInfo,
         loadBalanceInfo,
         ttlInfo]
