#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\environment\fittingSvc.py
import sys
from collections import defaultdict
import uthread
from carbon.common.script.util.commonutils import StripTags
from carbon.common.script.util.linkUtil import GetShowInfoLink
from eve.client.script.ui.shared.fittingGhost.fittingSearchUtil import SearchFittingHelper
from eve.client.script.ui.shared.fittingMgmtWindow import ViewFitting
from eve.common.script.sys.eveCfg import GetActiveShip
from shipfitting import Fitting
import inventorycommon
from inventorycommon.util import IsShipFittingFlag, IsShipFittable, IsModularShip
import service
import util
import blue
from eve.client.script.ui.control import entries as listentry
import form
import localization
import carbonui.const as uiconst
import log
import evetypes
from carbonui.util.various_unsorted import SortListOfTuples, GetClipboardData
from shipfitting.importFittingUtil import FindShipAndFittingName, ImportFittingUtil
from shipfitting.exportFittingUtil import GetFittingEFTString
from utillib import KeyVal

class fittingSvc(service.Service):
    __guid__ = 'svc.fittingSvc'
    __exportedcalls__ = {'GetFittingDictForActiveShip': [],
     'ChangeOwner': []}
    __startupdependencies__ = ['settings', 'invCache']
    __notifyevents__ = ['OnSkillsChanged',
     'OnFittingAdded',
     'OnFittingDeleted',
     'OnGlobalConfigChanged']

    def __init__(self):
        service.Service.__init__(self)
        self.fittings = {}
        self.hasSkillByFittingID = {}
        self.importFittingUtil = None
        self.inSimulation = False
        self.InitSearchFittingHelper()
        self.busyFitting = False
        self.isGhostFittingEnabled = None

    def Run(self, ms = None):
        self.state = service.SERVICE_RUNNING
        self.fittings = {}

    def InitSearchFittingHelper(self):
        self.searchFittingHelper = SearchFittingHelper(cfg)
        uthread.new(self.searchFittingHelper.BuildNameDict)

    def GetFittingMgr(self, ownerID):
        if ownerID == session.charid:
            return sm.RemoteSvc('charFittingMgr')
        if ownerID == session.corpid:
            return sm.RemoteSvc('corpFittingMgr')
        raise RuntimeError("Can't find the fitting manager you're asking me to get. ownerID:", ownerID)

    def HasLegacyClientFittings(self):
        if len(settings.char.generic.Get('fittings', {})) > 0:
            return True
        return False

    def GetLegacyClientFittings(self):
        return settings.char.generic.Get('fittings', {})

    def DeleteLegacyClientFittings(self):
        settings.char.generic.Set('fittings', None)

    def GetFittingDictForCurrentFittingWindowShip(self, putModuleAmmoInHangar = True):
        if self.IsShipSimulated():
            return self.GetFittingDictForSimulatedShip(putModuleAmmoInHangar=putModuleAmmoInHangar)
        else:
            return self.GetFittingDictForActiveShip(putModuleAmmoInHangar=putModuleAmmoInHangar)

    def GetFittingDictForActiveShip(self, putModuleAmmoInHangar = True):
        shipID = util.GetActiveShip()
        shipInv = self.invCache.GetInventoryFromId(shipID, locationID=session.stationid2)
        visibleFittedItems = (i for i in shipInv.List() if inventorycommon.ItemIsVisible(i))
        fitData = self.CreateFittingData(visibleFittedItems, putModuleAmmoInHangar=putModuleAmmoInHangar)
        return (shipInv.GetItem().typeID, fitData)

    def GetFittingDictForSimulatedShip(self, putModuleAmmoInHangar = True):
        dogmaLocation = self.GetCurrentDogmaLocation()
        shipID = dogmaLocation.GetCurrentShipID()
        shipItem = dogmaLocation.GetDogmaItem(shipID)
        fittedItems = shipItem.GetFittedItems()
        items = fittedItems.values()
        items += shipItem.GetDrones().values()
        fitData = self.CreateFittingData(items, putModuleAmmoInHangar=putModuleAmmoInHangar)
        return (shipItem.typeID, fitData)

    def CreateFittingData(self, items, putModuleAmmoInHangar = True):
        fitData = []
        dronesByType = defaultdict(int)
        chargesByType = defaultdict(int)
        iceByType = defaultdict(int)
        fightersByType = defaultdict(int)
        for item in items:
            typeID = item.typeID
            flagID = item.flagID
            if IsShipFittingFlag(flagID) and IsShipFittable(item.categoryID):
                fitData.append((int(typeID), int(flagID), 1))
            elif item.categoryID == const.categoryDrone and flagID == const.flagDroneBay:
                dronesByType[typeID] += item.stacksize
            elif item.categoryID == const.categoryFighter and flagID == const.flagFighterBay:
                fightersByType[typeID] += item.stacksize
            elif item.categoryID == const.categoryCharge and flagID == const.flagCargo:
                chargesByType[typeID] += item.stacksize
            elif hasattr(item, 'groupID') and item.groupID == const.groupIceProduct and flagID == const.flagCargo:
                iceByType[typeID] += item.stacksize
            elif putModuleAmmoInHangar and item.categoryID == const.categoryCharge and flagID in const.moduleSlotFlags:
                chargesByType[typeID] += getattr(item, 'stacksize', 1)

        fitData += self.GetDataToAddToFitData(const.flagDroneBay, dronesByType)
        fitData += self.GetDataToAddToFitData(const.flagFighterBay, fightersByType)
        fitData += self.GetDataToAddToFitData(const.flagCargo, chargesByType)
        fitData += self.GetDataToAddToFitData(const.flagCargo, iceByType)
        return fitData

    def GetDataToAddToFitData(self, flag, qtyByTypeID):
        data = []
        for typeID, quantity in qtyByTypeID.iteritems():
            data.append((int(typeID), int(flag), int(quantity)))

        return data

    def DisplayFittingFromItems(self, shipTypeID, items):
        newItems = []
        for item in items:
            if not hasattr(item, 'flagID'):
                item.flagID = item.flag
            if not hasattr(item, 'stacksize'):
                item.stacksize = item.qtyDropped + item.qtyDestroyed
            item.categoryID = evetypes.GetCategoryID(item.typeID)
            newItems.append(item)

        fitData = self.CreateFittingData(newItems)
        fitting = util.KeyVal()
        fitting.shipTypeID = shipTypeID
        fitting.name = evetypes.GetName(shipTypeID)
        fitting.ownerID = None
        fitting.fittingID = None
        fitting.description = ''
        fitting.fitData = fitData
        self.DisplayFitting(fitting)

    def PersistFitting(self, ownerID, name, description, fit = None):
        if name is None or name.strip() == '':
            raise UserError('FittingNeedsToHaveAName')
        name = name.strip()
        fitting = util.KeyVal()
        fitting.name = name[:const.maxLengthFittingName]
        fitting.description = description[:const.maxLengthFittingDescription]
        self.PrimeFittings(ownerID)
        if ownerID == session.corpid:
            maxFittings = const.maxCorpFittings
        else:
            maxFittings = const.maxCharFittings
        if len(self.fittings[ownerID]) >= maxFittings:
            owner = cfg.eveowners.Get(ownerID).ownerName
            raise UserError('OwnerMaxFittings', {'owner': owner,
             'maxFittings': maxFittings})
        if fit is None:
            fitting.shipTypeID, fitting.fitData = self.GetFittingDictForActiveShip()
        else:
            fitting.shipTypeID, fitting.fitData = fit
        self.VerifyFitting(fitting)
        fitting.ownerID = ownerID
        fitting.fittingID = self.GetFittingMgr(ownerID).SaveFitting(ownerID, fitting)
        self.UpdateFittingWindow()
        sm.ScatterEvent('OnFittingsUpdated')
        return fitting

    def PersistManyFittings(self, ownerID, fittings):
        if ownerID == session.corpid:
            maxFittings = const.maxCorpFittings
        else:
            maxFittings = const.maxCharFittings
        self.PrimeFittings(ownerID)
        if len(self.fittings[ownerID]) + len(fittings) > maxFittings:
            owner = cfg.eveowners.Get(ownerID).ownerName
            raise UserError('OwnerMaxFittings', {'owner': owner,
             'maxFittings': maxFittings})
        fittingsToSave = {}
        tmpFittingID = -1
        for fitt in fittings:
            if fitt.name is None or fitt.name.strip() == '':
                raise UserError('FittingNeedsToHaveAName')
            fitting = util.KeyVal()
            fitting.fittingID = tmpFittingID
            fitting.name = fitt.name.strip()[:const.maxLengthFittingName]
            fitting.description = fitt.description[:const.maxLengthFittingDescription]
            fitting.shipTypeID = fitt.shipTypeID
            fitting.fitData = fitt.fitData
            self.VerifyFitting(fitting)
            fitting.ownerID = ownerID
            fittingsToSave[tmpFittingID] = fitting
            tmpFittingID -= 1

        newFittingIDs = self.GetFittingMgr(ownerID).SaveManyFittings(ownerID, fittingsToSave)
        for row in newFittingIDs:
            self.fittings[ownerID][row.realFittingID] = fittingsToSave[row.tempFittingID]
            self.fittings[ownerID][row.realFittingID].fittingID = row.realFittingID

        self.UpdateFittingWindow()
        return fitting

    def VerifyFitting(self, fitting):
        if fitting.name.find('@@') != -1 or fitting.description.find('@@') != -1:
            raise UserError('InvalidFittingInvalidCharacter')
        if fitting.shipTypeID is None:
            raise UserError('InvalidFittingDataTypeID', {'typeName': fitting.shipTypeID})
        shipTypeName = evetypes.GetNameOrNone(fitting.shipTypeID)
        if shipTypeName is None:
            raise UserError('InvalidFittingDataTypeID', {'typeName': fitting.shipTypeID})
        if evetypes.GetCategoryID(fitting.shipTypeID) not in (const.categoryShip, const.categoryStructure):
            raise UserError('InvalidFittingDataShipNotShip', {'typeName': shipTypeName})
        if len(fitting.fitData) == 0:
            raise UserError('ParseFittingFittingDataEmpty')
        for typeID, flag, qty in fitting.fitData:
            if not evetypes.Exists(typeID):
                raise UserError('InvalidFittingDataTypeID', {'typeID': typeID})
            try:
                int(flag)
            except TypeError:
                raise UserError('InvalidFittingDataInvalidFlag', {'type': typeID})

            if not (IsShipFittingFlag(flag) or flag in (const.flagDroneBay, const.flagCargo, const.flagFighterBay)):
                raise UserError('InvalidFittingDataInvalidFlag', {'type': typeID})
            try:
                int(qty)
            except TypeError:
                raise UserError('InvalidFittingDataInvalidQuantity', {'type': typeID})

            if qty == 0:
                raise UserError('InvalidFittingDataInvalidQuantity', {'type': typeID})

        return True

    def GetFittings(self, ownerID):
        self.PrimeFittings(ownerID)
        return self.fittings[ownerID]

    def GetFittingsForType(self, ownerID, typeID):
        allFittings = self.GetFittings(ownerID)
        return [ fitting for fitting in allFittings.items() if fitting[1]['shipTypeID'] == typeID ]

    def PrimeFittings(self, ownerID):
        if ownerID not in self.fittings:
            self.fittings[ownerID] = self.GetFittingMgr(ownerID).GetFittings(ownerID)

    def DeleteFitting(self, ownerID, fittingID):
        self.LogInfo('deleting fitting', fittingID, 'from owner', ownerID)
        self.GetFittingMgr(ownerID).DeleteFitting(ownerID, fittingID)
        if ownerID in self.fittings and fittingID in self.fittings[ownerID]:
            del self.fittings[ownerID][fittingID]
        self.UpdateFittingWindow()

    def LoadFittingFromFittingID(self, ownerID, fittingID):
        fitting = self.fittings.get(ownerID, {}).get(fittingID, None)
        return self.LoadFitting(fitting)

    def CheckBusyFittingAndRaiseIfNeeded(self):
        if self.busyFitting:
            sm.GetService('loading').ProgressWnd('', '', 1, 1)
            raise UserError('CustomInfo', {'info': localization.GetByLabel('UI/Fitting/FittingWindow/FittingManagement/BusyFittingWarning')})

    def DoFitManyShips(self, chargesByType, dronesByType, fightersByTypeID, fitRigs, fitting, iceByType, cargoItemsByType, maxAvailableFitting, modulesByFlag, fittingName = None):
        shipAccess = sm.StartService('gameui').GetShipAccess()
        try:
            failedInfo = None
            if fittingName is None or fittingName.strip() == '':
                fittingName = fitting.name or evetypes.GetName(fitting.shipTypeID)
                fittingName = StripTags(fittingName)
            self.busyFitting = True
            sm.GetService('inv').ChangeTreeUpdatingState(isUpdateEnabled=False)
            failedInfo = shipAccess.FitShips(shipTypeID=fitting.shipTypeID, modulesByFlag=modulesByFlag, itemLocationID=session.stationid2 or session.structureid, dronesByType=dronesByType, fightersByTypeID=fightersByTypeID, chargesByType=chargesByType, iceByType=iceByType, cargoItemsByType=cargoItemsByType, fitRigs=fitRigs, name=fittingName, numToFit=maxAvailableFitting)
        finally:
            self.busyFitting = False
            sm.GetService('inv').ChangeTreeUpdatingState(isUpdateEnabled=True)
            if failedInfo:
                failedToLoad, failedShipID = failedInfo
                if failedShipID:
                    self._RenameShip(failedShipID)
                if failedToLoad:
                    self.ShowFailedToLoadMsg(failedToLoad)

    def _RenameShip(self, failedShipID):
        badFitName = localization.GetByLabel('UI/Fitting/FittingWindow/FittingManagement/BadFitFittingFailed')
        self.invCache.GetInventoryMgr().SetLabel(failedShipID, badFitName)

    def GetMaxAvailabeAndMissingForFullFit(self, fitRigs, itemTypes, numToFit, qtyByTypeID, rigTypeIDs):
        missingForFullFit = {}
        maxRoundsForEachTypeID = {}
        for itemTypID, qtyNeeded in itemTypes.iteritems():
            if not fitRigs and itemTypID in rigTypeIDs:
                continue
            qtyInHangar = qtyByTypeID.get(itemTypID, 0)
            rounds = int(qtyInHangar / qtyNeeded)
            maxRoundsForEachTypeID[itemTypID] = rounds
            if rounds < numToFit:
                missingForFullFit[itemTypID] = qtyNeeded * numToFit - qtyInHangar

        maxAvailableFitting = min(maxRoundsForEachTypeID.values())
        return (maxAvailableFitting, missingForFullFit)

    def GetMaxAvailable(self, fitRigs, itemTypes, qtyByTypeID, rigTypeIDs):
        maxRoundsForEachTypeID = {}
        for itemTypID, qtyNeeded in itemTypes.iteritems():
            if not fitRigs and itemTypID in rigTypeIDs:
                continue
            qtyInHangar = qtyByTypeID.get(itemTypID, 0)
            rounds = int(qtyInHangar / qtyNeeded)
            maxRoundsForEachTypeID[itemTypID] = rounds

    def LoadFitting(self, fitting, getFailedDict = False):
        self.CheckBusyFittingAndRaiseIfNeeded()
        self._CheckValidFittingLocation(fitting)
        shipInv = self.invCache.GetInventoryFromId(util.GetActiveShip())
        if shipInv.item.typeID != fitting.shipTypeID:
            raise UserError('ShipTypeInFittingNotSameAsShip')
        chargesByType, dronesByType, fightersByTypeID, iceByType, itemTypes, modulesByFlag, rigsToFit, subsystems = self.GetTypesToFit(fitting, shipInv)
        fitRigs = False
        cargoItemsByType = defaultdict(int)
        if rigsToFit:
            if self.HasRigFitted():
                eve.Message('CustomNotify', {'notify': localization.GetByLabel('UI/Fitting/ShipHasRigsAlready')})
            elif eve.Message('FitRigs', {}, uiconst.YESNO) == uiconst.ID_YES:
                fitRigs = True
            else:
                for flagID, typeID in modulesByFlag.iteritems():
                    if flagID in const.rigSlotFlags:
                        cargoItemsByType[typeID] += 1

        cargoItemsByType = dict(cargoItemsByType)
        itemsToFit = defaultdict(set)
        for item in self.invCache.GetInventory(const.containerHangar).List(const.flagHangar):
            if item.typeID in itemTypes:
                qtyNeeded = itemTypes[item.typeID]
                if qtyNeeded == 0:
                    continue
                quantityToTake = min(item.stacksize, qtyNeeded)
                itemsToFit[item.typeID].add(item.itemID)
                itemTypes[item.typeID] -= quantityToTake

        if subsystems:
            shipType = shipInv.GetItem().typeID
            for flag, module in modulesByFlag.iteritems():
                if const.flagSubSystemSlot0 <= flag <= const.flagSubSystemSlot7:
                    moduleFitsShipType = int(sm.GetService('clientDogmaStaticSvc').GetTypeAttribute(module, const.attributeFitsToShipType))
                    if shipType != moduleFitsShipType:
                        raise UserError('CannotFitSubSystemNotShip', {'subSystemName': (const.UE_TYPEID, module),
                         'validShipName': (const.UE_TYPEID, moduleFitsShipType),
                         'shipName': (const.UE_TYPEID, shipType)})
                    if module in itemTypes and itemTypes[module] > 0:
                        raise UserError('CantUnfitSubSystems')

        self.CheckBusyFittingAndRaiseIfNeeded()
        self.busyFitting = True
        try:
            failedToLoad = shipInv.FitFitting(util.GetActiveShip(), itemsToFit, session.stationid2 or session.structureid, modulesByFlag, dronesByType, fightersByTypeID, chargesByType, iceByType, cargoItemsByType, fitRigs)
        finally:
            self.busyFitting = False

        if settings.user.ui.Get('useFittingNameForShips', 0):
            fittingName = StripTags(fitting.get('name'))
            fittingName = fittingName[:20]
            self.invCache.GetInventoryMgr().SetLabel(util.GetActiveShip(), fittingName)
        if getFailedDict:
            return failedToLoad
        self.ShowFailedToLoadMsg(failedToLoad)

    def ShowFailedToLoadMsg(self, failedToLoad):
        textList = []
        for typeID, qty in failedToLoad:
            if qty > 0:
                typeName = evetypes.GetName(typeID)
                link = GetShowInfoLink(typeID, typeName)
                textList.append((typeName.lower(), '%sx %s' % (qty, link)))

        if textList:
            textList = SortListOfTuples(textList)
            text = '<br>'.join(textList)
            text = localization.GetByLabel('UI/Fitting/MissingItems', types=text)
            eve.Message('CustomInfo', {'info': text}, modal=False)

    def _CheckValidFittingLocation(self, fitting):
        if session.stationid is None and session.structureid is None:
            raise UserError('CannotLoadFittingInSpace')
        if fitting is None:
            raise UserError('FittingDoesNotExist')

    def GetQt0yInHangarByTypeIDs(self, itemTypes, onlyGetNonSingletons = False):
        hangar = self.invCache.GetInventory(const.containerHangar)
        qtyByTypeID = defaultdict(int)
        for item in hangar.List(const.flagHangar):
            if item.typeID in itemTypes:
                if onlyGetNonSingletons and item.quantity < 0:
                    continue
                qtyByTypeID[item.typeID] += item.stacksize

        return qtyByTypeID

    def GetTypesToFit(self, fitting, shipInv):
        fittingObj = Fitting(fitting.fitData, shipInv)
        return (fittingObj.GetChargesByType(),
         fittingObj.GetDronesByType(),
         fittingObj.GetFigthersByType(),
         fittingObj.GetIceByType(),
         fittingObj.GetQuantityByType(),
         fittingObj.GetModulesByFlag(),
         fittingObj.FittingHasRigs(),
         fittingObj.FittingHasSubsystems())

    def HasRigFitted(self):
        shipInv = self.invCache.GetInventoryFromId(util.GetActiveShip(), locationID=session.stationid2)
        for item in shipInv.List():
            if const.flagRigSlot0 <= item.flagID <= const.flagRigSlot7:
                return True

        return False

    def UpdateFittingWindow(self):
        wnd = form.FittingMgmt.GetIfOpen()
        if wnd is not None:
            wnd.DrawFittings()

    def ChangeNameAndDescription(self, fittingID, ownerID, name, description):
        if name is None or name.strip() == '':
            raise UserError('FittingNeedsToHaveAName')
        name = name.strip()
        fittings = self.GetFittings(ownerID)
        if fittingID in fittings:
            fitting = fittings[fittingID]
            if name != fitting.name or description != fitting.description:
                if name.find('@@') != -1 or description.find('@@') != -1:
                    raise UserError('InvalidFittingInvalidCharacter')
                self.GetFittingMgr(ownerID).UpdateNameAndDescription(fittingID, ownerID, name, description)
                self.fittings[ownerID][fittingID].name = name
                self.fittings[ownerID][fittingID].description = description
        self.UpdateFittingWindow()

    def GetFitting(self, ownerID, fittingID):
        self.PrimeFittings(ownerID)
        if fittingID in self.fittings[ownerID]:
            return self.fittings[ownerID][fittingID]

    def ChangeOwner(self, ownerID, fittingID, newOwnerID):
        fitting = self.GetFitting(ownerID, fittingID)
        if fitting is None:
            raise UserError('FittingDoesNotExistAnymore')
        fit = (fitting.shipTypeID, fitting.fitData)
        if fitting.name is None or fitting.name.strip() == '':
            raise UserError('FittingNeedsToHaveAName')
        return self.PersistFitting(newOwnerID, fitting.name.strip(), fitting.description, fit=fit)

    def CheckFittingExist(self, ownerID, shipTypeID, fitData):
        fittings = self.GetFittings(ownerID)
        fittingExists = False
        for fitting in fittings.itervalues():
            if fitting.shipTypeID != shipTypeID:
                continue
            if fitting.fitData != fitData:
                continue
            fittingExists = True

        return fittingExists

    def DisplayFittingFromString(self, fittingString):
        fitting, truncated = self.GetFittingFromString(fittingString)
        if fitting == -1:
            raise UserError('FittingInvalidForViewing')
        self.DisplayFitting(fitting, truncated=truncated)

    def DisplayFitting(self, fitting, truncated = False):
        if uicore.uilib.Key(uiconst.VK_SHIFT):
            fittingsList = fitting.fitData[:]
            fittingsList.sort()
            newFittingStr = '%s' % fittingsList
            windowID = 'ViewFitting_%s' % newFittingStr
        else:
            windowID = 'ViewFitting'
        wnd = form.ViewFitting.GetIfOpen(windowID=windowID)
        if wnd:
            wnd.ReloadWnd(windowID=windowID, fitting=fitting, truncated=truncated)
            wnd.Maximize()
        else:
            form.ViewFitting.Open(windowID=windowID, fitting=fitting, truncated=truncated)

    def GetStringForFitting(self, fitting):
        typesDict = defaultdict(int)
        drones = {}
        fighters = {}
        charges = {}
        ice = {}
        for typeID, flag, qty in fitting.fitData:
            categoryID = evetypes.GetCategoryID(typeID)
            groupID = evetypes.GetGroupID(typeID)
            if IsShipFittable(categoryID):
                typesDict[typeID] += 1
            elif categoryID == const.categoryDrone:
                drones[typeID] = qty
            elif categoryID == const.categoryFighter:
                fighters[typeID] = qty
            elif categoryID == const.categoryCharge:
                charges[typeID] = qty
            elif groupID == const.groupIceProduct:
                ice[typeID] = qty

        retList = []
        subString = str(fitting.shipTypeID)
        retList.append(subString)
        for eachDict in [typesDict,
         drones,
         fighters,
         charges,
         ice]:
            for typeID, qty in eachDict.iteritems():
                subString = '%s;%s' % (typeID, qty)
                retList.append(subString)

        ret = ':'.join(retList)
        ret += '::'
        return ret

    def GetFittingFromString(self, fittingString):
        effectSlots = {const.effectHiPower: const.flagHiSlot0,
         const.effectMedPower: const.flagMedSlot0,
         const.effectLoPower: const.flagLoSlot0,
         const.effectRigSlot: const.flagRigSlot0,
         const.effectSubSystem: const.flagSubSystemSlot0,
         const.effectServiceSlot: const.flagServiceSlot0}
        truncated = False
        if not fittingString.endswith('::'):
            truncated = True
            fittingString = fittingString[:fittingString.rfind(':')]
        data = fittingString.split(':')
        fitting = util.KeyVal()
        fitData = []
        for line in data:
            typeInfo = line.split(';')
            if line == '':
                continue
            if len(typeInfo) == 1:
                fitting.shipTypeID = int(typeInfo[0])
                continue
            typeID, qty = typeInfo
            typeID, qty = int(typeID), int(qty)
            powerEffectID = sm.GetService('godma').GetPowerEffectForType(typeID)
            if powerEffectID is not None:
                startSlot = effectSlots[powerEffectID]
                for flag in xrange(startSlot, startSlot + qty):
                    fitData.append((typeID, flag, 1))

                effectSlots[powerEffectID] = flag + 1
            else:
                categoryID = evetypes.GetCategoryID(typeID)
                groupID = evetypes.GetGroupID(typeID)
                if categoryID == const.categoryDrone:
                    fitData.append((typeID, const.flagDroneBay, qty))
                if categoryID == const.categoryFighter:
                    fitData.append((typeID, const.flagFighterBay, qty))
                elif categoryID == const.categoryCharge:
                    fitData.append((typeID, const.flagCargo, qty))
                elif groupID == const.groupIceProduct:
                    fitData.append((typeID, const.flagCargo, qty))
                else:
                    continue

        shipName = evetypes.GetName(fitting.shipTypeID)
        fitting.name = shipName
        fitting.ownerID = None
        fitting.fittingID = None
        fitting.description = ''
        fitting.fitData = fitData
        return (fitting, truncated)

    def GetFittingInfoScrollList(self, fitting):
        scrolllist = []
        typesByRack = self.GetTypesByRack(fitting)
        for key, effectID in [('hiSlots', const.effectHiPower),
         ('medSlots', const.effectMedPower),
         ('lowSlots', const.effectLoPower),
         ('rigSlots', const.effectRigSlot),
         ('subSystems', const.effectSubSystem),
         ('serviceSlots', const.effectServiceSlot)]:
            slots = typesByRack[key]
            if len(slots) < 1:
                continue
            label = cfg.dgmeffects.Get(effectID).displayName
            scrolllist.append(listentry.Get('Header', {'label': label}))
            slotScrollList = []
            for typeID, qty in slots.iteritems():
                data = self._GetDataForFittingEntry(typeID, qty)
                data.singleton = 1
                data.effectID = effectID
                entry = listentry.Get('FittingModuleEntry', data=data)
                slotScrollList.append((evetypes.GetGroupID(typeID), entry))

            slotScrollList = SortListOfTuples(slotScrollList)
            scrolllist.extend(slotScrollList)

        for qtyByTypeIdDict, headerLabelPath, isValidGroup in ((typesByRack['charges'], 'UI/Generic/Charges', True),
         (typesByRack['ice'], 'UI/Inflight/MoonMining/Processes/Fuel', True),
         (typesByRack['drones'], 'UI/Drones/Drones', True),
         (typesByRack['fighters'], 'UI/Common/Fighters', True),
         (typesByRack['other'], 'UI/Fitting/FittingWindow/FittingManagement/OtherItems', False)):
            if len(qtyByTypeIdDict) > 0:
                scrolllist.append(listentry.Get('Header', {'label': localization.GetByLabel(headerLabelPath)}))
                scrolllist += self._GetFittingEntriesForGroup(qtyByTypeIdDict, isValidGroup)

        return scrolllist

    def _GetFittingEntriesForGroup(self, qtyByTypeIdDict, isValidGroup):
        entries = []
        for typeID, qty in qtyByTypeIdDict.iteritems():
            data = self._GetDataForFittingEntry(typeID, qty, isValidGroup)
            entry = listentry.Get('FittingModuleEntry', data=data)
            entries.append(entry)

        return entries

    def _GetDataForFittingEntry(self, typeID, qty, isValidGroup = True):
        data = util.KeyVal(typeID=typeID, showinfo=1, getIcon=True, label=str(util.FmtAmt(qty)) + 'x ' + evetypes.GetName(typeID), isValidGroup=isValidGroup)
        return data

    def GetTypesByRack(self, fitting):
        ret = {'hiSlots': defaultdict(int),
         'medSlots': defaultdict(int),
         'lowSlots': defaultdict(int),
         'rigSlots': defaultdict(int),
         'subSystems': defaultdict(int),
         'serviceSlots': defaultdict(int),
         'charges': {},
         'drones': {},
         'ice': {},
         'fighters': {},
         'other': {}}
        for typeID, flag, qty in fitting.fitData:
            if evetypes.GetCategoryID(typeID) == const.categoryCharge:
                ret['charges'][typeID] = qty
            elif evetypes.GetGroupID(typeID) == const.groupIceProduct:
                ret['ice'][typeID] = qty
            elif flag in const.hiSlotFlags:
                ret['hiSlots'][typeID] += 1
            elif flag in const.medSlotFlags:
                ret['medSlots'][typeID] += 1
            elif flag in const.loSlotFlags:
                ret['lowSlots'][typeID] += 1
            elif flag in const.rigSlotFlags:
                ret['rigSlots'][typeID] += 1
            elif flag >= const.flagServiceSlot0 and flag <= const.flagServiceSlot7:
                ret['serviceSlots'][typeID] += 1
            elif flag in const.subSystemSlotFlags:
                ret['subSystems'][typeID] += 1
            elif flag == const.flagDroneBay:
                ret['drones'][typeID] = qty
            elif flag == const.flagFighterBay:
                ret['fighters'][typeID] = qty
            else:
                ret['other'][typeID] = qty

        return ret

    def HasSkillForFit(self, fitting):
        fittingID = fitting.fittingID
        try:
            return self.hasSkillByFittingID[fittingID]
        except KeyError:
            self.LogInfo('HasSkillForFit::Cache miss', fittingID)
            sys.exc_clear()

        hasSkill = self.hasSkillByFittingID[fittingID] = self.CheckSkillRequirementsForFit(fitting)
        return hasSkill

    def CheckSkillRequirementsForFit(self, fitting):
        godma = sm.GetService('godma')
        if not godma.CheckSkillRequirementsForType(fitting.shipTypeID):
            return False
        for typeID, flag, qty in fitting.fitData:
            if flag in inventorycommon.const.rigSlotFlags:
                continue
            if not godma.CheckSkillRequirementsForType(typeID):
                return False

        return True

    def GetAllFittings(self):
        ret = {}
        charFittings = self.GetFittings(session.charid)
        corpFittings = self.GetFittings(session.corpid)
        for fittingID in charFittings:
            ret[fittingID] = charFittings[fittingID]

        for fittingID in corpFittings:
            ret[fittingID] = corpFittings[fittingID]

        return ret

    def OnSkillsChanged(self, *args):
        self.hasSkillByFittingID = {}

    def OnFittingAdded(self, ownerID, fitID):
        if ownerID in self.fittings:
            deleteFits = False
            if isinstance(fitID, (int, long)):
                if fitID not in self.fittings[ownerID]:
                    deleteFits = True
            elif isinstance(fitID, list):
                if any((x in self.fittings[ownerID] for x in fitID)):
                    deleteFits = True
            else:
                raise RuntimeError("fitID should always be an int, long, or list. It wasn't. fitID = {} and type(fitID) = {}".format(fitID, type(fitID)))
            if deleteFits is True:
                del self.fittings[ownerID]
                self.UpdateFittingWindow()
                sm.ScatterEvent('OnFittingsUpdated')

    def OnFittingDeleted(self, ownerID, fitID):
        if ownerID in self.fittings:
            if fitID in self.fittings[ownerID]:
                del self.fittings[ownerID][fitID]
                self.UpdateFittingWindow()
                sm.ScatterEvent('OnFittingsUpdated')

    def ImportFittingFromClipboard(self, *args):
        try:
            textInField = GetClipboardData()
            shipName, fitName = FindShipAndFittingName(textInField)
            importFittingUtil = self.GetImportFittingUtil()
            shipTypeID = importFittingUtil.nameAndTypesDict.get(shipName.lower(), None)
            if not shipTypeID:
                eve.Message('ImportingErrorFromClipboard')
                return
            itemLines, errorLines = importFittingUtil.GetAllItems(textInField)
            fitData = importFittingUtil.CreateFittingData(itemLines, shipTypeID)
            if not fitData:
                eve.Message('ImportingErrorFromClipboard')
                return
            fittingData = util.KeyVal(shipTypeID=shipTypeID, fitData=fitData, fittingID=None, description='', name=fitName, ownerID=0)
            self.DisplayFitting(fittingData)
            if errorLines:
                errorText = '<br>'.join(errorLines)
                text = '<b>%s</b><br>%s' % (localization.GetByLabel('UI/SkillQueue/CouldNotReadLines'), errorText)
                eve.Message('CustomInfo', {'info': text})
        except Exception as e:
            log.LogWarn('Failed to import fitting from clipboard, e = ', e)
            eve.Message('ImportingErrorFromClipboard')

    def GetImportFittingUtil(self):
        if self.importFittingUtil is None:
            self.importFittingUtil = ImportFittingUtil(cfg.dgmtypeeffects, sm.GetService('clientDogmaStaticSvc'))
        return self.importFittingUtil

    def ExportFittingToClipboard(self, fitting):
        fittingString = GetFittingEFTString(fitting)
        blue.pyos.SetClipboardData(fittingString)

    def SaveFitting(self, *args):
        fitting = self.GetFittingForCurrentInWnd()
        windowID = 'Save_ViewFitting_%s' % fitting.shipTypeID
        ViewFitting.Open(windowID=windowID, fitting=fitting, truncated=None)

    def GetFittingForCurrentInWnd(self, putModuleAmmoInHangar = True):
        fitting = KeyVal()
        fitting.shipTypeID, fitting.fitData = self.GetFittingDictForCurrentFittingWindowShip(putModuleAmmoInHangar=putModuleAmmoInHangar)
        fitting.fittingID = None
        fitting.description = ''
        fitting.ownerID = 0
        typeName = evetypes.GetName(fitting.shipTypeID)
        if self.inSimulation:
            shipName = name = 'simulated %s' % typeName
        else:
            shipName = cfg.evelocations.Get(GetActiveShip()).locationName
        fitting.name = shipName
        return fitting

    def GetShipIDForFittingWindow(self):
        if self.IsShipSimulated():
            fittingDL = self.GetCurrentDogmaLocation()
            return fittingDL.GetCurrentShipID()
        import util
        return util.GetActiveShip()

    def GetCurrentDogmaLocation(self):
        if self.IsShipSimulated():
            return sm.GetService('clientDogmaIM').GetFittingDogmaLocation()
        else:
            return sm.GetService('clientDogmaIM').GetDogmaLocation()

    def IsShipSimulated(self):
        return self.inSimulation

    def SetSimulationState(self, simulationOn = False):
        self.inSimulation = simulationOn

    def IsGhostFittingEnabled(self):
        if self.isGhostFittingEnabled is None:
            uthread.new(self._FetchGlobalConfigAndSetVariable)
            return False
        return self.isGhostFittingEnabled

    def _FetchGlobalConfigAndSetVariable(self):
        self.isGhostFittingEnabled = sm.GetService('machoNet').GetGlobalConfig().get('enableGhostFitting')

    def OnGlobalConfigChanged(self, configVals):
        enableGhostFittingValue = configVals.get('enableGhostFitting', '0')
        self.isGhostFittingEnabled = int(enableGhostFittingValue)

    def RemoveAndLoadChargesFromSimulatedShip(self, clientDL, actualShipItemID, simulatedChargeTypesAndQtyByFlagID):
        actualShipInv = sm.GetService('invCache').GetInventoryFromId(actualShipItemID)
        visibleFittedItems = (i for i in actualShipInv.List() if inventorycommon.ItemIsVisible(i))
        actualShip_chargeTypesAndQtyByFlagID = self.GetChargesAndQtyByFlag(visibleFittedItems)
        if actualShip_chargeTypesAndQtyByFlagID == simulatedChargeTypesAndQtyByFlagID:
            return {}
        actualShipInv.RemoveAllChargesToHangar(removeCrystals=True)
        blue.pyos.synchro.Yield()
        return self.FitSimulatedCharges(clientDL, simulatedChargeTypesAndQtyByFlagID)

    def FitSimulatedCharges(self, clientDL, simulated_chargeTypesAndQtyByFlagID):
        fitted = clientDL.GetShip().GetFittedItems()
        fittedByFlagID = {x.flagID:x for x in fitted.itervalues()}
        hangar = sm.GetService('invCache').GetInventory(const.containerHangar)
        invItemsByTypeIDs = defaultdict(list)
        for x in hangar.List(const.flagHangar):
            invItemsByTypeIDs[x.typeID].append(x)

        ammoFailedToLoad = defaultdict(int)
        for flagID, chargeInfo in simulated_chargeTypesAndQtyByFlagID.iteritems():
            chargeTypeID, qty = chargeInfo
            moduleItem = fittedByFlagID.get(flagID, None)
            if not moduleItem:
                continue
            invItemsForType = invItemsByTypeIDs.get(chargeTypeID, None)
            if not invItemsForType:
                ammoFailedToLoad[chargeTypeID] += qty
                continue
            try:
                clientDL.LoadChargeToModule(moduleItem.itemID, chargeTypeID, invItemsForType)
            except UserError as e:
                if e.msg == 'CannotLoadNotEnoughCharges':
                    ammoFailedToLoad[chargeTypeID] += qty
                else:
                    raise

        return ammoFailedToLoad

    def GetChargesAndQtyByFlag(self, fittedItems):
        chargeTypesAndQtyByFlagID = defaultdict(int)
        for item in fittedItems:
            flagID = item.flagID
            if item.categoryID == const.categoryCharge and flagID in const.moduleSlotFlags:
                stacksize = getattr(item, 'stacksize', 1)
                chargeTypesAndQtyByFlagID[flagID] = (item.typeID, stacksize)

        return chargeTypesAndQtyByFlagID
