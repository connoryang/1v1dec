#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\structure\structureSettings\structureSettingsWnd.py
from carbonui.primitives.container import Container
from eve.client.script.ui.control.buttonGroup import ButtonGroup
from eve.client.script.ui.control.buttons import Button
from eve.client.script.ui.control.eveLabel import EveLabelLarge
from eve.client.script.ui.control.themeColored import LineThemeColored
from eve.client.script.ui.structure import ChangeSignalConnect
from eve.client.script.ui.structure.structureBrowser.browserUIConst import ALL_PROFILES
from eve.client.script.ui.structure.structureSettings.serviceListCont import ServiceListCont
from eve.client.script.ui.structure.structureSettings.settingsCategoryCont import SettingsCategoryCont
from localization import GetByLabel
import log
import structures
import carbonui.const as uiconst
NO_GROUP = 0

class StructureProfileSettingCont(Container):
    TAB_ID = 'PROFILE_SETTINGS'

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.structureBrowserController = attributes.structureBrowserController
        self.allStructuresProfileController = attributes.allStructuresProfileController
        self.ChangeSignalConnection(connect=True)
        self.structureProfileController = None
        self.SetStructureProfileController()

    def ChangeSignalConnection(self, connect = True):
        signalAndCallback = [(self.structureBrowserController.on_profile_selected, self.OnProfileSelected)]
        ChangeSignalConnect(signalAndCallback, connect)

    def SetStructureProfileController(self):
        profileID = self.structureBrowserController.GetSelectedProfileID()
        if profileID != ALL_PROFILES:
            slimController = self.allStructuresProfileController.GetSlimProfileController(profileID)
            if slimController is None:
                return
            self.ChangeSignalConnectionForProfileController(connect=False)
            self.structureProfileController = slimController.GetFullProfileController()
            self.ChangeSignalConnectionForProfileController(connect=True)

    def ChangeSignalConnectionForProfileController(self, connect = True):
        if self.structureProfileController:
            signalAndCallback = [(self.structureProfileController.on_profile_value_changed, self.OnProfileChanged)]
            ChangeSignalConnect(signalAndCallback, connect)

    def OnTabSelect(self):
        profileID = self.structureBrowserController.GetSelectedProfileID()
        if self.structureProfileController is None:
            self.SetStructureProfileController()
        self.structureBrowserController.SetTabSelected(self.TAB_ID)
        self.ConstructUI()

    def ConstructUI(self, flush = True):
        self.Flush()
        profileID = self.structureBrowserController.GetSelectedProfileID()
        if profileID == ALL_PROFILES:
            return
        btnCont = Container(parent=self, idx=0, height=32, align=uiconst.TOBOTTOM)
        LineThemeColored(parent=btnCont, colorType=uiconst.COLORTYPE_UIHILIGHT, align=uiconst.TOTOP)
        self.saveBtn = Button(parent=btnCont, label=GetByLabel('UI/Common/Buttons/Save'), func=self.SaveProfile, align=uiconst.CENTERRIGHT)
        self.mainCont = Container(name='mainCont', parent=self, padding=(0, 4, 4, 4))
        self.categoryListCont = ServiceListCont(name='groupListCont', parent=self.mainCont, structureBrowserController=self.structureBrowserController)
        profileName = self.structureProfileController.GetProfileName()
        EveLabelLarge(text=profileName, parent=self.mainCont, state=uiconst.UI_DISABLED, align=uiconst.TOTOP, top=4, padBottom=5)
        self.categoryCont = SettingsCategoryCont(name='categoryCont', parent=self.mainCont, padding=(0, 2, 0, 2), structureBrowserController=self.structureBrowserController, structureProfileController=self.structureProfileController)

    def SaveProfile(self, *args):
        settingsToSave = []
        scBySettingID = self.structureProfileController.GetAllGroups()
        groupIDsInSettings = set()
        for settingID, scSet in scBySettingID.iteritems():
            for eachSg in scSet:
                if eachSg.GetSettingType() == structures.SETTINGS_TYPE_BOOL:
                    groupID = NO_GROUP
                else:
                    groupID = eachSg.GetGroupID()
                    groupIDsInSettings.add(groupID)
                settingsToSave.append((settingID, eachSg.GetValue(), groupID))

        accessGroupsController = sm.GetService('structureControllers').GetAccessGroupController()
        accessGroupsController.PopulatePublicGroupInfo(groupIDsInSettings, forceFetchInfoForPublicGroup=True)
        warning = False
        toSave = []
        for settingID, value, groupID in settingsToSave:
            if accessGroupsController.GetGroupInfoFromID(groupID, fetchToServer=False) is None:
                warning = True
                continue
            toSave.append((settingID, value, groupID))

        if warning:
            eve.Message('CustomNotify', {'notify': GetByLabel('UI/StructureSettingWnd/AccessListNotValid')})
        oldHadChangedValue = self.structureBrowserController.HasProfileChanged()
        try:
            self.structureBrowserController.SetProfileChangedValue(False)
            self.structureProfileController.SaveProfile(toSave)
        except Exception:
            self.structureBrowserController.SetProfileChangedValue(oldHadChangedValue)
            raise

    def OnProfileSelected(self, profileID):
        self.SetStructureProfileController()
        self.ConstructUI()

    def OnProfileChanged(self):
        self.saveBtn.Blink()
        self.structureBrowserController.SetProfileChangedValue(True)

    def Close(self):
        try:
            self.ChangeSignalConnection(connect=False)
            self.ChangeSignalConnectionForProfileController(connect=False)
        except Exception as e:
            log.LogError('Failed at closing structure setting wnd, e = ', e)
        finally:
            Container.Close(self)
