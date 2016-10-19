#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\common\script\planet\planetSurfaceCommon.py
pinTypeInstanceRestrictions = {const.typeTestSurfaceCommandCenter: 1}
pinTypeConstructionPrerequisitesSurface = {}
pinTypeConstructionPrerequisitesOrbit = {const.typeTestSurfaceCommandCenter: []}
pinTypePlanetRestrictions = {const.typeTestSurfaceCommandCenter: [const.typePlanetEarthlike]}

def GetMaximumPinInstances(pinTypeID):
    restriction = pinTypeInstanceRestrictions.get(pinTypeID, None)
    if restriction < 1:
        restriction = None
    return restriction


def GetSurfaceConstructionPrerequisites(pinTypeID):
    return pinTypeConstructionPrerequisitesSurface.get(pinTypeID, [])


def GetValidPlanetTypesForPinType(pinTypeID):
    return pinTypePlanetRestrictions.get(pinTypeID, [])


def GetOrbitalConstructionPrerequisites(pinTypeID):
    return pinTypeConstructionPrerequisitesOrbit.get(pinTypeID, [])


exports = {'planetSurfaceCommon.GetMaximumPinInstances': GetMaximumPinInstances,
 'planetSurfaceCommon.GetSurfaceConstructionPrerequisites': GetSurfaceConstructionPrerequisites,
 'planetSurfaceCommon.GetValidPlanetTypesForPinType': GetValidPlanetTypesForPinType,
 'planetSurfaceCommon.GetOrbitalConstructionPrerequisites': GetOrbitalConstructionPrerequisites}
