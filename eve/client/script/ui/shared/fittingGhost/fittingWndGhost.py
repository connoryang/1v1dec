#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\fittingGhost\fittingWndGhost.py
from carbon.common.script.util.format import FmtAmt
from carbonui.primitives.sprite import Sprite
from eve.client.script.ui.control.eveCombo import Combo
from eve.client.script.ui.control.tabGroup import TabGroup
from eve.client.script.ui.shared.fitting.cleanShipButton import CleanShipButton
from eve.client.script.ui.shared.fitting.fittingWnd import GetFixedWndHeight, GetOverlayWidthHeightAndAlignment
from eve.client.script.ui.shared.fitting.serviceCont import FittingServiceCont
from eve.client.script.ui.shared.fittingGhost import SIMULATION_SKILLS, SIMULATION_MODULES
from eve.client.script.ui.shared.fittingGhost.baseFittingGhost import FittingGhost
from eve.client.script.ui.shared.fittingGhost.dronePickerMenu import GetDroneMenu
from eve.client.script.ui.shared.fittingGhost.fittingUtilGhost import GetColoredText
from eve.client.script.ui.shared.fittingGhost.ghostShipIcon import GhostShipIcon
from eve.client.script.ui.shared.fittingGhost.sidePanelButtons import SidePanelTabGroup
from eve.client.script.ui.shared.fittingGhost.statsPanel import StatsPanelGhost
from eve.client.script.ui.shared.fittingGhost.ghostFittingPanels.minihangar import CargoCargoSlots, CargoDroneSlots, CargoFighterSlots, CargoStructureAmmoBay
import locks
from carbonui import const as uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.layoutGrid import LayoutGrid
from carbonui.util.various_unsorted import SetOrder
from eve.client.script.ui.control.buttons import ButtonIcon
from eve.client.script.ui.control.eveLabel import EveLabelMediumBold, EveLabelMedium
from eve.client.script.ui.control.eveWindow import Window
from eve.client.script.ui.shared.fitting.fittingUtil import GetBaseShapeSize, PANEL_WIDTH, GetTypeIDForController
from eve.client.script.ui.shared.fittingGhost.leftPanel import LeftPanel
from eve.client.script.ui.shared.skins.controller import FittingSkinPanelController
from eve.client.script.ui.shared.skins.skinPanel import SkinPanel
from eve.client.script.ui.station.fitting.fittingTooltipUtils import SetFittingTooltipInfo
from eve.client.script.ui.structure import ChangeSignalConnect
from eve.common.script.sys.eveCfg import GetActiveShip, IsControllingStructure
from localization import GetByLabel
import uthread
import blue
import log
WND_NORMAL_HEIGHT = 560
ANIM_DURATION = 0.25
TAB_CONFIGNAME_SKINS = 'skins'
TAB_CONFIGNAME_GHOSTFITTING = 'ghostfitting'
TAB_CONFIGNAME_STATS = 'stats'
LEFT_TABS = [TAB_CONFIGNAME_SKINS, TAB_CONFIGNAME_GHOSTFITTING]
FTTING_PANEL_SETTING_LEFT = 'fittingPanelLeft3'
FTTING_PANEL_SETTING_RIGHT = 'fittingPanelRight3'

