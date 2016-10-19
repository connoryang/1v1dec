#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\fitting\fittingController.py
import sys
from collections import defaultdict
import carbonui.const as uiconst
import dogma.const as dogmaConst
import evetypes
import inventorycommon.const as invConst
import shipmode
import signals
from carbon.common.script.util.logUtil import LogInfo, LogException
from eve.client.script.environment.t3shipSvc import NotEnoughSubSystems
from eve.client.script.ui.inflight.shipstance import ShipStanceButtonController
from eve.client.script.ui.shared.fitting.fittingSlotController import FittingSlotController, ShipFittingSlotController, StructureFittingSlotController, StructureFittingServiceSlotController
from eve.client.script.ui.shared.fitting.fittingStatsChanges import FittingStatsChanges
from eve.client.script.ui.shared.fitting.fittingUtil import IsCharge, ModifiedAttribute, NUM_SUBSYSTEM_SLOTS, TryFit, GHOST_FITTABLE_GROUPS, GetShipAttributeWithDogmaLocation, GetTypeIDForController
from eve.client.script.ui.shared.fittingGhost.controllerGhostFittingExtension import FittingControllerGhostFittingExtension
from eve.client.script.ui.util.uix import skillfittingTutorial
from evegraphics.utils import BuildSOFDNAFromTypeID
from inventorycommon.util import IsShipFittingFlag, IsModularShip

