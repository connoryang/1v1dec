#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\seasons\client\seasonreward.py
import carbonui.const as uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.fill import Fill
from carbonui.primitives.gradientSprite import GradientSprite
from carbonui.primitives.sprite import StreamingVideoSprite, Sprite
from carbonui.primitives.transform import Transform
from carbonui.uianimations import animations
from carbonui.util.color import Color
from eve.client.script.ui.control.buttons import Button
from eve.client.script.ui.control.eveLabel import EveLabelSmall, EveCaptionLarge, EveCaptionSmall, EveLabelLargeBold
import evetypes
from localization import GetByLabel
from seasons.client.const import get_reward_unlocked_header, get_reward_unlocked_body
from seasons.client.currenteventbanner import CurrentEventBanner
from seasons.client.seasonpoints import SeasonPoints
from seasons.client.uiutils import SEASON_LINE_BREAK_GRADIENT, get_reward_icon_in_size
import trinity
REWARD_BANNER_TOP = 35
REWARD_BANNER_HEIGHT = 222
REWARD_CONTAINER_DEFAULT_PADDING = 2
REWARD_CONTAINER_WIDTH = 400
REWARD_CONTENT_HEIGHT = 300
REWARD_HEADER_LABEL_HEIGHT = 35
REWARD_CONTAINER_HEIGHT = REWARD_CONTENT_HEIGHT + REWARD_HEADER_LABEL_HEIGHT
REWARD_BACKGROUND_OVERLAY_RGB_DATA = ((0.0, (0.5, 0.5, 0.5)), (0.5, (0.25, 0.25, 0.25)), (1.0, (0.0, 0.0, 0.0)))
REWARD_BACKGROUND_OVERLAY_ALPHA_DATA = ((1.0, 0.5), (0.5, 0.25), (1.0, 0.5))
REWARD_BACKGROUND_BANNER_OPACITY = 0.5
REWARD_BACKGROUND_FILL_COLOR = (0, 0, 0, 0.85)
REWARD_SEASON_POINTS_HEIGHT = 187
REWARD_SEASON_POINTS_BACKGROUND_HEIGHT = 40
REWARD_SEASON_TOP_PADDING = 2
REWARD_SEASON_POINTS_LABEL_CLASS = EveCaptionSmall
REWARD_SEASON_POINT_LABEL_SIZE = 36
REWARD_ITEM_ICON_SIZE = 140
REWARD_ICON_TEXTURE_SIZE = 128
REWARD_ITEM_ICON_TOP_MARGIN = -38
REWARD_ITEM_ICON_SCALING_CENTER = (0.5, 0.5)
REWARD_ITEM_ICON_GLOW_PADDING = 35
REWARD_ITEM_LABEL_HEIGHT = 35
REWARD_ITEM_LABEL_LINE_HEIGHT = 1
REWARD_ITEM_LABEL_LINE_OPACITY = 0.5
REWARD_ITEM_BACKGROUND_PADDING = 50
REWARD_BOTTOM_CONTAINER_HEIGHT = 80
REWARD_BOTTOM_CONTAINER_LABEL_SIDE_PAD = 50
REWARD_BOTTOM_CONTAINER_LABEL_PAD_TOP = 10
REWARD_NOTE_LABEL_HEIGHT = 30
REWARD_CONTINUE_BUTTON_HEIGHT = 40
REWARD_DISAPPEAR_ANIMATION_DURATION = 1
REWARD_GRADIENT_RGB_DATA = ((0.0, (0.05, 0.05, 0.05)), (0.5, (0.0, 0.0, 0.0)), (1.0, (0.05, 0.05, 0.05)))
REWARD_GRADIENT_ALPHA_DATA = ((0.0, 0.25), (0.5, 1.0), (1.0, 0.25))
ANIMATED_DEFAULT_OPACITY = 0.0
ANIMATED_DEFAULT_FADE_IN_DURATION = 1.0
ANIMATED_BOTTOM_CONTAINER_FADE_IN_DURATION = 2.5
ANIMATED_GRADIENT_BACKGROUND_RGD_DATA = ((0.0, (1.0, 1.0, 1.0)), (0.5, (1.0, 1.0, 1.0)), (1.0, (1.0, 1.0, 1.0)))
ANIMATED_GRADIENT_BACKGROUND_ALPHA_DATA = ((0.0, 0.0), (0.5, 1.0), (1.0, 0.0))
ANIMATED_GRADIENT_BACKGROUND_OPACITY = 0.25
ANIMATED_GRADIENT_BACKGROUND_DURATION = 0.5
ANIMATED_GRADIENT_BACKGROUND_OFFSET = 1.0
ANIMATED_ICON_OVERLAY_FILL_DURATION = 0.5
ANIMATED_ICON_OVERLAY_OPACITY = 0.75
ANIMATED_ICON_SIZE_FACTOR = 1.5
ANIMATED_ICON_SIZE_DURATION = 1.5
ANIMATED_ICON_SIZE_START_SCALE_SIZE = (1.0, 1.0)
ANIMATED_ICON_SIZE_END_SCALE_SIZE = (0.5, 0.5)
ICON_GLOW_ANIMATION_VIDEO_PATH = 'res:/video/seasons/squarerotatingglow.webm'
ICON_GLOW_ANIMATION_SIZE = 350
TOP_PADDING = 22

