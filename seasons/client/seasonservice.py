#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\seasons\client\seasonservice.py
import log
from collections import OrderedDict
from eve.client.script.ui.view.viewStateConst import ViewState
from eve.common.script.util.notificationconst import notificationTypeSeasonalChallengeCompleted
from gametime import GetWallclockTime
from notifications.common.notification import Notification
from seasons.client.seasonwindow import SeasonWindow
from seasons.common.const import SEASONAL_EVENTS_ID
from seasons.common.exceptions import ChallengeForCharacterNotFoundError
from service import Service
import uthread2
CHALLENGE_UPDATE_SLEEP_SECONDS = 1

class SeasonService(Service):
    __guid__ = 'svc.SeasonService'
    serviceName = 'svc.seasonService'
    __displayname__ = 'SeasonService'
    __servicename__ = 'SeasonService'
    __notifyevents__ = ['OnChallengeCompleted',
     'OnChallengeExpired',
     'OnSeasonalGoalsReset',
     'OnChallengeProgressUpdate',
     'OnSeasonalGoalCompleted',
     'OnSeasonalPointsUpdated',
     'OnSessionChanged',
     'OnViewStateChanged']

    def Run(self, *args, **kwargs):
        try:
            self._initialize_season_manager()
            self._initialize_finished_goals()
            self._initialize_challenges()
        except Exception:
            self.current_season = None
            log.LogTraceback('Failed to run seasonService')

        self.update_challenge_thread = None
        self.challenges_for_update = []
        Service.Run(self, *args, **kwargs)

    def _initialize_season_manager(self):
        self.season_manager = sm.RemoteSvc('seasonManager')
        self._fetch_season_data()
        if not self.is_season_active():
            settings.char.ui.Set('season_progress_width', 0)
            self._set_last_active_challenge(None)
            self.last_user_progress = None
        else:
            self.last_user_progress = self.season_manager.get_last_active_character_progress()
        self.current_user_progress = None

    def _initialize_finished_goals(self):
        self.finished_goals = OrderedDict()

    def _initialize_challenges(self):
        self.challenges = {}

    def is_season_active(self):
        return self.current_season is not None

    def get_challenge(self, challenge_id):
        if challenge_id is None:
            return
        try:
            if challenge_id not in self.challenges:
                self.challenges[challenge_id] = self.season_manager.get_challenge(challenge_id)
        except ChallengeForCharacterNotFoundError:
            self.challenges[challenge_id] = None

        return self.challenges[challenge_id]

    def get_active_challenges_by_character_id(self):
        return self.current_user_progress.challenges.copy()

    def get_max_active_challenges(self):
        return self.season_manager.get_max_active_challenges()

    def _set_last_active_challenge(self, challenge_id):
        settings.char.ui.Set('challenges_last_active', challenge_id)

    def get_last_active_challenge(self):
        last_active_challenge = settings.char.ui.Get('challenges_last_active', None)
        active_challenge_ids = self.current_user_progress.challenges.keys()
        if len(active_challenge_ids) == 0:
            raise ChallengeForCharacterNotFoundError
        if last_active_challenge is None or last_active_challenge not in active_challenge_ids:
            last_active_challenge = active_challenge_ids[0]
            self._set_last_active_challenge(last_active_challenge)
        return last_active_challenge

    def get_season_background(self):
        return self.current_season.background

    def get_season_background_minimal(self):
        return self.current_season.background_minimal

    def get_season_background_no_logo(self):
        return self.current_season.background_no_logo

    def get_season_title(self):
        return self.current_season.title

    def get_season_description(self):
        return self.current_season.description

    def get_season_news(self):
        return self.current_season.news

    def get_season_remaining_seconds(self):
        return self.season_manager.get_season_remaining_time()

    def get_challenges_for_last_active_character(self):
        return self.last_user_progress.challenges.copy()

    def get_points(self):
        if not session.charid:
            return self.last_user_progress.seasonal_points
        return self.current_user_progress.seasonal_points

    def get_max_points(self):
        if not session.charid:
            return self.last_user_progress.max_seasonal_points
        return self.current_user_progress.max_seasonal_points

    def get_rewards(self):
        if not session.charid:
            return self.last_user_progress.seasonal_goals
        return self.current_user_progress.seasonal_goals

    def get_next_reward(self):
        if not session.charid:
            return self.last_user_progress.next_seasonal_goal
        return self.current_user_progress.next_seasonal_goal

    def get_last_reward(self):
        if not session.charid:
            return self.last_user_progress.last_seasonal_goal
        return self.current_user_progress.last_seasonal_goal

    def _add_finished_goal(self, goal_id, goal_data):
        self.finished_goals[goal_id] = goal_data

    def get_and_clear_recently_finished_goals(self):
        finished_goals = self.finished_goals.copy()
        self._initialize_finished_goals()
        return finished_goals

    def OnChallengeProgressUpdate(self, challenge_id, new_progress):
        self._add_to_update_challenges(challenge_id, new_progress, self._update_challenge_progress)

    def _ReplaceChallenge(self, challenge_id, new_challenge):
        if challenge_id not in self.current_user_progress.challenges:
            self.LogException('Replace challenge failed for challenge: %s - character: %s' % (str(challenge_id), str(session.charid)))
            return
        del self.current_user_progress.challenges[challenge_id]
        if new_challenge is not None:
            self.current_user_progress.challenges[new_challenge.challenge_id] = new_challenge

    def OnChallengeCompleted(self, challenge_id, new_challenge):
        self._add_to_update_challenges(challenge_id, new_challenge, self._complete_challenge)

    def _AdvanceSeasonalGoal(self):
        self.current_user_progress.next_seasonal_goal['completed'] = True
        self._UpdateNextSeasonalGoal()

    def OnSeasonalGoalCompleted(self, goal_id, goal_data):
        self._add_finished_goal(goal_id, goal_data)
        self._blink_neocom()
        self._AdvanceSeasonalGoal()
        sm.GetService('audio').SendUIEvent('scope_earn_rewards_play')
        sm.ScatterEvent('OnSeasonalGoalCompletedInClient', goal_id, goal_data)

    def _fetch_character_data(self, character_id):
        if character_id is None or not self.is_season_active():
            return
        if self.current_user_progress is None or self.current_user_progress.character_id != character_id:
            if self.last_user_progress and self.last_user_progress.character_id == character_id:
                self.current_user_progress = self.last_user_progress
            else:
                self.current_user_progress = self.season_manager.get_character_progress_by_character_id()

    def OnSessionChanged(self, isRemote, sess, change):
        self._fetch_character_data(sess.charid)

    def OnViewStateChanged(self, oldViewName, newViewName):
        if oldViewName in (ViewState.CharacterSelector, ViewState.CharacterCreation):
            char_id = getattr(session, 'charid', None)
            self._fetch_character_data(char_id)

    def _fetch_season_data(self):
        self.current_season = self.season_manager.get_current_season()

    def _UpdateNextSeasonalGoal(self):
        for goal in self.current_user_progress.seasonal_goals.values():
            if not goal['completed']:
                self.current_user_progress.next_seasonal_goal = goal
                return

        self.current_user_progress.next_seasonal_goal = None

    def OnSeasonalPointsUpdated(self, season_id, new_points):
        if season_id == self.current_season.season_id:
            self.current_user_progress.seasonal_points = new_points
            self._UpdateNextSeasonalGoal()
            sm.ScatterEvent('OnSeasonalPointsUpdatedInClient', new_points)
        else:
            self.LogWarn('Trying to update points for season %s which is not active' % season_id)

    def _blink_neocom(self):
        sm.GetService('neocom').Blink(SEASONAL_EVENTS_ID)

    def OnChallengeExpired(self, challenge_id, new_challenge):
        self._add_to_update_challenges(challenge_id, new_challenge, self._expire_challenge)

    def OnSeasonalGoalsReset(self):
        sorted_goals = sorted(self.current_user_progress.seasonal_goals.keys())
        for goal_id in sorted_goals:
            self.current_user_progress.seasonal_goals[goal_id]['completed'] = False

        self.current_user_progress.seasonal_points = 0
        first_goal_key = sorted_goals[0]
        self.current_user_progress.next_seasonal_goal = self.current_user_progress.seasonal_goals[first_goal_key]
        sm.ScatterEvent('OnSeasonalGoalsResetInClient')

    def _add_to_update_challenges(self, challenge_id, new_challenge_or_progress, update_function):
        self.challenges_for_update.append((challenge_id, new_challenge_or_progress, update_function))
        if self.update_challenge_thread is None or not self.update_challenge_thread.IsAlive():
            self.update_challenge_thread = uthread2.StartTasklet(self._update_challenges)

    def _update_challenges(self):
        while len(self.challenges_for_update):
            challenge_id, new_challenge_or_progress, update_function = self.challenges_for_update.pop(0)
            update_function(challenge_id, new_challenge_or_progress)
            uthread2.sleep(CHALLENGE_UPDATE_SLEEP_SECONDS)

    def _expire_challenge(self, old_challenge_id, new_challenge):
        self._ReplaceChallenge(old_challenge_id, new_challenge)
        self._set_last_active_challenge(None)
        sm.ScatterEvent('OnChallengeExpiredInClient', old_challenge_id)

    def _complete_challenge(self, old_challenge_id, new_challenge):
        last_active_challenge = self.get_challenge(old_challenge_id)
        points_awarded = last_active_challenge.points_awarded
        self._ReplaceChallenge(old_challenge_id, new_challenge)
        self._set_last_active_challenge(None)
        sm.GetService('audio').SendUIEvent('scope_complete_task_play')
        sm.ScatterEvent('OnChallengeCompletedInClient', old_challenge_id)

    def _update_challenge_progress(self, challenge_id, new_progress):
        self._set_last_active_challenge(challenge_id)
        try:
            self.current_user_progress.challenges[challenge_id].progress = new_progress
        except KeyError:
            self.LogException('Update progress failed for challenge: %s - character: %s.' % (str(challenge_id), str(session.charid)))
            return

        sm.ScatterEvent('OnChallengeProgressUpdateInClient', challenge_id, new_progress)