class FittingController(object):
    __notifyevents__ = ['OnDogmaAttributeChanged',
     'OnStanceActive',
     'OnDogmaItemChange',
     'OnGodmaFlushLocation',
     'OnAttributes',
     'OnAttribute',
     'ProcessActiveShipChanged',
     'OnPostCfgDataChanged',
     'OnDogmaDronesChanged']
    SLOTGROUPS = ()
    SLOTGROUP_LAYOUT_ARCS = {0: (-35.0, 82.0),
     1: (54.0, 82.0),
     2: (143.0, 82.0),
     3: (233.0, 51.0),
     4: (287.0, 31.0)}
    SLOT_CLASS = FittingSlotController

    def __init__(self, itemID, typeID = None):
        sm.RegisterNotify(self)
        self.ghostFittingExtension = FittingControllerGhostFittingExtension()
        self._itemID = itemID
        self._typeID = typeID or GetTypeIDForController(itemID)
        self.SetDogmaLocation()
        self.ghostFittedItem = None
        self._skinMaterialSetID = None
        self.on_new_itemID = signals.Signal()
        self.on_stats_changed = signals.Signal()
        self.on_hardpoints_fitted = signals.Signal()
        self.on_subsystem_fitted = signals.Signal()
        self.on_module_online_state = signals.Signal()
        self.on_item_ghost_fitted = signals.Signal()
        self.on_name_changed = signals.Signal()
        self.on_skin_material_changed = signals.Signal()
        self.on_stance_activated = signals.Signal()
        self.on_should_close = signals.Signal()
        self.on_slots_with_menu_changed = signals.Signal()
        self.on_controller_changing = signals.Signal()
        self.on_drones_changed = signals.Signal()
        self.slotsByFlagID = {}
        self.slotFlagWithMenu = None
        self.ConstructSlotControllers()
        self._UpdateSkinMaterial()

    def GetSlotClass(self, flagID):
        return self.SLOT_CLASS

    def SetDogmaLocation(self):
        if self.IsSimulated():
            dogmaLocation = self.ghostFittingExtension.GetDogmaLocation()
        else:
            dogmaLocation = sm.GetService('clientDogmaIM').GetDogmaLocation()
        self.dogmaLocation = dogmaLocation

    def ConstructSlotControllers(self):
        for slot in self.slotsByFlagID.values():
            slot.Close()

        self.slotsByFlagID = {}
        self.slotsByGroups = {}
        for groupIdx, flagIDs in self.SLOTGROUPS:
            group = []
            for i, flagID in enumerate(flagIDs):
                invItem = self.GetFittedModulesByFlagID().get(flagID, None)
                slotClass = self.GetSlotClass(flagID)
                slotController = slotClass(flagID=flagID, parentController=self)
                self.slotsByFlagID[flagID] = slotController
                group.append(slotController)

            self.slotsByGroups[groupIdx] = group

        self._UpdateSlots()

    def GetSlotsByGroups(self):
        return self.slotsByGroups

    def GetTotalNumSlots(self):
        return sum([ len(group) for group in self.slotsByGroups.itervalues() ])

    def _UpdateSlots(self):
        for flagID, slot in self.slotsByFlagID.iteritems():
            self.SetSlotModuleAndChargeIDs(slot, flagID)

        for slot in self.slotsByFlagID.itervalues():
            slot.on_item_fitted()

    def OnSlotAttributeChanged(self, flagID, shipID, itemID, attributeID, value):
        slot = self.slotsByFlagID[flagID]
        self.SetSlotModuleAndChargeIDs(slot, flagID)
        slot.OnSlotAttributeChanged(shipID, itemID, attributeID, value)

    def SetSlotModuleAndChargeIDs(self, slot, flagID):
        module, charge = self._GetModuleAndCharge(flagID=flagID)
        chargeItemID = charge.itemID if charge else None
        moduleItemID = module.itemID if module else None
        slot.SetModuleAndChargeIDs(moduleItemID, chargeItemID)

    def UpdateItem(self, itemID, typeID = None):
        oldItemID = self._itemID
        oldTypeID = self._typeID
        self._itemID = itemID
        if typeID is None:
            typeID = GetTypeIDForController(itemID)
        self._typeID = typeID
        if self.IsControllerChanging(itemID, typeID, oldItemID, oldTypeID):
            self.on_controller_changing(itemID)
        self._UpdateSkinMaterial()
        self.on_new_itemID()
        self._UpdateSlots()

    def _UpdateSkinMaterial(self):
        skin = sm.GetService('skinSvc').GetAppliedSkin(session.charid, self._itemID, self._typeID)
        self._skinMaterialSetID = skin.materialSetID if skin else None

    def SetSkinMaterialSetID(self, materialSetID):
        if materialSetID == self._skinMaterialSetID:
            return
        self._skinMaterialSetID = materialSetID
        self.on_skin_material_changed()

    def _GetDogmaItem(self):
        return self.dogmaLocation.dogmaItems[self._itemID]

    def GetDogmaLocation(self):
        return self.dogmaLocation

    def GetItemID(self):
        return self._itemID

    def GetTypeID(self):
        if self._typeID:
            return self._typeID
        return self._GetDogmaItem().typeID

    def IsShip(self):
        return evetypes.GetCategoryID(self.GetTypeID()) == const.categoryShip

    def GetModelDNA(self):
        return BuildSOFDNAFromTypeID(self.GetTypeID(), materialSetID=self._skinMaterialSetID)

    def GetAttribute(self, attributeID):
        return GetShipAttributeWithDogmaLocation(self.dogmaLocation, self.GetItemID(), attributeID)

    def GetFittedModules(self):
        return self._GetDogmaItem().GetFittedItems().values()

    def SetGhostFittedItem(self, ghostItem = None):
        if ghostItem and evetypes.GetCategoryID(ghostItem.typeID) not in GHOST_FITTABLE_GROUPS:
            return
        if self.IsSwitchingShips():
            return
        self.ghostFittedItem = ghostItem
        self.on_item_ghost_fitted()
        self.on_stats_changed()

    def GetGhostFittedItem(self):
        return self.ghostFittedItem

    def GetNumTurretsAndLaunchersFitted(self):
        turretsFitted = 0
        launchersFitted = 0
        modulesByGroupInShip = {}
        for module in self.GetFittedModules():
            if module.groupID not in modulesByGroupInShip:
                modulesByGroupInShip[module.groupID] = []
            modulesByGroupInShip[module.groupID].append(module)
            if self.dogmaLocation.dogmaStaticMgr.TypeHasEffect(module.typeID, dogmaConst.effectLauncherFitted):
                launchersFitted += 1
            if self.dogmaLocation.dogmaStaticMgr.TypeHasEffect(module.typeID, dogmaConst.effectTurretFitted):
                turretsFitted += 1

        return (launchersFitted, turretsFitted)

    def GetFittedModulesByFlagID(self):
        modulesByFlag = {}
        for module in self.GetFittedModules():
            modulesByFlag[module.flagID, IsCharge(module.typeID)] = module

        return modulesByFlag

    def GetFittedModulesByGroupID(self):
        modulesByGroupInShip = defaultdict(list)
        for module in self.GetFittedModules():
            modulesByGroupInShip[module.groupID].append(module)

        return modulesByGroupInShip

    def _GetModuleAndCharge(self, flagID):
        module = charge = None
        for item in self.GetFittedModules():
            if item.flagID == flagID:
                if IsCharge(item.typeID):
                    charge = item
                else:
                    module = item

        return (module, charge)

    def GetSlotAdditionInfo(self, typeAttributesByID):
        hiSlotAddition = 0
        medSlotAddition = 0
        lowSlotAddition = 0
        if self.GetItemID() and self.IsShip():
            subSystemSlot = typeAttributesByID.get(dogmaConst.attributeSubSystemSlot, None)
            if subSystemSlot is not None:
                slotOccupant = self.dogmaLocation.GetSubSystemInFlag(self.GetItemID(), int(subSystemSlot))
                if slotOccupant is not None:
                    attributesByName = self.dogmaLocation.dogmaStaticMgr.attributesByName
                    GTA = lambda attributeID: self.dogmaLocation.dogmaStaticMgr.GetTypeAttribute2(slotOccupant.typeID, attributeID)
                    hiSlotAddition = -GTA(attributesByName['hiSlotModifier'].attributeID)
                    medSlotAddition = -GTA(attributesByName['medSlotModifier'].attributeID)
                    lowSlotAddition = -GTA(attributesByName['lowSlotModifier'].attributeID)
        return (lowSlotAddition, medSlotAddition, hiSlotAddition)

    def GetHardpointAdditionInfo(self, typeAttributesByID):
        turretAddition = 0
        launcherAddition = 0
        if self.GetItemID() and self.IsShip():
            subSystemSlot = typeAttributesByID.get(dogmaConst.attributeSubSystemSlot, None)
            if subSystemSlot is not None:
                slotOccupant = self.dogmaLocation.GetSubSystemInFlag(self.GetItemID(), int(subSystemSlot))
                if slotOccupant is not None:
                    attributesByName = self.dogmaLocation.dogmaStaticMgr.attributesByName
                    GTA = lambda attributeID: self.dogmaLocation.dogmaStaticMgr.GetTypeAttribute2(slotOccupant.typeID, attributeID)
                    turretAddition = -GTA(attributesByName['turretHardPointModifier'].attributeID)
                    launcherAddition = -GTA(attributesByName['launcherHardPointModifier'].attributeID)
        turretAddition += typeAttributesByID.get(dogmaConst.attributeTurretHardpointModifier, 0.0)
        launcherAddition += typeAttributesByID.get(dogmaConst.attributeLauncherHardPointModifier, 0.0)
        return (turretAddition, launcherAddition)

    def OnDogmaAttributeChanged(self, shipID, itemID, attributeID, value):
        if shipID == self.GetItemID():
            if attributeID == const.attributeIsOnline:
                self.on_stats_changed()
                if itemID in self.dogmaLocation.dogmaItems:
                    dogmaItem = self.dogmaLocation.dogmaItems[itemID]
                    self.on_module_online_state(dogmaItem)
            if attributeID == const.attributeUpgradeSlotsLeft:
                self.on_stats_changed()
        if attributeID in (const.attributeIsOnline, const.attributeQuantity):
            try:
                dogmaItem = self.dogmaLocation.GetDogmaItem(itemID)
                flagID = dogmaItem.flagID
            except KeyError:
                if isinstance(itemID, tuple) and itemID[0] == self.GetItemID():
                    flagID = itemID[1]
                else:
                    return

            try:
                self.OnSlotAttributeChanged(flagID, shipID, itemID, attributeID, value)
            except KeyError:
                pass

    def OnPostCfgDataChanged(self, cfgname, entry, *args):
        if cfgname == 'evelocations' and entry[0] == self.GetItemID():
            self.on_name_changed()

    def OnDogmaDronesChanged(self):
        self.on_drones_changed()

    def OnGodmaFlushLocation(self, locationID):
        pass

    def OnDogmaItemChange(self, item, change):
        locationOrFlagIsInChange = const.ixFlag in change or const.ixLocationID in change
        didStacksizeFlagOrLocationChange = const.ixStackSize in change or locationOrFlagIsInChange
        if not didStacksizeFlagOrLocationChange:
            return
        oldLocationID = change.get(const.ixLocationID, None)
        if self.GetItemID() not in (oldLocationID, item.locationID):
            return
        if item.groupID in const.turretModuleGroups:
            self.on_hardpoints_fitted()
        updateSlotsAndStats = False
        if self._IsSubsystemBeingLoaded(change, item):
            self.on_subsystem_fitted(throttle=True)
            updateSlotsAndStats = True
        elif locationOrFlagIsInChange:
            updateSlotsAndStats = True
        if updateSlotsAndStats:
            self._UpdateSlots()
            self.on_stats_changed()

    def OnAttribute(self, attributeName, item, value, updateStats = 1):
        self.WaitForShip()
        try:
            self.GetService('godma').GetItem(item.itemID)
        except AttributeError:
            sys.exc_clear()
            return

        if updateStats:
            self.on_stats_changed()

    def OnAttributes(self, changeList):
        self.WaitForShip()
        slotsChanged = False
        for attributeName, item, value in changeList:
            if attributeName in ('hiSlots', 'medSlots', 'lowSlots'):
                slotsChanged = True

        self.on_stats_changed()
        if slotsChanged:
            self._UpdateSlots()

    def ProcessActiveShipChanged(self, shipID, oldShipID):
        if not self.IsSimulated():
            self.UpdateItem(shipID)

    def _IsSubsystemBeingLoaded(self, change, item):
        locationOrFlagIsInChange = const.ixLocationID in change or const.ixFlag in change
        if not locationOrFlagIsInChange:
            return False
        if item.locationID != self.GetItemID():
            return False
        if not IsShipFittingFlag(item.flagID):
            return False
        if item.categoryID != const.categorySubSystem:
            return False
        return True

    def Close(self):
        self.on_stats_changed.clear()
        self.on_subsystem_fitted.clear()
        self.on_hardpoints_fitted.clear()
        self.on_new_itemID.clear()
        self.on_module_online_state.clear()
        self.on_item_ghost_fitted.clear()
        self.on_name_changed.clear()
        self.on_skin_material_changed.clear()
        self.on_stance_activated.clear()
        self.on_should_close.clear()
        self.on_slots_with_menu_changed.clear()
        self.on_controller_changing.clear()
        self.on_drones_changed.clear()
        sm.UnregisterNotify(self)

    def OnDropData(self, dragObj, nodes):
        if not self.AcceptPossibleRemovalTax(nodes):
            return
        skills = sm.GetService('skills').GetSkills()
        for node in nodes:
            if node.Get('__guid__', None) in ('xtriui.InvItem', 'listentry.InvItem'):
                requiredSkills = sm.GetService('skills').GetRequiredSkills(node.rec.typeID)
                for skillID, level in requiredSkills.iteritems():
                    if getattr(skills.get(skillID, None), 'skillLevel', 0) < level:
                        sm.GetService('tutorial').OpenTutorialSequence_Check(skillfittingTutorial)
                        break

        recs = []
        for node in nodes:
            if getattr(node, 'rec', None):
                recs.append(node.rec)

        TryFit(recs, self.GetItemID())

    def AcceptPossibleRemovalTax(self, nodes):
        acceptPossibleRemovalTax = sm.GetService('invCache').AcceptPossibleRemovalTax([ n.item for n in nodes ])
        return acceptPossibleRemovalTax

    def OnStanceActive(self, shipID, stanceID):
        if self._itemID == shipID:
            self.on_stance_activated(stanceID)

    def WaitForShip(self):
        self.dogmaLocation.WaitForShip()

    def IsSwitchingShips(self):
        return self.dogmaLocation.IsSwitchingShips()

    def GetNumTurretsFitted(self):
        return self._GetNumHardpointsFitted(const.effectTurretFitted)

    def GetNumLaunchersFitted(self):
        return self._GetNumHardpointsFitted(const.effectLauncherFitted)

    def _GetNumHardpointsFitted(self, effect):
        hardpointsFitted = 0
        for module in self.GetFittedModules():
            if self.dogmaLocation.dogmaStaticMgr.TypeHasEffect(module.typeID, effect):
                hardpointsFitted += 1

        return hardpointsFitted

    def GetNumTurretHardpointsLeft(self):
        return self.GetAttribute(const.attributeTurretSlotsLeft)

    def GetNumLauncherHardpointsLeft(self):
        return self.GetAttribute(const.attributeLauncherSlotsLeft)

    def GetNumHiSlots(self):
        return self.GetAttribute(const.attributeHiSlots)

    def GetNumMedSlots(self):
        return self.GetAttribute(const.attributeMedSlots)

    def GetNumLowSlots(self):
        return self.GetAttribute(const.attributeLowSlots)

    def GetNumSubsystemSlots(self):
        if self.HasSubsystems():
            return NUM_SUBSYSTEM_SLOTS
        else:
            return 0

    def HasSubsystems(self):
        return bool(self.GetAttribute(const.attributeTechLevel) > 2)

    def HasStance(self):
        return shipmode.ship_has_stances(self.GetTypeID())

    def StripFitting(self, prompt = True):
        if prompt and uicore.Message('AskStripShip', None, uiconst.YESNO, suppress=uiconst.ID_YES) != uiconst.ID_YES:
            return
        sm.GetService('invCache').GetInventoryFromId(self.GetItemID()).StripFitting()

    def GetCharges(self):
        return self.dogmaLocation.GetSublocations(self.GetItemID())

    def GetModel(self):
        typeID = self.GetTypeID()
        try:
            if IsModularShip(typeID):
                try:
                    isSimulated = self.IsSimulated()
                    return sm.GetService('t3ShipSvc').MakeModularShipFromShipItem(self._GetDogmaItem(), isSimulated)
                except NotEnoughSubSystems:
                    LogInfo('CreateAndActiveShipModel - Not enough subsystems do display ship in fittingWindow')
                    return
                except:
                    LogException('failed bulding modular ship')
                    return

            else:
                spaceObjectFactory = sm.GetService('sofService').spaceObjectFactory
                return spaceObjectFactory.BuildFromDNA(self.GetModelDNA())
        except Exception as e:
            LogException(str(e))

    def GetScenePath(self):
        if self.IsSimulated():
            return self.ghostFittingExtension.GetScenePath()
        else:
            return 'res:/dx9/scene/fitting/fitting.red'

    def GetGhostFittedTypeID(self):
        if self.ghostFittedItem:
            return self.ghostFittedItem.typeID
        else:
            return None

    def GetPowerLoad(self):
        fittingChanges = FittingStatsChanges(self.GetGhostFittedTypeID())
        powerLoad = self.GetAttribute(const.attributePowerLoad)
        xtraPowerload = fittingChanges.GetExtraPowerLoad()
        return ModifiedAttribute(value=powerLoad, addition=xtraPowerload, higherIsBetter=False)

    def GetPowerOutput(self):
        ghostTypeID = self.GetGhostFittedTypeID()
        fittingChanges = FittingStatsChanges(ghostTypeID)
        powerOutput = self.GetAttribute(const.attributePowerOutput)
        multiplyPower = fittingChanges.GetMultiplyPower()
        xtraPower = fittingChanges.GetExtraPower()
        return ModifiedAttribute(value=powerOutput, multiplier=multiplyPower, addition=xtraPower)

    def GetCPULoad(self):
        fittingChanges = FittingStatsChanges(self.GetGhostFittedTypeID())
        cpuLoad = self.GetAttribute(const.attributeCpuLoad)
        xtraCpuLoad = fittingChanges.GetExtraCpuLoad()
        return ModifiedAttribute(value=cpuLoad, addition=xtraCpuLoad, higherIsBetter=False)

    def GetCPUOutput(self):
        fittingChanges = FittingStatsChanges(self.GetGhostFittedTypeID())
        cpuOutput = self.GetAttribute(const.attributeCpuOutput)
        multiplyCpu = fittingChanges.GetMultiplyCpu()
        xtraCpu = fittingChanges.GetExtraCpu()
        return ModifiedAttribute(value=cpuOutput, multiplier=multiplyCpu, addition=xtraCpu)

    def GetCalibrationLoad(self):
        fittingChanges = FittingStatsChanges(self.GetGhostFittedTypeID())
        calibrationLoad = self.GetAttribute(const.attributeUpgradeLoad)
        caliXtraLoad = fittingChanges.GetExtraCalibrationLoad()
        return ModifiedAttribute(value=calibrationLoad, addition=caliXtraLoad, higherIsBetter=False)

    def GetCalibrationOutput(self):
        fittingChanges = FittingStatsChanges(self.GetGhostFittedTypeID())
        calibrationOutput = self.GetAttribute(const.attributeUpgradeCapacity)
        return ModifiedAttribute(value=calibrationOutput)

    def GetCPUPercentage(self):
        return round(100.0 * self.GetCPULoad().value / self.GetCPUOutput().value, 1)

    def GetPowerPercentage(self):
        return round(100.0 * self.GetPowerLoad().value / self.GetPowerOutput().value, 1)

    def GetCalibrationPercentage(self):
        return round(100.0 * self.GetCalibrationLoad().value / self.GetCalibrationOutput().value, 1)

    def GetSlotController(self, flagID):
        return self.slotsByFlagID[flagID]

    def UpdateStats(self):
        self.on_stats_changed()

    def IsSimulated(self):
        return False

    def GetCurrentAttributeValues(self):
        return {}

    def IsFittableType(self, typeID):
        return False

    def SetSlotWithMenu(self, newFlagID):
        oldFlagID = self.slotFlagWithMenu
        self.slotFlagWithMenu = newFlagID
        self.on_slots_with_menu_changed(oldFlagID, newFlagID)

    def HasFighterBay(self):
        return self.dogmaLocation.GetAccurateAttributeValue(self.GetItemID(), const.attributeFighterCapacity)

    def IsControllerChanging(self, newItemID, newTypeID, oldItemID, oldTypeID):
        oldTypeID = oldTypeID or GetTypeIDForController(oldItemID)
        newTypeID = newTypeID or GetTypeIDForController(newItemID)
        if evetypes.GetCategoryID(oldTypeID) != evetypes.GetCategoryID(newTypeID):
            return True
        return False

    def ControllerForCategory(self):
        pass

    def HasNavigationPanel(self):
        return True

    def HasFuelPanel(self):
        return False

    def HasDronePanel(self):
        return True


