#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\fittingGhost\leftPanel.py
from collections import Counter
import uthread
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.flowcontainer import FlowContainer, CONTENT_ALIGN_LEFT, CONTENT_ALIGN_RIGHT
from carbonui.primitives.frame import Frame
from carbonui.util.sortUtil import SortListOfTuples
from eve.client.script.ui.control.buttons import Button, ToggleButtonGroup
from eve.client.script.ui.control.eveIcon import Icon
from eve.client.script.ui.control.eveLabel import EveLabelMedium
from eve.client.script.ui.control.eveScroll import Scroll
import carbonui.const as uiconst
from eve.client.script.ui.control.utilMenu import UtilMenu
from eve.client.script.ui.shared.comtool.lscchannel import ACTION_ICON
from eve.client.script.ui.shared.export import ImportLegacyFittingsWindow, ImportFittingsWindow, ExportFittingsWindow
from eve.client.script.ui.shared.fittingGhost import BROWSE_MODULES, BROWSE_CHARGES
from eve.client.script.ui.shared.fittingGhost.browsers.chargesBrowserUtil import ChargeBrowserListProvider
from eve.client.script.ui.shared.fittingGhost.browsers.fittingBrowser import FittingBrowserListProvider
from eve.client.script.ui.shared.fittingGhost.browsers.hardwareBrowser import HardwareBrowserListProvider
from eve.client.script.ui.shared.fittingGhost.browsers.searchBrowser import SearchBrowserListProvider
from eve.client.script.ui.shared.fittingGhost.filterBtn import AddFittingFilterButtons, AddHardwareButtons, SetSettingForFilterBtns, BTN_TYPE_RESOURCES, BTN_TYPE_PERSONAL_FITTINGS, BTN_TYPE_CORP_FITTINGS
from eve.client.script.ui.shared.fittingGhost.ghostFittingPanels.chargeButtons import ModuleChargeButton
from eve.client.script.ui.shared.fittingGhost.missingItemsPopup import BuyAllMessageBox
from eve.client.script.ui.shared.fittingGhost.searchCont import SearchCont, FITTING_MODE, HARDWARE_MODE
from eve.client.script.ui.shared.fittingGhost.toggleButtonGhost import ToggleButtonGhost
from eve.client.script.ui.shared.fittingMgmtWindow import FittingMgmt, OpenOrLoadMultiFitWnd
from eve.client.script.ui.station.fitting.fittingTooltipUtils import SetFittingTooltipInfo
from eve.client.script.ui.structure import ChangeSignalConnect
from eve.common.script.sys.eveCfg import GetActiveShip, IsDocked
import evetypes
import inventorycommon.typeHelpers
from inventorycommon.util import IsModularShip
from localization import GetByLabel
import telemetry
import log
BROWSE_FITTINGS = 'fittings'
BROWSE_HARDWARE = 'hardware'
BROWSER_BTN_ID_CONFIG = 'fitting_browserBtnID'
HW_BTN_ID_CONFIG = 'fitting_hardwarBrowserBtnID'

