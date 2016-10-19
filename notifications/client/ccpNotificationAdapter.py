#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\notifications\client\ccpNotificationAdapter.py
from notifications.common.notification import Notification
import blue

class CCPNotificationAdapter(object):
    __notifyevents__ = ['OnCCPNotification']

    def OnCCPNotification(self, title, subtitle, text, notificationTypeID, language = None):
        if language is None or language == session.languageID:
            notification = Notification(notificationID=1, typeID=notificationTypeID, senderID=None, receiverID=session.charid, processed=0, created=blue.os.GetWallclockTime(), data={'text': text})
            notification.subject = title
            notification.subtext = subtitle
            sm.ScatterEvent('OnNewNotificationReceived', notification)
