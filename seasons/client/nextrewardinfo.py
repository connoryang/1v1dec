#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\seasons\client\nextrewardinfo.py
import carbonui.const as uiconst
from carbonui.primitives.container import Container
from eve.client.script.ui.control.eveLabel import EveLabelSmall
from seasons.client.const import get_next_reward_label
from seasons.client.const import get_all_rewards_unlocked_label, get_all_rewards_unlocked_state
from seasons.client.seasonpoints import SeasonPoints
from seasons.client.uiutils import SEASON_THEME_TEXT_COLOR_REGULAR
NEXT_REWARD_LABEL_TOP = 6
NEXT_REWARD_STATE_TOP = 7
POINTS_ICON_SIZE = 20
NEXT_REWARD_LABEL_HEIGHT = 15
POINTS_HEIGHT = 15

class NextRewardInfo(Container):
    __notifyevents__ = ['OnSeasonalGoalCompletedInClient', 'OnSeasonalGoalsResetInClient']

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        sm.RegisterNotify(self)
        self.season_service = attributes.season_service
        self.base_container = Container(name='base_container', parent=self, align=uiconst.CENTERRIGHT, width=self.width, height=self.height)
        next_reward_label_container = Container(name='next_reward_label_container', parent=self.base_container, align=uiconst.TOPRIGHT, width=self.width, height=NEXT_REWARD_LABEL_HEIGHT)
        self.next_reward_label = EveLabelSmall(name='next_reward_label', parent=next_reward_label_container, align=uiconst.TORIGHT, text='', top=NEXT_REWARD_LABEL_TOP)
        self.next_reward_label.color = SEASON_THEME_TEXT_COLOR_REGULAR
        self.next_reward_state_container = None
        self._update_text()

    def _update_text(self):
        next_reward = self.season_service.get_next_reward()
        self.next_reward_label.text = self._get_next_reward_label(next_reward)
        if self.next_reward_state_container:
            self.next_reward_state_container.Flush()
            self.next_reward_state_container.Close()
        self.next_reward_state_container = Container(name='next_reward_state_container', parent=self.base_container, align=uiconst.TOPRIGHT, width=self.width, height=POINTS_ICON_SIZE)
        if next_reward:
            self.next_reward_state = SeasonPoints(name='next_reward_points', parent=self.next_reward_state_container, points=next_reward['points_required'], season_points_size=POINTS_ICON_SIZE, reward_label_class=EveLabelSmall, align=uiconst.TOPRIGHT, height=POINTS_HEIGHT, top=NEXT_REWARD_LABEL_HEIGHT + NEXT_REWARD_STATE_TOP)
            return
        self.next_reward_state = EveLabelSmall(name='next_reward_state', parent=self.next_reward_state_container, align=uiconst.TORIGHT, text=get_all_rewards_unlocked_state(), top=NEXT_REWARD_LABEL_HEIGHT + NEXT_REWARD_STATE_TOP)
        self.next_reward_state.color = SEASON_THEME_TEXT_COLOR_REGULAR

    def _get_next_reward_label(self, next_reward):
        if next_reward:
            return get_next_reward_label()
        return get_all_rewards_unlocked_label()

    def OnSeasonalGoalCompletedInClient(self, reward_id, reward_data):
        self._update_text()

    def OnSeasonalGoalsResetInClient(self):
        self._update_text()
