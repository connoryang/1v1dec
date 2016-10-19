#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\carbonui\graphs\bargraph.py
from carbonui.primitives.container import Container
from carbonui.graphs.graphsutil import GetGraphX
from carbonui.primitives.vectorline import VectorLine
from carbonui.primitives.frame import Frame
import trinity
import carbonui.const as uiconst
from carbonui.util.color import Color
DEFAULT_TEXTURE = 'res:/UI/Texture/classes/graph/simple_frame_fill.png'

class GraphBar(Frame):
    __guid__ = 'uiprimitives.GraphBar'
    default_name = 'GraphBar'
    default_cornerSize = 2
    default_pickRadius = 0.0
    default_fillCenter = True
    default_hoverColor = (1.2, 0.5, 1.0, 1.0)
    default_align = uiconst.TOPLEFT

    def ApplyAttributes(self, attributes):
        Frame.ApplyAttributes(self, attributes)
        self.originalColor = (self.color.r,
         self.color.g,
         self.color.b,
         self.color.a)
        self.originaltexture = self.texturePath
        self.hoverColor = attributes.get('hoverColor', self.default_hoverColor)

    def OnMouseEnter(self, *args):
        self.texturePath = 'res:/texture/global/white.dds'
        self.color = self.hoverColor

    def OnMouseExit(self, *args):
        self.color = self.originalColor
        self.texturePath = self.originaltexture


class BarGraph(Container):
    default_name = 'BarGraph'
    default_negativeColor = Color.RED
    default_color = Color.GREEN
    default_texture = DEFAULT_TEXTURE
    default_align = uiconst.TOPLEFT
    default_zoom = 30
    default_barSize = 7

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.negativeColor = attributes.get('negativeColor', self.default_negativeColor)
        self.graphContainer = attributes.get('graphContainer', None)
        self.barSize = attributes.get('barSize', self.default_barSize)
        self.barSizeMinMax = attributes.get('barSizeMinMax', (self.barSize, self.barSize))
        self.data = attributes.get('data', [])
        self.hints = attributes.get('hints', [])
        self.color = attributes.get('color', self.default_color)
        self.texture = attributes.get('texture', self.default_texture)
        self.axis = attributes.get('axis', None)
        if self.axis:
            self.axis.UpdateRanges(self.data)
        self.zoom = attributes.get('zoom', None)
        self.Build()

    def SetRange(self, dataRange, zoom):
        start, end = dataRange
        if zoom != self.zoom:
            self.zoom = zoom
            self.Rebuild()

    def Build(self, animate = False):
        width, height = self.graphContainer.GetAbsoluteSize()
        barWidth = width / self.zoom - 1.0 - 1.0
        barWidth = min(max(barWidth, self.barSizeMinMax[0]), self.barSizeMinMax[1])
        for i, point in enumerate(self.data):
            volume = self.data[i]
            x = GetGraphX(i, width, self.zoom)
            y = self.axis.GetAxisValue(volume)
            zero = self.axis.GetAxisValue(0)
            color = self.color
            if y > zero:
                tmp = y
                y = zero
                zero = tmp
                color = self.negativeColor
            if self.hints and len(self.hints) > 0:
                hint = self.hints[i]
            else:
                hint = None
            GraphBar(parent=self, align=uiconst.TOPLEFT, width=barWidth, height=zero - y - 2, top=y, left=x - barWidth / 2.0, hint=hint, state=uiconst.UI_MOUSEHOVER, color=color, texturePath=self.texture)

        if self.axis.minimum < 0:
            zero = self.axis.GetAxisValue(0)
            VectorLine(parent=self, align=uiconst.TOALL, translationFrom=(0, zero), translationTo=(x, zero), color=(1.0, 1.0, 1.0, 0.5), widthFrom=1.0, widthTo=1.0, spriteEffect=trinity.TR2_SFX_FILL)
        if animate:
            uicore.animations.MorphScalar(self, 'opacity', startVal=0.0, endVal=1.0, duration=0.3, timeOffset=2.3)
        self.width = GetGraphX(len(self.data), width, self.zoom)
        self.height = height

    def Rebuild(self):
        self.Flush()
        self.Build()
