#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\camera\enterSpaceCamera.py
import math
from eve.client.script.ui.camera.baseSpaceCamera import BaseSpaceCamera
from eve.client.script.ui.camera.cameraUtil import GetSpeedDirection, GetBall, GetBallPosition, GetBallMaxZoom, GetBallRadius, GetInitialLookAtDistance, GetBallWaitForModel, IsDynamicCameraMovementEnabled
from eve.client.script.ui.view.viewStateConst import ViewState
import evecamera
import uthread
import blue
import geo2

class EnterSpaceCamera(BaseSpaceCamera):
    cameraID = evecamera.CAM_ENTERSPACE
    name = 'EnterSpaceCamera'
    __notifyevents__ = BaseSpaceCamera.__notifyevents__ + ['OnCurrSessionSpaceEnteredFirstTime']

    def __init__(self):
        BaseSpaceCamera.__init__(self)
        self.animEntryThread = None

    def Update(self):
        BaseSpaceCamera.Update(self)
        if IsDynamicCameraMovementEnabled():
            self.SetFovTarget(self.GetDynamicFov())
        ball = GetBall(self.ego)
        if ball:
            self.SetAtPosition(GetBallPosition(ball))

    def StartAnimation(self):
        self.animEntryThread = uthread.new(self._OnActivated)

    def _OnActivated(self):
        duration = 15.0
        ball = GetBallWaitForModel(self.ego)
        self.SetEyePosition(geo2.Vec3Scale(GetSpeedDirection(ball), 2 * GetBallRadius(ball)))
        self.SetMaxZoom(GetBallMaxZoom(ball, self.nearClip))
        uicore.animations.MorphScalar(self, 'yaw', self.yaw, self.yaw + math.pi / 20, duration=duration)
        uicore.animations.MorphScalar(self, 'pitch', self.pitch, self.pitch + math.pi / 40, duration=duration)
        dist = GetInitialLookAtDistance(self.maxZoom, self.minZoom)
        zoom0 = self.GetZoomProportionByZoomDistance(5 * dist)
        zoom1 = self.GetZoomProportionByZoomDistance(dist)
        uicore.animations.MorphScalar(self, 'zoom', zoom0, zoom1, duration=duration * 0.8)
        blue.synchro.SleepWallclock(duration * 1000)
        uthread.new(self.SwitchToPrimaryCamera)

    def GetMinZoomProp(self):
        return self.maxZoom / self.minZoom

    def SwitchToPrimaryCamera(self):
        sm.GetService('viewState').GetView(ViewState.Space).ActivatePrimaryCamera()

    def OnDeactivated(self):
        BaseSpaceCamera.OnDeactivated(self)
        uicore.animations.StopAllAnimations(self)
        if self.animEntryThread:
            self.animEntryThread.kill()
            self.animEntryThread = None

    def OnCurrSessionSpaceEnteredFirstTime(self):
        if self.isActive:
            self.StartAnimation()

    def Track(self, itemID):
        self.SwitchToPrimaryCamera()
