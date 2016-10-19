#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\projectdiscovery\client\projects\subcellular\resultwindow.py
import math
import localization
import uicontrols
import uiprimitives
from carbon.common.script.util.format import FmtAmt
from carbonui.uianimations import animations
from categoryselector import CategorySelector
from eve.client.script.ui.control import themeColored
from eve.client.script.ui.control.eveLabel import *
from eve.client.script.ui.control.tooltips import TooltipPanel
from eve.client.script.ui.tooltips.tooltipsWrappers import TooltipBaseWrapper
from info import INFO as PROJECT_INFO
from projectdiscovery.client import const
from projectdiscovery.client.projects.subcellular import nested_categories_from_json

class ResultWindow(uiprimitives.Container):

    def ApplyAttributes(self, attributes):
        super(ResultWindow, self).ApplyAttributes(attributes)
        self.isTrainingPhase = attributes.get('isTrainingPhase')
        self.starting_scale = attributes.get('starting_scale')
        self.bottom_container = attributes.get('bottom_container')
        self.projectdiscoverySvc = sm.RemoteSvc('ProjectDiscovery')
        self.finishedTraining = False
        self.result = None
        self.audio_service = sm.GetService('audio')
        self.setup_layout()
        self.categories_selected.cascade_categories_out()
        self.disable_ui()

    def setup_layout(self):
        self.left_main_container = uiprimitives.Container(name='left_main_container', parent=self, align=uiconst.TOLEFT_PROP, width=0.5, clipChildren=True, top=20)
        self.task_label = themeColored.LabelThemeColored(parent=self.left_main_container, align=uiconst.CENTERTOP, text=localization.GetByLabel('UI/ProjectDiscovery/Subcellular/ResultScreen/WindowHeaderText'), top=40, fontsize=28)
        self.category_container = uiprimitives.Container(name='category_container', parent=self, align=uiconst.TOLEFT_PROP, width=0.5, padTop=45, clipChildren=True)
        self.categories_selected = CategorySelector(categories=nested_categories_from_json(PROJECT_INFO['info']['classes']), parent=self.category_container, state=uiconst.UI_DISABLED, starting_scale=self.starting_scale)
        self.legend_container = uiprimitives.Container(name='legendContainer', parent=self.category_container, width=100, height=28, align=uiconst.BOTTOMRIGHT, opacity=0, top=93, left=-5, idx=0)
        self.legend_icon = LegendIcon(name='legendIcon', parent=self.legend_container, texturePath='res:/UI/Texture/classes/ProjectDiscovery/helpTooltipUp.png', align=uiconst.TOLEFT, width=28, height=28)
        self.legend_label = uicontrols.Label(parent=self.legend_container, align=uiconst.CENTERLEFT, text=localization.GetByLabel('UI/ProjectDiscovery/Subcellular/ResultScreen/LegendIconLabel'), left=30, height=15)
        self.main_button_container = uiprimitives.Container(name='ResultMainContinueButtonContainer', parent=self.bottom_container, align=uiconst.CENTERBOTTOM, width=355, height=53, bgTexturePath='res:/UI/Texture/classes/ProjectDiscovery/footerBG.png', state=uiconst.UI_DISABLED, opacity=0)
        self.continue_button_container = uiprimitives.Container(name='ResultContinueButtonContainer', parent=self.main_button_container, width=250, align=uiconst.CENTER, height=40, top=5)
        self.continue_button = uicontrols.Button(name='resultContinueButton', parent=self.continue_button_container, align=uiconst.CENTER, label=localization.GetByLabel('UI/ProjectDiscovery/Subcellular/ResultScreen/ContinueButtonLabel'), fontsize=18, fixedwidth=170, fixedheight=30, func=lambda x: self.close())
        uiprimitives.Sprite(parent=self.continue_button_container, align=uiconst.CENTERLEFT, width=34, height=20, texturePath='res:/UI/Texture/classes/ProjectDiscovery/submitArrow.png', opacity=0.7)
        uiprimitives.Sprite(parent=uiprimitives.Transform(parent=self.continue_button_container, align=uiconst.CENTERRIGHT, width=34, height=20, rotation=math.pi), align=uiconst.CENTERRIGHT, width=34, height=20, texturePath='res:/UI/Texture/classes/ProjectDiscovery/submitArrow.png', opacity=0.7)

    def close(self):
        if not self.result:
            sm.ScatterEvent(const.Events.ContinueFromReward)
        elif self.isTrainingPhase:
            sm.ScatterEvent(const.Events.ContinueFromTrainingResult)
            self.audio_service.SendUIEvent(const.Sounds.RewardsWindowLoopStop)
            self.audio_service.SendUIEvent(const.Sounds.RewardsWindowClosePlay)
            self.audio_service.SendUIEvent(const.Sounds.MainImageLoopPlay)
        else:
            sm.ScatterEvent(const.Events.CloseResult, self.result)
            sm.ScatterEvent(const.Events.ContinueFromResult)
        animations.FadeOut(self, duration=0.4)
        self.categories_selected.cascade_categories_out()
        self.categories_selected.reset_categories()
        self.legend_container.SetOpacity(0)
        self.disable_ui()

    def assign_result(self, result):
        self.result = result
        if self._is_solution_known():
            task_label_path = 'UI/ProjectDiscovery/Subcellular/ResultScreen/WindowHeaderText'
        else:
            task_label_path = 'UI/ProjectDiscovery/Subcellular/ResultScreen/WindowHeaderTextUnknown'
        self.task_label.SetText(localization.GetByLabel(task_label_path))
        self.legend_icon.tooltipPanelClassInfo = LegendTooltipWrapper(known_solution=self._is_solution_known())
        for super_cat in self.categories_selected.super_categories:
            for subcat in super_cat.sub_categories:
                subcat.set_available()
                if self._is_solution_known():
                    self._show_known_solution(subcat)
                else:
                    self._show_unknown_solution(subcat)
                subcat.exclude_texture.state = uiconst.UI_HIDDEN
                subcat.category['selected'] = False
                subcat.set_unclickable()

    def open(self):
        animations.FadeIn(self, callback=self.enable_button)
        animations.FadeIn(self.main_button_container)

    def show_result(self):
        self.enable_ui()
        self.categories_selected.cascade_categories_in()
        self.legend_container.SetOpacity(1)

    def enable_ui(self):
        self.state = uiconst.UI_NORMAL
        self.enable_button()
        self.main_button_container.SetState(uiconst.UI_NORMAL)
        if self.result:
            self.enable_categories()

    def disable_ui(self):
        self.state = uiconst.UI_DISABLED
        self.disable_categories()
        self.disable_button()
        self.main_button_container.SetState(uiconst.UI_DISABLED)
        self.main_button_container.SetOpacity(0)

    def _show_known_solution(self, subcat):
        subcat.hide_percentage_and_color_overlay()
        if subcat.category['id'] not in self.result['playerSelection'] and subcat.category['id'] not in self.result['task']['solution']:
            subcat.set_unavailable()
        elif subcat.category['id'] in self.result['playerSelection'] and subcat.category['id'] in self.result['task']['solution']:
            subcat.correct_texture.opacity = 1
        elif subcat.category['id'] in self.result['playerSelection'] and subcat.category['id'] not in self.result['task']['solution']:
            subcat.unmatched_texture.opacity = 1
        elif subcat.category['id'] not in self.result['playerSelection'] and subcat.category['id'] in self.result['task']['solution']:
            subcat.missed_texture.opacity = 1
        subcat.set_unselected()

    def _show_unknown_solution(self, subcat):
        subcat.hide_percentage_and_color_overlay()
        subcat.set_unavailable()
        if subcat.category['id'] in self.result['playerSelection']:
            subcat.set_selected()
            subcat.set_available()
            subcat.set_percentage(str(0))
            subcat.show_percentage_and_color_overlay()
        else:
            subcat.set_unselected()
        if self._is_solution_voted():
            for vote in self.result['task']['votes']:
                if subcat.category['id'] == vote['result']:
                    if vote['percentage'] > 0.01 or subcat.category['id'] in self.result['playerSelection']:
                        subcat.show_percentage_and_color_overlay()
                        subcat.set_percentage(FmtAmt(vote['percentage'] * 100, showFraction=0))
                        color = subcat.lerp_color(vote['percentage'], 1)
                        subcat.color_overlay.SetRGB(color[0], color[1], color[2], 1)
                        subcat.set_available()
                    else:
                        subcat.hide_percentage_and_color_overlay()
                        subcat.set_unavailable()

    def enable_categories(self):
        self.category_container.state = uiconst.UI_NORMAL
        self.categories_selected.state = uiconst.UI_NORMAL

    def disable_categories(self):
        self.category_container.state = uiconst.UI_DISABLED
        self.categories_selected.state = uiconst.UI_DISABLED

    def enable_button(self):
        self.continue_button.SetState(uiconst.UI_NORMAL)

    def disable_button(self):
        self.continue_button.SetState(uiconst.UI_DISABLED)

    def kill(self):
        self.main_button_container.Close()
        self.Close()

    def _is_solution_known(self):
        return self.result and 'task' in self.result.keys() and 'solution' in self.result['task'] and self.result['task']['solution']

    def _is_solution_voted(self):
        return self.result and 'task' in self.result.keys() and 'votes' in self.result['task'] and self.result['task']['votes']


