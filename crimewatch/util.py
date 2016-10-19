#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\crimewatch\util.py
import hashlib
import const
import collections
import math
from inventorycommon.const import categoryDrone, categoryFighter
import evetypes
try:
    from carbon.common.script.sys.basesession import FindSessions
except ImportError:
    FindSession = lambda x, y: None

def GetShipIDForCharID(charID):
    sessions = FindSessions('charid', [charID])
    if sessions:
        return sessions[0].shipid


def GetAggressorIdFromEffectData(effect_key, effect_info):
    category_id = evetypes.GetCategoryID(effect_info.moduleTypeID)
    source_owner_id = effect_info.sourceOwnerID
    aggressor_id = effect_key.shipID
    return GetAggressorId(category_id, source_owner_id, aggressor_id)


def GetAggressorId(category_id, source_owner_id, aggressor_id):
    if category_id in (categoryDrone, categoryFighter):
        ship_id = GetShipIDForCharID(source_owner_id)
        if ship_id:
            return ship_id
    return aggressor_id


def CalculateTagRequirementsForSecIncrease(startSecStatus, requestedSecStatus):
    if not const.characterSecurityStatusMin < requestedSecStatus <= const.characterSecurityStatusMax:
        raise RuntimeError('CalculateTagRequirementsForSecIncrease called with out-of-range requestedSecStatus', requestedSecStatus)
    if requestedSecStatus <= startSecStatus:
        raise RuntimeError('CalculateTagRequirementsForSecIncrease: requestedSecStatus must be higher than startSecStatus', requestedSecStatus, startSecStatus)
    requiredTags = collections.OrderedDict()
    secStatus = startSecStatus
    while secStatus < requestedSecStatus:
        for tagTypeID, (minSecStatus, maxSecStatus) in const.securityLevelsPerTagType.iteritems():
            if minSecStatus <= secStatus < maxSecStatus:
                numTagsRequired = int(math.ceil((min(requestedSecStatus, maxSecStatus) - secStatus) / const.securityGainPerTag))
                requiredTags[tagTypeID] = numTagsRequired
                secStatus += numTagsRequired * const.securityGainPerTag
                break
        else:
            raise RuntimeError('CalculateTagRequirementsForSecIncrease: No tags available for reaching requestedSecStatus', requestedSecStatus, secStatus, startSecStatus)

    return requiredTags


def IsItemFreeForAggression(targetGroupID):
    return targetGroupID in const.targetGroupsWithNoPenalties


def GetKillReportHashValue(kill):
    string = '%s%s%s%s' % (kill.victimCharacterID,
     kill.finalCharacterID,
     kill.victimShipTypeID,
     kill.killTime)
    return hashlib.sha1(string).hexdigest()
