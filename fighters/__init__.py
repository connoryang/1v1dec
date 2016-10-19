#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\fighters\__init__.py
import dogma.const as dogmaConst
from inventorycommon.const import flagFighterTube0, flagFighterTube1, flagFighterTube2, flagFighterTube3, flagFighterTube4
from .storages import AbilityStorage, TypeStorage
ABILITY_SLOT_0 = 0
ABILITY_SLOT_1 = 1
ABILITY_SLOT_2 = 2
ABILITY_SLOT_IDS = (ABILITY_SLOT_0, ABILITY_SLOT_1, ABILITY_SLOT_2)
ABILITY_SLOT_ID_KEY = 'abilitySlotID'
SLOTNUMBER_BY_TUBEFLAG = {flagFighterTube0: 1,
 flagFighterTube1: 2,
 flagFighterTube2: 3,
 flagFighterTube3: 4,
 flagFighterTube4: 5}
TARGET_MODE_UNTARGETED = 'untargeted'
TARGET_MODE_ITEMTARGETED = 'itemTargeted'
TARGET_MODE_POINTTARGETED = 'pointTargeted'
SQUADRON_SIZE_SLIMITEM_NAME = 'fighter.squadronSize'
MAX_SQUADRON_SIZE = 12
MAX_SCOOP_DISTANCE = 5000
DEFAULT_CONTROLLER_ORBIT_DISTANCE = 1500
MINIMUM_TARGET_ORBIT_DISTANCE = 1000
FIGHTER_CLASS_LIGHT = 'LIGHT'
FIGHTER_CLASS_SUPPORT = 'SUPPORT'
FIGHTER_CLASS_HEAVY = 'HEAVY'
fighterClassByDogmaAttribute = {dogmaConst.attributeFighterSquadronIsLight: FIGHTER_CLASS_LIGHT,
 dogmaConst.attributeFighterSquadronIsSupport: FIGHTER_CLASS_SUPPORT,
 dogmaConst.attributeFighterSquadronIsHeavy: FIGHTER_CLASS_HEAVY}
shipTubeCountAttributeByFighterClass = {FIGHTER_CLASS_LIGHT: dogmaConst.attributeFighterLightSlots,
 FIGHTER_CLASS_SUPPORT: dogmaConst.attributeFighterSupportSlots,
 FIGHTER_CLASS_HEAVY: dogmaConst.attributeFighterHeavySlots}
classNameMessageByFighterClass = {FIGHTER_CLASS_LIGHT: 'UI/Fighters/Class/Light',
 FIGHTER_CLASS_SUPPORT: 'UI/Fighters/Class/Support',
 FIGHTER_CLASS_HEAVY: 'UI/Fighters/Class/Heavy'}
numTubesByFlag = {flagFighterTube0: 1,
 flagFighterTube1: 2,
 flagFighterTube2: 3,
 flagFighterTube3: 4,
 flagFighterTube4: 5}

def GetAbilityIDForSlot(fighterTypeID, abilitySlotID):
    for slotID, typeAbility in IterTypeAbilities(fighterTypeID):
        if abilitySlotID == slotID and typeAbility is not None:
            return typeAbility.abilityID


def GetAbilityNameIDForSlot(fighterTypeID, abilitySlotID):
    abilityID = GetAbilityIDForSlot(fighterTypeID, abilitySlotID)
    ability = AbilityStorage()[abilityID]
    return ability.displayNameID


def GetCooldownSecondsForSlot(fighterTypeID, abilitySlotID):
    for slotID, typeAbility in IterTypeAbilities(fighterTypeID):
        if abilitySlotID == slotID and typeAbility is not None:
            return typeAbility.cooldownSeconds


def GetChargeCountForTypeAndSlot(fighterTypeID, abilitySlotID):
    for slotID, typeAbility in IterTypeAbilities(fighterTypeID):
        if abilitySlotID == slotID and typeAbility is not None:
            if typeAbility.charges is not None:
                return typeAbility.charges.chargeCount


def GetChargeRearmTimeForTypeAndSlot(fighterTypeID, abilitySlotID):
    for slotID, typeAbility in IterTypeAbilities(fighterTypeID):
        if abilitySlotID == slotID and typeAbility is not None:
            if typeAbility.charges is not None:
                return typeAbility.charges.rearmTimeSeconds


def GetEffectRepeatCountForAbility(fighterTypeID, abilitySlotID):
    chargeCountForTypeAndSlot = GetChargeCountForTypeAndSlot(fighterTypeID, abilitySlotID)
    if chargeCountForTypeAndSlot is not None:
        return 1
    cooldownSeconds = GetCooldownSecondsForSlot(fighterTypeID, abilitySlotID)
    if cooldownSeconds is not None:
        return 1
    return 1000


def IterTypeAbilities(fighterTypeID):
    typeStorage = TypeStorage()
    typeAbilities = typeStorage.get(fighterTypeID)
    if typeAbilities is not None:
        yield (ABILITY_SLOT_0, typeAbilities.abilitySlot0)
        yield (ABILITY_SLOT_1, typeAbilities.abilitySlot1)
        yield (ABILITY_SLOT_2, typeAbilities.abilitySlot2)


def CheckAbilitySlotIDIsValid(abilitySlotID):
    if abilitySlotID not in ABILITY_SLOT_IDS:
        raise ValueError('Invalid ability slot ID')


def GetAbilityTargetMode(abilityID):
    abilityStorage = AbilityStorage()
    try:
        ability = abilityStorage[abilityID]
    except KeyError:
        raise ValueError('Invalid abilityID')

    if ability is not None:
        return ability.targetMode


def GetTurretGraphicIDsForFighter(fighterTypeID):
    turretGraphicIDs = {}
    abilityStorage = AbilityStorage()
    for abilitySlotID, typeAbility in IterTypeAbilities(fighterTypeID):
        if typeAbility is None:
            continue
        abilityID = typeAbility.abilityID
        ability = abilityStorage[abilityID]
        if ability.turretGraphicID:
            turretGraphicIDs[abilitySlotID] = ability.turretGraphicID

    return turretGraphicIDs
