#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\notifications\common\formatters\opportunity.py
from achievements.common.achievementGroups import GetAchievementGroup
from achievements.common.opportunityTaskMap import GROUP_TO_REWARD
import gatekeeper
from localization import GetByLabel
from notifications.common.formatters.baseFormatter import BaseNotificationFormatter

class AchievementOpportunityFormatter(BaseNotificationFormatter):

    @staticmethod
    def MakeData(groupID):
        return {'groupID': groupID}

    def Format(self, notification):
        import eve.common.script.util.eveFormat as eveFormat
        data = notification.data
        groupID = data['groupID']
        group = GetAchievementGroup(groupID)
        notificationPath = group.notificationPath
        subject = GetByLabel(notificationPath)
        notification.subject = subject
        iskReward = GROUP_TO_REWARD[groupID]
        iskText = eveFormat.FmtISK(iskReward, showFractionsAlways=False)
        contextText = GetByLabel('UI/Generic/FormatReference/opportunityRewardName')
        notification.subtext = '<color=0xFF20D603>%s %s</color>' % (iskText, contextText)

    def MakeSampleData(self):
        from utillib import KeyVal
        msg = KeyVal({'groupID': 10})
        return AchievementOpportunityFormatter.MakeData(msg)
