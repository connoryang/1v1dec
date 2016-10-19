#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\dogma\effects\__init__.py
import evetypes
from dogma import const
EXPRESSIONS = {'LocationRequiredSkillModifier': 'on all items located in {domain} requiring skill {skillTypeID}',
 'LocationGroupModifier': 'on all items located in {domain} in group {groupID}',
 'OwnerRequiredSkillModifier': 'on all items owned by {domain} that require skill {skillTypeID}',
 'ItemModifier': '{domain}',
 'GangItemModifier': 'on ships in gang',
 'GangRequiredSkillModifier': 'on items fitted to ships in gang that require skill {skillTypeID}'}

def _GetModifierDict(realDict):
    ret = {}
    for key, value in realDict.iteritems():
        if key in ('modifiedAttributeID', 'modifyingAttributeID'):
            newValue = cfg.dgmattribs.Get(value).attributeName
        elif key == 'domain':
            if value is None:
                newValue = 'self'
            else:
                newValue = value.replace('ID', '')
        elif key == 'skillTypeID':
            newValue = evetypes.GetName(value)
        elif key == 'groupID':
            newValue = evetypes.GetGroupNameByGroup(value)
        else:
            newValue = value
        ret[key] = newValue

    ret['domainInfo'] = EXPRESSIONS.get(ret['func'], ' UNKNOWN {func}').format(**ret)
    return ret


def IterReadableModifierStrings(modifiers):
    for modifierDict in modifiers:
        if modifierDict['func'] in EXPRESSIONS:
            formatDict = _GetModifierDict(modifierDict)
            yield 'Modifies {modifiedAttributeID} on {domainInfo} with attribute {modifyingAttributeID}'.format(**formatDict)
        elif modifierDict['func'] == 'EffectStopper':
            effectID = modifierDict['effectID']
            yield 'Forcibly stops effect %s' % cfg.dgmeffects.Get(effectID).effectName


def IsCloakingEffect(effectID):
    return effectID in [const.effectCloaking, const.effectCloakingWarpSafe, const.effectCloakingPrototype]


class Effect(object):
    __guid__ = 'dogmaXP.Effect'
    isPythonEffect = True
    __modifier_only__ = False
    __modifies_character__ = False
    __modifies_ship__ = False
    __modifier_domain_other__ = False
    MODIFIER_CHANGES = []
    LOCATION_AND_GROUP_MODIFIER_CHANGES = []
    SKILL_MODIFIER_CHANGES_FOR_LOCATION = []
    SKILL_MODIFER_CHANGES_FOR_OWNER = []

    def RestrictedStop(self, *args):
        pass

    def PreStartChecks(self, *args):
        pass

    def StartChecks(self, *args):
        pass

    def Start(self, *args):
        pass

    def Stop(self, *args):
        pass

    def AddModifiers(self, dogmaLM, toItemID, fromItemID):
        for operation, toAttribID, fromAttribID in self.MODIFIER_CHANGES:
            dogmaLM.AddModifier(operation, toItemID, toAttribID, fromItemID, fromAttribID)

    def RemoveModifiers(self, dogmaLM, toItemID, fromItemID):
        for operation, toAttribID, fromAttribID in self.MODIFIER_CHANGES:
            dogmaLM.RemoveModifier(operation, toItemID, toAttribID, fromItemID, fromAttribID)

    def AddLocationGroupModifiers(self, dogmaLM, toLocationID, fromItemID):
        for operation, groupID, toAttribID, fromAttribID in self.LOCATION_AND_GROUP_MODIFIER_CHANGES:
            dogmaLM.AddLocationGroupModifier(operation, toLocationID, groupID, toAttribID, fromItemID, fromAttribID)

    def RemoveLocationGroupModifiers(self, dogmaLM, toLocationID, fromItemID):
        for operation, groupID, toAttribID, fromAttribID in self.LOCATION_AND_GROUP_MODIFIER_CHANGES:
            dogmaLM.RemoveLocationGroupModifier(operation, toLocationID, groupID, toAttribID, fromItemID, fromAttribID)

    def AddLocationRequiredSkillModifiers(self, dogmaLM, toLocationID, fromItemID):
        for operation, skillTypeID, affectedAttributeID, affectingAttributeID in self.SKILL_MODIFIER_CHANGES_FOR_LOCATION:
            dogmaLM.AddLocationRequiredSkillModifier(operation, toLocationID, skillTypeID, affectedAttributeID, fromItemID, affectingAttributeID)

    def RemoveLocationRequiredSkillModifiers(self, dogmaLM, toLocationID, fromItemID):
        for operation, skillTypeID, affectedAttributeID, affectingAttributeID in self.SKILL_MODIFIER_CHANGES_FOR_LOCATION:
            dogmaLM.RemoveLocationRequiredSkillModifier(operation, toLocationID, skillTypeID, affectedAttributeID, fromItemID, affectingAttributeID)

    def AddOwnerRequiredSkillModifiers(self, dogmaLM, ownerID, fromItemID):
        for operation, affectedSkillTypeID, affectedAttributeID, affectingAttributeID in self.SKILL_MODIFER_CHANGES_FOR_OWNER:
            dogmaLM.AddOwnerRequiredSkillModifier(operation, ownerID, affectedSkillTypeID, affectedAttributeID, fromItemID, affectingAttributeID)

    def RemoveOwnerRequiredSkillModifiers(self, dogmaLM, ownerID, fromItemID):
        for operation, affectedSkillTypeID, affectedAttributeID, affectingAttributeID in self.SKILL_MODIFER_CHANGES_FOR_OWNER:
            dogmaLM.RemoveOwnerRequiredSkillModifier(operation, ownerID, affectedSkillTypeID, affectedAttributeID, fromItemID, affectingAttributeID)


