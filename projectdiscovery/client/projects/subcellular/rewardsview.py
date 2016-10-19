#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\projectdiscovery\client\projects\subcellular\rewardsview.py
import math
import blue
import carbonui.const as uiconst
import localization
import taskimages
import uicls
import uicontrols
import uiprimitives
import uthread
from carbon.common.script.util.format import FmtAmt
from carbonui.primitives.base import ScaleDpi
from carbonui.uianimations import animations
from eve.client.script.ui.control.eveLabel import EveLabelLargeBold
from projectdiscovery.client import const
from projectdiscovery.client.util.eventlistener import eventlistener, on_event
from projectdiscovery.client.util.util import calculate_score_bar_length, calculate_rank_band

@eventlistener()

class RewardsView(uiprimitives.Container):
    default_clipChildren = True

    def ApplyAttributes(self, attributes):
        super(RewardsView, self).ApplyAttributes(attributes)
        self.projectDiscovery = sm.RemoteSvc('ProjectDiscovery')
        self.isTraining = False
        self.XP_Reward = 0
        self.ISK_Reward = 0
        self.bottom_container = attributes.get('bottom_container')
        self.playerState = attributes.get('playerState')
        self.experience = self.playerState.experience
        self.player_rank = self.playerState.rank
        self.total_xp_needed_for_current_rank = self.projectDiscovery.get_total_needed_xp(self.player_rank)
        self.total_xp_needed_for_next_rank = self.projectDiscovery.get_total_needed_xp(self.player_rank + 1)
        self.original_rank_band = calculate_rank_band(self.player_rank)
        self.rank_band = self.original_rank_band
        self.score_bar_height = 7
        self.setup_rewards_screen()

    def setup_rewards_screen(self):
        self.parent_container = uiprimitives.Container(name='parentContainer', parent=self, align=uiconst.CENTER, height=400, width=450, top=-10)
        self.background_container = uiprimitives.Container(name='background', parent=self.parent_container, width=450, height=285, align=uiconst.CENTERTOP, bgColor=(0.037, 0.037, 0.037, 1))
        uicontrols.Frame(parent=self.background_container, color=(0.36, 0.36, 0.36, 0.36))
        self.main_container = uiprimitives.Container(name='mainContainer', parent=self.background_container, width=440, height=275, align=uiconst.CENTER)
        self.rank_container = uiprimitives.Container(name='rankContainer', parent=self.parent_container, width=450, height=100, align=uiconst.CENTERBOTTOM, bgColor=(0.037, 0.037, 0.037, 1))
        uicontrols.Frame(parent=self.rank_container, color=(0.36, 0.36, 0.36, 0.36))
        self.agent_container = uiprimitives.Container(name='agentContainer', parent=self.main_container, align=uiconst.TOPLEFT, height=180, width=150, left=5, top=5)
        self.agent_image = uiprimitives.Sprite(name='agentImage', parent=self.agent_container, align=uiconst.TOPLEFT, height=150, width=150, texturePath='res:/UI/Texture/classes/ProjectDiscovery/lundberg.jpg')
        self.agent_label = uicontrols.Label(name='agentName', parent=self.agent_container, align=uiconst.BOTTOMLEFT, text=localization.GetByLabel('UI/ProjectDiscovery/AgentName'), top=5, height=18, fontsize=14)
        self.SOE_image = uiprimitives.Sprite(name='SOE_logo', parent=self.main_container, align=uiconst.BOTTOMLEFT, height=75, width=75, texturePath='res:/UI/Texture/Corps/14_128_1.png')
        self.text_container = uiprimitives.Container(name='textContainer', parent=self.main_container, align=uiconst.TOPRIGHT, width=270, height=80, top=20)
        self.text_header_container = uiprimitives.Container(name='textHeaderContainer', parent=self.text_container, align=uiconst.TOTOP, height=20)
        self.header_message = EveLabelLargeBold(parent=self.text_header_container, align=uiconst.TOTOP, text=localization.GetByLabel('UI/ProjectDiscovery/Subcellular/RewardsScreen/Header'))
        self.main_message = uicontrols.Label(parent=self.text_container, align=uiconst.TOTOP, text=localization.GetByLabel('UI/ProjectDiscovery/Subcellular/RewardsScreen/ThanksMessage'))
        self.setup_reward_container()
        self.setup_reward_footer()
        self.setup_continue_button()

    def setup_continue_button(self):
        self.main_button_container = uiprimitives.Container(name='MainRewardsContinueButtonContainer', parent=self.bottom_container, align=uiconst.CENTERBOTTOM, width=355, height=53, bgTexturePath='res:/UI/Texture/classes/ProjectDiscovery/footerBG.png', state=uiconst.UI_HIDDEN)
        self.continue_button_container = uiprimitives.Container(name='RewardsContinueButtonContainer', parent=self.main_button_container, width=250, align=uiconst.CENTER, height=40, top=5)
        self.continue_button = uicontrols.Button(name='RewardViewContinueButton', parent=self.continue_button_container, align=uiconst.CENTER, label=localization.GetByLabel('UI/ProjectDiscovery/Subcellular/RewardsScreen/ContinueButtonLabel'), fontsize=18, fixedwidth=170, fixedheight=30, func=lambda x: self.fade_out(), state=uiconst.UI_DISABLED)
        uiprimitives.Sprite(parent=self.continue_button_container, align=uiconst.CENTERLEFT, width=34, height=20, texturePath='res:/UI/Texture/classes/ProjectDiscovery/submitArrow.png', opacity=0.7)
        uiprimitives.Sprite(parent=uiprimitives.Transform(parent=self.continue_button_container, align=uiconst.CENTERRIGHT, width=34, height=20, rotation=math.pi), align=uiconst.CENTERRIGHT, width=34, height=20, texturePath='res:/UI/Texture/classes/ProjectDiscovery/submitArrow.png', opacity=0.7)

    def setup_reward_container(self):
        self.reward_container = uiprimitives.Container(name='reward_container', parent=self.main_container, align=uiconst.BOTTOMRIGHT, width=270, height=130)
        self.setup_experience_reward_container()
        self.setup_isk_reward_container()
        self.setup_analysis_kredits_container()

    def setup_experience_reward_container(self):
        self.experience_points_container = uiprimitives.Container(parent=self.reward_container, width=360, height=40, align=uiconst.TOTOP, bgColor=(0.36, 0.36, 0.36, 0.36))
        self.experience_points_icon = uiprimitives.Sprite(parent=uiprimitives.Container(parent=self.experience_points_container, width=40, height=40, align=uiconst.TOLEFT, left=10), name='experience_points_Logo', align=uiconst.TOALL, texturePath='res:/UI/Texture/classes/ProjectDiscovery/experiencePointsIcon.png')
        self.experience_points_label = uicontrols.Label(parent=uiprimitives.Container(parent=self.experience_points_container, align=uiconst.TOLEFT, width=75, height=50), align=uiconst.CENTERLEFT, text=localization.GetByLabel('UI/ProjectDiscovery/Subcellular/RewardsScreen/ExperiencePointsLabel'), fontsize=14)
        self.experience_points = uicontrols.Label(parent=uiprimitives.Container(parent=self.experience_points_container, align=uiconst.CENTERRIGHT, width=20, height=50, left=25), align=uiconst.CENTER, fontsize=16, text='0')

    def setup_isk_reward_container(self):
        self.ISK_reward_container = uiprimitives.Container(parent=self.reward_container, width=360, height=40, align=uiconst.TOTOP, top=5, bgColor=(0.36, 0.36, 0.36, 0.36))
        self.ISK_reward_icon = uiprimitives.Sprite(parent=uiprimitives.Container(parent=self.ISK_reward_container, width=40, height=40, align=uiconst.TOLEFT, left=10), name='ISK_reward_Logo', align=uiconst.TOALL, texturePath='res:/ui/texture/WindowIcons/wallet.png')
        self.ISK_reward_label = uicontrols.Label(parent=uiprimitives.Container(parent=self.ISK_reward_container, align=uiconst.TOLEFT, width=75, height=50), align=uiconst.CENTERLEFT, text=localization.GetByLabel('UI/ProjectDiscovery/Subcellular/RewardsScreen/IskLabel'), fontsize=14)
        self.ISK_reward = uicontrols.Label(parent=uiprimitives.Container(parent=self.ISK_reward_container, align=uiconst.CENTERRIGHT, width=20, height=50, left=25), align=uiconst.CENTER, fontsize=16, text='0')

    def setup_analysis_kredits_container(self):
        self.analysis_kredits_container = uiprimitives.Container(parent=self.reward_container, width=360, height=40, align=uiconst.TOTOP, bgColor=(0.36, 0.36, 0.36, 0.36), top=5)
        self.analysis_kredits_icon = uiprimitives.Sprite(parent=uiprimitives.Container(parent=self.analysis_kredits_container, width=40, height=40, align=uiconst.TOLEFT, left=10), name='Analyst_points_Logo', align=uiconst.TOALL, texturePath='res:/UI/Texture/classes/ProjectDiscovery/analysisKreditsIcon.png')
        self.analysis_kredits_label = uicontrols.Label(parent=uiprimitives.Container(parent=self.analysis_kredits_container, align=uiconst.TOLEFT, width=75, height=50), align=uiconst.CENTERLEFT, text=localization.GetByLabel('UI/ProjectDiscovery/AnalysisKreditsLabel'), fontsize=14)
        self.analysis_kredits = uicontrols.Label(parent=uiprimitives.Container(parent=self.analysis_kredits_container, align=uiconst.CENTERRIGHT, width=20, height=50, left=25), align=uiconst.CENTER, fontsize=16, text='0')

    def setup_reward_footer(self):
        self.rank_header = uiprimitives.Container(parent=self.rank_container, align=uiconst.TOTOP, height=20, bgColor=(0.36, 0.36, 0.36, 0.36))
        uicontrols.Label(parent=self.rank_header, text=localization.GetByLabel('UI/ProjectDiscovery/Subcellular/RewardsScreen/ScientistRank'), align=uiconst.CENTERLEFT, left=5)
        self.footer_container = uiprimitives.Container(name='footerContainer', parent=self.rank_container, align=uiconst.CENTER, height=65, width=435, top=10, bgTexturePath='res:/UI/Texture/classes/ProjectDiscovery/rankInfoBackground.png')
        self.rank_icon_container = uiprimitives.Container(name='rankIconContainer', parent=self.footer_container, align=uiconst.CENTERLEFT, width=64, height=64, bgTexturePath='res:/UI/Texture/classes/ProjectDiscovery/rankIconBackground.png')
        self.rank_icon = uiprimitives.Sprite(name='rank_icon', parent=self.rank_icon_container, align=uiconst.CENTER, width=64, height=64, texturePath=self.get_rank_icon_path())
        self.rank_information_container = uiprimitives.Container(name='rankInfoContainer', parent=self.footer_container, align=uiconst.TOLEFT, width=360, left=64)
        self.rank_label = uicontrols.Label(name='rankLabel', parent=self.rank_information_container, align=uiconst.TOPLEFT, text='', fontsize=14)
        self.rank = uicontrols.Label(name='rank', parent=self.rank_information_container, align=uiconst.TOPRIGHT, text='', fontsize=14)
        self.scorebar_container = uiprimitives.Container(name='scorebarContainer', parent=self.rank_information_container, align=uiconst.TOBOTTOM, height=60)
        self._initialize_score_bar_length()
        self.total_points_container = uiprimitives.Container(name='totalPointsContainer', parent=self.scorebar_container, align=uiconst.TOTOP, width=self.scorebar_container.width, height=15, top=10)
        self.total_points_label = uicontrols.Label(name='totalPointsLabel', parent=self.total_points_container, align=uiconst.TOPLEFT, text=localization.GetByLabel('UI/ProjectDiscovery/Subcellular/RewardsScreen/TotalExperiencePointsLabel'), fontsize=12)
        self.total_points = uicontrols.Label(name='totalPoints', parent=self.total_points_container, align=uiconst.TOPRIGHT, fontsize=12)
        self.score_bar = uicls.VectorLine(name='ScoreBar', parent=self.scorebar_container, align=uiconst.TOTOP, translationFrom=(0, self.score_bar_height), translationTo=(1, self.score_bar_height), colorFrom=(1.0, 1.0, 1.0, 0.95), colorTo=(1.0, 1.0, 1.0, 0.95), widthFrom=3, widthTo=3)
        self.empty_score_bar = uicls.VectorLine(name='EmptyScoreBar', parent=self.scorebar_container, align=uiconst.TOTOP_NOPUSH, translationFrom=(0, self.score_bar_height), translationTo=(self.scoreBarLength, self.score_bar_height), colorFrom=(0.0, 0.0, 0.0, 0.75), colorTo=(0.0, 0.0, 0.0, 0.75), widthFrom=4, widthTo=4)
        self.needed_points_container = uiprimitives.Container(parent=self.scorebar_container, align=uiconst.TOBOTTOM, width=self.scorebar_container.width, height=15, top=10)
        self.needed_points_label = uicontrols.Label(parent=self.needed_points_container, align=uiconst.BOTTOMLEFT, text=localization.GetByLabel('UI/ProjectDiscovery/Subcellular/RewardsScreen/NeededXpLabel'), fontsize=12)
        self.needed_points = uicontrols.Label(parent=self.needed_points_container, align=uiconst.TOPRIGHT, fontsize=12)

    def _initialize_score_bar_length(self):
        self.scoreBarLength = self.rank_information_container.width
        self.oldScoreBarLength = self.calculate_score_bar_length()

    def close(self):
        self.main_button_container.Close()
        self.Close()

    @on_event(const.Events.CloseResult)
    def on_result_closed(self, result):
        self.set_score_bar_length(self.calculate_score_bar_length())
        self.XP_Reward = result['XP_Reward']
        self.ISK_Reward = result['ISK_Reward']
        self.AK_Reward = result['AK_Reward']
        self.playerState = result['playerState']
        self.show_reward_containers()
        if 'isTraining' in result:
            self.display_training_complete_message()
        else:
            self.display_normal_thanking_message()
        self.update_analysis_kredits_container()
        self.update_isk_reward_container()
        self.update_player_info()
        self.update_experience_labels()

    def display_normal_thanking_message(self):
        self.header_message.SetText(localization.GetByLabel('UI/ProjectDiscovery/Subcellular/RewardsScreen/Header'))
        self.main_message.SetText(localization.GetByLabel('UI/ProjectDiscovery/Subcellular/RewardsScreen/ThanksMessage'))

    def display_training_complete_message(self):
        self.header_message.SetText(localization.GetByLabel('UI/ProjectDiscovery/Subcellular/RewardsScreen/TutorialCompletedHeader'))
        self.main_message.SetText(localization.GetByLabel('UI/ProjectDiscovery/Subcellular/RewardsScreen/TutorialCompletedMessage'))

    def show_reward_containers(self):
        self.experience_points_container.SetOpacity(1)
        self.ISK_reward_container.SetOpacity(1)
        self.analysis_kredits_container.SetOpacity(1)

    def update_experience_labels(self):
        self.needed_points.SetText('{:,.0f}'.format(self.needed_experience))
        self.total_points.SetText('{:,.0f}'.format(self.experience))

    def update_player_info(self):
        self.experience = self.playerState.experience
        self.player_rank = self.playerState.rank
        self.total_xp_needed_for_current_rank = self.projectDiscovery.get_total_needed_xp(self.player_rank)
        self.total_xp_needed_for_next_rank = self.projectDiscovery.get_total_needed_xp(self.player_rank + 1)
        self.needed_experience = self.total_xp_needed_for_next_rank - self.experience

    def update_isk_reward_container(self):
        if self.ISK_Reward == 0:
            self.ISK_reward_container.SetOpacity(0)
        if self.XP_Reward <= 0:
            self.experience_points_container.SetOpacity(0)
            self.main_message.SetText(localization.GetByLabel('UI/ProjectDiscovery/Subcellular/RewardsScreen/ThanksButNoRewardsMessage'))

    def update_analysis_kredits_container(self):
        if self.AK_Reward == 0:
            self.analysis_kredits_container.SetOpacity(0)
        else:
            self.analysis_kredits.SetText(str(FmtAmt(self.AK_Reward)))
            self.header_message.SetText(localization.GetByLabel('UI/ProjectDiscovery/Subcellular/RewardsScreen/NewRankHeader'))
            self.main_message.SetText(localization.GetByLabel('UI/ProjectDiscovery/Subcellular/RewardsScreen/NewRankMessage'))

    def set_score_bar_length(self, length):
        if self.score_bar:
            self.score_bar.translationTo = (length, self.score_bar_height)

    def update_rank_values(self):
        self.update_player_info()
        self.rank.SetText(const.Texts.RankLabel + str(self.player_rank))
        self.update_experience_labels()
        self.rank_label.SetText(localization.GetByLabel('UI/ProjectDiscovery/RankTitles/RankTitle' + str(self.rank_band)))
        self.tick_rewards()
        self.update_experience_values()

    def update_experience_values(self):
        self.oldExperience = self.experience
        self.experience = self.playerState.experience
        uthread.new(self.update_experience_points_values)
        self.oldNeededExperience = self.needed_experience
        self.needed_experience = self.total_xp_needed_for_next_rank - self.experience
        uthread.new(self.update_needed_experience_points_values)

    def tick_rewards(self):
        uthread.new(self.update_xp_reward)
        uthread.new(self.update_isk_reward)

    def update_needed_experience_points_values(self):
        while self.oldNeededExperience > self.needed_experience:
            self.oldNeededExperience -= 2
            self.needed_points.SetText(FmtAmt(self.oldNeededExperience))
            blue.synchro.Sleep(1)

        self.needed_points.SetText(FmtAmt(self.oldNeededExperience))

    def update_experience_points_values(self):
        while self.oldExperience < self.experience:
            self.oldExperience += 2
            self.total_points.SetText(FmtAmt(self.oldExperience))
            blue.synchro.Sleep(1)

        self.total_points.SetText(FmtAmt(self.experience))

    def update_xp_reward(self):
        counter = 0
        while counter + 2 < self.XP_Reward:
            counter += 2
            self.experience_points.SetText(counter)
            blue.synchro.Sleep(1)

        self.experience_points.SetText(FmtAmt(self.XP_Reward))

    def update_isk_reward(self):
        if self.ISK_Reward:
            counter = 0
            while counter + 1000 < self.ISK_Reward:
                counter += 1000
                self.ISK_reward.SetText(FmtAmt(counter))
                blue.synchro.Sleep(1)

            self.ISK_reward.SetText(FmtAmt(self.ISK_Reward))

    def reset_reward_labels(self):
        self.ISK_reward.SetText('0')
        self.experience_points.SetText('0')

    def get_rank_icon_path(self):
        return const.rank_paths[calculate_rank_band(self.player_rank)]

    def get_rank_band(self):
        rank_band = int(math.ceil(float(self.player_rank) / 10 + 0.1))
        if rank_band < 1:
            rank_band = 1
        elif rank_band > 11:
            rank_band = 11
        return rank_band

    def calculate_score_bar_length(self):
        return calculate_score_bar_length(self.experience, self.total_xp_needed_for_current_rank, self.total_xp_needed_for_next_rank, self.scoreBarLength)

    def update_score_bar(self):
        if self.XP_Reward <= 0:
            return
        sm.ScatterEvent(const.Events.UpdateScoreBar, self.playerState)
        new_score_bar_length = self.calculate_score_bar_length()
        counter = self.oldScoreBarLength
        self.oldScoreBarLength = new_score_bar_length
        uthread.new(self.tick_score_bar, counter, new_score_bar_length)

    def tick_score_bar(self, counter, new_score_bar_length):
        while counter >= new_score_bar_length:
            counter += 1
            if counter >= ScaleDpi(self.scoreBarLength):
                counter = -1
                self.rank_band = calculate_rank_band(self.player_rank)
                if self.rank_band > self.original_rank_band:
                    self.original_rank_band = self.rank_band
                    self.fade_badge_out()
            else:
                self.set_score_bar_length(counter)
                blue.synchro.Sleep(1)

        while counter < new_score_bar_length:
            counter += 1
            self.set_score_bar_length(counter)
            blue.synchro.Sleep(1)

    def fade_badge_out(self):
        animations.FadeOut(self.rank_icon, duration=0.5, callback=self.fade_badge_in)
        animations.FadeOut(self.rank_label, duration=0.5)

    def fade_badge_in(self):
        self.rank_icon.SetTexturePath(self.get_rank_icon_path())
        animations.FadeIn(self.rank_icon, timeOffset=0.2, duration=0.5, curveType=uiconst.ANIM_OVERSHOT5)
        self.rank_label.SetText(localization.GetByLabel('UI/ProjectDiscovery/RankTitles/RankTitle' + str(self.rank_band)))
        animations.FadeIn(self.rank_label, timeOffset=0.2, duration=0.4, curveType=uiconst.ANIM_OVERSHOT5)

    def fade_out(self):
        self.main_button_container.SetState(uiconst.UI_HIDDEN)
        sm.ScatterEvent(const.Events.RewardViewFadeOut)
        animations.FadeOut(self, duration=0.5, callback=self.continue_from_reward)

    @on_event(const.Events.ProcessingViewFinished)
    def fade_in(self):
        self.update_rank_values()
        animations.FadeIn(self, duration=0.5, callback=self.update_score_bar)
        sm.GetService('audio').SendUIEvent(const.Sounds.RewardsWindowLoopPlay)
        self.enable_button()

    def continue_from_reward(self):
        if self.isTraining:
            if self.tutorial_completed:
                sm.ScatterEvent(const.Events.ProjectDiscoveryStarted, True)
        else:
            sm.ScatterEvent(const.Events.ContinueFromReward)
        self.reset_reward_labels()
        self.disable_button()
        taskimages.Audio.play_sound = True
        sm.GetService('audio').SendUIEvent(const.Sounds.RewardsWindowLoopStop)
        sm.GetService('audio').SendUIEvent(const.Sounds.RewardsWindowClosePlay)
        sm.GetService('audio').SendUIEvent(const.Sounds.MainImageLoopPlay)

    def enable_button(self):
        self.continue_button.state = uiconst.UI_NORMAL
        self.main_button_container.SetState(uiconst.UI_NORMAL)

    def disable_button(self):
        self.continue_button.state = uiconst.UI_DISABLED
