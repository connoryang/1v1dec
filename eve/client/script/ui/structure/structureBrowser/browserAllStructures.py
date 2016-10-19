#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\structure\structureBrowser\browserAllStructures.py
import gametime
import uthread
from carbon.common.script.util.timerstuff import AutoTimer
from carbonui.primitives.container import Container
from carbonui.util.bunch import Bunch
from eve.client.script.ui.control.eveScroll import Scroll
from eve.client.script.ui.control.scrollUtil import TabFinder
from eve.client.script.ui.structure import ChangeSignalConnect
import eve.client.script.ui.structure.structureBrowser.browserUIConst as browserUIConst
from eve.client.script.ui.structure.structureBrowser.filterCont import FilterCont
from eve.client.script.ui.structure.structureBrowser.entries.structureEntry import StructureEntry
from eve.client.script.ui.structure.structureBrowser.controllers.structureEntryController import StructureEntryController
from eve.client.script.ui.structure.structureBrowser.tempUtils import GetGroupingForStructure
from inventorycommon.util import IsNPC
from localization import GetByLabel
import log
OWNER_ANY = 1
OWNER_NPC = 2
OWNER_CORP = 3

class BrowserAllStructures(Container):
    default_name = 'BrowserAllStructures'

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.controller = attributes.structureBrowserController
        self.ChangeSignalConnection(connect=True)
        self.isInitialized = False
        self.serviceChangedTimer = None
        self.serviceChangedTimestamp = gametime.GetWallclockTimeNow()

    def ChangeSignalConnection(self, connect = True):
        signalAndCallback = [(self.controller.on_change_location_range, self.OnLocationRangeChanged),
         (self.controller.on_change_owner_value, self.OnOwnerValueChanged),
         (self.controller.on_text_filter_changed, self.OnTextFilterChanged),
         (self.controller.on_service_settings_changed, self.OnServiceSettingsChanged),
         (self.controller.on_structure_type_changed, self.OnStructureTypeChanged),
         (self.controller.on_structures_changed, self.OnStructuresChanged)]
        ChangeSignalConnect(signalAndCallback, connect)

    def OnTabSelect(self):
        self.LoadPanel()

    def LoadPanel(self):
        self.display = True
        if self.isInitialized:
            self.UpdateScroll()
            return
        self.isInitialized = True
        self.comboCont = FilterCont(name='comboCont', parent=self, structureBrowserController=self.controller)
        self.scroll = Scroll(parent=self, id='AllStructuresScroll')
        self.scroll.GetTabStops = self.GetTabStops
        self.scroll.sr.fixedColumns = StructureEntry.GetFixedColumns()
        self.scroll.OnSelectionChange = self.OnScrollSelectionChange
        self.UpdateScroll()

    def GetTabStops(self, headertabs, idx = None):
        return TabFinder().GetTabStops(self.scroll.sr.nodes, headertabs, StructureEntry, idx=idx)

    def UpdateScroll(self):
        if self.controller.AreServiceFiltersDisbled():
            structureServicesChecked = browserUIConst.ALL_SERVICES
        else:
            structureServicesChecked = self.controller.GetServicesChecked()
        scrollList = self.GetScrollList(structureServicesChecked)
        self.scroll.LoadContent(contentList=scrollList, headers=StructureEntry.GetHeaders(structureServicesChecked), noContentHint=GetByLabel('UI/Structures/Browser/NoStructuresFound'))

    def IsFilteredOut(self, structureController):
        if self._IsFilteredByOwner(structureController):
            return True
        if self._IsFilteredOutByStructureType(structureController):
            return True
        if self._IsFilteredOutByText(structureController):
            return True
        if self._IsFilteredOutByServices(structureController):
            return True
        return False

    def _IsFilteredByOwner(self, structureController):
        ownerValue = self.controller.GetStructureOwnerValue()
        if ownerValue == browserUIConst.OWNER_ANY:
            return False
        ownerID = structureController.GetOwnerID()
        if ownerValue == browserUIConst.OWNER_CORP:
            if ownerID == session.corpid:
                return False
            else:
                return True
        if ownerValue == browserUIConst.OWNER_NPC:
            if IsNPC(ownerID):
                return False
            else:
                return True
        return False

    def _IsFilteredOutByStructureType(self, structureController):
        groupingsChecked = self.controller.GetStructureTypesChecked()
        if browserUIConst.ALL_STRUCTURES in groupingsChecked:
            return False
        structureTypeID = structureController.GetTypeID()
        groupForStructure = GetGroupingForStructure(structureTypeID)
        if groupForStructure in groupingsChecked:
            return False
        else:
            return True

    def _IsFilteredOutByText(self, structureController):
        filterText = self.controller.GetTextFilter()
        if filterText:
            text = structureController.GetName() + structureController.GetOwnerName() + structureController.GetSystemName()
            if text.lower().find(filterText) == -1:
                return True
        return False

    def _IsFilteredOutByServices(self, structureController):
        if self.controller.AreServiceFiltersDisbled():
            return False
        structureServicesChecked = self.controller.GetServicesChecked()
        for serviceID in structureServicesChecked:
            if structureController.HasService(serviceID):
                return False

        return True

    def GetScrollList(self, structureServicesChecked):
        scrollList = []
        structureControllers = self.controller.GetAllStructures()
        for controller in structureControllers:
            if self.IsFilteredOut(controller):
                continue
            node = Bunch(controller=controller, decoClass=StructureEntry, columnSortValues=StructureEntry.GetColumnSortValues(controller, structureServicesChecked), charIndex=controller.GetName(), structureServicesChecked=structureServicesChecked, GetSortValue=StructureEntry.GetSortValue)
            scrollList.append(node)

        return scrollList

    def OnScrollSelectionChange(self, entries):
        pass

    def OnOwnerCombo(self, *args):
        self.UpdateScroll()

    def OnServiceSettingsChanged(self):
        uthread.new(self.OnServiceSettingsChanged_thread)

    def OnServiceSettingsChanged_thread(self):
        DELAY = 500
        recentlyLoaded = gametime.GetTimeDiff(self.serviceChangedTimestamp, gametime.GetWallclockTimeNow()) / const.MSEC < DELAY
        if recentlyLoaded:
            self.serviceChangedTimer = AutoTimer(DELAY, self.DoUpdateScroll)
        else:
            self.DoUpdateScroll()

    def DoUpdateScroll(self):
        self.serviceChangedTimestamp = gametime.GetWallclockTimeNow()
        self.serviceChangedTimer = None
        self.UpdateScroll()

    def OnOwnerValueChanged(self, value):
        self.UpdateScroll()

    def OnLocationRangeChanged(self, value):
        self.UpdateScroll()

    def OnTextFilterChanged(self):
        self.UpdateScroll()

    def OnStructureTypeChanged(self, value):
        self.UpdateScroll()

    def OnStructuresChanged(self):
        self.UpdateScroll()

    def Close(self):
        try:
            self.ChangeSignalConnection(connect=False)
        except Exception as e:
            log.LogError('Failed at closing all structures browser, e = ', e)
        finally:
            self.controller = None
            Container.Close(self)
