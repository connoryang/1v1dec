#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\dockedUI\modeBtn.py
from carbonui.primitives.container import Container
import carbonui.const as uiconst
from carbonui.primitives.sprite import Sprite
from eve.client.script.ui.control.buttons import ButtonIcon
from eve.client.script.ui.control.eveLabel import EveLabelMedium
from eve.client.script.ui.shared.dockedUI.inControlCont import PlayerInControlCont
COLOR_UNDOCK = (0.75, 0.6, 0.0, 1.0)
COLOR_DOCKED_MODE = (0.0, 0.713, 0.75, 1.0)
COLOR_TAKE_CONTROL = (172 / 255.0,
 84 / 255.0,
 40 / 255.0,
 1.0)
GLOW_COLOR_1 = (0.8, 0.8, 0.1, 0.3)
GLOW_COLOR_2 = (1.0, 1.0, 0.8, 0.2)

class LobbyBtnBase(Container):
    default_state = uiconst.UI_PICKCHILDREN
    default_align = uiconst.TOLEFT_PROP
    default_width = 0.33
    arrowColor = COLOR_DOCKED_MODE
    spriteContWidth = 64
    spriteContHeight = 34
    MOUSE_ENTER_COLOR = (0.8, 1, 1)

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.onClickFunc = attributes.callback
        self.isMouseOverDisabledFunc = attributes.isMouseOverDisabledFunc
        self.enabled = True
        self.spriteCont = Container(name='spriteCont', align=uiconst.CENTERTOP, pos=(0,
         0,
         self.spriteContWidth,
         self.spriteContHeight), parent=self, state=uiconst.UI_NORMAL)
        self.spriteCont.OnMouseEnter = self.OnMouseEnterArrow
        self.spriteCont.OnMouseExit = self.OnMouseExitArrow
        self.spriteCont.OnClick = self.OnSpriteClicked
        self.arrowSprites = []
        self.AddArrowSprites(self.spriteContHeight, self.spriteContWidth)
        self.btnLabel = EveLabelMedium(parent=self, align=uiconst.TOTOP_NOPUSH, top=8 + self.spriteContHeight)

    def AddArrowSprites(self, height, width):
        pass

    def AnimateBtnSprites(self, endColor):
        if self.isMouseOverDisabledFunc and self.isMouseOverDisabledFunc():
            return
        for i, s in enumerate(self.arrowSprites):
            uicore.animations.SpColorMorphTo(s, startColor=(s.color.r, s.color.g, s.color.b), endColor=endColor, duration=0.1)

    def OnMouseEnterArrow(self, *args):
        if self.enabled:
            self.AnimateBtnSprites(self.MOUSE_ENTER_COLOR)

    def OnMouseExitArrow(self, *args):
        if self.enabled:
            self.AnimateBtnSprites(self.arrowColor[:3])

    def OnSpriteClicked(self, *args):
        if not self.CanClickBtn():
            return
        self.OnMouseExitArrow()
        for i, s in enumerate(self.arrowSprites):
            uicore.animations.SpGlowFadeIn(s, glowColor=GLOW_COLOR_1, glowExpand=1, loops=1, duration=1.0, curveType=uiconst.ANIM_WAVE, timeOffset=i * 0.1)

        self.onClickFunc()

    def CanClickBtn(self):
        return bool(self.onClickFunc and self.enabled)

    def SetBtnLabel(self, text):
        self.btnLabel.text = '<center>%s</center>' % text

    def SetBtnHint(self, hint):
        self.spriteCont.hint = hint

    def AdjustBtnHeight(self):
        self.height = self.spriteCont.height + self.btnLabel.height + 6

    def EnableBtn(self):
        self.enabled = True
        self.spriteCont.opacity = 1.0

    def DisableBtn(self):
        self.enabled = False
        self.spriteCont.opacity = 0.2

    def LockBtn(self):
        self.opacity = 0.5
        self.state = uiconst.UI_DISABLED

    def UnlockBtn(self):
        self.opacity = 1.0
        self.state = uiconst.UI_PICKCHILDREN

    def AnimateArrow(self, arrowIdx):
        arrow = self.arrowSprites[arrowIdx]
        uicore.animations.SpGlowFadeIn(arrow, glowColor=GLOW_COLOR_2, glowExpand=1, loops=1, duration=0.2)

    def StartConfirmedAnimation(self):
        for i, s in enumerate(self.arrowSprites):
            uicore.animations.StopAllAnimations(s)
            s.glowColor = (0, 0, 0, 0)
            uicore.animations.SpColorMorphTo(s, startColor=(1, 0.8, 0), endColor=(1, 0, 0), loops=1000, duration=1, curveType=uiconst.ANIM_WAVE, timeOffset=i * 0.1 - 0.5, includeAlpha=False)
            uicore.animations.SpGlowFadeIn(s, glowColor=GLOW_COLOR_2, glowExpand=1, loops=1000, duration=1, curveType=uiconst.ANIM_WAVE, timeOffset=i * 0.1)


class DockedModeBtn(LobbyBtnBase):
    isLeftBtn = True

    def AddArrowSprites(self, height, width):
        w = -width if self.isLeftBtn else width
        for i in xrange(3):
            texturePath = 'res:/UI/Texture/classes/Lobby/%s.png' % (i + 1)
            s = Sprite(parent=self.spriteCont, texturePath=texturePath, align=uiconst.CENTERTOP, pos=(0,
             0,
             w,
             height), state=uiconst.UI_DISABLED)
            s.SetRGB(*self.arrowColor)
            self.arrowSprites.append(s)


class UndockBtn(DockedModeBtn):
    isLeftBtn = False
    arrowColor = COLOR_UNDOCK
    MOUSE_ENTER_COLOR = (1, 1, 0.8)

    def ApplyAttributes(self, attributes):
        DockedModeBtn.ApplyAttributes(self, attributes)


class ControlBtn(LobbyBtnBase):
    default_name = 'controlBtn'
    default_align = uiconst.TOLEFT_PROP
    default_width = 0.33
    default_height = 30
    arrowColor = COLOR_TAKE_CONTROL
    MOUSE_ENTER_COLOR = (1, 200 / 255.0, 190 / 255.0)

    def AddArrowSprites(self, height, width):
        texturePath = 'res:/UI/Texture/classes/Lobby/takeControl2.png'
        self.spriteCont.left = 0
        s = Sprite(parent=self.spriteCont, texturePath=texturePath, align=uiconst.CENTER, pos=(0, 0, 35, 30), state=uiconst.UI_DISABLED)
        s.SetRGB(*self.arrowColor)
        self.arrowSprites.append(s)

    def CanClickBtn(self):
        return bool(self.onClickFunc)
