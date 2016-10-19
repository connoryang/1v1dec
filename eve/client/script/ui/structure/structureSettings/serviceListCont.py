#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\structure\structureSettings\serviceListCont.py
from carbonui.primitives.container import Container
from carbonui.primitives.flowcontainer import FlowContainer, CONTENT_ALIGN_CENTER, CONTENT_ALIGN_RIGHT, CONTENT_ALIGN_LEFT
from eve.client.script.ui.control.buttons import ToggleButtonGroupButton
import carbonui.const as uiconst
from eve.client.script.ui.structure import ChangeSignalConnect
from localization import GetByLabel
import structures

class ServiceListCont(Container):
    default_align = uiconst.TORIGHT
    default_padBottom = 8
    default_padTop = 0
    default_width = 48
    default_clipChildren = True

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.SetController(attributes.structureBrowserController)

    def SetController(self, controller):
        self.structureBrowserController = controller
        self.ChangeSignalConnection(connect=True)
        self.LoadList()

    def ChangeSignalConnection(self, connect = True):
        signalAndCallback = [(self.structureBrowserController.on_category_selected, self.OnCategorySelected)]
        ChangeSignalConnect(signalAndCallback, connect)

    def LoadList(self):
        self.Flush()
        self.AddHullButtons()
        Container(parent=self, name='push', pos=(0, 0, 20, 20), align=uiconst.NOALIGN)
        self.AddSerivceModuleButtons()

    def AddHullButtons(self):
        for categoryID in structures.CATEGORIES_HULL:
            self.AddButton(categoryID, color=None)

    def AddSerivceModuleButtons(self):
        usedCat, unusedCat = self.GetModuleCategories()
        usedCat.sort(key=lambda x: (self.GetCategoryNamePath(x) if x else None))
        for categoryID in usedCat:
            self.AddButton(categoryID, color=(0.4, 0.4, 0.4, 0.1))

        if unusedCat:
            pass

    def GetCategoryNamePath(self, categoryID):
        categoryNamePath = structures.CATEGORY_LABELS.get(categoryID, None)
        return categoryNamePath

    def AddButton(self, categoryID, color):
        categoryNamePath = self.GetCategoryNamePath(categoryID)
        if categoryNamePath is None:
            return
        iconPath = structures.CATEGORY_TEXTURES.get(categoryID, None)
        btn = ServiceToggleButton(name='Button_%s' % categoryID, parent=self, controller=self.structureBrowserController, btnID=categoryID, iconPath=iconPath, hint=GetByLabel(categoryNamePath), colorSelected=color, categoryID=categoryID)
        if categoryID == self.structureBrowserController.GetSelectedCategory():
            btn.SetSelected(animate=False)
        return btn

    def LoadCategory(self, categoryID, *args):
        self.structureBrowserController.SelectCategory(categoryID)

    def OnCategorySelected(self, *args):
        pass

    def SortScrollList(self, scrollList):
        return sorted(scrollList, key=lambda x: x.sort_sortValue)

    def GetModuleCategories(self):
        usedCat = []
        unusedCat = []
        for catID in structures.CATEGORIES_MODULES:
            usedCat.append(catID)

        return (usedCat, unusedCat)

    def Close(self):
        self.ChangeSignalConnection(connect=False)
        FlowContainer.Close(self)


class ServiceToggleButton(ToggleButtonGroupButton):
    default_height = 38
    default_width = 48
    default_iconSize = 26
    default_align = uiconst.TOTOP
    default_showBg = False

    def ApplyAttributes(self, attributes):
        ToggleButtonGroupButton.ApplyAttributes(self, attributes)
        self.controller = self.controller
        self.ChangeSignalConnection(connect=True)
        self.categoryID = attributes.categoryID

    def ChangeSignalConnection(self, connect = True):
        signalAndCallback = [(self.controller.on_category_selected, self.OnCategorySelected)]
        ChangeSignalConnect(signalAndCallback, connect)

    def OnClick(self, *args):
        if not self.isDisabled:
            self.controller.SelectCategory(self.categoryID)

    def OnCategorySelected(self, categoryID):
        if categoryID == self.categoryID:
            self.SetSelected()
        else:
            self.SetDeselected()

    def Close(self):
        self.ChangeSignalConnection(connect=False)
        ToggleButtonGroupButton.Close(self)
