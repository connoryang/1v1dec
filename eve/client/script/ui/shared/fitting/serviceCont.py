#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\fitting\serviceCont.py
from carbonui.primitives.container import Container
import carbonui.const as uiconst
from carbonui.primitives.sprite import Sprite
from eve.client.script.ui.control.eveIcon import Icon
from eve.client.script.ui.control.eveLabel import EveLabelMedium
from eve.client.script.ui.inflight.shipModuleButton.moduleButtonTooltip import TooltipModuleWrapper
from eve.client.script.ui.shared.fitting.baseSlot import FittingSlotBase
from eve.client.script.ui.shared.fitting.fittingUtil import GetScaleFactor
from eve.client.script.ui.shared.fitting.utilBtns import FittingUtilBtn
import evetypes
import inventorycommon.const as invConst
from localization import GetByLabel
import uthread

class FittingServiceCont(Container):
    default_name = 'FittingServiceCont'
    default_height = 70
    default_width = 300
    default_align = uiconst.CENTERBOTTOM
    default_top = 4

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.controller = attributes.controller
        self.slotsByFlagID = {}
        scaleFactor = GetScaleFactor()
        slotWidth = int(round(44.0 * scaleFactor))
        slotHeight = int(round(44.0 * scaleFactor))
        label = EveLabelMedium(parent=self, text=GetByLabel('UI/Fitting/StructureServices'), align=uiconst.TOBOTTOM)
        top = label.textheight + 2
        width = 0
        for i, flagID in enumerate(invConst.serviceSlotFlags):
            left = i * (slotWidth + 4)
            slot = FittingServiceSlot(name='%s' % flagID, parent=self, pos=(left,
             top,
             slotWidth,
             slotHeight), controller=self.controller.GetSlotController(flagID))
            self.slotsByFlagID[flagID] = slot
            width += slotWidth + 4

        self.width = width
        self.height = slotHeight + label.textheight + 100
        self.controller.on_slots_with_menu_changed.connect(self.OnSlotsWithMenuChanged)

    def OnSlotsWithMenuChanged(self, oldFlagID, newFlagID):
        slot = self.slotsByFlagID.get(oldFlagID, None)
        if slot is not None:
            slot.HideUtilButtons()


class FittingServiceSlot(FittingSlotBase):
    SLOT_SIZE = 48
    default_align = uiconst.BOTTOMLEFT
    default_height = SLOT_SIZE
    default_width = SLOT_SIZE
    isDragObject = True
    underlayTexturePath = 'res:/UI/Texture/classes/Fitting/stationServiceSlotFrame.png'

    def ApplyAttributes(self, attributes):
        FittingSlotBase.ApplyAttributes(self, attributes)
        self.sr.underlay = Sprite(bgParent=self, name='underlay', state=uiconst.UI_DISABLED, padding=(0, 0, 0, 0), texturePath=self.underlayTexturePath)
        self.flagIcon = Icon(parent=self, name='flagIcon', align=uiconst.CENTER, state=uiconst.UI_DISABLED, width=self.width, height=self.height)
        self.UpdateFitting()

    def UpdateFitting(self):
        if not self.controller.SlotExists() and not self.controller.GetModule():
            self.DisableSlot()
            return
        self.EnableSlot()
        self.SetDragState()
        self.PrepareUtilButtons()
        iconSize = int(self.SLOT_SIZE * GetScaleFactor())
        self.flagIcon.SetSize(iconSize, iconSize)
        if self.controller.GetModule():
            self.flagIcon.LoadIconByTypeID(self.controller.GetModule().typeID, ignoreSize=True)
        else:
            slotIcon = 'res:/UI/Texture/classes/Fitting/stationServiceSlot.png'
            self.flagIcon.LoadIcon(slotIcon, ignoreSize=True)
        if self.controller.GetModule():
            self.tooltipPanelClassInfo = TooltipModuleWrapper()
            modulehint = evetypes.GetName(self.controller.GetModuleTypeID())
            if not self.controller.SlotExists():
                modulehint = GetByLabel('UI/Fitting/SlotDoesNotExist')
            self.hint = modulehint
        else:
            self.tooltipPanelClassInfo = None
            self.hint = self._emptyHint
        self.Hilite(0)
        self.UpdateOnlineDisplay()

    def OnDropData(self, dragObj, nodes):
        if self.controller.GetModule() is not None and not self.controller.SlotExists():
            return
        items = self.GetDroppedItems(nodes)
        for item in items:
            if not getattr(item, 'typeID', None):
                return
            uthread.new(self.AddItem, item)

    def AddItem(self, item, sourceLocation = None):
        if not getattr(item, 'typeID', None):
            return
        validFitting = False
        for effect in cfg.dgmtypeeffects.get(item.typeID, []):
            if effect.effectID in (const.effectServiceSlot,):
                validFitting = True
                if effect.effectID == self.controller.GetPowerType():
                    self.controller.FitModule(item)
                    return
                uicore.Message('ItemDoesntFitPower', {'item': evetypes.GetName(item.typeID),
                 'slotpower': cfg.dgmeffects.Get(self.controller.GetPowerType()).displayName,
                 'itempower': cfg.dgmeffects.Get(effect.effectID).displayName})

        if not validFitting:
            raise UserError('ItemNotHardware', {'itemname': item.typeID})

    def OnMouseEnter(self, *args):
        if self.controller.GetModule() is not None:
            self.ShowUtilButtons()
        else:
            self.hint = self._emptyHint
            self.Hilite(1)
            uicore.Message('ListEntryEnter')

    def OnMouseExit(self, *args):
        if not self.controller.GetModule():
            self.Hilite(0)

    def PrepareUtilButtons(self):
        for btn in self.utilButtons:
            btn.Close()

        self.utilButtons = []
        if not self.controller.GetModule():
            return
        btns = self.GetUtilBtns()
        i = 0
        for btnData in btns:
            left = int(self.left + self.width / 2.0 - 8)
            top = self.height + 20 + i * 16
            utilBtn = FittingUtilBtn(parent=self.parent, icon=btnData.iconPath, left=left, top=top, btnData=btnData, mouseOverFunc=self.ShowUtilButtons, align=uiconst.BOTTOMLEFT, controller=self.controller)
            if btnData.onlineBtn == 1:
                self.sr.onlineButton = utilBtn
            self.utilButtons.append(utilBtn)
            i += 1

    def GetUtilBtns(self):
        btns = []
        isRig = False
        for effect in cfg.dgmtypeeffects.get(self.controller.GetModuleTypeID(), []):
            if effect.effectID == const.effectRigSlot:
                isRig = True
                break

        isOnlinable = self.controller.IsOnlineable()
        if isRig:
            btns += self.GetRigsBtns()
        else:
            btns = self.GetModuleBtns(isOnlinable)
        return btns
