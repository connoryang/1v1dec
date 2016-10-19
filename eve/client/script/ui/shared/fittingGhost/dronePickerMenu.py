#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\fittingGhost\dronePickerMenu.py
import evetypes
from carbonui.control.menuLabel import MenuLabel
import carbonui.const as uiconst
from carbonui.util.sortUtil import SortListOfTuples
from eve.client.script.ui.control.buttons import ButtonIcon
from eve.client.script.ui.control.checkbox import Checkbox
from eve.client.script.ui.control.eveLabel import EveLabelMedium
from eve.client.script.ui.control.eveScroll import Scroll
from localization import GetByLabel
from eve.client.script.ui.control import entries as listentry
from utillib import KeyVal

def GetDroneMenu(controller, menuParent, *args):
    scroll = Scroll(parent=menuParent, align=uiconst.TOTOP, height=100)
    scroll.isSimulated = controller.IsSimulated()
    LoadDroneScroll(scroll)


def LoadDroneScroll(scroll):
    dogmaLocation = sm.GetService('clientDogmaIM').GetFittingDogmaLocation()
    isSimulated = scroll.isSimulated
    scroll.Clear()
    sortedDroneInfo = GetSortedDroneInfo(dogmaLocation)
    activeDronesCopy = dogmaLocation.GetActiveDrones()
    maxWidth = 100
    scrollList = []
    for droneName, drone in sortedDroneInfo:
        qty = getattr(drone.invItem, 'quantity', 1)
        for i in xrange(qty):
            droneID = drone.itemID
            numActive = activeDronesCopy.get(droneID)
            if numActive > 0:
                checked = True
                activeDronesCopy[droneID] -= 1
            else:
                checked = False
            data = {'label': droneName,
             'checked': checked,
             'itemID': droneID,
             'typeID': drone.typeID,
             'getIcon': True,
             'OnClick': ChangeDroneActivityStateEntry,
             'removeFunc': RemoveDrone if isSimulated else None}
            width = ItemEntryCheckbox.GetEntryWidth(ItemEntryCheckbox, data)
            maxWidth = max(maxWidth, width)
            entry = listentry.Get(entryType=None, data=data, decoClass=ItemEntryCheckbox)
            scrollList.append(entry)

    if not scrollList:
        text = GetByLabel('UI/Common/NothingFound')
        scrollList.append(listentry.Get('Generic', data={'label': text}))
        textwidth, textheight = EveLabelMedium.MeasureTextSize(text, maxLines=1)
        maxWidth = textwidth + 10
    scroll.GetEntryWidth = lambda : maxWidth
    scroll.AddNodes(0, scrollList)
    UpdateScrollSize(scroll)


def GetSortedDroneInfo(dogmaLocation):
    shipDogmaItem = dogmaLocation.GetShip()
    if not shipDogmaItem:
        return []
    drones = shipDogmaItem.GetDrones()
    droneInfo = []
    for drone in drones.itervalues():
        droneName = evetypes.GetName(drone.typeID)
        info = (droneName.lower(), (droneName, drone))
        droneInfo.append(info)

    sortedDroneInfo = SortListOfTuples(droneInfo)
    return sortedDroneInfo


def UpdateScrollSize(scroll):
    contentHeight = scroll.GetContentHeight() + 2
    scroll.height = min(contentHeight, 400)


def ChangeDroneActivityStateEntry(node, newValue, *args):
    dogmaLocation = node.scroll.dogmaLocation
    shift = uicore.uilib.Key(uiconst.VK_SHIFT)
    dogmaLocation.SetDroneActivityState(node.itemID, newValue)
    if shift:
        TryChangeSameTypeDrones(node, newValue, dogmaLocation)
        LoadDroneScroll(node.scroll)
    sm.GetService('ghostFittingSvc').SendOnStatsUpdatedEvent()


def TryChangeSameTypeDrones(node, newValue, dogmaLocation):
    typeID = node.typeID
    scroll = node.scroll
    nodeIdx = node.idx
    try:
        for eachNode in scroll.GetNodes():
            if eachNode.idx == nodeIdx:
                continue
            if eachNode.typeID == typeID and eachNode.checked != newValue:
                dogmaLocation.SetDroneActivityState(eachNode.itemID, newValue)

    except UserError:
        return


def RemoveDrone(node):
    droneID = node.itemID
    sm.GetService('ghostFittingSvc').UnfitDrone(droneID)
    node.scroll.RemoveNodes([node])
    UpdateScrollSize(node.scroll)


class ItemEntryCheckbox(listentry.Item):
    __guid__ = 'listentry.ItemEntryCheckbox'
    ENTRYHEIGHT = 28
    ICONLEFT = 24

    def Startup(self, *args):
        listentry.Item.Startup(self, args)
        self.checkbox = Checkbox(text='', parent=self, configName='cb', retval=None, checked=0, align=uiconst.TOPLEFT, pos=(6, 4, 0, 0), callback=self.OnClick, state=uiconst.UI_NORMAL)
        self.checkbox.data = {}
        self.checkbox.ToggleState = self.ToggleCbState
        self.removeBtn = ButtonIcon(texturePath='res:/UI/Texture/Icons/73_16_210.png', pos=(0, 0, 16, 16), align=uiconst.CENTERRIGHT, parent=self, hint=GetByLabel('UI/Generic/RemoveItem'), idx=0, func=self.RemoveItem)
        self.removeBtn.display = False

    def Load(self, args):
        listentry.Item.Load(self, args)
        data = self.sr.node
        self.checkbox.SetChecked(data.checked, 0)
        self.checkbox.data = {'key': data.cfgname,
         'retval': data.retval}
        self.sr.icon.left = self.ICONLEFT
        self.sr.icon.state = uiconst.UI_DISABLED
        self.sr.label.left = self.sr.icon.left + self.sr.icon.width + 4
        if self.sr.techIcon:
            self.sr.techIcon.left = self.ICONLEFT
        self.sr.infoicon.display = False
        if data.removeFunc:
            self.removeBtn.display = True

    def OnClick(self, *args):
        node = self.sr.node
        isChecked = node.checked
        if isChecked:
            eve.Message('DiodeDeselect')
        else:
            eve.Message('DiodeClick')
        newValue = not isChecked
        if node.Get('OnClick', None):
            node.OnClick(node, newValue)
        node.checked = newValue
        self.checkbox.SetChecked(newValue, report=0)

    def ToggleCbState(self, *args):
        return self.OnClick()

    def GetMenu(self):
        return [(MenuLabel('UI/Commands/ShowInfo'), self.ShowInfo, (self.sr.node,))]

    def RemoveItem(self, *args):
        node = self.sr.node
        if node.Get('removeFunc', None):
            node.removeFunc(node)

    def GetEntryWidth(cls, node):
        label = node['label']
        textwidth, textheight = EveLabelMedium.MeasureTextSize(label, maxLines=1)
        return cls.ICONLEFT + textwidth + 40 + 24

    def GetDragData(self):
        typeID = self.sr.node.typeID
        keyVal = KeyVal(__guid__='listentry.GenericMarketItem', typeID=typeID, label=evetypes.GetName(typeID))
        return [keyVal]
