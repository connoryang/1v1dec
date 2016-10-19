#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\carbonui\graphs\lowhighvaluegraph.py
import trinity
from carbonui.primitives.container import Container
from carbonui.primitives.vectorline import VectorLine
from carbonui.graphs.graphsutil import GetGraphX
import carbonui.const as uiconst
from graphsutil import GetGraphY

class LowHighValueGraph(Container):
    default_name = 'lowhighvaluegraph'
    default_width = 100
    default_height = 100
    default_align = uiconst.TOPLEFT
    default_zoom = 30

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.graphContainer = attributes.get('graphContainer', None)
        self.data = attributes.get('data', None)
        self.maxValue = attributes.get('maxValue', 0)
        self.markerSize = attributes.get('markerSize', 4)
        self.zoom = attributes.get('zoom', self.default_zoom)
        self.axis = attributes.get('axis', None)
        self.Build()

    def Build(self):
        width, height = self.graphContainer.GetAbsoluteSize()
        minimum = min(self.data[0])
        maximum = max(self.data[1])
        for i in xrange(len(self.data)):
            x = GetGraphX(i, width, self.zoom)
            if self.axis is not None:
                y1 = self.axis.GetAxisValue(self.data[i][0])
                y2 = self.axis.GetAxisValue(self.data[i][1])
            else:
                y1 = GetGraphY(self.data[i][0], minimum, maximum, height)
                y2 = GetGraphY(self.data[i][1], minimum, maximum, height)
            VectorLine(name='rangeLine', parent=self, translationFrom=(x, y1), translationTo=(x, y2), width=100, height=100, widthFrom=1.0, widthTo=1.0, spriteEffect=trinity.TR2_SFX_FILL, color=(1.0, 1.0, 1.0, 0.2))

    def SetRange(self, dataRange, zoom):
        start, end = dataRange
        if zoom != self.zoom:
            self.zoom = zoom
            self.Rebuild()

    def Rebuild(self):
        self.Flush()
        self.Build()
