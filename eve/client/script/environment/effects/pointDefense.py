#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\environment\effects\pointDefense.py
from eve.client.script.environment.effects.GenericEffect import GenericEffect
import blue

class PointDefense(GenericEffect):
    __guid__ = 'effects.PointDefense'

    def __init__(self, trigger, *args):
        GenericEffect.__init__(self, trigger, *args)
        self.ballIDs = [trigger.shipID]
        self.ballpark = sm.GetService('michelle').GetBallpark()
        self.trigger = trigger
        self.gfx = None

    def Prepare(self):
        self.gfx = self.RecycleOrLoad(self.graphicFile)
        structureID = self.ballIDs[0]
        structureBall = self.fxSequencer.GetBall(structureID)
        self.gfx.translationCurve = structureBall
        self.gfx.rotationCurve = structureBall
        fx = self.gfx.effectChildren[0]
        fx.sourceObject = getattr(structureBall, 'model', None)
        self.AddSoundToEffect(scaler=1, model=fx.sourceObject)
        scene = self.fxSequencer.GetScene()
        scene.objects.append(self.gfx)

    def Start(self, duration):
        if self.gfx is not None:
            self.UpdateTargets(self.gfx.effectChildren[0])
            self.SendAudioEvent('point_defense_battery_play')

    def Repeat(self, duration):
        if self.gfx is not None:
            self.UpdateTargets(self.gfx.effectChildren[0])

    def Stop(self, reason = None):
        if self.gfx is not None:
            scene = self.fxSequencer.GetScene()
            scene.objects.fremove(self.gfx)
            self.gfx = None
            self.SendAudioEvent('point_defense_battery_stop')

    def UpdateTargets(self, fx):
        radius = self.fxSequencer.GetTypeAttribute(self.trigger.moduleTypeID, const.attributeEmpFieldRange)
        ballIDs = self.ballpark.GetBallsInRange(self.trigger.shipID, radius)
        shipModels = []
        for bID in ballIDs:
            b = self.fxSequencer.GetBall(bID)
            m = getattr(b, 'model', None)
            if m is not None:
                shipModels.append(m)

        del fx.targetObjects[:]
        for m in shipModels:
            fx.targetObjects.append(m)
