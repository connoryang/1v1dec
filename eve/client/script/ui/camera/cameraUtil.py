#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\camera\cameraUtil.py
import math
from evecamera import LOOKATRANGE_MAX, LOOKATRANGE_MAX_NEW
from evegraphics import settings as gfxsettings
import geo2
import evespacescene
from logmodule import LogException
import trinity
import blue
import destiny
from evecamera.utils import GetARZoomMultiplier
import uthread
FOV_MIN = 0.55
FOV_MAX = 1.1

def IsBobbingEnabled():
    return gfxsettings.Get(gfxsettings.UI_CAMERA_BOBBING_ENABLED)


def GetCameraMaxLookAtRange():
    return LOOKATRANGE_MAX_NEW


def GetPanVectorForZoomToCursor(fov):
    th = math.radians(90 * fov / 2.0)
    dist = uicore.desktop.width / (2.0 * math.tan(th))
    x = -(uicore.uilib.x - uicore.desktop.width / 2)
    y = uicore.uilib.y - uicore.desktop.height / 2
    return geo2.Vec3Normalize((x, y, dist))


def SetShipDirection(camera):
    scene = sm.GetService('sceneManager').GetRegisteredScene('default')
    proj = camera.projectionMatrix.transform
    view = camera.viewMatrix.transform
    pickDir = scene.PickInfinity(uicore.ScaleDpi(uicore.uilib.x), uicore.ScaleDpi(uicore.uilib.y), proj, view)
    if pickDir:
        bp = sm.GetService('michelle').GetRemotePark()
        if bp is not None:
            try:
                bp.CmdGotoDirection(pickDir[0], pickDir[1], pickDir[2])
                sm.ScatterEvent('OnClientEvent_MoveWithDoubleClick')
                sm.GetService('menu').ClearAlignTargets()
                sm.GetService('flightPredictionSvc').GotoDirection(pickDir)
            except RuntimeError as e:
                if e.args[0] != 'MonikerSessionCheckFailure':
                    raise e


def GetZoomDz():
    dz = CheckInvertZoom(uicore.uilib.dz)
    return GetPowerOfWithSign(dz)


def CheckInvertZoom(dz):
    if gfxsettings.Get(gfxsettings.UI_INVERT_CAMERA_ZOOM):
        return -dz
    return dz


def GetPowerOfWithSign(value, power = 1.1):
    return math.copysign(math.fabs(value) ** power, value)


def GetCameraInertiaMultiplier():
    multiplier = gfxsettings.Get(gfxsettings.UI_CAMERA_INERTIA)
    if multiplier < 0:
        return 1.0 / (1.0 - multiplier)
    else:
        return 1.0 + multiplier


def GetDurationByDistance(pos0, pos1, minTime = 0.3, maxTime = 1.0):
    dist = geo2.Vec3Distance(pos0, pos1)
    duration = max(minTime, min(minTime + (maxTime - minTime) * dist / 100000.0, maxTime))
    return duration


def GetBallRadius(ball):
    model = GetBallModel(ball)
    if model and model.__bluetype__ in evespacescene.EVESPACE_TRINITY_CLASSES:
        rad = model.GetBoundingSphereRadius()
    elif model and len(getattr(model, 'children', [])) > 0:
        rad = model.children[0].GetBoundingSphereRadius()
    else:
        rad = None
    if rad is None or rad <= 0.0:
        rad = ball.radius * 1.1
    return rad


def GetBallModel(ball):
    return getattr(ball, 'model', None)


def GetBallPosition(ball):
    if getattr(ball, 'model', None) and not isinstance(ball.model, trinity.EvePlanet):
        elpc = trinity.EveLocalPositionCurve()
        elpc.parent = ball.model
        elpc.behavior = trinity.EveLocalPositionBehavior.centerBounds
        vec = elpc.GetVectorAt(blue.os.GetSimTime())
    else:
        vec = ball.GetVectorAt(blue.os.GetSimTime())
    return (vec.x, vec.y, vec.z)


def GetSpeedDirection(ball):
    if getattr(ball, 'model', None) and hasattr(ball.model.rotationCurve, 'value'):
        quat = ball.model.rotationCurve.value
    else:
        quat = ball.GetQuaternionAt(blue.os.GetSimTime())
        quat = (quat.x,
         quat.y,
         quat.z,
         quat.w)
    return geo2.QuaternionTransformVector(quat, (0, 0, 1))


def GetBall(itemID):
    bp = sm.GetService('michelle').GetBallpark()
    if not bp:
        return None
    return bp.GetBall(itemID)


def GetBallWaitForModel(ballID):
    ball = None
    while ball is None:
        ball = GetBall(ballID)
        blue.synchro.Yield()

    while not getattr(ball, 'model', None):
        blue.synchro.Yield()

    blue.synchro.Yield()
    return ball


def GetBallMaxZoom(ball, nearClip):
    rad = GetBallRadius(ball)
    zoomMultiplier = 1.5 * GetARZoomMultiplier(trinity.GetAspectRatio())
    return (rad + nearClip) * zoomMultiplier + 2


def IsBallWarping(itemID):
    ball = GetBall(itemID)
    if not ball:
        return False
    return ball.mode == destiny.DSTBALL_WARP


def IsAutoTrackingEnabled():
    return settings.char.ui.Get('orbitCameraAutoTracking', False)


def IsDynamicCameraMovementEnabled():
    return gfxsettings.Get(gfxsettings.UI_CAMERA_DYNAMIC_CAMERA_MOVEMENT)


def CheckShowModelTurrets(ball):
    if hasattr(ball, 'LookAtMe'):
        uthread.new(ball.LookAtMe)


