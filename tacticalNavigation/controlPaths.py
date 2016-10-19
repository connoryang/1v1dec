#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\tacticalNavigation\controlPaths.py
import math
from carbon.common.script.util.mathUtil import RayToPlaneIntersection
import geo2
import trinity
import carbonui.const as uiconst
import tacticalNavigation.ui as navUI
from evegraphics.wrappers.vectorFunctions import OffsetPositionFunction, VectorFunction, XZPlaneRotationFunction, AverageVectorFunction
_PATH_STATE_PICK_XZ = 0
_PATH_STATE_PICK_Y = 1
_PATH_STATE_INACTIVE = 2
_PATH_STATE_DONE = 3
LABEL_OFFSET = (0, 0, 0)
_MAX_PICK_DISTANCE = 4000000

class AreaIndication:
    _resPath = ''

    def __init__(self):
        self.model = trinity.Load(self._resPath)
        self._started = False

    def Start(self):
        self._started = True
        sm.GetService('sceneManager').RegisterPersistentSpaceObject((self, self._resPath), self.model)
        self.Update()

    def SetCurves(self, source, destination):
        pass

    def Update(self):
        pass

    def Abort(self):
        if self._started:
            sm.GetService('sceneManager').RemovePersistentSpaceObject((self, self._resPath))
        self.model.translationCurve = None
        self.model.rotationCurve = None


class ConeAreaIndication(AreaIndication):
    _resPath = 'res:/ui/inflight/tactical/superWeaponCone.red'

    def SetCurves(self, sourceFunction, destinationFunction):
        self.sourceFunction = sourceFunction
        self.destinationFunction = destinationFunction
        self.model.translationCurve = sourceFunction.GetBlueFunction()

    def Update(self):
        sourcePoint = self.sourceFunction.GetValue()
        destPoint = self.destinationFunction.GetValue()
        d = geo2.Vec3Subtract(destPoint, sourcePoint)
        length = geo2.Vec3Length(d)
        self.model.scaling = (length, length, length)
        self.model.rotation = geo2.QuaternionRotationArc((0, 1, 0), geo2.Vec3Normalize(d))


class CylinderAreaIndication(AreaIndication):
    _resPath = 'res:/ui/inflight/tactical/superWeaponCylinder.red'

    def __init__(self, radius):
        AreaIndication.__init__(self)
        self.radius = radius

    def SetCurves(self, sourceFunction, destinationFunction):
        self.sourceFunction = sourceFunction
        self.destinationFunction = destinationFunction
        self.model.translationCurve = sourceFunction.GetBlueFunction()

    def Update(self):
        sourcePoint = self.sourceFunction.GetValue()
        destPoint = self.destinationFunction.GetValue()
        d = geo2.Vec3Subtract(destPoint, sourcePoint)
        length = geo2.Vec3Length(d)
        self.model.scaling = (self.radius, length, self.radius)
        self.model.rotation = geo2.QuaternionRotationArc((0, 1, 0), geo2.Vec3Normalize(d))


class SphereAreaIndication(AreaIndication):
    _resPath = 'res:/ui/inflight/tactical/rangeSphere.red'

    def __init__(self, radius):
        AreaIndication.__init__(self)
        self.scaling = radius * 2

    def Start(self):
        AreaIndication.Start(self)
        self.model.scaling = (self.scaling, self.scaling, self.scaling)

    def SetCurves(self, sourceFunction, destinationFunction):
        self.model.translationCurve = destinationFunction.GetBlueFunction()


class SliceAreaIndication(AreaIndication):
    _resPath = 'res:/ui/inflight/tactical/superWeaponSlice.red'

    def __init__(self, radius):
        AreaIndication.__init__(self)
        self.scaling = radius * 2
        self.xaxis = (1, 0, 0)
        self.zaxis = (0, 0, -1)
        self.rotation = (0, 0, 0, 1)

    def Start(self):
        AreaIndication.Start(self)
        self.model.scaling = (self.scaling, self.scaling, self.scaling)

    def SetCurves(self, sourceFunction, destinationFunction):
        self.sourceFunction = sourceFunction
        self.destinationFunction = destinationFunction
        self.model.translationCurve = sourceFunction.GetBlueFunction()

    def SetAxis(self, xaxis, zaxis):
        self.xaxis = xaxis
        self.zaxis = zaxis
        yaxis = geo2.Vec3Normalize(geo2.Vec3Cross(zaxis, xaxis))
        self.rotation = geo2.QuaternionRotationMatrix((xaxis + (0,),
         yaxis + (0,),
         zaxis + (0,),
         (0, 0, 0, 1)))

    def Update(self):
        sourcePoint = self.sourceFunction.GetValue()
        destPoint = self.destinationFunction.GetValue()
        d = geo2.Vec3Subtract(destPoint, sourcePoint)
        length = geo2.Vec3Length(d)
        self.model.scaling = (length, self.scaling, length)
        self.model.rotation = self.rotation


