#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\evegraphics\ui\lineController.py
import trinity
LINE_CONNECTOR_ATTACKING = 'attacking'
LINE_CONNECTOR_LOCKING = 'locking'
LINE_CONNECTOR_MOVING = 'moving'
LINE_CONNECTOR_RANGE = 'range'
LINE_CONNECTOR_ORBIT = 'orbit'
LINE_CONNECTOR_RANGE_SPHERE = 'rangeSphere'
LINE_CONNECTOR_ANCHOR_SPHERE = 'anchorSphere'
LINE_CONNECTOR_ANCHOR_STRAIGHT = 'anchorStraight'
LINE_CONNECTOR_POINT_TO_POINT = 'pointToPoint'
_LINE_CONNECTORS = {LINE_CONNECTOR_ATTACKING: 'res:/dx9/model/ui/lineConnectorAttacking.red',
 LINE_CONNECTOR_LOCKING: 'res:/dx9/model/ui/lineConnectorLocking.red',
 LINE_CONNECTOR_MOVING: 'res:/dx9/model/ui/lineConnectorMoving.red',
 LINE_CONNECTOR_ORBIT: 'res:/dx9/model/ui/lineConnectorMoving.red',
 LINE_CONNECTOR_RANGE: 'res:/dx9/model/ui/lineConnectorGeneric.red',
 LINE_CONNECTOR_RANGE_SPHERE: 'res:/dx9/model/ui/lineConnectorGeneric.red',
 LINE_CONNECTOR_ANCHOR_SPHERE: 'res:/dx9/model/ui/lineConnectorGeneric.red',
 LINE_CONNECTOR_ANCHOR_STRAIGHT: 'res:/dx9/model/ui/lineConnectorGeneric.red',
 LINE_CONNECTOR_POINT_TO_POINT: 'res:/dx9/model/ui/lineConnectorGeneric.red'}
_LINE_CONNECTOR_TYPE = {LINE_CONNECTOR_RANGE: trinity.EveConnectorStyle.XZ_CircleStraight,
 LINE_CONNECTOR_RANGE_SPHERE: trinity.EveConnectorStyle.XZ_Circle,
 LINE_CONNECTOR_ANCHOR_SPHERE: trinity.EveConnectorStyle.CurvedAnchor,
 LINE_CONNECTOR_ANCHOR_STRAIGHT: trinity.EveConnectorStyle.StraightAnchor,
 LINE_CONNECTOR_POINT_TO_POINT: trinity.EveConnectorStyle.PointToPoint,
 LINE_CONNECTOR_ORBIT: trinity.EveConnectorStyle.Orbit}

class LineSet:

    def __init__(self, lineSet):
        self.lines = {}
        self.lineSet = lineSet

    def RebuildLine(self, lineID):
        line = self.lines[lineID]
        del self.lines[lineID]
        self.lineSet.RemoveLine(lineID)
        line.lineID = self.lineSet.AddStraightLine(line.startPos, line.color, line.endPos, line.color, line.width)
        self.lineSet.SubmitChanges()
        self.lines[line.lineID] = line

    def AddLine(self, p0, p1, color, width = 1.0):
        line = Line(self, p0, p1, color, width)
        line.lineID = self.lineSet.AddStraightLine(line.startPos, line.color, line.endPos, line.color, line.width)
        self.lineSet.SubmitChanges()
        self.lines[line.lineID] = line
        return line

    def RemoveLine(self, lineID):
        del self.lines[lineID]
        self.lineSet.RemoveLine(lineID)
        self.lineSet.SubmitChanges()

    def Clear(self):
        for key in self.lines:
            self.lineSet.RemoveLine(key)

        self.lineSet.SubmitChanges()
        self.lines.clear()

    def Destroy(self):
        self.Clear()
        self.lineSet = None


class Line:

    def __init__(self, lineSet, p0, p1, color, width = 1.0):
        self.lineID = None
        self.lineSet = lineSet
        self.width = width
        self.color = color
        self.startPos = p0
        self.endPos = p1

    def SetStartPosition(self, p):
        self.startPos = p
        self.lineSet.RebuildLine(self.lineID)

    def SetEndPosition(self, p):
        self.endPos = p
        self.lineSet.RebuildLine(self.lineID)

    def SetColor(self, color):
        self.color = color
        self.lineSet.RebuildLine(self.lineID)


