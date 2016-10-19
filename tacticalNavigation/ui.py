#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\tacticalNavigation\ui.py
import trinity
import evegraphics.ui.lineController as lc
from evegraphics.wrappers.transformLabel import HoverLabel
COLOR_MOVE = (0, 0.678, 0.933)
COLOR_WARP = (0.318, 0.38, 0.675)
COLOR_ATTACK = (1.0, 0.1, 0.025)
COLOR_GENERIC = (1.0, 1.0, 1.0)
ALPHA_SOLID = 1.0
ALPHA_HIGH = 0.5
ALPHA_MEDIUM = 0.3
ALPHA_LOW = 0.1
DEFAULT_LINE_WIDTH = 2.0

def ColorCombination(color, alpha):
    return color + (alpha,)


STYLE_DOTTED = 'STYLE_DOTTED'
STYLE_FAINT = 'STYLE_FAINT'
STYLE_MEDIUM = 'STYLE_MEDIUM'
STYLE_STRONG = 'STYLE_STRONG'

def GetConnectorStyle(lineStyle, color):
    if lineStyle == STYLE_DOTTED:
        return lc.ConnectorStyle(2.0, (0,
         0,
         0,
         ALPHA_HIGH), True, True, ColorCombination(color, ALPHA_SOLID), 0.0004)
    if lineStyle == STYLE_FAINT:
        return lc.ConnectorStyle(1.5, ColorCombination(color, ALPHA_LOW))
    if lineStyle == STYLE_STRONG:
        return lc.ConnectorStyle(2.0, ColorCombination(color, ALPHA_HIGH))
    if lineStyle == STYLE_MEDIUM:
        return lc.ConnectorStyle(2.0, ColorCombination(color, ALPHA_MEDIUM))


def _CreateConnector(lineType, lineStyle, color, rootObject, destObject):
    lineStyle = GetConnectorStyle(lineStyle, color)
    lineController = lc.LineController.GetGlobalInstance()
    connector = lineController.CreateConnector(lineType, rootObject, destObject)
    lineStyle.Apply(connector)
    return connector


def CreateCurvedAnchorConnector(lineStyle, color, rootObject, destObject):
    return _CreateConnector(lc.LINE_CONNECTOR_ANCHOR_SPHERE, lineStyle, color, rootObject, destObject)


def CreateStraightAnchorConnector(lineStyle, color, rootObject, destObject):
    return _CreateConnector(lc.LINE_CONNECTOR_ANCHOR_STRAIGHT, lineStyle, color, rootObject, destObject)


def CreateStraightConnector(lineStyle, color, rootObject, destObject):
    return _CreateConnector(lc.LINE_CONNECTOR_POINT_TO_POINT, lineStyle, color, rootObject, destObject)


def CreateRangeCircleConnector(lineStyle, color, rootObject, destObject):
    return _CreateConnector(lc.LINE_CONNECTOR_RANGE_SPHERE, lineStyle, color, rootObject, destObject)


def CreateMovementConnector(sourceObject, destObject):
    lineController = lc.LineController.GetGlobalInstance()
    connector = lineController.CreateConnector(lc.LINE_CONNECTOR_MOVING, sourceObject, destObject)
    connector.SetWidth(DEFAULT_LINE_WIDTH)
    connector.SetColor(ColorCombination(COLOR_MOVE, ALPHA_MEDIUM))
    return connector


def CreateOrbitConenctor(sourceObject, destObject):
    lineController = lc.LineController.GetGlobalInstance()
    connector = lineController.CreateConnector(lc.LINE_CONNECTOR_ORBIT, sourceObject, destObject)
    connector.SetWidth(DEFAULT_LINE_WIDTH)
    connector.SetColor(ColorCombination(COLOR_MOVE, ALPHA_MEDIUM))
    return connector


def CreateAgressionConnector(sourceObject, destObject):
    lineController = lc.LineController.GetGlobalInstance()
    connector = lineController.CreateConnector(lc.LINE_CONNECTOR_MOVING, sourceObject, destObject)
    connector.SetWidth(DEFAULT_LINE_WIDTH)
    connector.SetColor(ColorCombination(COLOR_ATTACK, ALPHA_MEDIUM))
    return connector


def CreateHoverLabel(text, color, positionCurve, root = None):
    if root is None:
        root = CreateAndAddRoot(positionCurve)
    label = HoverLabel(text, root, size=18, scaling=0.0025, hspace=1)
    label.SetDiffuseColor(color)
    return label


def RemoveHoverLabel(label, remove = True):
    if remove:
        DestroyAndRemoveRoot(label.parent)
    label.parent.translationCurve = None
    label.parent = None


def CreateAndAddRoot(positionCurve):
    root = trinity.EveRootTransform()
    root.translationCurve = positionCurve
    scene = sm.GetService('sceneManager').GetRegisteredScene('default')
    scene.objects.append(root)
    return root


def DestroyAndRemoveRoot(root):
    scene = sm.GetService('sceneManager').GetRegisteredScene('default')
    scene.objects.fremove(root)