class LegendIcon(uiprimitives.Sprite):

    def OnMouseEnter(self, *args):
        self.SetTexturePath('res:/UI/Texture/classes/ProjectDiscovery/helpTooltipOver.png')

    def OnMouseExit(self, *args):
        self.SetTexturePath('res:/UI/Texture/classes/ProjectDiscovery/helpTooltipUp.png')


class LegendTooltipWrapper(TooltipBaseWrapper):

    def __init__(self, known_solution):
        self._knownSolution = known_solution

    def CreateTooltip(self, parent, owner, idx):
        self.tooltipPanel = TooltipPanel(parent=parent, owner=owner, idx=idx)
        self.tooltipPanel.LoadGeneric1ColumnTemplate()
        self.legend_container = uiprimitives.Container(name='legendContainer', align=uiconst.TOPLEFT, height=220, width=210)
        if self._knownSolution:
            self.create_known_solution_tooltip()
        else:
            self.create_unknown_solution_tooltip()
        self.tooltipPanel.AddCell(self.legend_container, cellPadding=(0, 5, 0, -10))
        return self.tooltipPanel

    def create_unknown_solution_tooltip(self):
        self.selection_legend_container = uiprimitives.Container(parent=self.legend_container, align=uiconst.TOTOP, height=70)
        self.selection_sprite = uiprimitives.Sprite(parent=uiprimitives.Container(parent=self.selection_legend_container, align=uiconst.TOLEFT, width=55), height=51, width=54, align=uiconst.TOPLEFT, texturePath='res:/UI/Texture/classes/ProjectDiscovery/categorySelected.png')
        self.selection_legend_label_container = uiprimitives.Container(parent=uiprimitives.Container(parent=self.selection_legend_container, align=uiconst.TOLEFT, width=145), align=uiconst.TOLEFT, width=50)
        self.selection_legend_label_header = EveLabelMediumBold(parent=self.selection_legend_label_container, text=localization.GetByLabel('UI/ProjectDiscovery/Subcellular/ResultScreen/SelectionLegendLabelHeader'), align=uiconst.TOPLEFT, top=20, left=5)
        self.popular_legend_container = uiprimitives.Container(parent=self.legend_container, align=uiconst.TOTOP, height=70)
        self.popular_sprite_container = uiprimitives.Container(parent=self.popular_legend_container, align=uiconst.TOLEFT, width=55)
        self.popular_other_hex = uiprimitives.Sprite(parent=self.popular_sprite_container, texturePath='res:/UI/Texture/classes/ProjectDiscovery/hexOutline.png', height=40, width=44, align=uiconst.CENTERTOP, state=uiconst.UI_DISABLED, color=(0.32, 0.32, 0.32, 1))
        self.popular_other_sprite = uiprimitives.Sprite(parent=self.popular_sprite_container, height=32, width=36, top=4, align=uiconst.CENTERTOP, texturePath='res:/UI/Texture/classes/ProjectDiscovery/hexMask.png')
        self.popular_other_sprite.SetRGB(0.33, 0.49, 0.26, 1)
        self.popular_legend_label_container = uiprimitives.Container(parent=uiprimitives.Container(parent=self.popular_legend_container, align=uiconst.TOLEFT, width=145), align=uiconst.CENTERLEFT, width=50, height=65, top=-5)
        self.popular_legend_label_header = EveLabelMediumBold(parent=self.popular_legend_label_container, text=localization.GetByLabel('UI/ProjectDiscovery/Subcellular/ResultScreen/PopularLegendLabelHeader'), align=uiconst.TOPLEFT)
        self.popular_legend_label = uicontrols.Label(parent=self.popular_legend_label_container, text=localization.GetByLabel('UI/ProjectDiscovery/Subcellular/ResultScreen/PopularLegendLabel'), align=uiconst.CENTERLEFT, width=200)
        self.unpopular_legend_container = uiprimitives.Container(parent=self.legend_container, align=uiconst.TOTOP, height=70)
        self.unpopular_sprite_container = uiprimitives.Container(parent=self.unpopular_legend_container, align=uiconst.TOLEFT, width=55)
        self.unpopular_other_hex = uiprimitives.Sprite(parent=self.unpopular_sprite_container, texturePath='res:/UI/Texture/classes/ProjectDiscovery/hexOutline.png', height=40, width=44, align=uiconst.CENTERTOP, state=uiconst.UI_DISABLED, color=(0.32, 0.32, 0.32, 1))
        self.unpopular_other_sprite = uiprimitives.Sprite(parent=self.unpopular_sprite_container, height=32, width=36, top=4, align=uiconst.CENTERTOP, texturePath='res:/UI/Texture/classes/ProjectDiscovery/hexMask.png')
        self.unpopular_other_sprite.SetRGB(0.5, 0.22, 0.17, 1)
        self.unpopular_legend_label_container = uiprimitives.Container(parent=uiprimitives.Container(parent=self.unpopular_legend_container, align=uiconst.TOLEFT, width=145), align=uiconst.CENTERLEFT, width=50, height=65, top=-5)
        self.unpopular_legend_label_header = EveLabelMediumBold(parent=self.unpopular_legend_label_container, text=localization.GetByLabel('UI/ProjectDiscovery/Subcellular/ResultScreen/UnpopularLegendLabelHeader'), align=uiconst.TOPLEFT)
        self.unpopular_legend_label = uicontrols.Label(parent=self.unpopular_legend_label_container, text=localization.GetByLabel('UI/ProjectDiscovery/Subcellular/ResultScreen/UnpopularLegendLabel'), align=uiconst.CENTERLEFT, width=150)

    def create_known_solution_tooltip(self):
        self.correct_legend_container = uiprimitives.Container(parent=self.legend_container, align=uiconst.TOTOP, height=70)
        self.correct_legend_sprite = uiprimitives.Sprite(parent=uiprimitives.Container(parent=self.correct_legend_container, align=uiconst.TOLEFT, width=55), height=51, width=54, align=uiconst.TOPLEFT, texturePath='res:/UI/Texture/classes/ProjectDiscovery/categoryMatch.png')
        self.correct_legend_label_container = uiprimitives.Container(parent=uiprimitives.Container(parent=self.correct_legend_container, align=uiconst.TOLEFT, width=145), align=uiconst.CENTERLEFT, width=50, height=65)
        self.correct_legend_label_header = EveLabelMediumBold(parent=self.correct_legend_label_container, text=localization.GetByLabel('UI/ProjectDiscovery/Subcellular/ResultScreen/CorrectLegendLabelHeader'), align=uiconst.TOPLEFT)
        self.correct_legend_label = uicontrols.Label(parent=self.correct_legend_label_container, text=localization.GetByLabel('UI/ProjectDiscovery/Subcellular/ResultScreen/CorrectLegendLabel'), align=uiconst.CENTERLEFT, width=200)
        self.missed_legend_container = uiprimitives.Container(parent=self.legend_container, align=uiconst.TOTOP, height=70)
        self.missed_legend_sprite = uiprimitives.Sprite(parent=uiprimitives.Container(parent=self.missed_legend_container, align=uiconst.TOLEFT, width=55), height=51, width=54, align=uiconst.TOPLEFT, texturePath='res:/UI/Texture/classes/ProjectDiscovery/categoryMissed.png')
        self.missed_legend_label_container = uiprimitives.Container(parent=uiprimitives.Container(parent=self.missed_legend_container, align=uiconst.TOLEFT, width=145), align=uiconst.CENTERLEFT, width=50, height=65)
        self.missed_legend_label_header = EveLabelMediumBold(parent=self.missed_legend_label_container, text=localization.GetByLabel('UI/ProjectDiscovery/Subcellular/ResultScreen/MissedLegendLabelHeader'), align=uiconst.TOPLEFT)
        self.missed_legend_label = uicontrols.Label(parent=self.missed_legend_label_container, text=localization.GetByLabel('UI/ProjectDiscovery/Subcellular/ResultScreen/MissedLegendLabel'), align=uiconst.CENTERLEFT, width=150)
        self.unmatched_legend_container = uiprimitives.Container(parent=self.legend_container, align=uiconst.TOTOP, height=70)
        self.unmatched_legend_sprite = uiprimitives.Sprite(parent=uiprimitives.Container(parent=self.unmatched_legend_container, align=uiconst.TOLEFT, width=55), height=51, width=54, align=uiconst.TOPLEFT, texturePath='res:/UI/Texture/classes/ProjectDiscovery/categoryWrong.png')
        self.unmatched_legend_label_container = uiprimitives.Container(parent=uiprimitives.Container(parent=self.unmatched_legend_container, align=uiconst.TOLEFT, width=145), align=uiconst.CENTERLEFT, width=50, height=65)
        self.unmatched_legend_label_header = EveLabelMediumBold(parent=self.unmatched_legend_label_container, text=localization.GetByLabel('UI/ProjectDiscovery/Subcellular/ResultScreen/UnmatchedLegendLabelHeader'), align=uiconst.TOPLEFT)
        self.unmatched_legend_label = uicontrols.Label(parent=self.unmatched_legend_label_container, text=localization.GetByLabel('UI/ProjectDiscovery/Subcellular/ResultScreen/UnmatchedLegendLabel'), align=uiconst.CENTERLEFT, width=150, top=5)
