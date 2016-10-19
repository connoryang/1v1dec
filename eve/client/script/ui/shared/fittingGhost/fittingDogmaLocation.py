#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\fittingGhost\fittingDogmaLocation.py
import weakref
from carbon.common.lib import telemetry
from dogma.attributes.limit import LimitAttributeOnItem
from dogma.dogmaWrappers import WrappedMethod
from dogma.effects.environment import Environment
from dogma.items.structureModuleDogmaItem import GhostStructureModuleDogmaItem
from eve.client.script.ui.shared.fitting.fittingUtil import GetSensorStrengthAttribute
from eve.client.script.ui.shared.fittingGhost import FAKE_FLAGID
from eve.client.script.ui.shared.fittingGhost.ghostFittingUtil import GhostFittingDataObject
from eve.common.script.dogma.baseDogmaLocation import BaseDogmaLocation
from dogma.items.dblessDogmaItem import DBLessDogmaItem
from dogma.items.droneDogmaItem import DroneDogmaItem
from dogma.items.moduleDogmaItem import GhostModuleDogmaItem
from dogma.items.shipDogmaItem import GhostShipDogmaItem
from eveuniverse.security import securityClassZeroSec
from inventorycommon.util import IsShipFittable, IsStructureFittable
from shipfitting.fittingDogmaLocationUtil import GetFittingItemDragData, GetTurretAndMissileDps, CapacitorSimulator, GetAlphaStrike
from shipfitting.fittingDogmaLocationUtil import SelectedDroneTracker
from shipfitting.droneUtil import GetOptimalDroneDamage
import uthread
import log
import blue
from shipfitting.fittingStuff import IsRigSlot
from utillib import KeyVal

