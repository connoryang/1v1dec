#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\seasons\client\seasoncharacterselectionsidebar.py
import math
import util
import trinity
import localization
import carbonui.const as uiconst
from carbonui.uianimations import animations
from carbonui.primitives.container import Container
from carbonui.control.scrollContainer import ScrollContainer
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.fill import Fill
from carbonui.primitives.line import Line
from carbonui.primitives.sprite import Sprite
from gametime.ingameclock import InGameClock
from eve.client.script.ui.control.eveLabel import Label, EveLabelLargeBold, EveLabelMediumBold
from seasons.client import const as season_client_const
from seasons.client.challengetaskentry import ChallengeTaskEntry, calculate_challenge_height
from seasons.client.seasoncharacterselectioncurrentevent import CurrentEvent
from seasons.client.uiutils import fill_default_background_color_for_container, fill_header_background_color_for_container
from seasons.client.uiutils import add_base_border_line_to_container
from seasons.client.uiutils import SEASON_DEFAULT_BORDER_LINE_WEIGHT, SEASON_DEFAULT_BORDER_LINE_COLOR, SEASONS_THEME_BACKGROUND_COLOR
import uthread
SEASON_BAR_WIDTH = 350
SEASON_BASE_PADDING = 6
SEASON_TITLE_HEIGHT = 50
SCOPE_LOGO_WIDTH = 40
SEASON_TITLE_LABEL_HEIGHT = 20
SEASON_TITLE_DESCRIPTION_HEIGHT = 20
CLOCK_WIDTH = 40
CLOCK_LABEL_SIZE = 11
FLOATING_NEWS_HEIGHT = 20
FLOATING_NEWS_ANIMATION_DURATION = 5
FLOATING_NEWS_COLOR = (0.549, 0.604, 0.718, 1.0)
SEASON_EXPANDER_HEIGHT = 20
SEASON_EXPANDER_LABEL_TEXT = localization.GetByLabel('UI/Seasons/CurrentEvent')
SEASON_EXPANDER_ARROW_RES_PATH = 'res:/UI/Texture/classes/Neocom/arrowDown.png'
SEASON_EXPANDER_SPRITE_SIZE = 7
CHALLENGES_HEADER_LABEL_HEIGHT = 20
CHALLENGES_HEADER_LABEL_TEXT = localization.GetByLabel('UI/Seasons/ActiveChallenges')
CHALLENGES_HEADER_FONTSIZE = 10
CHALLENGES_HEADER_PAD_TOP = 2
CHALLENGES_HEADER_PAD_BOT = 4
CHALLENGE_HEIGHT = 150
CHALLENGE_PROGRESS_FRAME_WIDTH_REDUCTION = 9
CHALLENGE_PROGRESS_BAR_PADDING = 7
CHALLENGE_PADDING = 4
CHALLENGE_ADDITIONAL_PADDING = 34
CHALLENGES_PAD_TOP = 10
CHALLENGE_BOTTOM_PADDING = 8
SCROLL_PADDING = 7
SEASON_DETAILS_PADDING = 1
SEASON_DETAILS_HEIGHT = 300
NEXT_EVENT_HEIGHT = 125
PANEL_FADE_DURATION = 0.15
MINIMUM_SCREEN_WIDTH = 1535
SEASON_BAR_BACKGROUND_COLOR = (0.137, 0.196, 0.302, 0.25)

