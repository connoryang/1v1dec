#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\achievements\common\achievementGroups.py
from achievements.common.achievementConst import AchievementConsts
from achievements.common.achievementGroup import AchievementGroup
from opportunityTaskMap import OpportunityConst
from opportunityTaskMap import GROUP_TO_TASK_IDS
from achievements.common.achievementGroupStore import AchievementGroupStore
group103 = AchievementGroup(nameLabelPath='Achievements/GroupNameText/welcome', descriptionLabelPath='Achievements/GroupDescriptionText/welcome', notificationPath='Achievements/GroupNotificationText/welcome', groupID=OpportunityConst.SKILL, achievementTaskIDs=GROUP_TO_TASK_IDS[OpportunityConst.SKILL], groupConnections=[OpportunityConst.LOOK], treePosition=(2, 3))
group100 = AchievementGroup(nameLabelPath='Achievements/GroupNameText/look', descriptionLabelPath='Achievements/GroupDescriptionText/look', notificationPath='Achievements/GroupNotificationText/look', groupID=OpportunityConst.LOOK, achievementTaskIDs=GROUP_TO_TASK_IDS[OpportunityConst.LOOK], groupConnections=[OpportunityConst.FLY], treePosition=(1, 1))
group101 = AchievementGroup(nameLabelPath='Achievements/GroupNameText/fly', descriptionLabelPath='Achievements/GroupDescriptionText/fly', notificationPath='Achievements/GroupNotificationText/fly', groupID=OpportunityConst.FLY, achievementTaskIDs=GROUP_TO_TASK_IDS[OpportunityConst.FLY], groupConnections=[OpportunityConst.KILL], treePosition=(1, 2))
group102 = AchievementGroup(nameLabelPath='Achievements/GroupNameText/kill', descriptionLabelPath='Achievements/GroupDescriptionText/kill', notificationPath='Achievements/GroupNotificationText/kill', groupID=OpportunityConst.KILL, achievementTaskIDs=GROUP_TO_TASK_IDS[OpportunityConst.KILL], groupConnections=[OpportunityConst.LOOT], treePosition=(1, 3))
group121 = AchievementGroup(nameLabelPath='Achievements/GroupNameText/loot', descriptionLabelPath='Achievements/GroupDescriptionText/loot', notificationPath='Achievements/GroupNotificationText/loot', groupID=OpportunityConst.LOOT, achievementTaskIDs=GROUP_TO_TASK_IDS[OpportunityConst.LOOT], groupConnections=[OpportunityConst.STATION], treePosition=(7, 2))
group105 = AchievementGroup(nameLabelPath='Achievements/GroupNameText/station', descriptionLabelPath='Achievements/GroupDescriptionText/station', notificationPath='Achievements/GroupNotificationText/station', groupID=OpportunityConst.STATION, achievementTaskIDs=GROUP_TO_TASK_IDS[OpportunityConst.STATION], groupConnections=[OpportunityConst.FITTING], treePosition=(2, 1))
group108 = AchievementGroup(nameLabelPath='Achievements/GroupNameText/fitting', descriptionLabelPath='Achievements/GroupDescriptionText/fitting', notificationPath='Achievements/GroupNotificationText/fitting', groupID=OpportunityConst.FITTING, achievementTaskIDs=GROUP_TO_TASK_IDS[OpportunityConst.FITTING], groupConnections=[OpportunityConst.MINE], treePosition=(3, 3))
group106 = AchievementGroup(nameLabelPath='Achievements/GroupNameText/mine', descriptionLabelPath='Achievements/GroupDescriptionText/mine', notificationPath='Achievements/GroupNotificationText/mine', groupID=OpportunityConst.MINE, achievementTaskIDs=GROUP_TO_TASK_IDS[OpportunityConst.MINE], groupConnections=[OpportunityConst.MARKET], treePosition=(3, 1))
group107 = AchievementGroup(nameLabelPath='Achievements/GroupNameText/market', descriptionLabelPath='Achievements/GroupDescriptionText/market', notificationPath='Achievements/GroupNotificationText/market', groupID=OpportunityConst.MARKET, achievementTaskIDs=GROUP_TO_TASK_IDS[OpportunityConst.MARKET], groupConnections=[OpportunityConst.ROUTE], treePosition=(3, 2))
group111 = AchievementGroup(nameLabelPath='Achievements/GroupNameText/career', descriptionLabelPath='Achievements/GroupDescriptionText/career', notificationPath='Achievements/GroupNotificationText/career', groupID=OpportunityConst.ROUTE, achievementTaskIDs=GROUP_TO_TASK_IDS[OpportunityConst.ROUTE], groupConnections=[OpportunityConst.AGENTS], treePosition=(4, 1))
group114 = AchievementGroup(nameLabelPath='Achievements/GroupNameText/mission', descriptionLabelPath='Achievements/GroupDescriptionText/mission', notificationPath='Achievements/GroupNotificationText/mission', groupID=OpportunityConst.AGENTS, achievementTaskIDs=GROUP_TO_TASK_IDS[OpportunityConst.AGENTS], groupConnections=[OpportunityConst.INDUSTRY], treePosition=(5, 3))
group112 = AchievementGroup(nameLabelPath='Achievements/GroupNameText/industry', descriptionLabelPath='Achievements/GroupDescriptionText/industry', notificationPath='Achievements/GroupNotificationText/industry', groupID=OpportunityConst.INDUSTRY, achievementTaskIDs=GROUP_TO_TASK_IDS[OpportunityConst.INDUSTRY], groupConnections=[OpportunityConst.EXPLORATION], treePosition=(5, 1), suggestedGroup=False)
group113 = AchievementGroup(nameLabelPath='Achievements/GroupNameText/exploration', descriptionLabelPath='Achievements/GroupDescriptionText/exploration', notificationPath='Achievements/GroupNotificationText/exploration', groupID=OpportunityConst.EXPLORATION, achievementTaskIDs=GROUP_TO_TASK_IDS[OpportunityConst.EXPLORATION], groupConnections=[OpportunityConst.DEATH], treePosition=(5, 2), suggestedGroup=False)
group115 = AchievementGroup(nameLabelPath='Achievements/GroupNameText/death', descriptionLabelPath='Achievements/GroupDescriptionText/death', notificationPath='Achievements/GroupNotificationText/death', groupID=OpportunityConst.DEATH, achievementTaskIDs=GROUP_TO_TASK_IDS[OpportunityConst.DEATH], groupConnections=[OpportunityConst.CORP], treePosition=(6, 3), triggeredBy=AchievementConsts.LOSE_SHIP, suggestedGroup=False)
group116 = AchievementGroup(nameLabelPath='Achievements/GroupNameText/corp', descriptionLabelPath='Achievements/GroupDescriptionText/corp', notificationPath='Achievements/GroupNotificationText/corp', groupID=OpportunityConst.CORP, achievementTaskIDs=GROUP_TO_TASK_IDS[OpportunityConst.CORP], groupConnections=[OpportunityConst.WORMHOLE], treePosition=(6, 2), suggestedGroup=False)
group117 = AchievementGroup(nameLabelPath='Achievements/GroupNameText/wormhole', descriptionLabelPath='Achievements/GroupDescriptionText/wormhole', notificationPath='Achievements/GroupNotificationText/wormhole', groupID=OpportunityConst.WORMHOLE, achievementTaskIDs=GROUP_TO_TASK_IDS[OpportunityConst.WORMHOLE], groupConnections=[OpportunityConst.SALVAGE], treePosition=(6, 1), triggeredBy=AchievementConsts.ENTER_WORMHOLE, suggestedGroup=False)
group118 = AchievementGroup(nameLabelPath='Achievements/GroupNameText/salvage', descriptionLabelPath='Achievements/GroupDescriptionText/salvage', notificationPath='Achievements/GroupNotificationText/salvage', groupID=OpportunityConst.SALVAGE, achievementTaskIDs=GROUP_TO_TASK_IDS[OpportunityConst.SALVAGE], groupConnections=[OpportunityConst.PODDED], treePosition=(7, 1), suggestedGroup=False)
group119 = AchievementGroup(nameLabelPath='Achievements/GroupNameText/podded', descriptionLabelPath='Achievements/GroupDescriptionText/podded', notificationPath='Achievements/GroupNotificationText/podded', groupID=OpportunityConst.PODDED, achievementTaskIDs=GROUP_TO_TASK_IDS[OpportunityConst.PODDED], groupConnections=[OpportunityConst.SOCIAL], treePosition=(7, 2), triggeredBy=AchievementConsts.LOSE_POD, suggestedGroup=False)
group109 = AchievementGroup(nameLabelPath='Achievements/GroupNameText/social', descriptionLabelPath='Achievements/GroupDescriptionText/social', notificationPath='Achievements/GroupNotificationText/social', groupID=OpportunityConst.SOCIAL, achievementTaskIDs=GROUP_TO_TASK_IDS[OpportunityConst.SOCIAL], groupConnections=[], treePosition=(4, 3), suggestedGroup=False)
group120 = AchievementGroup(nameLabelPath='Achievements/GroupNameText/agents', descriptionLabelPath='Achievements/GroupDescriptionText/career', notificationPath='Achievements/GroupNotificationText/agents', groupID=OpportunityConst.AGENTSEXP, achievementTaskIDs=GROUP_TO_TASK_IDS[OpportunityConst.AGENTSEXP], groupConnections=[OpportunityConst.DEATH], treePosition=(8, 7), suggestedGroup=False)
group104 = AchievementGroup(nameLabelPath='Achievements/GroupNameText/warp', descriptionLabelPath='Achievements/GroupDescriptionText/warp', notificationPath='Achievements/GroupNotificationText/warp', groupID=OpportunityConst.WARP, achievementTaskIDs=GROUP_TO_TASK_IDS[OpportunityConst.WARP], groupConnections=[OpportunityConst.STATION], treePosition=(2, 2), suggestedGroup=False)
group110 = AchievementGroup(nameLabelPath='Achievements/GroupNameText/stargate', descriptionLabelPath='Achievements/GroupDescriptionText/stargate', notificationPath='Achievements/GroupNotificationText/stargate', groupID=OpportunityConst.STARGATE, achievementTaskIDs=GROUP_TO_TASK_IDS[OpportunityConst.STARGATE], groupConnections=[OpportunityConst.ROUTE], treePosition=(4, 2), suggestedGroup=False)
group109.SetTreePosition((16, 4))
group119.SetTreePosition((10, 11))
group118.SetTreePosition((12, 4))
group117.SetTreePosition((14, 11))
group116.SetTreePosition((15, 4))
group115.SetTreePosition((9, 10))
group113.SetTreePosition((13, 4))
group112.SetTreePosition((16, 6))
group114.SetTreePosition((14, 7))
group111.SetTreePosition((12, 6))
group107.SetTreePosition((10, 5))
group106.SetTreePosition((10, 7))
group108.SetTreePosition((12, 8))
group105.SetTreePosition((14, 9))
group121.SetTreePosition((12, 10))
group102.SetTreePosition((10, 9))
group101.SetTreePosition((8, 8))
group100.SetTreePosition((8, 6))
group103.SetTreePosition((8, 4))
_achievementGroups3 = [group103,
 group100,
 group101,
 group102,
 group121,
 group105,
 group108,
 group106,
 group107,
 group111,
 group114,
 group112,
 group113,
 group115,
 group116,
 group117,
 group118,
 group119,
 group109]
mainGroupsStore = AchievementGroupStore(_achievementGroups3)

def GetAchievementGroups():
    return mainGroupsStore.GetAchievementGroups()


def GetTaskIds():
    return mainGroupsStore.GetTaskIds()


def GetFirstIncompleteAchievementGroup():
    alreadyActivated = settings.char.ui.Get('opportunities_aura_activated', [])
    return mainGroupsStore.GetFirstIncompleteAchievementGroup(alreadyActivated)


def GroupTriggeredByTask(task):
    alreadyActivated = settings.char.ui.Get('opportunities_aura_activated', [])
    for each in GetAchievementGroups():
        if each.triggeredBy == task and each.groupID not in alreadyActivated and not each.IsCompleted():
            return each


def GetAchievementGroup(groupID):
    return mainGroupsStore.GetAchievementGroup(groupID=groupID)


def GetGroupForAchievement(achievementID):
    return mainGroupsStore.GetGroupForAchievement(achievementID)


def GetActiveAchievementGroup():
    activeGroupID = sm.GetService('achievementSvc').GetActiveAchievementGroupID()
    return GetAchievementGroup(activeGroupID)
