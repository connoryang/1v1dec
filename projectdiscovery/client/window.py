#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\projectdiscovery\client\window.py
import logging
import math
import blue
import carbonui.const as uiconst
import const
import localization
import uicls
import uicontrols
import uiprimitives
import uthread
from carbon.common.script.util.format import FmtAmt
from carbonui.primitives.base import ScaleDpi
from carbonui.uianimations import animations
from eve.client.script.ui.control import themeColored
from eve.client.script.ui.control.eveWindow import Window
from eve.client.script.ui.tooltips.tooltipUtil import SetTooltipHeaderAndDescription
from projectdiscovery.client.const import Events
from projectdiscovery.client.projects.subcellular.subcellularatlas import SubcellularAtlas
from projectdiscovery.client.projects.subcellular.tutorial import Tutorial
from projectdiscovery.client.util.dialogue import Dialogue
from projectdiscovery.client.util.eventlistener import eventlistener, on_event
from projectdiscovery.client.util.tutorialtooltips import TutorialTooltips
from projectdiscovery.client.util.util import calculate_score_bar_length, calculate_rank_band
from projectdiscovery.common.const import INITIAL_PLAYER_SCORE, PLAYER_NOT_IN_DATABASE_ERROR_CODE
from projectdiscovery.common.exceptions import NoConnectionToAPIError, MissingKeyError
logger = logging.getLogger(__name__)

@eventlistener()

