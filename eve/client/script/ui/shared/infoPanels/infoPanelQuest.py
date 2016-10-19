#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\infoPanels\infoPanelQuest.py
from __builtin__ import sm
from achievements.client.achievementTaskEntry import BlurredBackgroundSprite
import blue
from carbonui import const as uiconst
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.fill import Fill
from carbonui.primitives.layoutGrid import LayoutGrid
from carbonui.primitives.sprite import Sprite
from carbonui.uianimations import animations
from eve.client.script.ui.control.eveLabel import EveLabelMedium
from eve.client.script.ui.control.themeColored import FillThemeColored
from eve.client.script.ui.shared.infoPanels.InfoPanelBase import InfoPanelBase
from eve.client.script.ui.shared.infoPanels.infoPanelControls import InfoPanelHeaderBackground
from eve.client.script.ui.shared.infoPanels import infoPanelConst
import localization
import uthread

class InfoPanelQuests(InfoPanelBase):
    default_name = 'InfoPanelQuests'
    default_iconTexturePath = 'res:/UI/Texture/Classes/InfoPanels/daily_opportunities.png'
    default_state = uiconst.UI_PICKCHILDREN
    hasSettings = False
    label = 'UI/Quest/InfoPanelTitle'
    panelTypeID = infoPanelConst.PANEL_QUESTS
    __notifyevents__ = InfoPanelBase.__notifyevents__ + ['OnQuestCompletedClient']

    def ApplyAttributes(self, attributes):
        super(InfoPanelQuests, self).ApplyAttributes(attributes)
        self.titleLabel = self.headerCls(parent=self.headerCont, align=uiconst.CENTERLEFT, state=uiconst.UI_DISABLED, text=localization.GetByLabel('UI/Quest/InfoPanelTitle'), color=(1.0, 1.0, 1.0, 1.0))
        self.topCont.clipChildren = True

    @staticmethod
    def IsAvailable():
        return sm.GetService('quest').IsFeatureActive()

    def ConstructNormal(self):
        if self.mainCont.children:
            return
        quests = sm.GetService('quest').GetQuests()
        for quest in quests:
            QuestEntry(parent=self.mainCont, align=uiconst.TOTOP, quest=quest)

    def OnQuestCompletedClient(self, quest):
        for entry in self.mainCont.children:
            try:
                entry.UpdateQuest(quest)
            except TypeError:
                pass

        swoop = Sprite(parent=self.topCont, align=uiconst.RELATIVE, top=0, rotation=-0.3, width=300, height=50, texturePath='res:/UI/Texture/classes/Animations/swoopGradient.png', opacity=0.3)
        animations.MorphScalar(swoop, 'left', startVal=-300, endVal=300, duration=1.2, callback=swoop.Close)
        animations.FadeTo(swoop, startVal=0.0, endVal=0.25, curveType=uiconst.ANIM_BOUNCE, duration=0.7, timeOffset=0.1)


RES_AVAILABLE = 'res:/UI/Texture/Classes/InfoPanels/opportunitiesIncompleteBox.png'
RES_COMPLETED = 'res:/UI/Texture/Classes/InfoPanels/opportunitiesCheck.png'

