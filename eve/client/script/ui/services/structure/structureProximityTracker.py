#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\services\structure\structureProximityTracker.py
from carbon.common.script.util.timerstuff import AutoTimer
from collections import defaultdict
from eve.client.script.ui.services.structure.error import InvalidStateOfRegistry
import service
import telemetry
import uthread
from util import IsStation
UPDATE_STRUCTURE_VISIBILITY_TIMEOUT = 2000

class StructureProximityTracker(service.Service):
    __guid__ = 'svc.structureProximityTracker'
    __notifyevents__ = ['OnBallAdded',
     'DoBallRemove',
     'DoBallsRemove',
     'OnSessionChanged',
     'OnStructuresReloaded']
    __dependencies__ = ['michelle', 'structureDirectory']

    def Run(self, *args):
        self.structureVisibilityRegistry = defaultdict(bool)
        self.dockableStructuresInSystem = defaultdict(bool)
        self._TriggerStructureVisibilityUpdates()

    def IsStructureDockable(self, structureID):
        return self.dockableStructuresInSystem[structureID]

    def IsStructureInRange(self, structureID):
        return self.michelle.IsBallVisible(structureID)

    def IsStructureVisible(self, structureID):
        return self.IsStructureDockable(structureID) or self.IsStructureInRange(structureID)

    def _SetStructureVisibility(self, structureID, isVisible):
        self.structureVisibilityRegistry[structureID] = isVisible
        sm.ScatterEvent('OnStructureVisibilityUpdated', structureID)

    def _ClearVisibilityRegistry(self):
        for structureID in self.structureVisibilityRegistry:
            self._SetStructureVisibility(structureID, False)

        self.structureVisibilityRegistry.clear()
        sm.ScatterEvent('OnStructuresVisibilityUpdated')

    def _ResetVisibility(self):
        for structureID in self.structureVisibilityRegistry:
            self._SetStructureVisibility(structureID, False)

        sm.ScatterEvent('OnStructuresVisibilityUpdated')

    @telemetry.ZONE_METHOD
    def _RefreshDockability(self):
        self.dockableStructuresInSystem.clear()
        hasVisibilityChangedForAnyStructure = False
        newDockableStructures = self._GetDockableStructures()
        for structureID in self.structureVisibilityRegistry:
            isStructureInRange = self.IsStructureInRange(structureID)
            wasStructureDockable = self.IsStructureDockable(structureID)
            isStructureDockable = structureID in newDockableStructures
            self.dockableStructuresInSystem[structureID] = isStructureDockable
            hasVisibilityChanged = not isStructureInRange and wasStructureDockable != isStructureDockable
            if hasVisibilityChanged:
                hasVisibilityChangedForAnyStructure = True
                self._SetStructureVisibility(structureID, isStructureDockable)

        for structureID in newDockableStructures:
            self.dockableStructuresInSystem[structureID] = True

        if hasVisibilityChangedForAnyStructure:
            sm.ScatterEvent('OnStructuresVisibilityUpdated')

    @telemetry.ZONE_METHOD
    def _GetDockableStructures(self):
        dockableStructures = []
        allDockableStructuresInSolarSystem = self.structureDirectory.GetStructuresInSystem()
        for structureID in allDockableStructuresInSolarSystem:
            shouldTrackStructure = not IsStation(structureID)
            if shouldTrackStructure:
                dockableStructures.append(structureID)

        return dockableStructures

    def _TriggerStructureVisibilityUpdates(self):
        setattr(self, 'updateStructureVisibilityTimerThread', AutoTimer(UPDATE_STRUCTURE_VISIBILITY_TIMEOUT, self._UpdateStructureVisibility))

    @telemetry.ZONE_METHOD
    def _UpdateStructureVisibility(self):
        hasVisibilityChangedForAnyStructure = False
        for structureID, wasVisible in self.structureVisibilityRegistry.iteritems():
            isVisible = self.IsStructureVisible(structureID)
            if wasVisible != isVisible:
                hasVisibilityChangedForAnyStructure = True
                self._SetStructureVisibility(structureID, isVisible)

        if hasVisibilityChangedForAnyStructure:
            sm.ScatterEvent('OnStructuresVisibilityUpdated')

    def _CallFunctionWithStructureVisibilityUpdatesPaused(self, functionToCall, *args):
        self.updateStructureVisibilityTimerThread = None
        try:
            functionToCall(*args)
            self._TriggerStructureVisibilityUpdates()
        except InvalidStateOfRegistry:
            pass

    def OnSessionChanged(self, isRemote, session, change):
        hasSolarSystemChanged = 'solarsystemid' in change
        hasStructureIdChanged = 'structureid' in change
        if hasSolarSystemChanged:
            self._CallFunctionWithStructureVisibilityUpdatesPaused(self._ClearVisibilityRegistry)
        elif hasStructureIdChanged:
            self._CallFunctionWithStructureVisibilityUpdatesPaused(self._ResetVisibility)

    def OnStructuresReloaded(self):
        self._CallFunctionWithStructureVisibilityUpdatesPaused(self._RefreshDockability)

    def OnBallAdded(self, slimItem):
        if slimItem.categoryID == const.categoryStructure:
            structureToAdd = slimItem.itemID
            self._CallFunctionWithStructureVisibilityUpdatesPaused(self._AddStructureToRegistry, structureToAdd)

    def DoBallRemove(self, ball, slimItem, terminal):
        if slimItem.categoryID == const.categoryStructure:
            structureToRemove = slimItem.itemID
            self._CallFunctionWithStructureVisibilityUpdatesPaused(self._RemoveStructureFromRegistry, structureToRemove)

    def DoBallsRemove(self, pythonBalls, isRelease):
        structuresToRemove = []
        for _ball, slimItem, _terminal in pythonBalls:
            if slimItem.categoryID == const.categoryStructure:
                structuresToRemove.append(slimItem.itemID)

        if structuresToRemove:
            self._CallFunctionWithStructureVisibilityUpdatesPaused(self._RemoveStructuresFromRegistry, structuresToRemove)

    def _AddStructureToRegistry(self, structureToAdd):
        if structureToAdd in self.structureVisibilityRegistry:
            raise InvalidStateOfRegistry()
        isVisible = self.IsStructureVisible(structureToAdd)
        self.structureVisibilityRegistry[structureToAdd] = self._SetStructureVisibility(structureToAdd, isVisible)
        sm.ScatterEvent('OnStructuresVisibilityUpdated')

    def _RemoveStructureFromRegistry(self, structureToRemove):
        if structureToRemove not in self.structureVisibilityRegistry:
            raise InvalidStateOfRegistry()
        self._SetStructureVisibility(structureToRemove, False)
        del self.structureVisibilityRegistry[structureToRemove]
        sm.ScatterEvent('OnStructuresVisibilityUpdated')

    def _RemoveStructuresFromRegistry(self, structuresToRemove):
        for structureToRemove in structuresToRemove:
            self._RemoveStructureFromRegistry(structureToRemove)
