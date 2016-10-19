#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\carbonui\graphs\axis.py
from carbon.common.script.util.format import FmtAmt
from carbonui.primitives.container import Container
from carbonui.util.color import Color
import carbonui.const as uiconst
from eve.client.script.ui.control.eveLabel import Label
AXIS_TIGHT = 0
AXIS_FROM_ZERO = 1
AXIS_CUSTOM = 2

class VerticalAxis(Container):
    default_lowerMarginPercent = 0.0
    default_higherMarginPercent = 0.0
    default_gridLineCount = 10
    default_behavior = AXIS_TIGHT
    default_textAlignment = uiconst.BOTTOMRIGHT

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.rangesUpdated = False
        self.lowerMarginPercent = attributes.get('lowerMarginPercent', self.default_lowerMarginPercent)
        self.higherMarginPercent = attributes.get('higherMarginPercent', self.default_higherMarginPercent)
        self.gridLineCount = attributes.get('gridLineCount', self.default_gridLineCount)
        self.textAlignment = attributes.get('textAlignment', self.default_textAlignment)
        self.behavior = attributes.get('behavior', self.default_behavior)
        self.maximum = -1e+20
        self.minimum = 1e+20
        self.rangesUpdated = False
        self.Build()

    def Build(self):
        contAutoSize = Container(name='AxisContainer', parent=self)
        d = self.gridLineCount
        for i in xrange(d):
            axisContainer = Container(parent=contAutoSize, align=uiconst.TOTOP_PROP, height=1.0 / d)
            if not self.rangesUpdated:
                return
            labelText = FmtAmt(self.GetValue(1.0 - float(i) / (self.gridLineCount - 1)), 'sn')
            Label(name='leftLabel', parent=axisContainer, align=self.textAlignment, text=labelText, color=Color.WHITE)

    def GetValue(self, ratio):
        return float(ratio) * (self.maximum - self.minimum) + self.minimum

    def UpdateRanges(self, data):
        self.maximum = max(self.maximum, max(data))
        self.minimum = min(self.minimum, min(data))
        range = self.maximum - self.minimum
        if self.behavior == AXIS_FROM_ZERO:
            self.minimum = min(self.minimum, 0)
        else:
            self.minimum -= range * self.lowerMarginPercent
        self.maximum += range * self.higherMarginPercent
        self.rangesUpdated = True
        self.Rebuild()

    def Rebuild(self):
        self.Flush()
        self.Build()

    def SetCustomRanges(self, minimum, maximum):
        self.maximum = maximum
        self.minimum = minimum
        self.behavior = AXIS_CUSTOM
        self.rangesUpdated = True

    def GetAxisValue(self, value):
        width, height = self.GetAbsoluteSize()
        offset = 0.0
        if 0.0 < self.height < 1.0:
            offset = self.parent.GetAbsoluteSize()[1] * (1.0 - self.height)
        ret = offset + height * (1.0 - (float(value) - self.minimum) / (self.maximum - self.minimum))
        return int(self.padding[1] + ret)

    def GetGridLines(self):
        width, height = self.GetAbsoluteSize()
        return map(lambda x: float(x) / self.gridLineCount * height, xrange(self.gridLineCount + 1))


class TimeAxis(Container):
    pass
