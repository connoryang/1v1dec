#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\structure\structureBrowser\browserMyCorpStructures.py
from carbonui.control.dragResizeCont import DragResizeCont
from carbonui.primitives.container import Container
from carbonui.util.bunch import Bunch
from eve.client.script.ui.control.eveScroll import Scroll
from eve.client.script.ui.control.scrollUtil import TabFinder
from eve.client.script.ui.control.tabGroup import TabGroup
from eve.client.script.ui.quickFilter import QuickFilterEdit
from eve.client.script.ui.structure import ChangeSignalConnect
import eve.client.script.ui.structure.structureBrowser.browserUIConst as browserUIConst
from eve.client.script.ui.structure.structureBrowser.controllers.structureEntryController import StructureEntryController
from eve.client.script.ui.structure.structureBrowser.entries.structureEntryMyCorp import StructureEntryMyCorp, StructureEntryMyCorpAllProfiles
from eve.client.script.ui.structure.structureBrowser.structureProfiles import StructureProfiles
from eve.client.script.ui.structure.structureSettings.structureSettingsWnd import StructureProfileSettingCont
from localization import GetByLabel
import carbonui.const as uiconst
from eve.client.script.ui.control.eveLabel import EveCaptionSmall, EveLabelMedium, EveLabelLarge
OWNER_ANY = 1
OWNER_NPC = 2
OWNER_CORP = 3

