#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\shipfitting\fittingStuff.py
import evetypes
from inventorycommon.util import IsShipFittingFlag
from inventorycommon import const as invConst

def GetHardwareLayoutForShip(moduleTypeID, shipTypeID, dogmaStaticMgr, currentModuleList):
    typeID = moduleTypeID
    groupID = evetypes.GetGroupID(moduleTypeID)
    hardwareAttribs = {}
    typeEffects = dogmaStaticMgr.TypeGetEffects(typeID)
    GTA = dogmaStaticMgr.GetTypeAttribute2
    isTurret = isLauncher = False
    if const.effectHiPower in typeEffects:
        hardwareAttribs[const.attributeHiSlots] = int(GTA(shipTypeID, const.attributeHiSlots))
        if const.effectTurretFitted in typeEffects:
            hardwareAttribs[const.attributeTurretSlotsLeft] = int(GTA(shipTypeID, const.attributeTurretSlotsLeft))
            isTurret = True
        elif const.effectLauncherFitted in typeEffects:
            hardwareAttribs[const.attributeLauncherSlotsLeft] = int(GTA(shipTypeID, const.attributeLauncherSlotsLeft))
            isLauncher = True
    elif const.effectMedPower in typeEffects:
        hardwareAttribs[const.attributeMedSlots] = int(GTA(shipTypeID, const.attributeMedSlots))
    elif const.effectLoPower in typeEffects:
        hardwareAttribs[const.attributeLowSlots] = int(GTA(shipTypeID, const.attributeLowSlots))
    elif const.effectRigSlot in typeEffects:
        hardwareAttribs[const.attributeRigSlots] = int(GTA(shipTypeID, const.attributeRigSlots))
    elif const.effectSubSystem in typeEffects:
        hardwareAttribs[const.attributeMaxSubSystems] = int(GTA(shipTypeID, const.attributeMaxSubSystems))
    elif const.effectServiceSlot in typeEffects:
        hardwareAttribs[const.attributeServiceSlots] = int(GTA(shipTypeID, const.attributeServiceSlots))
    turretsFitted = 0
    launchersFitted = 0
    rigsFitted = 0
    calibration = 0
    shipHardwareModifierAttribs = dogmaStaticMgr.GetShipHardwareModifierAttribs()
    modulesByGroup = 0
    modulesByType = 0
    for item in currentModuleList:
        if not IsShipFittingFlag(item.flagID):
            continue
        if item.groupID == groupID:
            modulesByGroup += 1
        if item.typeID == typeID:
            modulesByType += 1
        if const.flagHiSlot0 <= item.flagID <= const.flagHiSlot7:
            if isTurret:
                if dogmaStaticMgr.TypeHasEffect(item.typeID, const.effectTurretFitted):
                    turretsFitted += 1
            elif isLauncher:
                if dogmaStaticMgr.TypeHasEffect(item.typeID, const.effectLauncherFitted):
                    launchersFitted += 1
        elif const.flagRigSlot0 <= item.flagID <= const.flagRigSlot7:
            rigsFitted += 1
            calibration += GTA(item.typeID, const.attributeUpgradeCost)
        elif const.flagSubSystemSlot0 <= item.flagID <= const.flagSubSystemSlot7:
            for attributeID, modifyingAttributeID in shipHardwareModifierAttribs:
                if attributeID not in hardwareAttribs:
                    continue
                hardwareAttribs[attributeID] += GTA(item.typeID, modifyingAttributeID)

    return (hardwareAttribs,
     turretsFitted,
     launchersFitted,
     rigsFitted,
     calibration,
     modulesByGroup,
     modulesByType)


def IsModuleTooBig(moduleTypeID, shipTypeID, isCapitalShip = None, isStructure = None):
    if isCapitalShip is None:
        isCapitalShip = evetypes.GetGroupID(shipTypeID) in cfg.GetShipGroupByClassType()[const.GROUP_CAPITALSHIPS]
    if isStructure is None:
        isStructure = evetypes.GetCategoryID(shipTypeID) == const.categoryStructure
    if not isCapitalShip and not isStructure:
        itemVolume = evetypes.GetVolume(moduleTypeID)
        if itemVolume > const.maxNonCapitalModuleSize:
            return True
    return False


