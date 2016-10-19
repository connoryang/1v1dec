#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\logcontrol\logcontrolsvc.py
import blue
import service
import log

class LogControlSvc(service.Service):
    __guid__ = 'svc.LogControl'
    __notifyevents__ = ['OnSessionChanged']

    def OnSessionChanged(self, isRemote, sess, change):
        if 'role' not in change:
            return
        if session and session.role & service.ROLEMASK_ELEVATEDPLAYER == 0:
            log.LogInfo('Insufficient karma, proceeding quietly...')
            blue.LogControl.LogtypeInfoIsPrivilegedOnly = True
        else:
            blue.LogControl.LogtypeInfoIsPrivilegedOnly = False