class SinglePointPath:

    def __init__(self, showRange = True, agressive = False, maxDistance = _MAX_PICK_DISTANCE, fixedDistance = False, baseDistance = 0):
        if agressive:
            self.color = navUI.COLOR_ATTACK
        else:
            self.color = navUI.COLOR_MOVE
        self.secondaryColor = navUI.ColorCombination(self.color, navUI.ALPHA_MEDIUM)
        self.primaryColor = navUI.ColorCombination(self.color, navUI.ALPHA_HIGH)
        self.state = _PATH_STATE_INACTIVE
        self.maxDistance = maxDistance
        self.fixedDistance = fixedDistance
        self.baseDistance = baseDistance
        self.anchorFunction = None
        self.offsetAnchorFunction = None
        self.planarFunction = None
        self.destinationFunction = None
        self.xzLine = None
        self.yLine = None
        self.yArc = None
        self.distanceCircle = None
        self.pathLine = None
        self.label = None
        self.areaIndication = None
        self.showRange = showRange

    def SetMaxDistance(self, distance):
        self.maxDistance = distance

    def SetFixedDistance(self, isFixed):
        self.fixedDistance = isFixed

    def Start(self, anchorCurve = None, areaIndication = None):
        self.anchorFunction = VectorFunction(anchorCurve)
        self.offsetAnchorFunction = OffsetPositionFunction(anchorCurve)
        self.planarFunction = OffsetPositionFunction(anchorCurve)
        planarCurve = self.planarFunction.GetBlueFunction()
        self.destinationFunction = OffsetPositionFunction(anchorCurve)
        destCurve = self.destinationFunction.GetBlueFunction()
        xzDirectionCurve = XZPlaneRotationFunction(anchorCurve, destCurve).GetBlueFunction()
        if anchorCurve is not None:
            labelCurve = AverageVectorFunction([destCurve, anchorCurve]).GetBlueFunction()
        else:
            labelCurve = AverageVectorFunction([destCurve, trinity.TriVectorCurve()]).GetBlueFunction()
        self.labelFunction = OffsetPositionFunction(labelCurve, LABEL_OFFSET)
        labelCurve = self.labelFunction.GetBlueFunction()
        self.distanceCircle = navUI.CreateRangeCircleConnector(navUI.STYLE_STRONG, self.color, anchorCurve, destCurve)
        self.xzLine = navUI.CreateStraightConnector(navUI.STYLE_DOTTED, self.color, anchorCurve, xzDirectionCurve)
        self.yLine = navUI.CreateStraightAnchorConnector(navUI.STYLE_FAINT, self.color, planarCurve, destCurve)
        self.yArc = navUI.CreateCurvedAnchorConnector(navUI.STYLE_DOTTED, self.color, anchorCurve, destCurve)
        self.pathLine = navUI.CreateStraightConnector(navUI.STYLE_STRONG, self.color, anchorCurve, destCurve)
        self.areaIndication = areaIndication
        if areaIndication is not None:
            areaIndication.SetCurves(self.offsetAnchorFunction, self.destinationFunction)
            areaIndication.Start()
        if self.showRange:
            self.label = navUI.CreateHoverLabel('0', navUI.ColorCombination(self.color, navUI.ALPHA_SOLID), labelCurve)
            self.label.measurer.fontSize = 20
        self.state = _PATH_STATE_PICK_XZ

    def Abort(self):

        def _destroyConnector(connector):
            if connector is not None:
                connector.Destroy()

        _destroyConnector(self.distanceCircle)
        _destroyConnector(self.pathLine)
        _destroyConnector(self.xzLine)
        _destroyConnector(self.yLine)
        _destroyConnector(self.yArc)
        self.distanceCircle = None
        self.pathLine = None
        self.xzLine = None
        self.yLine = None
        self.yArc = None
        self.state = _PATH_STATE_INACTIVE
        if self.label is not None:
            navUI.RemoveHoverLabel(self.label)
            self.label = None
        if self.areaIndication is not None:
            self.areaIndication.Abort()
            self.areaIndication = None

    def AddPoint(self):
        if self.state == _PATH_STATE_PICK_XZ:
            self.state = _PATH_STATE_PICK_Y
        elif self.state == _PATH_STATE_PICK_Y:
            self.state = _PATH_STATE_DONE

    def _UpdateDistanceText(self):
        if self.label is not None:
            distance = geo2.Vec3Length(geo2.Vec3Subtract(self.anchorFunction.GetValue(), self.destinationFunction.GetValue()))
            distance -= self.baseDistance
            self.label.SetText(str(int(distance / 1000.0 + 0.5)))

    def UpdatePosition(self, cameraController):
        if self.state == _PATH_STATE_PICK_XZ:
            plane_center = self.anchorFunction.GetValue()
            ray_dir, ray_start = cameraController.GetPickVector()
            if ray_dir[1] == 0:
                return
            multiplier = (ray_start[1] - plane_center[1]) / -ray_dir[1]
            pick_position = geo2.Vec3Add(ray_start, geo2.Vec3Scale(ray_dir, multiplier))
            pick_dir = geo2.Vec3Subtract(pick_position, plane_center)
            maxDistance = self.maxDistance + self.baseDistance
            if multiplier < 0:
                pick_dir = geo2.Vec3Normalize(geo2.Vec3Scale(pick_dir, -1))
                pick_position = geo2.Vec3Add(plane_center, geo2.Vec3Scale(pick_dir, maxDistance))
            pick_length = geo2.Vec3Length(pick_dir)
            if pick_length > maxDistance or self.fixedDistance:
                pick_dir = geo2.Vec3Normalize(pick_dir)
                pick_position = geo2.Vec3Add(plane_center, geo2.Vec3Scale(pick_dir, maxDistance))
            self.planarFunction.SetOffsetWorldspace(pick_position)
            self.destinationFunction.SetOffsetWorldspace(pick_position)
            self._UpdateDistanceText()
        elif self.state == _PATH_STATE_PICK_Y:
            xz_position = self.planarFunction.GetValue()
            plane_center = self.anchorFunction.GetValue()
            xz_direction = geo2.Vec3Subtract(xz_position, plane_center)
            length = geo2.Vec3Length(xz_direction)
            xz_direction = geo2.Vec3Normalize(xz_direction)
            plane_dir = geo2.Vec3Cross(xz_direction, (0, 1, 0))
            ray_dir, start = cameraController.GetPickVector()
            pick_position, sign = RayToPlaneIntersection(start, ray_dir, plane_center, plane_dir, returnSign=True)
            pick_dir = geo2.Vec3Normalize(geo2.Vec3Subtract(pick_position, plane_center))
            pick_dir = geo2.Vec3Scale(pick_dir, sign)
            pick_position = geo2.Vec3Add(plane_center, geo2.Vec3Scale(pick_dir, length))
            self.destinationFunction.SetOffsetWorldspace(pick_position)
        base_offset = geo2.Vec3Subtract(self.destinationFunction.GetValue(), self.anchorFunction.GetValue())
        base_offset = geo2.Vec3Scale(geo2.Vec3Normalize(base_offset), self.baseDistance)
        self.offsetAnchorFunction.SetOffsetRelative(base_offset)
        if self.areaIndication is not None:
            self.areaIndication.Update()

    def IsComplete(self):
        return self.state == _PATH_STATE_DONE

    def IsFirstPointSet(self):
        return self.state > _PATH_STATE_PICK_XZ

    def GetEndPosition(self):
        if self.destinationFunction is not None:
            return self.destinationFunction.GetValue()