class LeftPanel(Container):
    default_clipChildren = True
    default_padBottom = 4
    default_padLeft = 10
    __notifyevents__ = ['OnFittingsUpdated',
     'OnFittingDeleted',
     'OnSkillFilteringUpdated',
     'OnSlotDblClicked']

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.fittingSvc = sm.GetService('fittingSvc')
        self.configName = attributes.configName
        self.controller = attributes.controller
        self.ChangeSignalConnection()
        self.loaded = False
        padding = 0
        self.ammoShowingForType = None
        btnCont = FlowContainer(parent=self, align=uiconst.TOBOTTOM, contentAlignment=CONTENT_ALIGN_RIGHT, padTop=4, padRight=0, contentSpacing=uiconst.BUTTONGROUPMARGIN)
        self.fitBtn = Button(parent=btnCont, label='Fit Ship', func=self.FitShip, align=uiconst.NOALIGN)
        self.builtShipBtn = Button(parent=btnCont, label=GetByLabel('UI/Fitting/FittingWindow/BuildShip'), func=self.BuildShip, align=uiconst.NOALIGN)
        self.saveBtn = Button(parent=btnCont, label=GetByLabel('UI/Fitting/FittingWindow/SaveFitAs'), func=self.SaveFitting, align=uiconst.NOALIGN)
        SetFittingTooltipInfo(targetObject=self.saveBtn, tooltipName='SaveFitting', includeDesc=False)
        self.AdjustButtons()
        self.btnGroup = ToggleButtonGroup(name='fittingToggleBtnGroup', parent=self, align=uiconst.TOTOP, callback=self.BrowserSelected, height=40, idx=-1)
        self.AddExportImportMenu()
        self.AddSearchFields()
        self.AddFilterCont()
        self.hwBrowserBtns = self.AddHardwareSelcetionCont()
        self.AddFittingFilterButtons()
        self.hardwareFilterBtns = self.AddHardwareFilterButtons()
        self.AddChargeFilterButtons()
        self.browserBtns = {}
        self.moduleChargeButtons = {}
        for btnID, labelPath, iconPath, dblClickCallback in ((BROWSE_FITTINGS,
          'UI/Fitting/FittingWindow/ShipAndFittings',
          'res:/UI/Texture/classes/Fitting/tabFittings.png',
          self.LoadFittingSetup), (BROWSE_HARDWARE,
          'UI/Fitting/FittingWindow/Hardware',
          'res:/UI/Texture/classes/Fitting/tabHardware.png',
          None)):
            btn = self.btnGroup.AddButton(btnID, GetByLabel(labelPath), iconPath=iconPath, btnClass=ToggleButtonGhost)
            self.browserBtns[btnID] = btn
            if dblClickCallback:
                btn.OnDblClick = dblClickCallback

        self.scroll = Scroll(parent=self, align=uiconst.TOALL, padding=(padding,
         2,
         padding,
         0))
        self.scroll.sr.content.OnDropData = self.OnDropData
        sm.RegisterNotify(self)

    def ChangeSignalConnection(self, connect = True):
        signalAndCallback = [(self.controller.on_new_itemID, self.OnSimulatedShipLoaded), (self.controller.on_slots_changed, self.OnSlotsChanged), (self.controller.on_simulation_state_changed, self.OnSimulationStateChanged)]
        ChangeSignalConnect(signalAndCallback, connect)

    def AddExportImportMenu(self):
        m = UtilMenu(menuAlign=uiconst.BOTTOMLEFT, parent=self, align=uiconst.BOTTOMLEFT, label=GetByLabel('UI/Fitting/FittingWindow/ImportAndExport'), labelAlign=uiconst.CENTERRIGHT, GetUtilMenu=self.GetExportImportMenu, texturePath='res:/ui/texture/icons/73_16_50.png', left=-8)

    def GetExportImportMenu(self, menuParent, *args):
        if boot.region != 'optic':
            text = GetByLabel('UI/Fitting/FittingWindow/FittingManagement/ImportFromClipboard')
            hint = GetByLabel('UI/Fitting/FittingWindow/FittingManagement/ImportFromClipboardHint')
            menuParent.AddIconEntry(icon=ACTION_ICON, text=text, hint=hint, callback=sm.GetService('fittingSvc').ImportFittingFromClipboard)
            menuParent.AddDivider()
        menuParent.AddIconEntry(icon=ACTION_ICON, text=GetByLabel('UI/Commands/Import'), callback=self.ImportFittings)
        menuParent.AddIconEntry(icon=ACTION_ICON, text=GetByLabel('UI/Commands/Export'), callback=self.ExportFittings)

    def ImportFittings(self, *args):
        ImportFittingsWindow.Open()

    def ExportFittings(self, *args):
        isCorp = False
        ExportFittingsWindow.Open(isCorp=isCorp)

    def Load(self):
        if self.loaded:
            return
        self.hardwareBtnGroup.SelectByID(settings.user.ui.Get(HW_BTN_ID_CONFIG, BROWSE_MODULES))
        self.btnGroup.SelectByID(settings.user.ui.Get(BROWSER_BTN_ID_CONFIG, BROWSE_FITTINGS))
        self.loaded = True

    @telemetry.ZONE_METHOD
    def AddSearchFields(self):
        self.searchparent = SearchCont(name='searchparent', parent=self, align=uiconst.TOTOP, height=18, padding=(0, 4, 0, 4), searchFunc=self.Search)

    def ReloadBrowser(self):
        btnID = settings.user.ui.Get(BROWSER_BTN_ID_CONFIG, BROWSE_FITTINGS)
        self.BrowserSelected(btnID)

    def OnSlotDblClicked(self, flagID, *args):
        SetSettingForFilterBtns(flagID, self.hardwareFilterBtns)
        btn = self.browserBtns.get(BROWSE_HARDWARE)
        if not btn.IsSelected():
            btn.OnClick()
        hwBtn = self.hwBrowserBtns.get(BROWSE_MODULES)
        hwBtn.OnClick()

    @telemetry.ZONE_METHOD
    def BrowserSelected(self, btnID, *args):
        settings.user.ui.Set(BROWSER_BTN_ID_CONFIG, btnID)
        if btnID == BROWSE_FITTINGS:
            self.chargeFilterCont.display = False
            self.hardwareFilterCont.display = False
            self.hardwarSelectionCont.display = False
            self.searchparent.ChangeSearchMode(FITTING_MODE)
            self.ShowOrHideElements(display=False)
            self.LoadFittings()
        elif btnID == BROWSE_HARDWARE:
            self.hardwarSelectionCont.display = True
            self.searchparent.ChangeSearchMode(HARDWARE_MODE)
            self.AddHardwareForChargesButtons()
            self.ShowOrHideElements(display=True)
            self.LoadHardware()

    def ShowOrHideElements(self, display = True):
        self.hardwareFilterCont.display = display
        self.fittingFilterCont.display = not display
        self.fittingFilterCont.display = not display

    def OnFittingDeleted(self, ownerID, fitID):
        self.OnFittingsUpdated()

    def OnFittingsUpdated(self):
        if settings.user.ui.Get(BROWSER_BTN_ID_CONFIG, BROWSE_FITTINGS) == BROWSE_FITTINGS:
            self.ReloadBrowser()

    def OnSkillFilteringUpdated(self):
        if IsHardwareTabSelected():
            self.ReloadBrowser()

    def LoadFittings(self):
        scrolllist = self.GetFittingScrolllist()
        self.searchparent.display = True
        self.scroll.Load(contentList=scrolllist, scrolltotop=0)

    @telemetry.ZONE_METHOD
    def LoadHardware(self):
        self.scroll.HideLoading()
        self.chargeFilterCont.display = False
        self.hardwareFilterCont.display = False
        if IsHardwareTabSelected() and IsChargeTabSelected():
            self.searchparent.display = False
            self.AddHardwareForChargesButtons()
            return
        self.searchparent.display = True
        self.hardwareFilterCont.display = True
        self.ChangeResourceBtn()
        uthread.new(self.LoadHardware_thread)

    @telemetry.ZONE_METHOD
    def LoadHardware_thread(self):
        self.scroll.Load(contentList=[])
        self.scroll.ShowLoading()
        resourceBtn = None
        if settings.user.ui.Get('fitting_filter_hardware_resources', False):
            resourceBtn = self.hardwareFilterBtns.get(BTN_TYPE_RESOURCES, None)
            if resourceBtn:
                resourceBtn.ShowLoading()
        scrolllist = self._GetHardwareScrollList()
        if IsModuleTabSelected() and IsHardwareTabSelected():
            self.scroll.Load(contentList=scrolllist, scrolltotop=0, noContentHint=GetByLabel('UI/Fitting/FittingWindow/NoModulesFound'))
        self.scroll.HideLoading()
        if resourceBtn:
            resourceBtn.HideLoading()

    def _GetHardwareScrollList(self):
        if settings.user.ui.Get('fitting_hardwareSearchField', ''):
            scrolllist = self.GetSearchResults()
        else:
            hardwareBrowserListProvider = HardwareBrowserListProvider(self.fittingSvc.searchFittingHelper, self.OnDropData)
            scrolllist = hardwareBrowserListProvider.GetGroupListForBrowse(marketGroupID=const.marketCategoryShipEquipment)
            scrolllist += hardwareBrowserListProvider.GetGroupListForBrowse(marketGroupID=const.marketCategoryShipModifications)
            scrolllist += hardwareBrowserListProvider.GetGroupListForBrowse(marketGroupID=const.marketCategoryDrones)
            scrolllist += self.GetStructureGroup()
        return scrolllist

    def GetStructureGroup(self):
        from eve.client.script.ui.control import entries as listentry
        label = 'Structure'
        data = {'GetSubContent': self.GetStructureGroupSubContent,
         'label': label,
         'id': ('ghostfitting_group', 'structure'),
         'showlen': 0,
         'sublevel': 0,
         'showicon': 'hide',
         'state': 'locked',
         'BlockOpenWindow': True}
        return [listentry.Get('Group', data=data)]

    def GetStructureGroupSubContent(self, nodedate, *args):
        hardwareBrowserListProvider = HardwareBrowserListProvider(self.fittingSvc.searchFittingHelper, self.OnDropData)
        scrolllist = hardwareBrowserListProvider.GetGroupListForBrowse(marketGroupID=const.marketCategoryStructureEquipment, sublevel=1)
        scrolllist += hardwareBrowserListProvider.GetGroupListForBrowse(marketGroupID=const.marketCategoryStructureModifications, sublevel=1)
        return scrolllist

    def ExitSimulation(self, *args):
        sm.GetService('fittingSvc').SetSimulationState(False)
        shipID = GetActiveShip()
        sm.GetService('ghostFittingSvc').SendOnSimulatedShipLoadedEvent(shipID, None)

    def LoadCurrentShip(self, *args):
        sm.GetService('ghostFittingSvc').LoadCurrentShip()

    def SaveFitting(self, *args):
        return self.fittingSvc.SaveFitting()

    def FitShip(self, *args):
        fittingSvc = sm.GetService('fittingSvc')
        if not fittingSvc.IsShipSimulated():
            return
        clientDL = sm.GetService('clientDogmaIM').GetDogmaLocation()
        fittingDL = sm.GetService('clientDogmaIM').GetFittingDogmaLocation()
        actualShip = clientDL.GetShip()
        simulatedShip = fittingDL.GetShip()
        if actualShip.typeID != simulatedShip.typeID:
            UserError('CustomNotify', {'notify': "Actual ship and simulated ship don't match"})
        fitting = fittingSvc.GetFittingForCurrentInWnd(putModuleAmmoInHangar=False)
        failedToLoad = fittingSvc.LoadFitting(fitting, getFailedDict=True) or {}
        failedToLoadCounter = Counter({x[0]:x[1] for x in failedToLoad})
        simulated_chargeTypesAndQtyByFlagID = fittingSvc.GetChargesAndQtyByFlag(simulatedShip.GetFittedItems().values())
        ammoFailedToLoad = fittingSvc.RemoveAndLoadChargesFromSimulatedShip(clientDL, actualShip.itemID, simulated_chargeTypesAndQtyByFlagID)
        faildToLoadInfo = failedToLoadCounter + Counter(ammoFailedToLoad)
        if faildToLoadInfo:
            self.OpenBuyAllBox(faildToLoadInfo)

    def OpenBuyAllBox(self, faildToLoadInfoCounters):
        faildToLoadInfo = dict(faildToLoadInfoCounters)
        BuyAllMessageBox.Open(missingText=GetByLabel('UI/Fitting/MissingItemsHeader'), faildToLoadInfo=faildToLoadInfo)

    def BuildShip(self, *args):
        fitting = sm.GetService('fittingSvc').GetFittingForCurrentInWnd()
        if not fitting.fitData:
            eve.Message('uiwarning03')
            return
        wnd = OpenOrLoadMultiFitWnd(fitting)
        wnd.Maximize()

    def GetFittingScrolllist(self, *args):
        fittingListProvider = FittingBrowserListProvider(self.OnDropData)
        return fittingListProvider.GetFittingScrolllist()

    @telemetry.ZONE_METHOD
    def Search(self, settingConfig, searchString):
        settings.user.ui.Set(settingConfig, searchString)
        self.ReloadBrowser()

    def LoadFittingSetup(self, *args):
        if sm.GetService('fittingSvc').HasLegacyClientFittings():
            wnd = ImportLegacyFittingsWindow.Open()
        else:
            wnd = FittingMgmt.Open()
        if wnd is not None and not wnd.destroyed:
            wnd.Maximize()

    def OnSimulatedShipLoaded(self, *args):
        self.AdjustButtons()

    def AdjustButtons(self):
        self._SetBtnStates()
        self.fitBtn.display = False
        self.builtShipBtn.display = False
        if self.controller.IsSimulated():
            if sm.GetService('ghostFittingSvc').IsSimulatingCurrentShipType():
                self.fitBtn.display = True
            else:
                self.builtShipBtn.display = True

    def _SetBtnStates(self):
        shipItem = self.controller.dogmaLocation.GetShip()
        shipTypeID = shipItem.typeID
        self.fitBtn.Disable()
        self.builtShipBtn.Disable()
        if IsDocked():
            self.fitBtn.Enable()
            if not IsModularShip(shipTypeID):
                self.builtShipBtn.Enable()

    @telemetry.ZONE_METHOD
    def AddHardwareForChargesButtons(self):
        self.chargeFilterCont.display = True
        self.hardwareFilterCont.display = False
        self.chargeFilterCont.Flush()
        Container(name='scaler', parent=self.chargeFilterCont, pos=(0, 0, 0, 30), align=uiconst.NOALIGN)
        hardware = self.GetHardware()
        self.moduleChargeButtons.clear()
        infoSvc = sm.GetService('info')
        for moduleTypeID in hardware:
            chargeTypeIDs = infoSvc.GetUsedWithTypeIDs(moduleTypeID)
            if not chargeTypeIDs:
                continue
            moduleName = evetypes.GetName(moduleTypeID)
            cont = ModuleChargeButton(parent=self.chargeFilterCont, pos=(0, 0, 30, 30), align=uiconst.NOALIGN, state=uiconst.UI_NORMAL, moduleTypeID=moduleTypeID, onClickFunc=self.OnHardwareIconClicked, usedWithChargesIDs=chargeTypeIDs)
            cont.hint = moduleName
            self.moduleChargeButtons[moduleTypeID] = cont

        btnSelected = self.moduleChargeButtons.get(self.ammoShowingForType, None)
        if not btnSelected and self.moduleChargeButtons:
            btnSelected = self.moduleChargeButtons.values()[0]
        if btnSelected:
            btnSelected.OnClick()
        else:
            self.scroll.Load(contentList=[], noContentHint=GetByLabel('UI/Fitting/FittingWindow/NoChargesFound'))

    def OnHardwareIconClicked(self, moduleTypeID, chargeTypeIDs):
        self.ammoShowingForType = moduleTypeID
        for btn in self.moduleChargeButtons.itervalues():
            if btn.GetModuleType() == moduleTypeID:
                btn.SetSelected()
            else:
                btn.SetDeselected()

        self.LoadChargesScrollList(moduleTypeID, chargeTypeIDs)

    def LoadChargesScrollList(self, moduleTypeID, chargeTypeIDs):
        provider = ChargeBrowserListProvider(dblClickFunc=self.TryFit, onDropDataFunc=self.OnDropData, reloadFunc=self.ReloadBrowser)
        scrolllist = provider.GetChargesScrollList(moduleTypeID, chargeTypeIDs)
        self.scroll.Load(contentList=scrolllist, noContentHint=GetByLabel('UI/Fitting/FittingWindow/NoChargesFound'))

    def TryFit(self, entry, moduleTypeID, ammoTypeID):
        ghostFittingSvc = sm.GetService('ghostFittingSvc')
        ghostFittingSvc.TryFitAmmoTypeToAll(moduleTypeID, ammoTypeID)

    def GetHardware(self):
        dogmaLocation = self.controller.GetDogmaLocation()
        shipDogmaItem = dogmaLocation.GetShip()
        hardwareDict = {}
        for module in shipDogmaItem.GetFittedItems().itervalues():
            typeID = module.typeID
            if self.IsCharge(typeID):
                continue
            flagID = module.flagID
            flagInHardware = hardwareDict.get(typeID, None)
            if flagInHardware:
                flagID = min(flagInHardware, flagID)
            hardwareDict[typeID] = flagID

        hardwareList = [ (flagID, typeID) for typeID, flagID in hardwareDict.iteritems() ]
        return SortListOfTuples(hardwareList, reverse=True)

    def IsCharge(self, typeID):
        return evetypes.GetCategoryID(typeID) == const.categoryCharge

    def OnSlotsChanged(self):
        if not IsHardwareTabSelected():
            return
        if not IsChargeTabSelected():
            return
        self.AddHardwareForChargesButtons()

    def OnSimulationStateChanged(self, inSimulation):
        if IsModuleTabSelected() and IsHardwareTabSelected() and settings.user.ui.Get('fitting_filter_hardware_resources', False):
            self.LoadHardware()
        self.ChangeResourceBtn()

    def OnDropData(self, dragObj, nodes):
        node = nodes[0]
        itemKey = node.itemID
        ghostFittingSvc = sm.GetService('ghostFittingSvc')
        ghostFittingSvc.UnfitModule(itemKey)
        ghostFittingSvc.SendFittingSlotsChangedEvent()

    @telemetry.ZONE_METHOD
    def AddFilterCont(self):
        self.filterCont = ContainerAutoSize(name='filterCont', parent=self, align=uiconst.TOTOP, padding=(0, 0, 0, 6))

    @telemetry.ZONE_METHOD
    def AddHardwareSelcetionCont(self):
        self.hardwarSelectionCont = Container(name='hardwarSelectionCont', parent=self, align=uiconst.TOTOP, height=20, padding=(0, 4, 0, 4))
        btnDict = {}
        self.hardwareBtnGroup = ToggleButtonGroup(name='fittingToggleBtnGroup', parent=self.hardwarSelectionCont, align=uiconst.TOTOP, callback=self.ChangeHardwareGroupSelected, height=20, idx=-1)
        for btnID, label in ((BROWSE_MODULES, 'UI/Fitting/FittingWindow/Modules'), (BROWSE_CHARGES, 'UI/Fitting/FittingWindow/Charges')):
            btn = self.hardwareBtnGroup.AddButton(btnID, GetByLabel(label), btnClass=ToggleButtonGhost)
            btnDict[btnID] = btn

        return btnDict

    def ChangeHardwareGroupSelected(self, btnID, *args):
        settings.user.ui.Set(HW_BTN_ID_CONFIG, btnID)
        self.LoadHardware()

    @telemetry.ZONE_METHOD
    def AddHardwareFilterButtons(self):
        self.hardwareFilterCont = FlowContainer(parent=self.filterCont, align=uiconst.TOTOP, contentAlignment=CONTENT_ALIGN_LEFT, padTop=4, contentSpacing=uiconst.BUTTONGROUPMARGIN)
        return AddHardwareButtons(self.hardwareFilterCont, 'fitting_filter_hardware_%s', self.HardwareFilterClicked, self.GetHardwareMenu, hintFunc=self.GetFilterHint)

    @telemetry.ZONE_METHOD
    def AddChargeFilterButtons(self):
        self.chargeFilterCont = FlowContainer(parent=self.filterCont, align=uiconst.TOTOP, contentAlignment=CONTENT_ALIGN_LEFT, padTop=4, contentSpacing=uiconst.BUTTONGROUPMARGIN)

    @telemetry.ZONE_METHOD
    def AddFittingFilterButtons(self):
        self.fittingFilterCont = FlowContainer(name='fittingFilterCont', parent=self.filterCont, align=uiconst.TOTOP, contentAlignment=CONTENT_ALIGN_LEFT, padTop=4, contentSpacing=uiconst.BUTTONGROUPMARGIN)
        AddFittingFilterButtons(self.fittingFilterCont, 'fitting_filter_ship_%s', self.FittingFilterClicked, hintFunc=self.GetFilterHint)

    def FittingFilterClicked(self, filterBtn, buttonType):
        self.FilterButtonClicked(filterBtn)
        self.LoadFittings()

    def HardwareFilterClicked(self, filterBtn, buttonType):
        self.FilterButtonClicked(filterBtn)
        self.LoadHardware()

    def GetHardwareMenu(self, filterBtn):
        m = []
        if filterBtn.buttonType == BTN_TYPE_RESOURCES:
            settingName = 'fitting_filter_resourcesOnOutput'
            onTotalOutput = settings.user.ui.Get(settingName, True)
            if onTotalOutput:
                text = GetByLabel('UI/Fitting/FittingWindow/FilterResourcesSettingRemaining')
            else:
                text = GetByLabel('UI/Fitting/FittingWindow/FilterResourcesSettingTotal')
            m += [(text, self.ToggleHardwareSetting, (settingName,))]
        return m

    def GetFilterHint(self, filterBtn):
        if filterBtn.buttonType == BTN_TYPE_RESOURCES:
            onTotalOutput = settings.user.ui.Get('fitting_filter_resourcesOnOutput', True)
            if onTotalOutput:
                typeOfFiltering = GetByLabel('UI/Fitting/FittingWindow/FilterResourcesTotal')
            else:
                typeOfFiltering = GetByLabel('UI/Fitting/FittingWindow/FilterResourcesRemaining')
            hint = GetByLabel(filterBtn.hintLabelPath, typeOfFiltering=typeOfFiltering)
            if not self.controller.IsSimulated():
                hint += '<br><br>%s' % GetByLabel('UI/Fitting/FittingWindow/OnlyAvailableInSimulation')
            return hint
        elif filterBtn.buttonType == BTN_TYPE_PERSONAL_FITTINGS:
            personalFittings = self.fittingSvc.GetFittings(session.charid)
            numFittings = '(%s/%s)' % (len(personalFittings), const.maxCharFittings)
            return GetByLabel(filterBtn.hintLabelPath, numFittings=numFittings)
        elif filterBtn.buttonType == BTN_TYPE_CORP_FITTINGS:
            corpFittings = self.fittingSvc.GetFittings(session.corpid)
            numFittings = '(%s/%s)' % (len(corpFittings), const.maxCorpFittings)
            return GetByLabel(filterBtn.hintLabelPath, numFittings=numFittings)
        else:
            return GetByLabel(filterBtn.hintLabelPath)

    def ToggleHardwareSetting(self, settingName):
        currentValue = settings.user.ui.Get(settingName, True)
        newValue = not currentValue
        settings.user.ui.Set(settingName, newValue)
        self.LoadHardware()

    def FilterButtonClicked(self, filterBtn):
        btnSettingConfig = filterBtn.btnSettingConfig
        filterOn = filterBtn.IsChecked()
        settings.user.ui.Set(btnSettingConfig, filterOn)

    def GetSearchResults(self):
        listProvider = SearchBrowserListProvider(self.fittingSvc.searchFittingHelper, self.OnDropData)
        scrolllist = listProvider.GetSearchResults()
        return scrolllist

    def CreateCurrentShipCont(self):
        self.shipCont.Flush()
        Frame(parent=self.shipCont, color=(1, 1, 1, 0.1))
        activeShip = GetActiveShip()
        clientDogmaLocation = sm.GetService('clientDogmaIM').GetDogmaLocation()
        shipDogmaItem = clientDogmaLocation.GetShip()
        shipTypeID = shipDogmaItem.typeID
        icon = Icon(parent=self.shipCont, pos=(0, 0, 40, 40), ignoreSize=True, state=uiconst.UI_DISABLED)
        if self.fittingSvc.IsShipSimulated():
            self.shipCont.OnClick = self.ExitSimulation
            icon.LoadIconByTypeID(shipTypeID)
        else:
            self.shipCont.OnClick = self.LoadCurrentShip
            hologramTexture = inventorycommon.typeHelpers.GetHoloIconPath(shipTypeID)
            icon.LoadTexture(hologramTexture)
        shipName = cfg.evelocations.Get(activeShip).name
        text = '%s<br>%s' % (evetypes.GetName(shipTypeID), shipName)
        self.shipnametext = EveLabelMedium(text=text, parent=self.shipCont, align=uiconst.TOTOP, top=2, padLeft=48)

    def ChangeResourceBtn(self):
        btn = self.hardwareFilterBtns.get(BTN_TYPE_RESOURCES, None)
        if not btn:
            return
        if self.controller.IsSimulated():
            btn.Enable()
        else:
            btn.Disable(opacity=0.3)

    def Close(self):
        try:
            self.ChangeSignalConnection(connect=False)
        except Exception as e:
            log.LogError('Failed at closing fitting left panel, e = ', e)
        finally:
            Container.Close(self)


def IsChargeTabSelected():
    isChargeTabSelected = settings.user.ui.Get(HW_BTN_ID_CONFIG, BROWSE_MODULES) == BROWSE_CHARGES
    return isChargeTabSelected


def IsHardwareTabSelected():
    return settings.user.ui.Get(BROWSER_BTN_ID_CONFIG, BROWSE_FITTINGS) == BROWSE_HARDWARE


def IsModuleTabSelected():
    return settings.user.ui.Get(HW_BTN_ID_CONFIG, BROWSE_MODULES) == BROWSE_MODULES
