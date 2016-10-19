#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\camera\capitalHangarCamera.py
import math
from eve.client.script.ui.camera.baseSpaceCamera import BaseSpaceCamera
import evecamera
import evetypes
from inventorycommon.const import groupSupercarrier
import geo2
TITAN_CAMERA_POSITION = (9995.4853515625, -2001.05224609375, 10192.3359375)
SUPER_CAPITAL_CAMERA_DIRECTION = (-0.2522106051445007, 0.3255149364471436, 0.8546369075775146)

class CapitalHangarCamera(BaseSpaceCamera):
    cameraID = evecamera.CAM_CAPITALHANGAR
    isBobbingCamera = True
    name = 'HangarCamera'
    kMinPitch = math.pi / 4
    kMaxPitch = math.pi / 2

    def AnimEnterHangar(self, model, startPos, endPos, duration = 5.0):
        self._PlaceCamera()

    def AnimSwitchShips(self, model, startPos, endPos, duration = 5.0):
        self._PlaceCamera()

    def SetShip(self, model, typeID):
        self.typeID = typeID
        self.model = model
        self.SetMaxZoom(self.model.GetBoundingSphereRadius() * 1.2)

    def PlaceShip(self, pos):
        self._PlaceCamera(animate=False)

    def _PlaceCamera(self, animate = True):
        duration = 5.0
        if self.IsSuperCarrier():
            self.MoveToSuperCapitalCameraPosition()
            if animate:
                self.AnimEntrySuperCarrier(duration)
        else:
            self.MoveToTitanCameraPosition()
            if animate:
                self.AnimEntryTitan(duration)

    def AnimEntryTitan(self, duration):
        uicore.animations.MorphScalar(self, 'pitch', self.kMaxPitch - math.pi / 15, self.kMaxPitch - math.pi / 20, duration=duration)
        uicore.animations.MorphScalar(self, 'zoom', self.zoom, 0.97 * self.zoom, duration=duration)

    def AnimEntrySuperCarrier(self, duration):
        uicore.animations.MorphScalar(self, 'pitch', self.kMaxPitch - math.pi / 15, self.kMaxPitch - math.pi / 20, duration=duration)
        uicore.animations.MorphScalar(self, 'zoom', self.zoom * 1.03, self.zoom, duration=duration)

    def IsSuperCarrier(self):
        return evetypes.GetGroupID(self.typeID) == groupSupercarrier

    def MoveToTitanCameraPosition(self):
        self.atPosition = self.model.translationCurve.value
        self.eyePosition = TITAN_CAMERA_POSITION
        self.SetMinZoom(geo2.Vec3Distance(self.atPosition, self.eyePosition))

    def MoveToSuperCapitalCameraPosition(self):
        self.atPosition = self.model.translationCurve.value
        optimalZoom = min(self.minZoom, max(self.maxZoom, 2.5 * self.model.GetBoundingSphereRadius()))
        diff = geo2.Vec3Scale(SUPER_CAPITAL_CAMERA_DIRECTION, optimalZoom)
        newEyePos = geo2.Vec3Add(diff, self.atPosition)
        self.eyePosition = newEyePos
        self.SetMinZoom(13000)

    def OnDeactivated(self):
        BaseSpaceCamera.OnDeactivated(self)
        self.model = None

    def Orbit(self, dx, dy):
        BaseSpaceCamera.Orbit(self, 0, dy)
