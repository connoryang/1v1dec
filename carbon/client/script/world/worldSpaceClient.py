#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\carbon\client\script\world\worldSpaceClient.py
import collections
import stackless
import uthread
from eve.common.script.world.eveBaseWorldSpaceSvc import BaseWorldSpaceService
from carbon.common.script.world.worldSpaceCommon import GetWorldSpace
from eve.client.script.world.eveWorldSpaceScene import EveWorldSpaceScene as WorldSpaceScene

class WorldSpaceClient(BaseWorldSpaceService):
    __guid__ = 'svc.worldSpaceClient'

    def __init__(self):
        BaseWorldSpaceService.__init__(self)
        self.activeWorldSpace = None
        self.showLoadingWindow = False
        self.instanceLoadedChannel = collections.defaultdict(list)

    def GetCurrentDistrict(self):
        if session.worldspaceid is None:
            return
        worldSpaceTypeID = self.GetWorldSpaceTypeIDFromWorldSpaceID(session.worldspaceid)
        if worldSpaceTypeID is None:
            return
        ws = GetWorldSpace(worldSpaceTypeID)
        return ws.GetDistrictID()

    def UnloadWorldSpaceInstance(self, instanceID):
        if self.IsInstanceLoaded(instanceID):
            uthread.Lock(self, 'Worldspace', instanceID)
            try:
                if self.IsInstanceLoaded(instanceID) and (session.worldspaceid is None or session.worldspaceid and session.worldspaceid != instanceID):
                    self.LogInfo('Unloading worldspace instance', instanceID)
                    instance = self.instances[instanceID]
                    proximity = sm.GetService('proximity')
                    proximity.UnloadInstance(instance)
                    sm.ChainEvent('ProcessWorldSpaceUnloading', instanceID)
                    BaseWorldSpaceService.UnloadWorldSpaceInstance(self, instanceID)
                    sm.ScatterEvent('OnWorldSpaceUnloaded', instanceID)
            finally:
                self.LogInfo('Unloaded worldspace instance', instanceID)
                uthread.UnLock(self, 'Worldspace', instanceID)

    def _LoadWorldSpaceFromServer(self, instanceID, worldSpaceID):
        self.LogInfo('Creating worldSpace layout', worldSpaceID, 'for instance', instanceID)
        newWorldSpace = WorldSpaceScene(worldSpaceID, instanceID)
        newWorldSpace.LoadProperties()
        self._FinishLoadingInstance(newWorldSpace)
        return newWorldSpace

    def LoadWorldSpaceInstance(self, instanceID, worldSpaceTypeID = None):
        uthread.Lock(self, 'Worldspace', instanceID)
        try:
            self.LogInfo('Loading WorldSpaceInstance')
            if instanceID not in self.instances:
                if worldSpaceTypeID is None:
                    worldSpaceTypeID = self.GetWorldSpaceTypeIDFromWorldSpaceID(instanceID)
                newWorldSpace = self._LoadWorldSpaceFromServer(instanceID, worldSpaceTypeID)
        finally:
            self.LogInfo('Done loading WorldSpaceInstance')
            uthread.UnLock(self, 'Worldspace', instanceID)

    def _FinishLoadingInstance(self, instance):
        worldSpaceID = instance.GetWorldSpaceID()
        worldSpaceTypeID = instance.GetWorldSpaceTypeID()
        self.instances[worldSpaceID] = instance
        self.worldSpaceLookup[worldSpaceTypeID].append(worldSpaceID)
        for each in self.instanceLoadedChannel[worldSpaceID]:
            while each.balance < 0:
                each.send(None)

        del self.instanceLoadedChannel[worldSpaceID]
        self.LogInfo('Loaded worldspace from server: worldSpaceID', worldSpaceID, 'worldSpaceTypeID', worldSpaceTypeID)
        sm.ScatterEvent('OnWorldSpaceLoaded', worldSpaceTypeID, worldSpaceID)

    def WaitForInstance(self, instanceID):
        if not self.IsInstanceLoaded(instanceID):
            self.instanceLoadedChannel[instanceID].append(stackless.channel())
            self.instanceLoadedChannel[instanceID][-1].receive()

    def UnloadInstances(self, unloadInstanceIDs):
        realInstanceIDList = []
        for instanceID in unloadInstanceIDs:
            realInstanceIDList.append(instanceID)

        for instanceID in realInstanceIDList:
            uthread.new(self.UnloadWorldSpaceInstance, instanceID).context = 'worldSpaceClient::UnloadWorldSpaceInstance'
