#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\environment\t3shipSvc.py
import evetypes
import inventorycommon.typeHelpers
import uthread
import service
import blue
import os
import trinity
import const
import random
from eve.client.script.ui.station.assembleModularShip import AssembleShip
MAX_WAIT_FOR_OTHER_PROCESS = 60000

class EveShip2BuildEvent:

    def __init__(self):
        self.isDone = False
        self.succeeded = False

    def __call__(self, success):
        self.isDone = True
        self.succeeded = success

    def Wait(self):
        while not self.isDone:
            blue.pyos.synchro.Yield()


class t3ShipSvc(service.Service):
    __guid__ = 'svc.t3ShipSvc'
    __displayname__ = 'Tech 3 Ship Builder'
    __exportedcalls__ = {'GetTech3ShipFromDict': [],
     'GetRandomSubsystems': []}

    def __init__(self):
        service.Service.__init__(self)
        self.buildsInProgress = {}
        self.impactEffectResPaths = {'amarr': 'res:/fisfx/impact/impact_amarr_01a.red',
         'caldari': 'res:/fisfx/impact/impact_caldari_01a.red',
         'gallente': 'res:/fisfx/impact/impact_gallente_01a.red',
         'minmatar': 'res:/fisfx/impact/impact_minmatar_01a.red'}

    def Run(self, ms = None):
        self.state = service.SERVICE_RUNNING

    def GetTech3ShipFromDict(self, shipTypeID, subSystems, race = None):
        shipsDir = blue.paths.ResolvePathForWriting('cache:/ships/')
        if not os.path.exists(shipsDir):
            os.makedirs(shipsDir)
        t = subSystems.values()
        t.sort()
        uniqueComboID = '_'.join([ str(id) for id in t ])
        cacheVersion = 'v7'
        blackFileCachePath = 'cache:/ships/%s_%s_%s.black' % (cacheVersion, shipTypeID, uniqueComboID)
        gr2FileCachePath = 'cache:/ships/%s_%s_%s.gr2' % (cacheVersion, shipTypeID, uniqueComboID)
        lockFileCachePath = 'cache:/ships/%s_%s_%s.lock' % (cacheVersion, shipTypeID, uniqueComboID)
        blackFilePath = blue.paths.ResolvePathForWriting(blackFileCachePath)
        gr2FilePath = blue.paths.ResolvePathForWriting(gr2FileCachePath)
        lockFilePath = blue.paths.ResolvePathForWriting(lockFileCachePath)
        model = None
        if os.path.exists(blackFilePath) and os.path.exists(gr2FilePath):
            self.LogInfo('Loading existing modular ship from', blackFileCachePath)
            model = trinity.LoadUrgent(blackFileCachePath)
            trinity.WaitForUrgentResourceLoads()
            if model is None:
                self.LogInfo('Failed to load - black file may no longer be compatible - deleting', blackFileCachePath)
                try:
                    os.remove(blackFilePath)
                    os.remove(gr2FilePath)
                    blue.resMan.loadObjectCache.Delete(blackFileCachePath)
                except OSError:
                    self.LogError("Couldn't delete", blackFileCachePath)

        if model is None:
            if blackFileCachePath in self.buildsInProgress:
                self.LogInfo('Build in progress for modular ship at', blackFileCachePath)
                doneChannel = self.buildsInProgress[blackFileCachePath]
                success = doneChannel.receive()
                self.LogInfo('Done waiting for modular ship at', blackFileCachePath)
            else:
                keepTrying = True
                while keepTrying:
                    try:
                        self.LogInfo('Checking for lock file', lockFilePath)
                        lockFile = os.mkdir(lockFilePath)
                        try:
                            self.LogInfo('Starting to build modular ship at', blackFileCachePath)
                            doneChannel = uthread.Channel()
                            self.buildsInProgress[blackFileCachePath] = doneChannel
                            builder = trinity.EveShip2Builder()
                            builder.weldThreshold = 0.02
                            builder.electronic = inventorycommon.typeHelpers.GetGraphicFile(subSystems[const.groupElectronicSubSystems])
                            builder.defensive = inventorycommon.typeHelpers.GetGraphicFile(subSystems[const.groupDefensiveSubSystems])
                            builder.engineering = inventorycommon.typeHelpers.GetGraphicFile(subSystems[const.groupEngineeringSubSystems])
                            builder.offensive = inventorycommon.typeHelpers.GetGraphicFile(subSystems[const.groupOffensiveSubSystems])
                            builder.propulsion = inventorycommon.typeHelpers.GetGraphicFile(subSystems[const.groupPropulsionSubSystems])
                            builder.highDetailOutputName = gr2FileCachePath
                            uthread.new(self.BuildShip, builder, blackFilePath, doneChannel)
                            success = doneChannel.receive()
                            self.LogInfo('Done building modular ship at', blackFileCachePath)
                        finally:
                            keepTrying = False
                            os.rmdir(lockFilePath)

                    except WindowsError:
                        self.LogInfo('Build in progress by another process for modular ship at', blackFileCachePath)
                        doneChannel = uthread.Channel()
                        self.buildsInProgress[blackFileCachePath] = doneChannel
                        start = blue.os.GetWallclockTime()
                        while os.path.exists(lockFilePath):
                            blue.synchro.Yield()
                            timeOut = blue.os.TimeDiffInMs(start, blue.os.GetWallclockTime())
                            if timeOut > MAX_WAIT_FOR_OTHER_PROCESS:
                                self.LogInfo('Build by another process seems to have failed for modular ship at', blackFileCachePath)
                                try:
                                    os.rmdir(lockFilePath)
                                except WindowsError:
                                    self.LogError("Can't delete lock file for modular ship at", blackFileCachePath)
                                    keepTrying = False

                                break

                        if os.path.exists(blackFilePath) and os.path.exists(gr2FilePath):
                            self.LogInfo('Other process finished building modular ship at', blackFileCachePath)
                            keepTrying = False
                            success = True
                        else:
                            success = False

                del self.buildsInProgress[blackFileCachePath]
            if not success:
                return
        if model is None:
            model = trinity.LoadUrgent(blackFileCachePath)
            trinity.WaitForUrgentResourceLoads()
        if model is not None and race is not None:
            impactEffectResPath = self.impactEffectResPaths.get(race, None)
            if impactEffectResPath is not None:
                model.impactOverlay = trinity.Load(impactEffectResPath)
        return model

    def GetRandomSubsystems(self, typeID):

        def CheckSubsystemValid(subsystemTypeID):
            fitsToType = sm.GetService('godma').GetTypeAttribute(subsystemTypeID, const.attributeFitsToShipType)
            return evetypes.IsPublished(typeID) and fitsToType == typeID

        subsystems = {}
        subsystemGroups = evetypes.GetGroupIDsByCategory(const.categorySubSystem)
        for groupID in subsystemGroups:
            subsystemsInGroup = evetypes.GetTypeIDsByGroup(groupID)
            validSubsystems = filter(CheckSubsystemValid, subsystemsInGroup)
            subsystems[groupID] = random.choice(validSubsystems)

        return subsystems

    def GetTech3ShipRandomSubsystems(self, typeID):
        subsystems = self.GetRandomSubsystems(typeID)
        return self.GetTech3ShipFromDict(typeID, subsystems)

    def SaveModelToCache(self, model, filePath):
        shipsDir = blue.paths.ResolvePathForWriting('cache:/ships/')
        if not os.path.exists(shipsDir):
            os.makedirs(shipsDir)
        s = os.path.splitext(filePath)
        tmpFilePath = s[0] + '.tmp%d' % blue.os.pid + s[1]
        blue.resMan.SaveObject(model, tmpFilePath)
        os.rename(tmpFilePath, filePath)

    def BuildShip(self, builder, path, doneChannel):
        shipsDir = blue.paths.ResolvePathForWriting('cache:/ships/')
        if not os.path.exists(shipsDir):
            os.makedirs(shipsDir)
        if builder.PrepareForBuild():
            trinity.WaitForResourceLoads()
            evt = EveShip2BuildEvent()
            builder.BuildAsync(evt)
            evt.Wait()
            if evt.succeeded:
                self.LogInfo('Modular model built successfully:', path)
                ship = builder.GetShip()
                ship.shadowEffect = trinity.Tr2Effect()
                ship.shadowEffect.effectFilePath = 'res:/graphics/effect/managed/space/spaceobject/shadow/shadow.fx'
                self.SaveModelToCache(ship, path)
                while doneChannel.balance < 0:
                    doneChannel.send(True)

                return
            self.LogError('Failed building ship:', path)
        while doneChannel.balance < 0:
            doneChannel.send(False)

    def MakeModularShipFromShipItem(self, ship, isSimulated = False):
        subSystemIds = {}
        for fittedItem in ship.GetFittedItems().itervalues():
            if fittedItem.categoryID == const.categorySubSystem:
                subSystemIds[fittedItem.groupID] = fittedItem.typeID

        if len(subSystemIds) < const.visibleSubSystems and session.solarsystemid is None and not isSimulated:
            windowID = 'assembleWindow_modular'
            AssembleShip.CloseIfOpen(windowID=windowID)
            AssembleShip.Open(windowID=windowID, ship=ship, groupIDs=subSystemIds.keys())
            return
        if len(subSystemIds) < const.visibleSubSystems:
            raise NotEnoughSubSystems('MakeModularShipFromShipItem - not enough subsystems')
        return self.GetTech3ShipFromDict(ship.typeID, subSystemIds)


class NotEnoughSubSystems(RuntimeError):
    pass