class QuestEntry(ContainerAutoSize):
    default_alignMode = uiconst.TOTOP
    default_clipChildren = False
    default_state = uiconst.UI_NORMAL
    default_padTop = 4

    def ApplyAttributes(self, attributes):
        super(QuestEntry, self).ApplyAttributes(attributes)
        self.quest = attributes.quest
        self.isCompleteMode = self.quest.isComplete
        self._updateThread = None
        self.details = None
        self.Layout()
        self.UpdateQuest()
        if self.isCompleteMode:
            self.ShowCompleted()
        else:
            self.ShowDetails()

    def Layout(self):
        Fill(bgParent=self, color=(0, 0, 0, 0.2))
        BlurredBackgroundSprite(bgParent=self, color=(1, 1, 1, 0.9))
        headerContainer = ContainerAutoSize(parent=self, align=uiconst.TOTOP, alignMode=uiconst.TOPLEFT)
        self.completedFill = FillThemeColored(bgParent=headerContainer, colorType=uiconst.COLORTYPE_UIHILIGHT, opacity=0.0)
        self.headerFill = InfoPanelHeaderBackground(bgParent=headerContainer)
        headerGrid = LayoutGrid(parent=headerContainer)
        if self.quest.isComplete:
            texturePath = RES_COMPLETED
        else:
            texturePath = RES_AVAILABLE
        self.check = Sprite(align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED, texturePath=texturePath, width=14, height=14)
        headerGrid.AddCell(self.check, cellPadding=(4, 3, 4, 3))
        headerGrid.AddCell(EveLabelMedium(align=uiconst.TOPLEFT, text=self.quest.titleLabel), cellPadding=(0, 2, 0, 2))
        self.timer = EveLabelMedium(parent=headerContainer, align=uiconst.CENTERRIGHT, state=uiconst.UI_DISABLED, left=4, opacity=0.0)

    def ShowCompleted(self):
        self.check.SetTexturePath(RES_COMPLETED)
        self.completedFill.opacity = 0.5
        self.timer.opacity = 0.6
        self.timer.state = uiconst.UI_NORMAL

    def UpdateQuest(self, quest = None):
        if quest is None:
            quest = self.quest
        if self.quest.id != quest.id:
            return
        self.quest = quest
        if not self.isCompleteMode and self.quest.isComplete:
            self.isCompleteMode = True
            self.AnimComplete()
            self.timer.state = uiconst.UI_NORMAL
        elif self.isCompleteMode and not self.quest.isComplete:
            self.isCompleteMode = False
            self.AnimAvailable()
            self.timer.state = uiconst.UI_DISABLED
        if self.isCompleteMode:
            if not self._updateThread:
                self._updateThread = uthread.new(self._UpdateThread)
            self.timer.text = self.quest.nextAvailableShortLabel
            self.timer.hint = self.quest.nextAvailableLabel

    def AnimComplete(self):
        self.check.SetTexturePath(RES_COMPLETED)
        animations.BlinkIn(self.check)
        animations.MorphScalar(self.completedFill, 'displayWidth', startVal=0.0, endVal=self.displayWidth)
        animations.FadeTo(self.completedFill, startVal=1.5, endVal=0.5, duration=1.5, timeOffset=0.5)
        animations.FadeIn(self.timer, endVal=0.6, timeOffset=0.5)

    def AnimAvailable(self):
        self.check.SetTexturePath(RES_AVAILABLE)
        animations.BlinkIn(self.check)
        animations.FadeTo(self.completedFill, startVal=self.completedFill.opacity, endVal=0.0)
        animations.FadeOut(self.timer, duration=0.3)

    def OnClick(self, *args):
        self.ToggleDetails()

    def ToggleDetails(self):
        if self.details and not self.details.destroyed:
            self.HideDetails()
        else:
            self.ShowDetails()

    def HideDetails(self):
        if not self.details or self.details.destroyed:
            return
        details = self.details
        self.details = None
        details.DisableAutoSize()
        animations.FadeOut(details, duration=0.15)
        animations.MorphScalar(details, 'height', startVal=details.height, endVal=0, duration=0.15, callback=details.Close)

    def ShowDetails(self):
        if self.details:
            return

        def thread():
            self.details = ContainerAutoSize(parent=self, align=uiconst.TOTOP, clipChildren=True)
            self.details.DisableAutoSize()
            EveLabelMedium(parent=self.details, align=uiconst.TOTOP, padding=(6, 3, 6, 2), text=self.quest.descriptionLabel)
            EveLabelMedium(parent=self.details, align=uiconst.TOTOP, padding=(6, 3, 6, 2), text=localization.GetByLabel('UI/Quest/RewardTitle'))
            EveLabelMedium(parent=self.details, align=uiconst.TOTOP, padding=(12, 6, 6, 12), text=self.quest.rewardLabel)
            _, height = self.details.GetAutoSize()
            animations.FadeIn(self.details, duration=0.3)
            animations.MorphScalar(self.details, 'height', startVal=self.details.height, endVal=height, duration=0.25, callback=self.details.EnableAutoSize)

        uthread.new(thread)

    def OnMouseEnter(self, *args):
        animations.FadeTo(self.headerFill.colorFill, startVal=self.headerFill.colorFill.opacity, endVal=0.3, curveType=uiconst.ANIM_OVERSHOT3, duration=0.5)

    def OnMouseExit(self, *args):
        animations.FadeTo(self.headerFill.colorFill, startVal=self.headerFill.colorFill.opacity, endVal=0.15, duration=0.1)

    def _UpdateThread(self):
        while self and not self.destroyed and self.isCompleteMode:
            self.UpdateQuest()
            blue.pyos.synchro.SleepWallclock(1000)

        self._updateThread = None


def __SakeReloadHook():
    try:
        sm.GetService('infoPanel').ReconstructAllPanels(animate=True)
    except Exception:
        import log
        log.LogException()