class LinePath:

    def __init__(self, lineSet, color = (1, 1, 1, 1)):
        self.lines = []
        self.lineSet = lineSet
        self.activePosition = (0, 0, 0)
        self.activeLine = None
        self.color = color

    def BeginPath(self, position = (0, 0, 0)):
        self.lines.append(self.lineSet.AddLine(position, self.activePosition, self.color))

    def SetPosition(self, position):
        self.lines[-1].SetEndPosition(position)
        self.activePosition = position

    def ConfirmPoint(self):
        self.BeginPath(self.activePosition)

    def UndoPoint(self):
        if len(self.lines) <= 1:
            return
        self.lineSet.RemoveLine(self.lines[-1].lineID)
        self.lines = self.lines[:-1]
        self.activeLine = self.lines[-1]
        self.SetPosition(self.activePosition)

    def EndPath(self):
        self.lineSet.Clear()
        self.lines = []

    def GetPath(self):
        if len(self.lines) == 0:
            return ((0, 0, 0), (0, 0, 0))
        return (self.lines[0].startPos, self.lines[-1].endPos)

    def GetStartPosition(self):
        if len(self.lines) == 0:
            return None
        return self.lines[0].startPos

    def GetEndPosition(self):
        if len(self.lines) == 0:
            return None
        return self.lines[-1].endPos


class ConnectorStyle:

    def __init__(self, width = 1.0, color = (0.8, 0.8, 0.8, 1.0), animated = False, autoScale = False, animationColor = (0.8, 0.8, 0.8, 1.0), animationScale = 1.0):
        self.width = width
        self.color = color
        self.animated = animated
        self.autoScale = autoScale
        self.animationColor = animationColor
        self.animationScale = animationScale

    def Apply(self, connector):
        lc = connector.lineConnector
        lc.lineWidth = self.width
        lc.color = self.color
        lc.isAnimated = self.animated
        lc.autoScaleAnimation = self.autoScale
        lc.animationColor = self.animationColor
        lc.animationScale = self.animationScale


class LineConnector:

    def __init__(self, container, connectorType, sourceCurve, destCurve):
        self.container = container
        self.type = connectorType
        self.lineConnector = None
        self.sourceCurve = sourceCurve
        self.destCurve = destCurve
        self.sourcePosition = (0, 0, 0)
        self.destPosition = (0, 0, 0)
        self.Load()

    def Load(self):
        if self.type not in _LINE_CONNECTORS:
            return
        self.lineConnector = trinity.Load(_LINE_CONNECTORS[self.type])
        if self.type in _LINE_CONNECTOR_TYPE:
            self.lineConnector.type = _LINE_CONNECTOR_TYPE[self.type]
        self.container.connectors.append(self.lineConnector)
        self.lineConnector.destObject = self.destCurve
        self.lineConnector.sourceObject = self.sourceCurve

    def Destroy(self):
        self.container.connectors.fremove(self.lineConnector)
        self.lineConnector = None
        self.type = None
        self.sourceCurve = None
        self.destCurve = None

    def SetDestinationCurve(self, curve):
        self.destCurve = curve
        self.lineConnector.destObject = curve

    def SetSourceCurve(self, curve):
        self.sourceCurve = curve
        self.lineConnector.sourceObject = curve

    def SetDestPosition(self, position):
        self.lineConnector.destPosition = position

    def SetSourcePosition(self, position):
        self.lineConnector.sourcePosition = position

    def SetColor(self, color):
        self.lineConnector.color = color

    def SetWidth(self, width):
        self.lineConnector.lineWidth = width


class LineController:
    _singletonInstance = None
    _CONNECTOR_CONTAINER_PATH = 'res:/dx9/model/ui/lineContainer.red'
    _FREEFORM_LINESET_PATH = 'res:/dx9/model/ui/lineSetTransparent.red'

    def __init__(self, scene = None):
        self._connectorContainer = trinity.Load(self._CONNECTOR_CONTAINER_PATH)
        self._freeformLineSet = trinity.Load(self._FREEFORM_LINESET_PATH)
        if scene is not None:
            scene.objects.append(self._connectorContainer)
            scene.objects.append(self._freeformLineSet)
        else:
            sm.GetService('sceneManager').RegisterPersistentSpaceObject((LineController, 0), self._connectorContainer)
            sm.GetService('sceneManager').RegisterPersistentSpaceObject((LineController, 1), self._freeformLineSet)

    def AddSpaceObjectConnector(self, source, dest, lineType):
        if lineType not in _LINE_CONNECTORS:
            return
        redFile = _LINE_CONNECTORS[lineType]
        connector = trinity.Load(redFile)
        connector.sourceObject.parentPositionCurve = source
        connector.sourceObject.parentRotationCurve = source
        connector.sourceObject.alignPositionCurve = dest
        connector.destObject.parentPositionCurve = dest
        connector.destObject.parentRotationCurve = dest
        connector.destObject.alignPositionCurve = source
        self._connectorContainer.connectors.append(connector)
        return id(connector)

    def CreateConnector(self, lineType, sourceCurve = None, destCurve = None):
        return LineConnector(self._connectorContainer, lineType, sourceCurve, destCurve)

    def CreateLinePath(self, color = (1, 1, 1, 1)):
        return LinePath(self.CreateLineSet(), color)

    def CreateLineSet(self):
        return LineSet(self._freeformLineSet)

    @staticmethod
    def GetGlobalInstance(scene = None):
        if LineController._singletonInstance is None:
            LineController._singletonInstance = LineController(scene)
        return LineController._singletonInstance