class ShipFittingController(FittingController):
    SLOT_CLASS = ShipFittingSlotController
    SLOTGROUPS = ((0, invConst.hiSlotFlags),
     (1, invConst.medSlotFlags),
     (2, invConst.loSlotFlags),
     (3, invConst.subSystemSlotFlags),
     (4, invConst.rigSlotFlags))

    def IsFittableType(self, typeID):
        return evetypes.GetCategoryID(typeID) in (const.categoryCharge, const.categorySubSystem, const.categoryModule)

    def ControllerForCategory(self):
        return const.categoryShip

    def GetStanceBtnControllerClass(self):
        return ShipStanceButtonController


class StructureFittingController(FittingController):
    SLOT_CLASS = StructureFittingSlotController
    SLOT_CLASS_SERVICES = StructureFittingServiceSlotController
    SLOTGROUPS = ((0, invConst.hiSlotFlags),
     (1, invConst.medSlotFlags),
     (2, invConst.loSlotFlags),
     (4, invConst.rigSlotFlags),
     (-1, invConst.serviceSlotFlags))

    def IsFittableType(self, typeID):
        return evetypes.GetCategoryID(typeID) in (const.categoryStructureModule, const.categoryCharge)

    def GetSlotClass(self, flagID):
        if flagID in invConst.serviceSlotFlags:
            return self.SLOT_CLASS_SERVICES
        return self.SLOT_CLASS

    def ControllerForCategory(self):
        return const.categoryStructure

    def GetStanceBtnControllerClass(self):
        return ShipStanceButtonController

    def HasNavigationPanel(self):
        return False

    def HasFuelPanel(self):
        return True

    def HasDronePanel(self):
        return False