class BrowserMyCorpStructures(Container):
    default_name = 'BrowserMyStructures'

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.structureBrowserController = attributes.structureBrowserController
        self.currentProfileLoaded = None
        self.tabs = None
        self.isInitialized = False

    def OnTabSelect(self):
        self.LoadPanel()

    def LoadPanel(self):
        self.display = True
        if self.isInitialized:
            return
        self.isInitialized = True
        self.allStructuresProfileController = sm.GetService('structureControllers').GetAllStructuresProfileController()
        self.ChangeSignalConnection(connect=True)
        profileParent = DragResizeCont(name='profileParent', parent=self, align=uiconst.TOLEFT_PROP, minSize=0.1, maxSize=0.5, defaultSize=0.5, settingsID='myStructuresSplitter')
        profileListCont = StructureProfiles(parent=profileParent, allStructuresProfileController=self.allStructuresProfileController, structureBrowserController=self.structureBrowserController)
        self.structeListAndProfileSettingsCont = Container(name='structureListAndProfileSettingsCont', parent=self, padding=(4, 0, 4, 4))
        self.LoadTabs()

    def ChangeSignalConnection(self, connect = True):
        signalAndCallback = [(self.structureBrowserController.on_profile_selected, self.OnProfileSelected),
         (self.allStructuresProfileController.on_profile_saved, self.OnProfileSaved),
         (self.structureBrowserController.on_profile_deleted, self.OnProfileDeleted),
         (self.structureBrowserController.on_corp_structures_changed, self.OnCorpStructuresChanged)]
        ChangeSignalConnect(signalAndCallback, connect)

    def LoadTabs(self):
        self.VerifySelectedProfileIdIsValid()
        profileID = self.structureBrowserController.GetSelectedProfileID()
        self.structeListAndProfileSettingsCont.Flush()
        myStructuresPanel = MyStructuresPanel(parent=self.structeListAndProfileSettingsCont, allStructuresProfileController=self.allStructuresProfileController, structureBrowserController=self.structureBrowserController)
        tabs = [(GetByLabel('UI/StructureBrowser/StructuresWithProfile'),
          myStructuresPanel,
          None,
          'myStructuresPanel',
          None,
          GetByLabel('UI/StructureBrowser/StructuresWithProfileHint'))]
        if profileID != browserUIConst.ALL_PROFILES:
            self.profileSettings = StructureProfileSettingCont(parent=self.structeListAndProfileSettingsCont, allStructuresProfileController=self.allStructuresProfileController, structureBrowserController=self.structureBrowserController)
            profileTab = (GetByLabel('UI/StructureBrowser/ProfileSettings'),
             self.profileSettings,
             None,
             'profileSettings',
             None,
             GetByLabel('UI/StructureBrowser/ProfileSettingsHint'))
            tabs.append(profileTab)
        self.tabs = TabGroup(parent=self.structeListAndProfileSettingsCont, tabs=tabs, height=32, idx=0, padLeft=0, groupID='profile_structuresAndsettings', padTop=0)
        self.profileDescLabel = EveLabelMedium(parent=self.structeListAndProfileSettingsCont, name='profileDescLabel', align=uiconst.TOTOP, idx=0)
        self.profileNameLabel = EveCaptionSmall(parent=self.structeListAndProfileSettingsCont, name='profileNameLabel', align=uiconst.TOTOP, idx=0)
        self.SetProfileName()

    def VerifySelectedProfileIdIsValid(self):
        profileID = self.structureBrowserController.GetSelectedProfileID()
        validProfileIDs = sm.GetService('structureControllers').GetValidProfileIDs()
        isProfileValid = profileID not in validProfileIDs
        if isProfileValid:
            self.structureBrowserController.SelectProfile(browserUIConst.ALL_PROFILES, sendSignal=False)
            self.currentProfileLoaded = browserUIConst.ALL_PROFILES

    def ForceProfileSettingsSelected(self):
        if self.tabs:
            self.tabs.AutoSelect()

    def OnProfileSelected(self, profileID):
        self.SetProfileName()
        if self.currentProfileLoaded is None or self._ProfileTypeHasChanged(profileID):
            self.LoadTabs()
        self.currentProfileLoaded = profileID

    def _ProfileTypeHasChanged(self, profileID):
        if profileID == self.currentProfileLoaded:
            return False
        if browserUIConst.ALL_PROFILES not in (profileID, self.currentProfileLoaded):
            return False
        return True

    def OnProfileSaved(self, profileID):
        self.structureBrowserController.SetProfileChangedValue(False)
        self.SetProfileName()

    def OnProfileDeleted(self, profileID, selectedProfileChanged):
        if selectedProfileChanged:
            self.LoadTabs()

    def OnCorpStructuresChanged(self):
        if self.structureBrowserController.GetSelectedTab() != MyStructuresPanel.TAB_ID:
            return
        self.LoadTabs()

    def SetProfileName(self):
        if self.structureBrowserController.GetSelectedProfileID() == browserUIConst.ALL_PROFILES:
            name = GetByLabel('UI/Structures/Browser/AnyProfile')
            desc = ''
        else:
            selectedProfileID = self.structureBrowserController.GetSelectedProfileID()
            selectedProfileController = self.allStructuresProfileController.GetSlimProfileController(selectedProfileID)
            name = selectedProfileController.GetProfileName()
            desc = selectedProfileController.GetProfileDescription()
        self.profileNameLabel.text = name
        self.profileDescLabel.text = desc
        self.profileNameLabel.display = False
        self.profileDescLabel.display = False

    def Close(self):
        if self.isInitialized:
            self.ChangeSignalConnection(connect=False)
        Container.Close(self)


