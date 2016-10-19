#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\common\lib\eveDustCommon\planetSurface.py
import appConst
import time
BLUE_SEC = 10000000L
EPOCH_BLUE_TIME = 116444736000000000L

def blue_os_GetTime(gmTime = None):
    if gmTime is None:
        gmTime = time.time()
    return EPOCH_BLUE_TIME + long(gmTime * BLUE_SEC)


ATTACK_TIMEOUT = 9000000000L

def HasAttackTimedOut(attackTimestamp, now = None):
    if now is None:
        now = blue_os_GetTime()
    return now > attackTimestamp


def GetConflictState(conflicts, corpID = None):
    conflictState = appConst.objectiveStateCeasefire
    for conflict in conflicts:
        if (corpID is None or corpID == conflict.attackerID) and not HasAttackTimedOut(conflict.expiryTime):
            if conflict.endTime is None:
                conflictState = appConst.objectiveStateWar

    return conflictState
