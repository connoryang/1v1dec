#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\parklife\tacticalConst.py
from carbonui.util.various_unsorted import SortListOfTuples
import evetypes
filterGroups = {const.groupStationServices,
 const.groupSecondarySun,
 const.groupTemporaryCloud,
 const.groupSolarSystem,
 const.groupRing,
 const.groupConstellation,
 const.groupRegion,
 const.groupCloud,
 const.groupComet,
 const.groupCosmicAnomaly,
 const.groupCosmicSignature,
 const.groupGlobalWarpDisruptor,
 const.groupPlanetaryCloud,
 const.groupCommandPins,
 const.groupExtractorPins,
 const.groupPlanetaryLinks,
 const.groupProcessPins,
 const.groupSpaceportPins,
 const.groupStoragePins,
 const.groupFlashpoint,
 const.groupSatellite,
 const.groupOrbitalTarget,
 const.groupMobileMicroJumpDisruptor,
 const.groupMobileDecoyUnit,
 const.groupMobileVault,
 const.groupObservatoryDeployable,
 const.groupFighterDrone,
 const.groupFighterBomber,
 const.groupTestOrbitals,
 const.groupStructureStargate,
 const.groupStructureAdministrationHub,
 const.groupStructureAdvertisementCenter,
 const.groupStructureIndustrialArray,
 const.groupStructureLaboratory,
 const.groupStructureDrillingPlatform,
 const.groupStructureObservatoryArray,
 11,
 const.groupExtractionControlUnitPins,
 const.groupDefenseBunkers,
 const.groupAncientCompressedIce,
 const.groupTerranArtifacts,
 const.groupShippingCrates,
 const.groupProximityDrone,
 const.groupRepairDrone,
 const.groupUnanchoringDrone,
 const.groupWarpScramblingDrone,
 const.groupZombieEntities,
 const.groupForceFieldArray,
 const.groupLogisticsArray,
 const.groupMobilePowerCore,
 const.groupMobileShieldGenerator,
 const.groupMobileStorage,
 const.groupStealthEmitterArray,
 const.groupStructureRepairArray,
 const.groupTargetPaintingBattery}
validCategories = (const.categoryStation,
 const.categoryShip,
 const.categoryEntity,
 const.categoryCelestial,
 const.categoryAsteroid,
 const.categoryDrone,
 const.categoryDeployable,
 const.categoryStarbase,
 const.categoryStructure,
 const.categoryCharge,
 const.categorySovereigntyStructure,
 const.categoryOrbital,
 const.categoryFighter)
bombGroups = (const.groupBomb,
 const.groupBombECM,
 const.groupBombEnergy,
 const.groupScannerProbe,
 const.groupWarpDisruptionProbe,
 const.groupSurveyProbe,
 const.groupStructureAreaMissile)
groups = []
for grpID in evetypes.IterateGroups():
    categoryID = evetypes.GetCategoryIDByGroup(grpID)
    if categoryID == const.categoryCharge and grpID not in bombGroups:
        continue
    if categoryID not in validCategories:
        continue
    if grpID in filterGroups:
        continue
    groupName = evetypes.GetGroupNameByGroup(grpID)
    groups.append((groupName.lower(), (grpID, groupName)))

groupList = SortListOfTuples(groups)
groupIDs = set((each[0] for each in groupList))

def IsInteractableEntity(groupID):
    return groupID in groupIDs
