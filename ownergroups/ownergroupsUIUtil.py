#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\ownergroups\ownergroupsUIUtil.py
from collections import defaultdict, OrderedDict
from carbon.common.script.util.linkUtil import GetShowInfoLink
from carbonui.util.sortUtil import SortListOfTuples
from ownergroups.ownergroupConst import MEMBERSHIP_TYPE_MEMBER, MEMBERSHIP_TYPE_MANAGER, MEMBERSHIP_TYPE_ADMIN, MEMBERSHIP_TYPE_EXCLUDED
membershipTypeTexturePathDict = {MEMBERSHIP_TYPE_MEMBER: 'res:/UI/Texture/classes/AccessGroups/temp_member.png',
 MEMBERSHIP_TYPE_MANAGER: 'res:/UI/Texture/classes/AccessGroups/manager.png',
 MEMBERSHIP_TYPE_ADMIN: 'res:/UI/Texture/classes/AccessGroups/admin.png',
 MEMBERSHIP_TYPE_EXCLUDED: 'res:/UI/Texture/classes/AccessGroups/blocked.png'}
membershipTypeLabelPath = {MEMBERSHIP_TYPE_MEMBER: 'UI/Structures/AccessGroups/Member',
 MEMBERSHIP_TYPE_MANAGER: 'UI/Structures/AccessGroups/Manager',
 MEMBERSHIP_TYPE_ADMIN: 'UI/Structures/AccessGroups/Admin',
 MEMBERSHIP_TYPE_EXCLUDED: 'UI/Structures/AccessGroups/Blocked'}
ACCESS_SORT_ORDER = [MEMBERSHIP_TYPE_ADMIN,
 MEMBERSHIP_TYPE_MANAGER,
 MEMBERSHIP_TYPE_MEMBER,
 MEMBERSHIP_TYPE_EXCLUDED]
MENU_LABEL_PATH_DICT = {(MEMBERSHIP_TYPE_MANAGER, True): 'UI/Structures/AccessGroups/RemoveManagerMembershipType',
 (MEMBERSHIP_TYPE_MANAGER, False): 'UI/Structures/AccessGroups/MakeManager',
 (MEMBERSHIP_TYPE_ADMIN, True): 'UI/Structures/AccessGroups/RemoveAdminMembershipType',
 (MEMBERSHIP_TYPE_ADMIN, False): 'UI/Structures/AccessGroups/MakeAdmin',
 (MEMBERSHIP_TYPE_EXCLUDED, True): 'UI/Structures/AccessGroups/UnblockMember',
 (MEMBERSHIP_TYPE_EXCLUDED, False): 'UI/Structures/AccessGroups/BlockMember'}

def GetMembershipTypeTextureAndLabelPaths(membershipType):
    texturePath = membershipTypeTexturePathDict.get(membershipType)
    labelPath = membershipTypeLabelPath.get(membershipType)
    return (texturePath, labelPath)


SET_AS_LABEL_PATH_DICT = {MEMBERSHIP_TYPE_ADMIN: 'UI/Structures/AccessGroups/SetAsAdmin',
 MEMBERSHIP_TYPE_MANAGER: 'UI/Structures/AccessGroups/SetAsManager',
 MEMBERSHIP_TYPE_MEMBER: 'UI/Structures/AccessGroups/SetAsMember',
 MEMBERSHIP_TYPE_EXCLUDED: 'UI/Structures/AccessGroups/SetAsBlocked'}

def GetSetAsMembershipLabelPaths(membershipType):
    labelPath = SET_AS_LABEL_PATH_DICT.get(membershipType)
    return labelPath


def GetChangeRestrictions(membershipType):
    if membershipType == MEMBERSHIP_TYPE_ADMIN:
        return []
    if membershipType == MEMBERSHIP_TYPE_MANAGER:
        return [MEMBERSHIP_TYPE_ADMIN, MEMBERSHIP_TYPE_MANAGER]
    return ACCESS_SORT_ORDER


def GetMembershipSortIdx(membership):
    return ACCESS_SORT_ORDER.index(membership)


errorDict = OrderedDict([('IsTheLastAdmin', 'UI/Structures/AccessGroups/Errors/IsTheLastAdmin'),
 ('MemberHasYouBlocked', 'UI/Structures/AccessGroups/Errors/MemberHasYouBlocked'),
 ('IllegalMemberID', 'UI/Structures/AccessGroups/Errors/IllegalMemberID'),
 ('ManagersCanNotAddAdminsOrManagers', 'UI/Structures/AccessGroups/Errors/ManagersCanNotAddAdminsOrManagers'),
 ('AdminsAndManagersMustBeCharacters', 'UI/Structures/AccessGroups/Errors/AdminsAndManagersMustBeCharacters'),
 ('NotAllowedToUpdateAdminOrManager', 'UI/Structures/AccessGroups/Errors/NotAllowedToUpdateAdminOrManager'),
 ('NotAllowedToPromoteToAdmin', 'UI/Structures/AccessGroups/Errors/NotAllowedToPromoteToAdmin')])

def GetWarningInfo(failedInfo):
    warningInfo = defaultdict(set)
    for memberID, error in failedInfo:
        warningInfo[error].add(memberID)

    return warningInfo


def GetTextForWarning(failedInfo):
    warningInfo = GetWarningInfo(failedInfo)
    textList = []
    for errorKey, memberIDs in warningInfo.iteritems():
        groupWarning = GetWarningForOneGroup(errorKey, memberIDs)
        if groupWarning:
            textList.append(groupWarning)

    textList = SortListOfTuples(textList)
    return textList


