#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\seasons\client\seasonprogressbar.py
from carbon.common.script.util.format import FmtAmt
import carbonui.const as uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.fill import Fill
from carbonui.primitives.frame import Frame
from carbonui.primitives.gradientSprite import GradientSprite
from carbonui.primitives.sprite import Sprite
from carbonui.uianimations import animations
from eve.client.script.ui.control.eveIcon import Icon
from eve.client.script.ui.control.eveLabel import EveLabelSmallBold
from eve.common.lib.appConst import defaultPadding
from seasons.client.const import REWARD_ACHIEVED_ICON_PATH, DEFAULT_ANIMATE_PROGRESS
from seasons.client.uiutils import fill_frame_background_color_for_container, SEASON_THEME_TEXT_COLOR_HIGHLIGHTED, SEASON_THEME_TEXT_COLOR_REGULAR
DEFAULT_PROGRESS_BAR_WIDTH = 550
DEFAULT_PROGRESS_BAR_HEIGHT = 40
DEFAULT_REWARD_POINTS_TOP_SETTING = False
PROGRESS_BAR_COLOR_START = (0.5, 0.5, 0.5)
PROGRESS_BAR_COLOR_END = (0.8, 0.8, 0.8)
PROGRESS_BAR_OPACITY = 0.7
PROGRESS_BAR_FRAME_OPACITY = 0.75
PROGRESS_BAR_FRAME_COLOR = (0.75, 0.75, 0.75)
PROGRESS_BAR_ANIMATION_DURATION = 1.5
REWARD_ICON_MARGIN = float(2 * defaultPadding)
DEFAULT_REWARD_ICON_MARKER_WIDTH = 2
REWARD_ICON_MARKER_HEIGHT = 1.5 * defaultPadding
REWARD_ACHIEVED_ICON_SIZE = 10
REWARD_POINTS_LABEL_WIDTH = 40
REWARD_ACHIEVEMENT_SPRITE_PADDING = 12
PROGRESS_WIDTH_TOL = 0.1
MIN_PROGRESS_WIDTH = 1.0
DEFAULT_USE_SETTINGS = False

