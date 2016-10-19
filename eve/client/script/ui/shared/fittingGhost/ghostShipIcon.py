#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\fittingGhost\ghostShipIcon.py
import inventorycommon
from carbonui.primitives.container import Container
import carbonui.const as uiconst
from carbonui.primitives.frame import Frame
from carbonui.primitives.sprite import Sprite
from carbonui.primitives.transform import Transform
import trinity
import log
from localization import GetByLabel
COLOR_BG = (0.0259, 0.0491, 0.075, 1.0)
OPACITY_NORMAL = 1.0
OPACITY_MOUSEOVER = 2.0
OPACITY_NORMAL_FRAME = 0.25
OPACITY_MOUSEOVER_FRAME = 0.45

class GhostShipIcon(Container):
    default_name = 'GhostShipIcon'
    default_align = uiconst.TOPRIGHT
    default_state = uiconst.UI_NORMAL
    isDragObject = True

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.typeID = attributes.typeID
        self.bgFrame = Frame(bgParent=self, cornerSize=10, opacity=OPACITY_NORMAL_FRAME, texturePath='res:/UI/Texture/Classes/ShipTree/groups/frameUnlocked.png')
        self.iconTransform = Transform(parent=self, align=uiconst.TOALL, scalingCenter=(0.5, 0.5))
        self.iconSprite = Sprite(name='iconSprite', parent=self.iconTransform, align=uiconst.CENTER, state=uiconst.UI_DISABLED, blendMode=trinity.TR2_SBM_ADD, pos=(0,
         0,
         self.width,
         self.width), idx=0, opacity=OPACITY_NORMAL)
        self.LoadTexturePath()

    def SetShipTypeID(self, typeID):
        self.typeID = typeID
        self.LoadTexturePath()

    def LoadTexturePath(self):
        try:
            texturePath = inventorycommon.typeHelpers.GetHoloIconPath(self.typeID)
        except AttributeError as e:
            texturePath = None
            log.LogException(e)

        self.iconSprite.SetTexturePath(texturePath)

    def OnMouseEnter(self, *args):
        uicore.animations.FadeTo(self.iconSprite, self.iconSprite.opacity, OPACITY_MOUSEOVER, duration=1.0, loops=1)
        uicore.animations.FadeTo(self.bgFrame, self.bgFrame.opacity, OPACITY_MOUSEOVER_FRAME, duration=1.0, loops=1)
        uicore.animations.Tr2DScaleTo(self.iconTransform, self.iconTransform.scale, (1.05, 1.05), duration=0.3)

    def OnMouseExit(self, *args):
        uicore.animations.FadeTo(self.iconSprite, self.iconSprite.opacity, OPACITY_NORMAL, duration=1.3)
        uicore.animations.FadeTo(self.bgFrame, self.bgFrame.opacity, OPACITY_NORMAL_FRAME, duration=1.0, loops=1)
        uicore.animations.Tr2DScaleTo(self.iconTransform, self.iconTransform.scale, (1.0, 1.0), duration=0.3)

    def GetHint(self):
        return GetByLabel('UI/Fitting/FittingWindow/SimulateMyShip', typeID=self.typeID)

    def OnClick(self, *args):
        sm.GetService('ghostFittingSvc').LoadCurrentShip()
