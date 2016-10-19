#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\projectdiscovery\client\projects\subcellular\subcellularatlas.py
import logging
import math
import blue
import carbonui.const as uiconst
import localization
import uicontrols
import uiprimitives
import uthread
from carbonui.uianimations import animations
from categoryselector import CategorySelector
from const import MSEC
from eve.client.script.ui.control import themeColored
from eve.client.script.ui.control.eveLoadingWheel import LoadingWheel
from eve.client.script.ui.tooltips.tooltipUtil import SetTooltipHeaderAndDescription
from gametime import GetWallclockTime, GetTimeDiff
from info import INFO as PROJECT_INFO
from projectdiscovery.client import const
from projectdiscovery.client.projects.subcellular import nested_categories_from_json
from projectdiscovery.client.projects.subcellular.processingview import ProcessingView
from projectdiscovery.client.projects.subcellular.resultwindow import ResultWindow
from projectdiscovery.client.projects.subcellular.rewardsview import RewardsView
from projectdiscovery.client.projects.subcellular.taskimages import TaskImage
from projectdiscovery.client.util.dialogue import Dialogue
from projectdiscovery.client.util.eventlistener import eventlistener, on_event
from projectdiscovery.common.exceptions import MissingKeyError, NoConnectionToAPIError
logger = logging.getLogger(__name__)
RESULT_TIME_OUT = 10

@eventlistener()

