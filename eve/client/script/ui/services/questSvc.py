#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\services\questSvc.py
from __builtin__ import sm
from carbon.common.script.sys import service
from eve.common.script.util import notificationconst
import gametime
from notifications.common.notification import Notification
import localization
QUEST_KILL_WANTED_NPC = 1

class QuestSvc(service.Service):
    __guid__ = 'svc.quest'
    __servicename__ = 'quest'
    __displayname__ = 'Quest Service'
    __notifyevents__ = ['OnQuestCompleted']

    def Run(self, ms):
        service.Service.Run(self, ms)
        self.quests = None

    def IsFeatureActive(self):
        globalConfig = sm.GetService('machoNet').GetGlobalConfig()
        return not bool(globalConfig.get('disableDailyOpportunities', False))

    def GetQuests(self):
        self._PrimeQuests()
        return [ Quest(qid, timestamp) for qid, timestamp in self.quests.iteritems() ]

    def OnQuestCompleted(self, questID, timestamp):
        self._PrimeQuests()
        self.quests[questID] = timestamp
        quest = Quest(questID, timestamp)
        sm.ScatterEvent('OnQuestCompletedClient', quest)
        notification = QuestCompleteNotification(quest)
        sm.ScatterEvent('OnNewNotificationReceived', notification)

    def _PrimeQuests(self):
        if self.quests is None:
            self.quests = sm.RemoteSvc('questMgr').GetMyQuests()


QUEST_ID_TO_TITLE = {QUEST_KILL_WANTED_NPC: 'UI/Quest/TitleKillNpc'}
QUEST_ID_TO_DESCRIPTION = {QUEST_KILL_WANTED_NPC: 'UI/Quest/DescriptionKillNpc'}
QUEST_ID_TO_REWARD = {QUEST_KILL_WANTED_NPC: 'UI/Quest/RewardKillNpc'}

class Quest(object):

    def __init__(self, questID, timestamp):
        self.id = questID
        self._timestamp = timestamp

    @property
    def isComplete(self):
        return gametime.GetWallclockTime() < self._timestamp

    @property
    def titleLabel(self):
        return localization.GetByLabel(QUEST_ID_TO_TITLE[self.id])

    @property
    def descriptionLabel(self):
        return localization.GetByLabel(QUEST_ID_TO_DESCRIPTION[self.id])

    @property
    def rewardLabel(self):
        return localization.GetByLabel(QUEST_ID_TO_REWARD[self.id])

    @property
    def nextAvailableLabel(self):
        timeLeft = self._timestamp - gametime.GetWallclockTime()
        return localization.GetByLabel('UI/Quest/TimeUntilAvailable', time=timeLeft)

    @property
    def nextAvailableShortLabel(self):
        timeLeft = self._timestamp - gametime.GetWallclockTime()
        return localization.GetByLabel('UI/Quest/TimeUntilAvailableShort', time=timeLeft)


class QuestCompleteNotification(Notification):

    def __init__(self, quest):
        super(QuestCompleteNotification, self).__init__(notificationID=-1, typeID=notificationconst.notificationTypeQuestComplete, senderID=None, receiverID=None, processed=False, created=gametime.GetWallclockTime(), data=None)
        self.subject = localization.GetByLabel('UI/Quest/QuestCompleteNotificationSubject', title=quest.titleLabel, reward=quest.rewardLabel)

    def Activate(self):
        pass
