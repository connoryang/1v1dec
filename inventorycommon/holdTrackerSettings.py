#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\inventorycommon\holdTrackerSettings.py
from inventorycommon import const as inventoryConst
CARGO_TRACKING_FORMAT = 'cargoHoldForShipType%s'

class CargoTrackingSettings(object):

    def GetStringForType(self, type):
        return CARGO_TRACKING_FORMAT % type

    def GetTrackedHoldForShip(self):
        trackedHold = inventoryConst.shipCargoHold
        shipType = self._GetCurrentShipTypeID()
        if shipType:
            trackedHold = settings.char.ui.Get(self.GetStringForType(shipType), inventoryConst.shipCargoHold)
        return trackedHold

    def SaveTrackedHoldForShip(self, hold):
        if hold == None:
            hold = inventoryConst.shipCargoHold
        shipType = self._GetCurrentShipTypeID()
        if shipType:
            settings.char.ui.Set(self.GetStringForType(shipType), hold)

    def IsCargoHoldBlinkEnabled(self):
        return settings.user.ui.Get('BlinkCargoHudIcon', True)

    def _GetCurrentShipTypeID(self):
        if session.shipid and session.solarsystemid:
            shipItem = sm.GetService('godma').GetItem(session.shipid)
            if shipItem:
                return shipItem.typeID
