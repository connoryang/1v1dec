#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\environment\effects\GenericEffect.py
import blue
import trinity
import audio2
from evegraphics.fsd.graphicIDs import GetGraphicFile
import eve.client.script.environment.spaceObject.ship as ship
from eve.client.script.environment.effects.effectConsts import FX_TF_NONE, FX_TF_SCALE_SYMMETRIC, FX_TF_SCALE_RADIUS, FX_TF_SCALE_BOUNDING, FX_TF_ROTATION_BALL, FX_TF_POSITION_BALL, FX_TF_POSITION_MODEL, FX_TF_POSITION_TARGET
STOP_REASON_DEFAULT = 'STOP_REASON_DEFAULT'
STOP_REASON_BALL_REMOVED = 'STOP_REASON_BALL_REMOVED'

class GenericEffect(object):
    __guid__ = 'effects.GenericEffect'

    def __init__(self, trigger, effect = None, graphicFile = None):
        self.ballIDs = [trigger.shipID, trigger.targetID]
        self.gfx = None
        self.gfxModel = None
        self.graphicFile = graphicFile
        self.transformFlags = [0] if effect is None else effect.transformFlags
        self.mergeFlags = [0] if effect is None else effect.mergeFlags
        if trigger.duration is not None and trigger.duration > 0:
            self.duration = trigger.duration
        else:
            self.duration = getattr(effect, 'duration', 10000)
        if hasattr(effect, 'secondaryGraphicID'):
            self.secondaryGraphicFile = GetGraphicFile(getattr(effect, 'secondaryGraphicID'))
        else:
            self.secondaryGraphicFile = None
        self.scaleTime = getattr(effect, 'timeScale', False)
        self.sourceOffset = 0 if effect is None else effect.sourceOffset
        self.destinationOffset = 0 if effect is None else effect.destinationOffset
        self.animationName = None if effect is None else getattr(effect, 'animationName', None)
        self.graphicInfo = trigger.graphicInfo
        self.startTime = trigger.startTime
        self.timeFromStart = trigger.timeFromStart
        self.moduleID = trigger.moduleID
        self.fxSequencer = sm.GetService('FxSequencer')
        self.observer = None

    def Prepare(self, addToScene = True):
        pass

    def Start(self, duration):
        pass

    def Stop(self, reason = STOP_REASON_DEFAULT):
        pass

    def Repeat(self, duration):
        pass

    def GetBalls(self):
        return self.ballIDs

    def GetBallPositionCurve(self, ball):
        if hasattr(ball, 'GetPositionCurve'):
            return ball.GetPositionCurve()
        return ball

    def GetEffectShipID(self):
        return self.ballIDs[0]

    def GetEffectShipBall(self):
        return self.fxSequencer.GetBall(self.GetEffectShipID())

    def GetEffectTargetID(self):
        return self.ballIDs[1]

    def GetEffectTargetBall(self):
        return self.fxSequencer.GetBall(self.GetEffectTargetID())

    def PlayOldAnimations(self, tf):
        curveTypes = ['trinity.TriScalarCurve',
         'trinity.TriVectorCurve',
         'trinity.TriRotationCurve',
         'trinity.TriColorCurve']
        curves = tf.Find(curveTypes)
        now = blue.os.GetSimTime()
        for curve in curves:
            curve.start = now

    def PlayNamedAnimations(self, model, animName):
        if not model:
            return
        for each in model.curveSets:
            if each.name == animName:
                each.Play()

    def GetEffectRadius(self):
        srcRadius = 35
        if self.gfx:
            effectBall = self.GetEffectShipBall()
            if effectBall is not None:
                srcRadius = effectBall.radius
        return srcRadius

    def ScaleEffectAudioEmitter(self, entity, scaler = 1.0):
        srcRadius = self.GetEffectRadius()
        if srcRadius < 0:
            return
        attenuation = pow(srcRadius, 0.95) * 33 * scaler
        if entity is not None:
            entity.SetAttenuationScalingFactor(attenuation)

    def AttachObserverToTriEventCurve(self):
        if self.gfx is None:
            return
        for curve in self.gfx.Find('trinity.TriEventCurve'):
            if curve.name == 'audioEvents':
                curve.eventListener = self.observer.observer

    def CheckForExistingObserver(self, location, name):
        if location is not None:
            for observer in location.Find('trinity.TriObserverLocal'):
                if getattr(observer, 'observer', None) is not None:
                    if observer.observer.name == name:
                        self.observer = observer
                        return

        if self.gfx is None:
            return
        for observer in self.gfx.Find('trinity.TriObserverLocal'):
            if getattr(observer, 'observer', None) is not None:
                if 'booster' not in observer.observer.name:
                    self.observer = observer
                    return

    def AddSoundToEffect(self, scaler = 1.0, model = None):
        shipID = self.GetEffectShipID()
        emitter_name = 'effect_' + str(shipID) + '_' + self.__guid__
        self.CheckForExistingObserver(model, emitter_name)
        if self.observer is None:
            self.observer = trinity.TriObserverLocal()
            entity = audio2.AudEmitter(emitter_name)
            self.observer.observer = entity
            if model is None:
                model = self.gfx
            self.AttachObserverToModel(model)
            self.AttachObserverToTriEventCurve()
            if hasattr(self.observer, 'observer') and self.observer.observer is not None:
                self.ScaleEffectAudioEmitter(self.observer.observer, scaler)

    def SetupEffectEmitter(self):
        if self.observer is None:
            self.AddSoundToEffect(scaler=1.0)

    def SendAudioEvent(self, eventName):
        triObserver = self.observer
        if hasattr(triObserver, 'observer') and triObserver.observer is not None:
            triObserver.observer.SendEvent(eventName)

    def AttachObserverToModel(self, model):
        model.observers.append(self.observer)

    def AddToScene(self, effect):
        scene = self.fxSequencer.GetScene()
        if scene is not None:
            scene.objects.append(effect)

    def RemoveFromScene(self, effect):
        scene = self.fxSequencer.GetScene()
        if scene is not None:
            scene.objects.fremove(effect)

    def RecycleOrLoad(self, resPath):
        return trinity.Load(resPath)

    def _SpawnClientBall(self, position):
        bp = self.fxSequencer.GetBallpark()
        if bp is None:
            return
        egopos = bp.GetCurrentEgoPos()
        ballPosition = (position[0] + egopos[0], position[1] + egopos[1], position[2] + egopos[2])
        return bp.AddClientSideBall(ballPosition)

    def _DestroyClientBall(self, ball):
        bp = self.fxSequencer.GetBallpark()
        if bp is not None:
            bp.RemoveBall(ball.id)


