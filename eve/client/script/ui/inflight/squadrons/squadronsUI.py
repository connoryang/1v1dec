#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\inflight\squadrons\squadronsUI.py
from collections import namedtuple
from carbon.common.lib.const import SEC
from carbonui.control.menuLabel import MenuLabel
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from eve.client.script.parklife import states
from eve.client.script.ui.control.buttons import ButtonIcon
from eve.client.script.ui.control.tooltips import ShortcutHint
from eve.client.script.ui.inflight.shipHud.leftSideButton import LeftSideButton
from eve.client.script.ui.inflight.squadrons.effectsCont import EffectsCont
from eve.client.script.ui.inflight.squadrons.abilitiesCont import AbilitiesCont
from eve.client.script.ui.inflight.squadrons.shipFighterState import GetShipFighterState
from eve.client.script.ui.inflight.squadrons.squadronCont import SquadronCont, SquadronContEmpty
from eve.client.script.ui.inflight.squadrons.squadronController import SquadronController
import carbonui.const as uiconst
from eve.client.script.ui.inflight.squadrons.squadronManagementController import SquadronMgmtController
from eve.client.script.ui.services.menuSvcExtras import movementFunctions
from eve.client.script.ui.shared.inventory.invWindow import Inventory
from eve.common.script.mgt.fighterConst import TUBE_STATE_EMPTY, TUBE_STATE_READY, TUBE_STATE_UNLOADING
from eve.common.script.sys.eveCfg import GetActiveShip
from fighters import TARGET_MODE_POINTTARGETED, TARGET_MODE_UNTARGETED, TARGET_MODE_ITEMTARGETED
from fighters.client import GetFighterTubesForShip, SquadronIsHeavy, SquadronIsSupport, SquadronIsLight
import gametime
from localization import GetByLabel
from utillib import KeyVal
from collections import defaultdict
SelectedFighterTuple = namedtuple('SelectedFighterTuple', ['fighterItemID', 'tubeFlagID', 'squadron'])
SQUADRON_WIDTH = 80
BUTTONCONT_WIDTH = 36
HUDBUTTON_HEIGHT = 32

