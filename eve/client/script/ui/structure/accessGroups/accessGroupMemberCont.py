#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\structure\accessGroups\accessGroupMemberCont.py
from carbonui.primitives.container import Container
from carbonui.util.bunch import Bunch
from carbonui.util.various_unsorted import SortListOfTuples
from eve.client.script.ui.control.eveScroll import Scroll
from eve.client.script.ui.structure import ChangeSignalConnect
from eve.client.script.ui.structure.accessGroups.accessMemberEntry import AccessMemberEntry
from eve.client.script.ui.structure.accessGroups.ownerGroupUtils import GetOwnerIDsAndMembershipTypeFromNodes, GetOwnerTypeSortValue
from localization import GetByLabel
from ownergroups.ownergroupConst import PUBLIC_MEMBER_ID
from ownergroups.ownergroupsUIUtil import ACCESS_SORT_ORDER

class AccessGroupMemberCont(Container):

    def ApplyAttributes(self, attributes):
        self.currentGroupID = None
        self.groupMemberEntries = {}
        self.controller = attributes.controller
        self.ChangeSignalConnection(connect=True)
        Container.ApplyAttributes(self, attributes)
        self.scroll = Scroll(name='memberScroll', parent=self)
        self.scroll.sr.content.OnDropData = self.OnDropDataInScroll

    def ChangeSignalConnection(self, connect = True):
        signalAndCallback = [(self.controller.on_group_selected, self.LoadGroup),
         (self.controller.on_groupmembers_changed, self.OnGroupMembersChanged),
         (self.controller.on_groupmembers_removed, self.OnGroupMembersRemoved),
         (self.controller.on_group_updated, self.UpdateGroup)]
        ChangeSignalConnect(signalAndCallback, connect)

    def UpdateGroup(self, groupID):
        if groupID == self.currentGroupID:
            self.LoadGroup(groupID)

    def LoadGroup(self, groupID):
        myGroupInfo = self.controller.GetMyGroupInfo(groupID)
        if myGroupInfo is None:
            return
        self.groupMemberEntries = {}
        self.currentGroupID = groupID
        searchResults = self.controller.GetCurrentSearchResults()
        try:
            groupMembers = self.GetFilteredMembers(groupID, searchResults)
        except UserError as e:
            self.scroll.Load(contentList=[], noContentHint='UI/Structures/AccessGroups/MemberlistNotLoaded')
            eve.Message(e.msg, e.dict)
            return

        toPrime = groupMembers.keys()
        cfg.eveowners.Prime(toPrime)
        scrollList = []
        for memberID, membershipType in groupMembers.iteritems():
            node, sortValue = self.GetNodeAndSortValueForAccessEntry(groupID, memberID, membershipType)
            self.groupMemberEntries[memberID] = node
            scrollList.append((sortValue, node))

        scrollList = SortListOfTuples(scrollList)
        if searchResults:
            noContentHint = GetByLabel('UI/Structures/AccessGroups/SearchNoContentHint')
        else:
            noContentHint = ''
        self.scroll.Load(contentList=scrollList, noContentHint=noContentHint)

    def GetFilteredMembers(self, groupID, searchResults):
        groupMembers = self.controller.GetMembers(groupID)
        if searchResults:
            matchedMembers, _ = searchResults
            return {memberID:m for memberID, m in groupMembers.iteritems() if memberID in matchedMembers}
        else:
            return groupMembers

    def GetSortValue(self, membershipType, ownerName, entryType):
        ownerTypeSortValue = GetOwnerTypeSortValue(entryType)
        accessSortValue = ACCESS_SORT_ORDER.index(membershipType)
        sortValue = (accessSortValue, ownerTypeSortValue, ownerName.lower())
        return sortValue

    def GetNodeAndSortValueForAccessEntry(self, groupID, memberID, membershipType):
        ownerInfo, ownerName, entryType = self._GetOwnerInfoAndName(memberID)
        sortValue = self.GetSortValue(membershipType, ownerName, entryType)
        node = Bunch(decoClass=AccessMemberEntry, ownerName=ownerName, itemID=memberID, memberID=memberID, membershipType=membershipType, entryType=entryType, controller=self.controller, groupID=groupID, ownerInfo=ownerInfo, OnDropData=self.OnDropDataInScroll)
        node.sort_sortValue = sortValue
        return (node, sortValue)

    def _GetOwnerInfoAndName(self, memberID):
        if memberID == PUBLIC_MEMBER_ID:
            return (None, GetByLabel('UI/Structures/AccessGroups/PublicUser'), PUBLIC_MEMBER_ID)
        else:
            ownerInfo = cfg.eveowners.Get(memberID)
            ownerName = ownerInfo.name
            return (ownerInfo, ownerName, ownerInfo.typeID)

    def UpdateAccessMemberEntryNode(self, memberID, membershipType):
        node = self.groupMemberEntries[memberID]
        node.membershipType = membershipType
        ownerInfo, ownerName, entryType = self._GetOwnerInfoAndName(memberID)
        sortValue = self.GetSortValue(membershipType, ownerName, entryType)
        node.sort_sortValue = sortValue
        if node.panel:
            node.panel.Load(node)

    def OnGroupMembersChangedSameMembershipType(self, groupID, memberIDs, membershipType, *args):
        membershipTypesByMemberID = {x:membershipType for x in memberIDs}
        self.OnGroupMembersChanged(groupID, membershipTypesByMemberID)

    def OnGroupMembersChanged(self, groupID, *args):
        membershipTypesByMemberID = self.controller.GetMembers(groupID)
        if self.currentGroupID != groupID:
            return
        entriesToAdd = []
        for eachMemberID, membershipType in membershipTypesByMemberID.iteritems():
            if eachMemberID in self.groupMemberEntries:
                self.UpdateAccessMemberEntryNode(eachMemberID, membershipType)
            else:
                node, sortValue = self.GetNodeAndSortValueForAccessEntry(groupID, eachMemberID, membershipType)
                self.groupMemberEntries[eachMemberID] = node
                entriesToAdd.append(node)

        self.scroll.AddNodes(0, entriesToAdd)
        self.scroll.Sort('sortValue')

    def OnGroupMembersRemoved(self, groupID, memberIDs):
        if self.currentGroupID != groupID:
            return
        nodesToRemove = []
        for eachMemberID in memberIDs:
            node = self.groupMemberEntries.pop(eachMemberID, None)
            if node:
                nodesToRemove.append(node)

        self.scroll.RemoveNodes(nodesToRemove)

    def OnDropDataInScroll(self, dragObj, nodes):
        membershipTypesByMemberID = GetOwnerIDsAndMembershipTypeFromNodes(nodes)
        if membershipTypesByMemberID:
            self.controller.AddMembers(self.currentGroupID, membershipTypesByMemberID)

    def Close(self, *args):
        self.ChangeSignalConnection(connect=False)
        Container.Close(self)
