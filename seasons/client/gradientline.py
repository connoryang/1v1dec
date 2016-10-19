#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\seasons\client\gradientline.py
from carbonui.primitives.gradientSprite import GradientSprite
GRADIENT_LINE_RGB_DATA = ((0.0, (0.0, 0.0, 0.0)), (0.5, (1.0, 1.0, 1.0)), (1.0, (0.0, 0.0, 0.0)))
GRADIENT_LINE_OPACITY = 0.7
GRADIENT_LINE_HEIGHT = 1

class GradientLine(GradientSprite):
    default_rgbData = GRADIENT_LINE_RGB_DATA
    default_opacity = GRADIENT_LINE_OPACITY
    default_height = GRADIENT_LINE_HEIGHT