class FittingWindowGhost(Window):
    __guid__ = 'form.FittingWindowGhost'
    __notifyevents__ = ['OnSetDevice', 'OnSessionChanged']
    default_topParentHeight = 0
    default_fixedHeight = WND_NORMAL_HEIGHT
    default_windowID = 'fittingGhost'
    default_captionLabelPath = 'Tooltips/StationServices/ShipFittingGhost'
    default_descriptionLabelPath = 'Tooltips/StationServices/ShipFittingGhost_description'
    default_iconNum = 'res:/ui/Texture/WindowIcons/fitting.png'

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        self.MakeUnResizeable()
        self.HideHeaderFill()
        self.windowReady = False
        self.controller = None
        self._layoutLock = locks.Lock()
        shipID = attributes.shipID or GetActiveShip()
        self.LoadController(shipID)
        self.LoadWnd()

    def LoadWnd(self):
        self.ConstructLayout()
        self.LoadLeftPanel(key=None)

    def LoadController(self, shipID):
        try:
            if self.controller:
                self.ChangeSignalConnection(connect=False)
                self.controller.Close()
            self.controller = sm.GetService('ghostFittingSvc').LoadGhostFittingController(shipID)
        except UserError:
            self.Close()
            raise

        self._fixedHeight = GetFixedWndHeight(self.controller)
        self.ChangeSignalConnection(connect=True)

    def OnControllerChanging(self, itemID):
        self.LoadController(itemID)
        self.LoadWnd()

    def ChangeSignalConnection(self, connect = True):
        signalAndCallback = [(self.controller.on_stats_changed, self.UpdateStats),
         (self.controller.on_new_itemID, self.OnNewItem),
         (self.controller.on_should_close, self.Close),
         (self.controller.on_simulation_state_changed, self.OnSimulationStateChanged),
         (self.controller.on_controller_changing, self.OnControllerChanging)]
        ChangeSignalConnect(signalAndCallback, connect)

    def ConstructLayout(self):
        self._fixedHeight = GetFixedWndHeight(self.controller)
        self.height = self._fixedHeight
        with self._layoutLock:
            self.sr.main.Flush()
            width = PANEL_WIDTH if self.IsLeftPanelExpanded() else 0
            skinController = FittingSkinPanelController(fitting=self.controller)
            self.leftPanel = Container(name='leftPanel', parent=self.sr.main, align=uiconst.TOLEFT, width=width, idx=0)
            self.ghostLeftPanel = LeftPanel(name='leftPanel', parent=self.leftPanel, align=uiconst.TOALL, configName=TAB_CONFIGNAME_GHOSTFITTING, controller=self.controller)
            self.ghostLeftPanel.display = False
            self.skinLeftPanel = Container(name='skinLeftPanel', parent=self.leftPanel, align=uiconst.TOALL)
            self.skinLeftPanel.display = False
            self.skinLeftPanel.configName = TAB_CONFIGNAME_SKINS
            self.cleanShipBtn = CleanShipButton(parent=self.skinLeftPanel, align=uiconst.TOBOTTOM)
            self.skinPanel = SkinPanel(name='SkinPanel', parent=self.skinLeftPanel, align=uiconst.TOALL, controller=skinController, settingsPrefix='Fitting_SkinPanel', logContext='FittingWindow')
            self.leftSubPanels = [self.ghostLeftPanel, self.skinLeftPanel]
            width = PANEL_WIDTH if self.IsRightPanelExpanded() else 0
            self.rightPanel = StatsPanelGhost(name='rightside', parent=self.sr.main, align=uiconst.TORIGHT, width=width, idx=0, controller=self.controller)
            mainCont = Container(name='mainCont', parent=self.sr.main, top=-8)
            overlayWidth, overlayHeight, overlayAlignment = GetOverlayWidthHeightAndAlignment(self.controller)
            self.overlayCont = Container(name='overlayCont', parent=mainCont, align=overlayAlignment, width=overlayWidth, height=overlayHeight)
            self.fighterAndDroneCont = None
            self.ConstructPanelExpanderBtn()
            self.ConstructInventoryIcons()
            self.ConstructPowerAndCpuLabels()
            self.ConstructGhostFittingSwitch()
            self.ConstructCurrentGhostIcon()
            if self.controller.ControllerForCategory() == const.categoryStructure:
                self.serviceCont = FittingServiceCont(parent=mainCont, controller=self.controller)
                fittingAlignment = uiconst.TOPLEFT
            else:
                fittingAlignment = uiconst.CENTER
            FittingGhost(parent=mainCont, owner=self, controller=self.controller, align=fittingAlignment)
            self.windowReady = True
            self.width = self.GetWindowWidth()
            self.SetFixedWidth(self.width)
            self.ChangeSkinDisplay()
            self.UpdateStats()

    def LoadLeftPanel(self, key):
        if key is None:
            key = settings.user.ui.Get(FTTING_PANEL_SETTING_LEFT, '')
        for eachPanel in self.leftSubPanels:
            if eachPanel.configName != key:
                eachPanel.display = False

        if key == 'ghostfitting':
            self.ghostLeftPanel.Load()
            self.ghostLeftPanel.display = True
        elif key == 'skins':
            self.skinPanel.Load()
            self.skinLeftPanel.display = True
        self.leftPanelTabs.SetSelectedBtn(key)

    def ConstructInventoryIcons(self):
        cargoDroneCont = ContainerAutoSize(name='cargoDroneCont', parent=self.overlayCont, align=uiconst.BOTTOMLEFT, width=110, left=const.defaultPadding, top=4)
        if IsControllingStructure():
            cargoSlot = CargoStructureAmmoBay(name='structureCargoSlot', parent=cargoDroneCont, align=uiconst.TOTOP, height=32, controller=self.controller)
            SetFittingTooltipInfo(cargoSlot, 'StructureAmmoHold')
        else:
            cargoSlot = CargoCargoSlots(name='cargoSlot', parent=cargoDroneCont, align=uiconst.TOTOP, height=32, controller=self.controller)
            SetFittingTooltipInfo(cargoSlot, 'CargoHold')
        self.fighterAndDroneCont = Container(name='fighterAndDroneCont', parent=cargoDroneCont, align=uiconst.TOTOP, height=32)
        self.ContructDroneAndFighterIcons()

    def ContructDroneAndFighterIcons(self):
        self.fighterAndDroneCont.Flush()
        if self.controller.HasFighterBay():
            slot = CargoFighterSlots(name='fighterSlot', parent=self.fighterAndDroneCont, align=uiconst.TOTOP, height=32, controller=self.controller)
            SetFittingTooltipInfo(slot, 'FighterBay')
        else:
            slot = CargoDroneSlots(name='droneSlot', parent=self.fighterAndDroneCont, align=uiconst.TOTOP, height=32, controller=self.controller, getDroneMenuFunc=self.GetDroneMenu)
            SetFittingTooltipInfo(slot, 'DroneBay')
        self.fighterOrDroneSlot = slot

    def ReloadDroneAndFighterIconsIfNeeded(self):
        if self.fighterAndDroneCont is None:
            return
        if self.controller.HasFighterBay() and isinstance(self.fighterOrDroneSlot, CargoFighterSlots):
            return
        if not self.controller.HasFighterBay() and isinstance(self.fighterOrDroneSlot, CargoDroneSlots):
            return
        self.ContructDroneAndFighterIcons()

    def GetDroneMenu(self, menuParent):
        return GetDroneMenu(self.controller, menuParent)

    def ConstructGhostFittingSwitch(self):
        texturePath = 'res:/UI/Texture/classes/Fitting/iconSimulatorToggle.png'
        iconSize = 32
        switchCont = Container(parent=self.overlayCont, state=uiconst.UI_PICKCHILDREN, align=uiconst.TOPLEFT, pos=(const.defaultPadding,
         const.defaultPadding,
         100,
         32))
        modeOptions = [(GetByLabel('UI/Fitting/FittingWindow/ModuleMode'), SIMULATION_MODULES), (GetByLabel('UI/Fitting/FittingWindow/SkillMode'), SIMULATION_SKILLS)]
        currentMode = sm.GetService('ghostFittingSvc').GetSimulationMode()
        self.ghostFittingSwitch = ButtonIcon(texturePath=texturePath, parent=switchCont, align=uiconst.CENTERLEFT, pos=(0,
         0,
         iconSize,
         iconSize), func=self.ToggleGhostFitting, iconSize=iconSize)
        left = self.ghostFittingSwitch.left + self.ghostFittingSwitch.width
        self.simulateLabel = EveLabelMedium(parent=switchCont, text='Simulate', align=uiconst.CENTERLEFT, left=left)
        self.simulationMode = Combo(label='', parent=switchCont, options=modeOptions, name='simulationMode', select=int(currentMode == SIMULATION_SKILLS), callback=self.OnSimulationModeChanged, align=uiconst.CENTERLEFT, left=left)
        isSimulated = sm.GetService('fittingSvc').IsShipSimulated()
        self.ChangeSimulateUIstate(isSimulated)

    def ToggleGhostFitting(self, *args):
        fittingSvc = sm.GetService('fittingSvc')
        ghostFittingSvc = sm.GetService('ghostFittingSvc')
        isSimulated = fittingSvc.IsShipSimulated()
        self.ghostFittingSwitch.state = uiconst.UI_DISABLED
        if isSimulated:
            fittingSvc.SetSimulationState(False)
            shipID = GetActiveShip()
            newTypeID = GetTypeIDForController(shipID)
            ghostFittingSvc.SendOnSimulatedShipLoadedEvent(shipID, newTypeID)
            self.ChangeSimulateUIstate(False)
        else:
            fittingDL = sm.GetService('clientDogmaIM').GetFittingDogmaLocation()
            shipItem = fittingDL.GetShip()
            if shipItem:
                fittingSvc.SetSimulationState(True)
                ghostFittingSvc.SendOnSimulatedShipLoadedEvent(shipItem.itemID, shipItem.typeID)
            else:
                ghostFittingSvc.LoadCurrentShip()
        newState = not isSimulated
        self.ChangeSimulateUIstate(newState)
        self.controller.OnSimulationStateChanged(newState)

    def ChangeSimulateUIstate(self, inSimulation):
        self.simulateLabel.display = not inSimulation
        self.simulationMode.display = inSimulation
        if inSimulation:
            self.ghostFittingSwitch.hint = GetByLabel('UI/Fitting/FittingWindow/ExitSimulationMode')
        else:
            self.ghostFittingSwitch.hint = GetByLabel('UI/Fitting/FittingWindow/EnterSimulationMode')

    def ChangeCurrentShipGhostDisplay(self):
        self.currentShipGhost.display = self.controller.IsSimulated()

    def ConstructCurrentGhostIcon(self):
        shipTypeID = GetTypeIDForController(session.shipid)
        self.currentShipGhost = GhostShipIcon(name='currentShipGhost', parent=self.overlayCont, typeID=shipTypeID, align=uiconst.TOPRIGHT, pos=(0, 10, 64, 64))
        self.ChangeCurrentShipGhostDisplay()

    def ChangeSkinDisplay(self):
        isSimulated = sm.GetService('fittingSvc').IsShipSimulated()
        if isSimulated:
            self.skinPanel.opacity = 0.25
            self.skinPanel.state = uiconst.UI_DISABLED
        else:
            self.skinPanel.opacity = 1.0
            self.skinPanel.state = uiconst.UI_PICKCHILDREN

    def OnSimulationModeChanged(self, combo, text, value):
        sm.GetService('ghostFittingSvc').SetSimulationMode(value)
        self.controller.OnSimulationModeChanged(value)

    def OnSimulationStateChanged(self, inSimulation):
        self.ChangeCurrentShipGhostDisplay()
        self.ChangeSimulateUIstate(inSimulation)
        self.ChangeSkinDisplay()

    def IsRightPanelExpanded(self):
        return settings.user.ui.Get(FTTING_PANEL_SETTING_RIGHT, TAB_CONFIGNAME_STATS) == TAB_CONFIGNAME_STATS

    def IsLeftPanelExpanded(self):
        return settings.user.ui.Get(FTTING_PANEL_SETTING_LEFT, '') in LEFT_TABS

    def ConstructPanelExpanderBtn(self):
        tabBtnData = [(GetByLabel('UI/Fitting/FittingWindow/Skins'), TAB_CONFIGNAME_SKINS, TAB_CONFIGNAME_SKINS), (GetByLabel('UI/Fitting/FittingWindow/FittingTab'), TAB_CONFIGNAME_GHOSTFITTING, TAB_CONFIGNAME_GHOSTFITTING)]
        self.leftPanelTabs = SidePanelTabGroup(parent=self.overlayCont, align=uiconst.CENTERLEFT, idx=0, tabBtnData=tabBtnData, func=self.LeftPanelToggles, padLeft=2)
        tabBtnData = [(GetByLabel('UI/Fitting/FittingWindow/StatsTab'), TAB_CONFIGNAME_STATS, TAB_CONFIGNAME_STATS)]
        selectedTab = settings.user.ui.Get(FTTING_PANEL_SETTING_RIGHT, '')
        self.rightPanelTabs = SidePanelTabGroup(parent=self.overlayCont, align=uiconst.CENTERRIGHT, idx=0, tabBtnData=tabBtnData, func=self.ToggleRight, isLeftAligned=False, selectedTab=selectedTab, padRight=2)

    def ToggleRight(self, configName, *args):
        currentlyExpaned = self.IsRightPanelExpanded()
        if currentlyExpaned:
            newValue = ''
        else:
            newValue = configName
        settings.user.ui.Set(FTTING_PANEL_SETTING_RIGHT, newValue)
        self._fixedWidth = self.GetWindowWidth()
        if currentlyExpaned:
            self.CollapseRightPanel()
        else:
            self.ExpandRightPanel()
        self.rightPanelTabs.SetSelectedBtn(newValue)

    def CollapseRightPanel(self):
        uicore.animations.MorphScalar(self, 'width', self.width, self._fixedWidth, duration=ANIM_DURATION)
        uicore.animations.MorphScalar(self.rightPanel, 'width', self.rightPanel.width, 0, duration=ANIM_DURATION)
        uicore.animations.FadeTo(self.rightPanel, self.rightPanel.opacity, 0.0, duration=ANIM_DURATION, sleep=True)

    def ExpandRightPanel(self):
        uicore.animations.MorphScalar(self, 'width', self.width, self._fixedWidth, duration=ANIM_DURATION)
        uicore.animations.MorphScalar(self.rightPanel, 'width', self.rightPanel.width, PANEL_WIDTH, duration=ANIM_DURATION)
        uicore.animations.FadeTo(self.rightPanel, self.rightPanel.opacity, 1.0, duration=ANIM_DURATION, sleep=True)

    def LeftPanelToggles(self, configName, *args):
        currentlyShowing = settings.user.ui.Get(FTTING_PANEL_SETTING_LEFT, '')
        newSelected = ''
        if currentlyShowing == configName:
            settings.user.ui.Set(FTTING_PANEL_SETTING_LEFT, newSelected)
            self.ColllapseLeftPanel()
        elif configName in LEFT_TABS:
            newSelected = configName
            settings.user.ui.Set(FTTING_PANEL_SETTING_LEFT, newSelected)
            if not currentlyShowing:
                self.ExpandLeftPanelTab(configName)
            uthread.new(self.LoadLeftPanel, configName)
        self.leftPanelTabs.SetSelectedBtn(newSelected)

    def ColllapseLeftPanel(self):
        self._fixedWidth = self.GetWindowWidth()
        uicore.animations.MorphScalar(self, 'width', self.width, self._fixedWidth, duration=ANIM_DURATION)
        uicore.animations.MorphScalar(self, 'left', self.left, self.left + PANEL_WIDTH, duration=ANIM_DURATION)
        uicore.animations.MorphScalar(self.leftPanel, 'width', self.leftPanel.width, 0, duration=ANIM_DURATION)
        uicore.animations.FadeTo(self.leftPanel, self.leftPanel.opacity, 0.0, duration=ANIM_DURATION, sleep=True)

    def ExpandLeftPanelTab(self, configName):
        self._fixedWidth = self.GetWindowWidth()
        uicore.animations.MorphScalar(self, 'width', self.width, self._fixedWidth, duration=ANIM_DURATION)
        uicore.animations.MorphScalar(self, 'left', self.left, self.left - PANEL_WIDTH, duration=ANIM_DURATION)
        uicore.animations.MorphScalar(self.leftPanel, 'width', self.leftPanel.width, PANEL_WIDTH, duration=ANIM_DURATION)
        uicore.animations.FadeTo(self.leftPanel, self.leftPanel.opacity, 1.0, duration=ANIM_DURATION, sleep=True)

    def GetWindowWidth(self):
        width = GetBaseShapeSize() + 8
        if self.IsLeftPanelExpanded():
            width += PANEL_WIDTH
        if self.IsRightPanelExpanded():
            width += PANEL_WIDTH
        return width

    def OnSessionChanged(self, *args):
        newTypeID = GetTypeIDForController(session.shipid)
        self.currentShipGhost.SetShipTypeID(newTypeID)

    def OnSetDevice(self):
        if self.controller and self.controller.GetItemID():
            uthread.new(self.LoadWnd)

    def InitializeStatesAndPosition(self, *args, **kw):
        current = self.GetRegisteredPositionAndSize()
        default = self.GetDefaultSizeAndPosition()
        fixedHeight = self._fixedHeight
        fixedWidth = self.GetWindowWidth()
        Window.InitializeStatesAndPosition(self, *args, **kw)
        if fixedWidth is not None:
            self.width = fixedWidth
            self._fixedWidth = fixedWidth
        if fixedHeight is not None:
            self.height = fixedHeight
            self._fixedHeight = fixedHeight
        if list(default) == list(current)[:4]:
            settings.user.ui.Set('defaultFittingPosition', 1)
            dw = uicore.desktop.width
            dh = uicore.desktop.height
            self.left = (dw - self.width) / 2
            self.top = (dh - self.height) / 2
        self.MakeUnpinable()
        self.Unlock()
        uthread.new(uicore.registry.SetFocus, self)
        self._collapseable = 0

    def _OnClose(self, *args):
        settings.user.ui.Set('defaultFittingPosition', 0)

    def MouseDown(self, *args):
        uthread.new(uicore.registry.SetFocus, self)
        SetOrder(self, 0)

    def GhostFitItem(self, ghostItem = None):
        if not self.controller:
            return
        self.controller.SetGhostFittedItem(ghostItem)

    def OnStartMinimize_(self, *args):
        sm.ChainEvent('ProcessFittingWindowStartMinimize')

    def OnEndMinimize_(self, *args):
        sm.ChainEvent('ProcessFittingWindowEndMinimize')

    def OnUIScalingChange(self, *args):
        pass

    def OnNewItem(self):
        uthread.new(self.EnableGhostSwitch)
        self.UpdateStats()

    def EnableGhostSwitch(self):
        blue.pyos.synchro.SleepWallclock(500.0)
        self.ghostFittingSwitch.state = uiconst.UI_NORMAL

    def UpdateStats(self):
        if not self.windowReady:
            return
        self.UpdateCPU()
        self.UpdatePower()
        self.UpdateCalibration()
        self.ReloadDroneAndFighterIconsIfNeeded()

    def ConstructPowerAndCpuLabels(self):
        powerGridAndCpuCont = LayoutGrid(parent=self.overlayCont, columns=1, state=uiconst.UI_PICKCHILDREN, align=uiconst.BOTTOMRIGHT, top=10, left=10)
        cpu_statustextHeader = EveLabelMediumBold(text=GetByLabel('UI/Fitting/FittingWindow/CPUStatusHeader'), name='cpu_statustextHeader', state=uiconst.UI_NORMAL, align=uiconst.TOPRIGHT)
        SetFittingTooltipInfo(targetObject=cpu_statustextHeader, tooltipName='CPU')
        powerGridAndCpuCont.AddCell(cpu_statustextHeader)
        self.cpu_statustext = EveLabelMedium(text='', name='cpu_statustext', state=uiconst.UI_NORMAL, align=uiconst.TOPRIGHT)
        SetFittingTooltipInfo(targetObject=self.cpu_statustext, tooltipName='CPU')
        powerGridAndCpuCont.AddCell(self.cpu_statustext)
        powerGridAndCpuCont.AddCell(cellObject=Container(name='spacer', align=uiconst.TOTOP, height=10))
        power_statustextHeader = EveLabelMediumBold(text=GetByLabel('UI/Fitting/FittingWindow/PowergridHeader'), name='power_statustextHeader', state=uiconst.UI_NORMAL, align=uiconst.TOPRIGHT)
        SetFittingTooltipInfo(targetObject=power_statustextHeader, tooltipName='PowerGrid')
        powerGridAndCpuCont.AddCell(power_statustextHeader)
        self.power_statustext = EveLabelMedium(text='', name='power_statustext', state=uiconst.UI_NORMAL, align=uiconst.TOPRIGHT)
        powerGridAndCpuCont.AddCell(self.power_statustext)
        SetFittingTooltipInfo(targetObject=self.power_statustext, tooltipName='PowerGrid')
        self.calibration_statustext = EveLabelMedium(text='', parent=self.overlayCont, name='calibrationstatustext', pos=(8, 50, 0, 0), idx=0, state=uiconst.UI_NORMAL)
        SetFittingTooltipInfo(targetObject=self.calibration_statustext, tooltipName='Calibration')

    def UpdateCPU(self):
        cpuLoadInfo = self.controller.GetCPULoad()
        cpuOutputInfo = self.controller.GetCPUOutput()
        cpuLoadText = FmtAmt(cpuOutputInfo.value - cpuLoadInfo.value, showFraction=1)
        coloredCpuLoadText = GetColoredText(isBetter=cpuLoadInfo.isBetterThanBefore, text=cpuLoadText)
        cpuOutputText = FmtAmt(cpuOutputInfo.value, showFraction=1)
        coloredCpuOutputText = GetColoredText(isBetter=cpuOutputInfo.isBetterThanBefore, text=cpuOutputText)
        self.cpu_statustext.text = '%s/%s' % (coloredCpuLoadText, coloredCpuOutputText)

    def UpdatePower(self):
        powerLoadInfo = self.controller.GetPowerLoad()
        powerOutputInfo = self.controller.GetPowerOutput()
        powerLoadText = FmtAmt(powerOutputInfo.value - powerLoadInfo.value, showFraction=1)
        coloredPowerLoadText = GetColoredText(isBetter=powerLoadInfo.isBetterThanBefore, text=powerLoadText)
        powerOutputText = FmtAmt(powerOutputInfo.value, showFraction=1)
        coloredPowerOutputText = GetColoredText(isBetter=powerOutputInfo.isBetterThanBefore, text=powerOutputText)
        self.power_statustext.text = '%s/%s' % (coloredPowerLoadText, coloredPowerOutputText)

    def UpdateCalibration(self):
        calibrationLoadInfo = self.controller.GetCalibrationLoad()
        calibrationOutputInfo = self.controller.GetCalibrationOutput()
        calibrationLoadText = FmtAmt(calibrationOutputInfo.value - calibrationLoadInfo.value, showFraction=1)
        coloredCalibrationLoadText = GetColoredText(isBetter=calibrationLoadInfo.isBetterThanBefore, text=calibrationLoadText)
        calibrationOutputText = FmtAmt(calibrationOutputInfo.value, showFraction=1)
        coloredCalibrationOutputText = GetColoredText(isBetter=calibrationOutputInfo.isBetterThanBefore, text=calibrationOutputText)
        self.calibration_statustext.text = '%s/%s' % (coloredCalibrationLoadText, coloredCalibrationOutputText)

    def GetMenu(self, *args):
        m = Window.GetMenu(self, *args)
        m += [None]
        m += [('Reset all search variables', self.ResetAllSearchVariables, ())]
        m += [('Clear resources dictionary', self.ClearResoureDict, ())]
        m += [('Reload ghostfitting DL', self.ReloadFittingDogmaLocation, ())]
        return m

    def ClearResoureDict(self):
        sm.GetService('fittingSvc').searchFittingHelper.ResetCpuAndPowergridDicts()

    def ResetAllSearchVariables(self):
        sm.GetService('fittingSvc').searchFittingHelper.ResetAllVariables()

    def ReloadFittingDogmaLocation(self):
        sm.GetService('ghostFittingSvc').ResetFittingDomaLocation(force=True)
        sm.GetService('fittingSvc').SetSimulationState(simulationOn=False)
        itemID = GetActiveShip()
        self.OnControllerChanging(itemID)

    def Close(self, setClosed = False, *args, **kwds):
        try:
            self.ChangeSignalConnection(connect=False)
        except Exception as e:
            log.LogError('Failed at changing signal connections for ghost fitting wnd, e = ', e)
        finally:
            Window.Close(self, setClosed, *args, **kwds)
            self.controller.Close()
