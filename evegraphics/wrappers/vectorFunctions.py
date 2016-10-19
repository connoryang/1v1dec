#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\evegraphics\wrappers\vectorFunctions.py
import blue
import geo2
import trinity

def _VectorToTuple(vector):
    return (vector.x, vector.y, vector.z)


class VectorFunction:

    def __init__(self, parentFunction):
        self.curve = parentFunction

    def GetBlueFunction(self):
        return self.curve

    def GetValue(self):
        if self.curve is None:
            return (0, 0, 0)
        return _VectorToTuple(self.curve.GetVectorAt(blue.os.GetSimTime()))


class OffsetPositionFunction(VectorFunction):

    def __init__(self, parentFunction, offset = (0, 0, 0), rotationFunction = None):
        curve = trinity.EveLocalPositionCurve()
        curve.behavior = trinity.EveLocalPositionBehavior.offsetPosition
        curve.parentPositionCurve = parentFunction
        curve.parentRotationCurve = rotationFunction
        curve.positionOffset = offset
        VectorFunction.__init__(self, curve)

    def SetOffsetWorldspace(self, worldPos):
        position = (0, 0, 0)
        if self.curve.parentPositionCurve is not None:
            position = _VectorToTuple(self.curve.parentPositionCurve.GetVectorAt(blue.os.GetSimTime()))
        self.SetOffsetRelative(geo2.Vec3Subtract(worldPos, position))

    def SetOffsetRelative(self, offset):
        self.curve.positionOffset = offset

    def GetOffset(self):
        return self.curve.positionOffset

    def SetParentFunction(self, curve):
        self.curve.parentPositionCurve = curve


class AverageVectorFunction(VectorFunction):

    def __init__(self, vectorFunctions):
        curve = trinity.TriVectorSequencer()
        curve.operator = trinity.TRIOP_AVERAGE
        for each in vectorFunctions:
            curve.functions.append(each)

        VectorFunction.__init__(self, curve)


class XZProjectionFunction(VectorFunction):

    def __init__(self, positionFunction, planeY = 0):
        curve = trinity.TriVectorSequencer()
        curve.operator = trinity.TRIOP_MULTIPLY
        curve.functions.append(positionFunction)
        self.projectionCurve = trinity.TriVectorCurve()
        self.projectionCurve.value = (0, planeY, 0)
        VectorFunction.__init__(self, curve)

    def SetPlaneY(self, planeY):
        self.projectionCurve.value = (0, planeY, 0)


class XZPlaneRotationFunction(VectorFunction):

    def __init__(self, originFunction, targetFunction):
        curve = trinity.EveLocalPositionCurve()
        curve.behavior = trinity.EveLocalPositionBehavior.offsetPlaneRotation
        curve.parentPositionCurve = originFunction
        curve.alignPositionCurve = targetFunction
        VectorFunction.__init__(self, curve)