def GetName(effectID):
    return cfg.dgmeffects.Get(effectID).effectName


def IsDefault(typeID, effectID):
    for effectRow in cfg.dgmtypeeffects[typeID]:
        if effectID == effectRow.effectID:
            if effectRow.isDefault:
                return True
            else:
                return False

    raise KeyError()


def GetEwarTypeByEffectID(effectID):
    effect = cfg.dgmeffects.Get(effectID)
    if effect.electronicChance:
        return 'electronic'
    if effect.propulsionChance:
        return 'propulsion'
    ewarType = ALL_EWAR_TYPES.get(effectID, None)
    return ewarType


ALL_EWAR_TYPES = {}
OFFENSIVE_EWAR_TYPES = {const.effectEwTargetPaint: 'ewTargetPaint',
 const.effectTargetMaxTargetRangeAndScanResolutionBonusHostile: 'ewRemoteSensorDamp',
 const.effectTargetGunneryMaxRangeAndTrackingSpeedBonusHostile: 'ewTrackingDisrupt',
 const.effectTargetGunneryMaxRangeAndTrackingSpeedAndFalloffBonusHostile: 'ewTrackingDisrupt',
 const.effectTurretWeaponRangeFalloffTrackingSpeedMultiplyTargetHostile: 'ewTrackingDisrupt',
 const.effectEntitySensorDampen: 'ewRemoteSensorDamp',
 const.effectSensorBoostTargetedHostile: 'ewRemoteSensorDamp',
 const.effectEntityTrackingDisrupt: 'ewTrackingDisrupt',
 const.effectGuidanceDisrupt: 'ewGuidanceDisrupt',
 const.effectEntityTargetPaint: 'ewTargetPaint',
 const.effectWarpScramble: 'warpScrambler',
 const.effectDecreaseTargetSpeed: 'webify',
 const.effectWarpScrambleForEntity: 'warpScrambler',
 const.effectModifyTargetSpeed2: 'webify',
 const.effectConcordWarpScramble: 'warpScrambler',
 const.effectConcordModifyTargetSpeed: 'webify',
 const.effectWarpScrambleBlockMWDWithNPCEffect: 'warpScramblerMWD',
 const.effectWarpDisruptSphere: 'focusedWarpScrambler',
 const.effectLeech: 'ewEnergyVampire',
 const.effectEnergyDestabilizationNew: 'ewEnergyNeut',
 const.effectEntityCapacitorDrain: 'ewEnergyNeut',
 const.effectEnergyDestabilizationForStructure: 'ewEnergyNeut',
 const.effectEnergyNeutralizerFalloff: 'ewEnergyNeut',
 const.effectEnergyNosferatuFalloff: 'ewEnergyVampire',
 const.effectWarpScrambleForStructure: 'warpScrambler',
 const.effectDecreaseTargetSpeedForStructures: 'webify',
 const.effectEssWarpScramble: 'warpScrambler',
 const.effectWarpScrambleTargetMWDBlockActivationForEntity: 'warpScramblerMWD',
 const.effectEwTestEffectJam: 'electronic',
 const.effectEntityTargetJam: 'electronic',
 const.effectFighterAbilityECM: 'electronic',
 const.effectFighterAbilityEnergyNeutralizer: 'ewEnergyNeut',
 const.effectFighterAbilityStasisWebifier: 'webify',
 const.effectFighterAbilityWarpDisruption: 'warpScrambler',
 const.effectFighterAbilityTackle: 'fighterTackle',
 const.effectRemoteSensorDampFalloff: 'ewRemoteSensorDamp',
 const.effectRemoteTargetPaintFalloff: 'ewTargetPaint',
 const.effectRemoteTrackingDisruptFalloff: 'ewTrackingDisrupt',
 const.effectRemoteWebifierFalloff: 'webify',
 const.effectRemoteGuidanceDisruptFalloff: 'ewGuidanceDisrupt',
 const.effectRemoteECMFalloff: 'electronic',
 const.effectEntityECMFalloff: 'electronic',
 const.effectStructureEwEffectJam: 'electronic',
 const.effectStructureEwTargetPaint: 'ewTargetPaint',
 const.effectStructureEnergyNeutralizerFalloff: 'ewEnergyNeut',
 const.effectStructureWarpScrambleBlockMWDWithNPCEffect: 'warpScramblerMWD',
 const.effectStructureDecreaseTargetSpeed: 'webify',
 const.effectStructureTargetMaxTargetRangeAndScanResolutionBonusHostile: 'ewRemoteSensorDamp',
 const.effectStructureTargetGunneryMaxRangeAndTrackingSpeedAndFalloffBonusHostile: 'ewTrackingDisrupt',
 const.effectDoomsdayAOEECM: 'electronic',
 const.effectDoomsdayAOEPaint: 'ewTargetPaint',
 const.effectDoomsdayAOENeut: 'ewEnergyNeut',
 const.effectDoomsdayAOEWeb: 'webify',
 const.effectDoomsdayAOETrack: 'ewTrackingDisrupt',
 const.effectDoomsdayAOEDamp: 'ewRemoteSensorDamp',
 const.effectStructureModuleEffectStasisWebifier: 'webify',
 const.effectStructureModuleEffectTargetPainter: 'ewTargetPaint',
 const.effectStructureModuleEffectRemoteSensorDampener: 'ewRemoteSensorDamp',
 const.effectStructureModuleEffectECM: 'electronic',
 const.effectStructureModuleEffectWeaponDisruption: 'ewTrackingDisrupt',
 const.effectEntityEnergyNeutralizerFalloff: 'ewEnergyNeut',
 const.effectStarbaseEnergyNeutralizerFalloff: 'ewEnergyNeut',
 const.effectRemoteSensorDampEntity: 'ewRemoteSensorDamp',
 const.effectRemoteTargetPaintEntity: 'ewTargetPaint',
 const.effectRemoteWeaponDisruptEntity: 'ewTrackingDisrupt',
 const.effectRemoteWebifierEntity: 'webify'}
