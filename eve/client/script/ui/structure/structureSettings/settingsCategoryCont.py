#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\structure\structureSettings\settingsCategoryCont.py
from carbonui.control.scrollContainer import ScrollContainer
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from eve.client.script.ui.control.eveLabel import EveCaptionSmall
from carbonui.primitives.sprite import Sprite
import carbonui.const as uiconst
from eve.client.script.ui.control.themeColored import FillThemeColored
from eve.client.script.ui.structure import ChangeSignalConnect
from eve.client.script.ui.structure.structureSettings import AreGroupNodes
from eve.client.script.ui.structure.structureSettings.settingSection import SettingSection
from localization import GetByLabel
import structures

class SettingsCategoryCont(Container):
    __notifyevents__ = ['OnExternalDragInitiated', 'OnExternalDragEnded']

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.structureProfileController = attributes.structureProfileController
        self.structureBrowserController = attributes.structureBrowserController
        self.ChangeSignalConnection(connect=True)
        self.categoryID = self.structureBrowserController.GetSelectedCategory()
        self.categoryTypeCont = CategoryTypeCont(parent=self)
        self.settingsParent = ScrollContainer(parent=self, name='profileParent', align=uiconst.TOALL)
        self.fillUnderlay = FillThemeColored(bgParent=self.settingsParent, colorType=uiconst.COLORTYPE_UIBASECONTRAST)
        self.settingSections = []
        self.LoadCurrentCategory()
        self.draggingNodes = False
        sm.RegisterNotify(self)

    def ChangeSignalConnection(self, connect = True):
        signalAndCallback = [(self.structureBrowserController.on_category_selected, self.LoadCategorySettings)]
        ChangeSignalConnect(signalAndCallback, connect)

    def SetCurrentCategoryID(self, categoryID):
        self.categoryID = categoryID

    def LoadCategorySettings(self, categoryID):
        self.SetCurrentCategoryID(categoryID)
        self.LoadCurrentCategory()

    def LoadCurrentCategory(self):
        self.categoryTypeCont.SetCategoryName(self.categoryID)
        settingsForCategory = structures.SETTINGS_BY_CATEGORY[self.categoryID]
        self.settingsParent.Flush()
        self.settingSections = []
        settingsCont = ContainerAutoSize(parent=self.settingsParent, name='settingsCont', align=uiconst.TOTOP)
        for settingID in settingsForCategory:
            s = SettingSection(parent=settingsCont, align=uiconst.TOTOP, structureProfileController=self.structureProfileController, settingID=settingID)
            self.settingSections.append(s)

    def OnExternalDragInitiated(self, dragSource, dragData):
        if AreGroupNodes(dragData):
            self.draggingNodes = True
            self._DragChanged(initiated=True)

    def OnExternalDragEnded(self):
        if self.draggingNodes:
            self._DragChanged(initiated=False)
        self.draggingNodes = False

    def _DragChanged(self, initiated):
        for s in self.settingSections:
            s.DragChanged(initiated)

    def Close(self):
        self.settingSections = []
        self.ChangeSignalConnection(connect=False)
        self.structureProfileController = None
        self.structureBrowserController = None
        Container.Close(self)


class CategoryTypeCont(Container):
    default_align = uiconst.TOTOP
    default_height = 32

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.categorySprite = Sprite(parent=self, name='profileTypeSprite', align=uiconst.CENTERLEFT, pos=(0, 0, 26, 26))
        self.categoryNameLabel = EveCaptionSmall(name='groupName', parent=self, padLeft=32, align=uiconst.CENTERLEFT)

    def SetCategoryName(self, categoryID):
        categoryNamePath = structures.CATEGORY_LABELS[categoryID]
        self.categoryNameLabel.text = GetByLabel(categoryNamePath)
        texturePath = structures.CATEGORY_TEXTURES[categoryID]
        self.categorySprite.SetTexturePath(texturePath=texturePath)