class ShipEffect(GenericEffect):
    __guid__ = 'effects.ShipEffect'

    def Stop(self, reason = STOP_REASON_DEFAULT):
        if self.gfx is None:
            raise RuntimeError('ShipEffect: no effect defined:' + self.__guid__)
        self.RemoveFromScene(self.gfxModel)
        self.gfx = None
        if self.gfxModel:
            self.gfxModel.translationCurve = None
            self.gfxModel.rotationCurve = None
        self.gfxModel = None
        self.observer = None

    def Prepare(self, addToScene = True):
        shipBall = self.GetEffectShipBall()
        if shipBall is None:
            raise RuntimeError('ShipEffect: no ball found:' + self.__guid__)
        self.gfx = self.RecycleOrLoad(self.graphicFile)
        if self.gfx is None:
            raise RuntimeError('ShipEffect: no effect found:' + self.__guid__)
        self.AddSoundToEffect(2)
        if type(self.gfx) == trinity.EveTransform:
            self.gfxModel = trinity.EveRootTransform()
            self.gfxModel.children.append(self.gfx)
        else:
            self.gfxModel = self.gfx
        self.gfxModel.modelRotationCurve = getattr(shipBall.model, 'modelRotationCurve', None)
        self.gfxModel.modelTranslationCurve = getattr(shipBall.model, 'modelTranslationCurve', None)
        effectBall = shipBall
        if FX_TF_POSITION_BALL in self.transformFlags:
            self.gfxModel.translationCurve = self.GetBallPositionCurve(shipBall)
        if FX_TF_POSITION_MODEL in self.transformFlags:
            behavior = trinity.EveLocalPositionBehavior.centerBounds
            self.gfxModel.translationCurve = trinity.EveLocalPositionCurve(behavior)
            self.gfxModel.translationCurve.parent = shipBall.model
        if FX_TF_POSITION_TARGET in self.transformFlags:
            effectBall = self.GetEffectTargetBall()
            self.gfxModel.translationCurve = self.GetBallPositionCurve(effectBall)
        if FX_TF_SCALE_BOUNDING in self.transformFlags:
            shipBBoxMin, shipBBoxMax = effectBall.model.GetLocalBoundingBox()
            bBox = (max(-shipBBoxMin[0], shipBBoxMax[0]) * 1.2, max(-shipBBoxMin[1], shipBBoxMax[1]) * 1.2, max(-shipBBoxMin[2], shipBBoxMax[2]) * 1.2)
            self.gfxModel.scaling = bBox
        elif FX_TF_SCALE_SYMMETRIC in self.transformFlags:
            radius = effectBall.model.GetBoundingSphereRadius()
            self.gfxModel.scaling = (radius, radius, radius)
            self.gfx.translation = (0, 0, 0)
        elif FX_TF_SCALE_RADIUS in self.transformFlags:
            radius = effectBall.model.GetBoundingSphereRadius()
            self.gfxModel.scaling = (radius, radius, radius)
        if FX_TF_ROTATION_BALL in self.transformFlags:
            self.gfxModel.rotationCurve = effectBall
        self.gfxModel.name = self.__guid__
        if addToScene:
            self.AddToScene(self.gfxModel)

    def Start(self, duration):
        if self.gfx is None:
            raise RuntimeError('ShipEffect: no effect defined:' + self.__guid__)
        curveSets = self.gfx.curveSets
        if len(curveSets) > 0:
            if self.scaleTime:
                length = self.gfx.curveSets[0].GetMaxCurveDuration()
                if length > 0.0:
                    scaleValue = length / (duration / 1000.0)
                    self.gfx.curveSets[0].scale = scaleValue
            curveSets[0].PlayFrom(self.timeFromStart / float(const.SEC))

    def Repeat(self, duration):
        if self.gfx is None:
            return
        if self.gfxModel is not None:
            gfxModelChildren = self.gfxModel.children
            if len(gfxModelChildren):
                curveSets = gfxModelChildren[0].curveSets
                if len(curveSets):
                    curveSets[0].Play()


def GetBoundingBox(shipBall, scale = 1.0):
    if not isinstance(shipBall, ship.Ship):
        return (shipBall.radius, shipBall.radius, shipBall.radius)
    if hasattr(shipBall, 'GetModel'):
        model = shipBall.GetModel()
    else:
        model = getattr(shipBall, 'model', None)
    if model is None:
        return (shipBall.radius, shipBall.radius, shipBall.radius)
    if hasattr(model, 'GetLocalBoundingBox'):
        shipBBoxMin, shipBBoxMax = model.GetLocalBoundingBox()
        if shipBBoxMin is None or shipBBoxMax is None:
            raise RuntimeError('StretchEffect: invalid LocalBoundingBox')
        else:
            return (scale * max(-shipBBoxMin[0], shipBBoxMax[0]), scale * max(-shipBBoxMin[1], shipBBoxMax[1]), scale * max(-shipBBoxMin[2], shipBBoxMax[2]))
    else:
        raise RuntimeError('StretchEffect: needs GetLocalBoundingBox')