class ArcPath:

    def __init__(self, agressive = False, degrees = 30.0, maxDistance = _MAX_PICK_DISTANCE, baseDistance = 0):
        radians = degrees * math.pi / 360.0
        self.color = navUI.COLOR_ATTACK
        self.arcScale = math.tan(radians)
        self.point1Path = None
        self.destinationConnector1 = None
        self.destinationConnector2 = None
        self.arcLine = None
        self.destinationFunction1 = None
        self.destinationFunction2 = None
        self.isComplete = False
        self.pickLength = 1.0
        self.pickPlaneDirection = (0, 0, 1)
        self.maxDistance = maxDistance
        self.baseDistance = baseDistance
        self.fixedDistance = False
        self.agressive = True
        self.areaIndication = None
        self.direction = (0, 0, 0)

    def SetMaxDistance(self, distance):
        self.maxDistance = distance
        if self.point1Path is not None:
            self.point1Path.SetMaxDistance(distance)

    def SetFixedDistance(self, isFixed):
        self.fixedDistance = isFixed
        if self.point1Path is not None:
            self.point1Path.SetFixedDistance(isFixed)

    def Start(self, anchorCurve = None, areaIndication = None):
        self.point1Path = SinglePointPath(agressive=self.agressive, maxDistance=self.maxDistance, fixedDistance=self.fixedDistance, baseDistance=self.baseDistance)
        self.point1Path.Start(anchorCurve)
        self.areaIndication = areaIndication
        self.anchorFunction = VectorFunction(anchorCurve)
        self.destinationFunction1 = OffsetPositionFunction(anchorCurve)
        self.destinationFunction2 = OffsetPositionFunction(anchorCurve)

    def Abort(self):
        if self.point1Path is not None:
            self.point1Path.Abort()
        if self.destinationConnector1 is not None:
            self.destinationConnector1.Destroy()
            self.destinationConnector1 = None
        if self.destinationConnector2 is not None:
            self.destinationConnector2.Destroy()
            self.destinationConnector2 = None
        if self.arcLine is not None:
            self.arcLine.Destroy()
            self.arcLine = None
        if self.areaIndication is not None:
            self.areaIndication.Abort()
            self.areaIndication = None

    def AddPoint(self):
        if not self.point1Path.IsComplete():
            self.point1Path.AddPoint()
            if self.point1Path.IsComplete():
                sourceCurve = self.point1Path.offsetAnchorFunction.GetBlueFunction()
                destCurve1 = self.destinationFunction1.GetBlueFunction()
                self.destinationConnector1 = navUI.CreateStraightConnector(navUI.STYLE_STRONG, self.color, sourceCurve, destCurve1)
                destCurve2 = self.destinationFunction2.GetBlueFunction()
                self.destinationConnector2 = navUI.CreateStraightConnector(navUI.STYLE_STRONG, self.color, sourceCurve, destCurve2)
                self.pickPlaneDirection = geo2.Vec3Subtract(self.point1Path.offsetAnchorFunction.GetValue(), self.point1Path.destinationFunction.GetValue())
                self.pickLength = geo2.Vec3Length(self.pickPlaneDirection)
                self.pickPlaneDirection = geo2.Vec3Normalize(self.pickPlaneDirection)
                self.arcLine = navUI.CreateStraightConnector(navUI.STYLE_DOTTED, self.color, destCurve1, destCurve2)
                if self.areaIndication is not None:
                    self.areaIndication.SetCurves(self.point1Path.offsetAnchorFunction, self.point1Path.destinationFunction)
                    self.areaIndication.Start()
        else:
            self.isComplete = True

    def UpdatePosition(self, cameraController):
        if not self.point1Path.IsComplete():
            self.point1Path.UpdatePosition(cameraController)
            return
        if not self.IsComplete():
            ray_dir, start = cameraController.GetPickVector()
            plane_position = self.point1Path.GetEndPosition()
            pick_position = RayToPlaneIntersection(start, ray_dir, plane_position, self.pickPlaneDirection)
            plane_offset = geo2.Vec3Subtract(pick_position, plane_position)
            plane_offset = geo2.Vec3Normalize(plane_offset)
            z_axis = plane_offset
            plane_offset = geo2.Vec3Scale(plane_offset, self.arcScale * self.pickLength)
            destination1_offset = geo2.Vec3Add(plane_position, plane_offset)
            destination2_offset = geo2.Vec3Subtract(plane_position, plane_offset)
            self.destinationFunction1.SetOffsetWorldspace(destination1_offset)
            self.destinationFunction2.SetOffsetWorldspace(destination2_offset)
            x_axis = geo2.Vec3Normalize(geo2.Vec3Subtract(plane_position, self.point1Path.offsetAnchorFunction.GetValue()))
            if self.areaIndication is not None:
                self.areaIndication.SetAxis(x_axis, z_axis)
                self.areaIndication.Update()

    def IsComplete(self):
        return self.isComplete

    def IsFirstPointSet(self):
        if not self.point1Path:
            return False
        return self.point1Path.IsFirstPointSet()

    def GetPath(self):
        return (self.destinationFunction1.GetValue(), self.destinationFunction2.GetValue())