def DoesModuleTypeIDFit(dogmaLocation, moduleTypeID, flagID):
    if not CanFitModuleToShipTypeOrGroup(dogmaLocation, moduleTypeID):
        return 'cantFitModuleToShip'
    shipID = dogmaLocation.shipID
    shipItem = dogmaLocation.dogmaItems[shipID]
    dogmaStaticMgr = dogmaLocation.dogmaStaticMgr
    if not IsCategoryOK_StructureVsShipRestrictions(shipItem.typeID, moduleTypeID):
        return 'ModuleNotAppropriateForShipCategory'
    if IsModuleTooBig(moduleTypeID, shipItem.typeID):
        return 'ModuleTooBigForThisShip'
    try:
        CheckCanFitType(dogmaLocation, moduleTypeID, shipID)
    except UserError as e:
        if e.msg == 'CantFitTooManyByGroup':
            return 'CantFitTooManyByGroup'
        if e.msg == 'CantFitTooManyByType':
            return 'CantFitTooManyByType'
        if e.msg == 'ModuleNotPowered':
            return 'ModuleNotPowered'

    currentModuleList = shipItem.GetFittedItems().values()
    hardwareLayout, turretsFitted, launchersFitted, rigsFitted, totalCalibration, modulesByGroup, modulesByType = GetHardwareLayoutForShip(moduleTypeID, shipItem.typeID, dogmaStaticMgr, currentModuleList)
    maxGroupFitted = dogmaStaticMgr.GetTypeAttribute(moduleTypeID, const.attributeMaxGroupFitted)
    if maxGroupFitted is not None and maxGroupFitted <= modulesByGroup:
        return 'CantFitTooManyByGroup'
    maxTypeFitted = dogmaStaticMgr.GetTypeAttribute(moduleTypeID, const.attributeMaxTypeFitted)
    if maxTypeFitted is not None and maxTypeFitted <= modulesByType:
        return 'CantFitTooManyByType'
    if dogmaStaticMgr.TypeHasEffect(moduleTypeID, const.effectLauncherFitted):
        balance = hardwareLayout[const.attributeLauncherSlotsLeft] - launchersFitted
        if balance < 1:
            return 'NotEnoughLauncherSlots'
    if dogmaStaticMgr.TypeHasEffect(moduleTypeID, const.effectTurretFitted):
        balance = hardwareLayout[const.attributeTurretSlotsLeft] - turretsFitted
        if balance < 1:
            return 'NotEnoughTurretSlots'
    if dogmaStaticMgr.TypeHasEffect(moduleTypeID, const.effectRigSlot):
        balance = hardwareLayout[const.attributeRigSlots] - rigsFitted
        if balance < 1:
            return 'NotEnoughUpgradeSlots'
    try:
        firstSlot, firstNonSlot = GetValidSlotsForType(dogmaStaticMgr, hardwareLayout, moduleTypeID)
        if flagID < firstSlot or flagID >= firstNonSlot:
            return 'SlotNotPresent'
    except UserError as e:
        if e.msg == 'ModuleNotPowered':
            return 'ModuleNotPowered'

    return ''


def IsFittable(effectID):
    isFittable = effectID in (const.effectHiPower,
     const.effectMedPower,
     const.effectLoPower,
     const.effectSubSystem,
     const.effectRigSlot,
     const.effectServiceSlot)
    return isFittable


def IsRightSlotForType(typeID, powerType):
    for effect in cfg.dgmtypeeffects.get(typeID, []):
        if IsFittable(effect.effectID) and effect.effectID == powerType:
            return True

    return False


def GetSlotTypeForType(typeID):
    for effect in cfg.dgmtypeeffects.get(typeID, []):
        if IsFittable(effect.effectID):
            return effect.effectID


POWER_TO_FLAG_DICT = {const.effectHiPower: invConst.hiSlotFlags,
 const.effectMedPower: invConst.medSlotFlags,
 const.effectLoPower: invConst.loSlotFlags,
 const.effectRigSlot: invConst.rigSlotFlags,
 const.effectSubSystem: invConst.subSystemSlotFlags}

def GetSlotListForTypeID(typeID):
    slotType = GetSlotTypeForType(typeID)
    return POWER_TO_FLAG_DICT.get(slotType, [])