def GetWarningForOneGroup(errorKey, memberIDs):
    errorLabel = errorDict.get(errorKey, None)
    if errorLabel is None:
        return
    sortNumber = errorDict.keys().index(errorKey)
    memberList = []
    for eachMemberID in memberIDs:
        try:
            if eachMemberID is None:
                continue
            ownerInfo = cfg.eveowners.Get(eachMemberID)
            charName = ownerInfo.name
            text = GetShowInfoLink(ownerInfo.typeID, charName, itemID=eachMemberID)
            memberList.append((charName.lower(), text))
        except KeyError as e:
            pass

    if not memberList:
        return
    memberList = SortListOfTuples(memberList)
    memberText = '<br>'.join(memberList)
    return (sortNumber, (errorLabel, {'memberList': memberText}))


MADE_ADMIN = 'res:/UI/Texture/classes/AccessGroups/madeAdmin.png'
MADE_MANAGER = 'res:/UI/Texture/classes/AccessGroups/madeManager.png'
MADE_MEMBER = 'res:/UI/Texture/classes/AccessGroups/madeMember.png'
BLOCK_MEMBER = 'res:/UI/Texture/classes/AccessGroups/memberBlocked.png'
REMOVE_MEMBER = 'res:/UI/Texture/classes/AccessGroups/memberRemoved.png'
TEXTS_AND_ICONS_FOR_MEMBERC_CHANGES = {(None, MEMBERSHIP_TYPE_EXCLUDED): ('UI/Structures/LoggedChanges/AddBlockedMember', BLOCK_MEMBER),
 (None, MEMBERSHIP_TYPE_MEMBER): ('UI/Structures/LoggedChanges/AddMember', MADE_MEMBER),
 (None, MEMBERSHIP_TYPE_MANAGER): ('UI/Structures/LoggedChanges/AddManager', MADE_MANAGER),
 (None, MEMBERSHIP_TYPE_ADMIN): ('UI/Structures/LoggedChanges/AddAdmin', MADE_ADMIN),
 (MEMBERSHIP_TYPE_EXCLUDED, MEMBERSHIP_TYPE_MEMBER): ('UI/Structures/LoggedChanges/ChangeToMemberFromBlocked', MADE_MEMBER),
 (MEMBERSHIP_TYPE_EXCLUDED, MEMBERSHIP_TYPE_MANAGER): ('UI/Structures/LoggedChanges/ChangeToManagerFromBlocked', MADE_MANAGER),
 (MEMBERSHIP_TYPE_EXCLUDED, MEMBERSHIP_TYPE_ADMIN): ('UI/Structures/LoggedChanges/ChangeToAdminFromBlocked', MADE_ADMIN),
 (MEMBERSHIP_TYPE_EXCLUDED, None): ('UI/Structures/LoggedChanges/RemoveBlockedFromGroup', REMOVE_MEMBER),
 (MEMBERSHIP_TYPE_MEMBER, MEMBERSHIP_TYPE_EXCLUDED): ('UI/Structures/LoggedChanges/ChangeToBlockedFromMember', BLOCK_MEMBER),
 (MEMBERSHIP_TYPE_MEMBER, MEMBERSHIP_TYPE_MANAGER): ('UI/Structures/LoggedChanges/ChangeToManagerFromMember', MADE_MANAGER),
 (MEMBERSHIP_TYPE_MEMBER, MEMBERSHIP_TYPE_ADMIN): ('UI/Structures/LoggedChanges/ChangeToAdminFromMember', MADE_ADMIN),
 (MEMBERSHIP_TYPE_MEMBER, None): ('UI/Structures/LoggedChanges/RemoveMemberFromGroup', REMOVE_MEMBER),
 (MEMBERSHIP_TYPE_MANAGER, MEMBERSHIP_TYPE_EXCLUDED): ('UI/Structures/LoggedChanges/CangeToBlockedFromManager', BLOCK_MEMBER),
 (MEMBERSHIP_TYPE_MANAGER, MEMBERSHIP_TYPE_MEMBER): ('UI/Structures/LoggedChanges/ChangeToMemberFromManager', MADE_MEMBER),
 (MEMBERSHIP_TYPE_MANAGER, MEMBERSHIP_TYPE_ADMIN): ('UI/Structures/LoggedChanges/ChangeToAdminFromManager', MADE_ADMIN),
 (MEMBERSHIP_TYPE_MANAGER, None): ('UI/Structures/LoggedChanges/RemoveManagerFromGroup', REMOVE_MEMBER),
 (MEMBERSHIP_TYPE_ADMIN, MEMBERSHIP_TYPE_EXCLUDED): ('UI/Structures/LoggedChanges/ChangeToBlockedFromAdmin', BLOCK_MEMBER),
 (MEMBERSHIP_TYPE_ADMIN, MEMBERSHIP_TYPE_MEMBER): ('UI/Structures/LoggedChanges/ChangeToMemberFromAdmin', MADE_MEMBER),
 (MEMBERSHIP_TYPE_ADMIN, MEMBERSHIP_TYPE_MANAGER): ('UI/Structures/LoggedChanges/ChangeToManagerFromAdmin', MADE_MANAGER),
 (MEMBERSHIP_TYPE_ADMIN, None): ('UI/Structures/LoggedChanges/RemoveAdminFromGroup', REMOVE_MEMBER)}
