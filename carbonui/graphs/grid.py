#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\carbonui\graphs\grid.py
import trinity
import geo2
from carbonui.primitives.container import Container
from carbonui.primitives.vectorline import VectorLine
from carbonui.primitives.line import Line
from carbonui.graphs.graphsutil import GetGraphX
import carbonui.const as uiconst

class Grid(Container):
    default_name = 'grid'
    default_align = uiconst.TOPLEFT
    default_topColor = (1.0, 1.0, 1.0, 0.3)
    default_bottomColor = (1.0, 1.0, 1.0, 0.1)
    default_leftColor = (1.0, 0.0, 0.0, 0.1)
    default_rightColor = (0.0, 1.0, 0.0, 0.1)
    default_state = uiconst.UI_DISABLED

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.topColor = attributes.get('topColor', self.default_topColor)
        self.bottomColor = attributes.get('bottomColor', self.default_bottomColor)
        self.leftColor = attributes.get('leftColor', self.default_leftColor)
        self.rightColor = attributes.get('rightColor', self.default_rightColor)
        self.verticalAxis = attributes.get('verticalAxis', None)
        self.horizontalAxis = attributes.get('horizontalAxis ', None)
        self.Build()

    def Build(self):
        width, height = self.parent.GetAbsoluteSize()
        if self.verticalAxis is not None:
            count = self.verticalAxis.gridLineCount
            for i in xrange(count):
                vertContainer = Container(parent=self, align=uiconst.TOTOP_PROP, height=1.0 / count)
                delta = float(i) / count
                color = geo2.Vec4Lerp(self.topColor, self.bottomColor, delta)
                Line(name='topLine', parent=vertContainer, align=uiconst.TOBOTTOM, padding=(0, 0, 0, 0), weight=1, color=color)

        if self.horizontalAxis is not None:
            verticalLines = self.horizontalAxis.GetGridLines()
            count = len(verticalLines)
            for i, line in enumerate(verticalLines):
                delta = float(i) / count
                color = geo2.Vec4Lerp(self.leftColor, self.rightColor, delta)
                VectorLine(parent=self, align=uiconst.TOALL, translationFrom=(line, 0), translationTo=(line, height), color=color, widthFrom=1.0, widthTo=1.0, spriteEffect=trinity.TR2_SFX_FILL)

        self.width = width
        self.height = height

    def Rebuild(self):
        self.Flush()
        self.Build()
