#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\seasons\client\challengeinfopaneltaskentry.py
import carbonui.const as uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.fill import Fill
from carbonui.primitives.sprite import Sprite
from carbonui.uianimations import animations
from eve.client.script.ui.control.eveLabel import EveLabelMediumBold, EveLabelMedium
from eve.client.script.ui.shared.infoPanels.infoPanelControls import InfoPanelHeaderBackground
from achievements.client.achievementTaskEntry import CheckMouseOverUtil, BlurredBackgroundSprite
from seasons.client.challengetaskprogressbar import ChallengeTaskProgressBar
from seasons.client.const import get_challenge_progress_counter_label_text
from seasons.client.seasonpoints import SeasonPoints, DEFAULT_SEASON_POINTS_SIZE
from seasons.client.uiutils import get_agent_icon
import uthread
import blue
CHALLENGE_CONTAINER_WIDTH = 271
PROGRESS_FRAME_WIDTH_OFFSET = 9
PROGRESS_LABEL_LEFT = 7
HEADER_HEIGHT = 23
HEADER_PAD_TOP = 4
HEADER_PAD_BOTTOM = 4
HEADER_MOUSE_OVER_ANIMATION_SCALE = 2.0
HEADER_MOUSE_OVER_ANIMATION_DURATION = 0.5
HEADER_MOUSE_RESET_ANIMATION_SCALE = 1.0
HEADER_MOUSE_RESET_ANIMATION_DURATION = 0.1
LABEL_CONTAINER_HEIGHT = 25
LABEL_CONTAINER_WIDTH = CHALLENGE_CONTAINER_WIDTH - DEFAULT_SEASON_POINTS_SIZE
DETAILS_INFO_SIZE = 64
AGENT_CONTAINER_SIZE = DETAILS_INFO_SIZE - 10
AGENT_ICON_PADDING = 5
AGENT_ICON_SIZE_OFFSET = 4
AGENT_BORDER_COLOR = (1, 1, 1, 0.5)
AGENT_BORDER_WIDTH = 1
DETAILS_SIZE = DETAILS_INFO_SIZE + LABEL_CONTAINER_HEIGHT
DETAILS_PAD_RIGHT = 7
DETAILS_BACKGROUND_COLOR = (0, 0, 0, 0.2)
DETAILS_BLURRED_BACKGROUND_COLOR = (1, 1, 1, 0.9)
DETAILS_PAD_LEFT = 5
CHALLENGE_DESCRIPTION_WIDTH = CHALLENGE_CONTAINER_WIDTH - DETAILS_INFO_SIZE - DETAILS_PAD_RIGHT - DETAILS_PAD_LEFT
CHALLENGE_DESCRIPTION_PADDING = 10
CHALLENGE_DESCRIPTION_COLOR = (1, 1, 1, 0.5)
CHALLENGE_DESCRIPTION_PAD_SIDES = 5
FINISHED_CHECK_WIDTH = 14
FINISHED_CHECK_HEIGHT = 14
FINISHED_CHECK_ANIMATION_GLOW_COLOR = (1, 1, 1, 0.25)
FINISHED_CHECK_ANIMATION_GLOW_EXPAND = 2
FINISHED_CHECK_ANIMATION_DURATION = 0.5
COMPLETED_BACKGROUND_HIGHLIGHT_COLOR = (0.196, 1.0, 0.137, 0.5)
COMPLETED_CHECK_RES_PATH = 'res:/UI/Texture/Classes/InfoPanels/opportunitiesCheck.png'
EXPIRED_BACKGROUND_HIGHLIGHT_COLOR = (1, 0.75, 0, 0.5)
DEFAULT_SHOW_DETAILS = True

