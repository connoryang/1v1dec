#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\seasons\client\const.py
from carbon.common.script.util.format import FmtAmt
from localization import GetByLabel
SCOPE_LOGO_RES_PATH = 'res:/UI/Texture/WindowIcons/scopeNetwork.png'
SEASON_POINTS_ICON_PATH = 'res:/UI/Texture/classes/Seasons/iconSeasonPoints.png'
REWARD_ACHIEVED_ICON_PATH = 'res:/UI/Texture/classes/Seasons/achievedStar.png'
SEASON_LEADERBOARDS_ICON = 'res:/UI/Texture/WindowIcons/achievements.png'
SEASONS_TITLE_LABEL = 'UI/Seasons/Title'
SEASONS_SUBCAPTION_LABEL = 'UI/Seasons/Subcaption'
SEASON_TIME_REMAINING_LABEL = 'UI/Seasons/SeasonTimeRemaining'
TIME_REMAINING_LABEL = 'UI/Seasons/TimeRemaining'
REWARD_UNLOCKED_HEADER_LABEL = 'UI/Seasons/RewardUnlockedHeader'
REWARD_UNLOCKED_BODY_LABEL = 'UI/Seasons/RewardUnlockedBody'
NEXT_REWARD_LABEL = 'UI/Seasons/NextReward'
ALL_REWARDS_UNLOCKED_FIRST_LINE_LABEL = 'UI/Seasons/AllRewardsUnlockedFirstLine'
ALL_REWARDS_UNLOCKED_SECOND_LINE_LABEL = 'UI/Seasons/AllRewardsUnlockedSecondLine'
SEASON_TOP_CAPSULEERS_LABEL = 'UI/Seasons/TopCapsuleers'
CHALLENGE_PROGRESS_COUNTER_LABEL = 'UI/Seasons/ChallengeProgressCounter'
SEASONS_INSTRUCTIONS_LABEL = 'UI/Seasons/Instructions'
SEASONS_CURRENT_EVENT_LABEL = 'UI/Seasons/CurrentEvent'
SEASON_CURRENT_BANNER_HEIGHT = 341
SEASON_CURRENT_BANNER_WIDTH = 607
DEFAULT_ANIMATE_PROGRESS = True

def get_seasons_title_label_path():
    return SEASONS_TITLE_LABEL


def get_seasons_title():
    return GetByLabel(get_seasons_title_label_path())


def get_seasons_subcaption():
    return GetByLabel(SEASONS_SUBCAPTION_LABEL)


def get_points_label_text(points):
    return FmtAmt(points)


def get_challenge_progress_counter_label_text(challenge):
    return GetByLabel(CHALLENGE_PROGRESS_COUNTER_LABEL, progress=FmtAmt(challenge.progress), max_progress=FmtAmt(challenge.max_progress), challenge_progress_text=challenge.progress_text)


def get_season_time_remaining(time_remaining):
    return GetByLabel(SEASON_TIME_REMAINING_LABEL, time_remaining=time_remaining)


def get_time_remaining_string(days, hours, minutes, seconds):
    return GetByLabel(TIME_REMAINING_LABEL, days=int(days), hours=int(hours), minutes=int(minutes))


def get_leaderboards_link_title():
    return GetByLabel(SEASON_TOP_CAPSULEERS_LABEL)


def get_reward_unlocked_header():
    return GetByLabel(REWARD_UNLOCKED_HEADER_LABEL)


def get_reward_unlocked_body():
    return GetByLabel(REWARD_UNLOCKED_BODY_LABEL)


def get_next_reward_label():
    return GetByLabel(NEXT_REWARD_LABEL)


def get_all_rewards_unlocked_label():
    return GetByLabel(ALL_REWARDS_UNLOCKED_FIRST_LINE_LABEL)


def get_all_rewards_unlocked_state():
    return GetByLabel(ALL_REWARDS_UNLOCKED_SECOND_LINE_LABEL)


def get_seasons_instructions():
    return GetByLabel(SEASONS_INSTRUCTIONS_LABEL)


def get_current_event_label():
    return GetByLabel(SEASONS_CURRENT_EVENT_LABEL)
