#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\inflight\bracketsAndTargets\targetInBarFighter.py
import random
import base
from carbonui.primitives.container import Container
from carbonui.primitives.sprite import Sprite
from eve.client.script.ui.inflight.bracketsAndTargets.targetInBar import TargetInBar
from eve.client.script.ui.inflight.squadrons.fightersHealthGaugeCont import FightersHealthGauge
from spacecomponents.client.messages import MSG_ON_TARGET_BRACKET_REMOVED, MSG_ON_TARGET_BRACKET_ADDED
import carbonui.const as uiconst

class TargetInBarFighter(TargetInBar):
    __guid__ = 'uicls.TargetInBarFighter'

    def ApplyAttributes(self, attributes):
        TargetInBar.ApplyAttributes(self, attributes)
        self.damageTimer = base.AutoTimer(random.randint(750, 1000), self.UpdateDamage)

    def AddUIObjects(self, slimItem, itemID, *args):
        self.itemID = itemID
        barAndImageCont = Container(parent=self, name='barAndImageCont', align=uiconst.TOTOP, height=100, state=uiconst.UI_NORMAL)
        self.barAndImageCont = barAndImageCont
        self.iconSize = iconSize = 94
        iconPar = Container(parent=barAndImageCont, name='iconPar', width=iconSize, height=iconSize, align=uiconst.CENTERTOP, state=uiconst.UI_DISABLED)
        self.sr.iconPar = iconPar
        self.AddUIDeathObjects(80)
        self.fightersHealthGauge = FightersHealthGauge(parent=iconPar, align=uiconst.TOTOP, height=86, top=4)
        self.fightersHealthGauge.LoadBySlimItem(slimItem)
        circle = Sprite(name='circle', align=uiconst.CENTER, parent=iconPar, width=iconSize + 2, height=iconSize + 2, texturePath='res:/UI/Texture/classes/Target/outerCircle.png', color=(1.0, 1.0, 1.0, 0.5), state=uiconst.UI_DISABLED)
        self.circle = circle
        self.UpdateDamage()
        self.barAndImageCont.hint = self.fightersHealthGauge.hint
        bp = sm.GetService('michelle').GetBallpark()
        bp.componentRegistry.SendMessageToItem(self.itemID, MSG_ON_TARGET_BRACKET_ADDED, self)

    def UpdateDamage(self):
        bp = sm.GetService('michelle').GetBallpark()
        if bp is None:
            self.sr.damageTimer = None
            return
        dmg = bp.GetDamageState(self.itemID)
        if dmg is not None:
            self.SetDamage(dmg)
            self.barAndImageCont.hint = self.fightersHealthGauge.hint

    def SetDamage(self, state, *args):
        damage = state[0]
        self.fightersHealthGauge.UpdateFighters(damage=damage)

    def SetSquadronSize(self, squadronSize):
        self.fightersHealthGauge.SetSquadronSize(squadronSize)
        self.fightersHealthGauge.UpdateFighters()

    def _OnClose(self, *args):
        bp = sm.GetService('michelle').GetBallpark()
        bp.componentRegistry.SendMessageToItem(self.itemID, MSG_ON_TARGET_BRACKET_REMOVED)
        self.damageTimer = None
        TargetInBar._OnClose(self, args)
