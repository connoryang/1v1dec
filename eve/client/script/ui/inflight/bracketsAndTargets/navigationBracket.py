#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\inflight\bracketsAndTargets\navigationBracket.py
from carbonui.primitives.container import Container
from carbonui.primitives.sprite import Sprite
from eve.client.script.parklife import states
from eve.client.script.ui.inflight.bracketsAndTargets.inSpaceBracket import InSpaceBracket
from eve.client.script.ui.services.menuSvcExtras import movementFunctions
import carbonui.const as uiconst

class NavigationBracket(InSpaceBracket):

    def ApplyAttributes(self, attributes):
        InSpaceBracket.ApplyAttributes(self, attributes)
        self.navSelectHilight = Container(name='navSelectHilight', parent=self, align=uiconst.CENTER, state=uiconst.UI_DISABLED, width=86, height=86)
        self.ringSprite = Sprite(bgParent=self.navSelectHilight, texturePath='res:/UI/Texture/classes/ShipUI/Fighters/selectionRingInSpace.png')
        self.bracketSprite = Sprite(bgParent=self.navSelectHilight, texturePath='res:/UI/Texture/classes/ShipUI/Fighters/selectionBracketInSpace.png')
        isSelected = self.itemID in movementFunctions.GetFightersSelectedForNavigation()
        self.navSelectHilight.display = isSelected

    def OnStateChange(self, itemID, flag, status, *args):
        InSpaceBracket.OnStateChange(self, itemID, flag, status, *args)
        if flag == states.selectedForNavigation and itemID == self.itemID:
            if status:
                self.ShowNavigationHilite()
            else:
                self.HideNavigationHilite()

    def ShowNavigationHilite(self):
        if self.navSelectHilight.display:
            return
        self.navSelectHilight.display = True
        self.ringSprite.opacity = 0.2
        self.bracketSprite.opacity = 3.0
        uicore.animations.FadeTo(self.ringSprite, self.ringSprite.opacity, 1.0, duration=0.2)
        uicore.animations.FadeTo(self.bracketSprite, self.bracketSprite.opacity, 1.0, duration=0.2)

    def HideNavigationHilite(self):
        self.navSelectHilight.display = False

    def OnTacticalItemClick(self):
        if uicore.uilib.Key(uiconst.VK_CONTROL):
            movementFunctions.ToggleSelectForNavigation(self.itemID)
        else:
            InSpaceBracket.OnTacticalItemClick(self)

    def OnClickSelect(self):
        if not uicore.uilib.Key(uiconst.VK_CONTROL) and not uicore.cmd.IsCombatCommandLoaded('CmdApproachItem'):
            InSpaceBracket.OnClickSelect(self)
