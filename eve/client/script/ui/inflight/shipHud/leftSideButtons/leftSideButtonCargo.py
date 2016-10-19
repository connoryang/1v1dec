#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\inflight\shipHud\leftSideButtons\leftSideButtonCargo.py
from eve.client.script.environment.invControllers import ShipCargo, GetNameForFlag
from eve.client.script.ui.inflight.shipHud.leftSideButton import LeftSideButton
from eve.client.script.ui.services.menusvc import MenuList
from eve.client.script.ui.shared.inventory.invWindow import Inventory
from eve.common.script.sys.eveCfg import GetActiveShip
from inventorycommon.holdTracker import HoldTracker
from inventorycommon.holdTrackerSettings import CargoTrackingSettings
from invCtrl import GetInvCtrlFromInvID
import localization
import carbonui.const as uiconst
from eve.client.script.ui.inflight.shipHud.leftSideButton import BTN_SIZE
TRACKED_HOLD_COLOR = (0.27, 0.72, 1.0, 1.0)

class LeftSideButtonCargo(LeftSideButton):
    default_name = 'inFlightCargoBtn'
    default_texturePath = 'res:/UI/Texture/icons/44_32_10.png'
    label = 'UI/Generic/Cargo'
    cmdName = 'OpenCargoHoldOfActiveShip'
    _tracker = None

    def ApplyAttributes(self, attributes):
        LeftSideButton.ApplyAttributes(self, attributes)
        self.LoadTracker()

    def LoadTracker(self):
        if sm.GetService('experimentClientSvc').IsProgressCargoButtonEnabled():
            self.adjustForTracker()
            self._tracker = HoldTracker(cargoButton=self, trackingSettings=CargoTrackingSettings(), getControllerFromIDFunc=GetInvCtrlFromInvID)
        else:
            self._tracker = None

    def adjustForTracker(self):
        self.busy.state = uiconst.UI_DISABLED
        self.busyContainer.state = uiconst.UI_DISABLED

    def BlinkWhite(self):
        uicore.animations.FadeIn(self.blinkBG, callback=self.OnBlinkedIn, duration=1.0)

    def OnBlinkedIn(self, *args):
        uicore.animations.FadeOut(self.blinkBG, duration=0.25)

    def OnClick(self, *args):
        LeftSideButton.OnClick(self)
        shipID = GetActiveShip()
        if shipID is None:
            return
        Inventory.OpenOrShow(('ShipCargo', shipID), usePrimary=False, toggle=True)

    def SetFillRatio(self, ratio):
        reverseRatio = min(1.0, max(0.0, 1.0 - ratio))
        offset = BTN_SIZE * reverseRatio
        self.busy.top = -offset
        self.busyContainer.top = offset
        self.busy.opacity = max(0.4, ratio)
        self.busy.display = True

    def OnDropData(self, dragObj, nodes):
        ShipCargo().OnDropData(nodes)

    def AddMoreToTooltipPanel(self, tooltipPanel):
        if self._tracker:
            holds = self._tracker.GetHoldsDictionary()
            mainHold = self._tracker.mainHoldName
            for cargoHold, percentageFull in holds.iteritems():
                percentage, locationFlag = percentageFull
                localizedname = GetNameForFlag(locationFlag)
                label, value = tooltipPanel.AddLabelValue(label=localizedname, value=percentage)
                if cargoHold == mainHold:
                    label.bold = True
                    label.opacity = 1.0
                    label.color = TRACKED_HOLD_COLOR
                    value.bold = True
                    value.color = TRACKED_HOLD_COLOR

    def GetMenu(self):
        if self._tracker:
            menu = MenuList()
            submenu = MenuList()
            holds = self._tracker.GetHoldsDictionary()
            mainHold = self._tracker.mainHoldName
            for cargoHold, percentageFull in holds.iteritems():
                percentage, locationFlag = percentageFull
                holdName = GetNameForFlag(locationFlag)
                holdText = holdName
                if mainHold == cargoHold:
                    holdText = localization.GetByLabel('UI/Inflight/Submenus/HoldOrBayTracked', holdName=holdName)
                submenu.append(self.MakeMenuItem(text=holdText, callbackFunction=lambda x = cargoHold: self.SetCargoHold(x)))

            menu.append([localization.GetByLabel('UI/Inflight/Submenus/TrackHoldBay'), submenu])
            return menu

    def SetCargoHold(self, choiceHold):
        if self._tracker:
            self._tracker.SetMainCargoHold(choiceHold)

    def MakeMenuItem(self, text, callbackFunction):
        return (text, callbackFunction)

    def _OnClose(self, *args, **kw):
        if self._tracker:
            self.busy.display = False
            self._tracker.Destroy()
            self._tracker = None
            uicore.animations.StopAllAnimations(self.blinkBG)
        LeftSideButton._OnClose(self, args, kw)
