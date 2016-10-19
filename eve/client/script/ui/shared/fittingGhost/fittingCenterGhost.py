#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\fittingGhost\fittingCenterGhost.py
import math
from carbonui.primitives.container import Container
import carbonui.const as uiconst
from carbonui.primitives.sprite import Sprite
from eve.client.script.ui.control.scenecontainer import SceneContainerBaseNavigation
from eve.client.script.ui.shared.fittingGhost import SIMULATION_MODULES
from eve.client.script.ui.shared.fittingGhost.fittingLayout import FittingLayoutGhost
from eve.client.script.ui.shared.fitting.fittingUtil import GetScaleFactor
from eve.client.script.ui.shared.fittingGhost.slotGhost import FittingSlotGhost
from eve.client.script.ui.shared.fitting.shipSceneContainer import ShipSceneContainer
from eve.client.script.ui.shared.fitting.slotAdder import SlotAdder
from eve.client.script.ui.station.fitting.stanceSlot import StanceSlots
from eve.common.script.sys.eveCfg import IsControllingStructure
from eve.client.script.ui.inflight.shipHud.groupAllIcon import GroupAllButton
import uthread
import blue

class FittingCenterGhost(FittingLayoutGhost):
    default_align = uiconst.CENTER
    default_state = uiconst.UI_PICKCHILDREN

    def ApplyAttributes(self, attributes):
        FittingLayoutGhost.ApplyAttributes(self, attributes)
        self.controller = attributes.controller
        self.controller.on_stats_changed.connect(self.UpdateGauges)
        self.controller.on_new_itemID.connect(self.OnNewItem)
        self.controller.on_slots_with_menu_changed.connect(self.OnSlotsWithMenuChanged)
        self.controller.on_simulation_mode_changed.connect(self.OnSimulationModeChanged)
        self.controller.on_simulation_state_changed.connect(self.OnSimulationStateChanged)
        self.slots = {}
        self.slotList = []
        self.menuSlots = {}
        self.AddSlots()
        self.AddSceneContainer()
        uthread.new(self.AnimateSlots)
        self.UpdateGauges()
        self.SetShipStance()
        if self.controller.IsSimulated():
            self.ChangeRadialMenuIconDisplayByMode()
            showGroupAll = False
        else:
            self.ChangeRadialMenuIconDisplay(displayState=False)
            showGroupAll = True
        self.groupAllButton.display = showGroupAll

    def OnNewItem(self):
        self.UpdateGauges()
        self.SetShipStance()

    def GetSlots(self):
        return self.slots

    def AddToSlotsWithMenu(self, slot):
        self.menuSlots[slot] = 1

    def ClearSlotsWithMenu(self):
        for slot in self.menuSlots.iterkeys():
            slot.HideUtilButtons()

        self.menuSlots = {}

    def AddSceneContainer(self):
        size = 550 * GetScaleFactor()
        self.sceneContainerParent = ShipSceneParent(parent=self, align=uiconst.CENTER, width=size, height=size, shipID=self.controller.GetItemID(), controller=self.controller)
        self.sceneContainer = self.sceneContainerParent.sceneContainer
        self.sceneNavigation = self.sceneContainerParent.sceneNavigation

    def AddSlots(self):
        self.slotCont = Container(parent=self, name='slotCont', align=uiconst.TOALL, state=uiconst.UI_PICKCHILDREN, idx=0)
        self.slotList = []
        slotAdder = SlotAdder(self.controller, FittingSlotGhost)
        for groupIdx, group in self.controller.GetSlotsByGroups().iteritems():
            if groupIdx < 0:
                continue
            arcStart, arcLength = self.controller.SLOTGROUP_LAYOUT_ARCS[groupIdx]
            slotAdder.StartGroup(arcStart, arcLength, len(group))
            for slotIdx, slotController in enumerate(group):
                slot = slotAdder.AddSlot(self.slotCont, slotController.flagID)
                self.slotList.append(slot)
                self.slots[slotController.flagID] = slot

        self.stances = StanceSlots(parent=self.slotCont, shipID=self.controller.GetItemID(), angleToPos=lambda angle: slotAdder.GetPositionNumbers(angle), typeID=self.controller.GetTypeID(), controller=self.controller)
        self.slotList.extend(self.stances.GetStanceContainers())
        self.AddRadialMenuIcons()

    def AddRadialMenuIcons(self):
        import inventorycommon.const as invConst
        rad = int(243 * self.scaleFactor)
        cX = cY = self.baseShapeSize / 2

        def GetLocation(angle, size = 16):
            cos = math.cos(angle * math.pi / 180.0)
            sin = math.sin(angle * math.pi / 180.0)
            left = int(round(rad * cos + cX - size / 2))
            top = int(round(rad * sin + cY - size / 2))
            return (left, top)

        left, top = GetLocation(227)
        texturePath = 'res:/ui/Texture/classes/RadialMenu/fitting/high.png'
        self.allHiSlotsIcon = Sprite(name='hiSlotRadial', parent=self.slotCont, align=uiconst.TOPLEFT, texturePath=texturePath, pos=(left,
         top,
         16,
         16), state=uiconst.UI_NORMAL)
        self.allHiSlotsIcon.OnMouseDown = (self.TryOpenRadialMenu, self.allHiSlotsIcon, invConst.hiSlotFlags)
        left, top = GetLocation(315)
        texturePath = 'res:/ui/Texture/classes/RadialMenu/fitting/med.png'
        self.allMedSlotsIcon = Sprite(name='medSlotRadial', parent=self.slotCont, align=uiconst.TOPLEFT, texturePath=texturePath, pos=(left,
         top,
         16,
         16))
        self.allMedSlotsIcon.OnMouseDown = (self.TryOpenRadialMenu, self.allMedSlotsIcon, invConst.medSlotFlags)
        left, top = GetLocation(45)
        texturePath = 'res:/ui/Texture/classes/RadialMenu/fitting/low.png'
        self.allLoSlotsIcon = Sprite(name='loSlotRadial', parent=self.slotCont, align=uiconst.TOPLEFT, texturePath=texturePath, pos=(left,
         top,
         16,
         16))
        self.allLoSlotsIcon.OnMouseDown = (self.TryOpenRadialMenu, self.allLoSlotsIcon, invConst.loSlotFlags)
        left, top = GetLocation(227)
        self.groupAllButton = GroupAllButton(parent=self, idx=0, left=left, top=top)

    def CheckGroupAllButton(self):
        if self.groupAllButton is not None and not self.groupAllButton.destroyed:
            self.groupAllButton.CheckGroupAllButton()

    def TryOpenRadialMenu(self, icon, slotList, *args):
        uthread.new(self.ExpandRadialMenu, icon, slotList)

    def ExpandRadialMenu(self, anchorObject, slotList, *args):
        from eve.client.script.ui.shared.fittingGhost.fittingRadialMenu import RadialMenuFitting
        radialMenu = RadialMenuFitting(name='radialMenuFitting', parent=uicore.layer.menu, state=uiconst.UI_NORMAL, align=uiconst.TOPLEFT, anchorObject=anchorObject, slotList=slotList)
        uicore.layer.menu.radialMenu = radialMenu
        uicore.uilib.SetMouseCapture(radialMenu)

    def ChangeRadialMenuIconDisplay(self, displayState):
        for element in [self.allHiSlotsIcon, self.allMedSlotsIcon, self.allLoSlotsIcon]:
            element.display = displayState

    def AnimateSlots(self):
        uthread.new(self.EntryAnimation, self.slotList)

    def EntryAnimation(self, toAnimate):
        for obj in toAnimate:
            obj.opacity = 0.0

        for i, obj in enumerate(toAnimate):
            if obj.state == uiconst.UI_DISABLED:
                endOpacity = 0.05
            else:
                endOpacity = 1.0
                sm.GetService('audio').SendUIEvent('wise:/msg_fittingSlotHi_play')
            uicore.animations.FadeTo(obj, 0.0, endOpacity, duration=0.3)
            blue.synchro.SleepWallclock(5)

    def UpdateGauges(self):
        self.UpdatePowerGauge()
        self.UpdateCPUGauge()
        self.UpdateCalibrationGauge()

    def UpdatePowerGauge(self):
        powerLoad = self.controller.GetPowerLoad()
        powerOutput = self.controller.GetPowerOutput()
        portion = 0.0
        if powerLoad.value:
            if powerOutput.value == 0.0:
                portion = 1.0
            else:
                portion = powerLoad.value / powerOutput.value
        self.powerGauge.SetValue(portion)

    def UpdateCPUGauge(self):
        cpuLoad = self.controller.GetCPULoad()
        cpuOutput = self.controller.GetCPUOutput()
        portion = 0.0
        if cpuLoad:
            if cpuOutput.value == 0:
                portion = 1
            else:
                portion = cpuLoad.value / cpuOutput.value
        self.cpuGauge.SetValue(portion)

    def UpdateCalibrationGauge(self):
        calibrationLoad = self.controller.GetCalibrationLoad()
        calibrationOutput = self.controller.GetCalibrationOutput()
        if calibrationLoad.value and calibrationOutput.value > 0:
            portion = calibrationLoad.value / calibrationOutput.value
        else:
            portion = 0.0
        self.calibrationGauge.SetValue(portion)

    def SetShipStance(self):
        if self.controller.HasStance():
            self.ShowStanceButtons()
        else:
            self.HideStanceButtons()

    def ShowStanceButtons(self):
        self.stances.display = True
        self.stances.ShowStances(self.controller.GetItemID(), self.controller.GetTypeID())

    def HideStanceButtons(self):
        self.stances.display = False

    def GetTooltipPosition(self):
        return (uicore.uilib.x - 5,
         uicore.uilib.y - 5,
         10,
         10)

    def OnSlotsWithMenuChanged(self, oldFlagID, newFlagID):
        slot = self.slots.get(oldFlagID, None)
        if slot is not None:
            slot.HideUtilButtons()

    def OnSimulationStateChanged(self, isSimulated):
        if isSimulated:
            self.ChangeRadialMenuIconDisplayByMode()
        else:
            self.ChangeRadialMenuIconDisplay(displayState=False)
        self.groupAllButton.display = not isSimulated

    def OnSimulationModeChanged(self, newMode):
        self.ChangeRadialMenuIconDisplayByMode()

    def ChangeRadialMenuIconDisplayByMode(self):
        simulationMode = sm.GetService('ghostFittingSvc').GetSimulationMode()
        if simulationMode == SIMULATION_MODULES:
            displayState = True
        else:
            displayState = False
        self.ChangeRadialMenuIconDisplay(displayState=displayState)


