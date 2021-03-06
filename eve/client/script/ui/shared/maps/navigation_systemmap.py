#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\maps\navigation_systemmap.py
from eve.client.script.ui.inflight.scanner import Scanner
import evecamera
import trinity
import uthread
import uix
import uiutil
import blue
import geo2
import maputils
import uicls
from collections import namedtuple
import carbonui.const as uiconst
import log
from mapcommon import SYSTEMMAP_SCALE
X_AXIS = geo2.Vector(1.0, 0.0, 0.0)
Y_AXIS = geo2.Vector(0.0, 1.0, 0.0)
Z_AXIS = geo2.Vector(0.0, 0.0, 1.0)
WorldToScreenParameters = namedtuple('WorldToScreenParameters', 'viewport projectionTransform viewTransform')

def GetRayAndPointFromScreen(x, y):
    proj, view, vp = uix.GetFullscreenProjectionViewAndViewport()
    ray, start = trinity.device.GetPickRayFromViewport(x, y, vp, view.transform, proj.transform)
    ray = geo2.Vector(*ray)
    start = geo2.Vector(*start)
    return (ray, start)


def GetWorldToScreenParameters():
    dev = trinity.device
    vp = dev.viewport
    viewport = (vp.x,
     vp.y,
     vp.width,
     vp.height,
     vp.minZ,
     vp.maxZ)
    camera = sm.GetService('sceneManager').GetRegisteredCamera(evecamera.CAM_SYSTEMMAP)
    viewTransform = camera.viewMatrix.transform
    return WorldToScreenParameters(viewport, camera.projectionMatrix.transform, viewTransform)


def ProjectTransform(projectionParameters, worldTransform):
    return geo2.Vec3Project(worldTransform[3][:3], projectionParameters.viewport, projectionParameters.projectionTransform, projectionParameters.viewTransform, worldTransform)


def RayToPlaneIntersection(P, d, Q, n):
    denom = geo2.Vec3Dot(n, d)
    if abs(denom) < 1e-05:
        return P
    else:
        distance = -geo2.Vec3Dot(Q, n)
        t = -(geo2.Vec3Dot(n, P) + distance) / denom
        scaledRay = geo2.Vector(*d) * t
        P += scaledRay
        return P


