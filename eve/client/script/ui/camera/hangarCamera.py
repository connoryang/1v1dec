#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\camera\hangarCamera.py
import math
from eve.client.script.ui.camera.cameraUtil import GetInitialLookAtDistance
import evecamera
from eve.client.script.ui.camera.baseSpaceCamera import BaseSpaceCamera
import carbonui.const as uiconst
import geo2
hangarMinZoom = 2050.0
hangarMaxZoom = 10.0

class HangarCamera(BaseSpaceCamera):
    cameraID = evecamera.CAM_HANGAR
    isBobbingCamera = False
    name = 'HangarCamera'
    kMaxPitch = math.pi / 2.0 + math.pi / 50.0
    minFov = 0.3
    maxFov = 1.0

    def __init__(self):
        BaseSpaceCamera.__init__(self)
        self.model = None

    def SetShip(self, model, typeID):
        uicore.animations.StopAllAnimations(self)
        self.fov = 1.0
        self.model = model
        self.typeID = typeID
        self.UpdateMinMaxZoom()

    def PlaceShip(self, pos):
        self.atPosition = pos

    def AnimEnterHangar(self, model, startPos, endPos, duration = 5.0):
        self._AnimEnterHangarPitch(duration)
        self._AnimEnterHangarYaw(duration)
        self._AnimEnterHangarZoom(duration, model)
        self._AnimEnterHangarFOV(duration)

    def _AnimEnterHangarFOV(self, duration):
        self.fov = 0.7
        uicore.animations.MorphScalar(self, 'fov', self.fov, self.default_fov, duration=0.45 * duration, timeOffset=0.55 * duration)

    def _AnimEnterHangarZoom(self, duration, model):
        dist = GetInitialLookAtDistance(self.maxZoom, self.minZoom)
        zoom0 = self.GetZoomProportionByZoomDistance(1.2 * dist)
        zoom1 = self.GetZoomProportionByZoomDistance(2.0 * dist)
        self.zoom = zoom0
        self._AnimZoom(duration, zoom0, zoom1)

    def _AnimSwitchShipsZoom(self, duration, model):
        dist = GetInitialLookAtDistance(self.maxZoom, self.minZoom)
        zoom0 = self.GetZoomProportionByZoomDistance(1.0 * dist)
        zoom1 = self.GetZoomProportionByZoomDistance(1.2 * dist)
        self._AnimZoom(duration, zoom0, zoom1)

    def _AnimZoom(self, duration, zoom0, zoom1):
        zoom1 = min(zoom1, 1.0)
        self.zoom = zoom0
        cs = uicore.animations.MorphScalar(self, 'zoom', zoom0, zoom1, duration=duration, curveType=uiconst.ANIM_LINEAR)
        cs.curves[0].startTangent = 0.0

    def UpdateMinMaxZoom(self):
        radius = self.model.boundingSphereRadius
        maxZoom = max(hangarMaxZoom, 1.5 * radius)
        if maxZoom >= hangarMinZoom:
            maxZoom = 0.999 * hangarMinZoom
        minZoom = hangarMinZoom
        self.SetMinMaxZoom(minZoom, maxZoom)
        self.zoom = max(self.GetMinZoomProp(), min(self.zoom, 1.0))

    def _AnimEnterHangarYaw(self, duration):
        yaw0 = 14 * math.pi / 8
        yaw1 = 9 * math.pi / 8
        uicore.animations.MorphScalar(self, 'yaw', yaw0, yaw1, duration=duration, timeOffset=0)

    def _AnimEnterHangarPitch(self, duration):
        pitch0 = 7 * math.pi / 16
        pitch1 = self.kMaxPitch
        uicore.animations.MorphScalar(self, 'pitch', pitch0, pitch1, duration=duration)

    def AnimSwitchShips(self, model, startPos, endPos, duration = 5.0):
        self.atPosition = endPos
        uicore.animations.MorphScalar(self, 'yaw', 0.0, -math.pi / 10, duration=duration)
        uicore.animations.MorphScalar(self, 'pitch', math.pi / 2 + math.pi / 25, self.kMaxPitch, duration=duration)
        self._AnimSwitchShipsZoom(duration, model)
        uicore.animations.MorphScalar(self, 'fov', 0.7, self.default_fov, duration=duration)

    def Orbit(self, *args):
        BaseSpaceCamera.Orbit(self, *args)
        uicore.animations.StopAnimation(self, 'yaw')
        uicore.animations.StopAnimation(self, 'pitch')

    def OnDeactivated(self):
        BaseSpaceCamera.OnDeactivated(self)
        self.model = None

    def Update(self):
        BaseSpaceCamera.Update(self)
        if self.model and self.model.translationCurve:
            atPos = self.model.translationCurve.value
            diff = geo2.Vec3Subtract(atPos, self._atPosition)
            self.atPosition = atPos
            self.eyePosition = geo2.Vec3Add(self.eyePosition, diff)
