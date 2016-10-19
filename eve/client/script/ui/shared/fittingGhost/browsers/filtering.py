#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\fittingGhost\browsers\filtering.py
import evetypes
from inventorycommon.util import IsModularShip
from utillib import KeyVal
import telemetry
import blue

def GetFilters(isSimulated):
    slotFilterInfo = KeyVal(showHiSlots=settings.user.ui.Get('fitting_filter_hardware_hiSlot', False), showMedSlots=settings.user.ui.Get('fitting_filter_hardware_medSlot', False), showLoSlots=settings.user.ui.Get('fitting_filter_hardware_loSlot', False), showRigSlots=settings.user.ui.Get('fitting_filter_hardware_rigSlot', False), showDrones=settings.user.ui.Get('fitting_filter_hardware_drones', False))
    filterMode_resourcesOnOutput = settings.user.ui.Get('fitting_filter_resourcesOnOutput', True)
    filters = KeyVal(filterString=settings.user.ui.Get('fitting_hardwareSearchField', '').lower(), filterByShipCanUse=settings.user.ui.Get('fitting_filter_hardware_ship', False), filterOnCpu=settings.user.ui.Get('fitting_filter_hardware_resources', False) and isSimulated and filterMode_resourcesOnOutput, filterOnCpuLeft=settings.user.ui.Get('fitting_filter_hardware_resources', False) and isSimulated and not filterMode_resourcesOnOutput, filterOnPowergrid=settings.user.ui.Get('fitting_filter_hardware_resources', False) and isSimulated and filterMode_resourcesOnOutput, filterOnPowergridLeft=settings.user.ui.Get('fitting_filter_hardware_resources', False) and isSimulated and not filterMode_resourcesOnOutput, filterOnSkills=settings.user.ui.Get('fitting_filter_hardware_skills', False), slotFilterInfo=slotFilterInfo)
    return filters


def GetCpuAndPowerLeft(dogmaLocation):
    cpuOutput = GetCpuOutputOfCurrentShip(dogmaLocation)
    cpuUsed = dogmaLocation.GetAttributeValue(dogmaLocation.GetCurrentShipID(), const.attributeCpuLoad)
    cpuLeft = cpuOutput - cpuUsed
    powerOutput = GetPowerOutputOfCurrentShip(dogmaLocation)
    powerUsed = dogmaLocation.GetAttributeValue(dogmaLocation.GetCurrentShipID(), const.attributePowerLoad)
    powerLeft = powerOutput - powerUsed
    return (cpuLeft, powerLeft)


def GetCpuOutputOfCurrentShip(dogmaLocation):
    return dogmaLocation.GetAttributeValue(dogmaLocation.GetCurrentShipID(), const.attributeCpuOutput)


def GetPowerOutputOfCurrentShip(dogmaLocation):
    return dogmaLocation.GetAttributeValue(dogmaLocation.GetCurrentShipID(), const.attributePowerOutput)


def GetResourceRigsFitted(dogmaLocation):
    rigList = []
    shipID = dogmaLocation.GetCurrentShipID()
    for flagID in const.rigSlotFlags:
        rigItemID = dogmaLocation.GetSlotOther(shipID, flagID)
        if not rigItemID:
            continue
        dogmaItem = dogmaLocation.SafeGetDogmaItem(rigItemID)
        if not dogmaItem:
            continue
        if evetypes.GetGroupID(dogmaItem.typeID) == const.groupRigCore:
            rigList.append(dogmaItem.typeID)

    rigList.sort()
    return tuple(rigList)


