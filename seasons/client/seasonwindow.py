#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\seasons\client\seasonwindow.py
import localization
import carbonui.const as uiconst
from carbonui.control.scrollContainer import ScrollContainer
from carbonui.primitives.sprite import Sprite
from carbonui.primitives.container import Container
from eve.client.script.ui.control.eveLabel import EveLabelSmall, EveLabelMedium, EveLabelLargeBold
from eve.client.script.ui.control.eveLabel import EveCaptionSmall
from eve.client.script.ui.control.eveWindow import Window
from eve.common.lib.appConst import defaultPadding
from seasons.common.const import SEASONAL_EVENTS_ID
from seasons.client.challengetaskentry import ChallengeTaskEntry, calculate_challenges_height
from seasons.client.const import SCOPE_LOGO_RES_PATH, get_seasons_title_label_path, get_seasons_title, get_seasons_subcaption
from seasons.client.const import get_seasons_instructions, get_current_event_label
from seasons.client.currenteventbanner import CurrentEventBanner
from seasons.client.nextrewardinfo import NextRewardInfo
from seasons.client.nextrewardpreview import NextRewardPreview
from seasons.client.seasonpoints import SeasonPoints
from seasons.client.seasonprogressbar import SeasonProgressBar
from seasons.client.seasonremainingtime import SeasonRemainingTime
from seasons.client.seasonreward import SeasonReward
from seasons.client.uiutils import SEASON_THEME_TEXT_COLOR_REGULAR, SEASON_FRAME_CORNER_GRADIENT, fill_default_background_color_for_container
from seasons.client.uiutils import fill_header_background_color_for_container, fill_container_with_color_and_opacity
from seasons.client.uiutils import add_season_points_corner_gradient, SEASON_LINE_BREAK_GRADIENT
DEFAULT_WIDTH = 606
DEFAULT_HEIGHT = 650
MINIMAL_WIDTH = 350
DEFAULT_MIN_WIDTH = 315
WIDTH_TOL = 2
DEFAULT_WIDTH_RATIO_HEADER_ICON = 0.07
DEFAULT_HEIGHT_RATIO_HEADER = 0.14
DEFAULT_HEIGHT_RATIO_CURRENT_EVENT = 0.46
DEFAULT_HEIGHT_RATIO_CHALLENGES = 0.4
DEFAULT_HEIGHT_RATIO_CURRENT_EVENTS_TITLE = 0.08
DEFAULT_HEIGHT_RATIO_CURRENT_EVENT_BANNER = 0.92
DEFAULT_HEIGHT_RATIO_CURRENT_EVENTS_REWARDS = 0.24
DEFAULT_HEIGHT_HEADER = DEFAULT_HEIGHT * DEFAULT_HEIGHT_RATIO_HEADER
DEFAULT_HEIGHT_CURRENT_EVENT = DEFAULT_HEIGHT * DEFAULT_HEIGHT_RATIO_CURRENT_EVENT
DEFAULT_HEIGHT_CHALLENGES = DEFAULT_HEIGHT * DEFAULT_HEIGHT_RATIO_CHALLENGES
DEFAULT_HEIGHT_RATIO_HEADER_TITLE = 0.33
DEFAULT_HEIGHT_RATIO_HEADER_SUBCAPTION = 0.12
DEFAULT_HEIGHT_HEADER_TITLE = DEFAULT_HEIGHT_HEADER * DEFAULT_HEIGHT_RATIO_HEADER_TITLE
DEFAULT_HEIGHT_HEADER_SUBCAPTION = DEFAULT_HEIGHT_HEADER * DEFAULT_HEIGHT_RATIO_HEADER_SUBCAPTION
INSTRUCTIONS_LINE_HEIGHT = 1
INSTRUCTIONS_LINE_OPACITY = 0.5
DEFAULT_HEIGHT_CURRENT_EVENTS_TITLE = DEFAULT_HEIGHT_CURRENT_EVENT * DEFAULT_HEIGHT_RATIO_CURRENT_EVENTS_TITLE
DEFAULT_HEIGHT_CURRENT_EVENT_BANNER = DEFAULT_HEIGHT_CURRENT_EVENT * DEFAULT_HEIGHT_RATIO_CURRENT_EVENT_BANNER
DEFAULT_HEIGHT_CURRENT_EVENTS_REWARDS = DEFAULT_HEIGHT_CURRENT_EVENT * DEFAULT_HEIGHT_RATIO_CURRENT_EVENTS_REWARDS
MAIN_CONTAINER_PADDING = 2
DEFAULT_PADDING = float(DEFAULT_WIDTH) / 90
HEADER_ICON_CONTAINER_WIDTH = DEFAULT_WIDTH * DEFAULT_WIDTH_RATIO_HEADER_ICON
HEADER_ICON_SIZE = HEADER_ICON_CONTAINER_WIDTH + DEFAULT_PADDING
HEADER_INFO_SUBCAPTION_TOP = -3
HEADER_INFO_INSTRUCTIONS_HEIGHT = DEFAULT_HEIGHT_HEADER / 2.0 - defaultPadding
CHALLENGES_CONTAINER_HEIGHT = 15
CHALLENGE_WIDTH = 298
PROGRESS_FRAME_WIDTH = CHALLENGE_WIDTH
PROGRESS_FRAME_WIDTH_REDUCTION = 9
CHALLENGES_SCROLL_WRAPPER_WIDTH = DEFAULT_WIDTH
SEASON_POINTS_WIDTH = 130
SEASON_POINTS_HEIGHT = 40
SEASON_POINTS_FONTSIZE = 20
SEASON_POINTS_GRADIENT_LEFT = -2
NEXT_REWARD_WIDTH = 65
NEXT_REWARD_HEIGHT = 40
NEXT_REWARD_PREVIEW_SIZE = 80
NEXT_REWARD_PADDING = 10
NEXT_REWARD_PREVIEW_LEFT = 7
PROGRESS_BAR_WIDTH = DEFAULT_WIDTH - NEXT_REWARD_WIDTH - SEASON_POINTS_WIDTH - NEXT_REWARD_PREVIEW_SIZE - 2 * NEXT_REWARD_PADDING - NEXT_REWARD_PREVIEW_LEFT
PROGRESS_BAR_HEIGHT = 40
CURRENT_EVENT_BACKGROUND_COLOR = (0, 0, 0)
CURRENT_EVENT_BACKGROUND_OPACITY = 0.25
CURRENT_EVENT_REWARDS_BACKGROUND_OPACITY = 0.5
CURRENT_EVENT_BANNER_TOP = -50
CURRENT_EVENT_REWARDS_TOP = -8
DEFAULT_TOP_CURRENT_EVENT_INFO = DEFAULT_HEIGHT_CURRENT_EVENT_BANNER + DEFAULT_HEIGHT_CURRENT_EVENTS_TITLE
DEFAULT_LEFT_CURRENT_EVENT_INFO = 1

