#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\structure\structureBrowser\controllers\structureBrowserController.py
from collections import defaultdict, Counter
from eve.client.script.ui.station import stationServiceConst
from eve.client.script.ui.structure.scheduleUtil import GetUniqueSchedules
from eve.client.script.ui.structure.structureBrowser.controllers.structureEntryController import StructureEntryController
from inventorycommon.util import IsWormholeRegion
from localization import GetByLabel
from signals import Signal
import carbonui.const as uiconst
import eve.client.script.ui.structure.structureBrowser.browserUIConst as browserUIConst
import structures

class StructureBrowserController(object):
    __notifyevents__ = ['OnStructureStateChanged',
     'OnStructuresReloaded',
     'OnCorporationStructuresReloaded',
     'OnProfileSettingsChange']

    def __init__(self):
        self.rangeSelected = settings.char.ui.Get(browserUIConst.UI_SETTING_STRUCTUREBROWSER_FILTERS % 'location', const.rangeSolarSystem)
        self.structureOwnerValue = 0
        self.currentTextFilter = ''
        self.structureTypesChecked = settings.char.ui.Get(browserUIConst.UI_SETTING_STRUCTUREBROWSER_FILTERS % 'structureTypes', set([browserUIConst.ALL_STRUCTURES]))
        self.tabSelected = 0
        self.categoryIDSelected = structures.CATEGORY_HULL_DOCKING
        self.profileChanged = False
        self.selectedProfile = browserUIConst.ALL_PROFILES
        self.on_change_location_range = Signal()
        self.on_change_owner_value = Signal()
        self.on_text_filter_changed = Signal()
        self.on_service_settings_changed = Signal()
        self.on_structure_type_changed = Signal()
        self.on_structure_state_changed = Signal()
        self.on_structures_changed = Signal()
        self.on_corp_structures_changed = Signal()
        self.on_category_selected = Signal()
        self.on_profile_selected = Signal()
        self.on_profile_deleted = Signal()
        self.myStructureControllers = {}
        self.allStructuresControllers = {}
        sm.RegisterNotify(self)

    def OnProfileSettingsChange(self, profileIDs):
        currentProfile = self.GetSelectedProfileID()
        if currentProfile in profileIDs:
            if self.HasProfileChanged():
                headerText = GetByLabel('UI/StructureBrowser/ProfileWasModifiedHeader')
                questionText = GetByLabel('UI/StructureBrowser/ProfileWasModifiedBody')
                if eve.Message('CustomQuestion', {'header': headerText,
                 'question': questionText}, uiconst.YESNO) != uiconst.ID_YES:
                    return
            self.selectedProfile = None
            self.SelectProfile(currentProfile, askQuestion=False)

    def GetMyStructures(self):
        structuresInfo = sm.GetService('structureDirectory').GetCorporationStructures()
        stationControllers = self._GetControllersFromStructureList(browserUIConst.IGNORE_RANGE, structuresInfo, self.myStructureControllers)
        return stationControllers

    def GetAllStructures(self):
        structuresInfo = sm.GetService('structureDirectory').GetStructures()
        rangeSelected = self.GetRange()
        stationControllers = self._GetControllersFromStructureList(rangeSelected, structuresInfo, self.allStructuresControllers)
        return stationControllers

    def _GetControllersFromStructureList(self, rangeSelected, structuresInfo, cacheDict):
        cacheDict.clear()
        stationControllers = []

        def IsInRange(info):
            if rangeSelected == browserUIConst.IGNORE_RANGE:
                return True
            if rangeSelected == const.rangeSolarSystem and session.solarsystemid2 != info['solarSystemID']:
                return False
            if rangeSelected == const.rangeConstellation:
                solarsystemInfo = cfg.mapSystemCache.Get(info['solarSystemID'])
                if solarsystemInfo.constellationID != session.constellationid:
                    return False
            return True

        idsToPrime = {eachInfo['structureID'] for eachInfo in structuresInfo.itervalues()}
        idsToPrime.union({eachInfo['solarSystemID'] for eachInfo in structuresInfo.itervalues()})
        cfg.evelocations.Prime(idsToPrime)
        for eachInfo in structuresInfo.itervalues():
            if not IsInRange(eachInfo):
                continue
            sController = StructureEntryController(eachInfo['structureID'], eachInfo['solarSystemID'], eachInfo['structureTypeID'], eachInfo['ownerID'], structureServices=eachInfo['services'], profileID=eachInfo.get('profileID'), currentSchedule=eachInfo.get('currentSchedule', 0), nextSchedule=eachInfo.get('nextSchedule', 0), state=eachInfo.get('state'), unanchoring=eachInfo.get('unanchoring'), fuelExpires=eachInfo.get('fuelExpires'))
            cacheDict[eachInfo['structureID']] = sController
            stationControllers.append(sController)

        return stationControllers

    def GetLocationOptions(self):
        locationOptions = []
        if not IsWormholeRegion(session.regionid):
            locationOptions += [const.rangeRegion, const.rangeConstellation]
        locationOptions += [const.rangeSolarSystem]
        return locationOptions

    def GetRange(self):
        locationOptions = self.GetLocationOptions()
        if self.rangeSelected not in locationOptions:
            self.rangeSelected = locationOptions[0]
        return self.rangeSelected

    def ChangeLocationRange(self, value):
        settingName = browserUIConst.UI_SETTING_STRUCTUREBROWSER_FILTERS % 'location'
        settings.char.ui.Set(settingName, value)
        self.rangeSelected = value
        self.on_change_location_range(value)

    def GetStructureOwnerValue(self):
        return self.structureOwnerValue

    def ChangeStructureOwnerFilter(self, value):
        self.structureOwnerValue = value
        self.on_change_owner_value(value)

    def GetTextFilter(self):
        return self.currentTextFilter

    def TextFilterChanged(self, filterText):
        self.currentTextFilter = filterText
        self.on_text_filter_changed()

    def ToggleAnyService(self):
        settingName = browserUIConst.UI_SETTING_STRUCTUREBROWSER_SERVICEFILTERS_DISABLED
        serviceFilterDisabled = settings.char.ui.Get(settingName, True)
        settings.char.ui.Set(settingName, not serviceFilterDisabled)
        self.on_service_settings_changed()

    def ToggleServiceSetting(self, configName):
        settingName = browserUIConst.UI_SETTING_STRUCTUREBROWSER_SERVICESETTING % configName
        currentSettings = settings.char.ui.Get(settingName, True)
        settings.char.ui.Set(settingName, not currentSettings)
        self.on_service_settings_changed()

    def GetServicesChecked(self):
        serviceIDsChecked = []
        serviceData = self.GetSortedServiceOption()
        for x in serviceData:
            settingName = browserUIConst.UI_SETTING_STRUCTUREBROWSER_SERVICESETTING % x.name
            isChecked = settings.char.ui.Get(settingName, True)
            if isChecked:
                serviceIDsChecked.append(x.name)

        return serviceIDsChecked

    def AreServiceFiltersDisbled(self):
        return settings.char.ui.Get(browserUIConst.UI_SETTING_STRUCTUREBROWSER_SERVICEFILTERS_DISABLED, True)

    def GetStructureTypesChecked(self):
        return self.structureTypesChecked

    def ToggleStructureTypeChecked(self, value):
        if value in self.structureTypesChecked:
            self.structureTypesChecked.remove(value)
        else:
            self.structureTypesChecked.add(value)
        settingName = browserUIConst.UI_SETTING_STRUCTUREBROWSER_FILTERS % 'structureTypes'
        settings.char.ui.Set(settingName, self.structureTypesChecked)
        self.on_structure_type_changed(value)

    def GetSortedServiceOption(self):
        serviceData = [ x for x in stationServiceConst.serviceData ]
        serviceData.sort(key=lambda x: x.label)
        return serviceData

    def GetUniqueSchedulesForCorpStructures(self):
        myStructures = self.GetMyStructures()
        schedulesInUse = []
        for eachStructure in myStructures:
            schedulesInUse.append(eachStructure.GetCurrentSchedule())
            if eachStructure.GetCurrentSchedule() != eachStructure.GetNextWeekSchedule():
                schedulesInUse.append(eachStructure.GetNextWeekSchedule())

        return GetUniqueSchedules(schedulesInUse)

    def SetTabSelected(self, tabSelected):
        self.tabSelected = tabSelected

    def GetSelectedTab(self):
        return self.tabSelected

    def OnStructureStateChanged(self, solarSystemID, structureID, state):
        sController = self.myStructureControllers.get(structureID, None)
        if sController is None:
            return
        sController.StructureStateChanged(structureID, state)

    def OnStructuresReloaded(self):
        self.on_structures_changed()

    def OnCorporationStructuresReloaded(self):
        self.on_corp_structures_changed()

    def SelectCategory(self, categoryID):
        self.categoryIDSelected = categoryID
        self.on_category_selected(categoryID)

    def GetSelectedCategory(self):
        return self.categoryIDSelected

    def SetProfileChangedValue(self, value):
        self.profileChanged = value

    def HasProfileChanged(self):
        return self.profileChanged

    def PlayerWantsToLeaveProfile(self):
        if not self.HasProfileChanged():
            return True
        headerText = GetByLabel('UI/StructureBrowser/UnsavedChanges')
        questionText = GetByLabel('UI/StructureBrowser/UnsavedChangesQuestion')
        ret = eve.Message('CustomQuestion', {'header': headerText,
         'question': questionText}, uiconst.YESNO)
        if ret == uiconst.ID_YES:
            return True
        return False

    def SelectProfile(self, profileID, sendSignal = True, askQuestion = True):
        validProfileIDs = sm.GetService('structureControllers').GetValidProfileIDs()
        if profileID not in validProfileIDs:
            profileID = browserUIConst.ALL_PROFILES
        newProfileSelected = self.selectedProfile != profileID
        if askQuestion and newProfileSelected and not self.PlayerWantsToLeaveProfile():
            return
        if newProfileSelected:
            self.SetProfileChangedValue(False)
        self.selectedProfile = profileID
        if sendSignal:
            self.on_profile_selected(profileID)

    def GetSelectedProfileID(self):
        return self.selectedProfile

    def ProfileDeleted(self, profileID):
        if self.GetSelectedProfileID() == profileID:
            selectedProfileChanged = True
            self.selectedProfile = browserUIConst.ALL_PROFILES
        else:
            selectedProfileChanged = False
        self.on_profile_deleted(profileID, selectedProfileChanged)

    def SetProfileSettingsSelected(self):
        settings.user.tabgroups.Set('StructureBrowser', 1)
        settings.user.tabgroups.Set('profile_structuresAndsettings', 1)
