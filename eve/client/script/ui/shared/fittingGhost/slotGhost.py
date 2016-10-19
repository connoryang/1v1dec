#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\fittingGhost\slotGhost.py
import math
import logging
from carbonui.primitives.sprite import Sprite
from carbonui.primitives.transform import Transform
from eve.client.script.ui.shared.fitting.baseSlot import FittingSlotBase
from eve.client.script.ui.shared.fitting.fittingUtil import GetScaleFactor, RigFittingCheck
import evetypes
from eve.client.script.ui.shared.fitting.utilBtns import FittingUtilBtn, UtilBtnData
from eve.client.script.ui.shared.fittingGhost import BROWSE_MODULES, SIMULATION_MODULES, SIMULATION_SKILLS
from eve.client.script.ui.shared.fittingGhost.ghostFittingUtil import ONLINE, OFFLINE, ACTIVE, OVERHEATED
from shipfitting.fittingStuff import IsRightSlotForType
import uicontrols
import uix
import uiutil
import mathUtil
import uthread
import blue
import util
import carbon.client.script.util.lg as lg
import service
import base
import uicls
import carbonui.const as uiconst
import localization
from eve.client.script.ui.inflight.shipModuleButton.moduleButtonTooltip import TooltipModuleWrapper
from eve.client.script.ui.station.fitting.fittingTooltipUtils import SetFittingTooltipInfo
import telemetry
import inventorycommon.typeHelpers
MAXMODULEHINTWIDTH = 300
logger = logging.getLogger(__name__)

