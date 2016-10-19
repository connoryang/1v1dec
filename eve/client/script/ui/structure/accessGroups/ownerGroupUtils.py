#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\structure\accessGroups\ownerGroupUtils.py
from brennivin.itertoolsext import Bundle
from eve.client.script.ui.control.allUserEntries import AllUserEntries
from eve.client.script.ui.util.linkUtil import GetItemIDFromTextLink
from ownergroups.ownergroupConst import MEMBERSHIP_TYPE_MEMBER, PUBLIC_MEMBER_ID

def GetOwnerIDsAndMembershipTypeFromNodes(nodes, useNodeMembershipType = False, membershipType = MEMBERSHIP_TYPE_MEMBER):
    if not nodes:
        return
    firstNode = nodes[0]
    guid = firstNode.__guid__
    if guid not in AllUserEntries():
        nodes = GetTextLinkNode(firstNode)
        if nodes is None:
            return
    membershipTypesByMemberID = {}
    for eachNode in nodes:
        if useNodeMembershipType:
            membershipType = eachNode.get('membershipType', membershipType)
        else:
            membershipType = membershipType
        membershipTypesByMemberID[eachNode.itemID] = membershipType

    return membershipTypesByMemberID


def GetTextLinkNode(node):
    validTypeIDs = const.characterTypeByBloodline.values() + [const.typeCorporation, const.typeAlliance]
    memberID = GetItemIDFromTextLink(node, validTypeIDs)
    if memberID is None:
        return
    return [Bundle(itemID=memberID)]


def GetMemberIDsToUpdate(memberIDs, failedInfo):
    failedIDs = {x[0] for x in failedInfo}
    membersToUpdate = {x for x in memberIDs if x not in failedIDs}
    return membersToUpdate


def GetOwnerTypeSortValue(typeID):
    if typeID == const.typeCorporation:
        return 2
    if typeID == const.typeAlliance:
        return 1
    if typeID == PUBLIC_MEMBER_ID:
        return 0
    return 3


def ConvertDBRowToBundle(dbRow):
    ret = Bundle()
    for eachColName in dbRow.__columns__:
        value = getattr(dbRow, eachColName)
        ret[eachColName] = value

    return ret


def GetMembershipTypeByMemberID(members):
    membershipTypeByMemberID = {x.memberID:x.membershipType for x in members}
    return membershipTypeByMemberID
