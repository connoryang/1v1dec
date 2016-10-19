#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\structure\structureBrowser\extaColumnUtil.py
from eve.client.script.ui.station.stationServiceConst import serviceDataByNameID, serviceIDAlwaysPresent
from eve.common.script.util.eveFormat import FmtISK
from localization import GetByLabel
import structures

def GetSettingDataObjectForServiceName(serviceName):
    serviceData = serviceDataByNameID.get(serviceName, None)
    if not serviceData or serviceData.serviceID == serviceIDAlwaysPresent:
        return
    settingIDForService = structures.SERVICES_ACCESS_SETTINGS.get(serviceData.serviceID, None)
    if settingIDForService is None:
        return
    settingInfo = structures.SETTING_OBJECT_BY_SETTINGID.get(settingIDForService, None)
    return settingInfo


def GetHeaderForService(serviceName):
    settingData = GetSettingDataObjectForServiceName(serviceName)
    if settingData is None:
        return
    labelPath = settingData.labelPath
    if labelPath:
        return GetByLabel(labelPath)


class ExtraColumnProvider(object):
    NO_VALUE_FOUND_CHAR = '-'

    def GetColumnText(self, controller, serviceName):
        serviceData = serviceDataByNameID.get(serviceName, None)
        if not serviceData:
            return
        settingData = GetSettingDataObjectForServiceName(serviceName)
        if settingData is None:
            return
        value = controller.GetInfoForExtraColumns(serviceData.serviceID, settingData)
        if value is None:
            return self.NO_VALUE_FOUND_CHAR
        text = self.FormatColumnValue(value, settingData.valueType)
        return text

    def FormatColumnValue(self, value, valueType):
        if valueType == structures.SETTINGS_TYPE_INT:
            return int(value)
        if valueType == structures.SETTINGS_TYPE_PERCENTAGE:
            return GetByLabel('UI/Structures/Browser/PercentageText', value=value)
        if valueType == structures.SETTINGS_TYPE_BOOL:
            return bool(value)
        if valueType == structures.SETTINGS_TYPE_ISK:
            return FmtISK(value, showFractionsAlways=0)
        return value