class SquadronsUI(ContainerAutoSize):
    default_width = SQUADRON_WIDTH
    default_height = 266

    def ApplyAttributes(self, attributes):
        ContainerAutoSize.ApplyAttributes(self, attributes)
        self.shipFighterState = GetShipFighterState()
        self.parentFunc = attributes.parentFunc
        self.squadrons = []
        self.lastSelected = None
        left = BUTTONCONT_WIDTH + 4
        numOfTubes = GetFighterTubesForShip()
        self.DrawControlButtons()
        for i, tubeFlagID in enumerate(const.fighterTubeFlags):
            if i < numOfTubes:
                squadron = SquadronUI(parent=self, align=uiconst.BOTTOMLEFT, tubeFlagID=tubeFlagID, left=left)
                left = squadron.left + squadron.width + 6
                self.squadrons.append(squadron)
                self.width += SQUADRON_WIDTH

    def DrawControlButtons(self):
        buttonCont = Container(parent=self, align=uiconst.BOTTOMLEFT, width=BUTTONCONT_WIDTH, height=120)
        self.fighterToggleBtn = FighterDragButton(name='fighterToggleBtn', parent=buttonCont, align=uiconst.BOTTOMLEFT, top=0, left=2, iconSize=24, texturePath='res:/UI/Texture/classes/ShipUI/Fighters/positionFighters_Up.png', downTexture='res:/UI/Texture/classes/ShipUI/Fighters/positionFighters_Down.png', hoverTexture='res:/UI/Texture/classes/ShipUI/Fighters/positionFighters_Over.png', func=self.OnToggleFightersDetached)
        self.recallAll = FightersButtonRecallAll(parent=buttonCont, align=uiconst.BOTTOMLEFT, top=25)
        self.openFighterBay = self.GetFighterBayBtn(buttonCont)
        self.launchAll = FightersButtonLaunchAll(parent=buttonCont, align=uiconst.BOTTOMLEFT, top=25 + HUDBUTTON_HEIGHT * 2)

    def GetFighterBayBtn(self, buttonCont):
        if session.structureid:
            return FightersButtonOpenStructureBay(parent=buttonCont, align=uiconst.BOTTOMLEFT, top=25 + HUDBUTTON_HEIGHT)
        else:
            return FightersButtonOpenBay(parent=buttonCont, align=uiconst.BOTTOMLEFT, top=25 + HUDBUTTON_HEIGHT)

    def OnToggleFightersDetached(self, *args):
        self.parentFunc(args)
        self.KeepSelection()

    def KeepSelection(self):
        selectedFighters = movementFunctions.GetFightersSelectedForNavigation()
        for fighterID in selectedFighters:
            movementFunctions.SelectForNavigation(fighterID)

    def SelectAll(self):
        for squadron in self.squadrons:
            squadron.SelectSquadron()

    def ClearSelection(self):
        for squadron in self.squadrons:
            squadron.DeselectSquadron()

    def GetSelectedSquadrons(self):
        selectedSquadrons = []
        for squadron in self.squadrons:
            if squadron.IsSelected():
                selectedSquadrons.append(SelectedFighterTuple(fighterItemID=squadron.GetFighterItemID(), tubeFlagID=squadron.tubeFlagID, squadron=squadron))

        return selectedSquadrons

    def OnF(self, abilitySlotID):
        untargetedAbilityFighters = []
        itemTargetedAbilityFighters = []
        pointTargetedAbilityFighters = []
        isAllAbilitiesActive = self.shipFighterState.IsAllAbilitiesInSlotActiveOrInCooldown(abilitySlotID)
        for squadron in self.GetSelectedSquadrons():
            try:
                ability = squadron.squadron.modulesCont.abilityIcons[abilitySlotID]
            except KeyError:
                continue

            abilityActivationStatus = self.shipFighterState.GetAbilityActivationStatus(squadron.fighterItemID, abilitySlotID)
            if isAllAbilitiesActive:
                if abilityActivationStatus:
                    if abilityActivationStatus.isPending:
                        continue
                    if abilityActivationStatus.isDeactivating:
                        continue
            else:
                if abilityActivationStatus:
                    continue
                if self.shipFighterState.GetAbilityCooldown(squadron.fighterItemID, abilitySlotID):
                    continue
            if ability.targetMode == TARGET_MODE_UNTARGETED:
                untargetedAbilityFighters.append(squadron.fighterItemID)
            elif ability.targetMode == TARGET_MODE_ITEMTARGETED:
                itemTargetedAbilityFighters.append(squadron.fighterItemID)
            elif ability.targetMode == TARGET_MODE_POINTTARGETED:
                pointTargetedAbilityFighters.append(squadron.fighterItemID)

        fightersSvc = sm.GetService('fighters')
        if isAllAbilitiesActive:
            fighterIDs = untargetedAbilityFighters + itemTargetedAbilityFighters + pointTargetedAbilityFighters
            fightersSvc.DeactivateAbilitySlots(fighterIDs, abilitySlotID)
        else:
            if untargetedAbilityFighters:
                fightersSvc.ActivateAbilitySlotsOnSelf(untargetedAbilityFighters, abilitySlotID)
            if itemTargetedAbilityFighters:
                targetID = sm.GetService('target').GetActiveTargetID()
                fightersSvc.ActivateAbilitySlotsOnTarget(itemTargetedAbilityFighters, abilitySlotID, targetID)
            if pointTargetedAbilityFighters:
                eveCommands = sm.GetService('cmd')
                eveCommands.CmdAimMultiSquadronFighterAbilities(pointTargetedAbilityFighters, abilitySlotID)

    def SetLastSelectedTube(self, tubeFlagID):
        self.lastSelected = tubeFlagID

    def GetLastSelectedTube(self):
        return self.lastSelected

    def MultiSelectSquadrons(self, selectedSquadron):
        if selectedSquadron <= self.lastSelected:
            minSelected = selectedSquadron
            maxSelected = self.lastSelected
        else:
            minSelected = self.lastSelected
            maxSelected = selectedSquadron
        for squadron in self.squadrons:
            if squadron.tubeFlagID >= minSelected and squadron.tubeFlagID <= maxSelected:
                squadron.SelectSquadron()


