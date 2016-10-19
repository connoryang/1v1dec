#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\dogma\effects\modifiers.py


class BaseModifier(object):

    def __init__(self, operator, domain, modifiedAttributeID, modifyingAttributeID):
        self.operator = operator
        self.domain = domain
        self.modifiedAttributeID = modifiedAttributeID
        self.modifyingAttributeID = modifyingAttributeID
        self.isShipModifier = domain == 'shipID'
        self.isCharModifier = domain == 'charID'
        self.isStuctureModifier = domain == 'structureID'

    def _GetDomainID(self, env):
        if self.domain is None:
            return env.itemID
        return getattr(env, self.domain)

    def Start(self, env, dogmaLM, itemID, shipID, charID, otherID, targetID):
        self._GetStartFunc(dogmaLM)(*self._GetArgs(env, itemID))

    def Stop(self, env, dogmaLM, itemID, shipID, charID, otherID, targetID):
        self._GetStopFunc(dogmaLM)(*self._GetArgs(env, itemID))

    def IsShipModifier(self):
        return self.isShipModifier

    def IsCharModifier(self):
        return self.isCharModifier

    def IsStructureModifier(self):
        return self.isStuctureModifier


class ItemModifier(BaseModifier):

    def _GetArgs(self, env, itemID):
        return (self.operator,
         self._GetDomainID(env),
         self.modifiedAttributeID,
         itemID,
         self.modifyingAttributeID)

    def _GetStartFunc(self, dogmaLM):
        return dogmaLM.AddModifier

    def _GetStopFunc(self, dogmaLM):
        return dogmaLM.RemoveModifier


def _GetItemModifier(effectDict):
    return ItemModifier(effectDict['operator'], effectDict['domain'], effectDict['modifiedAttributeID'], effectDict['modifyingAttributeID'])


class LocationModifier(ItemModifier):

    def _GetStartFunc(self, dogmaLM):
        return dogmaLM.AddLocationModifier

    def _GetStopFunc(self, dogmaLM):
        return dogmaLM.RemoveLocationModifier


def _GetLocationModifier(effectDict):
    return LocationModifier(effectDict['operator'], effectDict['domain'], effectDict['modifiedAttributeID'], effectDict['modifyingAttributeID'])


class RequiredSkillModifier(BaseModifier):

    def __init__(self, operator, domain, modifiedAttributeID, modifyingAttributeID, skillTypeID):
        super(RequiredSkillModifier, self).__init__(operator, domain, modifiedAttributeID, modifyingAttributeID)
        self.skillTypeID = skillTypeID

    def _GetArgs(self, env, itemID):
        return (self.operator,
         self._GetDomainID(env),
         self.skillTypeID,
         self.modifiedAttributeID,
         itemID,
         self.modifyingAttributeID)


class LocationRequiredSkillModifier(RequiredSkillModifier):

    def _GetStartFunc(self, dogmaLM):
        return dogmaLM.AddLocationRequiredSkillModifier

    def _GetStopFunc(self, dogmaLM):
        return dogmaLM.RemoveLocationRequiredSkillModifier


def _GetLocationRequiredSkillModifier(effectDict):
    return LocationRequiredSkillModifier(effectDict['operator'], effectDict['domain'], effectDict['modifiedAttributeID'], effectDict['modifyingAttributeID'], effectDict['skillTypeID'])


class OwnerRequiredSkillModifier(RequiredSkillModifier):

    def _GetStartFunc(self, dogmaLM):
        return dogmaLM.AddOwnerRequiredSkillModifier

    def _GetStopFunc(self, dogmaLM):
        return dogmaLM.RemoveOwnerRequiredSkillModifier

    def IsShipModifier(self):
        return True

    def IsCharModifier(self):
        return True


def _GetOwnerRequiredSkillModifier(effectDict):
    return OwnerRequiredSkillModifier(effectDict['operator'], effectDict['domain'], effectDict['modifiedAttributeID'], effectDict['modifyingAttributeID'], effectDict['skillTypeID'])


class LocationGroupModifier(BaseModifier):

    def __init__(self, operator, domain, modifiedAttributeID, modifyingAttributeID, groupID):
        super(LocationGroupModifier, self).__init__(operator, domain, modifiedAttributeID, modifyingAttributeID)
        self.groupID = groupID

    def _GetArgs(self, env, itemID):
        return (self.operator,
         self._GetDomainID(env),
         self.groupID,
         self.modifiedAttributeID,
         itemID,
         self.modifyingAttributeID)

    def _GetStartFunc(self, dogmaLM):
        return dogmaLM.AddLocationGroupModifier

    def _GetStopFunc(self, dogmaLM):
        return dogmaLM.RemoveLocationGroupModifier


def _GetLocationGroupModifier(effectDict):
    return LocationGroupModifier(effectDict['operator'], effectDict['domain'], effectDict['modifiedAttributeID'], effectDict['modifyingAttributeID'], effectDict['groupID'])


class GangItemModifier(ItemModifier):

    def _GetArgs(self, env, itemID):
        return (self._GetDomainID(env),
         self.operator,
         self.modifiedAttributeID,
         itemID,
         self.modifyingAttributeID)

    def _GetStartFunc(self, dogmaLM):
        return dogmaLM.AddGangShipModifier

    def _GetStopFunc(self, dogmaLM):
        return dogmaLM.RemoveGangShipModifier


def _GetGangItemModifier(effectDict):
    return GangItemModifier(effectDict['operator'], 'shipID', effectDict['modifiedAttributeID'], effectDict['modifyingAttributeID'])


class GangRequiredSkillModifier(RequiredSkillModifier):

    def _GetArgs(self, env, itemID):
        return (self._GetDomainID(env),
         self.operator,
         self.skillTypeID,
         self.modifiedAttributeID,
         itemID,
         self.modifyingAttributeID)

    def _GetStartFunc(self, dogmaLM):
        return dogmaLM.AddGangRequiredSkillModifier

    def _GetStopFunc(self, dogmaLM):
        return dogmaLM.RemoveGangRequiredSkillModifier


def _GetGangRequiredSkillModifier(effectDict):
    return GangRequiredSkillModifier(effectDict['operator'], 'shipID', effectDict['modifiedAttributeID'], effectDict['modifyingAttributeID'], effectDict['skillTypeID'])


modifierGetterByType = {'ItemModifier': _GetItemModifier,
 'LocationRequiredSkillModifier': _GetLocationRequiredSkillModifier,
 'OwnerRequiredSkillModifier': _GetOwnerRequiredSkillModifier,
 'LocationModifier': _GetLocationModifier,
 'LocationGroupModifier': _GetLocationGroupModifier,
 'GangItemModifier': _GetGangItemModifier,
 'GangRequiredSkillModifier': _GetGangRequiredSkillModifier}

def GetModifierClassByTypeString(modifierType):
    return modifierGetterByType.get(modifierType)
