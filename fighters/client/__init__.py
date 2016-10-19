#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\fighters\client\__init__.py
from eve.common.script.mgt.fighterConst import TEXTURE_BY_ROLE
from eve.common.script.sys.eveCfg import GetActiveShip
from eveexceptions import UserError
from fighters import SQUADRON_SIZE_SLIMITEM_NAME

def LoadShipIfNecessary(dogmaLocation, shipID):
    if not dogmaLocation.IsItemLoaded(shipID):
        dogmaLocation.LoadItem(shipID)


def GetFighterTubesForShip():
    myShip = GetActiveShip()
    dogmaLocation = sm.GetService('clientDogmaIM').GetDogmaLocation()
    LoadShipIfNecessary(dogmaLocation, myShip)
    numOfTubes = int(dogmaLocation.GetAttributeValue(myShip, const.attributeFighterTubes))
    return numOfTubes


def GetLightSupportHeavySlotsForShip():
    myShip = GetActiveShip()
    dogmaLocation = sm.GetService('clientDogmaIM').GetDogmaLocation()
    LoadShipIfNecessary(dogmaLocation, myShip)
    lightSlots = GetShipLightSlots(dogmaLocation, myShip)
    supportSlots = GetShipSupportSlots(dogmaLocation, myShip)
    heavySlots = GetShipHeavySlots(dogmaLocation, myShip)
    return (lightSlots, supportSlots, heavySlots)


def GetShipLightSlots(dogmaLocation, shipID):
    lightSlots = int(dogmaLocation.GetAttributeValue(shipID, const.attributeFighterLightSlots))
    return lightSlots


def GetShipSupportSlots(dogmaLocation, shipID):
    supportSlots = int(dogmaLocation.GetAttributeValue(shipID, const.attributeFighterSupportSlots))
    return supportSlots


def GetShipHeavySlots(dogmaLocation, shipID):
    heavySlots = int(dogmaLocation.GetAttributeValue(shipID, const.attributeFighterHeavySlots))
    return heavySlots


def GetMaxSquadronSize(typeID):
    return int(GetFighterAttribute(typeID, const.attributeFighterSquadronMaxSize))


def SquadronIsLight(typeID):
    return bool(GetFighterAttribute(typeID, const.attributeFighterSquadronIsLight))


def SquadronIsSupport(typeID):
    return bool(GetFighterAttribute(typeID, const.attributeFighterSquadronIsSupport))


def SquadronIsHeavy(typeID):
    return bool(GetFighterAttribute(typeID, const.attributeFighterSquadronIsHeavy))


def GetFighterAttribute(typeID, attributeID):
    return sm.GetService('godma').GetTypeAttribute(typeID, attributeID)


def GetSquadronSizeFromSlimItem(slimItem):
    return getattr(slimItem, SQUADRON_SIZE_SLIMITEM_NAME)


def GetSquadronClassResPath(typeID):
    if SquadronIsHeavy(typeID):
        return 'res:/UI/Texture/classes/CarrierBay/iconFighterHeavy.png'
    if SquadronIsSupport(typeID):
        return 'res:/UI/Texture/classes/CarrierBay/iconFighterMedium.png'
    if SquadronIsLight(typeID):
        return 'res:/UI/Texture/classes/CarrierBay/iconFighterLight.png'


def GetSquadronClassTooltip(typeID):
    if SquadronIsHeavy(typeID):
        return 'UI/Fighters/Class/Heavy'
    if SquadronIsSupport(typeID):
        return 'UI/Fighters/Class/Support'
    if SquadronIsLight(typeID):
        return 'UI/Fighters/Class/Light'


def GetSquadronRole(typeID):
    return int(GetFighterAttribute(typeID, const.attributeFighterSquadronRole))


def GetSquadronRoleResPath(typeID):
    squadronRoleID = GetSquadronRole(typeID)
    return TEXTURE_BY_ROLE[squadronRoleID]


def ConvertAbilityFailureReason(fighterID, abilitySlotID, failureReasonUserError):
    if failureReasonUserError.msg == 'ModuleActivationDeniedSafetyPreventsSuspect':
        return UserError('CannotActivateAbilitySafetyPreventsSuspect', failureReasonUserError.dict)
    if failureReasonUserError.msg == 'ModuleActivationDeniedSafetyPreventsCriminal':
        return UserError('CannotActivateAbilitySafetyPreventsCriminal', failureReasonUserError.dict)
    if failureReasonUserError.msg == 'ModuleActivationDeniedSafetyPreventsLimitedEngagement':
        return UserError('CannotActivateAbilitySafetyPreventsLimitedEngagement', failureReasonUserError.dict)
    return failureReasonUserError
