#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\environment\effects\stretchEffect.py
import trinity
import geo2
import const
import uthread
from eve.client.script.environment.effects.GenericEffect import GenericEffect, GetBoundingBox, STOP_REASON_DEFAULT
import blue

class StretchEffect(GenericEffect):
    __guid__ = 'effects.StretchEffect'

    def Stop(self, reason = STOP_REASON_DEFAULT):
        if self.gfx is None:
            raise RuntimeError('StretchEffect: no effect defined: ' + str(getattr(self, 'graphicFile', 'None')))
        if self.gfx.curveSets is not None and len(self.gfx.curveSets) > 0:
            self.FadeOutAudio()
        self.RemoveFromScene(self.gfxModel)
        if isinstance(self.gfx.source, trinity.EveLocalPositionCurve):
            self.gfx.source.parentPositionCurve = None
            self.gfx.source.parentRotationCurve = None
            self.gfx.source.alignPositionCurve = None
        if isinstance(self.gfx.dest, trinity.EveLocalPositionCurve):
            self.gfx.dest.parentPositionCurve = None
            self.gfx.dest.parentRotationCurve = None
            self.gfx.dest.alignPositionCurve = None
        self.gfx = None
        self.gfxModel = None

    def Prepare(self):
        shipBall = self.GetEffectShipBall()
        positionCurve = self.GetBallPositionCurve(shipBall)
        targetBall = self.GetEffectTargetBall()
        if shipBall is None:
            raise RuntimeError('StretchEffect: no ball found')
        if not getattr(shipBall, 'model', None):
            raise RuntimeError('StretchEffect: no model found')
        if targetBall is None:
            raise RuntimeError('StretchEffect: no target ball found')
        self.gfx = self.RecycleOrLoad(self.graphicFile)
        if self.gfx is None:
            raise RuntimeError('StretchEffect: no effect found: ' + str(getattr(self, 'graphicFile', 'None')))
        self.ScaleEffectAudioEmitters()
        self.gfxModel = self.gfx
        sourceBehavior = trinity.EveLocalPositionBehavior.nearestBounds
        self.gfx.source = trinity.EveLocalPositionCurve(sourceBehavior)
        self.gfx.source.offset = self.sourceOffset
        destBehavior = trinity.EveLocalPositionBehavior.nearestBounds
        self.gfx.dest = trinity.EveLocalPositionCurve(destBehavior)
        self.gfx.dest.offset = self.destinationOffset
        self.gfx.source.parentPositionCurve = positionCurve
        self.gfx.source.parentRotationCurve = shipBall
        self.gfx.source.alignPositionCurve = targetBall
        self.gfx.dest.parentPositionCurve = targetBall
        self.gfx.dest.parentRotationCurve = targetBall
        self.gfx.dest.alignPositionCurve = positionCurve
        sourceScale = GetBoundingBox(shipBall, scale=1.2)
        self.gfx.source.boundingSize = sourceScale
        targetScale = GetBoundingBox(targetBall, scale=1.2)
        self.gfx.dest.boundingSize = targetScale
        self.AddToScene(self.gfxModel)

    def Start(self, duration):
        if self.gfx is None:
            raise RuntimeError('StretchEffect: no effect defined: ' + str(getattr(self, 'graphicFile', 'None')))
        if self.gfx.curveSets is not None and len(self.gfx.curveSets) > 0:
            if self.scaleTime:
                length = self.gfx.curveSets[0].GetMaxCurveDuration()
                if length > 0.0:
                    scaleValue = length / (duration / 1000.0)
                    self.gfx.curveSets[0].scale = scaleValue
            self.gfx.Start()

    def FadeOutAudio(self):
        for curve in self.gfx.curveSets[0].curves:
            if curve.name.lower() in ('audioeventssource', 'audioeventsdest'):
                if hasattr(curve, 'audioEmitter'):
                    curve.audioEmitter.SendEvent('fade_out')

    def Repeat(self, duration):
        if self.gfx is None:
            return
        if self.gfx.curveSets is not None and len(self.gfx.curveSets) > 0:
            self.FadeOutAudio()
            self.gfx.curveSets[0].Play()

    def ScaleEffectAudioEmitters(self):
        shipBall = self.GetEffectShipBall()
        targetBall = self.GetEffectTargetBall()
        srcRadius = shipBall.radius
        destRadius = targetBall.radius
        srcAudio = None
        destAudio = None
        if shipBall is None or targetBall is None:
            return
        if self.gfx.stretchObject and len(self.gfx.stretchObject.observers) > 0:
            srcAudio = self.gfx.stretchObject.observers[0].observer
        elif self.gfx.sourceObject and len(self.gfx.stretchObject.observers) > 0:
            srcAudio = self.gfx.sourceObject.observers[0].observer
        if self.gfx.destObject and len(self.gfx.destObject.observers) > 0:
            destAudio = self.gfx.destObject.observers[0].observer
        srcAttenuation = pow(srcRadius, 0.95) * 33
        destAttenuation = pow(destRadius, 0.95) * 33
        if srcAudio is not None and destAudio is not None:
            srcAudio.SetAttenuationScalingFactor(srcAttenuation)
            destAudio.SetAttenuationScalingFactor(destAttenuation)


