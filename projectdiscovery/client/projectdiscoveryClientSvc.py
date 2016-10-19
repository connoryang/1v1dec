#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\projectdiscovery\client\projectdiscoveryClientSvc.py
from projectdiscovery.client.const import Events
from service import Service
PROJECT_DISCOVERY_ID = 'ProjectDiscovery'

class ProjectDiscoveryClientService(Service):
    __servicename__ = 'ProjectDiscoveryClient'
    __displayname__ = 'ProjectDiscoveryClient'
    __guid__ = 'svc.ProjectDiscoveryClient'
    __notifyevents__ = ['OnAnalysisKreditsChange']

    def __init__(self, *args, **kwargs):
        Service.__init__(self, *args, **kwargs)

    def Run(self, *args, **kwargs):
        Service.Run(self, *args, **kwargs)

    def OnAnalysisKreditsChange(self):
        sm.ScatterEvent(Events.UpdateAnalysisKredits)
        sm.GetService('neocom').Blink(PROJECT_DISCOVERY_ID)
