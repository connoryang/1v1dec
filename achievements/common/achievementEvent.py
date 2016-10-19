#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\achievements\common\achievementEvent.py
from achievements.common.achievementConst import AchievementEventConst
import eve.common.lib.infoEventConst as infoEventConst
import evetypes

def LogIndustryReprocessCount(eventHandler, eventData):
    eventHandler.LogAchievementEvent(eventData.itemID, AchievementEventConst.INDUSTRY_REPROCESS_COUNT, amount=1)


achievementEventHandlersByLogEventIDs = {infoEventConst.infoEventRefinedTypesAmount: LogIndustryReprocessCount}

def IsEventAnAchievement(logEventID):
    return logEventID in achievementEventHandlersByLogEventIDs


def GetAchievementEventLogHandler(logEventID):
    return achievementEventHandlersByLogEventIDs.get(logEventID)