class SeasonCharacterSelectionSidebar(Container):
    default_align = uiconst.TORIGHT_NOPUSH
    default_width = SEASON_BAR_WIDTH
    season_container = None

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.season_sidebar_fill = Fill(bgParent=self, color=SEASON_BAR_BACKGROUND_COLOR)
        self.redeemable_items_panel_height = attributes.redeemable_items_panel_height
        self.hide_season = True if trinity.device.width < MINIMUM_SCREEN_WIDTH else False
        self.season_sidebar_fill.display = not self.hide_season

    def load_data(self):
        self.season_service = sm.GetService('seasonService')
        self._construct_season_header()
        self._construct_floating_news()
        self._construct_season_expander()
        self.clock.update_clock()
        self.floating_news_thread = None
        self._construct_season()

    def _construct_season_header(self):
        season_header_container = Container(name='season_header_container', parent=self, align=uiconst.TOTOP, height=SEASON_TITLE_HEIGHT)
        add_base_border_line_to_container(season_header_container, uiconst.TOLEFT)
        add_base_border_line_to_container(season_header_container, uiconst.TOBOTTOM)
        season_header_content_container = Container(name='season_header_container', parent=season_header_container, align=uiconst.TOTOP, height=season_header_container.height)
        fill_default_background_color_for_container(season_header_content_container)
        Fill(bgParent=season_header_content_container, color=SEASONS_THEME_BACKGROUND_COLOR)
        season_top_container = Container(name='season_top_container', parent=season_header_content_container, align=uiconst.TOTOP, height=SEASON_TITLE_HEIGHT)
        Line(parent=season_top_container, align=uiconst.TOBOTTOM, weight=1)
        scope_logo_container = Container(name='scope_logo_container', parent=season_top_container, align=uiconst.TOLEFT, width=SCOPE_LOGO_WIDTH, padBottom=SEASON_BASE_PADDING, padLeft=SEASON_BASE_PADDING)
        Sprite(name='scope_logo', parent=scope_logo_container, texturePath=season_client_const.SCOPE_LOGO_RES_PATH, align=uiconst.TOALL)
        clock_container = Container(name='clock_container', parent=season_top_container, align=uiconst.TORIGHT, width=CLOCK_WIDTH)
        self.clock = InGameClock(parent=clock_container, align=uiconst.TOALL, label_font_size=CLOCK_LABEL_SIZE)
        scope_title_container = Container(name='scope_title_container', parent=season_top_container, align=uiconst.TOTOP, height=SEASON_TITLE_LABEL_HEIGHT, padLeft=SEASON_BASE_PADDING, padTop=SEASON_BASE_PADDING)
        EveLabelLargeBold(name='scope_title_label', parent=scope_title_container, text=season_client_const.get_seasons_title())
        scope_title_description_container = Container(name='scope_title_description_container', parent=season_top_container, align=uiconst.TOTOP, height=SEASON_TITLE_DESCRIPTION_HEIGHT, padLeft=SEASON_BASE_PADDING)
        Label(name='scope_title_description_label', parent=scope_title_description_container, text=season_client_const.get_seasons_subcaption(), align=uiconst.TOPLEFT, fontsize=10)

    def _construct_floating_news(self):
        self.season_floating_news_container = Container(name='season_floating_news_container', parent=self, align=uiconst.TOTOP, height=FLOATING_NEWS_HEIGHT, clipChildren=True)
        add_base_border_line_to_container(self.season_floating_news_container, uiconst.TOLEFT)
        add_base_border_line_to_container(self.season_floating_news_container, uiconst.TOBOTTOM)
        self.season_floating_news_content_container = Container(name='season_floating_news_container', parent=self.season_floating_news_container, align=uiconst.TOTOP, height=self.season_floating_news_container.height)
        Fill(bgParent=self.season_floating_news_content_container, color=SEASONS_THEME_BACKGROUND_COLOR)
        self.floating_news_thread = uthread.new(self._float_the_news)

    def _construct_float_news_label(self):
        self.season_floating_news_content_container.Flush()
        self.floating_news_label = Label(name='floating_news_label', parent=self.season_floating_news_content_container, align=uiconst.CENTERLEFT)
        self.floating_news_label.color = FLOATING_NEWS_COLOR

    def _float_the_news(self):
        news = self.season_service.get_season_news()
        while not self.destroyed:
            for newsString in news:
                self._construct_float_news_label()
                self.floating_news_label.SetText(newsString)
                width_factor = float(self.floating_news_label.width) / float(SEASON_BAR_WIDTH)
                animation_duration = FLOATING_NEWS_ANIMATION_DURATION * width_factor
                animations.MoveInFromRight(self.floating_news_label, SEASON_BAR_WIDTH, curveType=uiconst.ANIM_LINEAR, duration=FLOATING_NEWS_ANIMATION_DURATION, sleep=True)
                animations.MoveOutLeft(self.floating_news_label, self.floating_news_label.width, curveType=uiconst.ANIM_LINEAR, duration=animation_duration, sleep=True)

    def _construct_season_expander(self):
        expander_container = Container(name='expander_container', parent=self, align=uiconst.TOTOP, height=SEASON_EXPANDER_HEIGHT)
        add_base_border_line_to_container(expander_container, uiconst.TOLEFT)
        self.expander_bottom_line = Line(parent=expander_container, align=uiconst.TOBOTTOM, weight=SEASON_DEFAULT_BORDER_LINE_WEIGHT, color=SEASON_DEFAULT_BORDER_LINE_COLOR, state=uiconst.UI_HIDDEN)
        expander_content_container = Container(name='expander_container', parent=expander_container, align=uiconst.TOTOP, height=expander_container.height, state=uiconst.UI_NORMAL)
        fill_default_background_color_for_container(expander_content_container)
        EveLabelMediumBold(name='expander_label', parent=expander_content_container, text=SEASON_EXPANDER_LABEL_TEXT, align=uiconst.CENTERLEFT, padLeft=SEASON_BASE_PADDING)
        expander_sprite_container = Container(name='expander_sprite_container', parent=expander_content_container, align=uiconst.TORIGHT, width=SEASON_EXPANDER_SPRITE_SIZE, padRight=SEASON_BASE_PADDING)
        self.expander_sprite = Sprite(name='expander_sprite', parent=expander_sprite_container, texturePath=SEASON_EXPANDER_ARROW_RES_PATH, align=uiconst.CENTER, width=SEASON_EXPANDER_SPRITE_SIZE, height=SEASON_EXPANDER_SPRITE_SIZE)
        expander_content_container.OnClick = self._toggle_display_season
        self.expander_sprite.OnClick = self._toggle_display_season

    def _toggle_display_season(self):
        if not self.season_container:
            self.expander_bottom_line.Hide()
            self._construct_season()
            return
        if self.season_container.display:
            self.expander_sprite.rotation = math.pi
            uicore.animations.FadeOut(self.season_container, duration=PANEL_FADE_DURATION)
            self.expander_bottom_line.Show()
        self.season_container.display = not self.season_container.display
        self.season_sidebar_fill.display = not self.season_sidebar_fill.display
        if self.season_container.display:
            self.expander_sprite.rotation = 0
            self.expander_bottom_line.Hide()
            uicore.animations.FadeIn(self.season_container, duration=PANEL_FADE_DURATION)

    def _construct_season(self):
        if self.season_container and not self.season_container.destroyed:
            return
        self.season_container = Container(name='season_container', parent=self, align=uiconst.TOTOP, height=uicore.desktop.height - SEASON_TITLE_HEIGHT - FLOATING_NEWS_HEIGHT - SEASON_EXPANDER_HEIGHT - CHALLENGE_ADDITIONAL_PADDING, bgColor=util.Color.BLACK if self.hide_season else None, opacity=0 if self.hide_season else 1)
        self.season_container.display = not self.hide_season
        self.expander_bottom_line.display = self.hide_season
        add_base_border_line_to_container(self.season_container, uiconst.TOLEFT)
        add_base_border_line_to_container(self.season_container, uiconst.TOBOTTOM)
        self.season_container_scroll = ScrollContainer(name='season_container_scroll', parent=self.season_container, align=uiconst.TOTOP, height=self.season_container.height)
        self._construct_season_details(parent_container=self.season_container_scroll)
        self._construct_challenges(parent_container=self.season_container_scroll)

    def _construct_season_details(self, parent_container):
        CurrentEvent(name='season_details_container', parent=parent_container, season_service=self.season_service, align=uiconst.TOTOP, width=SEASON_BAR_WIDTH - 2 * SEASON_DETAILS_PADDING - SCROLL_PADDING, height=SEASON_DETAILS_HEIGHT, padding=SEASON_DETAILS_PADDING)

    def _construct_challenges(self, parent_container):
        challenges_container = Container(name='challenges_container', parent=parent_container, align=uiconst.TOTOP, height=CHALLENGE_ADDITIONAL_PADDING, padTop=CHALLENGES_PAD_TOP)
        challenges_content_container = ContainerAutoSize(name='challenges_content_container', parent=challenges_container, align=uiconst.TOTOP, height=challenges_container.height)
        challenges_header_container = Container(name='challenges_header_container', parent=challenges_content_container, align=uiconst.TOTOP, height=CHALLENGES_HEADER_LABEL_HEIGHT, padBottom=CHALLENGES_HEADER_PAD_BOT)
        fill_header_background_color_for_container(challenges_header_container)
        Label(name='challenges_label', parent=challenges_header_container, align=uiconst.TOTOP, text=CHALLENGES_HEADER_LABEL_TEXT, bold=True, fontize=CHALLENGES_HEADER_FONTSIZE, padTop=CHALLENGES_HEADER_PAD_TOP, padLeft=SEASON_BASE_PADDING)
        challenges = self.season_service.get_challenges_for_last_active_character()
        challenge_width = SEASON_BAR_WIDTH - CHALLENGE_PROGRESS_BAR_PADDING - 2 * CHALLENGE_PADDING
        for challenge in challenges.itervalues():
            challenge_height, title_text_height, description_text_height = calculate_challenge_height(challenge, challenge_width)
            challenge_task_entry_container = Container(name='challenge_task_entry_container', parent=challenges_content_container, align=uiconst.TOTOP, width=challenge_width, height=challenge_height, padding=CHALLENGE_PADDING)
            ChallengeTaskEntry(name='challengetaskentry_%s' % challenge.challenge_id, parent=challenge_task_entry_container, align=uiconst.TOTOP, width=challenge_width, height=challenge_height, challenge=challenge, challenge_title_height=title_text_height, challenge_description_height=description_text_height, progress_frame_width=challenge_width, progress_frame_width_reduction=CHALLENGE_PROGRESS_FRAME_WIDTH_REDUCTION, padBottom=CHALLENGE_BOTTOM_PADDING)
            challenges_container.height += challenge_height + CHALLENGE_BOTTOM_PADDING

    def reconstruct_season(self):
        if self.season_container and not self.season_container.destroyed:
            self._remove_season()
        else:
            self._construct_season()

    def _remove_season(self):
        if self.season_container and not self.season_container.destroyed:
            self.expander_bottom_line.Show()
            season_container = self.season_container
            self.season_container = None
            uicore.animations.FadeOut(season_container, duration=PANEL_FADE_DURATION)
            uicore.animations.MorphScalar(season_container, 'height', season_container.height, 0, duration=PANEL_FADE_DURATION, callback=season_container.Close)
