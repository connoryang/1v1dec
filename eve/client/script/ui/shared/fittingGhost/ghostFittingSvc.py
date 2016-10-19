#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\fittingGhost\ghostFittingSvc.py
from contextlib import contextmanager
import dogma.const as dogmaConst
import evetypes
import shipmode
import threadutils
import uthread
import telemetry
from eve.client.script.ui.shared.fitting.fittingControllerUtil import GetFittingController
from eve.client.script.ui.shared.fitting.fittingUtil import GetPowerType
from eve.client.script.ui.shared.fittingGhost import SIMULATION_MODULES
from eve.client.script.ui.shared.fittingGhost.fittingUtilGhost import GetDefaultAndOverheatEffectForType, CheckChargeForLauncher, GetFlagIdToUse
from eve.client.script.ui.shared.fittingGhost.ghostFittingUtil import GhostFittingDataObject, ONLINE, OVERHEATED, ACTIVE, OFFLINE, DBLessGhostFittingDataObject
from dogma.items.chargeDogmaItem import ChargeDogmaItem
from dogma.items.moduleDogmaItem import ModuleDogmaItem
from inventorycommon.util import IsSubSystemFlag
from localization import GetByLabel
from shipfitting.fittingDogmaLocationUtil import GetNumChargesFullyLoaded
from shipfitting.fittingStuff import DoesModuleTypeIDFit, IsRightSlotForType, CheckCanFitType, IsRigSlot, GetSlotListForTypeID
import inventorycommon.const as invConst
import service
import blue
import log
from shipmode.inventory import InventoryGhost
from utillib import KeyVal
import carbonui.const as uiconst
allSlots = invConst.subSystemSlotFlags + invConst.rigSlotFlags + invConst.loSlotFlags + invConst.medSlotFlags + invConst.hiSlotFlags + invConst.serviceSlotFlags
AVAILABLEFLAGS = {dogmaConst.effectLoPower: (invConst.flagLoSlot0, 8),
 dogmaConst.effectMedPower: (invConst.flagMedSlot0, 8),
 dogmaConst.effectHiPower: (invConst.flagHiSlot0, 8),
 dogmaConst.effectRigSlot: (invConst.flagRigSlot0, 3)}

