#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\structure\structureBrowser\structureBrowserWnd.py
from carbonui.primitives.container import Container
from eve.client.script.ui.control.eveLabel import WndCaptionLabel
from eve.client.script.ui.control.eveWindow import Window
from eve.client.script.ui.control.tabGroup import TabGroup
from eve.client.script.ui.structure.structureBrowser.browserMyCorpStructures import BrowserMyCorpStructures
from eve.client.script.ui.structure.structureBrowser.browserAllStructures import BrowserAllStructures
from localization import GetByLabel
import carbonui.const as uiconst

class StructureBrowserWnd(Window):
    default_captionLabelPath = 'UI/Structures/Browser/StructureBrowser'
    descriptionLabelPath = 'UI/Structures/Browser/StructureBrowserDescription'
    default_name = 'Structure Browser'
    default_windowID = 'StructureBrowser'
    default_width = 800
    default_height = 600
    default_iconNum = 'res:/UI/Texture/WindowIcons/structureBrowser.png'
    default_minSize = (600, 450)

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        self.browserMyStructures = None
        self.tabs = None
        self.SetWndIcon(self.iconNum, mainTop=-8)
        WndCaptionLabel(text=GetByLabel('UI/Structures/Browser/StructureBrowser'), subcaption=GetByLabel('UI/StructureBrowser/Delayed5Minutes'), parent=self.sr.topParent, align=uiconst.RELATIVE)
        self.controller = sm.GetService('structureControllers').GetStructureBrowserController()
        self.browserCont = Container(name='browserCont', parent=self.sr.main, padding=4)
        self.browserAllStructures = BrowserAllStructures(parent=self.browserCont, structureBrowserController=self.controller, padTop=4)
        if session.corprole & const.corpRoleStationManager:
            self.browserMyStructures = BrowserMyCorpStructures(parent=self.browserCont, padTop=4, structureBrowserController=self.controller)
            tabs = ((GetByLabel('UI/Structures/Browser/AllStructures'),
              self.browserAllStructures,
              None,
              'allStructures',
              None,
              GetByLabel('UI/StructureBrowser/TabAllStructures')), (GetByLabel('UI/Structures/Browser/MyStructures'),
              self.browserMyStructures,
              None,
              'myStructures',
              None,
              GetByLabel('UI/StructureBrowser/TabMyStructures')))
            self.tabs = TabGroup(parent=self.browserCont, tabs=tabs, height=26, labelPadding=12, idx=0, padLeft=0, groupID='StructureBrowser')
        else:
            self.browserAllStructures.LoadPanel()

    def ForceProfileSettingsSelected(self):
        if self.tabs:
            self.tabs.AutoSelect()
        if self.browserAllStructures:
            self.browserMyStructures.ForceProfileSettingsSelected()

    def CloseByUser(self, *args):
        browserController = sm.GetService('structureControllers').GetStructureBrowserController()
        if not browserController.PlayerWantsToLeaveProfile():
            return
        browserController.SetProfileChangedValue(False)
        Window.CloseByUser(self, *args)
