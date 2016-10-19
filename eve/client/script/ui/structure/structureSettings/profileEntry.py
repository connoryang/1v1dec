#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\structure\structureSettings\profileEntry.py
from carbonui import const as uiconst
import carbonui
from carbonui.primitives.fill import Fill
from eve.client.script.ui.control.buttons import ButtonIcon
from sovDashboard.sovStatusEntries import MouseInsideScrollEntry

class ProfileEntryBase(MouseInsideScrollEntry):
    default_align = uiconst.TOTOP
    default_state = uiconst.UI_NORMAL
    rightBtnTexturePath = 'res:/UI/Texture/Icons/73_16_50.png'

    def ApplyAttributes(self, attributes):
        MouseInsideScrollEntry.ApplyAttributes(self, attributes)
        self.blinkBG = None
        if self.rightBtnTexturePath:
            self.rightBtn = ButtonIcon(name='optionIcon', parent=self, align=uiconst.CENTERRIGHT, pos=(2, 0, 16, 16), iconSize=16, texturePath=self.rightBtnTexturePath, func=self.OnRightBtnClicked, opacity=0.0)
            self.rightBtn.OnMouseEnter = self.OnRightBtnMouseEnter
        else:
            self.rightBtn = None

    def OnRightBtnClicked(self, *args):
        carbonui.control.menu.ShowMenu(self)

    def OnRightBtnMouseEnter(self, *args):
        ButtonIcon.OnMouseEnter(self.rightBtn, *args)
        self.OnMouseEnter(*args)

    def OnMouseEnter(self, *args):
        MouseInsideScrollEntry.OnMouseEnter(self, *args)
        self.FadeSprites(1.0)
        self.ChangeRightContDisplay(True)

    def OnMouseNoLongerInEntry(self):
        MouseInsideScrollEntry.OnMouseNoLongerInEntry(self)
        self.FadeSprites(0.0)
        self.ChangeRightContDisplay(False)

    def FadeSprites(self, toValue):
        if self.rightBtn:
            uicore.animations.FadeTo(self.rightBtn, startVal=self.rightBtn.opacity, endVal=toValue, duration=0.1, loops=1)

    def ChangeRightContDisplay(self, show = False):
        pass

    def GetMenu(self, *args):
        pass

    def CheckConstructBlinkBG(self):
        if self.blinkBG is None:
            self.blinkBG = Fill(bgParent=self, color=(1.0, 1.0, 1.0, 0.0))
