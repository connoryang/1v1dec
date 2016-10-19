#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\common\script\dogma\baseDogmaStaticSvc.py
import evetypes
import service
import bluepy
import telemetry
import sys
from eve.common.script.sys.rowset import IndexedRowLists, IndexedRows

class BaseDogmaStaticSvc(service.Service):
    __guid__ = 'svc.baseDogmaStaticSvc'
    __notifyevents__ = ['OnCfgRevisionChange']

    def __init__(self):
        service.Service.__init__(self)
        self.attributes = {}
        self.attributesByName = {}
        self.attributesByTypeAttribute = {}
        self.effects = {}
        self.requiredSkills = {}
        self.unwantedEffects = {const.effectHiPower: True,
         const.effectLoPower: True,
         const.effectMedPower: True,
         const.effectSkillEffect: True}

    def Run(self, *args):
        self.Load()

    def OnCfgRevisionChange(self, uniqueRefName, cfgEntryName, cacheID, keyIDs, keyCols, oldRow, newRow):
        keyID, keyID2, keyID3 = keyIDs
        if cacheID == const.cacheDogmaAttributes:
            self.LoadAttributes()
        elif cacheID == const.cacheDogmaEffects:
            self.LoadEffects()
        elif cacheID == const.cacheDogmaTypeAttributes:
            self.LoadTypeAttributes(keyID, keyID2, newRow)
        elif cacheID == const.cacheDogmaTypeEffects:
            self.LoadTypeEffects(keyID, keyID2, newRow)

    def RefreshTwoKeyIndexedRows(self, ir, keyID, keyID2, newRow):
        if keyID in ir:
            ir2 = ir[keyID]
            if keyID2 in ir2:
                del ir2[keyID2]
        if newRow:
            if keyID in ir:
                ir2 = ir[keyID]
            else:
                ir2 = IndexedRows()
                ir[keyID] = ir2
            ir2[keyID2] = newRow

    def Load(self):
        with bluepy.Timer('LoadAttributes'):
            self.LoadAttributes()
        with bluepy.Timer('LoadTypeAttributes'):
            self.LoadTypeAttributes()
        with bluepy.Timer('LoadEffects'):
            self.LoadEffects()
        with bluepy.Timer('LoadTypeEffects'):
            self.LoadTypeEffects(run=True)
        self.crystalGroupIDs = cfg.GetCrystalGroups()
        self.controlBunkersByFactionID = {}
        for typeID in evetypes.GetTypeIDsByGroup(const.groupControlBunker):
            factionID = int(self.GetTypeAttribute2(typeID, const.attributeFactionID))
            self.controlBunkersByFactionID[factionID] = typeID

        import re
        cgre = re.compile('chargeGroup\\d{1,2}')
        cgattrs = tuple([ a.attributeID for a in cfg.dgmattribs if cgre.match(a.attributeName) is not None ])
        self.chargeGroupAttributes = cgattrs
        self.crystalModuleGroupIDs = {}
        for categoryID in (const.categoryModule, const.categoryStructureModule, const.categoryStarbase):
            for groupID in evetypes.GetGroupIDsByCategory(categoryID):
                typeIDs = evetypes.GetTypeIDsByGroup(groupID)
                if len(typeIDs) > 0:
                    typeID = typeIDs.pop()
                    for attributeID in cgattrs:
                        v = self.GetTypeAttribute(typeID, attributeID)
                        if v is not None and v in self.crystalGroupIDs:
                            self.crystalModuleGroupIDs[groupID] = True
                            break

    def LoadAttributes(self):
        self.attributes = IndexedRows(cfg.dgmattribs.data.itervalues(), ('attributeID',))
        if len(self.attributes) == 0:
            self.LogError('STATIC DATA MISSING: Dogma Attributes')
        self.attributesByName = IndexedRows(cfg.dgmattribs.data.itervalues(), ('attributeName',))
        self.attributesByCategory = IndexedRowLists(cfg.dgmattribs.data.itervalues(), ('attributeCategory',))
        chargedAttributes = []
        for att in self.attributes.itervalues():
            if att.chargeRechargeTimeID and att.attributeCategory != 8:
                chargedAttributes.append(att)

        self.chargedAttributes = IndexedRows(chargedAttributes, ('attributeID',))
        self.attributesRechargedByAttribute = IndexedRowLists(chargedAttributes, ('chargeRechargeTimeID',))
        self.attributesCappedByAttribute = IndexedRowLists(chargedAttributes, ('maxAttributeID',))
        self.attributesByIdx = {}
        self.idxByAttribute = {}
        self.canFitShipGroupAttributes = []
        self.allowedDroneGroupAttributes = []
        self.chargeGroupAttributes = []
        for att in self.attributesByCategory[const.dgmAttrCatGroup]:
            if att.attributeName.startswith('canFitShipGroup'):
                self.canFitShipGroupAttributes.append(att.attributeID)
            elif att.attributeName.startswith('allowedDroneGroup'):
                self.allowedDroneGroupAttributes.append(att.attributeID)
            elif att.attributeName.startswith('chargeGroup'):
                self.chargeGroupAttributes.append(att.attributeID)

        self.canFitShipTypeAttributes = []
        self.requiresSovUpgrade = []
        self.requiredSkillAttributes = {}
        for att in self.attributesByCategory[const.dgmAttrCatType]:
            if att.attributeName.startswith('canFitShipType'):
                self.canFitShipTypeAttributes.append(att.attributeID)
            elif att.attributeName.startswith('anchoringRequiresSovUpgrade'):
                self.requiresSovUpgrade.append(att.attributeID)
            elif att.attributeName.startswith('requiredSkill'):
                levelAttribute = self.attributesByName[att.attributeName + 'Level']
                self.requiredSkillAttributes[att.attributeID] = levelAttribute.attributeID

        self.shipHardwareModifierAttribs = [(const.attributeHiSlots, const.attributeHiSlotModifier),
         (const.attributeMedSlots, const.attributeMedSlotModifier),
         (const.attributeLowSlots, const.attributeLowSlotModifier),
         (const.attributeTurretSlotsLeft, const.attributeTurretHardpointModifier),
         (const.attributeLauncherSlotsLeft, const.attributeLauncherHardPointModifier)]
        self.resistanceAttributesByLayer = {}
        for attributeID, layerName, hpAttributeID, uniformityAttributeID in ((const.attributeShieldCharge,
          'Shield',
          const.attributeShieldCapacity,
          const.attributeShieldUniformity), (const.attributeArmorDamage,
          'Armor',
          const.attributeArmorHP,
          const.attributeArmorUniformity), (const.attributeDamage,
          '',
          const.attributeHp,
          const.attributeStructureUniformity)):
            self.resistanceAttributesByLayer[attributeID] = [ getattr(const, 'attribute%s%s' % (layerName, resName)) for resName in ('EmDamageResonance', 'ExplosiveDamageResonance', 'KineticDamageResonance', 'ThermalDamageResonance') ]

        self.damageAttributes = (const.attributeEmDamage,
         const.attributeExplosiveDamage,
         const.attributeKineticDamage,
         const.attributeThermalDamage)
        self.damageStateAttributes = (const.attributeDamage, const.attributeArmorDamage, const.attributeShieldCharge)
        self.layerResAttributesByDamage = {}
        for layerAttributeID, resAttribs in self.resistanceAttributesByLayer.iteritems():
            self.layerResAttributesByDamage[layerAttributeID] = zip(self.damageAttributes, resAttribs)

    def LoadEffects(self):
        self.effects = IndexedRows(cfg.dgmeffects.data.itervalues(), ('effectID',))
        if len(self.effects) == 0:
            self.LogError('STATIC DATA MISSING: Dogma Effects')
        self.effectsByName = IndexedRows(cfg.dgmeffects.data.itervalues(), ('effectName',))

    def LoadTypeEffects(self, typeID = None, effectID = None, newRow = None, run = False):
        if typeID is None:
            rs = []
            for typeValues in cfg.dgmtypeeffects.values():
                rs.extend(typeValues)

            if len(rs) == 0:
                self.LogError('STATIC DATA MISSING: Dogma Type Effects')
            self.effectsByType = IndexedRows(rs, ('typeID', 'effectID'))
            self.typesByEffect = IndexedRows(rs, ('effectID', 'typeID'))
        else:
            self.RefreshTwoKeyIndexedRows(self.effectsByType, typeID, effectID, newRow)
            self.RefreshTwoKeyIndexedRows(self.typesByEffect, effectID, typeID, newRow)
        self.passiveFilteredEffectsByType = {}
        for typeID in self.effectsByType.iterkeys():
            passiveEffects = []
            for effectID in self.effectsByType[typeID].iterkeys():
                if self.unwantedEffects.has_key(effectID):
                    continue
                effect = self.effects[effectID]
                if effect.effectCategory in [const.dgmEffPassive, const.dgmEffSystem]:
                    passiveEffects.append(effectID)

            if len(passiveEffects):
                self.passiveFilteredEffectsByType[typeID] = passiveEffects

        defaultEffect = {}
        for typeID2 in cfg.dgmtypeeffects:
            for r in cfg.dgmtypeeffects[typeID2]:
                if r.isDefault == 1:
                    defaultEffect[typeID2] = r.effectID

        self.defaultEffectByType = defaultEffect

    def LoadAllTypeAttributes(self):
        raise NotImplementedError('LoadAllTypeAttributes - not implemented')

    def LoadSpecificTypeAttributes(self, typeID, attributeID, newRow):
        raise NotImplementedError('LoadSpecificTypeAttributes - not implemented')

    def LoadTypeAttributes(self, typeID = None, attributeID = None, newRow = None):
        if typeID is None:
            self.LoadAllTypeAttributes()
        else:
            self.LoadSpecificTypeAttributes(typeID, attributeID, newRow)

    def GetTypeAttribute(self, typeID, attributeID, defaultValue = None):
        try:
            return self.attributesByTypeAttribute[typeID][attributeID]
        except KeyError:
            return defaultValue

    def GetTypeAttribute2(self, typeID, attributeID):
        try:
            return self.attributesByTypeAttribute[typeID][attributeID]
        except KeyError:
            return self.attributes[attributeID].defaultValue

    @telemetry.ZONE_METHOD
    def GetRequiredSkills(self, typeID):
        if typeID in self.requiredSkills:
            return self.requiredSkills[typeID]
        ret = {}
        for attributeID, levelAttributeID in self.requiredSkillAttributes.iteritems():
            requiredSkill = self.GetTypeAttribute(typeID, attributeID)
            requiredLevel = self.GetTypeAttribute2(typeID, levelAttributeID)
            if requiredSkill is not None and requiredSkill not in ret:
                ret[int(requiredSkill)] = int(requiredLevel)

        self.requiredSkills[typeID] = ret
        return ret

    def GetEffect(self, effectID):
        return self.effects[effectID]

    def GetEffectTypes(self):
        return self.effects

    def GetEffectType(self, effectID):
        return self.effects[effectID]

    def GetAttributeType(self, attributeID):
        if isinstance(attributeID, str):
            return self.attributesByName[attributeID]
        return self.attributes[attributeID]

    def GetAttributeByName(self, attributeName):
        ret = self.attributesByName[attributeName]
        return ret.attributeID

    def TypeHasAttribute(self, typeID, attributeID):
        return typeID in self.attributesByTypeAttribute and attributeID in self.attributesByTypeAttribute[typeID]

    def TypeGetOrderedEffectIDs(self, typeID, categoryID = None):
        return self.effectsByType[typeID].iterkeys()

    def TypeGetEffects(self, typeID):
        return self.effectsByType.get(typeID, {})

    def TypeExists(self, typeID):
        return typeID in self.attributesByTypeAttribute

    def TypeHasEffect(self, typeID, effectID):
        return self.effectsByType.has_key(typeID) and self.effectsByType[typeID].has_key(effectID)

    def GetAttributesByCategory(self, categoryID):
        return self.attributesByCategory.get(categoryID, [])

    def EffectGetTypes(self, effectID):
        return self.typesByEffect.get(effectID, {})

    def AttributeGetTypes(self, attributeID):
        return self.typesByAttribute.get(attributeID, {})

    def GetCanFitShipGroups(self, typeID):
        rtn = []
        for att in self.canFitShipGroupAttributes:
            try:
                rtn.append(self.attributesByTypeAttribute[typeID][att])
            except KeyError:
                sys.exc_clear()

        return rtn

    def GetChargeGroupAttributes(self):
        return self.chargeGroupAttributes

    def GetCanFitShipTypes(self, typeID):
        rtn = []
        for att in self.canFitShipTypeAttributes:
            try:
                rtn.append(self.attributesByTypeAttribute[typeID][att])
            except KeyError:
                sys.exc_clear()

        return rtn

    def CanFitModuleToShipTypeOrGroup(self, moduleTypeID, shipTypeID, shipGroupID):
        canFitShipGroups = self.GetCanFitShipGroups(moduleTypeID)
        canFitShipTypes = self.GetCanFitShipTypes(moduleTypeID)
        if not canFitShipGroups and not canFitShipTypes:
            return True
        if canFitShipGroups and shipGroupID in canFitShipGroups:
            return True
        if canFitShipTypes and shipTypeID in canFitShipTypes:
            return True
        return False

    def GetAllowedDroneGroups(self, typeID):
        groups = []
        attributes = self.attributesByTypeAttribute.get(typeID)
        if attributes:
            for attributeID in self.allowedDroneGroupAttributes:
                value = attributes.get(attributeID)
                if value:
                    groups.append(int(value))

        return groups

    def GetDefaultEffect(self, typeID):
        return self.defaultEffectByType[typeID]

    def GetShipHardwareModifierAttribs(self):
        return self.shipHardwareModifierAttribs

    def GetValidChargeGroupsForType(self, typeID):
        ret = set()
        for attributeID in self.chargeGroupAttributes:
            try:
                ret.add(int(self.GetTypeAttribute(typeID, attributeID)))
            except TypeError:
                pass

        return ret

    def GetSkillModifiedAttributePercentageValue(self, attributeID, modifyingAttributeID, skillTypeID, skillRecord = None):
        percentageMod = 1.0
        skillLevel = 0
        if skillRecord:
            skillLevel = skillRecord.skillLevel
            try:
                percentageMod = (100 + self.GetTypeAttribute(skillTypeID, modifyingAttributeID, None) * skillLevel) / 100.0
            except TypeError as e:
                self.LogError('dogmaStaticMgr::GetSkillModifiedAttributePercentageValue.Failed calculating modification! %s' % e)
                percentageMod = 1.0

            if not 0.0 <= percentageMod <= 1.0:
                self.LogError('dogmaStaticMgr::GetSkillModifiedAttributePercentageValue.Value %s not a percentile!' % percentageMod)
                percentageMod = 1.0
        return percentageMod

    def GetPassiveFilteredEffectsByType(self, typeID):
        return self.passiveFilteredEffectsByType.get(typeID, [])
