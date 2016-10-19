#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\structure\deployment\deploymentEntity.py
from carbon.common.script.util.mathUtil import RayToPlaneIntersection
from evegraphics.utils import BuildSOFDNAFromTypeID
from carbonui.uicore import uicorebase as uicore
import evetypes
from signals import Signal
import structures
import trinity
import blue
import geo2
DEPLOY_DIST_MAX = 800000

class StructurePlacementEntity(object):

    def __init__(self, typeID):
        self.typeID = typeID
        self.radius = evetypes.GetRadius(typeID)
        self.movingOffset = None
        self.cameraMatrixes = None
        self._opacity = 0.0
        self.blueprintColor = None
        self.ballpark = sm.GetService('michelle').GetBallpark()
        self.model_valid = self._LoadModel(':variant?placement', display=True)
        self.model_invalid = self._LoadModel(':variant?forbiddenplacement', display=False)
        self.on_location_updated = Signal()
        self.UpdateModel()

    @property
    def model(self):
        if self.model_valid and self.model_valid.display:
            return self.model_valid
        if self.model_invalid and self.model_invalid.display:
            return self.model_invalid

    def IsValidLocation(self):
        ship = self.ballpark.GetBall(session.shipid)
        position = geo2.Vec3AddD((ship.x, ship.y, ship.z), self.GetPosition())
        balls = [ (item.typeID, (ball.x, ball.y, ball.z), ball.radius) for ball, item in self.ballpark.GetBallsAndItems() ]
        balls += [ (item.typeID, xyz, 0) for ball, item, xyz in self.ballpark.GetWarpinPoints() ]
        return structures.IsValidLocation(self.typeID, position, balls)

    def UpdateModel(self):
        isValidLocation = self.IsValidLocation()
        if isValidLocation:
            if not self.model_valid.display:
                self.model_invalid.display = False
                self.model_valid.display = True
                self.model_valid.translationCurve.value = self.model_invalid.translationCurve.value
                self.model_valid.modelRotationCurve.value = self.model_invalid.modelRotationCurve.value
        elif not self.model_invalid.display:
            self.model_valid.display = False
            self.model_invalid.display = True
            self.model_invalid.translationCurve.value = self.model_valid.translationCurve.value
            self.model_invalid.modelRotationCurve.value = self.model_valid.modelRotationCurve.value
        self.on_location_updated(isValidLocation)

    def GetCurrShipPosition(self):
        ball = self.ballpark.GetBall(session.shipid)
        pos = ball.GetVectorAt(blue.os.GetSimTime())
        pos = (pos.x, 0, pos.z)
        camOffset = self.GetCamera().eyePosition
        camOffset = (camOffset[0], 0.0, camOffset[2])
        camDist = geo2.Vec3Length(camOffset)
        return geo2.Vec3Subtract(pos, geo2.Vec3Scale(camOffset, (structures.GetDeploymentDistance(const.typeCapsule) + self.radius) / camDist))

    def _LoadModel(self, variant, display):
        scene = sm.GetService('sceneManager').GetRegisteredScene('default')
        if scene is None:
            return
        sof = sm.GetService('sofService').spaceObjectFactory
        model = sof.BuildFromDNA(BuildSOFDNAFromTypeID(self.typeID) + variant)
        model.modelRotationCurve = trinity.TriRotationCurve()
        model.translationCurve = trinity.TriVectorCurve()
        model.name = 'StructurePlacement'
        model.translationCurve.value = self.GetCurrShipPosition()
        model.display = display
        scene.objects.append(model)
        return model

    def Close(self):
        scene = sm.GetService('sceneManager').GetRegisteredScene('default')
        if scene:
            if self.model_valid:
                scene.objects.fremove(self.model_valid)
            if self.model_invalid:
                scene.objects.fremove(self.model_invalid)

    def UpdateModelPosition(self, pos):
        self.UpdateModel()
        if self.model:
            pos = geo2.Vec3Add(pos, self.movingOffset)
            pos = self.EnforcePositionRestrictions(pos)
            if pos:
                self.model.translationCurve.value = pos

    def GetPosition(self):
        return self.model.translationCurve.value

    def GetRotation(self):
        return geo2.QuaternionRotationGetYawPitchRoll(self.model.modelRotationCurve.value)

    def EnforcePositionRestrictions(self, pos):
        vecLen = geo2.Vec3Length(pos)
        if vecLen > DEPLOY_DIST_MAX:
            return geo2.Vec3Scale(pos, DEPLOY_DIST_MAX / vecLen)
        else:
            return pos

    def UpdateModelRotation(self, dx):
        if self.model:
            rotation = geo2.QuaternionRotationAxis((0, 1.0, 0), dx)
            self.model.modelRotationCurve.value = geo2.QuaternionMultiply(self.model.modelRotationCurve.value, rotation)

    def MoveDragObject(self):
        pYPlane = self.GetMousePosToYPlaneIntersection()
        self.UpdateModelPosition(pYPlane)

    def GetMousePosToYPlaneIntersection(self):
        ray, p0 = self.GetRayAndPointFromScreen()
        pYPlane = self.GetIntersectionToYPlane(p0, ray)
        return pYPlane

    def RotateDragObject(self):
        dx = float(uicore.uilib.dx * 0.01)
        self.UpdateModelRotation(dx)

    def GetRayAndPointFromScreen(self):
        x = float(uicore.uilib.x)
        y = float(uicore.uilib.y)
        data = self.GetCameraMatrixes()
        start = geo2.Vec3Unproject((x, y, 0.0), *data)
        end = geo2.Vec3Unproject((x, y, 100000.0), *data)
        ray = geo2.Vec3SubtractD(end, start)
        ray = geo2.Vector(*ray)
        start = geo2.Vector(*start)
        return (ray, start)

    def GetCameraMatrixes(self):
        if self.cameraMatrixes:
            return self.cameraMatrixes
        camera = self.GetCamera()
        viewPort = (0.0,
         0.0,
         float(uicore.desktop.width),
         float(uicore.desktop.height),
         0,
         100000.0)
        self.cameraMatrixes = (viewPort,
         camera.projectionMatrix.transform,
         camera.viewMatrix.transform,
         geo2.MatrixIdentity())
        return self.cameraMatrixes

    def GetCamera(self):
        return sm.GetService('sceneManager').GetActiveCamera()

    def GetIntersectionToYPlane(self, p0, ray):
        return RayToPlaneIntersection(p0, ray, (0, 0, 0), (0, 1.0, 0))

    def StartMoving(self):
        structPos = self.model.translationCurve.value
        structPos = (structPos[0], 0, structPos[2])
        mousePos = self.GetMousePosToYPlaneIntersection()
        self.movingOffset = geo2.Vec3Subtract(structPos, mousePos)

    def EndMoving(self):
        self.cameraMatrixes = None
        self.movingOffset = None