class FittingDogmaLocation(BaseDogmaLocation):
    __notifyevents__ = ['OnServerBrainUpdated']

    def __init__(self, broker, charBrain = None):
        BaseDogmaLocation.__init__(self, broker)
        self.manualEffectCategories = {const.dgmEffActivation: True,
         const.dgmEffTarget: True,
         const.dgmEffArea: True}
        self.godma = sm.GetService('godma')
        self.scatterAttributeChanges = True
        self.dogmaStaticMgr = sm.GetService('clientDogmaStaticSvc')
        self.effectCompiler = sm.GetService('ghostFittingEffectCompiler')
        self.instanceFlagQuantityCache = {}
        self.shipID = None
        self.brain = None
        self.shipIDBeingDisembarked = None
        if charBrain:
            self.SetBrainData(session.charid, charBrain)
        self.selectedDronesTracker = SelectedDroneTracker()
        self.locationName = 'FittingDogmaLocation'
        sm.RegisterNotify(self)

    def SetBrainData(self, charID, brain):
        self.brain = brain

    def GetBrainData(self, charID):
        return self.brain

    def GetCurrentShipID(self):
        return self.shipID

    def GetActiveShipID(self, characterID):
        return self.shipID

    def CheckApplyBrainEffects(self, shipID):
        return self.IsItemIdInDogmaItems(shipID)

    def IsItemIdInDogmaItems(self, itemID):
        return itemID in self.dogmaItems

    def OnServerBrainUpdated(self, brainData):
        self.LogInfo('FittingDogmaLocation:OnServerBrainUpdated received for character %s' % session.charid)
        shipID = self.GetCurrentShipID()
        if shipID is None:
            self.ProcessBrainData(session.charid, brainData)
            return
        with self.brainUpdate.Event(shipID):
            self.RemoveBrainEffects(shipID, session.charid, 'fittingDogmaLocation.OnServerBrainUpdated')
            self.ProcessBrainData(session.charid, brainData)
            self.ApplyBrainEffects(shipID, session.charid, 'fittingDogmaLocation.OnServerBrainUpdated')

    def LoadMyShip(self, typeID):
        self.LoadItem(session.charid)
        s = GhostFittingDataObject(None, 0, typeID)
        itemKey = s.GetItemKey()
        self.LoadItem(itemKey, item=s)
        self.pilotsByShipID[itemKey] = session.charid
        shipDogmaItem = self.GetDogmaItem(itemKey)
        charDogmaItem = self.GetDogmaItem(session.charid)
        oldShipID = self.shipID
        self.shipID = itemKey
        charDogmaItem.SetLocation(self.shipID, shipDogmaItem, const.flagPilot)
        self.MakeShipActive(self.shipID, oldShipID)
        return shipDogmaItem

    def FitItemToLocation(self, locationID, itemID, flagID):
        if self._IsLocationIDInvalidForFitting(locationID):
            return
        wasItemLoaded = self.IsItemIdInDogmaItems(itemID)
        if not self.IsItemIdInDogmaItems(locationID):
            self.LoadItem(locationID)
            if not wasItemLoaded:
                self.LogInfo('Neither location not item loaded, returning early', locationID, itemID)
                return
        if not self.IsItemIdInDogmaItems(itemID):
            self.LoadItem(itemID)
            return
        locationDogmaItem = self.SafeGetDogmaItem(locationID)
        if locationDogmaItem is None:
            self.LogInfo('FitItemToLocation::Fitted to None item', itemID, locationID, flagID)
            return
        dogmaItem = self.GetDogmaItem(itemID)
        dogmaItem.SetLocation(locationID, locationDogmaItem, flagID)
        startedEffects = self.StartPassiveEffects(itemID, dogmaItem.typeID)
        if flagID != FAKE_FLAGID:
            sm.GetService('ghostFittingSvc').SendOnStatsUpdatedEvent()

    def UnfitItemFromShip(self, itemID):
        self.selectedDronesTracker.UnregisterDroneFromActive(itemID)
        item = self.SafeGetDogmaItem(itemID)
        if item and not self.IsCharge(item):
            chargeItem = self.GetChargeFromShipFlag(item.flagID)
            if chargeItem:
                self.UnfitItemFromShip(chargeItem.itemID)
        self.UnfitItemFromLocation(self.shipID, itemID)
        self.UnloadItem(itemID)

    def GetQuantityFromCache(self, locationID, flagID):
        return 1

    def GetInstance(self, item):
        instanceRow = [item.itemID]
        for attributeID in self.GetAttributesByIndex().itervalues():
            v = getattr(item, self.dogmaStaticMgr.attributes[attributeID].attributeName, 0)
            instanceRow.append(v)

        return instanceRow

    def OnlineModule(self, itemKey):
        self.ChangeModuleStatus(itemKey, const.effectOnline)

    def ActivateModule(self, itemKey, moduleTypeID, flagID):
        typeEffectInfo = sm.GetService('ghostFittingSvc').GetDefaultAndOverheatEffect(moduleTypeID)
        defaultEffectID = typeEffectInfo.defaultEffect.effectID
        self.ChangeModuleStatus(itemKey, defaultEffectID)
        self.TryStartPassiveEffects(itemKey, moduleTypeID, flagID)

    def TryStartPassiveEffects(self, itemID, moduleTypeID, flagID):
        if not IsRigSlot(flagID):
            return
        self.StartPassiveEffects(itemID, moduleTypeID)

    def OverheatModule(self, itemKey, moduleTypeID):
        typeEffectInfo = sm.GetService('ghostFittingSvc').GetDefaultAndOverheatEffect(moduleTypeID)
        if typeEffectInfo.overloadEffect:
            self.ChangeModuleStatus(itemKey, typeEffectInfo.overloadEffect.effectID)

    def OfflineSimulatedModule(self, itemKey, moduleTypeID, flagID):
        self.OfflineModule(itemKey)
        self.TryStopPassiveEffects(itemKey, moduleTypeID, flagID)
        typeEffectInfo = sm.GetService('ghostFittingSvc').GetDefaultAndOverheatEffect(moduleTypeID)
        if typeEffectInfo.defaultEffect:
            self.StopEffect(typeEffectInfo.defaultEffect.effectID, itemKey)
        if typeEffectInfo.overloadEffect:
            self.StopEffect(typeEffectInfo.overloadEffect.effectID, itemKey)

    def TryStopPassiveEffects(self, itemID, itemTypeID, flagID):
        if not IsRigSlot(flagID):
            return
        dogmaItem = self.SafeGetDogmaItem(itemID)
        if dogmaItem is None:
            return
        self.StopPassiveEffects(dogmaItem, itemID, itemTypeID)

    def GetItem(self, itemID):
        if itemID != session.charid:
            return self.dogmaItems.get(itemID)
        item = self.godma.GetItem(itemID)
        return item

    def GetCharacter(self, itemID, flush = False):
        return self.GetItem(itemID)

    def ShouldStartChanceBasedEffect(self, *args, **kwargs):
        return False

    def StartSystemEffect(self):
        pass

    def AddTargetEx(self, *args, **kwargs):
        return 1

    def ChangeModuleStatus(self, itemKey, effectID = None):
        dogmaItem = self.GetDogmaItem(itemKey)
        envInfo = dogmaItem.GetEnvironmentInfo()
        env = Environment(itemID=envInfo.itemID, charID=envInfo.charID, shipID=self.shipID, targetID=envInfo.targetID, otherID=envInfo.otherID, effectID=effectID, dogmaLM=weakref.proxy(self), expressionID=None, structureID=envInfo.structureID)
        self.StartEffect(effectID, itemKey, env, checksOnly=None)

    def CheckSkillRequirementsForType(self, typeID, *args):
        missingSkills = self.GetMissingSkills(typeID)
        return missingSkills

    @telemetry.ZONE_METHOD
    def GetMissingSkills(self, typeID, skillSvc = None):
        if skillSvc is None:
            skillSvc = sm.GetService('skills')
        missingSkills = {}
        for requiredSkillTypeID, requiredSkillLevel in self.dogmaStaticMgr.GetRequiredSkills(typeID).iteritems():
            mySkill = skillSvc.GetSkill(requiredSkillTypeID)
            if mySkill is None or mySkill.skillLevel < requiredSkillLevel:
                missingSkills[requiredSkillTypeID] = requiredSkillLevel

        return missingSkills

    def SetQuantity(self, itemKey, quantity):
        shipID, flagID, typeID = itemKey
        if self.IsItemLoaded(shipID):
            return self.SetAttributeValue(itemKey, const.attributeQuantity, quantity)

    def GetTurretAndMissileDps(self, shipID):
        return GetTurretAndMissileDps(shipID, self, self.dogmaStaticMgr.TypeHasEffect)

    def GetAlphaStrike(self):
        return GetAlphaStrike(self, self.dogmaStaticMgr.TypeHasEffect)

    def GetOptimalDroneDamage(self, shipID, activeDrones):
        return GetOptimalDroneDamage(shipID, self, activeDrones)

    def GetOptimalDroneDamage2(self, shipID, activeDrones):
        return self.GetOptimalDroneDamage(shipID, activeDrones)

    def IsModuleIncludedInCalculation(self, module):
        dogmaItem = self.GetDogmaItem(module.itemID)
        return dogmaItem.IsActive()

    def GetDragData(self, itemID):
        return GetFittingItemDragData(itemID, self)

    def GetClassForItem(self, item):
        categoryID = item.categoryID
        if categoryID == const.categoryShip:
            return GhostShipDogmaItem
        if IsStructureFittable(categoryID):
            return GhostStructureModuleDogmaItem
        if IsShipFittable(categoryID):
            return GhostModuleDogmaItem
        return BaseDogmaLocation.GetClassForItem(self, item)

    def GetShip(self):
        return self.GetShipItem()

    def GetShipItem(self):
        return self.SafeGetDogmaItem(self.shipID)

    def GetFittedItemsToShip(self):
        shipItem = self.GetShipItem()
        if shipItem:
            return shipItem.GetFittedItems()
        else:
            return {}

    def GetModuleFromShipFlag(self, flagID):
        return self.GetItemFromShipFlag(flagID, getCharge=False)

    def GetChargeFromShipFlag(self, flagID):
        return self.GetItemFromShipFlag(flagID, getCharge=True)

    def GetItemFromShipFlag(self, flagID, getCharge):
        fittedItems = self.GetFittedItemsToShip()
        for eachItem in fittedItems.itervalues():
            try:
                if eachItem.flagID != flagID:
                    continue
                if getCharge and self.IsCharge(eachItem) or not getCharge and not self.IsCharge(eachItem):
                    return eachItem
            except ReferenceError as e:
                self.LogWarn(e)

    def IsCharge(self, fittedItem):
        if isinstance(fittedItem.itemID, tuple):
            return True
        if fittedItem.categoryID == const.categoryCharge:
            return True
        return False

    def GetChargeNonDB(self, shipID, flagID):
        for itemID, fittedItem in self.GetFittedItemsToShip().iteritems():
            if isinstance(itemID, tuple):
                continue
            if fittedItem.flagID != flagID:
                continue
            if fittedItem.categoryID == const.categoryCharge:
                return fittedItem

    def GetSensorStrengthAttribute(self, shipID):
        return GetSensorStrengthAttribute(self, shipID)

    @WrappedMethod
    def MakeShipActive(self, shipID, oldShipID):
        uthread.pool('MakeShipActive', self._MakeShipActive, shipID, oldShipID)

    @WrappedMethod
    def _MakeShipActive(self, shipID, oldShipID):
        myCharID = session.charid
        self.LoadItem(myCharID)
        uthread.Lock(self, 'makeShipActive')
        try:
            while not session.IsItSafe():
                self.LogInfo('MakeShipActive - session is mutating. Sleeping for 250ms')
                blue.pyos.synchro.SleepSim(250)

            if shipID is None:
                log.LogTraceback('Unexpectedly got shipID = None')
                return
            self.shipIDBeingDisembarked = self.GetCurrentShipID()
            shipDogmaItem = self.GetDogmaItem(shipID)
            self.StartPassiveEffects(shipID, shipDogmaItem.typeID)
            self.scatterAttributeChanges = False
            try:
                self.selectedDronesTracker.Clear()
                if oldShipID is not None:
                    self.UnfitItemFromLocation(oldShipID, myCharID)
                    if shipID != oldShipID:
                        self.UnloadItem(oldShipID)
                self.ApplyBrainEffects(shipID, myCharID)
            finally:
                self.shipIDBeingDisembarked = None
                self.scatterAttributeChanges = True

        finally:
            uthread.UnLock(self, 'makeShipActive')

    def GetCapacity(self, shipID, attributeID, flagID):
        keyVal = KeyVal(capacity=0, used=0)
        if flagID == const.flagDroneBay:
            keyVal.capacity = self.GetAttributeValue(shipID, const.attributeDroneCapacity)
            used = 0
            shipDogmaItem = self.GetDogmaItem(shipID)
            for droneID in shipDogmaItem.drones:
                used += self.GetAttributeValue(droneID, const.attributeVolume)

            keyVal.used = used
        return keyVal

    def CapacitorSimulator(self, shipID):
        return CapacitorSimulator(self, shipID)

    def RemoveFittedModules(self):
        try:
            for itemKey, item in self.dogmaItems.items():
                if itemKey not in self.dogmaItems:
                    continue
                if isinstance(item, (GhostModuleDogmaItem, DBLessDogmaItem, DroneDogmaItem)):
                    self.UnfitItemFromShip(itemKey)

            self.moduleListsByShipGroup.pop(self.shipID, None)
            self.moduleListsByShipType.pop(self.shipID, None)
        finally:
            self.scatterAttributeChanges = True

    def _IsLocationIDInvalidForFitting(self, locationID):
        if locationID == self.shipIDBeingDisembarked:
            return True
        isLocationIDValidForFitting = locationID not in (self.GetCurrentShipID(), session.charid)
        return isLocationIDValidForFitting

    def OnAttributeChanged(self, attributeID, itemKey, value = None, oldValue = None):
        value = BaseDogmaLocation.OnAttributeChanged(self, attributeID, itemKey, value=value, oldValue=oldValue)
        if self.scatterAttributeChanges:
            sm.ScatterEvent('OnDogmaAttributeChanged', self.shipID, itemKey, attributeID, value)

    def GetQuantity(self, itemID):
        return getattr(self.GetItem(itemID), 'stacksize', 1)

    def GetAccurateAttributeValue(self, itemID, attributeID, *args):
        return self.GetAttributeValue(itemID, attributeID)

    def DecreaseItemAttribute(self, itemKey, attributeID, itemKey2, attributeID2, limit = None, scaleFactor = 1):
        pass

    def AddLocationRequiredSkillModifierWithSource(self, operation, toLocationID, skillID, toAttribID, fromAttrib):
        if toLocationID is None:
            return
        BaseDogmaLocation.AddLocationRequiredSkillModifierWithSource(self, operation, toLocationID, skillID, toAttribID, fromAttrib)

    def IncreaseItemAttribute(self, itemKey, attributeID, itemKey2, attributeID2, limit = None, scaleFactor = 1):
        value = scaleFactor * self.GetAttributeValue(itemKey2, attributeID2)
        if limit:
            value = LimitAttributeOnItem(self.dogmaItems.get(itemKey), blue.os.GetSimTime() / const.SEC, limit, value)
        new, old = self.IncreaseItemAttributeEx(itemKey, attributeID, value, alsoReturnOldValue=True)
        if attributeID in (const.attributeShieldCharge, const.attributeCapacitorCharge) and new > old:
            actingItem = self.dogmaItems.get(itemKey2)
            if actingItem is None:
                self.broker.LogWarn('No actingItem in IncreaseItemAttribute', itemKey, attributeID, itemKey2, attributeID2)
        return new

    def IncreaseItemAttributeEx(self, itemKey, attributeID, value, silently = 0, alsoReturnOldValue = False):
        dogmaItem = self.GetDogmaItem(itemKey)
        if not dogmaItem.CanAttributeBeModified():
            if alsoReturnOldValue:
                return (0, 0)
            return 0
        attrib = dogmaItem.attributes[attributeID]
        oldValue = attrib.GetValue()
        attrib.SetBaseValue(oldValue + value)
        newValue = attrib.GetValue()
        if alsoReturnOldValue:
            return (newValue, oldValue)
        return newValue

    def DecreaseItemAttributeEx(self, itemKey, attributeID, reduction, silently = 0, alsoReturnOldValue = False):
        dogmaItem = self.dogmaItems.get(itemKey, None)
        if dogmaItem is None or not dogmaItem.CanAttributeBeModified():
            if alsoReturnOldValue:
                return (0, 0)
            return 0
        oldValue = dogmaItem.attributes[attributeID].GetValue()
        if oldValue - reduction < 0:
            newValue = 0
        else:
            newValue = oldValue - reduction
        dogmaItem.attributes[attributeID].SetBaseValue(newValue)
        if alsoReturnOldValue:
            return (newValue, oldValue)
        return newValue

    def IsInWeaponBank(self, *args):
        return False

    def WaitForShip(self, *args):
        pass

    def CheckItemsMissingInAddModifier(self, toItemID, fromAttrib):
        if not fromAttrib:
            raise RuntimeError('Item missing from AddModifier')

    def GetSecurityClass(self):
        return securityClassZeroSec

    def StartEffect_PreChecks(self, effect, dogmaItem, environment, byUser):
        BaseDogmaLocation.StartEffect_PreChecks(self, effect, dogmaItem, environment, byUser)
        if effect.effectCategory in (const.dgmEffActivation, const.dgmEffTarget) and dogmaItem.IsOnline():
            self._CheckIfTooManyModulesInGroupAreActive(effect, dogmaItem, environment)

    def _CheckIfTooManyModulesInGroupAreActive(self, effect, dogmaItem, environment):
        shipCategoryID = environment.shipCategoryID
        shipID = environment.shipID
        itemID = dogmaItem.itemID
        itemGroupID = dogmaItem.groupID
        if shipCategoryID != const.categoryShip:
            return
        if not self.IsShipLoaded(shipID):
            return
        maxGroupActive = self.GetAttributeValue(itemID, const.attributeMaxGroupActive)
        if itemGroupID == self.GetAttributeValue(shipID, const.attributeMaxShipGroupActiveID):
            maxGroupActive = max(self.GetAttributeValue(shipID, const.attributeMaxShipGroupActive), maxGroupActive)
        if maxGroupActive > 0:
            itemTypeID = dogmaItem.typeID
            shipDogmaItem = self.GetDogmaItem(shipID)
            modules = shipDogmaItem.GetFittedItems().itervalues()
            total = len([ item for item in modules if item.groupID == itemGroupID and item.IsActive() ])
            if total >= maxGroupActive:
                raise UserError('EffectCrowdedOut', {'module': itemTypeID,
                 'count': total})

    def SetDroneActivityState(self, droneID, setActive, qty = 1):
        return self.selectedDronesTracker.SetDroneActivityState(droneID, setActive, qty=qty)

    def RegisterDroneAsActive(self, droneID, qty = 1, raiseError = True):
        return self.selectedDronesTracker.RegisterDroneAsActive(droneID, qty=qty, raiseError=raiseError)

    def UnregisterDroneFromActive(self, droneID, qty = 1):
        return self.selectedDronesTracker.UnregisterDroneFromActive(droneID, qty=qty)

    def GetActiveDrones(self):
        return self.selectedDronesTracker.GetSelectedDrones()

    @telemetry.ZONE_METHOD
    def GetSubSystemInFlag(self, shipID, flagID):
        dogmaItem = self.GetModuleFromShipFlag(flagID)
        return dogmaItem
