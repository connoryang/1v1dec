#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\notifications\common\formatters\seasons.py
from notifications.common.formatters.baseFormatter import BaseNotificationFormatter
from localization import GetByLabel

class SeasonalChallengeCompletedFormatter(BaseNotificationFormatter):

    def __init__(self):
        BaseNotificationFormatter.__init__(self, subjectLabel='Notifications/SeasonalChallengeCompletedSubject', subtextLabel='Notifications/SeasonalChallengeCompletedSubtext')

    def Format(self, notification):
        data = notification.data
        points_awarded = data.get('points_awarded')
        notification.subject = GetByLabel(self.subjectLabel, points_awarded=points_awarded)
        notification.subtext = GetByLabel(self.subtextLabel)
