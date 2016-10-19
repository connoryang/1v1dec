#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\structure\structureSettings\schedule\scheduleTooltip.py
from carbonui.primitives.container import Container
from eve.client.script.ui.structure.structureSettings.schedule.vulnerabilitySchedule import VulnerabilitySchedulerWithReinforcement
from localization import GetByLabel
import structures
import carbonui.const as uiconst

class ScheduleTooltip(object):
    scheduleSize = 300

    def AddScheduleToTooltip(self, tooltipPanel, typeID, hoursThisWeek, hoursNextWeek):
        tooltipPanel.margin = (8, 8, 8, 8)
        tooltipPanel.cellSpacing = (30, 10)
        tooltipPanel.AddLabelLarge(text=GetByLabel('UI/StructureProfiles/ThisWeek'), align=uiconst.CENTER, bold=True)
        thisWeekSchedule = structures.Schedule(hoursThisWeek)
        scheduleCont = Container(width=self.scheduleSize, height=self.scheduleSize, align=uiconst.TOPLEFT)
        VulnerabilitySchedulerWithReinforcement(parent=scheduleCont, canModify=False, schedule=thisWeekSchedule, frame=False)
        if hoursThisWeek == hoursNextWeek:
            tooltipPanel.columns = 1
            tooltipPanel.AddCell(cellObject=scheduleCont)
        else:
            tooltipPanel.columns = 2
            tooltipPanel.AddLabelLarge(text=GetByLabel('UI/StructureProfiles/NextWeek'), align=uiconst.CENTER, bold=True)
            tooltipPanel.AddCell(cellObject=scheduleCont)
            nextWeekSchedule = structures.Schedule(hoursNextWeek)
            scheduleCont = Container(width=self.scheduleSize, height=self.scheduleSize, align=uiconst.TOPLEFT)
            VulnerabilitySchedulerWithReinforcement(parent=scheduleCont, canModify=False, schedule=nextWeekSchedule, frame=False)
            tooltipPanel.AddCell(cellObject=scheduleCont)
