#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\carbonui\graphs\pointgraph.py
import random
import blue
from carbonui.primitives.container import Container
from carbonui.primitives.sprite import Sprite
from carbonui.graphs.graphsutil import GetGraphX
from carbonui.primitives.base import ReverseScaleDpi
import carbonui.const as uiconst
from . import ANIM_NONE, ANIM_BOTTOM_FROM_LEFT, ANIM_BOTTOM_FROM_RIGHT, ANIM_BOTTOM_RANDOM, ANIM_BOTTOM_SIMULTANEOUS
from graphsutil import GetGraphY

class GraphPoint(Sprite):
    default_name = 'graphpoint'

    def ApplyAttributes(self, attributes):
        Sprite.ApplyAttributes(self, attributes)
        self.originalColor = (self.color.r,
         self.color.g,
         self.color.b,
         self.color.a)
        self.originalSize = (self.width, self.height)
        self.originalPosition = (self.left, self.top)
        self.hoverColor = attributes.get('hoverColor', self.color)

    def OnMouseEnter(self, *args):
        self.color = self.hoverColor
        self.width = self.originalSize[0] * 1.5
        self.height = self.originalSize[1] * 1.5
        self.left = self.originalPosition[0] - (self.width - self.originalSize[0]) / 2
        self.top = self.originalPosition[1] - (self.height - self.originalSize[1]) / 2

    def OnMouseExit(self, *args):
        self.color = self.originalColor
        self.width = self.originalSize[0]
        self.height = self.originalSize[1]
        self.left = self.originalPosition[0]
        self.top = self.originalPosition[1]


class PointGraph(Container):
    default_name = 'pointgraph'
    default_align = uiconst.TOPLEFT
    default_width = 100
    default_height = 100
    default_pointSize = 7.0
    default_pointColor = (0.2, 0.54, 1.0, 1.0)
    default_pointHoverColor = (1.2, 0.5, 1.0, 1.0)
    default_texture = 'res:/UI/Texture/classes/graph/point.png'
    default_animation = ANIM_NONE
    default_animationDelay = 0.0
    default_animationDuration = 1.0
    default_zoom = 30

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.graphContainer = attributes.get('graphContainer', None)
        self.pointSize = attributes.get('pointSize', self.default_pointSize)
        self.pointSizeMinMax = attributes.get('pointSizeMinMax', (self.pointSize, self.pointSize))
        self.pointColor = attributes.get('pointColor', self.default_pointColor)
        self.pointHoverColor = attributes.get('pointHoverColor', self.default_pointHoverColor)
        self.texture = attributes.get('texture', self.default_texture)
        self.data = attributes.get('data', None)
        self.hints = attributes.get('hints', None)
        self.animation = attributes.get('animation', self.default_animation)
        self.zoom = attributes.get('zoom', self.default_zoom)
        self.axis = attributes.get('axis', None)
        if self.data is None:
            return
        if self.axis is not None:
            self.axis.UpdateRanges(self.data)
        self.Build(animate=True)

    def AddAnimation(self, sprite, index):
        if self.animation == ANIM_NONE:
            return
        width, height = self.GetAbsoluteSize()
        count = len(self.data)
        if self.animation == ANIM_BOTTOM_FROM_LEFT:
            offset = index / float(count)
        elif self.animation == ANIM_BOTTOM_FROM_RIGHT:
            offset = 1.0 - index / float(count)
        elif self.animation == ANIM_BOTTOM_RANDOM:
            offset = random.random() * self.default_animationDuration
        else:
            offset = 0
        uicore.animations.MorphScalar(sprite, 'displayY', height - 10, sprite.top, duration=self.default_animationDuration, curveType=uiconst.ANIM_OVERSHOT, timeOffset=self.default_animationDelay + offset)

    def Build(self, animate = False):
        blue.pyos.BeNice()
        width, height = self.graphContainer.GetAbsoluteSize()
        minimum, maximum = min(self.data), max(self.data)
        pointSize = float(width + 1) / self.zoom
        pointSize = min(max(pointSize, self.pointSizeMinMax[0]), self.pointSizeMinMax[1])
        for i, point in enumerate(self.data):
            x = GetGraphX(i, width, self.zoom) - pointSize / 2.0
            if self.axis is None:
                y = GetGraphY(point, minimum, maximum, height) - pointSize / 2.0
            else:
                y = self.axis.GetAxisValue(point)
            if self.hints is not None and len(self.hints) != 0:
                hint = self.hints[i]
            else:
                hint = None
            sprite = GraphPoint(name='medianSprite', parent=self, texturePath=self.texture, width=pointSize, height=pointSize, color=self.pointColor, hoverColor=self.pointHoverColor, left=x, top=y, hint=hint)
            if animate:
                self.AddAnimation(sprite, i)

        self.width = GetGraphX(len(self.data), width, self.zoom) + self.pointSize
        self.height = height

    def SetRange(self, dataRange, zoom):
        start, end = dataRange
        if zoom != self.zoom:
            self.zoom = zoom
            self.Rebuild()

    def Rebuild(self):
        self.Flush()
        self.Build(animate=False)
