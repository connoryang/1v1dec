#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\carbonui\graphs\minimap.py
import trinity
from carbonui.primitives.container import Container
from carbonui.primitives.frame import Frame
from carbonui.primitives.polygon import Polygon
from carbonui.primitives.vectorline import VectorLine
import carbonui.const as uiconst
from graphsutil import GetGraphY

def GetGraphX(i, count, width):
    return width * ((i + 1) / float(count + 1))


class MapSlider(Container):
    default_name = 'mapslider'
    default_color = (1.0, 1.0, 1.0, 0.3)
    default_hoverColor = (1.0, 1.0, 1.0, 0.5)

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.drag = False
        self.dragStart = 0
        self.dragOffset = 0
        self.color = attributes.get('color', self.default_color)
        self.hoverColor = attributes.get('hoverColor', self.default_hoverColor)
        self.frame = Frame(name='myFrame', bgParent=self, texturePath='res:/UI/Texture/classes/shipTree/infoPanel/selected.png', cornerSize=8, color=self.color)

    def OnMouseDown(self, *args):
        self.drag = True
        self.dragStart = (uicore.uilib.x, uicore.uilib.y)
        self.dragOffset = self.left - uicore.uilib.x

    def OnMouseEnter(self, *args):
        if self.hoverColor:
            self.frame.color = self.hoverColor

    def OnMouseExit(self, *args):
        if self.color:
            self.frame.color = self.color

    def OnMouseUp(self, *args):
        self.drag = False

    def OnMouseMove(self, *args):
        if self.drag:
            newPos = uicore.uilib.x + self.dragOffset
            self.UpdatePosition(newPos)

    def JumpToAndStartDrag(self, position):
        self.drag = True
        self.dragOffset = position

    def UpdatePosition(self, pos = None):
        if pos is None:
            pos = self.left
        pos = max(0, pos)
        parentWidth = float(self.parent.GetAbsoluteSize()[0])
        pos = min(pos, parentWidth - self.width)
        self.left = pos
        self.parent.UpdateGraphData(self.left / parentWidth, (self.left + self.width) / parentWidth)


class MiniMap(Container):
    default_state = uiconst.UI_MOUSEDOWN

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.graph = attributes.get('graph', None)
        self.data = attributes.get('data', [])
        self.zoom = attributes.get('zoom', 30)
        self.range = attributes.get('range', None)
        self.lines = attributes.get('lines', None)
        self.maximum = max(self.data)
        self.minimum = min(self.data)
        self.Build()

    def Build(self):
        self.AddGraph()
        self.AddLines()
        size = self.GetAbsoluteSize()
        width = size[0] * (self.range[1] - self.range[0]) / float(len(self.data))
        sliderPos = GetGraphX(self.range[0], len(self.data), size[0])
        self.slider = MapSlider(name='myMapSlider', parent=self, align=uiconst.TOLEFT, height=size[1], width=width, left=sliderPos, top=0, maxValue=self.maximum, state=uiconst.UI_MOUSEDOWN)

    def AddGraph(self):
        polygon = Polygon(parent=self)
        color = (1.0, 1.0, 1.0, 0.3)
        polygon.color = color
        ro = polygon.GetRenderObject()
        thisWidth, thisHeight = self.GetAbsoluteSize()
        count = len(self.data)
        for i in xrange(count):
            vert1 = trinity.Tr2Sprite2dVertex()
            vert1.position = (GetGraphX(i, count, thisWidth), thisHeight)
            vert1.color = color
            ro.vertices.append(vert1)
            vert2 = trinity.Tr2Sprite2dVertex()
            vert2.position = (GetGraphX(i, count, thisWidth), GetGraphY(self.data[i], self.minimum, self.maximum, thisHeight))
            vert2.color = color
            ro.vertices.append(vert2)

        for i in xrange(count - 1):
            triangle1 = trinity.Tr2Sprite2dTriangle()
            triangle1.index0 = 2 * i
            triangle1.index1 = 2 * i + 1
            triangle1.index2 = 2 * i + 2
            ro.triangles.append(triangle1)
            triangle2 = trinity.Tr2Sprite2dTriangle()
            triangle2.index0 = 2 * i + 1
            triangle2.index1 = 2 * i + 3
            triangle2.index2 = 2 * i + 2
            ro.triangles.append(triangle2)

    def AddLines(self):
        thisWidth, thisHeight = self.GetAbsoluteSize()
        count = len(self.data)
        for i in self.lines:
            x = thisWidth * (i / float(count))
            VectorLine(name='minimapMonth', parent=self, translationFrom=(x, 0), translationTo=(x, thisHeight), widthFrom=1.0, widthTo=1.0, spriteEffect=trinity.TR2_SFX_FILL, color=(1.0, 1.0, 1.0, 0.1))

    def UpdateGraphData(self, start, end):
        startIndex = int(start * len(self.data))
        endIndex = int(end * len(self.data))
        self.parent.SetRange(startIndex, endIndex, True)

    def Rebuild(self):
        self.Flush()
        self.Build()

    def SetRange(self, dataRange, zoomRange):
        width, height = self.GetAbsoluteSize()
        self.zoom = zoomRange
        oldWidth = self.slider.width
        self.slider.width = width * zoomRange / len(self.data)
        delta = -oldWidth + self.slider.width
        self.slider.UpdatePosition()

    def OnMouseDown(self, *args):
        offset = uicore.uilib.x - self.GetAbsoluteLeft() - self.slider.width / 2.0
        self.slider.UpdatePosition(offset)
        self.slider.OnMouseDown(*args)

    def OnMouseMove(self, *args):
        self.slider.OnMouseMove(*args)

    def OnMouseUp(self, *args):
        self.slider.OnMouseUp()
