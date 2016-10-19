#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\structure\structureBrowser\entries\structureEntry.py
from carbon.common.script.util.commonutils import StripTags
from eve.client.script.ui.control.baseListEntry import BaseListEntryCustomColumns
from eve.client.script.ui.control.eveIcon import ItemIcon
from eve.client.script.ui.control.eveLabel import Label
from eve.client.script.ui.control.glowSprite import GlowSprite
from eve.client.script.ui.eveFontConst import EVE_MEDIUM_FONTSIZE
from eve.client.script.ui.station import stationServiceConst
from eve.client.script.ui.structure.structureBrowser.browserUIConst import ALL_SERVICES
from eve.client.script.ui.structure.structureBrowser.extaColumnUtil import ExtraColumnProvider, GetHeaderForService
from eve.client.script.ui.structure.structureBrowser.controllers.structureEntryController import StructureEntryController
from localization import GetByLabel
import carbonui.const as uiconst
from utillib import KeyVal
HEIGHT = 48
ICONSIZE = 20
LABEL_PARAMS = (EVE_MEDIUM_FONTSIZE, 0, 0)

class StructureEntry(BaseListEntryCustomColumns):
    default_name = 'StructureEntry'

    def ApplyAttributes(self, attributes):
        BaseListEntryCustomColumns.ApplyAttributes(self, attributes)
        self.controller = self.node.controller
        self.AddColumnText(self.controller.GetNumJumps())
        self.AddColumnText(self.controller.GetSecurityWithColor())
        self.AddColumnText(self.controller.GetOwnerName())
        self.AddColumnName()
        self.AddColumnServices()
        self.AddExtraColumns()

    def AddColumnName(self):
        column = self.AddColumnContainer()
        name = self.controller.GetName()
        size = HEIGHT - 4
        ItemIcon(parent=column, align=uiconst.CENTERLEFT, typeID=self.controller.GetTypeID(), width=size, height=size, state=uiconst.UI_DISABLED)
        Label(parent=column, text=name, align=uiconst.CENTERLEFT, left=HEIGHT, state=uiconst.UI_NORMAL)

    def AddColumnServices(self):
        column = self.AddColumnContainer()
        structureServices = self.controller.GetServices()
        structureServicesChecked = self.node.structureServicesChecked
        for i, data in enumerate(structureServices):
            left = i * ICONSIZE
            opacity = 1.0 if structureServicesChecked == ALL_SERVICES or data.name in structureServicesChecked else 0.2
            gs = StructureServiceIcon(name=data.name, parent=column, texturePath=data.iconID, pos=(left,
             0,
             ICONSIZE,
             ICONSIZE), hintHeader=data.label, opacity=opacity, serviceName=data.name, controller=self.controller, serviceID=data.serviceID)
            gs.DelegateEvents(self)

    def AddExtraColumns(self):
        structureServicesChecked = self.node.structureServicesChecked
        if structureServicesChecked == ALL_SERVICES:
            return
        for serviceName in structureServicesChecked:
            columnText = ExtraColumnProvider().GetColumnText(self.controller, serviceName)
            if columnText is not None:
                self.AddColumnText(columnText)

    def GetDragData(self):
        nodesSelected = self.sr.node.scroll.GetSelectedNodes(self.sr.node)
        data = []
        for eachNode in nodesSelected:
            k = KeyVal(__guid__='xtriui.ListSurroundingsBtn', itemID=eachNode.controller.GetItemID(), typeID=eachNode.controller.GetTypeID(), label=StripTags(eachNode.controller.GetName().replace('<br>', '-')), isMyCorpStructureEntry=True)
            data.append(k)

        return data

    @staticmethod
    def GetColumnSortValues(controller, structureServicesChecked):
        baseColumns = (controller.GetNumJumps(),
         controller.GetSecurity(),
         controller.GetOwnerName().lower(),
         '%s %s' % (controller.GetSystemName(), StripTags(controller.GetName()).lower()),
         len(controller.GetServices()))
        return baseColumns

    @staticmethod
    def GetSortValue(node, by, sortDirection, idx):
        return (node.columnSortValues[idx],) + tuple(node.columnSortValues)

    @staticmethod
    def GetExtraHeaders(structureServicesChecked):
        extraHeaders = []
        if structureServicesChecked == ALL_SERVICES:
            return []
        for serviceName in structureServicesChecked:
            header = GetHeaderForService(serviceName)
            if header:
                extraHeaders += [header]

        return extraHeaders

    @staticmethod
    def GetHeaders(structureServicesChecked):
        extraHeaders = StructureEntry.GetExtraHeaders(structureServicesChecked)
        baseColumns = [GetByLabel('UI/Common/Jumps'),
         GetByLabel('UI/Common/Security'),
         GetByLabel('UI/Common/Owner'),
         GetByLabel('UI/Common/Name'),
         GetByLabel('UI/Structures/Browser/ServicesColumn')]
        return baseColumns + extraHeaders

    @staticmethod
    def GetDynamicHeight(node, width):
        return HEIGHT

    @staticmethod
    def GetDefaultColumnWidth():
        return {GetByLabel('UI/Industry/System'): 70,
         GetByLabel('UI/Common/Name'): 230}

    @staticmethod
    def GetFixedColumns():
        return {GetByLabel('UI/Structures/Browser/ServicesColumn'): ICONSIZE * len(stationServiceConst.serviceData) + 2}

    def GetMenu(self):
        return sm.GetService('menu').GetMenuFormItemIDTypeID(itemID=self.controller.GetItemID(), typeID=self.controller.GetTypeID())

    @staticmethod
    def GetColWidths(node, idx = None):
        controller = node.controller
        widths = []
        if idx is None or idx == 0:
            jumpText = unicode(controller.GetNumJumps())
            widths.append(uicore.font.MeasureTabstops([(jumpText,) + LABEL_PARAMS])[0])
        if idx is None or idx == 1:
            securityText = unicode(controller.GetSecurity())
            widths.append(uicore.font.MeasureTabstops([(securityText,) + LABEL_PARAMS])[0])
        if idx is None or idx == 2:
            widths.append(uicore.font.MeasureTabstops([(controller.GetOwnerName(),) + LABEL_PARAMS])[0])
        if idx is None or idx == 3:
            nameToUse = max(StripTags(controller.GetName(), ignoredTags=('br',)).split('<br>'), key=len)
            widths.append(uicore.font.MeasureTabstops([(nameToUse,) + LABEL_PARAMS])[0] + HEIGHT - 4)
        return widths


class StructureServiceIcon(GlowSprite):
    default_align = uiconst.CENTERLEFT
    default_state = uiconst.UI_NORMAL

    def ApplyAttributes(self, attributes):
        GlowSprite.ApplyAttributes(self, attributes)
        self.controller = attributes.controller
        self.hintHeader = attributes.hintHeader
        self.serviceName = attributes.serviceName
        self.serviceID = attributes.serviceID

    def GetHint(self):
        hint = self.hintHeader
        textHelper = ExtraColumnProvider()
        extraHeader = GetHeaderForService(self.serviceName)
        extraText = textHelper.GetColumnText(self.controller, self.serviceName)
        if extraHeader and extraText and extraText != textHelper.NO_VALUE_FOUND_CHAR:
            hint += '<br>%s: %s' % (extraHeader, extraText)
        return hint


class StructureServiceIconMyCorp(StructureServiceIcon):

    def GetHint(self):
        return self.hintHeader
