#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\structure\accessGroups\groupCont.py
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from eve.client.script.ui.control.eveLabel import EveCaptionSmall, EveLabelLarge, EveCaptionMedium
import carbonui.const as uiconst
from eve.client.script.ui.control.tabGroup import TabGroup
from eve.client.script.ui.structure import ChangeSignalConnect
from eve.client.script.ui.structure.accessGroups.accessGroupMemberCont import AccessGroupMemberCont
from eve.client.script.ui.structure.accessGroups.addCont import AddMemberCont, AddPublic
from eve.client.script.ui.structure.accessGroups.auditLogCont import AuditLogCont
from eve.client.script.ui.structure.accessGroups.dropBar import DropCont
import ownergroups.ownergroupConst as ownergroupConst
from localization import GetByLabel

class GroupCont(Container):

    def ApplyAttributes(self, attributes):
        self.currentGroupID = None
        Container.ApplyAttributes(self, attributes)
        self.controller = attributes.controller
        self.ChangeSignalConnection(connect=True)
        self.ConstructUI()

    def ChangeSignalConnection(self, connect = True):
        signalAndCallback = [(self.controller.on_group_updated, self.UpdateGroup), (self.controller.on_group_selected, self.GroupSelected)]
        ChangeSignalConnect(signalAndCallback, connect)

    def ConstructUI(self):
        self.hintLabel = EveCaptionMedium(parent=self, align=uiconst.TOTOP, top=50, text='<center>%s' % GetByLabel('UI/Structures/AccessGroups/CreateGroup'))
        self.innerCont = Container(parent=self, name='innerCont')
        self.nameAndDescCont = NameAndDescCont(name='nameAndDescCont', parent=self.innerCont, align=uiconst.TOTOP)
        self.dropCont = DropCont(parent=self.innerCont, align=uiconst.TOTOP, controller=self.controller)
        btnText = GetByLabel('UI/Structures/AccessGroups/AddPublic')
        self.addParent = Container(parent=self.innerCont, align=uiconst.TOBOTTOM, height=32)
        self.addMemberCont = AddPublic(parent=self.addParent, padBottom=2, func=self.AddPublicGroup)
        self.addMemberCont = AddMemberCont(parent=self.addParent, func=self.AddMembers, padBottom=2, padRight=4)
        self.groupCont = Container(name='browserCont', parent=self.innerCont, padding=(0, 2, 0, 4))
        self.groupMemberCont = AccessGroupMemberCont(name='groupMemberCont', parent=self.groupCont, controller=self.controller)
        self.auditLogCont = AuditLogCont(name='auditLogCont', parent=self.groupCont, controller=self.controller)
        tabs = ((GetByLabel('UI/Structures/AccessGroups/GroupMembers'),
          self.groupMemberCont,
          None,
          'groupMemberCont',
          None), (GetByLabel('UI/Structures/AccessGroups/GroupLogs'),
          self.auditLogCont,
          None,
          'auditLogCont',
          None))
        self.tabs = TabGroup(parent=self.groupCont, tabs=tabs, height=26, labelPadding=12, idx=0, padLeft=0, groupID='groupMemberConts', callback=self.OnTabSelected, autoselecttab=True)

    def UpdateGroup(self, groupID):
        if groupID == self.currentGroupID:
            self.LoadGroup(groupID)

    def LoadGroup(self, groupID):
        myGroupInfo = self.controller.GetMyGroupInfo(groupID)
        if myGroupInfo is None:
            return
        self.currentGroupID = groupID
        self.dropCont.dropGridCont.SetCurrentGroupID(groupID, myGroupInfo.membershipType)
        self.nameAndDescCont.SetNameAndDescription(myGroupInfo.name, myGroupInfo.description)

    def Close(self, *args):
        self.ChangeSignalConnection(connect=False)
        Container.Close(self)

    def GroupSelected(self, groupID):
        if groupID is None:
            self.innerCont.display = False
            self.hintLabel.display = True
            return
        self.innerCont.display = True
        self.hintLabel.display = False
        if self.controller.IsGroupCorpOwned(groupID):
            self.dropCont.display = False
            self.addParent.display = False
        else:
            self.dropCont.display = True
            self.addParent.display = True
        self.LoadGroup(groupID)
        if self.tabs.destroyed:
            return
        selectedTabName = self.tabs.GetSelectedArgs()
        if selectedTabName == 'groupMemberCont':
            self.groupMemberCont.LoadGroup(groupID)
        elif selectedTabName == 'auditLogCont':
            self.auditLogCont.LoadGroup(groupID)

    def OnTabSelected(self, tabIdx):
        selectedGroupID = self.controller.GetSelectedGroupID()
        self.GroupSelected(selectedGroupID)

    def AddPublicGroup(self, *args):
        self.controller.AddPublicMember(self.currentGroupID)

    def AddMembers(self, characters):
        members = {characterID:ownergroupConst.MEMBERSHIP_TYPE_MEMBER for characterID in characters}
        self.controller.AddMembers(self.currentGroupID, members)


class NameAndDescCont(Container):
    MAX_DESC_HEIGHT = 100

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.groupNameLabel = EveCaptionSmall(name='groupName', parent=self, padLeft=10, align=uiconst.TOTOP)
        self.groupDescLabel = EveLabelLarge(name='groupDescLabel', parent=self, padLeft=10, align=uiconst.TOTOP)

    def SetNameAndDescription(self, name, description):
        self.groupNameLabel.text = name
        self.groupDescLabel.text = description
        if description:
            self.groupDescLabel.display = True
        else:
            self.groupDescLabel.display = False

    def UpdateAlignment(self, *args, **kwds):
        retVal = Container.UpdateAlignment(self, *args, **kwds)
        if getattr(self, 'groupNameLabel', None) and getattr(self, 'groupDescLabel', None):
            self.groupDescLabel.SetBottomAlphaFade(self.MAX_DESC_HEIGHT, 10)
            newHeight = self.groupNameLabel.height + min(self.MAX_DESC_HEIGHT, self.groupDescLabel.textheight) + 4
            self.height = newHeight
        return retVal
