#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\structures\deployment.py
import math
import inventorycommon.const
GROUP_DISTANCE = {inventorycommon.const.groupWreck: 5000,
 inventorycommon.const.groupCargoContainer: 5000,
 inventorycommon.const.groupSpawnContainer: 5000,
 inventorycommon.const.groupSecureCargoContainer: 5000,
 inventorycommon.const.groupAuditLogSecureContainer: 5000,
 inventorycommon.const.groupFreightContainer: 5000}
CATEGORY_DISTANCES = {inventorycommon.const.categoryEntity: 5000,
 inventorycommon.const.categoryShip: 5000,
 inventorycommon.const.categoryDrone: 5000,
 inventorycommon.const.categoryFighter: 5000,
 inventorycommon.const.categoryDeployable: 5000,
 inventorycommon.const.categoryAsteroid: 5000,
 inventorycommon.const.categoryCelestial: 1000000,
 inventorycommon.const.categoryOrbital: 1000000,
 inventorycommon.const.categorySovereigntyStructure: 1000000,
 inventorycommon.const.categoryStation: 1000000,
 inventorycommon.const.categoryStarbase: 1000000,
 inventorycommon.const.categoryStructure: 1000000}

def GetDeploymentDistance(typeID):
    import evetypes
    groupID = evetypes.GetGroupID(typeID)
    categoryID = evetypes.GetCategoryID(typeID)
    return GROUP_DISTANCE.get(groupID, CATEGORY_DISTANCES.get(categoryID, 0))


def IsValidLocation(typeID, location, balls):
    return FindDeploymentConflict(typeID, location, balls) is None


def FindDeploymentConflict(typeID, location, balls):
    import evetypes
    typeRadius = evetypes.GetRadius(typeID)
    for typeID, position, radius in balls:
        minimum = GetDeploymentDistance(typeID)
        if minimum and DistanceBetween(location, position) < minimum + typeRadius + radius:
            return (typeID, minimum)


def DistanceBetween(a, b):
    return math.sqrt(sum([ (a - b) ** 2 for a, b in zip(a, b) ]))