class ProjectDiscoveryWindow(Window):
    __guid__ = 'ProjectDiscoveryWindow'
    default_captionLabelPath = 'UI/Industry/Industry'
    default_descriptionLabelPath = 'UI/Industry/IndustryTooltip'
    default_caption = 'Project Discovery'
    default_windowID = 'ProjectDiscoveryWindow'
    default_iconNum = 'res:/UI/Texture/WindowIcons/projectdiscovery.png'
    default_topParentHeight = 0
    default_isStackable = False
    default_isCollapseable = False
    default_minSize = (900, 600)
    default_maxSize = (1250, 785)

    @on_event('OnWindowClosed')
    def on_window_closed(self, wndID, wndCaption, wndGUID):
        sm.GetService('audio').SendUIEvent(const.Sounds.MainImageLoopStop)
        sm.GetService('audio').SendUIEvent(const.Sounds.MainImageLoadStop)
        sm.GetService('audio').SendUIEvent(const.Sounds.RewardsWindowLoopStop)

    @on_event('OnWindowMinimized')
    def on_window_minimized(self, wnd):
        sm.GetService('audio').SendUIEvent(const.Sounds.MainImageLoopStop)
        sm.GetService('audio').SendUIEvent(const.Sounds.MainImageLoadStop)
        sm.GetService('audio').SendUIEvent(const.Sounds.RewardsWindowLoopStop)
        self._minimize_tutorial_tooltips()

    def _minimize_tutorial_tooltips(self):
        if self.tutorial_tooltips is not None:
            self.tutorial_tooltips.hide_tooltip()

    @on_event('OnWindowMaximized')
    def on_window_maximized(self, wnd, wasMinimized):
        sm.GetService('audio').SendUIEvent(const.Sounds.MainImageLoopPlay)
        self._maximize_tutorial_tooltips()

    def _maximize_tutorial_tooltips(self):
        if self.tutorial_tooltips is not None:
            self.tutorial_tooltips.show_tooltip()

    @on_event('OnProjectDiscoveryHeaderDragged')
    def on_drag_header(self):
        if not self.IsLocked():
            self._BeginDrag()

    @on_event('OnProjectDiscoveryMouseDownOnHeader')
    def on_mouse_down_header(self):
        self.dragMousePosition = (uicore.uilib.x, uicore.uilib.y)

    @on_event('OnProjectDiscoveryMouseEnterHeader')
    def on_mouse_enter_header(self):
        uicore.uilib.SetCursor(uiconst.UICURSOR_HASMENU)

    @on_event('OnProjectDiscoveryMouseExitHeader')
    def on_mouse_exit_header(self):
        uicore.uilib.SetCursor(uiconst.UICURSOR_POINTER)

    def OnResizeUpdate(self, *args):
        scale = self.get_scale()
        self.resize_background(scale)
        sm.ScatterEvent('OnProjectDiscoveryResized', scale)

    def get_scale(self):
        scale = self.width / float(self.default_minSize[0])
        if self.width > self.height * (self.default_minSize[0] / float(self.default_minSize[1])):
            scale = self.height / float(self.default_minSize[1])
        return scale

    def resize_background(self, scale):
        self.project_container.SetSize(self.original_project_width * scale, self.original_project_height * scale)
        self.gridBackground.SetSize(self.width, self.height)
        self.gridBackground.scale = (2 * (1 / scale), 2 * (1 / scale))
        self.gridBackground.scalingCenter = (0.5 * scale, 0.5)
        self.result_background.SetSize(self.width, self.height)
        self.result_background.scale = (2 * (1 / scale), 2 * (1 / scale))
        self.result_background.scalingCenter = (0.5 * scale, 0.5)

    def OnEndScale_(self, wnd, *args):
        sm.ScatterEvent('OnProjectDiscoveryEndResize')

    def OnStartScale_(self, wnd, *args):
        sm.ScatterEvent('OnProjectDiscoveryStartResize')

    def ApplyAttributes(self, attributes):
        super(ProjectDiscoveryWindow, self).ApplyAttributes(attributes)
        self.main = self.GetMainArea()
        self.isTraining = False
        self.projectdiscoverySvc = sm.RemoteSvc('ProjectDiscovery')
        settings.char.ui.Set('loadStatisticsAfterSubmission', False)
        self.tutorial = None
        self.project = None
        self.tutorial_tooltips = None
        self.playerState = self.projectdiscoverySvc.get_player_state()
        self.player_statistics = None
        try:
            self.player_statistics = self.projectdiscoverySvc.player_statistics(get_history=True)
        except (NoConnectionToAPIError, MissingKeyError):
            self.show_connection_error_dialogue()

        self.setup_layout()
        if self.player_statistics:
            uthread.new(self.load_project)

    def setup_layout(self):
        self.setup_side_panels()
        self.bottom_container = uiprimitives.Container(name='bottom_container', parent=self.sr.main, align=uiconst.TOBOTTOM, height=50)
        self.project_container = uiprimitives.Container(name='ProjectContainer', parent=self.main, align=uiconst.TOPLEFT, height=self.default_minSize[1], width=self.default_minSize[0], top=-20)
        self.original_project_height = self.project_container.height
        self.original_project_width = self.project_container.width
        self.show_background_grid()
        self.header = WindowHeader(parent=self.main.parent, align=uiconst.CENTERTOP, height=53, width=355, idx=0, top=2, bgTexturePath='res:/UI/Texture/classes/ProjectDiscovery/headerBG.png', playerState=self.playerState, playerStatistics=self.player_statistics)
        self.help_button = uicontrols.ButtonIcon(name='helpButton', parent=self.bottom_container, align=uiconst.BOTTOMLEFT, iconSize=22, width=22, height=22, texturePath='res:/UI/Texture/WindowIcons/question.png', func=lambda : self.start_tutorial())
        SetTooltipHeaderAndDescription(targetObject=self.help_button, headerText='', descriptionText=localization.GetByLabel('UI/ProjectDiscovery/HelpTutorialTooltip'))
        uthread.new(self.animate_background)

    def setup_side_panels(self):
        uiprimitives.Sprite(parent=self.main, align=uiconst.CENTERRIGHT, width=14, height=416, top=-20, texturePath='res:/UI/Texture/classes/ProjectDiscovery/sideElement.png')
        uiprimitives.Sprite(parent=uiprimitives.Transform(parent=self.main, align=uiconst.CENTERLEFT, width=14, height=416, top=-20, rotation=math.pi), align=uiconst.TOLEFT_NOPUSH, width=14, height=416, texturePath='res:/UI/Texture/classes/ProjectDiscovery/sideElement.png')

    @on_event(const.Events.NoConnectionToAPI)
    def show_connection_error_dialogue(self):
        self.dialogue = Dialogue(name='ConnectionErrorDialogue', parent=self.main, align=uiconst.CENTER, width=450, height=150, messageText=localization.GetByLabel('UI/ProjectDiscovery/ConnectionErrorDialogueMessage'), messageHeaderText=localization.GetByLabel('UI/ProjectDiscovery/ConnectionErrorDialogueHeader'), label=localization.GetByLabel('UI/ProjectDiscovery/NotificationHeader'), buttonLabel=localization.GetByLabel('UI/ProjectDiscovery/CloseProjectDiscoveryButtonLabel'), onCloseEvent=Events.CloseWindow)

    def load_project(self):
        if not self.playerState.finishedTutorial:
            uthread.new(self.start_tutorial)
        else:
            uthread.new(self.start_project, False)

    @on_event(Events.ProjectDiscoveryStarted)
    def start_project(self, show_dialogue):
        self._clear_tutorial_and_project()
        if self.destroyed:
            return
        self.help_button.Enable()
        self.project = SubcellularAtlas(parent=self.project_container, playerState=self.playerState, starting_scale=self.get_scale())
        self.project.start(show_dialogue)

    def start_tutorial(self):
        self._clear_tutorial_and_project()
        if self.destroyed:
            return
        if self.isTraining:
            self.start_tutorial_tooltips()
            return
        self.isTraining = True
        self.help_button.Disable()
        self.tutorial = Tutorial(parent=self.project_container, playerState=self.playerState, starting_scale=self.get_scale())
        self.tutorial.start()

    def _clear_tutorial_and_project(self):
        self._clear_tutorial()
        self._clear_project()

    def _clear_tutorial(self):
        if self.tutorial:
            self.tutorial.close()
            self.isTraining = False
            self.tutorial = None

    def _clear_project(self):
        if self.project:
            self.project.close()
            self.project = None

    @on_event(Events.StartTutorial)
    def start_tutorial_tooltips(self):
        if self.destroyed:
            return
        self.help_button.Enable()
        if not self.tutorial_tooltips:
            self.tutorial_tooltips = TutorialTooltips()
            if self.isTraining:
                self.tutorial_tooltips.add_steps(self.tutorial.get_tutorial_tooltip_steps())
            else:
                self.tutorial_tooltips.add_steps(self.project.get_tutorial_tooltip_steps())
            self.tutorial_tooltips.add_steps(self.get_tutorial_tooltip_steps())
        self.tutorial_tooltips.start()

    @on_event(Events.QuitTutorialTooltips)
    def close_tutorial_tooltips(self):
        self.tutorial_tooltips = None

    def get_tutorial_tooltip_steps(self):
        return [{'owner': self.header.rankIcon,
          'header': localization.GetByLabel('UI/ProjectDiscovery/Subcellular/Tutorial/RankIconHeader'),
          'text': localization.GetByLabel('UI/ProjectDiscovery/Subcellular/Tutorial/RankIconText')}, {'owner': self.header.accuracyRatingContainer,
          'header': localization.GetByLabel('UI/ProjectDiscovery/Subcellular/Tutorial/AccuracyRatingHeader'),
          'text': localization.GetByLabel('UI/ProjectDiscovery/Subcellular/Tutorial/AccuracyRatingText')}, {'owner': self.help_button,
          'header': localization.GetByLabel('UI/ProjectDiscovery/Subcellular/Tutorial/FooterButtonsHeader'),
          'text': localization.GetByLabel('UI/ProjectDiscovery/Subcellular/Tutorial/FooterButtonsText')}]

    def show_background_grid(self):
        self.gridContainer = uiprimitives.Container(name='gridContainer', parent=self.main, align=uiconst.TOALL, clipChildren=True, padBottom=-49)
        self.background_shade = uiprimitives.Sprite(name='background_shade', parent=self.gridContainer, align=uiconst.TOALL, texturePath='res:/UI/Texture/classes/ProjectDiscovery/backgroundShade.png', padTop=-20, padLeft=2, padRight=2, padBottom=0, opacity=0.5)
        self.gridBackground = uiprimitives.Sprite(name='gridBackground', parent=self.gridContainer, align=uiconst.TOPLEFT, texturePath='res:/UI/Texture/classes/ProjectDiscovery/hexBGTile.png', tileX=True, tileY=True, scale=(2, 2))
        self.gridBackground.scalingCenter = (0.4, 0.5)
        self.result_background = themeColored.SpriteThemeColored(name='gridBackgroundResult', parent=self.gridContainer, align=uiconst.TOPLEFT, texturePath='res:/UI/Texture/classes/ProjectDiscovery/hexBGTileResults.png', opacity=0, tileX=True, tileY=True)
        self.result_background.scalingCenter = (0.4, 0.5)
        self.fill = themeColored.FillThemeColored(name='backgroundFill', align=uiconst.TOALL, parent=self.main, padTop=-20, padLeft=2, padRight=2, padBottom=-50, opacity=1)

    def animate_background(self):
        animations.FadeTo(self.gridBackground, duration=1, curveType=uiconst.ANIM_OVERSHOT5)

    def close_background_grid(self):
        self.gridContainer.Flush()
        self.gridContainer.Close()

    @on_event(Events.PercentageCountFinished)
    def animate_result_background_in(self):
        animations.FadeOut(self.gridBackground, duration=0.5)
        animations.FadeIn(self.result_background, duration=1, curveType=uiconst.ANIM_OVERSHOT5, endVal=1.5)

    @on_event(Events.ContinueFromReward)
    def animate_normal_background(self):
        animations.FadeOut(self.result_background, duration=0.5)
        animations.FadeIn(self.gridBackground, duration=1, curveType=uiconst.ANIM_OVERSHOT5)

    @on_event(Events.ContinueFromTrainingResult)
    def animate_training_background(self):
        self.animate_normal_background()

    @on_event(Events.UpdateAnalysisKredits)
    def on_analysis_kredits_update(self):
        player_state = self.projectdiscoverySvc.get_player_state()
        self.header.update_analysis_kredits(player_state)

    @on_event(Events.RestartWindow)
    def restart_window(self):
        self.CloseByUser()
        uicore.cmd.ToggleProjectDiscovery()

    @on_event(Events.CloseWindow)
    def close_window(self):
        self.CloseByUser()


