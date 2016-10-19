#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\seasons\client\challengetaskprogressbar.py
import carbonui.const as uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.frame import Frame
from carbonui.uianimations import animations
from eve.client.script.ui.shared.infoPanels.infoPanelConst import POINT_RIGHT_HEADER_FRAME_TEXTURE_PATH
from eve.client.script.ui.shared.infoPanels.infoPanelConst import POINT_RIGHT_HEADER_BACKGROUND_TEXTURE_PATH
from eve.client.script.ui.shared.infoPanels.infoPanelConst import POINT_RIGHT_HEADER_COLOR
from seasons.client.challengeexpirationtimer import ChallengeExpirationTimer, CHALLENGE_EXPIRATION_CLOCK_SIZE
from seasons.client.const import get_challenge_progress_counter_label_text, DEFAULT_ANIMATE_PROGRESS
from seasons.client.uiutils import SEASON_THEME_TEXT_COLOR_HIGHLIGHTED, SEASON_THEME_TEXT_COLOR_REGULAR, SEASON_THEME_TEXT_COLOR_INACTIVE
PROGRESS_FRAME_CORNER_SIZE = 16
PROGRESS_FRAME_OFFSET = -14
PROGRESS_FRAME_PAD_RIGHT = 7
PROGRESS_BAR_CORNER_SIZE = 15
PROGRESS_BAR_OFFSET = -13
PROGRESS_BAR_PAD_RIGHT = -1
PROGRESS_BAR_UPDATE_ANIMATION_SPEED = 2
DEFAULT_PROGRESS_LABEL_PAD_LEFT = -2
DEFAULT_ADAPT_TEXT_COLOR_TO_PROGRESS = False
TOOLTIP_WRAP_WIDTH = 200

class ChallengeTaskProgressBar(Container):

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.challenge = attributes.challenge
        self.pickState = uiconst.TR2_SPS_ON
        self.adapt_text_color_to_progress = attributes.Get('adapt_text_color_to_progress', DEFAULT_ADAPT_TEXT_COLOR_TO_PROGRESS)
        self.progress_frame_width = attributes.progress_frame_width
        self.progress_frame_width_offset = attributes.progress_frame_width_offset
        self.progress_frame_width_max = self._get_max_progress_frame_width(attributes)
        self.progress_label_left = attributes.Get('progress_label_left', DEFAULT_PROGRESS_LABEL_PAD_LEFT)
        self.animate_progress = attributes.Get('animate_progress', DEFAULT_ANIMATE_PROGRESS)
        self.show_expiration_timer = attributes.Get('show_expiration_timer', False)
        self.label_type_function = attributes.label_type_function
        self._construct_progress_label()
        self._construct_progress_bar()
        self.update_progress_bar(self.challenge.progress)

    def _get_max_progress_frame_width(self, attributes):
        progress_frame_width_max = self.progress_frame_width
        if attributes.padLeft:
            progress_frame_width_max -= attributes.padLeft
        if attributes.padRight:
            progress_frame_width_max -= attributes.padRight
        return progress_frame_width_max

    def _construct_progress_label(self):
        self.challenge_content_container = Container(name='challenge_content_container', parent=self, align=uiconst.ANCH_TOPLEFT, width=self.progress_frame_width, height=self.height, padLeft=self.padLeft)
        if self.show_expiration_timer:
            self._construct_expiration_timer()
        challenge_label_container = Container(name='challenge_label_container', parent=self.challenge_content_container, padLeft=self.progress_label_left, align=uiconst.TOLEFT, width=self.progress_frame_width - self.height)
        self.challenge_label = self.label_type_function(name='challenge_label', parent=challenge_label_container, align=uiconst.CENTERLEFT)
        self._update_counter()

    def _construct_progress_bar(self):
        self.progress_frame = Frame(name='progress_bar_frame', texturePath=POINT_RIGHT_HEADER_FRAME_TEXTURE_PATH, cornerSize=PROGRESS_FRAME_CORNER_SIZE, offset=PROGRESS_FRAME_OFFSET, parent=self, color=POINT_RIGHT_HEADER_COLOR, align=uiconst.TOALL, padRight=PROGRESS_FRAME_PAD_RIGHT)
        self.progress_frame_container = Container(name='progress_frame_container', parent=self, align=uiconst.TOLEFT, clipChildren=True)
        self.progress_bar_container = Container(name='progress_bar_container', parent=self.progress_frame_container, align=uiconst.TOLEFT)
        self.progress_bar = Frame(name='progress_bar_fill', texturePath=POINT_RIGHT_HEADER_BACKGROUND_TEXTURE_PATH, cornerSize=PROGRESS_BAR_CORNER_SIZE, offset=PROGRESS_BAR_OFFSET, parent=self.progress_bar_container, color=POINT_RIGHT_HEADER_COLOR, padRight=PROGRESS_BAR_PAD_RIGHT)

    def update_progress_bar(self, new_progress):
        progress_width = self._calculate_progress_width(new_progress)
        self.progress_bar_container.width = progress_width - self.progress_frame_width_offset
        if progress_width > self.progress_frame_width_max - self.progress_frame_width_offset:
            new_width = self.progress_frame_width_max
        else:
            new_width = progress_width - self.progress_frame_width_offset
        if self.animate_progress:
            animations.MorphScalar(self.progress_frame_container, 'width', self.progress_frame_container.width, new_width, PROGRESS_BAR_UPDATE_ANIMATION_SPEED)
            return
        self.progress_frame_container.width = new_width

    def _calculate_progress_width(self, new_progress):
        progress = float(new_progress) / float(self.challenge.max_progress)
        return float(self.progress_frame_width_max) * progress

    def update_challenge(self, new_progress):
        self.challenge.progress = new_progress
        self.update_progress_bar(new_progress)
        self._update_counter()

    def _update_counter(self):
        challenge_progress_counter_text = get_challenge_progress_counter_label_text(self.challenge)
        self.challenge_label.SetText(challenge_progress_counter_text)
        if self.adapt_text_color_to_progress:
            self.challenge_label.color = self._get_text_color_from_progress()

    def _construct_expiration_timer(self):
        expiration_timer_container = Container(name='expiration_timer_container', parent=self.challenge_content_container, align=uiconst.TORIGHT, width=CHALLENGE_EXPIRATION_CLOCK_SIZE, padRight=PROGRESS_FRAME_PAD_RIGHT)
        ChallengeExpirationTimer(name='expiration_timer', parent=expiration_timer_container, align=uiconst.CENTER, width=CHALLENGE_EXPIRATION_CLOCK_SIZE, height=CHALLENGE_EXPIRATION_CLOCK_SIZE, expiration_date=self.challenge.expiration_date)

    def _get_text_color_from_progress(self):
        if self.challenge.progress == 0:
            return SEASON_THEME_TEXT_COLOR_INACTIVE
        if self.challenge.progress == self.challenge.max_progress:
            return SEASON_THEME_TEXT_COLOR_HIGHLIGHTED
        return SEASON_THEME_TEXT_COLOR_REGULAR

    def LoadTooltipPanel(self, tooltipPanel, *args, **kwds):
        if uicore.uilib.tooltipHandler.IsUnderTooltip(self):
            return
        tooltipPanel.LoadGeneric2ColumnTemplate()
        if self.challenge.objective_text:
            tooltipPanel.AddLabelMedium(text=self.challenge.objective_text, colSpan=tooltipPanel.columns, wrapWidth=TOOLTIP_WRAP_WIDTH)

    def GetHint(self):
        return None
