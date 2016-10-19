#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\projectdiscovery\client\projects\subcellular\tutorial.py
import copy
import logging
import math
import random
import carbonui.const as uiconst
import localization
import uicontrols
import uiprimitives
import uthread
from carbonui.uianimations import animations
from categoryselector import CategorySelector
from eve.client.script.ui.control.eveLabel import EveCaptionLarge
from eve.client.script.ui.tooltips.tooltipUtil import SetTooltipHeaderAndDescription
from info import INFO as PROJECT_INFO
from processingview import ProcessingView
from projectdiscovery.client import const
from projectdiscovery.client.projects.subcellular import nested_categories_from_json
from projectdiscovery.client.util.dialogue import Dialogue
from projectdiscovery.client.util.eventlistener import eventlistener, on_event
from projectdiscovery.common.exceptions import MissingKeyError, NoConnectionToAPIError
from resultwindow import ResultWindow
from rewardsview import RewardsView
from taskimages import TaskImage
logger = logging.getLogger(__name__)

@eventlistener()

class Tutorial(uiprimitives.Container):
    MAX_CATEGORIES = PROJECT_INFO['resultSchema']['maxItems'] - 1

    def ApplyAttributes(self, attributes):
        super(Tutorial, self).ApplyAttributes(attributes)
        self.service = sm.RemoteSvc('ProjectDiscovery')
        self.selection = []
        self.isGreeting = False
        self.isSubmitting = False
        self.project_id = self.service.get_project_id()
        self.playerState = attributes.get('playerState')
        self.starting_scale = attributes.get('starting_scale')
        self.bottom_container = self.parent.parent.FindChild('bottom_container')
        self.loading = False
        self.task_number = None
        self.finishedTaskCount = 0
        self.setup_layout()

    def setup_layout(self):
        self.dialogue_container = uiprimitives.Container(name='dialogue_container', parent=self.parent, idx=0)
        self.left_main_container = uiprimitives.Container(name='left_main_container', parent=self, align=uiconst.TOLEFT_PROP, width=0.5, clipChildren=True, top=20)
        self.category_container = uiprimitives.Container(name='category_container', parent=self, align=uiconst.TOLEFT_PROP, width=0.5, padTop=45, clipChildren=True)
        self.task_label = EveCaptionLarge(parent=self.left_main_container, align=uiconst.CENTERTOP, text=localization.GetByLabel('UI/ProjectDiscovery/Subcellular/Tutorial/TaskLabel'), color=(0.48, 0.48, 0.48, 1), top=35)
        self.explanation_icon = uiprimitives.Sprite(parent=self.left_main_container, align=uiconst.TOPRIGHT, width=54, height=54, top=35, left=15, texturePath='res:/UI/Texture/WindowIcons/attention.png', state=uiconst.UI_HIDDEN)
        self.training_task_image = TaskImage(label=const.Texts.TaskImageLabel, parent=self.left_main_container, align=uiconst.TOPLEFT_PROP, pos=(25, 80, 420, 445), starting_scale=self.starting_scale)
        self.result_window = ResultWindow(name='ResultWindow', parent=self.parent, align=uiconst.TOALL, opacity=0, isTrainingPhase=True, taskImage=self.training_task_image, starting_scale=self.starting_scale, bottom_container=self.bottom_container)
        self.rewards_view = RewardsView(parent=self.parent, opacity=0, playerState=self.playerState, bottom_container=self.bottom_container, idx=0, state=uiconst.UI_DISABLED)
        self.rewards_view.isTraining = True
        self.rewards_view.tutorial_completed = False
        self.processing_view = ProcessingView(parent=self.parent, opacity=0, state=uiconst.UI_DISABLED)
        self.training_category_selector = CategorySelector(categories=nested_categories_from_json(PROJECT_INFO['info']['classes']), parent=self.category_container, state=uiconst.UI_HIDDEN, starting_scale=self.starting_scale)
        self.main_button_container = uiprimitives.Container(name='main_button_container', parent=self.bottom_container, align=uiconst.CENTERBOTTOM, width=355, height=53, bgTexturePath='res:/UI/Texture/classes/ProjectDiscovery/footerBG.png')
        self.submit_button_container = uiprimitives.Container(name='submitButtonContainer', parent=self.main_button_container, width=250, align=uiconst.CENTER, height=40, top=5)
        self.submit_button = uicontrols.Button(name='submitButton', parent=self.submit_button_container, align=uiconst.CENTER, label=localization.GetByLabel('UI/ProjectDiscovery/SubmitButtonLabel'), fontsize=18, fixedwidth=170, fixedheight=30, func=lambda x: self.submit_training_solution())
        uiprimitives.Sprite(parent=self.submit_button_container, align=uiconst.CENTERLEFT, width=34, height=20, texturePath='res:/UI/Texture/classes/ProjectDiscovery/submitArrow.png', opacity=0.7)
        uiprimitives.Sprite(parent=uiprimitives.Transform(parent=self.submit_button_container, align=uiconst.CENTERRIGHT, width=34, height=20, rotation=math.pi), align=uiconst.CENTERRIGHT, width=34, height=20, texturePath='res:/UI/Texture/classes/ProjectDiscovery/submitArrow.png', opacity=0.7)
        self.task_id = uicontrols.Label(parent=self, align=uiconst.BOTTOMRIGHT, height=20, opacity=0.5, left=10)
        self.refresh_task_button = uicontrols.Button(name='refreshTaskButton', parent=self.category_container, align=uiconst.CENTER, func=lambda x: self.reset_task(), idx=0, label='Refresh Task', fixedwidth=120, fixedheight=30, state=uiconst.UI_HIDDEN)

    def get_total_task_count(self):
        count = 0
        for level in self.levelList:
            count += level['tasksToFinishLevel']

        return count

    def get_finished_task_count(self):
        count = 1
        for x in range(0, self.level):
            count += self.levelList[x]['tasksToFinishLevel']

        return count

    @on_event(const.Events.QuitTutorialTooltips)
    def enable_everything_after_tutorial(self):
        self.enable_ui()

    def get_tutorial_tooltip_steps(self):
        return [{'owner': self.training_task_image.images_container,
          'header': localization.GetByLabel('UI/ProjectDiscovery/Subcellular/Tutorial/SampleImageHeader'),
          'text': localization.GetByLabel('UI/ProjectDiscovery/Subcellular/Tutorial/SampleImageText')},
         {'owner': self.training_category_selector,
          'header': localization.GetByLabel('UI/ProjectDiscovery/Subcellular/Tutorial/CategorySelectionHeader'),
          'text': localization.GetByLabel('UI/ProjectDiscovery/Subcellular/Tutorial/CategorySelectionText')},
         {'owner': self.training_category_selector.super_categories[0],
          'header': localization.GetByLabel('UI/ProjectDiscovery/Subcellular/Tutorial/NucleusHeader'),
          'text': localization.GetByLabel('UI/ProjectDiscovery/Subcellular/Tutorial/NucleusText')},
         {'owner': self.training_category_selector.super_categories[1],
          'header': localization.GetByLabel('UI/ProjectDiscovery/Subcellular/Tutorial/CytoplasmHeader'),
          'text': localization.GetByLabel('UI/ProjectDiscovery/Subcellular/Tutorial/CytoplasmText')},
         {'owner': self.training_category_selector.super_categories[2],
          'header': localization.GetByLabel('UI/ProjectDiscovery/Subcellular/Tutorial/PeripheryHeader'),
          'text': localization.GetByLabel('UI/ProjectDiscovery/Subcellular/Tutorial/PeripheryText')},
         {'owner': self.training_category_selector.super_categories[3],
          'header': localization.GetByLabel('UI/ProjectDiscovery/Subcellular/Tutorial/MiscellaneousHeader'),
          'text': localization.GetByLabel('UI/ProjectDiscovery/Subcellular/Tutorial/MiscellaneousText')},
         {'owner': self.training_category_selector.super_categories[4],
          'header': localization.GetByLabel('UI/ProjectDiscovery/Subcellular/Tutorial/NotIdentifiableHeader'),
          'text': localization.GetByLabel('UI/ProjectDiscovery/Subcellular/Tutorial/NotIdentifiableText')},
         {'owner': self.training_task_image.colorFilterContainer,
          'header': localization.GetByLabel('UI/ProjectDiscovery/Subcellular/Tutorial/ChannelFilterHeader'),
          'text': localization.GetByLabel('UI/ProjectDiscovery/Subcellular/Tutorial/ChannelFilterText')},
         {'owner': self.main_button_container,
          'header': localization.GetByLabel('UI/ProjectDiscovery/Subcellular/Tutorial/SubmitButtonHeader'),
          'text': localization.GetByLabel('UI/ProjectDiscovery/Subcellular/Tutorial/SubmitButtonText')}]

    @on_event(const.Events.ProjectDiscoveryStarted)
    def skip_tutorial(self, show_dialogue):
        self.service.skip_tutorial()

    def start(self):
        self.show_greeting_dialogue()
        if self.playerState.finishedTutorial:
            self.playerState = self.service.reset_tutorial()
        self.level = self.playerState.tutorialLevel
        self.levelList = copy.deepcopy(const.get_training_task_list(self.project_id))
        self.levelDict = copy.deepcopy(self.levelList[self.level])
        self.new_training_task()
        self.finishedTaskCount = self.get_finished_task_count()
        self.set_task_label()

    def show_greeting_dialogue(self):
        self.disable_ui()
        Dialogue(name='greetingDialogue', parent=self.dialogue_container, align=uiconst.CENTER, width=450, height=340, messageText=localization.GetByLabel('UI/ProjectDiscovery/Subcellular/Tutorial/GreetingText'), messageHeaderText=localization.GetByLabel('UI/ProjectDiscovery/Subcellular/Tutorial/GreetingHeader'), label=localization.GetByLabel('UI/ProjectDiscovery/Subcellular/Tutorial/GreetingLabel'), buttonLabel=localization.GetByLabel('UI/ProjectDiscovery/Subcellular/Tutorial/GreetingButton'), toHide=self, isTutorial=True)

    def close(self):
        self.dialogue_container.Close()
        self.main_button_container.Close()
        self.result_window.Close()
        self.processing_view.Close()
        self.training_task_image.Flush()
        self.training_task_image.Close()
        self.training_category_selector.Close()
        self.rewards_view.Close()
        self.Close()

    def reset_task(self):
        if not self.loading:
            self.loading = True
            self.refresh_task_button.SetState(uiconst.UI_HIDDEN)
            self.training_task_image.reset_image()
            self.training_category_selector.cascade_categories_out()
            self.training_category_selector.reset_categories()
            self.new_training_task()
            self.loading = False

    def new_training_task(self):
        self.training_task_image.reset_image()
        self.selection = []
        self.hide_explanation_icon()
        if not self.levelDict:
            logger.error('tutorial.py::new_training_task:: no training tasks found')
            return
        self.choose_random_task()
        self.explanation = self.levelDict[self.task_number]
        try:
            self.task = self.service.new_training_task(self.task_number)
        except (NoConnectionToAPIError, MissingKeyError):
            self.disable_ui()
            self.training_category_selector.cascade_categories_out()
            self.category_container.SetState(uiconst.UI_NORMAL)
            self.training_category_selector.SetState(uiconst.UI_DISABLED)
            self.show_error_message_and_button()
            return

        self.task_id.SetText(self.task['taskId'])
        self.delete_task_number()
        self.set_categories_to_solution()
        self.set_task_label()
        sm.ScatterEvent(const.Events.NewTask, self.task)
        self.training_category_selector.cascade_categories_in()
        self.training_category_selector.SetState(uiconst.UI_NORMAL)
        self.enable_ui()

    def show_error_message_and_button(self):
        self.training_task_image.hide_loading_wheel()
        self.training_task_image.show_error_message()
        self.refresh_task_button.SetState(uiconst.UI_NORMAL)

    def set_task_label(self):
        self.task_label.SetText(localization.GetByLabel('UI/ProjectDiscovery/Subcellular/Tutorial/TaskLabel') + ' ' + str(self.finishedTaskCount) + '/' + str(self.get_total_task_count()))

    def set_categories_to_solution(self):
        relevant_categories = list(self.task['solution'])
        for super_cat in self.training_category_selector.super_categories:
            for sub in super_cat.sub_categories:
                if sub.id in self.task['solution']:
                    relevant_categories.extend(sub.excludes)

        for super_cat in self.training_category_selector.super_categories:
            for sub in super_cat.sub_categories:
                if sub.id in self.task['solution']:
                    temp_list = list(super_cat.sub_categories)
                    if sub in temp_list:
                        temp_list.remove(sub)
                    max_cats = 2
                    if len(temp_list) < max_cats:
                        max_cats = len(temp_list)
                    for n in range(0, max_cats):
                        item = random.choice(temp_list)
                        relevant_categories.append(item.id)
                        if item in temp_list:
                            temp_list.remove(item)

                    break

        for super_cat in self.training_category_selector.super_categories:
            for sub in super_cat.sub_categories:
                if sub.id not in relevant_categories:
                    sub.set_unavailable()
                    sub.set_unclickable()
                else:
                    sub.set_clickable()
                    sub.set_available()

    def delete_task_number(self):
        if self.task_number:
            del self.levelDict[self.task_number]
            self.task_number = None

    def choose_random_task(self):
        if not self.task_number:
            self.task_number = random.choice(self.levelDict.keys()[1:])

    def hide_explanation_icon(self):
        self.explanation_icon.SetAlpha(0)
        self.explanation_icon.SetState(uiconst.UI_HIDDEN)

    def open_error_dialogue(self):
        self.disable_ui()
        self.dialogue = Dialogue(name='ErrorDialogue', parent=self.dialogue_container, align=uiconst.CENTER, width=450, height=215, messageText=localization.GetByLabel('UI/ProjectDiscovery/NoCategorySelectedErrorMessage'), messageHeaderText=localization.GetByLabel('UI/ProjectDiscovery/NoCategorySelectedHeader'), label=localization.GetByLabel('UI/ProjectDiscovery/NotificationHeader'), buttonLabel=localization.GetByLabel('UI/ProjectDiscovery/ErrorButton'), toHide=self)

    def open_too_many_categories_selected_dialogue(self):
        self.disable_ui()
        self.dialogue = Dialogue(name='ErrorDialogue', parent=self.dialogue_container, align=uiconst.CENTER, width=450, height=215, messageText=localization.GetByLabel('UI/ProjectDiscovery/TooManyCategoriesMessage'), messageHeaderText=localization.GetByLabel('UI/ProjectDiscovery/TooManyCategoriesHeader'), label=localization.GetByLabel('UI/ProjectDiscovery/NotificationHeader'), buttonLabel=localization.GetByLabel('UI/ProjectDiscovery/ErrorButton'), toHide=self)

    def disable_ui(self):
        self.left_main_container.state = uiconst.UI_DISABLED
        self.category_container.state = uiconst.UI_DISABLED
        self.main_button_container.state = uiconst.UI_DISABLED
        self.training_category_selector.state = uiconst.UI_DISABLED

    @on_event(const.Events.EnableUI)
    def enable_ui(self):
        self.training_task_image.state = uiconst.UI_NORMAL
        self.left_main_container.state = uiconst.UI_NORMAL
        self.category_container.state = uiconst.UI_NORMAL
        self.main_button_container.state = uiconst.UI_NORMAL
        self.training_category_selector.state = uiconst.UI_NORMAL

    def submit_training_solution(self):
        if self.isSubmitting:
            return
        if not self.selection:
            self.open_error_dialogue()
            return
        self.isSubmitting = True
        self.finishedTaskCount += 1
        sm.GetService('audio').SendUIEvent(const.Sounds.MainImageLoopStop)
        classification = list(set([ cat['id'] for cat in self.selection if not cat['excluded'] ]))
        self.result = {'playerSelection': classification,
         'task': {'solution': self.task['solution']}}
        SetTooltipHeaderAndDescription(targetObject=self.explanation_icon, headerText='', descriptionText=self.explanation)
        self.result_window.assign_result(self.result)
        self.training_category_selector.cascade_categories_out()
        self.training_category_selector.state = uiconst.UI_DISABLED
        animations.FadeOut(self.main_button_container)
        animations.FadeOut(self.training_task_image.colorFilterContainer)
        animations.FadeOut(self.task_label)
        animations.FadeOut(self.refresh_task_button)
        self.training_task_image.start_transmission_animation()
        self.left_main_container.state = uiconst.UI_DISABLED
        self.category_container.state = uiconst.UI_DISABLED
        self.main_button_container.state = uiconst.UI_DISABLED

    @on_event(const.Events.TransmissionFinished)
    def on_transmission_finished(self):
        self.left_main_container.state = uiconst.UI_NORMAL
        self.result_window.open()
        self.result_window.show_result()
        animations.FadeIn(self.training_task_image.colorFilterContainer)
        self.show_and_blink_explanation_icon()

    def show_and_blink_explanation_icon(self):
        self.explanation_icon.SetAlpha(0)
        self.explanation_icon.SetState(uiconst.UI_NORMAL)
        animations.FadeIn(self.explanation_icon, duration=1, loops=5, curveType=uiconst.ANIM_OVERSHOT5)

    def is_tutorial_finished(self):
        self.playerState = self.service.get_player_state()
        return self.playerState.tutorialLevel >= self.get_number_of_levels()

    def get_number_of_levels(self):
        return len(self.levelList)

    @on_event(const.Events.ContinueFromTrainingResult)
    def on_training_result_closed(self):
        self.isSubmitting = False
        self.increment_level_if_needed()
        uthread.new(self.new_training_task)
        animations.FadeIn(self, duration=1)
        animations.FadeIn(self.main_button_container)
        animations.FadeIn(self.training_task_image.colorFilterContainer)
        animations.FadeIn(self.task_label, timeOffset=1)
        animations.FadeIn(self.refresh_task_button)
        self.training_task_image.state = uiconst.UI_NORMAL
        self.left_main_container.state = uiconst.UI_NORMAL
        self.category_container.state = uiconst.UI_NORMAL
        self.main_button_container.state = uiconst.UI_NORMAL

    def end_tutorial(self):
        if self.service.give_tutorial_rewards():
            result = {'XP_Reward': self.service.get_tutorial_xp_reward(),
             'LP_Reward': 0,
             'ISK_Reward': 0,
             'AK_Reward': 0,
             'playerState': self.service.get_player_state(),
             'player': {'score': 0.5},
             'isTraining': True}
            self.rewards_view.tutorial_completed = True
            sm.ScatterEvent(const.Events.CloseResult, result)
            self.processing_view.start()
            settings.char.ui.Set('loadStatisticsAfterSubmission', True)
        else:
            sm.ScatterEvent(const.Events.ProjectDiscoveryStarted, True)
        self.Close()

    def increment_level_if_needed(self):
        self.levelDict['tasksToFinishLevel'] -= 1
        if self.levelDict['tasksToFinishLevel'] <= 0:
            self.playerState = self.service.increase_tutorial_level()
            if self.is_tutorial_finished():
                self.end_tutorial()
            else:
                self.level = self.playerState.tutorialLevel
                self.levelDict = copy.deepcopy(self.levelList[self.level])

    def _update_excluded(self, excluder):
        excluded = set()
        for cat in self.selection:
            excluded.update(cat.get('excludes', []))

        sm.ScatterEvent(const.Events.ExcludeCategories, excluder, excluded)

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
