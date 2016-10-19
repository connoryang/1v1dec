#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\structure\accessGroups\groupInfoWnd.py
from carbon.common.script.util.linkUtil import GetShowInfoLink
from carbonui.control.scrollContainer import ScrollContainer
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from eve.client.script.ui.control.eveLabel import EveLabelMedium, WndCaptionLabel
from eve.client.script.ui.control.eveWindow import Window
from localization import GetByLabel
import carbonui.const as uiconst
from utillib import KeyVal

class GroupInfoWnd(Window):
    default_minSize = (200, 130)
    default_width = 300
    default_iconNum = 'res:/UI/Texture/WindowIcons/accessGroups.png'
    default_captionLabelPath = 'UI/Structures/AccessGroups/AccessGroup'

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        self.SetWndIcon(self.iconNum, mainTop=-8)
        self.sr.mainIcon.state = uiconst.UI_NORMAL
        self.sr.mainIcon.GetDragData = self.GetDragDataForIcon
        self.sr.mainIcon.isDragObject = True
        self.groupID = attributes.groupID
        self.groupInfo = GetGroupInfo(self.groupID)
        self.groupName = self.groupInfo['name']
        wndCaption = WndCaptionLabel(text=self.groupName, parent=self.sr.topParent, align=uiconst.RELATIVE)
        scrollContainer = ScrollContainer(parent=self.sr.main, padding=(10, 0, 10, 10))
        self.contentCont = ContainerAutoSize(parent=scrollContainer, align=uiconst.TOTOP, columns=1)
        self.LoadContentCont()
        w, h = self.contentCont.GetAbsoluteSize()
        newHeight = h + self.sr.topParent.height + 40
        self.height = newHeight

    def LoadContentCont(self):
        self.contentCont.Flush()
        groupDesc = self.groupInfo['description']
        admins = self.groupInfo['admins']
        if groupDesc:
            EveLabelMedium(parent=self.contentCont, text=groupDesc, padTop=6, align=uiconst.TOTOP)
        else:
            descText = GetByLabel('UI/Structures/AccessGroups/NoGroupDescription')
            EveLabelMedium(parent=self.contentCont, text=descText, align=uiconst.TOTOP, padTop=6, italic=True)
        for adminID in admins:
            ownerInfo = cfg.eveowners.Get(adminID)
            charName = ownerInfo.name
            charText = GetShowInfoLink(ownerInfo.typeID, charName, itemID=adminID)
            text = GetByLabel('UI/Structures/AccessGroups/GroupOwner', ownerName=charText)
            EveLabelMedium(parent=self.contentCont, text=text, align=uiconst.TOTOP, padTop=6, state=uiconst.UI_NORMAL)

    def GetDragDataForIcon(self):
        ret = KeyVal(nodeType='AccessGroupEntry', groupID=self.groupID, label=self.groupName)
        return [ret]


def GetGroupInfo(groupID):
    accessGroupsController = sm.GetService('structureControllers').GetAccessGroupController()
    groupInfo = accessGroupsController.GetGroupInfoFromID(groupID)
    return groupInfo
