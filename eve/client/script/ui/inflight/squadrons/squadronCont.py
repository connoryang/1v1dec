#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\inflight\squadrons\squadronCont.py
from math import pi
from carbon.common.script.util.timerstuff import AutoTimer
from carbonui.primitives.container import Container
import carbonui.const as uiconst
from carbonui.primitives.frame import Frame
from carbonui.primitives.sprite import Sprite
from carbonui.util.color import Color
import const
from eve.client.script.ui.control.eveLabel import EveLabelSmall
from eve.client.script.ui.control.gaugeCircular import GaugeCircular
from eve.client.script.ui.inflight.overview import KILOMETERS10, KILOMETERS10000000
from eve.client.script.ui.inflight.squadrons.fightersHealthGaugeCont import FightersHealthGauge
from eve.client.script.ui.inflight.squadrons.squadronController import SquadronController
from eve.client.script.ui.inflight.squadrons.squadronManagementCont import SquadronNumber
from eve.common.script.mgt.fighterConst import COLOR_OPEN, LABEL_BY_STATE, TUBE_STATE_EMPTY
from localization import GetByLabel
import localization
import uthread2

class SquadronCont(Container):
    default_width = 86
    default_height = 116
    default_align = uiconst.TOPLEFT

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.controller = attributes.controller
        tubeFlagID = attributes.tubeFlagID
        textCont = Container(parent=self, align=uiconst.TOBOTTOM, top=10, height=30)
        self.squadronNumber = SquadronNumber(parent=self, top=1, left=1)
        self.squadronNumber.SetColor(False)
        self.squadronNumber.SetText(tubeFlagID)
        self.fighterHealthCont = FightersHealthGauge(parent=self, align=uiconst.TOTOP, height=86, tubeFlagID=tubeFlagID)
        self.OnMouseEnter = self.fighterHealthCont.OnMouseEnter
        self.OnMouseExit = self.fighterHealthCont.OnMouseExit
        self.selectHilight = Container(name='navSelectHilight', parent=self.fighterHealthCont, align=uiconst.CENTER, state=uiconst.UI_DISABLED, width=86, height=86)
        self.ringSprite = Sprite(bgParent=self.selectHilight, texturePath='res:/UI/Texture/classes/ShipUI/Fighters/selectionRing.png')
        self.bracketSprite = Sprite(bgParent=self.selectHilight, texturePath='res:/UI/Texture/classes/ShipUI/Fighters/selectionBracket.png')
        self.selectHilight.display = False
        self.loadingGauge = GaugeCircular(parent=self, radius=26, align=uiconst.CENTER, colorStart=Color.GRAY3, colorEnd=Color.GRAY3, colorBg=Color.BLACK, lineWidth=2.5, state=uiconst.UI_DISABLED, showMarker=True, top=-15, idx=0, startAngle=pi / 2)
        self.loadingGauge.display = False
        self.actionLabel = SquadronActionLabel(parent=textCont, align=uiconst.CENTERTOP, top=2)
        self.speedLabel = SquadronInfoLabel(parent=textCont, align=uiconst.CENTERBOTTOM, top=2)
        if self.controller.GetIsInSpace(tubeFlagID):
            self.SetSquadronInfo(tubeFlagID)
        self.SetSquadronAction(tubeFlagID)
        self.damageTimer = AutoTimer(1000, self.UpdateDamage)

    def SetSquadronInfo(self, tubeFlagID):
        self.speedLabel.SetSquadronInfo(tubeFlagID)

    def StopSquadronTimer(self):
        self.speedLabel.text = ''
        self.speedLabel.StopLooping()

    def SetSquadronAction(self, tubeFlagID):
        self.actionLabel.SetSquadronAction(tubeFlagID)

    def SetNewSquadron(self, fighterItemID, typeID, squadronSize):
        self.fighterItemID = fighterItemID
        self.fighterHealthCont.LoadFighterToSquadron(typeID)
        self.fighterHealthCont.SetSquadronSize(squadronSize)
        self.hint = self.fighterHealthCont.hint

    def ClearFighters(self):
        self.fighterHealthCont.ClearFighters()

    def GetFighterItemID(self):
        return self.fighterItemID

    def UpdateDamage(self):
        bp = sm.GetService('michelle').GetBallpark()
        if bp is None:
            return
        damageState = bp.GetDamageState(self.fighterItemID)
        if damageState is not None:
            shieldDamage = damageState[0]
            self.fighterHealthCont.UpdateFighters(damage=shieldDamage)
            self.hint = self.fighterHealthCont.hint

    def ShowSelectionHilite(self):
        if self.selectHilight.display:
            return
        self.selectHilight.display = True
        self.ringSprite.opacity = 0.2
        self.bracketSprite.opacity = 3.0
        uicore.animations.FadeTo(self.ringSprite, self.ringSprite.opacity, 1.0, duration=0.2)
        uicore.animations.FadeTo(self.bracketSprite, self.bracketSprite.opacity, 1.0, duration=0.2)

    def HideSelectionHilite(self):
        self.selectHilight.display = False

    def _OnClose(self, *args):
        self.damageTimer = None
        Container._OnClose(self, args)