class SeasonProgressBar(Container):
    __notifyevents__ = ['OnSeasonalGoalCompletedInClient', 'OnSeasonalPointsUpdatedInClient', 'OnSeasonalGoalsResetInClient']

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        sm.RegisterNotify(self)
        self.season_service = attributes.season_service
        animate_progress = attributes.Get('animate_progress', DEFAULT_ANIMATE_PROGRESS)
        self.use_settings_to_recover_last_progress = attributes.Get('use_settings_to_recover_last_progress', DEFAULT_USE_SETTINGS)
        self.progress_bar_height = attributes.Get('progress_bar_height', DEFAULT_PROGRESS_BAR_HEIGHT)
        self.progress_bar_max_width = attributes.Get('progress_bar_width', DEFAULT_PROGRESS_BAR_WIDTH)
        self.reward_icon_size = self.progress_bar_height - REWARD_ICON_MARGIN
        self.reward_points_label_on_top = attributes.Get('reward_points_label_on_top', DEFAULT_REWARD_POINTS_TOP_SETTING)
        self.reward_icon_marker_width = attributes.Get('reward_icon_marker_width', DEFAULT_REWARD_ICON_MARKER_WIDTH)
        self.rewards = self.season_service.get_rewards()
        self.max_season_progress = float(self.season_service.get_max_points())
        self.reward_achievement_sprites = dict()
        self.reward_points_labels = dict()
        self._construct_progress_bar(animate_progress)

    def _construct_progress_bar(self, animate_progress = True):
        self._construct_rewards()
        self._construct_progress(animate_progress)
        self._construct_frame()

    def _construct_rewards(self):
        for reward_id, reward in self.rewards.items():
            progress_x = self._calculate_progress_width_from_points(reward['points_required'])
            progress_x_padding = float(self.reward_icon_size) / 2.0 - defaultPadding
            reward_x_position_in_progress_bar = max(progress_x_padding, progress_x - progress_x_padding)
            reward_icon_container = Container(name='reward_%d_icon_container' % reward_id, parent=self, align=uiconst.CENTERLEFT, width=self.reward_icon_size, height=self.reward_icon_size, left=reward_x_position_in_progress_bar)
            self._construct_reward_points_label(reward_id, reward, reward_x_position_in_progress_bar)
            self._construct_reward_markers(reward_id, reward_x_position_in_progress_bar)
            self._construct_reward_icon(reward_id, reward, reward_icon_container)

    def _construct_reward_points_label(self, reward_id, reward, reward_x_position_in_progress_bar):
        icon_padding = float(self.reward_icon_size) / 2.0
        reward_points_label_container = Container(name='reward_%s_points_label_container' % reward_id, parent=self, align=uiconst.CENTERLEFT, width=REWARD_POINTS_LABEL_WIDTH, height=REWARD_ACHIEVED_ICON_SIZE)
        reward_points_label = EveLabelSmallBold(name='reward_%s_points_label' % reward_id, text=FmtAmt(reward['points_required']), parent=reward_points_label_container, state=uiconst.UI_NORMAL, align=uiconst.CENTERLEFT)
        reward_points_label_container_left = reward_x_position_in_progress_bar + icon_padding - float(reward_points_label.width)
        reward_points_label_container.left = reward_points_label_container_left
        reward_points_label_container_top = icon_padding + float(reward_points_label.height)
        if self.reward_points_label_on_top:
            reward_points_label_container_top = -reward_points_label_container_top
        reward_points_label_container.top = reward_points_label_container_top
        reward_achievement_sprite_left = -REWARD_ACHIEVEMENT_SPRITE_PADDING
        reward_achievement_sprite = Sprite(name='reward_%s_achieved_sprite' % reward_id, parent=reward_points_label_container, align=uiconst.CENTERLEFT, texturePath=REWARD_ACHIEVED_ICON_PATH, width=REWARD_ACHIEVED_ICON_SIZE, height=REWARD_ACHIEVED_ICON_SIZE, left=reward_achievement_sprite_left, top=-1)
        self.reward_achievement_sprites[reward_id] = reward_achievement_sprite
        self.reward_points_labels[reward_id] = reward_points_label
        self._update_reward_achievement_sprites(reward_id, reward)

    def _construct_reward_markers(self, reward_id, reward_x_position_in_progress_bar):
        marker_padding_width = float(self.reward_icon_marker_width) / 2.0
        marker_padding_height = float(REWARD_ICON_MARKER_HEIGHT) / 2.0 - defaultPadding
        icon_padding = float(self.reward_icon_size) / 2.0
        Fill(name='reward_%d_icon_marker_top' % reward_id, parent=self, align=uiconst.CENTERLEFT, width=self.reward_icon_marker_width, height=REWARD_ICON_MARKER_HEIGHT, left=reward_x_position_in_progress_bar + icon_padding - marker_padding_width, top=-icon_padding + marker_padding_height, opacity=1.0)
        Fill(name='reward_%d_icon_marker_bottom' % reward_id, parent=self, align=uiconst.CENTERLEFT, width=self.reward_icon_marker_width, height=REWARD_ICON_MARKER_HEIGHT, left=reward_x_position_in_progress_bar + icon_padding - marker_padding_width, top=icon_padding - marker_padding_height, opacity=1.0)

    def _construct_reward_icon(self, reward_id, reward, reward_icon_container):
        reward_icon = Icon(name='reward_%d_icon' % reward_id, parent=reward_icon_container, align=uiconst.TOALL, padding=defaultPadding)
        reward_icon.LoadIconByTypeID(reward['reward_type_id'])

    def _construct_progress(self, animate_progress = True):
        progress_bar_container = Container(name='progress_bar_container', parent=self, align=uiconst.CENTERLEFT, width=self.width, height=self.progress_bar_height)
        self.progress_container = Container(name='progress_container', parent=progress_bar_container, align=uiconst.TOTOP, width=self.width - REWARD_ICON_MARGIN, height=self.progress_bar_height - REWARD_ICON_MARGIN, padding=defaultPadding)
        self.progress_gradient_fill = GradientSprite(name='progress_gradient_fill', align=uiconst.CENTERLEFT, parent=self.progress_container, rgbData=((0.0, PROGRESS_BAR_COLOR_START), (1.0, PROGRESS_BAR_COLOR_END)), opacity=PROGRESS_BAR_OPACITY, width=0, height=self.progress_container.height)
        self._update_progress_bar(animate_progress)

    def _construct_frame(self):
        progress_bar_background_frame_container = Container(name='progress_bar_background_frame_container', parent=self, align=uiconst.CENTERLEFT, width=self.progress_bar_max_width, height=self.progress_bar_height)
        fill_frame_background_color_for_container(progress_bar_background_frame_container)
        Frame(name='progress_bar_background_frame', bgParent=progress_bar_background_frame_container, frameConst=uiconst.FRAME_BORDER1_CORNER0, opacity=PROGRESS_BAR_FRAME_OPACITY, color=PROGRESS_BAR_FRAME_COLOR)

    def _calculate_progress_width_from_points(self, points):
        if points <= 0:
            return 0.0
        progress = float(points)
        progress_ratio = progress / self.max_season_progress
        max_progress_width = float(self.progress_bar_max_width - REWARD_ICON_MARGIN)
        if progress_ratio > 1:
            return max_progress_width
        offset_width_for_extra_points = float(self.reward_icon_size / 2.0 - REWARD_ICON_MARGIN)
        max_points_progress_width = max_progress_width - offset_width_for_extra_points - REWARD_ICON_MARGIN
        return max(MIN_PROGRESS_WIDTH, max_points_progress_width * progress_ratio)

    def _update_progress_bar(self, animate_progress = True):
        if not animate_progress:
            self.progress_gradient_fill.width = settings.char.ui.Get('season_progress_width', 0.0)
            return
        season_points = self.season_service.get_points()
        progress_width = self._calculate_progress_width_from_points(season_points)
        last_progress_width = self._get_last_progress_width(progress_width)
        self.progress_gradient_fill.width = last_progress_width
        self._set_last_progress_width(progress_width)
        animations.MorphScalar(self.progress_gradient_fill, 'width', last_progress_width, progress_width, duration=PROGRESS_BAR_ANIMATION_DURATION)

    def _get_last_progress_width(self, progress_width):
        if not self.use_settings_to_recover_last_progress:
            return 0.0
        last_progress_width = settings.char.ui.Get('season_progress_width', 0.0)
        if last_progress_width + PROGRESS_WIDTH_TOL >= progress_width:
            return 0.0
        return last_progress_width

    def _set_last_progress_width(self, progress_width):
        if not self.use_settings_to_recover_last_progress:
            return
        settings.char.ui.Set('season_progress_width', progress_width)

    def _update_reward_achievement_sprites(self, reward_id, reward_data):
        reward_achievement_sprite = self.reward_achievement_sprites[reward_id]
        reward_points_label = self.reward_points_labels[reward_id]
        is_reward_achieved = self._is_reward_achieved(reward_data)
        if is_reward_achieved:
            reward_points_label.color = SEASON_THEME_TEXT_COLOR_HIGHLIGHTED
            reward_achievement_sprite.color = SEASON_THEME_TEXT_COLOR_HIGHLIGHTED
        else:
            reward_points_label.color = SEASON_THEME_TEXT_COLOR_REGULAR
            reward_achievement_sprite.color = SEASON_THEME_TEXT_COLOR_REGULAR
        reward_achievement_sprite.display = is_reward_achieved

    def _is_reward_achieved(self, reward):
        return reward['points_required'] <= self.season_service.get_points()

    def OnSeasonalPointsUpdatedInClient(self, season_points):
        self._update_progress_bar()

    def OnSeasonalGoalsResetInClient(self):
        self._update_progress_bar()
        for reward_id, reward_data in self.rewards.items():
            self._update_reward_achievement_sprites(reward_id, reward_data)

    def OnSeasonalGoalCompletedInClient(self, reward_id, reward_data):
        self._update_reward_achievement_sprites(reward_id, reward_data)
