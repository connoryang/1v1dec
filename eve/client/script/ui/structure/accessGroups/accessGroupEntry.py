#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\structure\accessGroups\accessGroupEntry.py
import carbonui
from eve.client.script.ui.control.buttons import ButtonIcon
from eve.client.script.ui.control.eveLabel import EveLabelLarge
from eve.client.script.ui.control.themeColored import FillThemeColored
from eve.client.script.ui.structure import ChangeSignalConnect
from eve.client.script.ui.structure.accessGroups.ownerGroupUtils import GetOwnerIDsAndMembershipTypeFromNodes
from ownergroups.ownergroupConst import MEMBERSHIP_TYPE_ADMIN
from sovDashboard.sovStatusEntries import MouseInsideScrollEntry
import carbonui.const as uiconst
from utillib import KeyVal
ADMIN_OPACITY = 1.0
OTHER_MEMBERSHIPTYPE_OPACITY = 0.4

class AccessGroupEntry(MouseInsideScrollEntry):
    default_name = 'AccessGroupEntry'
    ENTRYHEIGHT = 36
    isDragObject = True

    def ApplyAttributes(self, attributes):
        MouseInsideScrollEntry.ApplyAttributes(self, attributes)
        node = attributes.node
        self.controller = node.controller
        isNormal = node.isNormal
        self.groupID = node.groupInfo.groupID
        self.ChangeSignalConnection(connect=True)
        self.ConstructHiliteFill()
        membershipType = node.groupInfo.membershipType
        if membershipType == MEMBERSHIP_TYPE_ADMIN:
            fillOpacity = ADMIN_OPACITY
        else:
            fillOpacity = OTHER_MEMBERSHIPTYPE_OPACITY
        self.bgFill = FillThemeColored(name='bgFill', bgParent=self, padding=(1, 1, 1, 1), colorType=uiconst.COLORTYPE_UIBASECONTRAST, opacity=fillOpacity)
        self.groupNameLabel = EveLabelLarge(name='groupName', parent=self, left=10, align=uiconst.CENTERLEFT)
        texturePath = 'res:/UI/Texture/Icons/73_16_50.png'
        self.optionIcon = ButtonIcon(name='MyButtonIcon', parent=self, align=uiconst.TOPRIGHT, pos=(2, 2, 16, 16), iconSize=16, texturePath=texturePath, func=self.OnClickOption)
        self.optionIcon.opacity = 0.0
        if not isNormal:
            self.opacity = 0.1

    def ChangeSignalConnection(self, connect = True):
        signalAndCallback = [(self.controller.on_group_selected, self.OnGroupSelected)]
        ChangeSignalConnect(signalAndCallback, connect)

    def Load(self, node):
        groupInfo = node.groupInfo
        self.groupNameLabel.text = groupInfo.name
        self.hint = groupInfo.description

    def OnClick(self, *args):
        self.Select()
        self.controller.SelectGroup(self.groupID)

    def GetMenu(self, *args):
        return self.controller.GetMenuForGroupID(self.sr.node)

    def GetDragData(self):
        ret = KeyVal(nodeType='AccessGroupEntry', groupID=self.groupID, label=self.sr.node.groupInfo.name)
        return [ret]

    def OnGroupSelected(self, groupID):
        if groupID == self.groupID:
            self.Select()
        else:
            self.Deselect()

    def OnDropData(self, dragSource, dragData):
        if not dragData:
            return
        groupID = self.groupID
        membershipTypesByMemberID = GetOwnerIDsAndMembershipTypeFromNodes(dragData, useNodeMembershipType=True)
        if membershipTypesByMemberID:
            self.controller.AddMembers(groupID, membershipTypesByMemberID)

    def OnClickOption(self, *args):
        carbonui.control.menu.ShowMenu(self)

    def OnMouseEnter(self, *args):
        MouseInsideScrollEntry.OnMouseEnter(self, *args)
        self.FadeOptionIcon(self.optionIcon.opacity, 1.0)

    def OnMouseNoLongerInEntry(self):
        MouseInsideScrollEntry.OnMouseNoLongerInEntry(self)
        self.FadeOptionIcon(self.optionIcon.opacity, 0.0)

    def FadeOptionIcon(self, fromValue, toValue):
        uicore.animations.FadeTo(self.optionIcon, startVal=fromValue, endVal=toValue, duration=0.1, loops=1)

    def Close(self):
        self.ChangeSignalConnection(connect=False)
        MouseInsideScrollEntry.Close(self)