class ShipSceneParent(Container):

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.controller = attributes.controller
        self.controller.on_new_itemID.connect(self.OnNewShipLoaded)
        self.sceneContainer = ShipSceneContainer(align=uiconst.TOALL, parent=self, state=uiconst.UI_DISABLED, controller=self.controller)
        self.SetScene()
        self.sceneContainer.LoadShipModel()
        scaleFactor = GetScaleFactor()
        self.sceneNavigation = SceneContainerBaseNavigation(parent=self, align=uiconst.TOALL, pos=(0, 0, 0, 0), idx=0, state=uiconst.UI_NORMAL, pickRadius=225 * scaleFactor)
        self.sceneNavigation.Startup(self.sceneContainer)
        self.sceneNavigation.OnDropData = self.OnDropData
        self.sceneNavigation.GetMenu = self.GetShipMenu

    def SetScene(self):
        scenePath = self.controller.GetScenePath()
        self.sceneContainer.PrepareSpaceScene(scenePath=scenePath)
        self.sceneContainer.SetStencilMap()

    def OnNewShipLoaded(self):
        self.SetScene()
        self.sceneContainer.ReloadShipModel()

    def OnDropData(self, dragObj, nodes):
        self.controller.OnDropData(dragObj, nodes)

    def GetShipMenu(self, *args):
        if self.controller.GetItemID() is None:
            return []
        if self.controller.IsSimulated():
            return sm.GetService('menu').GetMenuFormItemIDTypeID(None, typeID=self.controller.GetTypeID(), ignoreMarketDetails=False)
        if IsControllingStructure():
            return sm.GetService('menu').CelestialMenu(session.structureid)
        if session.stationid or session.structureid:
            hangarInv = sm.GetService('invCache').GetInventory(const.containerHangar)
            hangarItems = [hangarInv.GetItem()] + hangarInv.List(const.flagHangar)
            for each in hangarItems:
                if each and each.itemID == self.controller.GetItemID():
                    return sm.GetService('menu').InvItemMenu(each)

        elif session.solarsystemid:
            return sm.GetService('menu').CelestialMenu(session.shipid)
