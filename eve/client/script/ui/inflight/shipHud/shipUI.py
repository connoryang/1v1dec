#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\inflight\shipHud\shipUI.py
from carbonui.control.layer import LayerCore
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.line import Line
from carbonui.primitives.sprite import Sprite
from carbonui.util.color import Color
from eve.client.script.parklife import states
from eve.client.script.ui.control.buttons import ButtonIcon
from eve.client.script.ui.control.eveLabel import *
from eve.client.script.ui.control.utilMenu import UtilMenu
from eve.client.script.ui.inflight.radialMenuScanner import RadialMenuScanner
from eve.client.script.ui.inflight.shipAlert import ShipAlertContainer
from eve.client.script.ui.inflight.shipHud.capacitorContainer import CapacitorContainer
from eve.client.script.ui.inflight.shipHud.ewarContainer import EwarContainer
from eve.client.script.ui.inflight.shipHud.heatGauges import HeatGauges
from eve.client.script.ui.inflight.shipHud.hpGauges import HPGauges
from eve.client.script.ui.inflight.shipHud.hudButtonsCont import HudButtonsCont
from eve.client.script.ui.inflight.notifySettingsWindow import NotifySettingsWindow
from eve.client.script.ui.inflight.shipHud.hudShape import HUDShape, StructureHUDShape
from eve.client.script.ui.inflight.shipHud.releaseControlBtn import ReleaseControlBtn
from eve.client.script.ui.inflight.shipHud.safeLogoffTimer import SafeLogoffTimer
from eve.client.script.ui.inflight.shipHud.activeShipController import ActiveShipController
from eve.client.script.ui.inflight.shipHud.shipHudConst import SHIP_UI_HEIGHT, SHIP_UI_WIDTH
from eve.client.script.ui.inflight.shipHud.slotsContainer import SlotsContainer
from eve.client.script.ui.inflight.shipHud.speedGauge import SpeedGauge
from eve.client.script.ui.inflight.shipSafetyButton import SafetyButton
from eve.client.script.ui.inflight.squadrons.shipFighterState import GetShipFighterState
from eve.client.script.ui.inflight.squadrons.squadronsUI import SquadronsUI
from eve.client.script.ui.inflight.stanceButtons import StanceButtons
from eve.client.script.ui.services.menuSvcExtras import movementFunctions
from eve.client.script.ui.util.uix import GetSlimItemName
from eve.client.script.util.settings import IsShipHudTopAligned, SetShipHudTopAligned
from eve.common.script.sys.eveCfg import IsControllingStructure
from gametime import GetDurationInClient
from localization import GetByLabel
from sensorsuite.overlay.sitecompass import Compass
import blue
import telemetry
import uthread
SLOTS_CONTAINER_LEFT = SHIP_UI_WIDTH / 2.0 + 78
SLOTS_CONTAINER_TOP = -1
SLOTS_CONTAINER_WIDTH = 512
SLOTS_CONTAINER_HEIGHT = 152
EWAR_CONTAINER_WIDTH = 480
EWAR_CONTAINER_HEIGHT = 44

