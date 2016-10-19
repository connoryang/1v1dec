#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\environment\spaceObject\spaceObject.py
import random
import math
import types
import blue
import geo2
from evegraphics.explosions.spaceObjectExplosionManager import SpaceObjectExplosionManager
from signals.signal import Signal
import trinity
import decometaclass
import carbon.common.script.util.mathCommon as mathCommon
import carbon.client.script.util.timecurves as timecurves
from carbon.common.lib.builtinmangler import strx
import uthread2
import logging
import locks
import evegraphics.utils as gfxutils
import evegraphics.settings as gfxsettings
import eveSpaceObject
import eveSpaceObject.spaceobjaudio as spaceobjaudio
import eveSpaceObject.spaceobjanimation as spaceobjanimation
import eve.common.lib.appConst as const
from eve.client.script.environment.spaceObject.ExplosionManager import ExplosionManager
import evegraphics.fsd.explosionBuckets as fsdExplosionBuckets
BOOSTER_GFX_SND_RESPATHS = {eveSpaceObject.gfxRaceAmarr: ('res:/dx9/model/ship/booster/booster_amarr.red', 'ship_booster_amarr'),
 eveSpaceObject.gfxRaceCaldari: ('res:/dx9/model/ship/booster/booster_caldari.red', 'ship_booster_caldari'),
 eveSpaceObject.gfxRaceGallente: ('res:/dx9/model/ship/booster/booster_gallente.red', 'ship_booster_gallente'),
 eveSpaceObject.gfxRaceMinmatar: ('res:/dx9/model/ship/booster/booster_minmatar.red', 'ship_booster_minmatar'),
 eveSpaceObject.gfxRaceJove: (None, 'ship_booster_jove'),
 eveSpaceObject.gfxRaceAngel: (None, 'ship_booster_angel'),
 eveSpaceObject.gfxRaceSleeper: (None, 'ship_booster_sleeper'),
 eveSpaceObject.gfxRaceORE: (None, 'ship_booster_ORE'),
 eveSpaceObject.gfxRaceConcord: (None, 'ship_booster_concord'),
 eveSpaceObject.gfxRaceRogue: (None, 'ship_booster_roguedrone'),
 eveSpaceObject.gfxRaceSansha: (None, 'ship_booster_sansha'),
 eveSpaceObject.gfxRaceSOCT: (None, 'ship_booster_soct'),
 eveSpaceObject.gfxRaceTalocan: (None, 'ship_booster_talocan'),
 eveSpaceObject.gfxRaceGeneric: (None, 'ship_booster_generic'),
 eveSpaceObject.gfxRaceSoE: (None, 'ship_booster_soe'),
 eveSpaceObject.gfxRaceMordu: (None, 'ship_booster_mordu')}

