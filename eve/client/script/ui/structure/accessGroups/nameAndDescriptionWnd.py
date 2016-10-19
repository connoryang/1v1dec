#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\structure\accessGroups\nameAndDescriptionWnd.py
from eve.client.script.ui.control.buttonGroup import ButtonGroup
from eve.client.script.ui.control.eveEditPlainText import EditPlainText
from eve.client.script.ui.control.eveWindow import Window
import carbonui.const as uiconst
from eve.client.script.ui.control.eveSinglelineEdit import SinglelineEdit
from eve.client.script.ui.control.eveLabel import EveLabelSmall
from localization import GetByLabel

class AccessGroupsNameAndDescBaseWnd(Window):
    default_name = 'Edit Groups window'
    default_windowID = 'AccessGroupsNameAndDescBaseWnd'
    default_width = 200
    default_height = 200
    default_topParentHeight = 0
    confirmLabelPath = ''

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        self.MakeUnResizeable()
        self.controller = attributes.controller
        self.btnGroup = ButtonGroup(parent=self.sr.main, idx=0, line=True)
        self.btnGroup.AddButton(GetByLabel(self.confirmLabelPath), self.OnConfirmClicked)
        self.btnGroup.AddButton(GetByLabel('UI/Commands/Cancel'), self.Cancel)
        self.groupNameField = SinglelineEdit(parent=self.sr.main, align=uiconst.TOTOP, label=GetByLabel('UI/Structures/AccessGroups/GroupName'), padding=4, top=10, maxLength=30)
        EveLabelSmall(name='titleHeader', parent=self.sr.main, text=GetByLabel('UI/Structures/AccessGroups/GroupDescription'), align=uiconst.TOTOP, top=6, padLeft=4)
        self.groupDescField = EditPlainText(parent=self.sr.main, padding=(4, 0, 4, 4), maxLength=200)
        self.PopulateFields()

    def PopulateFields(self):
        pass

    def OnConfirmClicked(self, *args):
        name = self.groupNameField.GetValue().strip()
        desc = self.groupDescField.GetValue().strip()
        if name:
            self.Confirm(name, desc)
            self.CloseByUser()
        else:
            uicore.Message('uiwarning03')

    def Confirm(self, name, desc):
        pass

    def Cancel(self, *args):
        self.CloseByUser()


class AccessGroupsCreateWnd(AccessGroupsNameAndDescBaseWnd):
    default_captionLabelPath = 'UI/Structures/AccessGroups/CreateNewGroup'
    confirmLabelPath = 'UI/Structures/AccessGroups/CreateGroupBtn'

    def Confirm(self, name, desc):
        self.controller.OnCreateGroup(name, desc)


class AccessGroupsEditGroup(AccessGroupsNameAndDescBaseWnd):
    default_captionLabelPath = 'UI/Structures/AccessGroups/EditGroupCaption'
    confirmLabelPath = 'UI/Structures/AccessGroups/EditGroupBtn'

    def ApplyAttributes(self, attributes):
        self.groupInfo = attributes.groupInfo
        AccessGroupsNameAndDescBaseWnd.ApplyAttributes(self, attributes)

    def PostApplyAttributes(self, attributes):
        caption = GetByLabel(self.default_captionLabelPath, oldGroupName=self.groupInfo.name)
        attributes.caption = caption
        AccessGroupsNameAndDescBaseWnd.PostApplyAttributes(self, attributes)

    def PopulateFields(self):
        oldGroupName = self.groupInfo.name
        self.groupNameField.SetText(oldGroupName)
        oldGroupDesc = self.groupInfo.description
        self.groupDescField.SetText(oldGroupDesc)

    def Confirm(self, newName, newDesc):
        groupID = self.groupInfo.groupID
        self.controller.EditGroupNameAndDescription(groupID, newName, newDesc)