class SquadronUI(Container):
    __notifyevents__ = ['OnStateChange']
    default_width = SQUADRON_WIDTH
    default_height = 266
    default_name = 'squadronCont'

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        sm.RegisterNotify(self)
        self.squadronMgmtController = SquadronMgmtController()
        self.inSpace = False
        self.shipFighterState = GetShipFighterState()
        self.tubeFlagID = attributes.tubeFlagID
        fighters = self.GetFightersState()
        if fighters:
            fighterID = fighters.itemID
            fighterTypeID = fighters.typeID
            squadronSize = fighters.squadronSize
        else:
            fighterID = None
            fighterTypeID = None
            squadronSize = None
        self.fighterID = fighterID
        self.fighterTypeID = fighterTypeID
        self.controller = SquadronController()
        self.squadronCont = SquadronCont(parent=self, controller=self.controller, align=uiconst.BOTTOMLEFT, tubeFlagID=self.tubeFlagID, state=uiconst.UI_NORMAL)
        self.squadronCont.OnClick = self.OnSquadronClick
        self.squadronCont.GetMenu = self.GetSquadronMenu
        self.squadronCont.SetNewSquadron(fighterID, fighterTypeID, squadronSize)
        self.squadronContEmpty = SquadronContEmpty(parent=self, controller=self.controller, fighterID=fighterID, fighterTypeID=fighterTypeID, align=uiconst.BOTTOMLEFT, tubeFlagID=self.tubeFlagID)
        self.squadronContEmpty.GetMenu = self.GetSquadronMenu
        if not fighterID and not fighterTypeID:
            self.ShowEmpty()
        else:
            self.HideEmpty()
        self.effectsCont = EffectsCont(parent=self, controller=self.controller, fighterID=fighterID, fighterTypeID=fighterTypeID, tubeFlagID=self.tubeFlagID, top=self.squadronCont.height, align=uiconst.BOTTOMLEFT)
        self.modulesCont = AbilitiesCont(parent=self, left=20, top=self.squadronCont.height, align=uiconst.BOTTOMLEFT)
        self.modulesCont.SetNewSquadron(fighterID, fighterTypeID)
        self.SetupFighters()
        self.shipFighterState.signalOnFighterTubeStateUpdate.connect(self.OnFighterTubeStateUpdate)
        self.shipFighterState.signalOnFighterTubeContentUpdate.connect(self.OnFighterTubeContentUpdate)
        self.shipFighterState.signalOnFighterInSpaceUpdate.connect(self.OnFighterInSpaceUpdate)
        self.shipFighterState.signalOnIncomingEwarStarted.connect(self.OnEwarUpdated)
        self.shipFighterState.signalOnIncomingEwarEnded.connect(self.OnEwarUpdated)

    def SetupFighters(self):
        if self.inSpace:
            self.ShowInSpaceUI()
        else:
            self.HideInSpaceUI()

    def ShowInSpaceUI(self):
        self.modulesCont.ShowModules()
        self.effectsCont.ShowEffects()

    def HideInSpaceUI(self):
        self.modulesCont.HideModules()
        self.effectsCont.HideEffects()

    def ShowEmpty(self):
        self.squadronContEmpty.display = True
        self.squadronCont.display = False

    def HideEmpty(self):
        self.squadronContEmpty.display = False
        self.squadronCont.display = True

    def GetFightersInSpaceState(self):
        fighterInSpace = self.shipFighterState.GetFightersInSpace(self.tubeFlagID)
        if fighterInSpace is not None:
            self.inSpace = True
            return fighterInSpace

    def GetFightersInTubeState(self):
        fighterInTube = self.shipFighterState.GetFightersInTube(self.tubeFlagID)
        if fighterInTube is not None:
            self.inSpace = False
            return fighterInTube

    def GetFightersState(self):
        fightersInTube = self.GetFightersInTubeState()
        if fightersInTube:
            return fightersInTube
        fightersInSpace = self.GetFightersInSpaceState()
        if fightersInSpace:
            return fightersInSpace

    def OnEwarUpdated(self, targetBallID, sourceBallID, sourceModuleID, jammingType):
        if targetBallID != self.fighterID:
            return
        self.effectsCont.BuildEffectsData()

    def OnFighterTubeStateUpdate(self, tubeFlagID):
        if tubeFlagID == self.tubeFlagID:
            tubeStatus = self.shipFighterState.GetTubeStatus(self.tubeFlagID)
            self.squadronCont.SetSquadronAction(self.tubeFlagID)
            if tubeStatus.statusID == TUBE_STATE_EMPTY:
                self.ShowEmpty()
            else:
                self.HideEmpty()
                if tubeStatus.endTime:
                    self.squadronCont.loadingGauge.display = True
                    now = gametime.GetSimTime()
                    duration = float(tubeStatus.endTime - tubeStatus.startTime)
                    loadingProgress = max(0.0, min(1.0, (now - tubeStatus.startTime) / duration))
                    self.squadronCont.loadingGauge.SetValue(loadingProgress, animate=False)
                    remainingTime = tubeStatus.endTime - now
                    remainingTimeSeconds = max(float(remainingTime) / SEC, 0.1)
                    self.squadronCont.loadingGauge.SetValueTimed(1.0, remainingTimeSeconds)
                else:
                    self.squadronCont.loadingGauge.display = False

    def OnFighterTubeContentUpdate(self, tubeFlagID):
        if tubeFlagID == self.tubeFlagID:
            tubeStatus = self.shipFighterState.GetTubeStatus(self.tubeFlagID)
            if tubeStatus.statusID in (TUBE_STATE_EMPTY, TUBE_STATE_READY, TUBE_STATE_UNLOADING):
                self.ShowEmpty()
                self.squadronCont.ClearFighters()
            else:
                self.HideEmpty()
                fightersInTube = self.GetFightersInTubeState()
                if fightersInTube:
                    self.squadronCont.SetNewSquadron(fightersInTube.itemID, fightersInTube.typeID, fightersInTube.squadronSize)
                    self.fighterID = fightersInTube.itemID
                    self.fighterTypeID = fightersInTube.typeID
                    self.effectsCont.UpdateFighterID(self.fighterID)

    def OnFighterInSpaceUpdate(self, fighterID, tubeFlagID):
        if tubeFlagID == self.tubeFlagID:
            fightersInSpace = self.GetFightersInSpaceState()
            if fightersInSpace:
                self.squadronCont.SetNewSquadron(fightersInSpace.itemID, fightersInSpace.typeID, fightersInSpace.squadronSize)
                self.modulesCont.SetNewSquadron(fightersInSpace.itemID, fightersInSpace.typeID)
                self.squadronCont.SetSquadronInfo(tubeFlagID)
                self.ShowInSpaceUI()
            else:
                self.squadronCont.StopSquadronTimer()
                self.HideInSpaceUI()

    def Close(self):
        self.shipFighterState.signalOnFighterTubeStateUpdate.disconnect(self.OnFighterTubeStateUpdate)
        self.shipFighterState.signalOnFighterTubeContentUpdate.disconnect(self.OnFighterTubeContentUpdate)
        self.shipFighterState.signalOnFighterInSpaceUpdate.disconnect(self.OnFighterInSpaceUpdate)
        self.shipFighterState.signalOnIncomingEwarStarted.disconnect(self.OnEwarUpdated)
        self.shipFighterState.signalOnIncomingEwarEnded.disconnect(self.OnEwarUpdated)
        self.squadronCont.damageTimer = None
        Container.Close(self)

    def OnSquadronClick(self, *args):
        ctrl = uicore.uilib.Key(uiconst.VK_CONTROL)
        shift = uicore.uilib.Key(uiconst.VK_SHIFT)
        if not ctrl and not shift and uicore.cmd.IsSomeCombatCommandLoaded():
            uicore.cmd.ExecuteCombatCommand(self.fighterID, uiconst.UI_CLICK)
        elif shift:
            if self.parent.GetLastSelectedTube():
                self.parent.MultiSelectSquadrons(self.tubeFlagID)
                self.parent.SetLastSelectedTube(self.tubeFlagID)
        elif ctrl:
            if movementFunctions.IsSelectedForNavigation(self.fighterID):
                self.DeselectSquadron()
            else:
                self.SelectSquadron()
                self.parent.SetLastSelectedTube(self.tubeFlagID)
        else:
            self.parent.ClearSelection()
            if movementFunctions.IsSelectedForNavigation(session.shipid):
                movementFunctions.DeselectForNavigation(session.shipid)
            self.SelectSquadron()
            self.parent.SetLastSelectedTube(self.tubeFlagID)

    def IsSelected(self):
        if self.shipFighterState.GetFightersInSpace(self.tubeFlagID) is None:
            return False
        return movementFunctions.IsSelectedForNavigation(self.fighterID)

    def OnStateChange(self, itemID, flag, flagState, *args):
        if flag == states.selectedForNavigation and itemID == self.fighterID:
            if flagState:
                self.squadronCont.ShowSelectionHilite()
            else:
                self.squadronCont.HideSelectionHilite()

    def SelectSquadron(self):
        movementFunctions.SelectForNavigation(self.fighterID)

    def DeselectSquadron(self):
        movementFunctions.DeselectForNavigation(self.fighterID)

    def GetFighterItemID(self):
        return self.squadronCont.GetFighterItemID()

    def GetSquadronMenu(self):
        m = []
        ship = sm.GetService('godma').GetItem(session.shipid)
        if ship is None:
            return m
        tubeStatus = self.shipFighterState.GetTubeStatus(self.tubeFlagID)
        if tubeStatus.statusID == TUBE_STATE_EMPTY:
            m += self._GetSquadronMenuForEmptyTube()
            return m
        if self.GetFightersInSpaceState():
            m.append((MenuLabel('UI/Inventory/Fighters/RecallToLaunchTube'), self.RecallFighterToTube))
            m.append((MenuLabel('UI/Drones/ReturnDroneAndOrbit'), self.ReturnAndOrbit))
            m.append((MenuLabel('UI/Fighters/AbandonFighter'), self.AbandonFighter))
        elif self.GetFightersInTubeState():
            m.append((MenuLabel('UI/Inventory/Fighters/LaunchToSpace'), self.LaunchFightersFromTube))
            m.append((MenuLabel('UI/Inventory/Fighters/UnloadFromLaunchTube'), self.UnloadTubeToFighterBay))
        m += sm.GetService('menu').CelestialMenu(self.fighterID, typeID=self.fighterTypeID)
        return m

    def _GetSquadronMenuForEmptyTube(self):
        HEAVY = 0
        LIGHT = 1
        SUPPORT = 2
        OTHER = 3
        m = []
        fightersInBay = sm.GetService('invCache').GetInventoryFromId(session.shipid).ListFighterBay()
        optionsByClass = defaultdict(list)
        for fighter in fightersInBay:
            typeID = fighter.typeID
            if SquadronIsHeavy(typeID):
                fighterClass = HEAVY
            elif SquadronIsLight(typeID):
                fighterClass = LIGHT
            elif SquadronIsSupport(typeID):
                fighterClass = SUPPORT
            else:
                fighterClass = OTHER
            fighterLabel = GetByLabel('UI/Inflight/Drone/DroneBayEntryWithStacksize', drone=fighter.typeID, stacksize=fighter.stacksize)
            optionsByClass[fighterClass].append((fighterLabel, self.LoadFighterToTube, (fighter.itemID,)))

        for fighterClass in (HEAVY,
         LIGHT,
         SUPPORT,
         OTHER):
            options = optionsByClass.get(fighterClass, [])
            if not options:
                continue
            sortedOptions = sorted(options, key=lambda x: x[0])
            m += sortedOptions
            m += [None]

        return m

    def RecallFighterToTube(self):
        self.squadronMgmtController.RecallFighterToTube(self.fighterID)

    def LoadFighterToTube(self, fighterID):
        self.squadronMgmtController.LoadFightersToTube(fighterID, self.tubeFlagID)

    def UnloadTubeToFighterBay(self):
        self.squadronMgmtController.UnloadTubeToFighterBay(self.tubeFlagID)

    def LaunchFightersFromTube(self):
        self.squadronMgmtController.LaunchFightersFromTube(self.tubeFlagID)

    def AbandonFighter(self):
        sm.GetService('fighters').AbandonFighter(self.fighterID)

    def ReturnAndOrbit(self):
        sm.GetService('fighters').CmdReturnAndOrbit([self.fighterID])


