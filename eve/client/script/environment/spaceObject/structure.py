#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\environment\spaceObject\structure.py
import blue
import uthread
import structures
import evetypes
import logging
from eve.client.script.environment.spaceObject.buildableStructure import BuildableStructure
from eve.client.script.environment.model.turretSet import TurretSet
from evegraphics.explosions.spaceObjectExplosionManager import SpaceObjectExplosionManager
STATE_CONSTRUCT = 'construct'
STATE_VULNERABLE = 'vulnerable'
STATE_INVULNERABLE = 'invulnerable'
STATE_SIEGED = 'sieged'
STATE_DECONSTRUCT = 'deconstruct'
STATES = {structures.STATE_UNKNOWN: STATE_INVULNERABLE,
 structures.STATE_UNANCHORED: STATE_DECONSTRUCT,
 structures.STATE_ANCHORING: STATE_CONSTRUCT,
 structures.STATE_ONLINE: STATE_INVULNERABLE,
 structures.STATE_SHIELD_VULNERABLE: STATE_VULNERABLE,
 structures.STATE_SHIELD_REINFORCE: STATE_SIEGED,
 structures.STATE_ARMOR_VULNERABLE: STATE_VULNERABLE,
 structures.STATE_ARMOR_REINFORCE: STATE_SIEGED,
 structures.STATE_HULL_VULNERABLE: STATE_VULNERABLE}

class Structure(BuildableStructure):
    __unloadable__ = True

    def __init__(self):
        BuildableStructure.__init__(self)
        self.Init()

    def Release(self):
        BuildableStructure.Release(self)
        self.Init()

    def Init(self):
        self.fitted = False
        self.state = None
        self.timer = None
        self.turrets = []
        self.modules = {}

    def Assemble(self):
        self.SetStaticRotation()
        self.SetupSharedAmbientAudio()
        self.OnSlimItemUpdated(self.typeData.get('slimItem'))

    def OnSlimItemUpdated(self, item):
        if item is None or self.unloaded:
            return
        if item.state and (item.state != self.state or item.timer != self.timer):
            if item.timer and item.state == structures.STATE_ANCHORING:
                start, end, paused = item.timer
                duration = (end - start) / const.SEC
                elapsed = duration - max(end - blue.os.GetWallclockTime(), 0L) / const.SEC
            else:
                duration = 0
                elapsed = 0
            self.state = item.state
            self.timer = item.timer
            self.GotoState(STATES[self.state], duration, elapsed)
        if set([ i[0] for i in item.modules or [] if evetypes.GetGraphicID(i[1]) is not None ]) != set(self.modules.keys()):
            uthread.new(self.ReloadHardpoints)

    def OnDamageState(self, damageState):
        BuildableStructure.OnDamageState(self, damageState)
        if self.model is not None and damageState is not None:
            states = [ (d if d is not None else 0.0) for d in damageState ]
            self.model.SetImpactDamageState(states[0], states[1], states[2], False)

    def GotoState(self, state, totalTime = 0, elapsedTime = 0):
        if state == STATE_CONSTRUCT:
            uthread.new(self.BuildStructure, float(totalTime), float(elapsedTime))
        elif state == STATE_DECONSTRUCT:
            uthread.new(self.TearDownStructure, float(totalTime), float(elapsedTime))
        else:
            uthread.new(self.LoadModelWithState, state)

    def LoadModelWithState(self, newState):
        if self.model is None:
            self.LoadModel()
        self.TriggerAnimation(newState)
        self.FitHardpoints()
        self.StartStructureLoopAnimation()

    def LoadModel(self, fileName = None, loadedModel = None):
        self.model = self.GetStructureModel()
        self.SetAnimationSequencer(self.model)
        self.NotifyModelLoaded()

    def ReloadHardpoints(self):
        self.UnfitHardpoints()
        self.FitHardpoints()

    def UnfitHardpoints(self):
        if not self.fitted:
            return
        self.logger.debug('Unfitting hardpoints')
        newModules = {}
        for key, val in self.modules.iteritems():
            if val not in self.turrets:
                newModules[key] = val

        self.modules = newModules
        del self.turrets[:]
        self.fitted = False

    def FitHardpoints(self, blocking = False):
        if self.fitted:
            return
        if self.model is None:
            self.logger.warning('FitHardpoints - No model')
            return
        self.logger.debug('Fitting hardpoints')
        self.fitted = True
        newTurretSetDict = TurretSet.FitTurrets(self.id, self.model, self.typeData.get('sofFactionName', None))
        self.turrets = []
        for key, val in newTurretSetDict.iteritems():
            self.modules[key] = val
            self.turrets.append(val)

    def LookAtMe(self):
        if not self.model:
            return
        if not self.fitted:
            self.FitHardpoints()

    def StopStructureLoopAnimation(self):
        animationUpdater = self.GetStructureModel().animationUpdater
        if animationUpdater is not None:
            animationUpdater.PlayLayerAnimation('TrackMaskLayer1', 'Layer1Loop', False, 1, 0, 1, True)

    def StartStructureLoopAnimation(self):
        animationUpdater = self.GetStructureModel().animationUpdater
        if animationUpdater is not None:
            animationUpdater.PlayLayerAnimation('TrackMaskLayer1', 'Layer1Loop', False, 0, 0, 1, True)

    def BuildStructure(self, anchoringTime, elapsedTime):
        self.LoadUnLoadedModels()
        self.logger.debug('Structure: BuildStructure %s', self.GetTypeID())
        self.PreBuildingSteps()
        delay = int((anchoringTime - elapsedTime) * 1000)
        uthread.new(self._EndStructureBuild, delay)
        self.TriggerAnimation(STATE_CONSTRUCT, curveLength=anchoringTime, elapsedTime=elapsedTime)

    def _EndStructureBuild(self, delay):
        blue.pyos.synchro.SleepSim(delay)
        if self.released or self.exploded:
            return
        self.StartStructureLoopAnimation()
        self.PostBuildingSteps(True)
        self.LoadModel()

    def TearDownStructure(self, unanchoringTime, elapsedTime):
        self.LoadUnLoadedModels()
        self.logger.debug('Structure: TearDownStructure %s', self.GetTypeID())
        self.StopStructureLoopAnimation()
        self.PreBuildingSteps()
        delay = int((unanchoringTime - elapsedTime) * 1000)
        uthread.new(self._EndStructureTearDown, delay)
        self.TriggerAnimation(STATE_DECONSTRUCT, curveLength=unanchoringTime, elapsedTime=elapsedTime)

    def _EndStructureTearDown(self, delay):
        blue.pyos.synchro.SleepSim(delay)
        if self.released or self.exploded:
            return
        self.PostBuildingSteps(False)
        self.model = self.GetNanoContainerModel()

    def Explode(self, explosionURL = None, scaling = 1.0, managed = False, delay = 0.0):
        if SpaceObjectExplosionManager.USE_EXPLOSION_BUCKETS:
            self.logger.debug('Exploding with explosion bucket')
            scene = sm.GetService('space').GetScene()
            wreckSwitchTime, _, __ = SpaceObjectExplosionManager.ExplodeBucketForBall(self, scene)
            return wreckSwitchTime
        explosionURL, (delay, _) = self.GetExplosionInfo()
        explosionLocatorSets = None
        if hasattr(self.model, 'locatorSets'):
            explosionLocatorSets = self.model.locatorSets.FindByName('explosions')
        rotation = self.GetStaticRotation()
        self.explosionManager.PlayClientSideExplosionBall(explosionURL, (self.x, self.y, self.z), rotation, explosionLocatorSets)
        return delay