class SubcellularAtlas(uiprimitives.Container):
    MAX_CATEGORIES = PROJECT_INFO['resultSchema']['maxItems'] - 1

    def ApplyAttributes(self, attributes):
        super(SubcellularAtlas, self).ApplyAttributes(attributes)
        self.task_time = None
        self.selection = []
        self.tutorial = None
        self.service = sm.RemoteSvc('ProjectDiscovery')
        self.submitting = False
        self.playerState = attributes.get('playerState')
        self.starting_scale = attributes.get('starting_scale')
        self.bottom_container = self.parent.parent.FindChild('bottom_container')
        self.clipChildren = True
        self.result = None
        self.getting_new_task = False
        self.setup_layout()

    def setup_layout(self):
        self.dialogue_container = uiprimitives.Container(name='dialogue_container', parent=self.parent, idx=0)
        self.left_main_container = uiprimitives.Container(name='left_main_container', parent=self, align=uiconst.TOLEFT_PROP, width=0.5, clipChildren=True, top=20)
        self.category_container = uiprimitives.Container(name='category_container', parent=self, align=uiconst.TOLEFT_PROP, width=0.5, padTop=45, clipChildren=True)
        self.loading_container = uiprimitives.Container(name='loadingContainer', parent=self.category_container, align=uiconst.CENTER, width=100, height=100, state=uiconst.UI_HIDDEN)
        self.loading_result_label = themeColored.LabelThemeColored(name='loadingResultLabel', parent=self.loading_container, align=uiconst.CENTERTOP, text=localization.GetByLabel('UI/ProjectDiscovery/LoadingResultLabel'), fontsize=20)
        self.loading_wheel = LoadingWheel(name='ResultLoadingIndicator', parent=self.loading_container, align=uiconst.CENTER, width=64, height=64)
        self.error_container = uiprimitives.Container(parent=self.category_container, align=uiconst.CENTER, width=100, height=100, state=uiconst.UI_HIDDEN)
        self.error_label = themeColored.LabelThemeColored(parent=self.error_container, align=uiconst.CENTERTOP, text=localization.GetByLabel('UI/ProjectDiscovery/LoadingResultErrorLabel'), fontsize=20)
        self.task_label = themeColored.LabelThemeColored(parent=self.left_main_container, align=uiconst.CENTERTOP, text=localization.GetByLabel('UI/ProjectDiscovery/TaskLabel'), top=40, fontsize=28, opacity=1)
        self.task_image = TaskImage(label=const.Texts.TaskImageLabel, parent=self.left_main_container, align=uiconst.TOPLEFT_PROP, pos=(25, 80, 420, 445), starting_scale=self.starting_scale)
        self.checkbox_container = uiprimitives.Container(name='checkboxContainer', parent=self.task_image, align=uiconst.BOTTOMLEFT, width=110, height=20, left=8, top=10)
        self.report_checkbox = uicontrols.Checkbox(name='reportCheckbox', parent=self.checkbox_container, text=localization.GetByLabel('UI/ProjectDiscovery/ReportCheckboxLabel'))
        SetTooltipHeaderAndDescription(self.report_checkbox, headerText=localization.GetByLabel('UI/ProjectDiscovery/AbnormalSampleTooltipHeader'), descriptionText=localization.GetByLabel('UI/ProjectDiscovery/AbnormalSampleTooltipDescription'))
        self.result_window = ResultWindow(name='ResultWindow', parent=self.parent, align=uiconst.TOALL, opacity=0, isTrainingPhase=False, starting_scale=self.starting_scale, bottom_container=self.bottom_container)
        self.rewards_view = RewardsView(parent=self.parent.parent, opacity=0, align=uiconst.TOALL, playerState=self.playerState, bottom_container=self.bottom_container, idx=1, state=uiconst.UI_DISABLED)
        self.processing_view = ProcessingView(parent=self.parent.parent, opacity=0, idx=2, state=uiconst.UI_DISABLED)
        self.category_selector = CategorySelector(categories=nested_categories_from_json(PROJECT_INFO['info']['classes']), parent=self.category_container, state=uiconst.UI_DISABLED, starting_scale=self.starting_scale)
        self.main_button_container = uiprimitives.Container(name='main_button_container', parent=self.bottom_container, align=uiconst.CENTERBOTTOM, width=355, height=53, bgTexturePath='res:/UI/Texture/classes/ProjectDiscovery/footerBG.png')
        self.submit_button_container = uiprimitives.Container(name='submitButtonContainer', parent=self.main_button_container, width=250, align=uiconst.CENTER, height=40, top=5)
        self.submit_button = uicontrols.Button(name='SubcellularSubmitButton', parent=self.submit_button_container, align=uiconst.CENTER, label=localization.GetByLabel('UI/ProjectDiscovery/SubmitButtonLabel'), fontsize=18, fixedwidth=170, fixedheight=30, func=lambda x: self.submit_solution())
        uiprimitives.Sprite(parent=self.submit_button_container, align=uiconst.CENTERLEFT, width=34, height=20, texturePath='res:/UI/Texture/classes/ProjectDiscovery/submitArrow.png', opacity=0.7)
        uiprimitives.Sprite(parent=uiprimitives.Transform(parent=self.submit_button_container, align=uiconst.CENTERRIGHT, width=34, height=20, rotation=math.pi), align=uiconst.CENTERRIGHT, width=34, height=20, texturePath='res:/UI/Texture/classes/ProjectDiscovery/submitArrow.png', opacity=0.7)
        self.task_id = uicontrols.Label(name='TaskID', parent=self.bottom_container, align=uiconst.BOTTOMRIGHT, height=20, opacity=0, left=10)
        self.new_task_button = uicontrols.ButtonIcon(name='newTaskButton', parent=self.left_main_container, align=uiconst.TOPLEFT, texturePath='res:/UI/Texture/classes/ProjectDiscovery/recycleButtonUp.png', hoverTexture='res:/UI/Texture/classes/ProjectDiscovery/recycleButtonOver.png', downTexture='res:/UI/Texture/classes/ProjectDiscovery/recycleButtonDown.png', iconSize=24, func=lambda : self.reset_and_get_new_task(), idx=0, left=32, top=54)
        SetTooltipHeaderAndDescription(self.new_task_button, headerText='', descriptionText=localization.GetByLabel('UI/ProjectDiscovery/NewTaskButtonTooltipDescription'))

    def start(self, show_dialogue):
        if show_dialogue:
            self.disable_ui()
            Dialogue(name='finishedTutorialDialogue', parent=self.dialogue_container, align=uiconst.CENTER, width=450, height=330, messageText=localization.GetByLabel('UI/ProjectDiscovery/Subcellular/Tutorial/FinishedMessage'), messageHeaderText=localization.GetByLabel('UI/ProjectDiscovery/Subcellular/Tutorial/FinishedHeader'), label=localization.GetByLabel('UI/ProjectDiscovery/Subcellular/Tutorial/GreetingLabel'), buttonLabel=localization.GetByLabel('UI/ProjectDiscovery/ErrorButton'), toHide=self)
        uthread.new(self.get_new_task)

    def close(self):
        self.task_image.reset_image()
        self.rewards_view.close()
        self.result_window.kill()
        self.processing_view.Close()
        self.main_button_container.Close()
        self.dialogue_container.Close()
        self.task_id.Close()
        self.Close()

    @on_event(const.Events.ResetAndGetNewTask)
    def reset_and_get_new_task(self):
        self.category_selector.reset_categories()
        self.enable_ui()
        self.category_selector.state = uiconst.UI_DISABLED
        self.task_image.reset_image()
        self.get_new_task()

    def get_new_task(self):
        if self.getting_new_task:
            return
        self.getting_new_task = True
        self.selection = []
        try:
            self.task = self.service.new_task()
        except (MissingKeyError, NoConnectionToAPIError):
            self.open_task_retrieval_error_dialogue()
            return

        sm.ScatterEvent(const.Events.NewTask, self.task)
        self.task_time = GetWallclockTime()
        self.task_id.SetAlpha(0)
        self.task_id.SetText(self.task['taskId'])
        settings.char.ui.Set('UpdateAccInfo', True)

    @on_event(const.Events.MainImageLoaded)
    def set_getting_new_task_to_false(self):
        if self.category_selector:
            self.category_selector.state = uiconst.UI_NORMAL
        self.getting_new_task = False

    def _update_excluded(self, excluder):
        excluded = set()
        for cat in self.selection:
            if '*' in cat.get('excludes'):
                excluded.update(cat.get('excludes', []))
            elif 12 in cat.get('excludes', []):
                excludes = list(cat.get('excludes', []))
                excludes.append(121)
                excludes.append(122)
                excludes.append(123)
                excluded.update(excludes, [])
            else:
                excluded.update(cat.get('excludes', []))

        sm.ScatterEvent(const.Events.ExcludeCategories, excluder, excluded)

    def open_no_categories_selected_error_dialogue(self):
        self.disable_ui()
        self.dialogue = Dialogue(name='ErrorDialogue', parent=self.dialogue_container, align=uiconst.CENTER, width=450, height=215, messageText=localization.GetByLabel('UI/ProjectDiscovery/NoCategorySelectedErrorMessage'), messageHeaderText=localization.GetByLabel('UI/ProjectDiscovery/NoCategorySelectedHeader'), label=localization.GetByLabel('UI/ProjectDiscovery/NotificationHeader'), buttonLabel=localization.GetByLabel('UI/ProjectDiscovery/ErrorButton'), toHide=self)

    def open_too_many_categories_selected_dialogue(self):
        self.disable_ui()
        self.dialogue = Dialogue(name='ErrorDialogue', parent=self.dialogue_container, align=uiconst.CENTER, width=450, height=215, messageText=localization.GetByLabel('UI/ProjectDiscovery/TooManyCategoriesMessage'), messageHeaderText=localization.GetByLabel('UI/ProjectDiscovery/TooManyCategoriesHeader'), label=localization.GetByLabel('UI/ProjectDiscovery/NotificationHeader'), buttonLabel=localization.GetByLabel('UI/ProjectDiscovery/ErrorButton'), toHide=self)

    def open_classification_error_dialogue(self):
        self.disable_ui()
        self.dialogue = Dialogue(name='ErrorDialogue', parent=self.dialogue_container, align=uiconst.CENTER, width=450, height=215, messageText=localization.GetByLabel('UI/ProjectDiscovery/ClassificationErrorMessage'), messageHeaderText=localization.GetByLabel('UI/ProjectDiscovery/ClassificationErrorHeader'), label=localization.GetByLabel('UI/ProjectDiscovery/NotificationHeader'), buttonLabel=localization.GetByLabel('UI/ProjectDiscovery/ErrorButton'), toHide=self, onCloseEvent=const.Events.RestartWindow)

    def open_task_retrieval_error_dialogue(self):
        self.disable_ui()
        self.dialogue = Dialogue(name='ErrorDialogue', parent=self.dialogue_container, align=uiconst.CENTER, width=450, height=215, messageText=localization.GetByLabel('UI/ProjectDiscovery/TaskRetrievalErrorMessage'), messageHeaderText=localization.GetByLabel('UI/ProjectDiscovery/TaskRetrievalErrorHeader'), label=localization.GetByLabel('UI/ProjectDiscovery/NotificationHeader'), buttonLabel=localization.GetByLabel('UI/ProjectDiscovery/ErrorButton'), toHide=self, onCloseEvent=const.Events.ResetAndGetNewTask)

    def disable_ui(self):
        self.left_main_container.state = uiconst.UI_DISABLED
        self.category_container.state = uiconst.UI_DISABLED
        self.main_button_container.state = uiconst.UI_DISABLED

    @on_event(const.Events.EnableUI)
    def enable_ui(self):
        self.task_image.state = uiconst.UI_NORMAL
        self.left_main_container.state = uiconst.UI_NORMAL
        self.category_container.state = uiconst.UI_NORMAL
        self.main_button_container.state = uiconst.UI_NORMAL

    def submit_solution(self):
        if self.submitting:
            return
        if not self.selection:
            self.open_no_categories_selected_error_dialogue()
            return
        sm.GetService('audio').SendUIEvent(const.Sounds.MainImageLoopStop)
        self.disable_ui()
        self.submitting = True
        self._animate_out()
        self.classification = list(set([ cat['id'] for cat in self.selection if not cat['excluded'] ]))
        duration = self.get_duration()
        try:
            self.result = self.service.post_classification(self.task, self.classification, duration, remark=bool(self.report_checkbox.GetValue()))
        except:
            self.disable_ui()
            self.open_classification_error_dialogue()
            raise

    def get_duration(self):
        duration = GetTimeDiff(self.task_time, GetWallclockTime()) / MSEC
        if duration < 0:
            duration = 0
        return duration

    def _animate_out(self):
        animations.FadeOut(self.main_button_container)
        animations.FadeOut(self.task_image.colorFilterContainer)
        animations.FadeOut(self.task_label)
        animations.FadeOut(self.checkbox_container)
        animations.FadeOut(self.new_task_button)
        self.new_task_button.SetState(uiconst.UI_DISABLED)
        uthread.new(self.category_selector.cascade_categories_out)
        self.category_selector.state = uiconst.UI_DISABLED
        self.task_image.start_transmission_animation()

    @on_event(const.Events.TransmissionFinished)
    def prepare_result_screen(self):
        self.left_main_container.state = uiconst.UI_NORMAL
        animations.FadeIn(self.task_image.colorFilterContainer)
        self.result_window.open()
        uthread.new(self.wait_for_result)

    def wait_for_result(self):
        seconds = 1
        while not self.has_result():
            self.show_loading()
            seconds += 1
            if seconds > RESULT_TIME_OUT:
                self.respond_to_result_timeout()
                return
            blue.synchro.Sleep(1000)

        self.use_result()

    def respond_to_result_timeout(self):
        logger.error('ProjectDiscovery::wait_for_result: Result took longer than 10 seconds to arrive, giving up.')
        self.show_loading_error()
        self.result_window.enable_ui()

    def use_result(self):
        self.result['playerSelection'] = self.classification
        self.result_window.assign_result(self.result)
        if settings.char.ui.Get('loadStatisticsAfterSubmission'):
            sm.ScatterEvent('OnUpdateHeader')
            settings.char.ui.Set('loadStatisticsAfterSubmission', False)
        self.enable_ui()
        self.category_container.state = uiconst.UI_DISABLED
        self.main_button_container.state = uiconst.UI_DISABLED
        self.hide_loading()
        self.result_window.show_result()
        self.task_id.SetAlpha(0.5)

    def has_result(self):
        if self.result:
            return True
        return False

    def show_loading(self):
        self.loading_container.SetState(uiconst.UI_NORMAL)

    def hide_loading(self):
        self.loading_container.SetState(uiconst.UI_HIDDEN)

    def show_loading_error(self):
        self.hide_loading()
        self.error_container.SetState(uiconst.UI_NORMAL)

    def hide_loading_error(self):
        self.error_container.SetState(uiconst.UI_HIDDEN)

    def get_tutorial_tooltip_steps(self):
        return [{'owner': self.task_image.image_sprite,
          'header': localization.GetByLabel('UI/ProjectDiscovery/Subcellular/Tutorial/SampleImageHeader'),
          'text': localization.GetByLabel('UI/ProjectDiscovery/Subcellular/Tutorial/SampleImageText')},
         {'owner': self.category_selector,
          'header': localization.GetByLabel('UI/ProjectDiscovery/Subcellular/Tutorial/CategorySelectionHeader'),
          'text': localization.GetByLabel('UI/ProjectDiscovery/Subcellular/Tutorial/CategorySelectionText')},
         {'owner': self.category_selector.super_categories[0],
          'header': localization.GetByLabel('UI/ProjectDiscovery/Subcellular/Tutorial/NucleusHeader'),
          'text': localization.GetByLabel('UI/ProjectDiscovery/Subcellular/Tutorial/NucleusText')},
         {'owner': self.category_selector.super_categories[1],
          'header': localization.GetByLabel('UI/ProjectDiscovery/Subcellular/Tutorial/CytoplashHeader'),
          'text': localization.GetByLabel('UI/ProjectDiscovery/Subcellular/Tutorial/CytoplashText')},
         {'owner': self.category_selector.super_categories[2],
          'header': localization.GetByLabel('UI/ProjectDiscovery/Subcellular/Tutorial/PeripheryHeader'),
          'text': localization.GetByLabel('UI/ProjectDiscovery/Subcellular/Tutorial/PeripheryText')},
         {'owner': self.training_category_selector.super_categories[3],
          'header': localization.GetByLabel('UI/ProjectDiscovery/Subcellular/Tutorial/MiscellaneousHeader'),
          'text': localization.GetByLabel('UI/ProjectDiscovery/Subcellular/Tutorial/MiscellaneousText')},
         {'owner': self.training_category_selector.super_categories[4],
          'header': localization.GetByLabel('UI/ProjectDiscovery/Subcellular/Tutorial/NotIdentifiableHeader'),
          'text': localization.GetByLabel('UI/ProjectDiscovery/Subcellular/Tutorial/NotIdentifiableText')}]

    @on_event(const.Events.CategoryChanged)
    def on_category_changed(self, hexagon):
        if hexagon.category['selected']:
            if len(self.selection) > self.MAX_CATEGORIES:
                hexagon.set_unselected()
                self.open_too_many_categories_selected_dialogue()
                return
            self.selection.append(hexagon.category)
        elif hexagon.category in self.selection:
            self.selection.remove(hexagon.category)
        self._update_excluded(hexagon.category['id'])

    @on_event(const.Events.ContinueFromReward)
    def on_continue_from_reward(self):
        if not self.result:
            self.submitting = False
            self.task_image.state = uiconst.UI_DISABLED
            self.category_selector.reset_categories()
        self.category_selector.reset_categories()
        self.hide_loading()
        self.hide_loading_error()
        self.result = None
        uthread.new(self.get_new_task)
        self.report_checkbox.SetValue(0)
        self._animate_in()
        self.enable_ui()

    def _animate_in(self):
        animations.FadeIn(self, duration=1)
        animations.FadeIn(self.main_button_container)
        animations.FadeIn(self.task_image.colorFilterContainer)
        animations.FadeIn(self.task_label)
        animations.FadeIn(self.checkbox_container)
        animations.FadeIn(self.new_task_button)
        self.new_task_button.SetState(uiconst.UI_NORMAL)
        self.category_selector.cascade_categories_in()

    @on_event(const.Events.ContinueFromResult)
    def reset_task_image(self):
        self.submitting = False
        self.task_image.state = uiconst.UI_DISABLED
        animations.FadeOut(self, duration=0.4, callback=self.task_image.reset_image)
