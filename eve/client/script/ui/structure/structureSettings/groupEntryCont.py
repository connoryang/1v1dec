#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\structure\structureSettings\groupEntryCont.py
from carbonui.control.menuLabel import MenuLabel
from eve.client.script.ui.control.eveLabel import EveLabelMedium
import carbonui.const as uiconst
from eve.client.script.ui.structure.structureSettings.profileEntry import ProfileEntryBase
from eve.client.script.ui.structure.structureSettings.uiSettingUtil import AddValueEdit
from localization import GetByLabel
import structures
from utillib import KeyVal
LABEL_LEFT = 26
VALUE_TYPES = (structures.SETTINGS_TYPE_INT,
 structures.SETTINGS_TYPE_FLOAT,
 structures.SETTINGS_TYPE_PERCENTAGE,
 structures.SETTINGS_TYPE_ISK)

class GroupEntry(ProfileEntryBase):
    default_align = uiconst.TOTOP
    default_state = uiconst.UI_NORMAL
    default_height = 28
    isDragObject = True
    rightBtnTexturePath = 'res:/UI/Texture/Icons/73_16_210.png'

    def ApplyAttributes(self, attributes):
        ProfileEntryBase.ApplyAttributes(self, attributes)
        self.settingGroupController = attributes.settingGroupController
        self.structureProfileController = attributes.structureProfileController
        self.groupID = attributes.groupID
        groupInfo = attributes.groupInfo
        hint = GetByLabel('UI/StructureSettingWnd/RemoveGroup')
        EveLabelMedium(name='groupName', parent=self, left=LABEL_LEFT, align=uiconst.CENTERLEFT, text=groupInfo['name'], hint=groupInfo['description'])
        self.valueEdit = None
        if self.settingGroupController.GetSettingType() in VALUE_TYPES:
            self.AddValueEdit()

    def OnRightBtnClicked(self, *args):
        self.RemoveGroup()

    def GetDragData(self):
        accessGroupsController = sm.GetService('structureControllers').GetAccessGroupController()
        groupInfo = accessGroupsController.GetGroupInfoFromID(self.groupID)
        if not groupInfo:
            return []
        ret = KeyVal(nodeType='AccessGroupEntry', groupID=self.groupID, label=groupInfo['name'])
        return [ret]

    def GetMenu(self, *args):
        m = [(MenuLabel('UI/StructureSettingWnd/RemoveGroup'), self.RemoveGroup, ()), (MenuLabel('UI/StructureSettingWnd/ShowGroupInfo'), self.ShowGroupInfo, ())]
        accessGroupsController = sm.GetService('structureControllers').GetAccessGroupController()
        myGroups = accessGroupsController.GetMyGroups()
        if self.groupID in myGroups:
            m += [(MenuLabel('UI/StructureSettingWnd/ViewGroup'), self.ViewGroup, ())]
        return m

    def RemoveGroup(self):
        self.structureProfileController.RemoveGroup(self.settingGroupController)

    def Close(self):
        self.settingGroupController = None
        ProfileEntryBase.Close(self)

    def AddValueEdit(self):
        if self.settingGroupController.GetSettingType() in VALUE_TYPES:
            self.valueEdit = AddValueEdit(parent=self, sgController=self.settingGroupController, callback=self.OnValueChanged)
            self.valueEdit.left = self.rightBtn.left + self.rightBtn.width

    def OnValueChanged(self, *args):
        if self.valueEdit is None:
            return
        value = self.valueEdit.GetValue()
        self.settingGroupController.SetValue(value)

    def ShowGroupInfo(self):
        from eve.client.script.ui.structure.accessGroups.groupInfoWnd import GroupInfoWnd
        GroupInfoWnd.Open(groupID=self.groupID, windowID='groupInfoWnd_%s' % self.groupID)
        return True

    def ViewGroup(self):
        accessGroupsController = sm.GetService('structureControllers').GetAccessGroupController()
        from eve.client.script.ui.structure.accessGroups.accesGroupsWnd import AccessGroupsWnd
        wnd = AccessGroupsWnd.GetIfOpen()
        accessGroupsController.SelectGroup(self.groupID, sendSignal=bool(wnd))
        if not wnd:
            AccessGroupsWnd.Open()
