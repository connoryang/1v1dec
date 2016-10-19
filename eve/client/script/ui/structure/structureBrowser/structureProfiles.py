#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\structure\structureBrowser\structureProfiles.py
from carbonui.primitives.container import Container
from carbonui.util.bunch import Bunch
from carbonui.util.sortUtil import SortListOfTuples
from eve.client.script.ui.control.eveLabel import EveLabelMedium
from eve.client.script.ui.control.eveScroll import Scroll
from eve.client.script.ui.control.infoIcon import MoreInfoIcon
from eve.client.script.ui.control.themeColored import FillThemeColored
from eve.client.script.ui.structure import ChangeSignalConnect
from eve.client.script.ui.structure.accessGroups.addCont import AddCont
from eve.client.script.ui.structure.structureBrowser.browserUIConst import ALL_PROFILES
from eve.client.script.ui.structure.structureBrowser.nameAndDescriptionWnd import CreateProfileWnd
from eve.client.script.ui.structure.structureBrowser.entries.structureProfileEntry import StructureProfileEntry, StructureAllProfilesEntry
from eve.client.script.ui.structure.structureSettings.controllers.slimProfileController import SlimStructureProfileController, SlimStructureAllProfilesController
from localization import GetByLabel
import log
from utillib import KeyVal
import carbonui.const as uiconst

class StructureProfiles(Container):
    explanationLabelPath = 'UI/StructureProfiles/ProfileHint'

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.allStructuresProfileController = attributes.allStructuresProfileController
        self.structureBrowserController = attributes.structureBrowserController
        self.ChangeSignalConnection(connect=True)
        self.AddHeader()
        self.addCont = AddProfileCont(parent=self, padTop=4, controller=self.allStructuresProfileController, padBottom=2, height=32)
        self.scroll = Scroll(name='structureProfileScroll', parent=self, padTop=2)
        self.scroll.multiSelect = False
        self.LoadProfileList()

    def ChangeSignalConnection(self, connect = True):
        signalAndCallback = [(self.allStructuresProfileController.on_profile_saved, self.OnProfileSaved), (self.structureBrowserController.on_profile_deleted, self.OnProfileDeleted)]
        ChangeSignalConnect(signalAndCallback, connect)

    def AddHeader(self):
        headerCont = Container(name='headerCont', parent=self, align=uiconst.TOTOP, height=32, clipChildren=True)
        fill = FillThemeColored(parent=headerCont, padBottom=1, colorType=uiconst.COLORTYPE_UIHEADER)
        text = GetByLabel('UI/StructureProfiles/StructureProfiles')
        label = EveLabelMedium(text=text, parent=headerCont, left=8, top=0, state=uiconst.UI_DISABLED, maxLines=1, align=uiconst.CENTERLEFT, bold=True)
        left = label.left + label.textwidth + 4
        helpIcon = MoreInfoIcon(parent=headerCont, hint=GetByLabel(self.explanationLabelPath), left=left, top=2)

    def LoadProfileList(self):
        selectedProfileID = self.structureBrowserController.GetSelectedProfileID()
        profileControllers = self.allStructuresProfileController.GetProfiles()
        scrollList = []
        for profileID, eachProfileController in profileControllers.iteritems():
            nodeData = Bunch(decoClass=StructureProfileEntry, profileController=eachProfileController, allStructuresProfileController=self.allStructuresProfileController, structureBrowserController=self.structureBrowserController, isSelected=profileID == selectedProfileID)
            sortValue = eachProfileController.GetProfileName().lower()
            scrollList.append((sortValue, nodeData))

        scrollList = SortListOfTuples(scrollList)
        anyProfileText = GetByLabel('UI/Structures/Browser/AnyProfile')
        anyProfileDesc = GetByLabel('UI/StructureProfiles/AnyProfileDesc')
        controllerForShowAll = SlimStructureAllProfilesController(ALL_PROFILES, profileData=KeyVal(name=anyProfileText, description=anyProfileDesc))
        nodeData = Bunch(decoClass=StructureAllProfilesEntry, profileController=controllerForShowAll, allStructuresProfileController=self.allStructuresProfileController, structureBrowserController=self.structureBrowserController, isSelected=ALL_PROFILES == selectedProfileID)
        scrollList.insert(0, nodeData)
        self.scroll.Load(contentList=scrollList)

    def OnProfileSaved(self, profileID):
        self.LoadProfileList()

    def OnProfileDeleted(self, profileID, selectedProfileChanged):
        self.LoadProfileList()

    def Close(self):
        try:
            self.ChangeSignalConnection(connect=False)
        except Exception as e:
            log.LogError('Failed at closing struture profile, e = ', e)
        finally:
            Container.Close(self)


class AddProfileCont(AddCont):
    default_name = 'AddGroupCont'
    tooltipPath = 'UI/Structures/AccessGroups/CreateNewGroup'

    def ApplyAttributes(self, attributes):
        AddCont.ApplyAttributes(self, attributes)
        self.createNewLabel.text = GetByLabel('UI/StructureProfiles/NewProfile')

    def OnAddEntry(self, *args):
        CreateProfileWnd.Open(controller=self.controller)
