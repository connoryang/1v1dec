#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\fittingGhost\ghostFittingPanels\chargeButtons.py
from carbonui.primitives.container import Container
from carbonui.primitives.fill import Fill
import carbonui.const as uiconst
from eve.client.script.ui.control.eveIcon import Icon

class ModuleChargeButton(Container):

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.hint = attributes.moduleName
        self.fill = Fill(bgParent=self, color=(1, 1, 1, 0.1))
        self.onClickFunc = attributes.onClickFunc
        self.moduleTypeID = attributes.moduleTypeID
        self.usedWithChargesIDs = attributes.usedWithChargesIDs
        icon = Icon(parent=self, name='icon', pos=(0, 0, 30, 30), align=uiconst.CENTER, state=uiconst.UI_DISABLED, typeID=self.moduleTypeID, ignoreSize=True)

    def GetModuleType(self):
        return self.moduleTypeID

    def GetMenu(self):
        return sm.GetService('menu').GetMenuFormItemIDTypeID(None, self.moduleTypeID, ignoreMarketDetails=0)

    def OnClick(self, *args):
        if self.onClickFunc:
            self.onClickFunc(self.moduleTypeID, self.usedWithChargesIDs)

    def SetSelected(self):
        self.fill.display = True

    def SetDeselected(self):
        self.fill.display = False
