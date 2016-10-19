#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\structure\accessGroups\accessGroupListCont.py
from collections import defaultdict
from carbonui.primitives.container import Container
from carbonui.util.bunch import Bunch
from eve.client.script.ui.control.eveScroll import Scroll
from eve.client.script.ui.structure import ChangeSignalConnect
from eve.client.script.ui.structure.accessGroups.accessGroupEntry import AccessGroupEntry
from carbonui.util.various_unsorted import SortListOfTuples
from eve.client.script.ui.control import entries as listentry
from eve.client.script.ui.structure.accessGroups.addCont import AddGroupCont
from ownergroups.ownergroupsUIUtil import ACCESS_SORT_ORDER
DEFAULT_CORP_GROUP = -2

class GroupListCont(Container):

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.controller = attributes.controller
        self.ChangeSignalConnection(connect=True)
        self.addCont = AddGroupCont(parent=self, controller=self.controller)
        self.scroll = Scroll(name='groupListScroll', parent=self, padBottom=4)
        self.LoadGroups()

    def ChangeSignalConnection(self, connect = True):
        signalAndCallback = [(self.controller.on_new_group_created, self.LoadGroups),
         (self.controller.on_group_deleted, self.LoadGroups),
         (self.controller.on_group_updated, self.LoadGroups),
         (self.controller.on_groups_reload, self.LoadGroups)]
        ChangeSignalConnect(signalAndCallback, connect)

    def LoadGroups(self, *args):
        myGroups = self.controller.GetMyGroups()
        searchResults = self.controller.GetCurrentSearchResults()
        groupIDs = set()
        nodesByMembership = defaultdict(list)
        for groupID, g in myGroups.iteritems():
            groupIDs.add(groupID)
            groupName = g.name
            nodeData = Bunch(decoClass=AccessGroupEntry, controller=self.controller, groupInfo=g, isNormal=self.IsNormalGroup(groupID, searchResults))
            node = (groupName.lower(), nodeData)
            if g.creatorID == session.corpid:
                myMembership = DEFAULT_CORP_GROUP
            else:
                myMembership = g.membershipType
            nodesByMembership[myMembership].append(node)

        scrollList = []
        for eachMemberShipType in [DEFAULT_CORP_GROUP] + ACCESS_SORT_ORDER:
            nodes = nodesByMembership.get(eachMemberShipType)
            if nodes:
                sortedNodes = SortListOfTuples(nodes)
                scrollList += sortedNodes
                scrollList.append(listentry.Get('Space', {'height': 12}))

        self.scroll.Load(contentList=scrollList)
        groupID = None
        lastLoadedGroupID = settings.user.ui.Get('accessGroup_lastGroup', None)
        if lastLoadedGroupID in groupIDs:
            groupID = lastLoadedGroupID
        elif len(scrollList) > 1:
            firstNode = scrollList[0]
            groupID = firstNode.groupInfo.groupID
        self.controller.SelectGroup(groupID)

    def IsNormalGroup(self, groupID, searchResults):
        if searchResults is None:
            return True
        _, groupsWithMatchedMembers = searchResults
        return groupID in groupsWithMatchedMembers

    def Close(self):
        self.ChangeSignalConnection(connect=False)
        Container.Close(self)