class LocatorStretchEffect(StretchEffect):
    __guid__ = 'effects.StretchEffect'

    def Prepare(self):
        shipBall = self.GetEffectShipBall()
        positionCurve = self.GetBallPositionCurve(shipBall)
        targetBall = self.GetEffectTargetBall()
        if shipBall is None:
            raise RuntimeError('LocatorStretchEffect: no ball found')
        if not getattr(shipBall, 'model', None):
            raise RuntimeError('LocatorStretchEffect: no model found')
        if targetBall is None:
            raise RuntimeError('LocatorStretchEffect: no target ball found')
        if not getattr(targetBall, 'model', None):
            raise RuntimeError('LocatorStretchEffect: no target model found')
        self.gfx = self.RecycleOrLoad(self.graphicFile)
        if self.gfx is None:
            raise RuntimeError('StretchEffect: no effect found: ' + str(getattr(self, 'graphicFile', 'None')))
        self.ScaleEffectAudioEmitters()
        self.gfxModel = self.gfx
        sourceBehavior = trinity.EveLocalPositionBehavior.nearestBounds
        self.gfx.source = trinity.EveLocalPositionCurve(sourceBehavior)
        destBehavior = trinity.EveLocalPositionBehavior.damageLocator
        self.gfx.dest = trinity.EveLocalPositionCurve(destBehavior)
        self.gfx.source.parentPositionCurve = positionCurve
        self.gfx.source.parentRotationCurve = shipBall
        self.gfx.source.alignPositionCurve = self.gfx.dest
        self.gfx.dest.parent = targetBall.model
        self.gfx.dest.alignPositionCurve = positionCurve
        sourceScale = GetBoundingBox(shipBall, scale=1.2)
        self.gfx.source.boundingSize = sourceScale
        self.AddToScene(self.gfxModel)

    def Stop(self, reason = STOP_REASON_DEFAULT):
        if self.gfx is None:
            raise RuntimeError('ShipEffect: no effect defined: ' + str(getattr(self, 'graphicFile', 'None')))
        if self.gfx.curveSets is not None and len(self.gfx.curveSets) > 0:
            self.FadeOutAudio()
        self.RemoveFromScene(self.gfxModel)
        self.gfx.source.parentPositionCurve = None
        self.gfx.source.parentRotationCurve = None
        self.gfx.source.alignPositionCurve = None
        self.gfx.source = None
        self.gfx.dest.parent = None
        self.gfx.dest.alignPositionCurve = None
        self.gfx.dest = None
        self.gfx = None
        self.gfxModel = None


class TurretStretchEffect(StretchEffect):
    __guid__ = 'effects.TurretStretchEffect'

    def __init__(self, trigger, effect = None, graphicFile = None):
        StretchEffect.__init__(self, trigger, effect, graphicFile)
        self.delayUntilDamageApplied = 13750.0

    def Prepare(self):
        StretchEffect.Prepare(self)
        shipBall = self.GetEffectShipBall()
        targetBall = self.GetEffectTargetBall()
        turret = shipBall.modules.get(self.moduleID, None)
        if turret is None:
            raise RuntimeError("StretchEffect: No module '%s' found" % self.moduleID)
        turretSet = turret.GetTurretSet()
        firingBoneWorldTransform = turretSet.GetFiringBoneWorldTransform(0)
        _, __, offsetPosition = geo2.MatrixDecompose(firingBoneWorldTransform)
        sourceOffsetCurve = trinity.TriVectorCurve()
        sourceOffsetCurve.value = offsetPosition
        self.gfx.source = sourceOffsetCurve
        destBehavior = trinity.EveLocalPositionBehavior.damageLocator
        self.gfx.dest = trinity.EveLocalPositionCurve(destBehavior)
        self.gfx.dest.parent = targetBall.model
        self.gfx.dest.alignPositionCurve = shipBall
        uthread.new(self.CreateImpact, targetBall, offsetPosition)

    def CreateImpact(self, targetBall, source):
        blue.synchro.Sleep(100)
        damageDuration = 3000
        targetPos = targetBall.GetVectorAt(blue.os.GetSimTime())
        target = geo2.Vector(targetPos.x, targetPos.y, targetPos.z)
        direction = geo2.Vec3Normalize(geo2.Vec3Subtract(source, target))
        targetBall.model.CreateImpact(self.gfx.dest.damageLocatorIndex, direction, damageDuration * 0.001, 2.0)


class CenterToCenterStretchEffect(StretchEffect):
    __guid__ = 'effects.CenterToCenterStretchEffect'

    def Prepare(self):
        StretchEffect.Prepare(self)
        self.gfxModel.source.behavior = trinity.EveLocalPositionBehavior.damageLocator
        self.gfxModel.source.parent = self.GetEffectShipBall().model
        self.gfxModel.dest.behavior = trinity.EveLocalPositionBehavior.damageLocator
        self.gfxModel.dest.parent = self.GetEffectTargetBall().model
        p = self.GetEffectShipBall().GetVectorAt(blue.os.GetSimTime())
        sourcePos = geo2.Vector(p.x, p.y, p.z)
        p = self.GetEffectTargetBall().GetVectorAt(blue.os.GetSimTime())
        targetPos = geo2.Vector(p.x, p.y, p.z)
        sourceToTargetDir = geo2.Vec3Direction(sourcePos, targetPos)
        uthread.new(self.CreateImpact, sourceToTargetDir)

    def CreateImpact(self, sourceToTargetDir):
        blue.synchro.Sleep(50)
        damageDuration = 3000
        targetToSourceDir = geo2.Vec3Scale(sourceToTargetDir, -1)
        self.GetEffectTargetBall().model.CreateImpact(self.gfx.dest.damageLocatorIndex, sourceToTargetDir, damageDuration * 0.001, 2.0)
        self.GetEffectShipBall().model.CreateImpact(self.gfx.source.damageLocatorIndex, targetToSourceDir, damageDuration * 0.001, 2.0)
