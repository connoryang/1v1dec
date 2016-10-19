#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\inflight\squadrons\fightersHealthGaugeCont.py
from math import cos, sin
from carbonui.primitives.container import Container
from carbonui.primitives.sprite import Sprite
from carbonui.primitives.vectorlinetrace import VectorLineTrace
from eve.client.script.ui.control.eveIcon import Icon
from eve.client.script.ui.inflight.squadrons.shipFighterState import GetShipFighterState
from eve.common.script.mgt.fighterConst import HEALTHY_FIGHTER_SPACE, DAMAGED_FIGHTER, DEAD_FIGHTER, HINTTEXT_BY_ROLE, TUBE_STATES_INSPACE, HEALTHY_FIGHTER_TUBE
import evetypes
from fighters.client import GetMaxSquadronSize, GetSquadronSizeFromSlimItem, GetSquadronRoleResPath, GetSquadronRole
from localization import GetByLabel
import mathUtil
import trinity
import carbonui.const as uiconst
import util

class FightersHealthGauge(Container):
    default_height = 86
    default_width = 86
    default_align = uiconst.TOPLEFT
    default_state = uiconst.UI_PICKCHILDREN
    isDragObject = True

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.shipFighterState = GetShipFighterState()
        self.typeID = None
        self.squadronSize = None
        self.squadronMaxSize = None
        self.noHealthyFighters = 0
        self.squadronState = attributes.get('state', None)
        self.tubeFlagID = attributes.get('tubeFlagID', None)
        dashColors = self.GetDashColors()
        self.classIcon = Sprite(name='classIcon', parent=self, align=uiconst.CENTERBOTTOM, width=16, height=16, top=18)
        self.classIcon.OnMouseEnter = self.OnMouseEnter
        self.classIcon.OnMouseExit = self.OnMouseExit
        self.classIcon.GetDragData = self.GetDragData
        self.fightersGauge = FighterHealthGaugeLine(parent=self, dashColors=dashColors, align=uiconst.CENTER)
        Sprite(parent=self, align=uiconst.CENTER, width=86, height=86, texturePath='res:/UI/Texture/classes/ShipUI/Fighters/fighterItemOverlay.png', state=uiconst.UI_DISABLED)
        self.fighterIcon = Icon(parent=self, align=uiconst.CENTER, width=52, height=52, state=uiconst.UI_DISABLED, blendMode=1, textureSecondaryPath='res:/UI/Texture/classes/ShipUI/Fighters/fighterItemMask.png', spriteEffect=trinity.TR2_SFX_MODULATE)
        Sprite(parent=self, align=uiconst.CENTER, width=86, height=86, texturePath='res:/UI/Texture/classes/ShipUI/Fighters/fighterItemUnderlay.png', state=uiconst.UI_DISABLED)
        self.hilite = Sprite(parent=self, name='hilite', width=86, height=86, align=uiconst.CENTER, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/ShipUI/Fighters/fighterItemUnderlayOver.png')
        self.hilite.display = False

    def LoadFighterToSquadron(self, typeID):
        if typeID == self.typeID:
            return
        self.typeID = typeID
        self.fighterIcon.LoadIconByTypeID(typeID=typeID)
        self.squadronMaxSize = GetMaxSquadronSize(self.typeID)
        roleTexturePath = GetSquadronRoleResPath(self.typeID)
        self.classIcon.LoadTexture(roleTexturePath)
        hintString = HINTTEXT_BY_ROLE[GetSquadronRole(self.typeID)]
        self.classIcon.hint = GetByLabel(hintString)
        self.UpdateHint()

    def ClearFighters(self):
        self.fightersGauge.ClearFighters()

    def UpdateHint(self, damage = None):
        typeName = evetypes.GetName(self.typeID)
        if self.tubeFlagID is not None:
            tubeStatus = self.shipFighterState.GetTubeStatus(self.tubeFlagID)
            if tubeStatus.statusID not in TUBE_STATES_INSPACE:
                damage = None
        if damage and damage < 0.99:
            damageNumber = round((1.0 - damage) * 100)
            hintText = GetByLabel('UI/Inventory/Fighters/SquadronHintWithDamage', typeName=typeName, numFighters=int(self.noHealthyFighters), damagePercentage=damageNumber)
        else:
            hintText = GetByLabel('UI/Inventory/Fighters/SquadronHint', typeName=typeName, numFighters=int(self.noHealthyFighters))
        self.hint = hintText

    def SetSquadronSize(self, squadronSize):
        self.squadronSize = squadronSize
        self.UpdateFighters()

    def GetDashColors(self, damage = None):
        self.noHealthyFighters = 0
        dashColors = []
        if self.tubeFlagID is not None:
            tubeStatus = self.shipFighterState.GetTubeStatus(self.tubeFlagID)
            if tubeStatus.statusID not in TUBE_STATES_INSPACE:
                damage = None
        if not self.typeID:
            return dashColors
        for i in xrange(1, self.squadronMaxSize + 1):
            if i <= self.squadronSize:
                self.noHealthyFighters += 1
                dashColor = self.GetHealthyFighterColor()
                if damage and damage < 0.99:
                    if i == self.squadronSize:
                        dashColor = DAMAGED_FIGHTER
                        self.noHealthyFighters -= 1
            else:
                dashColor = DEAD_FIGHTER
            dashColors.append(dashColor)

        return dashColors

    def GetHealthyFighterColor(self):
        if self.tubeFlagID is None:
            return HEALTHY_FIGHTER_SPACE
        else:
            tubeStatus = self.shipFighterState.GetTubeStatus(self.tubeFlagID)
            if tubeStatus.statusID in TUBE_STATES_INSPACE:
                return HEALTHY_FIGHTER_SPACE
            return HEALTHY_FIGHTER_TUBE

    def GetDragData(self):
        if self.squadronState is not None:
            squadronData = util.KeyVal()
            squadronData.tubeFlagID = self.tubeFlagID
            squadronData.squadronState = self.squadronState
            squadronData.typeID = self.typeID
            squadronData.__guid__ = 'uicls.FightersHealthGauge'
            return [squadronData]
        else:
            return []

    def UpdateFighters(self, damage = None):
        if not self.typeID:
            return
        dashColors = self.GetDashColors(damage)
        self.fightersGauge.UpdateFighterColors(dashColors)
        self.UpdateHint(damage)

    def LoadBySlimItem(self, slimItem):
        self.LoadFighterToSquadron(slimItem.typeID)
        squadronSize = GetSquadronSizeFromSlimItem(slimItem)
        self.SetSquadronSize(squadronSize)
        self.UpdateFighters()

    def OnMouseEnter(self, *args):
        self.hilite.display = True

    def OnMouseExit(self, *args):
        self.hilite.display = False


class FighterHealthGaugeLine(VectorLineTrace):
    __notifyevents__ = ['OnUIScalingChange']
    demoCount = 0
    default_state = uiconst.UI_PICKCHILDREN

    def ApplyAttributes(self, attributes):
        VectorLineTrace.ApplyAttributes(self, attributes)
        self.dashSizeFactor = attributes.dashSizeFactor or 6.0
        self.startAngle = attributes.startAngle or mathUtil.DegToRad(138)
        self.range = attributes.range or mathUtil.DegToRad(265)
        self.radius = attributes.radius or 30
        self.lineWidth = attributes.lineWidth or 2.5
        self.gapEnds = attributes.gapEnds or True
        self.dashColors = attributes.dashColors or None
        self.PlotFighters()
        sm.RegisterNotify(self)

    def ClearFighters(self):
        self.dashColors = None
        self.Flush()

    def UpdateFighterColors(self, dashColors):
        self.dashColors = dashColors
        self.Flush()
        self.PlotFighters()

    def PlotFighters(self):
        if not self.dashColors:
            return
        dashCount = len(self.dashColors)
        circum = self.radius * self.range
        if self.gapEnds:
            gapStepRad = self.range / (dashCount * (self.dashSizeFactor + 1))
        else:
            gapStepRad = self.range / (dashCount * (self.dashSizeFactor + 1) - 1)
        dashStepRad = gapStepRad * self.dashSizeFactor
        pixelRad = self.range / circum
        centerOffset = self.radius + self.lineWidth * 0.5
        jointOffset = min(gapStepRad / 3, pixelRad / 2)
        rot = self.startAngle
        if self.gapEnds:
            rot += gapStepRad / 2
        for i, color in enumerate(self.dashColors):
            r, g, b, a = color
            point = (centerOffset + self.radius * cos(rot - jointOffset), centerOffset + self.radius * sin(rot - jointOffset))
            self.AddPoint(point, (r,
             g,
             b,
             0.0))
            point = (centerOffset + self.radius * cos(rot + jointOffset), centerOffset + self.radius * sin(rot + jointOffset))
            self.AddPoint(point, color)
            smoothRad = pixelRad * 4 + jointOffset
            while smoothRad < dashStepRad - jointOffset:
                point = (centerOffset + self.radius * cos(rot + smoothRad), centerOffset + self.radius * sin(rot + smoothRad))
                self.AddPoint(point, color)
                smoothRad += pixelRad * 4

            rot += dashStepRad
            point = (centerOffset + self.radius * cos(rot - jointOffset), centerOffset + self.radius * sin(rot - jointOffset))
            self.AddPoint(point, color)
            point = (centerOffset + self.radius * cos(rot + jointOffset), centerOffset + self.radius * sin(rot + jointOffset))
            self.AddPoint(point, (r,
             g,
             b,
             0.0))
            rot += gapStepRad

        self.width = self.height = centerOffset * 2

    def OnUIScalingChange(self, *args):
        if not self.destroyed:
            self.Flush()
            self.PlotFighters()