DEFENSIVE_EWAR_TYPES = {const.effectRemoteTracking: 'remoteTracking',
 const.effectEnergyTransfer: 'energyTransfer',
 const.effectTargetMaxTargetRangeAndScanResolutionBonusAssistance: 'sensorBooster',
 const.effectScanStrengthTargetPercentBonus: 'eccmProjector',
 const.effectRemoteHullRepair: 'remoteHullRepair',
 const.effectTargetArmorRepair: 'remoteArmorRepair',
 const.effectShieldTransfer: 'shieldTransfer',
 const.effectRemoteArmorRepairFalloff: 'remoteArmorRepair',
 const.effectAncillaryRemoteArmorRepairer: 'remoteArmorRepair',
 const.effectRemoteEnergyTransferFalloff: 'energyTransfer',
 const.effectRemoteHullRepairFalloff: 'remoteHullRepair',
 const.effectRemoteShieldTransferFalloff: 'shieldTransfer',
 const.effectAncillaryRemoteShieldBooster: 'shieldTransfer',
 const.effectRemoteSensorBoostFalloff: 'sensorBooster',
 const.effectRemoteTrackingAssistFalloff: 'remoteTracking',
 const.effectRemoteECCMFalloff: 'eccmProjector',
 const.effectStructureTargetMaxTargetRangeAndScanResolutionBonusAssistance: 'sensorBooster',
 const.effectStructureTargetGunneryMaxRangeFalloffTrackingSpeedBonusAssistance: 'remoteTracking',
 const.effectRemoteArmorRepairEntity: 'remoteArmorRepair',
 const.effectRemoteHullRepairEntity: 'shieldTransfer',
 const.effectRemoteShieldTransferEntity: 'remoteHullRepair'}
ALL_EWAR_TYPES = OFFENSIVE_EWAR_TYPES.copy()
ALL_EWAR_TYPES.update(DEFENSIVE_EWAR_TYPES)
SKILL_ACCELERATOR_EFFECT_IDS = {const.effectAnalyticalMindIntelligenceBonusModAddIntelligenceLocationChar,
 const.effectEmpathyCharismaBonusModAddCharismaLocationChar,
 const.effectInstantRecallMemoryBonusModAddMemoryLocationChar,
 const.effectIronWillWillpowerBonusModAddWillpowerLocationChar,
 const.effectSpatialAwarenessPerceptionBonusModAddPerceptionLocationChar}

def IsBoosterSkillAccelerator(dogmaStaticMgr, boosterRecord):
    boosterEffectIds = dogmaStaticMgr.GetPassiveFilteredEffectsByType(boosterRecord.boosterTypeID)
    for effect_id in SKILL_ACCELERATOR_EFFECT_IDS:
        if effect_id in boosterEffectIds:
            return True

    return False