class GhostFittingSvc(service.Service):
    __guid__ = 'svc.ghostFittingSvc'
    __exportedcalls__ = {}
    __startupdependencies__ = []
    __notifyevents__ = []

    @telemetry.ZONE_METHOD
    def __init__(self):
        service.Service.__init__(self)
        self.effectsByType = {}
        self.activeDrones = set()
        self.simulationMode = SIMULATION_MODULES
        self.ghostFittingController = None

    def Run(self, ms = None):
        self.state = service.SERVICE_RUNNING
        self.clientDogmaLocation = sm.GetService('clientDogmaIM').GetDogmaLocation()
        self.ResetFittingDomaLocation()

    def ResetFittingDomaLocation(self, force = False):
        self.fittingDogmaLocation = sm.GetService('clientDogmaIM').GetFittingDogmaLocation(force=force)

    def FitDronesToShip(self, droneTypeID, qty = 1, raiseError = True):
        for i in xrange(qty):
            dogmaItem = self.FitADroneToShip(droneTypeID, raiseError)
            if dogmaItem is None:
                break

        self.SendOnStatsUpdatedEvent()

    def FitADroneToShip(self, droneTypeID, raiseError = True, sendUpdateEvent = False):
        shipDogmaItem = self.fittingDogmaLocation.GetShipItem()
        shipID = shipDogmaItem.itemID
        g = GhostFittingDataObject(shipID, const.flagDroneBay, droneTypeID)
        capacityInfo = self.fittingDogmaLocation.GetCapacity(shipID, None, const.flagDroneBay)
        volume = evetypes.GetVolume(droneTypeID)
        if capacityInfo.used + volume > capacityInfo.capacity:
            return
        counter = 0
        while g.GetItemKey() in shipDogmaItem.drones:
            g.SetNumber(counter)
            counter += 1

        itemKey = g.GetItemKey()
        dogmaItem = self.GetLoadedItem(itemKey, item=g)
        dogmaItem.stacksize = 1
        self.fittingDogmaLocation.RegisterDroneAsActive(itemKey, raiseError=raiseError)
        if sendUpdateEvent:
            self.SendOnStatsUpdatedEvent()
        return dogmaItem

    def GetLoadedItem(self, itemKey, item = None):
        self.fittingDogmaLocation.LoadItem(itemKey=itemKey, item=item)
        return self.fittingDogmaLocation.SafeGetDogmaItem(itemKey)

    def FitModuleToShipAndChangeState(self, shipID, flagID, moduleTypeID, preview = False):
        dogmaItem = self.FitModuleToShip(shipID, flagID, moduleTypeID, preview)
        if not dogmaItem:
            return
        itemKey = dogmaItem.itemID
        with self.EatCpuPowergridActiveUserErrors():
            self.PerformActionAndSetNewState(ONLINE, itemKey, moduleTypeID, flagID)
        with self.EatCpuPowergridActiveUserErrors():
            self.PerformActionAndSetNewState(ACTIVE, itemKey, moduleTypeID, flagID)
        if IsSubSystemFlag(flagID):
            self.SendSubSystemsChangedEvent()
        return dogmaItem

    def FitModuleToShip(self, shipID, flagID, moduleTypeID, preview = False):
        usedFlags = {x.flagID for x in self.fittingDogmaLocation.GetFittedItemsToShip().itervalues()}
        flagID = GetFlagIdToUse(moduleTypeID, flagID, usedFlags)
        canFitModuleInSlot = self.CanFitModuleInSlot(shipID, moduleTypeID, flagID, preview=preview)
        if not canFitModuleInSlot:
            return
        g = GhostFittingDataObject(shipID, flagID, moduleTypeID)
        itemKey = g.GetItemKey()
        dogmaItem = self.GetLoadedItem(itemKey, g)
        return dogmaItem

    def CanFitModuleInSlot(self, shipID, moduleTypeID, flagID, preview = False):
        errorText = DoesModuleTypeIDFit(self.fittingDogmaLocation, moduleTypeID, flagID)
        if errorText:
            self.LogInfo('Couldn not fit a module to ship, errorText = ' + errorText, shipID, flagID, moduleTypeID)
            return False
        if self.fittingDogmaLocation.GetSlotOther(shipID, flagID):
            self.LogInfo('Couldn not fit a module to ship, something there ', shipID, flagID, moduleTypeID)
            return False
        powerType = GetPowerType(flagID)
        if powerType == const.effectSubSystem:
            dogmaItemInFlag = self.fittingDogmaLocation.GetSubSystemInFlag(None, flagID)
            if dogmaItemInFlag and not preview:
                return
        if not IsRightSlotForType(moduleTypeID, powerType):
            self.LogInfo('Couldn not fit a module to ship, not right slot ', shipID, flagID, moduleTypeID)
            return False
        CheckCanFitType(self.fittingDogmaLocation, moduleTypeID, shipID)
        return True

    def UnfitDrone(self, itemKey, scatter = True):
        self.fittingDogmaLocation.UnregisterDroneFromActive(itemKey)
        self.UnfitModule(itemKey, scatter)

    def UnfitModule(self, itemKey, scatter = True):
        fittingSvc = sm.GetService('fittingSvc')
        if not fittingSvc.IsShipSimulated():
            log.LogWarn('cant use ghost fitting to unfit non-simulated ship')
            return
        dogmaItem = self.fittingDogmaLocation.SafeGetDogmaItem(itemKey)
        flagID = None
        if dogmaItem:
            with self.EatCpuPowergridActiveUserErrors():
                flagID = dogmaItem.flagID
                self.PerformActionAndSetNewState(OFFLINE, dogmaItem.itemID, dogmaItem.typeID, flagID)
        self.fittingDogmaLocation.UnfitItemFromShip(itemKey)
        if scatter:
            self.SendFittingSlotsChangedEvent()
            self.SendOnStatsUpdatedEvent()
            if IsSubSystemFlag(flagID):
                self.SendSubSystemsChangedEvent()

    def FitAmmoList(self, ammoInfo):
        for typeID, flagID in ammoInfo:
            self.FitAmmoToLocation(flagID, typeID)

    def FitAmmoToLocation(self, flagID, ammoTypeID):
        moduleItem = self.fittingDogmaLocation.GetModuleFromShipFlag(flagID)
        if not moduleItem:
            return
        doesFit = CheckChargeForLauncher(self.fittingDogmaLocation.dogmaStaticMgr, moduleItem.typeID, ammoTypeID)
        if not doesFit:
            return
        oldAmmo = self.fittingDogmaLocation.GetChargeFromShipFlag(flagID)
        if oldAmmo:
            try:
                self.UnfitModule(oldAmmo.itemID, scatter=False)
            except Exception as e:
                print 'e = ', e

        shipID = self.fittingDogmaLocation.GetCurrentShipID()
        g = DBLessGhostFittingDataObject(shipID, flagID, ammoTypeID)
        chargeKey = g.GetItemKey()
        chargeItem = self.GetLoadedItem(chargeKey, g)
        GAV = self.fittingDogmaLocation.GetAccurateAttributeValue
        numCharges = GetNumChargesFullyLoaded(chargeKey, moduleItem.itemID, GAV)
        chargeItem.stacksize = numCharges

    def GetDefaultAndOverheatEffect(self, typeID):
        if typeID not in self.effectsByType:
            effectsForType = GetDefaultAndOverheatEffectForType(typeID)
            self.effectsByType[typeID] = effectsForType
        return self.effectsByType[typeID]

    def GetModuleStatus(self, itemKey, typeID, flagID):
        if IsSubSystemFlag(flagID):
            return ONLINE
        typeEffectInfo = self.GetDefaultAndOverheatEffect(typeID)
        currentState = self.GetCurrentState(itemKey, typeEffectInfo, flagID)
        return currentState

    def ResetModuleStatus(self):
        self.OfflineAllModules()
        self.activeDrones.clear()
        self.fittingDogmaLocation.RemoveFittedModules()

    def PerformActionAndSetNewState(self, newState, itemKey, typeID, flagID):
        typeEffectInfo = self.GetDefaultAndOverheatEffect(typeID)
        if newState == OVERHEATED and not typeEffectInfo.overloadEffect:
            newState = ACTIVE
        if newState == ACTIVE and not typeEffectInfo.defaultEffect:
            return
        if newState == ONLINE:
            self.fittingDogmaLocation.OnlineModule(itemKey)
        elif newState == ACTIVE:
            self.fittingDogmaLocation.ActivateModule(itemKey, typeID, flagID)
        elif newState == OVERHEATED:
            self.fittingDogmaLocation.OverheatModule(itemKey, typeID)
        elif newState == OFFLINE:
            self.fittingDogmaLocation.OfflineSimulatedModule(itemKey, typeID, flagID)
        else:
            log.LogWarn('something went wrong!')
            return

    def GetCurrentState(self, itemKey, typeEffectInfo, flagID):
        dogmaItem = self.fittingDogmaLocation.GetDogmaItem(itemKey)
        if IsRigSlot(flagID):
            if typeEffectInfo.defaultEffect.effectID in dogmaItem.activeEffects:
                return ACTIVE
            else:
                return OFFLINE
        elif not typeEffectInfo.defaultEffect or not typeEffectInfo.isActivatable:
            if dogmaItem.IsOnline():
                return ONLINE
            else:
                return OFFLINE
        else:
            if not dogmaItem.IsOnline():
                return OFFLINE
            if not dogmaItem.IsActive():
                return ONLINE
            if typeEffectInfo.overloadEffect and typeEffectInfo.overloadEffect.effectID in dogmaItem.activeEffects:
                return OVERHEATED
            return ACTIVE

    def GetNewState(self, currentState, typeEffectInfo, flagID):
        isRigSlot = IsRigSlot(flagID)
        newState = None
        if currentState == ONLINE:
            if typeEffectInfo.defaultEffect and typeEffectInfo.isActivatable:
                newState = ACTIVE
            else:
                newState = OFFLINE
        elif currentState == ACTIVE:
            if typeEffectInfo.overloadEffect:
                newState = OVERHEATED
            else:
                newState = OFFLINE
        elif currentState == OVERHEATED:
            newState = OFFLINE
        elif currentState == OFFLINE:
            if isRigSlot:
                newState = ACTIVE
            else:
                newState = ONLINE
        return newState

    def SwitchBetweenModes(self, itemKey, typeID, flagID):
        typeEffectInfo = self.GetDefaultAndOverheatEffect(typeID)
        currentState = self.GetCurrentState(itemKey, typeEffectInfo, flagID)
        newState = self.GetNewState(currentState, typeEffectInfo, flagID)
        if newState is not None:
            self.PerformActionAndSetNewState(newState, itemKey, typeID, flagID)
        else:
            log.LogWarn('newState was None')
        self.SendOnStatsUpdatedEvent()

    def OnlineAllSlots(self):
        return self.OnlineAllInRack(allSlots)

    def ActivateAllSlots(self):
        return self.ActivateSlotList(allSlots)

    def OnlineAllInRack(self, slotList):
        with self.PerformAndScatterUpdateEvent():
            self.OnlineSlotList(slotList)

    def ActivateAllHighSlots(self, slotList):
        with self.PerformAndScatterUpdateEvent():
            self.ActivateSlotList(slotList)

    def OverheatAllInRack(self, slotList):
        with self.PerformAndScatterUpdateEvent():
            self.OverheatSlotList(slotList)

    def OfflineAllInRack(self, slotList):
        with self.PerformAndScatterUpdateEvent():
            self.OfflineSlotList(slotList)

    def UnfitAllAmmoInRack(self, slotList):
        with self.PerformAndScatterUpdateEvent():
            self.UnfitAllInSlotlist(slotList, unfitModules=False)

    def UnfitAllModulesInRack(self, slotList):
        with self.PerformAndScatterUpdateEvent():
            self.UnfitAllInSlotlist(slotList)

    def UnfitAllInSlotlist(self, slotList, unfitModules = True):
        for flagID in slotList:
            ghostAmmo = self.fittingDogmaLocation.GetChargeFromShipFlag(flagID)
            if ghostAmmo:
                self.UnfitModule(ghostAmmo.itemID)
            if unfitModules:
                ghostModule = self.fittingDogmaLocation.GetModuleFromShipFlag(flagID)
                if ghostModule:
                    self.PerformActionAndSetNewState(0, ghostModule.itemID, ghostModule.typeID, ghostModule.flagID)
                    self.UnfitModule(ghostModule.itemID)

    def OnlineSlotList(self, slotList):
        self.OfflineSlotList(slotList)
        self.PerformActionOnSlotList(ONLINE, slotList)

    def ActivateSlotList(self, slotList):
        self.OfflineSlotList(slotList)
        self.OnlineSlotList(slotList)
        self.PerformActionOnSlotList(ACTIVE, slotList)

    def OverheatSlotList(self, slotList):
        self.ActivateSlotList(slotList)
        self.PerformActionOnSlotList(OVERHEATED, slotList)

    def OfflineSlotList(self, slotList):
        self.PerformActionOnSlotList(OFFLINE, slotList)

    def OfflineAllModules(self):
        self.OfflineSlotList(invConst.hiSlotFlags)
        self.OfflineSlotList(invConst.medSlotFlags)
        self.OfflineSlotList(invConst.loSlotFlags)

    def PerformActionOnSlotList(self, action, slotList):
        for flagID in slotList:
            ghostItem = self.fittingDogmaLocation.GetModuleFromShipFlag(flagID)
            if ghostItem:
                with self.EatCpuPowergridActiveUserErrors():
                    self.PerformActionAndSetNewState(action, ghostItem.itemID, ghostItem.typeID, flagID)

    @contextmanager
    def EatCpuPowergridActiveUserErrors(self):
        try:
            yield
        except UserError as e:
            if e.msg in ('EffectAlreadyActive2', 'NotEnoughCpu', 'NotEnoughPower', 'NoCharges', 'EffectCrowdedOut'):
                self.LogInfo('UserError ingored when fitting= ' + e.msg + str(e.args))
            else:
                raise

    @contextmanager
    def PerformAndScatterUpdateEvent(self):
        try:
            yield
        finally:
            self.SendFittingSlotsChangedEvent()

    def LoadCurrentShip(self):
        self.ResetModuleStatus()
        clientDL = sm.GetService('clientDogmaIM').GetDogmaLocation()
        ship = clientDL.GetDogmaItem(clientDL.GetActiveShipID(session.charid))
        moduleInfoToLoad = []
        chargeInfoToLoad = []
        for module in ship.GetFittedItems().values():
            if isinstance(module, ModuleDogmaItem):
                info = (module.typeID, module.flagID, 1)
                moduleInfoToLoad.append(info)
            elif isinstance(module, ChargeDogmaItem):
                info = (module.typeID, module.flagID)
                chargeInfoToLoad.append(info)
            else:
                continue

        droneInfo = []
        for drone in ship.GetDrones().itervalues():
            info = (drone.typeID, drone.invItem.stacksize)
            droneInfo.append(info)

        blue.pyos.synchro.Yield()
        self.LoadSimulatedFitting(ship.typeID, moduleInfoToLoad, droneInfo)
        self.FitAmmoList(chargeInfoToLoad)

    def SimulateFitting(self, fitting, *args):
        droneInfo = [ (typeID, qty) for typeID, flagID, qty in fitting.fitData if evetypes.GetCategoryID(typeID) == const.categoryDrone ]
        return self.LoadSimulatedFitting(fitting.shipTypeID, fitting.fitData, droneInfo)

    def LoadSimulatedFitting(self, shipTypeID, moduleInfo, droneInfo = []):
        if not sm.GetService('fittingSvc').IsGhostFittingEnabled():
            log.LogWarn('Trying to load simulated fitting, config not set')
            return
        if self.fittingDogmaLocation.GetCurrentShipID():
            if not self.ShouldContinueAfterAskingAboutSwitchingShips():
                return
        self.ResetModuleStatus()
        shipDogmaItem = self.LoadShip(shipTypeID)
        shipItemKey = shipDogmaItem.itemID
        sm.GetService('fittingSvc').SetSimulationState(True)
        self.SendOnSimulatedShipLoadedEvent(shipItemKey, shipTypeID)
        moduleInfo.sort(key=lambda x: x[1], reverse=True)
        rigsAndModulesInfo = [ m for m in moduleInfo if m[1] in allSlots ]
        for typeID, flagID, stacksize in rigsAndModulesInfo:
            try:
                self.FitModuleToShip(shipItemKey, flagID, typeID)
            finally:
                pass

        self.OnlineAllSlots()
        blue.pyos.synchro.Yield()
        self.ActivateAllSlots()
        for typeID, stacksize in droneInfo:
            try:
                self.FitDronesToShip(typeID, stacksize, raiseError=False)
            finally:
                pass

        self.SendOnStatsUpdatedEvent()

    def LoadShip(self, shipTypeID):
        self.ResetModuleStatus()
        if self.fittingDogmaLocation.GetCurrentShipID():
            currentDLShip = self.fittingDogmaLocation.GetShip()
        else:
            currentDLShip = None
        if currentDLShip and currentDLShip.typeID == shipTypeID:
            shipDogmaItem = currentDLShip
        else:
            shipDogmaItem = self.fittingDogmaLocation.LoadMyShip(shipTypeID)
        return shipDogmaItem

    def TryFitAmmoTypeToAll(self, moduleTypeID, ammoTypeID):
        fittingSvc = sm.GetService('fittingSvc')
        if not fittingSvc.IsShipSimulated():
            return
        for flagID in const.hiSlotFlags + const.medSlotFlags + const.loSlotFlags:
            moduleItem = self.fittingDogmaLocation.GetModuleFromShipFlag(flagID)
            if moduleItem and moduleItem.typeID == moduleTypeID:
                self.FitAmmoToLocation(flagID, ammoTypeID)

        self.SendFittingSlotsChangedEvent()

    def TryFitModuleToOneSlot(self, moduleTypeID, preview = False):
        fittingSvc = sm.GetService('fittingSvc')
        shipID = self.fittingDogmaLocation.shipID
        if not fittingSvc.IsShipSimulated():
            return
        if evetypes.GetCategoryID(moduleTypeID) == const.categoryDrone:
            return self.FitADroneToShip(moduleTypeID, raiseError=False, sendUpdateEvent=True)
        flagIDs = GetSlotListForTypeID(moduleTypeID)
        dogmaItemFitted = None
        for flagID in flagIDs:
            oldGhostFittedItem = self.fittingDogmaLocation.GetModuleFromShipFlag(flagID)
            if oldGhostFittedItem and getattr(oldGhostFittedItem, 'isPreviewItem', None):
                self.UnfitModule(oldGhostFittedItem.itemID)
            dogmaItemFitted = self.FitModuleToShipAndChangeState(shipID, flagID, moduleTypeID, preview=preview)
            if dogmaItemFitted:
                break

        if dogmaItemFitted:
            self.SendFittingSlotsChangedEvent()
        return dogmaItemFitted

    def SetSimulationMode(self, simulationMode):
        self.simulationMode = simulationMode

    def GetSimulationMode(self):
        return self.simulationMode

    def GetGhostFittingController(self):
        return self.ghostFittingController

    def LoadGhostFittingController(self, itemID):
        self.ghostFittingController = GetFittingController(itemID, ghost=True)
        return self.ghostFittingController

    def SendOnSimulatedShipLoadedEvent(self, shipItemKey, shipTypeID):
        self.SendOnSimulatedShipLoadedEvent_throttled(self, shipItemKey, shipTypeID)

    @threadutils.throttled(0.5)
    def SendOnSimulatedShipLoadedEvent_throttled(self, shipItemKey, shipTypeID):
        ghostFittingController = self.GetGhostFittingController()
        if ghostFittingController:
            ghostFittingController.OnSimulationStateChanged(True)
            uthread.new(ghostFittingController.OnSimulatedShipLoaded, shipItemKey, shipTypeID)

    def SendOnStatsUpdatedEvent(self):
        self.SendOnStatsUpdatedEvent_throttled(self)

    @threadutils.throttled(0.5)
    def SendOnStatsUpdatedEvent_throttled(self):
        ghostFittingController = self.GetGhostFittingController()
        if ghostFittingController:
            ghostFittingController.UpdateStats()

    def SendFittingSlotsChangedEvent(self):
        self.SendFittingSlotsChangedEvent_throttled(self)

    @threadutils.throttled(0.5)
    def SendFittingSlotsChangedEvent_throttled(self):
        ghostFittingController = self.GetGhostFittingController()
        if ghostFittingController:
            uthread.new(ghostFittingController.OnFittingSlotsChanged)

    def SendSubSystemsChangedEvent(self):
        self.SendSubSystemsChangedEvent_throttled(self)

    @threadutils.throttled(0.5)
    def SendSubSystemsChangedEvent_throttled(self):
        ghostFittingController = self.GetGhostFittingController()
        if ghostFittingController:
            uthread.new(ghostFittingController.OnSubSystemsChanged)

    def LoadFakeItem(self, shipID, moduleTypeID):
        g = GhostFittingDataObject(shipID, flagID=-1, typeID=moduleTypeID)
        itemKey = g.GetItemKey()
        self.fittingDogmaLocation.LoadItem(itemKey=itemKey, item=g)
        info = KeyVal(powerValue=self.fittingDogmaLocation.GetAttributeValue(itemKey, const.attributePower), cpuValue=self.fittingDogmaLocation.GetAttributeValue(itemKey, const.attributeCpu))
        self.fittingDogmaLocation.UnfitItemFromShip(itemKey)
        return info

    def IsSimulatingCurrentShipType(self):
        actualShip = self.clientDogmaLocation.GetShip()
        simulatedShip = self.fittingDogmaLocation.GetShip()
        return actualShip and simulatedShip and actualShip.typeID == simulatedShip.typeID

    def GetSimulatedShipStance(self, ship_id, type_id):
        inv = InventoryGhost(ship_id, invConst.flagHiddenModifers, self.fittingDogmaLocation, GhostFittingDataObject)
        currentStance = shipmode.get_current_ship_stance(type_id, inv.list_items())
        if currentStance is None:
            stancesByTypes = shipmode.data.get_stance_by_type(type_id).items()
            if not stancesByTypes:
                return
            stancesByTypes.sort(key=lambda x: x[1])
            inv.create_item(stancesByTypes[0][0])
        return shipmode.get_current_ship_stance(type_id, inv.list_items())

    def SetSimulatedStance(self, stance_id, ship_id):
        if not self.ghostFittingController:
            return
        inventory = InventoryGhost(ship_id, invConst.flagHiddenModifers, self.fittingDogmaLocation, GhostFittingDataObject)
        typeID = inventory.get_type_id(ship_id)
        notifier = StanceNotifier(self.ghostFittingController, ship_id)
        shipStance = shipmode.ShipStance(inventory, notifier, shipmode.data.get_modes_by_type(typeID))
        shipStance.set_stance(stance_id, 0)

    def ShouldContinueAfterAskingAboutSwitchingShips(self):
        if eve.Message('LoadSimulatedShip', buttons=uiconst.YESNO, suppress=uiconst.ID_YES) == uiconst.ID_YES:
            return True
        return False


class StanceNotifier(object):

    def __init__(self, controller, ship_id):
        self.ship_id = ship_id
        self.controller = controller

    def on_stance_changed(self, old_stance_id, new_stance_id):
        self.controller.OnStanceActive(self.ship_id, new_stance_id)
        sm.ScatterEvent('OnStanceActive', self.ship_id, new_stance_id)