class FittingSlotGhost(FittingSlotBase):
    __guid__ = 'xtriui.FittingSlotGhost'
    __notifyevents__ = ['OnRefreshModuleBanks']
    default_name = 'fittingSlot'
    default_width = 44
    default_height = 54
    default_align = uiconst.TOPLEFT
    default_state = uiconst.UI_NORMAL
    isDragObject = True
    slotsToHintDict = {'hiSlot': ('UI/Fitting/EmptyHighPowerSlot', 'EmptyHighSlot'),
     'medSlot': ('UI/Fitting/EmptyMediumPowerSlot', 'EmptyMidSlot'),
     'loSlot': ('UI/Fitting/EmptyLowPowerSlot', 'EmptyLowSlot'),
     'subSystemSlot': ('UI/Fitting/EmptySubsystemSlot', ''),
     'rigSlot': ('UI/Fitting/EmptyRigSlot', '')}

    @telemetry.ZONE_METHOD
    def ApplyAttributes(self, attributes):
        FittingSlotBase.ApplyAttributes(self, attributes)
        self.flagIcon = uicontrols.Icon(parent=self, name='flagIcon', align=uiconst.CENTER, state=uiconst.UI_DISABLED, width=self.width, height=self.height)
        self.sr.underlay = Sprite(bgParent=self, name='underlay', state=uiconst.UI_DISABLED, padding=(-10, -5, -10, -5), texturePath='res:/UI/Texture/Icons/81_64_1.png')
        self.dontHaveLine = None
        self.moduleSlotFill = None
        self.skillSprite = None
        self.groupMark = None
        self.chargeIndicator = None
        sm.RegisterNotify(self)
        self.radCosSin = attributes.radCosSin
        self.invReady = 1
        self.UpdateFitting()
        self.controller.on_simulation_mode_changed.connect(self.UpdateSimulationMode)

    def ConstructDontHaveLine(self):
        if self.dontHaveLine:
            return
        self.dontHaveLine = Sprite(parent=self, name='dontHaveLine', align=uiconst.TOALL, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/Fitting/moduleFrameDots.png', padding=(-10, -5, -10, -5), color=(1, 1, 0, 1.0))

    def ConstructModuleSlotFill(self):
        if self.moduleSlotFill:
            return
        self.moduleSlotFill = Sprite(parent=self, name='moduleSlotFill', align=uiconst.TOALL, state=uiconst.UI_DISABLED, padding=(-8, -4, -8, -4), texturePath='res:/UI/Texture/classes/Fitting/moduleSlotFill.png', color=(1, 1, 1, 0.5))
        self.moduleSlotFill.display = False

    def ConstructSkillSprite(self):
        if self.skillSprite:
            return
        self.skillSprite = Sprite(parent=self, name='skillSprite', align=uiconst.TOALL, state=uiconst.UI_DISABLED, padding=(-8, -4, -8, -4), texturePath='res:/UI/Texture/classes/Fitting/slotGlowInner.png', color=(1, 1, 1, 0.5))
        self.skillSprite.display = False

    def ConstructGroupMark(self):
        if self.groupMark:
            return
        self.groupMark = Sprite(parent=self, name='groupMark', pos=(-10, 14, 16, 16), align=uiconst.CENTER, state=uiconst.UI_NORMAL, idx=0)
        self.groupMark.GetMenu = self.GetGroupMenu

    def ConstructChargeIndicator(self):
        if self.chargeIndicator:
            return
        self.chargeIndicator = Sprite(parent=self, name='chargeIndicator', padTop=-2, height=7, align=uiconst.TOTOP, state=uiconst.UI_HIDDEN, texturePath='res:/UI/Texture/Icons/81_64_2.png', ignoreSize=True)
        self.chargeIndicator.rectWidth = 44
        self.chargeIndicator.rectHeight = 7

    def OnRefreshModuleBanks(self):
        self.SetGroup()

    def SetGroup(self):
        try:
            if self.controller.GetModule() is not None and not self.controller.SlotExists():
                self.controller.DestroyWeaponBank()
        except ReferenceError:
            pass

        parentID = self.controller.GetParentID()
        allGroupsDict = settings.user.ui.Get('linkedWeapons_groupsDict', {})
        groupDict = allGroupsDict.get(parentID, {})
        ret = self.GetBankGroup(groupDict)
        if ret is None:
            if self.groupMark:
                self.groupMark.Hide()
            return
        groupNumber = ret.groupNumber
        self.ConstructGroupMark()
        self.groupMark.state = uiconst.UI_NORMAL
        self.groupMark.rotation = -self.GetRotation()
        if groupNumber < 0:
            availGroups = [1,
             2,
             3,
             4,
             5,
             6,
             7,
             8]
            for masterID, groupNum in groupDict.iteritems():
                if groupNum in availGroups:
                    availGroups.remove(groupNum)

            groupNumber = availGroups[0] if availGroups else ''
        self.groupMark.texturePath = 'res:/UI/Texture/Icons/73_16_%s.png' % (176 + groupNumber)
        self.groupMark.hint = localization.GetByLabel('UI/Fitting/GroupNumber', groupNumber=groupNumber)
        groupDict[ret.masterID] = groupNumber
        allGroupsDict[parentID] = groupDict
        settings.user.ui.Set('linkedWeapons_groupsDict', allGroupsDict)

    def GetBankGroup(self, groupDict):
        module = self.controller.GetModule()
        try:
            if not module:
                return None
        except ReferenceError:
            return None

        masterID = self.controller.IsInWeaponBank()
        if not masterID:
            return None
        if masterID in groupDict:
            groupNumber = groupDict.get(masterID)
        else:
            groupNumber = -1
        ret = util.KeyVal()
        ret.masterID = masterID
        ret.groupNumber = groupNumber
        return ret

    def PrepareUtilButtons(self):
        for btn in self.utilButtons:
            btn.Close()

        self.utilButtons = []
        if not self.controller.GetModule():
            return
        myrad, cos, sin, cX, cY = self.radCosSin
        btns = self.GetUtilBtns()
        rad = myrad - 34
        i = 0
        for btnData in btns:
            left = int((rad - i * 16) * cos) + cX - 16 / 2
            top = int((rad - i * 16) * sin) + cY - 16 / 2
            utilBtn = FittingUtilBtn(parent=self.parent, icon=btnData.iconPath, left=left, top=top, btnData=btnData, mouseOverFunc=self.ShowUtilButtons, controller=self.controller)
            if btnData.onlineBtn == 1:
                self.sr.onlineButton = utilBtn
            self.utilButtons.append(utilBtn)
            i += 1

    def GetUtilBtns(self):
        btns = []
        if self.controller.GetCharge():
            btns += self.GetChargesBtns()
        isRig = False
        for effect in cfg.dgmtypeeffects.get(self.controller.GetModuleTypeID(), []):
            if effect.effectID == const.effectRigSlot:
                isRig = True
                break

        isSubSystem = evetypes.GetCategoryID(self.controller.GetModuleTypeID()) == const.categorySubSystem
        isOnlinable = self.controller.IsOnlineable()
        if isRig:
            btns += self.GetRigsBtns()
        elif isSubSystem:
            btns += self.GetSubSystemBtns()
        else:
            btns += self.GetModuleBtns(isOnlinable)
        return btns

    def GetChargesBtns(self):
        moduleTypeID = self.controller.GetModuleTypeID()
        btns = [UtilBtnData(localization.GetByLabel('UI/Fitting/RemoveCharge'), 'ui_38_16_200', self.controller.Unfit, 1, 0), UtilBtnData(localization.GetByLabel('UI/Fitting/ShowChargeInfo'), 'ui_38_16_208', self.ShowChargeInfo, 1, 0), UtilBtnData(evetypes.GetName(moduleTypeID), inventorycommon.typeHelpers.GetIconFile(moduleTypeID), None, 1, 0)]
        return btns

    def GetSubSystemBtns(self):
        btns = [UtilBtnData(localization.GetByLabel('UI/Commands/ShowInfo'), 'ui_38_16_208', self.ShowInfo, 1, 0)]
        return btns

    def DisableSlot(self):
        FittingSlotBase.DisableSlot(self)
        self.UpdateGhostFittingIcons(None)
        self.Hilite(0)

    def EnableSlot(self):
        FittingSlotBase.EnableSlot(self)
        self.sr.underlay.display = True

    def HideSlot(self):
        self.state = uiconst.UI_HIDDEN

    @telemetry.ZONE_METHOD
    def UpdateFitting(self):
        if self.destroyed:
            return
        if not self.controller.SlotExists() and not self.controller.GetModule():
            if self.controller.IsSubsystemSlot() and self.controller.parentController.HasStance():
                self.HideSlot()
            else:
                self.DisableSlot()
            return
        self.EnableSlot()
        self.SetDragState()
        if self.controller.GetCharge():
            chargeQty = self.controller.GetChargeQuantity()
            if self.controller.GetModule() is None:
                portion = 1.0
            else:
                cap = self.controller.GetChargeCapacity()
                if cap.capacity == 0:
                    portion = 1.0
                else:
                    portion = cap.used / cap.capacity
            step = max(0, min(4, int(portion * 5.0)))
            self.ConstructChargeIndicator()
            self.chargeIndicator.rectTop = 10 * step
            self.chargeIndicator.state = uiconst.UI_NORMAL
            self.chargeIndicator.hint = '%s %d%%' % (evetypes.GetName(self.controller.GetCharge().typeID), portion * 100)
        elif not self.controller.GetModule():
            self.HideUtilButtons(1)
            if self.chargeIndicator:
                self.chargeIndicator.Hide()
        elif self.controller.IsChargeable():
            self.ConstructChargeIndicator()
            self.chargeIndicator.rectTop = 0
            self.chargeIndicator.state = uiconst.UI_NORMAL
            self.chargeIndicator.hint = localization.GetByLabel('UI/Fitting/NoCharge')
        elif self.chargeIndicator:
            self.chargeIndicator.Hide()
        if self.controller.GetModule():
            self.tooltipPanelClassInfo = TooltipModuleWrapper()
            modulehint = evetypes.GetName(self.controller.GetModuleTypeID())
            if self.controller.GetCharge():
                modulehint += '<br>%s' % localization.GetByLabel('UI/Fitting/ChargeQuantity', charge=self.controller.GetCharge().typeID, chargeQuantity=chargeQty)
            if not self.controller.SlotExists():
                modulehint = localization.GetByLabel('UI/Fitting/SlotDoesNotExist')
            self.hint = modulehint
        else:
            self.tooltipPanelClassInfo = None
            self.hint = self._emptyHint
            tooltipName = self._emptyTooltip
            if tooltipName:
                SetFittingTooltipInfo(targetObject=self, tooltipName=tooltipName, includeDesc=False)
        self.PrepareUtilButtons()
        iconSize = int(48 * GetScaleFactor())
        self.flagIcon.SetSize(iconSize, iconSize)
        if self.controller.GetCharge() or self.controller.GetModule():
            self.flagIcon.LoadIconByTypeID((self.controller.GetCharge() or self.controller.GetModule()).typeID, ignoreSize=True)
            self.flagIcon.rotation = -self.GetRotation()
        else:
            rev = 0
            slotIcon = {const.flagSubSystemSlot0: 'res:/UI/Texture/Icons/81_64_9.png',
             const.flagSubSystemSlot1: 'res:/UI/Texture/Icons/81_64_10.png',
             const.flagSubSystemSlot2: 'res:/UI/Texture/Icons/81_64_11.png',
             const.flagSubSystemSlot3: 'res:/UI/Texture/Icons/81_64_12.png',
             const.flagSubSystemSlot4: 'res:/UI/Texture/Icons/81_64_13.png'}.get(self.controller.GetFlagID(), None)
            if slotIcon is None:
                slotIcon = {const.effectLoPower: 'res:/UI/Texture/Icons/81_64_5.png',
                 const.effectMedPower: 'res:/UI/Texture/Icons/81_64_6.png',
                 const.effectHiPower: 'res:/UI/Texture/Icons/81_64_7.png',
                 const.effectRigSlot: 'res:/UI/Texture/Icons/81_64_8.png'}.get(self.controller.GetPowerType(), None)
            else:
                rev = 1
            if slotIcon is not None:
                self.flagIcon.LoadIcon(slotIcon, ignoreSize=True)
            if rev:
                self.flagIcon.rotation = mathUtil.DegToRad(180.0)
            else:
                self.flagIcon.rotation = 0.0
        self.SetGroup()
        self.UpdateOnlineDisplay()
        self.UpdateStatusDisplay()
        self.UpdateGhostFittingIcons(self.controller.GetModule())
        if not self.hilitedFromMathing:
            self.Hilite(0)

    def IsCharge(self, typeID):
        return evetypes.GetCategoryID(typeID) == const.categoryCharge

    def Add(self, item, sourceLocation = None):
        if self.controller.parentController.IsSimulated():
            return self.AddSimulatedItem(item, sourceLocation)
        else:
            guid = getattr(item, '__guid__', None)
            if guid is None or guid in ('listentry.InvItem', 'xtriui.InvItem'):
                return self.AddRealItem(item, sourceLocation)
            sm.GetService('ghostFittingSvc').LoadCurrentShip()
            return self.AddSimulatedItem(item, sourceLocation)

    def AddSimulatedItem(self, item, sourceLocation):
        if not IsRightSlotForType(item.typeID, self.controller.GetPowerType()):
            return
        shipID = self.controller.GetParentID()
        ghostFittingSvc = sm.GetService('ghostFittingSvc')
        ghostFittingSvc.FitModuleToShipAndChangeState(shipID, self.controller.GetFlagID(), item.typeID)
        ghostFittingSvc.SendFittingSlotsChangedEvent()

    def AddRealItem(self, item, sourceLocation = None):
        if not getattr(item, 'typeID', None):
            return
        if not RigFittingCheck(item):
            return
        requiredSkills = sm.GetService('skills').GetRequiredSkills(item.typeID)
        for skillID, level in requiredSkills.iteritems():
            if getattr(sm.GetService('skills').HasSkill(skillID), 'skillLevel', 0) < level:
                sm.GetService('tutorial').OpenTutorialSequence_Check(uix.skillfittingTutorial)
                break

        if self.IsCharge(item.typeID) and self.controller.IsChargeable():
            self.controller.FitCharge(item)
        validFitting = False
        for effect in cfg.dgmtypeeffects.get(item.typeID, []):
            if self.IsFittableItem(effect.effectID):
                validFitting = True
                if effect.effectID == self.controller.GetPowerType():
                    shift = uicore.uilib.Key(uiconst.VK_SHIFT)
                    isFitted = item.locationID == self.controller.GetParentID() and item.flagID != const.flagCargo
                    if isFitted and shift:
                        if self.controller.GetModule():
                            if self.controller.GetModule().typeID == item.typeID:
                                self.controller.LinkWithWeapon(item)
                                return
                            else:
                                uicore.Message('CustomNotify', {'notify': localization.GetByLabel('UI/Fitting/GroupingIncompatible')})
                                return
                    self.controller.FitModule(item)
                    return
                uicore.Message('ItemDoesntFitPower', {'item': evetypes.GetName(item.typeID),
                 'slotpower': cfg.dgmeffects.Get(self.controller.GetPowerType()).displayName,
                 'itempower': cfg.dgmeffects.Get(effect.effectID).displayName})

        if not validFitting:
            raise UserError('ItemNotHardware', {'itemname': item.typeID})

    def IsFittableItem(self, effectID):
        isFittableItem = effectID in (const.effectHiPower,
         const.effectMedPower,
         const.effectLoPower,
         const.effectSubSystem,
         const.effectRigSlot,
         const.effectServiceSlot)
        return isFittableItem

    def GetMenu(self):
        if self.controller.GetModuleTypeID() and self.controller.GetModuleID():
            m = FittingSlotBase.GetMenu(self)
            m += self.GetGroupMenu()
            return m

    def GetGroupMenu(self, *args):
        masterID = self.controller.IsInWeaponBank()
        if masterID:
            return [(uiutil.MenuLabel('UI/Fitting/ClearGroup'), self.UnlinkModule, ())]
        return []

    def OnDblClick(self, *args):
        if self.controller.IsSimulated():
            sm.ScatterEvent('OnSlotDblClicked', self.controller.GetFlagID())

    def OnClick(self, *args):
        if self.controller.IsSimulated() and self.controller.GetSimulationMode() == SIMULATION_MODULES:
            return self.OnClickSimulated()

    def OnClickSimulated(self):
        if self.controller.GetModule() is None:
            return
        uicore.registry.SetFocus(self)
        typeID = self.controller.GetModuleTypeID()
        itemKey = self.controller.GetModuleID()
        flagID = self.controller.GetFlagID()
        ghostFittingSvc = sm.GetService('ghostFittingSvc')
        ghostFittingSvc.SwitchBetweenModes(itemKey, typeID, flagID)
        self.UpdateStatusDisplay()

    def UpdateStatusDisplay(self):
        self.HideElement(self.moduleSlotFill)
        ghostFittingSvc = sm.GetService('ghostFittingSvc')
        simulationMode = ghostFittingSvc.GetSimulationMode()
        if not self.controller.parentController.IsSimulated() or simulationMode != SIMULATION_MODULES:
            return
        itemKey = self.controller.GetModuleID()
        typeID = self.controller.GetModuleTypeID()
        flagID = self.controller.GetFlagID()
        if itemKey is None or typeID is None:
            return
        typeEffectInfo = ghostFittingSvc.GetDefaultAndOverheatEffect(typeID)
        currentStatus = ghostFittingSvc.GetModuleStatus(itemKey, typeID, flagID)
        self.flagIcon.SetAlpha(1.0)
        self.ConstructModuleSlotFill()
        if typeEffectInfo.defaultEffect and typeEffectInfo.isActivatable:
            texturePath = 'res:/UI/Texture/classes/Fitting/slotGlowInner.png'
        else:
            texturePath = 'res:/UI/Texture/classes/Fitting/slotGlowOuter.png'
        self.moduleSlotFill.SetTexturePath(texturePath)
        self.moduleSlotFill.display = True
        if currentStatus == OFFLINE:
            self.flagIcon.SetAlpha(0.25)
            self.moduleSlotFill.SetRGB(0.5, 0.5, 0.5, 0.2)
        elif currentStatus == ONLINE:
            self.moduleSlotFill.SetRGB(0.5, 0.5, 0.5, 1.5)
        elif currentStatus == ACTIVE:
            self.ConstructModuleSlotFill()
            self.moduleSlotFill.SetRGB(1, 1, 0, 1.0)
        elif currentStatus == OVERHEATED:
            self.ConstructModuleSlotFill()
            self.moduleSlotFill.SetRGB(1, 0, 0, 1.0)

    def ShowChargeInfo(self, *args):
        if self.controller.GetCharge():
            sm.GetService('info').ShowInfo(self.controller.GetCharge().typeID, self.controller.GetCharge().itemID)

    def UnlinkModule(self):
        self.controller.DestroyWeaponBank()

    def _OnEndDrag(self, *args):
        self.left = self.top = -2

    def OnEndDrag(self, *args):
        if self.controller.GetModule() is not None:
            sm.ScatterEvent('OnResetSlotLinkingMode', self.controller.GetModule().typeID)

    def GetTooltipPosition(self):
        rect, point = self.PositionHint()
        return rect

    def GetTooltipPointer(self):
        rect, point = self.PositionHint()
        return point

    def UpdateInfo_TimedCall(self, *args):
        if self.destroyed or self.moduleButtonHint.destroyed:
            self.moduleButtonHint = None
            self.updateTimer = None
            return
        if self.controller.GetModuleTypeID():
            if self.controller.GetCharge():
                chargeItemID = self.controller.GetCharge().itemID
            else:
                chargeItemID = None
            self.moduleButtonHint.UpdateAllInfo(self.controller.GetModuleID(), chargeItemID, fromWhere='fitting')

    def PositionHint(self, *args):
        myRotation = self.rotation + 2 * math.pi
        myRotation = -myRotation
        sl, st, sw, sh = self.parent.GetAbsolute()
        cX = sl + sw / 2.0
        cY = st + sh / 2.0
        rad, cos, sin, oldcX, oldcY = self.radCosSin
        hintLeft = int(round(rad * cos))
        hintTop = int(round(rad * sin))
        cap = rad * 0.7
        if hintLeft < -cap:
            point = uiconst.POINT_RIGHT_2
        elif hintLeft > cap:
            point = uiconst.POINT_LEFT_2
        elif hintTop < -cap:
            if hintLeft < 0:
                point = uiconst.POINT_BOTTOM_3
            else:
                point = uiconst.POINT_BOTTOM_1
        elif hintLeft < 0:
            point = uiconst.POINT_TOP_3
        else:
            point = uiconst.POINT_TOP_1
        return ((hintLeft + cX - 15,
          hintTop + cY - 15,
          30,
          30), point)

    def OnDropData(self, dragObj, nodes):
        if self.controller.GetModule() is not None and not self.controller.SlotExists():
            return
        items = self.GetDroppedItems(nodes)
        chargeTypeID = None
        chargeItems = []
        for item in items:
            if not getattr(item, 'typeID', None):
                lg.Info('fittingUI', 'Dropped a non-item here', item)
                return
            if self.controller.IsChargeable() and self.IsCharge(item.typeID):
                if chargeTypeID is None:
                    chargeTypeID = item.typeID
                if chargeTypeID == item.typeID:
                    chargeItems.append(item)
            else:
                uthread.new(self.Add, item)

        if len(chargeItems):
            self.controller.FitCharges(chargeItems)

    def _OnClose(self, *args):
        self.updateTimer = None
        moduleButtonHint = getattr(uicore.layer.hint, 'moduleButtonHint', None)
        if moduleButtonHint and not moduleButtonHint.destroyed:
            if moduleButtonHint.fromWhere == 'fitting':
                uicore.layer.hint.moduleButtonHint.FadeOpacity(0.0)

    def GetDroppedItems(self, nodes):
        items = []
        for node in nodes:
            if node.__guid__ in ('listentry.InvItem', 'xtriui.InvItem'):
                invType = node.rec
                if self.controller.IsFittableType(invType.typeID):
                    items.append(invType)
            elif node.__guid__ in ('listentry.GenericMarketItem', 'listentry.Item', 'listentry.FittingModuleEntry'):
                if self.controller.IsFittableType(node.typeID):
                    items.append(node.invtype or util.KeyVal(typeID=node.typeID))

        return items

    def UpdateGhostFittingIcons(self, invItem):
        fittingSvc = sm.GetService('fittingSvc')
        if fittingSvc.IsShipSimulated() and invItem:
            self.SetMissingIcon(invItem)
            self.SetSkillIcon(invItem)
        else:
            self.HideElement(self.dontHaveLine)
            self.HideElement(self.skillSprite)
            self.HideElement(self.moduleSlotFill)
            self.sr.underlay.display = True

    def HideElement(self, element):
        if element:
            element.display = False

    def SetMissingIcon(self, invItem):
        return
        self.ConstructDontHaveLine()
        self.dontHaveLine.display = False
        self.sr.underlay.display = True
        if invItem is None or not session.stationid2:
            return
        hangarInv = sm.GetService('invCache').GetInventory(const.containerHangar)
        items = hangarInv.List(const.flagHangar)
        for eachItem in items:
            if eachItem.typeID == invItem.typeID:
                return

        self.dontHaveLine.display = True
        self.sr.underlay.display = False

    def SetSkillIcon(self, invItem):
        simulationMode = sm.GetService('ghostFittingSvc').GetSimulationMode()
        fittingSvc = sm.GetService('fittingSvc')
        if invItem is None or simulationMode != SIMULATION_SKILLS or not fittingSvc.IsShipSimulated():
            self.HideElement(self.skillSprite)
            return
        dogmaLocation = fittingSvc.GetCurrentDogmaLocation()
        missingSkills = dogmaLocation.CheckSkillRequirementsForType(invItem.typeID)
        self.ConstructSkillSprite()
        self.skillSprite.display = True
        if missingSkills:
            self.skillSprite.SetRGB(1, 0, 0, 0.5)
        else:
            self.skillSprite.SetRGB(0, 1, 0, 0.5)

    def UpdateSimulationMode(self, newMode):
        self.UpdateOnlineDisplay()
        self.UpdateStatusDisplay()
        self.UpdateGhostFittingIcons(self.controller.GetModule())