class SpaceObjectLogAdapter(logging.LoggerAdapter):

    def __init__(self, logger, extra = None, so_id = None):
        self.so_id = so_id
        super(SpaceObjectLogAdapter, self).__init__(logger, extra)

    def add_so_id(self, msg, *args, **kwargs):
        msg, kwargs = self.process(msg, kwargs)
        so_id_arg = [self.so_id]
        if args:
            new_args = list(args)
            new_args = so_id_arg + new_args
        else:
            new_args = so_id_arg
        msg = '[%s] ' + msg
        return (msg, new_args, kwargs)

    def debug(self, msg, *args, **kwargs):
        new_msg, new_args, kwargs = self.add_so_id(msg, *args, **kwargs)
        self.logger.debug(new_msg, *new_args, **kwargs)

    def info(self, msg, *args, **kwargs):
        new_msg, new_args, kwargs = self.add_so_id(msg, *args, **kwargs)
        self.logger.info(new_msg, *new_args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        new_msg, new_args, kwargs = self.add_so_id(msg, *args, **kwargs)
        self.logger.warning(new_msg, *new_args, **kwargs)

    def error(self, msg, *args, **kwargs):
        new_msg, new_args, kwargs = self.add_so_id(msg, *args, **kwargs)
        self.logger.error(new_msg, *new_args, **kwargs)

    def critical(self, msg, *args, **kwargs):
        new_msg, new_args, kwargs = self.add_so_id(msg, *args, **kwargs)
        self.logger.critical(new_msg, *new_args, **kwargs)

    def exception(self, msg, *args, **kwargs):
        new_msg, new_args, kwargs = self.add_so_id(msg, *args, **kwargs)
        kwargs['exc_info'] = 1
        self.logger.exception(new_msg, *new_args, **kwargs)

    def log(self, level, msg, *args, **kwargs):
        new_msg, new_args, kwargs = self.add_so_id(msg, *args, **kwargs)
        self.logger.log(level, new_msg, *new_args, **kwargs)


class SpaceObject(decometaclass.WrapBlueClass('destiny.ClientBall')):
    __persistdeco__ = 0
    __update_on_reload__ = 1

    def __init__(self):
        self.explodeOnRemove = False
        self.exploded = False
        self.unloaded = False
        self.model = None
        self.additionalModels = []
        self.animationSequencer = None
        self.animationStateObject = None
        self.released = False
        self.wreckID = None
        self._audioEntities = []
        self._audioEntity = None
        self.logger = logging.getLogger('spaceObject.' + self.__class__.__name__)
        self.logger = SpaceObjectLogAdapter(self.logger, so_id=self.id)
        self.modelLoadedEvent = locks.Event()
        self.modelLoadSignal = Signal()
        self.explosionModel = None
        self.typeID = None
        self.typeData = {}
        self.explosionManager = ExplosionManager()

    def GetPositionCurve(self):
        return self

    def GetTypeID(self):
        if self.typeID is None:
            self.typeID = self.typeData.get('typeID', None)
        return self.typeID

    def SetServices(self, spaceMgr, serviceMgr):
        self.spaceMgr = spaceMgr
        self.sm = serviceMgr
        self.spaceObjectFactory = serviceMgr.GetService('sofService').spaceObjectFactory

    def Prepare(self):
        self.typeID = self.typeData.get('typeID', None)
        self.LoadModel()
        self.Assemble()

    def HasBlueInterface(self, obj, interfaceName):
        if hasattr(obj, 'TypeInfo'):
            return interfaceName in obj.TypeInfo()[1]
        return False

    def _GetComponentRegistry(self):
        return self.ballpark.componentRegistry

    def TriggerAnimation(self, state, **kwargs):
        if self.animationSequencer is None:
            return
        self.logger.debug('SpaceObject: Trigger animation %s with parameters %s', state, kwargs)
        for parameterName, parameterValue in kwargs.iteritems():
            self.animationSequencer.SetStateParameter(state, parameterName, parameterValue)

        self.animationSequencer.GoToState(state)
        if self.animationStateObject:
            self.RemoveAndClearModel(self.animationStateObject)
            self.animationStateObject = None
        if state in self.typeData['animationStateObjects']:
            dnaToLoad = self.typeData['animationStateObjects'][state]
            self.animationStateObject = self.spaceObjectFactory.BuildFromDNA(dnaToLoad)
            self._SetupModelAttributes(self.animationStateObject, '%d_%s' % (self.id, state))
            self.animationStateObject.rotationCurve = self.model.rotationCurve
            self._AddModelToScene(self.animationStateObject)

    def GetCurrentAnimationState(self, stateMachineName):
        if self.animationSequencer is None:
            return
        for stateMachine in self.animationSequencer.stateMachines:
            if stateMachine.name == stateMachineName:
                if stateMachine.currentState is None:
                    return
                else:
                    return stateMachine.currentState.name

    def GetModel(self):
        if not self.model:
            if blue.os.isOnMainTasklet:
                return None
            self.modelLoadedEvent.wait()
        return self.model

    def GetDNA(self):
        materialSetID = self.typeData.get('slimItem').skinMaterialSetID
        return gfxutils.BuildSOFDNAFromTypeID(self.typeData['typeID'], materialSetID=materialSetID)

    def _LoadModelResource(self, fileName = None):
        self.logger.debug('LoadModel: %s', fileName)
        model = None
        sofDNA = self.GetDNA()
        self.logger.debug("LoadModel fileName='%s' sofDNA='%s'", fileName, sofDNA)
        if sofDNA is not None and fileName is None:
            model = self.spaceObjectFactory.BuildFromDNA(sofDNA)
        else:
            if fileName is None:
                fileName = self.typeData.get('graphicFile')
            if fileName is not None and len(fileName):
                model = blue.resMan.LoadObject(fileName)
        if model is None:
            self.logger.error('Error: Object type %s has invalid graphicFile, using graphicID: %s', self.typeData['typeID'], self.typeData['graphicID'])
        return model

    def _SetupModelAndAddToScene(self, fileName = None, loadedModel = None):
        if loadedModel:
            model = loadedModel
        else:
            model = self._LoadModelResource(fileName)
        if self.released:
            return None
        if not model:
            self.logger.error('Could not load model for spaceobject. FileName:%s typeID:%s', fileName, getattr(self, 'typeID', '?'))
            return None
        self._SetupModelAttributes(model, '%d' % self.id)
        self._AddModelToScene(model)
        return model

    def _SetupModelAttributes(self, model, objectName):
        model.translationCurve = self
        model.rotationCurve = self
        model.name = objectName
        if hasattr(model, 'useCurves'):
            model.useCurves = 1
        if model and hasattr(model, 'albedoColor'):
            model.albedoColor = eveSpaceObject.GetAlbedoColor(model)

    def _AddModelToScene(self, model):
        if model is not None:
            scene = self.spaceMgr.GetScene()
            if scene is not None:
                scene.objects.append(model)
            else:
                raise RuntimeError('Invalid object loaded by spaceObject: %s' % str(model))

    def LoadAdditionalModel(self, fileName = None):
        model = self._SetupModelAndAddToScene(fileName)
        if fileName is not None:
            self.additionalModels.append(model)
        return model

    def NotifyModelLoaded(self):
        if self.model is not None:
            self.logger.debug('SpaceObject - NotifyModelLoaded')
            self.modelLoadedEvent.set()
            self.modelLoadSignal()
            self.sm.GetService('FxSequencer').NotifyModelLoaded(self.id)
        else:
            self.logger.warning('SpaceObject - NotifyModelLoaded called without a model present, no notification was done')

    def RegisterForModelLoad(self, func):
        self.modelLoadSignal.connect(func)

    def LoadModel(self, fileName = None, loadedModel = None):
        self.model = self._SetupModelAndAddToScene(fileName, loadedModel)
        if self.model is None:
            return
        self.SetupAnimationInformation(self.model)
        self.NotifyModelLoaded()

    def SetupAnimationInformation(self, model):
        self._SetupAnimationStateMachines(model)
        self._SetupAnimationUpdater(model)

    def SetAnimationSequencer(self, model):
        if model is not None and hasattr(model, 'animationSequencer'):
            self.animationSequencer = model.animationSequencer
        else:
            self.animationSequencer = None

    def _SetupAnimationStateMachines(self, model):
        animationStates = self.typeData['animationStates']
        if len(animationStates) == 0:
            return
        spaceobjanimation.LoadAnimationStates(animationStates, cfg.graphicStates, model, trinity)
        self.SetAnimationSequencer(model)

    def _SetupAnimationUpdater(self, model):
        if not hasattr(model, 'animationUpdater') or not self.typeData['animationStates']:
            return
        if self._audioEntity is None:
            self._audioEntity = self._GetGeneralAudioEntity(model=model)
        if model is not None and model.animationUpdater is not None:
            model.animationUpdater.eventListener = self._audioEntity

    def Assemble(self):
        pass

    def GetStaticRotation(self):
        rot = self.typeData.get('dunRotation', None)
        if rot:
            yaw, pitch, roll = map(math.radians, rot)
            return geo2.QuaternionRotationSetYawPitchRoll(yaw, pitch, roll)
        else:
            return (0.0, 0.0, 0.0, 1.0)

    def SetStaticRotation(self):
        if self.model is None:
            return
        self.model.rotationCurve = None
        rot = self.typeData.get('dunRotation', None)
        if rot:
            yaw, pitch, roll = map(math.radians, rot)
            quat = geo2.QuaternionRotationSetYawPitchRoll(yaw, pitch, roll)
            if hasattr(self.model, 'rotation'):
                if type(self.model.rotation) == types.TupleType:
                    self.model.rotation = quat
                else:
                    self.model.rotation.SetYawPitchRoll(yaw, pitch, roll)
            else:
                self.model.rotationCurve = trinity.TriRotationCurve()
                self.model.rotationCurve.value = quat
                if self.animationStateObject is not None:
                    self.animationStateObject.rotationCurve = self.model.rotationCurve

    def _FindClosestBallDir(self, constgrp):
        bp = self.sm.StartService('michelle').GetBallpark()
        dist = 1e+100
        closestID = None
        for ballID, slimItem in bp.slimItems.iteritems():
            if slimItem.groupID == constgrp:
                test = bp.DistanceBetween(self.id, ballID)
                if test < dist:
                    dist = test
                    closestID = ballID

        if closestID is None:
            return (1.0, 0.0, 0.0)
        ball = bp.GetBall(closestID)
        direction = geo2.Vec3SubtractD((self.x, self.y, self.z), (ball.x, ball.y, ball.z))
        return direction

    def FindClosestMoonDir(self):
        return self._FindClosestBallDir(const.groupMoon)

    def FindClosestPlanetDir(self):
        return self._FindClosestBallDir(const.groupPlanet)

    def GetStaticDirection(self):
        return self.typeData.get('dunDirection', None)

    def SetStaticDirection(self):
        if self.model is None:
            return
        self.model.rotationCurve = None
        direction = self.GetStaticDirection()
        if direction is None:
            self.logger.error('No static direction defined - no rotation will be applied')
            return
        self.AlignToDirection(direction)

    def AlignToDirection(self, direction):
        if not self.model:
            return
        zaxis = direction
        if geo2.Vec3LengthSqD(zaxis) > 0.0:
            zaxis = geo2.Vec3NormalizeD(zaxis)
            xaxis = geo2.Vec3CrossD(zaxis, (0, 1, 0))
            if geo2.Vec3LengthSqD(xaxis) == 0.0:
                zaxis = geo2.Vec3AddD(zaxis, mathCommon.RandomVector(0.0001))
                zaxis = geo2.Vec3NormalizeD(zaxis)
                xaxis = geo2.Vec3CrossD(zaxis, (0, 1, 0))
            xaxis = geo2.Vec3NormalizeD(xaxis)
            yaxis = geo2.Vec3CrossD(xaxis, zaxis)
        else:
            self.logger.error('Invalid direction (%s). Unable to rotate it.', direction)
            return
        mat = ((xaxis[0],
          xaxis[1],
          xaxis[2],
          0.0),
         (yaxis[0],
          yaxis[1],
          yaxis[2],
          0.0),
         (-zaxis[0],
          -zaxis[1],
          -zaxis[2],
          0.0),
         (0.0, 0.0, 0.0, 1.0))
        quat = geo2.QuaternionRotationMatrix(mat)
        if hasattr(self.model, 'modelRotationCurve'):
            if not self.model.modelRotationCurve:
                self.model.modelRotationCurve = trinity.TriRotationCurve(0.0, 0.0, 0.0, 1.0)
            self.model.modelRotationCurve.value = quat
        else:
            self.model.rotationCurve = None

    def UnSync(self):
        if self.model is None:
            return
        startTime = long(random.random() * 123456.0 * 1234.0)
        scaling = 0.95 + random.random() * 0.1
        curves = timecurves.ReadCurves(self.model)
        timecurves.ResetTimeCurves(curves, startTime, scaling)

    def Display(self, display = 1, canYield = True):
        if self.model is None:
            if display:
                self.logger.warning('Display - No model')
            return
        if canYield:
            blue.synchro.Yield()
        if eve.session.shipid == self.id and display and self.IsCloaked():
            self.sm.StartService('FxSequencer').OnSpecialFX(self.id, None, None, None, None, 'effects.CloakNoAmim', 0, 1, 0, 5, 0)
            return
        if self.model:
            self.model.display = display

    def IsCloaked(self):
        return self.isCloaked

    def OnDamageState(self, damageState):
        pass

    def GetDamageState(self):
        bp = sm.GetService('michelle').GetBallpark()
        if bp is not None:
            return bp.GetDamageState(self.id)

    def _UpdateImpacts(self):
        states = self.GetDamageState()
        if states is not None and self.model is not None:
            damageState = [ (d if d is not None else 0.0) for d in states ]
            self.model.SetImpactDamageState(damageState[0], damageState[1], damageState[2], True)

    def DoFinalCleanup(self):
        if not self.sm.IsServiceRunning('FxSequencer'):
            return
        self.sm.GetService('FxSequencer').RemoveAllBallActivations(self.id)
        self.ClearExplosion()
        if not self.released:
            self.explodeOnRemove = False
            self.Release()
        elif self.HasModels():
            scene = self.spaceMgr.GetScene()
            self.ClearAndRemoveAllModels(scene)

    def ClearExplosion(self, model = None):
        if hasattr(self, 'gfx') and self.gfx is not None:
            self.RemoveAndClearModel(self.gfx)
            self.gfx = None
        if self.explosionModel is not None:
            if getattr(self, 'explosionDisplayBinding', False):
                self.explosionDisplayBinding.destinationObject = None
                self.explosionDisplayBinding = None
            self.RemoveAndClearModel(self.explosionModel)
            self.explosionModel = None

    def Release(self, origin = None):
        uthread2.StartTasklet(self._Release, origin)

    def _Release(self, origin = None):
        if self.released:
            return
        self.released = True
        if self.explodeOnRemove:
            delay = self.Explode()
            if delay:
                blue.synchro.SleepSim(delay)
        self.Display(display=0, canYield=False)
        for model in self.additionalModels:
            if model is not None:
                model.display = False

        if hasattr(self.model, 'animationSequencer'):
            self.model.animationSequencer = None
        self.animationSequencer = None
        if hasattr(self.model, 'animationUpdater') and self.model.animationUpdater is not None:
            self.model.animationUpdater.eventListener = None
        self._audioEntities = []
        self._audioEntity = None
        scene = self.spaceMgr.GetScene()
        camera = sm.GetService('sceneManager').GetActiveSpaceCamera()
        lookingAt = camera.GetLookAtItemID()
        interestID = camera.GetTrackItemID()
        if self.explodeOnRemove and (self.id == lookingAt or interestID == self.id):
            self.RemoveAllModelsFromScene(scene)
        else:
            self.ClearAndRemoveAllModels(scene)

    def HasModels(self):
        return self.model is not None

    def ClearAndRemoveAllModels(self, scene):
        self.RemoveAndClearModel(self.model, scene)
        self.model = None
        for m in self.additionalModels:
            self.RemoveAndClearModel(m, scene)

        self.additionalModels = []
        if self.animationStateObject is not None:
            self.RemoveAndClearModel(self.animationStateObject, scene)
        self.animationStateObject = None

    def RemoveAllModelsFromScene(self, scene):
        if scene is None:
            return
        scene.objects.fremove(self.model)
        for m in self.additionalModels:
            scene.objects.fremove(m)

        if self.animationStateObject is not None:
            scene.objects.fremove(self.animationStateObject)

    def RemoveAndClearModel(self, model, scene = None):
        if model:
            self._Clearcurves(model)
        else:
            self.released = True
            return
        self.RemoveFromScene(model, scene)

    def _Clearcurves(self, model):
        if hasattr(model, 'translationCurve'):
            model.translationCurve = None
            model.rotationCurve = None
        if hasattr(model, 'observers'):
            for ob in model.observers:
                ob.observer = None

    def RemoveFromScene(self, model, scene):
        if scene is None:
            scene = self.spaceMgr.GetScene()
        if scene:
            scene.objects.fremove(model)

    def GetExplosionInfo(self):
        raceName = self.typeData.get('sofRaceName', None)
        return eveSpaceObject.GetDeathExplosionInfo(self.model, self.radius, raceName)

    def GetExplosionLookAtDelay(self):
        return eveSpaceObject.GetDeathExplosionLookDelay(self.model, self.radius)

    def Explode(self, explosionURL = None, scaling = 1.0, managed = False, delay = 0.0):
        if self.exploded:
            return False
        self.sm.ScatterEvent('OnObjectExplode', self.GetModel())
        self.exploded = True
        delayedRemove = delay
        self.explodedTime = blue.os.GetTime()
        if gfxsettings.Get(gfxsettings.UI_EXPLOSION_EFFECTS_ENABLED):
            if SpaceObjectExplosionManager.USE_EXPLOSION_BUCKETS:
                explosionBucket = fsdExplosionBuckets.GetExplosionBucketByTypeID(self.typeData['typeID'])
                if explosionBucket:
                    self.logger.debug('Exploding with explosion bucket')
                    scene = sm.GetService('space').GetScene()
                    wreckSwitchTime, _, __ = SpaceObjectExplosionManager.ExplodeBucketForBall(self, scene)
                    return wreckSwitchTime
            if managed:
                gfx = self.explosionManager.GetExplosion(explosionURL, callback=self.ClearExplosion)
            else:
                if explosionURL is None:
                    self.logger.error('explosionURL not set when calling Explode. Possibly wrongly authored content. typeID: %s', self.typeID)
                    explosionURL, (delay, scaling) = self.GetExplosionInfo()
                explosionURL = explosionURL.replace('.blue', '.red').replace('/Effect/', '/Effect3/')
                gfx = trinity.Load(explosionURL)
                if not gfx:
                    self.logger.error('Failed to load explosion: %s - using default', explosionURL)
                    gfx = trinity.Load('res:/Model/Effect3/Explosion/entityExplode_large.red')
                if isinstance(gfx, trinity.EveEffectRoot2):
                    msg = 'ExplosionManager circumvented, explosion not managed for %s. (Class:%s, Type:%s)'
                    self.logger.warning(msg, explosionURL, self.__class__.__name__, self.typeID)
                    gfx.Start()
                elif not isinstance(gfx, (trinity.EveRootTransform, trinity.EveEffectRoot2)):
                    root = trinity.EveRootTransform()
                    root.children.append(gfx)
                    root.name = explosionURL
                    gfx = root
            gfx.translationCurve = self
            self.explosionModel = gfx
            scale = scaling
            gfx.scaling = (gfx.scaling[0] * scale, gfx.scaling[1] * scale, gfx.scaling[2] * scale)
            scene = self.spaceMgr.GetScene()
            if scene is not None:
                scene.objects.append(gfx)
        if self.wreckID is not None:
            wreckBall = self.sm.StartService('michelle').GetBall(self.wreckID)
            if wreckBall is not None:
                uthread2.StartTasklet(wreckBall.DisplayWreck, delayedRemove)
        return delayedRemove

    def PrepareForFiring(self):
        pass

    def GetEventNameFromSlimItem(self, defaultSoundUrl):
        slimItem = self.typeData.get('slimItem')
        eventName = spaceobjaudio.GetSoundUrl(slimItem, defaultSoundUrl)
        return eventName

    def SetupAmbientAudio(self, defaultSoundUrl = None):
        audioUrl = self.GetEventNameFromSlimItem(defaultSoundUrl)
        if audioUrl is None:
            return
        audentity = self._GetGeneralAudioEntity()
        if audentity is not None:
            spaceobjaudio.PlayAmbientAudio(audentity, audioUrl)

    def SetupSharedAmbientAudio(self, defaultSoundUrl = None):
        eventName = self.GetEventNameFromSlimItem(defaultSoundUrl)
        if eventName is None or self.model is None:
            return
        spaceobjaudio.SetupSharedEmitterForAudioEvent(self.model, eventName)

    def LookAtMe(self):
        pass

    def _GetGeneralAudioEntity(self, model = None, recreate = False):
        if model is None:
            model = self.model
        if model is None:
            self._audioEntity = None
            self.logger.warning('model is None, cannot play audio.')
        elif recreate or self._audioEntity is None:
            self._audioEntity = spaceobjaudio.SetupAudioEntity(model)
            self._audioEntities.append(self._audioEntity)
        return self._audioEntity

    def PlayGeneralAudioEvent(self, eventName):
        audentity = self._GetGeneralAudioEntity()
        if audentity is not None:
            spaceobjaudio.SendEvent(audentity, eventName)

    def GetNamedAudioEmitterFromObservers(self, emitterName):
        if getattr(self, 'model', None) is None:
            return
        for triObserver in self.model.observers:
            if triObserver.observer.name.lower() == emitterName:
                return triObserver.observer

    def PlaySound(self, event):
        if self.model is None:
            return
        if hasattr(self.model, 'observers'):
            for obs in self.model.observers:
                obs.observer.SendEvent(unicode(event))
                return

        self.logger.error("Space Object: %s can't play sound. Sound observer not found.", self.typeData.get('typeName', None))