class MyStructuresPanel(Container):
    TAB_ID = 'STRUCUTRES'

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.allStructuresProfileController = attributes.allStructuresProfileController
        self.structureBrowserController = attributes.structureBrowserController
        self.isInitialized = False
        self.ChangeSignalConnection(connect=True)

    def ChangeSignalConnection(self, connect = True):
        signalAndCallback = [(self.structureBrowserController.on_profile_selected, self.OnProfileSelected), (self.allStructuresProfileController.on_profile_saved, self.OnProfileAssigned), (self.allStructuresProfileController.on_profile_assigned, self.OnProfileAssigned)]
        ChangeSignalConnect(signalAndCallback, connect)

    def OnTabSelect(self):
        self.structureBrowserController.SetTabSelected(self.TAB_ID)
        self.LoadPanel()

    def LoadPanel(self):
        if self.isInitialized:
            self.UpdateScroll()
            return
        self.topPanel = Container(name='topPanel', parent=self, align=uiconst.TOTOP, height=20, padding=(0, 6, 0, 6))
        self.profilaNameLabel = EveLabelLarge(text='', parent=self.topPanel, state=uiconst.UI_DISABLED, align=uiconst.TOPLEFT, top=2)
        self.scroll = Scroll(parent=self, id='MyStructuresScroll')
        self.scroll.sr.fixedColumns = StructureEntryMyCorp.GetFixedColumns()
        self.scroll.OnSelectionChange = self.OnScrollSelectionChange
        self.scroll.GetTabStops = self.GetTabStops
        self.filterEdit = QuickFilterEdit(name='searchField', parent=self.topPanel, hinttext=GetByLabel('UI/Inventory/Filter'), maxLength=64, align=uiconst.TORIGHT, OnClearFilter=self.OnFilterEditCleared, padRight=4)
        self.filterEdit.ReloadFunction = self.OnFilterEdit
        self.UpdateScroll()
        self.isInitialized = True

    def GetTabStops(self, headertabs, idx = None):
        decoClass = self.GetDecoClass()
        return TabFinder().GetTabStops(self.scroll.sr.nodes, headertabs, decoClass, idx=idx)

    def LoadProfile(self, profileID):
        self.UpdateScroll()

    def UpdateScroll(self):
        if self.structureBrowserController.GetSelectedTab() != self.TAB_ID:
            return
        self.SetLabelProfileName()
        decoClass = self.GetDecoClass()
        scrollList = self.GetScrollList(decoClass=decoClass)
        self.scroll.LoadContent(contentList=scrollList, headers=decoClass.GetHeaders(), noContentHint=GetByLabel('UI/Structures/Browser/NoStructuresFound'))

    def SetLabelProfileName(self):
        currentProfileID = self.structureBrowserController.GetSelectedProfileID()
        c = self.allStructuresProfileController.GetSlimProfileController(currentProfileID)
        if c:
            text = c.GetProfileName()
        else:
            text = ''
        self.profilaNameLabel.text = text

    def IsFilteredOut(self, controller):
        filterText = self.filterEdit.GetValue().strip().lower()
        if filterText:
            text = controller.GetName() + controller.GetOwnerName() + controller.GetSystemName()
            if text.lower().find(filterText) == -1:
                return True
        currentProfileID = self.structureBrowserController.GetSelectedProfileID()
        if currentProfileID != browserUIConst.ALL_PROFILES and currentProfileID != controller.GetProfileID():
            return True
        return False

    def GetScrollList(self, decoClass):
        scrollList = []
        structureControllers = self.structureBrowserController.GetMyStructures()
        for controller in structureControllers:
            if self.IsFilteredOut(controller):
                continue
            slimProfileController = self.allStructuresProfileController.GetSlimProfileController(controller.GetProfileID())
            node = Bunch(controller=controller, decoClass=decoClass, columnSortValues=decoClass.GetColumnSortValues(controller, slimProfileController), charIndex=controller.GetName(), slimProfileController=slimProfileController, GetSortValue=decoClass.GetSortValue)
            scrollList.append(node)

        return scrollList

    def GetDecoClass(self):
        allProfilesVisible = self.structureBrowserController.GetSelectedProfileID() == browserUIConst.ALL_PROFILES
        if allProfilesVisible:
            return StructureEntryMyCorpAllProfiles
        else:
            return StructureEntryMyCorp

    def OnScrollSelectionChange(self, entries):
        pass

    def OnServiceCombo(self, *args):
        self.UpdateScroll()

    def OnFilterEdit(self):
        self.UpdateScroll()

    def OnFilterEditCleared(self):
        self.UpdateScroll()

    def OnProfileSelected(self, profileID):
        if self.structureBrowserController.GetSelectedTab() == self.TAB_ID:
            self.LoadProfile(profileID)

    def OnProfileAssigned(self, profileID):
        self.UpdateScroll()

    def Close(self):
        self.ChangeSignalConnection(connect=False)
        Container.Close(self)
