#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\structure\structureSettings\schedule\smallSchedule.py
import datetime
from carbonui.primitives.container import Container
import carbonui.const as uiconst
from carbonui.primitives.fill import Fill
from carbonui.primitives.frame import Frame
import structures

class SmallSchedule(Container):
    default_height = 30
    default_width = 49
    HOURS_IN_BLOCK = 4
    DAY_WIDTH = 5
    BLOCK_HEIGHT = 5
    DAY_SPACER = 2
    DAY_COLOR = (1.0, 1.0, 1.0, 0.15)
    TODAY_COLOR = (1.0, 1.0, 1.0, 0.35)

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.vulnerableHoursInt = attributes.vulnerableHours
        isSameSchedule = attributes.get('isSameSchedule', True)
        today = datetime.datetime.today().weekday()
        blocks = self.GetBlocks()
        for eachDay, eachBlock in blocks:
            toTop = eachBlock * self.BLOCK_HEIGHT
            left = self.GetLeftForDay(eachDay)
            Fill(parent=self, pos=(left,
             toTop,
             self.DAY_WIDTH,
             self.BLOCK_HEIGHT - 1), align=uiconst.TOPLEFT, color=(1, 1, 0, 0.75))

        for i in xrange(7):
            if i == today:
                color = self.TODAY_COLOR
            else:
                color = self.DAY_COLOR
            left = self.GetLeftForDay(dayNum=i)
            Fill(parent=self, pos=(left,
             0,
             self.DAY_WIDTH,
             0), align=uiconst.TOLEFT_NOPUSH, color=color)

        if not isSameSchedule:
            Frame(bgParent=self, color=(1, 0, 0, 0.2), padding=-4)
            Fill(bgParent=self, color=(1, 0, 0, 0.1), padding=-4)

    def GetLeftForDay(self, dayNum):
        left = dayNum * (self.DAY_WIDTH + self.DAY_SPACER)
        return left

    def GetBlocks(self):
        schedule = structures.Schedule(self.vulnerableHoursInt)
        vulnerableHours = schedule.GetVulnerableHours()
        blocks = set()
        for each in vulnerableHours:
            day, hour = each
            blockNum = hour / self.HOURS_IN_BLOCK
            blocks.add((day, blockNum))

        return blocks
