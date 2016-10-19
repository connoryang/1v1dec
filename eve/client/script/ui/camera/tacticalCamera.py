#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\camera\tacticalCamera.py
import geo2
from eve.client.script.parklife import states
from eve.client.script.ui.camera.baseSpaceCamera import BaseSpaceCamera
from eve.client.script.ui.camera.cameraUtil import GetDurationByDistance, GetBallPosition, GetBall, GetBallMaxZoom, IsBallWarping, CheckShowModelTurrets, VectorLerper, GetCameraInertiaMultiplier, IsAutoTrackingEnabled, PositionAnimatorDetached, PositionAnimatorAttached
import evecamera
DEFAULT_EYEDIST = 40000
FREE_ORBIT_DIST = 250
LOOKAT_DIST = 50000

class TacticalCamera(BaseSpaceCamera):
    name = 'TacticalCamera'
    __notifyevents__ = BaseSpaceCamera.__notifyevents__ + ['OnStateChange']
    cameraID = evecamera.CAM_TACTICAL
    kPanSpeed = 8.0
    kOrbitSpeed = 5.0
    default_fov = 1.0
    default_atPosition = (0, 0, 0)
    default_eyePosition = (-DEFAULT_EYEDIST, DEFAULT_EYEDIST, DEFAULT_EYEDIST)
    maxFov = 1.0
    minFov = 0.3

    def __init__(self):
        BaseSpaceCamera.__init__(self)
        self.lastLookAtID = None
        self.sceneCursor = (0, 0, 0)
        self.positionAnimator = PositionAnimatorDetached(self)
        self.trackBall = None
        self.trackBallMorpher = VectorLerper()

    def GetLookAtItemID(self):
        if self.IsAttached():
            return self.GetItemID()
        else:
            return None

    def IsAttached(self):
        return self.positionAnimator.IsAttached()

    def LookAt(self, itemID, allowSwitchCamera = True, **kwargs):
        if not self.IsManualControlEnabled():
            return
        if self.CheckObjectTooFar(itemID) and itemID != self.ego:
            self.Track(itemID)
            return
        self.StopTracking()
        if itemID == self.GetItemID():
            self.ResetFOV()
            if itemID != self.ego:
                self.LookAt(self.ego)
            return
        sm.ScatterEvent('OnCameraLookAt', itemID == self.ego, itemID)
        self.StopUpdateThreads()
        self.ResetFOV()
        ball = GetBall(itemID)
        if not ball:
            return
        CheckShowModelTurrets(ball)
        duration = self.AnimateLookAt(ball)
        self._SetLookAtBall(ball, duration=duration)

    def AnimateLookAt(self, ball):
        eyePos1 = self.GetLookAtEyePos(ball)
        duration = self.AnimLookAtTransit(ball, eyePos1)
        return duration

    def AnimLookAtTransit(self, ball, eyePos1):
        ballPos = GetBallPosition(ball)
        self.SetAppropriateAtPositionForRotation(ballPos)
        duration = GetDurationByDistance(self.positionAnimator.GetAtPosition(), ballPos, minTime=0.3, maxTime=0.6)
        self.TransitTo(ballPos, eyePos1, duration=duration, smoothing=0.0)
        return duration

    def GetLookAtEyePos(self, ball):
        distance = self.GetLookAtDistance(ball)
        lookVec = geo2.Vec3Scale(self.GetLookAtDirection(), distance)
        eyePos1 = geo2.Vec3Add(GetBallPosition(ball), lookVec)
        return eyePos1

    def GetLookAtDistance(self, ball):
        if self.IsAttached():
            distance = self.GetZoomDistance()
        else:
            distance = geo2.Vec3Distance(self.eyePosition, GetBallPosition(ball))
        maxZoom = GetBallMaxZoom(ball, self.nearClip)
        minZoom = evecamera.LOOKATRANGE_MAX_NEW
        distance = max(maxZoom, min(distance, minZoom))
        return distance

    def _SetLookAtBall(self, ball, duration = 0.6):
        if ball:
            self.positionAnimator = PositionAnimatorAttached(self, ball, duration)
            self.UpdateMaxZoom()
            self.lastLookAtID = ball.id
        else:
            self.positionAnimator = PositionAnimatorDetached(self)

    def OnDeactivated(self):
        BaseSpaceCamera.OnDeactivated(self)
        self._SetLookAtBall(None)
        self.StopTracking()

    def UpdateMaxZoom(self):
        ball = self.GetZoomToBall()
        if ball:
            self.SetMaxZoom(GetBallMaxZoom(ball, self.nearClip))

    def GetZoomToBall(self):
        if self.trackBall:
            return self.trackBall
        if self.positionAnimator.ball:
            return self.positionAnimator.ball

    def Pan(self, dx = None, dy = None, dz = None):
        if not self.IsManualControlEnabled():
            return
        if self.IsActiveOrTrackingShipWarping():
            return
        self.StopTracking()
        if self.IsAttached():
            self.Detach()
        k = self.GetPanSpeed()
        BaseSpaceCamera.Pan(self, k * dx, k * dy, k * dz)

    def StopTracking(self):
        self.Track(None)

    def IsTracking(self):
        return self.trackBall is not None

    def GetPanSpeed(self):
        return 0.01 + 0.001 * self.GetDistanceToCursor() ** 0.9

    def Detach(self):
        if self.IsActiveOrTrackingShipWarping():
            return
        self.StopUpdateThreads()
        self.positionAnimator = PositionAnimatorDetached(self)
        if self.lastLookAtID:
            self.lastLookAtID = None
            self.sceneCursor = self.atPosition
        self.SetAtPosToFixedDistance()
        sm.ScatterEvent('OnCameraLookAt', False, None)

    def SetAtPosToFixedDistance(self):
        self.SetAtPosition(geo2.Vec3AddD(self._eyePosition, geo2.Vec3Scale(self.GetLookAtDirectionWithOffset(), -100.0)))

    def GetDistanceToCursor(self):
        return geo2.Vec3Distance(self.eyePosition, self.sceneCursor)

    def ResetCamera(self, *args):
        self.LookAt(self.ego)

    def OnActivated(self, lastCamera = None, itemID = None, duration = None, **kwargs):
        settings.char.ui.Set('spaceCameraID', evecamera.CAM_TACTICAL)
        if lastCamera:
            distance = max(self.maxZoom, min(geo2.Vec3Length(self.eyePosition), self.minZoom))
            if lastCamera.cameraID in (evecamera.CAM_SHIPORBIT, evecamera.CAM_UNDOCK, evecamera.CAM_ENTERSPACE):
                self._ResetEyeAndAtPosition(lastCamera.eyePosition, lastCamera.atPosition, distance)
            else:
                animate = lastCamera.cameraID not in (evecamera.CAM_SHIPPOV, evecamera.CAM_HANGAR)
                self._ResetEyeAndAtPosition(self.eyePosition, self.atPosition, distance, animate)
            self._SetLookAtBall(GetBall(lastCamera.GetItemID()))
            if lastCamera.cameraID != evecamera.CAM_SHIPPOV:
                self.fov = lastCamera.fov
            self.ResetFOV()
        else:
            if not itemID:
                itemID = self.ego
            self._SetLookAtBall(GetBall(itemID))
            self.SetEyePosition(self.default_eyePosition)
        BaseSpaceCamera.OnActivated(self, **kwargs)

    def _GetNewDirection(self, direction):
        y = geo2.Vec2Length((direction[0], direction[2]))
        direction = (direction[0], y, direction[2])
        direction = geo2.Vec3Normalize(direction)
        return direction

    def _ResetEyeAndAtPosition(self, eyePos0, atPos0, distance = LOOKAT_DIST, animate = True, duration = None):
        direction = self._GetNewDirection(geo2.Vec3Subtract(eyePos0, atPos0))
        eyePos1 = geo2.Vec3Add(atPos0, geo2.Vec3Scale(direction, distance))
        if animate:
            if duration is None:
                duration = GetDurationByDistance(eyePos0, eyePos1, 0.4, 0.6)
            atPos1 = atPos0
            diff = geo2.Vec3Scale(geo2.Vec3Direction(atPos0, eyePos0), distance / 5)
            atPos0 = geo2.Vec3Add(atPos0, diff)
            self.Transit(atPos0, eyePos0, atPos1, eyePos1, duration=duration, callback=self.EnableManualControl)
        else:
            self.SetAtPosition(atPos0)
            self.SetEyePosition(eyePos1)

    def Update(self):
        BaseSpaceCamera.Update(self)
        if not session.solarsystemid:
            return
        if self.IsActiveOrTrackingShipWarping() and not self.IsAttached():
            self.LookAt(self.ego)
        if self.positionAnimator.GetItemID():
            self.positionAnimator.Update()
            if self.IsTracking():
                atPos = self.GetTrackingAtPosition()
            else:
                atPos = self.positionAnimator.GetAtPosition()
            self.SetAtPosition(atPos)
            self.SetEyePosition(self.positionAnimator.GetEyePosition())
        if self.IsAttached():
            self._EnforceMaximumDistanceAttached()
        else:
            self._EnforceMaximumDistanceDetached()

    def _EnforceMaximumDistanceAttached(self):
        dist = geo2.Vec3Length(self.positionAnimator.GetAtPosition())
        if dist > evecamera.LOOKATRANGE_MAX_NEW and not self.IsInTransit():
            self.LookAt(self.ego)

    def GetTrackingAtPosition(self):
        ballPos = GetBallPosition(self.trackBall)
        if geo2.Vec3Length(ballPos) > evecamera.LOOKATRANGE_MAX_NEW:
            direction = geo2.Vec3Normalize(geo2.Vec3Subtract(ballPos, self.eyePosition))
            ballPos = geo2.Vec3Add(self.eyePosition, geo2.Vec3Scale(direction, evecamera.LOOKATRANGE_MAX_NEW))
        return self.trackBallMorpher.GetValue(self.atPosition, ballPos)

    def IsActiveOrTrackingShipWarping(self):
        return IsBallWarping(self.GetItemID()) or IsBallWarping(self.ego)

    def GetItemID(self):
        return self.positionAnimator.GetItemID()

    def _EnforceMaximumDistanceDetached(self):
        dist = geo2.Vec3Length(self.eyePosition)
        if dist > evecamera.LOOKATRANGE_MAX_NEW and not self.IsInTransit():
            direction = geo2.Vec3Normalize(self.eyePosition)
            newEye = geo2.Vec3Scale(direction, evecamera.LOOKATRANGE_MAX_NEW)
            diff = geo2.Vec3Subtract(self.eyePosition, newEye)
            self.SetEyePosition(newEye)
            self.SetAtPosition(geo2.Vec3Subtract(self._atPosition, diff))

    def OnCurrentShipWarping(self):
        if self.isActive:
            self.LookAt(self.ego)

    def Track(self, itemID = None):
        if itemID is None and not self.trackBall:
            return
        ball = GetBall(itemID)
        if ball and ball not in (self.positionAnimator.ball, self.trackBall):
            self._TrackItem(ball)
        else:
            self._TrackNothing()
        self.UpdateMaxZoom()

    def _TrackNothing(self):
        self.trackBall = None

    def _TrackItem(self, ball):
        self.trackBallMorpher.Reset(3.0 / GetCameraInertiaMultiplier())
        ballPos = GetBallPosition(ball)
        self.StopUpdateThreads()
        self.SetAppropriateAtPositionForRotation(ballPos)
        self.trackBall = ball

    def SetAppropriateAtPositionForRotation(self, atPos):
        distanceToNewAtPos = geo2.Vec3Distance(self.eyePosition, atPos)
        distanceToNewAtPos = min(evecamera.LOOKATRANGE_MAX_NEW, distanceToNewAtPos)
        lookVec = geo2.Vec3Scale(self.GetLookAtDirection(), distanceToNewAtPos)
        newAtPos = geo2.Vec3Subtract(self.eyePosition, lookVec)
        if newAtPos != self._eyePosition:
            self.SetAtPosition(newAtPos)

    def OnBallRemoved(self, ball):
        if self.positionAnimator and ball == self.positionAnimator.ball:
            self.Detach()
        if ball == self.trackBall:
            self.StopTracking()

    def OnStateChange(self, itemID, flag, flagState, *args):
        if not self.isActive:
            return
        if flagState and flag == states.selected and IsAutoTrackingEnabled():
            if not uicore.cmd.IsSomeCombatCommandLoaded():
                self.Track(itemID)

    def Orbit(self, *args):
        if self.IsTracking() and self.IsBeyondZoomDistance():
            self.StopTracking()
            self.AnimLookAtTransit(self.positionAnimator.ball, self.eyePosition)
        else:
            BaseSpaceCamera.Orbit(self, *args)

    def IsBeyondZoomDistance(self):
        return self.GetZoomDistance() > self.minZoom

    def Zoom(self, dz):
        if self.IsTracking() and self.CheckObjectTooFar(self.trackBall.id):
            return
        BaseSpaceCamera.Zoom(self, dz)