class SquadronContEmpty(Container):
    default_width = 86
    default_height = 116
    default_align = uiconst.TOPLEFT
    default_state = uiconst.UI_NORMAL

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.controller = attributes.controller
        tubeFlagID = attributes.tubeFlagID
        textCont = Container(parent=self, align=uiconst.TOBOTTOM, height=30, top=10)
        self.squadronNumber = SquadronNumber(parent=self, top=1, left=1)
        self.squadronNumber.SetColor(True)
        self.squadronNumber.SetText(tubeFlagID)
        self.actionLabel = SquadronActionLabel(parent=textCont, align=uiconst.CENTERTOP, top=2)
        self.fighterCont = Container(parent=self, align=uiconst.TOTOP, height=86, state=uiconst.UI_DISABLED)
        Sprite(parent=self.fighterCont, texturePath='res:/UI/Texture/classes/ShipUI/Fighters/fighterItemEmpty_Up.png', align=uiconst.CENTER, height=86, width=86)
        self.hilite = Sprite(parent=self.fighterCont, name='hilite', texturePath='res:/UI/Texture/classes/ShipUI/Fighters/fighterItemEmpty_Over.png', align=uiconst.CENTER, height=86, width=86)
        self.hilite.display = False
        self.actionLabel.text = GetByLabel(LABEL_BY_STATE[TUBE_STATE_EMPTY])
        self.actionLabel.SetTextColor(COLOR_OPEN)

    def OnMouseEnter(self, *args):
        self.hilite.display = True

    def OnMouseExit(self, *args):
        self.hilite.display = False


class SquadronActionLabel(EveLabelSmall):

    def ApplyAttributes(self, attributes):
        EveLabelSmall.ApplyAttributes(self, attributes)
        self.controller = SquadronController()

    def SetSquadronAction(self, tubeFlagID):
        action, color = self.controller.GetSquadronAction(tubeFlagID)
        self.text = GetByLabel(action)
        self.SetTextColor(color.GetRGBA())


class SquadronInfoLabel(EveLabelSmall):

    def ApplyAttributes(self, attributes):
        EveLabelSmall.ApplyAttributes(self, attributes)
        self._keepLooping = False
        self.controller = SquadronController()

    def SetSquadronInfo(self, tubeFlagID):
        if self._keepLooping:
            return
        self._keepLooping = True
        uthread2.StartTasklet(self.LoopText, tubeFlagID)

    def LoopText(self, tubeFlagID):
        isVelocity = False
        while self._keepLooping:
            if isVelocity:
                self.text = self.GetDistanceText(tubeFlagID)
            else:
                self.text = self.GetVelocityText(tubeFlagID)
            isVelocity = not isVelocity
            uthread2.Sleep(3)

    def StopLooping(self):
        self._keepLooping = False

    def GetDistanceText(self, tubeFlagID):
        distance = self.controller.GetSquadronDistance(tubeFlagID)
        if distance is None:
            return GetByLabel('UI/Generic/Unknown')
        return self.FormatDistance(distance)

    def GetVelocityText(self, tubeFlagID):
        velocity = self.controller.GetSquadronVelocity(tubeFlagID)
        if velocity is None:
            return GetByLabel('UI/Generic/Unknown')
        return GetByLabel('UI/Inflight/MetersPerSecond', speed=int(velocity))

    def FormatVelocity(self, velocity):
        if velocity is None or velocity == '':
            return u''
        velocity = localization.formatters.FormatNumeric(int(velocity), useGrouping=True)
        return velocity

    def FormatDistance(self, distance):
        if distance is None or distance == '':
            return u''
        formatFunc = localization.formatters.FormatNumeric
        distance = max(0, distance)
        if distance < KILOMETERS10:
            currentDist = int(distance)
            distance = GetByLabel('/Carbon/UI/Common/FormatDistance/fmtDistInMeters', distance=formatFunc(currentDist, useGrouping=True))
        elif distance < KILOMETERS10000000:
            currentDist = long(distance / 1000)
            distance = GetByLabel('/Carbon/UI/Common/FormatDistance/fmtDistInKiloMeters', distance=formatFunc(currentDist, useGrouping=True))
        else:
            currentDist = round(distance / const.AU, 1)
            distance = GetByLabel('/Carbon/UI/Common/FormatDistance/fmtDistInAU', distance=formatFunc(currentDist, useGrouping=True, decimalPlaces=1))
        return distance or u''

    def _OnClose(self, *args, **kw):
        self.StopLooping()
        EveLabelSmall._OnClose(self, args, kw)