@eventlistener()

class WindowHeader(uiprimitives.Container):
    default_state = uiconst.UI_HIDDEN

    def ApplyAttributes(self, attributes):
        super(WindowHeader, self).ApplyAttributes(attributes)
        self.pdService = sm.RemoteSvc('ProjectDiscovery')
        self.playerState = attributes.get('playerState')
        self.player_statistics = attributes.get('playerStatistics')
        self.experience = self.playerState.experience
        self.rank = self.playerState.rank
        self.total_xp_needed_for_next_rank = self.pdService.get_total_needed_xp(self.rank + 1)
        self.total_xp_needed_for_current_rank = self.pdService.get_total_needed_xp(self.rank)
        self.full_needle_rotation = -4.7
        self.setup_layout()
        self.score = 0
        self.needle_Rotation = self.score * self.full_needle_rotation
        self.state = uiconst.UI_NORMAL
        self.update_header()

    def setup_layout(self):
        self.headerContainer = uiprimitives.Container(name='headerContainer', parent=self, align=uiconst.CENTERTOP, height=34, width=230)
        self.scoreBarContainer = uiprimitives.Container(name='scoreBarContainer', parent=self, align=uiconst.CENTERBOTTOM, height=8, width=self.headerContainer.width - 10, bgColor=(0.62, 0.54, 0.53, 0.26), top=10)
        self._initialize_score_bar_length()
        self.scoreBar = uicls.VectorLine(name='scoreBar', parent=self.scoreBarContainer, align=uiconst.CENTERLEFT, translationFrom=(0, 0), translationTo=(self.calculate_score_bar_length(), 0), colorFrom=(1.0, 1.0, 1.0, 0.95), colorTo=(1.0, 1.0, 1.0, 0.95), widthFrom=3, widthTo=3, left=3)
        uicls.VectorLine(name='emptyScoreBar', parent=self.scoreBarContainer, align=uiconst.CENTERLEFT, translationFrom=(0, 0), translationTo=(self.scoreBarLength, 0), colorFrom=(0.0, 0.0, 0.0, 0.75), colorTo=(0.0, 0.0, 0.0, 0.75), widthFrom=3, widthTo=3, left=5)
        self.rankInfoContainer = uiprimitives.Container(name='rankInfoContainer', parent=self.headerContainer, align=uiconst.TOLEFT, width=75, top=3)
        self.rankIcon = uiprimitives.Sprite(name='rankIcon', parent=self.rankInfoContainer, texturePath=self.get_rank_icon_path(), height=36, width=36, align=uiconst.TOLEFT, left=5)
        SetTooltipHeaderAndDescription(targetObject=self.rankIcon, headerText=localization.GetByLabel('UI/ProjectDiscovery/AnalystRankTooltip'), descriptionText=localization.GetByLabel('UI/ProjectDiscovery/AnalysisKreditsLabel') + ': ' + str(FmtAmt(self.playerState.analysisKredits)))
        self.rankLabel = uicontrols.Label(parent=self.rankInfoContainer, fontsize=16, text=self.rank, align=uiconst.CENTERLEFT, height=20, left=40)
        self.accuracyRatingContainer = uiprimitives.Container(name='accuracyRatingContainer', parent=self.headerContainer, align=uiconst.TORIGHT, width=75, left=5, top=3)
        self.accuracyRatingIconContainer = uiprimitives.Container(name='accuracyRatingIconContainer', parent=self.accuracyRatingContainer, height=32, width=32, align=uiconst.CENTER, left=20, bgTexturePath='res:/UI/Texture/classes/ProjectDiscovery/accuracyMeterBack.png')
        self.emptySprite = uiprimitives.Sprite(name='emptySprite', parent=self.accuracyRatingIconContainer, width=32, height=32, align=uiconst.CENTER)
        SetTooltipHeaderAndDescription(targetObject=self.emptySprite, headerText='', descriptionText=localization.GetByLabel('UI/ProjectDiscovery/AccuracyRatingTooltip'))
        self.accuracyNeedleIconContainer = uiprimitives.Transform(parent=self.accuracyRatingIconContainer, height=32, width=32, align=uiconst.TORIGHT, rotation=0)
        self.accuracyNeedleIcon = uiprimitives.Sprite(name='accuracyNeedleIcon', parent=self.accuracyNeedleIconContainer, texturePath='res:/UI/Texture/classes/ProjectDiscovery/accuracyMeterNeedle.png', width=32, height=32, rotation=2.4, align=uiconst.CENTER)
        self.accuracyArcFill = uicls.Polygon(parent=self.accuracyRatingIconContainer, align=uiconst.CENTER)
        self.accuracyArcFill.MakeArc(radius=0, outerRadius=10, fromDeg=-225.0, toDeg=-225.0, outerColor=(1.0, 1.0, 0, 0.7), innerColor=(1.0, 1.0, 0, 0.7))
        self.accuracyRatingLabel = uicontrols.Label(name='AccuracyRating', parent=self.accuracyRatingContainer, fontsize=16, text='00,0%', align=uiconst.CENTERLEFT, autoFitToText=True, height=20)
        self.state = uiconst.UI_NORMAL

    def _initialize_score_bar_length(self):
        self.scoreBarLength = self.scoreBarContainer.width - 10
        self.oldScoreBarLength = self.calculate_score_bar_length()

    def OnMouseDownDrag(self, *args):
        sm.ScatterEvent('OnProjectDiscoveryHeaderDragged')

    def OnMouseDown(self, *args):
        sm.ScatterEvent('OnProjectDiscoveryMouseDownOnHeader')

    def OnMouseEnter(self, *args):
        sm.ScatterEvent('OnProjectDiscoveryMouseEnterHeader')

    def OnMouseExit(self, *args):
        sm.ScatterEvent('OnProjectDiscoveryMouseExitHeader')

    def get_player_statistics(self, get_history):
        statistics = None
        try:
            statistics = self.pdService.player_statistics(get_history)
        except (NoConnectionToAPIError, MissingKeyError):
            sm.ScatterEvent(const.Events.NoConnectionToAPI)

        return statistics

    def update_accuracy_rating_text(self):
        self.accuracyRatingLabel.SetText(str(FmtAmt(self.score * 100, showFraction=1) + '%'))

    def update_accuracy_meter(self):
        animations.Tr2DRotateTo(self.accuracyNeedleIconContainer, startAngle=self.accuracyNeedleIconContainer.rotation, endAngle=self.needle_Rotation, curveType=uiconst.ANIM_LINEAR)
        self.accuracyArcFill.MakeArc(radius=0, outerRadius=10, fromDeg=-225.0, toDeg=self.score * 265 - 225.0, outerColor=(1.0, 1.0, 0, 0.7), innerColor=(1.0, 1.0, 0, 0.7))

    @on_event('OnUpdateHeader')
    def update_header(self):
        if self.player_statistics:
            if 'message' in self.player_statistics:
                logger.warning('ProjectDiscovery::update_header::Unhandled message received from the API: %s' % self.player_statistics['message'])
                if 'code' in self.player_statistics:
                    if self.player_statistics['code'] == PLAYER_NOT_IN_DATABASE_ERROR_CODE:
                        self.score = INITIAL_PLAYER_SCORE
                        self.needle_Rotation = self.score * self.full_needle_rotation
                        self.update_accuracy_rating_text()
                        self.update_accuracy_meter()
            else:
                self.score = self.player_statistics['projects'][0]['score']
                self.needle_Rotation = self.score * self.full_needle_rotation
                self.update_accuracy_rating_text()
                self.update_accuracy_meter()

    @on_event(Events.CloseResult)
    def on_result_closed(self, result):
        self.score = result['player']['score']
        self.needle_Rotation = self.score * self.full_needle_rotation
        self.update_accuracy_rating_text()
        self.update_accuracy_meter()
        self.player_statistics = self.get_player_statistics(True)
        self.update_header()

    @on_event(Events.UpdateScoreBar)
    def on_score_bar_update(self, player_state):
        self.playerState = player_state
        self.rank = self.playerState.rank
        self.total_xp_needed_for_current_rank = self.pdService.get_total_needed_xp(self.rank)
        self.total_xp_needed_for_next_rank = self.pdService.get_total_needed_xp(self.rank + 1)
        self.experience = self.playerState.experience
        self.update_analysis_kredits(player_state)
        uthread.new(self.update_score_bar)

    def update_analysis_kredits(self, player_state):
        self.playerState = player_state
        SetTooltipHeaderAndDescription(targetObject=self.rankIcon, headerText=localization.GetByLabel('UI/ProjectDiscovery/AnalystRankTooltip'), descriptionText=localization.GetByLabel('UI/ProjectDiscovery/AnalysisKreditsLabel') + ': ' + str(FmtAmt(self.playerState.analysisKredits)))

    def calculate_score_bar_length(self):
        return calculate_score_bar_length(self.experience, self.total_xp_needed_for_current_rank, self.total_xp_needed_for_next_rank, self.scoreBarLength)

    def update_score_bar(self):
        new_score_bar_length = self.calculate_score_bar_length()
        counter = self.oldScoreBarLength
        self.oldScoreBarLength = new_score_bar_length
        while counter >= new_score_bar_length:
            counter += 0.5
            if counter >= ScaleDpi(self.scoreBarLength - 5):
                counter = -1
                self.update_rank_values()
            else:
                if self.scoreBar.renderObject:
                    self.scoreBar.renderObject.translationTo = (counter, 0)
                blue.synchro.Sleep(1)

        while counter < new_score_bar_length:
            counter += 0.5
            if self.scoreBar.renderObject:
                self.scoreBar.renderObject.translationTo = (counter, 0)
            blue.synchro.Sleep(1)

        self.update_rank_values()

    def get_rank_icon_path(self):
        return const.rank_paths[calculate_rank_band(self.rank)]

    def update_rank_values(self):
        self.rankIcon.SetTexturePath(self.get_rank_icon_path())
        self.rankIcon.ReloadTexture()
        self.rankLabel.SetText(self.rank)
        self.rankLabel.ResolveAutoSizing()

    @on_event('OnUIScalingChange')
    def update_score_bar_scale(self, change):
        self.scoreBar.translationTo = (self.calculate_score_bar_length(), 0)