class ShipUI(LayerCore):
    __notifyevents__ = ['OnShipScanCompleted',
     'OnJamStart',
     'OnJamEnd',
     'OnCargoScanComplete',
     'DoBallRemove',
     'OnSetDevice',
     'OnAssumeStructureControl',
     'OnRelinquishStructureControl',
     'OnUIRefresh',
     'OnUIScalingChange',
     'ProcessPendingOverloadUpdate',
     'OnSafeLogoffTimerStarted',
     'OnSafeLogoffActivated',
     'OnSafeLogoffAborted',
     'OnSafeLogoffFailed',
     'DoBallsRemove',
     'OnSetCameraOffset',
     'ProcessShipEffect',
     'OnStateChange']

    def ApplyAttributes(self, attributes):
        LayerCore.ApplyAttributes(self, attributes)
        self.setupShipTasklet = None
        self.updateTasklet = None
        self.controller = ActiveShipController()
        self.controller.on_new_itemID.connect(self.OnShipChanged)
        self.ResetSelf()

    def Close(self):
        LayerCore.Close(self)
        self.controller.Close()

    def OnSetCameraOffset(self, cameraOffset):
        self.UpdatePosition()

    def OnSetDevice(self):
        self.UpdatePosition()

    def OnUIScalingChange(self, *args):
        self.OnUIRefresh()

    def OnUIRefresh(self):
        self.CloseView(recreate=False)
        self.OpenView()

    @telemetry.ZONE_METHOD
    def ResetSelf(self):
        self.sr.safetyButton = None
        self.fighterHudBinding = None
        self.sr.selectedcateg = 0
        self.sr.pendingreloads = []
        self.sr.reloadsByID = {}
        self.sr.rampTimers = {}
        self.shipuiReady = False
        self.initing = None
        self.jammers = {}
        self.assumingdelay = None
        if self.updateTasklet is not None:
            self.updateTasklet.kill()
        self.updateTasklet = None
        if self.setupShipTasklet is not None:
            self.setupShipTasklet.kill()
        self.setupShipTasklet = None
        self.logoffTimer = None
        self.Flush()

    def CheckPendingReloads(self):
        if self.sr.pendingreloads:
            rl = self.sr.pendingreloads[0]
            while rl in self.sr.pendingreloads:
                self.sr.pendingreloads.remove(rl)

            module = self.GetModule(rl)
            if module:
                module.AutoReload()

    def CheckSession(self, change):
        if sm.GetService('autoPilot').GetState():
            self.OnAutoPilotOn()
        else:
            self.OnAutoPilotOff()

    @telemetry.ZONE_METHOD
    def UpdatePosition(self):
        cameraOffset = sm.GetService('sceneManager').GetCameraOffset()
        halfWidth = uicore.desktop.width / 2
        baseOffset = -cameraOffset * halfWidth
        wndLeft = settings.char.windows.Get('shipuialignleftoffset', 0)
        maxRight, minLeft = self.GetShipuiOffsetMinMax()
        self.hudContainer.left = min(maxRight, max(minLeft, baseOffset + wndLeft))
        self.ewarCont.left = self.hudContainer.left
        if IsShipHudTopAligned():
            self.hudContainer.SetAlign(uiconst.CENTERTOP)
            self.ewarCont.SetAlign(uiconst.CENTERTOP)
            self.sr.indicationContainer.top = self.hudContainer.height + self.ewarCont.height
        else:
            self.hudContainer.SetAlign(uiconst.CENTERBOTTOM)
            self.ewarCont.SetAlign(uiconst.CENTERBOTTOM)
            self.sr.indicationContainer.top = -(self.ewarCont.height + self.sr.indicationContainer.height)
        if self.IsFightersDetached():
            left, top = settings.char.ui.Get('fightersDetachedPosition', (0, 0))
            buttonWidth = 32
            left = min(left, uicore.desktop.width - buttonWidth)
            top = min(top, uicore.desktop.height - self.fighterCont.height)
            self.fighterCont.left = left
            self.fighterCont.top = top
            settings.char.ui.Set('fightersDetachedPosition', (left, top))
        self.AlignFighters()
        self.sr.shipAlertContainer.UpdatePosition()

    def MakeFighterHudBinding(self):
        cs = uicore.uilib.bracketCurveSet
        self.fighterHudBinding = trinity.CreatePythonBinding(cs, self.compass, 'absoluteRight', self.fighterCont, 'left')

    def RemoveFighterHudBinding(self):
        if self.fighterHudBinding:
            cs = uicore.uilib.bracketCurveSet
            cs.bindings.fremove(self.fighterHudBinding)
            self.fighterHudBinding = None

    def OnShipMouseDown(self, wnd, btn, *args):
        if btn != 0:
            return
        self.dragging = True
        if not self.hudContainer:
            return
        self.grab = [uicore.uilib.x, self.hudContainer.left]
        uthread.new(self.BeginDrag)

    def GetShipuiOffsetMinMax(self, *args):
        magicNumber = 275
        if self.CheckShipHasFighterBay():
            magicNumber = 300
        sidePanelsLeft, sidePanelsRight = uicore.layer.sidepanels.GetSideOffset()
        maxRight = uicore.desktop.width / 2 - self.slotsContainer.width / 2 - magicNumber - sidePanelsRight
        minLeft = -(uicore.desktop.width / 2 - 180) + sidePanelsLeft
        return (maxRight, minLeft)

    def OnToggleShipSelected(self, *args):
        if not self.CheckShipHasFighterBay():
            return
        if not self.IsFightersShown():
            self.DeselectShip()
            return
        x, y = self.grab
        currentX, currentY = uicore.uilib.x, self.hudContainer.left
        if x != currentX or y != currentY:
            return
        if uicore.uilib.Key(uiconst.VK_CONTROL):
            if movementFunctions.IsSelectedForNavigation(session.shipid):
                self.DeselectShip()
            else:
                self.SelectShip()
        else:
            self.SelectShip()
            self.fighterCont.ClearSelection()

    def SelectShip(self):
        movementFunctions.SelectForNavigation(session.shipid)

    def DeselectShip(self):
        movementFunctions.DeselectForNavigation(session.shipid)

    def OnStateChange(self, itemID, flag, flagState, *args):
        if not self.CheckShipHasFighterBay():
            return
        if flag == states.selectedForNavigation and itemID == session.shipid:
            if flagState:
                self.ShowSelectionHilite()
            else:
                self.HideSelectionHilite()

    def ShowSelectionHilite(self):
        if self.shipSelectHilight.display:
            return
        self.shipSelectHilight.display = True
        self.ringSprite.opacity = 0.2
        self.bracketSprite.opacity = 3.0
        uicore.animations.FadeTo(self.ringSprite, self.ringSprite.opacity, 1.0, duration=0.2)
        uicore.animations.FadeTo(self.bracketSprite, self.bracketSprite.opacity, 1.0, duration=0.2)

    def HideSelectionHilite(self):
        self.shipSelectHilight.display = False

    def OnShipMouseUp(self, wnd, btn, *args):
        if btn != 0:
            return
        sm.StartService('ui').ForceCursorUpdate()
        self.dragging = False

    def BeginDrag(self, *args):
        cameraOffset = sm.GetService('sceneManager').GetCameraOffset()
        halfWidth = uicore.desktop.width / 2
        baseOffset = -cameraOffset * halfWidth
        while not self.hudContainer.destroyed and getattr(self, 'dragging', 0):
            uicore.uilib.SetCursor(uiconst.UICURSOR_DIVIDERADJUST)
            maxRight, minLeft = self.GetShipuiOffsetMinMax()
            grabMouseDiff = uicore.uilib.x - self.grab[0]
            combinedOffset = min(maxRight, max(minLeft, self.grab[1] + grabMouseDiff))
            dragOffset = combinedOffset - baseOffset
            if -8 <= dragOffset <= 8:
                settings.char.windows.Set('shipuialignleftoffset', 0)
                self.hudContainer.left = baseOffset
            else:
                self.hudContainer.left = combinedOffset
                settings.char.windows.Set('shipuialignleftoffset', dragOffset)
            self.ewarCont.left = self.hudContainer.left
            blue.pyos.synchro.SleepWallclock(1)

    def ConstructOverlayContainer(self):
        self.toggleLeftBtn = Sprite(parent=self.overlayContainer, name='expandBtnLeft', pos=(56, 122, 28, 28), align=uiconst.TOPLEFT, state=uiconst.UI_NORMAL, texturePath='res:/UI/Texture/classes/ShipUI/expandBtnLeft.png')
        self.toggleLeftBtn.OnClick = self.ToggleHudButtons
        hudButtonsExpanded = settings.user.ui.Get('hudButtonsExpanded', 1)
        self.toggleLeftBtn.hint = [GetByLabel('UI/Inflight/ShowButtons'), GetByLabel('UI/Inflight/HideButtons')][hudButtonsExpanded]
        self.optionsCont = Container(parent=self.overlayContainer, name='optionsCont', pos=(190, 190, 16, 16), align=uiconst.TOPLEFT, state=uiconst.UI_PICKCHILDREN)
        self.moduleToggleCont = Container(parent=self.overlayContainer, name='moduleToggleCont', pos=(206, 170, 24, 24), align=uiconst.TOPLEFT, state=uiconst.UI_PICKCHILDREN)
        if not IsControllingStructure():
            self.stopButton = StopButton(parent=self.overlayContainer, align=uiconst.TOPLEFT, controller=self.controller, left=75, top=155)
            self.maxspeedButton = MaxSpeedButton(parent=self.overlayContainer, align=uiconst.TOPLEFT, controller=self.controller, left=168, top=155)

    @telemetry.ZONE_METHOD
    def OnOpenView(self):
        self.ResetSelf()
        self.state = uiconst.UI_HIDDEN
        self.hudContainer = Container(name='hudContainer', parent=self, controller=self.controller, align=uiconst.CENTERBOTTOM, width=SHIP_UI_WIDTH, height=SHIP_UI_HEIGHT)
        self.overlayContainer = Container(parent=self.hudContainer, name='overlayContainer', pos=(0, 0, 256, 256), align=uiconst.CENTER, state=uiconst.UI_PICKCHILDREN, idx=0)
        self.ConstructOverlayContainer()
        if IsControllingStructure():
            shipShape = StructureHUDShape(parent=self.hudContainer, align=uiconst.CENTER)
        else:
            shipShape = HUDShape(parent=self.hudContainer, align=uiconst.CENTER)
        self.shipuiMainShape = shipShape.shipuiMainShape
        self.capacitorContainer = CapacitorContainer(parent=self.hudContainer, align=uiconst.CENTER, top=-1, controller=self.controller)
        self.capacitorContainer.OnMouseDown = (self.OnShipMouseDown, self.capacitorContainer)
        self.capacitorContainer.OnMouseUp = (self.OnShipMouseUp, self.capacitorContainer)
        self.capacitorContainer.OnClick = self.OnToggleShipSelected
        heatPicker = Container(name='heatPicker', parent=self.hudContainer, align=uiconst.CENTER, width=160, height=160, pickRadius=43, state=uiconst.UI_NORMAL)
        self.heatGauges = HeatGauges(parent=heatPicker, align=uiconst.CENTERTOP, controller=self.controller)
        self.hpGauges = HPGauges(name='healthGauges', parent=self.hudContainer, align=uiconst.CENTER, pos=(0, -37, 148, 74), controller=self.controller)
        if IsControllingStructure():
            ReleaseControlBtn(parent=self.hudContainer, top=29, align=uiconst.CENTERBOTTOM, itemID=self.controller.GetItemID(), func=sm.GetService('structureControl').Alight)
        else:
            self.speedGauge = SpeedGauge(parent=self.hudContainer, top=29, align=uiconst.CENTERBOTTOM, controller=self.controller)
        self.compass = Compass(parent=self.hudContainer, pickRadius=-1)
        self.shipSelectHilight = Container(name='navSelectHilight', parent=self.compass, align=uiconst.CENTER, state=uiconst.UI_DISABLED, width=206, height=206)
        self.ringSprite = Sprite(bgParent=self.shipSelectHilight, texturePath='res:/UI/Texture/classes/ShipUI/Fighters/selectionRingLarge.png')
        self.bracketSprite = Sprite(bgParent=self.shipSelectHilight, texturePath='res:/UI/Texture/classes/ShipUI/Fighters/selectionBracketLarge.png')
        self.shipSelectHilight.display = False
        self.slotsContainer = SlotsContainer(parent=self.hudContainer, pos=(SLOTS_CONTAINER_LEFT,
         SLOTS_CONTAINER_TOP,
         SLOTS_CONTAINER_WIDTH,
         SLOTS_CONTAINER_HEIGHT), align=uiconst.CENTERLEFT, state=uiconst.UI_PICKCHILDREN, controller=self.controller)
        self.stanceButtons = StanceButtons(parent=self.hudContainer, pos=(SLOTS_CONTAINER_LEFT + 8,
         1,
         40,
         120), name='stanceButtons', align=uiconst.CENTERLEFT, state=uiconst.UI_PICKCHILDREN, buttonSize=36)
        self.hudButtons = HudButtonsCont(parent=self.hudContainer, align=uiconst.CENTERRIGHT, left=690, top=15)
        self.ewarCont = EwarContainer(parent=self, align=uiconst.CENTERBOTTOM, top=SHIP_UI_HEIGHT, height=EWAR_CONTAINER_HEIGHT, width=EWAR_CONTAINER_WIDTH)
        self.sr.shipAlertContainer = ShipAlertContainer(parent=self.hudContainer)
        self.sr.indicationContainer = Container(parent=self.hudContainer, name='indicationContainer', align=uiconst.CENTERTOP, pos=(0, 0, 400, 50))
        self.sr.safetyButton = SafetyButton(parent=self.overlayContainer, left=40, top=28)
        self.ConstructReadoutCont()
        self.settingsMenu = UtilMenu(menuAlign=uiconst.BOTTOMLEFT, parent=self.optionsCont, align=uiconst.TOPLEFT, GetUtilMenu=self.GetHUDOptionMenu, pos=(0, 0, 16, 16), texturePath='res:/UI/Texture/Icons/73_16_50.png', hint=GetByLabel('UI/Inflight/Options'))
        self.moduleToggleBtn = ButtonIcon(name='moduleToggleBtn', parent=self.moduleToggleCont, align=uiconst.TOPLEFT, width=24, height=24, iconSize=24, texturePath='res:/UI/Texture/classes/ShipUI/Fighters/toggleModules_Up.png', downTexture='res:/UI/Texture/classes/ShipUI/Fighters/toggleModules_Down.png', hoverTexture='res:/UI/Texture/classes/ShipUI/Fighters/toggleModules_Over.png', func=self.OnToggleHudModules)
        self.moduleToggleBtn.display = False
        self.DrawFighters()
        self.hudContainer.state = uiconst.UI_PICKCHILDREN
        self.UpdatePosition()
        self.shipuiReady = True
        self.SetupShip()

    def DrawFighters(self):
        if hasattr(self, 'fighterCont'):
            self.fighterCont.Close()
        self.fighterCont = SquadronsUI(name='fighters', parent=self, state=uiconst.UI_PICKCHILDREN, parentFunc=self.OnToggleFightersDetached)
        self.AlignFighters()
        if self.IsFightersDetached():
            left, top = settings.char.ui.Get('fightersDetachedPosition', (uicore.desktop.width / 2, uicore.desktop.height / 2 - 60))
            self.fighterCont.left = left
            self.fighterCont.top = top
            self.slotsContainer.display = True
            self.moduleToggleBtn.Disable()
        self.SetFighterButtonsHint()
        self.fighterCont.KeepSelection()

    def SetFighterButtonsHint(self):
        if self.IsFightersDetached():
            self.fighterCont.fighterToggleBtn.hint = GetByLabel('UI/Inflight/HUDOptions/ClickToAttach')
            self.moduleToggleBtn.hint = ''
        else:
            self.fighterCont.fighterToggleBtn.hint = GetByLabel('UI/Inflight/HUDOptions/DragToDetach')
            self.moduleToggleBtn.hint = GetByLabel('UI/Inflight/HUDOptions/ClickToToggle')

    def CheckShipHasFighterBay(self):
        shipTypeID = self.controller.GetTypeID()
        godmaSM = sm.GetService('godma').GetStateManager()
        return godmaSM.GetType(shipTypeID).fighterCapacity > 0

    def OptionsBtnMouseEnter(self, *args):
        self.options.SetAlpha(1.0)

    def OptionsBtnMouseExit(self, *args):
        self.options.SetAlpha(0.8)

    def CheckControl(self):
        control = sm.GetService('pwn').GetCurrentControl()
        if control:
            self.OnAssumeStructureControl()

    def SetButtonState(self):
        if settings.user.ui.Get('hudButtonsExpanded', 1):
            self.hudButtons.state = uiconst.UI_PICKCHILDREN
            if IsControllingStructure():
                self.hudButtons.autopilotBtn.Disable()
            else:
                self.hudButtons.autopilotBtn.Enable()
        else:
            self.hudButtons.state = uiconst.UI_HIDDEN

    def ConstructReadoutLabel(self, refName):
        cont = ContainerAutoSize(name=refName, parent=self.readoutCont, align=uiconst.TOTOP)
        label = EveLabelSmall(parent=cont, left=2, state=uiconst.UI_DISABLED, align=uiconst.TOPRIGHT)
        Line(parent=cont, top=6, width=-130, height=1, align=uiconst.TOPRIGHT)
        Line(parent=cont, top=6, width=-130, height=1, align=uiconst.TOPRIGHT, color=(0.1, 0.1, 0.1, 0.5))
        return label

    @telemetry.ZONE_METHOD
    def ConstructReadoutCont(self):
        self.readoutCont = ContainerAutoSize(name='readoutCont', parent=self.hudContainer, pos=(278, 22, 200, 0), align=uiconst.TOPLEFT, state=uiconst.UI_HIDDEN)
        self.readoutShieldLabel = self.ConstructReadoutLabel('shield')
        self.readoutArmorLabel = self.ConstructReadoutLabel('armor')
        self.readoutStructureLabel = self.ConstructReadoutLabel('structure')

    def OnAssumeStructureControl(self, *args):
        now = blue.os.GetSimTime()
        self.assumingdelay = now
        uthread.new(self.DelayedOnAssumeStructureControl, now)

    def DelayedOnAssumeStructureControl(self, issueTime):
        blue.pyos.synchro.SleepSim(250)
        if self.assumingdelay is None:
            return
        issuedAt = self.assumingdelay
        if issuedAt != issueTime:
            return
        self.assumingdelay = None
        self.ShowStructureControl()

    def ShowStructureControl(self, *args):
        if self.controller.IsControllingTurret():
            self.initing = 1
            self.slotsContainer.InitSlots()
            self.hudButtons.InitButtons()
            self.initing = 0

    def OnRelinquishStructureControl(self, *args):
        self.SetupShip()

    def UpdateButtonsForShip(self):
        itemID = self.controller.GetItemID()
        typeID = self.controller.GetTypeID()
        if self.stanceButtons.HasStances():
            self._HideStancePanel()
        self.stanceButtons.UpdateButtonsForShip(itemID, typeID)
        if self.stanceButtons.HasStances():
            self._ShowStancePanel()

    def _ShowStancePanel(self):
        self.slotsContainer.left = SLOTS_CONTAINER_LEFT + 44
        self.stanceButtons.Show()

    def _HideStancePanel(self):
        self.slotsContainer.left = SLOTS_CONTAINER_LEFT
        self.stanceButtons.Hide()

    def GetHUDOptionMenu(self, menuParent):
        showPassive = settings.user.ui.Get('showPassiveModules', 1)
        text = GetByLabel('UI/Inflight/HUDOptions/DisplayPassiveModules')
        menuParent.AddCheckBox(text=text, checked=showPassive, callback=self.ToggleShowPassive)
        showEmpty = settings.user.ui.Get('showEmptySlots', 0)
        text = GetByLabel('UI/Inflight/HUDOptions/DisplayEmptySlots')
        menuParent.AddCheckBox(text=text, checked=showEmpty, callback=self.ToggleShowEmpty)
        showReadout = settings.user.ui.Get('showReadout', 0)
        text = GetByLabel('UI/Inflight/HUDOptions/DisplayReadout')
        menuParent.AddCheckBox(text=text, checked=showReadout, callback=self.ToggleReadout)
        readoutType = settings.user.ui.Get('readoutType', 1)
        text = GetByLabel('UI/Inflight/HUDOptions/DisplayReadoutAsPercentage')
        if showReadout:
            callback = self.ToggleReadoutType
        else:
            callback = None
        menuParent.AddCheckBox(text=text, checked=readoutType, callback=callback)
        showZoomBtns = settings.user.ui.Get('showZoomBtns', 0)
        text = GetByLabel('UI/Inflight/HUDOptions/DisplayZoomButtons')
        menuParent.AddCheckBox(text=text, checked=showZoomBtns, callback=self.ToggleShowZoomBtns)
        showTooltips = settings.user.ui.Get('showModuleTooltips', 1)
        text = GetByLabel('UI/Inflight/HUDOptions/DisplayModuleTooltips')
        menuParent.AddCheckBox(text=text, checked=showTooltips, callback=self.ToggleShowModuleTooltips)
        lockModules = settings.user.ui.Get('lockModules', 0)
        text = GetByLabel('UI/Inflight/HUDOptions/LockModulesInPlace')
        menuParent.AddCheckBox(text=text, checked=lockModules, callback=self.ToggleLockModules)
        menuParent.AddCheckBox(text=GetByLabel('UI/Inflight/HUDOptions/BlinkCargo'), checked=self.GetCargoBlinkValue(), callback=self.ToggleBlinkCargo)
        lockOverload = settings.user.ui.Get('lockOverload', 0)
        text = GetByLabel('UI/Inflight/HUDOptions/LockOverloadState')
        menuParent.AddCheckBox(text=text, checked=lockOverload, callback=self.ToggleOverloadLock)
        text = GetByLabel('UI/Inflight/HUDOptions/AlignHUDToTop')
        cb = menuParent.AddCheckBox(text=text, checked=IsShipHudTopAligned(), callback=self.ToggleAlign)
        cb.isToggleEntry = False
        menuParent.AddDivider()
        text = GetByLabel('UI/Inflight/NotifySettingsWindow/DamageAlertSettings')
        iconPath = 'res:/UI/Texture/classes/UtilMenu/BulletIcon.png'
        menuParent.AddIconEntry(icon=iconPath, text=text, callback=self.ShowNotifySettingsWindow)
        if sm.GetService('logger').IsInDragMode():
            text = GetByLabel('UI/Accessories/Log/ExitMessageMovingMode')
            enterArgs = False
        else:
            text = GetByLabel('UI/Accessories/Log/EnterMessageMovingMode')
            enterArgs = True
        menuParent.AddIconEntry(icon='res:/UI/Texture/classes/UtilMenu/BulletIcon.png', text=text, callback=(sm.GetService('logger').MoveNotifications, enterArgs))

    def ShowNotifySettingsWindow(self):
        NotifySettingsWindow.Open()

    def ToggleAlign(self):
        SetShipHudTopAligned(not IsShipHudTopAligned())
        self.UpdatePosition()
        for each in uicore.layer.abovemain.children[:]:
            if each.name == 'message':
                each.Close()
                break

        msg = getattr(uicore.layer.target, 'message', None)
        if msg:
            msg.Close()

    def CheckShowReadoutCont(self):
        if settings.user.ui.Get('showReadout', 0):
            self.readoutCont.state = uiconst.UI_DISABLED
            self.hudButtons.top = 30
        else:
            self.readoutCont.state = uiconst.UI_HIDDEN
            self.hudButtons.top = 15

    def ToggleReadout(self):
        current = not settings.user.ui.Get('showReadout', 0)
        settings.user.ui.Set('showReadout', current)
        self.CheckShowReadoutCont()

    def GetCargoBlinkValue(self):
        return settings.user.ui.Get('BlinkCargoHudIcon', True)

    def ToggleBlinkCargo(self):
        settings.user.ui.Set('BlinkCargoHudIcon', not self.GetCargoBlinkValue())

    def ToggleReadoutType(self):
        current = settings.user.ui.Get('readoutType', 1)
        settings.user.ui.Set('readoutType', not current)

    def ToggleShowZoomBtns(self):
        settings.user.ui.Set('showZoomBtns', not settings.user.ui.Get('showZoomBtns', 0))
        self.hudButtons.InitButtons()

    def ToggleLockModules(self):
        settings.user.ui.Set('lockModules', not settings.user.ui.Get('lockModules', 0))
        self.slotsContainer.CheckGroupAllButton()

    def ToggleOverloadLock(self):
        settings.user.ui.Set('lockOverload', not settings.user.ui.Get('lockOverload', 0))

    def ToggleShowModuleTooltips(self):
        settings.user.ui.Set('showModuleTooltips', not settings.user.ui.Get('showModuleTooltips', 1))

    def ToggleHudButtons(self):
        isExpanded = self.hudButtons.state == uiconst.UI_PICKCHILDREN
        if isExpanded:
            self.hudButtons.state = uiconst.UI_HIDDEN
        else:
            self.hudButtons.state = uiconst.UI_PICKCHILDREN
        settings.user.ui.Set('hudButtonsExpanded', not isExpanded)
        sm.GetService('ui').StopBlink(self.toggleLeftBtn)
        self.CheckExpandBtns()

    def OnToggleHudModules(self, *args):
        settings.user.ui.Set('displayFighterUI', not settings.user.ui.Get('displayFighterUI', False))
        self.ShowHideFighters()

    def OnToggleFightersDetached(self, *args):
        isDetached = self.IsFightersDetached()
        settings.user.ui.Set('detachFighterUI', not isDetached)
        if isDetached:
            self.AttachHudModules()
        else:
            self.DetachHudModules()

    def AttachHudModules(self):
        self.moduleToggleBtn.Enable()
        self.AlignFighters()
        self.fighterCont.left = 0
        self.fighterCont.top = 10
        self.MakeFighterHudBinding()
        self.ShowHideFighters()
        self.SetFighterButtonsHint()

    def DetachHudModules(self):
        self.moduleToggleBtn.Disable()
        self.slotsContainer.display = True
        self.RemoveFighterHudBinding()
        self.DrawFighters()

    def InitFighters(self):
        if not self.IsFightersDetached():
            self.MakeFighterHudBinding()
            self.ShowHideFighters()
        else:
            self.DetachHudModules()
            self.slotsContainer.display = True

    def ShowHideFighters(self):
        displayFighters = self.IsFightersShown()
        isDetached = self.IsFightersDetached()
        if self.CheckShipHasFighterBay():
            if isDetached:
                self.fighterCont.display = True
                self.slotsContainer.display = True
                return
            if displayFighters == True:
                self.fighterCont.display = True
                self.slotsContainer.display = False
                return
        self.fighterCont.ClearSelection()
        self.fighterCont.display = False
        self.slotsContainer.display = True
        self.DeselectShip()

    def AlignFighters(self):
        if self.IsFightersDetached():
            self.fighterCont.SetAlign(uiconst.TOPLEFT)
        elif IsShipHudTopAligned():
            self.fighterCont.SetAlign(uiconst.TOTOP)
        else:
            self.fighterCont.SetAlign(uiconst.TOBOTTOM)
            self.fighterCont.top = 10

    def IsFightersDetached(self):
        return settings.user.ui.Get('detachFighterUI', False)

    def IsFightersShown(self):
        return settings.user.ui.Get('displayFighterUI', False)

    def CheckExpandBtns(self):
        on = settings.user.ui.Get('hudButtonsExpanded', 1)
        if on:
            self.toggleLeftBtn.LoadTexture('res:/UI/Texture/classes/ShipUI/expandBtnRight.png')
        else:
            self.toggleLeftBtn.LoadTexture('res:/UI/Texture/classes/ShipUI/expandBtnLeft.png')
        self.toggleLeftBtn.hint = [GetByLabel('UI/Inflight/ShowButtons'), GetByLabel('UI/Inflight/HideButtons')][on]

    def AddBookmarks(self, bookmarkIDs):
        isMove = not uicore.uilib.Key(uiconst.VK_SHIFT)
        sm.GetService('invCache').GetInventoryFromId(session.shipid).AddBookmarks(bookmarkIDs, const.flagCargo, isMove)

    def Scanner(self, button):
        self.expandTimer = None
        uicore.layer.menu.Flush()
        radialMenu = RadialMenuScanner(name='radialMenu', parent=uicore.layer.menu, state=uiconst.UI_NORMAL, align=uiconst.TOPLEFT, anchorObject=button)
        uicore.layer.menu.radialMenu = radialMenu
        uicore.uilib.SetMouseCapture(radialMenu)

    def BlinkButton(self, key):
        self.slotsContainer.BlinkButton(key)

    def ChangeOpacityForRange(self, currentRange, *args):
        if getattr(self, 'slotContainer', None):
            self.slotsContainer.ChangeOpacityForRange(self, currentRange)

    def ResetModuleButtonOpacity(self, *args):
        if getattr(self, 'slotContainer', None):
            self.slotsContainer.ResetModuleButtonOpacity()

    def ToggleRackOverload(self, slotName):
        self.slotsContainer.ToggleRackOverload(slotName)

    def ProcessPendingOverloadUpdate(self, moduleIDs):
        self.slotsContainer.ProcessPendingOverloadUpdate(moduleIDs)

    def ResetSwapMode(self):
        self.slotsContainer.ResetSwapMode()

    def StartDragMode(self, itemID, typeID):
        self.slotsContainer.StartDragMode(itemID, typeID)

    def GetPosFromFlag(self, slotFlag):
        return self.slotsContainer.GetPosFromFlag(slotFlag)

    def GetSlotByName(self, name):
        return self.slotsContainer.FindChild(name)

    def ChangeSlots(self, toFlag, fromFlag):
        self.slotsContainer.ChangeSlots(toFlag, fromFlag)

    def SwapSlots(self, slotFlag1, slotFlag2):
        self.slotsContainer.SwapSlots(slotFlag1, slotFlag2)

    def LinkWeapons(self, master, slave, slotFlag1, slotFlag2, merge = False):
        self.slotsContainer.LinkWeapons(master, slave, slotFlag1, slotFlag2, merge)

    def GetModuleType(self, flag):
        return self.slotsContainer.GetModuleType(flag)

    def GetModuleFromID(self, moduleID):
        return self.slotsContainer.GetModuleFromID(moduleID)

    def ToggleShowEmpty(self):
        self.slotsContainer.ToggleShowEmpty()

    def ToggleShowPassive(self):
        self.slotsContainer.ToggleShowPassive()

    def GetModuleForFKey(self, key):
        return self.slotsContainer.GetModuleForFKey(key)

    def GetModule(self, moduleID):
        return self.slotsContainer.GetModule(moduleID)

    def OnF(self, sidx, gidx):
        if not self.CheckShipHasFighterBay():
            self.slotsContainer.OnF(sidx, gidx)
            return
        shipIsSelected, fightersSelected = movementFunctions.GetSelectedShipAndFighters()
        if self.IsFightersDetached():
            moduleIsActive = self.IsModuleActiveForFKey(sidx, gidx)
            isAllAbilitiesActiveOrInCooldown = GetShipFighterState().IsAllAbilitiesInSlotActiveOrInCooldown(sidx)
            if shipIsSelected:
                if isAllAbilitiesActiveOrInCooldown:
                    if moduleIsActive is not None:
                        self.slotsContainer.OnF(sidx, gidx)
                    if moduleIsActive is None or moduleIsActive == True:
                        self.fighterCont.OnF(sidx)
                else:
                    self.fighterCont.OnF(sidx)
                    if moduleIsActive == False:
                        self.slotsContainer.OnF(sidx, gidx)
            else:
                self.fighterCont.OnF(sidx)
        elif self.IsFightersShown():
            self.fighterCont.OnF(sidx)
        else:
            self.slotsContainer.OnF(sidx, gidx)

    def GetModuleDefaultEffect(self, sidx, gidx):
        slot = self.slotsContainer.slotsByOrder.get((gidx, sidx), None)
        if not slot:
            return
        if not slot.sr.module:
            return
        if slot.sr.module.state != uiconst.UI_NORMAL:
            return
        if slot.sr.module.def_effect is None:
            return
        return slot.sr.module.def_effect

    def IsModuleActiveForFKey(self, sidx, gidx):
        defaultEffect = self.GetModuleDefaultEffect(sidx, gidx)
        if defaultEffect:
            return defaultEffect.isActive

    def OnFKeyOverload(self, sidx, gidx):
        self.slotsContainer.OnFKeyOverload(sidx, gidx)

    def OnReloadAmmo(self):
        self.slotsContainer.OnReloadAmmo()

    def OnCloseView(self):
        self.ResetSelf()
        settings.user.ui.Set('selected_shipuicateg', self.sr.selectedcateg)
        t = uthread.new(sm.GetService('space').OnShipUIReset)
        t.context = 'ShipUI::OnShipUIReset'

    @telemetry.ZONE_METHOD
    def DoBallsRemove(self, pythonBalls, isRelease):
        if isRelease:
            self.UnhookBall()
            self.jammers = {}
            return
        for ball, slimItem, terminal in pythonBalls:
            self.DoBallRemove(ball, slimItem, terminal)

        if isRelease:
            self.compass.RemoveAll()

    def DoBallRemove(self, ball, slimItem, terminal):
        if ball is None:
            return
        log.LogInfo('DoBallRemove::shipui', ball.id)
        if self.controller.GetBall() is not None and ball.id == self.controller.GetBall().id:
            self.UnhookBall()
        uthread.new(self.UpdateJammersAfterBallRemoval, ball.id)

    def UpdateJammersAfterBallRemoval(self, ballID):
        jams = self.jammers.keys()
        for jammingType in jams:
            jam = self.jammers[jammingType]
            for id in jam.keys():
                sourceBallID, moduleID, targetBallID = id
                if ballID == sourceBallID:
                    del self.jammers[jammingType][id]

    def ProcessShipEffect(self, godmaStm, effectState):
        if effectState.error is not None:
            uthread.new(uicore.Message, effectState.error[0], effectState.error[1])

    def OnJamStart(self, sourceBallID, moduleID, targetBallID, jammingType, startTime, duration):
        durationInClient = GetDurationInClient(startTime, duration)
        if durationInClient < 0.0:
            return
        if jammingType not in self.jammers:
            self.jammers[jammingType] = {}
        jammerID = (sourceBallID, moduleID, targetBallID)
        self.jammers[jammingType][jammerID] = (blue.os.GetSimTime(), durationInClient)
        if self.ewarCont and targetBallID == session.shipid:
            self.ewarCont.StartTimer(jammingType, jammerID, durationInClient)

    def OnJamEnd(self, sourceBallID, moduleID, targetBallID, jammingType):
        if jammingType in self.jammers:
            jammerID = (sourceBallID, moduleID, targetBallID)
            if jammerID in self.jammers[jammingType]:
                del self.jammers[jammingType][jammerID]

    def OnShipScanCompleted(self, shipID, capacitorCharge, capacitorCapacity, hardwareList):
        bp = sm.GetService('michelle').GetBallpark()
        if not bp:
            return
        slimItem = bp.slimItems[shipID]
        wndName = GetByLabel('UI/Inflight/ScanWindowName', itemName=GetSlimItemName(slimItem), title=GetByLabel('UI/Inflight/ScanResult'))
        import form
        form.ShipScan.CloseIfOpen(windowID=('shipscan', shipID))
        form.ShipScan.Open(windowID=('shipscan', shipID), caption=wndName, shipID=shipID, results=(capacitorCharge, capacitorCapacity, hardwareList))

    def OnCargoScanComplete(self, shipID, cargoList):
        bp = sm.GetService('michelle').GetBallpark()
        if not bp:
            return
        slimItem = bp.slimItems[shipID]
        windowID = ('cargoscanner', shipID)
        import form
        wnd = form.CargoScan.Open(windowID=windowID, shipID=shipID, cargoList=cargoList)
        if wnd:
            wnd.LoadResult(cargoList)

    def UnhookBall(self):
        self.controller.InvalidateBall()

    def OnShipChanged(self, *args):
        self.SetupShip(animate=True)

    def SetupShip(self, animate = False):
        if self.setupShipTasklet is not None:
            self.setupShipTasklet.kill()
        self.setupShipTasklet = uthread.new(self._SetupShip, animate)

    @telemetry.ZONE_METHOD
    def _SetupShip(self, animate = False):
        if self.destroyed or self.initing or not self.shipuiReady:
            return
        self.initing = True
        try:
            if not self.controller.IsLoaded():
                return
            if not sm.GetService('viewState').IsViewActive('planet') and not (eve.hiddenUIState and 'shipui' in eve.hiddenUIState):
                self.state = uiconst.UI_PICKCHILDREN
            self.ResetUpdateTasklet()
            self.sr.rampTimers = {}
            self.slotsContainer.InitSlots(animate)
            self.hudButtons.InitButtons()
            self.SetButtonState()
            self.CheckExpandBtns()
            self.CheckControl()
            self.UpdateButtonsForShip()
            self.capacitorContainer.InitCapacitor()
            self.DrawFighters()
            self.InitFighters()
            self.ShowHideFighters()
            if self.CheckShipHasFighterBay():
                self.moduleToggleBtn.display = True
            else:
                self.moduleToggleBtn.display = False
                if self.shipSelectHilight.display:
                    self.shipSelectHilight.display = False
            blue.pyos.synchro.SleepWallclock(200)
        finally:
            self.initing = False

    def ResetUpdateTasklet(self):
        if self.updateTasklet:
            self.updateTasklet.kill()
        self.updateTasklet = uthread.new(self.UpdateGauges)

    def SetSpeed(self, speedRatio):
        self.controller.SetSpeed(speedRatio)

    def Hide(self):
        self.state = uiconst.UI_HIDDEN

    def Show(self):
        self.state = uiconst.UI_PICKCHILDREN

    def OnMouseEnter(self, *args):
        uicore.layer.inflight.HideTargetingCursor()

    def GetMenu(self):
        return self.controller.GetMenu()

    @telemetry.ZONE_FUNCTION
    def UpdateGauges(self):
        while not self.destroyed:
            try:
                if self.controller.IsLoaded():
                    self.heatGauges.Update()
                    self.hpGauges.Update()
                    self.UpdateReadouts()
            except Exception as e:
                log.LogException(e)

            blue.synchro.SleepWallclock(500)

    def UpdateReadouts(self):
        structure = self.controller.GetStructureHPPortion()
        armor = self.controller.GetArmorHPPortion()
        shield = self.controller.GetShieldHPPortion()
        self.CheckShowReadoutCont()
        if self.readoutCont.state != uiconst.UI_HIDDEN:
            if settings.user.ui.Get('readoutType', 1):
                self.readoutShieldLabel.text = GetByLabel('UI/Common/Formatting/Percentage', percentage=shield * 100)
                self.readoutArmorLabel.text = GetByLabel('UI/Common/Formatting/Percentage', percentage=armor * 100)
                self.readoutStructureLabel.text = GetByLabel('UI/Common/Formatting/Percentage', percentage=structure * 100)
            else:
                self.readoutShieldLabel.text = GetByLabel('UI/Inflight/GaugeAbsolute', left=self.controller.GetShieldHP(), total=self.controller.GetShieldHPMax())
                self.readoutArmorLabel.text = GetByLabel('UI/Inflight/GaugeAbsolute', left=self.controller.GetArmorHP(), total=self.controller.GetArmorHPMax())
                self.readoutStructureLabel.text = GetByLabel('UI/Inflight/GaugeAbsolute', left=self.controller.GetStructureHP(), total=self.controller.GetStructureHPMax())

    def OnSafeLogoffTimerStarted(self, safeLogoffTime):
        if self.logoffTimer is not None:
            self.logoffTimer.Close()
        self.logoffTimer = SafeLogoffTimer(parent=uicore.layer.abovemain, logoffTime=safeLogoffTime)
        self.logoffTimer.left = sm.GetService('window').GetCameraLeftOffset(self.logoffTimer.width, self.logoffTimer.align, self.logoffTimer.left)

    def OnSafeLogoffActivated(self):
        if self.logoffTimer is not None:
            self.logoffTimer.timer.SetText('0.0')
            self.logoffTimer.timer.SetTextColor(Color.GREEN)
        sm.GetService('clientStatsSvc').OnProcessExit()

    def OnSafeLogoffAborted(self, reasonCode):
        self.AbortSafeLogoffTimer()
        uicore.Message('CustomNotify', {'notify': GetByLabel(reasonCode)})

    def OnSafeLogoffFailed(self, failedConditions):
        self.AbortSafeLogoffTimer()
        uicore.Message('CustomNotify', {'notify': '<br>'.join([GetByLabel('UI/Inflight/SafeLogoff/ConditionsFailedHeader')] + [ GetByLabel(error) for error in failedConditions ])})

    def AbortSafeLogoffTimer(self):
        if self.logoffTimer is not None:
            self.logoffTimer.AbortLogoff()
            self.logoffTimer = None


class MaxSpeedButton(Sprite):
    default_name = 'MaxSpeedButton'
    default_width = 12
    default_height = 12
    default_state = uiconst.UI_NORMAL
    default_texturePath = 'res:/UI/Texture/classes/ShipUI/plus.png'

    def ApplyAttributes(self, attributes):
        Sprite.ApplyAttributes(self, attributes)
        self.controller = attributes.controller

    def OnClick(self, *args):
        self.controller.SetMaxSpeed()

    def GetHint(self):
        return GetByLabel('UI/Inflight/SetFullSpeed', maxSpeed=self.controller.GetSpeedMaxFormatted())


class StopButton(Sprite):
    default_name = 'StopButton'
    default_width = 12
    default_height = 12
    default_state = uiconst.UI_NORMAL
    default_texturePath = 'res:/UI/Texture/classes/ShipUI/minus.png'
    default_hint = GetByLabel('UI/Inflight/StopTheShip')

    def ApplyAttributes(self, attributes):
        Sprite.ApplyAttributes(self, attributes)
        self.controller = attributes.controller

    def OnClick(self, *args):
        self.controller.StopShip()
