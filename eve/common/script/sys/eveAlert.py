#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\common\script\sys\eveAlert.py
import svc

class Alert(svc.alert):
    __guid__ = 'svc.eveAlert'
    __replaceservice__ = 'alert'

    def _GetSessionInfo(self):
        if session:
            return (session.userid,
             session.charid,
             session.solarsystemid2,
             session.stationid)
        return (None, None, None, None)
