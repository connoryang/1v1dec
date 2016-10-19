#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\dockedUI\lobbyToggleButtonGroupButton.py
from eve.client.script.ui.control.buttons import ToggleButtonGroupButton
import carbonui.const as uiconst

class LobbyToggleButtonGroupButton(ToggleButtonGroupButton):

    @apply
    def displayRect():
        fget = ToggleButtonGroupButton.displayRect.fget

        def fset(self, value):
            ToggleButtonGroupButton.displayRect.fset(self, value)
            self.label.width = uicore.ReverseScaleDpi(self.displayWidth) - 6
            buttonHeight = uicore.ReverseScaleDpi(self.displayHeight)
            if self.label.textheight < buttonHeight:
                self.label.top = (buttonHeight - self.label.textheight) / 2
                self.label.align = uiconst.CENTERTOP
            else:
                self.label.top = 0
                self.label.align = uiconst.CENTER

        return property(**locals())