class ChallengeInfoPanelTaskEntry(ContainerAutoSize):
    default_padLeft = 0
    default_padRight = 0
    default_padTop = 0
    default_padBottom = 4
    default_state = uiconst.UI_NORMAL
    default_clipChildren = False
    default_alignMode = uiconst.TOTOP
    tooltipPointer = uiconst.POINT_LEFT_2
    details_container = None
    callbackTaskExpanded = None
    counter_background = None

    def ApplyAttributes(self, attributes):
        ContainerAutoSize.ApplyAttributes(self, attributes)
        self.challenge = attributes.challenge
        self.open_challenges = attributes.open_challenges_function
        show_details = attributes.Get('show_details', DEFAULT_SHOW_DETAILS)
        self._construct_header()
        if show_details:
            self._show_details()
        self.objects_for_animations = []

    def _construct_header(self):
        self.header_container = ChallengeTaskProgressBar(name='header_container', parent=self, align=uiconst.TOTOP, challenge=self.challenge, progress_frame_width=CHALLENGE_CONTAINER_WIDTH, progress_frame_width_offset=PROGRESS_FRAME_WIDTH_OFFSET, height=HEADER_HEIGHT, padTop=HEADER_PAD_TOP, padBottom=HEADER_PAD_BOTTOM, label_type_function=EveLabelMediumBold, state=uiconst.UI_NORMAL, show_expiration_timer=True, progress_label_left=PROGRESS_LABEL_LEFT)
        self.header_container.OnClick = self._toggle_details

    def _toggle_details(self):
        if self.are_details_shown():
            self._hide_details()
        else:
            self._show_details()

    def _hide_details(self, *args):
        if self.are_details_shown():
            settings.char.ui.Set('show_challenge_details_in_info_panel', False)
            self.details_container.Close()
            self.details_container.Flush()

    def _show_details(self):
        if self.are_details_shown():
            return
        settings.char.ui.Set('show_challenge_details_in_info_panel', True)
        uthread.new(self._show_details_thread)

    def are_details_shown(self):
        return self.details_container is not None and not self.details_container.destroyed

    def _show_details_thread(self):
        global blue
        self.details_container = Container(name='details_container', align=uiconst.TOTOP, parent=self, height=DETAILS_SIZE, padRight=DETAILS_PAD_RIGHT, state=uiconst.UI_NORMAL)
        self.details_container.OnClick = self.open_challenges
        self._construct_details_header()
        self._construct_details_info()
        if self._is_completed():
            self._animate_completion()
        elif self.challenge.is_expired:
            self.expire_challenge()
        if self.callbackTaskExpanded:
            self.callbackTaskExpanded(self)
        blue.synchro.Yield()

    def _construct_details_header(self):
        self.details_header_container = Container(name='details_header_container', parent=self.details_container, align=uiconst.TOTOP, height=LABEL_CONTAINER_HEIGHT)
        self.counter_background = InfoPanelHeaderBackground(bgParent=self.details_header_container)
        self.objects_for_animations.append(self.counter_background.colorFill)
        self.construct_finish_check()
        self._construct_header_label()
        self._construct_reward()

    def construct_finish_check(self):
        self.finished_check_container = Container(name='finished_check_container', parent=self.details_header_container, width=FINISHED_CHECK_WIDTH, align=uiconst.TOLEFT, padLeft=DETAILS_PAD_LEFT)
        finished_check_icon_container = Container(name='finished_check_container', parent=self.finished_check_container, width=FINISHED_CHECK_WIDTH, height=FINISHED_CHECK_WIDTH, align=uiconst.CENTER)
        self.finished_check = Sprite(name='finished_check', parent=finished_check_icon_container, align=uiconst.TOALL)
        self.finished_check_container.Hide()

    def _construct_header_label(self):
        challenge_header_label_container = Container(name='challenge_header_label_container', parent=self.details_header_container, align=uiconst.TOLEFT, width=LABEL_CONTAINER_WIDTH, padLeft=DETAILS_PAD_LEFT)
        self.challenge_header_label = EveLabelMediumBold(name='challenge_header_label', parent=challenge_header_label_container, text=self.challenge.name, align=uiconst.CENTERLEFT)

    def _construct_reward(self):
        season_points_container = Container(name='challenge_header_label_container', parent=self.details_header_container, align=uiconst.TORIGHT, padRight=DETAILS_PAD_RIGHT)
        season_points = SeasonPoints(name='reward_container', parent=season_points_container, points=self.challenge.points_awarded, align=uiconst.TOTOP, height=DEFAULT_SEASON_POINTS_SIZE, reward_label_class=EveLabelMediumBold, state=uiconst.UI_NORMAL)
        season_points.OnClick = self.open_challenges
        season_points_container.width = season_points.width

    def _construct_details_info(self):
        self.details_info_container = Container(name='details_info_container', align=uiconst.TOTOP, parent=self.details_container, height=DETAILS_INFO_SIZE)
        Fill(bgParent=self.details_info_container, color=DETAILS_BACKGROUND_COLOR)
        BlurredBackgroundSprite(bgParent=self.details_info_container, color=DETAILS_BLURRED_BACKGROUND_COLOR)
        self._construct_agent()
        self._construct_challenge_description()
        self._set_details_info_size()

    def _construct_agent(self):
        agent_container = Container(name='agent_container', parent=self.details_info_container, align=uiconst.TOLEFT, width=AGENT_CONTAINER_SIZE, padding=AGENT_ICON_PADDING)
        agent_picture_container = Container(name='agent_container', parent=agent_container, align=uiconst.CENTERTOP, width=AGENT_CONTAINER_SIZE, height=AGENT_CONTAINER_SIZE, padding=AGENT_BORDER_WIDTH)
        agent_background_container = InfoPanelHeaderBackground(bgParent=agent_picture_container, color=AGENT_BORDER_COLOR)
        self.objects_for_animations.append(agent_background_container.colorFill)
        agent_icon = get_agent_icon(name='agent_icon', parent=agent_picture_container, align=uiconst.CENTER, size=AGENT_CONTAINER_SIZE - AGENT_ICON_SIZE_OFFSET, agent_id=self.challenge.agent_id)
        agent_icon.OnClick = self.open_challenges

    def _construct_challenge_description(self):
        self.challenge_description_container = Container(name='challenge_description_container', parent=self.details_info_container, align=uiconst.TOTOP, height=DETAILS_INFO_SIZE)
        self.challenge_description_label = EveLabelMedium(name='challenge_description_label', parent=self.challenge_description_container, align=uiconst.CENTERLEFT, width=CHALLENGE_DESCRIPTION_WIDTH - CHALLENGE_DESCRIPTION_PAD_SIDES, padLeft=CHALLENGE_DESCRIPTION_PAD_SIDES, text=self.challenge.message_text, color=CHALLENGE_DESCRIPTION_COLOR)
        self.objects_for_animations.append(self.challenge_description_label)

    def _set_details_info_size(self):
        details_info_height = max(self.challenge_description_label.height + CHALLENGE_DESCRIPTION_PADDING, self.details_info_container.height)
        self.details_info_container.height = details_info_height
        self.challenge_description_container.height = details_info_height

    def OnMouseEnter(self, *args):
        animations.MorphScalar(self.header_container, 'opacity', startVal=self.opacity, endVal=HEADER_MOUSE_OVER_ANIMATION_SCALE, curveType=uiconst.ANIM_OVERSHOT, duration=HEADER_MOUSE_OVER_ANIMATION_DURATION)
        CheckMouseOverUtil(self, self.ResetMouseOverState)

    def ResetMouseOverState(self, *args):
        if self.destroyed:
            return
        animations.MorphScalar(self.header_container, 'opacity', startVal=self.opacity, endVal=HEADER_MOUSE_RESET_ANIMATION_SCALE, duration=HEADER_MOUSE_RESET_ANIMATION_DURATION)

    def GetHint(self):
        return None

    def update_challenge_progress(self, new_progress):
        self.challenge.progress = new_progress
        self.header_container.update_challenge(new_progress)
        self._update_counter()

    def _update_counter(self):
        if not hasattr(self, 'challenge_text'):
            return
        challenge_progress_counter_text = get_challenge_progress_counter_label_text(self.challenge)
        self.challenge_header_label.SetText(challenge_progress_counter_text)

    def complete_challenge(self):
        self.update_challenge_progress(self.challenge.max_progress)
        if not self.are_details_shown():
            return
        self._animate_completion()

    def _is_completed(self):
        return self.challenge.progress >= self.challenge.max_progress

    def _animate_completion(self):
        uthread.new(self._animation_thread, COMPLETED_BACKGROUND_HIGHLIGHT_COLOR, icon_path=COMPLETED_CHECK_RES_PATH)

    def _animation_thread(self, background_highlight_color, icon_path = None):
        if self.counter_background is not None:
            self.counter_background.colorFill.color = background_highlight_color
        if icon_path:
            self._add_finished_check(icon_path)

    def _add_finished_check(self, icon_path):
        self.finished_check.SetTexturePath(icon_path)
        self.finished_check_container.Show()
        animations.SpGlowFadeIn(self.finished_check, glowColor=FINISHED_CHECK_ANIMATION_GLOW_COLOR, glowExpand=FINISHED_CHECK_ANIMATION_GLOW_EXPAND, duration=FINISHED_CHECK_ANIMATION_DURATION, curveType=uiconst.ANIM_WAVE)

    def expire_challenge(self):
        uthread.new(self._animation_thread, EXPIRED_BACKGROUND_HIGHLIGHT_COLOR)
