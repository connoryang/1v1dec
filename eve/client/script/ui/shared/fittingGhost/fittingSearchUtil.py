#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\fittingGhost\fittingSearchUtil.py
import itertools
from eve.common.lib.appConst import GROUP_CAPITALSHIPS
import evetypes
from shipfitting.fittingStuff import IsModuleTooBig, GetSlotTypeForType, GetCanFitModuleTypeToShipType, IsRigSizeRestricted, IsCategoryOK_StructureVsShipRestrictions
MODULE_CATEGORIES = (const.marketCategoryShipEquipment,
 const.marketCategoryShipModifications,
 const.marketCategoryDrones,
 const.marketCategoryStructureEquipment,
 const.marketCategoryShipModifications)

class SearchFittingHelper(object):
    __notifyevents__ = ['OnSkillsChanged']

    def __init__(self, cfg, *args):
        self.cfg = cfg
        self.dogmaStaticMgr = sm.GetService('clientDogmaIM').GetDogmaLocation().dogmaStaticMgr
        self.ResetAllVariables()
        sm.RegisterNotify(self)

    def ResetAllVariables(self):
        self.typeNames_lower = {}
        self.canFitModuleToShip = {}
        self.rigRestricted = {}
        self.tooBigModule = {}
        self.restrictedByDroneOrFighter = {}
        self.restrictedByModularShipRules = {}
        self.slotTypeByTypeID = {}
        self.shipRigSizeByTypeID = {}
        self.isCapitalShipByTypeID = {}
        self.marketCategoryByTypeID = {}
        self.isHiSlot = {}
        self.isMedSlot = {}
        self.isLoSlot = {}
        self.isRigSlot = {}
        self.isDrone = {}
        self.isFighter = {}
        self.isDroneOrFighter = {}
        self.missingSkills = {}
        self.cpuRequirementsByModuleTypeID = {}
        self.powergridRequirementsByModuleTypeID = {}
        self.searchableTypeIDs = None

    def GetTypeName(self, typeID):
        try:
            return self.typeNames_lower[typeID]
        except KeyError:
            t = evetypes.GetName(typeID)
            lower = t.lower()
            self.typeNames_lower[typeID] = lower
            return lower

    def ResetCpuAndPowergridDicts(self):
        self.cpuRequirementsByModuleTypeID = {}
        self.powergridRequirementsByModuleTypeID = {}

    def CanFitModuleToShipTypeOrGroup(self, shipTypeID, dogmaLocation, moduleTypeID):
        dictKey = (shipTypeID, moduleTypeID)
        try:
            return self.canFitModuleToShip[dictKey]
        except KeyError:
            canFit = GetCanFitModuleTypeToShipType(dogmaLocation, shipTypeID, moduleTypeID)
            if canFit:
                canFit = IsCategoryOK_StructureVsShipRestrictions(shipTypeID, moduleTypeID)
            self.canFitModuleToShip[dictKey] = canFit
            return canFit

    def IsRigSizeRestricted(self, dogmaStaticMgr, moduleTypeID, shipRigSize):
        dictKey = (moduleTypeID, shipRigSize)
        try:
            return self.rigRestricted[dictKey]
        except KeyError:
            isRestricted = IsRigSizeRestricted(dogmaStaticMgr, moduleTypeID, shipRigSize)
            self.rigRestricted[dictKey] = isRestricted
            return isRestricted

    def IsModuleTooBig(self, shipTypeID, moduleTypeID, isCapitalShip):
        dictKey = (shipTypeID, moduleTypeID)
        try:
            return self.tooBigModule[dictKey]
        except KeyError:
            tooBig = IsModuleTooBig(moduleTypeID, shipTypeID, isCapitalShip)
            self.tooBigModule[dictKey] = tooBig
            return tooBig

    def RestrictedByDroneOrFighter(self, dogmaStaticMgr, shipTypeID, typeID):
        dictKey = (shipTypeID, typeID)
        try:
            return self.restrictedByDroneOrFighter[dictKey]
        except KeyError:
            restricted = False
            if self.IsDroneOrFighter(typeID):
                isDrone = self.IsDrone(typeID)
                if isDrone:
                    droneBayCapacity = dogmaStaticMgr.GetTypeAttribute2(shipTypeID, const.attributeDroneCapacity)
                    if droneBayCapacity == 0:
                        restricted = True
                else:
                    fighterBayCapacity = dogmaStaticMgr.GetTypeAttribute2(shipTypeID, const.attributeFighterCapacity)
                    if fighterBayCapacity == 0:
                        restricted = True
            self.restrictedByDroneOrFighter[dictKey] = restricted
            return restricted

    def IsModuleRestrictedForModularShip(self, dogmaStaticMgr, shipTypeID, moduleTypeD):
        dictKey = (shipTypeID, moduleTypeD)
        try:
            return self.restrictedByModularShipRules[dictKey]
        except KeyError:
            isRestricted = False
            moduleCategoryID = evetypes.GetCategoryID(moduleTypeD)
            if moduleCategoryID == const.categorySubSystem:
                validShipTypeID = dogmaStaticMgr.GetTypeAttribute2(moduleTypeD, const.attributeFitsToShipType)
                if validShipTypeID != shipTypeID:
                    isRestricted = True
            self.restrictedByModularShipRules[dictKey] = isRestricted
            return isRestricted

    def IsHislotModule(self, moduleTypeID):
        return self.IsSpecificSlotType(moduleTypeID, const.effectHiPower, self.isHiSlot)

    def IsMedslotModule(self, moduleTypeID):
        return self.IsSpecificSlotType(moduleTypeID, const.effectMedPower, self.isMedSlot)

    def IsLoSlot(self, moduleTypeID):
        return self.IsSpecificSlotType(moduleTypeID, const.effectLoPower, self.isLoSlot)

    def IsRigSlot(self, moduleTypeID):
        return self.IsSpecificSlotType(moduleTypeID, const.effectRigSlot, self.isRigSlot)

    def IsDroneOrFighter(self, typeID):
        try:
            return self.isDroneOrFighter[typeID]
        except KeyError:
            isDroneOrFighter = self.IsDrone(typeID) or self.IsFighter(typeID)
            self.isDroneOrFighter[typeID] = isDroneOrFighter
            return isDroneOrFighter

    def IsDrone(self, typeID):
        try:
            return self.isDrone[typeID]
        except KeyError:
            categoryID = evetypes.GetCategoryID(typeID)
            isDrone = categoryID == const.categoryDrone
            self.isDrone[typeID] = isDrone
            return isDrone

    def IsFighter(self, typeID):
        try:
            return self.isFighter[typeID]
        except KeyError:
            categoryID = evetypes.GetCategoryID(typeID)
            isFighter = categoryID == const.categoryFighter
            self.isFighter[typeID] = isFighter
            return isFighter

    def IsSpecificSlotType(self, moduleTypeID, slotTypeWanted, cacheDict):
        try:
            return cacheDict[moduleTypeID]
        except KeyError:
            slotType = self.GetSlotTypeForModuleType(moduleTypeID)
            if slotType == slotTypeWanted:
                isRightType = True
            else:
                isRightType = False
            cacheDict[moduleTypeID] = isRightType
            return isRightType

    def GetSlotTypeForModuleType(self, moduleTypeID):
        try:
            return self.slotTypeByTypeID[moduleTypeID]
        except KeyError:
            slotType = GetSlotTypeForType(moduleTypeID)
            self.slotTypeByTypeID[moduleTypeID] = slotType
            return slotType

    def GetShipRigSize(self, dogmaStaticMgr, shipTypeID):
        try:
            return self.shipRigSizeByTypeID[shipTypeID]
        except KeyError:
            rigSize = dogmaStaticMgr.GetTypeAttribute2(shipTypeID, const.attributeRigSize)
            self.shipRigSizeByTypeID[shipTypeID] = rigSize
            return rigSize

    def IsCapitalSize(self, groupID):
        try:
            return self.isCapitalShipByTypeID[groupID]
        except KeyError:
            isCapitalSize = groupID in self.cfg.GetShipGroupByClassType()[GROUP_CAPITALSHIPS]
            self.isCapitalShipByTypeID[groupID] = isCapitalSize
            return isCapitalSize

    def GetCPUForModuleType(self, ghostFitting, shipID, moduleTypeID, shipTypeID, resourceRigsFitted):
        dictKey = (shipTypeID, resourceRigsFitted, moduleTypeID)
        try:
            return self.cpuRequirementsByModuleTypeID[dictKey]
        except KeyError:
            cpuValue = self.dogmaStaticMgr.GetTypeAttribute2(moduleTypeID, const.attributeCpu)
            if cpuValue != 0:
                cpuValue, powerValue = self.GetCpuAndPower(ghostFitting, shipID, moduleTypeID, dictKey)
            else:
                self.cpuRequirementsByModuleTypeID[dictKey] = cpuValue
            return cpuValue

    def GetPowergridForModuleType(self, ghostFitting, shipID, moduleTypeID, shipTypeID, resourceRigsFitted):
        dictKey = (shipTypeID, resourceRigsFitted, moduleTypeID)
        try:
            return self.powergridRequirementsByModuleTypeID[dictKey]
        except KeyError:
            powerValue = self.dogmaStaticMgr.GetTypeAttribute2(moduleTypeID, const.attributePower)
            if powerValue != 0:
                cpuValue, powerValue = self.GetCpuAndPower(ghostFitting, shipID, moduleTypeID, dictKey)
            else:
                self.powergridRequirementsByModuleTypeID[dictKey] = powerValue
            return powerValue

    def GetSearcableTypeIDs(self, marketGroups):
        if not self.searchableTypeIDs:
            myGroups = []
            for x in MODULE_CATEGORIES:
                myGroups += marketGroups[x]

            typeIDs = [ i for i in itertools.chain.from_iterable([ x.types for x in myGroups ]) ]
            self.searchableTypeIDs = typeIDs
        return self.searchableTypeIDs

    def GetMarketCategoryForType(self, typeID, allMarketGroups):
        try:
            return self.marketCategoryByTypeID[typeID]
        except KeyError:
            for mg in allMarketGroups:
                if typeID in mg.types:
                    topMarketCategory = mg
                    break
            else:
                topMarketCategory = None

            self.marketCategoryByTypeID[typeID] = topMarketCategory
            return topMarketCategory

    def GetCpuAndPower(self, ghostFittingSvc, shipID, moduleTypeID, dictKey):
        info = ghostFittingSvc.LoadFakeItem(shipID, moduleTypeID)
        self.cpuRequirementsByModuleTypeID[dictKey] = info.cpuValue
        self.powergridRequirementsByModuleTypeID[dictKey] = info.powerValue
        return (info.cpuValue, info.powerValue)

    def GetMissingSkills(self, typeID, dogmaLocation, skillSvc):
        try:
            return self.missingSkills[typeID]
        except KeyError:
            missingSkillsForType = dogmaLocation.GetMissingSkills(typeID, skillSvc)
            self.missingSkills[typeID] = missingSkillsForType
            return missingSkillsForType

    def OnSkillsChanged(self, skillInfos):
        toRemove = []
        for changedSkillTypeID, skillInfo in skillInfos.iteritems():
            newSkillLevel = skillInfo.skillLevel
            for eachTypeID, missingSkillInfo in self.missingSkills.iteritems():
                missingLevel = missingSkillInfo.get(changedSkillTypeID, None)
                if missingLevel is not None and missingLevel <= newSkillLevel:
                    toRemove.append((eachTypeID, changedSkillTypeID))

        for typeID, skillTypeID in toRemove:
            self.missingSkills[typeID].pop(skillTypeID)

        if toRemove:
            sm.ScatterEvent('OnSkillFilteringUpdated')

    def BuildNameDict(self):
        marketGroups = sm.GetService('marketutils').GetMarketGroups()
        typeIDs = set(self.GetSearcableTypeIDs(marketGroups))
        for text, typeID in evetypes.GetTypeIDByNameDict().iteritems():
            if typeID not in typeIDs:
                continue
            self.typeNames_lower[typeID] = text
