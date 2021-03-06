#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\common\script\util\warUtil.py
import util
import blue
import log
from collections import namedtuple
from itertools import izip
BaseWar = namedtuple('War', ['warID',
 'declaredByID',
 'againstID',
 'timeDeclared',
 'timeFinished',
 'retracted',
 'timeStarted',
 'retractedBy',
 'billID',
 'mutual',
 'allies',
 'createdFromWarID',
 'openForAllies',
 'canBeRetracted'])

class War(BaseWar):
    __guid__ = 'warUtil.War'

    def Copy(self, **kwargs):
        values = []
        for fieldName, value in izip(self._fields, self):
            if fieldName in kwargs:
                values.append(kwargs[fieldName])
            elif isinstance(value, dict):
                values.append(value.copy())
            else:
                values.append(value)

        return War(*values)

    @classmethod
    def GetFields(cls):
        return cls._fields

    @property
    def noOfAllies(self):
        return len([ allyRow for allyRow in self.allies.itervalues() if util.IsAllyActive(allyRow) ])


def WarCreatorIterator(row):
    for attributeName in War.GetFields():
        try:
            yield getattr(row, attributeName)
        except AttributeError:
            if attributeName == 'allies':
                yield {}
            else:
                log.LogException('WarCreateorIterator found attribute (%s) that was not in war row' % attributeName)
                yield


def CreateWarFromRow(row, change = None):
    if change is None:
        return War(*[ value for value in WarCreatorIterator(row) ])
    else:
        values = []
        for attributeName, value in zip(row.GetFields(), row):
            if attributeName in change:
                value = change[attributeName][1]
            values.append(value)

        ret = War(*values)
        return ret


def GetAddRemoveFromChange(change):
    bAdd = 1
    bRemove = 1
    for old, new in change.itervalues():
        if old is None and new is None:
            continue
        if old is not None:
            bAdd = 0
        if new is not None:
            bRemove = 0

    if bAdd and bRemove:
        raise RuntimeError('GetAddRemoveFromChange WTF')
    return (bAdd, bRemove)


def HandleWarChange(war, warsByWarID, warsByOwnerID, ownerIDs, change):
    bAdd, bRemove = GetAddRemoveFromChange(change)
    if 'warID' not in change and bAdd:
        bAdd = 0
    if bRemove:
        try:
            del warsByWarID[change['warID'][0]]
        except KeyError:
            pass

    else:
        newWar = CreateWarFromRow(war)
        warsByWarID[newWar.warID] = newWar
        for ownerID in ownerIDs:
            try:
                warsByOwnerID[ownerID].add(newWar.warID)
            except KeyError:
                pass


def ProcessAllyJoinNotifications(ownerIDs, war, change, notificationCall):
    oldAllies, newAllies = change['allies']
    alliesAdded = set(newAllies.keys()).difference(oldAllies.keys())
    for ownerID in ownerIDs:
        if len(alliesAdded) == 0:
            continue
        corpRoleMask = 0
        if ownerID == war.againstID:
            notificationType = const.notificationTypeAllyJoinedWarDefenderMsg
            data = {'aggressorID': war.declaredByID}
            corpRoleMask = const.corpRoleDirector
        elif ownerID == war.declaredByID:
            notificationType = const.notificationTypeAllyJoinedWarAggressorMsg
            data = {'defenderID': war.againstID}
        elif ownerID in newAllies:
            notificationType = const.notificationTypeAllyJoinedWarAllyMsg
            data = {'defenderID': war.againstID,
             'aggressorID': war.declaredByID}
        else:
            continue
        for allyID in alliesAdded:
            data.update({'allyID': allyID,
             'startTime': newAllies[allyID].timeStarted})
            notificationCall(notificationType, ownerID, corpRoleMask=corpRoleMask, senderID=const.ownerCONCORD, data=data)


def GetAllyCostToConcord(war, baseCostFunc):
    currentTime = blue.os.GetWallclockTime()
    activeAllies = len([ ally for ally in war.allies.itervalues() if currentTime < ally.timeFinished ])
    if activeAllies == 0:
        return 0
    else:
        return baseCostFunc() * 2 ** min(activeAllies - 1, 20)


exports = {'warUtil.War': War,
 'warUtil.CreateWarFromRow': CreateWarFromRow,
 'warUtil.GetAddRemoveFromChange': GetAddRemoveFromChange,
 'warUtil.HandleWarChange': HandleWarChange,
 'warUtil.ProcessAllyJoinNotifications': ProcessAllyJoinNotifications,
 'warUtil.GetAllyCostToConcord': GetAllyCostToConcord}
