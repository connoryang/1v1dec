#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\achievements\common\opportunityTaskMap.py
from achievements.common.achievementConst import AchievementConsts

class OpportunityConst:
    LOOK = 100
    FLY = 101
    KILL = 102
    SKILL = 103
    WARP = 104
    STATION = 105
    MINE = 106
    MARKET = 107
    FITTING = 108
    SOCIAL = 109
    STARGATE = 110
    ROUTE = 111
    INDUSTRY = 112
    EXPLORATION = 113
    AGENTS = 114
    DEATH = 115
    CORP = 116
    WORMHOLE = 117
    SALVAGE = 118
    PODDED = 119
    AGENTSEXP = 120
    LOOT = 121


GROUP_TO_TASK_IDS = {OpportunityConst.LOOK: [AchievementConsts.UI_ROTATE_IN_SPACE,
                         AchievementConsts.UI_ZOOM_IN_SPACE,
                         AchievementConsts.LOOK_AT_OBJECT,
                         AchievementConsts.LOOK_AT_OWN_SHIP],
 OpportunityConst.FLY: [AchievementConsts.DOUBLE_CLICK, AchievementConsts.APPROACH],
 OpportunityConst.KILL: [AchievementConsts.ORBIT_NPC,
                         AchievementConsts.LOCK_NPC,
                         AchievementConsts.ACTIVATE_GUN,
                         AchievementConsts.KILL_NPC,
                         AchievementConsts.KILL_NPC_MULTI],
 OpportunityConst.SKILL: [AchievementConsts.START_TRAINING],
 OpportunityConst.WARP: [AchievementConsts.WARP],
 OpportunityConst.STATION: [AchievementConsts.DOCK_IN_STATION, AchievementConsts.MOVE_FROM_CARGO_TO_HANGAR],
 OpportunityConst.MINE: [AchievementConsts.UNDOCK_FROM_STATION,
                         AchievementConsts.ORBIT_ASTEROID,
                         AchievementConsts.LOCK_ASTEROID,
                         AchievementConsts.ACTIVATE_MINER,
                         AchievementConsts.MINE_ORE,
                         AchievementConsts.REFINE_ORE],
 OpportunityConst.MARKET: [AchievementConsts.USE_STARGATE, AchievementConsts.PLACE_SELL_ORDER, AchievementConsts.PLACE_BUY_ORDER],
 OpportunityConst.FITTING: [AchievementConsts.UNFIT_MODULE,
                            AchievementConsts.FIT_HISLOT,
                            AchievementConsts.FIT_MEDSLOT,
                            AchievementConsts.FIT_LOSLOT],
 OpportunityConst.SOCIAL: [AchievementConsts.CHAT_IN_LOCAL, AchievementConsts.INVITE_TO_CONVO, AchievementConsts.ADD_CONTACT],
 OpportunityConst.STARGATE: [AchievementConsts.USE_STARGATE],
 OpportunityConst.ROUTE: [AchievementConsts.TALK_TO_AGENT,
                          AchievementConsts.SET_DESTINATION,
                          AchievementConsts.OPEN_MAP,
                          AchievementConsts.JUMP_TO_NEXT_SYSTEM,
                          AchievementConsts.ACTIVATE_AUTOPILOT],
 OpportunityConst.INDUSTRY: [AchievementConsts.LOAD_BLUEPRINT, AchievementConsts.START_INDUSTRY_JOB, AchievementConsts.DELIVER_INDUSTRY_JOB],
 OpportunityConst.EXPLORATION: [AchievementConsts.ENTER_DISTRIBUTION_SITE,
                                AchievementConsts.FIT_PROBE_LAUNCHER,
                                AchievementConsts.LAUNCH_PROBES,
                                AchievementConsts.GET_PERFECT_SCAN_RESULTS],
 OpportunityConst.AGENTS: [AchievementConsts.ACCEPT_MISSION, AchievementConsts.COMPLETE_MISSION],
 OpportunityConst.DEATH: [AchievementConsts.LOSE_SHIP, AchievementConsts.ACTIVATE_SHIP],
 OpportunityConst.CORP: [AchievementConsts.OPEN_CORP_FINDER, AchievementConsts.JOIN_CORP],
 OpportunityConst.WORMHOLE: [AchievementConsts.ENTER_WORMHOLE, AchievementConsts.BOOKMARK_WORMHOLE],
 OpportunityConst.SALVAGE: [AchievementConsts.USE_SALVAGER, AchievementConsts.SALVAGE],
 OpportunityConst.PODDED: [AchievementConsts.LOSE_POD],
 OpportunityConst.AGENTSEXP: [AchievementConsts.CAREER_AGENT, AchievementConsts.ACCEPT_MISSION, AchievementConsts.COMPLETE_MISSION],
 OpportunityConst.LOOT: [AchievementConsts.LOOT_FROM_NPC_WRECK, AchievementConsts.LOOT_MULTI_NPC_WRECK, AchievementConsts.WARP]}
REWARD_1 = 25000
REWARD_2 = 50000
REWARD_3 = 75000
REWARD_4 = 100000
REWARD_5 = 150000
REWARD_6 = 200000
GROUP_TO_REWARD = {OpportunityConst.LOOK: REWARD_1,
 OpportunityConst.FLY: REWARD_1,
 OpportunityConst.KILL: REWARD_2,
 OpportunityConst.SKILL: REWARD_1,
 OpportunityConst.WARP: REWARD_2,
 OpportunityConst.STATION: REWARD_2,
 OpportunityConst.MINE: REWARD_2,
 OpportunityConst.MARKET: REWARD_3,
 OpportunityConst.FITTING: REWARD_3,
 OpportunityConst.SOCIAL: REWARD_4,
 OpportunityConst.STARGATE: REWARD_3,
 OpportunityConst.ROUTE: REWARD_4,
 OpportunityConst.INDUSTRY: REWARD_5,
 OpportunityConst.EXPLORATION: REWARD_5,
 OpportunityConst.AGENTS: REWARD_4,
 OpportunityConst.DEATH: REWARD_6,
 OpportunityConst.CORP: REWARD_5,
 OpportunityConst.WORMHOLE: REWARD_5,
 OpportunityConst.SALVAGE: REWARD_5,
 OpportunityConst.PODDED: REWARD_6,
 OpportunityConst.AGENTSEXP: REWARD_1,
 OpportunityConst.LOOT: REWARD_2}

def BuildIndex(idArrayDict):
    index = {}
    for key, taskList in idArrayDict.iteritems():
        for value in taskList:
            index[value] = key

    return index


TASK_ID_TO_GROUP = BuildIndex(GROUP_TO_TASK_IDS)