def IsNanVector3(values):
    for value in values:
        if math.isnan(value):
            return True

    return False


def IsInfVector3(values):
    for value in values:
        if value > math.fabs(1e+38):
            return True

    return False


def SolveQuadratic(a, b, c):
    d = math.sqrt(b ** 2 - 4 * a * c)
    x1 = -2 * c / (b + d)
    x2 = -2 * c / (b - d)
    return max(x1, x2)


def GetInitialLookAtDistance(maxZoom, minZoom, objRadius = None):
    kPower = 0.95
    a = 1.0 / minZoom ** kPower
    b = FOV_MIN / 2.0
    r = objRadius or maxZoom
    r = max(objRadius, maxZoom)
    c = -r
    radius = SolveQuadratic(a, b, c)
    return radius


class Vector3Chaser(object):

    def __init__(self, speed = 1.0):
        self._value = (0, 0, 0)
        self._targetValue = None
        self._speed = speed
        self._updateTime = None

    def GetValue(self):
        if self._updateTime != blue.os.GetTime():
            self.Update()
        return self._value

    def SetTargetValue(self, value, speed = None):
        if IsNanVector3(value):
            LogException('Camera: Attempting to set an invalid value: %s' % repr(value))
            return
        self._targetValue = value
        if speed is not None:
            self._speed = speed

    def Update(self):
        self._updateTime = blue.os.GetTime()
        if not self._targetValue or self._targetValue == self._value:
            return
        if self._speed == 0.0:
            return
        dt = 1.0 / blue.os.fps
        diff = geo2.Vec3Subtract(self._targetValue, self._value)
        prop = dt * (1.0 * self._speed)
        prop = min(1.0, prop)
        dV = geo2.Vec3Scale(diff, prop)
        self._value = geo2.Vec3Add(self._value, dV)
        if prop == 1.0:
            self._targetValue = None

    def ResetValue(self, speed = None):
        self.SetTargetValue((0, 0, 0), speed)


class VectorLerper(object):

    def __init__(self, duration = 1.0):
        self.duration = duration
        self._v0 = (0, 0, 0)
        self._v1 = (0, 0, 0)
        self.Reset()

    def Reset(self, duration = None):
        if duration:
            self.duration = duration
        self.startTime = blue.os.GetSimTime()

    def SetStartValue(self, value):
        self._v0 = value

    def GetValue(self, v0 = None, v1 = None):
        if v0 is None:
            v0 = self._v0
        t = self.GetTime()
        if self._IsTimePastDuration(t):
            self._v1 = v1
        elif hasattr(v0, '__iter__'):
            self._v1 = geo2.Lerp(v0, v1, t / self.duration)
        else:
            self._v1 = v0 + (v1 - v0) * t
        return self._v1

    def GetLastValue(self):
        return self._v1

    def IsDone(self):
        t = self.GetTime()
        return self._IsTimePastDuration(t)

    def _IsTimePastDuration(self, t):
        return t >= self.duration

    def GetTime(self):
        return (blue.os.GetSimTime() - self.startTime) / float(SEC)


class PositionAnimatorDetached(object):

    def __init__(self, camera):
        self.camera = camera
        self.ball = None
        self.positionDiff = (0, 0, 0)
        self.ballPosLast = None
        self.SetAbstractBall()

    def GetAtPosition(self):
        return geo2.Vec3Add(self.camera._atPosition, self.positionDiff)

    def Update(self):
        if not self.ball:
            return
        ballPos = GetBallPosition(self.ball)
        if self.ballPosLast:
            self.positionDiff = geo2.Vec3SubtractD(ballPos, self.ballPosLast)
        self.ballPosLast = ballPos

    def GetEyePosition(self):
        return geo2.Vec3Add(self.camera._eyePosition, self.positionDiff)

    def _SetBall(self, ball, animate, duration):
        self.positionDiff = (0, 0, 0)
        self.ballPosLast = None
        self.ball = ball
        self.Update()

    def SetAbstractBall(self, animate = True, duration = 0.6):
        bp = self._GetBallpark()
        if not bp:
            return
        pos = bp.GetCurrentEgoPos()
        if self.ball:
            pos = geo2.Vec3AddD(pos, GetBallPosition(self.ball))
        ball = bp.AddClientSideBall(pos)
        self._SetBall(ball, animate, 0.0)

    def _GetBallpark(self):
        michelle = sm.GetServiceIfRunning('michelle')
        if not michelle:
            return None
        return michelle.GetBallpark()

    def IsAttached(self):
        return False

    def GetItemID(self):
        if self.ball:
            return self.ball.id


class PositionAnimatorAttached(object):

    def __init__(self, camera, ball, duration):
        self.camera = camera
        self.ball = ball
        self.atPosition = camera._atPosition
        self.atPositionDiff = (0, 0, 0)
        self.SetBall(ball, duration)

    def GetAtPosition(self):
        return self.atPosition

    def Update(self):
        if not self.ball:
            return (0, 0, 0)
        atPosLast = self.atPosition
        if self.GetItemID() == self.camera.ego:
            self.atPosition = (0, 0, 0)
        else:
            self.atPosition = GetBallPosition(self.ball)
        self.atPositionDiff = geo2.Vec3SubtractD(self.atPosition, atPosLast)

    def GetEyePosition(self):
        ret = self.camera._eyePosition
        if self.GetItemID() != session.shipid:
            ret = geo2.Vec3AddD(ret, self.atPositionDiff)
        return ret

    def SetBall(self, ball, duration = 0.6):
        self._SetBall(ball, duration)

    def _SetBall(self, ball, duration):
        self.ball = ball

    def GetItemID(self):
        if self.ball:
            return self.ball.id

    def IsAttached(self):
        return True
