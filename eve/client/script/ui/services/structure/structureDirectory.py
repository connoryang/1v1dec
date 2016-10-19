#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\services\structure\structureDirectory.py
import service
import util
import expiringdict
REMOTESVC = 'structureDirectory'

class StructureDirectory(service.Service):
    __guid__ = 'svc.structureDirectory'
    __notifyevents__ = ['OnCorporationStructuresUpdated', 'OnSessionChanged']
    __dependencies__ = ['objectCaching']

    def Run(self, memStream = None):
        self.knownStructures = expiringdict.ExpiringDict(1000, 3600)

    def GetStructureInfo(self, structureID):
        if not util.IsPlayerItem(structureID):
            return None
        if structureID not in self.knownStructures:
            self.knownStructures[structureID] = sm.RemoteSvc(REMOTESVC).GetStructureInfo(structureID)
        return self.knownStructures[structureID]

    def GetStructures(self):
        return sm.RemoteSvc(REMOTESVC).GetMyCharacterStructures(session.regionid)

    def GetCorporationStructures(self):
        return sm.RemoteSvc(REMOTESVC).GetMyCorporationStructures(session.corpid)

    def GetStructuresInSystem(self):
        if session.solarsystemid2:
            return sm.RemoteSvc(REMOTESVC).GetMyDockableStructures(session.solarsystemid2)
        return set()

    def GetStructureMapData(self, solarsystemID):
        return sm.RemoteSvc(REMOTESVC).GetStructureMapData(solarsystemID)

    def CanContractFrom(self, structureID):
        return self.GetStructureInfo(structureID) is not None

    def OnCorporationStructuresUpdated(self):
        self.objectCaching.InvalidateCachedMethodCall('structureDirectory', 'GetMyCorporationStructures', session.corpid)
        sm.ScatterEvent('OnCorporationStructuresReloaded')

    def Reload(self):
        self.objectCaching.InvalidateCachedMethodCall('structureDirectory', 'GetMyDockableStructures', session.solarsystemid2)
        self.objectCaching.InvalidateCachedMethodCall('structureDirectory', 'GetMyCharacterStructures', session.regionid)
        self.objectCaching.InvalidateCachedMethodCall('structureDirectory', 'GetMyCorporationStructures', session.corpid)
        sm.ScatterEvent('OnStructuresReloaded')

    def OnSessionChanged(self, isRemote, sess, change):
        if 'solarsystemid2' in change:
            sm.ScatterEvent('OnStructuresReloaded')