class SeasonWindow(Window):
    __guid__ = SEASONAL_EVENTS_ID
    default_captionLabelPath = get_seasons_title_label_path()
    default_windowID = SEASONAL_EVENTS_ID
    default_iconNum = SCOPE_LOGO_RES_PATH
    default_isStackable = False
    default_topParentHeight = 0
    default_minSize = (DEFAULT_MIN_WIDTH, DEFAULT_HEIGHT)
    default_maxSize = (DEFAULT_WIDTH, None)
    default_width = DEFAULT_WIDTH
    default_height = DEFAULT_HEIGHT
    __notifyevents__ = ['OnChallengeProgressUpdateInClient',
     'OnChallengeCompletedInClient',
     'OnChallengeExpiredInClient',
     'OnSeasonalPointsUpdatedInClient',
     'OnSeasonalGoalsResetInClient',
     'OnSeasonalGoalCompletedInClient']

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        sm.RegisterNotify(self)
        self.season_service = sm.GetService('seasonService')
        self.challenge_entries = dict()
        self.challenges_scroll_container = None
        self.challenges_scroll_wrapper_container = None
        self.current_event_rewards_wrapper_container = None
        self.current_event_banner_wrapper = None
        self.last_width = self.width
        self._load_current_event_banner_texture()
        self.season_reward = SeasonReward(parent=self.sr.main, season_service=self.season_service, align=uiconst.TOTOP_NOPUSH, width=self.width, height=self.height)
        self.main_container = Container(name='main_container', parent=self.sr.main, align=uiconst.TOALL, padding=MAIN_CONTAINER_PADDING)
        self._create_header()
        self._create_current_event_view()
        self._create_challenges_view()

    def _is_default_width(self, width):
        return width >= DEFAULT_WIDTH - WIDTH_TOL

    def _is_minimal_width(self, width):
        return width <= MINIMAL_WIDTH

    def _get_padded_size(self, size, padding = defaultPadding):
        return size - 2 * padding

    def _load_current_event_banner_texture(self):
        if self._is_minimal_width(self.width):
            self.current_event_banner_texture = self.season_service.get_season_background_minimal()
            return
        self.current_event_banner_texture = self.season_service.get_season_background()

    def _create_header(self):
        header_container = Container(name='header_container', parent=self.main_container, align=uiconst.TOTOP, width=self.main_container.width, height=DEFAULT_HEIGHT_HEADER, clipChildren=True)
        self._create_header_icon(parent_container=header_container)
        self._create_header_info(parent_container=header_container)

    def _create_header_icon(self, parent_container):
        header_icon_container = Container(name='header_icon_container', parent=parent_container, align=uiconst.TOLEFT, width=HEADER_ICON_CONTAINER_WIDTH, height=DEFAULT_HEIGHT_HEADER)
        Sprite(name='header_icon', parent=header_icon_container, texturePath=self.iconNum, align=uiconst.TOPLEFT, padding=defaultPadding, width=HEADER_ICON_SIZE, height=HEADER_ICON_SIZE)

    def _create_header_info(self, parent_container):
        self.header_info_container = Container(name='header_info_container', parent=parent_container, align=uiconst.TOLEFT, width=self._get_padded_size(DEFAULT_WIDTH - HEADER_ICON_CONTAINER_WIDTH, DEFAULT_PADDING), height=DEFAULT_HEIGHT_HEADER, padLeft=DEFAULT_PADDING)
        self._create_header_info_title()
        self._create_header_info_subcaption()
        self._create_header_info_instructions_line()
        self._create_header_info_instructions()

    def _create_header_info_title(self):
        header_title_container = Container(name='header_title_container', parent=self.header_info_container, align=uiconst.TOTOP, width=self.header_info_container.width, height=DEFAULT_HEIGHT_HEADER_TITLE)
        header_title = EveCaptionSmall(name='header_title', parent=header_title_container, text=get_seasons_title(), align=uiconst.TOPLEFT, padding=defaultPadding)
        header_title.color = SEASON_THEME_TEXT_COLOR_REGULAR

    def _create_header_info_subcaption(self):
        header_subcaption_container = Container(name='header_subcaption_container', parent=self.header_info_container, align=uiconst.TOTOP, width=self.header_info_container.width, height=DEFAULT_HEIGHT_HEADER_SUBCAPTION)
        header_subcaption = EveLabelSmall(name='header_subcaption', parent=header_subcaption_container, text=get_seasons_subcaption(), align=uiconst.TOPLEFT, padLeft=defaultPadding, padBottom=defaultPadding, top=HEADER_INFO_SUBCAPTION_TOP)
        header_subcaption.color = SEASON_THEME_TEXT_COLOR_REGULAR

    def _create_header_info_instructions_line(self):
        header_instructions_line_container = Container(name='header_instructions_line_container', parent=self.header_info_container, align=uiconst.TOTOP, width=self.main_container.width, height=INSTRUCTIONS_LINE_HEIGHT, padding=(-HEADER_ICON_CONTAINER_WIDTH,
         defaultPadding,
         defaultPadding,
         defaultPadding))
        Sprite(name='header_instructions_line', parent=header_instructions_line_container, texturePath=SEASON_LINE_BREAK_GRADIENT, align=uiconst.TOPLEFT, width=self.header_info_container.width, height=header_instructions_line_container.height, opacity=INSTRUCTIONS_LINE_OPACITY, useSizeFromTexture=False)

    def _create_header_info_instructions(self):
        self.header_instructions_container = Container(name='header_instructions_container', parent=self.header_info_container, align=uiconst.TOLEFT, width=self._get_padded_size(self.width, 2 * DEFAULT_PADDING), height=HEADER_INFO_INSTRUCTIONS_HEIGHT, left=-HEADER_INFO_INSTRUCTIONS_HEIGHT + defaultPadding)
        header_instructions = EveLabelSmall(name='header_instructions', parent=self.header_instructions_container, text=get_seasons_instructions(), align=uiconst.TOTOP, padding=defaultPadding)
        header_instructions.color = SEASON_THEME_TEXT_COLOR_REGULAR

    def _create_current_event_view(self):
        self.current_event_container = Container(name='current_event_container', parent=self.main_container, align=uiconst.TOTOP, width=DEFAULT_WIDTH, height=DEFAULT_HEIGHT_CURRENT_EVENT, clipChildren=True)
        fill_container_with_color_and_opacity(self.current_event_container, CURRENT_EVENT_BACKGROUND_COLOR, CURRENT_EVENT_BACKGROUND_OPACITY)
        self._create_current_event_title()
        self._create_current_event_rewards()
        self._create_current_event_banner()

    def _create_current_event_title(self):
        parent_container = self.current_event_container
        current_event_title_container = Container(name='current_event_title_container', parent=parent_container, align=uiconst.TOTOP, width=parent_container.width, height=DEFAULT_HEIGHT_CURRENT_EVENTS_TITLE)
        fill_header_background_color_for_container(current_event_title_container)
        current_event_title_label_container = Container(name='current_event_title_label_container', parent=current_event_title_container, align=uiconst.TOTOP, width=parent_container.width, height=DEFAULT_HEIGHT_CURRENT_EVENTS_TITLE, padding=(DEFAULT_PADDING,
         0,
         DEFAULT_PADDING,
         0))
        current_event_title_label = EveLabelMedium(text=get_current_event_label(), parent=current_event_title_label_container, align=uiconst.CENTERLEFT, bold=True)
        current_event_title_label.color = SEASON_THEME_TEXT_COLOR_REGULAR
        self._create_current_event_time(parent_container=current_event_title_container)

    def _create_current_event_time(self, parent_container):
        SeasonRemainingTime(name='current_event_time_container', parent=parent_container, season_service=self.season_service, align=uiconst.CENTERRIGHT, width=parent_container.width / 2, height=parent_container.height, time_label_align=uiconst.CENTERRIGHT, padding=defaultPadding)

    def _create_current_event_rewards(self, animate_progress = True):
        parent_container = self.current_event_container
        if self.current_event_rewards_wrapper_container:
            self.current_event_rewards_wrapper_container.Flush()
            self.current_event_rewards_wrapper_container.Close()
        is_layout_in_one_row = self._is_default_width(self.width)
        if is_layout_in_one_row:
            self._create_current_event_rewards_content(parent_container, animate_progress, one_row=True)
            return
        self._create_current_event_rewards_content(parent_container, animate_progress, one_row=False)

    def _create_current_event_rewards_content(self, parent_container, animate_progress = True, one_row = True):
        container_height = DEFAULT_HEIGHT_CURRENT_EVENTS_REWARDS
        container_top = DEFAULT_TOP_CURRENT_EVENT_INFO - DEFAULT_HEIGHT_CURRENT_EVENTS_REWARDS
        if not one_row:
            container_height += DEFAULT_HEIGHT_CURRENT_EVENTS_REWARDS
            container_top -= DEFAULT_HEIGHT_CURRENT_EVENTS_REWARDS
        self.current_event_rewards_wrapper_container = Container(name='current_event_rewards_wrapper_container', parent=parent_container, align=uiconst.ANCH_CENTERTOP, width=self.width - NEXT_REWARD_PREVIEW_LEFT, height=container_height, top=container_top, left=DEFAULT_LEFT_CURRENT_EVENT_INFO)
        fill_container_with_color_and_opacity(self.current_event_rewards_wrapper_container, CURRENT_EVENT_BACKGROUND_COLOR, CURRENT_EVENT_REWARDS_BACKGROUND_OPACITY)
        top_container_align = uiconst.TOLEFT if one_row else uiconst.ANCH_CENTERTOP
        current_event_rewards_container_top = Container(name='current_event_rewards_container_top', parent=self.current_event_rewards_wrapper_container, align=top_container_align, width=self.current_event_rewards_wrapper_container.width, height=DEFAULT_HEIGHT_CURRENT_EVENTS_REWARDS)
        current_event_rewards_container_bot = None
        if not one_row:
            current_event_rewards_container_bot = Container(name='current_event_rewards_container_bot', parent=self.current_event_rewards_wrapper_container, align=uiconst.ANCH_CENTERTOP, width=self.current_event_rewards_wrapper_container.width, height=DEFAULT_HEIGHT_CURRENT_EVENTS_REWARDS, top=DEFAULT_HEIGHT_CURRENT_EVENTS_REWARDS)
        season_points_wrapper_container = Container(name='season_points_wrapper_container', parent=current_event_rewards_container_top, align=uiconst.TOLEFT, width=SEASON_POINTS_WIDTH, height=SEASON_POINTS_HEIGHT)
        add_season_points_corner_gradient(season_points_wrapper_container, SEASON_POINTS_GRADIENT_LEFT)
        self.season_points_container = SeasonPoints(name='season_points_container', parent=season_points_wrapper_container, points=self.season_service.get_points(), align=uiconst.TOLEFT, season_points_size=SEASON_POINTS_HEIGHT, reward_label_class=EveLabelLargeBold, reward_label_fontsize=SEASON_POINTS_FONTSIZE, top=CURRENT_EVENT_REWARDS_TOP)
        progress_bar_parent = current_event_rewards_container_top if one_row else current_event_rewards_container_bot
        progress_bar_width = self._get_padded_size(PROGRESS_BAR_WIDTH, defaultPadding + DEFAULT_PADDING)
        progress_bar_align = uiconst.TOLEFT if one_row else uiconst.CENTERTOP
        progress_bar_top = CURRENT_EVENT_REWARDS_TOP
        if not one_row:
            progress_bar_top -= defaultPadding
        SeasonProgressBar(name='rewards_progress_bar_container', parent=progress_bar_parent, season_service=self.season_service, align=progress_bar_align, width=progress_bar_width, height=DEFAULT_HEIGHT_CURRENT_EVENTS_REWARDS, progress_bar_width=progress_bar_width, progress_bar_height=PROGRESS_BAR_HEIGHT, use_settings_to_recover_last_progress=True, animate_progress=animate_progress, top=progress_bar_top)
        next_reward_preview_wrapper = Container(name='next_reward_preview_wrapper', parent=current_event_rewards_container_top, align=uiconst.TORIGHT, width=NEXT_REWARD_PREVIEW_SIZE, height=NEXT_REWARD_PREVIEW_SIZE, left=NEXT_REWARD_PREVIEW_LEFT)
        NextRewardPreview(name='next_reward_preview_container', parent=next_reward_preview_wrapper, season_service=self.season_service, align=uiconst.TOBOTTOM, width=NEXT_REWARD_PREVIEW_SIZE, height=NEXT_REWARD_PREVIEW_SIZE, padBottom=NEXT_REWARD_PADDING)
        NextRewardInfo(name='next_reward_info_container', parent=current_event_rewards_container_top, season_service=self.season_service, align=uiconst.TORIGHT, width=NEXT_REWARD_WIDTH, height=NEXT_REWARD_HEIGHT, padding=DEFAULT_PADDING, top=CURRENT_EVENT_REWARDS_TOP)

    def _create_current_event_banner(self):
        parent_container = self.current_event_container
        if self.current_event_banner_wrapper:
            self.current_event_banner_wrapper.Flush()
            self.current_event_banner_wrapper.Close()
        self.current_event_banner_wrapper = Container(name='current_event_banner_wrapper', parent=parent_container, align=uiconst.TOTOP, width=self.width, height=DEFAULT_HEIGHT_CURRENT_EVENT_BANNER, clipChildren=True)
        CurrentEventBanner(name='current_event_banner_container', parent=self.current_event_banner_wrapper, banner_texture=self.current_event_banner_texture, align=uiconst.TOTOP, width=self.current_event_banner_wrapper.width, height=self.current_event_banner_wrapper.height, clipChildren=True)

    def _create_challenges_view(self):
        challenges_header_container = Container(name='challenges_header_container', parent=self.main_container, align=uiconst.TOTOP, width=DEFAULT_WIDTH, height=DEFAULT_HEIGHT_CURRENT_EVENTS_TITLE)
        fill_header_background_color_for_container(challenges_header_container)
        challenges_header_label_container = Container(name='challenges_header_label_container', parent=challenges_header_container, align=uiconst.TOTOP, width=DEFAULT_WIDTH, height=DEFAULT_HEIGHT_CURRENT_EVENTS_TITLE, padding=(DEFAULT_PADDING,
         0,
         DEFAULT_PADDING,
         0))
        challenges_label = EveLabelMedium(name='challenges_label', parent=challenges_header_label_container, align=uiconst.CENTERLEFT, text=localization.GetByLabel('UI/Seasons/ActiveChallenges'), bold=True)
        challenges_label.color = SEASON_THEME_TEXT_COLOR_REGULAR
        self._load_challenges()
        self._redraw_challenges()

    def _load_challenges(self):
        self.challenges = self.season_service.get_active_challenges_by_character_id()
        self.challenges_height_one_column, self.challenge_entries_height_one_column = calculate_challenges_height(challenges=self.challenges, challenge_text_width=self._get_padded_size(CHALLENGE_WIDTH), are_challenges_in_two_columns=False)
        self.challenges_height_two_columns, self.challenge_entries_height_two_columns = calculate_challenges_height(challenges=self.challenges, challenge_text_width=self._get_padded_size(CHALLENGE_WIDTH), are_challenges_in_two_columns=True)

    def _get_challenges_height(self):
        number_of_challenges = len(self.challenges)
        if self._are_challenges_in_two_columns():
            return self.challenges_height_two_columns + (number_of_challenges / 2 + 1) * defaultPadding
        return self.challenges_height_one_column + (number_of_challenges + 1) * defaultPadding

    def _get_challenge_entries_height(self):
        if self._are_challenges_in_two_columns():
            return self.challenge_entries_height_two_columns
        return self.challenge_entries_height_one_column

    def _redraw_challenges(self, animate_progress = True):
        if self.challenges_scroll_wrapper_container:
            self.challenges_scroll_wrapper_container.Flush()
            self.challenges_scroll_wrapper_container.Close()
        self.challenge_entries.clear()
        self.challenges_scroll_wrapper_container = Container(name='challenges_scroll_wrapper_container', parent=self.main_container, align=uiconst.TOLEFT, width=self._get_padded_size(self.width, defaultPadding), height=DEFAULT_HEIGHT_CHALLENGES, padding=defaultPadding)
        number_of_challenges = len(self.challenges)
        if number_of_challenges == 0:
            return
        self._redraw_challenges_scroll(animate_progress)

    def _redraw_challenges_scroll(self, animate_progress = True):
        challenges_scroll_height = self._get_challenges_height()
        self.challenges_scroll_container = ScrollContainer(name='challenges_scroll_container', parent=self.challenges_scroll_wrapper_container, align=uiconst.TOLEFT, width=self.challenges_scroll_wrapper_container.width, height=challenges_scroll_height)
        self.challenges_container = Container(name='challenges_container', parent=self.challenges_scroll_container, align=uiconst.TOTOP, width=self.challenges_scroll_container.width, height=challenges_scroll_height)
        fill_default_background_color_for_container(self.challenges_container)
        challenges_grid = Container(name='challenges_grid', parent=self.challenges_container, align=uiconst.TOTOP, width=self._get_padded_size(self.challenges_container.width), height=self._get_padded_size(challenges_scroll_height), padding=(defaultPadding,
         defaultPadding,
         defaultPadding,
         defaultPadding))
        if self._are_challenges_in_two_columns():
            self._redraw_challenges_in_two_columns(parent_container=challenges_grid, animate_progress=animate_progress)
            return
        self._redraw_challenges_in_one_column(parent_container=challenges_grid, animate_progress=animate_progress)

    def _redraw_challenges_in_one_column(self, parent_container, animate_progress):
        challenge_top = 0
        challenge_count = 1
        challenge_width = self._get_padded_size(CHALLENGE_WIDTH)
        for challenge in self.challenges.itervalues():
            challenge_height, title_text_height, description_text_height = self._get_challenge_entries_height()[challenge.challenge_id]
            challenge_height += defaultPadding
            self.challenge_entries[challenge.challenge_id] = ChallengeTaskEntry(name='challengetaskentry_%s' % challenge.challenge_id, parent=parent_container, align=uiconst.TOPLEFT, width=challenge_width, height=challenge_height, challenge=challenge, challenge_title_height=title_text_height, challenge_description_height=description_text_height, progress_frame_width=self._get_padded_size(PROGRESS_FRAME_WIDTH), progress_frame_width_reduction=PROGRESS_FRAME_WIDTH_REDUCTION, animate_progress=animate_progress, padRight=defaultPadding, padBottom=defaultPadding, top=challenge_top)
            challenge_top += challenge_height
            challenge_count += 1

    def _redraw_challenges_in_two_columns(self, parent_container, animate_progress):
        challenge_count, challenges_in_column_one, challenges_in_column_two = self._get_challenges_in_two_columns()
        challenge_top = 0
        number_of_rows = challenge_count / 2
        for row in xrange(0, number_of_rows):
            challenge_width = self._get_padded_size(CHALLENGE_WIDTH)
            challenge_one_height = self._redraw_challenge_in_column_one_and_get_height(row, challenges_in_column_one, parent_container, challenge_width, challenge_top, animate_progress)
            if row < len(challenges_in_column_two):
                challenge_two_height = self._redraw_challenge_in_column_two_and_get_height(row, challenges_in_column_two, parent_container, challenge_width, challenge_top, animate_progress)
                challenge_top += max(challenge_one_height, challenge_two_height)

    def _get_challenges_in_two_columns(self):
        challenge_count = 1
        challenges_in_column_one = []
        challenges_in_column_two = []
        for challenge_id in self.challenges.keys():
            if challenge_count % 2:
                challenges_in_column_one.append(challenge_id)
            else:
                challenges_in_column_two.append(challenge_id)
            challenge_count += 1

        return (challenge_count, challenges_in_column_one, challenges_in_column_two)

    def _redraw_challenge_in_column_one_and_get_height(self, row, challenges_in_column_one, parent_container, challenge_width, challenge_top, animate_progress):
        challenge_one_id = challenges_in_column_one[row]
        challenge_one_height, challenge_one_title_text_height, challenge_one_description_text_height = self._get_challenge_entries_height()[challenge_one_id]
        challenge_one_height += defaultPadding
        self._redraw_challenge(parent_container=parent_container, challenge_id=challenge_one_id, width=challenge_width, height=challenge_one_height, title_height=challenge_one_title_text_height, description_height=challenge_one_description_text_height, top=challenge_top, left=0, animate_progress=animate_progress)
        return challenge_one_height

    def _redraw_challenge_in_column_two_and_get_height(self, row, challenges_in_column_two, parent_container, challenge_width, challenge_top, animate_progress):
        challenge_two_id = challenges_in_column_two[row]
        challenge_two_height, challenge_two_title_text_height, challenge_two_description_text_height = self._get_challenge_entries_height()[challenge_two_id]
        challenge_two_height += defaultPadding
        self._redraw_challenge(parent_container=parent_container, challenge_id=challenge_two_id, width=challenge_width, height=challenge_two_height, title_height=challenge_two_title_text_height, description_height=challenge_two_description_text_height, top=challenge_top, left=challenge_width + defaultPadding, animate_progress=animate_progress)
        return challenge_two_height

    def _redraw_challenge(self, parent_container, challenge_id, width, height, title_height, description_height, top, left, animate_progress):
        challenge = self.challenges[challenge_id]
        self.challenge_entries[challenge_id] = ChallengeTaskEntry(name='challengetaskentry_%s' % challenge_id, parent=parent_container, align=uiconst.TOPLEFT, width=width, height=height, challenge=challenge, challenge_title_height=title_height, challenge_description_height=description_height, progress_frame_width=self._get_padded_size(PROGRESS_FRAME_WIDTH), progress_frame_width_reduction=PROGRESS_FRAME_WIDTH_REDUCTION, animate_progress=animate_progress, padRight=defaultPadding, padBottom=defaultPadding, top=top, left=left)

    def _are_challenges_in_two_columns(self):
        return self._is_default_width(self.width)

    def OnChallengeProgressUpdateInClient(self, challenge_id, new_progress):
        self.challenge_entries[challenge_id].update_challenge_progress(new_progress)

    def OnSeasonalPointsUpdatedInClient(self, season_points):
        self.season_points_container.update_points(season_points)

    def OnSeasonalGoalCompletedInClient(self, goal_id, goal_data):
        self.season_reward.show_finished_goals()

    def OnSeasonalGoalsResetInClient(self):
        self.OnSeasonalPointsUpdatedInClient(0)

    def OnChallengeCompletedInClient(self, old_challenge_id):
        self.challenge_entries[old_challenge_id].complete_challenge()
        self._load_challenges()
        self._redraw_challenges()

    def OnChallengeExpiredInClient(self, old_challenge_id):
        self._load_challenges()
        self._redraw_challenges()

    def OnResizeUpdate(self, *args):
        is_current_event_rewards_redraw_required = self._is_current_event_rewards_redraw_required_on_resize()
        is_challenge_redraw_required = self._is_challenge_redraw_required_on_resize()
        is_current_event_texture_change_required = self._is_current_event_texture_change_required_on_resize()
        self.last_width = self.width
        if is_current_event_texture_change_required:
            self._load_current_event_banner_texture()
        self._resize_header()
        self._resize_current_event_rewards(is_current_event_rewards_redraw_required)
        self._resize_current_event_banner(is_current_event_rewards_redraw_required)
        self._resize_challenges(is_challenge_redraw_required)
        self._resize_season_rewards_overlay(is_current_event_rewards_redraw_required)

    def _is_current_event_rewards_redraw_required_on_resize(self):
        return self.last_width != self.width

    def _is_challenge_redraw_required_on_resize(self):
        is_current_layout_mode_default = self._is_default_width(self.width)
        was_last_layout_mode_default = self._is_default_width(self.last_width)
        return was_last_layout_mode_default != is_current_layout_mode_default

    def _is_current_event_texture_change_required_on_resize(self):
        is_current_layout_mode_minimal = self._is_minimal_width(self.width)
        was_last_layout_mode_minimal = self._is_minimal_width(self.last_width)
        return is_current_layout_mode_minimal != was_last_layout_mode_minimal

    def _resize_header(self):
        self.header_info_container.width = self._get_padded_size(self.width - HEADER_ICON_CONTAINER_WIDTH, DEFAULT_PADDING)
        self.header_instructions_container.width = self._get_padded_size(self.width, 2 * DEFAULT_PADDING)

    def _resize_current_event_rewards(self, is_redraw_required = False):
        if is_redraw_required:
            self._create_current_event_rewards(animate_progress=False)

    def _resize_current_event_banner(self, is_redraw_required = False):
        if is_redraw_required:
            self._create_current_event_banner()

    def _resize_challenges(self, is_redraw_required = False):
        if self.challenges_scroll_container is not None:
            self.challenges_scroll_container.width = self._get_padded_size(self.width, defaultPadding)
        if is_redraw_required:
            self._redraw_challenges(animate_progress=False)

    def _resize_season_rewards_overlay(self, is_redraw_required = False):
        self.season_reward.resize(self.width, self.height)
