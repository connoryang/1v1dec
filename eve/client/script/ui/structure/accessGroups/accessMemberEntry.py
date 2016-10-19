#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\structure\accessGroups\accessMemberEntry.py
from brennivin.itertoolsext import Bundle
import carbonui
from carbonui.primitives.container import Container
from carbonui.primitives.sprite import Sprite
from eve.client.script.ui.control.buttons import ButtonIcon
from eve.client.script.ui.control.eveLabel import EveLabelMedium
from eve.client.script.ui.shared.stateFlag import FlagIconWithState, GetRelationShipFlag
from eve.client.script.ui.util.uix import GetOwnerLogo
from localization import GetByLabel
from ownergroups.ownergroupConst import MEMBERSHIP_TYPE_MEMBER, PUBLIC_MEMBER_ID
from ownergroups.ownergroupsUIUtil import GetMembershipTypeTextureAndLabelPaths
from sovDashboard.sovStatusEntries import MouseInsideScrollEntry
import carbonui.const as uiconst
from utillib import KeyVal

class AccessMemberEntry(MouseInsideScrollEntry):
    __guid__ = 'AccessMemberEntry'
    default_name = 'DashboardEntry'
    portraitSize = 32
    ENTRYHEIGHT = 37
    isDragObject = True
    __notifyevents__ = ['OnContactChange']

    def ApplyAttributes(self, attributes):
        MouseInsideScrollEntry.ApplyAttributes(self, attributes)
        node = attributes.node
        self.controller = node.controller
        self.memberID = node.memberID
        self.groupID = node.groupID
        self.entryType = node.entryType
        self.ownerPicture = Container(name='ownerPicture', parent=self, align=uiconst.TOPLEFT, pos=(2,
         2,
         self.portraitSize,
         self.portraitSize))
        membershipLeft = self.ownerPicture.left + self.ownerPicture.width + 4
        self.membershipTypeSprite = Sprite(name='membershipTypeSprite', parent=self, align=uiconst.CENTERLEFT, pos=(membershipLeft,
         -1,
         20,
         20))
        ownerLabelLeft = self.membershipTypeSprite.left + self.membershipTypeSprite.width + 8
        self.ownerNameLabel = EveLabelMedium(name='ownerNameLabel', parent=self, left=ownerLabelLeft, align=uiconst.CENTERLEFT)
        texturePath = 'res:/UI/Texture/Icons/73_16_50.png'
        self.optionIcon = ButtonIcon(name='MyButtonIcon', parent=self, align=uiconst.TOPRIGHT, pos=(2, 2, 16, 16), iconSize=16, texturePath=texturePath, func=self.OnClickOption)
        self.optionIcon.opacity = 0.0
        self.stateFlag = FlagIconWithState(parent=self, align=uiconst.BOTTOMRIGHT, left=4, top=4)
        sm.RegisterNotify(self)

    def Load(self, node):
        membershipType = node.membershipType
        self.ownerNameLabel.text = node.ownerName
        self.LoadOwnerPicture()
        if membershipType == MEMBERSHIP_TYPE_MEMBER:
            self.membershipTypeSprite.display = False
        else:
            accessTexturePath, hintPath = GetMembershipTypeTextureAndLabelPaths(membershipType)
            self.membershipTypeSprite.texturePath = accessTexturePath
            self.membershipTypeSprite.hint = GetByLabel(hintPath)
            self.membershipTypeSprite.display = True

    def LoadOwnerPicture(self):
        self.ownerPicture.Flush()
        if self.entryType == PUBLIC_MEMBER_ID:
            texturePath = 'res:/UI/Texture/classes/AccessGroups/browser.png'
            Sprite(parent=self.ownerPicture, align=uiconst.CENTER, pos=(0, 0, 32, 32), texturePath=texturePath)
        else:
            GetOwnerLogo(self.ownerPicture, self.memberID, size=32, noServerCall=True)
            self.LoadOwnerFlag()

    def GetMenu(self, *args):
        selectedNodes = self.sr.node.scroll.GetSelectedNodes(self.sr.node)
        return self.controller.GetMenuForMember(self.groupID, selectedNodes)

    def OnClick(self, *args):
        self.sr.node.scroll.SelectNode(self.sr.node)

    def GetDragData(self, *args):
        selectedNodes = self.sr.node.scroll.GetSelectedNodes(self.sr.node)
        ret = []
        for eachNode in selectedNodes:
            memberID = eachNode.memberID
            if memberID == PUBLIC_MEMBER_ID:
                continue
            ownerInfo = eachNode.ownerInfo
            k = KeyVal(__guid__='listentry.User', itemID=memberID, charID=memberID, info=ownerInfo, membershipType=eachNode.membershipType)
            ret.append(k)

        return ret

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

    def OnContactChange(self, contactIDs, contactType = None):
        if self.memberID in contactIDs:
            self.LoadOwnerFlag()

    def LoadOwnerFlag(self):
        ownerInfo = self.sr.node.ownerInfo
        if ownerInfo is None:
            return
        flagInfo = self.GetOwnerFlagInfo(ownerInfo)
        self.stateFlag.ModifyIcon(flagInfo)

    def GetOwnerFlagInfo(self, ownerInfo):
        allianceID = None
        corpID = None
        charID = None
        if ownerInfo.typeID == const.typeAlliance:
            allianceID = ownerInfo.ownerID
        elif ownerInfo.typeID == const.typeCorporation:
            corpID = ownerInfo.ownerID
        else:
            charID = ownerInfo.ownerID
        flag = GetRelationShipFlag(charID, corpID, allianceID)
        flagInfo = sm.GetService('state').GetStatePropsColorAndBlink(flag)
        return flagInfo

    def OnDropData(self, dragObj, nodes):
        data = self.sr.node
        if data.OnDropData:
            data.OnDropData(dragObj, nodes)