class FightersButtonOpenBay(LeftSideButton):
    default_name = 'inFlightFigtherBayBtn'
    default_texturePath = 'res:/UI/Texture/classes/ShipUI/Fighters/iconFighterBay.png'
    invIDText = 'ShipFighterBay'
    toolTipDescriptionPath = 'Tooltips/Hud/FighterBay_description'

    def OnClick(self, *args):
        LeftSideButton.OnClick(self)
        shipID = GetActiveShip()
        if shipID is None:
            return
        Inventory.OpenOrShow((self.invIDText, shipID), usePrimary=False, toggle=True)

    def LoadTooltipPanel(self, tooltipPanel, *args):
        tooltipPanel.LoadGeneric2ColumnTemplate()
        tooltipPanel.AddLabelShortcut(GetByLabel('Tooltips/Hud/FighterBay'), '')
        tooltipPanel.AddLabelMedium(text=GetByLabel(self.toolTipDescriptionPath), wrapWidth=200, colSpan=tooltipPanel.columns, color=(0.6, 0.6, 0.6, 1))


class FightersButtonOpenStructureBay(FightersButtonOpenBay):
    invIDText = 'StructureFighterBay'
    toolTipDescriptionPath = 'Tooltips/Hud/FighterBayStructure_description'


class FightersButtonLaunchAll(LeftSideButton):
    default_name = 'launchAllFightersBtn'
    default_texturePath = 'res:/UI/Texture/classes/ShipUI/Fighters/iconScrambleSquads-.png'

    def OnClick(self, *args):
        LeftSideButton.OnClick(self)
        shipID = GetActiveShip()
        if shipID is None:
            return
        uicore.layer.shipui.fighterCont.SelectAll()
        sm.GetService('fighters').LaunchAllFighters()

    def LoadTooltipPanel(self, tooltipPanel, *args):
        tooltipPanel.LoadGeneric2ColumnTemplate()
        tooltipPanel.AddLabelShortcut(GetByLabel('Tooltips/Hud/LaunchAll'), '')
        tooltipPanel.AddLabelMedium(text=GetByLabel('Tooltips/Hud/LaunchAll_description'), wrapWidth=200, colSpan=tooltipPanel.columns, color=(0.6, 0.6, 0.6, 1))


