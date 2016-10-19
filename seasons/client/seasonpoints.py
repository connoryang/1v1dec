#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\seasons\client\seasonpoints.py
import carbonui.const as uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.sprite import Sprite
from eve.client.script.ui.control.eveLabel import EveLabelSmallBold
from seasons.client.const import SEASON_POINTS_ICON_PATH, get_points_label_text
from seasons.client.uiutils import SEASON_THEME_TEXT_COLOR_HIGHLIGHTED
DEFAULT_SEASON_POINTS_SIZE = 24
DEFAULT_REWARD_LABEL_CLASS = EveLabelSmallBold
DEFAULT_REWARD_LABEL_PADLEFT = 2
DEFAULT_ON_CLICK_FUNCTION = None
REWARD_LABEL_WIDTH = 50

class SeasonPoints(Container):

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        reward_label_class = attributes.Get('reward_label_class', DEFAULT_REWARD_LABEL_CLASS)
        reward_label_fontsize = attributes.Get('reward_label_fontsize', None)
        reward_label_padLeft = attributes.Get('reward_label_padLeft', DEFAULT_REWARD_LABEL_PADLEFT)
        season_points_size = attributes.Get('season_points_size', DEFAULT_SEASON_POINTS_SIZE)
        on_click_function = attributes.Get('on_click_function', DEFAULT_ON_CLICK_FUNCTION)
        self.reward_icon_container = Container(name='reward_icon_container', parent=self, align=uiconst.CENTERLEFT, width=season_points_size, height=season_points_size)
        reward_icon = Sprite(name='reward_icon', parent=self.reward_icon_container, align=uiconst.TOALL, texturePath=SEASON_POINTS_ICON_PATH)
        reward_label_container = Container(name='reward_label_container', parent=self, align=uiconst.CENTERLEFT, width=REWARD_LABEL_WIDTH, height=season_points_size, left=season_points_size)
        self.reward_label = reward_label_class(name='reward_label', text='', bold=True, parent=reward_label_container, align=uiconst.CENTERLEFT, padLeft=reward_label_padLeft)
        self.reward_label.color = SEASON_THEME_TEXT_COLOR_HIGHLIGHTED
        if reward_label_fontsize:
            self.reward_label.fontsize = reward_label_fontsize
        self.update_points(attributes.points)
        if on_click_function:
            reward_icon.onClick = on_click_function
            self.reward_label.onClick = on_click_function

    def update_points(self, points):
        self.points = points
        self.reward_label.text = get_points_label_text(self.points)
        self.width = self.reward_icon_container.width + self.reward_label.width
