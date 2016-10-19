#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\structure\dockedOverlay\dockedPanel.py
from carbon.common.script.util.linkUtil import GetShowInfoLink
from carbonui.primitives.container import Container
from carbonui.primitives.sprite import Sprite
from eve.client.script.ui.control.buttons import Button
from eve.client.script.ui.control.eveLabel import EveLabelMedium
from eve.client.script.ui.control.eveWindow import Window
import carbonui.const as uiconst
from eve.common.script.sys.eveCfg import GetActiveShip
import evetypes

class DockedPanel(Window):
    default_name = 'DockedPanel'
    default_topParentHeight = 0
    default_isPinable = False
    default_isMinimizable = False
    default_isKillable = False
    default_height = 250
    default_width = 300
    default_clipChildren = True
    default_scope = 'structure'

    @staticmethod
    def default_top(*args):
        return 16

    @staticmethod
    def default_left(*args):
        return uicore.desktop.width - DockedPanel.default_width - 16

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        self.height = self.default_height
        self.width = self.default_width
        self.structureID = attributes.structureID
        self.BuildUI()

    def BuildUI(self):
        inv = sm.GetService('invCache').GetInventoryFromId(self.structureID)
        item = inv.GetItem()
        stationName = cfg.evelocations.Get(self.structureID).name or evetypes.GetName(item.typeID)
        stationText = GetShowInfoLink(item.typeID, stationName, itemID=self.structureID)
        self.nameLabel = EveLabelMedium(name='nameLabel', parent=self.sr.main, text=stationText, padLeft=10, align=uiconst.TOTOP, state=uiconst.UI_NORMAL)
        ownerText = GetShowInfoLink(const.typeCorporation, cfg.eveowners.Get(item.ownerID).name, itemID=item.ownerID)
        self.ownerLabel = EveLabelMedium(name='ownerLabel', parent=self.sr.main, text=ownerText, padLeft=10, align=uiconst.TOTOP, state=uiconst.UI_NORMAL)
        Button(parent=self.sr.main, align=uiconst.TOTOP, label='_Take control', func=self.TakeControl, padding=(10, 2, 10, 2))
        self.AddCurrentShip()
        Button(parent=self.sr.main, align=uiconst.TOTOP, label='_Undock', func=self.Undock, padding=(10, 2, 10, 2))

    def Undock(self, *args):
        sm.GetService('structureDocking').Undock(self.structureID)

    def TakeControl(self, *args):
        sm.GetService('structureControl').Board(self.structureID)

    def AddCurrentShip(self):
        activeShipID = GetActiveShip()
        if not activeShipID:
            return
        inv = sm.GetService('invCache').GetInventoryFromId(activeShipID)
        item = inv.GetItem()
        shipName = GetShowInfoLink(item.typeID, cfg.evelocations.Get(activeShipID).name, itemID=activeShipID)
        self.ownerLabel = EveLabelMedium(name='ownerLabel', parent=self.sr.main, text=shipName, padLeft=10, align=uiconst.TOTOP, state=uiconst.UI_NORMAL)
        texturePath = evetypes.inventorycommon.typeHelpers.GetHoloIconPath(item.typeID)
        cont = Container(parent=self.sr.main, name='shipCont', align=uiconst.TOTOP, height=128)
        sprite = Sprite(name='shipSprite', parent=cont, pos=(0, 0, 128, 128), align=uiconst.CENTER, texturePath=texturePath)
        sprite.GetMenu = (self.GetShipMenu, item)
        sprite.OnDblClick = self.DoubleClickShip

    def GetShipMenu(self, item):
        return sm.GetService('menu').InvItemMenu(item, True, False)

    def DoubleClickShip(self, *args):
        uicore.cmd.OpenCargoHoldOfActiveShip()
