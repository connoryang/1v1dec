#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\carbonui\graphs\donchianchannel.py
import trinity
from carbonui.primitives.polygon import Polygon
from carbonui.graphs.graphsutil import GetGraphX
import carbonui.const as uiconst
from . import *
from graphsutil import GetGraphY, MovingHigh, MovingLow

class DonchianChannel(Polygon):
    default_name = 'donchianchannel'
    default_align = uiconst.TOPLEFT
    default_animation = ANIM_NONE
    default_animationDelay = 0.0
    default_animationDuration = 1.0
    default_zoom = 20

    def ApplyAttributes(self, attributes):
        Polygon.ApplyAttributes(self, attributes)
        self.graphContainer = attributes.get('graphContainer', None)
        self.data = attributes.get('data', [])
        self.animation = attributes.get('animation', self.default_animation)
        self.animationDelay = attributes.get('animationDelay', self.default_animationDelay)
        self.animationDuration = attributes.get('animationDuration', self.default_animationDuration)
        self.zoom = attributes.get('zoom', self.default_zoom)
        self.axis = attributes.get('axis', None)
        if self.axis:
            self.axis.UpdateRanges(self.data[0])
            self.axis.UpdateRanges(self.data[1])
        self.Build()

    def Build(self):
        low = MovingLow(self.data[0], 5)
        hi = MovingHigh(self.data[1], 5)
        maximum = max(max(self.data[0]), max(self.data[1]))
        minimum = min(min(self.data[0]), min(self.data[1]))
        color = (self.color.r,
         self.color.g,
         self.color.b,
         self.color.a)
        ro = self.GetRenderObject()
        width, height = self.graphContainer.GetAbsoluteSize()
        count = len(self.data[0])
        for i in xrange(count):
            if self.axis is None:
                hiY = GetGraphY(hi[i], minimum, maximum, height)
                lowY = GetGraphY(low[i], minimum, maximum, height)
            else:
                hiY = self.axis.GetAxisValue(hi[i])
                lowY = self.axis.GetAxisValue(low[i])
            x = GetGraphX(i, width, self.zoom)
            vert1 = trinity.Tr2Sprite2dVertex()
            vert1.position = (x, hiY)
            vert1.color = color
            ro.vertices.append(vert1)
            vert2 = trinity.Tr2Sprite2dVertex()
            vert2.position = (x, lowY)
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

        self.AddAnimation()

    def AddAnimation(self):
        if self.animation == ANIM_NONE:
            return
        if self.animation == ANIM_FADE_IN:
            endValue = self.color[3]
            uicore.animations.FadeIn(self, endVal=endValue, duration=self.animationDuration, timeOffset=self.animationDelay)
        else:
            uicore.animations.FadeIn(self, endVal=0.0, duration=self.animationDuration, timeOffset=self.animationDelay)

    def SetRange(self, dataRange, zoom):
        start, end = dataRange
        if zoom != self.zoom:
            self.zoom = zoom
            self.Rebuild()

    def Rebuild(self):
        self.Flush()
        self.Build()
