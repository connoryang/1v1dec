#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\tacticalNavigation\navigationBracket.py
import uiprimitives
import tacticalNavigation.ui as tacticalui
import carbonui.const as uiconst
from carbonui.primitives.sprite import Sprite
NAVIGATION_BRACKET_PATH = 'res:/ui/texture/classes/bracket/selectioncircle.png'
BRACKET_SIZE = 24

class NavigationPointBracket(uiprimitives.Bracket):
    __guid__ = 'uicls.NavigationPointBracket'

    def ApplyAttributes(self, attributes):
        uiprimitives.Bracket.ApplyAttributes(self, attributes)
        color = tacticalui.ColorCombination(tacticalui.COLOR_MOVE, tacticalui.ALPHA_HIGH)
        Sprite(parent=self, width=attributes.width, height=attributes.height, texturePath=NAVIGATION_BRACKET_PATH, state=uiconst.UI_DISABLED, color=color, align=uiconst.CENTER)

    @staticmethod
    def Create(trackingCurve):
        bracket = NavigationPointBracket(parent=uicore.layer.bracket, curveSet=uicore.uilib.bracketCurveSet, align=uiconst.ABSOLUTE, width=BRACKET_SIZE, height=BRACKET_SIZE, state=uiconst.UI_DISABLED)
        bracket.trackBall = trackingCurve
        return bracket
