#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\carbonui\graphs\market.py
from carbon.common.script.util.format import FmtDate, FmtAmt
import carbonui.const as uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.graphs.minimap import MiniMap
from carbonui.graphs.pointgraph import PointGraph
from carbonui.graphs.donchianchannel import DonchianChannel
from carbonui.graphs.axis import VerticalAxis, TimeAxis, AXIS_FROM_ZERO
from carbonui.graphs.lowhighvaluegraph import LowHighValueGraph
from carbonui.graphs.linegraph import LineGraph
from carbonui.graphs.bargraph import BarGraph
from carbonui.graphs.grid import Grid
from carbonui.graphs import ANIM_BOTTOM_FROM_LEFT
from graphsutil import MovingAvg, GetGraphX

class MarketGraph(Container):
    default_state = uiconst.UI_ACTIVE
    default_zoom = 30

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.data = attributes.get('data', None)
        self.zoom = attributes.get('zoom', self.default_zoom)
        if self.data is None:
            return
        count = len(self.data)
        self.range = (count - self.zoom, count)
        self.rebuildOnResize = []
        self.AddMiniMap()
        self.leftAxisWidth = 50
        self.rightAxisWidth = 50
        self.topAxis = TimeAxis(parent=self, align=uiconst.TOTOP, height=30, padding=(self.leftAxisWidth,
         0,
         self.rightAxisWidth,
         0))
        self.leftAxis = VerticalAxis(parent=self, align=uiconst.TOLEFT, width=self.leftAxisWidth, lowerMarginPercent=0.1, higherMarginPercent=0.05)
        self.rightAxisContainer = Container(parent=self, align=uiconst.TORIGHT, width=self.rightAxisWidth)
        self.rightAxis = VerticalAxis(parent=self.rightAxisContainer, behavior=AXIS_FROM_ZERO, textAlignment=uiconst.BOTTOMLEFT, align=uiconst.TOBOTTOM_PROP, height=0.3, gridLineCount=4)
        self.graphClipper = Container(name='GraphClipper', parent=self, align=uiconst.TOALL, clipChildren=True)
        self.graphCont = ContainerAutoSize(name='MainGraphArea', parent=self.graphClipper, align=uiconst.TOPLEFT)
        self.AddDonchianChannel()
        self.AddMedianPoints()
        self.AddLowHighGraph()
        self.AddMovingAverages()
        self.AddBarGraph()
        self.AddGrid()

    def AddGrid(self):
        self.grid = Grid(parent=self.graphCont, verticalAxis=self.leftAxis, horizontalAxis=self.topAxis)

    def AddBarGraph(self):
        data = [ x[4] for x in self.data ]
        hints = [ FmtDate(point[0], 'ln') + '\nOrders: ' + FmtAmt(point[5], 'sn') + '\nQuantity: ' + FmtAmt(point[4], 'sn') for point in self.data ]
        self.barGraph = BarGraph(parent=self.graphCont, graphContainer=self.graphClipper, barSizeMinMax=(2, 20), data=data, axis=self.rightAxis, hints=hints, zoom=self.zoom, color=(0.5, 1.0, 0.5, 0.5))

    def AddMovingAverages(self):
        closing = [ x[3] for x in self.data ]
        avg5Data = MovingAvg(closing, 5)
        avg20Data = MovingAvg(closing, 20)
        self.movingAvg5 = LineGraph(parent=self.graphCont, graphContainer=self.graphClipper, data=avg5Data, color=(1.0, 0.2, 0.1, 1.0), zoom=self.zoom, axis=self.leftAxis)
        self.movingAvg20 = LineGraph(parent=self.graphCont, graphContainer=self.graphClipper, data=avg20Data, color=(0.4, 0.2, 1.0, 1.0), zoom=self.zoom, axis=self.leftAxis)

    def AddLowHighGraph(self):
        data = [ (x[1], x[2]) for x in self.data ]
        self.lowHigh = LowHighValueGraph(parent=self.graphCont, graphContainer=self.graphClipper, data=data, zoom=self.zoom, axis=self.leftAxis)

    def AddDonchianChannel(self):
        data = ([ x[1] for x in self.data ], [ y[2] for y in self.data ])
        self.donchian = DonchianChannel(data=data, parent=self.graphCont, graphContainer=self.graphClipper, color=(0.8, 0.8, 1.0, 0.35), zoom=self.zoom, axis=self.leftAxis)

    def OnMouseWheel(self, event):
        value = event / 4
        self.zoom += value
        self.zoom = min(len(self.data), max(5, self.zoom))
        self.SetRange(*self.range)

    def __OnResize(self, *args):
        if hasattr(self, 'miniMap'):
            self.miniMap.Rebuild()
        if hasattr(self, 'median'):
            self.median.Show(False)
        for thing in getattr(self, 'rebuildOnResize', []):
            thing.Rebuild()

    def AddMiniMap(self):
        data = [ x[3] for x in self.data ]
        lines = []
        for i, point in enumerate(self.data):
            if FmtDate(point[0], fmt='ln').endswith('01'):
                lines.append(i)

        self.miniMap = MiniMap(name='MiniMap', parent=self, align=uiconst.TOBOTTOM, height=60, data=data, range=self.range, zoom=self.zoom, lines=lines)

    def AddMedianPoints(self):
        data = [ x[3] for x in self.data ]
        hints = [ FmtDate(point[0], 'ln') + '\n' + FmtAmt(point[3], 'sn') for point in self.data ]
        self.median = PointGraph(parent=self.graphCont, graphContainer=self.graphClipper, data=data, hints=hints, zoom=self.zoom, axis=self.leftAxis, pointSizeMinMax=(5, 10), animation=ANIM_BOTTOM_FROM_LEFT)
        self.rebuildOnResize.append(self.median)

    def MoveGraph(self, start):
        if self.graphCont is None:
            return
        width = self.graphClipper.GetAbsoluteSize()[0]
        offset = GetGraphX(start, width, self.zoom) - width / (2.0 * self.zoom)
        self.graphCont.left = -offset

    def SetRange(self, start, end, fromMiniMap = False):
        self.MoveGraph(start)
        self.range = (start, end)
        self.median.SetRange(self.range, self.zoom)
        self.donchian.SetRange(self.range, self.zoom)
        self.lowHigh.SetRange(self.range, self.zoom)
        self.movingAvg5.SetRange(self.range, self.zoom)
        self.movingAvg20.SetRange(self.range, self.zoom)
        self.barGraph.SetRange(self.range, self.zoom)
        if not fromMiniMap:
            self.miniMap.SetRange(self.range, self.zoom)
