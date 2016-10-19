#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\carbonui\graphs\linegraph.py
import trinity
from carbonui.primitives.vectorlinetrace import VectorLineTrace
from carbonui.graphs.graphsutil import GetGraphX
import carbonui.const as uiconst
from . import *

class LineGraph(VectorLineTrace):
    default_name = 'linegraph'
    default_align = uiconst.TOPLEFT
    default_animation = ANIM_NONE
    default_animationDuration = 1.0
    default_animationDelay = 0.0
    default_cornerType = 0
    default_lineWidth = 1.0
    default_spriteEffect = trinity.TR2_SFX_FILL_AA
    default_color = (1.0, 1.0, 1.0, 1.0)
    default_zoom = 30
    default_state = uiconst.UI_DISABLED

    def ApplyAttributes(self, attributes):
        VectorLineTrace.ApplyAttributes(self, attributes)
        self.graphContainer = attributes.get('graphContainer', None)
        self.data = attributes.get('data', None)
        if self.data is None:
            return
        self.maxValue = attributes.get('maxValue', 0)
        self.color = attributes.get('color', self.default_color)
        self.animation = attributes.get('animation', self.default_animation)
        self.animationDelay = attributes.get('animationDelay', self.default_animationDelay)
        self.animationDuration = attributes.get('animationDuration', self.default_animationDuration)
        self.zoom = attributes.get('zoom', self.default_zoom)
        self.axis = attributes.get('axis', None)
        self.Build()

    def Build(self, animate = False):
        width, height = self.graphContainer.GetAbsoluteSize()
        color = (self.color.r,
         self.color.g,
         self.color.b,
         self.color.a)
        for i, point in enumerate(self.data):
            x = GetGraphX(i, width, self.zoom)
            if self.axis:
                y = self.axis.GetAxisValue(point)
            else:
                y = 0
            self.AddPoint((x, y), color)

        if animate:
            self.AddAnimation()

    def AddAnimation(self):
        uicore.animations.MorphScalar(self, 'end', 0.0, 1.0, duration=self.animationDuration, curveType=uiconst.ANIM_LINEAR, loops=1, timeOffset=self.animationDelay)

    def SetRange(self, dataRange, zoom):
        start, end = dataRange
        if zoom != self.zoom:
            self.zoom = zoom
            self.Rebuild()

    def Rebuild(self):
        self.Flush()
        self.Build()