def GetValidSlotsForType(dogmaIM, hardwareLayout, typeID):
    eff = dogmaIM.TypeGetEffects(typeID)
    if const.effectLoPower in eff:
        slotsAllowed = hardwareLayout[const.attributeLowSlots]
        firstSlot, firstNonSlot = const.flagLoSlot0, min(const.flagLoSlot0 + slotsAllowed, const.flagLoSlot7 + 1)
    elif const.effectHiPower in eff:
        slotsAllowed = hardwareLayout[const.attributeHiSlots]
        firstSlot, firstNonSlot = const.flagHiSlot0, min(const.flagHiSlot0 + slotsAllowed, const.flagHiSlot7 + 1)
    elif const.effectMedPower in eff:
        slotsAllowed = hardwareLayout[const.attributeMedSlots]
        firstSlot, firstNonSlot = const.flagMedSlot0, min(const.flagMedSlot0 + slotsAllowed, const.flagMedSlot7 + 1)
    elif const.effectRigSlot in eff:
        slotsAllowed = hardwareLayout[const.attributeRigSlots]
        firstSlot, firstNonSlot = const.flagRigSlot0, min(const.flagRigSlot0 + slotsAllowed, const.flagRigSlot7 + 1)
    elif const.effectSubSystem in eff:
        slotsAllowed = hardwareLayout[const.attributeMaxSubSystems]
        desiredFlag = int(dogmaIM.GetTypeAttribute2(typeID, const.attributeSubSystemSlot))
        if not cfg.IsSubSystemVisible(desiredFlag):
            firstSlot = const.flagSubSystemSlot0 + const.visibleSubSystems
            firstNonSlot = min(const.flagSubSystemSlot0 + slotsAllowed, const.flagSubSystemSlot7 + 1)
            if firstNonSlot < const.flagSubSystemSlot0 + const.visibleSubSystems:
                raise UserError('NoSuitableSlotsForThisSubSystem', {'subSystemName': (const.UE_TYPEID, typeID)})
        else:
            firstSlot, firstNonSlot = desiredFlag, desiredFlag + 1
            flag = desiredFlag
    elif const.effectServiceSlot in eff:
        slotsAllowed = hardwareLayout[const.attributeServiceSlots]
        firstSlot, firstNonSlot = const.flagServiceSlot0, min(const.flagServiceSlot0 + slotsAllowed, const.flagServiceSlot7 + 1)
    else:
        slotsAllowed = 0
    if slotsAllowed <= 0:
        raise UserError('ModuleNotPowered', {'type': typeID})
    return (int(firstSlot), int(firstNonSlot))


def CanFitModuleToShipTypeOrGroup(dogmaLocation, typeID):
    shipItem = dogmaLocation.dogmaItems[dogmaLocation.GetCurrentShipID()]
    return GetCanFitModuleTypeToShipType(dogmaLocation, shipItem.typeID, typeID)


def GetCanFitModuleTypeToShipType(dogmaLocation, shipTypeID, moduleTypeID):
    groupID = evetypes.GetGroupID(shipTypeID)
    return dogmaLocation.dogmaStaticMgr.CanFitModuleToShipTypeOrGroup(moduleTypeID, shipTypeID, groupID)


def IsRigSizeRestricted(dogmaStaticMgr, moduleTypeID, shipRigSize):
    if not dogmaStaticMgr.TypeHasEffect(moduleTypeID, const.effectRigSlot):
        return False
    rigSize = dogmaStaticMgr.GetTypeAttribute2(moduleTypeID, const.attributeRigSize)
    if shipRigSize != rigSize:
        return True
    return False


def IsCategoryOK_StructureVsShipRestrictions(shipTypeID, moduleTypeID):
    moduelCategoryID = evetypes.GetCategoryID(moduleTypeID)
    if evetypes.GetCategoryID(shipTypeID) == const.categoryStructure:
        return moduelCategoryID == const.categoryStructureModule
    else:
        return moduelCategoryID != const.categoryStructureModule


def IsRigSlot(flagID):
    return flagID in invConst.rigSlotFlags


def CheckCanFitType(dogmaLocation, typeID, locationID):
    maxGroupFitted = dogmaLocation.dogmaStaticMgr.GetTypeAttribute(typeID, const.attributeMaxGroupFitted)
    if maxGroupFitted:
        groupID = evetypes.GetGroupID(typeID)
        modulesByGroup = dogmaLocation.GetModuleListByShipGroup(locationID, groupID)
        if len(modulesByGroup) >= maxGroupFitted:
            shipItem = dogmaLocation.dogmaItems[locationID]
            raise UserError('CantFitTooManyByGroup', {'ship': shipItem.typeID,
             'module': typeID,
             'groupName': evetypes.GetGroupName(typeID),
             'noOfModules': int(maxGroupFitted),
             'noOfModulesFitted': len(modulesByGroup)})
    maxTypeFitted = dogmaLocation.dogmaStaticMgr.GetTypeAttribute(typeID, const.attributeMaxTypeFitted)
    if maxTypeFitted:
        modulesByType = dogmaLocation.GetModuleListByShipType(locationID, typeID)
        if len(modulesByType) >= maxTypeFitted:
            shipItem = dogmaLocation.dogmaItems[locationID]
            raise UserError('CantFitTooManyByType', {'ship': shipItem.typeID,
             'module': typeID,
             'noOfModules': int(maxTypeFitted),
             'noOfModulesFitted': len(modulesByType)})
