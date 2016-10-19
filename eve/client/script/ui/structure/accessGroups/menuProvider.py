#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\structure\accessGroups\menuProvider.py
from collections import defaultdict
from carbon.common.script.sys.serviceConst import ROLEMASK_ELEVATEDPLAYER
from carbonui.control.menuLabel import MenuLabel
from carbonui.util.sortUtil import SortListOfTuples
from eve.client.script.ui.structure.accessGroups.nameAndDescriptionWnd import AccessGroupsEditGroup
from localization import GetByLabel
from ownergroups.ownergroupConst import MEMBERSHIP_TYPE_MANAGER, MEMBERSHIP_TYPE_ADMIN, MEMBERSHIP_TYPE_EXCLUDED, MEMBERSHIP_TYPE_MEMBER, PUBLIC_MEMBER_ID
from ownergroups.ownergroupsUIUtil import MENU_LABEL_PATH_DICT, ACCESS_SORT_ORDER
import blue

class MenuProvider(object):

    def GetMenuForMember(self, groupID, nodes, myMemberShipType, parentController, corpOwnedGroup):
        characterListDict = defaultdict(list)
        nodesByMemberID = {}
        for eachNode in nodes:
            memberID = eachNode.memberID
            nodesByMemberID[memberID] = eachNode
            for eachMembershipType in [MEMBERSHIP_TYPE_MANAGER, MEMBERSHIP_TYPE_ADMIN, MEMBERSHIP_TYPE_EXCLUDED]:
                if not self._CanModifyOther(myMemberShipType, eachMembershipType):
                    continue
                if eachNode.membershipType == eachMembershipType:
                    memberShipKey = (eachMembershipType, True)
                else:
                    memberShipKey = (eachMembershipType, False)
                characterListDict[memberShipKey].append(memberID)

        m = []
        for eachMembershipType, memberIDs in characterListDict.iteritems():
            membershipType, haveLevel = eachMembershipType
            charIDs = self._GetFilteredCharIDsBasedOnMembership(myMemberShipType, nodesByMemberID, doTypeCheck=True)
            label = GetByLabel(MENU_LABEL_PATH_DICT.get(eachMembershipType))
            if not charIDs:
                continue
            if len(charIDs) > 1:
                label += ' (%s)' % len(charIDs)
            sortValue = ACCESS_SORT_ORDER.index(membershipType)
            if haveLevel:
                newMembershipType = MEMBERSHIP_TYPE_MEMBER
            else:
                newMembershipType = membershipType
            m.append(((sortValue, label.lower()), (label, parentController.UpdateMembershipTypes, (groupID, charIDs, newMembershipType))))

        m = SortListOfTuples(m)
        removeText = GetByLabel('UI/Structures/AccessGroups/RemoveMember')
        removableMemberIDs = self._GetFilteredCharIDsBasedOnMembership(myMemberShipType, nodesByMemberID)
        if session.charid in nodesByMemberID:
            removableMemberIDs.add(session.charid)
        if not corpOwnedGroup and removableMemberIDs:
            if len(removableMemberIDs) > 1:
                removeText += ' (%s)' % len(removableMemberIDs)
            m += [(removeText, parentController.RemoveMembers, (groupID, removableMemberIDs))]
        memberMenuOptions = self._GetGenericMemberMenuOptions(nodesByMemberID)
        if memberMenuOptions:
            m += [None] + memberMenuOptions
        return m

    def _GetFilteredCharIDsBasedOnMembership(self, ownMembership, membershipTypeByMemberID, doTypeCheck = False):
        filteredMemberIDs = set()
        for memberID, node in membershipTypeByMemberID.iteritems():
            if doTypeCheck and node.entryType in (PUBLIC_MEMBER_ID, const.typeAlliance, const.typeCorporation):
                continue
            if ownMembership == MEMBERSHIP_TYPE_ADMIN or self._CanModifyOther(ownMembership, node.membershipType):
                filteredMemberIDs.add(memberID)

        return filteredMemberIDs

    def _GetGenericMemberMenuOptions(self, nodesByMemberID):
        if len(nodesByMemberID) != 1:
            return []
        node = nodesByMemberID.values()[0]
        if node.ownerInfo is None:
            return []
        memberID = node.memberID
        typeID = node.ownerInfo.typeID
        if typeID == const.typeAlliance:
            menuLabel = MenuLabel('UI/Common/Alliance')
        elif typeID == const.typeCorporation:
            menuLabel = MenuLabel('UI/Common/Corporation')
        else:
            menuLabel = MenuLabel('UI/Common/Pilot')
        memberMenuOptions = [(menuLabel, ('isDynamic', sm.GetService('menu').GetMenuFormItemIDTypeID, (memberID, typeID)))]
        return memberMenuOptions

    def _CanModifyOther(self, myMembership, theirMembership):
        if myMembership == MEMBERSHIP_TYPE_ADMIN:
            return True
        myIndex = ACCESS_SORT_ORDER.index(myMembership)
        theirIndex = ACCESS_SORT_ORDER.index(theirMembership)
        if myIndex < theirIndex:
            return True
        return False

    def GetMenuForGroupID(self, node, parentController):
        groupID = node.groupInfo.groupID
        accessRight = node.groupInfo.membershipType
        ownedByCorp = node.groupInfo.creatorID == session.corpid
        m = []
        if not ownedByCorp:
            m += [(MenuLabel('UI/Structures/AccessGroups/AddMembers'), uicore.cmd.OpenPeopleAndPlaces, ())]
        if accessRight == MEMBERSHIP_TYPE_ADMIN and not ownedByCorp:
            m += [(MenuLabel('UI/Structures/AccessGroups/EditGroup'), self._EditGroup, (parentController, groupID)), None, (MenuLabel('UI/Structures/AccessGroups/DeleteGroup'), parentController.Delete, (groupID,))]
        if session.role & ROLEMASK_ELEVATEDPLAYER:
            m.append(('GM: groupID: ' + str(groupID), blue.pyos.SetClipboardData, (str(groupID),)))
        return m

    def _EditGroup(self, parentController, groupID):
        groupInfo = parentController.GetMyGroupInfo(groupID)
        editWnd = AccessGroupsEditGroup(controller=parentController, groupInfo=groupInfo)
