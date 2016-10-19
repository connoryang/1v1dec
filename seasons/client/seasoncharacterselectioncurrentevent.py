#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\seasons\client\seasoncharacterselectioncurrentevent.py
import carbonui.const as uiconst
from carbonui.primitives.container import Container
from eve.client.script.ui.control.eveLabel import EveLabelLargeBold
from eve.common.lib.appConst import defaultPadding
from seasons.client.currenteventbanner import CurrentEventBanner
from seasons.client.nextrewardinfo import NextRewardInfo
from seasons.client.nextrewardpreview import NextRewardPreview
from seasons.client.seasonpoints import SeasonPoints
from seasons.client.seasonprogressbar import SeasonProgressBar
from seasons.client.seasonremainingtime import SeasonRemainingTime
from seasons.client.uiutils import fill_default_background_color_for_container, add_season_points_corner_gradient
SEASON_MAIN_REWARD_ICON_SIZE = 80
SEASON_DETAILS_HEADER_TOP_HEIGHT = 30
SEASON_BANNER_TOP = 10
SEASON_DETAILS_FIRST_LINE_HEIGHT = 40
SEASON_DETAILS_THIRD_LINE_HEIGHT = 20
PROGRESS_BAR_PADDING = 15
SEASON_INFO_SECOND_LINE_PADDING_TOP = 10
SEASON_INFO_THIRD_LINE_PADDING = 10
SEASON_INFO_THIRD_LINE_TOP = -10
SEASON_DETAILS_BANNER_PADDING = 1
SEASON_INFO_PADDING = 10
SEASON_POINTS_ICON_SIZE = 32
SEASON_POINTS_GRADIENT_LEFT = 0
NEXT_REWARD_LEFT = SEASON_MAIN_REWARD_ICON_SIZE + defaultPadding + 8

class CurrentEvent(Container):

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.season_service = attributes.season_service
        season_details_content_container = Container(name='season_details_content_container', parent=self, align=uiconst.TOPLEFT, width=self.width, height=self.height)
        fill_default_background_color_for_container(season_details_content_container)
        self._create_next_reward_preview(parent_container=season_details_content_container)
        self._create_event_banner(parent_container=season_details_content_container)
        self._create_season_info(parent_container=season_details_content_container)

    def _create_next_reward_preview(self, parent_container):
        NextRewardPreview(name='season_main_reward_container', parent=parent_container, season_service=self.season_service, align=uiconst.TORIGHT_NOPUSH, width=SEASON_MAIN_REWARD_ICON_SIZE, height=SEASON_MAIN_REWARD_ICON_SIZE, padding=defaultPadding)

    def _create_event_banner(self, parent_container):
        SEASON_DETAILS_BANNER_HEIGHT = float(parent_container.height) / 2 - SEASON_INFO_PADDING
        SEASON_DETAILS_HEADER_HEIGHT = SEASON_DETAILS_BANNER_HEIGHT / 2
        season_details_top_container = Container(name='season_details_top_container', parent=parent_container, align=uiconst.TOTOP, height=SEASON_DETAILS_BANNER_HEIGHT, clipChildren=True, padding=SEASON_DETAILS_BANNER_PADDING)
        season_details_header_container = Container(name='season_details_header_container', parent=season_details_top_container, align=uiconst.CENTER, height=SEASON_DETAILS_HEADER_HEIGHT, width=self.width)
        fill_default_background_color_for_container(season_details_header_container)
        current_event_banner_container = Container(name='season_details_banner_container', parent=season_details_header_container, align=uiconst.TOTOP, height=SEASON_DETAILS_HEADER_HEIGHT, width=self.width)
        CurrentEventBanner(name='season_details_top_banner_container', parent=current_event_banner_container, banner_texture=self.season_service.get_season_background_minimal(), align=uiconst.CENTER, width=current_event_banner_container.width, top=SEASON_BANNER_TOP)

    def _create_season_info(self, parent_container):
        SEASON_DETAILS_INFO_HEIGHT = float(self.height) / 2
        SECOND_LINE_HEIGHT = SEASON_DETAILS_INFO_HEIGHT - SEASON_DETAILS_FIRST_LINE_HEIGHT - SEASON_DETAILS_THIRD_LINE_HEIGHT
        season_details_bottom_container = Container(name='season_details_bottom_container', parent=parent_container, align=uiconst.TOTOP, width=self.width, height=SEASON_DETAILS_INFO_HEIGHT)
        first_line_container = Container(name='first_line_container', parent=season_details_bottom_container, align=uiconst.TOTOP, width=season_details_bottom_container.width, height=SEASON_DETAILS_FIRST_LINE_HEIGHT)
        second_line_container = Container(name='second_line_container', parent=season_details_bottom_container, align=uiconst.TOTOP, width=season_details_bottom_container.width, height=SECOND_LINE_HEIGHT, padTop=SEASON_INFO_SECOND_LINE_PADDING_TOP)
        third_line_container = Container(name='third_line_container', parent=season_details_bottom_container, align=uiconst.TOTOP, width=season_details_bottom_container.width, height=SEASON_DETAILS_THIRD_LINE_HEIGHT, padding=(SEASON_INFO_THIRD_LINE_PADDING,
         0,
         SEASON_INFO_THIRD_LINE_PADDING,
         0), top=SEASON_INFO_THIRD_LINE_TOP)
        self._create_season_info_first_line(parent_container=first_line_container)
        self._create_season_info_second_line(parent_container=second_line_container)
        self._create_season_info_third_line(parent_container=third_line_container)

    def _create_season_info_first_line(self, parent_container):
        season_points_wrapper_container = Container(name='season_points_wrapper_container', parent=parent_container, align=uiconst.TOLEFT, width=float(parent_container.width) / 2, height=parent_container.height)
        add_season_points_corner_gradient(season_points_wrapper_container, SEASON_POINTS_GRADIENT_LEFT)
        self.season_points_container = SeasonPoints(name='season_points_container', parent=season_points_wrapper_container, points=self.season_service.get_points(), align=uiconst.TOLEFT, season_points_size=SEASON_POINTS_ICON_SIZE, reward_label_class=EveLabelLargeBold)
        NextRewardInfo(name='next_reward_info_container', parent=parent_container, season_service=self.season_service, align=uiconst.TOPRIGHT, width=float(parent_container.width) / 2 - NEXT_REWARD_LEFT, height=parent_container.height, left=NEXT_REWARD_LEFT)

    def _create_season_info_second_line(self, parent_container):
        progress_bar_width = parent_container.width - PROGRESS_BAR_PADDING
        progress_bar_height = 50
        SeasonProgressBar(name='rewards_progress_bar_container', parent=parent_container, season_service=self.season_service, align=uiconst.CENTER, width=progress_bar_width, height=parent_container.height, progress_bar_width=progress_bar_width, progress_bar_height=progress_bar_height, reward_points_label_on_top=False, use_settings_to_recover_last_progress=False, top=-15)

    def _create_season_info_third_line(self, parent_container):
        SeasonRemainingTime(name='current_event_time_container', parent=parent_container, season_service=self.season_service, align=uiconst.CENTERLEFT, width=float(parent_container.width) / 2, height=parent_container.height)
