#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\common\script\util\fleetcommon.py
import evefleet.const as fleetConst
from infoEventConst import infoEventFleetBroadcast

def IsSuperior(member, myself):
    if member.charID == myself.charID:
        return True
    if myself.role == fleetConst.fleetRoleLeader:
        return False
    if member.role == fleetConst.fleetRoleLeader:
        return True
    if myself.squadID > 0:
        if member.role != fleetConst.fleetRoleMember and member.wingID == myself.wingID:
            return True
    return False


def IsSubordinateOrEqual(member, myself):
    if member.charID == myself.charID:
        return True
    if myself.role == fleetConst.fleetRoleLeader:
        return True
    if myself.squadID > 0:
        if member.squadID == myself.squadID:
            return True
    if myself.role == fleetConst.fleetRoleWingCmdr:
        if member.wingID == myself.wingID:
            return True
    return False


def ShouldSendBroadcastTo(member, myself, scope):
    if scope == fleetConst.BROADCAST_ALL:
        return True
    if scope == fleetConst.BROADCAST_UP and IsSuperior(member, myself):
        return True
    if scope == fleetConst.BROADCAST_DOWN and IsSubordinateOrEqual(member, myself):
        return True
    return False


def LogBroadcast(messageName, scope, itemID):
    for idx in range(len(fleetConst.ALL_BROADCASTS)):
        if fleetConst.ALL_BROADCASTS[idx] == messageName:
            break

    sm.GetService('infoGatheringMgr').LogInfoEventFromServer(infoEventFleetBroadcast, idx, int_1=1, int_2=scope)
    sm.GetService('fleetObjectHandler').LogPlayerEvent('Broadcast', messageName, scope, itemID)
    sm.GetService('fleetObjectHandler').LogPlayerEventJson('Broadcast', broadcastName=messageName, scope=scope, targetID=itemID)


def IsOpenToCorp(fleet):
    return fleet.get('inviteScope', 0) & fleetConst.INVITE_CORP == fleetConst.INVITE_CORP


def IsOpenToAlliance(fleet):
    return fleet.get('inviteScope', 0) & fleetConst.INVITE_ALLIANCE == fleetConst.INVITE_ALLIANCE


def IsOpenToMilitia(fleet):
    return fleet.get('inviteScope', 0) & fleetConst.INVITE_MILITIA == fleetConst.INVITE_MILITIA


def IsOpenToPublic(fleet):
    return fleet.get('inviteScope', 0) & fleetConst.INVITE_PUBLIC == fleetConst.INVITE_PUBLIC