class SystemMapLayer(uicls.LayerCore):
    __guid__ = 'uicls.SystemMapLayer'
    __update_on_reload__ = 0
    default_align = uiconst.TOALL
    default_cursor = uiconst.UICURSOR_SELECTDOWN
    activeManipAxis = None
    _isPicked = False

    def Startup(self):
        self.sr.movingProbe = None
        self.sr.rangeProbe = None
        sm.RegisterNotify(self)

    def SetInterest(self, itemID, interpolate = True):
        solarsystem = sm.GetService('systemmap').GetCurrentSolarSystem()
        if solarsystem is None:
            log.LogTrace('No solar system (SystemmapNav::SetInterest)')
            return
        endPos = None
        for tf in solarsystem.children:
            tfName = getattr(tf, 'name', None)
            if tfName is None:
                continue
            if tfName.startswith('systemParent_'):
                for stf in tf.children:
                    stfName = getattr(stf, 'name', None)
                    if stfName is None:
                        continue
                    try:
                        prefix, stfItemID = stfName.split('_')
                        if prefix == 'scanResult':
                            stfItemID = ('result', stfItemID)
                        else:
                            stfItemID = int(stfItemID)
                    except:
                        continue

                    if stfItemID == itemID:
                        endPos = stf.worldTransform[3][:3]
                        break

                if endPos:
                    break
            elif tfName.startswith('bm_') and isinstance(itemID, tuple) and itemID[0] == 'bookmark':
                tfItemID = int(tfName.split('_')[1])
                if tfItemID == itemID[1]:
                    endPos = tf.worldTransform[3][:3]
                    break
            elif tfName.endswith(str(itemID)):
                endPos = tf.worldTransform[3][:3]
                break

        if endPos is None and itemID == eve.session.shipid:
            endPos = maputils.GetMyPos()
            endPos.Scale(SYSTEMMAP_SCALE)
            endPos = (endPos.x, endPos.y, endPos.z)
        self.FocusOnTrinityPoint(endPos, interpolate=interpolate)

    def FocusOnPoint(self, endPos):
        scaledEndPos = geo2.Vec3Scale(endPos, SYSTEMMAP_SCALE)
        self.FocusOnTrinityPoint(scaledEndPos)

    def FocusOnTrinityPoint(self, triVector, interpolate = True):
        if triVector and interpolate:
            now = blue.os.GetSimTime()
            cameraParent = self.GetCameraParent()
            if cameraParent.translationCurve:
                startPos = cameraParent.translationCurve.GetVectorAt(now)
                startPos = (startPos.x, startPos.y, startPos.z)
            else:
                startPos = cameraParent.translation
            nullV = (0, 0, 0)
            vc = trinity.TriVectorCurve()
            vc.extrapolation = trinity.TRIEXT_CONSTANT
            vc.AddKey(0.0, startPos, nullV, nullV, trinity.TRIINT_HERMITE)
            vc.AddKey(0.5, triVector, nullV, nullV, trinity.TRIINT_HERMITE)
            vc.Sort()
            cameraParent.translationCurve = vc
            cameraParent.useCurves = 1
            vc.start = now
        elif triVector:
            cameraParent = self.GetCameraParent()
            cameraParent.translationCurve = None
            cameraParent.translation = triVector

    def GetCameraParent(self):
        camera = sm.GetService('sceneManager').GetRegisteredCamera(evecamera.CAM_SYSTEMMAP)
        return camera.GetCameraParent()

    def OnMouseMove(self, *args):
        self.sr.hint = ''
        lib = uicore.uilib
        alt = lib.Key(uiconst.VK_MENU)
        camera = sm.GetService('sceneManager').GetRegisteredCamera(evecamera.CAM_SYSTEMMAP)
        dx = lib.dx
        dy = lib.dy
        if not lib.leftbtn and not lib.rightbtn and not self.sr.rangeProbe:
            uthread.new(self.TryToHilight)
        if not self._isPicked:
            return
        if lib.leftbtn:
            if self.sr.movingProbe:
                if alt:
                    self.ScaleProbesAroundCenter()
                else:
                    x, y = uicore.ScaleDpi(uicore.uilib.x), uicore.ScaleDpi(uicore.uilib.y)
                    self.MoveActiveProbe(x, y)
                    self.ShowGrid()
                return
            if self.sr.rangeProbe:
                self.ScaleActiveProbe()
                uicore.uilib.SetCursor(uiconst.UICURSOR_DRAGGABLE)
                return
        if lib.leftbtn and not lib.rightbtn:
            fov = camera.fieldOfView
            camera.OrbitParent(-dx * fov * 0.1, dy * fov * 0.1)
            sm.GetService('systemmap').SortBubbles()
        elif lib.rightbtn and not lib.leftbtn:
            cameraParent = self.GetCameraParent()
            if cameraParent.translationCurve:
                pos = cameraParent.translationCurve.GetVectorAt(blue.os.GetSimTime())
                cameraParent.translationCurve = None
                cameraParent.translation = (pos.x, pos.y, pos.z)
            scalefactor = camera.translationFromParent * (camera.fieldOfView * 0.001)
            offset = (dx * scalefactor, -dy * scalefactor, 0.0)
            offset = geo2.QuaternionTransformVector(camera.rotationAroundParent, offset)
            cameraParent.translation = geo2.Vec3Subtract(cameraParent.translation, offset)
        elif lib.leftbtn and lib.rightbtn:
            modifier = uicore.mouseInputHandler.GetCameraZoomModifier()
            camera.Dolly(modifier * -(dy * 0.01) * abs(camera.translationFromParent))
            camera.translationFromParent = camera.CheckTranslationFromParent(camera.translationFromParent)

    def OnDblClick(self, *args):
        picktype, pickobject = self.GetPick()
        if pickobject:
            if pickobject.name.startswith('cursor'):
                cursorName, side, probeID = pickobject.name.split('_')
                sm.GetService('scanSvc').FocusOnProbe(probeID)

    def OnMouseEnter(self, *args):
        if not uicore.cmd.IsUIHidden():
            uicore.layer.main.state = uiconst.UI_PICKCHILDREN

    def OnMouseDown(self, button):
        systemmap = sm.GetService('systemmap')
        self._isPicked = True
        uiutil.SetOrder(self, 0)
        systemmap.CollapseBubbles()
        systemmap.SortBubbles()
        scannerWnd = Scanner.GetIfOpen()
        picktype, pickobject = self.GetPick()
        if uicore.uilib.leftbtn and pickobject:
            if pickobject.name[:6] == 'cursor':
                cursorName, side, probeID = pickobject.name.split('_')
                if probeID:
                    sm.GetService('scanSvc').StartMoveMode()
                    probe = scannerWnd.GetControl(probeID)
                    if probe:
                        cursorAxis = cursorName[6:]
                        x = uicore.ScaleDpi(uicore.uilib.x)
                        y = uicore.ScaleDpi(uicore.uilib.y)
                        self.PickAxis(x, y, probe, cursorAxis.lower())
                        if scannerWnd:
                            scannerWnd.HighlightProbeIntersections()
                        return
        if scannerWnd and button == 0:
            pickedProbeControl = self.TryPickSphereBorder()
            if pickedProbeControl:
                self.sr.rangeProbe = pickedProbeControl
                pickedProbeControl.ShowScanRanges()
                uicore.uilib.SetCursor(uiconst.UICURSOR_DRAGGABLE)
                scannerWnd.StartScaleMode(self.GetDotInCameraAlignedPlaneFromProbe(pickedProbeControl))
            else:
                uicore.uilib.SetCursor(uiconst.UICURSOR_SELECTDOWN)

    def OnMouseUp(self, button):
        if not uicore.cmd.IsUIHidden():
            uicore.layer.main.state = uiconst.UI_PICKCHILDREN
        if not (uicore.uilib.leftbtn or uicore.uilib.rightbtn):
            self._isPicked = False
        if button == 1:
            if uicore.uilib.leftbtn and (self.sr.movingProbe or self.sr.rangeProbe):
                scannerWnd = Scanner.GetIfOpen()
                if scannerWnd:
                    scannerWnd.CancelProbeMoveOrScaling()
                    if self.sr.movingProbe:
                        self.sr.movingProbe.ShowIntersection()
                    self.sr.movingProbe = None
                    self.sr.rangeProbe = None
                    scannerWnd.lastScaleUpdate = None
                    scannerWnd.lastMoveUpdate = None
            uthread.new(self.TryToHilight)
            uiutil.SetOrder(self, -1)
            return
        uiutil.SetOrder(self, -1)
        scannerWnd = Scanner.GetIfOpen()
        if scannerWnd:
            if self.sr.rangeProbe:
                uthread.new(scannerWnd.RegisterProbeRange, self.sr.rangeProbe)
            if self.sr.movingProbe:
                uthread.new(scannerWnd.RegisterProbeMove, self.sr.movingProbe)
            scannerWnd = scannerWnd.StopScaleMode()
        if scannerWnd and self.sr.rangeProbe:
            uthread.new(scannerWnd.RegisterProbeRange, self.sr.rangeProbe)
        if scannerWnd and self.sr.movingProbe:
            uthread.new(scannerWnd.RegisterProbeMove, self.sr.movingProbe)
        self.sr.rangeProbe = None
        if self.sr.movingProbe:
            self.sr.movingProbe.ShowIntersection()
        self.sr.movingProbe = None
        if scannerWnd:
            scannerWnd.HideDistanceRings()
        uthread.new(self.TryToHilight)
        sm.GetService('systemmap').SortBubbles()
        sm.GetService('ui').ForceCursorUpdate()

    def OnMouseWheel(self, *args):
        modifier = uicore.mouseInputHandler.GetCameraZoomModifier()
        self.ZoomBy(modifier * uicore.uilib.dz)
        return 1

    def ZoomBy(self, amount):
        camera = sm.GetService('sceneManager').GetRegisteredCamera(evecamera.CAM_SYSTEMMAP)
        camera.Dolly(amount * 0.001 * abs(camera.translationFromParent))
        camera.translationFromParent = camera.CheckTranslationFromParent(camera.translationFromParent)

    def ScaleProbesAroundCenter(self):
        x, y = uicore.ScaleDpi(uicore.uilib.x), uicore.ScaleDpi(uicore.uilib.y)
        mousePos = geo2.Vector(x, y, 0)
        probeData = sm.GetService('scanSvc').GetProbeData()
        scannerWnd = Scanner.GetIfOpen()
        if scannerWnd is None:
            return
        probes = scannerWnd.GetProbeSpheres()
        centroid = geo2.Vector(0, 0, 0)
        numProbes = 0
        for probeID, probeControl in probes.iteritems():
            if probeID not in probeData or probeData[probeID].state != const.probeStateIdle:
                continue
            probePos = probeControl.GetWorldPosition()
            centroid += probePos
            numProbes += 1

        if numProbes <= 1:
            return
        centroid /= numProbes
        projectionParams = GetWorldToScreenParameters()
        centroidTansform = ((SYSTEMMAP_SCALE,
          0,
          0,
          0),
         (0,
          SYSTEMMAP_SCALE,
          0,
          0),
         (0,
          0,
          SYSTEMMAP_SCALE,
          0),
         (centroid.x,
          centroid.y,
          centroid.z,
          1.0))
        screenCentroid = geo2.Vector(*ProjectTransform(projectionParams, centroidTansform))
        screenCentroid.z = 0
        probeScreenPos = geo2.Vector(*ProjectTransform(projectionParams, self.sr.movingProbe.locator.worldTransform))
        probeScreenPos.z = 0
        centerToProbe = probeScreenPos - screenCentroid
        centerToProbeLength = geo2.Vec2Length(centerToProbe)
        if centerToProbeLength < 0.1:
            return
        centerToProbeNormal = centerToProbe / centerToProbeLength
        toMouseDotProduct = geo2.Vec2Dot(mousePos - screenCentroid, centerToProbeNormal)
        projectedPos = screenCentroid + toMouseDotProduct * centerToProbeNormal
        toProjectedLength = geo2.Vec2Length(projectedPos - screenCentroid)
        if toProjectedLength < 0.1:
            return
        moveScale = toProjectedLength / centerToProbeLength
        if toMouseDotProduct < 0:
            moveScale = -moveScale
        for probeID, probeControl in probes.iteritems():
            if probeID not in probeData or probeData[probeID].state != const.probeStateIdle:
                continue
            pos = probeControl.GetWorldPosition()
            toProbe = pos - centroid
            endPos = centroid + toProbe * moveScale
            endPos = (endPos.x / SYSTEMMAP_SCALE, endPos.y / SYSTEMMAP_SCALE, endPos.z / SYSTEMMAP_SCALE)
            probeControl.SetPosition(endPos)

        scannerWnd.ShowCentroidLines()
        scannerWnd.HighlightProbeIntersections()
        sm.GetService('systemmap').HighlightItemsWithinProbeRange()

    def GetMenu(self, *args):
        picktype, pickobject = self.GetPick()
        if pickobject and pickobject.name[:6] == 'cursor':
            cursorName, side, probeID = pickobject.name.split('_')
            if probeID:
                try:
                    probeID = int(probeID)
                except ValueError:
                    return []

                return sm.StartService('scanSvc').GetProbeMenu(probeID)
        return []

    def GetDotInCameraAlignedPlaneFromProbe(self, probeControl):
        return self.GetDotInCameraAlignedPlaneFromPosition(probeControl.GetWorldPosition())

    def GetDotInCameraAlignedPlaneFromPosition(self, targetPlanePos):
        x, y = uicore.ScaleDpi(uicore.uilib.x), uicore.ScaleDpi(uicore.uilib.y)
        ray, start = GetRayAndPointFromScreen(x, y)
        camera = sm.GetService('sceneManager').GetRegisteredCamera(evecamera.CAM_SYSTEMMAP)
        viewDir = geo2.QuaternionTransformVector(camera.rotationAroundParent, (0.0, 0.0, 1.0))
        viewDir = geo2.Vec3Normalize(viewDir)
        targetPlaneNormal = geo2.Vector(*viewDir)
        pos = RayToPlaneIntersection(start, ray, targetPlanePos, targetPlaneNormal)
        return pos

    def TryToHilight(self):
        if getattr(self, '_tryToHilight_Busy', None):
            self._tryToHilight_Pending = True
            return
        if self.destroyed:
            return
        self._tryToHilight_Busy = True
        picktype, pickobject = self.GetPick()
        if pickobject and hasattr(pickobject, 'name') and pickobject.name[:6] == 'cursor':
            scannerWnd = Scanner.GetIfOpen()
            if scannerWnd:
                scannerWnd.HiliteCursor(pickobject)
            self.HighlightBorderOfProbe()
            if uicore.uilib.mouseOver == self:
                uicore.uilib.SetCursor(uiconst.UICURSOR_SELECTDOWN)
        else:
            scannerWnd = Scanner.GetIfOpen()
            if scannerWnd:
                scannerWnd.HiliteCursor()
            pickedProbeControl = self.TryPickSphereBorder()
            blue.pyos.synchro.SleepWallclock(100)
            if self.destroyed:
                return
            _pickedProbeControl = self.TryPickSphereBorder()
            if _pickedProbeControl and _pickedProbeControl == pickedProbeControl:
                self.HighlightBorderOfProbe(pickedProbeControl)
                uicore.uilib.SetCursor(uiconst.UICURSOR_DRAGGABLE)
            else:
                self.HighlightBorderOfProbe()
                if uicore.uilib.mouseOver == self:
                    uicore.uilib.SetCursor(uiconst.UICURSOR_SELECTDOWN)
        if self.destroyed:
            return
        self._tryToHilight_Busy = False
        if getattr(self, '_tryToHilight_Pending', None):
            self._tryToHilight_Pending = False
            self.TryToHilight()

    def TryPickSphereBorder(self):
        matches = []
        scannerWnd = Scanner.GetIfOpen()
        if scannerWnd:
            x, y = uicore.ScaleDpi(uicore.uilib.x), uicore.ScaleDpi(uicore.uilib.y)
            ray, start = GetRayAndPointFromScreen(x, y)
            pickRadiusRay, pickRadiusStart = GetRayAndPointFromScreen(x - 30, y)
            camera = sm.GetService('sceneManager').GetRegisteredCamera(evecamera.CAM_SYSTEMMAP)
            if camera is None:
                return
            viewDir = geo2.QuaternionTransformVector(camera.rotationAroundParent, (0.0, 0.0, 1.0))
            viewDir = geo2.Vec3Normalize(viewDir)
            targetPlaneNormal = geo2.Vector(*viewDir)
            scanSvc = sm.StartService('scanSvc')
            probeData = scanSvc.GetProbeData()
            probes = scannerWnd.GetProbeSpheres()
            for probeID, probeControl in probes.iteritems():
                if probeID not in probeData or probeData[probeID].state != const.probeStateIdle:
                    continue
                targetPlanePos = geo2.Vector(probeControl.locator.worldTransform[3][0], probeControl.locator.worldTransform[3][1], probeControl.locator.worldTransform[3][2])
                rad = list(probeControl.sphere.scaling)[0] * SYSTEMMAP_SCALE
                pos = RayToPlaneIntersection(start, ray, targetPlanePos, targetPlaneNormal)
                picRadiusPos = RayToPlaneIntersection(pickRadiusStart, pickRadiusRay, targetPlanePos, targetPlaneNormal)
                pickRad = (trinity.TriVector(*picRadiusPos) - trinity.TriVector(*pos)).Length()
                diffFromPickToSphereBorder = (trinity.TriVector(*targetPlanePos) - trinity.TriVector(*pos)).Length()
                if rad + pickRad > diffFromPickToSphereBorder > rad - pickRad:
                    matches.append((abs(rad - diffFromPickToSphereBorder), probeControl))

        if matches:
            matches = uiutil.SortListOfTuples(matches)
            return matches[0]

    def HighlightBorderOfProbe(self, probeControl = None):
        scannerWnd = Scanner.GetIfOpen()
        if scannerWnd:
            probes = scannerWnd.GetProbeSpheres()
            for _probeID, _probeControl in probes.iteritems():
                if probeControl and _probeControl == probeControl:
                    probeControl.HighlightBorder(True)
                else:
                    _probeControl.HighlightBorder(False)

    def _DiffProjectedPoint(self, ray, start):
        self.endPlanePos = RayToPlaneIntersection(start, ray, self.targetPlanePos, self.targetPlaneNormal)
        displacement = self.endPlanePos - self.startPlanePos
        self.startPlanePos = self.endPlanePos
        if self.activeManipAxis in ('xy', 'yz', 'xz'):
            finalDisplacement = displacement
        else:
            if self.activeManipAxis == 'x':
                scaledDir = geo2.Vector(1.0, 0.0, 0.0)
            elif self.activeManipAxis == 'y':
                scaledDir = geo2.Vector(0.0, 1.0, 0.0)
            elif self.activeManipAxis == 'z':
                scaledDir = geo2.Vector(0.0, 0.0, 1.0)
            dot = geo2.Vec3Dot(displacement, scaledDir)
            scaledDir = geo2.Vec3Scale(scaledDir, dot)
            finalDisplacement = scaledDir
        return finalDisplacement

    def GetTranslation(self):
        return geo2.Vector(self.sr.movingProbe.locator.worldTransform[3][0], self.sr.movingProbe.locator.worldTransform[3][1], self.sr.movingProbe.locator.worldTransform[3][2])

    def PickAxis(self, x, y, pickobject, axis):
        ray, start = GetRayAndPointFromScreen(x, y)
        self.sr.movingProbe = pickobject
        self.activeManipAxis = axis
        self.ShowGrid()
        self.targetPlaneNormal = self.GetTargetPlaneNormal(ray)
        self.targetPlanePos = self.GetTranslation()
        if self.targetPlaneNormal and pickobject:
            self.startPlanePos = RayToPlaneIntersection(start, ray, self.targetPlanePos, self.targetPlaneNormal)

    def ScaleActiveProbe(self, *args):
        if self.sr.rangeProbe:
            scannerWnd = Scanner.GetIfOpen()
            if scannerWnd:
                scannerWnd.ScaleProbe(self.sr.rangeProbe, self.GetDotInCameraAlignedPlaneFromProbe(self.sr.rangeProbe))

    def MoveActiveProbe(self, x, y):
        if self.activeManipAxis and self.targetPlaneNormal and self.sr.movingProbe:
            ray, start = GetRayAndPointFromScreen(x, y)
            diff = self._DiffProjectedPoint(ray, start)
            scannerWnd = Scanner.GetIfOpen()
            if scannerWnd:
                diff = geo2.Vector(*diff)
                diff *= 1.0 / SYSTEMMAP_SCALE
                scannerWnd.MoveProbe(self.sr.movingProbe, diff)
                scannerWnd.ShowCentroidLines()

    def GetTargetPlaneNormal(self, ray):
        if self.activeManipAxis in ('y',):
            camera = sm.GetService('sceneManager').GetRegisteredCamera(evecamera.CAM_SYSTEMMAP)
            y, p, r = geo2.QuaternionRotationGetYawPitchRoll(camera.rotationAroundParent)
            q = geo2.QuaternionRotationSetYawPitchRoll(y, 0.0, 0.0)
            return geo2.QuaternionTransformVector(q, (0.0, 0.0, 1.0))
        elif self.activeManipAxis in ('x', 'z', 'xz'):
            return Y_AXIS
        elif self.activeManipAxis in ('y', 'xy'):
            return Z_AXIS
        else:
            return X_AXIS

    def _OnClose(self):
        pass

    def ShowGrid(self):
        XZ = bool(self.activeManipAxis == 'xz')
        YZ = bool(self.activeManipAxis == 'yz')
        XY = bool(self.activeManipAxis == 'xy')
        if self.sr.movingProbe and (XZ or YZ or XY):
            scannerWnd = Scanner.GetIfOpen()
            if scannerWnd:
                scannerWnd.ShowDistanceRings(self.sr.movingProbe, self.activeManipAxis)

    def GetPick(self):
        scene = sm.GetService('sceneManager').GetRegisteredScene('systemmap')
        x, y = uicore.ScaleDpi(uicore.uilib.x), uicore.ScaleDpi(uicore.uilib.y)
        if scene:
            projection, view, viewport = uix.GetFullscreenProjectionViewAndViewport()
            pick = scene.PickObject(x, y, projection, view, viewport)
            if pick:
                return ('scene', pick)
        return (None, None)