class SeasonReward(Container):
    default_padLeft = REWARD_CONTAINER_DEFAULT_PADDING
    default_padTop = REWARD_CONTAINER_DEFAULT_PADDING
    default_padRight = REWARD_CONTAINER_DEFAULT_PADDING
    default_padBottom = REWARD_CONTAINER_DEFAULT_PADDING
    default_align = uiconst.TOALL

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.Hide()
        self.season_service = attributes.season_service
        self.width = min(self.width, REWARD_CONTAINER_WIDTH) - 2 * REWARD_CONTAINER_DEFAULT_PADDING
        self.finished_goals = []
        self._create_reward_view()
        self._create_finished_background_overlay()
        self.show_finished_goals()

    def show_finished_goals(self):
        self.finished_goals += self.season_service.get_and_clear_recently_finished_goals().values()
        if self.display or not self.finished_goals:
            return
        self._display_reward(self.finished_goals.pop(0))

    def _create_reward_view(self):
        self.reward_container = Container(name='reward_container', parent=self, align=uiconst.CENTER, width=self.parent.width, height=REWARD_CONTAINER_HEIGHT)
        self.reward_main_container = Container(name='reward_main_container', parent=self.reward_container, align=uiconst.TOALL)
        self._create_reward_header()
        self._create_reward_content_container()
        self._create_reward_content()
        self.reward_event_banner_container = Container(name='reward_event_banner_container', parent=self.reward_main_container, align=uiconst.CENTERTOP, width=self.width, height=REWARD_BANNER_HEIGHT, opacity=ANIMATED_DEFAULT_OPACITY, top=REWARD_BANNER_TOP)
        self.reward_event_banner = CurrentEventBanner(name='reward_event_banner', parent=self.reward_event_banner_container, banner_texture=self.season_service.get_season_background_no_logo(), align=uiconst.CENTER, opacity=REWARD_BACKGROUND_BANNER_OPACITY)
        self.reward_main_container.Hide()

    def _create_finished_background_overlay(self):
        GradientSprite(name='finished_gradient_overlay', align=uiconst.TOALL, parent=self, rgbData=REWARD_BACKGROUND_OVERLAY_RGB_DATA, alphaData=REWARD_BACKGROUND_OVERLAY_ALPHA_DATA, radial=True)
        finished_fill_container = Container(name='finished_fill_container', parent=self, align=uiconst.TOALL)
        Fill(bgParent=finished_fill_container, color=REWARD_BACKGROUND_FILL_COLOR)

    def _create_reward_header(self):
        self.reward_header_label_container = Container(name='reward_header_label_container', parent=self.reward_main_container, align=uiconst.TOTOP, width=self.width, height=REWARD_HEADER_LABEL_HEIGHT, opacity=ANIMATED_DEFAULT_OPACITY)
        EveCaptionLarge(name='reward_header_label', parent=self.reward_header_label_container, align=uiconst.CENTERTOP, text=get_reward_unlocked_header(), bold=True)
        self.reward_header_line = Sprite(name='reward_header_container_line', parent=self.reward_header_label_container, texturePath=SEASON_LINE_BREAK_GRADIENT, align=uiconst.BOTTOMLEFT, width=self.width, height=REWARD_ITEM_LABEL_LINE_HEIGHT, opacity=REWARD_ITEM_LABEL_LINE_OPACITY, useSizeFromTexture=False)

    def _create_reward_content_container(self):
        self.reward_content_container = Container(name='reward_content_container', parent=self.reward_main_container, align=uiconst.TOTOP, height=REWARD_CONTENT_HEIGHT)

    def _create_reward_content(self):
        self._create_item_reward_icon()
        self._create_reward_season_points()
        self._create_item_reward_label()
        self._create_reward_bottom_container()

    def _create_reward_season_points(self):
        self.reward_season_points_container = Container(name='reward_season_points_container', parent=self.reward_content_container, align=uiconst.TOTOP, height=REWARD_SEASON_POINTS_HEIGHT, opacity=ANIMATED_DEFAULT_OPACITY)
        self.reward_season_points_top_container = Container(name='reward_season_points_top_container', parent=self.reward_season_points_container, align=uiconst.TOTOP, height=REWARD_SEASON_POINTS_BACKGROUND_HEIGHT)
        reward_season_points_label_container = Container(name='reward_season_points_label_container', parent=self.reward_season_points_top_container, align=uiconst.TOTOP, height=REWARD_SEASON_POINT_LABEL_SIZE, padTop=REWARD_SEASON_TOP_PADDING)
        self.reward_points = SeasonPoints(name='reward_season_points_label', parent=reward_season_points_label_container, align=uiconst.CENTER, height=REWARD_SEASON_POINTS_HEIGHT, points=0, reward_label_class=REWARD_SEASON_POINTS_LABEL_CLASS, season_points_size=REWARD_SEASON_POINT_LABEL_SIZE)
        self.reward_season_points_background_container = None
        self._create_reward_season_points_background()

    def _create_reward_season_points_background(self):
        if self.reward_season_points_background_container:
            self.reward_season_points_background_container.Flush()
            self.reward_season_points_background_container.Close()
        self.reward_season_points_background_container = Container(name='reward_season_points_background_container', parent=self.reward_season_points_top_container, align=uiconst.CENTER, width=self.width, height=REWARD_SEASON_POINTS_BACKGROUND_HEIGHT)
        self.season_points_background = self._add_gradient_reward_background(self.reward_season_points_background_container)

    def _create_item_reward_icon(self):
        self.reward_item_icon_glow_container = Transform(name='reward_item_icon_glow_container', parent=self.reward_content_container, align=uiconst.CENTER, height=REWARD_ITEM_ICON_SIZE, width=REWARD_ITEM_ICON_SIZE, top=REWARD_ITEM_ICON_TOP_MARGIN, scalingCenter=REWARD_ITEM_ICON_SCALING_CENTER)
        self.reward_item_icon_glow_container.Hide()
        self.reward_item_icon_container = Container(name='reward_item_icon_container', parent=self.reward_item_icon_glow_container, align=uiconst.TOALL, padding=REWARD_ITEM_ICON_GLOW_PADDING)
        self.reward_item_icon_overlay_fill = Fill(parent=self.reward_item_icon_container, color=Color.WHITE, opacity=ANIMATED_ICON_OVERLAY_OPACITY)
        Fill(bgParent=self.reward_item_icon_container, color=REWARD_BACKGROUND_FILL_COLOR)

    def _create_item_reward_label(self):
        self.reward_item_label_container = Container(name='reward_item_label_container', parent=self.reward_content_container, align=uiconst.TOTOP, width=self.width, height=REWARD_ITEM_LABEL_HEIGHT, opacity=ANIMATED_DEFAULT_OPACITY)
        Sprite(name='reward_item_label_line', parent=self.reward_item_label_container, texturePath=SEASON_LINE_BREAK_GRADIENT, align=uiconst.TOBOTTOM, width=self.width - REWARD_ITEM_BACKGROUND_PADDING * 2, height=REWARD_ITEM_LABEL_LINE_HEIGHT, opacity=REWARD_ITEM_LABEL_LINE_OPACITY, useSizeFromTexture=False)
        self.reward_item_label = EveLabelLargeBold(name='reward_item_label', parent=self.reward_item_label_container, align=uiconst.CENTER, text='')
        self.reward_label_background_container = None
        self._create_reward_label_background()

    def _create_reward_label_background(self):
        if self.reward_label_background_container:
            self.reward_label_background_container.Flush()
            self.reward_label_background_container.Close()
        self.reward_label_background_container = Container(name='reward_label_background_container', parent=self.reward_item_label_container, align=uiconst.TOTOP, width=self.width, height=REWARD_ITEM_LABEL_HEIGHT)
        self.reward_label_background = self._add_gradient_reward_background(self.reward_label_background_container)

    def _create_reward_bottom_container(self):
        self.reward_bottom_container = Container(name='reward_bottom_container', parent=self.reward_content_container, align=uiconst.TOTOP, height=REWARD_BOTTOM_CONTAINER_HEIGHT)
        self.reward_note_label_container = Container(name='reward_note_label_container', parent=self.reward_bottom_container, align=uiconst.TOTOP, height=REWARD_NOTE_LABEL_HEIGHT, padLeft=REWARD_BOTTOM_CONTAINER_LABEL_SIDE_PAD, padRight=REWARD_BOTTOM_CONTAINER_LABEL_SIDE_PAD, padTop=REWARD_BOTTOM_CONTAINER_LABEL_PAD_TOP, opacity=ANIMATED_DEFAULT_OPACITY)
        EveLabelSmall(name='reward_note_label', parent=self.reward_note_label_container, align=uiconst.TOTOP, text=get_reward_unlocked_body())
        self.reward_close_button_container = Container(name='reward_close_button_container', parent=self.reward_bottom_container, align=uiconst.TOTOP, height=REWARD_CONTINUE_BUTTON_HEIGHT, opacity=ANIMATED_DEFAULT_OPACITY)
        Button(name='reward_close_button', parent=self.reward_close_button_container, align=uiconst.CENTER, label=GetByLabel('UI/Generic/Close'), func=self._close_reward)
        Sprite(name='reward_bottom_container_line', parent=self.reward_bottom_container, texturePath=SEASON_LINE_BREAK_GRADIENT, align=uiconst.TOBOTTOM, width=self.width, height=REWARD_ITEM_LABEL_LINE_HEIGHT, opacity=REWARD_ITEM_LABEL_LINE_OPACITY, useSizeFromTexture=False)
        self.reward_bottom_background_container = None
        self._create_reward_bottom_background()

    def _create_reward_bottom_background(self):
        if self.reward_bottom_background_container:
            self.reward_bottom_background_container.Flush()
            self.reward_bottom_background_container.Close()
        self.reward_bottom_background_container = Container(name='reward_bottom_background_container', parent=self.reward_bottom_container, align=uiconst.CENTER, width=self.width, height=REWARD_BOTTOM_CONTAINER_HEIGHT)

    def _add_gradient_reward_background(self, parent_container):
        return GradientSprite(name='gradient_reward_background', align=uiconst.TOTOP_NOPUSH, parent=parent_container, width=parent_container.width, height=parent_container.height, rgbData=REWARD_GRADIENT_RGB_DATA, alphaData=REWARD_GRADIENT_ALPHA_DATA)

    def _close_reward(self, *args):
        if self.finished_goals:
            self.reward_main_container.Hide()
            self._show_next_reward()
        else:
            self._hide_rewards()

    def _show_next_reward(self):
        self.reward_content_container.Flush()
        self.animated_gradient_background.Close()
        self._create_reward_content()
        self._display_reward(self.finished_goals.pop(0))

    def _play_reward_audio(self):
        sm.GetService('audio').SendUIEvent('scope_earn_rewards_play')

    def _hide_and_reset(self):
        self.Hide()
        self.opacity = 1.0

    def _hide_rewards(self):
        animations.FadeOut(self, duration=REWARD_DISAPPEAR_ANIMATION_DURATION, callback=self._hide_and_reset)

    def _display_reward(self, reward):
        self.Show()
        self._update_reward_info(reward)
        self._animate_reward()
        self._play_reward_audio()

    def _update_reward_info(self, reward):
        reward_type = reward['reward_type_id']
        reward_points = reward['points_required']
        try:
            self.reward_item_icon = get_reward_icon_in_size(reward_type_id=reward_type, size=REWARD_ICON_TEXTURE_SIZE, name='reward_item_icon', parent=self.reward_item_icon_container, align=uiconst.TOALL)
        except Exception:
            self.reward_item_icon = None
            log.LogError('Failed to load Scope Network reward unlocked icon for item type %d' % reward_type)

        self.reward_item_label.text = evetypes.GetName(reward_type)
        self.reward_points.update_points(reward_points)

    def _animate_reward(self):
        self.animated_gradient_background = GradientSprite(name='animated_gradient_background', parent=self.reward_container, align=uiconst.TOALL, rgbData=ANIMATED_GRADIENT_BACKGROUND_RGD_DATA, alphaData=ANIMATED_GRADIENT_BACKGROUND_ALPHA_DATA, opacity=ANIMATED_GRADIENT_BACKGROUND_OPACITY)
        animations.MorphScalar(self.reward_container, 'width', endVal=self.width, duration=ANIMATED_GRADIENT_BACKGROUND_DURATION, timeOffset=ANIMATED_GRADIENT_BACKGROUND_OFFSET, callback=self._show_reward)

    def _show_reward(self):
        self.reward_main_container.Show()
        self._animate_reward_content()
        self._animate_icon()
        self._remove_animated_gradient_background()

    def _animate_reward_content(self):
        animations.FadeIn(self.reward_event_banner_container, duration=ANIMATED_DEFAULT_FADE_IN_DURATION)
        animations.FadeIn(self.reward_item_label_container, duration=ANIMATED_DEFAULT_FADE_IN_DURATION)
        animations.FadeIn(self.reward_header_label_container, duration=ANIMATED_DEFAULT_FADE_IN_DURATION)
        animations.FadeIn(self.reward_season_points_container, duration=ANIMATED_DEFAULT_FADE_IN_DURATION, callback=self._animate_bottom_container)

    def _animate_bottom_container(self):
        animations.FadeIn(self.reward_close_button_container, duration=ANIMATED_BOTTOM_CONTAINER_FADE_IN_DURATION)
        animations.FadeIn(self.reward_note_label_container, duration=ANIMATED_BOTTOM_CONTAINER_FADE_IN_DURATION)

    def _animate_icon(self):
        self.reward_item_icon_glow_container.width *= ANIMATED_ICON_SIZE_FACTOR
        self.reward_item_icon_glow_container.height *= ANIMATED_ICON_SIZE_FACTOR
        self.reward_item_icon_glow_container.Show()
        animations.MorphVector2(self.reward_item_icon_glow_container, 'scale', startVal=ANIMATED_ICON_SIZE_START_SCALE_SIZE, endVal=ANIMATED_ICON_SIZE_END_SCALE_SIZE, duration=ANIMATED_ICON_SIZE_DURATION)
        animations.MorphScalar(self.reward_item_icon_overlay_fill, 'opacity', startVal=ANIMATED_ICON_OVERLAY_OPACITY, endVal=ANIMATED_DEFAULT_OPACITY, duration=ANIMATED_ICON_OVERLAY_FILL_DURATION)
        self._animate_icon_glow()

    def _animate_icon_glow(self):
        animation_video_container = Container(parent=self.reward_item_icon_glow_container, name='animation_video_container', align=uiconst.CENTER, width=ICON_GLOW_ANIMATION_SIZE, height=ICON_GLOW_ANIMATION_SIZE)
        StreamingVideoSprite(bgParent=animation_video_container, name='animation_video', videoPath=ICON_GLOW_ANIMATION_VIDEO_PATH, videoLoop=True, spriteEffect=trinity.TR2_SFX_COPY)

    def _remove_animated_gradient_background(self):
        self.animated_gradient_background.Hide()

    def resize(self, width, height):
        default_width = REWARD_CONTAINER_WIDTH - 2 * REWARD_CONTAINER_DEFAULT_PADDING
        new_width = width - 2 * REWARD_CONTAINER_DEFAULT_PADDING
        self.width = min(new_width, default_width)
        self.height = height - 2 * REWARD_CONTAINER_DEFAULT_PADDING - TOP_PADDING
        self.width = min(new_width, default_width)
        self.reward_container.width = self.width
        self.reward_event_banner_container.width = self.width
        self.reward_event_banner.width = self.width
        self.reward_header_line.width = self.width
        self._create_reward_season_points_background()
        self._create_reward_label_background()
        self._create_reward_bottom_background()
        self.season_points_background.width = self.width
        self.reward_label_background.width = self.width
