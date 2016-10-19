#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\structure\structureBrowser\filterCont.py
from carbonui.primitives.container import Container
from eve.client.script.ui.control.eveCombo import Combo
from eve.client.script.ui.control.utilMenu import UtilMenu
from eve.client.script.ui.quickFilter import QuickFilterEdit
from eve.client.script.ui.station import stationServiceConst
import eve.client.script.ui.structure.structureBrowser.browserUIConst as browserUIConst
import evetypes
from inventorycommon.util import IsWormholeRegion
from localization import GetByLabel
import carbonui.const as uiconst
locationToName = {const.rangeRegion: GetByLabel('UI/Common/LocationTypes/Region'),
 const.rangeConstellation: GetByLabel('UI/Common/LocationTypes/Constellation'),
 const.rangeSolarSystem: GetByLabel('UI/Common/LocationTypes/SolarSystem')}

class FilterCont(Container):
    __notifyevents__ = ['OnSessionChanged']
    default_height = 30
    default_align = uiconst.TOTOP

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.controller = attributes.structureBrowserController
        self.ConstructUI()
        sm.RegisterNotify(self)

    def ConstructUI(self):
        self.uiLeft = 0
        self.AddOwnerCombo()
        self.AddLocationCombo()
        self.AddStructureWheel()
        self.AddServiceWheel()
        self.AddFilterBox()

    def AddOwnerCombo(self):
        ownerOptions = [(GetByLabel('UI/Industry/AllFacilities'), browserUIConst.OWNER_ANY), (GetByLabel('UI/Industry/PublicFacilities'),
          browserUIConst.OWNER_NPC,
          None,
          'res:/UI/Texture/Classes/Inventory/readOnly.png'), (GetByLabel('UI/Industry/CorpOwnedFacilities'),
          browserUIConst.OWNER_CORP,
          None,
          'res:/UI/Texture/Classes/Industry/iconCorp.png')]
        selected = self.controller.GetStructureOwnerValue()
        self.ownerCombo = Combo(name='ownerCombo', parent=self, align=uiconst.CENTERLEFT, prefsKey='StructureBrowserOwner', callback=self.ChangeStructureOwnerFilter, options=ownerOptions, select=selected, padRight=4, top=-2, left=self.uiLeft)
        self.uiLeft = self.ownerCombo.left + self.ownerCombo.width + 10

    def AddLocationCombo(self):
        locationOptions = self.GetLocationOptions()
        selected = self.controller.GetRange()
        self.locationRange = Combo(label='', parent=self, options=locationOptions, name='locationRange', select=selected, callback=self.ChangeLocationRange, left=self.uiLeft, top=-2, align=uiconst.CENTERLEFT)
        self.uiLeft = self.locationRange.left + self.locationRange.width + 10

    def GetLocationOptions(self):
        locationOptions = []
        locationIDs = self.controller.GetLocationOptions()
        for locationID in locationIDs:
            text = locationToName[locationID]
            locationOptions.append((text, locationID))

        return locationOptions

    def AddStructureWheel(self):
        structureTypeMenu = UtilMenu(menuAlign=uiconst.TOPLEFT, parent=self, align=uiconst.CENTERLEFT, pos=(self.uiLeft,
         -2,
         16,
         16), GetUtilMenu=self.GetStructureTypeMenu, texturePath='res:/UI/Texture/SettingsCogwheel.png', iconSize=18, label=GetByLabel('UI/Structures/Browser/StructureType'))
        self.uiLeft = structureTypeMenu.left + structureTypeMenu.width + 10

    def AddServiceWheel(self):
        serviceMenu = UtilMenu(menuAlign=uiconst.TOPLEFT, parent=self, align=uiconst.CENTERLEFT, pos=(self.uiLeft,
         -2,
         16,
         16), GetUtilMenu=self.GetServiceMenu, texturePath='res:/UI/Texture/SettingsCogwheel.png', iconSize=18, label=GetByLabel('UI/Structures/Browser/ServiceFilter'))
        self.uiLeft = serviceMenu.left + serviceMenu.width + 10

    def AddFilterBox(self):
        text = self.controller.GetTextFilter()
        self.filterEdit = QuickFilterEdit(name='searchField', parent=self, hinttext=GetByLabel('UI/Inventory/Filter'), maxLength=64, align=uiconst.CENTERRIGHT, OnClearFilter=self.OnFilterEditCleared, padRight=4, text=text)
        self.filterEdit.ReloadFunction = self.OnFilterEdit

    def GetServiceMenu(self, menuParent):
        serviceData = self.controller.GetSortedServiceOption()
        serviceFilterDisabled = self.controller.AreServiceFiltersDisbled()
        menuParent.AddCheckBox(text=GetByLabel('UI/Structures/Browser/DisableServiceFilter'), checked=serviceFilterDisabled, callback=self.AnyServiceCallback)
        menuParent.AddDivider()
        for data in serviceData:
            settingName = browserUIConst.UI_SETTING_STRUCTUREBROWSER_SERVICESETTING % data.name
            currentSettings = settings.char.ui.Get(settingName, True)
            if serviceFilterDisabled:
                callbackInfo = None
            else:
                callbackInfo = (self.ServiceCallback, data.name)
            menuParent.AddCheckBox(text=data.label, checked=currentSettings, callback=callbackInfo)

    def AnyServiceCallback(self):
        self.controller.ToggleAnyService()

    def ServiceCallback(self, configName):
        self.controller.ToggleServiceSetting(configName)

    def GetStructureTypeMenu(self, menuParent):
        checkedOptions = self.controller.GetStructureTypesChecked()
        showingAll = browserUIConst.ALL_STRUCTURES in checkedOptions
        menuParent.AddCheckBox(text=GetByLabel('UI/Structures/Browser/AnyStructureType'), checked=showingAll, callback=(self.StructureTypeCallback, browserUIConst.ALL_STRUCTURES))
        menuParent.AddDivider()
        for groupingID, typeIDInfo in browserUIConst.CITADEL_TYPEIDS.iteritems():
            nameTypeID, typeIDs = typeIDInfo
            label = evetypes.GetName(nameTypeID)
            isChceked = groupingID in checkedOptions
            if showingAll:
                callbackInfo = None
            else:
                callbackInfo = (self.StructureTypeCallback, groupingID)
            menuParent.AddCheckBox(text=label, checked=isChceked, callback=callbackInfo)

    def StructureTypeCallback(self, configName):
        self.controller.ToggleStructureTypeChecked(configName)

    def ChangeStructureOwnerFilter(self, cb, label, value):
        self.controller.ChangeStructureOwnerFilter(value)

    def ChangeLocationRange(self, cb, label, value):
        self.controller.ChangeLocationRange(value)

    def OnFilterEdit(self):
        self.RecordTextFieldChanges()

    def OnFilterEditCleared(self):
        self.RecordTextFieldChanges()

    def RecordTextFieldChanges(self):
        filterText = self.filterEdit.GetValue().strip().lower()
        self.controller.TextFilterChanged(filterText)

    def OnSessionChanged(self, isremote, sess, change):
        if 'regionid' in change:
            oldRegionID, newRegionID = change['regionid']
            if IsWormholeRegion(oldRegionID) or IsWormholeRegion(newRegionID):
                self.SetLocationOptions()

    def SetLocationOptions(self):
        selected = self.controller.GetRange()
        locationOptions = self.GetLocationOptions()
        self.locationRange.LoadOptions(locationOptions, select=selected)
