#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\infoPanels\infoPanelChallenges.py
from carbon.common.script.util.timerstuff import AutoTimer
import carbonui.const as uiconst
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from eve.client.script.ui.shared.infoPanels.InfoPanelBase import InfoPanelBase
from eve.client.script.ui.shared.infoPanels.infoPanelConst import PANEL_CHALLENGES, MODE_COLLAPSED
from localization import GetByLabel
from seasons.client.challengeinfopaneltaskentry import ChallengeInfoPanelTaskEntry
from seasons.client.seasonwindow import SeasonWindow
from seasons.common.exceptions import ChallengeForCharacterNotFoundError
CHALLENGES_PANEL_ICON = 'res:/UI/Texture/classes/Seasons/iconScopeNetwork_16.png'
CHALLENGES_PANEL_LABEL = 'UI/Seasons/InfoPanelChallengesTitle'
CHALLENGE_CONTAINER_GRID_COLUMNS = 2
CHALLENGE_CONTAINER_GRID_OPACITY = 0.0
OPEN_CHALLENGES_BUTTON_ICON_TEXTURE_PATH = 'res:/ui/Texture/Classes/InfoPanels/opportunitiesTreeIcon.png'
OPEN_CHALLENGES_BUTTON_ICON_SIZE = 16
OPEN_CHALLENGES_LABEL = 'UI/Seasons/SeasonWindowInfoPanelLink'
OPEN_CHALLENGES_LABEL_LEFT = 4
HIDE_CHALLENGE_TIMEOUT = 20000
COMPLETED_CHALLENGE_FADE_OUT_DURATION = 3.0

class InfoPanelChallenges(InfoPanelBase):
    __guid__ = 'uicls.InfoPanelChallenges'
    default_name = 'InfoPanelChallenges'
    default_iconTexturePath = CHALLENGES_PANEL_ICON
    default_state = uiconst.UI_PICKCHILDREN
    default_height = 120
    label = CHALLENGES_PANEL_LABEL
    hasSettings = False
    panelTypeID = PANEL_CHALLENGES
    challengeContainer = None
    __notifyevents__ = ['OnChallengeProgressUpdateInClient', 'OnChallengeCompletedInClient', 'OnChallengeExpiredInClient']

    def ApplyAttributes(self, attributes):
        self.seasonService = sm.GetService('seasonService')
        self._LoadActiveChallenge()
        self.challengeContainer = None
        self.challengeTaskEntry = None
        self.openChallengesLinkGrid = None
        InfoPanelBase.ApplyAttributes(self, attributes)
        self.titleLabel = self.headerCls(name='title', text='<color=white>%s</color>' % GetByLabel(self.label), parent=self.headerCont, align=uiconst.CENTERLEFT, state=uiconst.UI_DISABLED)
        self._ConstructPanel()

    def _LoadActiveChallenge(self):
        try:
            challengeID = self.seasonService.get_last_active_challenge()
            self.challenge = self._GetChallenge(challengeID)
        except ChallengeForCharacterNotFoundError:
            self.challenge = None

    @staticmethod
    def IsAvailable():
        return sm.GetService('seasonService').is_season_active()

    def _IsCollapsed(self):
        return sm.GetService('infoPanel').GetModeForPanel(PANEL_CHALLENGES) == MODE_COLLAPSED

    def _ShouldShowChallengeDetails(self):
        return not self._IsCollapsed() and settings.char.ui.Get('show_challenge_details_in_info_panel', True)

    def _ConstructChallengeContainer(self):
        if not self.challengeContainer or self.challengeContainer.destroyed:
            self.mainCont.Flush()
            if self.challenge is None:
                self.challengeContainer = None
            else:
                self.challengeContainer = ContainerAutoSize(parent=self.mainCont, name='challengeContainer', align=uiconst.TOTOP)
        if self.challengeContainer:
            self.challengeContainer.Flush()

    def _ConstructChallengeDetails(self):
        if self.challenge is None:
            self.challengeTaskEntry = None
            return
        self.challengeTaskEntry = ChallengeInfoPanelTaskEntry(name='challengeInfoPanelTaskEntry', parent=self.challengeContainer, align=uiconst.TOTOP, challenge=self.challenge, open_challenges_function=self._OpenChallenges, show_details=self._ShouldShowChallengeDetails())

    def _GetChallenge(self, challengeID):
        return self.seasonService.get_challenge(challengeID)

    def _OpenChallenges(self, *args):
        SeasonWindow.Open()

    def OnChallengeProgressUpdateInClient(self, challengeID, newProgress):
        self.hideChallengeTimerThread = None
        if not self._IsChallengeAlreadyShown(challengeID):
            self.challenge = self._GetChallenge(challengeID)
            self._ConstructPanel()
        self.challengeTaskEntry.update_challenge_progress(newProgress)

    def OnChallengeCompletedInClient(self, oldChallengeID):
        if oldChallengeID is None:
            return
        if not self._IsChallengeAlreadyShown(oldChallengeID):
            self.challenge = self.seasonService.get_challenge(oldChallengeID)
            self._ConstructPanel()
        self.challengeTaskEntry.complete_challenge()
        setattr(self, 'hideChallengeTimerThread', AutoTimer(HIDE_CHALLENGE_TIMEOUT, self._HideCompletedChallenge))

    def OnChallengeExpiredInClient(self, challengeID):
        if challengeID is None:
            return
        if not self._IsChallengeAlreadyShown(challengeID):
            self.challenge = self.seasonService.get_challenge(challengeID)
            self._ConstructPanel()
        self.challengeTaskEntry.expire_challenge()
        setattr(self, 'hideChallengeTimerThread', AutoTimer(HIDE_CHALLENGE_TIMEOUT, self._HideCompletedChallenge))

    def _IsAnyChallengeShown(self):
        return self.challenge is not None

    def _IsChallengeAlreadyShown(self, challengeID):
        return self._IsAnyChallengeShown() and self.challenge.challenge_id == challengeID

    def _HideCompletedChallenge(self):
        try:
            if self.hideChallengeTimerThread:
                uicore.animations.FadeOut(self.challengeTaskEntry, duration=COMPLETED_CHALLENGE_FADE_OUT_DURATION, callback=self._ResetPanel())
        finally:
            self.hideChallengeTimerThread = None

        self._ResetPanel()

    def _ConstructPanel(self):
        self._ConstructChallengeContainer()
        self._ConstructChallengeDetails()

    def _ResetPanel(self):
        self.challengeContainer = None
        self._LoadActiveChallenge()
        self._ConstructPanel()
