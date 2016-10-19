#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\view\hangarBehaviours\defaultHangarBehaviours.py
import geo2
import math
import trinity
from baseHangarBehaviours import BaseHangarShipBehaviour, BaseHangarTrafficBehaviour
import eveHangar.hangar as hangarUtil
import blue

class DefaultHangarShipBehaviour(BaseHangarShipBehaviour):

    def SetAnchorPoint(self, hangarScene):
        self.shipAnchorPoint = (0.0, hangarUtil.SHIP_FLOATING_HEIGHT, 0.0)

    def PlaceShip(self, model, typeID):
        self.model = model
        trinity.WaitForResourceLoads()
        self.InitModelPosition()
        boundingBoxYBottom = self.GetBoundingBoxYBottom(model)
        translation = geo2.Vec3Subtract(self.shipAnchorPoint, (0.0, boundingBoxYBottom, 0.0))
        offset = geo2.Vec3Scale(self.model.GetBoundingSphereCenter(), 0.5)
        self.model.translationCurve.value = geo2.Vec3Add(translation, offset)
        self.endPos = self.model.translationCurve.value
        uicore.animations.StopAnimation(self.model.translationCurve, 'value')

    def InitModelPosition(self):
        self.model.rotationCurve = trinity.TriRotationCurve()
        self.model.rotationCurve.value = geo2.QuaternionRotationAxis((0, 1, 0), math.pi)
        self.model.translationCurve = trinity.TriVectorCurve()

    def AnimModelBoosters(self, duration):
        if not self.model.boosters:
            return
        self.model.translationCurve.value = self.startPos
        self.model.boosters.alwaysOnIntensity = 0.65
        self.model.boosters.alwaysOn = True
        self.model.boosters.display = True
        uicore.animations.MorphScalar(self.model.boosters, 'alwaysOnIntensity', self.model.boosters.alwaysOnIntensity, 0.0, duration=0.3 * duration, timeOffset=0.5 * duration)

    def AnimateShipEntry(self, model, typeID, duration = 5.0):
        self.PlaceShip(model, typeID)
        dist = duration * 250
        self.startPos = geo2.Vec3Add(self.endPos, (0, 0, dist))
        cs = uicore.animations.MorphVector3(model.translationCurve, 'value', self.startPos, self.endPos, duration=duration, callback=self.OnAnimShipEntryEnd)
        cs.curves[0].startTangent = geo2.Vec3Subtract(self.endPos, self.startPos)
        self.AnimModelBoosters(duration)

    def GetBoundingBoxYBottom(self, model):
        localBB = model.GetLocalBoundingBox()
        boundingBoxYBottom = localBB[0][1]
        return boundingBoxYBottom

    def GetAnimEndPosition(self):
        return self.endPos

    def GetAnimStartPosition(self):
        return self.startPos

    def OnAnimShipEntryEnd(self):
        blue.synchro.SleepWallclock(1000)
        center = self.model.boundingSphereCenter
        initialPos = (-center[0], 0.0, -center[2])
        yDelta = min(BaseHangarShipBehaviour.MIN_SHIP_BOBBING_HALF_DISTANCE, self.model.boundingSphereRadius * 0.05)
        delta = (0.0, yDelta, 0.0)
        bobTime = max(BaseHangarShipBehaviour.MIN_SHIP_BOBBING_TIME, self.model.boundingSphereRadius)
        bobTime = min(bobTime, BaseHangarShipBehaviour.MAX_SHIP_BOBBING_TIME)
        self.ApplyShipBobbing(self.model, initialPos, delta, bobTime)


class DefaultHangarTrafficBehaviour(BaseHangarTrafficBehaviour):

    def __init__(self):
        super(DefaultHangarTrafficBehaviour, self).__init__()
        self.hangarTraffic = hangarUtil.HangarTraffic()

    def Setup(self, scene):
        self.hangarTraffic.SetupScene(scene)

    def CleanUp(self):
        if self.hangarTraffic:
            self.hangarTraffic.CleanupScene()
        self.hangarTraffic = None