class FightersButtonRecallAll(LeftSideButton):
    default_name = 'recallAllFightersBtn'
    default_texturePath = 'res:/UI/Texture/classes/ShipUI/Fighters/iconRecallSquads.png'

    def OnClick(self, *args):
        LeftSideButton.OnClick(self)
        shipID = GetActiveShip()
        if shipID is None:
            return
        uicore.layer.shipui.fighterCont.SelectAll()
        sm.GetService('fighters').RecallAllFightersToTubes()

    def LoadTooltipPanel(self, tooltipPanel, *args):
        recallShortcut = uicore.cmd.GetShortcutStringByFuncName('CmdDronesReturnToBay')
        tooltipPanel.LoadGeneric2ColumnTemplate()
        tooltipPanel.AddLabelShortcut(GetByLabel('Tooltips/Hud/RecallAll'), recallShortcut)
        tooltipPanel.AddLabelMedium(text=GetByLabel('Tooltips/Hud/RecallAll_description'), wrapWidth=200, colSpan=tooltipPanel.columns, color=(0.6, 0.6, 0.6, 1))


class FighterDragButton(ButtonIcon):
    isDragObject = True

    def GetDragData(self, *args):
        return [KeyVal(__guid__='fakeDragData')]

    def PrepareDrag(self, dragContainer, dragSource):
        settings.user.ui.Set('detachFighterUI', True)
        buttonWidth = 32
        shipUI = uicore.layer.shipui
        uicore.uilib.ClipCursor(0, buttonWidth, uicore.desktop.width - buttonWidth, uicore.desktop.height)
        shipUI.RemoveFighterHudBinding()
        dragContainer.width = shipUI.fighterCont.width
        dragContainer.height = shipUI.fighterCont.height
        shipUI.fighterCont.SetParent(dragContainer)
        shipUI.fighterCont.left = 0
        shipUI.fighterCont.top = -shipUI.fighterCont.height
        shipUI.fighterCont.SetAlign(uiconst.TOPLEFT)
        return (0, 0)

    def OnEndDrag(self, dragSource, dropLocation, dragData):
        shipUI = uicore.layer.shipui
        posX = uicore.uilib.x
        posY = uicore.uilib.y - shipUI.fighterCont.height
        settings.char.ui.Set('fightersDetachedPosition', (posX, posY))
        shipUI.DrawFighters()
        uicore.uilib.UnclipCursor()
