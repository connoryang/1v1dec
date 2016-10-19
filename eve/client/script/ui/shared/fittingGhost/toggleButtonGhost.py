#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\fittingGhost\toggleButtonGhost.py
from carbonui.primitives.layoutGrid import LayoutGrid
from eve.client.script.ui.control.buttons import ToggleButtonGroupButton
import carbonui.const as uiconst

class ToggleButtonGhost(ToggleButtonGroupButton):

    def ConstructLayout(self, iconOpacity, iconPath, iconSize, label):
        if iconPath and label:
            contentCont = LayoutGrid(parent=self, align=uiconst.CENTER, left=-10)
            self.AddIcon(contentCont, iconOpacity, iconPath, iconSize)
            self.AddLabel(contentCont, label)
            self.icon = None
        else:
            return ToggleButtonGroupButton.ConstructLayout(self, iconOpacity, iconPath, iconSize, label)
