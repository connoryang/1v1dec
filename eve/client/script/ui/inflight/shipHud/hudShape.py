#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\inflight\shipHud\hudShape.py
from carbonui.primitives.container import Container
from carbonui.primitives.sprite import Sprite
import carbonui.const as uiconst
import trinity
from eve.client.script.ui.control.themeColored import SpriteThemeColored
SIZE = 160

class HUDShape(Container):
    default_width = SIZE
    default_height = SIZE
    default_name = 'HUDShape'
    dotTexturePath = 'res:/UI/Texture/classes/ShipUI/mainDOT.png'
    mainTexturePath = 'res:/UI/Texture/classes/ShipUI/mainUnderlay.png'

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        Sprite(parent=self, name='mainDot', pos=(0,
         0,
         SIZE,
         SIZE), align=uiconst.CENTER, state=uiconst.UI_DISABLED, texturePath=self.dotTexturePath, spriteEffect=trinity.TR2_SFX_DOT, blendMode=trinity.TR2_SBM_ADD)
        self.shipuiMainShape = SpriteThemeColored(parent=self, name='shipuiMainShape', pos=(0,
         0,
         SIZE,
         SIZE), align=uiconst.CENTER, state=uiconst.UI_DISABLED, texturePath=self.mainTexturePath, opacity=1.0, colorType=uiconst.COLORTYPE_UIBASE)


class StructureHUDShape(HUDShape):
    dotTexturePath = 'res:/UI/Texture/classes/ShipUI/mainDOT.png'
    mainTexturePath = 'res:/UI/Texture/classes/ShipUI/mainUnderlay.png'
