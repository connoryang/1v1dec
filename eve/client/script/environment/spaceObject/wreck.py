#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\environment\spaceObject\wreck.py
import random
import blue
import math
import uthread
import trinity
import geo2
from eve.client.script.environment.spaceObject.spaceObject import SpaceObject
from eve.client.script.environment.spaceObject.ExplosionManager import ExplosionManager
from evegraphics.explosions.spaceObjectExplosionManager import SpaceObjectExplosionManager

class Wreck(SpaceObject):

    def Assemble(self):
        self.UnSync()
        if self.model is None:
            return
        if not hasattr(self.model, 'locatorSets'):
            return
        explosionLocatorSets = self.model.locatorSets.FindByName('explosions')
        ExplosionManager.SetUpChildExplosion(self.model, explosionLocatorSets)
        self.SetupAmbientAudio()

    def SetRotation(self, yaw, pitch, roll):
        if hasattr(self.model, 'modelRotationCurve'):
            self.model.modelRotationCurve = trinity.TriRotationCurve()
            quat = geo2.QuaternionRotationSetYawPitchRoll(yaw, pitch, roll)
            self.model.modelRotationCurve.value = quat
        else:
            self.model.rotationCurve = None
            self.model.rotation.SetYawPitchRoll(yaw, pitch, roll)

    def SetRandomRotation(self):
        yaw, pitch, roll = random.random() * 6.28, random.random() * 6.28, random.random() * 6.28
        self.SetRotation(yaw, pitch, roll)
        self.model.display = 1

    def SetDungeonRotation(self, dunRotation):
        yaw, pitch, roll = map(math.radians, dunRotation)
        self.SetRotation(yaw, pitch, roll)
        self.model.display = 1

    def SetBallRotation(self, ball):
        self.model.rotationCurve = None
        slimItem = getattr(ball, 'typeData', {}).get('slimItem', None)
        if getattr(ball.model, 'modelRotationCurve', None) is not None:
            self.model.modelRotationCurve = ball.model.modelRotationCurve
        elif getattr(slimItem, 'dunRotation', None) is not None:
            self.SetDungeonRotation(slimItem.dunRotation)
        else:
            self.SetRotation(ball.yaw, ball.pitch, ball.roll)
        ball.wreckID = self.id
        self.model.display = 0
        if SpaceObjectExplosionManager.USE_EXPLOSION_BUCKETS:
            SpaceObjectExplosionManager.GetWreckSwitchTimeWhenItIsAvailable(ball.id, self.StartDisplayWreckThread)
        else:
            _, (timeUntilDisplay, __) = ball.GetExplosionInfo()
            uthread.pool('Wreck::DisplayWreck', self.DisplayWreck, timeUntilDisplay)

    def StartDisplayWreckThread(self, timeInBlueTime):
        uthread.pool('Wreck::DisplayWreck', self._DisplayWreckAtTime, timeInBlueTime)

    def _DisplayWreckAtTime(self, timeInBlueTime):
        blue.synchro.SleepUntilSim(timeInBlueTime)
        self.DisplayWreck()

    def Prepare(self):
        SpaceObject.Prepare(self)
        michelle = self.sm.GetService('michelle')
        slimItem = self.typeData.get('slimItem')
        explodedShipBall = michelle.GetBall(slimItem.launcherID)
        if explodedShipBall is not None and getattr(explodedShipBall, 'model', None) is not None:
            self.SetBallRotation(explodedShipBall)
        elif getattr(slimItem, 'dunRotation', None) is not None:
            self.SetDungeonRotation(slimItem.dunRotation)
        else:
            self.SetRandomRotation()

    def Display(self, display = 1, canYield = True):
        if display and getattr(self, 'delayedDisplay', 0):
            return
        SpaceObject.Display(self, display, canYield)

    def DisplayWreck(self, duration = None):
        if duration:
            blue.pyos.synchro.SleepSim(duration)
        if self.model is not None and self.model.display == 0:
            self.model.display = 1

    def Explode(self):
        if self.exploded:
            return False
        self.exploded = True
        return 0.0
