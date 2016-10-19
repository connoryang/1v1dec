#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\camera\undockCamera.py
import math
from eve.client.script.ui.camera.baseSpaceCamera import BaseSpaceCamera
from eve.client.script.ui.camera.cameraUtil import GetSpeedDirection, GetBall, GetBallPosition, GetBallMaxZoom, GetBallRadius, GetBallWaitForModel, IsDynamicCameraMovementEnabled
from eve.client.script.ui.view.viewStateConst import ViewState
import evecamera
import uthread
import blue
import geo2

class UndockCamera(BaseSpaceCamera):
    cameraID = evecamera.CAM_UNDOCK
    name = 'UndockCamera'

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

    def OnActivated(self, **kwargs):
        BaseSpaceCamera.OnActivated(self, **kwargs)
        self.animEntryThread = uthread.new(self._OnActivated)

    def _OnActivated(self):
        duration = 30.0
        ball = GetBallWaitForModel(self.ego)
        self.SetEyePosition(geo2.Vec3Scale(GetSpeedDirection(ball), 2 * GetBallRadius(ball)))
        self.SetMaxZoom(GetBallMaxZoom(ball, self.nearClip))
        self.pitch -= math.pi / 40
        uicore.animations.MorphScalar(self, 'yaw', self.yaw, self.yaw + math.pi / 3, duration=duration)
        uicore.animations.MorphScalar(self, 'pitch', self.pitch, self.pitch - math.pi / 10, duration=duration)
        zoom0 = 0.48
        zoom1 = 0.65
        self.SetZoom(zoom0)
        uicore.animations.MorphScalar(self, 'zoom', zoom0, zoom1, duration=duration * 0.8)
        blue.synchro.SleepWallclock(duration * 1000 + 500)
        uthread.new(self.SwitchToPrimaryCamera)

    def SwitchToPrimaryCamera(self):
        sm.GetService('viewState').GetView(ViewState.Space).ActivatePrimaryCamera()

    def OnDeactivated(self):
        BaseSpaceCamera.OnDeactivated(self)
        uicore.animations.StopAllAnimations(self)
        if self.animEntryThread:
            self.animEntryThread.kill()
            self.animEntryThread = None

    def Track(self, itemID):
        self.SwitchToPrimaryCamera()

    def LookAt(self, itemID, **kwargs):
        self.SwitchToPrimaryCamera()

    def LookAtMaintainDistance(self, itemID):
        pass
