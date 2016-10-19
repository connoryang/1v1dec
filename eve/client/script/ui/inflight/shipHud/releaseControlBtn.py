#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\inflight\shipHud\releaseControlBtn.py
import carbonui.const as uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.sprite import Sprite
from eve.client.script.ui.control.buttons import ButtonIcon
from localization import GetByLabel
import math
MOUSE_OFF_OPACITY = 0.5
MOUSE_ON_OPACITY = 1.0
COLOR_TAKE_CONTROL = (172 / 255.0,
 84 / 255.0,
 40 / 255.0,
 1.0)

class ReleaseControlBtn(Container):
    default_name = 'ReleaseControlBtn'
    default_width = 104
    default_height = 44
    default_state = uiconst.UI_NORMAL

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.func = attributes.func
        self.itemID = attributes.itemID
        self.hintText = GetByLabel('UI/Inflight/HUDOptions/ReleaseControl')
        self.pickParent = Container(name='speedCircularPickParent', parent=self, align=uiconst.CENTERBOTTOM, pos=(0, 0, 144, 144), pickRadius=72, state=uiconst.UI_NORMAL)
        self.pickParent.OnMouseMove = self.OnMoveInPickParent
        self.pickParent.OnMouseExit = self.OnMouseExit
        self.pickParent.OnMouseEnter = self.OnMouseEnter
        self.pickParent.OnClick = self.OnClick
        self.arrowSprite = Sprite(parent=self.pickParent, name='releaseArrow', pos=(0, 0, 104, 44), align=uiconst.CENTERBOTTOM, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/ShipUI/releaseArrow.png', opacity=MOUSE_OFF_OPACITY, color=COLOR_TAKE_CONTROL)
        Sprite(parent=self.pickParent, name='buttonBody', pos=(0, 0, 104, 44), align=uiconst.CENTERBOTTOM, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/ShipUI/buttonBody.png')

    def OnMouseEnter(self, *args):
        self.OnMoveInPickParent()

    def OnMoveInPickParent(self, *args):
        isInside = self.IsInside()
        if isInside:
            hint = self.hintText
            opacity = MOUSE_ON_OPACITY
        else:
            hint = ''
            opacity = MOUSE_OFF_OPACITY
        self.hint = hint
        self.arrowSprite.opacity = opacity

    def IsInside(self):
        if uicore.uilib.GetMouseOver() != self.pickParent:
            return False
        l, t, w, h = self.pickParent.GetAbsolute()
        centerX = l + w / 2
        centerY = t + h / 2
        y = float(uicore.uilib.y - centerY)
        x = float(uicore.uilib.x - centerX)
        if x and y:
            angle = math.atan(x / y)
            deg = angle / math.pi * 180.0
            factor = (45.0 + deg) / 90.0
            if factor < 0.0 or factor > 1.0:
                return False
            return True
        return False

    def OnMouseExit(self, *args):
        self.arrowSprite.opacity = MOUSE_OFF_OPACITY
        self.hint = ''

    def OnClick(self, *args):
        if self.IsInside():
            self.func(self.itemID)
