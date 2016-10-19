#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\structure\structureSettings\schedule\schedulePickeCombo.py
from carbonui.control.scrollentries import SE_GenericCore
from eve.client.script.ui.control.eveCombo import Combo
from eve.client.script.ui.structure.structureSettings.schedule.smallSchedule import SmallSchedule
from eve.client.script.ui.structure.structureSettings.schedule.vulnerabilitySchedulePicker import ScheduleEntry
import carbonui.const as uiconst
HEADER_OPTION = 0

class PickerCombo(Combo):
    default_height = 36
    default_width = 200

    def ApplyAttributes(self, attributes):
        Combo.ApplyAttributes(self, attributes)
        self.sr.iconParent.width = 50

    def OnEntryClick(self, entry, *args):
        uicore.Message('ComboEntrySelect')
        key, val = entry.sr.node.data
        self.SelectItemByValue(val)
        if val == HEADER_OPTION:
            self.Cleanup()
        if self.OnChange:
            self.OnChange(self, key, val)

    def UpdateSelectedValue(self, entry):
        text = entry[0]
        value = entry[1]
        self.sr.selected.text = text
        if value == HEADER_OPTION:
            self.sr.iconParent.display = False
        else:
            self.sr.iconParent.Flush()
            SmallSchedule(parent=self.sr.iconParent, align=uiconst.CENTERLEFT, vulnerableHours=value)
            self.sr.iconParent.display = True
        self.selectedValue = entry[1]

    def GetScrollEntry(self, label, returnValue, hint = None, icon = None, indentLevel = None):
        data, returnValue = Combo.GetScrollEntry(self, label, returnValue, hint, icon, indentLevel)
        if data.data[1] == HEADER_OPTION:
            decoClass = SE_GenericCore
        else:
            decoClass = ScheduleEntry
        data.decoClass = decoClass
        data.vulnerableHours = returnValue
        return (data, returnValue)

    def SelectItemByValue(self, val):
        for each in self.entries:
            if each[1] == val:
                self.UpdateSelectedValue(each)
                return True

        self.SelectItemByIndex(HEADER_OPTION)
        return True

    def SetMenuTop(self, menu, t, h):
        menu.top = max(8, t - menu.height)
