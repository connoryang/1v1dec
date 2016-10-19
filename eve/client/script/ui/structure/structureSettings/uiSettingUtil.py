#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\structure\structureSettings\uiSettingUtil.py
from carbonui import const as uiconst
from eve.client.script.ui.control.eveSinglelineEdit import SinglelineEdit
from localization import GetByLabel
import structures

def GetUnit(settingType):
    if settingType == structures.SETTINGS_TYPE_PERCENTAGE:
        return '%'
    if settingType == structures.SETTINGS_TYPE_ISK:
        return GetByLabel('UI/Common/ISK')
    return ''


def AddValueEdit(parent, sgController, callback):
    settingType = sgController.GetSettingType()
    unit = GetUnit(settingType)
    amountEdit = SinglelineEditWithUnit(name='amountEdit', parent=parent, align=uiconst.CENTERRIGHT, OnChange=callback, unit=unit, pos=(4, 0, 60, 0))
    settingInfo = sgController.GetSettingInfo()
    valueRange = settingInfo.valueRange
    minValue, maxValue = valueRange
    value = sgController.GetValue()
    if settingType in (structures.SETTINGS_TYPE_INT, structures.SETTINGS_TYPE_ISK):
        amountEdit.IntMode(*valueRange)
        value = int(value)
    else:
        amountEdit.FloatMode(*valueRange)
        value = float(value)
    amountEdit.SetValue(value)
    labelClass = amountEdit.sr.text.__class__
    maxText = '%s %s' % (maxValue, unit)
    labelWidth, labelHeight = labelClass.MeasureTextSize(maxText)
    newWidth = max(labelWidth + 30, amountEdit.width)
    amountEdit.width = newWidth
    return amountEdit


class SinglelineEditWithUnit(SinglelineEdit):

    def ApplyAttributes(self, attributes):
        self.unit = attributes.unit
        SinglelineEdit.ApplyAttributes(self, attributes)

    def SetText(self, text, format = 0):
        SinglelineEdit.SetText(self, text, format)
        if self.unit:
            self.sr.text.text += ' %s ' % self.unit