@telemetry.ZONE_METHOD
def GetValidTypeIDs(typeList, searchFittingHelper):
    fittingSvc = sm.GetService('fittingSvc')
    isSimulated = fittingSvc.IsShipSimulated()
    filters = GetFilters(isSimulated)
    fittingHelper = searchFittingHelper
    dogmaLocation = fittingSvc.GetCurrentDogmaLocation()
    skillSvc = sm.GetService('skills')
    ship = dogmaLocation.GetShip()
    if not ship:
        return typeList
    shipID = ship.itemID
    shipTypeID = ship.typeID
    dogmaStaticMgr = dogmaLocation.dogmaStaticMgr
    shipRigSize = fittingHelper.GetShipRigSize(dogmaStaticMgr, shipTypeID)
    isCapitalShip = fittingHelper.IsCapitalSize(evetypes.GetGroupID(shipTypeID))
    isModularShip = IsModularShip(shipTypeID)
    cpuLeft, powerLeft = GetCpuAndPowerLeft(dogmaLocation)
    cpuOutput = GetCpuOutputOfCurrentShip(dogmaLocation)
    powerOutput = GetPowerOutputOfCurrentShip(dogmaLocation)
    resourceRigsFitted = GetResourceRigsFitted(dogmaLocation)
    ghostFitting = sm.GetService('ghostFittingSvc')
    ret = []
    for typeID in typeList:
        if filters.filterByShipCanUse:
            if not fittingHelper.CanFitModuleToShipTypeOrGroup(shipTypeID, dogmaLocation, typeID):
                continue
            if fittingHelper.IsRigSizeRestricted(dogmaStaticMgr, typeID, shipRigSize):
                continue
            if fittingHelper.IsModuleTooBig(shipTypeID, typeID, isCapitalShip):
                continue
            if fittingHelper.RestrictedByDroneOrFighter(dogmaStaticMgr, shipTypeID, typeID):
                continue
            if isModularShip:
                if fittingHelper.IsModuleRestrictedForModularShip(dogmaStaticMgr, shipTypeID, typeID):
                    continue
        filterOutFromSlotType = DoSlotTypeFiltering(fittingHelper, typeID, filters.slotFilterInfo)
        if filterOutFromSlotType:
            continue
        if filters.filterOnSkills:
            missingSkills = fittingHelper.GetMissingSkills(typeID, dogmaLocation, skillSvc)
            if missingSkills:
                continue
        if filters.filterOnCpu:
            usedByType = fittingHelper.GetCPUForModuleType(ghostFitting, shipID, typeID, shipTypeID, resourceRigsFitted)
            if usedByType > cpuOutput:
                continue
        if filters.filterOnPowergrid:
            usedByType = fittingHelper.GetPowergridForModuleType(ghostFitting, shipID, typeID, shipTypeID, resourceRigsFitted)
            if usedByType > powerOutput:
                continue
        if filters.filterOnCpuLeft:
            usedByType = fittingHelper.GetCPUForModuleType(ghostFitting, shipID, typeID, shipTypeID, resourceRigsFitted)
            if usedByType > cpuLeft:
                continue
        if filters.filterOnPowergridLeft:
            usedByType = fittingHelper.GetPowergridForModuleType(ghostFitting, shipID, typeID, shipTypeID, resourceRigsFitted)
            if usedByType > powerLeft:
                continue
        if not filters.filterString or filters.filterString in fittingHelper.GetTypeName(typeID):
            ret.append(typeID)
        blue.pyos.BeNice(200)

    return ret


def DoSlotTypeFiltering(fittingHelper, moduleTypeID, filterInfo):
    if filterInfo.showHiSlots + filterInfo.showLoSlots + filterInfo.showMedSlots + filterInfo.showRigSlots + filterInfo.showDrones in (0,):
        return False
    toCheck = [(filterInfo.showHiSlots, fittingHelper.IsHislotModule),
     (filterInfo.showLoSlots, fittingHelper.IsLoSlot),
     (filterInfo.showMedSlots, fittingHelper.IsMedslotModule),
     (filterInfo.showRigSlots, fittingHelper.IsRigSlot),
     (filterInfo.showDrones, fittingHelper.IsDroneOrFighter)]
    for doCheck, checkFunc in toCheck:
        if doCheck:
            isSlotType = checkFunc(moduleTypeID)
            if isSlotType:
                return False

    return True
