#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\environment\effects\shipRenderEffect.py
from eve.client.script.environment.effects.GenericEffect import ShipEffect, STOP_REASON_DEFAULT
from evegraphics.utils import GetCorrectEffectPath
import eveSpaceObject.spaceobjaudio as spaceobjaudio

class ShipRenderEffect(ShipEffect):
    __guid__ = 'effects.ShipRenderEffect'

    def Prepare(self):
        shipBall = self.GetEffectShipBall()
        self.sourceObject = shipBall.model
        path = GetCorrectEffectPath(self.graphicFile, self.sourceObject)
        self.gfx = self.RecycleOrLoad(path)
        self.sourceObject.overlayEffects.append(self.gfx)
        self.AddSoundToEffect(scaler=1.0, model=self.sourceObject)

    def Start(self, duration):
        shipBall = self.GetEffectShipBall()
        if hasattr(shipBall, 'RegisterModelChangeNotification'):
            shipBall.RegisterModelChangeNotification(self.ChangeModel)
        if self.gfx is None:
            raise RuntimeError('ShipEffect: no effect defined')
        if self.gfx.curveSet is not None:
            if self.scaleTime:
                length = self.gfx.curveSet.GetMaxCurveDuration()
                if length > 0.0:
                    scaleValue = length / (duration / 1000.0)
                    self.gfx.curveSet.scale = scaleValue
            self.gfx.curveSet.Play()

    def Stop(self, reason = STOP_REASON_DEFAULT):
        if self.gfx in self.sourceObject.overlayEffects:
            self.sourceObject.overlayEffects.remove(self.gfx)
        if self.observer in self.sourceObject.observers:
            self.sourceObject.observers.remove(self.observer)
        self.gfx = None
        self.gfxModel = None
        self.sourceObject = None
        self.observer = None

    def Repeat(self, duration):
        if self.gfx is None:
            return
        if self.gfx.curveSet:
            self.gfx.curveSet.Play()

    def ChangeModel(self, model):
        if self.sourceObject and self.gfx:
            if self.gfx in self.sourceObject.overlayEffects:
                self.sourceObject.overlayEffects.remove(self.gfx)
        self.sourceObject = model
        if self.gfx:
            self.sourceObject.overlayEffects.append(self.gfx)

    def AttachObserverToModel(self, model):
        model.observers.append(self.observer)

    def GetEffectRadius(self):
        srcRadius = 35
        if self.sourceObject:
            srcRadius = self.sourceObject.boundingSphereRadius
        return srcRadius


class ShipRenderTargetedEffect(ShipEffect):
    __guid__ = 'effects.ShipRenderTargetedEffect'

    def Prepare(self):
        shipBall = self.GetEffectShipBall()
        self.sourceObject = shipBall.model
        targetBall = self.GetEffectTargetBall()
        self.targetObject = targetBall
        self.gfx = self.RecycleOrLoad(self.graphicFile)
        self.gfx.target = targetBall
        for gfxParameter, val in self.graphicInfo.iteritems():
            if hasattr(self.gfx, gfxParameter):
                setattr(self.gfx, gfxParameter, val)

        self.sourceObject.effectChildren.append(self.gfx)
        self.AddSoundToEffect(4.0, model=self.sourceObject)
        self.SetupLinkAudio(self.gfx)

    def Start(self, duration):
        shipBall = self.GetEffectShipBall()
        if hasattr(shipBall, 'RegisterModelChangeNotification'):
            shipBall.RegisterModelChangeNotification(self.ChangeModel)

    def Stop(self, reason = STOP_REASON_DEFAULT):
        if self.gfx in self.sourceObject.effectChildren:
            self.sourceObject.effectChildren.remove(self.gfx)
        if self.observer in self.sourceObject.observers:
            self.sourceObject.observers.remove(self.observer)
        self.gfx = None
        self.gfxModel = None
        self.sourceObject = None
        self.targetObject = None
        self.RemoveLinkAudio()

    def ChangeModel(self, model):
        if self.sourceObject and self.gfx:
            if self.gfx in self.sourceObject.effectChildren:
                self.sourceObject.effectChildren.remove(self.gfx)
        self.sourceObject = model
        if self.gfx:
            self.sourceObject.effectChildren.append(self.gfx)

    def AttachObserverToModel(self, model):
        model.observers.append(self.observer)

    def GetEffectRadius(self):
        srcRadius = 35
        if self.sourceObject:
            srcRadius = self.sourceObject.boundingSphereRadius
        return srcRadius

    def SetupLinkAudio(self, linkFX):
        linkAudioEmitter = self.observer.observer
        audparam = spaceobjaudio.bindAudioParameterToAttribute(linkFX, 'linkStrength', linkFX.linkStrengthBindings)
        linkAudioEmitter.parameters.append(audparam)
        self.SendAudioEvent('structure_invulnerability_link_play')

    def RemoveLinkAudio(self):
        self.SendAudioEvent('fade_out')
        self.observer = None
