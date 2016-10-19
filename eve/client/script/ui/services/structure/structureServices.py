#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\services\structure\structureServices.py
import service
import structures
from eve.client.script.ui.station import stationServiceConst

class StructureServices(service.Service):
    __guid__ = 'svc.structureServices'
    __notifyevents__ = ['OnSessionChanged', 'OnStructureServiceChanged']

    def Run(self, *args):
        self.onlineServices = None
        self.structureID = None

    def OnSessionChanged(self, isRemote, session, change):
        if 'structureid' in change and session.structureid:
            self._FetchOnlineServices()

    def GetCurrentStructureServices(self):
        return structures.SERVICES_ACCESS_SETTINGS.keys()

    def IsServiceAvailable(self, serviceID):
        if serviceID in structures.ONLINE_SERVICES:
            return True
        if serviceID == stationServiceConst.serviceIDAlwaysPresent:
            return True
        if self.onlineServices is None or self.structureID != session.structureid:
            self._FetchOnlineServices()
        return serviceID in self.onlineServices

    def OnStructureServiceChanged(self, structureID):
        if structureID == session.structureid:
            self._FetchOnlineServices()
        sm.ScatterEvent('OnStructureServiceUpdated')

    def _FetchOnlineServices(self):
        if session.structureid is not None:
            self.onlineServices = sm.RemoteSvc('structureSettings').CharacterGetServices(session.structureid)
        self.structureID = session.structureid
