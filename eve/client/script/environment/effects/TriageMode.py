#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\environment\effects\TriageMode.py
from eve.client.script.environment.effects.GenericEffect import STOP_REASON_DEFAULT
from eve.client.script.environment.effects.shipRenderEffect import ShipRenderEffect

class TriageMode(ShipRenderEffect):
    __guid__ = 'effects.TriageMode'

    def Stop(self, reason = STOP_REASON_DEFAULT):
        ShipRenderEffect.Stop(self, reason)
        shipID = self.ballIDs[0]
        shipBall = self.fxSequencer.GetBall(shipID)
        shipBall.TriggerAnimation('normal')

    def Start(self, duration):
        ShipRenderEffect.Start(self, duration)
        shipID = self.ballIDs[0]
        shipBall = self.fxSequencer.GetBall(shipID)
        shipBall.TriggerAnimation('siege')

    def Repeat(self, duration):
        ShipRenderEffect.Repeat(self, duration)
